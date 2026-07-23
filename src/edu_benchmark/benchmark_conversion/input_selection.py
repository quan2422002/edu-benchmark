"""Load audited snapshots, build pass inputs, and select a deterministic pilot."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .corrections import apply_dialogue_corrections
from .dialogue_split import DialogueSplitError, parse_dialogue_turns
from .schema import (
    CANONICAL_QUALITY_DECISIONS,
    CONVERSION_INPUT_COLUMNS,
    dump_json_string_list,
    validate_conversion_input_row,
)

EXPECTED_CRITERIA_PER_SAMPLE = 18


class SnapshotContractError(ValueError):
    """Raised when snapshot tables cannot be joined safely."""


@dataclass(frozen=True)
class AuditSnapshot:
    """Three phase-1 audit tables belonging to one source batch."""

    source_batch: str
    normalized_rows: list[dict[str, str]]
    quality_rows: list[dict[str, str]]
    checklist_rows: list[dict[str, str]]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SnapshotContractError(f"Missing snapshot table: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_audit_snapshot(
    *,
    source_batch: str,
    normalized_path: Path,
    quality_path: Path,
    checklist_path: Path,
) -> AuditSnapshot:
    """Read one immutable phase-1 audit snapshot."""

    return AuditSnapshot(
        source_batch=source_batch,
        normalized_rows=_read_csv(normalized_path),
        quality_rows=_read_csv(quality_path),
        checklist_rows=_read_csv(checklist_path),
    )


def _unique_index(rows: Sequence[Mapping[str, str]], *, table_name: str) -> dict[str, Mapping[str, str]]:
    index: dict[str, Mapping[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        sample_id = str(row.get("sample_id", "")).strip()
        if not sample_id:
            raise SnapshotContractError(f"{table_name} row {row_number} is missing sample_id")
        if sample_id in index:
            raise SnapshotContractError(f"{table_name} contains duplicate sample_id: {sample_id}")
        index[sample_id] = row
    return index


def aggregate_all_raw_audit_evidence(
    checklist_rows: Iterable[Mapping[str, str]],
) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Union all detailed criterion evidence per sample with stable ordering."""

    evidence: dict[str, set[str]] = defaultdict(set)
    criterion_counts: Counter[str] = Counter()
    seen_pairs: set[tuple[str, str]] = set()
    for row_number, row in enumerate(checklist_rows, start=2):
        sample_id = str(row.get("sample_id", "")).strip()
        criterion_id = str(row.get("criterion_id", "")).strip()
        if not sample_id or not criterion_id:
            raise SnapshotContractError(
                f"Checklist row {row_number} is missing sample_id or criterion_id"
            )
        pair = (sample_id, criterion_id)
        if pair in seen_pairs:
            raise SnapshotContractError(
                f"Checklist contains duplicate sample/criterion pair: {sample_id}/{criterion_id}"
            )
        seen_pairs.add(pair)
        criterion_counts[sample_id] += 1
        fragment_id = str(row.get("evidence_fragment_id", "")).strip()
        if fragment_id:
            evidence[sample_id].update(
                part.strip() for part in fragment_id.split(";") if part.strip()
            )
        else:
            evidence[sample_id]
    return (
        {sample_id: sorted(values) for sample_id, values in evidence.items()},
        dict(criterion_counts),
    )


def normalize_blocking_evidence(value: str) -> str:
    """Normalize phase-1 sample-level blocking evidence to a JSON list."""

    stripped = str(value or "").strip()
    if not stripped:
        return "[]"
    if stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise SnapshotContractError("Invalid JSON blocking evidence") from exc
        if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
            raise SnapshotContractError("Blocking evidence JSON must contain strings")
        values = [item.strip() for item in parsed if item.strip()]
    else:
        values = [item.strip() for item in stripped.split(";") if item.strip()]
    return dump_json_string_list(values)


def build_pass_conversion_input(
    snapshots: Sequence[AuditSnapshot],
    *,
    dialogue_corrections: Mapping[str, Sequence[Mapping[str, str]]] | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Join phase-1 tables and build validated pass-only conversion input."""

    output_rows: list[dict[str, str]] = []
    validation_errors: list[dict[str, str]] = []
    seen_across_batches: set[str] = set()
    dialogue_corrections = dialogue_corrections or {}

    for snapshot in snapshots:
        normalized = _unique_index(snapshot.normalized_rows, table_name="normalized_dialogue_rows")
        quality = _unique_index(snapshot.quality_rows, table_name="quality_check_suggestions")
        evidence, criterion_counts = aggregate_all_raw_audit_evidence(snapshot.checklist_rows)

        id_sets = {
            "normalized_dialogue_rows": set(normalized),
            "quality_check_suggestions": set(quality),
            "raw_dialogue_checklist_results": set(evidence),
        }
        union = set().union(*id_sets.values())
        if any(ids != union for ids in id_sets.values()):
            details = ", ".join(
                f"{name} missing {len(union - ids)}" for name, ids in id_sets.items()
            )
            raise SnapshotContractError(f"Snapshot sample IDs do not align: {details}")
        overlap = seen_across_batches & union
        if overlap:
            raise SnapshotContractError(
                f"Sample IDs overlap source batches: {sorted(overlap)[:3]}"
            )
        seen_across_batches.update(union)

        for sample_id in sorted(union):
            normalized_row = normalized[sample_id]
            quality_row = quality[sample_id]
            decision = str(quality_row.get("quality_decision", "")).strip()
            if decision not in CANONICAL_QUALITY_DECISIONS:
                raise SnapshotContractError(
                    f"Noncanonical quality_decision for {sample_id}: {decision!r}"
                )
            if criterion_counts.get(sample_id) != EXPECTED_CRITERIA_PER_SAMPLE:
                raise SnapshotContractError(
                    f"{sample_id} has {criterion_counts.get(sample_id, 0)} checklist criteria; "
                    f"expected {EXPECTED_CRITERIA_PER_SAMPLE}"
                )
            if decision != "pass":
                continue
            raw_dialogue = str(normalized_row.get("dialogue", ""))
            conversion_dialogue, correction_ids = apply_dialogue_corrections(
                raw_dialogue, dialogue_corrections.get(sample_id, [])
            )
            row = {
                "sample_id": sample_id,
                "source_batch": snapshot.source_batch,
                "source_file": str(normalized_row.get("source_file", "")),
                "source_row_number": str(normalized_row.get("source_row_number", "")),
                "grade": str(normalized_row.get("grade", "")),
                "grade_label": str(normalized_row.get("grade_label", "")),
                "stt": str(normalized_row.get("stt", "")),
                "lesson": str(normalized_row.get("lesson", "")),
                "position": str(normalized_row.get("position", "")),
                "question": str(normalized_row.get("question", "")),
                "bloom_level": str(normalized_row.get("bloom_level", "")),
                "answer_sgv": str(normalized_row.get("answer_sgv", "")),
                "raw_dialogue": raw_dialogue,
                "conversion_dialogue": conversion_dialogue,
                "dialogue_correction_ids": dump_json_string_list(correction_ids),
                "raw_quality_decision": decision,
                "raw_quality_confidence_score": str(quality_row.get("confidence_score", "")),
                "raw_audit_blocking_criterion_ids": str(
                    quality_row.get("blocking_criterion_ids", "")
                ),
                "raw_audit_blocking_evidence_fragment_ids": normalize_blocking_evidence(
                    str(quality_row.get("evidence_fragment_ids", ""))
                ),
                "raw_audit_all_evidence_fragment_ids": dump_json_string_list(
                    evidence[sample_id]
                ),
            }
            row_errors = validate_conversion_input_row(row)
            for error_code in row_errors:
                validation_errors.append(
                    {
                        "sample_id": sample_id,
                        "source_batch": snapshot.source_batch,
                        "severity": "blocking",
                        "error_code": error_code,
                        "message": f"Conversion input contract violation: {error_code}",
                    }
                )
            output_rows.append({column: row.get(column, "") for column in CONVERSION_INPUT_COLUMNS})

    return sorted(output_rows, key=lambda row: row["sample_id"]), validation_errors


def cognitive_band(value: str) -> str:
    """Map raw Bloom labels to the three pilot strata."""

    normalized = value.casefold()
    if "vận dụng" in normalized:
        return "Vận dụng"
    if "thông hiểu" in normalized or normalized.startswith("hiểu"):
        return "Hiểu"
    if "nhận biết" in normalized or normalized.startswith("biết"):
        return "Biết"
    return "Khác"


def turn_count_bin(turn_count: int) -> str:
    """Return the Plan-01 dialogue-length stratum."""

    if 4 <= turn_count <= 6:
        return "4-6"
    if 7 <= turn_count <= 9:
        return "7-9"
    if turn_count >= 10:
        return ">=10"
    return "<4"


def select_conversion_pilot(
    rows: Sequence[Mapping[str, str]], *, size_per_grade: int = 10
) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Select a deterministic, split-compatible pilot for each grade."""

    enriched_by_grade: dict[str, list[dict[str, str]]] = defaultdict(list)
    invalid_parse_counts: Counter[str] = Counter()
    for original in sorted(rows, key=lambda row: str(row["sample_id"])):
        row = dict(original)
        try:
            turns = parse_dialogue_turns(row["conversion_dialogue"])
        except DialogueSplitError:
            invalid_parse_counts[row["grade"]] += 1
            continue
        row["_pilot_cognitive_band"] = cognitive_band(row["bloom_level"])
        row["_pilot_turn_count"] = str(len(turns))
        row["_pilot_turn_bin"] = turn_count_bin(len(turns))
        evidence = json.loads(row["raw_audit_all_evidence_fragment_ids"])
        row["_pilot_evidence_band"] = "single" if len(evidence) == 1 else "multiple"
        enriched_by_grade[row["grade"]].append(row)

    selected: list[dict[str, str]] = []
    grade_summaries: dict[str, object] = {}
    fallbacks: list[str] = []
    for grade in ("6", "7", "8", "9"):
        candidates = enriched_by_grade.get(grade, [])
        if len(candidates) < size_per_grade:
            raise SnapshotContractError(
                f"Grade {grade} has only {len(candidates)} split-compatible pass rows"
            )
        grade_selected: list[dict[str, str]] = []
        remaining = list(candidates)
        cognitive_seen: Counter[str] = Counter()
        turn_bins_seen: Counter[str] = Counter()
        evidence_seen: Counter[str] = Counter()
        lesson_seen: Counter[str] = Counter()

        while len(grade_selected) < size_per_grade:
            under_lesson_cap = [row for row in remaining if lesson_seen[row["lesson"]] < 2]
            pool = under_lesson_cap or remaining
            if not under_lesson_cap:
                fallbacks.append(
                    f"grade {grade}: lesson cap relaxed at selection "
                    f"{len(grade_selected) + 1}"
                )
            best: dict[str, str] | None = None
            best_score = -1
            for row in pool:
                score = (
                    100 * (cognitive_seen[row["_pilot_cognitive_band"]] == 0)
                    + 80 * (turn_bins_seen[row["_pilot_turn_bin"]] == 0)
                    + 50 * (evidence_seen[row["_pilot_evidence_band"]] == 0)
                    + 30 * (lesson_seen[row["lesson"]] == 0)
                    + 5 * (lesson_seen[row["lesson"]] == 1)
                )
                if score > best_score:
                    best = row
                    best_score = score
            assert best is not None
            grade_selected.append(best)
            remaining.remove(best)
            cognitive_seen[best["_pilot_cognitive_band"]] += 1
            turn_bins_seen[best["_pilot_turn_bin"]] += 1
            evidence_seen[best["_pilot_evidence_band"]] += 1
            lesson_seen[best["lesson"]] += 1

        required_categories = {
            "cognitive": {"Biết", "Hiểu", "Vận dụng"},
            "turn_bin": {"4-6", "7-9", ">=10"},
            "evidence": {"single", "multiple"},
        }
        achieved_categories = {
            "cognitive": set(cognitive_seen),
            "turn_bin": set(turn_bins_seen),
            "evidence": set(evidence_seen),
        }
        for dimension, required in required_categories.items():
            missing = sorted(required - achieved_categories[dimension])
            if missing:
                fallbacks.append(
                    f"grade {grade}: unavailable selected {dimension} strata: {', '.join(missing)}"
                )
        selected.extend(grade_selected)
        grade_summaries[grade] = {
            "selected_count": len(grade_selected),
            "split_incompatible_pass_rows_excluded": invalid_parse_counts[grade],
            "cognitive_band_counts": dict(sorted(cognitive_seen.items())),
            "turn_bin_counts": dict(sorted(turn_bins_seen.items())),
            "evidence_band_counts": dict(sorted(evidence_seen.items())),
            "lesson_counts": dict(sorted(lesson_seen.items())),
        }

    clean_selected = [
        {key: value for key, value in row.items() if not key.startswith("_pilot_")}
        for row in selected
    ]
    summary: dict[str, object] = {
        "selection_method": "deterministic_greedy_v0",
        "size_per_grade": size_per_grade,
        "total_selected": len(clean_selected),
        "grades": grade_summaries,
        "fallbacks": fallbacks,
    }
    return clean_selected, summary

"""File-oriented orchestration for deterministic benchmark conversion."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .corrections import apply_dialogue_corrections, load_dialogue_corrections
from .dialogue_split import (
    DialogueSplitError,
    parse_dialogue_turns,
    split_each_tutor_turn_candidates,
    split_final_tutor_response_candidate,
)
from .input_selection import (
    AuditSnapshot,
    cognitive_band,
    load_audit_snapshot,
    select_conversion_pilot,
    turn_count_bin,
    build_pass_conversion_input,
)
from .schema import (
    CANDIDATE_SPLIT_COLUMNS,
    CONVERSION_INPUT_COLUMNS,
    INPUT_ERROR_COLUMNS,
    PLAN01_CANDIDATE_SPLIT_COLUMNS,
    PLAN01_TRACE_COLUMNS,
    CONVERSION_DISPOSITION_COLUMNS,
    SPLIT_ERROR_COLUMNS,
    TRACE_COLUMNS,
    validate_candidate_split_row,
    validate_conversion_input_row,
    validate_conversion_trace_row,
    validate_conversion_disposition_row,
)

PLAN02_POLICY_ID = "D02-01-multi-candidate-each-tutor-turn"

PILOT_ID_COLUMNS = [
    "sample_id",
    "grade",
    "lesson",
    "bloom_level",
    "cognitive_band",
    "turn_count",
    "turn_count_bin",
    "raw_audit_evidence_count",
]

MULTI_CANDIDATE_PILOT_ID_COLUMNS = [
    "sample_id",
    "grade",
    "lesson",
    "bloom_level",
    "turn_count",
    "candidate_count",
    "max_history_turn_count",
    "dialogue_correction_ids",
    "selection_reason",
]

PLAN02_EXPECTED_RAW_SAMPLE_COUNT = 665
PLAN02_EXPECTED_CANDIDATE_COUNT = 2028
PLAN02_EXPECTED_RAW_BY_GRADE = {"6": 106, "7": 132, "8": 209, "9": 218}
PLAN02_EXPECTED_CANDIDATES_BY_GRADE = {
    "6": 279,
    "7": 438,
    "8": 557,
    "9": 754,
}
PLAN02_EXPECTED_CANDIDATES_PER_RAW = {
    "2": 292,
    "3": 167,
    "4": 105,
    "5": 85,
    "6": 14,
    "7": 2,
}
PLAN02_EXPECTED_HISTORY_TURN_COUNTS = {
    "0": 665,
    "2": 665,
    "4": 373,
    "6": 206,
    "8": 101,
    "10": 16,
    "12": 2,
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV table."""

    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(
    path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, str]]
) -> None:
    """Write a CSV with stable column order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def default_snapshot_specs(experiment_root: Path) -> list[dict[str, object]]:
    """Return the two immutable input snapshot specifications."""

    inherited = experiment_root / "inherited_resources" / "from_20260709_155523"
    return [
        {
            "source_batch": "grade6_7",
            "normalized_path": inherited / "raw_audit_grade6_7" / "normalized_dialogue_rows.csv",
            "quality_path": inherited / "raw_audit_grade6_7" / "quality_check_suggestions.csv",
            "checklist_path": inherited
            / "raw_audit_grade6_7"
            / "raw_dialogue_checklist_results.repaired.csv",
        },
        {
            "source_batch": "grade8_9",
            "normalized_path": inherited / "raw_audit_grade8_9" / "normalized_dialogue_rows.csv",
            "quality_path": inherited / "raw_audit_grade8_9" / "quality_check_suggestions.csv",
            "checklist_path": inherited
            / "raw_audit_grade8_9"
            / "raw_dialogue_checklist_results.regex_repaired.csv",
        },
    ]


def run_conversion_input_build(
    experiment_root: Path,
    *,
    snapshot_specs: Sequence[Mapping[str, object]] | None = None,
    corrections_path: Path | None = None,
) -> dict[str, object]:
    """Build and write all joined pass inputs for Plan 01."""

    specs = snapshot_specs or default_snapshot_specs(experiment_root)
    snapshots: list[AuditSnapshot] = []
    for spec in specs:
        snapshots.append(
            load_audit_snapshot(
                source_batch=str(spec["source_batch"]),
                normalized_path=Path(spec["normalized_path"]),
                quality_path=Path(spec["quality_path"]),
                checklist_path=Path(spec["checklist_path"]),
            )
        )
    output_root = experiment_root / "outputs" / "benchmark_conversion"
    correction_file = corrections_path or output_root / "dialogue_corrections.csv"
    corrections = load_dialogue_corrections(correction_file)
    rows, errors = build_pass_conversion_input(
        snapshots, dialogue_corrections=corrections
    )
    write_csv_rows(
        output_root / "conversion_input_pass_samples.csv",
        CONVERSION_INPUT_COLUMNS,
        rows,
    )
    write_csv_rows(
        output_root / "input_validation_errors.csv",
        INPUT_ERROR_COLUMNS,
        errors,
    )
    return {
        "input_row_count": len(rows),
        "unique_sample_count": len({row["sample_id"] for row in rows}),
        "blocking_error_count": sum(error["severity"] == "blocking" for error in errors),
        "corrected_sample_count": len(corrections),
        "output_root": str(output_root),
    }


def run_conversion_pilot(
    experiment_root: Path,
    *,
    input_path: Path | None = None,
    size_per_grade: int = 10,
    split_strategy: str = "final_tutor_response",
) -> dict[str, object]:
    """Select, split, validate, and write the deterministic conversion pilot."""

    if split_strategy != "final_tutor_response":
        raise ValueError(f"Unsupported split strategy: {split_strategy}")
    conversion_root = experiment_root / "outputs" / "benchmark_conversion"
    source_path = input_path or conversion_root / "conversion_input_pass_samples.csv"
    source_rows = read_csv_rows(source_path)
    invalid_input_rows = {
        row["sample_id"]: violations
        for row in source_rows
        if (violations := validate_conversion_input_row(row))
    }
    if invalid_input_rows:
        first_sample = sorted(invalid_input_rows)[0]
        raise ValueError(
            "Pilot input contains conversion-contract violations; "
            f"first: {first_sample}: {invalid_input_rows[first_sample]}"
        )
    eligibility_errors: list[dict[str, str]] = []
    for row in source_rows:
        try:
            split_final_tutor_response_candidate(row)
        except DialogueSplitError as exc:
            eligibility_errors.append(
                {
                    "sample_id": row["sample_id"],
                    "source_batch": row["source_batch"],
                    "severity": "excluded_from_pilot",
                    "error_code": exc.code,
                    "message": str(exc),
                }
            )
    selected, selection_summary = select_conversion_pilot(
        source_rows, size_per_grade=size_per_grade
    )

    candidates: list[dict[str, str]] = []
    traces: list[dict[str, str]] = []
    selected_split_errors: list[dict[str, str]] = []
    pilot_ids: list[dict[str, str]] = []
    for row in selected:
        try:
            turns = parse_dialogue_turns(row["conversion_dialogue"])
            candidate = split_final_tutor_response_candidate(row)
            candidate_errors = validate_candidate_split_row(candidate)
            if candidate_errors:
                raise DialogueSplitError(
                    "candidate_contract_violation", "; ".join(candidate_errors)
                )
        except DialogueSplitError as exc:
            selected_split_errors.append(
                {
                    "sample_id": row["sample_id"],
                    "source_batch": row["source_batch"],
                    "severity": "blocking",
                    "error_code": exc.code,
                    "message": str(exc),
                }
            )
            continue
        candidates.append(candidate)
        traces.append({field: candidate.get(field, "") for field in TRACE_COLUMNS})
        evidence_count = len(json.loads(row["raw_audit_all_evidence_fragment_ids"]))
        pilot_ids.append(
            {
                "sample_id": row["sample_id"],
                "grade": row["grade"],
                "lesson": row["lesson"],
                "bloom_level": row["bloom_level"],
                "cognitive_band": cognitive_band(row["bloom_level"]),
                "turn_count": str(len(turns)),
                "turn_count_bin": turn_count_bin(len(turns)),
                "raw_audit_evidence_count": str(evidence_count),
            }
        )

    output_root = conversion_root / "pilot_v0"
    write_csv_rows(output_root / "pilot_sample_ids.csv", PILOT_ID_COLUMNS, pilot_ids)
    write_csv_rows(
        output_root / "benchmark_candidate_splits.csv",
        PLAN01_CANDIDATE_SPLIT_COLUMNS,
        candidates,
    )
    write_csv_rows(
        output_root / "conversion_trace.csv", PLAN01_TRACE_COLUMNS, traces
    )
    write_csv_rows(
        output_root / "dialogue_split_errors.csv",
        SPLIT_ERROR_COLUMNS,
        eligibility_errors + selected_split_errors,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "pilot_selection_summary.json").write_text(
        json.dumps(selection_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "selected_raw_sample_count": len(selected),
        "candidate_count": len(candidates),
        "excluded_incompatible_count": len(eligibility_errors),
        "selected_split_error_count": len(selected_split_errors),
        "split_error_count": len(eligibility_errors) + len(selected_split_errors),
        "grade_counts": dict(
            sorted(
                {
                    grade: sum(row["grade"] == grade for row in pilot_ids)
                    for grade in {row["grade"] for row in pilot_ids}
                }.items()
            )
        ),
        "output_root": str(output_root),
    }


def _split_error(
    row: Mapping[str, str],
    *,
    error_code: str,
    message: str,
) -> dict[str, str]:
    return {
        "sample_id": str(row.get("sample_id", "")),
        "source_batch": str(row.get("source_batch", "")),
        "severity": "blocking",
        "error_code": error_code,
        "message": message,
    }


def _validate_multi_candidate_inputs(
    source_rows: Sequence[Mapping[str, str]],
    *,
    corrections_path: Path,
) -> list[dict[str, str]]:
    """Validate Plan-02 inputs and reproduce every correction from raw text."""

    errors: list[dict[str, str]] = []
    corrections = load_dialogue_corrections(corrections_path)
    seen_sample_ids: set[str] = set()
    source_sample_ids = {
        str(row.get("sample_id", "")).strip() for row in source_rows
    }
    for missing_sample_id in sorted(set(corrections) - source_sample_ids):
        errors.append(
            {
                "sample_id": missing_sample_id,
                "source_batch": "",
                "severity": "blocking",
                "error_code": "correction_sample_missing_from_input",
                "message": "Correction table references a sample outside the input.",
            }
        )

    for row in source_rows:
        sample_id = str(row.get("sample_id", "")).strip()
        if sample_id in seen_sample_ids:
            errors.append(
                _split_error(
                    row,
                    error_code="duplicate_sample_id",
                    message=f"Duplicate conversion input sample_id: {sample_id}",
                )
            )
            continue
        seen_sample_ids.add(sample_id)
        for violation in validate_conversion_input_row(row):
            errors.append(
                _split_error(
                    row,
                    error_code=violation,
                    message=f"Conversion input contract violation: {violation}",
                )
            )
        try:
            reproduced_dialogue, reproduced_correction_ids = (
                apply_dialogue_corrections(
                    str(row.get("raw_dialogue", "")),
                    corrections.get(sample_id, []),
                )
            )
            recorded_correction_ids = json.loads(
                str(row.get("dialogue_correction_ids", ""))
            )
            if reproduced_dialogue != str(row.get("conversion_dialogue", "")):
                errors.append(
                    _split_error(
                        row,
                        error_code="conversion_dialogue_not_reproducible",
                        message=(
                            "conversion_dialogue does not match the raw dialogue "
                            "plus the approved correction overlay."
                        ),
                    )
                )
            if reproduced_correction_ids != recorded_correction_ids:
                errors.append(
                    _split_error(
                        row,
                        error_code="dialogue_correction_ids_mismatch",
                        message=(
                            "Recorded correction IDs do not match the approved "
                            "correction overlay."
                        ),
                    )
                )
            turns = parse_dialogue_turns(reproduced_dialogue)
            if not any(turn.role == "tutor" for turn in turns):
                errors.append(
                    _split_error(
                        row,
                        error_code="no_tutor_turns",
                        message="Dialogue has no tutor turn to convert.",
                    )
                )
        except (DialogueSplitError, ValueError, json.JSONDecodeError) as exc:
            error_code = (
                exc.code
                if isinstance(exc, DialogueSplitError)
                else "correction_or_parse_failure"
            )
            errors.append(
                _split_error(
                    row,
                    error_code=error_code,
                    message=str(exc),
                )
            )
    return errors


def select_multi_candidate_migration_pilot(
    rows: Sequence[Mapping[str, str]],
    *,
    size_per_grade: int = 5,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Select a deterministic, diverse Plan-02 migration pilot."""

    if size_per_grade < 1:
        raise ValueError("size_per_grade must be positive")
    by_grade: dict[str, list[dict[str, str]]] = defaultdict(list)
    for original in sorted(rows, key=lambda item: str(item["sample_id"])):
        row = dict(original)
        turns = parse_dialogue_turns(str(row["conversion_dialogue"]))
        candidate_count = sum(turn.role == "tutor" for turn in turns)
        row["_turn_count"] = str(len(turns))
        row["_candidate_count"] = str(candidate_count)
        row["_max_history_turn_count"] = str(2 * (candidate_count - 1))
        row["_selection_reason"] = ""
        by_grade[str(row["grade"])].append(row)

    selected: list[dict[str, str]] = []
    pilot_ids: list[dict[str, str]] = []
    for grade in ("6", "7", "8", "9"):
        grade_rows = by_grade.get(grade, [])
        if len(grade_rows) < size_per_grade:
            raise ValueError(
                f"Grade {grade} has only {len(grade_rows)} rows; "
                f"{size_per_grade} required"
            )
        grade_selected: list[dict[str, str]] = []
        forced = [
            row
            for row in grade_rows
            if json.loads(str(row["dialogue_correction_ids"]))
        ]
        for row in forced:
            if len(grade_selected) >= size_per_grade:
                break
            row["_selection_reason"] = "approved_correction_coverage"
            grade_selected.append(row)

        selected_ids = {row["sample_id"] for row in grade_selected}
        covered_counts = {
            int(row["_candidate_count"]) for row in grade_selected
        }
        for candidate_count in sorted(
            {int(row["_candidate_count"]) for row in grade_rows}
        ):
            if len(grade_selected) >= size_per_grade:
                break
            if candidate_count in covered_counts:
                continue
            row = next(
                item
                for item in grade_rows
                if int(item["_candidate_count"]) == candidate_count
                and item["sample_id"] not in selected_ids
            )
            row["_selection_reason"] = (
                f"candidate_count_stratum_{candidate_count}"
            )
            grade_selected.append(row)
            selected_ids.add(row["sample_id"])
            covered_counts.add(candidate_count)

        for row in grade_rows:
            if len(grade_selected) >= size_per_grade:
                break
            if row["sample_id"] in selected_ids:
                continue
            row["_selection_reason"] = "deterministic_fill"
            grade_selected.append(row)
            selected_ids.add(row["sample_id"])

        for row in sorted(grade_selected, key=lambda item: item["sample_id"]):
            selected.append(
                {
                    key: value
                    for key, value in row.items()
                    if not key.startswith("_")
                }
            )
            pilot_ids.append(
                {
                    "sample_id": row["sample_id"],
                    "grade": row["grade"],
                    "lesson": row["lesson"],
                    "bloom_level": row["bloom_level"],
                    "turn_count": row["_turn_count"],
                    "candidate_count": row["_candidate_count"],
                    "max_history_turn_count": row[
                        "_max_history_turn_count"
                    ],
                    "dialogue_correction_ids": row[
                        "dialogue_correction_ids"
                    ],
                    "selection_reason": row["_selection_reason"],
                }
            )
    return selected, pilot_ids


def _build_multi_candidate_outputs(
    rows: Sequence[Mapping[str, str]],
) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    candidates: list[dict[str, str]] = []
    traces: list[dict[str, str]] = []
    raw_summaries: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    candidate_ids: set[str] = set()

    for row in sorted(rows, key=lambda item: str(item["sample_id"])):
        try:
            row_candidates = split_each_tutor_turn_candidates(row)
            target_indices: list[int] = []
            row_candidate_ids: set[str] = set()
            row_traces: list[dict[str, str]] = []
            for candidate in row_candidates:
                violations = validate_candidate_split_row(candidate)
                if violations:
                    raise DialogueSplitError(
                        "candidate_contract_violation",
                        "; ".join(violations),
                    )
                candidate_id = candidate["benchmark_candidate_id"]
                if (
                    candidate_id in candidate_ids
                    or candidate_id in row_candidate_ids
                ):
                    raise DialogueSplitError(
                        "duplicate_candidate_id",
                        f"Duplicate candidate ID: {candidate_id}",
                    )
                target_index = int(candidate["_target_tutor_turn_index"])
                trace = {
                    "benchmark_candidate_id": candidate_id,
                    "sample_id": candidate["sample_id"],
                    "source_batch": str(row.get("source_batch", "")),
                    "source_file": str(row.get("source_file", "")),
                    "source_row_number": str(
                        row.get("source_row_number", "")
                    ),
                    "target_tutor_turn_index": str(target_index),
                    "split_strategy": "each_tutor_turn",
                    "dialogue_correction_ids": str(
                        row.get("dialogue_correction_ids", "[]")
                    ),
                }
                trace_violations = validate_conversion_trace_row(trace)
                if trace_violations:
                    raise DialogueSplitError(
                        "trace_contract_violation",
                        "; ".join(trace_violations),
                    )
                row_candidate_ids.add(candidate_id)
                target_indices.append(target_index)
                row_traces.append(trace)

            raw_summary = {
                "sample_id": str(row["sample_id"]),
                "grade": str(row["grade"]),
                "candidate_count": str(len(row_candidates)),
                "first_target_tutor_turn_index": str(min(target_indices)),
                "last_target_tutor_turn_index": str(max(target_indices)),
                "conversion_disposition": "converted",
                "reason_code": "",
                "reason": "",
            }
            summary_violations = (
                validate_conversion_disposition_row(raw_summary)
            )
            if summary_violations:
                raise DialogueSplitError(
                    "raw_summary_contract_violation",
                    "; ".join(summary_violations),
                )
            candidate_ids.update(row_candidate_ids)
            candidates.extend(row_candidates)
            traces.extend(row_traces)
            raw_summaries.append(raw_summary)
        except (DialogueSplitError, ValueError) as exc:
            errors.append(
                _split_error(
                    row,
                    error_code=(
                        exc.code
                        if isinstance(exc, DialogueSplitError)
                        else "multi_candidate_conversion_failure"
                    ),
                    message=str(exc),
                )
            )

    candidates.sort(
        key=lambda row: (
            row["sample_id"],
            int(row["_target_tutor_turn_index"]),
        )
    )
    traces.sort(
        key=lambda row: (
            row["sample_id"],
            int(row["target_tutor_turn_index"]),
        )
    )
    raw_summaries.sort(key=lambda row: row["sample_id"])
    return candidates, traces, raw_summaries, errors


def _multi_candidate_statistics(
    candidates: Sequence[Mapping[str, str]],
    raw_summaries: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    return {
        "raw_sample_count": len(raw_summaries),
        "candidate_family_count": len(
            {row["sample_id"] for row in candidates}
        ),
        "candidate_count": len(candidates),
        "raw_sample_counts_by_grade": dict(
            sorted(Counter(row["grade"] for row in raw_summaries).items())
        ),
        "candidate_counts_by_grade": dict(
            sorted(Counter(row["grade"] for row in candidates).items())
        ),
        "candidates_per_raw_dialogue": dict(
            sorted(
                Counter(
                    row["candidate_count"] for row in raw_summaries
                ).items(),
                key=lambda item: int(item[0]),
            )
        ),
        "history_turn_counts": dict(
            sorted(
                Counter(
                    str(len(json.loads(row["conversation_history"])))
                    for row in candidates
                ).items(),
                key=lambda item: int(item[0]),
            )
        ),
    }


def _validate_plan02_baseline(statistics: Mapping[str, object]) -> None:
    expected = {
        "raw_sample_count": PLAN02_EXPECTED_RAW_SAMPLE_COUNT,
        "candidate_family_count": PLAN02_EXPECTED_RAW_SAMPLE_COUNT,
        "candidate_count": PLAN02_EXPECTED_CANDIDATE_COUNT,
        "raw_sample_counts_by_grade": PLAN02_EXPECTED_RAW_BY_GRADE,
        "candidate_counts_by_grade": PLAN02_EXPECTED_CANDIDATES_BY_GRADE,
        "candidates_per_raw_dialogue": PLAN02_EXPECTED_CANDIDATES_PER_RAW,
        "history_turn_counts": PLAN02_EXPECTED_HISTORY_TURN_COUNTS,
    }
    mismatches = [
        f"{field}: expected {value!r}, got {statistics.get(field)!r}"
        for field, value in expected.items()
        if statistics.get(field) != value
    ]
    if mismatches:
        raise ValueError(
            "Plan-02 acceptance baseline mismatch: " + "; ".join(mismatches)
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _create_staging_directory(output_root: Path) -> Path:
    output_root.parent.mkdir(parents=True, exist_ok=True)
    return Path(
        tempfile.mkdtemp(
            prefix=f".{output_root.name}.staging-",
            dir=output_root.parent,
        )
    )


def _atomic_publish_directory(staging_root: Path, output_root: Path) -> None:
    """Replace one output bundle while preserving rollback on swap failure."""

    backup_root: Path | None = None
    if output_root.exists():
        backup_root = Path(
            tempfile.mkdtemp(
                prefix=f".{output_root.name}.backup-",
                dir=output_root.parent,
            )
        )
        backup_root.rmdir()
        os.replace(output_root, backup_root)
    try:
        os.replace(staging_root, output_root)
    except Exception:
        if backup_root is not None and backup_root.exists():
            os.replace(backup_root, output_root)
        raise
    if backup_root is not None and backup_root.exists():
        shutil.rmtree(backup_root)


def _validate_serialized_candidate_mapping(
    *,
    source_rows: Sequence[Mapping[str, str]],
    candidate_path: Path,
    trace_path: Path,
    disposition_path: Path,
) -> dict[str, object]:
    """Exhaustively validate serialized candidates using regex-parsed turns."""

    candidates = read_csv_rows(candidate_path)
    traces = read_csv_rows(trace_path)
    dispositions = read_csv_rows(disposition_path)
    errors: list[str] = []

    source_by_id = {
        str(row["sample_id"]): row for row in source_rows
    }
    candidate_ids = [
        str(row["benchmark_candidate_id"]) for row in candidates
    ]
    trace_ids = [str(row["benchmark_candidate_id"]) for row in traces]
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("duplicate_candidate_ids")
    if len(trace_ids) != len(set(trace_ids)):
        errors.append("duplicate_trace_ids")
    if set(candidate_ids) != set(trace_ids):
        errors.append("candidate_trace_id_set_mismatch")

    trace_by_id = {
        str(row["benchmark_candidate_id"]): row for row in traces
    }
    dispositions_by_id = {
        str(row["sample_id"]): row for row in dispositions
    }
    if set(dispositions_by_id) != set(source_by_id):
        errors.append("source_disposition_id_set_mismatch")

    candidates_by_sample: dict[str, list[dict[str, str]]] = defaultdict(
        list
    )
    for candidate in candidates:
        candidates_by_sample[str(candidate["sample_id"])].append(candidate)

    regex_parsed_source_count = 0
    trailing_student_source_count = 0
    exact_mapping_pass_count = 0
    for sample_id, source in sorted(source_by_id.items()):
        try:
            turns = parse_dialogue_turns(
                str(source["conversion_dialogue"])
            )
        except DialogueSplitError as exc:
            errors.append(f"{sample_id}:regex_turn_parse:{exc.code}")
            continue
        regex_parsed_source_count += 1
        trailing_student_source_count += turns[-1].role == "student"
        expected_target_indices = [
            turn.turn_index for turn in turns if turn.role == "tutor"
        ]
        expected_ids = {
            f"BC-{sample_id}-AI{turn_index:02d}"
            for turn_index in expected_target_indices
        }
        actual_family = candidates_by_sample.get(sample_id, [])
        actual_ids = {
            str(row["benchmark_candidate_id"]) for row in actual_family
        }
        if actual_ids != expected_ids:
            errors.append(f"{sample_id}:candidate_family_target_mismatch")

        disposition = dispositions_by_id.get(sample_id)
        if disposition is not None:
            if (
                disposition.get("conversion_disposition") != "converted"
            ):
                errors.append(f"{sample_id}:nonconverted_disposition")
            if disposition.get("candidate_count") != str(
                len(expected_target_indices)
            ):
                errors.append(f"{sample_id}:disposition_count_mismatch")

        for candidate in actual_family:
            candidate_id = str(candidate["benchmark_candidate_id"])
            trace = trace_by_id.get(candidate_id)
            if trace is None:
                continue
            try:
                target_index = int(trace["target_tutor_turn_index"])
                target = turns[target_index - 1]
                history = json.loads(candidate["conversation_history"])
            except (IndexError, ValueError, json.JSONDecodeError):
                errors.append(f"{candidate_id}:unreadable_target_or_history")
                continue
            expected_history = [
                {
                    "turn_index": turn.turn_index,
                    "role": turn.role,
                    "content": turn.content,
                }
                for turn in turns[1 : target_index - 1]
            ]
            expected_id = f"BC-{sample_id}-AI{target_index:02d}"
            exact = (
                target.role == "tutor"
                and candidate_id == expected_id
                and trace["sample_id"] == sample_id
                and trace["split_strategy"] == "each_tutor_turn"
                and trace["dialogue_correction_ids"]
                == source["dialogue_correction_ids"]
                and candidate["student_prompt"] == turns[0].content
                and history == expected_history
                and candidate["gold_response"] == target.content
                and candidate["gold_answer"] == source["answer_sgv"]
            )
            if exact:
                exact_mapping_pass_count += 1
            else:
                errors.append(f"{candidate_id}:exact_mapping_mismatch")

    return {
        "status": "pass" if not errors else "failed",
        "validation_method": (
            "TURN_PATTERN_regex_parse_and_exact_structural_comparison"
        ),
        "source_row_count": len(source_rows),
        "regex_parsed_source_count": regex_parsed_source_count,
        "trailing_student_source_count": trailing_student_source_count,
        "candidate_row_count": len(candidates),
        "trace_row_count": len(traces),
        "disposition_row_count": len(dispositions),
        "exact_mapping_pass_count": exact_mapping_pass_count,
        "failure_count": len(errors),
        "failure_examples": errors[:50],
    }


def _publish_failure_bundle(
    output_root: Path,
    *,
    errors: Sequence[Mapping[str, str]],
    failure_phase: str,
) -> None:
    """Publish a failed bundle without leaving prior candidate files visible."""

    staging_root = _create_staging_directory(output_root)
    try:
        write_csv_rows(
            staging_root / "dialogue_split_errors.csv",
            SPLIT_ERROR_COLUMNS,
            errors,
        )
        summary = {
            "run_status": "failed",
            "policy_id": PLAN02_POLICY_ID,
            "failure_phase": failure_phase,
            "blocking_error_count": len(errors),
        }
        (staging_root / "conversion_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        (staging_root / "run_status.json").write_text(
            json.dumps(
                {
                    "status": "failed",
                    "policy_id": PLAN02_POLICY_ID,
                    "failure_phase": failure_phase,
                    "candidate_bundle_published": False,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        _atomic_publish_directory(staging_root, output_root)
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)


def _write_multi_candidate_outputs(
    output_root: Path,
    *,
    source_rows: Sequence[Mapping[str, str]],
    source_path: Path,
    corrections_path: Path,
    candidates: Sequence[Mapping[str, str]],
    traces: Sequence[Mapping[str, str]],
    raw_summaries: Sequence[Mapping[str, str]],
    errors: Sequence[Mapping[str, str]],
    extra_summary: Mapping[str, object] | None = None,
    pilot_ids: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, object]:
    staging_root = _create_staging_directory(output_root)
    try:
        output_paths = {
            "benchmark_candidate_splits.csv": staging_root
            / "benchmark_candidate_splits.csv",
            "conversion_trace.csv": staging_root / "conversion_trace.csv",
            "conversion_dispositions.csv": staging_root
            / "conversion_dispositions.csv",
            "dialogue_split_errors.csv": staging_root
            / "dialogue_split_errors.csv",
        }
        write_csv_rows(
            output_paths["benchmark_candidate_splits.csv"],
            CANDIDATE_SPLIT_COLUMNS,
            candidates,
        )
        write_csv_rows(
            output_paths["conversion_trace.csv"], TRACE_COLUMNS, traces
        )
        write_csv_rows(
            output_paths["conversion_dispositions.csv"],
            CONVERSION_DISPOSITION_COLUMNS,
            raw_summaries,
        )
        write_csv_rows(
            output_paths["dialogue_split_errors.csv"],
            SPLIT_ERROR_COLUMNS,
            errors,
        )
        if pilot_ids is not None:
            output_paths["pilot_sample_ids.csv"] = (
                staging_root / "pilot_sample_ids.csv"
            )
            write_csv_rows(
                output_paths["pilot_sample_ids.csv"],
                MULTI_CANDIDATE_PILOT_ID_COLUMNS,
                pilot_ids,
            )

        mapping_validation = _validate_serialized_candidate_mapping(
            source_rows=source_rows,
            candidate_path=output_paths[
                "benchmark_candidate_splits.csv"
            ],
            trace_path=output_paths["conversion_trace.csv"],
            disposition_path=output_paths["conversion_dispositions.csv"],
        )
        if mapping_validation["status"] != "pass":
            raise ValueError(
                "Serialized candidate mapping validation failed: "
                f"{mapping_validation['failure_examples']}"
            )
        mapping_validation_path = (
            staging_root / "candidate_mapping_validation.json"
        )
        mapping_validation_path.write_text(
            json.dumps(
                mapping_validation,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        output_paths["candidate_mapping_validation.json"] = (
            mapping_validation_path
        )

        summary = {
            "run_status": "complete",
            "policy_id": PLAN02_POLICY_ID,
            "split_strategy": "each_tutor_turn",
            **_multi_candidate_statistics(candidates, raw_summaries),
            "blocking_error_count": len(errors),
            "corrected_sample_count": sum(
                json.loads(str(row["dialogue_correction_ids"])) != []
                for row in traces
                if str(row["target_tutor_turn_index"]) == "2"
            ),
            "input_path": str(source_path),
            "input_sha256": _sha256_file(source_path),
            "corrections_path": str(corrections_path),
            "corrections_sha256": _sha256_file(corrections_path),
            **dict(extra_summary or {}),
        }
        summary["file_sha256"] = {
            name: _sha256_file(path)
            for name, path in output_paths.items()
        }
        summary_path = staging_root / "conversion_summary.json"
        summary_path.write_text(
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        run_status = {
            "status": "complete",
            "policy_id": PLAN02_POLICY_ID,
            "candidate_bundle_published": True,
            "conversion_summary_sha256": _sha256_file(summary_path),
            "required_files": sorted(
                [*output_paths, "conversion_summary.json"]
            ),
        }
        (staging_root / "run_status.json").write_text(
            json.dumps(
                run_status,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        _atomic_publish_directory(staging_root, output_root)
        return {**summary, "output_root": str(output_root)}
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)


def run_multi_candidate_migration_pilot(
    experiment_root: Path,
    *,
    input_path: Path | None = None,
    corrections_path: Path | None = None,
    output_dir: Path | None = None,
    size_per_grade: int = 5,
) -> dict[str, object]:
    """Run the deterministic Plan-02 multi-candidate migration pilot."""

    conversion_root = experiment_root / "outputs" / "benchmark_conversion"
    source_path = input_path or (
        conversion_root / "conversion_input_pass_samples.csv"
    )
    correction_file = corrections_path or (
        conversion_root / "dialogue_corrections.csv"
    )
    output_root = output_dir or (
        conversion_root / "multi_candidate_migration_pilot"
    )
    source_rows = read_csv_rows(source_path)
    input_errors = _validate_multi_candidate_inputs(
        source_rows, corrections_path=correction_file
    )
    if input_errors:
        _publish_failure_bundle(
            output_root,
            errors=input_errors,
            failure_phase="input_validation",
        )
        raise ValueError(
            f"Plan-02 pilot input has {len(input_errors)} blocking errors"
        )
    selected, pilot_ids = select_multi_candidate_migration_pilot(
        source_rows, size_per_grade=size_per_grade
    )
    candidates, traces, raw_summaries, errors = (
        _build_multi_candidate_outputs(selected)
    )
    if errors:
        _publish_failure_bundle(
            output_root,
            errors=errors,
            failure_phase="candidate_build",
        )
        raise ValueError(
            f"Plan-02 migration pilot has {len(errors)} blocking errors"
        )
    try:
        return _write_multi_candidate_outputs(
            output_root,
            source_rows=selected,
            source_path=source_path,
            corrections_path=correction_file,
            candidates=candidates,
            traces=traces,
            raw_summaries=raw_summaries,
            errors=[],
            extra_summary={
                "pilot_size_per_grade": size_per_grade,
                "selected_raw_sample_count": len(selected),
                "selection_method": (
                    "deterministic_correction_and_candidate_count_strata_v1"
                ),
            },
            pilot_ids=pilot_ids,
        )
    except Exception as exc:
        publish_errors = [
            {
                "sample_id": "",
                "source_batch": "",
                "severity": "blocking",
                "error_code": "pilot_publish_validation_failed",
                "message": str(exc),
            }
        ]
        _publish_failure_bundle(
            output_root,
            errors=publish_errors,
            failure_phase="serialized_mapping_or_publish",
        )
        raise


def run_full_multi_candidate_conversion(
    experiment_root: Path,
    *,
    input_path: Path | None = None,
    corrections_path: Path | None = None,
    output_dir: Path | None = None,
    enforce_plan02_baseline: bool = True,
) -> dict[str, object]:
    """Convert all Plan-02 inputs after validating the approved contract."""

    conversion_root = experiment_root / "outputs" / "benchmark_conversion"
    source_path = input_path or (
        conversion_root / "conversion_input_pass_samples.csv"
    )
    correction_file = corrections_path or (
        conversion_root / "dialogue_corrections.csv"
    )
    output_root = output_dir or (conversion_root / "full_v0")
    source_rows = read_csv_rows(source_path)
    input_errors = _validate_multi_candidate_inputs(
        source_rows, corrections_path=correction_file
    )
    if input_errors:
        _publish_failure_bundle(
            output_root,
            errors=input_errors,
            failure_phase="input_validation",
        )
        raise ValueError(
            f"Plan-02 full input has {len(input_errors)} blocking errors"
        )
    candidates, traces, raw_summaries, errors = (
        _build_multi_candidate_outputs(source_rows)
    )
    if errors:
        _publish_failure_bundle(
            output_root,
            errors=errors,
            failure_phase="candidate_build",
        )
        raise ValueError(
            f"Plan-02 full conversion has {len(errors)} blocking errors"
        )
    statistics = _multi_candidate_statistics(candidates, raw_summaries)
    try:
        if enforce_plan02_baseline:
            _validate_plan02_baseline(statistics)
        return _write_multi_candidate_outputs(
            output_root,
            source_rows=source_rows,
            source_path=source_path,
            corrections_path=correction_file,
            candidates=candidates,
            traces=traces,
            raw_summaries=raw_summaries,
            errors=[],
            extra_summary={
                "baseline_enforced": enforce_plan02_baseline,
            },
        )
    except Exception as exc:
        publish_errors = [
            {
                "sample_id": "",
                "source_batch": "",
                "severity": "blocking",
                "error_code": "full_publish_validation_failed",
                "message": str(exc),
            }
        ]
        _publish_failure_bundle(
            output_root,
            errors=publish_errors,
            failure_phase="baseline_serialized_mapping_or_publish",
        )
        raise

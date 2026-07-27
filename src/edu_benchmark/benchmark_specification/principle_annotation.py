"""Unordered-set annotation tooling for Plan 03 pedagogical principles."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .manifest import sha256_file

CONTEXT_INPUT_COLUMNS = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
)
GROUNDING_INPUT_COLUMNS = CONTEXT_INPUT_COLUMNS + (
    "source_question",
    "gold_answer",
)
CANDIDATE_ANNOTATION_COLUMNS = (
    "benchmark_candidate_id",
    "sample_id",
    "student_state_summary",
    "coverage_gap_reason",
    "grounding_effect",
    "grounding_change_reason",
    "coder_id",
    "review_status",
    "adjudication_status",
)
PRINCIPLE_LABEL_COLUMNS = (
    "benchmark_candidate_id",
    "principle_id",
    "selection_rationale",
    "context_evidence",
    "grounding_evidence",
    "coder_id",
    "review_status",
)
REVIEW_QUEUE_COLUMNS = (
    "benchmark_candidate_id",
    "sample_id",
    "coder_id",
    "review_reason_codes",
    "context_principle_set",
    "final_principle_set",
    "context_coverage_gap_reason",
    "final_coverage_gap_reason",
    "grounding_change_reason",
    "suggested_reviewer_action",
)
PRINCIPLE_IDS = frozenset(
    {
        "PRINCIPLE-CHALLENGE",
        "PRINCIPLE-EXPLANATION",
        "PRINCIPLE-MODELLING",
        "PRINCIPLE-PRACTICE",
        "PRINCIPLE-FEEDBACK",
        "PRINCIPLE-QUESTIONING",
    }
)
CANONICAL_DOCUMENTS = (
    "experiments/20260722_000940/outputs/benchmark_specification/task_discovery/pedagogical_principles.csv",
    "experiments/20260722_000940/outputs/benchmark_specification/task_discovery/task_discovery_codebook.md",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capabilities.csv",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capability_model.md",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/capability_overlap_matrix.csv",
)
RUNTIME_DOCUMENTS = (
    "agents/pedagogical-principle-annotator/SKILL.md",
    "agents/pedagogical-principle-annotator/references/two_pass_annotation_contract.md",
    "experiments/20260722_000940/outputs/benchmark_specification/task_discovery/pedagogical_principles.csv",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capabilities.csv",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/capability_overlap_matrix.csv",
)
ALLOWED_GROUNDING_EFFECTS = frozenset({"unchanged", "changed", "conflict"})
ALLOWED_REVIEW_REASONS = frozenset(
    {
        "label_set_changed",
        "coverage_decision_changed",
        "context_grounding_conflict",
        "coverage_gap",
        "high_label_count",
        "principle_boundary_ambiguous",
        "codebook_clarification_proposed",
    }
)
THRESHOLD_KEYS = (
    "exact_set_agreement_min",
    "mean_jaccard_min",
    "minimum_per_principle_f1",
    "coverage_gap_agreement_min",
    "grounding_effect_agreement_min",
)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader.fieldnames), [dict(row) for row in reader]


def _write_csv(
    path: Path,
    columns: Sequence[str],
    rows: Iterable[Mapping[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _relative(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(repo_root.resolve()))
    except ValueError:
        return str(resolved)


def _require_columns(
    path: Path, header: Sequence[str], required: Sequence[str]
) -> None:
    missing = sorted(set(required) - set(header))
    if missing:
        raise ValueError(f"{path}: missing required columns: {missing}")


def _ordered_ids(rows: Sequence[Mapping[str, str]]) -> list[tuple[str, str]]:
    ids = [
        (row["benchmark_candidate_id"].strip(), row["sample_id"].strip())
        for row in rows
    ]
    if any(not candidate_id or not sample_id for candidate_id, sample_id in ids):
        raise ValueError("Candidate and sample IDs must be non-empty")
    candidate_ids = [candidate_id for candidate_id, _ in ids]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Duplicate benchmark_candidate_id")
    return ids


def _ordered_id_sha256(ids: Sequence[tuple[str, str]]) -> str:
    payload = "\n".join(
        f"{candidate_id}\t{sample_id}" for candidate_id, sample_id in ids
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _document_records(
    repo_root: Path, relative_paths: Sequence[str]
) -> list[dict[str, object]]:
    records = []
    for relative in relative_paths:
        path = repo_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append(
            {
                "path": relative,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return records


def _select_rows(
    rows: Sequence[dict[str, str]],
    *,
    selection_path: Path | None,
    per_grade: int | None,
) -> list[dict[str, str]]:
    if selection_path is None:
        selected = list(rows)
    else:
        selection_header, selection_rows = _read_csv(selection_path)
        _require_columns(
            selection_path,
            selection_header,
            ("benchmark_candidate_id", "sample_id", "grade"),
        )
        by_id = {row["benchmark_candidate_id"]: row for row in rows}
        if len(by_id) != len(rows):
            raise ValueError("Grounding input contains duplicate benchmark_candidate_id")
        selected = []
        grade_counts: Counter[str] = Counter()
        for selection in selection_rows:
            grade = selection["grade"].strip()
            if per_grade is not None and grade_counts[grade] >= per_grade:
                continue
            candidate_id = selection["benchmark_candidate_id"].strip()
            row = by_id.get(candidate_id)
            if row is None:
                raise ValueError(
                    f"Selection candidate is missing from grounding input: {candidate_id}"
                )
            if (
                row["sample_id"].strip() != selection["sample_id"].strip()
                or row["grade"].strip() != grade
            ):
                raise ValueError(f"Selection identity mismatch: {candidate_id}")
            selected.append(row)
            grade_counts[grade] += 1
        if per_grade is not None:
            expected_grades = ("6", "7", "8", "9")
            actual = {grade: grade_counts[grade] for grade in expected_grades}
            if actual != {grade: per_grade for grade in expected_grades}:
                raise ValueError(
                    f"Expected {per_grade} candidates per grade 6-9, found {actual}"
                )
    _ordered_ids(selected)
    sample_ids = [row["sample_id"] for row in selected]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Pilot selection must use distinct source sample_id values")
    return selected


def build_annotation_inputs(
    *,
    repo_root: Path,
    grounding_input_path: Path,
    output_dir: Path,
    selection_path: Path | None = None,
    per_grade: int | None = None,
    created_at: str | None = None,
) -> dict[str, object]:
    """Build physically isolated context and grounding views for schema v3."""

    header, rows = _read_csv(grounding_input_path)
    _require_columns(grounding_input_path, header, GROUNDING_INPUT_COLUMNS)
    if "gold_response" in header:
        raise ValueError("Grounding source must not contain gold_response")
    selected = _select_rows(
        rows,
        selection_path=selection_path,
        per_grade=per_grade,
    )
    ids = _ordered_ids(selected)
    context_rows = [
        {column: row[column] for column in CONTEXT_INPUT_COLUMNS}
        for row in selected
    ]
    grounding_rows = [
        {column: row[column] for column in GROUNDING_INPUT_COLUMNS}
        for row in selected
    ]
    if any(not row["source_question"].strip() for row in grounding_rows):
        raise ValueError("Grounding input contains an empty source_question")

    context_path = output_dir / "principle_annotation_pass1_input.csv"
    grounding_path = output_dir / "principle_annotation_grounding_input.csv"
    manifest_path = output_dir / "principle_annotation_grounding_manifest.json"
    _write_csv(context_path, CONTEXT_INPUT_COLUMNS, context_rows)
    _write_csv(grounding_path, GROUNDING_INPUT_COLUMNS, grounding_rows)

    stable_created_at = created_at
    if stable_created_at is None and manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("manifest_version") == "plan03-principle-grounding-v3":
            stable_created_at = previous.get("created_at")

    manifest = {
        "manifest_version": "plan03-principle-grounding-v3",
        "created_at": stable_created_at or datetime.now().astimezone().isoformat(),
        "grounding_pool": {
            "path": _relative(grounding_input_path, repo_root),
            "sha256": sha256_file(grounding_input_path),
        },
        "selection": (
            {
                "path": _relative(selection_path, repo_root),
                "sha256": sha256_file(selection_path),
                "per_grade": per_grade,
            }
            if selection_path is not None
            else None
        ),
        "batch": {
            "size": len(selected),
            "ordered_id_sha256": _ordered_id_sha256(ids),
            "grade_counts": dict(
                sorted(Counter(row["grade"] for row in selected).items())
            ),
            "unique_sample_count": len({row["sample_id"] for row in selected}),
        },
        "views": {
            "context": {
                "path": _relative(context_path, repo_root),
                "sha256": sha256_file(context_path),
                "columns": list(CONTEXT_INPUT_COLUMNS),
            },
            "grounding": {
                "path": _relative(grounding_path, repo_root),
                "sha256": sha256_file(grounding_path),
                "columns": list(GROUNDING_INPUT_COLUMNS),
                "gold_response_excluded": True,
            },
        },
        "canonical_documents": _document_records(
            repo_root, CANONICAL_DOCUMENTS
        ),
        "runtime_documents": _document_records(repo_root, RUNTIME_DOCUMENTS),
        "pilot_policy": {
            "model": "gpt-5.4-mini",
            "reasoning_effort": "medium",
            "instance_count": 2,
            "label_structure": "unordered_set",
            "hard_label_limit": None,
            "mandatory_review_above": 3,
            "review_status": "needs_uet_review",
        },
    }
    _write_json(manifest_path, manifest)
    return {
        "candidate_count": len(selected),
        "ordered_id_sha256": _ordered_id_sha256(ids),
        "grade_counts": manifest["batch"]["grade_counts"],
        "manifest_path": str(manifest_path),
    }


def validate_input_pair(
    *,
    repo_root: Path,
    context_path: Path,
    grounding_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    """Validate v3 field isolation, ordered IDs, hashes, and locked documents."""

    context_header, context_rows = _read_csv(context_path)
    grounding_header, grounding_rows = _read_csv(grounding_path)
    if tuple(context_header) != CONTEXT_INPUT_COLUMNS:
        raise ValueError(f"Invalid context header: {context_header}")
    if tuple(grounding_header) != GROUNDING_INPUT_COLUMNS:
        raise ValueError(f"Invalid grounding header: {grounding_header}")
    if {"gold_response", "gold_answer", "source_question"} & set(context_header):
        raise ValueError("Context input leaks grounding or response fields")
    if "gold_response" in grounding_header:
        raise ValueError("Grounding input leaks gold_response")
    context_ids = _ordered_ids(context_rows)
    grounding_ids = _ordered_ids(grounding_rows)
    if context_ids != grounding_ids:
        raise ValueError("Context and grounding ordered ID sets differ")
    if any(not row["source_question"].strip() for row in grounding_rows):
        raise ValueError("Grounding input contains an empty source_question")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != "plan03-principle-grounding-v3":
        raise ValueError("Unexpected grounding manifest version")
    views = manifest.get("views", {})
    if views.get("context", {}).get("sha256") != sha256_file(context_path):
        raise ValueError("Context hash mismatch")
    if views.get("grounding", {}).get("sha256") != sha256_file(grounding_path):
        raise ValueError("Grounding hash mismatch")
    if views.get("grounding", {}).get("gold_response_excluded") is not True:
        raise ValueError("Grounding manifest must record gold_response exclusion")
    if manifest.get("batch", {}).get("ordered_id_sha256") != _ordered_id_sha256(
        context_ids
    ):
        raise ValueError("Ordered ID hash mismatch")
    for key, expected in (
        ("canonical_documents", CANONICAL_DOCUMENTS),
        ("runtime_documents", RUNTIME_DOCUMENTS),
    ):
        records = manifest.get(key, [])
        if [item.get("path") for item in records] != list(expected):
            raise ValueError(f"{key} paths differ from the contract")
        for item in records:
            path = repo_root / item["path"]
            if not path.is_file() or sha256_file(path) != item.get("sha256"):
                raise ValueError(f"Locked document hash mismatch: {item['path']}")
    return {
        "status": "passed",
        "candidate_count": len(context_rows),
        "ordered_id_sha256": _ordered_id_sha256(context_ids),
    }


def _read_phase(
    bundle_dir: Path, phase: str
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    metadata_path = bundle_dir / f"principle_annotation_{phase}.csv"
    labels_path = bundle_dir / f"principle_annotation_{phase}_labels.csv"
    metadata_header, metadata_rows = _read_csv(metadata_path)
    label_header, label_rows = _read_csv(labels_path)
    if tuple(metadata_header) != CANDIDATE_ANNOTATION_COLUMNS:
        raise ValueError(f"{phase} candidate annotation header mismatch")
    if tuple(label_header) != PRINCIPLE_LABEL_COLUMNS:
        raise ValueError(f"{phase} principle label header mismatch")
    return metadata_rows, label_rows


def _validate_phase(
    *,
    metadata_rows: Sequence[dict[str, str]],
    label_rows: Sequence[dict[str, str]],
    expected_ids: Sequence[tuple[str, str]],
    coder_id: str,
    context_phase: bool,
) -> tuple[dict[str, set[str]], dict[str, dict[str, str]]]:
    if _ordered_ids(metadata_rows) != list(expected_ids):
        raise ValueError("Annotation candidate IDs differ from input")
    metadata_by_id = {
        row["benchmark_candidate_id"]: row for row in metadata_rows
    }
    labels_by_id = {candidate_id: set() for candidate_id, _ in expected_ids}
    seen_pairs: set[tuple[str, str]] = set()
    for row in label_rows:
        candidate_id = row["benchmark_candidate_id"].strip()
        principle_id = row["principle_id"].strip()
        if candidate_id not in metadata_by_id:
            raise ValueError(f"Unknown label candidate: {candidate_id}")
        if principle_id not in PRINCIPLE_IDS:
            raise ValueError(f"{candidate_id}: unknown principle {principle_id}")
        pair = (candidate_id, principle_id)
        if pair in seen_pairs:
            raise ValueError(f"Duplicate candidate-principle pair: {pair}")
        seen_pairs.add(pair)
        labels_by_id[candidate_id].add(principle_id)
        if not row["selection_rationale"].strip():
            raise ValueError(f"{candidate_id}: selection_rationale is required")
        if not row["context_evidence"].strip():
            raise ValueError(f"{candidate_id}: context_evidence is required")
        if context_phase and row["grounding_evidence"].strip():
            raise ValueError(f"{candidate_id}: context phase cannot use grounding evidence")
        if (
            row["coder_id"] != coder_id
            or row["review_status"] != "needs_uet_review"
        ):
            raise ValueError(f"{candidate_id}: invalid label authority/status")

    for candidate_id, sample_id in expected_ids:
        row = metadata_by_id[candidate_id]
        if row["sample_id"] != sample_id:
            raise ValueError(f"{candidate_id}: sample_id mismatch")
        if not row["student_state_summary"].strip():
            raise ValueError(f"{candidate_id}: student_state_summary is required")
        if (
            row["coder_id"] != coder_id
            or row["review_status"] != "needs_uet_review"
            or row["adjudication_status"].strip()
        ):
            raise ValueError(f"{candidate_id}: AI output cannot be confirmed")
        label_set = labels_by_id[candidate_id]
        gap = row["coverage_gap_reason"].strip()
        if bool(label_set) == bool(gap):
            raise ValueError(
                f"{candidate_id}: exactly one of principle set and coverage gap is required"
            )
        if context_phase:
            if (
                row["grounding_effect"] != "not_seen"
                or row["grounding_change_reason"].strip()
            ):
                raise ValueError(f"{candidate_id}: context phase cannot use grounding")
        elif row["grounding_effect"] not in ALLOWED_GROUNDING_EFFECTS:
            raise ValueError(f"{candidate_id}: invalid grounding_effect")
    return labels_by_id, metadata_by_id


def derive_grounding_effect(
    context_set: set[str],
    final_set: set[str],
    *,
    context_gap: bool,
    final_gap: bool,
    context_grounding_conflict: bool = False,
) -> str:
    """Derive changed/unchanged; retain semantic conflict only for a stable decision."""

    if context_set != final_set or context_gap != final_gap:
        return "changed"
    return "conflict" if context_grounding_conflict else "unchanged"


def _set_text(values: set[str]) -> str:
    return ";".join(sorted(values))


def reconcile_annotation_draft(
    *, bundle_dir: Path, coder_id: str
) -> dict[str, object]:
    """Derive grounding effects and mandatory v3 review rows."""

    context_metadata, context_labels = _read_phase(bundle_dir, "pass1")
    final_metadata, final_labels = _read_phase(bundle_dir, "final")
    expected_ids = _ordered_ids(context_metadata)
    context_sets, context_by_id = _validate_phase(
        metadata_rows=context_metadata,
        label_rows=context_labels,
        expected_ids=expected_ids,
        coder_id=coder_id,
        context_phase=True,
    )
    final_sets, final_by_id = _validate_phase(
        metadata_rows=final_metadata,
        label_rows=final_labels,
        expected_ids=expected_ids,
        coder_id=coder_id,
        context_phase=False,
    )
    queue_path = bundle_dir / "principle_annotation_review_queue.csv"
    queue_header, queue_rows = _read_csv(queue_path)
    if tuple(queue_header) != REVIEW_QUEUE_COLUMNS:
        raise ValueError("Review queue header mismatch")
    queue_by_id = {row["benchmark_candidate_id"]: row for row in queue_rows}
    if len(queue_by_id) != len(queue_rows):
        raise ValueError("Duplicate review queue row")

    changed_count = conflict_count = 0
    for candidate_id, _ in expected_ids:
        before = context_by_id[candidate_id]
        after = final_by_id[candidate_id]
        declared_conflict = after["grounding_effect"] == "conflict"
        effect = derive_grounding_effect(
            context_sets[candidate_id],
            final_sets[candidate_id],
            context_gap=bool(before["coverage_gap_reason"].strip()),
            final_gap=bool(after["coverage_gap_reason"].strip()),
            context_grounding_conflict=declared_conflict,
        )
        after["grounding_effect"] = effect
        if effect == "changed":
            changed_count += 1
            if not after["grounding_change_reason"].strip():
                after["grounding_change_reason"] = (
                    "Code phát hiện tập nguyên tắc hoặc quyết định khoảng trống thay "
                    "đổi giữa vòng context và vòng grounding."
                )
        elif effect == "unchanged":
            after["grounding_change_reason"] = ""
        else:
            conflict_count += 1
            if not after["grounding_change_reason"].strip():
                raise ValueError(f"{candidate_id}: conflict requires a semantic reason")

        reasons: set[str] = set()
        if context_sets[candidate_id] != final_sets[candidate_id]:
            reasons.add("label_set_changed")
        if bool(before["coverage_gap_reason"].strip()) != bool(
            after["coverage_gap_reason"].strip()
        ):
            reasons.add("coverage_decision_changed")
        if effect == "conflict":
            reasons.add("context_grounding_conflict")
        if after["coverage_gap_reason"].strip():
            reasons.add("coverage_gap")
        if len(final_sets[candidate_id]) > 3:
            reasons.add("high_label_count")
        if not reasons:
            continue

        row = queue_by_id.get(candidate_id)
        if row is None:
            row = {column: "" for column in REVIEW_QUEUE_COLUMNS}
            row.update(
                {
                    "benchmark_candidate_id": candidate_id,
                    "sample_id": after["sample_id"],
                    "coder_id": coder_id,
                    "suggested_reviewer_action": (
                        "UET rà tập nguyên tắc và căn cứ context/grounding."
                    ),
                }
            )
            queue_by_id[candidate_id] = row
        existing = {
            code for code in row["review_reason_codes"].split(";") if code
        }
        row.update(
            {
                "review_reason_codes": ";".join(sorted(existing | reasons)),
                "context_principle_set": _set_text(context_sets[candidate_id]),
                "final_principle_set": _set_text(final_sets[candidate_id]),
                "context_coverage_gap_reason": before["coverage_gap_reason"],
                "final_coverage_gap_reason": after["coverage_gap_reason"],
                "grounding_change_reason": after["grounding_change_reason"],
            }
        )

    ordered_queue = [
        queue_by_id[candidate_id]
        for candidate_id, _ in expected_ids
        if candidate_id in queue_by_id
    ]
    _write_csv(
        bundle_dir / "principle_annotation_final.csv",
        CANDIDATE_ANNOTATION_COLUMNS,
        final_metadata,
    )
    _write_csv(queue_path, REVIEW_QUEUE_COLUMNS, ordered_queue)
    return {
        "candidate_count": len(expected_ids),
        "review_queue_count": len(ordered_queue),
        "changed_count": changed_count,
        "conflict_count": conflict_count,
    }


def validate_annotation_bundle(
    *, input_dir: Path, bundle_dir: Path, coder_id: str
) -> dict[str, object]:
    """Fail closed on one schema-v3 annotator bundle."""

    _, expected_input = _read_csv(
        input_dir / "principle_annotation_pass1_input.csv"
    )
    expected_ids = _ordered_ids(expected_input)
    context_metadata, context_labels = _read_phase(bundle_dir, "pass1")
    final_metadata, final_labels = _read_phase(bundle_dir, "final")
    context_sets, context_by_id = _validate_phase(
        metadata_rows=context_metadata,
        label_rows=context_labels,
        expected_ids=expected_ids,
        coder_id=coder_id,
        context_phase=True,
    )
    final_sets, final_by_id = _validate_phase(
        metadata_rows=final_metadata,
        label_rows=final_labels,
        expected_ids=expected_ids,
        coder_id=coder_id,
        context_phase=False,
    )
    queue_header, queue_rows = _read_csv(
        bundle_dir / "principle_annotation_review_queue.csv"
    )
    if tuple(queue_header) != REVIEW_QUEUE_COLUMNS:
        raise ValueError("Review queue header mismatch")
    queue_ids: set[str] = set()
    for row in queue_rows:
        candidate_id = row["benchmark_candidate_id"]
        if (
            candidate_id not in final_by_id
            or row["sample_id"] != final_by_id[candidate_id]["sample_id"]
            or row["coder_id"] != coder_id
        ):
            raise ValueError(f"Invalid review queue identity: {candidate_id}")
        reasons = {
            code for code in row["review_reason_codes"].split(";") if code
        }
        if not reasons or not reasons <= ALLOWED_REVIEW_REASONS:
            raise ValueError(f"Invalid review reason codes: {candidate_id}")
        if candidate_id in queue_ids:
            raise ValueError(f"Duplicate review queue row: {candidate_id}")
        queue_ids.add(candidate_id)

    required_queue: set[str] = set()
    for candidate_id, _ in expected_ids:
        before = context_by_id[candidate_id]
        after = final_by_id[candidate_id]
        expected_effect = derive_grounding_effect(
            context_sets[candidate_id],
            final_sets[candidate_id],
            context_gap=bool(before["coverage_gap_reason"].strip()),
            final_gap=bool(after["coverage_gap_reason"].strip()),
            context_grounding_conflict=after["grounding_effect"] == "conflict",
        )
        if after["grounding_effect"] != expected_effect:
            raise ValueError(
                f"{candidate_id}: grounding_effect must be derived as {expected_effect}"
            )
        if (
            after["grounding_effect"] in {"changed", "conflict"}
            and not after["grounding_change_reason"].strip()
        ):
            raise ValueError(f"{candidate_id}: grounding change reason is required")
        if (
            context_sets[candidate_id] != final_sets[candidate_id]
            or bool(before["coverage_gap_reason"].strip())
            != bool(after["coverage_gap_reason"].strip())
            or after["grounding_effect"] == "conflict"
            or after["coverage_gap_reason"].strip()
            or len(final_sets[candidate_id]) > 3
        ):
            required_queue.add(candidate_id)
    missing = sorted(required_queue - queue_ids)
    if missing:
        raise ValueError(f"Required review queue rows missing: {missing}")

    manifest_path = bundle_dir / "principle_annotation_run_manifest.json"
    handoff_path = bundle_dir / "handoff.md"
    if not manifest_path.is_file() or not handoff_path.is_file():
        raise ValueError("Run manifest and handoff are required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("manifest_version")
        != "plan03-principle-annotation-run-v3"
        or manifest.get("coder_id") != coder_id
        or manifest.get("candidate_count") != len(expected_ids)
        or manifest.get("closed") is not True
    ):
        raise ValueError("Run manifest identity/count/closed state is invalid")
    if (
        manifest.get("model") != "gpt-5.4-mini"
        or manifest.get("reasoning_effort") != "medium"
    ):
        raise ValueError("Run manifest model configuration mismatch")
    input_manifest = input_dir / "principle_annotation_grounding_manifest.json"
    if manifest.get("input_manifest_sha256") != sha256_file(input_manifest):
        raise ValueError("Run manifest input hash mismatch")
    return {
        "status": "passed",
        "candidate_count": len(expected_ids),
        "review_queue_count": len(queue_rows),
        "changed_count": sum(
            row["grounding_effect"] == "changed" for row in final_metadata
        ),
        "conflict_count": sum(
            row["grounding_effect"] == "conflict" for row in final_metadata
        ),
        "coverage_gap_count": sum(
            bool(row["coverage_gap_reason"].strip()) for row in final_metadata
        ),
        "high_label_count": sum(
            len(final_sets[candidate_id]) > 3 for candidate_id, _ in expected_ids
        ),
    }


def validate_thresholds(path: Path) -> dict[str, object]:
    """Require UET pre-registration before any dual specialist run."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if (
        data.get("status") != "uet_approved"
        or not data.get("approved_by")
        or not data.get("approved_at")
        or data.get("schema_version") != "unordered-set-v3"
    ):
        raise ValueError("UET v3 thresholds have not been approved before the run")
    for key in THRESHOLD_KEYS:
        value = data.get(key)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0 <= float(value) <= 1
        ):
            raise ValueError(f"Invalid threshold: {key}")
    return data


def _principle_metrics(
    sets_a: Mapping[str, set[str]],
    sets_b: Mapping[str, set[str]],
) -> list[dict[str, object]]:
    rows = []
    for principle_id in sorted(PRINCIPLE_IDS):
        tp = sum(
            principle_id in sets_a[candidate_id]
            and principle_id in sets_b[candidate_id]
            for candidate_id in sets_a
        )
        a_only = sum(
            principle_id in sets_a[candidate_id]
            and principle_id not in sets_b[candidate_id]
            for candidate_id in sets_a
        )
        b_only = sum(
            principle_id not in sets_a[candidate_id]
            and principle_id in sets_b[candidate_id]
            for candidate_id in sets_a
        )
        precision = tp / (tp + b_only) if tp + b_only else 1.0
        recall = tp / (tp + a_only) if tp + a_only else 1.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        rows.append(
            {
                "principle_id": principle_id,
                "both_selected": tp,
                "annotator_a_only": a_only,
                "annotator_b_only": b_only,
                "annotator_b_vs_a_precision": f"{precision:.6f}",
                "annotator_b_vs_a_recall": f"{recall:.6f}",
                "symmetric_f1": f"{f1:.6f}",
            }
        )
    return rows


def compare_annotation_bundles(
    *,
    bundle_a: Path,
    bundle_b: Path,
    thresholds_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    """Compare two closed unordered-set bundles deterministically."""

    thresholds = validate_thresholds(thresholds_path)
    input_dir_a = bundle_a.resolve().parent.parent
    input_dir_b = bundle_b.resolve().parent.parent
    if input_dir_a != input_dir_b:
        raise ValueError("Dual-run bundles do not share one input directory")
    manifest_a = json.loads(
        (bundle_a / "principle_annotation_run_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    manifest_b = json.loads(
        (bundle_b / "principle_annotation_run_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    validate_annotation_bundle(
        input_dir=input_dir_a,
        bundle_dir=bundle_a,
        coder_id=str(manifest_a.get("coder_id", "")),
    )
    validate_annotation_bundle(
        input_dir=input_dir_a,
        bundle_dir=bundle_b,
        coder_id=str(manifest_b.get("coder_id", "")),
    )
    metadata_a, labels_a = _read_phase(bundle_a, "final")
    metadata_b, labels_b = _read_phase(bundle_b, "final")
    ids_a = _ordered_ids(metadata_a)
    if ids_a != _ordered_ids(metadata_b):
        raise ValueError("Dual-run candidate IDs differ")
    by_a = {row["benchmark_candidate_id"]: row for row in metadata_a}
    by_b = {row["benchmark_candidate_id"]: row for row in metadata_b}
    sets_a = {candidate_id: set() for candidate_id, _ in ids_a}
    sets_b = {candidate_id: set() for candidate_id, _ in ids_a}
    for row in labels_a:
        sets_a[row["benchmark_candidate_id"]].add(row["principle_id"])
    for row in labels_b:
        sets_b[row["benchmark_candidate_id"]].add(row["principle_id"])

    exact_hits = gap_hits = grounding_hits = 0
    jaccards: list[float] = []
    comparison = []
    for candidate_id, sample_id in ids_a:
        set_a, set_b = sets_a[candidate_id], sets_b[candidate_id]
        exact = set_a == set_b
        union = set_a | set_b
        jaccard = 1.0 if not union else len(set_a & set_b) / len(union)
        gap_equal = bool(by_a[candidate_id]["coverage_gap_reason"].strip()) == bool(
            by_b[candidate_id]["coverage_gap_reason"].strip()
        )
        grounding_equal = (
            by_a[candidate_id]["grounding_effect"]
            == by_b[candidate_id]["grounding_effect"]
        )
        exact_hits += exact
        gap_hits += gap_equal
        grounding_hits += grounding_equal
        jaccards.append(jaccard)
        requires_review = (
            not exact
            or not gap_equal
            or not grounding_equal
            or bool(by_a[candidate_id]["coverage_gap_reason"].strip())
            or bool(by_b[candidate_id]["coverage_gap_reason"].strip())
            or len(set_a) > 3
            or len(set_b) > 3
        )
        comparison.append(
            {
                "benchmark_candidate_id": candidate_id,
                "sample_id": sample_id,
                "annotator_a_principle_set": _set_text(set_a),
                "annotator_b_principle_set": _set_text(set_b),
                "exact_set_match": str(exact).lower(),
                "label_set_jaccard": f"{jaccard:.6f}",
                "coverage_gap_match": str(gap_equal).lower(),
                "grounding_effect_match": str(grounding_equal).lower(),
                "annotator_a_only": _set_text(set_a - set_b),
                "annotator_b_only": _set_text(set_b - set_a),
                "requires_uet_review": str(requires_review).lower(),
            }
        )
    count = len(ids_a)
    principle_rows = _principle_metrics(sets_a, sets_b)
    min_f1 = min(float(row["symmetric_f1"]) for row in principle_rows)
    metrics = {
        "exact_set_agreement": exact_hits / count,
        "mean_jaccard": sum(jaccards) / count,
        "minimum_per_principle_f1": min_f1,
        "coverage_gap_agreement": gap_hits / count,
        "grounding_effect_agreement": grounding_hits / count,
    }
    gate_map = {
        "exact_set_agreement": "exact_set_agreement_min",
        "mean_jaccard": "mean_jaccard_min",
        "minimum_per_principle_f1": "minimum_per_principle_f1",
        "coverage_gap_agreement": "coverage_gap_agreement_min",
        "grounding_effect_agreement": "grounding_effect_agreement_min",
    }
    passed = all(
        metrics[metric] >= float(thresholds[threshold])
        for metric, threshold in gate_map.items()
    )
    _write_csv(
        output_dir / "dual_run_comparison.csv",
        tuple(comparison[0]) if comparison else (),
        comparison,
    )
    _write_csv(
        output_dir / "dual_run_principle_metrics.csv",
        (
            "principle_id",
            "both_selected",
            "annotator_a_only",
            "annotator_b_only",
            "annotator_b_vs_a_precision",
            "annotator_b_vs_a_recall",
            "symmetric_f1",
        ),
        principle_rows,
    )
    summary = {
        "summary_version": "plan03-dual-run-reproducibility-v3",
        "candidate_count": count,
        "interpretation": (
            "AI inter-instance reproducibility; not human inter-rater reliability"
        ),
        "metrics": metrics,
        "pre_registered_thresholds": {
            key: thresholds[key] for key in THRESHOLD_KEYS
        },
        "gate_status": "passed" if passed else "failed",
        "bundle_hashes": {
            "annotator_a_final": sha256_file(
                bundle_a / "principle_annotation_final.csv"
            ),
            "annotator_a_final_labels": sha256_file(
                bundle_a / "principle_annotation_final_labels.csv"
            ),
            "annotator_b_final": sha256_file(
                bundle_b / "principle_annotation_final.csv"
            ),
            "annotator_b_final_labels": sha256_file(
                bundle_b / "principle_annotation_final_labels.csv"
            ),
        },
    }
    _write_json(output_dir / "dual_run_reproducibility_summary.json", summary)
    return summary

"""File-oriented orchestration for Plan-01 benchmark conversion."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .corrections import load_dialogue_corrections
from .dialogue_split import DialogueSplitError, parse_dialogue_turns, split_final_tutor_response_candidate
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
    SPLIT_ERROR_COLUMNS,
    TRACE_COLUMNS,
    validate_candidate_split_row,
    validate_conversion_input_row,
)

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
            parse_dialogue_turns(row["conversion_dialogue"])
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
        CANDIDATE_SPLIT_COLUMNS,
        candidates,
    )
    write_csv_rows(output_root / "conversion_trace.csv", TRACE_COLUMNS, traces)
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

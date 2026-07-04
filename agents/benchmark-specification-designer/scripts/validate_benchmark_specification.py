#!/usr/bin/env python3
"""Validate v0 benchmark task, rubric, serious-error, and provenance CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ALLOWED_STATUS = {"draft", "needs_uet_review", "needs_hnmu_review", "confirmed", "retired"}
REVIEW_STATUSES = {"needs_uet_review", "needs_hnmu_review", "draft"}
TASK_COLUMNS = (
    "task_id",
    "task_name",
    "definition",
    "scope",
    "input_requirements",
    "output_requirements",
    "status",
    "research_ids",
    "learning_material_ids",
    "teacher_decision_needed",
)
RUBRIC_COLUMNS = ("rubric_id", "task_id", "criterion", "observable_evidence", "score_levels", "status")
ERROR_COLUMNS = ("error_id", "description", "suggested_action", "affected_rubric_ids", "status")
PROVENANCE_COLUMNS = ("item_id", "item_type", "research_ids", "learning_material_ids", "rationale", "status")
ITEM_TYPES = {"task", "rubric", "serious_error"}


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], list[str]]:
    if not path.is_file():
        return [], [], [f"File not found: {path}"]
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader), []


def _split_ids(value: str) -> list[str]:
    return [part.strip() for chunk in value.split(";") for part in chunk.split(",") if part.strip()]


def _validate_columns(name: str, fieldnames: list[str], required: tuple[str, ...]) -> list[str]:
    missing = [column for column in required if column not in fieldnames]
    return [f"{name} missing required columns: {', '.join(missing)}"] if missing else []


def validate_benchmark_specification(directory: Path) -> list[str]:
    """Return validation errors for benchmark specification CSV files in a directory."""

    errors: list[str] = []
    if not directory.is_dir():
        return [f"Directory not found: {directory}"]

    task_fields, task_rows, task_read_errors = _read_csv(directory / "benchmark_tasks.csv")
    rubric_fields, rubric_rows, rubric_read_errors = _read_csv(directory / "rubrics.csv")
    error_fields, error_rows, error_read_errors = _read_csv(directory / "serious_errors.csv")
    prov_fields, prov_rows, prov_read_errors = _read_csv(directory / "provenance_matrix.csv")
    errors.extend(task_read_errors + rubric_read_errors + error_read_errors + prov_read_errors)
    if errors:
        return errors

    for name, fields, required in (
        ("benchmark_tasks.csv", task_fields, TASK_COLUMNS),
        ("rubrics.csv", rubric_fields, RUBRIC_COLUMNS),
        ("serious_errors.csv", error_fields, ERROR_COLUMNS),
        ("provenance_matrix.csv", prov_fields, PROVENANCE_COLUMNS),
    ):
        errors.extend(_validate_columns(name, fields, required))
    if errors:
        return errors

    task_ids: set[str] = set()
    for row_number, row in enumerate(task_rows, start=2):
        task_id = (row.get("task_id") or "").strip()
        status = (row.get("status") or "").strip()
        research_ids = _split_ids(row.get("research_ids") or "")
        learning_ids = _split_ids(row.get("learning_material_ids") or "")

        if not task_id:
            errors.append(f"benchmark_tasks.csv row {row_number}: task_id is required")
        elif task_id in task_ids:
            errors.append(f"benchmark_tasks.csv row {row_number}: duplicate task_id '{task_id}'")
        else:
            task_ids.add(task_id)
        for column in ("task_name", "definition", "scope", "input_requirements", "output_requirements"):
            if not (row.get(column) or "").strip():
                errors.append(f"benchmark_tasks.csv row {row_number}: {column} is required")
        if status not in ALLOWED_STATUS:
            errors.append(f"benchmark_tasks.csv row {row_number}: invalid status '{status}'")
        if not research_ids and status not in REVIEW_STATUSES:
            errors.append(f"benchmark_tasks.csv row {row_number}: confirmed/non-review task needs research_ids")
        if not learning_ids and status not in REVIEW_STATUSES:
            errors.append(f"benchmark_tasks.csv row {row_number}: confirmed/non-review task needs learning_material_ids")
        if status in {"needs_uet_review", "needs_hnmu_review"} and not (row.get("teacher_decision_needed") or "").strip():
            errors.append(f"benchmark_tasks.csv row {row_number}: review status requires teacher_decision_needed")

    rubric_ids: set[str] = set()
    for row_number, row in enumerate(rubric_rows, start=2):
        rubric_id = (row.get("rubric_id") or "").strip()
        task_id = (row.get("task_id") or "").strip()
        status = (row.get("status") or "").strip()
        if not rubric_id:
            errors.append(f"rubrics.csv row {row_number}: rubric_id is required")
        elif rubric_id in rubric_ids:
            errors.append(f"rubrics.csv row {row_number}: duplicate rubric_id '{rubric_id}'")
        else:
            rubric_ids.add(rubric_id)
        if task_id not in task_ids:
            errors.append(f"rubrics.csv row {row_number}: unknown task_id '{task_id}'")
        for column in ("criterion", "observable_evidence", "score_levels"):
            if not (row.get(column) or "").strip():
                errors.append(f"rubrics.csv row {row_number}: {column} is required")
        if status not in ALLOWED_STATUS:
            errors.append(f"rubrics.csv row {row_number}: invalid status '{status}'")

    error_ids: set[str] = set()
    for row_number, row in enumerate(error_rows, start=2):
        error_id = (row.get("error_id") or "").strip()
        status = (row.get("status") or "").strip()
        affected = _split_ids(row.get("affected_rubric_ids") or "")
        if not error_id:
            errors.append(f"serious_errors.csv row {row_number}: error_id is required")
        elif error_id in error_ids:
            errors.append(f"serious_errors.csv row {row_number}: duplicate error_id '{error_id}'")
        else:
            error_ids.add(error_id)
        for column in ("description", "suggested_action"):
            if not (row.get(column) or "").strip():
                errors.append(f"serious_errors.csv row {row_number}: {column} is required")
        if not affected:
            errors.append(f"serious_errors.csv row {row_number}: affected_rubric_ids is required")
        for rubric_id in affected:
            if rubric_id not in rubric_ids:
                errors.append(f"serious_errors.csv row {row_number}: unknown affected rubric_id '{rubric_id}'")
        if status not in ALLOWED_STATUS:
            errors.append(f"serious_errors.csv row {row_number}: invalid status '{status}'")

    item_lookup = {
        "task": task_ids,
        "rubric": rubric_ids,
        "serious_error": error_ids,
    }
    for row_number, row in enumerate(prov_rows, start=2):
        item_id = (row.get("item_id") or "").strip()
        item_type = (row.get("item_type") or "").strip()
        status = (row.get("status") or "").strip()
        research_ids = _split_ids(row.get("research_ids") or "")
        learning_ids = _split_ids(row.get("learning_material_ids") or "")
        if item_type not in ITEM_TYPES:
            errors.append(f"provenance_matrix.csv row {row_number}: item_type must be one of {sorted(ITEM_TYPES)}")
        elif item_id not in item_lookup[item_type]:
            errors.append(f"provenance_matrix.csv row {row_number}: unknown {item_type} item_id '{item_id}'")
        if not (row.get("rationale") or "").strip():
            errors.append(f"provenance_matrix.csv row {row_number}: rationale is required")
        if status not in ALLOWED_STATUS:
            errors.append(f"provenance_matrix.csv row {row_number}: invalid status '{status}'")
        if not research_ids and not learning_ids and status not in REVIEW_STATUSES:
            errors.append(f"provenance_matrix.csv row {row_number}: supported/confirmed item needs research_ids or learning_material_ids")

    return errors


def main() -> int:
    """Run the command-line validator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing benchmark specification CSV files")
    args = parser.parse_args()
    errors = validate_benchmark_specification(args.directory)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate HNMU raw-dialogue audit checklist outputs.

The validator checks schema-level, format-level, and criteria-registry coverage
requirements for `raw_dialogue_checklist_results.csv`. It does not judge
pedagogical or subject-matter correctness; that authority remains with
HNMU/UET reviewers.

Input:
    A CSV path containing one row per (`sample_id`, `criterion_id`) decision.
    By default, the validator also reads the Plan 04 per-sample criteria
    registry and checks that every sample has exactly the required criteria.

Output:
    A list of validation error strings from `validate_raw_dialogue_audit_output`,
    or process exit code 0/1 when run as a CLI.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable

DEFAULT_CRITERIA_REGISTRY_PATH = Path("experiments/20260709_155523/reports/raw-dialogue-audit-criteria-v0.csv")

REQUIRED_COLUMNS = (
    "sample_id",
    "criterion_id",
    "criterion_group",
    "criterion_name",
    "result",
    "confidence_score",
    "evidence_fragment_id",
    "evidence_source",
    "evidence_match_reason",
    "reason",
    "suggested_reviewer_action",
    "checked_by",
    "checked_at",
)

ALLOWED_RESULTS = {"pass", "fail", "uncertain", "not_applicable"}
CRITERION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
REGISTRY_REQUIRED_COLUMNS = ("criterion_id", "required_per_sample")


def _read_required_criteria(registry_path: Path | None) -> tuple[set[str], list[str]]:
    """Read required per-sample criterion IDs from the criteria registry.

    Args:
        registry_path: CSV path containing the audit criteria registry. When
            ``None``, registry validation is disabled.

    Returns:
        A tuple ``(required_ids, errors)``. ``required_ids`` contains all
        ``criterion_id`` values whose ``required_per_sample`` is ``true``.
        ``errors`` contains registry file or schema problems.
    """
    if registry_path is None:
        return set(), []
    if not registry_path.exists():
        return set(), [f"criteria registry does not exist: {registry_path}"]
    if registry_path.is_dir():
        return set(), [f"expected criteria registry CSV, got directory: {registry_path}"]

    try:
        with registry_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                return set(), ["criteria registry has no header row"]
            errors = [
                f"criteria registry missing required column: {column}"
                for column in REGISTRY_REQUIRED_COLUMNS
                if column not in reader.fieldnames
            ]
            if errors:
                return set(), errors

            required_ids: set[str] = set()
            seen_ids: set[str] = set()
            for index, row in enumerate(reader, start=2):
                criterion_id = (row.get("criterion_id") or "").strip()
                required = (row.get("required_per_sample") or "").strip().lower()
                if not criterion_id:
                    errors.append(f"criteria registry row {index}: criterion_id is required")
                    continue
                if criterion_id in seen_ids:
                    errors.append(f"criteria registry row {index}: duplicate criterion_id: {criterion_id}")
                seen_ids.add(criterion_id)
                if not CRITERION_ID_PATTERN.match(criterion_id):
                    errors.append(f"criteria registry row {index}: unsupported criterion_id: {criterion_id}")
                if required not in {"true", "false"}:
                    errors.append(
                        f"criteria registry row {index}: required_per_sample must be true or false"
                    )
                if required == "true":
                    required_ids.add(criterion_id)
            if not required_ids:
                errors.append("criteria registry contains no required per-sample criteria")
            return required_ids, errors
    except UnicodeDecodeError as exc:
        return set(), [f"criteria registry must be UTF-8 or UTF-8-SIG: {exc}"]
    except csv.Error as exc:
        return set(), [f"criteria registry parse error: {exc}"]


def _read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Read a CSV file into dictionaries and return rows plus errors.

    Args:
        path: CSV file path to read.

    Returns:
        A tuple `(rows, errors)`. `rows` is empty when the file cannot be read
        as CSV. `errors` contains file-level read or header errors.
    """
    if not path.exists():
        return [], [f"file does not exist: {path}"]
    if path.is_dir():
        return [], [f"expected a CSV file, got directory: {path}"]

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                return [], ["CSV has no header row"]
            missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
            errors = [f"missing required column: {column}" for column in missing]
            return list(reader), errors
    except UnicodeDecodeError as exc:
        return [], [f"CSV must be UTF-8 or UTF-8-SIG: {exc}"]
    except csv.Error as exc:
        return [], [f"CSV parse error: {exc}"]


def validate_raw_dialogue_audit_output(
    path: Path,
    criteria_registry_path: Path | None = DEFAULT_CRITERIA_REGISTRY_PATH,
) -> list[str]:
    """Validate raw-dialogue audit checklist CSV output.

    Args:
        path: Path to `raw_dialogue_checklist_results.csv` or a compatible CSV
            file with the required columns.
        criteria_registry_path: Optional criteria registry CSV. When provided,
            every `sample_id` must have exactly the required per-sample
            `criterion_id` values from the registry. Pass ``None`` only for
            schema-only validation of legacy fixtures.

    Returns:
        A list of human-readable validation errors. An empty list means the
        file satisfies the schema-level and registry-level contract.
    """
    required_criteria, registry_errors = _read_required_criteria(criteria_registry_path)
    rows, errors = _read_rows(path)
    errors = registry_errors + errors
    if errors:
        return errors
    if not rows:
        return ["CSV contains no data rows"]

    seen_pairs: set[tuple[str, str]] = set()
    criteria_by_sample: dict[str, set[str]] = {}
    for index, row in enumerate(rows, start=2):
        sample_id = (row.get("sample_id") or "").strip()
        criterion_id = (row.get("criterion_id") or "").strip()
        result = (row.get("result") or "").strip()
        confidence = (row.get("confidence_score") or "").strip()

        if not sample_id:
            errors.append(f"row {index}: sample_id is required")
        if not criterion_id:
            errors.append(f"row {index}: criterion_id is required")
        elif not CRITERION_ID_PATTERN.match(criterion_id):
            errors.append(f"row {index}: criterion_id has unsupported characters: {criterion_id}")
        if sample_id and criterion_id:
            pair = (sample_id, criterion_id)
            if pair in seen_pairs:
                errors.append(f"row {index}: duplicate sample_id + criterion_id: {sample_id}, {criterion_id}")
            seen_pairs.add(pair)
            criteria_by_sample.setdefault(sample_id, set()).add(criterion_id)
            if required_criteria and criterion_id not in required_criteria:
                errors.append(f"row {index}: criterion_id not in required registry: {criterion_id}")

        if result not in ALLOWED_RESULTS:
            errors.append(f"row {index}: invalid result '{result}'")

        try:
            score = float(confidence)
        except ValueError:
            errors.append(f"row {index}: confidence_score must be numeric")
        else:
            if not 0.0 <= score <= 1.0:
                errors.append(f"row {index}: confidence_score must be between 0 and 1")

        for column in ("criterion_group", "criterion_name", "checked_by", "checked_at"):
            if not (row.get(column) or "").strip():
                errors.append(f"row {index}: {column} is required")

        if result in {"fail", "uncertain"}:
            if not (row.get("reason") or "").strip():
                errors.append(f"row {index}: reason is required for {result}")
            if not (row.get("suggested_reviewer_action") or "").strip():
                errors.append(f"row {index}: suggested_reviewer_action is required for {result}")

    if required_criteria:
        for sample_id, observed_criteria in sorted(criteria_by_sample.items()):
            missing = sorted(required_criteria - observed_criteria)
            extra = sorted(observed_criteria - required_criteria)
            if missing:
                errors.append(
                    f"sample {sample_id}: missing required criterion_id values: {', '.join(missing)}"
                )
            if extra:
                errors.append(
                    f"sample {sample_id}: extra criterion_id values not in registry: {', '.join(extra)}"
                )

    return errors


def main(argv: Iterable[str] | None = None) -> int:
    """Run the CSV validator from the command line.

    Args:
        argv: Optional command-line argument iterable. When omitted, arguments
            are read from `sys.argv` through `argparse`.

    Returns:
        Process exit code: `0` when validation passes, `1` otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Path to raw_dialogue_checklist_results.csv")
    parser.add_argument(
        "--criteria-registry",
        type=Path,
        default=DEFAULT_CRITERIA_REGISTRY_PATH,
        help="Path to raw-dialogue-audit-criteria-v0.csv. Defaults to the Plan 04 registry.",
    )
    parser.add_argument(
        "--no-criteria-registry",
        action="store_true",
        help="Disable per-sample criterion coverage checks; use only for legacy schema fixtures.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    registry_path = None if args.no_criteria_registry else args.criteria_registry
    errors = validate_raw_dialogue_audit_output(args.csv_path, registry_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

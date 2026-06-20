#!/usr/bin/env python3
"""Validate the structural integrity of a literature evidence matrix CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_COLUMNS = (
    "record_id",
    "title",
    "year",
    "venue",
    "url_or_doi",
    "publication_status",
    "study_type",
    "education_domain",
    "learner_level",
    "tutoring_capabilities",
    "task_or_dataset",
    "human_expert_role",
    "rubric_or_metric",
    "reliability_evidence",
    "main_findings",
    "limitations",
    "relevance_to_project",
    "evidence_location",
    "reviewer_notes",
)

ALLOWED_PUBLICATION_STATUS = {"peer_reviewed", "preprint", "thesis", "other"}


def _looks_like_source(value: str) -> bool:
    """Return whether a value resembles a DOI or an HTTP(S) URL."""

    normalized = value.strip().lower()
    if normalized.startswith("10.") and "/" in normalized:
        return True
    parsed = urlparse(normalized)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_evidence_matrix(path: Path) -> list[str]:
    """Return human-readable validation errors for an evidence matrix."""

    errors: list[str] = []
    if not path.is_file():
        return [f"File not found: {path}"]

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return errors

        seen_ids: set[str] = set()
        seen_titles: set[str] = set()
        row_count = 0
        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            record_id = (row.get("record_id") or "").strip()
            title = (row.get("title") or "").strip()
            source = (row.get("url_or_doi") or "").strip()
            status = (row.get("publication_status") or "").strip()
            relevance = (row.get("relevance_to_project") or "").strip()

            if not record_id:
                errors.append(f"Row {row_number}: record_id is required")
            elif record_id in seen_ids:
                errors.append(f"Row {row_number}: duplicate record_id '{record_id}'")
            else:
                seen_ids.add(record_id)

            normalized_title = " ".join(title.lower().split())
            if not title:
                errors.append(f"Row {row_number}: title is required")
            elif normalized_title in seen_titles:
                errors.append(f"Row {row_number}: duplicate normalized title '{title}'")
            else:
                seen_titles.add(normalized_title)

            if not _looks_like_source(source):
                errors.append(f"Row {row_number}: url_or_doi is not a DOI or HTTP(S) URL")
            if status not in ALLOWED_PUBLICATION_STATUS:
                errors.append(
                    f"Row {row_number}: publication_status must be one of "
                    f"{sorted(ALLOWED_PUBLICATION_STATUS)}"
                )
            if not relevance:
                errors.append(f"Row {row_number}: relevance_to_project is required")

        if row_count == 0:
            errors.append("Evidence matrix has no study records")

    return errors


def main() -> int:
    """Run the command-line validator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="Path to evidence_matrix.csv")
    args = parser.parse_args()
    errors = validate_evidence_matrix(args.matrix)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.matrix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

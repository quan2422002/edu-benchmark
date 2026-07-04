#!/usr/bin/env python3
"""Validate v0 learning-resource source and fragment mappings."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urlparse


SOURCE_COLUMNS = (
    "learning_material_id",
    "source_title",
    "material_type",
    "grade",
    "source_url",
    "source_key",
    "local_file_path",
    "version_label",
    "status",
    "notes",
)

FRAGMENT_COLUMNS = (
    "fragment_id",
    "learning_material_id",
    "page_start",
    "page_end",
    "section_label",
    "order_index",
    "location_note",
    "status",
)

ALLOWED_STATUS = {"draft", "needs_uet_review", "needs_hnmu_review", "confirmed", "retired"}
SOURCE_ID_RE = re.compile(r"^LM-[A-Z0-9]+-TIN(?:[6-9]|THCS|6-9)-[A-Z0-9][A-Z0-9-]*$")
FRAGMENT_ID_RE = re.compile(r"^LM-[A-Z0-9]+-TIN(?:[6-9]|THCS|6-9)-[A-Z0-9][A-Z0-9-]*#F\d{4}$")


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], list[str]]:
    if not path.is_file():
        return [], [], [f"File not found: {path}"]
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader), []


def _looks_like_url(value: str) -> bool:
    if not value:
        return True
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_int(value: str) -> bool:
    if not value:
        return True
    return value.isdigit()


def validate_learning_resource_registry(source_map: Path, fragments: Path | None = None) -> list[str]:
    """Return validation errors for source and optional fragment mappings."""

    errors: list[str] = []
    fieldnames, rows, read_errors = _read_csv(source_map)
    errors.extend(read_errors)
    if errors:
        return errors

    missing = [column for column in SOURCE_COLUMNS if column not in fieldnames]
    if missing:
        return [f"Source map missing required columns: {', '.join(missing)}"]

    if not rows:
        errors.append("Source map has no records")

    material_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        material_id = (row.get("learning_material_id") or "").strip()
        title = (row.get("source_title") or "").strip()
        material_type = (row.get("material_type") or "").strip()
        grade = (row.get("grade") or "").strip()
        source_url = (row.get("source_url") or "").strip()
        local_file_path = (row.get("local_file_path") or "").strip()
        notes = (row.get("notes") or "").strip()
        status = (row.get("status") or "").strip()

        if not material_id:
            errors.append(f"Row {row_number}: learning_material_id is required")
        elif material_id in material_ids:
            errors.append(f"Row {row_number}: duplicate learning_material_id '{material_id}'")
        else:
            material_ids.add(material_id)
            if not SOURCE_ID_RE.match(material_id):
                errors.append(f"Row {row_number}: learning_material_id has invalid v0 format '{material_id}'")

        if not title:
            errors.append(f"Row {row_number}: source_title is required")
        if not material_type:
            errors.append(f"Row {row_number}: material_type is required")
        if not grade:
            errors.append(f"Row {row_number}: grade is required")
        if status not in ALLOWED_STATUS:
            errors.append(f"Row {row_number}: status must be one of {sorted(ALLOWED_STATUS)}")
        if not _looks_like_url(source_url):
            errors.append(f"Row {row_number}: source_url must be empty or HTTP(S)")
        if not (source_url or local_file_path or notes):
            errors.append(
                f"Row {row_number}: at least one of source_url, local_file_path, or notes is required for retrieval"
            )

    if fragments is None:
        return errors

    frag_fields, frag_rows, frag_read_errors = _read_csv(fragments)
    errors.extend(frag_read_errors)
    if frag_read_errors:
        return errors

    frag_missing = [column for column in FRAGMENT_COLUMNS if column not in frag_fields]
    if frag_missing:
        errors.append(f"Fragment map missing required columns: {', '.join(frag_missing)}")
        return errors

    seen_fragments: set[str] = set()
    for row_number, row in enumerate(frag_rows, start=2):
        fragment_id = (row.get("fragment_id") or "").strip()
        material_id = (row.get("learning_material_id") or "").strip()
        status = (row.get("status") or "").strip()
        page_start = (row.get("page_start") or "").strip()
        page_end = (row.get("page_end") or "").strip()
        section_label = (row.get("section_label") or "").strip()
        order_index = (row.get("order_index") or "").strip()
        location_note = (row.get("location_note") or "").strip()

        if not fragment_id:
            errors.append(f"Fragment row {row_number}: fragment_id is required")
        elif fragment_id in seen_fragments:
            errors.append(f"Fragment row {row_number}: duplicate fragment_id '{fragment_id}'")
        else:
            seen_fragments.add(fragment_id)
            if not FRAGMENT_ID_RE.match(fragment_id):
                errors.append(f"Fragment row {row_number}: fragment_id has invalid v0 format '{fragment_id}'")

        if material_id not in material_ids:
            errors.append(f"Fragment row {row_number}: unknown learning_material_id '{material_id}'")
        elif fragment_id and not fragment_id.startswith(f"{material_id}#F"):
            errors.append(f"Fragment row {row_number}: fragment_id must start with parent ID plus '#F'")
        if status not in ALLOWED_STATUS:
            errors.append(f"Fragment row {row_number}: status must be one of {sorted(ALLOWED_STATUS)}")
        if not _is_int(page_start):
            errors.append(f"Fragment row {row_number}: page_start must be empty or an integer")
        if not _is_int(page_end):
            errors.append(f"Fragment row {row_number}: page_end must be empty or an integer")
        if page_start and page_end and int(page_start) > int(page_end):
            errors.append(f"Fragment row {row_number}: page_start cannot be greater than page_end")
        if not _is_int(order_index):
            errors.append(f"Fragment row {row_number}: order_index must be empty or an integer")
        if not (page_start or section_label or location_note):
            errors.append(
                f"Fragment row {row_number}: at least one locator is required: page_start, section_label, or location_note"
            )

    return errors


def main() -> int:
    """Run the command-line validator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_map", type=Path, help="Path to learning_resource_source_map.csv")
    parser.add_argument("--fragments", type=Path, help="Optional path to learning_resource_fragments.csv")
    args = parser.parse_args()
    errors = validate_learning_resource_registry(args.source_map, args.fragments)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.source_map}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Provenance checks for research and learning-resource identifiers."""

from __future__ import annotations

from typing import Mapping, Sequence

from .schema import split_ids


def validate_provenance_ids(
    rows: Sequence[Mapping[str, str]],
    *,
    known_item_ids: set[str],
    known_research_ids: set[str],
    known_learning_material_ids: set[str],
) -> list[str]:
    """Validate item and source identifiers without backfilling evidence."""

    errors: list[str] = []
    for index, row in enumerate(rows, start=2):
        item_id = str(row.get("item_id", "")).strip()
        if item_id not in known_item_ids:
            errors.append(f"row_{index}:unknown_item:{item_id}")
        research_ids = split_ids(row.get("research_ids", ""))
        material_ids = split_ids(row.get("learning_material_ids", ""))
        for research_id in research_ids:
            if research_id not in known_research_ids:
                errors.append(f"row_{index}:unknown_research_id:{research_id}")
        for material_id in material_ids:
            if material_id not in known_learning_material_ids:
                errors.append(
                    f"row_{index}:unknown_learning_material_id:{material_id}"
                )
        if not research_ids and not material_ids:
            status = str(row.get("status", "")).strip()
            if status not in {"needs_uet_review", "needs_hnmu_review", "draft"}:
                errors.append(f"row_{index}:unsupported_item_not_flagged:{item_id}")
    return errors

"""Utilities for the capability/principle two-tier rubric artifacts."""

from __future__ import annotations

from typing import Mapping, Sequence

from .schema import FLAT_RUBRIC_COLUMNS


def flatten_two_tier_rubrics(
    dimensions: Sequence[Mapping[str, str]],
    principle_rubrics: Sequence[Mapping[str, str]],
    tasks: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Create a flat export while preserving the two source tiers."""

    active_task_ids = [
        str(task["task_id"])
        for task in tasks
        if str(task.get("status", "")) != "retired"
    ]
    if len(active_task_ids) != 1:
        raise ValueError("The active design requires exactly one benchmark task")
    task_id = active_task_ids[0]
    rows: list[dict[str, str]] = []
    for dimension in dimensions:
        rows.append(
            {
                "rubric_id": str(dimension["dimension_id"]),
                "task_id": task_id,
                "principle_id": "",
                "criterion": str(dimension.get("criterion", "")),
                "observable_evidence": str(
                    dimension.get("observable_evidence", "")
                ),
                "score_levels": str(dimension.get("score_levels", "")),
                "status": str(dimension.get("status", "")),
            }
        )
    for rubric in principle_rubrics:
        rows.append(
            {
                "rubric_id": str(rubric.get("rubric_id", "")),
                "task_id": task_id,
                "principle_id": str(rubric.get("principle_id", "")),
                "criterion": str(rubric.get("criterion", "")),
                "observable_evidence": str(
                    rubric.get("observable_evidence", "")
                ),
                "score_levels": str(rubric.get("score_levels", "")),
                "status": str(rubric.get("status", "")),
            }
        )
    ids = [row["rubric_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Flattened rubric IDs are not unique")
    return sorted(rows, key=lambda row: (row["principle_id"], row["rubric_id"]))

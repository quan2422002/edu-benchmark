"""Materialize source-grounded inputs for pedagogical-principle annotation."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence

from .manifest import sha256_file

CANDIDATE_REQUIRED_COLUMNS = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "gold_answer",
)
SOURCE_REQUIRED_COLUMNS = (
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "question",
    "answer_sgv",
)
GROUNDING_POOL_COLUMNS = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "source_question",
    "gold_answer",
)
SOURCE_TO_CANDIDATE_FIELDS = (
    ("grade", "grade"),
    ("lesson", "lesson"),
    ("position", "position"),
    ("bloom_level", "bloom_level"),
    ("answer_sgv", "gold_answer"),
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
    rows: Sequence[Mapping[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _repo_relative(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(repo_root.resolve()))
    except ValueError:
        return str(resolved)


def _require_columns(path: Path, header: Sequence[str], required: Sequence[str]) -> None:
    missing = sorted(set(required) - set(header))
    if missing:
        raise ValueError(f"{path}: missing required columns: {missing}")


def materialize_principle_grounding_pool(
    *,
    repo_root: Path,
    candidate_path: Path,
    source_dialogue_paths: Sequence[Path],
    output_dir: Path,
    created_at: str | None = None,
) -> dict[str, object]:
    """Join source questions to benchmark candidates through a fail-closed sample_id join."""

    if not source_dialogue_paths:
        raise ValueError("At least one source dialogue path is required")

    candidate_header, candidate_rows = _read_csv(candidate_path)
    _require_columns(candidate_path, candidate_header, CANDIDATE_REQUIRED_COLUMNS)

    candidate_ids: set[str] = set()
    for row in candidate_rows:
        candidate_id = row["benchmark_candidate_id"].strip()
        sample_id = row["sample_id"].strip()
        if not candidate_id or not sample_id:
            raise ValueError("Candidate and sample IDs must be non-empty")
        if candidate_id in candidate_ids:
            raise ValueError(f"Duplicate benchmark_candidate_id: {candidate_id}")
        candidate_ids.add(candidate_id)

    source_by_sample: dict[str, dict[str, str]] = {}
    source_records: list[dict[str, object]] = []
    source_row_count = 0
    for source_path in source_dialogue_paths:
        source_header, source_rows = _read_csv(source_path)
        _require_columns(source_path, source_header, SOURCE_REQUIRED_COLUMNS)
        source_row_count += len(source_rows)
        source_records.append(
            {
                "path": _repo_relative(source_path, repo_root),
                "sha256": sha256_file(source_path),
                "row_count": len(source_rows),
            }
        )
        for row in source_rows:
            sample_id = row["sample_id"].strip()
            if not sample_id:
                raise ValueError(f"{source_path}: empty sample_id")
            if sample_id in source_by_sample:
                raise ValueError(f"Duplicate source sample_id across snapshots: {sample_id}")
            source_by_sample[sample_id] = row

    output_rows: list[dict[str, str]] = []
    used_sample_ids: set[str] = set()
    for candidate in candidate_rows:
        candidate_id = candidate["benchmark_candidate_id"].strip()
        sample_id = candidate["sample_id"].strip()
        source = source_by_sample.get(sample_id)
        if source is None:
            raise ValueError(
                f"{candidate_id}: sample_id not found in source dialogue snapshots: {sample_id}"
            )
        question = source["question"].strip()
        if not question:
            raise ValueError(f"{candidate_id}: source question is empty for {sample_id}")
        for source_field, candidate_field in SOURCE_TO_CANDIDATE_FIELDS:
            if source[source_field].strip() != candidate[candidate_field].strip():
                raise ValueError(
                    f"{candidate_id}: source/candidate mismatch for "
                    f"{source_field}->{candidate_field}"
                )
        output_rows.append(
            {
                "benchmark_candidate_id": candidate["benchmark_candidate_id"],
                "sample_id": candidate["sample_id"],
                "grade": candidate["grade"],
                "lesson": candidate["lesson"],
                "position": candidate["position"],
                "bloom_level": candidate["bloom_level"],
                "student_prompt": candidate["student_prompt"],
                "conversation_history": candidate["conversation_history"],
                "source_question": question,
                "gold_answer": candidate["gold_answer"],
            }
        )
        used_sample_ids.add(sample_id)

    output_path = output_dir / "candidate_principle_grounding_pool.csv"
    manifest_path = output_dir / "candidate_principle_grounding_pool_manifest.json"
    _write_csv(output_path, GROUNDING_POOL_COLUMNS, output_rows)

    stable_created_at = created_at
    if stable_created_at is None and manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("manifest_version") == "plan03-principle-grounding-pool-v1":
            stable_created_at = previous.get("created_at")

    manifest = {
        "manifest_version": "plan03-principle-grounding-pool-v1",
        "created_at": stable_created_at or datetime.now().astimezone().isoformat(),
        "join_policy": {
            "join_key": "sample_id",
            "join_cardinality": "many_candidates_to_exactly_one_source_dialogue",
            "source_question_field": "question",
            "gold_answer_source_field": "answer_sgv",
            "gold_response_excluded": True,
            "fail_closed_on": [
                "missing_source_sample_id",
                "duplicate_source_sample_id",
                "empty_source_question",
                "candidate_source_field_mismatch",
            ],
        },
        "candidate_input": {
            "path": _repo_relative(candidate_path, repo_root),
            "sha256": sha256_file(candidate_path),
            "row_count": len(candidate_rows),
            "unique_candidate_count": len(candidate_ids),
            "unique_sample_count": len(used_sample_ids),
        },
        "source_dialogue_inputs": source_records,
        "source_dialogue_union": {
            "row_count": source_row_count,
            "unique_sample_count": len(source_by_sample),
        },
        "output": {
            "path": _repo_relative(output_path, repo_root),
            "sha256": sha256_file(output_path),
            "row_count": len(output_rows),
            "columns": list(GROUNDING_POOL_COLUMNS),
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "candidate_count": len(output_rows),
        "source_sample_count": len(source_by_sample),
        "used_sample_count": len(used_sample_ids),
        "output_path": str(output_path),
        "manifest_path": str(manifest_path),
    }


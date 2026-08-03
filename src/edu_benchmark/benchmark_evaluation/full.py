"""Validate and lock the complete 1,400-candidate evaluation pool."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from .config_builder import PRINCIPLE_ORDER
from .smoke import load_required_principle_sets


FULL_SIZE = 1400
FULL_STATUS = "eligible_without_plan03_review"
GROUNDING_FIELDS = (
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


class FullManifestError(RuntimeError):
    """Raised when the exported full pool is not the exact eligible set."""


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def _normalized_history(value: str) -> list[dict[str, Any]]:
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("conversation history must be a list")
    normalized = []
    for turn in parsed:
        if not isinstance(turn, dict):
            raise ValueError("conversation turn must be an object")
        normalized.append(
            {
                "turn_index": int(turn["turn_index"]),
                "role": str(turn["role"]).strip(),
                "content": str(turn["content"]).strip(),
            }
        )
    return normalized


def build_full_manifest(
    *,
    eligible_csv: Path,
    grounding_pool_csv: Path,
    candidate_csv: Path,
    analysis_json: Path,
    requirement_run_jsonl: Path,
) -> dict[str, Any]:
    """Return a hash-locked manifest for exactly the eligible 1,400 rows."""

    rows, fields = _read_csv(eligible_csv)
    required_fields = {
        "benchmark_candidate_id",
        "eligibility_status",
        "required_principle_set",
        "principle_scores_json",
        "gold_response",
        *GROUNDING_FIELDS,
    }
    missing = sorted(required_fields - set(fields))
    if missing:
        raise FullManifestError(f"eligible CSV missing fields: {missing}")
    if len(rows) != FULL_SIZE:
        raise FullManifestError(
            f"expected {FULL_SIZE} eligible rows, found {len(rows)}"
        )
    candidate_ids = [row["benchmark_candidate_id"] for row in rows]
    if any(not value.strip() for value in candidate_ids):
        raise FullManifestError("eligible CSV contains an empty candidate ID")
    if len(set(candidate_ids)) != FULL_SIZE:
        raise FullManifestError("eligible CSV candidate IDs must be unique")
    invalid_status = sorted(
        row["benchmark_candidate_id"]
        for row in rows
        if row["eligibility_status"] != FULL_STATUS
    )
    if invalid_status:
        raise FullManifestError(
            f"rows do not have status {FULL_STATUS}: {invalid_status[:5]}"
        )

    analysis = json.loads(analysis_json.read_text(encoding="utf-8"))
    analysis_ids = set(
        analysis["eligibility"]["candidate_ids"][FULL_STATUS]
    )
    if set(candidate_ids) != analysis_ids or len(analysis_ids) != FULL_SIZE:
        raise FullManifestError(
            "eligible CSV IDs do not exactly match Plan 03 analysis"
        )

    grounding_rows, _ = _read_csv(grounding_pool_csv)
    grounding = {
        row["benchmark_candidate_id"]: row for row in grounding_rows
    }
    candidate_rows, _ = _read_csv(candidate_csv)
    candidates = {
        row["benchmark_candidate_id"]: row for row in candidate_rows
    }
    requirement_sets = load_required_principle_sets(requirement_run_jsonl)
    for row in rows:
        candidate_id = row["benchmark_candidate_id"]
        ground = grounding.get(candidate_id)
        candidate = candidates.get(candidate_id)
        if ground is None or candidate is None:
            raise FullManifestError(
                f"{candidate_id}: missing grounding or candidate row"
            )
        for field in GROUNDING_FIELDS:
            if field == "conversation_history":
                try:
                    equal = _normalized_history(
                        row[field]
                    ) == _normalized_history(ground[field])
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise FullManifestError(
                        f"{candidate_id}: invalid conversation history JSON"
                    ) from exc
            else:
                equal = row[field].strip() == ground[field].strip()
            if not equal:
                raise FullManifestError(
                    f"{candidate_id}: eligible CSV mismatch in {field}"
                )
        if row["gold_response"].strip() != candidate[
            "gold_response"
        ].strip():
            raise FullManifestError(
                f"{candidate_id}: eligible CSV mismatch in gold_response"
            )
        try:
            stored_set = tuple(json.loads(row["required_principle_set"]))
            scores = {
                str(key): int(value)
                for key, value in json.loads(
                    row["principle_scores_json"]
                ).items()
            }
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise FullManifestError(
                f"{candidate_id}: invalid principle JSON"
            ) from exc
        if set(scores) != set(PRINCIPLE_ORDER):
            raise FullManifestError(
                f"{candidate_id}: score map must cover six principles"
            )
        derived_set = tuple(
            principle_id
            for principle_id in PRINCIPLE_ORDER
            if scores[principle_id] >= 4
        )
        if not derived_set:
            raise FullManifestError(
                f"{candidate_id}: empty requirement_score>=4 set"
            )
        if stored_set != derived_set:
            raise FullManifestError(
                f"{candidate_id}: stored required set differs from scores"
            )
        if requirement_sets.get(candidate_id) != derived_set:
            raise FullManifestError(
                f"{candidate_id}: requirement run differs from eligible CSV"
            )

    sorted_ids = sorted(candidate_ids)
    ids_hash = hashlib.sha256(
        "\n".join(sorted_ids).encode("utf-8")
    ).hexdigest()
    return {
        "record_type": "benchmark_evaluation_full_candidate_manifest",
        "manifest_version": "full_1400_v1",
        "candidate_count": FULL_SIZE,
        "candidate_ids": sorted_ids,
        "candidate_ids_sha256": ids_hash,
        "selection_contract": {
            "source_status": FULL_STATUS,
            "selection_role": "complete_eligible_pool_not_sample",
            "required_principle_threshold": 4,
            "all_and_only_source_rows_required": True,
        },
        "input_sha256": {
            _portable(eligible_csv): _sha256(eligible_csv),
            _portable(grounding_pool_csv): _sha256(grounding_pool_csv),
            _portable(candidate_csv): _sha256(candidate_csv),
            _portable(analysis_json): _sha256(analysis_json),
            _portable(requirement_run_jsonl): _sha256(
                requirement_run_jsonl
            ),
        },
        "execution_gate": {
            "status": "closed_pending_pilot_and_budget_reauthorization",
            "reason": (
                "Tooling is installed, but the current conservative full-run "
                "upper bound exceeds the experiment hard budget."
            ),
        },
    }

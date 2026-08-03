"""Select a deterministic 30-candidate judge cost pilot."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import random
from typing import Any

from .pilot import bloom_group
from .smoke import load_required_principle_sets


COST_PILOT_SIZE = 30
GRADE_TARGETS = {"6": 8, "7": 8, "8": 7, "9": 7}
PRINCIPLE_MINIMUMS = {
    "PRINCIPLE-CHALLENGE": 2,
    "PRINCIPLE-EXPLANATION": 12,
    "PRINCIPLE-MODELLING": 5,
    "PRINCIPLE-PRACTICE": 5,
    "PRINCIPLE-FEEDBACK": 12,
    "PRINCIPLE-QUESTIONING": 10,
}
HISTORY_MINIMUMS = {"empty": 10, "nonempty": 10}
BLOOM_MINIMUMS = {"remember": 7, "understand": 7, "apply": 7}
SET_SIZE_MINIMUMS = {1: 5, 2: 8, 3: 5}
LENGTH_BUCKET_MINIMUMS = {"short": 8, "medium": 8, "long": 8}
MIN_DISTINCT_LESSONS = 20


class CostPilotSelectionError(RuntimeError):
    """Raised when the 30-candidate cost pilot cannot meet its contract."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def _coverage(selected: list[str], features: dict[str, dict[str, Any]]):
    return {
        "grade": Counter(features[cid]["grade"] for cid in selected),
        "principle": Counter(
            principle
            for cid in selected
            for principle in features[cid]["principles"]
        ),
        "history": Counter(features[cid]["history"] for cid in selected),
        "bloom": Counter(features[cid]["bloom"] for cid in selected),
        "set_size": Counter(features[cid]["set_size"] for cid in selected),
        "length": Counter(features[cid]["length"] for cid in selected),
        "lessons": len({features[cid]["lesson_key"] for cid in selected}),
        "families": len({features[cid]["family"] for cid in selected}),
    }


def _deficit(coverage: dict[str, Any]) -> int:
    value = sum(
        abs(coverage["grade"].get(key, 0) - target)
        for key, target in GRADE_TARGETS.items()
    )
    for name, minimums in (
        ("principle", PRINCIPLE_MINIMUMS),
        ("history", HISTORY_MINIMUMS),
        ("bloom", BLOOM_MINIMUMS),
        ("set_size", SET_SIZE_MINIMUMS),
        ("length", LENGTH_BUCKET_MINIMUMS),
    ):
        value += sum(
            max(0, minimum - coverage[name].get(key, 0))
            for key, minimum in minimums.items()
        )
    value += max(0, MIN_DISTINCT_LESSONS - coverage["lessons"])
    value += max(0, COST_PILOT_SIZE - coverage["families"])
    return value


def _plain(coverage: dict[str, Any]) -> dict[str, Any]:
    return {
        "grade_counts": dict(sorted(coverage["grade"].items())),
        "principle_incidence_counts": dict(
            sorted(coverage["principle"].items())
        ),
        "history_counts": dict(sorted(coverage["history"].items())),
        "bloom_group_counts": dict(sorted(coverage["bloom"].items())),
        "required_principle_set_size_counts": {
            str(key): value
            for key, value in sorted(coverage["set_size"].items())
        },
        "context_length_bucket_counts": dict(
            sorted(coverage["length"].items())
        ),
        "distinct_family_count": coverage["families"],
        "distinct_grade_lesson_count": coverage["lessons"],
    }


def build_judge_cost_pilot_manifest(
    *,
    pilot_manifest: Path,
    grounding_pool_csv: Path,
    requirement_run_jsonl: Path,
    seed: int = 20260729,
    restarts: int = 30000,
) -> dict[str, Any]:
    """Select 30 rows for cost estimation from the reviewed pilot frame."""

    pilot = json.loads(pilot_manifest.read_text(encoding="utf-8"))
    frame = list(pilot["candidate_ids"])
    anchors = list(pilot["smoke_anchor_candidate_ids"])
    if len(frame) != 80 or len(set(frame)) != 80:
        raise CostPilotSelectionError("pilot frame must contain 80 unique IDs")
    if len(anchors) != 10 or not set(anchors) <= set(frame):
        raise CostPilotSelectionError("cost pilot requires ten smoke anchors")
    rows = {
        row["benchmark_candidate_id"]: row
        for row in _read_csv(grounding_pool_csv)
    }
    required = load_required_principle_sets(requirement_run_jsonl)
    unavailable = sorted(set(frame) - set(rows) | set(frame) - set(required))
    if unavailable:
        raise CostPilotSelectionError(f"unavailable frame IDs: {unavailable}")

    lengths = sorted(
        (
            len(rows[cid]["student_prompt"])
            + len(rows[cid]["conversation_history"])
            + len(rows[cid]["source_question"])
            + len(rows[cid]["gold_answer"]),
            cid,
        )
        for cid in frame
    )
    length_bucket = {}
    for index, (_, cid) in enumerate(lengths):
        length_bucket[cid] = (
            "short" if index < 27 else "medium" if index < 54 else "long"
        )
    features = {}
    for cid in frame:
        row = rows[cid]
        features[cid] = {
            "grade": row["grade"],
            "principles": required[cid],
            "history": (
                "empty" if row["conversation_history"] == "[]" else "nonempty"
            ),
            "bloom": bloom_group(row["bloom_level"]),
            "set_size": len(required[cid]),
            "length": length_bucket[cid],
            "lesson_key": (row["grade"], row["lesson"]),
            "family": row["sample_id"],
        }

    remainder = sorted(set(frame) - set(anchors))
    best = None
    rng = random.Random(seed)
    for _ in range(restarts):
        selected = [*anchors, *rng.sample(remainder, COST_PILOT_SIZE - 10)]
        coverage = _coverage(selected, features)
        rank = (_deficit(coverage), -coverage["lessons"])
        if best is None or rank < best[0]:
            best = (rank, sorted(selected), coverage)
            if rank[0] == 0 and coverage["lessons"] >= 24:
                break
    if best is None or best[0][0] != 0:
        raise CostPilotSelectionError(
            "coverage search failed; "
            f"best={None if best is None else (best[0], _plain(best[2]))}"
        )
    selected = best[1]
    coverage = best[2]
    ids_hash = hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest()
    return {
        "record_type": "benchmark_evaluation_judge_cost_pilot_manifest",
        "manifest_version": "judge_cost_pilot_30_v1",
        "candidate_count": COST_PILOT_SIZE,
        "candidate_ids": selected,
        "candidate_ids_sha256": ids_hash,
        "smoke_anchor_candidate_ids": anchors,
        "selection_contract": {
            "selection_role": "cost_and_operational_calibration_not_quality_estimate",
            "source_frame": "pilot_80_v1",
            "grade_targets": GRADE_TARGETS,
            "principle_minimums": PRINCIPLE_MINIMUMS,
            "history_minimums": HISTORY_MINIMUMS,
            "bloom_group_minimums": BLOOM_MINIMUMS,
            "required_set_size_minimums": {
                str(key): value for key, value in SET_SIZE_MINIMUMS.items()
            },
            "context_length_bucket_minimums": LENGTH_BUCKET_MINIMUMS,
            "minimum_distinct_grade_lessons": MIN_DISTINCT_LESSONS,
            "include_smoke_anchors": True,
            "seed": seed,
            "deterministic_restarts": restarts,
        },
        "coverage": _plain(coverage),
        "input_sha256": {
            _portable(pilot_manifest): _sha256(pilot_manifest),
            _portable(grounding_pool_csv): _sha256(grounding_pool_csv),
            _portable(requirement_run_jsonl): _sha256(requirement_run_jsonl),
        },
        "limitations": [
            "The 30 candidates estimate judge cost and operational behavior only.",
            "The subset is not a population sample and does not validate judge accuracy.",
        ],
    }

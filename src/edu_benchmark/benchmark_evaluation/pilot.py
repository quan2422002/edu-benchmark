"""Deterministic coverage-oriented pilot selection."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import random
from typing import Any

from .smoke import load_required_principle_sets


class PilotSelectionError(RuntimeError):
    """Raised when the locked pilot coverage contract cannot be met."""


PILOT_SIZE = 80
GRADE_TARGETS = {"6": 20, "7": 20, "8": 20, "9": 20}
PRINCIPLE_MINIMUMS = {
    "PRINCIPLE-CHALLENGE": 8,
    "PRINCIPLE-EXPLANATION": 20,
    "PRINCIPLE-MODELLING": 12,
    "PRINCIPLE-PRACTICE": 12,
    "PRINCIPLE-FEEDBACK": 20,
    "PRINCIPLE-QUESTIONING": 20,
}
HISTORY_MINIMUMS = {"empty": 30, "nonempty": 30}
BLOOM_MINIMUMS = {"remember": 20, "understand": 20, "apply": 20}
SET_SIZE_MINIMUMS = {1: 12, 2: 12, 3: 12}
MIN_DISTINCT_LESSONS = 32
EXPECTED_ELIGIBLE = 1400


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


def bloom_group(value: str) -> str:
    """Collapse verbose Vietnamese Bloom labels into three stable groups."""

    normalized = value.strip().lower()
    if normalized.startswith(("nhận biết", "biết")):
        return "remember"
    if normalized.startswith(("thông hiểu", "hiểu")):
        return "understand"
    if normalized.startswith("vận dụng"):
        return "apply"
    raise PilotSelectionError(f"unsupported Bloom label: {value!r}")


def _coverage(
    selected: list[str], features: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    grade = Counter(
        features[candidate_id]["grade"] for candidate_id in selected
    )
    principle = Counter(
        principle_id
        for candidate_id in selected
        for principle_id in features[candidate_id]["principles"]
    )
    history = Counter(
        features[candidate_id]["history"] for candidate_id in selected
    )
    bloom = Counter(
        features[candidate_id]["bloom"] for candidate_id in selected
    )
    set_size = Counter(
        features[candidate_id]["set_size"] for candidate_id in selected
    )
    families = {
        features[candidate_id]["family"] for candidate_id in selected
    }
    lessons = {
        features[candidate_id]["lesson_key"] for candidate_id in selected
    }
    return {
        "grade": grade,
        "principle": principle,
        "history": history,
        "bloom": bloom,
        "set_size": set_size,
        "family_count": len(families),
        "lesson_count": len(lessons),
    }


def _deficit(coverage: dict[str, Any]) -> int:
    total = sum(
        abs(coverage["grade"].get(grade, 0) - target)
        for grade, target in GRADE_TARGETS.items()
    )
    total += sum(
        max(0, minimum - coverage["principle"].get(key, 0))
        for key, minimum in PRINCIPLE_MINIMUMS.items()
    )
    total += sum(
        max(0, minimum - coverage["history"].get(key, 0))
        for key, minimum in HISTORY_MINIMUMS.items()
    )
    total += sum(
        max(0, minimum - coverage["bloom"].get(key, 0))
        for key, minimum in BLOOM_MINIMUMS.items()
    )
    total += sum(
        max(0, minimum - coverage["set_size"].get(key, 0))
        for key, minimum in SET_SIZE_MINIMUMS.items()
    )
    total += max(0, MIN_DISTINCT_LESSONS - coverage["lesson_count"])
    return total


def _plain_coverage(coverage: dict[str, Any]) -> dict[str, Any]:
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
        "distinct_family_count": coverage["family_count"],
        "distinct_grade_lesson_count": coverage["lesson_count"],
    }


def build_pilot_manifest(
    *,
    grounding_pool_csv: Path,
    analysis_json: Path,
    requirement_run_jsonl: Path,
    smoke_anchor_manifest: Path,
    seed: int = 20260729,
    restarts: int = 96,
) -> dict[str, Any]:
    """Select 80 unique families under the approved coverage contract."""

    rows = {
        row["benchmark_candidate_id"]: row
        for row in _read_csv(grounding_pool_csv)
    }
    analysis = json.loads(analysis_json.read_text(encoding="utf-8"))
    eligible_ids = set(
        analysis["eligibility"]["candidate_ids"][
            "eligible_without_plan03_review"
        ]
    )
    if len(eligible_ids) != EXPECTED_ELIGIBLE:
        raise PilotSelectionError(
            f"expected {EXPECTED_ELIGIBLE} eligible candidates, "
            f"found {len(eligible_ids)}"
        )
    requirement_sets = load_required_principle_sets(
        requirement_run_jsonl
    )
    joined_ids = sorted(
        candidate_id
        for candidate_id in eligible_ids
        if candidate_id in rows
        and candidate_id in requirement_sets
        and requirement_sets[candidate_id]
    )
    if len(joined_ids) != EXPECTED_ELIGIBLE:
        raise PilotSelectionError(
            f"expected {EXPECTED_ELIGIBLE} fully joined candidates, "
            f"found {len(joined_ids)}"
        )

    features: dict[str, dict[str, Any]] = {}
    for candidate_id in joined_ids:
        row = rows[candidate_id]
        principles = requirement_sets[candidate_id]
        features[candidate_id] = {
            "grade": row["grade"],
            "family": row["sample_id"],
            "principles": principles,
            "history": (
                "empty"
                if row["conversation_history"] == "[]"
                else "nonempty"
            ),
            "bloom": bloom_group(row["bloom_level"]),
            "set_size": len(principles),
            "lesson_key": (row["grade"], row["lesson"]),
        }

    anchor_data = json.loads(
        smoke_anchor_manifest.read_text(encoding="utf-8")
    )
    anchor_ids = list(anchor_data["candidate_ids"])
    if len(anchor_ids) != 10 or len(anchor_ids) != len(set(anchor_ids)):
        raise PilotSelectionError(
            "smoke anchor manifest must contain 10 unique IDs"
        )
    unavailable_anchors = sorted(set(anchor_ids) - set(joined_ids))
    if unavailable_anchors:
        raise PilotSelectionError(
            f"unavailable smoke anchors: {unavailable_anchors}"
        )

    challenge_ids = sorted(
        candidate_id
        for candidate_id in joined_ids
        if "PRINCIPLE-CHALLENGE" in requirement_sets[candidate_id]
    )
    if (
        len(challenge_ids)
        != PRINCIPLE_MINIMUMS["PRINCIPLE-CHALLENGE"]
    ):
        raise PilotSelectionError(
            "Challenge census changed; expected exactly eight eligible "
            "candidates"
        )
    mandatory = list(dict.fromkeys([*anchor_ids, *challenge_ids]))
    mandatory_families = [
        features[candidate_id]["family"] for candidate_id in mandatory
    ]
    if len(mandatory_families) != len(set(mandatory_families)):
        raise PilotSelectionError(
            "mandatory anchors and Challenge census repeat a family"
        )

    best: tuple[
        tuple[int, int], list[str], dict[str, Any]
    ] | None = None
    for restart in range(restarts):
        rng = random.Random(seed + restart)
        selected = list(mandatory)
        selected_set = set(selected)
        used_families = set(mandatory_families)
        while len(selected) < PILOT_SIZE:
            coverage = _coverage(selected, features)
            lessons = {
                features[candidate_id]["lesson_key"]
                for candidate_id in selected
            }
            options: list[tuple[float, str]] = []
            for candidate_id in joined_ids:
                feature = features[candidate_id]
                if (
                    candidate_id in selected_set
                    or feature["family"] in used_families
                    or coverage["grade"].get(feature["grade"], 0)
                    >= GRADE_TARGETS[feature["grade"]]
                ):
                    continue
                score = sum(
                    16
                    for principle_id in feature["principles"]
                    if coverage["principle"].get(principle_id, 0)
                    < PRINCIPLE_MINIMUMS[principle_id]
                )
                score += 8 * (
                    coverage["history"].get(feature["history"], 0)
                    < HISTORY_MINIMUMS[feature["history"]]
                )
                score += 8 * (
                    coverage["bloom"].get(feature["bloom"], 0)
                    < BLOOM_MINIMUMS[feature["bloom"]]
                )
                score += 8 * (
                    coverage["set_size"].get(feature["set_size"], 0)
                    < SET_SIZE_MINIMUMS[feature["set_size"]]
                )
                score += 5 * (feature["lesson_key"] not in lessons)
                options.append((score + rng.random(), candidate_id))
            if not options:
                break
            _, chosen = max(options)
            selected.append(chosen)
            selected_set.add(chosen)
            used_families.add(features[chosen]["family"])
        if len(selected) != PILOT_SIZE:
            continue
        coverage = _coverage(selected, features)
        rank = (_deficit(coverage), -coverage["lesson_count"])
        if best is None or rank < best[0]:
            best = (rank, selected, coverage)

    if best is None or best[0][0] != 0:
        raise PilotSelectionError(
            f"coverage search failed after {restarts} deterministic "
            "restarts"
        )
    selected = sorted(best[1])
    coverage = _coverage(selected, features)
    if not set(anchor_ids) <= set(selected):
        raise PilotSelectionError("smoke anchors missing after selection")
    if not set(challenge_ids) <= set(selected):
        raise PilotSelectionError(
            "Challenge census missing after selection"
        )
    if coverage["family_count"] != PILOT_SIZE:
        raise PilotSelectionError(
            "pilot must use 80 distinct raw-dialogue families"
        )

    return {
        "record_type": "benchmark_evaluation_pilot_candidate_manifest",
        "manifest_version": "pilot_80_v1",
        "candidate_count": PILOT_SIZE,
        "candidate_ids": selected,
        "smoke_anchor_candidate_ids": anchor_ids,
        "challenge_census_candidate_ids": challenge_ids,
        "selection_contract": {
            "sampling_role": (
                "coverage_oriented_not_population_representative"
            ),
            "grade_targets": GRADE_TARGETS,
            "principle_minimums": PRINCIPLE_MINIMUMS,
            "history_minimums": HISTORY_MINIMUMS,
            "bloom_group_minimums": BLOOM_MINIMUMS,
            "required_set_size_minimums": {
                str(key): value
                for key, value in SET_SIZE_MINIMUMS.items()
            },
            "minimum_distinct_grade_lessons": MIN_DISTINCT_LESSONS,
            "unique_family_required": True,
            "include_all_eligible_challenge_candidates": True,
            "include_smoke_anchors": True,
            "seed": seed,
            "deterministic_restarts": restarts,
        },
        "coverage": _plain_coverage(coverage),
        "input_sha256": {
            _portable(grounding_pool_csv): _sha256(grounding_pool_csv),
            _portable(analysis_json): _sha256(analysis_json),
            _portable(requirement_run_jsonl): _sha256(
                requirement_run_jsonl
            ),
            _portable(smoke_anchor_manifest): _sha256(
                smoke_anchor_manifest
            ),
        },
        "limitations": [
            "Challenge and Practice are deliberately oversampled; "
            "unweighted pilot rates are not population estimates.",
            "The active pilot has two unique base models across three "
            "target configurations; the LearnLM-prompted configuration "
            "uses the same Gemini 3.5 Flash model as the baseline.",
            "LearnLM is integrated into Gemini and is not a separate "
            "specialized-education model; the specialized-model panel "
            "requirement remains an operational gap.",
        ],
    }

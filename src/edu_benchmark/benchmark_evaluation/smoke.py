"""Prepare deterministic smoke-test requests from the eligible pool."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path
import random
from typing import Any, Sequence

from .config_builder import PRINCIPLE_ORDER
from .dialogue_transport import NormalizedConversation, build_native_conversation
from .instruction_bundle import load_instruction_bundle
from .prompt_builder import build_candidate_system_instruction


class SmokePreparationError(RuntimeError):
    """Raised when smoke inputs cannot be joined safely."""


REQUIRED_SCORE_THRESHOLD = 4


@dataclass(frozen=True)
class PreparedTutorRequest:
    """Exact target-tutor request plus orchestration-only identifiers."""

    benchmark_candidate_id: str
    grade: str
    required_principle_ids: tuple[str, ...]
    system_instruction: str
    system_instruction_hash: str
    instruction_bundle_version: str
    instruction_bundle_sha256: str
    conversation: NormalizedConversation
    request_hash: str

    def trace_fields(self) -> dict[str, Any]:
        """Return the exact human-reviewable prompt payload for persistence."""

        messages = self.conversation.as_list()
        return {
            "system_prompt": self.system_instruction,
            "user_prompt": messages[-1]["content"],
            "conversation_messages": messages,
            "input_hash": self.request_hash,
            "system_instruction_hash": self.system_instruction_hash,
            "messages_hash": self.conversation.sha256,
            "instruction_bundle_version": self.instruction_bundle_version,
            "instruction_bundle_sha256": self.instruction_bundle_sha256,
            "required_principle_ids": list(
                self.required_principle_ids
            ),
        }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _hash_request(
    system_instruction: str, conversation: NormalizedConversation
) -> str:
    payload = json.dumps(
        {
            "system_instruction": system_instruction,
            "messages": conversation.as_list(),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_required_principle_sets(
    path: Path,
) -> dict[str, tuple[str, ...]]:
    """Derive and verify the exact score>=4 principle set for each record."""

    requirement_sets: dict[str, tuple[str, ...]] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            candidate_id = str(row["benchmark_candidate_id"])
            score_rows = row["normalized_response"]["principle_scores"]
            stored_required = tuple(row["required_principle_set"])
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise SmokePreparationError(
                f"{path}:{line_number}: invalid requirement record"
            ) from exc
        if candidate_id in requirement_sets:
            raise SmokePreparationError(
                f"{path}:{line_number}: duplicate candidate {candidate_id}"
            )
        try:
            scores = {
                str(item["principle_id"]): int(item["requirement_score"])
                for item in score_rows
            }
        except (KeyError, TypeError, ValueError) as exc:
            raise SmokePreparationError(
                f"{candidate_id}: invalid principle scores"
            ) from exc
        if set(scores) != set(PRINCIPLE_ORDER) or any(
            score not in {1, 2, 3, 4, 5} for score in scores.values()
        ):
            raise SmokePreparationError(
                f"{candidate_id}: principle scores must cover six canonical "
                "principles on the 1-5 scale"
            )
        derived_required = tuple(
            principle_id
            for principle_id in PRINCIPLE_ORDER
            if scores[principle_id] >= REQUIRED_SCORE_THRESHOLD
        )
        if stored_required != derived_required:
            raise SmokePreparationError(
                f"{candidate_id}: required_principle_set does not equal the "
                "exact requirement_score>=4 set"
            )
        requirement_sets[candidate_id] = derived_required
    return requirement_sets


def prepare_tutor_requests(
    *,
    grounding_pool_csv: Path,
    analysis_json: Path,
    requirement_run_jsonl: Path,
    instruction_bundle_path: Path,
    max_candidates: int = 10,
    seed: int = 20260728,
    fixed_candidate_ids: Sequence[str] | None = None,
) -> list[PreparedTutorRequest]:
    """Build exact target-tutor requests for a fixed set or small smoke."""

    if not 1 <= max_candidates <= 1400:
        raise SmokePreparationError(
            "target run must contain 1–1,400 candidates"
        )
    if fixed_candidate_ids is None and max_candidates > 10:
        raise SmokePreparationError(
            "runs above 10 candidates require a locked candidate manifest"
        )
    candidates = {
        row["benchmark_candidate_id"]: row
        for row in _read_csv(grounding_pool_csv)
    }
    analysis = json.loads(analysis_json.read_text(encoding="utf-8"))
    eligible_ids = set(
        analysis["eligibility"]["candidate_ids"][
            "eligible_without_plan03_review"
        ]
    )
    requirement_sets = load_required_principle_sets(requirement_run_jsonl)

    joined_ids = sorted(
        candidate_id
        for candidate_id in eligible_ids
        if candidate_id in candidates
        and candidate_id in requirement_sets
        and requirement_sets[candidate_id]
    )
    if len(joined_ids) != 1400:
        raise SmokePreparationError(
            f"expected 1,400 joined eligible candidates, found {len(joined_ids)}"
        )

    if fixed_candidate_ids is not None:
        selected = list(fixed_candidate_ids)
        if len(selected) != max_candidates:
            raise SmokePreparationError(
                "fixed candidate count must equal max_candidates"
            )
        if len(selected) != len(set(selected)):
            raise SmokePreparationError(
                "fixed candidate IDs must be unique"
            )
        unavailable = sorted(set(selected) - set(joined_ids))
        if unavailable:
            raise SmokePreparationError(
                "fixed candidates are not eligible and fully joined: "
                f"{unavailable}"
            )
    else:
        rng = random.Random(seed)
        by_grade: dict[str, list[str]] = {
            "6": [],
            "7": [],
            "8": [],
            "9": [],
        }
        for candidate_id in joined_ids:
            by_grade[candidates[candidate_id]["grade"]].append(candidate_id)
        for grade_ids in by_grade.values():
            rng.shuffle(grade_ids)
            grade_ids.sort(
                key=lambda candidate_id: (
                    candidates[candidate_id]["conversation_history"] == "[]",
                    len(requirement_sets[candidate_id]),
                )
            )

        selected = []
        while len(selected) < max_candidates:
            advanced = False
            for grade in ("6", "7", "8", "9"):
                if by_grade[grade] and len(selected) < max_candidates:
                    selected.append(by_grade[grade].pop(0))
                    advanced = True
            if not advanced:
                break

    instruction_bundle = load_instruction_bundle(instruction_bundle_path)
    prepared: list[PreparedTutorRequest] = []
    for candidate_id in selected:
        row = candidates[candidate_id]
        required = requirement_sets[candidate_id]
        conversation = build_native_conversation(
            row["student_prompt"], row["conversation_history"]
        )
        system_instruction, system_hash = build_candidate_system_instruction(
            grade=row["grade"],
            lesson=row["lesson"],
            source_question=row["source_question"],
            required_principle_ids=required,
            instruction_bundle=instruction_bundle,
        )
        prepared.append(
            PreparedTutorRequest(
                benchmark_candidate_id=candidate_id,
                grade=row["grade"],
                required_principle_ids=required,
                system_instruction=system_instruction,
                system_instruction_hash=system_hash,
                instruction_bundle_version=(
                    instruction_bundle.bundle_version
                ),
                instruction_bundle_sha256=instruction_bundle.sha256,
                conversation=conversation,
                request_hash=_hash_request(system_instruction, conversation),
            )
        )
    return prepared

def prepare_smoke_requests(
    *,
    grounding_pool_csv: Path,
    analysis_json: Path,
    requirement_run_jsonl: Path,
    instruction_bundle_path: Path,
    max_candidates: int = 10,
    seed: int = 20260728,
    fixed_candidate_ids: Sequence[str] | None = None,
) -> list[PreparedTutorRequest]:
    """Preserve the original 1–10 candidate smoke-test contract."""

    if not 1 <= max_candidates <= 10:
        raise SmokePreparationError(
            "smoke sample must contain 1–10 candidates"
        )
    return prepare_tutor_requests(
        grounding_pool_csv=grounding_pool_csv,
        analysis_json=analysis_json,
        requirement_run_jsonl=requirement_run_jsonl,
        instruction_bundle_path=instruction_bundle_path,
        max_candidates=max_candidates,
        seed=seed,
        fixed_candidate_ids=fixed_candidate_ids,
    )


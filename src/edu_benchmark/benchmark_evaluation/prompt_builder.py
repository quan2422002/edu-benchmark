"""Deterministic tutor system-instruction construction."""

from __future__ import annotations

import hashlib
from typing import Sequence

from .instruction_bundle import InstructionBundle, PRINCIPLE_ORDER


class PromptBuildError(ValueError):
    """Raised when an instruction cannot be built safely."""


_FORBIDDEN_TUTOR_FIELDS = (
    "gold_answer",
    "gold_response",
    "benchmark_candidate_id",
    "sample_id",
    "requirement_score",
)


def build_candidate_system_instruction(
    *,
    grade: str,
    lesson: str,
    source_question: str,
    required_principle_ids: Sequence[str],
    instruction_bundle: InstructionBundle,
) -> tuple[str, str]:
    """Build a candidate-specific system instruction without evaluator-only fields."""

    values = {
        "grade": grade,
        "lesson": lesson,
        "source_question": source_question,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise PromptBuildError(f"{name} must be non-empty")
    if not required_principle_ids:
        raise PromptBuildError("at least one required principle is needed")
    unknown = [
        principle_id
        for principle_id in required_principle_ids
        if principle_id not in instruction_bundle.principles_by_id
    ]
    if unknown:
        raise PromptBuildError(f"unknown principle IDs: {unknown}")
    if len(required_principle_ids) != len(set(required_principle_ids)):
        raise PromptBuildError("required principle IDs must be unique")

    required = set(required_principle_ids)
    ordered = [
        principle_id
        for principle_id in PRINCIPLE_ORDER
        if principle_id in required
    ]
    principle_blocks = "\n\n".join(
        instruction_bundle.render_principle(principle_id)
        for principle_id in ordered
    )
    instruction = instruction_bundle.system_instruction_template.format(
        general_instruction=instruction_bundle.general_instruction,
        grade=grade.strip(),
        lesson=lesson.strip(),
        source_question=source_question.strip(),
        principle_blocks=principle_blocks,
        response_style_instruction=(
            instruction_bundle.response_style_instruction
        ),
    ).strip()
    lowered = instruction.casefold()
    leaked = [field for field in _FORBIDDEN_TUTOR_FIELDS if field in lowered]
    if leaked:
        raise PromptBuildError(f"tutor instruction leaks evaluator fields: {leaked}")
    digest = hashlib.sha256(instruction.encode("utf-8")).hexdigest()
    return instruction, digest

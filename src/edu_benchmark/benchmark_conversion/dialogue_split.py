"""Parse raw HNMU dialogues and split the final tutor response."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Mapping

TURN_PATTERN = re.compile(r"^\s*(HS|AI)\s*:\s?(.*)$")


class DialogueSplitError(ValueError):
    """Raised when a raw dialogue cannot be split without silent repair."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class DialogueTurn:
    """One parsed dialogue turn."""

    turn_index: int
    role: str
    content: str


def parse_dialogue_turns(dialogue: str) -> list[DialogueTurn]:
    """Parse HS/AI lines while preserving turn content and order."""

    if not dialogue or not dialogue.strip():
        raise DialogueSplitError("empty_dialogue", "Dialogue is empty")
    turns: list[DialogueTurn] = []
    current_role: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_role is not None:
            turns.append(
                DialogueTurn(
                    turn_index=len(turns) + 1,
                    role="student" if current_role == "HS" else "tutor",
                    content="\n".join(current_lines),
                )
            )

    for line_number, line in enumerate(dialogue.splitlines(), start=1):
        match = TURN_PATTERN.match(line)
        if match:
            flush()
            current_role = match.group(1)
            current_lines = [match.group(2)]
        elif current_role is None:
            raise DialogueSplitError(
                "unknown_turn_label",
                f"Line {line_number} does not begin with HS: or AI:",
            )
        else:
            current_lines.append(line)
    flush()

    if not turns:
        raise DialogueSplitError("no_turns", "No HS:/AI: turns were found")
    if turns[0].role != "student":
        raise DialogueSplitError("first_turn_not_student", "The first turn must be HS")
    if turns[-1].role != "tutor":
        raise DialogueSplitError("last_turn_not_tutor", "The last turn must be AI")
    for previous, current in zip(turns, turns[1:]):
        if previous.role == current.role:
            raise DialogueSplitError(
                "non_alternating_roles",
                f"Turns {previous.turn_index} and {current.turn_index} have the same role",
            )
    return turns


def split_final_tutor_response_candidate(row: Mapping[str, str]) -> dict[str, str]:
    """Create one deterministic candidate using the final AI turn as gold."""

    conversion_dialogue = str(
        row.get("conversion_dialogue", "") or row.get("raw_dialogue", "")
    )
    turns = parse_dialogue_turns(conversion_dialogue)
    target = turns[-1]
    history = [
        {"turn_index": turn.turn_index, "role": turn.role, "content": turn.content}
        for turn in turns[1:-1]
    ]
    sample_id = str(row["sample_id"])
    candidate = {
        "benchmark_candidate_id": f"BC-{sample_id}-FINAL",
        "sample_id": sample_id,
        "source_batch": str(row.get("source_batch", "")),
        "source_file": str(row.get("source_file", "")),
        "source_row_number": str(row.get("source_row_number", "")),
        "grade": str(row.get("grade", "")),
        "lesson": str(row.get("lesson", "")),
        "position": str(row.get("position", "")),
        "bloom_level": str(row.get("bloom_level", "")),
        "student_prompt": turns[0].content,
        "conversation_history": json.dumps(history, ensure_ascii=False),
        "gold_response": target.content,
        "gold_answer": str(row.get("answer_sgv", "")),
        "raw_dialogue": str(row.get("raw_dialogue", "")),
        "conversion_dialogue": conversion_dialogue,
        "dialogue_correction_ids": str(row.get("dialogue_correction_ids", "[]")),
        "target_tutor_turn_index": str(target.turn_index),
        "split_strategy": "final_tutor_response",
        "raw_audit_blocking_evidence_fragment_ids": str(
            row.get("raw_audit_blocking_evidence_fragment_ids", "")
        ),
        "raw_audit_all_evidence_fragment_ids": str(
            row.get("raw_audit_all_evidence_fragment_ids", "")
        ),
    }
    return candidate

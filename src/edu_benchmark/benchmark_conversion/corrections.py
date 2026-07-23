"""Traceable, hash-guarded dialogue corrections approved by a human reviewer."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

from .dialogue_split import DialogueSplitError, DialogueTurn, TURN_PATTERN, parse_dialogue_turns

CORRECTION_COLUMNS = [
    "correction_id",
    "sample_id",
    "operation",
    "target_turn_index",
    "secondary_turn_index",
    "replacement_role",
    "original_dialogue_sha256",
    "decision_source",
    "reason",
]
ALLOWED_OPERATIONS = {"merge_adjacent_turns", "relabel_turn"}


def load_dialogue_corrections(path: Path) -> dict[str, list[dict[str, str]]]:
    """Load correction instructions grouped by sample ID."""

    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != CORRECTION_COLUMNS:
            raise ValueError(f"Unexpected dialogue-correction schema: {reader.fieldnames}")
        rows = list(reader)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    correction_ids: set[str] = set()
    for row in rows:
        correction_id = row["correction_id"].strip()
        sample_id = row["sample_id"].strip()
        operation = row["operation"].strip()
        if not correction_id or not sample_id:
            raise ValueError("Dialogue correction is missing correction_id or sample_id")
        if correction_id in correction_ids:
            raise ValueError(f"Duplicate correction_id: {correction_id}")
        if operation not in ALLOWED_OPERATIONS:
            raise ValueError(f"Unknown dialogue correction operation: {operation}")
        correction_ids.add(correction_id)
        grouped[sample_id].append(dict(row))
    return dict(grouped)


def _parse_turns_without_sequence_validation(dialogue: str) -> list[DialogueTurn]:
    turns: list[DialogueTurn] = []
    role: str | None = None
    content_lines: list[str] = []

    def flush() -> None:
        if role is not None:
            turns.append(
                DialogueTurn(
                    turn_index=len(turns) + 1,
                    role="student" if role == "HS" else "tutor",
                    content="\n".join(content_lines),
                )
            )

    for line_number, line in enumerate(dialogue.splitlines(), start=1):
        match = TURN_PATTERN.match(line)
        if match:
            flush()
            role = match.group(1)
            content_lines = [match.group(2)]
        elif role is None:
            raise DialogueSplitError(
                "unknown_turn_label",
                f"Line {line_number} does not begin with HS: or AI:",
            )
        else:
            content_lines.append(line)
    flush()
    return turns


def _render_turns(turns: Sequence[DialogueTurn]) -> str:
    labels = {"student": "HS", "tutor": "AI"}
    return "\n".join(f"{labels[turn.role]}: {turn.content}" for turn in turns)


def apply_dialogue_corrections(
    dialogue: str, corrections: Sequence[Mapping[str, str]]
) -> tuple[str, list[str]]:
    """Apply explicit corrections after verifying the immutable source hash."""

    if not corrections:
        return dialogue, []
    original_hash = hashlib.sha256(dialogue.encode("utf-8")).hexdigest()
    turns = _parse_turns_without_sequence_validation(dialogue)
    applied_ids: list[str] = []

    for correction in corrections:
        expected_hash = str(correction["original_dialogue_sha256"]).strip()
        if expected_hash != original_hash:
            raise ValueError(
                f"Source dialogue hash mismatch for {correction['correction_id']}: "
                f"expected {expected_hash}, got {original_hash}"
            )
        operation = str(correction["operation"]).strip()
        target_index = int(str(correction["target_turn_index"]).strip())
        if target_index < 1 or target_index > len(turns):
            raise ValueError(f"Correction target turn is out of range: {target_index}")
        target_position = target_index - 1
        replacement_role = str(correction["replacement_role"]).strip()
        replacement = {"HS": "student", "AI": "tutor"}.get(replacement_role)
        if replacement is None:
            raise ValueError(f"Unknown replacement_role: {replacement_role}")

        if operation == "merge_adjacent_turns":
            secondary_index = int(str(correction["secondary_turn_index"]).strip())
            if secondary_index != target_index + 1:
                raise ValueError("merge_adjacent_turns requires consecutive turn indices")
            secondary_position = secondary_index - 1
            if secondary_position >= len(turns):
                raise ValueError("Secondary correction turn is out of range")
            if (
                turns[target_position].role != replacement
                or turns[secondary_position].role != replacement
            ):
                raise ValueError("Merged turns do not match replacement_role")
            turns[target_position : secondary_position + 1] = [
                DialogueTurn(
                    turn_index=target_index,
                    role=replacement,
                    content=(
                        f"{turns[target_position].content}\n"
                        f"{turns[secondary_position].content}"
                    ),
                )
            ]
        elif operation == "relabel_turn":
            turns[target_position] = DialogueTurn(
                turn_index=target_index,
                role=replacement,
                content=turns[target_position].content,
            )
        else:  # pragma: no cover - guarded by the loader
            raise ValueError(f"Unsupported correction operation: {operation}")
        turns = [
            DialogueTurn(index, turn.role, turn.content)
            for index, turn in enumerate(turns, start=1)
        ]
        applied_ids.append(str(correction["correction_id"]).strip())

    corrected = _render_turns(turns)
    parse_dialogue_turns(corrected)
    return corrected, applied_ids

"""Strict native-message transport for tutor benchmark candidates."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence


class DialogueTransportError(ValueError):
    """Raised when a candidate cannot be represented as a native dialogue."""


@dataclass(frozen=True)
class ChatMessage:
    """Provider-neutral chat message."""

    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class NormalizedConversation:
    """Validated message sequence ending immediately before the tutor target."""

    messages: tuple[ChatMessage, ...]
    sha256: str

    def as_list(self) -> list[dict[str, str]]:
        return [message.as_dict() for message in self.messages]


def _canonical_hash(messages: Sequence[ChatMessage]) -> str:
    payload = json.dumps(
        [message.as_dict() for message in messages],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_history(value: str | Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise DialogueTransportError("conversation_history is not valid JSON") from exc
    else:
        parsed = value
    if not isinstance(parsed, list):
        raise DialogueTransportError("conversation_history must be a JSON list")
    if not all(isinstance(turn, Mapping) for turn in parsed):
        raise DialogueTransportError("every history turn must be an object")
    return list(parsed)


def build_native_conversation(
    student_prompt: str,
    conversation_history: str | Sequence[Mapping[str, Any]],
) -> NormalizedConversation:
    """Build a strict user/assistant sequence without flattening history into text."""

    if not isinstance(student_prompt, str) or not student_prompt.strip():
        raise DialogueTransportError("student_prompt must be non-empty")

    messages: list[ChatMessage] = [ChatMessage("user", student_prompt)]
    prior_source_role = "student"
    prior_turn_index: int | None = None

    for turn in _parse_history(conversation_history):
        turn_index = turn.get("turn_index")
        role = turn.get("role")
        content = turn.get("content")
        if not isinstance(turn_index, int) or isinstance(turn_index, bool):
            raise DialogueTransportError("turn_index must be an integer")
        if prior_turn_index is not None and turn_index <= prior_turn_index:
            raise DialogueTransportError("turn_index must increase strictly")
        if role not in {"student", "tutor"}:
            raise DialogueTransportError("history role must be student or tutor")
        if role == prior_source_role:
            raise DialogueTransportError("dialogue roles must alternate")
        if not isinstance(content, str) or not content.strip():
            raise DialogueTransportError("history content must be non-empty")
        native_role = "user" if role == "student" else "assistant"
        messages.append(ChatMessage(native_role, content))
        prior_source_role = role
        prior_turn_index = turn_index

    if messages[0].role != "user" or messages[-1].role != "user":
        raise DialogueTransportError(
            "candidate context must start and end with a student/user turn"
        )
    return NormalizedConversation(tuple(messages), _canonical_hash(messages))

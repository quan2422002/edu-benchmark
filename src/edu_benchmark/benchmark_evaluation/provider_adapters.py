"""Provider-native request adapters that preserve dialogue boundaries exactly."""

from __future__ import annotations

from typing import Any, Sequence

from .dialogue_transport import ChatMessage


class ProviderAdapterError(ValueError):
    """Raised when an adapter receives an invalid normalized message."""


def _validate(messages: Sequence[ChatMessage], system_instruction: str) -> None:
    if not system_instruction.strip():
        raise ProviderAdapterError("system_instruction must be non-empty")
    if not messages or messages[0].role != "user" or messages[-1].role != "user":
        raise ProviderAdapterError("messages must start and end with user")
    for index, message in enumerate(messages):
        if message.role not in {"user", "assistant"} or not message.content.strip():
            raise ProviderAdapterError(f"invalid normalized message at index {index}")
        if index and messages[index - 1].role == message.role:
            raise ProviderAdapterError("normalized roles must alternate")


def to_gemini_request(
    system_instruction: str, messages: Sequence[ChatMessage]
) -> dict[str, Any]:
    """Map assistant to Gemini's native model role."""

    _validate(messages, system_instruction)
    return {
        "system_instruction": system_instruction,
        "contents": [
            {
                "role": "model" if message.role == "assistant" else "user",
                "parts": [{"text": message.content}],
            }
            for message in messages
        ],
    }


def to_anthropic_request(
    system_instruction: str, messages: Sequence[ChatMessage]
) -> dict[str, Any]:
    """Map to Anthropic Messages API while keeping system separate."""

    _validate(messages, system_instruction)
    return {
        "system": system_instruction,
        "messages": [message.as_dict() for message in messages],
    }


def to_openai_compatible_request(
    system_instruction: str, messages: Sequence[ChatMessage]
) -> dict[str, Any]:
    """Map to the native system/user/assistant message contract."""

    _validate(messages, system_instruction)
    return {
        "messages": [
            {"role": "system", "content": system_instruction},
            *[message.as_dict() for message in messages],
        ]
    }

"""Reusable benchmark evaluation configuration and transport."""

from .dialogue_transport import (
    ChatMessage,
    DialogueTransportError,
    NormalizedConversation,
    build_native_conversation,
)
from .instruction_bundle import (
    InstructionBundle,
    InstructionBundleError,
    load_instruction_bundle,
)
from .prompt_builder import build_candidate_system_instruction

__all__ = [
    "ChatMessage",
    "DialogueTransportError",
    "InstructionBundle",
    "InstructionBundleError",
    "NormalizedConversation",
    "build_candidate_system_instruction",
    "build_native_conversation",
    "load_instruction_bundle",
]

"""Provider-neutral model invocation contracts and lazy provider registry."""

from .contracts import (
    GenerationSettings,
    ModelMessage,
    ModelProvider,
    ModelRequest,
    ModelResponse,
    ProviderCallError,
    StructuredOutput,
    TokenUsage,
)
from .ollama import OllamaConfigurationError, OllamaProvider
from .registry import ProviderRegistry, create_provider

__all__ = [
    "GenerationSettings",
    "ModelMessage",
    "ModelProvider",
    "ModelRequest",
    "ModelResponse",
    "OllamaConfigurationError",
    "OllamaProvider",
    "ProviderCallError",
    "ProviderRegistry",
    "StructuredOutput",
    "TokenUsage",
    "create_provider",
]

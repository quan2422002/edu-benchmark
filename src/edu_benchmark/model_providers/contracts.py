"""Provider-neutral request, response, and error contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable


@dataclass(frozen=True)
class ModelMessage:
    """One provider-neutral conversation message."""

    role: str
    content: str

    def __post_init__(self) -> None:
        normalized_role = self.role.strip().lower()
        if normalized_role not in {"user", "assistant"}:
            raise ValueError(f"unsupported model-message role: {self.role}")
        if not self.content.strip():
            raise ValueError("model-message content must be non-empty")
        object.__setattr__(self, "role", normalized_role)

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class GenerationSettings:
    """Generation controls shared across providers when supported."""

    max_output_tokens: int
    temperature: float | None = None
    top_p: float | None = None
    seed: int | None = None
    timeout_seconds: float = 180.0
    thinking_budget: int | None = None
    thinking_level: str | None = None
    include_thoughts: bool = False
    reasoning_effort: str | None = None

    def __post_init__(self) -> None:
        if self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")
        if self.thinking_budget is not None and self.thinking_level is not None:
            raise ValueError(
                "thinking_budget and thinking_level are mutually exclusive"
            )
        if self.thinking_level is not None:
            normalized_level = self.thinking_level.strip().upper()
            if normalized_level not in {"MINIMAL", "LOW", "MEDIUM", "HIGH"}:
                raise ValueError(f"unsupported thinking_level: {self.thinking_level}")
            object.__setattr__(self, "thinking_level", normalized_level)
        if self.reasoning_effort is not None:
            normalized_effort = self.reasoning_effort.strip().lower()
            if normalized_effort not in {"none", "low", "medium", "high", "xhigh"}:
                raise ValueError(
                    f"unsupported reasoning_effort: {self.reasoning_effort}"
                )
            object.__setattr__(self, "reasoning_effort", normalized_effort)


@dataclass(frozen=True)
class StructuredOutput:
    """Provider-neutral structured-output request."""

    name: str
    schema: Mapping[str, Any]
    mime_type: str = "application/json"
    strict: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("structured-output name must be non-empty")
        if not self.schema:
            raise ValueError("structured-output schema must be non-empty")


@dataclass(frozen=True)
class ModelRequest:
    """A task-neutral request passed from a workflow to a model provider."""

    backend: str
    model: str
    messages: tuple[ModelMessage, ...]
    system_instruction: str = ""
    generation: GenerationSettings = field(
        default_factory=lambda: GenerationSettings(max_output_tokens=4096)
    )
    structured_output: StructuredOutput | None = None
    provider_options: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_backend = self.backend.strip().lower().replace("-", "_")
        if not normalized_backend:
            raise ValueError("backend must be non-empty")
        if not self.model.strip():
            raise ValueError("model must be non-empty")
        if not self.messages:
            raise ValueError("messages must not be empty")
        object.__setattr__(self, "backend", normalized_backend)


@dataclass(frozen=True)
class TokenUsage:
    """Normalized token usage plus the lossless provider metadata."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelResponse:
    """A normalized provider response independent of benchmark workflows."""

    text: str
    backend: str
    model: str
    model_version: str = ""
    response_id: str = ""
    finish_reason: str = "UNKNOWN"
    usage: TokenUsage = field(default_factory=TokenUsage)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("model response text must be non-empty")


class ProviderCallError(RuntimeError):
    """Normalized provider failure with retry and transport metadata."""

    def __init__(
        self,
        message: str,
        *,
        backend: str,
        retryable: bool,
        http_status: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.backend = backend
        self.retryable = retryable
        self.http_status = http_status
        self.response_body = response_body


@runtime_checkable
class ModelProvider(Protocol):
    """Minimal synchronous model-provider boundary used by workflows."""

    backend: str

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate one normalized response."""

    def close(self) -> None:
        """Release provider-owned resources."""

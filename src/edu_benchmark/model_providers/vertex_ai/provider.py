"""Google Gen AI SDK transport for Vertex AI."""

from __future__ import annotations

import threading
from typing import Any

import google.auth
from google import genai
from google.auth.exceptions import DefaultCredentialsError
from google.genai import types

from ..contracts import (
    ModelRequest,
    ModelResponse,
    ProviderCallError,
    TokenUsage,
)


class VertexAIConfigurationError(RuntimeError):
    """Raised when Vertex AI configuration or ADC is unavailable."""


def normalize_finish_reason(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    name = getattr(value, "name", None)
    text = name if isinstance(name, str) and name.strip() else str(
        getattr(value, "value", value)
    )
    return text.rsplit(".", 1)[-1].strip().upper() or "UNKNOWN"


def _is_retryable(exc: BaseException, status: int | None) -> bool:
    if status in {408, 409, 425, 429} or (
        isinstance(status, int) and 500 <= status <= 599
    ):
        return True
    retryable_names = {
        "ConnectError",
        "ConnectTimeout",
        "DeadlineExceeded",
        "NetworkError",
        "PoolTimeout",
        "ReadTimeout",
        "ResourceExhausted",
        "ServiceUnavailable",
        "TimeoutException",
    }
    retryable_messages = (
        "temporary failure in name resolution",
        "name or service not known",
        "connection reset",
        "connection refused",
        "network is unreachable",
        "temporarily unavailable",
    )
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if type(current).__name__ in retryable_names:
            return True
        if any(value in str(current).lower() for value in retryable_messages):
            return True
        current = current.__cause__ or current.__context__
    return False


class VertexAIProvider:
    """Task-neutral Vertex AI provider with thread-local SDK clients."""

    backend = "vertex_ai"

    def __init__(
        self,
        *,
        project: str,
        location: str,
        client: Any | None = None,
        credentials: Any | None = None,
    ) -> None:
        self.project = project.strip()
        self.location = location.strip()
        if not self.project:
            raise VertexAIConfigurationError("Vertex project must not be empty")
        if not self.location:
            raise VertexAIConfigurationError("Vertex location must not be empty")
        self._injected_client = client
        if client is None and credentials is None:
            try:
                credentials, _ = google.auth.default(
                    quota_project_id=self.project
                )
            except DefaultCredentialsError as exc:
                raise VertexAIConfigurationError(
                    "Application Default Credentials are unavailable"
                ) from exc
        self._credentials = credentials
        self._thread_local = threading.local()
        self._clients: list[Any] = []
        self._clients_lock = threading.Lock()

    def _new_client(self, timeout_seconds: float) -> Any:
        client = genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location,
            credentials=self._credentials,
            http_options=types.HttpOptions(
                api_version="v1", timeout=int(timeout_seconds * 1000)
            ),
        )
        with self._clients_lock:
            self._clients.append(client)
        return client

    def _client(self, timeout_seconds: float) -> Any:
        if self._injected_client is not None:
            return self._injected_client
        client = getattr(self._thread_local, "client", None)
        client_timeout = getattr(self._thread_local, "timeout_seconds", None)
        if client is None or client_timeout != timeout_seconds:
            client = self._new_client(timeout_seconds)
            self._thread_local.client = client
            self._thread_local.timeout_seconds = timeout_seconds
        return client

    @staticmethod
    def _contents(request: ModelRequest) -> str | list[dict[str, Any]]:
        if len(request.messages) == 1 and request.messages[0].role == "user":
            return request.messages[0].content
        return [
            {
                "role": "model" if message.role == "assistant" else "user",
                "parts": [{"text": message.content}],
            }
            for message in request.messages
        ]

    @staticmethod
    def _config(request: ModelRequest) -> Any:
        generation = request.generation
        kwargs: dict[str, Any] = {
            "max_output_tokens": generation.max_output_tokens,
        }
        if request.system_instruction:
            kwargs["system_instruction"] = request.system_instruction
        if generation.seed is not None:
            kwargs["seed"] = generation.seed
        if generation.temperature is not None:
            kwargs["temperature"] = generation.temperature
        if generation.top_p is not None:
            kwargs["top_p"] = generation.top_p
        thinking: dict[str, Any] = {"include_thoughts": generation.include_thoughts}
        if generation.thinking_budget is not None:
            thinking["thinking_budget"] = generation.thinking_budget
        if generation.thinking_level is not None:
            thinking["thinking_level"] = getattr(
                types.ThinkingLevel, generation.thinking_level
            )
        if generation.thinking_budget is not None or generation.thinking_level is not None:
            kwargs["thinking_config"] = types.ThinkingConfig(**thinking)
        if request.structured_output is not None:
            kwargs["response_mime_type"] = request.structured_output.mime_type
            kwargs["response_json_schema"] = dict(
                request.structured_output.schema
            )
        kwargs.update(dict(request.provider_options))
        return types.GenerateContentConfig(**kwargs)

    def generate(self, request: ModelRequest) -> ModelResponse:
        if request.backend not in {"vertex", "vertex_ai", "google_vertex"}:
            raise ValueError(
                f"VertexAIProvider cannot handle backend {request.backend}"
            )
        try:
            response = self._client(
                request.generation.timeout_seconds
            ).models.generate_content(
                model=request.model,
                contents=self._contents(request),
                config=self._config(request),
            )
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if not isinstance(status, int):
                code = getattr(exc, "code", None)
                status = code if isinstance(code, int) else None
            raise ProviderCallError(
                f"Vertex AI call failed: {exc}",
                backend=self.backend,
                retryable=_is_retryable(exc, status),
                http_status=status,
            ) from exc
        candidates = getattr(response, "candidates", None) or []
        finish_reason = normalize_finish_reason(
            getattr(candidates[0], "finish_reason", None) if candidates else None
        )
        try:
            text = response.text
        except (AttributeError, ValueError):
            text = ""
        if not isinstance(text, str) or not text.strip():
            raise ProviderCallError(
                f"Vertex AI returned an empty response ({finish_reason})",
                backend=self.backend,
                retryable=True,
            )
        usage = getattr(response, "usage_metadata", None)
        usage_dict = (
            usage.model_dump(mode="json", exclude_none=True)
            if usage is not None and hasattr(usage, "model_dump")
            else {}
        )
        input_tokens = int(usage_dict.get("prompt_token_count", 0) or 0)
        output_tokens = int(
            (usage_dict.get("candidates_token_count", 0) or 0)
            + (usage_dict.get("thoughts_token_count", 0) or 0)
        )
        return ModelResponse(
            text=text,
            backend=self.backend,
            model=request.model,
            model_version=str(getattr(response, "model_version", "") or request.model),
            response_id=str(getattr(response, "response_id", "") or ""),
            finish_reason=finish_reason,
            usage=TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=int(
                    usage_dict.get("total_token_count", input_tokens + output_tokens)
                    or input_tokens + output_tokens
                ),
                metadata=usage_dict,
            ),
        )

    def close(self) -> None:
        if self._injected_client is not None:
            close = getattr(self._injected_client, "close", None)
            if callable(close):
                close()
            return
        with self._clients_lock:
            clients = list(self._clients)
            self._clients.clear()
        for client in clients:
            close = getattr(client, "close", None)
            if callable(close):
                close()

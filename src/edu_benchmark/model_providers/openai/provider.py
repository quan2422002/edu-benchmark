"""OpenAI Responses API transport for the shared provider boundary."""

from __future__ import annotations

import json
from typing import Any

import openai
from openai import OpenAI

from ..contracts import (
    ModelRequest,
    ModelResponse,
    ProviderCallError,
    TokenUsage,
)


class OpenAIConfigurationError(RuntimeError):
    """Raised when OpenAI provider configuration is incomplete."""


def _is_retryable_status(status: int | None) -> bool:
    return status in {408, 409, 425, 429} or (
        isinstance(status, int) and 500 <= status <= 599
    )


def _response_body(response: Any) -> str:
    dump = getattr(response, "model_dump", None)
    if callable(dump):
        try:
            return json.dumps(
                dump(mode="json", exclude_none=True), ensure_ascii=False
            )[:8000]
        except (TypeError, ValueError):
            pass
    return str(response)[:8000]


class OpenAIProvider:
    """Task-neutral OpenAI Responses API provider."""

    backend = "openai"

    def __init__(
        self,
        *,
        api_key: str = "",
        client: Any | None = None,
        timeout_seconds: float = 180.0,
    ) -> None:
        if client is None and not api_key.strip():
            raise OpenAIConfigurationError("OpenAI API key must be non-empty")
        self._client = client or OpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=0,
        )

    @staticmethod
    def _input(request: ModelRequest) -> str | list[dict[str, str]]:
        if len(request.messages) == 1 and request.messages[0].role == "user":
            return request.messages[0].content
        return [message.as_dict() for message in request.messages]

    def generate(self, request: ModelRequest) -> ModelResponse:
        if request.backend not in {"openai", "openai_api"}:
            raise ValueError(
                f"OpenAIProvider cannot handle backend {request.backend}"
            )
        generation = request.generation
        kwargs: dict[str, Any] = {
            "model": request.model,
            "input": self._input(request),
            "max_output_tokens": generation.max_output_tokens,
            "store": False,
            "truncation": "disabled",
        }
        if request.system_instruction:
            kwargs["instructions"] = request.system_instruction
        if generation.reasoning_effort is not None:
            kwargs["reasoning"] = {"effort": generation.reasoning_effort}
        if generation.temperature is not None:
            kwargs["temperature"] = generation.temperature
        if generation.top_p is not None:
            kwargs["top_p"] = generation.top_p
        if request.structured_output is not None:
            kwargs["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": request.structured_output.name,
                    "schema": dict(request.structured_output.schema),
                    "strict": request.structured_output.strict,
                }
            }
        kwargs.update(dict(request.provider_options))
        try:
            response = self._client.responses.create(**kwargs)
        except openai.APIStatusError as exc:
            status = getattr(exc, "status_code", None)
            raise ProviderCallError(
                f"OpenAI HTTP {status}: {exc}",
                backend=self.backend,
                retryable=_is_retryable_status(status),
                http_status=status,
                response_body=str(getattr(exc, "response", "") or "")[:8000],
            ) from exc
        except (openai.APIConnectionError, openai.APITimeoutError) as exc:
            raise ProviderCallError(
                f"OpenAI transport error: {exc}",
                backend=self.backend,
                retryable=True,
            ) from exc
        except openai.OpenAIError as exc:
            raise ProviderCallError(
                f"OpenAI API error: {exc}",
                backend=self.backend,
                retryable=False,
            ) from exc
        status = str(getattr(response, "status", "") or "").lower()
        incomplete = getattr(response, "incomplete_details", None)
        incomplete_reason = str(getattr(incomplete, "reason", "") or "").upper()
        finish_reason = (
            "STOP"
            if status == "completed"
            else incomplete_reason or status.upper() or "UNKNOWN"
        )
        text = str(getattr(response, "output_text", "") or "")
        if not text.strip():
            raise ProviderCallError(
                f"OpenAI returned an empty response ({finish_reason})",
                backend=self.backend,
                retryable=status in {"in_progress", "queued"},
                response_body=_response_body(response),
            )
        usage = getattr(response, "usage", None)
        usage_dict = (
            usage.model_dump(mode="json", exclude_none=True)
            if usage is not None and hasattr(usage, "model_dump")
            else {}
        )
        input_tokens = int(usage_dict.get("input_tokens", 0) or 0)
        output_tokens = int(usage_dict.get("output_tokens", 0) or 0)
        return ModelResponse(
            text=text,
            backend=self.backend,
            model=request.model,
            model_version=str(getattr(response, "model", "") or request.model),
            response_id=str(getattr(response, "id", "") or ""),
            finish_reason=finish_reason,
            usage=TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=int(
                    usage_dict.get("total_tokens", input_tokens + output_tokens)
                    or input_tokens + output_tokens
                ),
                metadata=usage_dict,
            ),
        )

    def close(self) -> None:
        close = getattr(self._client, "close", None)
        if callable(close):
            close()

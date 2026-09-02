"""Local Ollama HTTP transport for the shared model-provider boundary."""

from __future__ import annotations

import hashlib
import json
import socket
from collections.abc import Callable, Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ..contracts import (
    ModelRequest,
    ModelResponse,
    ProviderCallError,
    TokenUsage,
)


class OllamaConfigurationError(RuntimeError):
    """Raised when the local Ollama endpoint or digest is unsafe or invalid."""


_RETRYABLE_HTTP_STATUSES = {408, 409, 425, 429}
_ALLOWED_PROVIDER_OPTIONS = {
    "keep_alive",
    "logprobs",
    "options",
    "think",
    "top_logprobs",
}
_RESERVED_OLLAMA_OPTIONS = {"num_predict", "seed", "temperature", "top_p"}


def _normalize_digest(value: str | None) -> str:
    if value is None or not value.strip():
        return ""
    normalized = value.strip().lower()
    if normalized.startswith("sha256:"):
        normalized = normalized.removeprefix("sha256:")
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise OllamaConfigurationError(
            "expected_model_digest must be a 64-character SHA-256 digest"
        )
    return normalized


def _safe_nonnegative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(parsed, 0)


def _finish_reason(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"stop", "completed"}:
        return "STOP"
    if normalized in {"length", "max_tokens", "token_limit"}:
        return "MAX_TOKENS"
    return normalized.upper() or "UNKNOWN"


class OllamaProvider:
    """Task-neutral provider for a loopback-bound Ollama server."""

    backend = "ollama"

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11436",
        expected_model_digest: str | None = None,
        expected_server_version: str | None = None,
        allow_remote: bool = False,
        default_timeout_seconds: float = 30.0,
        max_response_bytes: int = 16 * 1024 * 1024,
        urlopen_fn: Callable[..., Any] = urlopen,
    ) -> None:
        normalized_url = base_url.strip().rstrip("/")
        parsed = urlparse(normalized_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise OllamaConfigurationError("base_url must be an absolute HTTP(S) URL")
        if (
            parsed.username
            or parsed.password
            or parsed.path not in {"", "/"}
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            raise OllamaConfigurationError(
                "base_url must not contain credentials, a path, query parameters, "
                "or fragments"
            )
        loopback_hosts = {"127.0.0.1", "::1", "localhost"}
        if not allow_remote and parsed.hostname.lower() not in loopback_hosts:
            raise OllamaConfigurationError(
                "non-loopback Ollama endpoints require allow_remote=True"
            )
        if default_timeout_seconds <= 0:
            raise OllamaConfigurationError("default_timeout_seconds must be positive")
        if max_response_bytes <= 0:
            raise OllamaConfigurationError("max_response_bytes must be positive")
        self.base_url = normalized_url
        self.expected_model_digest = _normalize_digest(expected_model_digest)
        self.expected_server_version = str(expected_server_version or "").strip()
        self.default_timeout_seconds = float(default_timeout_seconds)
        self.max_response_bytes = int(max_response_bytes)
        self._urlopen = urlopen_fn

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            try:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "Ollama request payload must be JSON serializable"
                ) from exc
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}", data=body, headers=headers, method=method
        )
        timeout = timeout_seconds or self.default_timeout_seconds
        try:
            with self._urlopen(request, timeout=timeout) as response:
                raw = response.read(self.max_response_bytes + 1)
                status = getattr(response, "status", 200)
        except HTTPError as exc:
            response_body = exc.read(8001).decode("utf-8", errors="replace")[:8000]
            status = int(exc.code)
            raise ProviderCallError(
                f"Ollama HTTP {status}",
                backend=self.backend,
                retryable=(
                    status in _RETRYABLE_HTTP_STATUSES or 500 <= status <= 599
                ),
                http_status=status,
                response_body=response_body,
            ) from exc
        except (URLError, TimeoutError, socket.timeout, ConnectionError) as exc:
            raise ProviderCallError(
                f"Ollama transport error: {exc}",
                backend=self.backend,
                retryable=True,
            ) from exc
        if len(raw) > self.max_response_bytes:
            raise ProviderCallError(
                "Ollama response exceeded the configured size limit",
                backend=self.backend,
                retryable=False,
                http_status=int(status),
            )
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderCallError(
                "Ollama returned invalid JSON",
                backend=self.backend,
                retryable=False,
                http_status=int(status),
                response_body=raw.decode("utf-8", errors="replace")[:8000],
            ) from exc
        if not isinstance(decoded, dict):
            raise ProviderCallError(
                "Ollama returned a non-object JSON response",
                backend=self.backend,
                retryable=False,
                http_status=int(status),
            )
        return decoded

    def server_version(self) -> str:
        """Return the server version without invoking a model."""

        response = self._request_json("GET", "/api/version")
        version = str(response.get("version", "") or "").strip()
        if not version:
            raise ProviderCallError(
                "Ollama version response did not contain a version",
                backend=self.backend,
                retryable=False,
            )
        return version

    def list_models(self) -> tuple[dict[str, Any], ...]:
        """Return sanitized local-model metadata without loading a model."""

        response = self._request_json("GET", "/api/tags")
        models = response.get("models", [])
        if not isinstance(models, list):
            raise ProviderCallError(
                "Ollama tags response did not contain a model list",
                backend=self.backend,
                retryable=False,
            )
        sanitized: list[dict[str, Any]] = []
        for model in models:
            if not isinstance(model, dict):
                continue
            sanitized.append(
                {
                    "name": str(model.get("name", "") or ""),
                    "model": str(model.get("model", "") or ""),
                    "modified_at": str(model.get("modified_at", "") or ""),
                    "size": _safe_nonnegative_int(model.get("size")),
                    "digest": str(model.get("digest", "") or "").lower(),
                    "details": dict(model.get("details", {}))
                    if isinstance(model.get("details"), dict)
                    else {},
                }
            )
        return tuple(sanitized)

    def list_running_models(self) -> tuple[dict[str, Any], ...]:
        """Return sanitized metadata for models currently loaded in memory."""

        response = self._request_json("GET", "/api/ps")
        models = response.get("models", [])
        if not isinstance(models, list):
            raise ProviderCallError(
                "Ollama process response did not contain a model list",
                backend=self.backend,
                retryable=False,
            )
        sanitized: list[dict[str, Any]] = []
        for model in models:
            if not isinstance(model, dict):
                continue
            sanitized.append(
                {
                    "name": str(model.get("name", "") or ""),
                    "model": str(model.get("model", "") or ""),
                    "expires_at": str(model.get("expires_at", "") or ""),
                    "size": _safe_nonnegative_int(model.get("size")),
                    "size_vram": _safe_nonnegative_int(model.get("size_vram")),
                    "digest": str(model.get("digest", "") or "").lower(),
                    "context_length": _safe_nonnegative_int(
                        model.get("context_length")
                    ),
                    "details": dict(model.get("details", {}))
                    if isinstance(model.get("details"), dict)
                    else {},
                }
            )
        return tuple(sanitized)

    def resolve_model(self, model_name: str) -> dict[str, Any]:
        """Resolve an exact local tag and enforce the optional digest lock."""

        requested = model_name.strip()
        if not requested:
            raise ValueError("model_name must be non-empty")
        aliases = {requested}
        if ":" not in requested:
            aliases.add(f"{requested}:latest")
        for model in self.list_models():
            if model.get("name") not in aliases and model.get("model") not in aliases:
                continue
            digest = _normalize_digest(str(model.get("digest", "") or ""))
            if self.expected_model_digest and digest != self.expected_model_digest:
                raise OllamaConfigurationError(
                    "resolved model digest does not match expected_model_digest"
                )
            return {**model, "digest": digest}
        raise OllamaConfigurationError(f"Ollama model is not installed: {requested}")

    def show_model(self, model_name: str) -> dict[str, Any]:
        """Return sanitized model details without returning template or license text."""

        response = self._request_json(
            "POST", "/api/show", payload={"model": model_name, "verbose": False}
        )
        details = response.get("details", {})
        model_info = response.get("model_info", {})
        return {
            "modified_at": str(response.get("modified_at", "") or ""),
            "details": dict(details) if isinstance(details, dict) else {},
            "capabilities": list(response.get("capabilities", []))
            if isinstance(response.get("capabilities"), list)
            else [],
            "model_info": dict(model_info) if isinstance(model_info, dict) else {},
            "template_sha256": hashlib.sha256(
                str(response.get("template", "") or "").encode("utf-8")
            ).hexdigest(),
            "parameters_sha256": hashlib.sha256(
                str(response.get("parameters", "") or "").encode("utf-8")
            ).hexdigest(),
            "license_sha256": hashlib.sha256(
                str(response.get("license", "") or "").encode("utf-8")
            ).hexdigest(),
            "template_characters": len(str(response.get("template", "") or "")),
            "parameters_characters": len(
                str(response.get("parameters", "") or "")
            ),
            "license_characters": len(str(response.get("license", "") or "")),
        }

    @staticmethod
    def _payload(request: ModelRequest) -> dict[str, Any]:
        generation = request.generation
        if generation.thinking_budget is not None:
            raise ValueError("Ollama does not support thinking_budget")
        if generation.reasoning_effort is not None:
            raise ValueError("Ollama does not support reasoning_effort")
        if generation.thinking_level == "MINIMAL":
            raise ValueError("Ollama does not support MINIMAL thinking_level")

        provider_options = dict(request.provider_options)
        unknown = set(provider_options) - _ALLOWED_PROVIDER_OPTIONS
        if unknown:
            raise ValueError(
                "unsupported Ollama provider_options: " + ", ".join(sorted(unknown))
            )
        supplied_options = provider_options.pop("options", {})
        if not isinstance(supplied_options, Mapping):
            raise ValueError("Ollama provider_options.options must be a mapping")
        collisions = set(supplied_options) & _RESERVED_OLLAMA_OPTIONS
        if collisions:
            raise ValueError(
                "Ollama provider_options.options cannot override shared settings: "
                + ", ".join(sorted(collisions))
            )
        options: dict[str, Any] = {
            "num_predict": generation.max_output_tokens,
            **dict(supplied_options),
        }
        if generation.temperature is not None:
            options["temperature"] = generation.temperature
        if generation.top_p is not None:
            options["top_p"] = generation.top_p
        if generation.seed is not None:
            options["seed"] = generation.seed

        messages: list[dict[str, str]] = []
        if request.system_instruction.strip():
            messages.append(
                {"role": "system", "content": request.system_instruction}
            )
        messages.extend(message.as_dict() for message in request.messages)
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "options": options,
            "stream": False,
        }
        think: bool | str | None = None
        if generation.thinking_level is not None:
            think = generation.thinking_level.lower()
        elif generation.include_thoughts:
            think = True
        if "think" in provider_options:
            if think is not None:
                raise ValueError(
                    "Ollama think cannot be set in both generation and provider_options"
                )
            supplied_think = provider_options.pop("think")
            if not isinstance(supplied_think, (bool, str)):
                raise ValueError("Ollama think must be a boolean or supported level")
            if isinstance(supplied_think, str):
                supplied_think = supplied_think.strip().lower()
                if supplied_think not in {"low", "medium", "high", "max"}:
                    raise ValueError("unsupported Ollama think level")
            think = supplied_think
        if think is not None:
            payload["think"] = think
        for key in ("keep_alive", "logprobs", "top_logprobs"):
            if key in provider_options:
                payload[key] = provider_options.pop(key)
        if request.structured_output is not None:
            if request.structured_output.mime_type != "application/json":
                raise ValueError("Ollama structured output requires application/json")
            payload["format"] = dict(request.structured_output.schema)
        return payload

    def generate(self, request: ModelRequest) -> ModelResponse:
        if request.backend not in {"ollama", "ollama_local", "ollama_native"}:
            raise ValueError(f"OllamaProvider cannot handle backend {request.backend}")
        response = self._request_json(
            "POST",
            "/api/chat",
            payload=self._payload(request),
            timeout_seconds=request.generation.timeout_seconds,
        )
        if response.get("done") is not True:
            raise ProviderCallError(
                "Ollama returned an incomplete non-streaming response",
                backend=self.backend,
                retryable=True,
            )
        message = response.get("message", {})
        if not isinstance(message, dict):
            message = {}
        role = str(message.get("role", "assistant") or "assistant").strip().lower()
        if role != "assistant":
            raise ProviderCallError(
                f"Ollama returned an unexpected message role: {role}",
                backend=self.backend,
                retryable=False,
            )
        text = str(message.get("content", "") or "")
        finish_reason = _finish_reason(response.get("done_reason"))
        if not text.strip():
            raise ProviderCallError(
                f"Ollama returned an empty response ({finish_reason})",
                backend=self.backend,
                retryable=False,
            )
        thinking = str(message.get("thinking", "") or "")
        input_tokens = _safe_nonnegative_int(response.get("prompt_eval_count"))
        output_tokens = _safe_nonnegative_int(response.get("eval_count"))
        metadata = {
            key: response[key]
            for key in (
                "created_at",
                "done_reason",
                "total_duration",
                "load_duration",
                "prompt_eval_duration",
                "eval_duration",
            )
            if key in response
        }
        metadata["thinking_present"] = bool(thinking)
        metadata["thinking_characters"] = len(thinking)
        if self.expected_server_version:
            metadata["ollama_version"] = self.expected_server_version
        response_model = str(response.get("model", "") or request.model)
        model_version = response_model
        if self.expected_model_digest:
            model_version = f"{response_model}@sha256:{self.expected_model_digest}"
        identity = "\n".join(
            (
                response_model,
                str(response.get("created_at", "") or ""),
                text,
                finish_reason,
            )
        )
        return ModelResponse(
            text=text,
            backend=self.backend,
            model=request.model,
            model_version=model_version,
            response_id="ollama_" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24],
            finish_reason=finish_reason,
            usage=TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                metadata=metadata,
            ),
        )

    def close(self) -> None:
        """The standard-library HTTP transport owns no persistent resources."""

"""Vertex custom-endpoint helpers for OpenAI-compatible vLLM servers."""

from __future__ import annotations

import json
from pathlib import Path
import threading
from typing import Any, Callable, Mapping
from urllib import error as urllib_error
from urllib import request as urllib_request

import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest

from .provider_adapters import to_openai_compatible_request
from .smoke import PreparedTutorRequest


class VertexEndpointError(RuntimeError):
    """Structured custom-endpoint failure with retry metadata."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool,
        http_status: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.http_status = http_status
        self.response_body = response_body


def endpoint_id_from_resource(value: str) -> str:
    """Accept a numeric endpoint ID or a full Vertex endpoint resource."""

    endpoint_id = value.rstrip("/").rsplit("/", 1)[-1].strip()
    if not endpoint_id.isdigit():
        raise ValueError("Vertex endpoint ID must be numeric")
    return endpoint_id


def load_lifecycle_manifest(path: Path) -> dict[str, Any]:
    """Load a deployment manifest and require a live SocraticLM endpoint."""

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid endpoint lifecycle manifest: {path}") from exc
    required = {
        "project",
        "location",
        "hf_model_id",
        "endpoint_resource",
        "model_resource",
        "deployed_model_id",
        "delete_by",
        "status",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise RuntimeError(
            "endpoint lifecycle manifest is missing: " + ", ".join(missing)
        )
    if manifest["status"] != "deployed":
        raise RuntimeError(
            "endpoint lifecycle manifest must have status='deployed'"
        )
    endpoint_id_from_resource(str(manifest["endpoint_resource"]))
    return manifest


def parse_openai_chat_response(
    body: Mapping[str, Any],
    *,
    fallback_model: str,
    normalize_finish_reason: Callable[[Any], str],
) -> dict[str, Any]:
    """Normalize a vLLM/OpenAI chat-completion response."""

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError("vLLM endpoint returned no choices")
    first = choices[0]
    finish_reason = normalize_finish_reason(first.get("finish_reason"))
    text = first.get("message", {}).get("content")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(
            "vLLM endpoint returned an empty response "
            f"(finish_reason={finish_reason})"
        )
    usage = body.get("usage") or {}
    return {
        "response_text": text,
        "response_id": str(body.get("id") or ""),
        "model_version": str(body.get("model") or fallback_model),
        "usage_metadata": dict(usage),
        "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
        "output_tokens": int(usage.get("completion_tokens", 0) or 0),
        "finish_reason": finish_reason,
    }


class VertexRawPredictCaller:
    """Call an OpenAI-compatible vLLM server through Vertex rawPredict."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        endpoint_id: str,
        model: str,
        max_output_tokens: int,
        seed: int,
        normalize_finish_reason: Callable[[Any], str],
        timeout_seconds: int = 180,
    ) -> None:
        self.project = project
        self.location = location
        self.endpoint_id = endpoint_id_from_resource(endpoint_id)
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.seed = seed
        self.normalize_finish_reason = normalize_finish_reason
        self.timeout_seconds = timeout_seconds
        self.credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            quota_project_id=self.project,
        )
        self.auth_lock = threading.Lock()

    def _token(self) -> str:
        with self.auth_lock:
            if not self.credentials.valid:
                self.credentials.refresh(GoogleAuthRequest())
            if not self.credentials.token:
                raise RuntimeError("ADC did not provide an access token")
            return self.credentials.token

    def call(self, prepared: PreparedTutorRequest) -> dict[str, Any]:
        native = to_openai_compatible_request(
            prepared.system_instruction, prepared.conversation.messages
        )
        payload = {
            "model": self.model,
            "messages": native["messages"],
            "max_tokens": self.max_output_tokens,
            "temperature": 0.0,
            "seed": self.seed,
            "stream": False,
        }
        url = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project}/locations/{self.location}/endpoints/"
            f"{self.endpoint_id}:rawPredict"
        )
        http_request = urllib_request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )
        try:
            with urllib_request.urlopen(
                http_request, timeout=self.timeout_seconds
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            retryable = (
                exc.code in {408, 409, 425, 429} or 500 <= exc.code <= 599
            )
            raise VertexEndpointError(
                f"Vertex rawPredict HTTP {exc.code}: {response_body[:500]}",
                retryable=retryable,
                http_status=exc.code,
                response_body=response_body,
            ) from exc
        except json.JSONDecodeError as exc:
            raise VertexEndpointError(
                "Vertex rawPredict returned invalid JSON",
                retryable=False,
            ) from exc
        if not isinstance(body, Mapping):
            raise VertexEndpointError(
                "Vertex rawPredict response must be a JSON object",
                retryable=False,
            )
        return parse_openai_chat_response(
            body,
            fallback_model=self.model,
            normalize_finish_reason=self.normalize_finish_reason,
        )

    def close(self) -> None:
        return None

"""Thread-local Google Gen AI SDK clients for standard Vertex AI."""

from __future__ import annotations

import threading
from typing import Any, Mapping

import google.auth
from google import genai
from google.auth.exceptions import DefaultCredentialsError
from google.genai import types

from src.vertex_ai_call.requirement_scoring import GenerationConfig


class VertexClientConfigurationError(RuntimeError):
    """Raised when the standard Vertex configuration is incomplete."""


class VertexRequirementClient:
    """Call Vertex AI with a locked prompt and structured response schema."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        system_prompt: str,
        response_schema: Mapping[str, Any],
        generation_config: GenerationConfig,
        client: Any | None = None,
    ) -> None:
        self._project = project.strip()
        self._location = location.strip()
        if not self._project:
            raise VertexClientConfigurationError("Vertex project must not be empty")
        if not self._location:
            raise VertexClientConfigurationError("Vertex location must not be empty")
        self._system_prompt = system_prompt
        self._response_schema = dict(response_schema)
        self._generation_config = generation_config
        self._injected_client = client
        self._credentials = None
        if client is None:
            try:
                self._credentials, _ = google.auth.default(
                    quota_project_id=self._project
                )
            except DefaultCredentialsError as exc:
                raise VertexClientConfigurationError(
                    "Application Default Credentials are unavailable"
                ) from exc
        self._thread_local = threading.local()
        self._created_clients: list[Any] = []
        self._created_clients_lock = threading.Lock()

    def _new_client(self) -> Any:
        client = genai.Client(
            vertexai=True,
            project=self._project,
            location=self._location,
            credentials=self._credentials,
            http_options=types.HttpOptions(
                api_version="v1",
                timeout=int(self._generation_config.timeout_seconds * 1000),
            ),
        )
        with self._created_clients_lock:
            self._created_clients.append(client)
        return client

    def _client_for_current_thread(self) -> Any:
        if self._injected_client is not None:
            return self._injected_client
        client = getattr(self._thread_local, "client", None)
        if client is None:
            client = self._new_client()
            self._thread_local.client = client
        return client

    def generate(self, user_prompt: str) -> dict[str, Any]:
        config_kwargs: dict[str, Any] = {
            "system_instruction": self._system_prompt,
            "max_output_tokens": self._generation_config.max_output_tokens,
            "seed": self._generation_config.seed,
            "response_mime_type": "application/json",
            "response_json_schema": self._response_schema,
        }
        if self._generation_config.temperature is not None:
            config_kwargs["temperature"] = self._generation_config.temperature
        if self._generation_config.top_p is not None:
            config_kwargs["top_p"] = self._generation_config.top_p

        thinking_kwargs: dict[str, Any] = {
            "include_thoughts": self._generation_config.include_thoughts,
        }
        if self._generation_config.thinking_budget is not None:
            thinking_kwargs["thinking_budget"] = (
                self._generation_config.thinking_budget
            )
        if self._generation_config.thinking_level is not None:
            thinking_kwargs["thinking_level"] = types.ThinkingLevel[
                self._generation_config.thinking_level
            ]
        config_kwargs["thinking_config"] = types.ThinkingConfig(
            **thinking_kwargs
        )
        config = types.GenerateContentConfig(**config_kwargs)
        response = self._client_for_current_thread().models.generate_content(
            model=self._generation_config.model,
            contents=user_prompt,
            config=config,
        )
        raw_text = response.text
        if not isinstance(raw_text, str) or not raw_text.strip():
            raise RuntimeError("Vertex AI returned an empty text response")
        candidates = getattr(response, "candidates", None) or []
        finish_reason = ""
        if candidates:
            finish_reason_value = getattr(candidates[0], "finish_reason", None)
            finish_reason = str(finish_reason_value or "")
        usage = getattr(response, "usage_metadata", None)
        if usage is None:
            usage_metadata: dict[str, Any] = {}
        elif hasattr(usage, "model_dump"):
            usage_metadata = usage.model_dump(mode="json", exclude_none=True)
        else:
            usage_metadata = {"value": str(usage)}
        return {
            "raw_response_text": raw_text,
            "response_id": str(getattr(response, "response_id", "") or ""),
            "model_version": str(getattr(response, "model_version", "") or ""),
            "finish_reason": finish_reason,
            "usage_metadata": usage_metadata,
        }

    def close(self) -> None:
        if self._injected_client is not None:
            close = getattr(self._injected_client, "close", None)
            if callable(close):
                close()
            return
        with self._created_clients_lock:
            clients = list(self._created_clients)
            self._created_clients.clear()
        for client in clients:
            close = getattr(client, "close", None)
            if callable(close):
                close()

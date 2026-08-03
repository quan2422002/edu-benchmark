"""ADC-authenticated Claude judge caller for Vertex AI."""

from __future__ import annotations

import json
import threading
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest

from .judge import PreparedJudgeRequest


class ClaudeJudgeCallError(RuntimeError):
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


class ClaudeVertexJudgeCaller:
    """Call Claude partner MaaS through rawPredict with project ADC."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        model: str,
        max_output_tokens: int,
        temperature: float = 0.0,
        timeout_seconds: int = 180,
    ) -> None:
        if max_output_tokens <= 0 or not 0 <= temperature <= 1:
            raise ValueError("invalid Claude generation config")
        self.project = project
        self.location = location
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds
        self.credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            quota_project_id=project,
        )
        self.auth_lock = threading.Lock()

    def _token(self) -> str:
        with self.auth_lock:
            if not self.credentials.valid:
                self.credentials.refresh(GoogleAuthRequest())
            if not self.credentials.token:
                raise ClaudeJudgeCallError(
                    "ADC did not provide an access token", retryable=False
                )
            return self.credentials.token

    def _url(self) -> str:
        host = (
            "aiplatform.googleapis.com"
            if self.location == "global"
            else f"{self.location}-aiplatform.googleapis.com"
        )
        return (
            f"https://{host}/v1/projects/{self.project}/locations/"
            f"{self.location}/publishers/anthropic/models/"
            f"{self.model}:rawPredict"
        )

    def call(self, prepared: PreparedJudgeRequest) -> dict[str, Any]:
        payload = {
            "anthropic_version": "vertex-2023-10-16",
            "max_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "system": prepared.system_prompt,
            "messages": [
                {"role": "user", "content": prepared.user_prompt}
            ],
        }
        request = urllib_request.Request(
            self._url(),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )
        try:
            with urllib_request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            retryable = (
                exc.code in {408, 409, 425, 429}
                or 500 <= exc.code <= 599
            )
            raise ClaudeJudgeCallError(
                f"Vertex Claude HTTP {exc.code}: {response_body[:800]}",
                retryable=retryable,
                http_status=exc.code,
                response_body=response_body,
            ) from exc
        except urllib_error.URLError as exc:
            raise ClaudeJudgeCallError(
                f"Vertex Claude network error: {exc}", retryable=True
            ) from exc
        except json.JSONDecodeError as exc:
            raise ClaudeJudgeCallError(
                "Vertex Claude returned invalid JSON", retryable=True
            ) from exc

        blocks = body.get("content")
        if not isinstance(blocks, list):
            raise ClaudeJudgeCallError(
                "Vertex Claude returned no content blocks",
                retryable=True,
                response_body=json.dumps(body, ensure_ascii=False)[:2000],
            )
        text = "\n".join(
            str(block.get("text") or "")
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
        finish_reason = (
            str(body.get("stop_reason") or "UNKNOWN").strip().upper()
        )
        if not text:
            raise ClaudeJudgeCallError(
                f"empty Claude response ({finish_reason})",
                retryable=True,
            )
        usage = body.get("usage")
        if not isinstance(usage, dict):
            usage = {}
        return {
            "response_text": text,
            "response_id": str(body.get("id") or ""),
            "model_version": str(body.get("model") or self.model),
            "finish_reason": finish_reason,
            "input_tokens": int(usage.get("input_tokens", 0) or 0),
            "output_tokens": int(usage.get("output_tokens", 0) or 0),
            "usage_metadata": usage,
        }

    def close(self) -> None:
        return None

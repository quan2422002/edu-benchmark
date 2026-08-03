"""Direct OpenAI Responses API caller for blind pairwise judging."""

from __future__ import annotations

import json
from typing import Any

import openai
from openai import OpenAI

from .judge import PreparedJudgeRequest


class OpenAIJudgeCallError(RuntimeError):
    """OpenAI failure with structured retry metadata."""

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


def _is_retryable_status(status: int | None) -> bool:
    return status in {408, 409, 425, 429} or (
        isinstance(status, int) and 500 <= status <= 599
    )


def _object(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def build_judge_response_schema(
    prepared: PreparedJudgeRequest,
) -> dict[str, Any]:
    """Build a strict per-request schema without exposing internal IDs."""

    criterion_names = [name for name, _ in prepared.rubric_name_to_id]
    error_names = [name for name, _ in prepared.error_name_to_id]
    confidence = {"type": "number", "minimum": 0, "maximum": 1}
    text = {"type": "string", "minLength": 1}
    side = _object(
        {
            "detected": {"type": "boolean"},
            "confidence": confidence,
            "rationale": text,
        }
    )
    criterion = _object(
        {
            "criterion_name": {
                "type": "string",
                "enum": criterion_names,
            },
            "winner": {
                "type": "string",
                "enum": ["response_1", "response_2", "tie"],
            },
            "confidence": confidence,
            "rationale": text,
            "response_1_evidence": text,
            "response_2_evidence": text,
        }
    )
    finding = _object(
        {
            "error_name": {"type": "string", "enum": error_names},
            "response_1": side,
            "response_2": side,
        }
    )
    overall = _object(
        {
            "winner": {
                "type": "string",
                "enum": ["response_1", "response_2", "tie"],
            },
            "confidence": confidence,
            "rationale": text,
        }
    )
    properties = {
        "criterion_judgments": {
            "type": "array",
            "minItems": len(criterion_names),
            "maxItems": len(criterion_names),
            "items": criterion,
        },
        "overall_judgment": overall,
    }
    if prepared.include_serious_errors:
        properties["serious_error_findings"] = {
            "type": "array",
            "maxItems": len(error_names),
            "items": finding,
        }
    return _object(properties)


def _response_body(response: Any) -> str:
    dump = getattr(response, "model_dump", None)
    if callable(dump):
        try:
            return json.dumps(
                dump(mode="json", exclude_none=True),
                ensure_ascii=False,
            )[:8000]
        except (TypeError, ValueError):
            pass
    return str(response)[:8000]


class OpenAIJudgeCaller:
    """Call the OpenAI Responses API with strict Structured Outputs."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_output_tokens: int,
        reasoning_effort: str = "medium",
        timeout_seconds: float = 180.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenAI API key must be non-empty")
        if max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        normalized_effort = reasoning_effort.strip().lower()
        if normalized_effort not in {
            "none",
            "low",
            "medium",
            "high",
            "xhigh",
        }:
            raise ValueError("invalid OpenAI reasoning effort")
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = normalized_effort
        # Retry is owned by the outer runner so every attempt is observable.
        self.client = OpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=0,
        )

    def call(self, prepared: PreparedJudgeRequest) -> dict[str, Any]:
        schema = build_judge_response_schema(prepared)
        schema_name = {
            "v2": "blind_pairwise_judgment_v2",
            "rubric-only-v3": "blind_pairwise_judgment_rubric_only_v3",
            "gold-answer-only-v4": (
                "blind_pairwise_judgment_gold_answer_only_v4"
            ),
        }[prepared.judge_output_contract_version]
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=prepared.system_prompt,
                input=prepared.user_prompt,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": self.reasoning_effort},
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    }
                },
                store=False,
                truncation="disabled",
            )
        except openai.APIStatusError as exc:
            status = getattr(exc, "status_code", None)
            response_body = str(getattr(exc, "response", "") or "")[:8000]
            raise OpenAIJudgeCallError(
                f"OpenAI HTTP {status}: {exc}",
                retryable=_is_retryable_status(status),
                http_status=status,
                response_body=response_body,
            ) from exc
        except (
            openai.APIConnectionError,
            openai.APITimeoutError,
        ) as exc:
            raise OpenAIJudgeCallError(
                f"OpenAI transport error: {exc}",
                retryable=True,
            ) from exc
        except openai.OpenAIError as exc:
            raise OpenAIJudgeCallError(
                f"OpenAI API error: {exc}",
                retryable=False,
            ) from exc

        status = str(getattr(response, "status", "") or "").lower()
        incomplete = getattr(response, "incomplete_details", None)
        incomplete_reason = str(
            getattr(incomplete, "reason", "") or ""
        ).upper()
        finish_reason = (
            "STOP"
            if status == "completed"
            else incomplete_reason or status.upper() or "UNKNOWN"
        )
        response_text = str(getattr(response, "output_text", "") or "")
        if not response_text.strip():
            raise OpenAIJudgeCallError(
                f"empty OpenAI response ({finish_reason})",
                retryable=status in {"in_progress", "queued"},
                response_body=_response_body(response),
            )
        usage = getattr(response, "usage", None)
        usage_dict = (
            usage.model_dump(mode="json", exclude_none=True)
            if usage is not None and hasattr(usage, "model_dump")
            else {}
        )
        return {
            "response_text": response_text,
            "response_id": str(getattr(response, "id", "") or ""),
            "model_version": str(
                getattr(response, "model", "") or self.model
            ),
            "finish_reason": finish_reason,
            "input_tokens": int(usage_dict.get("input_tokens", 0) or 0),
            "output_tokens": int(usage_dict.get("output_tokens", 0) or 0),
            "usage_metadata": usage_dict,
        }

    def close(self) -> None:
        self.client.close()

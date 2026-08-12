"""Direct OpenAI Responses API caller for blind pairwise judging."""

from __future__ import annotations

from typing import Any

from edu_benchmark.model_providers import (
    GenerationSettings,
    ModelMessage,
    ModelProvider,
    ModelRequest,
    ProviderCallError,
    StructuredOutput,
)
from edu_benchmark.model_providers.openai import OpenAIProvider

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
        provider: ModelProvider | None = None,
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
        self.provider = provider or OpenAIProvider(
            api_key=api_key,
            timeout_seconds=timeout_seconds,
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
        request = ModelRequest(
            backend="openai",
            model=self.model,
            system_instruction=prepared.system_prompt,
            messages=(ModelMessage(role="user", content=prepared.user_prompt),),
            generation=GenerationSettings(
                max_output_tokens=self.max_output_tokens,
                reasoning_effort=self.reasoning_effort,
            ),
            structured_output=StructuredOutput(
                name=schema_name,
                schema=schema,
                strict=True,
            ),
            provider_options={"store": False, "truncation": "disabled"},
        )
        try:
            response = self.provider.generate(request)
        except ProviderCallError as exc:
            raise OpenAIJudgeCallError(
                str(exc),
                retryable=exc.retryable,
                http_status=exc.http_status,
                response_body=exc.response_body,
            ) from exc
        return {
            "response_text": response.text,
            "response_id": response.response_id,
            "model_version": response.model_version,
            "finish_reason": response.finish_reason,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "usage_metadata": dict(response.usage.metadata),
        }

    def close(self) -> None:
        self.provider.close()

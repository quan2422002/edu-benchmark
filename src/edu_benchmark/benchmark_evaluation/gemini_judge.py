"""Gemini judge caller for blind pairwise benchmark evaluation."""

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
from edu_benchmark.model_providers.vertex_ai import VertexAIProvider

from .judge import PreparedJudgeRequest
from .openai_judge import build_judge_response_schema


class GeminiJudgeCallError(RuntimeError):
    """Gemini failure with structured retry metadata."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.http_status = http_status


def _build_gemini_response_schema(
    prepared: PreparedJudgeRequest,
) -> dict[str, Any]:
    """Keep Gemini's schema compact; exact rubric names are checked locally."""

    schema = build_judge_response_schema(prepared)
    criterion = schema["properties"]["criterion_judgments"]["items"]
    criterion["properties"]["criterion_name"] = {"type": "string"}
    if prepared.include_serious_errors:
        finding = schema["properties"]["serious_error_findings"]["items"]
        finding["properties"]["error_name"] = {"type": "string"}
    return schema


class GeminiVertexJudgeCaller:
    """Call Gemini with native system/user fields and thread-local clients."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        model: str,
        max_output_tokens: int,
        seed: int,
        thinking_level: str = "MEDIUM",
        temperature: float | None = None,
        timeout_ms: int = 180_000,
        provider: ModelProvider | None = None,
    ) -> None:
        if max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        if temperature is not None and not 0 <= temperature <= 2:
            raise ValueError("invalid Gemini temperature")
        normalized_level = thinking_level.strip().upper()
        if normalized_level not in {"MINIMAL", "LOW", "MEDIUM", "HIGH"}:
            raise ValueError("invalid Gemini thinking level")
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.seed = seed
        self.thinking_level = normalized_level
        self.temperature = temperature
        self.timeout_ms = timeout_ms
        self.provider = provider or VertexAIProvider(
            project=project,
            location=location,
        )

    def call(self, prepared: PreparedJudgeRequest) -> dict[str, Any]:
        request = ModelRequest(
            backend="vertex_ai",
            model=self.model,
            system_instruction=prepared.system_prompt,
            messages=(ModelMessage(role="user", content=prepared.user_prompt),),
            generation=GenerationSettings(
                max_output_tokens=self.max_output_tokens,
                seed=self.seed,
                thinking_level=self.thinking_level,
                include_thoughts=True,
                temperature=self.temperature,
                timeout_seconds=self.timeout_ms / 1000,
            ),
            structured_output=StructuredOutput(
                name="blind_pairwise_judgment_gemini",
                schema=_build_gemini_response_schema(prepared),
            ),
        )
        try:
            response = self.provider.generate(request)
        except ProviderCallError as exc:
            raise GeminiJudgeCallError(
                str(exc),
                retryable=exc.retryable,
                http_status=exc.http_status,
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

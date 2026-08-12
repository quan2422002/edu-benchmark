"""Requirement-scoring adapter over the shared model-provider contract."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from edu_benchmark.model_providers import (
    GenerationSettings,
    ModelMessage,
    ModelProvider,
    ModelRequest,
    StructuredOutput,
)
from .core import GenerationConfig


class RequirementResponseClient(Protocol):
    """Small domain-facing client used by the scoring workflow."""

    def generate(self, user_prompt: str) -> dict[str, Any]: ...

    def close(self) -> None: ...


class RequirementScoringModelClient:
    """Bind a scoring prompt and schema to a task-neutral model provider."""

    def __init__(
        self,
        *,
        provider: ModelProvider,
        backend: str,
        system_prompt: str,
        response_schema: Mapping[str, Any],
        generation_config: GenerationConfig,
    ) -> None:
        self._provider = provider
        self._backend = backend
        self._system_prompt = system_prompt
        self._response_schema = dict(response_schema)
        self._generation_config = generation_config

    def generate(self, user_prompt: str) -> dict[str, Any]:
        config = self._generation_config.model_policy()
        response = self._provider.generate(
            ModelRequest(
                backend=self._backend,
                model=config.model,
                system_instruction=self._system_prompt,
                messages=(ModelMessage(role="user", content=user_prompt),),
                generation=GenerationSettings(
                    max_output_tokens=config.max_output_tokens,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    seed=config.seed,
                    timeout_seconds=config.timeout_seconds,
                    thinking_budget=config.thinking_budget,
                    thinking_level=config.thinking_level,
                    include_thoughts=config.include_thoughts,
                ),
                structured_output=StructuredOutput(
                    name="pedagogical_principle_requirement_scoring",
                    schema=self._response_schema,
                ),
            )
        )
        return {
            "raw_response_text": response.text,
            "response_id": response.response_id,
            "model_version": response.model_version,
            "finish_reason": response.finish_reason,
            "usage_metadata": dict(response.usage.metadata),
        }

    def close(self) -> None:
        self._provider.close()


def build_vertex_requirement_client(
    *,
    project: str,
    location: str,
    system_prompt: str,
    response_schema: Mapping[str, Any],
    generation_config: GenerationConfig,
    sdk_client: Any | None = None,
) -> RequirementScoringModelClient:
    """Build the current Vertex-backed requirement-scoring client."""

    from edu_benchmark.model_providers.vertex_ai import VertexAIProvider

    return RequirementScoringModelClient(
        provider=VertexAIProvider(
            project=project,
            location=location,
            client=sdk_client,
        ),
        backend="vertex_ai",
        system_prompt=system_prompt,
        response_schema=response_schema,
        generation_config=generation_config,
    )

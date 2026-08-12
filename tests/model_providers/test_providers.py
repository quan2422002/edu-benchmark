"""Offline contract tests for shared model providers."""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from edu_benchmark.model_providers import (
    GenerationSettings,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ProviderCallError,
    ProviderRegistry,
    StructuredOutput,
    TokenUsage,
)
from edu_benchmark.model_providers.openai import OpenAIProvider
from edu_benchmark.model_providers.vertex_ai import VertexAIProvider


ROOT = Path(__file__).resolve().parents[2]


def _request(backend: str, model: str) -> ModelRequest:
    return ModelRequest(
        backend=backend,
        model=model,
        system_instruction="System instruction",
        messages=(ModelMessage("user", "User prompt"),),
        generation=GenerationSettings(
            max_output_tokens=2048,
            seed=17,
            thinking_level="medium",
        ),
        structured_output=StructuredOutput(
            name="offline_contract",
            schema={"type": "object", "properties": {}},
        ),
    )


def test_contract_normalizes_values_and_rejects_mixed_thinking_controls():
    request = _request("vertex-ai", "gemini-test")
    assert request.backend == "vertex_ai"
    assert request.generation.thinking_level == "MEDIUM"
    with pytest.raises(ValueError, match="mutually exclusive"):
        GenerationSettings(
            max_output_tokens=1,
            thinking_budget=0,
            thinking_level="LOW",
        )


def test_vertex_provider_maps_request_and_normalizes_response_offline():
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                text='{"ok":true}',
                response_id="vertex-response",
                model_version="gemini-test-001",
                candidates=[SimpleNamespace(finish_reason="STOP")],
                usage_metadata=SimpleNamespace(
                    model_dump=lambda **_: {
                        "prompt_token_count": 11,
                        "candidates_token_count": 7,
                        "thoughts_token_count": 2,
                        "total_token_count": 20,
                    }
                ),
            )

    fake_sdk = SimpleNamespace(models=FakeModels(), close=lambda: None)
    provider = VertexAIProvider(
        project="edu-benchmark",
        location="global",
        client=fake_sdk,
    )
    response = provider.generate(_request("vertex_ai", "gemini-test"))

    assert captured["model"] == "gemini-test"
    assert captured["contents"] == "User prompt"
    config = captured["config"].model_dump(mode="json", exclude_none=True)
    assert config["system_instruction"] == "System instruction"
    assert config["thinking_config"]["thinking_level"] == "MEDIUM"
    assert config["response_json_schema"] == {
        "type": "object",
        "properties": {},
    }
    assert response.response_id == "vertex-response"
    assert response.usage.input_tokens == 11
    assert response.usage.output_tokens == 9
    assert response.usage.total_tokens == 20


def test_vertex_provider_normalizes_retryable_transport_error():
    class FailingModels:
        @staticmethod
        def generate_content(**kwargs):
            raise RuntimeError("Temporary failure in name resolution")

    provider = VertexAIProvider(
        project="edu-benchmark",
        location="global",
        client=SimpleNamespace(models=FailingModels()),
    )
    with pytest.raises(ProviderCallError) as captured:
        provider.generate(_request("vertex_ai", "gemini-test"))
    assert captured.value.backend == "vertex_ai"
    assert captured.value.retryable is True


def test_openai_provider_maps_responses_request_offline():
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                output_text='{"ok":true}',
                id="openai-response",
                model="gpt-test-001",
                status="completed",
                incomplete_details=None,
                usage=SimpleNamespace(
                    model_dump=lambda **_: {
                        "input_tokens": 13,
                        "output_tokens": 5,
                        "total_tokens": 18,
                    }
                ),
            )

    fake_sdk = SimpleNamespace(responses=FakeResponses(), close=lambda: None)
    provider = OpenAIProvider(client=fake_sdk)
    request = ModelRequest(
        backend="openai",
        model="gpt-test",
        system_instruction="System instruction",
        messages=(ModelMessage("user", "User prompt"),),
        generation=GenerationSettings(
            max_output_tokens=1024,
            reasoning_effort="high",
        ),
        structured_output=StructuredOutput(
            name="offline_contract",
            schema={"type": "object", "properties": {}},
        ),
    )
    response = provider.generate(request)

    assert captured["model"] == "gpt-test"
    assert captured["instructions"] == "System instruction"
    assert captured["input"] == "User prompt"
    assert captured["reasoning"] == {"effort": "high"}
    assert captured["text"]["format"]["name"] == "offline_contract"
    assert captured["store"] is False
    assert response.finish_reason == "STOP"
    assert response.usage.total_tokens == 18


def test_registry_supports_extension_without_workflow_dependencies():
    class FakeProvider:
        backend = "offline"

        def generate(self, request):
            return ModelResponse(
                text="ok",
                backend=self.backend,
                model=request.model,
                usage=TokenUsage(),
            )

        def close(self):
            pass

    registry = ProviderRegistry()
    registry.register("offline", lambda: FakeProvider())
    assert registry.create("offline").backend == "offline"

    provider_root = ROOT / "src/edu_benchmark/model_providers"
    forbidden = {
        "edu_benchmark.requirement_scoring",
        "edu_benchmark.benchmark_evaluation",
    }
    for path in provider_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        assert not imports & forbidden, path

from __future__ import annotations

import io
import json
from urllib.error import HTTPError, URLError

import pytest

from edu_benchmark.model_providers import (
    GenerationSettings,
    ModelMessage,
    ModelRequest,
    ProviderCallError,
    StructuredOutput,
    create_provider,
)
from edu_benchmark.model_providers.ollama import (
    OllamaConfigurationError,
    OllamaProvider,
)


MODEL_DIGEST = "a" * 64


class FakeResponse:
    def __init__(self, payload: object, *, status: int = 200) -> None:
        self.status = status
        self._body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(payload).encode("utf-8")
        )

    def read(self, amount: int = -1) -> bytes:
        return self._body if amount < 0 else self._body[:amount]

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


class FakeUrlOpen:
    def __init__(self, *outcomes: object) -> None:
        self.outcomes = list(outcomes)
        self.calls: list[tuple[object, float]] = []

    def __call__(self, request: object, *, timeout: float) -> FakeResponse:
        self.calls.append((request, timeout))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, FakeResponse)
        return outcome


def model_request(**overrides: object) -> ModelRequest:
    values: dict[str, object] = {
        "backend": "ollama",
        "model": "qwen3.8:latest",
        "system_instruction": "Be a concise tutor.",
        "messages": (
            ModelMessage(role="user", content="First question"),
            ModelMessage(role="assistant", content="First answer"),
            ModelMessage(role="user", content="Follow-up question"),
        ),
        "generation": GenerationSettings(
            max_output_tokens=256,
            temperature=0.2,
            top_p=0.9,
            seed=7,
            timeout_seconds=42,
            thinking_level="MEDIUM",
        ),
        "provider_options": {
            "options": {"num_ctx": 4096, "top_k": 20},
            "keep_alive": -1,
        },
    }
    values.update(overrides)
    return ModelRequest(**values)  # type: ignore[arg-type]


def successful_response(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "model": "qwen3.8:latest",
        "created_at": "2026-09-02T03:30:00Z",
        "message": {
            "role": "assistant",
            "content": "Visible tutor answer",
            "thinking": "private reasoning must not leak",
        },
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": 21,
        "eval_count": 12,
        "total_duration": 100,
        "load_duration": 20,
        "prompt_eval_duration": 30,
        "eval_duration": 50,
    }
    values.update(overrides)
    return values


def decoded_payload(call: tuple[object, float]) -> dict[str, object]:
    request, _ = call
    return json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]


def test_generate_maps_conversation_options_and_separates_thinking() -> None:
    transport = FakeUrlOpen(FakeResponse(successful_response()))
    provider = OllamaProvider(
        expected_model_digest=MODEL_DIGEST,
        expected_server_version="0.32.14",
        urlopen_fn=transport,
    )

    response = provider.generate(model_request())

    payload = decoded_payload(transport.calls[0])
    assert payload == {
        "model": "qwen3.8:latest",
        "messages": [
            {"role": "system", "content": "Be a concise tutor."},
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Follow-up question"},
        ],
        "options": {
            "num_predict": 256,
            "num_ctx": 4096,
            "top_k": 20,
            "temperature": 0.2,
            "top_p": 0.9,
            "seed": 7,
        },
        "stream": False,
        "think": "medium",
        "keep_alive": -1,
    }
    assert transport.calls[0][1] == 42
    assert response.text == "Visible tutor answer"
    assert "private reasoning" not in response.text
    assert response.finish_reason == "STOP"
    assert response.model_version == f"qwen3.8:latest@sha256:{MODEL_DIGEST}"
    assert response.response_id.startswith("ollama_")
    assert response.usage.input_tokens == 21
    assert response.usage.output_tokens == 12
    assert response.usage.total_tokens == 33
    assert response.usage.metadata["thinking_present"] is True
    assert response.usage.metadata["thinking_characters"] == 31
    assert response.usage.metadata["ollama_version"] == "0.32.14"
    assert "thinking" not in response.usage.metadata


def test_generate_maps_json_schema_and_length_finish_reason() -> None:
    transport = FakeUrlOpen(
        FakeResponse(successful_response(done_reason="length", message={"content": "{}"}))
    )
    provider = OllamaProvider(urlopen_fn=transport)
    request = model_request(
        generation=GenerationSettings(max_output_tokens=64),
        provider_options={},
        structured_output=StructuredOutput(
            name="answer",
            schema={"type": "object", "properties": {"answer": {"type": "string"}}},
        ),
    )

    response = provider.generate(request)

    payload = decoded_payload(transport.calls[0])
    assert payload["format"] == request.structured_output.schema
    assert "think" not in payload
    assert response.finish_reason == "MAX_TOKENS"


def test_generate_maps_system_plus_single_user_turn() -> None:
    transport = FakeUrlOpen(FakeResponse(successful_response()))
    provider = OllamaProvider(urlopen_fn=transport)
    request = model_request(
        messages=(ModelMessage(role="user", content="One question"),),
        generation=GenerationSettings(max_output_tokens=32, include_thoughts=True),
        provider_options={},
    )

    provider.generate(request)

    payload = decoded_payload(transport.calls[0])
    assert payload["messages"] == [
        {"role": "system", "content": "Be a concise tutor."},
        {"role": "user", "content": "One question"},
    ]
    assert payload["think"] is True


@pytest.mark.parametrize(
    ("generation", "provider_options", "message"),
    [
        (GenerationSettings(max_output_tokens=10, thinking_budget=5), {}, "thinking_budget"),
        (
            GenerationSettings(max_output_tokens=10, reasoning_effort="high"),
            {},
            "reasoning_effort",
        ),
        (
            GenerationSettings(max_output_tokens=10, thinking_level="MINIMAL"),
            {},
            "MINIMAL",
        ),
        (
            GenerationSettings(max_output_tokens=10),
            {"stream": True},
            "unsupported Ollama provider_options",
        ),
        (
            GenerationSettings(max_output_tokens=10),
            {"options": {"seed": 1}},
            "cannot override shared settings",
        ),
    ],
)
def test_generate_rejects_unsupported_or_ambiguous_controls(
    generation: GenerationSettings,
    provider_options: dict[str, object],
    message: str,
) -> None:
    provider = OllamaProvider(urlopen_fn=FakeUrlOpen())

    with pytest.raises(ValueError, match=message):
        provider.generate(
            model_request(generation=generation, provider_options=provider_options)
        )


def test_generate_marks_http_and_transport_failures_for_retry() -> None:
    http_error = HTTPError(
        "http://127.0.0.1:11436/api/chat",
        503,
        "unavailable",
        {},
        io.BytesIO(b'{"error":"temporarily unavailable"}'),
    )
    provider = OllamaProvider(urlopen_fn=FakeUrlOpen(http_error))

    with pytest.raises(ProviderCallError) as captured:
        provider.generate(model_request())
    assert captured.value.http_status == 503
    assert captured.value.retryable is True

    provider = OllamaProvider(urlopen_fn=FakeUrlOpen(URLError("refused")))
    with pytest.raises(ProviderCallError) as captured:
        provider.generate(model_request())
    assert captured.value.http_status is None
    assert captured.value.retryable is True

    provider = OllamaProvider(urlopen_fn=FakeUrlOpen(TimeoutError("timed out")))
    with pytest.raises(ProviderCallError) as captured:
        provider.generate(model_request())
    assert captured.value.retryable is True


def test_generate_marks_client_errors_non_retryable() -> None:
    http_error = HTTPError(
        "http://127.0.0.1:11436/api/chat",
        400,
        "bad request",
        {},
        io.BytesIO(b'{"error":"invalid request"}'),
    )
    provider = OllamaProvider(urlopen_fn=FakeUrlOpen(http_error))

    with pytest.raises(ProviderCallError) as captured:
        provider.generate(model_request())
    assert captured.value.http_status == 400
    assert captured.value.retryable is False
    assert captured.value.response_body == '{"error":"invalid request"}'


@pytest.mark.parametrize(
    "response",
    [
        FakeResponse(b"not-json"),
        FakeResponse([]),
        FakeResponse(successful_response(done=False)),
        FakeResponse(successful_response(message={"content": ""})),
    ],
)
def test_generate_rejects_invalid_or_incomplete_responses(response: FakeResponse) -> None:
    provider = OllamaProvider(urlopen_fn=FakeUrlOpen(response))

    with pytest.raises(ProviderCallError):
        provider.generate(model_request())


def test_status_methods_resolve_and_lock_model_digest() -> None:
    transport = FakeUrlOpen(
        FakeResponse({"version": "0.32.14"}),
        FakeResponse(
            {
                "models": [
                    {
                        "name": "qwen3.8:latest",
                        "model": "qwen3.8:latest",
                        "modified_at": "2026-08-29T00:00:00Z",
                        "size": 18,
                        "digest": MODEL_DIGEST,
                        "details": {"quantization_level": "Q4_K_M"},
                    }
                ]
            }
        ),
        FakeResponse(
            {
                "details": {"quantization_level": "Q4_K_M"},
                "capabilities": ["completion", "thinking"],
                "model_info": {"general.parameter_count": 100},
                "template": "template",
                "parameters": "parameters",
                "license": "license",
            }
        ),
    )
    provider = OllamaProvider(
        expected_model_digest=MODEL_DIGEST, urlopen_fn=transport
    )

    assert provider.server_version() == "0.32.14"
    assert provider.resolve_model("qwen3.8:latest")["digest"] == MODEL_DIGEST
    details = provider.show_model("qwen3.8:latest")
    assert details["details"]["quantization_level"] == "Q4_K_M"
    assert "template" not in details
    assert "license" not in details
    assert len(details["template_sha256"]) == 64
    assert details["template_characters"] == 8
    assert details["parameters_characters"] == 10
    assert details["license_characters"] == 7


def test_configuration_defaults_to_loopback_and_registry_is_lazy() -> None:
    with pytest.raises(OllamaConfigurationError, match="non-loopback"):
        OllamaProvider(base_url="http://192.168.1.10:11434")
    with pytest.raises(OllamaConfigurationError, match="SHA-256"):
        OllamaProvider(expected_model_digest="not-a-digest")
    with pytest.raises(OllamaConfigurationError, match="must not contain"):
        OllamaProvider(base_url="http://127.0.0.1:11436/v1")

    provider = create_provider("ollama-local", urlopen_fn=FakeUrlOpen())
    assert isinstance(provider, OllamaProvider)
    assert provider.base_url == "http://127.0.0.1:11436"
    assert provider.close() is None
    assert provider.close() is None

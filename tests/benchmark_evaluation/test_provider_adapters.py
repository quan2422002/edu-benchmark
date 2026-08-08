from edu_benchmark.benchmark_evaluation.dialogue_transport import (
    build_native_conversation,
)
from edu_benchmark.benchmark_evaluation.provider_adapters import (
    to_anthropic_request,
    to_gemini_request,
    to_openai_compatible_request,
)


def _conversation():
    return build_native_conversation(
        "Lượt đầu",
        [
            {"turn_index": 2, "role": "tutor", "content": "Lượt hai"},
            {"turn_index": 3, "role": "student", "content": "Lượt ba"},
        ],
    )


def test_gemini_maps_assistant_to_model_without_content_changes():
    request = to_gemini_request("Hệ thống", _conversation().messages)
    assert request["system_instruction"] == "Hệ thống"
    assert [item["role"] for item in request["contents"]] == [
        "user",
        "model",
        "user",
    ]
    assert [
        item["parts"][0]["text"] for item in request["contents"]
    ] == ["Lượt đầu", "Lượt hai", "Lượt ba"]


def test_anthropic_keeps_system_separate():
    request = to_anthropic_request("Hệ thống", _conversation().messages)
    assert request["system"] == "Hệ thống"
    assert request["messages"][1] == {
        "role": "assistant",
        "content": "Lượt hai",
    }


def test_openai_compatible_uses_native_system_message():
    request = to_openai_compatible_request(
        "Hệ thống", _conversation().messages
    )
    assert request["messages"][0] == {
        "role": "system",
        "content": "Hệ thống",
    }
    assert request["messages"][-1]["role"] == "user"

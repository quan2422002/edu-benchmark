from __future__ import annotations

from edu_benchmark.model_providers.ollama.runtime import (
    model_is_preloaded_for_execution,
)


def test_preloaded_model_requires_matching_tag_full_gpu_and_context() -> None:
    running_models = [
        {
            "name": "qwen3.8:latest",
            "size": 17_278_099_782,
            "size_vram": 17_278_099_782,
            "context_length": 4096,
        }
    ]

    assert model_is_preloaded_for_execution(
        running_models,
        "qwen3.8:latest",
        context_length=4096,
    )


def test_preloaded_model_rejects_cpu_offload_or_wrong_context() -> None:
    cpu_offloaded = [
        {
            "model": "qwen3.8:latest",
            "size": 100,
            "size_vram": 98,
            "context_length": 4096,
        }
    ]
    wrong_context = [
        {
            "model": "qwen3.8:latest",
            "size": 100,
            "size_vram": 100,
            "context_length": 8192,
        }
    ]

    assert not model_is_preloaded_for_execution(
        cpu_offloaded,
        "qwen3.8:latest",
        context_length=4096,
    )
    assert not model_is_preloaded_for_execution(
        wrong_context,
        "qwen3.8:latest",
        context_length=4096,
    )

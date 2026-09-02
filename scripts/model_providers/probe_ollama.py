#!/usr/bin/env python3
"""Probe an existing Ollama server and optionally execute one fixed fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edu_benchmark.model_providers import (
    GenerationSettings,
    ModelMessage,
    ModelRequest,
    ProviderCallError,
)
from edu_benchmark.model_providers.ollama import (
    OllamaConfigurationError,
    OllamaProvider,
    inspect_runtime,
)
from edu_benchmark.model_providers.ollama.runtime import (
    gpu_snapshot,
    memory_snapshot,
    model_is_preloaded_for_execution,
)


DEFAULT_OUTPUT_DIR = Path(
    "experiments/20260902_082403/outputs/ollama_provider_v1"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a loopback Ollama runtime without starting or pulling it."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:11436")
    parser.add_argument("--model", default="qwen3.8:latest")
    parser.add_argument("--expected-version", default="0.32.14")
    parser.add_argument("--expected-quantization", default="Q4_K_M")
    parser.add_argument("--expected-digest")
    parser.add_argument("--expected-num-parallel", type=int, choices=(1, 2), default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--execute-model",
        action="store_true",
        help="Run one fixed non-benchmark chat fixture after metadata checks pass.",
    )
    return parser.parse_args()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def quantization_level(*records: dict[str, Any]) -> str:
    for record in records:
        details = record.get("details", {})
        if isinstance(details, dict):
            value = str(details.get("quantization_level", "") or "").strip()
            if value:
                return value
    return ""


def main() -> int:
    args = parse_args()
    provider = OllamaProvider(
        base_url=args.base_url,
        expected_model_digest=args.expected_digest,
    )
    generated_at = datetime.now(timezone.utc).isoformat()
    runtime_before = inspect_runtime()
    version = provider.server_version()
    resolved = provider.resolve_model(args.model)
    shown = provider.show_model(args.model)
    quantization = quantization_level(resolved, shown)
    running_models_before = (
        list(provider.list_running_models()) if args.execute_model else []
    )
    model_preloaded_before_execute = model_is_preloaded_for_execution(
        running_models_before,
        args.model,
        context_length=4096,
    )
    runtime_checks = dict(runtime_before["checks"])
    if args.execute_model:
        gpu_free_for_new_load = runtime_checks.pop("gpu_free_at_least_20_gib")
        runtime_checks["gpu_capacity_for_execution"] = (
            gpu_free_for_new_load or model_preloaded_before_execute
        )
    checks = {
        **runtime_checks,
        "server_version": version == args.expected_version,
        "model_tag": resolved.get("name") == args.model
        or resolved.get("model") == args.model,
        "model_digest": bool(resolved.get("digest")),
        "quantization": quantization.upper()
        == args.expected_quantization.upper(),
    }
    manifest = {
        "schema_version": "ollama-runtime-manifest-v1",
        "generated_at": generated_at,
        "base_url": args.base_url,
        "server_version": version,
        "expected_server_version": args.expected_version,
        "model": args.model,
        "model_digest": resolved.get("digest", ""),
        "expected_model_digest": args.expected_digest or "",
        "model_size_bytes": resolved.get("size", 0),
        "quantization": quantization,
        "expected_quantization": args.expected_quantization,
        "environment_contract": {
            "LOCAL_LLM_CACHE_ROOT": "/workspace/quannd/local_llm_cache",
            "OLLAMA_MODELS": "/workspace/quannd/local_llm_cache/ollama/models",
            "OLLAMA_HOST": "127.0.0.1:11436",
            "OLLAMA_NUM_PARALLEL": str(args.expected_num_parallel),
            "OLLAMA_MAX_LOADED_MODELS": "1",
            "OLLAMA_FLASH_ATTENTION": "1",
            "OLLAMA_KV_CACHE_TYPE": "f16",
            "CUDA_VISIBLE_DEVICES": "GPU-5e1bf88a-a431-9a0c-b462-37cd95b5e9b8",
        },
        "model_details": shown,
        "runtime_before": runtime_before,
        "execution_preflight": {
            "execute_model": bool(args.execute_model),
            "model_preloaded": model_preloaded_before_execute,
            "running_models": running_models_before,
        },
        "checks": checks,
        "ready": all(checks.values()),
    }
    atomic_json(args.output_dir / "runtime_manifest.json", manifest)
    if not manifest["ready"]:
        print(json.dumps({"ready": False, "checks": checks}, ensure_ascii=False))
        return 2

    if args.execute_model:
        locked_provider = OllamaProvider(
            base_url=args.base_url,
            expected_model_digest=str(resolved["digest"]),
            expected_server_version=version,
        )
        system_instruction = (
            "Bạn là gia sư Tin học. Trả lời ngắn gọn, rõ ràng và không "
            "tiết lộ quá trình suy luận nội bộ."
        )
        fixture_messages = (
            ModelMessage(
                role="user",
                content="Biến trong Python dùng để làm gì?",
            ),
            ModelMessage(
                role="assistant",
                content="Biến dùng để đặt tên và lưu một giá trị.",
            ),
            ModelMessage(
                role="user",
                content="Cho một ví dụ thật ngắn.",
            ),
        )
        fixture_sha256 = hashlib.sha256(
            json.dumps(
                {
                    "system_instruction": system_instruction,
                    "messages": [message.as_dict() for message in fixture_messages],
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        response = locked_provider.generate(
            ModelRequest(
                backend="ollama",
                model=args.model,
                system_instruction=system_instruction,
                messages=fixture_messages,
                generation=GenerationSettings(
                    max_output_tokens=256,
                    temperature=0.2,
                    top_p=0.9,
                    seed=20260902,
                    timeout_seconds=600,
                    thinking_level="MEDIUM",
                ),
                provider_options={
                    "options": {"num_ctx": 4096},
                    "keep_alive": -1,
                },
            )
        )
        runtime_after = {
            "memory": memory_snapshot(),
            "gpu": gpu_snapshot(),
        }
        running_models = list(locked_provider.list_running_models())
        loaded_model = next(
            (
                model
                for model in running_models
                if model.get("name") == args.model or model.get("model") == args.model
            ),
            {},
        )
        loaded_size = int(loaded_model.get("size", 0) or 0)
        loaded_vram = int(loaded_model.get("size_vram", 0) or 0)
        loaded_context = int(loaded_model.get("context_length", 0) or 0)
        probe_checks = {
            "response_nonempty": bool(response.text.strip()),
            "finish_reason_known": response.finish_reason != "UNKNOWN",
            "usage_present": response.usage.total_tokens > 0,
            "thinking_not_stored": "thinking" not in response.usage.metadata,
            "model_loaded": bool(loaded_model),
            "model_fully_on_gpu": loaded_size > 0 and loaded_vram >= loaded_size * 0.99,
            "model_context_length": loaded_context == 4096,
        }
        probe = {
            "schema_version": "ollama-provider-probe-v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "fixture_id": "ollama-provider-fixed-chat-v1",
            "fixture_sha256": fixture_sha256,
            "request": {
                "backend": "ollama",
                "model": args.model,
                "message_count": 3,
                "has_system_instruction": True,
                "max_output_tokens": 256,
                "thinking_level": "MEDIUM",
                "num_ctx": 4096,
                "seed": 20260902,
            },
            "response": asdict(response),
            "running_models": running_models,
            "runtime_after": runtime_after,
            "checks": probe_checks,
            "passed": all(probe_checks.values()),
        }
        atomic_json(args.output_dir / "provider_probe.json", probe)
        manifest["runtime_after"] = runtime_after
        manifest["running_models"] = running_models
        manifest["checks"].update(
            {
                "model_loaded": probe_checks["model_loaded"],
                "model_fully_on_gpu": probe_checks["model_fully_on_gpu"],
                "provider_probe": probe["passed"],
            }
        )
        manifest["ready"] = all(manifest["checks"].values())
        atomic_json(args.output_dir / "runtime_manifest.json", manifest)
        if not probe["passed"]:
            print(
                json.dumps(
                    {"ready": False, "checks": probe_checks}, ensure_ascii=False
                )
            )
            return 3
    print(
        json.dumps(
            {
                "ready": True,
                "server_version": version,
                "model": args.model,
                "model_digest": resolved["digest"],
                "execute_model": bool(args.execute_model),
            },
            ensure_ascii=False,
        )
    )
    return 0


def cli() -> int:
    try:
        return main()
    except (OllamaConfigurationError, ProviderCallError, OSError) as exc:
        print(
            json.dumps(
                {
                    "ready": False,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 4


if __name__ == "__main__":
    raise SystemExit(cli())

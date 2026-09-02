#!/usr/bin/env python3
"""Run a locked target-response config through the shared provider boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

from tqdm import tqdm

from edu_benchmark.benchmark_evaluation.smoke import prepare_tutor_requests
from edu_benchmark.benchmark_evaluation.resource_monitor import NvidiaSmiMonitor
from edu_benchmark.benchmark_evaluation.target_runner import (
    RetryPolicy,
    TargetRunConfig,
    TargetRunIdentity,
    TargetRunPaths,
    preflight_target_run,
    run_target_responses,
)
from edu_benchmark.model_providers import GenerationSettings, create_provider


ROOT = Path(__file__).resolve().parents[2]


def _path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("target run config must be a JSON object")
    return data


def _verify_file(entry: dict[str, Any], label: str) -> Path:
    path = _path(str(entry["path"]))
    expected = str(entry["sha256"])
    actual = _sha256(path)
    if actual != expected:
        raise RuntimeError(
            f"{label} SHA-256 mismatch: expected {expected}, found {actual}"
        )
    return path


def _run_config(raw: dict[str, Any]) -> TargetRunConfig:
    identity = TargetRunIdentity(**raw["identity"])
    generation = GenerationSettings(**raw["generation"])
    retry = RetryPolicy(**raw.get("retry", {}))
    return TargetRunConfig(
        identity=identity,
        backend=str(raw["backend"]),
        model=str(raw["model"]),
        generation=generation,
        provider_options=dict(raw.get("provider_options") or {}),
        provider_identity=dict(raw.get("provider_identity") or {}),
        resource_monitor=dict(raw.get("resource_monitor") or {}),
        retry=retry,
        max_concurrency=int(raw.get("max_concurrency", 1)),
        cost_basis=str(raw["cost_basis"]),
        input_usd_per_million=float(raw.get("input_usd_per_million", 0)),
        output_usd_per_million=float(raw.get("output_usd_per_million", 0)),
    )


def _provider_kwargs(raw: dict[str, Any]) -> dict[str, Any]:
    provider = dict(raw.get("provider_connection") or {})
    return provider


def _resource_monitor(raw: dict[str, Any]) -> NvidiaSmiMonitor | None:
    settings = dict(raw.get("resource_monitor") or {})
    if not settings.get("enabled", False):
        return None
    if settings.get("backend") != "nvidia_smi":
        raise ValueError("unsupported resource-monitor backend")
    return NvidiaSmiMonitor(
        gpu_uuid=str(settings["gpu_uuid"]),
        interval_seconds=float(settings.get("interval_seconds", 0.2)),
        executable=str(settings.get("executable", "/usr/bin/nvidia-smi")),
    )


def _verify_live_ollama(provider: Any, raw: dict[str, Any]) -> None:
    expected = dict(raw.get("provider_identity") or {})
    expected_version = str(expected.get("server_version", ""))
    version = provider.server_version()
    if expected_version and version != expected_version:
        raise RuntimeError(
            f"Ollama version drift: expected {expected_version}, found {version}"
        )
    model = provider.resolve_model(str(raw["model"]))
    expected_digest = str(expected.get("model_digest", ""))
    if expected_digest and model.get("digest") != expected_digest:
        raise RuntimeError("Ollama model digest drift")
    running = provider.list_running_models()
    matching = next(
        (
            item
            for item in running
            if item.get("name") == raw["model"]
            or item.get("model") == raw["model"]
        ),
        None,
    )
    if matching is None:
        raise RuntimeError("configured Ollama model is not preloaded")
    expected_parallel = int(expected.get("parallel", 1))
    expected_context = int(expected.get("num_ctx", 0)) * expected_parallel
    if int(matching.get("context_length", 0)) != expected_context:
        raise RuntimeError(
            "Ollama loaded context does not match num_ctx * parallel: "
            f"expected {expected_context}, found "
            f"{matching.get('context_length', 0)}"
        )


def _print_summary(manifest: dict[str, Any]) -> None:
    integrity = dict(manifest.get("integrity") or {})
    failed_count = len(manifest.get("failed_candidate_ids") or [])
    print(
        "Run result: "
        f"status={manifest['status']} | phase={manifest['phase']} | "
        f"recorded={integrity.get('record_count', 0)}/"
        f"{manifest['candidate_count']} | "
        f"completed={integrity.get('completed_record_count', 0)} | "
        f"review={integrity.get('needs_review_record_count', 0)} | "
        f"failed={failed_count}"
    )
    resource = dict(manifest.get("resource_summary") or {})
    if resource:
        print(
            "GPU result: "
            f"measured={resource.get('measured_candidate_count', 0)} | "
            f"vram_peak={resource.get('memory_used_peak_gib', 'n/a')} GiB | "
            f"vram_free_min={resource.get('memory_free_min_gib', 'n/a')} GiB | "
            f"util_peak={resource.get('gpu_utilization_peak_percent', 'n/a')}%"
        )
    print(f"Responses: {manifest['output_file']}")


def _progress_callback(
    progress: tqdm, state: dict[str, int]
) -> Callable[[dict[str, Any]], None]:
    def handle(event: dict[str, Any]) -> None:
        event_type = event["event"]
        if event_type == "retry_scheduled":
            tqdm.write(
                "[retry] "
                f"{event['benchmark_candidate_id']} "
                f"attempt {event['next_attempt']}/{event['max_attempts']} "
                f"after {event['delay_seconds']:.1f}s: "
                f"{event['exception_type']}",
                file=progress.fp,
            )
            return
        if event_type == "record_failed":
            state["failed"] += 1
            progress.update(1)
            tqdm.write(
                f"[failed] {event['benchmark_candidate_id']}: "
                f"{event['exception_type']}: {event['exception_message']}",
                file=progress.fp,
            )
            progress.set_postfix(
                ok=state["completed"],
                review=state["review"],
                failed=state["failed"],
                refresh=True,
            )
            return
        state["completed"] += event["response_status"] == "completed"
        state["review"] += event["response_status"] == "needs_review"
        resource = event.get("resource_usage") or {}
        postfix: dict[str, Any] = {
            "candidate": event["benchmark_candidate_id"],
            "ok": state["completed"],
            "review": state["review"],
            "failed": state["failed"],
            "sec": event["latency_seconds"],
            "tok": event["input_tokens"] + event["output_tokens"],
        }
        if resource:
            postfix["vram_peak_gib"] = resource["memory_used_peak_gib"]
            postfix["vram_free_gib"] = resource["memory_free_min_gib"]
        progress.update(1)
        progress.set_postfix(postfix, refresh=True)

    return handle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--execute-api",
        action="store_true",
        help="Without this switch, lock/validate preflight without model calls.",
    )
    parser.add_argument(
        "--max-new-records",
        type=int,
        help="Bound this invocation while preserving the locked selection/run ID.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = _load_config(args.config)
    sources = raw["sources"]
    grounding_pool = _verify_file(sources["grounding_pool"], "grounding pool")
    analysis = _verify_file(sources["analysis"], "requirement analysis")
    requirement_run = _verify_file(
        sources["requirement_run"], "requirement scoring run"
    )
    instruction_bundle = _verify_file(
        sources["instruction_bundle"], "instruction bundle"
    )
    full_manifest = _verify_file(
        sources["full_candidate_manifest"], "full candidate manifest"
    )
    full_data = json.loads(full_manifest.read_text(encoding="utf-8"))
    full_ids = list(full_data["candidate_ids"])
    expected_full_ids_hash = str(sources["full_candidate_manifest"]["ids_sha256"])
    actual_full_ids_hash = hashlib.sha256(
        "\n".join(sorted(full_ids)).encode("utf-8")
    ).hexdigest()
    if actual_full_ids_hash != expected_full_ids_hash:
        raise RuntimeError("full candidate ID hash mismatch")

    selection = raw["selection"]
    candidate_ids = list(selection["candidate_ids"])
    if len(candidate_ids) != int(selection["candidate_count"]):
        raise RuntimeError("selection candidate_count mismatch")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError("selection candidate IDs must be unique")
    if not set(candidate_ids) <= set(full_ids):
        raise RuntimeError("selection contains IDs outside the locked 1,400 set")

    prepared = prepare_tutor_requests(
        grounding_pool_csv=grounding_pool,
        analysis_json=analysis,
        requirement_run_jsonl=requirement_run,
        instruction_bundle_path=instruction_bundle,
        max_candidates=len(candidate_ids),
        seed=int(raw["generation"].get("seed") or 0),
        fixed_candidate_ids=candidate_ids,
    )
    config = _run_config(raw)
    paths = TargetRunPaths(_path(str(raw["output_dir"])))
    source_provenance = {
        name: {
            "path": str(entry["path"]),
            "sha256": str(entry["sha256"]),
            **(
                {"ids_sha256": str(entry["ids_sha256"])}
                if "ids_sha256" in entry
                else {}
            ),
        }
        for name, entry in sources.items()
    }
    selection_provenance = {
        key: value for key, value in selection.items() if key != "candidate_ids"
    }
    selection_provenance["candidate_ids"] = candidate_ids
    manifest = preflight_target_run(
        prepared=prepared,
        config=config,
        paths=paths,
        source_provenance=source_provenance,
        selection_provenance=selection_provenance,
    )
    print(
        "Target run: "
        f"{manifest['run_id']} | {config.backend}/{config.model} | "
        f"checkpoint={manifest['integrity']['record_count']}/"
        f"{manifest['candidate_count']} | output={paths.output_dir}",
        flush=True,
    )
    monitor_settings = config.resource_monitor
    if monitor_settings.get("enabled"):
        print(
            "GPU monitor: "
            f"{monitor_settings['backend']} | "
            f"uuid={monitor_settings['gpu_uuid']} | "
            f"interval={monitor_settings['interval_seconds']}s | unit=GiB",
            flush=True,
        )
    print(
        "Execution: "
        f"max_concurrency={config.max_concurrency} | "
        f"persistence=single_writer | "
        f"gpu_scope={'candidate' if config.max_concurrency == 1 else 'invocation'}",
        flush=True,
    )
    if not args.execute_api:
        _print_summary(manifest)
        print("Preflight locked. Add --execute-api to call the configured provider.")
        return 0

    provider = create_provider(config.backend, **_provider_kwargs(raw))
    initial_integrity = dict(manifest.get("integrity") or {})
    state = {
        "completed": int(initial_integrity.get("completed_record_count", 0)),
        "review": int(initial_integrity.get("needs_review_record_count", 0)),
        "failed": len(manifest.get("failed_candidate_ids") or []),
    }
    progress = tqdm(
        total=manifest["candidate_count"],
        initial=int(initial_integrity.get("record_count", 0)),
        desc=f"{config.model} pilot",
        unit="sample",
        dynamic_ncols=True,
        mininterval=0.5,
        file=sys.stderr,
    )
    try:
        if config.backend == "ollama":
            _verify_live_ollama(provider, raw)
        manifest = run_target_responses(
            prepared=prepared,
            provider=provider,
            config=config,
            paths=paths,
            source_provenance=source_provenance,
            selection_provenance=selection_provenance,
            resource_monitor=_resource_monitor(raw),
            max_new_records=args.max_new_records,
            event_callback=_progress_callback(progress, state),
        )
    finally:
        progress.close()
        provider.close()
    _print_summary(manifest)
    return 0 if manifest["phase"] in {
        "technical_smoke_completed",
        "pilot_completed",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())

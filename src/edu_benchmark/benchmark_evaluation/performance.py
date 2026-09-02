"""Performance summaries for completed or checkpointed target runs."""

from __future__ import annotations

import math
from statistics import mean, median
from typing import Any, Mapping, Sequence


def _percentile(values: Sequence[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return round(ordered[index], 4)


def summarize_target_run_performance(
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    observations = list(manifest.get("provider_observations") or [])
    latencies = [float(item["latency_seconds"]) for item in observations]
    output_tokens = sum(int(item.get("output_tokens", 0)) for item in observations)
    input_tokens = sum(int(item.get("input_tokens", 0)) for item in observations)
    elapsed_seconds = sum(
        float(item.get("elapsed_seconds", 0))
        for item in manifest.get("resume_history") or []
        if int(item.get("record_count_after", 0))
        > int(item.get("record_count_before", 0))
    )
    recorded_count = int(
        (manifest.get("integrity") or {}).get("record_count", len(observations))
    )
    configuration = dict(manifest.get("configuration") or {})
    max_concurrency = int(configuration.get("max_concurrency", 1))
    return {
        "run_id": manifest.get("run_id"),
        "status": manifest.get("status"),
        "max_concurrency": max_concurrency,
        "recorded_count": recorded_count,
        "completed_count": int(
            (manifest.get("integrity") or {}).get(
                "completed_record_count", 0
            )
        ),
        "needs_review_count": int(
            (manifest.get("integrity") or {}).get(
                "needs_review_record_count", 0
            )
        ),
        "failed_count": len(manifest.get("failed_candidate_ids") or []),
        "execution_elapsed_seconds": round(elapsed_seconds, 4),
        "samples_per_minute": (
            round(recorded_count * 60 / elapsed_seconds, 4)
            if elapsed_seconds > 0
            else None
        ),
        "aggregate_output_tokens_per_second": (
            round(output_tokens / elapsed_seconds, 4)
            if elapsed_seconds > 0
            else None
        ),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "request_latency_seconds": {
            "mean": round(mean(latencies), 4) if latencies else None,
            "median": round(median(latencies), 4) if latencies else None,
            "p95": _percentile(latencies, 0.95),
            "max": round(max(latencies), 4) if latencies else None,
        },
        "resource_summary": manifest.get("resource_summary"),
    }


def compare_target_run_performance(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    baseline_summary = summarize_target_run_performance(baseline)
    candidate_summary = summarize_target_run_performance(candidate)
    baseline_rate = baseline_summary["samples_per_minute"]
    candidate_rate = candidate_summary["samples_per_minute"]
    speedup = (
        round(candidate_rate / baseline_rate, 4)
        if baseline_rate and candidate_rate
        else None
    )
    return {
        "baseline": baseline_summary,
        "candidate": candidate_summary,
        "throughput_speedup": speedup,
    }

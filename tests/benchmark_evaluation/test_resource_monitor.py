import itertools
import time

import pytest

from edu_benchmark.benchmark_evaluation.resource_monitor import (
    NvidiaSmiMonitor,
    ResourceMonitoringError,
    summarize_gpu_samples,
)


def _sample(index: int) -> dict:
    return {
        "sampled_at": f"2026-09-02T00:00:0{index}+00:00",
        "gpu_uuid": "GPU-test",
        "gpu_name": "Test GPU",
        "driver_version": "1.0",
        "memory_total_mib": 24576,
        "memory_used_mib": 18000 + index * 100,
        "memory_free_mib": 6576 - index * 100,
        "utilization_gpu_percent": index * 20,
        "temperature_celsius": 50 + index,
        "power_draw_watts": 100.0 + index,
        "power_limit_watts": 350.0,
    }


def test_summarize_gpu_samples_reports_peak_and_headroom():
    summary = summarize_gpu_samples(
        [_sample(0), _sample(1), _sample(2)], interval_seconds=0.2
    )
    assert summary["memory_used_baseline_gib"] == round(18000 / 1024, 4)
    assert summary["memory_used_peak_gib"] == round(18200 / 1024, 4)
    assert summary["memory_peak_delta_from_baseline_gib"] == round(200 / 1024, 4)
    assert summary["memory_free_min_gib"] == round(6376 / 1024, 4)
    assert summary["gpu_utilization_peak_percent"] == 40
    assert summary["power_draw_peak_watts"] == 102.0


def test_monitor_samples_during_operation():
    counter = itertools.count()
    monitor = NvidiaSmiMonitor(
        gpu_uuid="GPU-test",
        interval_seconds=0.05,
        snapshot_fn=lambda: _sample(min(next(counter), 5)),
    )
    result, observation = monitor.measure(
        lambda: (time.sleep(0.13), "done")[1]
    )
    assert result == "done"
    assert observation["sample_count"] >= 4
    assert observation["gpu_uuid"] == "GPU-test"
    assert observation["memory_used_peak_gib"] > 18000 / 1024


def test_monitor_fails_before_operation_when_baseline_is_unavailable():
    called = False

    def operation():
        nonlocal called
        called = True

    monitor = NvidiaSmiMonitor(
        gpu_uuid="GPU-test",
        snapshot_fn=lambda: (_ for _ in ()).throw(
            ResourceMonitoringError("unavailable")
        ),
    )
    with pytest.raises(ResourceMonitoringError, match="unavailable"):
        monitor.measure(operation)
    assert called is False

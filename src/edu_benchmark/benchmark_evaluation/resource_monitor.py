"""Small, optional NVIDIA GPU monitor for local target-generation runs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import subprocess
import threading
import time
from typing import Any, Callable, TypeVar


T = TypeVar("T")


class ResourceMonitoringError(RuntimeError):
    """Raised before a model call when required GPU monitoring is unavailable."""

    retryable = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _optional_float(value: str) -> float | None:
    normalized = value.strip()
    if not normalized or normalized.lower() in {"n/a", "[n/a]", "not supported"}:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None


def nvidia_smi_snapshot(
    gpu_uuid: str,
    *,
    executable: str = "/usr/bin/nvidia-smi",
    timeout_seconds: float = 5.0,
) -> dict[str, Any]:
    """Read one device-level snapshot for the exact configured GPU UUID."""

    fields = (
        "uuid,name,driver_version,memory.total,memory.used,memory.free,"
        "utilization.gpu,temperature.gpu,power.draw,power.limit"
    )
    try:
        completed = subprocess.run(
            [
                executable,
                f"--id={gpu_uuid}",
                f"--query-gpu={fields}",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ResourceMonitoringError(
            f"nvidia-smi snapshot failed: {type(exc).__name__}"
        ) from exc
    rows = list(csv.reader(completed.stdout.splitlines()))
    if len(rows) != 1 or len(rows[0]) != 10:
        raise ResourceMonitoringError("unexpected nvidia-smi snapshot output")
    values = [value.strip() for value in rows[0]]
    if values[0] != gpu_uuid:
        raise ResourceMonitoringError(
            f"GPU UUID mismatch: expected {gpu_uuid}, found {values[0]}"
        )
    try:
        return {
            "sampled_at": _utc_now(),
            "gpu_uuid": values[0],
            "gpu_name": values[1],
            "driver_version": values[2],
            "memory_total_mib": int(values[3]),
            "memory_used_mib": int(values[4]),
            "memory_free_mib": int(values[5]),
            "utilization_gpu_percent": int(values[6]),
            "temperature_celsius": int(values[7]),
            "power_draw_watts": _optional_float(values[8]),
            "power_limit_watts": _optional_float(values[9]),
        }
    except ValueError as exc:
        raise ResourceMonitoringError(
            "nvidia-smi returned invalid numeric GPU fields"
        ) from exc


def summarize_gpu_samples(
    samples: list[dict[str, Any]], *, interval_seconds: float
) -> dict[str, Any]:
    if not samples:
        raise ResourceMonitoringError("GPU monitoring produced no samples")
    first = samples[0]
    last = samples[-1]
    used = [int(sample["memory_used_mib"]) for sample in samples]
    free = [int(sample["memory_free_mib"]) for sample in samples]
    utilization = [
        int(sample["utilization_gpu_percent"]) for sample in samples
    ]
    temperatures = [int(sample["temperature_celsius"]) for sample in samples]
    power = [
        float(sample["power_draw_watts"])
        for sample in samples
        if sample.get("power_draw_watts") is not None
    ]
    to_gib = lambda value: round(value / 1024, 4)
    return {
        "monitor": "nvidia_smi_device_sampling",
        "gpu_uuid": first["gpu_uuid"],
        "gpu_name": first["gpu_name"],
        "driver_version": first["driver_version"],
        "sampling_interval_seconds": interval_seconds,
        "sample_count": len(samples),
        "first_sampled_at": first["sampled_at"],
        "last_sampled_at": last["sampled_at"],
        "memory_total_gib": to_gib(int(first["memory_total_mib"])),
        "memory_used_baseline_gib": to_gib(used[0]),
        "memory_used_peak_gib": to_gib(max(used)),
        "memory_used_after_gib": to_gib(used[-1]),
        "memory_peak_delta_from_baseline_gib": to_gib(max(used) - used[0]),
        "memory_free_min_gib": to_gib(min(free)),
        "gpu_utilization_average_percent": round(
            sum(utilization) / len(utilization), 2
        ),
        "gpu_utilization_peak_percent": max(utilization),
        "temperature_peak_celsius": max(temperatures),
        "power_draw_average_watts": (
            round(sum(power) / len(power), 2) if power else None
        ),
        "power_draw_peak_watts": max(power) if power else None,
    }


@dataclass
class NvidiaSmiMonitor:
    """Sample one GPU while a synchronous provider request is in flight."""

    gpu_uuid: str
    interval_seconds: float = 0.2
    executable: str = "/usr/bin/nvidia-smi"
    snapshot_fn: Callable[[], dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if not self.gpu_uuid.strip():
            raise ValueError("gpu_uuid must be non-empty")
        if not 0.05 <= self.interval_seconds <= 10:
            raise ValueError("GPU sampling interval must be between 0.05 and 10s")

    def _snapshot(self) -> dict[str, Any]:
        if self.snapshot_fn is not None:
            return self.snapshot_fn()
        return nvidia_smi_snapshot(
            self.gpu_uuid,
            executable=self.executable,
        )

    def measure(self, operation: Callable[[], T]) -> tuple[T, dict[str, Any]]:
        samples = [self._snapshot()]
        stop = threading.Event()
        sampling_errors: list[BaseException] = []

        def sample_until_stopped() -> None:
            while not stop.wait(self.interval_seconds):
                try:
                    samples.append(self._snapshot())
                except BaseException as exc:  # preserve the provider call outcome
                    sampling_errors.append(exc)
                    stop.set()

        thread = threading.Thread(
            target=sample_until_stopped,
            name="target-gpu-monitor",
            daemon=True,
        )
        thread.start()
        operation_error: BaseException | None = None
        result: T | None = None
        try:
            result = operation()
        except BaseException as exc:
            operation_error = exc
        finally:
            stop.set()
            thread.join(timeout=max(2.0, self.interval_seconds * 2))
            try:
                samples.append(self._snapshot())
            except BaseException as exc:
                sampling_errors.append(exc)
        observation = summarize_gpu_samples(
            samples, interval_seconds=self.interval_seconds
        )
        if sampling_errors:
            error = ResourceMonitoringError(
                "GPU sampling failed during the provider request"
            )
            if operation_error is not None:
                setattr(operation_error, "resource_usage", observation)
                raise operation_error
            raise error from sampling_errors[0]
        if operation_error is not None:
            setattr(operation_error, "resource_usage", observation)
            raise operation_error
        assert result is not None
        return result, observation

"""Read-only inspection helpers for an isolated local Ollama runtime."""

from __future__ import annotations

import grp
import hashlib
import os
import pwd
import shutil
import subprocess
from pathlib import Path
from typing import Any


OLLAMA_VERSION = "0.32.14"
OLLAMA_ASSET_SIZE_BYTES = 1_421_191_399
OLLAMA_ASSET_SHA256 = (
    "c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"
)
DEFAULT_RUNTIME_ROOT = Path(
    "/workspace/quannd/local_llm_runtime/ollama/v0.32.14"
)
DEFAULT_CACHE_ROOT = Path("/workspace/quannd/local_llm_cache")
DEFAULT_GPU_UUID = "GPU-5e1bf88a-a431-9a0c-b462-37cd95b5e9b8"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_snapshot(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    stat = resolved.stat()
    disk = shutil.disk_usage(resolved)
    return {
        "path": str(resolved),
        "owner": pwd.getpwuid(stat.st_uid).pw_name,
        "group": grp.getgrgid(stat.st_gid).gr_name,
        "mode": f"{stat.st_mode & 0o777:03o}",
        "world_writable": bool(stat.st_mode & 0o002),
        "disk_total_bytes": disk.total,
        "disk_used_bytes": disk.used,
        "disk_free_bytes": disk.free,
    }


def memory_snapshot() -> dict[str, int]:
    selected = {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}
    values: dict[str, int] = {}
    with Path("/proc/meminfo").open(encoding="utf-8") as handle:
        for line in handle:
            key, _, remainder = line.partition(":")
            if key not in selected:
                continue
            kibibytes = int(remainder.strip().split()[0])
            values[f"{key.lower()}_bytes"] = kibibytes * 1024
    return values


def gpu_snapshot(gpu_uuid: str = DEFAULT_GPU_UUID) -> dict[str, Any]:
    fields = (
        "uuid,name,driver_version,memory.total,memory.used,memory.free,"
        "utilization.gpu"
    )
    command = [
        "/usr/bin/nvidia-smi",
        f"--id={gpu_uuid}",
        f"--query-gpu={fields}",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "error": type(exc).__name__, "uuid": gpu_uuid}
    values = [value.strip() for value in completed.stdout.strip().split(",")]
    if len(values) != 7:
        return {
            "available": False,
            "error": "unexpected_nvidia_smi_output",
            "uuid": gpu_uuid,
        }
    return {
        "available": True,
        "uuid": values[0],
        "name": values[1],
        "driver_version": values[2],
        "memory_total_mib": int(values[3]),
        "memory_used_mib": int(values[4]),
        "memory_free_mib": int(values[5]),
        "utilization_gpu_percent": int(values[6]),
    }


def model_is_preloaded_for_execution(
    running_models: list[dict[str, Any]],
    model_tag: str,
    *,
    context_length: int,
) -> bool:
    for model in running_models:
        if model.get("name") != model_tag and model.get("model") != model_tag:
            continue
        size = int(model.get("size", 0) or 0)
        size_vram = int(model.get("size_vram", 0) or 0)
        loaded_context = int(model.get("context_length", 0) or 0)
        return (
            size > 0
            and size_vram >= size * 0.99
            and loaded_context == context_length
        )
    return False


def inspect_runtime(
    *,
    runtime_root: Path = DEFAULT_RUNTIME_ROOT,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    gpu_uuid: str = DEFAULT_GPU_UUID,
) -> dict[str, Any]:
    binary = runtime_root / "bin" / "ollama"
    archive = runtime_root / "downloads" / "ollama-linux-amd64.tar.zst"
    runtime = path_snapshot(runtime_root)
    cache = path_snapshot(cache_root)
    archive_stat = archive.stat()
    binary_stat = binary.stat()
    archive_sha256 = sha256_file(archive)
    gpu = gpu_snapshot(gpu_uuid)
    return {
        "ollama_version": OLLAMA_VERSION,
        "runtime_root": runtime,
        "cache_root": cache,
        "binary": {
            "path": str(binary.resolve(strict=True)),
            "size_bytes": binary_stat.st_size,
            "sha256": sha256_file(binary),
            "executable_by_owner": bool(binary_stat.st_mode & 0o100),
        },
        "release_asset": {
            "path": str(archive.resolve(strict=True)),
            "size_bytes": archive_stat.st_size,
            "expected_size_bytes": OLLAMA_ASSET_SIZE_BYTES,
            "sha256": archive_sha256,
            "expected_sha256": OLLAMA_ASSET_SHA256,
        },
        "memory": memory_snapshot(),
        "gpu": gpu,
        "checks": {
            "runtime_on_workspace": runtime["path"].startswith("/workspace/"),
            "cache_on_workspace": cache["path"].startswith("/workspace/"),
            "cache_owned_by_current_user": cache["owner"]
            == pwd.getpwuid(os.getuid()).pw_name,
            "cache_not_world_writable": not cache["world_writable"],
            "cache_free_space_at_least_30_gib": cache["disk_free_bytes"]
            >= 30 * 1024**3,
            "binary_executable": bool(binary_stat.st_mode & 0o100),
            "asset_size": archive_stat.st_size == OLLAMA_ASSET_SIZE_BYTES,
            "asset_sha256": archive_sha256 == OLLAMA_ASSET_SHA256,
            "gpu_available": bool(gpu.get("available")),
            "gpu_uuid": gpu.get("uuid") == gpu_uuid,
            "gpu_free_at_least_20_gib": int(gpu.get("memory_free_mib", 0) or 0)
            >= 20 * 1024,
        },
    }

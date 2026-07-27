"""Hash-locked input manifests for Plan 03."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence


def sha256_file(path: Path) -> str:
    """Return a SHA-256 hex digest."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_input_manifest(
    repo_root: Path, input_paths: Sequence[Path], *, created_at: str | None = None
) -> dict[str, object]:
    """Build a stable manifest for explicit input files."""

    records: list[dict[str, object]] = []
    for path in input_paths:
        resolved = path.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(resolved)
        try:
            display_path = str(resolved.relative_to(repo_root.resolve()))
        except ValueError:
            display_path = str(resolved)
        records.append(
            {
                "path": display_path,
                "size_bytes": resolved.stat().st_size,
                "sha256": sha256_file(resolved),
            }
        )
    return {
        "manifest_version": "plan03-input-manifest-v1",
        "created_at": created_at or datetime.now().astimezone().isoformat(),
        "files": records,
    }


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    """Write a deterministic JSON manifest."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

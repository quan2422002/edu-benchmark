"""Shared helpers for learning-resource OCR and Markdown pipelines."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    ensure_directory(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def iter_image_paths(inputs: Sequence[Path], limit: int | None = None) -> Iterator[Path]:
    seen: set[Path] = set()
    count = 0
    for input_path in inputs:
        if input_path.is_dir():
            paths: Iterable[Path] = sorted(
                p for p in input_path.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            )
        elif input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
            paths = [input_path]
        else:
            paths = []

        for path in paths:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path
            count += 1
            if limit is not None and count >= limit:
                return


def read_path_list(path: Path) -> list[Path]:
    items: list[Path] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        items.append(Path(stripped))
    return items


def safe_stem_from_path(path: Path) -> str:
    raw = path.as_posix().strip("/")
    raw = re.sub(r"[^A-Za-z0-9._-]+", "__", raw)
    return raw


def relative_to_cwd(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def coerce_float(value: object, default: float | None = None) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def coerce_int(value: object, default: int | None = None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default

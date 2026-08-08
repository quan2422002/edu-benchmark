#!/usr/bin/env python
"""Build the manifest for Nguyen's OCR Markdown learning resources."""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.learning_resources.ocr_text_manifest import build_manifest_rows, write_manifest  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ocr-root", type=Path, default=Path("shared/learning_resources/ocr_text"))
    parser.add_argument("--source-registry", type=Path, default=Path("shared/learning_resources/registries/sgk_sgv_source_registry.csv"))
    parser.add_argument("--topic-map", type=Path, default=Path("shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv"))
    parser.add_argument("--output", type=Path, default=Path("shared/learning_resources/registries/ocr_text_manifest.csv"))
    parser.add_argument("--grade", default="6", help="Grade to include; use empty string for all grades.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_manifest_rows(
        ocr_root=args.ocr_root,
        source_registry_path=args.source_registry,
        only_grade=args.grade or None,
        topic_map_path=args.topic_map,
    )
    write_manifest(rows, args.output)
    print(f"Wrote {len(rows)} rows -> {args.output}")


if __name__ == "__main__":
    main()

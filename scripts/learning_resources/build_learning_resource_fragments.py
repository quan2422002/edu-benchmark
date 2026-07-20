#!/usr/bin/env python
"""Build learning-resource fragments from OCR Markdown manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.learning_resources.fragment_markdown import build_fragments, write_fragments, write_fragments_readme  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("shared/learning_resources/registries/ocr_text_manifest.csv"))
    parser.add_argument("--output", type=Path, default=Path("shared/learning_resources/fragments/learning_resource_fragments.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_fragments(args.manifest)
    write_fragments(rows, args.output)
    write_fragments_readme(args.output.parent / "README.md")
    print(f"Wrote {len(rows)} fragments -> {args.output}")


if __name__ == "__main__":
    main()

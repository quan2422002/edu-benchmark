#!/usr/bin/env python
"""Build the SQLite retrieval index for learning-resource fragments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.learning_resources.retrieval_index import build_index, write_index_readme  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("shared/learning_resources/registries/ocr_text_manifest.csv"))
    parser.add_argument("--fragments", type=Path, default=Path("shared/learning_resources/fragments/learning_resource_fragments.csv"))
    parser.add_argument("--output", type=Path, default=Path("shared/learning_resources/indexes/learning_resources_v0.sqlite"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = build_index(manifest_path=args.manifest, fragments_path=args.fragments, output_path=args.output)
    write_index_readme(args.output.parent / "README.md")
    print(stats)


if __name__ == "__main__":
    main()

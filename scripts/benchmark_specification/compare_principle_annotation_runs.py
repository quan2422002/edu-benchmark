#!/usr/bin/env python3
"""Compare two closed Plan 03 principle-annotation bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.benchmark_specification.principle_annotation import compare_annotation_bundles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-a", type=Path, required=True)
    parser.add_argument("--bundle-b", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = compare_annotation_bundles(bundle_a=args.bundle_a.resolve(), bundle_b=args.bundle_b.resolve(), thresholds_path=args.thresholds.resolve(), output_dir=args.output_dir.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

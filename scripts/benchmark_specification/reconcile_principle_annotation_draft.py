#!/usr/bin/env python3
"""Derive grounding effects and mandatory review rows before closing a v3 run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.benchmark_specification.principle_annotation import reconcile_annotation_draft


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--coder-id", required=True)
    args = parser.parse_args()
    result = reconcile_annotation_draft(
        bundle_dir=args.bundle_dir.resolve(),
        coder_id=args.coder_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

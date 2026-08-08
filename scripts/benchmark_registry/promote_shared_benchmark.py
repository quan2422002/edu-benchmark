#!/usr/bin/env python
"""Promote or validate the versioned shared benchmark artifact registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.benchmark_registry import (
    promote_shared_benchmark,
    validate_shared_benchmark,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_root = (args.output_root or repo_root / "shared/benchmark").resolve()
    if args.validate_only:
        result = validate_shared_benchmark(output_root)
    else:
        result = promote_shared_benchmark(repo_root, output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


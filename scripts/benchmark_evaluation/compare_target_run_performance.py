#!/usr/bin/env python3
"""Compare aggregate throughput and GPU summaries from two target manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.benchmark_evaluation.performance import (
    compare_target_run_performance,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    comparison = compare_target_run_performance(baseline, candidate)
    print(json.dumps(comparison, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

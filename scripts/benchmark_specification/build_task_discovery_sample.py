#!/usr/bin/env python3
"""Build the deterministic Plan-03 candidate census and discovery sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.benchmark_specification.pipeline import (
    run_task_discovery_preparation,
)

DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT
    )
    parser.add_argument("--per-grade", type=int, default=40)
    parser.add_argument("--seed", default="plan03-task-discovery-v1")
    args = parser.parse_args()
    result = run_task_discovery_preparation(
        args.experiment_root.resolve(),
        per_grade=args.per_grade,
        seed=args.seed,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

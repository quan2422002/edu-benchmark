#!/usr/bin/env python3
"""Run the deterministic Plan-01 conversion pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.benchmark_conversion.pipeline import run_conversion_pilot

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--input-path", type=Path)
    parser.add_argument("--pilot-size-per-grade", type=int, default=10)
    parser.add_argument(
        "--split-strategy",
        choices=["final_tutor_response"],
        default="final_tutor_response",
    )
    args = parser.parse_args()
    result = run_conversion_pilot(
        args.experiment_root.resolve(),
        input_path=args.input_path.resolve() if args.input_path else None,
        size_per_grade=args.pilot_size_per_grade,
        split_strategy=args.split_strategy,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["selected_split_error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

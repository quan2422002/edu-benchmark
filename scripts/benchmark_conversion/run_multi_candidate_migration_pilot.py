#!/usr/bin/env python3
"""Run the approved Plan-02 multi-candidate migration pilot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.benchmark_conversion.pipeline import (
    run_multi_candidate_migration_pilot,
)

DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT
    )
    parser.add_argument("--input-path", type=Path)
    parser.add_argument("--corrections-path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--pilot-size-per-grade", type=int, default=5)
    args = parser.parse_args()
    result = run_multi_candidate_migration_pilot(
        args.experiment_root.resolve(),
        input_path=args.input_path.resolve() if args.input_path else None,
        corrections_path=(
            args.corrections_path.resolve()
            if args.corrections_path
            else None
        ),
        output_dir=args.output_dir.resolve() if args.output_dir else None,
        size_per_grade=args.pilot_size_per_grade,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["blocking_error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

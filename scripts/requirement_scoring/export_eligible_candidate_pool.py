"""CLI argument parsing for exporting the eligible candidate pool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from edu_benchmark.requirement_scoring.export import (
    DEFAULT_ANALYSIS,
    DEFAULT_CANDIDATES,
    DEFAULT_GROUNDING_POOL,
    DEFAULT_OUTPUT,
    DEFAULT_RUN,
    DEFAULT_TRACE,
    export_eligible_candidate_pool,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export eligible_without_plan03_review candidates"
    )
    parser.add_argument("--analysis", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument(
        "--grounding-pool", type=Path, default=DEFAULT_GROUNDING_POOL
    )
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = export_eligible_candidate_pool(
        analysis_path=args.analysis.resolve(),
        run_path=args.run.resolve(),
        grounding_pool_path=args.grounding_pool.resolve(),
        candidates_path=args.candidates.resolve(),
        trace_path=args.trace.resolve(),
        output_path=args.output.resolve(),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

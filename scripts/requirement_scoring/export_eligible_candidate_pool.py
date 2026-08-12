"""CLI argument parsing for exporting the eligible candidate pool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from edu_benchmark.requirement_scoring.config import (
    RequirementScoringConfigError,
    load_requirement_scoring_config,
)
from edu_benchmark.requirement_scoring.export import export_eligible_candidate_pool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export eligible_without_plan03_review candidates"
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--analysis", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--grounding-pool", type=Path)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        config = load_requirement_scoring_config(args.config)
        for field, value in config.export_defaults().items():
            if getattr(args, field) is None:
                setattr(args, field, value)
        summary = export_eligible_candidate_pool(
            analysis_path=args.analysis.resolve(),
            run_path=args.run.resolve(),
            grounding_pool_path=args.grounding_pool.resolve(),
            candidates_path=args.candidates.resolve(),
            trace_path=args.trace.resolve(),
            output_path=args.output.resolve(),
        )
    except (RequirementScoringConfigError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

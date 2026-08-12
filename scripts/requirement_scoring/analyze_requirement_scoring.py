"""CLI argument parsing for deterministic requirement-score analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from edu_benchmark.requirement_scoring.analysis import (
    DEFAULT_BUNDLE,
    DEFAULT_PAPER_REGISTRY,
    DEFAULT_POOL,
    DEFAULT_TRACE,
    analyze_full_run,
)
from edu_benchmark.requirement_scoring.core import RequirementScoringError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze the validated full requirement-scoring run"
    )
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument(
        "--paper-registry", type=Path, default=DEFAULT_PAPER_REGISTRY
    )
    parser.add_argument("--expected-candidates", type=int, default=2028)
    parser.add_argument("--expected-families", type=int, default=665)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        analysis = analyze_full_run(
            bundle_dir=args.bundle_dir.resolve(),
            pool_path=args.pool.resolve(),
            trace_path=args.trace.resolve(),
            paper_registry_path=args.paper_registry.resolve(),
            expected_candidate_count=args.expected_candidates,
            expected_family_count=args.expected_families,
        )
    except (RequirementScoringError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    counts = analysis["eligibility"]["counts"]
    print(
        "Plan 03 completed: "
        f"eligible={counts['eligible_without_plan03_review']}, "
        f"review={counts['needs_uet_review']}, "
        f"blocked={counts['blocked']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

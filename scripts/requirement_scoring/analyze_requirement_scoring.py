"""CLI argument parsing for deterministic requirement-score analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from edu_benchmark.requirement_scoring.analysis import analyze_full_run
from edu_benchmark.requirement_scoring.config import (
    RequirementScoringConfigError,
    load_requirement_scoring_config,
)
from edu_benchmark.requirement_scoring.core import RequirementScoringError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze the validated full requirement-scoring run"
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path)
    parser.add_argument("--pool", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--paper-registry", type=Path)
    parser.add_argument("--expected-candidates", type=int)
    parser.add_argument("--expected-families", type=int)
    parser.add_argument("--selection-seed", type=int)
    parser.add_argument("--control-sample-per-grade", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        config = load_requirement_scoring_config(args.config)
        for field, value in config.analysis_defaults().items():
            if getattr(args, field) is None:
                setattr(args, field, value)
        analysis = analyze_full_run(
            bundle_dir=args.bundle_dir.resolve(),
            pool_path=args.pool.resolve(),
            trace_path=args.trace.resolve(),
            paper_registry_path=args.paper_registry.resolve(),
            expected_candidate_count=args.expected_candidates,
            expected_family_count=args.expected_families,
            selection_seed=args.selection_seed,
            control_sample_per_grade=args.control_sample_per_grade,
            repository_root=config.repository_root,
        )
    except (
        RequirementScoringConfigError,
        RequirementScoringError,
        OSError,
        ValueError,
    ) as exc:
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

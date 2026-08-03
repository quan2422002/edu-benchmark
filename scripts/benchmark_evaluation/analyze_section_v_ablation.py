#!/usr/bin/env python3
"""Build the validated machine-readable Section V analysis bundle."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.edu_benchmark.benchmark_evaluation.section_v_ablation import (
    build_results,
    write_results_atomic,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
FULL_JUDGE = (
    EXPERIMENT
    / "outputs/benchmark_evaluation/full_1400_v1/"
    "judge_full_batch_gold_answer_only_v4"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute Section V instruction ablation, judge robustness, and "
            "descriptive position sensitivity without model calls."
        )
    )
    parser.add_argument(
        "--candidate-pool",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/benchmark_candidate_pool/"
            "eligible_without_plan03_review.csv"
        ),
    )
    parser.add_argument(
        "--gemini-judge",
        type=Path,
        default=FULL_JUDGE / "gemini35/run_judgments.jsonl",
    )
    parser.add_argument(
        "--gpt-judge",
        type=Path,
        default=(
            FULL_JUDGE
            / "openai_gpt54_mini_medium/run_judgments.jsonl"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/benchmark_evaluation/"
            "section_v_ablation_analysis_v1/results.json"
        ),
    )
    parser.add_argument("--bootstrap-iterations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260730)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = build_results(
        candidate_pool=args.candidate_pool,
        gemini_judge=args.gemini_judge,
        gpt_judge=args.gpt_judge,
        iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    write_results_atomic(results, args.output)
    print(
        "Validation: "
        f"{results['judge_robustness']['validation']['status']}"
    )
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()

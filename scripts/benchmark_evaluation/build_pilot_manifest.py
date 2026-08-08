"""Build the locked 80-candidate evaluation pilot manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


from edu_benchmark.benchmark_evaluation.pilot import (  # noqa: E402
    build_pilot_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
DEFAULT_OUTPUT = (
    EXPERIMENT
    / "outputs/benchmark_evaluation/pilot_80_v1/candidate_manifest.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=20260729)
    parser.add_argument("--restarts", type=int, default=96)
    parser.add_argument(
        "--grounding-pool",
        type=Path,
        default=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
    )
    parser.add_argument(
        "--analysis",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/full_run_analysis.json"
        ),
    )
    parser.add_argument(
        "--requirement-run",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
    )
    parser.add_argument(
        "--smoke-anchor-manifest",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/benchmark_evaluation/"
            "smoke_gemini35_instruction_v2/run_manifest.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    expected_root = (
        EXPERIMENT / "outputs/benchmark_evaluation/pilot_80_v1"
    ).resolve()
    if args.output.resolve().parent != expected_root:
        raise ValueError(
            "pilot manifest must be directly under "
            "outputs/benchmark_evaluation/pilot_80_v1"
        )
    manifest = build_pilot_manifest(
        grounding_pool_csv=args.grounding_pool,
        analysis_json=args.analysis,
        requirement_run_jsonl=args.requirement_run,
        smoke_anchor_manifest=args.smoke_anchor_manifest,
        seed=args.seed,
        restarts=args.restarts,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(args.output)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

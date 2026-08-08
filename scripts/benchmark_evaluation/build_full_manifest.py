"""Build the locked manifest for the complete eligible pool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


from edu_benchmark.benchmark_evaluation.full import (  # noqa: E402
    build_full_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eligible-csv",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/benchmark_candidate_pool/"
            "eligible_without_plan03_review.csv"
        ),
    )
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
        "--candidates",
        type=Path,
        default=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
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
        "--output",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/benchmark_evaluation/full_1400_v1/"
            "candidate_manifest.json"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_full_manifest(
        eligible_csv=args.eligible_csv,
        grounding_pool_csv=args.grounding_pool,
        candidate_csv=args.candidates,
        analysis_json=args.analysis,
        requirement_run_jsonl=args.requirement_run,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(args.output)
    print(
        json.dumps(
            {
                "status": "validated_and_locked",
                "candidate_count": manifest["candidate_count"],
                "candidate_ids_sha256": manifest[
                    "candidate_ids_sha256"
                ],
                "execution_gate": manifest["execution_gate"],
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

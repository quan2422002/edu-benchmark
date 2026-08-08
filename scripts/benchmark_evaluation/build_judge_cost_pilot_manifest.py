"""Build the locked 30-candidate judge cost-pilot manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


from edu_benchmark.benchmark_evaluation.cost_pilot import (  # noqa: E402
    build_judge_cost_pilot_manifest,
)

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
EVALUATION = EXPERIMENT / "outputs/benchmark_evaluation"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pilot-manifest", type=Path,
        default=EVALUATION / "pilot_80_v1/candidate_manifest.json",
    )
    parser.add_argument(
        "--grounding-pool", type=Path,
        default=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
    )
    parser.add_argument(
        "--requirement-run", type=Path,
        default=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
    )
    parser.add_argument(
        "--output", type=Path,
        default=(
            EVALUATION
            / "full_1400_v1/judge_cost_pilot_30/"
            "candidate_manifest.json"
        ),
    )
    args = parser.parse_args()
    manifest = build_judge_cost_pilot_manifest(
        pilot_manifest=args.pilot_manifest,
        grounding_pool_csv=args.grounding_pool,
        requirement_run_jsonl=args.requirement_run,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(args.output)
    print(json.dumps({
        "status": "validated_and_locked",
        "candidate_count": manifest["candidate_count"],
        "coverage": manifest["coverage"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build and validate the Plan 05 configuration bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


from edu_benchmark.benchmark_evaluation.config_builder import (  # noqa: E402
    build_evaluation_config,
)
from edu_benchmark.benchmark_evaluation.validation import (  # noqa: E402
    validate_evaluation_config,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=EXPERIMENT / "outputs/benchmark_evaluation",
    )
    parser.add_argument(
        "--principles",
        type=Path,
        default=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/principle_foundation/"
            "pedagogical_principles.csv"
        ),
    )
    parser.add_argument(
        "--rubrics",
        type=Path,
        default=EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv",
    )
    parser.add_argument(
        "--serious-errors",
        type=Path,
        default=EXPERIMENT / "outputs/benchmark_rubric/serious_errors.csv",
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
        "--instruction-bundle",
        type=Path,
        default=(
            ROOT
            / "shared/prompts/benchmark_tutor_response_generation/"
            "instruction_bundle_v1.yaml"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_evaluation_config(
        output_dir=args.output_dir,
        principles_csv=args.principles,
        rubrics_csv=args.rubrics,
        serious_errors_csv=args.serious_errors,
        candidates_csv=args.candidates,
        analysis_json=args.analysis,
        instruction_bundle_path=args.instruction_bundle,
    )
    summary["validation"] = validate_evaluation_config(args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

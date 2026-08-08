#!/usr/bin/env python3
"""Create the approved Plan-03 A-D input manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.benchmark_specification.manifest import (
    build_input_manifest,
    write_manifest,
)

DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT
    )
    parser.add_argument("--created-at")
    args = parser.parse_args()
    experiment_root = args.experiment_root.resolve()
    paths = [
        experiment_root
        / "outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv",
        experiment_root
        / "outputs/benchmark_conversion/full_v0/conversion_trace.csv",
        experiment_root
        / "outputs/benchmark_conversion/full_v0/conversion_dispositions.csv",
        experiment_root
        / "outputs/benchmark_conversion/full_v0/conversion_summary.json",
        REPO_ROOT
        / "shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv",
        REPO_ROOT
        / "shared/learning_resources/fragments/learning_resource_fragments.csv",
        REPO_ROOT
        / "shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md",
        REPO_ROOT
        / "shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md",
    ]
    manifest = build_input_manifest(
        REPO_ROOT,
        paths,
        created_at=args.created_at,
    )
    output = (
        experiment_root
        / "outputs/benchmark_specification/plan03_a_to_d_input_manifest.json"
    )
    write_manifest(output, manifest)
    print(json.dumps({"output": str(output), **manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

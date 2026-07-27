#!/usr/bin/env python3
"""Build isolated context/grounding inputs for Plan 03 schema v3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.benchmark_specification.principle_annotation import (
    build_annotation_inputs,
    validate_input_pair,
)

TASK_DISCOVERY = (
    REPO_ROOT
    / "experiments/20260722_000940/outputs/benchmark_specification/task_discovery"
)
DEFAULT_INPUT = TASK_DISCOVERY / "method_revision_v3/candidate_principle_grounding_pool.csv"
DEFAULT_SELECTION = TASK_DISCOVERY / "task_discovery_sample.csv"
DEFAULT_OUTPUT = TASK_DISCOVERY / "method_revision_v3/pilot_40"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grounding-input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--per-grade", type=int, default=10)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    result = build_annotation_inputs(
        repo_root=REPO_ROOT,
        grounding_input_path=args.grounding_input.resolve(),
        selection_path=args.selection.resolve(),
        output_dir=output_dir,
        per_grade=args.per_grade,
    )
    validation = validate_input_pair(
        repo_root=REPO_ROOT,
        context_path=output_dir / "principle_annotation_pass1_input.csv",
        grounding_path=output_dir / "principle_annotation_grounding_input.csv",
        manifest_path=output_dir / "principle_annotation_grounding_manifest.json",
    )
    print(
        json.dumps(
            {"build": result, "validation": validation},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

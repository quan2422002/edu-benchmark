#!/usr/bin/env python
"""Build the source-grounded candidate pool for Plan 03 principle annotation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.benchmark_specification.principle_grounding import (
    materialize_principle_grounding_pool,
)

DEFAULT_CANDIDATE_INPUT = (
    REPO_ROOT
    / "experiments/20260722_000940/outputs/benchmark_conversion/full_v0"
    / "benchmark_candidate_splits.csv"
)
DEFAULT_SOURCE_INPUTS = (
    REPO_ROOT
    / "experiments/20260722_000940/inherited_resources/from_20260709_155523"
    / "raw_audit_grade6_7/normalized_dialogue_rows.csv",
    REPO_ROOT
    / "experiments/20260722_000940/inherited_resources/from_20260709_155523"
    / "raw_audit_grade8_9/normalized_dialogue_rows.csv",
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "experiments/20260722_000940/outputs/benchmark_specification"
    / "task_discovery/method_revision_v3"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-input", type=Path, default=DEFAULT_CANDIDATE_INPUT)
    parser.add_argument(
        "--source-dialogue",
        action="append",
        type=Path,
        dest="source_dialogues",
        help="Normalized source-dialogue CSV; repeat for every source snapshot.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--created-at")
    args = parser.parse_args()
    result = materialize_principle_grounding_pool(
        repo_root=REPO_ROOT,
        candidate_path=args.candidate_input,
        source_dialogue_paths=tuple(args.source_dialogues or DEFAULT_SOURCE_INPUTS),
        output_dir=args.output_dir,
        created_at=args.created_at,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the experiment-scoped two-table retrieval index for fragment v1/v1.1."""

from __future__ import annotations

import argparse
from pathlib import Path

from edu_benchmark.learning_resources.retrieval_index_v1 import (
    build_index_v1,
    write_index_validation_summary,
)


DEFAULT_ROOT = Path("experiments/20260903_135547/outputs")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fragments",
        type=Path,
        default=(
            DEFAULT_ROOT
            / "fragment_v1_1_v4/learning_resource_fragments_v1_1.csv"
        ),
    )
    parser.add_argument(
        "--sections",
        type=Path,
        default=DEFAULT_ROOT / "fragment_v1/learning_sections_v1.csv",
    )
    parser.add_argument(
        "--fragment-validation",
        type=Path,
        default=(
            DEFAULT_ROOT
            / "fragment_v1_1_v4/fragment_v1_1_validation_summary.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROOT / "retrieval_v1_2/learning_resources_v1_2.sqlite",
    )
    parser.add_argument(
        "--validation-output",
        type=Path,
        default=DEFAULT_ROOT / "retrieval_v1_2/retrieval_validation_summary.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_index_v1(
        fragments_path=args.fragments,
        sections_path=args.sections,
        validation_summary_path=args.fragment_validation,
        output_path=args.output,
    )
    write_index_validation_summary(summary, args.validation_output)


if __name__ == "__main__":
    main()

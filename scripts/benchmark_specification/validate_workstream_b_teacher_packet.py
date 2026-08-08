#!/usr/bin/env python3
"""Validate the Plan-03 Workstream-B HNMU/UET consultation packet."""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.benchmark_specification.schema import read_csv_rows
from edu_benchmark.benchmark_specification.teacher_packet import (
    validate_workstream_b_teacher_packet,
)

DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT
    )
    args = parser.parse_args()
    output_root = (
        args.experiment_root.resolve() / "outputs/benchmark_specification"
    )
    capabilities = read_csv_rows(
        output_root / "construct_v1_draft/tutor_capabilities.csv"
    )
    overlaps = read_csv_rows(
        output_root / "construct_v1_draft/capability_overlap_matrix.csv"
    )
    errors = validate_workstream_b_teacher_packet(
        output_root / "teacher_review_packets/workstream_b_round1",
        capability_ids={row["capability_id"] for row in capabilities},
        overlap_pairs={
            tuple(sorted((row["capability_id_a"], row["capability_id_b"])))
            for row in overlaps
        },
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: Workstream-B teacher packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

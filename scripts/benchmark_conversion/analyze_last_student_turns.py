#!/usr/bin/env python3
"""Analyze pass dialogues that end with a student turn."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.benchmark_conversion.last_turn_analysis import (
    LAST_TURN_ANALYSIS_COLUMNS,
    analyze_last_student_turns,
)
from edu_benchmark.benchmark_conversion.pipeline import read_csv_rows, write_csv_rows

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    args = parser.parse_args()
    output_root = (
        args.experiment_root.resolve() / "outputs" / "benchmark_conversion"
    )
    source_path = output_root / "conversion_input_pass_samples.csv"
    rows, summary = analyze_last_student_turns(read_csv_rows(source_path))
    write_csv_rows(
        output_root / "last_student_turn_analysis.csv",
        LAST_TURN_ANALYSIS_COLUMNS,
        rows,
    )
    (output_root / "last_student_turn_analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

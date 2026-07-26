#!/usr/bin/env python3
"""Build or validate the local teacher-facing HNMU Phase 1 bundle."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from edu_benchmark.dialogue_audit.teacher_bundle import (
    build_phase1_teacher_bundle,
    validate_phase1_teacher_bundle,
)

DEFAULT_EXPERIMENT_DIR = Path("experiments/20260709_155523")
DEFAULT_BUNDLE_DIR = DEFAULT_EXPERIMENT_DIR / "deliverables/hnmu_dialogue_audit_phase1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package canonical Plan 04 outputs into four teacher-facing Excel workbooks."
    )
    parser.add_argument("--experiment-dir", type=Path, default=DEFAULT_EXPERIMENT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_BUNDLE_DIR)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        result = validate_phase1_teacher_bundle(args.experiment_dir, args.output_dir)
    else:
        result = asdict(
            build_phase1_teacher_bundle(
                args.experiment_dir,
                args.output_dir,
                overwrite=args.overwrite,
            )
        )
        result["output_paths"] = [path.as_posix() for path in result["output_paths"]]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

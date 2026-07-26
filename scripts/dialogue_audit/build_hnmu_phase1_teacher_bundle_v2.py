#!/usr/bin/env python3
"""Build or validate the type-oriented local HNMU Phase 1 bundle v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.dialogue_audit.teacher_bundle_v2_complete import (
    rebuild_complete_phase1_teacher_bundle_v2 as build_phase1_teacher_bundle_v2,
    validate_complete_phase1_teacher_bundle_v2 as validate_phase1_teacher_bundle_v2,
)

DEFAULT_EXPERIMENT_DIR = Path("experiments/20260709_155523")
DEFAULT_BUNDLE_DIR = DEFAULT_EXPERIMENT_DIR / "deliverables/hnmu_dialogue_audit_phase1_v2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild the complete repaired canonical HNMU Phase 1 teacher bundle."
    )
    parser.add_argument("--experiment-dir", type=Path, default=DEFAULT_EXPERIMENT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_BUNDLE_DIR)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        result = validate_phase1_teacher_bundle_v2(args.experiment_dir, args.output_dir)
    else:
        result = build_phase1_teacher_bundle_v2(args.experiment_dir, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

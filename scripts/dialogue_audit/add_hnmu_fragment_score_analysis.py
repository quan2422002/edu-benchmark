#!/usr/bin/env python3
"""Rebuild or validate the complete repaired HNMU v2 bundle.

This compatibility entry point delegates to the canonical complete builder so it
cannot recreate fragment workbooks from the pre-repair checklist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.dialogue_audit.teacher_bundle_v2_complete import (
    rebuild_complete_phase1_teacher_bundle_v2 as add_fragment_analysis_outputs,
    validate_complete_phase1_teacher_bundle_v2 as validate_fragment_analysis_outputs,
)

DEFAULT_EXPERIMENT_DIR = Path("experiments/20260709_155523")
DEFAULT_BUNDLE_DIR = (
    DEFAULT_EXPERIMENT_DIR / "deliverables/hnmu_dialogue_audit_phase1_v2"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild the complete HNMU v2 bundle from repaired canonical sources."
    )
    parser.add_argument("--experiment-dir", type=Path, default=DEFAULT_EXPERIMENT_DIR)
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE_DIR)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        result = validate_fragment_analysis_outputs(args.experiment_dir, args.bundle_dir)
    else:
        result = add_fragment_analysis_outputs(args.experiment_dir, args.bundle_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

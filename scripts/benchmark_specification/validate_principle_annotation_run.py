#!/usr/bin/env python3
"""Validate one closed Plan 03 principle-annotation bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.benchmark_specification.principle_annotation import validate_annotation_bundle, validate_input_pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--coder-id", required=True)
    args = parser.parse_args()
    input_dir = args.input_dir.resolve()
    validate_input_pair(
        repo_root=REPO_ROOT,
        context_path=input_dir / "principle_annotation_pass1_input.csv",
        grounding_path=input_dir / "principle_annotation_grounding_input.csv",
        manifest_path=input_dir / "principle_annotation_grounding_manifest.json",
    )
    result = validate_annotation_bundle(input_dir=input_dir, bundle_dir=args.bundle_dir.resolve(), coder_id=args.coder_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate and publish the provisional Plan-03 B-D specialist bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.benchmark_specification.publication import (
    publish_specialist_draft,
)

DEFAULT_EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "20260722_000940"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT
    )
    parser.add_argument("--draft-root", type=Path)
    args = parser.parse_args()
    experiment_root = args.experiment_root.resolve()
    draft_root = (
        args.draft_root.resolve()
        if args.draft_root
        else (
            experiment_root
            / "outputs/benchmark_specification/specialist_draft"
        )
    )
    manifest = publish_specialist_draft(
        REPO_ROOT,
        experiment_root,
        draft_root,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

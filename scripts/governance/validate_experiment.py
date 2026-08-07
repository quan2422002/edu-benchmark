#!/usr/bin/env python3
"""Validate experiment governance metadata, plans, links, and artifact budgets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
# Temporary bootstrap until Plan 02 makes the src-layout package installable.
sys.path.insert(0, str(REPO_ROOT / "src"))

from edu_benchmark.governance import validate_experiment, validate_templates  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", type=Path, help="Experiment directory to validate")
    parser.add_argument(
        "--skip-templates",
        action="store_true",
        help="Do not validate the repository-wide governance templates",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiment = args.experiment
    if not experiment.is_absolute():
        experiment = REPO_ROOT / experiment
    issues = validate_experiment(experiment, repo_root=REPO_ROOT)
    if not args.skip_templates:
        issues.extend(validate_templates(REPO_ROOT))
    if issues:
        for issue in issues:
            print(issue.format(REPO_ROOT), file=sys.stderr)
        raise SystemExit(1)
    print(f"Governance validation passed: {experiment.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()


"""CLI argument parsing and dispatch for requirement-scoring operations."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from edu_benchmark.requirement_scoring.config import (
    RequirementScoringConfigError,
    load_requirement_scoring_config,
)
from edu_benchmark.requirement_scoring.core import RequirementScoringError
from edu_benchmark.requirement_scoring.workflow import (
    execute_run,
    finalize,
    finalize_full,
    prepare,
    retry_failed_full,
    run_full_dataset,
    run_full_pilot,
)


def add_common_arguments(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pool", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--bundle-name")
    parser.add_argument("--prompt", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--spec-manifest", type=Path)
    parser.add_argument("--calibration-input", type=Path)
    parser.add_argument("--snapshot-manifest", type=Path)
    parser.add_argument("--project")
    parser.add_argument("--location")
    parser.add_argument("--model")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--thinking-budget", type=int)
    parser.add_argument(
        "--thinking-level", choices=("MINIMAL", "LOW", "MEDIUM", "HIGH")
    )
    parser.add_argument(
        "--include-thoughts",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    parser.add_argument("--selection-seed", type=int)
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--max-retries", type=int)
    parser.add_argument("--max-requests", type=int)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--retry-base-delay-seconds", type=float)
    parser.add_argument("--spot-check-count", type=int)
    parser.add_argument(
        "--progress",
        action=argparse.BooleanOptionalAction,
        default=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Vertex AI pedagogical-principle requirement scoring"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("prepare", "finalize", "pilot", "calibration"):
        subparser = subparsers.add_parser(command)
        add_common_arguments(subparser)
        if command in {"pilot", "calibration"}:
            subparser.add_argument("--execute-api", action="store_true")
    for command in ("full", "retry-failed", "refresh-full-manifest"):
        subparser = subparsers.add_parser(command)
        add_common_arguments(subparser)
        if command == "retry-failed":
            subparser.add_argument("--additional-retries", type=int, default=2)
        if command != "refresh-full-manifest":
            subparser.add_argument("--execute-api", action="store_true")
    run_parser = subparsers.add_parser("run")
    add_common_arguments(run_parser)
    run_parser.add_argument("--run-id", choices=("a", "b"), required=True)
    run_parser.add_argument("--execute-api", action="store_true")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI overrides and fill omitted values from the selected config."""

    args = build_parser().parse_args(argv)
    config = load_requirement_scoring_config(args.config)
    args.config = config.path
    args.config_id = str(config.raw["config_id"])
    defaults = config.run_defaults(args.command)
    for field, value in defaults.items():
        if field == "thinking_level" and args.thinking_budget is not None:
            continue
        if field == "thinking_budget" and args.thinking_level is not None:
            continue
        if not hasattr(args, field) or getattr(args, field) is None:
            setattr(args, field, value)
    return args


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
    except (RequirementScoringConfigError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for field in (
        "pool",
        "output_root",
        "prompt",
        "schema",
        "spec_manifest",
        "calibration_input",
        "snapshot_manifest",
    ):
        setattr(args, field, getattr(args, field).resolve())
    try:
        if args.command == "prepare":
            prepare(args)
        elif args.command == "run":
            execute_run(args, run_id=args.run_id)
        elif args.command == "finalize":
            finalize(args)
        elif args.command in {"pilot", "calibration"}:
            run_full_pilot(args)
        elif args.command == "full":
            run_full_dataset(args)
        elif args.command == "retry-failed":
            retry_failed_full(args)
        elif args.command == "refresh-full-manifest":
            finalize_full(args)
    except (RequirementScoringError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI argument parsing and dispatch for requirement-scoring operations."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from edu_benchmark.requirement_scoring.core import RequirementScoringError
from edu_benchmark.requirement_scoring.workflow import (
    DEFAULT_CALIBRATION_INPUT,
    DEFAULT_LOCATION,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_POOL,
    DEFAULT_PROJECT,
    DEFAULT_PROMPT,
    DEFAULT_SCHEMA,
    DEFAULT_SNAPSHOT_MANIFEST,
    DEFAULT_SPEC_MANIFEST,
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
    *,
    default_max_requests: int = 120,
    default_concurrency: int = 20,
) -> None:
    parser.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--bundle-name")
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--spec-manifest", type=Path, default=DEFAULT_SPEC_MANIFEST)
    parser.add_argument(
        "--calibration-input", type=Path, default=DEFAULT_CALIBRATION_INPUT
    )
    parser.add_argument(
        "--snapshot-manifest", type=Path, default=DEFAULT_SNAPSHOT_MANIFEST
    )
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument("--model", default="gemini-3.5-flash")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--thinking-budget", type=int)
    parser.add_argument(
        "--thinking-level", choices=("MINIMAL", "LOW", "MEDIUM", "HIGH")
    )
    parser.add_argument(
        "--include-thoughts",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument("--selection-seed", type=int, default=20260727)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--max-requests", type=int, default=default_max_requests)
    parser.add_argument("--concurrency", type=int, default=default_concurrency)
    parser.add_argument("--retry-base-delay-seconds", type=float, default=2.0)
    parser.add_argument("--spot-check-count", type=int, default=4)
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
        add_common_arguments(
            subparser, default_max_requests=2500, default_concurrency=20
        )
        if command == "retry-failed":
            subparser.add_argument("--additional-retries", type=int, default=2)
        if command != "refresh-full-manifest":
            subparser.add_argument("--execute-api", action="store_true")
    run_parser = subparsers.add_parser("run")
    add_common_arguments(run_parser)
    run_parser.add_argument("--run-id", choices=("a", "b"), required=True)
    run_parser.add_argument("--execute-api", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
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

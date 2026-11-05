#!/usr/bin/env python3
"""Prepare or run the approved Plan 03 HNMU tool-calling pilot."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from loguru import logger

from edu_benchmark.dialogue_audit.agent_audit import (
    PilotConfig,
    PilotContractError,
    PilotExecutionError,
    prepare_pilot,
    run_cluster_recovery,
    run_pilot_split,
    smoke_sbt_section_normalization,
    validate_cluster_recovery_inputs,
    validate_pilot_inputs,
)


DEFAULT_CONFIG = Path(
    "experiments/20260903_135547/configs/"
    "plan03-tool-calling-pilot-v5-4-regression.json"
)
DEFAULT_OUTPUT_ROOT = Path(
    "experiments/20260903_135547/outputs/plan03_tool_calling_pilot"
)


def parse_args() -> argparse.Namespace:
    """Parse the thin command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--debug-diagnose",
        action="store_true",
        help=(
            "Include local variable values in unexpected-error tracebacks. "
            "Use only with a protected log because dialogue/prompt data may appear."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser(
        "prepare",
        help="Lock the configured deterministic selection without calling a model.",
    )
    prepare.add_argument("--overwrite-selection", action="store_true")

    subparsers.add_parser(
        "validate",
        help="Validate locked inputs and run fingerprints without calling a model.",
    )
    subparsers.add_parser(
        "validate-recovery",
        help="Validate one locked parent/cluster recovery without calling a model.",
    )
    smoke = subparsers.add_parser(
        "smoke-sbt-section",
        help="Compare canonical and decorated SBT section scope without a model call.",
    )
    smoke.add_argument("--grade", required=True)
    smoke.add_argument("--lesson", required=True)
    smoke.add_argument("--position", required=True)
    smoke.add_argument("--canonical-section-keywords", required=True)
    smoke.add_argument("--decorated-section-keywords", required=True)
    smoke.add_argument("--content-keywords", required=True)
    smoke.add_argument("--output", type=Path, required=True)

    run = subparsers.add_parser(
        "run",
        help="Run one paid development or holdout split through Vertex AI.",
    )
    run.add_argument("--split", choices=("development", "holdout"), required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    run.add_argument("--project")
    run.add_argument("--resume", action="store_true")
    run.add_argument(
        "--execute-api",
        action="store_true",
        help="Required opt-in gate for paid Vertex AI calls.",
    )
    recover = subparsers.add_parser(
        "recover-cluster",
        help="Recover the single cluster locked in the approved recovery config.",
    )
    recover.add_argument("--run-id", required=True)
    recover.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    recover.add_argument("--project")
    recover.add_argument(
        "--execute-api",
        action="store_true",
        help="Required opt-in gate for the paid Vertex AI recovery call.",
    )
    return parser.parse_args()


def _vertex_client(*, project: str, location: str, timeout_seconds: float):
    """Create one ADC-authenticated Google Gen AI client for Vertex AI."""

    import google.auth
    from google import genai
    from google.auth.exceptions import DefaultCredentialsError
    from google.genai import types

    try:
        credentials, _ = google.auth.default(quota_project_id=project)
    except DefaultCredentialsError as exc:
        raise PilotContractError(
            "Application Default Credentials are unavailable; run gcloud auth application-default login"
        ) from exc
    return genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials,
        http_options=types.HttpOptions(
            api_version="v1",
            timeout=int(timeout_seconds * 1000),
        ),
    )


def _configure_logging(*, diagnose: bool) -> None:
    """Configure immediate stderr logs without exposing locals by default."""

    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if diagnose else "INFO",
        backtrace=True,
        diagnose=diagnose,
        colorize=False,
        enqueue=False,
    )


def _run(args: argparse.Namespace) -> None:
    """Dispatch preparation or explicitly authorized execution."""

    config = PilotConfig.from_json(args.config)
    logger.info("Loaded Plan 03 config path={} command={}", args.config, args.command)
    if args.command == "prepare":
        result = prepare_pilot(config, overwrite_selection=args.overwrite_selection)
        logger.info(
            "Preparation completed summary={} ",
            json.dumps(result, ensure_ascii=False, sort_keys=True),
        )
        return
    if args.command == "validate":
        result = validate_pilot_inputs(config)
        logger.info(
            "Input validation completed summary={}",
            json.dumps(result, ensure_ascii=False, sort_keys=True),
        )
        return
    if args.command == "validate-recovery":
        result = validate_cluster_recovery_inputs(config)
        logger.info(
            "Recovery validation completed summary={}",
            json.dumps(result, ensure_ascii=False, sort_keys=True),
        )
        return
    if args.command == "smoke-sbt-section":
        result = smoke_sbt_section_normalization(
            index_path=config.retrieval_index_path,
            grade=args.grade,
            lesson=args.lesson,
            position=args.position,
            canonical_section_keywords=args.canonical_section_keywords,
            decorated_section_keywords=args.decorated_section_keywords,
            content_keywords=args.content_keywords,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info(
            "SBT section smoke completed output={} summary={}",
            args.output,
            json.dumps(result, ensure_ascii=False, sort_keys=True),
        )
        return

    if args.command == "recover-cluster" and config.recovery is None:
        raise PilotContractError(
            "recover-cluster requires a config with a recovery block"
        )
    if args.command == "run" and config.recovery is not None:
        raise PilotContractError(
            "A recovery config cannot run a full split; use recover-cluster"
        )

    if not args.execute_api:
        raise PilotContractError(
            "Paid model execution is disabled. Add --execute-api only when Quân intentionally runs the pilot."
        )
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None
    if load_dotenv is not None:
        load_dotenv()
    project = (
        str(args.project or "").strip()
        or os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
        or os.environ.get("VERTEX_AI_PROJECT", "").strip()
    )
    if not project:
        raise PilotContractError(
            "Vertex project is required via --project, GOOGLE_CLOUD_PROJECT, or VERTEX_AI_PROJECT"
        )
    output_dir = args.output_root / args.run_id
    client = _vertex_client(
        project=project,
        location=config.location,
        timeout_seconds=config.timeout_seconds,
    )
    logger.info(
        "Vertex client initialized project={} location={} command={} split={} run_id={} resume={}",
        project,
        config.location,
        args.command,
        getattr(args, "split", config.recovery.split if config.recovery else ""),
        args.run_id,
        getattr(args, "resume", False),
    )
    try:
        if args.command == "recover-cluster":
            summary = run_cluster_recovery(
                config=config,
                output_dir=output_dir,
                client=client,
            )
        else:
            summary = run_pilot_split(
                config=config,
                split=args.split,
                output_dir=output_dir,
                client=client,
                resume=args.resume,
            )
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()
    logger.info(
        "Run completed summary={}",
        json.dumps(summary, ensure_ascii=False, sort_keys=True),
    )


def main() -> None:
    """Configure logging and map failures to one nonzero process exit."""

    args = parse_args()
    _configure_logging(diagnose=args.debug_diagnose)
    try:
        _run(args)
    except (PilotContractError, PilotExecutionError) as exc:
        logger.error("Plan 03 command failed: {}: {}", type(exc).__name__, exc)
        raise SystemExit(1) from None
    except Exception:
        logger.exception("Unexpected Plan 03 command failure")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()

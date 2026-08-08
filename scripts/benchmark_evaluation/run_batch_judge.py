"""Prepare, submit, monitor, collect, and retry full judge batches."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
from typing import Any, Mapping


import google.auth  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402
from openai import OpenAI  # noqa: E402

from edu_benchmark.benchmark_evaluation.batch_judge import (  # noqa: E402
    BatchJudgeError,
    actual_cost_usd,
    append_jsonl,
    atomic_json,
    atomic_jsonl,
    build_gemini_batch_line,
    build_judgment_record,
    build_openai_batch_line,
    empirical_cost_projection,
    file_hash,
    parse_gemini_batch_output,
    parse_openai_batch_output,
    read_jsonl,
    utc_now,
    validate_judgment_records,
)
from edu_benchmark.benchmark_evaluation.judge import (  # noqa: E402
    PreparedJudgeRequest,
    prepare_judge_requests,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
EVALUATION_ROOT = EXPERIMENT / "outputs/benchmark_evaluation"
FULL_ROOT = EVALUATION_ROOT / "full_1400_v1"
DEFAULT_TARGETS = (
    FULL_ROOT / "target_gemini35/run_responses.jsonl",
    FULL_ROOT / "target_llama4_maverick/run_responses.jsonl",
    FULL_ROOT
    / "target_gemini35_learnlm_prompted/run_responses.jsonl",
)
TERMINAL_GEMINI_STATES = frozenset(
    {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_PAUSED",
        "JOB_STATE_EXPIRED",
    }
)
TERMINAL_OPENAI_STATES = frozenset(
    {"completed", "failed", "expired", "cancelled"}
)


def portable(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=(
            "prepare",
            "submit",
            "status",
            "collect",
            "watch",
            "retry-submit",
        ),
    )
    parser.add_argument("--provider", choices=("gemini", "openai"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--project", default="edu-benchmark")
    parser.add_argument("--location", default="global")
    parser.add_argument("--gcs-uri-prefix")
    parser.add_argument(
        "--gcloud-bin",
        type=Path,
        default=ROOT / "google-cloud-sdk/bin/gcloud",
    )
    parser.add_argument(
        "--api-key-env-file", type=Path, default=ROOT / "src/.env"
    )
    parser.add_argument("--target-run", type=Path, action="append", dest="target_runs")
    parser.add_argument(
        "--candidate-manifest",
        type=Path,
        default=FULL_ROOT / "candidate_manifest.json",
    )
    parser.add_argument(
        "--system-prompt",
        type=Path,
        default=(
            ROOT
            / "shared/prompts/benchmark_response_judging/"
            "system_prompt_gold_answer_only_v4.md"
        ),
    )
    parser.add_argument("--judge-contract", default="gold-answer-only-v4")
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--thinking-level", default="medium")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--retry-max-output-tokens", type=int)
    parser.add_argument("--max-batch-retries", type=int, default=1)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--input-usd-per-million", type=float, required=True)
    parser.add_argument("--output-usd-per-million", type=float, required=True)
    parser.add_argument("--calibration-judgments", type=Path, required=True)
    parser.add_argument("--budget-safety-multiplier", type=float, default=1.10)
    parser.add_argument("--stage-cap-usd", type=float, required=True)
    parser.add_argument("--remaining-budget-usd", type=float, required=True)
    parser.add_argument(
        "--candidate-csv",
        type=Path,
        default=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
        ),
    )
    parser.add_argument(
        "--grounding-pool",
        type=Path,
        default=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
    )
    parser.add_argument(
        "--conversion-input",
        type=Path,
        default=(
            ROOT
            / "experiments/20260722_000940/outputs/"
            "benchmark_conversion/conversion_input_pass_samples.csv"
        ),
    )
    parser.add_argument(
        "--learning-fragments",
        type=Path,
        default=(
            ROOT
            / "shared/learning_resources/fragments/"
            "learning_resource_fragments.csv"
        ),
    )
    parser.add_argument(
        "--requirement-run",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
    )
    parser.add_argument(
        "--rubrics",
        type=Path,
        default=EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv",
    )
    parser.add_argument(
        "--serious-errors",
        type=Path,
        default=EXPERIMENT / "outputs/benchmark_rubric/serious_errors.csv",
    )
    parser.add_argument(
        "--evaluation-schema",
        type=Path,
        default=EVALUATION_ROOT / "evaluation_schema.json",
    )
    parser.add_argument("--execute-api", action="store_true")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.judge_contract != "gold-answer-only-v4":
        raise ValueError("full batch runner is locked to gold-answer-only-v4")
    if (
        args.max_output_tokens <= 0
        or (
            args.retry_max_output_tokens is not None
            and args.retry_max_output_tokens <= 0
        )
        or args.poll_seconds <= 0
    ):
        raise ValueError("token and polling limits must be positive")
    if args.max_batch_retries < 0:
        raise ValueError("max-batch-retries must be non-negative")
    if (
        args.input_usd_per_million < 0
        or args.output_usd_per_million < 0
        or args.stage_cap_usd <= 0
        or args.remaining_budget_usd <= 0
        or args.budget_safety_multiplier < 1
    ):
        raise ValueError("invalid batch pricing or budget configuration")
    if args.provider == "gemini" and not args.gcs_uri_prefix:
        raise ValueError("Gemini batch requires --gcs-uri-prefix")
    if args.provider == "gemini" and not args.gcloud_bin.is_file():
        raise ValueError(f"gcloud executable not found: {args.gcloud_bin}")
    if args.output_dir.resolve() == EVALUATION_ROOT.resolve() or not (
        args.output_dir.resolve().is_relative_to(EVALUATION_ROOT.resolve())
    ):
        raise ValueError("output-dir must be inside benchmark_evaluation")
    if args.action != "prepare" and not args.execute_api:
        raise ValueError(
            f"{args.action} contacts a provider; add --execute-api explicitly"
        )


def load_candidate_ids(path: Path) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    ids = value.get("candidate_ids")
    if not isinstance(ids, list):
        raise ValueError("candidate manifest must contain candidate_ids")
    result = [str(item).strip() for item in ids]
    if len(result) != 1400 or len(set(result)) != 1400 or any(not item for item in result):
        raise ValueError("full candidate manifest must contain 1,400 unique IDs")
    return result


def prepare_requests(args: argparse.Namespace) -> list[PreparedJudgeRequest]:
    fixed_ids = load_candidate_ids(args.candidate_manifest)
    target_runs = args.target_runs or list(DEFAULT_TARGETS)
    prepared = prepare_judge_requests(
        candidate_csv=args.candidate_csv,
        grounding_pool_csv=args.grounding_pool,
        conversion_input_csv=args.conversion_input,
        learning_fragments_csv=args.learning_fragments,
        requirement_run_jsonl=args.requirement_run,
        rubrics_csv=args.rubrics,
        serious_errors_csv=args.serious_errors,
        target_run_jsonls=target_runs,
        system_prompt_path=args.system_prompt,
        seed=args.seed,
        expected_candidates_per_run=1400,
        expected_target_run_count=3,
        fixed_candidate_ids=fixed_ids,
        judge_output_contract_version=args.judge_contract,
    )
    counts = Counter(item.benchmark_candidate_id for item in prepared)
    if (
        len(prepared) != 4200
        or len(counts) != 1400
        or set(counts.values()) != {3}
        or len({item.comparison_id for item in prepared}) != 4200
    ):
        raise RuntimeError(
            "full batch requires 1,400 candidates x 3 targets = 4,200 comparisons"
        )
    return prepared


def input_paths(args: argparse.Namespace) -> list[Path]:
    return [
        args.candidate_csv,
        args.grounding_pool,
        args.requirement_run,
        args.rubrics,
        args.evaluation_schema,
        args.system_prompt,
        args.candidate_manifest,
        args.calibration_judgments,
        *(args.target_runs or list(DEFAULT_TARGETS)),
    ]


def config_fingerprint(args: argparse.Namespace, prepared: list[PreparedJudgeRequest]) -> str:
    value = {
        "provider": args.provider,
        "model": args.model,
        "project": args.project if args.provider == "gemini" else None,
        "location": args.location if args.provider == "gemini" else "direct_api",
        "judge_contract": args.judge_contract,
        "seed": args.seed,
        "thinking_level": args.thinking_level if args.provider == "gemini" else None,
        "reasoning_effort": args.reasoning_effort if args.provider == "openai" else None,
        "max_output_tokens": args.max_output_tokens,
        "comparison_ids": [item.comparison_id for item in prepared],
        "request_hashes": [item.request_sha256 for item in prepared],
        "input_sha256": {portable(path): file_hash(path) for path in input_paths(args)},
    }
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def judgment_path(args: argparse.Namespace) -> Path:
    return args.output_dir / "run_judgments.jsonl"


def manifest_path(args: argparse.Namespace) -> Path:
    return args.output_dir / "batch_manifest.json"


def error_path(args: argparse.Namespace) -> Path:
    return args.output_dir / "run_errors.jsonl"


def load_existing_records(
    args: argparse.Namespace,
    prepared_by_id: Mapping[str, PreparedJudgeRequest],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(judgment_path(args)):
        comparison_id = str(record.get("comparison_id") or "")
        prepared = prepared_by_id.get(comparison_id)
        if prepared is None or comparison_id in result:
            raise BatchJudgeError("unexpected or duplicate stored judgment")
        if record.get("request_sha256") != prepared.request_sha256:
            raise BatchJudgeError("stored judgment request hash mismatch")
        if record.get("judge_model_id") != args.model:
            raise BatchJudgeError("stored judgment model mismatch")
        result[comparison_id] = record
    return result


def batch_input_path(args: argparse.Namespace, attempt: int) -> Path:
    name = "batch_input.jsonl" if attempt == 0 else f"batch_input_retry_{attempt}.jsonl"
    return args.output_dir / name


def raw_output_path(args: argparse.Namespace, attempt: int) -> Path:
    name = (
        "provider_output.jsonl"
        if attempt == 0
        else f"provider_output_retry_{attempt}.jsonl"
    )
    return args.output_dir / name


def build_batch_input(
    args: argparse.Namespace,
    prepared: list[PreparedJudgeRequest],
    pending_ids: list[str],
    attempt: int,
    *,
    max_output_tokens: int | None = None,
) -> Path:
    by_id = {item.comparison_id: item for item in prepared}
    attempt_max_output_tokens = (
        args.max_output_tokens
        if max_output_tokens is None
        else max_output_tokens
    )
    rows = []
    for comparison_id in pending_ids:
        item = by_id[comparison_id]
        if args.provider == "gemini":
            rows.append(
                build_gemini_batch_line(
                    item,
                    max_output_tokens=attempt_max_output_tokens,
                    seed=args.seed,
                    thinking_level=args.thinking_level,
                )
            )
        else:
            rows.append(
                build_openai_batch_line(
                    item,
                    model=args.model,
                    max_output_tokens=attempt_max_output_tokens,
                    reasoning_effort=args.reasoning_effort,
                )
            )
    path = batch_input_path(args, attempt)
    atomic_jsonl(path, rows)
    return path


def new_manifest(
    args: argparse.Namespace,
    prepared: list[PreparedJudgeRequest],
    fingerprint: str,
) -> dict[str, Any]:
    calibration = read_jsonl(args.calibration_judgments)
    projection = empirical_cost_projection(
        calibration,
        request_count=len(prepared),
        input_usd_per_million=args.input_usd_per_million,
        output_usd_per_million=args.output_usd_per_million,
        safety_multiplier=args.budget_safety_multiplier,
    )
    if projection["projected_cost_usd"] > args.stage_cap_usd:
        raise RuntimeError("empirical batch projection exceeds stage cap")
    if projection["projected_cost_usd"] > args.remaining_budget_usd:
        raise RuntimeError("empirical batch projection exceeds remaining budget")
    return {
        "record_type": "judge_full_batch_manifest",
        "status": "prepared",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "experiment_id": "20260727_170150",
        "plan_id": "plan05",
        "pipeline_stage": "benchmark_evaluation_judge_full_batch",
        "run_id": args.output_dir.name,
        "execution_mode": "asynchronous_batch",
        "provider": args.provider,
        "project": args.project if args.provider == "gemini" else None,
        "location": args.location if args.provider == "gemini" else "direct_api",
        "model": args.model,
        "judge_output_contract_version": args.judge_contract,
        "learning_evidence_policy": "excluded_gold_answer_only",
        "configuration": {
            "seed": args.seed,
            "thinking_level": args.thinking_level if args.provider == "gemini" else None,
            "reasoning_effort": args.reasoning_effort if args.provider == "openai" else None,
            "max_output_tokens": args.max_output_tokens,
            "structured_output": True,
            "store": False if args.provider == "openai" else None,
        },
        "configuration_sha256": fingerprint,
        "input_sha256": {portable(path): file_hash(path) for path in input_paths(args)},
        "system_prompt": {
            "path": portable(args.system_prompt),
            "version": prepared[0].system_prompt_version,
            "sha256": prepared[0].system_prompt_sha256,
        },
        "evaluation_schema_sha256": file_hash(args.evaluation_schema),
        "comparison_ids": [item.comparison_id for item in prepared],
        "candidate_ids": sorted({item.benchmark_candidate_id for item in prepared}),
        "target_run_ids": sorted({item.target_run_id for item in prepared}),
        "progress": {
            "expected": len(prepared),
            "completed": 0,
            "failed": 0,
        },
        "failed_comparison_ids": [],
        "active_attempt": None,
        "job_history": [],
        "max_batch_retries": args.max_batch_retries,
        "budget": {
            "pricing_mode": "batch_discounted",
            "input_usd_per_million": args.input_usd_per_million,
            "output_usd_per_million": args.output_usd_per_million,
            "stage_cap_usd": args.stage_cap_usd,
            "remaining_budget_usd_at_prepare": args.remaining_budget_usd,
            "projection": projection,
            "actual_run_cost_usd": 0.0,
        },
        "methodological_limitations": [
            "Judge outputs are model judgments, not expert ground truth.",
            "Subject-matter accuracy is anchored only to gold_answer.",
        ],
    }


def load_or_prepare(
    args: argparse.Namespace,
) -> tuple[list[PreparedJudgeRequest], dict[str, Any]]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prepared = prepare_requests(args)
    fingerprint = config_fingerprint(args, prepared)
    path = manifest_path(args)
    if path.exists():
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("configuration_sha256") != fingerprint:
            raise RuntimeError(
                "existing batch manifest configuration does not match inputs"
            )
    else:
        manifest = new_manifest(args, prepared, fingerprint)
        atomic_json(path, manifest)
    prepared_by_id = {item.comparison_id: item for item in prepared}
    completed = load_existing_records(args, prepared_by_id)
    if not manifest["job_history"] and not batch_input_path(args, 0).exists():
        build_batch_input(
            args,
            prepared,
            [item.comparison_id for item in prepared],
            0,
        )
    manifest["progress"]["completed"] = len(completed)
    manifest["progress"]["failed"] = len(manifest.get("failed_comparison_ids", []))
    manifest["updated_at"] = utc_now()
    atomic_json(path, manifest)
    return prepared, manifest


def _openai_client(args: argparse.Namespace) -> OpenAI:
    from dotenv import load_dotenv

    load_dotenv(args.api_key_env_file, override=False)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            f"OPENAI_API_KEY is missing from environment and {args.api_key_env_file}"
        )
    return OpenAI(api_key=api_key, max_retries=0, timeout=180.0)


def _gemini_client(args: argparse.Namespace) -> genai.Client:
    credentials, _ = google.auth.default(quota_project_id=args.project)
    return genai.Client(
        vertexai=True,
        project=args.project,
        location=args.location,
        credentials=credentials,
        http_options=types.HttpOptions(api_version="v1", timeout=180_000),
    )


def run_gcloud(args: argparse.Namespace, *command: str) -> str:
    process = subprocess.run(
        [str(args.gcloud_bin), *command],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(
            "gcloud failed\n"
            f"command: {' '.join(command)}\n"
            f"stdout: {process.stdout}\n"
            f"stderr: {process.stderr}"
        )
    return process.stdout


def active_job(manifest: Mapping[str, Any]) -> dict[str, Any]:
    attempt = manifest.get("active_attempt")
    if not isinstance(attempt, int):
        raise RuntimeError("batch manifest has no active attempt")
    for job in manifest["job_history"]:
        if job.get("attempt") == attempt:
            return job
    raise RuntimeError("active batch attempt is missing from job history")


def submit_attempt(
    args: argparse.Namespace,
    prepared: list[PreparedJudgeRequest],
    manifest: dict[str, Any],
    *,
    retry: bool,
) -> None:
    if manifest.get("active_attempt") is not None:
        job = active_job(manifest)
        if not job.get("collected_at"):
            print(
                json.dumps(
                    {
                        "status": "already_submitted",
                        "provider": args.provider,
                        "job": job.get("provider_job_name"),
                        "state": job.get("state"),
                    },
                    indent=2,
                )
            )
            return
    if retry:
        pending_ids = list(manifest.get("failed_comparison_ids") or [])
        if not pending_ids:
            print(json.dumps({"status": "nothing_to_retry"}, indent=2))
            return
        attempt = max((int(job["attempt"]) for job in manifest["job_history"]), default=0) + 1
        if attempt > args.max_batch_retries:
            raise RuntimeError("maximum batch retry count reached")
    else:
        if manifest["job_history"]:
            raise RuntimeError("initial batch was already submitted")
        attempt = 0
        pending_ids = [item.comparison_id for item in prepared]

    existing = load_existing_records(
        args, {item.comparison_id: item for item in prepared}
    )
    pending_ids = [item for item in pending_ids if item not in existing]
    if not pending_ids:
        raise RuntimeError("no unresolved comparison remains to submit")
    projection = empirical_cost_projection(
        read_jsonl(args.calibration_judgments),
        request_count=len(pending_ids),
        input_usd_per_million=args.input_usd_per_million,
        output_usd_per_million=args.output_usd_per_million,
        safety_multiplier=args.budget_safety_multiplier,
    )
    current_cost = float(manifest["budget"].get("actual_run_cost_usd", 0) or 0)
    projected_total = current_cost + projection["projected_cost_usd"]
    if projected_total > args.stage_cap_usd:
        raise RuntimeError("batch attempt would exceed stage cap")
    if projected_total > args.remaining_budget_usd:
        raise RuntimeError("batch attempt would exceed remaining budget")

    attempt_max_output_tokens = (
        args.retry_max_output_tokens
        if retry and args.retry_max_output_tokens is not None
        else args.max_output_tokens
    )
    input_path = build_batch_input(
        args,
        prepared,
        pending_ids,
        attempt,
        max_output_tokens=attempt_max_output_tokens,
    )
    submitted_at = utc_now()
    if args.provider == "openai":
        client = _openai_client(args)
        try:
            with input_path.open("rb") as handle:
                uploaded = client.files.create(file=handle, purpose="batch")
            batch = client.batches.create(
                input_file_id=uploaded.id,
                endpoint="/v1/responses",
                completion_window="24h",
                metadata={
                    "experiment": "20260727_170150",
                    "plan": "plan05",
                    "contract": "gold-answer-only-v4",
                    "attempt": str(attempt),
                },
            )
        finally:
            client.close()
        job = {
            "attempt": attempt,
            "submitted_at": submitted_at,
            "request_count": len(pending_ids),
            "request_ids": pending_ids,
            "local_input": portable(input_path),
            "input_sha256": file_hash(input_path),
            "provider_input_file_id": uploaded.id,
            "provider_job_name": batch.id,
            "state": str(batch.status),
            "projection": projection,
            "max_output_tokens": attempt_max_output_tokens,
            "collected_at": None,
        }
    else:
        prefix = args.gcs_uri_prefix.rstrip("/")
        input_uri = f"{prefix}/input/attempt_{attempt}.jsonl"
        output_uri = f"{prefix}/output/attempt_{attempt}"
        run_gcloud(
            args,
            "storage",
            "cp",
            str(input_path),
            input_uri,
            "--project",
            args.project,
        )
        client = _gemini_client(args)
        try:
            batch = client.batches.create(
                model=args.model,
                src=input_uri,
                config=types.CreateBatchJobConfig(
                    display_name=(
                        f"edu-benchmark-plan05-judge-{args.output_dir.name}-"
                        f"a{attempt}"
                    )[:128],
                    dest=output_uri,
                ),
            )
        finally:
            client.close()
        job = {
            "attempt": attempt,
            "submitted_at": submitted_at,
            "request_count": len(pending_ids),
            "request_ids": pending_ids,
            "local_input": portable(input_path),
            "input_sha256": file_hash(input_path),
            "provider_input_uri": input_uri,
            "provider_output_uri_prefix": output_uri,
            "provider_job_name": str(batch.name),
            "state": str(getattr(batch.state, "value", batch.state)),
            "projection": projection,
            "max_output_tokens": attempt_max_output_tokens,
            "collected_at": None,
        }
    manifest["max_batch_retries"] = max(
        int(manifest.get("max_batch_retries", 0) or 0),
        args.max_batch_retries,
    )
    manifest["active_attempt"] = attempt
    manifest["job_history"].append(job)
    manifest["status"] = "submitted"
    manifest["updated_at"] = utc_now()
    atomic_json(manifest_path(args), manifest)
    print(json.dumps(job, ensure_ascii=False, indent=2))


def refresh_status(
    args: argparse.Namespace, manifest: dict[str, Any]
) -> tuple[dict[str, Any], bool, bool]:
    job = active_job(manifest)
    if args.provider == "openai":
        client = _openai_client(args)
        try:
            batch = client.batches.retrieve(job["provider_job_name"])
        finally:
            client.close()
        state = str(batch.status)
        job["provider_output_file_id"] = batch.output_file_id
        job["provider_error_file_id"] = batch.error_file_id
        job["provider_request_counts"] = (
            batch.request_counts.model_dump(mode="json", exclude_none=True)
            if batch.request_counts is not None
            else {}
        )
        terminal = state in TERMINAL_OPENAI_STATES
        succeeded = state == "completed"
    else:
        client = _gemini_client(args)
        try:
            batch = client.batches.get(name=job["provider_job_name"])
        finally:
            client.close()
        state = str(getattr(batch.state, "value", batch.state))
        output_info = batch.output_info
        job["provider_output_directory"] = (
            str(output_info.gcs_output_directory or "")
            if output_info is not None
            else ""
        )
        job["provider_completion_stats"] = (
            batch.completion_stats.model_dump(
                mode="json", by_alias=False, exclude_none=True
            )
            if batch.completion_stats is not None
            else {}
        )
        job["provider_error"] = (
            batch.error.model_dump(mode="json", exclude_none=True)
            if batch.error is not None
            else None
        )
        terminal = state in TERMINAL_GEMINI_STATES
        succeeded = state == "JOB_STATE_SUCCEEDED"
    job["state"] = state
    job["last_checked_at"] = utc_now()
    manifest["updated_at"] = utc_now()
    manifest["status"] = (
        "batch_succeeded"
        if succeeded
        else "batch_terminal_failed"
        if terminal
        else "running"
    )
    atomic_json(manifest_path(args), manifest)
    print(
        json.dumps(
            {
                "provider": args.provider,
                "job": job["provider_job_name"],
                "state": state,
                "terminal": terminal,
                "succeeded": succeeded,
                "request_counts": job.get("provider_request_counts")
                or job.get("provider_completion_stats"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return job, terminal, succeeded


def download_openai_output(
    args: argparse.Namespace, job: Mapping[str, Any]
) -> list[dict[str, Any]]:
    file_ids = [
        job.get("provider_output_file_id"),
        job.get("provider_error_file_id"),
    ]
    client = _openai_client(args)
    payloads: list[bytes] = []
    try:
        for file_id in file_ids:
            if file_id:
                payloads.append(client.files.content(str(file_id)).read())
    finally:
        client.close()
    rows = []
    for payload in payloads:
        for line in payload.decode("utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    atomic_jsonl(raw_output_path(args, int(job["attempt"])), rows)
    return rows


def download_gemini_output(
    args: argparse.Namespace, job: Mapping[str, Any]
) -> list[dict[str, Any]]:
    output_directory = str(job.get("provider_output_directory") or "").strip()
    if not output_directory:
        raise RuntimeError("Gemini batch job has no GCS output directory")
    listing = run_gcloud(
        args,
        "storage",
        "ls",
        "--recursive",
        f"{output_directory.rstrip('/')}/**",
    )
    uris = sorted(
        line.strip()
        for line in listing.splitlines()
        if line.strip().endswith(".jsonl")
    )
    if not uris:
        raise RuntimeError("Gemini batch output contains no JSONL files")
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="edu-benchmark-batch-") as temp:
        temp_dir = Path(temp)
        for index, uri in enumerate(uris):
            local = temp_dir / f"{index:04d}.jsonl"
            run_gcloud(args, "storage", "cp", uri, str(local))
            rows.extend(read_jsonl(local))
    atomic_jsonl(raw_output_path(args, int(job["attempt"])), rows)
    return rows


def collect(
    args: argparse.Namespace,
    prepared: list[PreparedJudgeRequest],
    manifest: dict[str, Any],
) -> bool:
    job, terminal, succeeded = refresh_status(args, manifest)
    if not terminal:
        raise RuntimeError("batch is still running; use status or watch")
    if not succeeded:
        raise RuntimeError(
            f"provider batch terminated unsuccessfully: {job['state']}"
        )
    raw_rows = (
        download_openai_output(args, job)
        if args.provider == "openai"
        else download_gemini_output(args, job)
    )
    prepared_by_id = {item.comparison_id: item for item in prepared}
    existing = load_existing_records(args, prepared_by_id)
    expected_ids = set(job["request_ids"])
    seen_ids: set[str] = set()
    failed_ids: set[str] = set()
    for raw in raw_rows:
        comparison_hint = str(
            raw.get("custom_id") or raw.get("id") or raw.get("key") or ""
        )
        try:
            comparison_id, provider_result = (
                parse_openai_batch_output(raw)
                if args.provider == "openai"
                else parse_gemini_batch_output(raw)
            )
            if comparison_id not in expected_ids:
                raise BatchJudgeError("unexpected comparison ID in provider output")
            if comparison_id in seen_ids:
                raise BatchJudgeError("duplicate comparison ID in provider output")
            seen_ids.add(comparison_id)
            record = build_judgment_record(
                prepared=prepared_by_id[comparison_id],
                provider_result=provider_result,
                provider=args.provider,
                judge_model=args.model,
                run_id=args.output_dir.name,
                evaluation_schema_sha256=file_hash(args.evaluation_schema),
                batch_attempt=int(job["attempt"]),
                provider_job_name=str(job["provider_job_name"]),
            )
            existing[comparison_id] = record
        except Exception as exc:
            if comparison_hint:
                failed_ids.add(comparison_hint)
            append_jsonl(
                error_path(args),
                {
                    "record_type": "judge_batch_item_error",
                    "occurred_at": utc_now(),
                    "provider": args.provider,
                    "model": args.model,
                    "provider_job_name": job["provider_job_name"],
                    "batch_attempt": job["attempt"],
                    "comparison_id": comparison_hint,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "traceback": "".join(
                        traceback.format_exception(
                            type(exc), exc, exc.__traceback__
                        )
                    ),
                    "provider_output": raw,
                },
            )
            print(
                f"[batch-item-error] comparison={comparison_hint or '<missing>'} "
                f"type={type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
    failed_ids.update(expected_ids - seen_ids)
    ordered_records = [
        existing[item.comparison_id]
        for item in prepared
        if item.comparison_id in existing
    ]
    atomic_jsonl(judgment_path(args), ordered_records)
    actual = actual_cost_usd(
        ordered_records,
        input_usd_per_million=args.input_usd_per_million,
        output_usd_per_million=args.output_usd_per_million,
    )
    all_ids = set(prepared_by_id)
    unresolved = sorted(all_ids - set(existing))
    failed_ids = set(unresolved)
    manifest["failed_comparison_ids"] = sorted(failed_ids)
    manifest["progress"] = {
        "expected": len(prepared),
        "completed": len(existing),
        "failed": len(failed_ids),
    }
    manifest["budget"]["actual_run_cost_usd"] = round(actual, 6)
    job["collected_at"] = utc_now()
    job["raw_output"] = portable(raw_output_path(args, int(job["attempt"])))
    job["raw_output_sha256"] = file_hash(
        raw_output_path(args, int(job["attempt"]))
    )
    manifest["active_attempt"] = None
    manifest["updated_at"] = utc_now()
    if failed_ids:
        manifest["status"] = "incomplete_retry_available"
        manifest["integrity"] = {
            "validated": False,
            "reason": "batch item failures remain",
        }
        completed = False
    else:
        manifest["integrity"] = validate_judgment_records(
            ordered_records, prepared_by_id, judge_model=args.model
        )
        manifest["status"] = "completed"
        completed = True
    atomic_json(manifest_path(args), manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "provider": args.provider,
                "completed": len(existing),
                "failed": len(failed_ids),
                "actual_run_cost_usd": round(actual, 6),
                "output": portable(judgment_path(args)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return completed


def main() -> None:
    args = parse_args()
    validate_args(args)
    prepared, manifest = load_or_prepare(args)
    if args.action == "prepare":
        print(
            json.dumps(
                {
                    "status": manifest["status"],
                    "provider": args.provider,
                    "comparisons": len(prepared),
                    "projection": manifest["budget"]["projection"],
                    "output_dir": portable(args.output_dir),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.action in {"submit", "retry-submit"}:
        submit_attempt(
            args,
            prepared,
            manifest,
            retry=args.action == "retry-submit",
        )
        return
    if manifest.get("status") == "completed":
        print(
            json.dumps(
                {
                    "status": "completed",
                    "provider": args.provider,
                    "completed": manifest["progress"]["completed"],
                    "output": portable(judgment_path(args)),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if manifest.get("active_attempt") is None:
        print(
            json.dumps(
                {
                    "status": manifest.get("status"),
                    "provider": args.provider,
                    "completed": manifest["progress"]["completed"],
                    "failed": manifest["progress"]["failed"],
                    "message": "no active provider batch",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(
            2
            if manifest.get("status") == "incomplete_retry_available"
            else 0
        )
    if args.action == "status":
        refresh_status(args, manifest)
        return
    if args.action == "collect":
        if not collect(args, prepared, manifest):
            raise SystemExit(2)
        return
    if args.action == "watch":
        while True:
            _, terminal, _ = refresh_status(args, manifest)
            if terminal:
                break
            time.sleep(args.poll_seconds)
        if not collect(args, prepared, manifest):
            raise SystemExit(2)
        return
    raise AssertionError(args.action)


if __name__ == "__main__":
    main()

"""CLI for preparing, running, and finalizing the Vertex requirement pilot."""

from __future__ import annotations

import copy
import importlib.metadata
import json
import os
import random
import re
import sys
import time
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Mapping, Sequence


from .core import (
    GenerationConfig,
    RequirementScoringError,
    atomic_write_json,
    atomic_write_text,
    build_grounding_payload,
    build_calibration_summary,
    build_pilot_summary,
    build_request_hash,
    canonical_json_hash,
    compare_runs,
    derive_principle_sets,
    load_grounding_pool,
    load_calibration_cases,
    load_pilot_input,
    load_run_records,
    parse_and_validate_response,
    serialize_user_prompt,
    select_pilot,
    sha256_file,
    utc_now,
    validate_run_records,
    validate_snapshot_manifest,
    validate_specification_manifest,
    write_pilot_input,
    write_review_queue,
)
from .provider import (
    RequirementResponseClient,
    build_vertex_requirement_client,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EXPERIMENT = REPOSITORY_ROOT / "experiments/20260727_170150"
DEFAULT_POOL = (
    DEFAULT_EXPERIMENT
    / "inherited_resources/from_20260722_000940/benchmark_specification/"
    "candidate_grounding/candidate_principle_grounding_pool.csv"
)
DEFAULT_OUTPUT_ROOT = (
    DEFAULT_EXPERIMENT / "outputs/principle_requirement_scoring"
)
DEFAULT_PROMPT = (
    REPOSITORY_ROOT
    / "shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md"
)
DEFAULT_SCHEMA = DEFAULT_OUTPUT_ROOT / "scoring_schema_v2.json"
DEFAULT_SPEC_MANIFEST = DEFAULT_OUTPUT_ROOT / "specification_manifest_v4.json"
DEFAULT_CALIBRATION_INPUT = DEFAULT_OUTPUT_ROOT / "calibration_cases_v1.csv"
DEFAULT_SNAPSHOT_MANIFEST = (
    DEFAULT_EXPERIMENT / "inherited_resources/snapshot_manifest.csv"
)
DEFAULT_PROJECT = "edu-benchmark"
DEFAULT_LOCATION = "global"

FULL_SINGLE_RUN_LIMITATIONS: tuple[dict[str, str], ...] = (
    {
        "limitation_id": "single_run_no_repeatability_estimate",
        "statement_vi": (
            "Full output chỉ có một run nên không thể tính agreement A/B "
            "hoặc độ lặp lại trên chính 2.028 candidate."
        ),
    },
    {
        "limitation_id": "no_expert_accuracy",
        "statement_vi": (
            "Chưa có nhãn chuyên gia cấp candidate nên không được diễn giải "
            "score như accuracy hoặc ground truth."
        ),
    },
    {
        "limitation_id": "provisional_model_scores",
        "statement_vi": (
            "Requirement score là đề xuất của model, còn chờ UET phân tích "
            "và HNMU xác nhận trong gói benchmark tích hợp."
        ),
    },
)


class _ProgressBar:
    """Dependency-free terminal progress for one request sweep."""

    def __init__(
        self,
        *,
        label: str,
        total: int,
        overall_total: int,
        request_ceiling: int,
        enabled: bool,
        stream: Any = None,
        width: int = 24,
    ) -> None:
        self.label = label
        self.total = total
        self.overall_total = overall_total
        self.request_ceiling = request_ceiling
        self.enabled = enabled
        self.stream = stream or sys.stderr
        self.width = width
        self.dynamic = bool(
            getattr(self.stream, "isatty", lambda: False)()
        )
        self._last_non_tty_processed = -1

    def _line(
        self,
        *,
        processed: int,
        completed: int,
        failed: int,
        requests: int,
    ) -> str:
        fraction = processed / self.total if self.total else 1.0
        filled = min(self.width, int(self.width * fraction))
        bar = "#" * filled + "-" * (self.width - filled)
        return (
            f"{self.label} [{bar}] {processed}/{self.total}"
            f" | completed {completed}/{self.overall_total}"
            f" | failed {failed}"
            f" | requests {requests}/{self.request_ceiling}"
        )

    def update(
        self,
        *,
        processed: int,
        completed: int,
        failed: int,
        requests: int,
    ) -> None:
        if not self.enabled:
            return
        line = self._line(
            processed=processed,
            completed=completed,
            failed=failed,
            requests=requests,
        )
        if self.dynamic:
            self.stream.write(f"\r{line}\033[K")
            self.stream.flush()
            return
        should_print = (
            processed == 0
            or processed == self.total
            or processed - self._last_non_tty_processed >= 5
        )
        if should_print:
            self.stream.write(line + "\n")
            self.stream.flush()
            self._last_non_tty_processed = processed

    def finish(
        self,
        *,
        processed: int,
        completed: int,
        failed: int,
        requests: int,
    ) -> None:
        if not self.enabled:
            return
        if self.dynamic:
            self.update(
                processed=processed,
                completed=completed,
                failed=failed,
                requests=requests,
            )
            self.stream.write("\n")
            self.stream.flush()
        elif self._last_non_tty_processed != processed:
            self.update(
                processed=processed,
                completed=completed,
                failed=failed,
                requests=requests,
            )


def _load_schema(path: Path) -> dict[str, Any]:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    response_schema = bundle.get("$defs", {}).get("scoring_response")
    if not isinstance(response_schema, dict):
        raise RequirementScoringError(
            "Scoring schema does not define $defs.scoring_response"
        )
    principle_score = bundle.get("$defs", {}).get("principle_score")
    if not isinstance(principle_score, dict):
        raise RequirementScoringError(
            "Scoring schema does not define $defs.principle_score"
        )
    resolved = copy.deepcopy(response_schema)
    resolved["properties"]["principle_scores"]["items"] = copy.deepcopy(
        principle_score
    )
    return resolved


def _config_from_args(args: Any) -> GenerationConfig:
    thinking_level = getattr(args, "thinking_level", None)
    thinking_budget = getattr(args, "thinking_budget", None)
    if (
        args.model.strip().lower().startswith("gemini-3")
        and thinking_level is None
        and thinking_budget is None
    ):
        thinking_level = "MEDIUM"
    return GenerationConfig(
        model=args.model,
        temperature=args.temperature,
        top_p=args.top_p,
        max_output_tokens=args.max_output_tokens,
        seed=args.seed,
        thinking_budget=thinking_budget,
        thinking_level=thinking_level,
        include_thoughts=getattr(args, "include_thoughts", False),
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        max_requests=args.max_requests,
        concurrency=args.concurrency,
        retry_base_delay_seconds=args.retry_base_delay_seconds,
    )


def _is_calibration(args: Any) -> bool:
    return getattr(args, "command", "pilot") == "calibration"


def _is_full(args: Any) -> bool:
    return getattr(args, "command", "pilot") in {
        "full",
        "retry-failed",
        "refresh-full-manifest",
    }


def _pilot_directory(args: Any) -> Path:
    bundle_name = getattr(args, "bundle_name", None)
    if bundle_name:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", bundle_name):
            raise RequirementScoringError(
                "--bundle-name must contain only letters, numbers, '.', '_' or '-'"
            )
        return args.output_root / bundle_name
    if _is_calibration(args):
        return args.output_root / "calibration_gemini35_medium_v1"
    if _is_full(args):
        return args.output_root / "full_gemini35_medium_v1"
    return args.output_root / "pilot_v4"


def _load_scoring_rows(args: Any) -> list[dict[str, Any]]:
    if _is_calibration(args):
        return load_calibration_cases(args.calibration_input)
    if _is_full(args):
        return load_grounding_pool(args.pool)
    return load_pilot_input(_pilot_directory(args) / "pilot_input.csv")


def _manifest_path(path: Path) -> str:
    """Use repository-relative paths when possible."""

    try:
        return str(path.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(path)


def _planned_manifest(
    *,
    args: Any,
    pilot_rows: Sequence[Mapping[str, Any]],
    generation_config: GenerationConfig,
) -> dict[str, Any]:
    model_policy = generation_config.model_policy()
    execution_policy = generation_config.execution_policy()
    ordered_ids = [row["benchmark_candidate_id"] for row in pilot_rows]
    prompt_hash = sha256_file(args.prompt)
    schema_hash = sha256_file(args.schema)
    code_paths = (
        REPOSITORY_ROOT / "src/edu_benchmark/requirement_scoring/core.py",
        REPOSITORY_ROOT / "src/edu_benchmark/requirement_scoring/provider.py",
        REPOSITORY_ROOT / "src/edu_benchmark/requirement_scoring/workflow.py",
        REPOSITORY_ROOT
        / "src/edu_benchmark/model_providers/vertex_ai/provider.py",
        REPOSITORY_ROOT
        / "scripts/requirement_scoring/run_requirement_scoring.py",
    )
    if _is_full(args):
        input_manifest = {
            "input_role": "full_grounding_pool",
            "scoring_input_path": _manifest_path(args.pool),
            "scoring_input_sha256": sha256_file(args.pool),
        }
        run_ids = ("full",)
        bundle_type = "full_single_run_requirement_scoring"
    else:
        input_path = (
            args.calibration_input
            if _is_calibration(args)
            else _pilot_directory(args) / "pilot_input.csv"
        )
        input_manifest = {
            "input_role": (
                "semantic_boundary_calibration"
                if _is_calibration(args)
                else "stratified_repeatability_pilot"
            ),
            "pilot_input_path": _manifest_path(input_path),
            "pilot_input_sha256": None,
        }
        run_ids = ("a", "b")
        bundle_type = (
            "semantic_boundary_calibration"
            if _is_calibration(args)
            else "stratified_repeatability_pilot"
        )
    return {
        "experiment_id": "20260727_170150",
        "bundle_version": _pilot_directory(args).name,
        **(
            {}
            if _is_full(args)
            else {"pilot_version": _pilot_directory(args).name}
        ),
        "bundle_type": bundle_type,
        "status": "prepared",
        "prompt_language": "vi",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "input": {
            "grounding_pool_path": _manifest_path(args.pool),
            "grounding_pool_sha256": sha256_file(args.pool),
            "ordered_candidate_ids_sha256": canonical_json_hash(ordered_ids),
            "candidate_count": len(pilot_rows),
            "family_count": len({row["sample_id"] for row in pilot_rows}),
            "grade_counts": {
                str(grade): sum(row["grade"] == grade for row in pilot_rows)
                for grade in (6, 7, 8, 9)
            },
            **input_manifest,
        },
        "specification": {
            "manifest_path": _manifest_path(args.spec_manifest),
            "manifest_sha256": sha256_file(args.spec_manifest),
            "prompt_path": _manifest_path(args.prompt),
            "prompt_sha256": prompt_hash,
            "schema_path": _manifest_path(args.schema),
            "schema_sha256": schema_hash,
        },
        "generation_config": generation_config.as_dict(),
        "generation_config_sha256": canonical_json_hash(generation_config.as_dict()),
        "provider": {
            "name": "Vertex AI",
            "mode": "standard_adc",
            "api_version": "v1",
            "project": args.project,
            "location": args.location,
            "model": model_policy.model,
            "sdk_package": "google-genai",
            "sdk_version": importlib.metadata.version("google-genai"),
            "response_mime_type": "application/json",
        },
        "code": {
            "git_commit": None,
            "git_commit_note": (
                "Project lead will commit manually after plans and roadmap are final"
            ),
            "files": [
                {
                    "path": str(path.relative_to(REPOSITORY_ROOT)),
                    "sha256": sha256_file(path),
                }
                for path in code_paths
            ],
        },
        "runtime": {
            "concurrency": execution_policy.concurrency,
            "retry_strategy": "retry_failed_candidates_after_each_full_sweep",
            "retry_count": execution_policy.max_retries,
            "retry_base_delay_seconds": (
                execution_policy.retry_base_delay_seconds
            ),
            "timeout_seconds": model_policy.timeout_seconds,
            "monetary_budget_usd": None,
            "cost_guard": "request_ceiling",
        },
        "request_ceiling": execution_policy.max_requests,
        "api_request_attempt_count": 0,
        "runs": {
            run_id: {
                "status": "pending",
                "completed_count": 0,
                "attempts_by_candidate": {},
                "failed_candidate_ids": [],
            }
            for run_id in run_ids
        },
        "metrics": None,
        "review_queue_count": None,
        "errors": [],
    }


def prepare(args: Any) -> dict[str, Any]:
    validate_snapshot_manifest(args.snapshot_manifest)
    validate_specification_manifest(args.spec_manifest, REPOSITORY_ROOT)
    rows = load_grounding_pool(args.pool)
    if _is_calibration(args):
        pilot_rows = load_calibration_cases(args.calibration_input)
    elif _is_full(args):
        pilot_rows = rows
    else:
        pilot_rows = select_pilot(rows, per_grade=10, seed=args.selection_seed)
    pilot_dir = _pilot_directory(args)
    pilot_input = pilot_dir / "pilot_input.csv"
    manifest_path = pilot_dir / "run_manifest.json"
    generation_config = _config_from_args(args)
    execution_policy = generation_config.execution_policy()
    run_count = 1 if _is_full(args) else 2
    minimum_requests = len(pilot_rows) * run_count
    if execution_policy.max_requests < minimum_requests:
        raise RequirementScoringError(
            f"max_requests must be at least {minimum_requests} for "
            f"{run_count} complete run(s)"
        )
    if execution_policy.concurrency < 1:
        raise RequirementScoringError("concurrency must be at least 1")
    if execution_policy.max_retries < 0:
        raise RequirementScoringError("max_retries must not be negative")
    if execution_policy.retry_base_delay_seconds < 0:
        raise RequirementScoringError(
            "retry_base_delay_seconds must not be negative"
        )
    planned = _planned_manifest(
        args=args,
        pilot_rows=pilot_rows,
        generation_config=generation_config,
    )
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("status") not in {
            "prepared",
            "running",
            "failed",
            "runs_completed",
        }:
            raise RequirementScoringError(
                "Active pilot already exists; refusing to overwrite it"
            )
        if (
            existing.get("generation_config_sha256")
            != planned["generation_config_sha256"]
            or existing.get("input", {}).get("ordered_candidate_ids_sha256")
            != planned["input"]["ordered_candidate_ids_sha256"]
            or existing.get("provider") != planned["provider"]
            or existing.get("specification") != planned["specification"]
        ):
            raise RequirementScoringError(
                "Existing pilot uses a different input/config; use a new pilot version"
            )
        return existing
    if _is_full(args):
        pass
    elif _is_calibration(args):
        planned["input"]["pilot_input_sha256"] = sha256_file(
            args.calibration_input
        )
    else:
        write_pilot_input(pilot_input, pilot_rows)
        planned["input"]["pilot_input_sha256"] = sha256_file(pilot_input)
    atomic_write_json(manifest_path, planned)
    return planned


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def _completed_records(path: Path, run_id: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    records = load_run_records(path)
    completed: dict[str, dict[str, Any]] = {}
    for record in records:
        if record.get("run_id") != run_id:
            raise RequirementScoringError(f"{path} contains another run_id")
        candidate_id = record.get("benchmark_candidate_id")
        if candidate_id in completed:
            raise RequirementScoringError(f"{path} contains duplicate records")
        completed[str(candidate_id)] = record
    return completed


def _generate_record(
    *,
    live_client: RequirementResponseClient,
    row: Mapping[str, Any],
    request_hash: str,
    run_id: str,
    generation_config: GenerationConfig,
) -> dict[str, Any]:
    candidate_id = str(row["benchmark_candidate_id"])
    payload = build_grounding_payload(row)
    user_prompt = serialize_user_prompt(payload)
    result = live_client.generate(user_prompt)
    normalized = parse_and_validate_response(
        result["raw_response_text"],
        expected_candidate_id=candidate_id,
    )
    required, alternative = derive_principle_sets(normalized)
    return {
        "run_id": run_id,
        "benchmark_candidate_id": candidate_id,
        "request_hash": request_hash,
        "user_prompt": user_prompt,
        "model": generation_config.model,
        "model_version": result["model_version"],
        "response_id": result["response_id"],
        "finish_reason": result["finish_reason"],
        "usage_metadata": result["usage_metadata"],
        "raw_response_text": result["raw_response_text"],
        "normalized_response": normalized,
        "required_principle_set": required,
        "alternative_principle_set": alternative,
        "created_at": utc_now(),
    }


def _safe_failure(
    *,
    candidate_id: str,
    attempt: int,
    exc: Exception,
) -> dict[str, Any]:
    return {
        "benchmark_candidate_id": candidate_id,
        "attempt": attempt,
        "error_type": type(exc).__name__,
        "error_message": str(exc)[:1000],
    }


def execute_run(
    args: Any,
    *,
    run_id: str,
    client: RequirementResponseClient | None = None,
    additional_retry_attempts: int = 0,
) -> None:
    if not args.execute_api:
        raise RequirementScoringError(
            "Real Vertex calls require the explicit --execute-api flag"
        )
    manifest_path = _pilot_directory(args) / "run_manifest.json"
    if not manifest_path.exists():
        raise RequirementScoringError("Run prepare before calling Vertex AI")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    generation_config = _config_from_args(args)
    execution_policy = generation_config.execution_policy()
    if canonical_json_hash(generation_config.as_dict()) != manifest.get(
        "generation_config_sha256"
    ):
        raise RequirementScoringError("CLI generation config differs from run manifest")
    provider = manifest.get("provider", {})
    if (
        provider.get("mode") != "standard_adc"
        or provider.get("project") != args.project
        or provider.get("location") != args.location
    ):
        raise RequirementScoringError(
            "CLI Vertex project/location differs from run manifest"
        )
    if manifest.get("prompt_language") != "vi":
        raise RequirementScoringError("Run manifest prompt_language must be 'vi'")
    pilot_rows = _load_scoring_rows(args)
    run_path = _pilot_directory(args) / f"run_{run_id}.jsonl"
    completed = _completed_records(run_path, run_id)
    prompt_hash = sha256_file(args.prompt)
    schema_hash = sha256_file(args.schema)
    prompt = args.prompt.read_text(encoding="utf-8")
    response_schema = _load_schema(args.schema)
    owns_client = client is None
    live_client = client or build_vertex_requirement_client(
        project=args.project,
        location=args.location,
        system_prompt=prompt,
        response_schema=response_schema,
        generation_config=generation_config,
    )
    run_state = manifest["runs"][run_id]
    attempts_by_candidate = {
        str(candidate_id): int(attempts)
        for candidate_id, attempts in run_state.get(
            "attempts_by_candidate", {}
        ).items()
    }
    work_items: list[tuple[dict[str, Any], str]] = []
    for row in pilot_rows:
        candidate_id = row["benchmark_candidate_id"]
        payload = build_grounding_payload(row)
        request_hash = build_request_hash(
            payload=payload,
            prompt_sha256=prompt_hash,
            schema_sha256=schema_hash,
            generation_config=generation_config,
        )
        if candidate_id in completed:
            if completed[candidate_id].get("request_hash") != request_hash:
                raise RequirementScoringError(
                    f"{candidate_id}: existing response hash does not match"
                )
            continue
        work_items.append((row, request_hash))
    manifest["status"] = "running"
    run_state["status"] = "running"
    run_state["completed_count"] = len(completed)
    run_state["attempts_by_candidate"] = attempts_by_candidate
    run_state["failed_candidate_ids"] = [
        row["benchmark_candidate_id"] for row, _ in work_items
    ]
    run_state.setdefault("retry_sweeps_completed", 0)
    run_state.setdefault("last_failures", [])
    manifest["updated_at"] = utc_now()
    atomic_write_json(manifest_path, manifest)
    try:
        pending = list(work_items)
        if additional_retry_attempts < 0:
            raise RequirementScoringError(
                "additional_retry_attempts must not be negative"
            )
        max_attempts_per_candidate = (
            execution_policy.max_retries + 1 + additional_retry_attempts
        )
        retry_sweep = int(run_state.get("retry_sweeps_completed", 0))
        progress_enabled = bool(getattr(args, "progress", False))
        with ThreadPoolExecutor(
            max_workers=execution_policy.concurrency,
            thread_name_prefix=f"vertex-{run_id}",
        ) as executor:
            while pending:
                eligible = [
                    item
                    for item in pending
                    if attempts_by_candidate.get(
                        item[0]["benchmark_candidate_id"], 0
                    )
                    < max_attempts_per_candidate
                ]
                request_capacity = (
                    execution_policy.max_requests
                    - int(manifest["api_request_attempt_count"])
                )
                if not eligible or request_capacity <= 0:
                    break
                sweep = eligible[:request_capacity]
                scheduled_ids = {
                    row["benchmark_candidate_id"] for row, _ in sweep
                }
                unscheduled = [
                    item
                    for item in pending
                    if item[0]["benchmark_candidate_id"] not in scheduled_ids
                ]
                for row, _ in sweep:
                    candidate_id = row["benchmark_candidate_id"]
                    attempts_by_candidate[candidate_id] = (
                        attempts_by_candidate.get(candidate_id, 0) + 1
                    )
                manifest["api_request_attempt_count"] += len(sweep)
                run_state["attempts_by_candidate"] = attempts_by_candidate
                run_state["active_sweep_size"] = len(sweep)
                run_state["last_failures"] = []
                manifest["updated_at"] = utc_now()
                atomic_write_json(manifest_path, manifest)

                sweep_label = (
                    "initial" if retry_sweep == 0 else f"retry {retry_sweep}"
                )
                progress = _ProgressBar(
                    label=f"Run {run_id.upper()} | {sweep_label}",
                    total=len(sweep),
                    overall_total=len(pilot_rows),
                    request_ceiling=execution_policy.max_requests,
                    enabled=progress_enabled,
                )
                processed_in_sweep = 0
                progress.update(
                    processed=processed_in_sweep,
                    completed=len(completed),
                    failed=0,
                    requests=int(manifest["api_request_attempt_count"]),
                )
                future_to_item: dict[
                    Future[dict[str, Any]], tuple[dict[str, Any], str]
                ] = {
                    executor.submit(
                        _generate_record,
                        live_client=live_client,
                        row=row,
                        request_hash=request_hash,
                        run_id=run_id,
                        generation_config=generation_config,
                    ): (row, request_hash)
                    for row, request_hash in sweep
                }
                failed_items: list[tuple[dict[str, Any], str]] = []
                last_failures: list[dict[str, Any]] = []
                for future in as_completed(future_to_item):
                    row, request_hash = future_to_item[future]
                    candidate_id = row["benchmark_candidate_id"]
                    try:
                        record = future.result()
                    except Exception as exc:
                        failed_items.append((row, request_hash))
                        last_failures.append(
                            _safe_failure(
                                candidate_id=candidate_id,
                                attempt=attempts_by_candidate[candidate_id],
                                exc=exc,
                            )
                        )
                    else:
                        _append_jsonl(run_path, record)
                        completed[candidate_id] = record
                    processed_in_sweep += 1
                    run_state["completed_count"] = len(completed)
                    run_state["last_failures"] = sorted(
                        last_failures,
                        key=lambda item: item["benchmark_candidate_id"],
                    )
                    run_state["failed_candidate_ids"] = sorted(
                        {
                            item[0]["benchmark_candidate_id"]
                            for item in failed_items + unscheduled
                        }
                    )
                    manifest["updated_at"] = utc_now()
                    atomic_write_json(manifest_path, manifest)
                    progress.update(
                        processed=processed_in_sweep,
                        completed=len(completed),
                        failed=len(last_failures),
                        requests=int(manifest["api_request_attempt_count"]),
                    )

                progress.finish(
                    processed=processed_in_sweep,
                    completed=len(completed),
                    failed=len(last_failures),
                    requests=int(manifest["api_request_attempt_count"]),
                )
                pending = failed_items + unscheduled
                run_state["failed_candidate_ids"] = sorted(
                    item[0]["benchmark_candidate_id"] for item in pending
                )
                run_state["active_sweep_size"] = 0
                manifest["updated_at"] = utc_now()
                atomic_write_json(manifest_path, manifest)
                retryable = [
                    item
                    for item in pending
                    if attempts_by_candidate.get(
                        item[0]["benchmark_candidate_id"], 0
                    )
                    < max_attempts_per_candidate
                ]
                if (
                    not retryable
                    or manifest["api_request_attempt_count"]
                    >= execution_policy.max_requests
                ):
                    break
                retry_sweep += 1
                run_state["retry_sweeps_completed"] = retry_sweep
                jitter = random.Random(
                    f"{generation_config.seed}:{run_id}:{retry_sweep}"
                ).uniform(0.0, execution_policy.retry_base_delay_seconds)
                delay = min(
                    execution_policy.retry_base_delay_seconds
                    * (2 ** (retry_sweep - 1))
                    + jitter,
                    30.0,
                )
                run_state["next_retry_delay_seconds"] = delay
                manifest["updated_at"] = utc_now()
                atomic_write_json(manifest_path, manifest)
                time.sleep(delay)

        if pending:
            failed_ids = sorted(
                row["benchmark_candidate_id"] for row, _ in pending
            )
            run_state["failed_candidate_ids"] = failed_ids
            raise RequirementScoringError(
                f"Run {run_id} has {len(failed_ids)} failed candidates after "
                "retry sweeps or request-ceiling exhaustion"
            )
        records = load_run_records(run_path)
        validate_run_records(records, pilot_rows, run_id=run_id)
        manifest["runs"][run_id] = {
            "status": "completed",
            "completed_count": len(records),
            "attempts_by_candidate": attempts_by_candidate,
            "failed_candidate_ids": [],
            "retry_sweeps_completed": retry_sweep,
            "path": _manifest_path(run_path),
            "sha256": sha256_file(run_path),
        }
        manifest["status"] = (
            "runs_completed"
            if all(
                state["status"] == "completed"
                for state in manifest["runs"].values()
            )
            else "running"
        )
        manifest["updated_at"] = utc_now()
        atomic_write_json(manifest_path, manifest)
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["runs"][run_id]["status"] = "failed"
        manifest["runs"][run_id]["completed_count"] = len(completed)
        manifest["errors"].append(
            {
                "run_id": run_id,
                "error_type": type(exc).__name__,
                "message": (
                    str(exc)
                    if isinstance(exc, RequirementScoringError)
                    else "Unexpected runner error; details were not persisted"
                ),
                "at": utc_now(),
            }
        )
        manifest["updated_at"] = utc_now()
        atomic_write_json(manifest_path, manifest)
        raise
    finally:
        if owns_client:
            live_client.close()


def finalize(args: Any) -> dict[str, Any]:
    pilot_dir = _pilot_directory(args)
    manifest_path = pilot_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pilot_rows = _load_scoring_rows(args)
    run_a = validate_run_records(
        load_run_records(pilot_dir / "run_a.jsonl"), pilot_rows, run_id="a"
    )
    run_b = validate_run_records(
        load_run_records(pilot_dir / "run_b.jsonl"), pilot_rows, run_id="b"
    )
    metrics, review_rows = compare_runs(
        run_a,
        run_b,
        pilot_rows,
        spot_check_count=args.spot_check_count,
        seed=args.selection_seed,
    )
    review_path = pilot_dir / "review_queue.csv"
    summary_path = pilot_dir / (
        "calibration_summary.md"
        if _is_calibration(args)
        else "pilot_summary.md"
    )
    write_review_queue(review_path, review_rows)
    summary = (
        build_calibration_summary(metrics, len(review_rows))
        if _is_calibration(args)
        else build_pilot_summary(metrics, len(review_rows))
    )
    atomic_write_text(summary_path, summary)
    manifest["metrics"] = metrics
    manifest["review_queue_count"] = len(review_rows)
    manifest["review_queue_sha256"] = sha256_file(review_path)
    manifest[
        "calibration_summary_sha256"
        if _is_calibration(args)
        else "pilot_summary_sha256"
    ] = sha256_file(summary_path)
    manifest["status"] = "awaiting_uet_review"
    manifest["updated_at"] = utc_now()
    atomic_write_json(manifest_path, manifest)
    return manifest


def finalize_full(args: Any) -> dict[str, Any]:
    """Validate a full single-run bundle without doing semantic analysis."""

    bundle_dir = _pilot_directory(args)
    manifest_path = bundle_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _load_scoring_rows(args)
    run_path = bundle_dir / "run_full.jsonl"
    records = load_run_records(run_path)
    validated = validate_run_records(records, rows, run_id="full")
    failed_candidate_ids = sorted(
        str(candidate_id)
        for candidate_id in manifest.get("runs", {})
        .get("full", {})
        .get("failed_candidate_ids", [])
    )
    if failed_candidate_ids:
        raise RequirementScoringError(
            "Cannot finalize full bundle while current failed candidates remain"
        )
    model_versions = Counter(
        str(record.get("model_version", "")) for record in records
    )
    finish_reasons = Counter(
        str(record.get("finish_reason", "")) for record in records
    )
    response_ids = {
        str(record.get("response_id", ""))
        for record in records
        if str(record.get("response_id", ""))
    }
    manifest["integrity"] = {
        "validated": True,
        "record_count": len(records),
        "candidate_count": len(rows),
        "family_count": len({row["sample_id"] for row in rows}),
        "score_count": len(records) * 6,
        "distinct_response_id_count": len(response_ids),
        "model_versions": dict(sorted(model_versions.items())),
        "finish_reasons": dict(sorted(finish_reasons.items())),
        "ordered_candidate_ids_sha256": canonical_json_hash(
            [row["benchmark_candidate_id"] for row in rows]
        ),
        "run_file_sha256": sha256_file(run_path),
        "validated_record_count": len(validated),
    }
    manifest["limitations"] = [
        dict(limitation) for limitation in FULL_SINGLE_RUN_LIMITATIONS
    ]
    manifest["failure_state"] = {
        "current_failure_count": 0,
        "current_failed_candidate_ids": [],
        "current_failure_source": "runs.full.failed_candidate_ids",
        "historical_error_count": len(manifest.get("errors", [])),
        "historical_errors_retained_for_provenance": True,
    }
    manifest["status"] = "completed_awaiting_analysis"
    manifest["updated_at"] = utc_now()
    atomic_write_json(manifest_path, manifest)
    return manifest


def run_full_pilot(args: Any) -> None:
    if not args.execute_api:
        raise RequirementScoringError(
            "The pilot command requires --execute-api; no request was sent"
        )
    pilot_dir = _pilot_directory(args)
    if getattr(args, "progress", False):
        print(f"Output directory: {pilot_dir}", file=sys.stderr)
    prepare(args)
    execute_run(args, run_id="a")
    execute_run(args, run_id="b")
    finalize(args)
    if getattr(args, "progress", False):
        print(
            f"Run completed; review bundle: {pilot_dir}",
            file=sys.stderr,
        )


def run_full_dataset(args: Any) -> None:
    if not args.execute_api:
        raise RequirementScoringError(
            "The full command requires --execute-api; no request was sent"
        )
    bundle_dir = _pilot_directory(args)
    if getattr(args, "progress", False):
        print(f"Output directory: {bundle_dir}", file=sys.stderr)
    prepare(args)
    execute_run(args, run_id="full")
    finalize_full(args)
    if getattr(args, "progress", False):
        print(
            f"Full run completed; analysis input: {bundle_dir}",
            file=sys.stderr,
        )


def retry_failed_full(
    args: Any,
    *,
    client: RequirementResponseClient | None = None,
) -> None:
    """Retry only missing records from a failed full bundle."""

    if not args.execute_api:
        raise RequirementScoringError(
            "The retry-failed command requires --execute-api; no request was sent"
        )
    if args.additional_retries < 1:
        raise RequirementScoringError("--additional-retries must be at least 1")
    bundle_dir = _pilot_directory(args)
    manifest_path = bundle_dir / "run_manifest.json"
    run_path = bundle_dir / "run_full.jsonl"
    if not manifest_path.is_file() or not run_path.is_file():
        raise RequirementScoringError(
            "retry-failed requires an existing full bundle and run_full.jsonl"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("bundle_type") != "full_single_run_requirement_scoring":
        raise RequirementScoringError("retry-failed only supports a full bundle")
    failed_ids = sorted(
        str(candidate_id)
        for candidate_id in manifest.get("runs", {})
        .get("full", {})
        .get("failed_candidate_ids", [])
    )
    if not failed_ids:
        raise RequirementScoringError("The full bundle has no failed candidates")
    rows = _load_scoring_rows(args)
    completed = _completed_records(run_path, "full")
    missing_ids = sorted(
        str(row["benchmark_candidate_id"])
        for row in rows
        if str(row["benchmark_candidate_id"]) not in completed
    )
    if missing_ids != failed_ids:
        raise RequirementScoringError(
            "Manifest failed IDs do not match missing run records"
        )
    recovery = {
        "started_at": utc_now(),
        "status": "running",
        "candidate_ids": failed_ids,
        "additional_retries": args.additional_retries,
        "runner_sha256": sha256_file(Path(__file__)),
        "api_request_attempt_count_before": int(
            manifest.get("api_request_attempt_count", 0)
        ),
    }
    manifest.setdefault("recovery_runs", []).append(recovery)
    atomic_write_json(manifest_path, manifest)
    if getattr(args, "progress", False):
        print(
            f"Retrying {len(failed_ids)} failed candidates in: {bundle_dir}",
            file=sys.stderr,
        )
    try:
        execute_run(
            args,
            run_id="full",
            client=client,
            additional_retry_attempts=args.additional_retries,
        )
        completed_manifest = finalize_full(args)
    except Exception:
        failed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        failed_recovery = failed_manifest["recovery_runs"][-1]
        failed_recovery["status"] = "failed"
        failed_recovery["completed_at"] = utc_now()
        failed_recovery["api_request_attempt_count_after"] = int(
            failed_manifest.get("api_request_attempt_count", 0)
        )
        atomic_write_json(manifest_path, failed_manifest)
        raise
    completed_recovery = completed_manifest["recovery_runs"][-1]
    completed_recovery["status"] = "completed"
    completed_recovery["completed_at"] = utc_now()
    completed_recovery["api_request_attempt_count_after"] = int(
        completed_manifest.get("api_request_attempt_count", 0)
    )
    atomic_write_json(manifest_path, completed_manifest)
    if getattr(args, "progress", False):
        print(
            f"Recovery completed; validated records: "
            f"{completed_manifest['integrity']['record_count']}",
            file=sys.stderr,
        )

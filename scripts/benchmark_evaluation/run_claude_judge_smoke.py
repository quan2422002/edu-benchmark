"""Run locked blind pairwise judge smoke or pilot batches."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import traceback
from typing import Any


from tqdm import tqdm  # noqa: E402

from edu_benchmark.benchmark_evaluation.claude_judge import (  # noqa: E402
    ClaudeVertexJudgeCaller,
)
from edu_benchmark.benchmark_evaluation.gemini_judge import (  # noqa: E402
    GeminiVertexJudgeCaller,
)
from edu_benchmark.benchmark_evaluation.openai_judge import (  # noqa: E402
    OpenAIJudgeCaller,
)
from edu_benchmark.benchmark_evaluation.costing import (  # noqa: E402
    BudgetPolicy,
    TokenPricing,
)
from edu_benchmark.benchmark_evaluation.judge import (  # noqa: E402
    GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES,
    JudgeOutputError,
    PreparedJudgeRequest,
    postprocess_judge_output,
    prepare_judge_requests,
    validate_judge_output,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
EVALUATION_ROOT = EXPERIMENT / "outputs/benchmark_evaluation"
EXPERIMENT_ID = "20260727_170150"
PLAN_ID = "plan05"
STAGE = "benchmark_evaluation_judge_smoke"
DEFAULT_OUTPUT = EVALUATION_ROOT / "judge_smoke_claude_blind_v2"
SUCCESS_FINISH_REASONS = frozenset({"END_TURN", "STOP"})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def portable(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def default_target_runs() -> list[Path]:
    return [
        EVALUATION_ROOT
        / "smoke_gemini35_instruction_v2/run_smoke.jsonl",
        EVALUATION_ROOT
        / "smoke_llama4_maverick_instruction_v2_retry1/run_smoke.jsonl",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai"),
        default="claude",
    )
    parser.add_argument(
        "--run-kind",
        choices=("smoke", "pilot", "cost-pilot", "full"),
        default="smoke",
    )
    parser.add_argument(
        "--judge-contract",
        choices=("v2", "rubric-only-v3", "gold-answer-only-v4"),
        default="v2",
        help=(
            "v2 includes serious-error detection and gating; "
            "rubric-only-v3 removes serious errors from model input/output; "
            "gold-answer-only-v4 additionally removes learning-resource "
            "fragments and anchors subject accuracy only to gold_answer."
        ),
    )
    parser.add_argument("--project", default="edu-benchmark")
    parser.add_argument("--location", default="us-east5")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--target-run", type=Path, action="append", dest="target_runs"
    )
    parser.add_argument(
        "--candidate-manifest",
        type=Path,
        help="Locked candidate subset manifest for cost-pilot runs.",
    )
    parser.add_argument(
        "--system-prompt",
        type=Path,
        default=(
            ROOT
            / "shared/prompts/benchmark_response_judging/"
            "system_prompt_v2.md"
        ),
    )
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--temperature", type=float)
    parser.add_argument(
        "--thinking-level",
        choices=("minimal", "low", "medium", "high"),
        default="medium",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=("none", "low", "medium", "high", "xhigh"),
        default="medium",
    )
    parser.add_argument(
        "--api-key-env-file",
        type=Path,
        default=ROOT / "src/.env",
        help=(
            "Local dotenv file containing OPENAI_API_KEY. It is never "
            "hashed, copied, or written to run artifacts."
        ),
    )
    parser.add_argument("--max-output-tokens", type=int, default=3072)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument(
        "--retry-backoff-base-seconds", type=float, default=2.0
    )
    parser.add_argument(
        "--retry-backoff-max-seconds", type=float, default=30.0
    )
    parser.add_argument(
        "--retry-jitter-seconds", type=float, default=1.0
    )
    parser.add_argument("--input-usd-per-million", type=float, default=3.30)
    parser.add_argument(
        "--output-usd-per-million", type=float, default=16.50
    )
    parser.add_argument(
        "--upper-bound-input-tokens", type=int, default=10000
    )
    parser.add_argument(
        "--actual-spend-to-date-usd", type=float, default=56.52
    )
    parser.add_argument("--hard-budget-usd", type=float, default=250.0)
    parser.add_argument("--reserve-usd", type=float, default=25.0)
    parser.add_argument("--stage-cap-usd", type=float, default=2.0)
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
    if min(
        args.concurrency,
        args.max_output_tokens,
        args.upper_bound_input_tokens,
    ) <= 0:
        raise ValueError("concurrency/token limits must be positive")
    if args.max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    if args.provider == "openai" and args.temperature is not None:
        raise ValueError("OpenAI GPT-5.4 judge must omit temperature")
    if (
        args.retry_backoff_base_seconds < 0
        or args.retry_backoff_max_seconds < 0
        or args.retry_jitter_seconds < 0
        or args.retry_backoff_base_seconds
        > args.retry_backoff_max_seconds
    ):
        raise ValueError("invalid retry backoff configuration")
    expected_target_runs = 3 if args.run_kind in {"pilot", "cost-pilot"} else 2
    if len(args.target_runs) != expected_target_runs:
        raise ValueError(
            f"{args.run_kind} requires exactly {expected_target_runs} "
            "--target-run inputs"
        )
    if args.run_kind == "cost-pilot" and args.candidate_manifest is None:
        raise ValueError("cost-pilot requires --candidate-manifest")
    output = args.output_dir.resolve()
    evaluation_root = EVALUATION_ROOT.resolve()
    if output == evaluation_root or not output.is_relative_to(evaluation_root):
        raise ValueError(
            "output must be inside outputs/benchmark_evaluation"
        )


def load_candidate_manifest_ids(path: Path) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    ids = value.get("candidate_ids")
    if not isinstance(ids, list):
        raise ValueError("candidate manifest must contain candidate_ids")
    result = [str(item).strip() for item in ids]
    if any(not item for item in result) or len(set(result)) != len(result):
        raise ValueError("candidate manifest IDs must be non-empty and unique")
    return result


def prepare_from_args(args):
    run_kind = getattr(args, "run_kind", "smoke")
    candidate_manifest = getattr(args, "candidate_manifest", None)
    fixed_ids = (
        load_candidate_manifest_ids(candidate_manifest)
        if candidate_manifest is not None
        else None
    )
    return prepare_judge_requests(
        candidate_csv=args.candidate_csv,
        grounding_pool_csv=args.grounding_pool,
        conversion_input_csv=args.conversion_input,
        learning_fragments_csv=args.learning_fragments,
        requirement_run_jsonl=args.requirement_run,
        rubrics_csv=args.rubrics,
        serious_errors_csv=args.serious_errors,
        target_run_jsonls=args.target_runs,
        system_prompt_path=args.system_prompt,
        seed=args.seed,
        expected_candidates_per_run={
            "smoke": 10,
            "pilot": 80,
            "cost-pilot": 30,
            "full": 1400,
        }[run_kind],
        expected_target_run_count=(
            3 if run_kind in {"pilot", "cost-pilot"} else 2
        ),
        fixed_candidate_ids=fixed_ids,
        judge_output_contract_version=getattr(
            args, "judge_contract", "v2"
        ),
    )


def load_completed(path, prepared_by_id, model):
    result = {}
    for record in read_jsonl(path):
        comparison_id = str(record.get("comparison_id") or "")
        prepared = prepared_by_id.get(comparison_id)
        if prepared is None or comparison_id in result:
            raise RuntimeError("unexpected or duplicate stored comparison")
        if record.get("request_sha256") != prepared.request_sha256:
            raise RuntimeError("stored request hash mismatch")
        if record.get("judge_model_id") != model:
            raise RuntimeError("stored judge model mismatch")
        if record.get("record_status") != "completed":
            raise RuntimeError("stored record is not completed")
        result[comparison_id] = record
    return result


def error_record(
    exc,
    prepared,
    attempt,
    max_attempts,
    retry,
    args,
    provider_result=None,
):
    usage = None
    finish_reason = None
    if isinstance(provider_result, dict):
        finish_reason = provider_result.get("finish_reason")
        usage = {
            "input_tokens": int(
                provider_result.get("input_tokens", 0) or 0
            ),
            "output_tokens": int(
                provider_result.get("output_tokens", 0) or 0
            ),
            "provider_metadata": provider_result.get(
                "usage_metadata", {}
            ),
        }
    return {
        "record_type": "judge_call_error",
        "occurred_at": utc_now(),
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "pipeline_stage": STAGE,
        "run_id": args.output_dir.name,
        "comparison_id": prepared.comparison_id,
        "benchmark_candidate_id": prepared.benchmark_candidate_id,
        "provider": args.provider,
        "model": args.model,
        "location": (
            args.location if args.provider != "openai" else "direct_api"
        ),
        "attempt": attempt,
        "max_attempts": max_attempts,
        "retryable": bool(getattr(exc, "retryable", True)),
        "retry_scheduled": retry,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "http_status": getattr(exc, "http_status", None),
        "finish_reason": finish_reason,
        "usage": usage,
        "response_body": getattr(exc, "response_body", None),
        "traceback": "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
        "request_sha256": prepared.request_sha256,
    }




def _retry_delay_seconds(
    *,
    attempt: int,
    comparison_id: str,
    seed: int,
    base_seconds: float,
    max_seconds: float,
    jitter_seconds: float,
) -> float:
    """Return deterministic exponential backoff with bounded jitter."""

    exponential = min(max_seconds, base_seconds * (2 ** (attempt - 1)))
    if jitter_seconds <= 0 or exponential >= max_seconds:
        return exponential
    digest = hashlib.sha256(
        f"{seed}:{comparison_id}:{attempt}".encode("utf-8")
    ).digest()
    fraction = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return min(max_seconds, exponential + fraction * jitter_seconds)


def call_one(
    *,
    caller,
    prepared: PreparedJudgeRequest,
    args,
    error_path,
    write_lock,
):
    max_attempts = args.max_retries + 1
    last_error = None
    for attempt in range(1, max_attempts + 1):
        started = time.monotonic()
        provider = None
        try:
            provider = caller.call(prepared)
            if provider["finish_reason"] not in SUCCESS_FINISH_REASONS:
                exc = JudgeOutputError(
                    f"non-terminal finish reason {provider['finish_reason']}"
                )
                exc.retryable = False
                exc.response_body = provider["response_text"]
                raise exc
            normalized = validate_judge_output(
                provider["response_text"],
                rubric_name_to_id=dict(prepared.rubric_name_to_id),
                error_name_to_id=dict(prepared.error_name_to_id),
                error_name_to_affected_rubric_ids=dict(
                    prepared.error_name_to_affected_rubric_ids
                ),
                include_serious_errors=prepared.include_serious_errors,
                criterion_name_aliases=(
                    GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES
                    if prepared.judge_output_contract_version
                    == "gold-answer-only-v4"
                    else None
                ),
            )
            postprocessed = postprocess_judge_output(
                normalized,
                response_1_source=prepared.response_1_source,
                response_2_source=prepared.response_2_source,
            )
            return {
                "record_type": "blind_pairwise_judgment",
                "record_status": "completed",
                "created_at": utc_now(),
                "experiment_id": EXPERIMENT_ID,
                "plan_id": PLAN_ID,
                "pipeline_stage": STAGE,
                "run_id": args.output_dir.name,
                "comparison_id": prepared.comparison_id,
                "benchmark_candidate_id": prepared.benchmark_candidate_id,
                "target_run_id": prepared.target_run_id,
                "target_response_id": prepared.target_response_id,
                "target_model_id": prepared.target_model_id,
                "judge_model_id": args.model,
                "judge_model_version": provider["model_version"],
                "judge_response_id": provider["response_id"],
                "attempt": attempt,
                "latency_seconds": round(time.monotonic() - started, 3),
                "finish_reason": provider["finish_reason"],
                **prepared.trace_fields(),
                "evaluation_schema_sha256": file_hash(
                    args.evaluation_schema
                ),
                "judge_output_contract_version": (
                    prepared.judge_output_contract_version
                ),
                "raw_judge_response": provider["response_text"],
                "blind_judgment": normalized,
                "raw_criterion_judgments": postprocessed[
                    "raw_criterion_judgments"
                ],
                "serious_error_findings": postprocessed[
                    "serious_error_findings"
                ],
                "adjusted_criterion_judgments": postprocessed[
                    "adjusted_criterion_judgments"
                ],
                "criterion_adjustments": postprocessed[
                    "criterion_adjustments"
                ],
                "overall_judgment": postprocessed["overall_judgment"],
                "usage": {
                    "input_tokens": provider["input_tokens"],
                    "output_tokens": provider["output_tokens"],
                    "provider_metadata": provider["usage_metadata"],
                },
            }
        except Exception as exc:
            last_error = exc
            if (
                isinstance(provider, dict)
                and getattr(exc, "response_body", None) is None
            ):
                exc.response_body = provider.get("response_text")
            retry = (
                bool(getattr(exc, "retryable", True))
                and attempt < max_attempts
            )
            diagnostic = error_record(
                exc,
                prepared,
                attempt,
                max_attempts,
                retry,
                args,
                provider,
            )
            with write_lock:
                append_jsonl(error_path, diagnostic)
                tqdm.write(
                    "[judge-error] Full diagnostic follows:\n"
                    + json.dumps(
                        diagnostic, ensure_ascii=False, indent=2
                    )
                )
            if not retry:
                break
            delay = _retry_delay_seconds(
                attempt=attempt,
                comparison_id=prepared.comparison_id,
                seed=args.seed,
                base_seconds=args.retry_backoff_base_seconds,
                max_seconds=args.retry_backoff_max_seconds,
                jitter_seconds=args.retry_jitter_seconds,
            )
            tqdm.write(
                "[judge-retry] "
                f"comparison={prepared.comparison_id} "
                f"delay_seconds={delay:.3f} "
                f"next_attempt={attempt + 1}/{max_attempts}"
            )
            time.sleep(delay)
    assert last_error is not None
    raise last_error


def validate_records(records, prepared_by_id):
    if len(records) != len(prepared_by_id):
        raise RuntimeError("final judgment count mismatch")
    ids = [record["comparison_id"] for record in records]
    if len(ids) != len(set(ids)) or set(ids) != set(prepared_by_id):
        raise RuntimeError("final comparison set mismatch")
    for record in records:
        prepared = prepared_by_id[record["comparison_id"]]
        if record.get("record_status") != "completed":
            raise RuntimeError("non-completed record")
        if record.get("request_sha256") != prepared.request_sha256:
            raise RuntimeError("request hash mismatch")
        if record.get("system_prompt") != prepared.system_prompt:
            raise RuntimeError("system prompt mismatch")
        if record.get("user_prompt") != prepared.user_prompt:
            raise RuntimeError("user prompt mismatch")
        if record.get("judge_output_contract_version") != (
            prepared.judge_output_contract_version
        ):
            raise RuntimeError("judge output contract mismatch")
        if not prepared.include_serious_errors and (
            record["serious_error_findings"]
            or record["criterion_adjustments"]
        ):
            raise RuntimeError("rubric-only contract contains error data")
        if not prepared.include_learning_evidence:
            if record.get("learning_evidence_fragment_ids"):
                raise RuntimeError("gold-answer-only contract contains evidence")
            if record.get("learning_evidence_included") is not False:
                raise RuntimeError("learning-evidence policy mismatch")
            if "## Căn cứ học liệu" in record["user_prompt"]:
                raise RuntimeError("gold-answer-only prompt contains evidence")
        raw_ids = {
            item["rubric_id"]
            for item in record["raw_criterion_judgments"]
        }
        adjusted_ids = {
            item["rubric_id"]
            for item in record["adjusted_criterion_judgments"]
        }
        expected_ids = set(prepared.applicable_rubric_ids)
        if raw_ids != expected_ids or adjusted_ids != expected_ids:
            raise RuntimeError("rubric coverage mismatch")
        adjusted_once = [
            item["rubric_id"]
            for item in record["criterion_adjustments"]
        ]
        if len(adjusted_once) != len(set(adjusted_once)):
            raise RuntimeError("criterion adjusted more than once")
        if record["overall_judgment"]["target_judgment"] not in {
            "Win",
            "Tie",
            "Lose",
        }:
            raise RuntimeError("target judgment missing")
    return {"validated": True, "record_count": len(records)}


def record_cost(records, pricing):
    return sum(
        pricing.estimate(
            int(record["usage"]["input_tokens"]),
            int(record["usage"]["output_tokens"]),
        )
        for record in records
    )


def failed_attempt_cost(error_path, pricing):
    total = 0.0
    for record in read_jsonl(error_path):
        usage = record.get("usage")
        if not isinstance(usage, dict):
            continue
        total += pricing.estimate(
            int(usage.get("input_tokens", 0) or 0),
            int(usage.get("output_tokens", 0) or 0),
        )
    return total


def total_run_cost(records, error_path, pricing):
    return record_cost(records, pricing) + failed_attempt_cost(
        error_path, pricing
    )


def main() -> None:
    global STAGE
    args = parse_args()
    STAGE = {
        "smoke": "benchmark_evaluation_judge_smoke",
        "pilot": "benchmark_evaluation_judge_pilot",
        "cost-pilot": "benchmark_evaluation_judge_cost_pilot",
        "full": "benchmark_evaluation_judge_full",
    }[args.run_kind]
    if args.target_runs is None:
        if args.run_kind in {"pilot", "cost-pilot", "full"}:
            expected = 3 if args.run_kind in {"pilot", "cost-pilot"} else 2
            raise ValueError(
                f"{args.run_kind} judge requires {expected} explicit "
                "--target-run inputs"
            )
        args.target_runs = default_target_runs()
    validate_args(args)
    prepared = prepare_from_args(args)
    if args.run_kind in {"pilot", "cost-pilot", "full"}:
        expected_candidates = {
            "pilot": 80,
            "cost-pilot": 30,
            "full": 1400,
        }[args.run_kind]
        expected_targets = (
            3 if args.run_kind in {"pilot", "cost-pilot"} else 2
        )
        expected_comparisons = expected_candidates * expected_targets
        candidate_counts = Counter(
            row.benchmark_candidate_id for row in prepared
        )
        if (
            len(prepared) != expected_comparisons
            or len(candidate_counts) != expected_candidates
            or set(candidate_counts.values()) != {expected_targets}
        ):
            raise RuntimeError(
                f"{args.run_kind} judge requires exactly "
                f"{expected_candidates} common candidates across "
                f"{expected_targets} target configurations and "
                f"{expected_comparisons} comparisons"
            )
    prepared_by_id = {row.comparison_id: row for row in prepared}
    judgment_path = args.output_dir / "run_judgments.jsonl"
    manifest_path = args.output_dir / "run_manifest.json"
    error_path = args.output_dir / "run_errors.jsonl"
    completed = load_completed(
        judgment_path, prepared_by_id, args.model
    )
    pending = [
        row for row in prepared if row.comparison_id not in completed
    ]
    pricing = TokenPricing(
        args.input_usd_per_million, args.output_usd_per_million
    )
    previous_run_cost = total_run_cost(
        list(completed.values()), error_path, pricing
    )
    upper_cost = (
        len(pending)
        * (args.max_retries + 1)
        * pricing.estimate(
            args.upper_bound_input_tokens, args.max_output_tokens
        )
    )
    if upper_cost > args.stage_cap_usd:
        raise RuntimeError("judge upper bound exceeds stage cap")
    BudgetPolicy(
        args.hard_budget_usd, args.reserve_usd
    ).assert_next_batch_allowed(
        actual_spend_usd=(
            args.actual_spend_to_date_usd + previous_run_cost
        ),
        next_batch_upper_bound_usd=upper_cost,
    )
    preflight = {
        "execute_api": args.execute_api,
        "run_kind": args.run_kind,
        "pipeline_stage": STAGE,
        "comparison_count": len(prepared),
        "existing_record_count": len(completed),
        "pending_request_count": len(pending),
        "previous_run_cost_usd": round(previous_run_cost, 6),
        "candidate_count": len(
            {row.benchmark_candidate_id for row in prepared}
        ),
        "project": args.project if args.provider != "openai" else None,
        "provider": args.provider,
        "location": (
            args.location if args.provider != "openai" else "direct_api"
        ),
        "model": args.model,
        "temperature": args.temperature,
        "thinking_level": (
            args.thinking_level if args.provider == "gemini" else None
        ),
        "reasoning_effort": (
            args.reasoning_effort if args.provider == "openai" else None
        ),
        "max_output_tokens": args.max_output_tokens,
        "concurrency": args.concurrency,
        "execution_mode": "thread_pool",
        "max_retries": args.max_retries,
        "retry_policy": {
            "backoff": "exponential_with_deterministic_jitter",
            "base_seconds": args.retry_backoff_base_seconds,
            "max_seconds": args.retry_backoff_max_seconds,
            "jitter_seconds": args.retry_jitter_seconds,
        },
        "output_dir": portable(args.output_dir),
        "system_prompt": portable(args.system_prompt),
        "system_prompt_sha256": prepared[0].system_prompt_sha256,
        "evaluation_schema_sha256": file_hash(args.evaluation_schema),
        "judge_output_contract_version": args.judge_contract,
        "learning_evidence_policy": (
            "excluded_gold_answer_only"
            if args.judge_contract == "gold-answer-only-v4"
            else "included_raw_audit_fragments"
        ),
        "upper_bound_cost_usd": round(upper_cost, 6),
        "upper_bound_includes_all_retry_attempts": True,
        "stage_cap_usd": args.stage_cap_usd,
        "candidate_manifest": (
            portable(args.candidate_manifest)
            if args.candidate_manifest is not None
            else None
        ),
    }
    print(json.dumps(preflight, ensure_ascii=False, indent=2))
    if not args.execute_api:
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_paths = [
        args.candidate_csv,
        args.grounding_pool,
        args.requirement_run,
        args.rubrics,
        args.evaluation_schema,
        args.system_prompt,
        *args.target_runs,
    ]
    if args.judge_contract != "gold-answer-only-v4":
        input_paths.extend(
            [args.conversion_input, args.learning_fragments]
        )
    if args.judge_contract == "v2":
        input_paths.append(args.serious_errors)
    if args.candidate_manifest is not None:
        input_paths.append(args.candidate_manifest)
    manifest = {
        "record_type": {
            "smoke": "judge_smoke_manifest",
            "pilot": "judge_pilot_manifest",
            "cost-pilot": "judge_cost_pilot_manifest",
            "full": "judge_full_manifest",
        }[args.run_kind],
        "status": "running",
        "updated_at": utc_now(),
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "pipeline_stage": STAGE,
        "run_kind": args.run_kind,
        "run_id": args.output_dir.name,
        "project": args.project if args.provider != "openai" else None,
        "provider": args.provider,
        "location": (
            args.location if args.provider != "openai" else "direct_api"
        ),
        "model": args.model,
        "generation_config": {
            "temperature": args.temperature,
            "max_output_tokens": args.max_output_tokens,
            "thinking_level": (
                args.thinking_level
                if args.provider == "gemini"
                else None
            ),
            "reasoning_effort": (
                args.reasoning_effort
                if args.provider == "openai"
                else None
            ),
            "store": False if args.provider == "openai" else None,
            "structured_outputs": (
                {
                    "v2": "strict_json_schema_v2",
                    "rubric-only-v3": (
                        "strict_json_schema_rubric_only_v3"
                    ),
                    "gold-answer-only-v4": (
                        "strict_json_schema_gold_answer_only_v4"
                    ),
                }[args.judge_contract]
                if args.provider == "openai"
                else (
                    "compact_json_schema_with_local_name_validation"
                    if args.provider == "gemini"
                    else None
                )
            ),
        },
        "seed": args.seed,
        "concurrency": args.concurrency,
        "execution_mode": "thread_pool",
        "max_retries": args.max_retries,
        "retry_policy": preflight["retry_policy"],
        "system_prompt": {
            "path": portable(args.system_prompt),
            "version": prepared[0].system_prompt_version,
            "sha256": prepared[0].system_prompt_sha256,
        },
        "evaluation_schema": {
            "path": portable(args.evaluation_schema),
            "sha256": file_hash(args.evaluation_schema),
        },
        "judge_output_contract_version": args.judge_contract,
        "learning_evidence_policy": preflight[
            "learning_evidence_policy"
        ],
        "input_sha256": {
            portable(path): file_hash(path) for path in input_paths
        },
        "comparison_ids": [row.comparison_id for row in prepared],
        "candidate_ids": sorted(
            {row.benchmark_candidate_id for row in prepared}
        ),
        "budget": {
            "input_usd_per_million": args.input_usd_per_million,
            "output_usd_per_million": args.output_usd_per_million,
            "upper_bound_cost_usd": round(upper_cost, 6),
            "stage_cap_usd": args.stage_cap_usd,
            "actual_spend_to_date_usd": args.actual_spend_to_date_usd,
            "hard_budget_usd": args.hard_budget_usd,
            "reserve_usd": args.reserve_usd,
            "accounting_policy": (
                "successful judgments plus failed API attempts whenever "
                "provider usage metadata is available"
            ),
        },
        "progress": {
            "expected": len(prepared),
            "completed": len(completed),
            "failed": 0,
        },
        "methodological_limitations": [
            (
                "The Gemini 3.5 Flash judge shares a provider and model "
                "family with one target tutor model; report its results "
                "separately and validate against blind human judgments."
            )
        ]
        if args.provider == "gemini"
        else [],
    }
    if args.judge_contract == "gold-answer-only-v4":
        manifest["methodological_limitations"].append(
            "Subject-matter accuracy is anchored only to gold_answer; "
            "learning-resource fragments are excluded from judge input."
        )
    if args.run_kind in {"pilot", "cost-pilot", "full"}:
        manifest["methodological_limitations"].append(
            "No independent human calibration is available before this "
            "pilot; all judge results remain exploratory."
        )
    atomic_json(manifest_path, manifest)
    if args.provider == "gemini":
        caller = GeminiVertexJudgeCaller(
            project=args.project,
            location=args.location,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            seed=args.seed,
            thinking_level=args.thinking_level,
            temperature=args.temperature,
        )
    elif args.provider == "claude":
        caller = ClaudeVertexJudgeCaller(
            project=args.project,
            location=args.location,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            temperature=(
                args.temperature if args.temperature is not None else 0.0
            ),
        )
    else:
        from dotenv import load_dotenv

        load_dotenv(args.api_key_env_file, override=False)
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing from the process environment "
                f"and {args.api_key_env_file}"
            )
        caller = OpenAIJudgeCaller(
            api_key=api_key,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
        )
    lock = threading.Lock()
    failed = []
    try:
        with tqdm(
            total=len(prepared),
            initial=len(completed),
            desc=f"{args.model} judge",
            unit="cmp",
            dynamic_ncols=True,
        ) as progress:
            with ThreadPoolExecutor(
                max_workers=args.concurrency
            ) as executor:
                futures = {
                    executor.submit(
                        call_one,
                        caller=caller,
                        prepared=row,
                        args=args,
                        error_path=error_path,
                        write_lock=lock,
                    ): row
                    for row in pending
                }
                for future in as_completed(futures):
                    row = futures[future]
                    try:
                        record = future.result()
                    except Exception as exc:
                        failed.append(row.comparison_id)
                        tqdm.write(
                            "[judge-failed] "
                            f"comparison={row.comparison_id} "
                            f"type={type(exc).__name__} error={exc}"
                        )
                    else:
                        with lock:
                            append_jsonl(judgment_path, record)
                        completed[row.comparison_id] = record
                    with lock:
                        cost = total_run_cost(
                            list(completed.values()), error_path, pricing
                        )
                    progress.update(1)
                    progress.set_postfix(
                        workers=args.concurrency,
                        failed=len(failed),
                        cost=f"${cost:.3f}",
                    )
                    manifest["updated_at"] = utc_now()
                    manifest["progress"] = {
                        "expected": len(prepared),
                        "completed": len(completed),
                        "failed": len(failed),
                    }
                    manifest["budget"]["actual_run_cost_usd"] = round(
                        cost, 6
                    )
                    atomic_json(manifest_path, manifest)
    finally:
        caller.close()

    records = read_jsonl(judgment_path)
    actual_cost = total_run_cost(records, error_path, pricing)
    manifest["updated_at"] = utc_now()
    manifest["failed_comparison_ids"] = sorted(failed)
    manifest["budget"]["actual_run_cost_usd"] = round(actual_cost, 6)
    if failed:
        manifest["status"] = "incomplete"
        manifest["integrity"] = {"validated": False}
        atomic_json(manifest_path, manifest)
        raise RuntimeError(
            f"{len(failed)} comparisons failed; see {error_path}"
        )
    manifest["integrity"] = validate_records(records, prepared_by_id)
    manifest["status"] = "completed"
    atomic_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "status": "completed",
                "records": len(records),
                "actual_run_cost_usd": round(actual_cost, 6),
                "output": portable(judgment_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

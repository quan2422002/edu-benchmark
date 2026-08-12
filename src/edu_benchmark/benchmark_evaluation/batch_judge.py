"""Provider-neutral helpers for asynchronous full judge batches.

This module keeps request construction, provider-output parsing, local
validation, and final record construction separate from the APIs that submit
and monitor batch jobs.  Synchronous judge callers remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from google.genai import types
from openai.types.responses.response import Response as OpenAIResponse
from edu_benchmark.model_providers.vertex_ai import normalize_finish_reason

from .gemini_judge import (
    _build_gemini_response_schema,
)
from .judge import (
    GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES,
    JudgeOutputError,
    PreparedJudgeRequest,
    postprocess_judge_output,
    validate_judge_output,
)
from .openai_judge import build_judge_response_schema


SUCCESS_FINISH_REASONS = frozenset({"STOP", "END_TURN"})


class BatchJudgeError(RuntimeError):
    """Raised when a batch artifact cannot be trusted or normalized."""


@dataclass(frozen=True)
class ParsedProviderResult:
    """Normalized provider response used by the common postprocessor."""

    response_text: str
    response_id: str
    model_version: str
    finish_reason: str
    input_tokens: int
    output_tokens: int
    usage_metadata: Mapping[str, Any]
    provider_request_id: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def atomic_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")
        handle.flush()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BatchJudgeError(
                f"{path}:{line_number}: invalid JSON"
            ) from exc
        if not isinstance(value, dict):
            raise BatchJudgeError(
                f"{path}:{line_number}: expected a JSON object"
            )
        rows.append(value)
    return rows


def schema_name(prepared: PreparedJudgeRequest) -> str:
    return {
        "v2": "blind_pairwise_judgment_v2",
        "rubric-only-v3": "blind_pairwise_judgment_rubric_only_v3",
        "gold-answer-only-v4": (
            "blind_pairwise_judgment_gold_answer_only_v4"
        ),
    }[prepared.judge_output_contract_version]


def build_openai_batch_line(
    prepared: PreparedJudgeRequest,
    *,
    model: str,
    max_output_tokens: int,
    reasoning_effort: str,
) -> dict[str, Any]:
    """Return one official `/v1/responses` Batch API request line."""

    return {
        "custom_id": prepared.comparison_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": model,
            "instructions": prepared.system_prompt,
            "input": prepared.user_prompt,
            "max_output_tokens": max_output_tokens,
            "reasoning": {"effort": reasoning_effort},
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name(prepared),
                    "schema": build_judge_response_schema(prepared),
                    "strict": True,
                }
            },
            "store": False,
            "truncation": "disabled",
        },
    }


def build_gemini_batch_line(
    prepared: PreparedJudgeRequest,
    *,
    max_output_tokens: int,
    seed: int,
    thinking_level: str,
) -> dict[str, Any]:
    """Return one Vertex Gemini GCS batch input line."""

    normalized_level = thinking_level.strip().upper()
    config = types.GenerateContentConfig(
        max_output_tokens=max_output_tokens,
        seed=seed,
        response_mime_type="application/json",
        response_json_schema=_build_gemini_response_schema(prepared),
        thinking_config=types.ThinkingConfig(
            thinking_level=getattr(types.ThinkingLevel, normalized_level),
            include_thoughts=False,
        ),
    ).model_dump(mode="json", by_alias=True, exclude_none=True)
    return {
        "id": prepared.comparison_id,
        "request": {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prepared.user_prompt}],
                }
            ],
            "system_instruction": {
                "parts": [{"text": prepared.system_prompt}]
            },
            "generation_config": config,
        },
    }


def _openai_output_text(response: OpenAIResponse) -> str:
    value = getattr(response, "output_text", "")
    if isinstance(value, str) and value.strip():
        return value
    pieces: list[str] = []
    for item in response.output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if isinstance(text, str):
                pieces.append(text)
    return "".join(pieces)


def parse_openai_batch_output(
    row: Mapping[str, Any],
) -> tuple[str, ParsedProviderResult]:
    comparison_id = str(row.get("custom_id") or "").strip()
    if not comparison_id:
        raise BatchJudgeError("OpenAI batch output is missing custom_id")
    error = row.get("error")
    if error:
        raise BatchJudgeError(
            f"{comparison_id}: OpenAI batch request error: {error}"
        )
    wrapper = row.get("response")
    if not isinstance(wrapper, Mapping):
        raise BatchJudgeError(
            f"{comparison_id}: OpenAI batch output is missing response"
        )
    status_code = int(wrapper.get("status_code", 0) or 0)
    if status_code != 200:
        raise BatchJudgeError(
            f"{comparison_id}: OpenAI batch HTTP {status_code}: "
            f"{wrapper.get('body')}"
        )
    body = wrapper.get("body")
    if not isinstance(body, Mapping):
        raise BatchJudgeError(
            f"{comparison_id}: OpenAI response body is not an object"
        )
    response = OpenAIResponse.model_validate(body)
    status = str(response.status or "").lower()
    incomplete = response.incomplete_details
    incomplete_reason = str(
        getattr(incomplete, "reason", "") or ""
    ).upper()
    finish_reason = (
        "STOP"
        if status == "completed"
        else incomplete_reason or status.upper() or "UNKNOWN"
    )
    response_text = _openai_output_text(response)
    if not response_text.strip():
        raise BatchJudgeError(
            f"{comparison_id}: empty OpenAI response ({finish_reason})"
        )
    usage = (
        response.usage.model_dump(mode="json", exclude_none=True)
        if response.usage is not None
        else {}
    )
    return comparison_id, ParsedProviderResult(
        response_text=response_text,
        response_id=str(response.id or ""),
        model_version=str(response.model or ""),
        finish_reason=finish_reason,
        input_tokens=int(usage.get("input_tokens", 0) or 0),
        output_tokens=int(usage.get("output_tokens", 0) or 0),
        usage_metadata=usage,
        provider_request_id=str(wrapper.get("request_id") or ""),
    )


def parse_gemini_batch_output(
    row: Mapping[str, Any],
) -> tuple[str, ParsedProviderResult]:
    comparison_id = str(row.get("id") or row.get("key") or "").strip()
    if not comparison_id:
        raise BatchJudgeError("Gemini batch output is missing id/key")
    status = row.get("status")
    if status not in (None, "", {}, []):
        raise BatchJudgeError(
            f"{comparison_id}: Gemini batch request status: {status}"
        )
    body = row.get("response")
    if not isinstance(body, Mapping):
        raise BatchJudgeError(
            f"{comparison_id}: Gemini batch output is missing response"
        )
    response = types.GenerateContentResponse.model_validate(body)
    candidates = response.candidates or []
    finish_reason = normalize_finish_reason(
        candidates[0].finish_reason if candidates else None
    )
    try:
        response_text = response.text or ""
    except (AttributeError, ValueError):
        response_text = ""
    if not response_text.strip():
        raise BatchJudgeError(
            f"{comparison_id}: empty Gemini response ({finish_reason})"
        )
    usage = (
        response.usage_metadata.model_dump(
            mode="json", by_alias=False, exclude_none=True
        )
        if response.usage_metadata is not None
        else {}
    )
    return comparison_id, ParsedProviderResult(
        response_text=response_text,
        response_id=str(response.response_id or ""),
        model_version=str(response.model_version or ""),
        finish_reason=finish_reason,
        input_tokens=int(usage.get("prompt_token_count", 0) or 0),
        output_tokens=int(
            (usage.get("candidates_token_count", 0) or 0)
            + (usage.get("thoughts_token_count", 0) or 0)
        ),
        usage_metadata=usage,
        provider_request_id="",
    )


def build_judgment_record(
    *,
    prepared: PreparedJudgeRequest,
    provider_result: ParsedProviderResult,
    provider: str,
    judge_model: str,
    run_id: str,
    evaluation_schema_sha256: str,
    batch_attempt: int,
    provider_job_name: str,
) -> dict[str, Any]:
    if provider_result.finish_reason not in SUCCESS_FINISH_REASONS:
        raise JudgeOutputError(
            f"non-terminal finish reason {provider_result.finish_reason}"
        )
    normalized = validate_judge_output(
        provider_result.response_text,
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
        "experiment_id": "20260727_170150",
        "plan_id": "plan05",
        "pipeline_stage": "benchmark_evaluation_judge_full_batch",
        "run_id": run_id,
        "comparison_id": prepared.comparison_id,
        "benchmark_candidate_id": prepared.benchmark_candidate_id,
        "target_run_id": prepared.target_run_id,
        "target_response_id": prepared.target_response_id,
        "target_model_id": prepared.target_model_id,
        "judge_model_id": judge_model,
        "judge_model_version": (
            provider_result.model_version or judge_model
        ),
        "judge_response_id": provider_result.response_id,
        "attempt": batch_attempt + 1,
        "execution_mode": "asynchronous_batch",
        "provider": provider,
        "provider_job_name": provider_job_name,
        "provider_request_id": provider_result.provider_request_id,
        "latency_seconds": None,
        "finish_reason": provider_result.finish_reason,
        **prepared.trace_fields(),
        "evaluation_schema_sha256": evaluation_schema_sha256,
        "judge_output_contract_version": (
            prepared.judge_output_contract_version
        ),
        "raw_judge_response": provider_result.response_text,
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
            "input_tokens": provider_result.input_tokens,
            "output_tokens": provider_result.output_tokens,
            "provider_metadata": dict(provider_result.usage_metadata),
        },
    }


def validate_judgment_records(
    records: Sequence[Mapping[str, Any]],
    prepared_by_id: Mapping[str, PreparedJudgeRequest],
    *,
    judge_model: str,
) -> dict[str, Any]:
    if len(records) != len(prepared_by_id):
        raise BatchJudgeError("final judgment count mismatch")
    ids = [str(record.get("comparison_id") or "") for record in records]
    if len(ids) != len(set(ids)) or set(ids) != set(prepared_by_id):
        raise BatchJudgeError("final comparison set mismatch")
    for record in records:
        comparison_id = str(record["comparison_id"])
        prepared = prepared_by_id[comparison_id]
        if record.get("record_status") != "completed":
            raise BatchJudgeError(f"{comparison_id}: non-completed record")
        if record.get("judge_model_id") != judge_model:
            raise BatchJudgeError(f"{comparison_id}: judge model mismatch")
        if record.get("request_sha256") != prepared.request_sha256:
            raise BatchJudgeError(f"{comparison_id}: request hash mismatch")
        if record.get("system_prompt") != prepared.system_prompt:
            raise BatchJudgeError(f"{comparison_id}: system prompt mismatch")
        if record.get("user_prompt") != prepared.user_prompt:
            raise BatchJudgeError(f"{comparison_id}: user prompt mismatch")
        if record.get("judge_output_contract_version") != (
            prepared.judge_output_contract_version
        ):
            raise BatchJudgeError(f"{comparison_id}: contract mismatch")
        raw_ids = {
            item["rubric_id"]
            for item in record["raw_criterion_judgments"]
        }
        if raw_ids != set(prepared.applicable_rubric_ids):
            raise BatchJudgeError(f"{comparison_id}: rubric mismatch")
        if not prepared.include_learning_evidence and (
            record.get("learning_evidence_fragment_ids")
            or record.get("learning_evidence_included") is not False
            or "## Căn cứ học liệu" in str(record.get("user_prompt") or "")
        ):
            raise BatchJudgeError(
                f"{comparison_id}: learning-evidence policy mismatch"
            )
    return {"validated": True, "record_count": len(records)}


def request_cost_usd(
    *,
    input_tokens: int,
    output_tokens: int,
    input_usd_per_million: float,
    output_usd_per_million: float,
) -> float:
    return (
        input_tokens * input_usd_per_million
        + output_tokens * output_usd_per_million
    ) / 1_000_000


def empirical_cost_projection(
    calibration_records: Sequence[Mapping[str, Any]],
    *,
    request_count: int,
    input_usd_per_million: float,
    output_usd_per_million: float,
    safety_multiplier: float,
) -> dict[str, Any]:
    if not calibration_records:
        raise BatchJudgeError("calibration judgments are empty")
    costs = []
    for record in calibration_records:
        usage = record.get("usage")
        if not isinstance(usage, Mapping):
            raise BatchJudgeError("calibration record is missing usage")
        costs.append(
            request_cost_usd(
                input_tokens=int(usage.get("input_tokens", 0) or 0),
                output_tokens=int(usage.get("output_tokens", 0) or 0),
                input_usd_per_million=input_usd_per_million,
                output_usd_per_million=output_usd_per_million,
            )
        )
    ordered = sorted(costs)
    rank = max(1, math.ceil(0.95 * len(ordered)))
    p95 = ordered[rank - 1]
    mean = sum(ordered) / len(ordered)
    projected = p95 * request_count * safety_multiplier
    return {
        "calibration_record_count": len(ordered),
        "mean_usd_per_request": round(mean, 9),
        "p95_usd_per_request": round(p95, 9),
        "safety_multiplier": safety_multiplier,
        "projected_request_count": request_count,
        "projected_cost_usd": round(projected, 6),
        "projection_policy": (
            "empirical_p95_batch_token_cost_x_request_count_x_safety"
        ),
    }


def actual_cost_usd(
    records: Sequence[Mapping[str, Any]],
    *,
    input_usd_per_million: float,
    output_usd_per_million: float,
) -> float:
    return sum(
        request_cost_usd(
            input_tokens=int(record["usage"]["input_tokens"]),
            output_tokens=int(record["usage"]["output_tokens"]),
            input_usd_per_million=input_usd_per_million,
            output_usd_per_million=output_usd_per_million,
        )
        for record in records
    )

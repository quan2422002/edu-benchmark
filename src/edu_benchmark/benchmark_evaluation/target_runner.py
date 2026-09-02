"""Provider-neutral orchestration for resumable target-response generation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import time
import traceback
from typing import Any, Callable, Mapping, Protocol, Sequence, TypeVar

from edu_benchmark.model_providers.contracts import (
    GenerationSettings,
    ModelMessage,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)

from .config_builder import PRINCIPLE_ORDER
from .smoke import PreparedTutorRequest


SUCCESS_FINISH_REASONS = frozenset({"STOP", "END_TURN"})
TRUNCATED_FINISH_REASONS = frozenset(
    {"MAX_TOKENS", "LENGTH", "TOKEN_LIMIT"}
)
LOCAL_COST_BASIS = "local_runtime_no_token_api_charge"
TOKEN_COST_BASES = frozenset({"token_usage", "legacy_token_usage"})
RUNTIME_COST_BASIS = "endpoint_runtime"


class TargetRunnerInvariantError(RuntimeError):
    """Non-retryable mismatch in a locked request or provider response."""

    retryable = False


T = TypeVar("T")


class ResourceMonitor(Protocol):
    """Optional monitor around a synchronous call or concurrent invocation."""

    def measure(self, operation: Callable[[], T]) -> tuple[T, dict[str, Any]]:
        ...


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def candidate_ids_sha256(candidate_ids: Sequence[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(candidate_ids)).encode("utf-8")
    ).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    """Append and fsync one checkpoint record."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(value), ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def normalize_finish_reason(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    name = getattr(value, "name", None)
    raw = name if isinstance(name, str) and name.strip() else getattr(
        value, "value", value
    )
    return str(raw).rsplit(".", 1)[-1].strip().upper() or "UNKNOWN"


def completion_state(finish_reason: Any) -> tuple[str, str | None]:
    normalized = normalize_finish_reason(finish_reason)
    if normalized in SUCCESS_FINISH_REASONS:
        return "completed", None
    if normalized in TRUNCATED_FINISH_REASONS:
        return "needs_review", "output_truncated"
    if normalized == "UNKNOWN":
        return "needs_review", "missing_finish_reason"
    return "needs_review", f"non_success_finish_reason:{normalized}"


def retry_delay_seconds(
    *,
    retry_index: int,
    base_seconds: float,
    max_seconds: float,
    jitter_seconds: float,
    seed: int,
    provider_retry_after_seconds: float | None = None,
) -> float:
    if retry_index < 1:
        raise ValueError("retry_index must be positive")
    exponential = min(max_seconds, base_seconds * (2 ** (retry_index - 1)))
    jitter = random.Random(seed + retry_index).uniform(0, jitter_seconds)
    provider_hint = max(0.0, provider_retry_after_seconds or 0.0)
    return round(min(max_seconds, max(exponential + jitter, provider_hint)), 3)


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2
    backoff_base_seconds: float = 2.0
    backoff_max_seconds: float = 30.0
    jitter_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.backoff_base_seconds < 0:
            raise ValueError("backoff_base_seconds must be non-negative")
        if self.backoff_max_seconds < self.backoff_base_seconds:
            raise ValueError("backoff_max_seconds must be >= base")
        if self.jitter_seconds < 0:
            raise ValueError("jitter_seconds must be non-negative")


@dataclass(frozen=True)
class TargetRunIdentity:
    experiment_id: str
    plan_id: str
    pipeline_stage: str
    run_id: str

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not str(value).strip():
                raise ValueError(f"{name} must be non-empty")


@dataclass(frozen=True)
class TargetRunConfig:
    identity: TargetRunIdentity
    backend: str
    model: str
    generation: GenerationSettings
    provider_options: Mapping[str, Any] = field(default_factory=dict)
    provider_identity: Mapping[str, Any] = field(default_factory=dict)
    resource_monitor: Mapping[str, Any] = field(default_factory=dict)
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    max_concurrency: int = 1
    cost_basis: str = LOCAL_COST_BASIS
    input_usd_per_million: float = 0.0
    output_usd_per_million: float = 0.0

    def __post_init__(self) -> None:
        if not self.backend.strip() or not self.model.strip():
            raise ValueError("backend and model must be non-empty")
        if self.input_usd_per_million < 0 or self.output_usd_per_million < 0:
            raise ValueError("token prices must be non-negative")
        if not 1 <= self.max_concurrency <= 32:
            raise ValueError("max_concurrency must be between 1 and 32")
        if self.cost_basis == LOCAL_COST_BASIS and (
            self.input_usd_per_million or self.output_usd_per_million
        ):
            raise ValueError("local runtime cost basis requires zero token prices")

    def locked_payload(self) -> dict[str, Any]:
        payload = {
            "identity": asdict(self.identity),
            "backend": self.backend,
            "model": self.model,
            "generation": asdict(self.generation),
            "provider_options": dict(self.provider_options),
            "provider_identity": dict(self.provider_identity),
            "resource_monitor": dict(self.resource_monitor),
            "retry": asdict(self.retry),
            "cost_basis": self.cost_basis,
            "input_usd_per_million": self.input_usd_per_million,
            "output_usd_per_million": self.output_usd_per_million,
        }
        # Preserve hashes of sequential manifests created before concurrency
        # became an explicit execution setting.
        if self.max_concurrency != 1:
            payload["max_concurrency"] = self.max_concurrency
        return payload

    @property
    def sha256(self) -> str:
        return sha256_json(self.locked_payload())


@dataclass(frozen=True)
class TargetRunPaths:
    output_dir: Path

    @property
    def responses(self) -> Path:
        return self.output_dir / "run_responses.jsonl"

    @property
    def errors(self) -> Path:
        return self.output_dir / "run_errors.jsonl"

    @property
    def manifest(self) -> Path:
        return self.output_dir / "run_manifest.json"


def to_model_request(
    prepared: PreparedTutorRequest, config: TargetRunConfig
) -> ModelRequest:
    return ModelRequest(
        backend=config.backend,
        model=config.model,
        system_instruction=prepared.system_instruction,
        messages=tuple(
            ModelMessage(role=message.role, content=message.content)
            for message in prepared.conversation.messages
        ),
        generation=config.generation,
        provider_options=dict(config.provider_options),
    )


def _estimate_cost(config: TargetRunConfig, response: ModelResponse) -> float:
    usage = response.usage
    return (
        usage.input_tokens * config.input_usd_per_million
        + usage.output_tokens * config.output_usd_per_million
    ) / 1_000_000


def build_response_record(
    *,
    prepared: PreparedTutorRequest,
    response: ModelResponse,
    config: TargetRunConfig,
    latency_seconds: float,
    attempt: int,
) -> dict[str, Any]:
    finish_reason = normalize_finish_reason(response.finish_reason)
    response_status, completion_issue = completion_state(finish_reason)
    response_id = response.response_id or hashlib.sha256(
        (
            config.identity.run_id
            + prepared.benchmark_candidate_id
            + prepared.request_hash
            + response.text
        ).encode("utf-8")
    ).hexdigest()[:24]
    return {
        "record_type": "target_response",
        "created_at": utc_now(),
        **asdict(config.identity),
        "benchmark_candidate_id": prepared.benchmark_candidate_id,
        "provider": config.backend,
        "model_id": config.model,
        "model_version": response.model_version or response.model,
        "response_id": response_id,
        "response_text": response.text,
        "finish_reason": finish_reason,
        "response_status": response_status,
        "completion_issue": completion_issue,
        **prepared.trace_fields(),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "estimated_cost_usd": round(_estimate_cost(config, response), 8),
            "cost_basis": config.cost_basis,
        },
        "latency_seconds": round(latency_seconds, 4),
        "attempt": attempt,
    }


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def validate_target_records(
    path: Path,
    *,
    expected_candidate_ids: set[str],
    expected_identity: TargetRunIdentity | None = None,
    expected_backend: str | None = None,
    expected_model: str | None = None,
) -> dict[str, Any]:
    """Validate both historical and current target-response record shapes."""

    if not path.exists():
        return {
            "validated": True,
            "record_count": 0,
            "completed_record_count": 0,
            "needs_review_record_count": 0,
        }
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    candidate_ids = [record.get("benchmark_candidate_id") for record in records]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError("target output contains duplicate candidate IDs")
    if not set(candidate_ids) <= expected_candidate_ids:
        raise RuntimeError("target output contains unexpected candidate IDs")
    expected_identity_values = asdict(expected_identity) if expected_identity else {}
    for record in records:
        if record.get("record_type") != "target_response":
            raise RuntimeError("invalid target record_type")
        for field_name, expected in expected_identity_values.items():
            if record.get(field_name) != expected:
                raise RuntimeError(f"target record {field_name} mismatch")
        if expected_backend and record.get("provider") != expected_backend:
            raise RuntimeError("target record provider mismatch")
        if expected_model and record.get("model_id") != expected_model:
            raise RuntimeError("target record model mismatch")
        if not str(record.get("response_text", "")).strip():
            raise RuntimeError("target output contains an empty response")
        finish_reason = normalize_finish_reason(record.get("finish_reason"))
        status, issue = completion_state(finish_reason)
        if record.get("finish_reason") != finish_reason:
            raise RuntimeError("finish_reason must be normalized")
        if record.get("response_status") != status:
            raise RuntimeError("response_status does not match finish_reason")
        if record.get("completion_issue") != issue:
            raise RuntimeError("completion_issue does not match finish_reason")
        system_prompt = record.get("system_prompt")
        messages = record.get("conversation_messages")
        if not isinstance(system_prompt, str) or not system_prompt.strip():
            raise RuntimeError("invalid system_prompt")
        if not isinstance(messages, list) or not messages:
            raise RuntimeError("invalid conversation_messages")
        if not all(
            isinstance(message, dict)
            and set(message) == {"role", "content"}
            and message["role"] in {"user", "assistant"}
            and isinstance(message["content"], str)
            and message["content"].strip()
            for message in messages
        ):
            raise RuntimeError("invalid conversation_messages")
        if messages[0]["role"] != "user" or messages[-1]["role"] != "user":
            raise RuntimeError("conversation must start and end with user")
        if any(
            left["role"] == right["role"]
            for left, right in zip(messages, messages[1:])
        ):
            raise RuntimeError("conversation message roles must alternate")
        if record.get("user_prompt") != messages[-1]["content"]:
            raise RuntimeError("user_prompt must equal final user message")
        for field_name in (
            "input_hash",
            "system_instruction_hash",
            "messages_hash",
            "instruction_bundle_sha256",
        ):
            if not _valid_sha256(record.get(field_name)):
                raise RuntimeError(f"invalid {field_name}")
        if record["system_instruction_hash"] != hashlib.sha256(
            system_prompt.encode("utf-8")
        ).hexdigest():
            raise RuntimeError("system_prompt hash mismatch")
        if record["messages_hash"] != hashlib.sha256(
            json.dumps(
                messages, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest():
            raise RuntimeError("conversation_messages hash mismatch")
        if record["input_hash"] != sha256_json(
            {"system_instruction": system_prompt, "messages": messages}
        ):
            raise RuntimeError("persisted request hash mismatch")
        required = record.get("required_principle_ids")
        if not isinstance(required, list) or not required:
            raise RuntimeError("invalid required_principle_ids")
        canonical = [item for item in PRINCIPLE_ORDER if item in set(required)]
        if required != canonical or len(required) != len(set(required)):
            raise RuntimeError("invalid required_principle_ids")
        usage = record.get("usage")
        if not isinstance(usage, dict):
            raise RuntimeError("invalid normalized usage")
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        cost = usage.get("estimated_cost_usd")
        if (
            not isinstance(input_tokens, int)
            or isinstance(input_tokens, bool)
            or input_tokens < 0
            or not isinstance(output_tokens, int)
            or isinstance(output_tokens, bool)
            or output_tokens < 0
        ):
            raise RuntimeError("invalid normalized usage")
        basis = usage.get("cost_basis", "legacy_token_usage")
        if basis == RUNTIME_COST_BASIS:
            if cost is not None:
                raise RuntimeError("endpoint runtime cost must be null per request")
        elif basis == LOCAL_COST_BASIS:
            if cost != 0.0:
                raise RuntimeError("local runtime token API cost must be zero")
        elif basis in TOKEN_COST_BASES:
            if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
                raise RuntimeError("invalid token-billed cost")
        else:
            raise RuntimeError("invalid usage cost_basis")
    return {
        "validated": True,
        "record_count": len(records),
        "completed_record_count": sum(
            record["response_status"] == "completed" for record in records
        ),
        "needs_review_record_count": sum(
            record["response_status"] == "needs_review" for record in records
        ),
    }


def _load_existing_records(
    path: Path, prepared_by_id: Mapping[str, PreparedTutorRequest]
) -> tuple[set[str], set[str], set[str]]:
    if not path.exists():
        return set(), set(), set()
    recorded: set[str] = set()
    completed: set[str] = set()
    needs_review: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        candidate_id = record.get("benchmark_candidate_id")
        if candidate_id in recorded:
            raise RuntimeError(f"duplicate target record for {candidate_id}")
        prepared = prepared_by_id.get(str(candidate_id))
        if prepared is None:
            raise RuntimeError(f"unexpected existing candidate {candidate_id}")
        for field_name, expected in (
            ("input_hash", prepared.request_hash),
            ("instruction_bundle_version", prepared.instruction_bundle_version),
            ("instruction_bundle_sha256", prepared.instruction_bundle_sha256),
        ):
            if record.get(field_name) != expected:
                raise RuntimeError(
                    f"existing target output {field_name} drift for {candidate_id}"
                )
        recorded.add(str(candidate_id))
        if record.get("response_status") == "completed":
            completed.add(str(candidate_id))
        elif record.get("response_status") == "needs_review":
            needs_review.add(str(candidate_id))
        else:
            raise RuntimeError(f"invalid response_status for {candidate_id}")
    return recorded, completed, needs_review


def _error_record(
    *,
    exc: Exception,
    prepared: PreparedTutorRequest,
    config: TargetRunConfig,
    attempt: int,
    retry_scheduled: bool,
) -> dict[str, Any]:
    return {
        "record_type": "api_call_error",
        "occurred_at": utc_now(),
        **asdict(config.identity),
        "benchmark_candidate_id": prepared.benchmark_candidate_id,
        "provider": config.backend,
        "model": config.model,
        "attempt": attempt,
        "max_attempts": config.retry.max_retries + 1,
        "retryable": bool(getattr(exc, "retryable", True)),
        "retry_scheduled": retry_scheduled,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "http_status": getattr(exc, "http_status", None),
        "response_body": getattr(exc, "response_body", None),
        "retry_after_seconds": getattr(exc, "retry_after_seconds", None),
        "resource_usage": getattr(exc, "resource_usage", None),
        "traceback": "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
        "request_hash": prepared.request_hash,
    }


def _validate_provider_response(
    response: ModelResponse,
    *,
    provider: ModelProvider,
    config: TargetRunConfig,
) -> None:
    if response.backend != provider.backend:
        raise TargetRunnerInvariantError("provider response backend mismatch")
    if response.model != config.model:
        raise TargetRunnerInvariantError("provider response model mismatch")
    expected_digest = str(config.provider_identity.get("model_digest", ""))
    if expected_digest and expected_digest not in response.model_version:
        raise TargetRunnerInvariantError("provider response model digest mismatch")
    lowered_text = response.text.lower()
    if "<think>" in lowered_text or "</think>" in lowered_text:
        raise TargetRunnerInvariantError(
            "provider response contains thinking markup"
        )


@dataclass(frozen=True)
class _ConcurrentOutcome:
    prepared: PreparedTutorRequest
    response: ModelResponse | None
    latency_seconds: float | None
    attempt: int
    error_records: tuple[Mapping[str, Any], ...]
    retry_events: tuple[Mapping[str, Any], ...]
    terminal_error: Exception | None


def _generate_concurrent_candidate(
    *,
    prepared: PreparedTutorRequest,
    provider: ModelProvider,
    config: TargetRunConfig,
    sleep: Callable[[float], None],
) -> _ConcurrentOutcome:
    """Generate one candidate without writing shared persistence artifacts."""

    error_records: list[Mapping[str, Any]] = []
    retry_events: list[Mapping[str, Any]] = []
    for attempt_index in range(config.retry.max_retries + 1):
        attempt = attempt_index + 1
        try:
            model_request = to_model_request(prepared, config)
            call_started = time.monotonic()
            response = provider.generate(model_request)
            latency = time.monotonic() - call_started
            _validate_provider_response(
                response,
                provider=provider,
                config=config,
            )
            return _ConcurrentOutcome(
                prepared=prepared,
                response=response,
                latency_seconds=latency,
                attempt=attempt,
                error_records=tuple(error_records),
                retry_events=tuple(retry_events),
                terminal_error=None,
            )
        except Exception as exc:
            retryable = bool(getattr(exc, "retryable", True))
            retry_scheduled = (
                retryable and attempt_index < config.retry.max_retries
            )
            error_records.append(
                _error_record(
                    exc=exc,
                    prepared=prepared,
                    config=config,
                    attempt=attempt,
                    retry_scheduled=retry_scheduled,
                )
            )
            if not retry_scheduled:
                return _ConcurrentOutcome(
                    prepared=prepared,
                    response=None,
                    latency_seconds=None,
                    attempt=attempt,
                    error_records=tuple(error_records),
                    retry_events=tuple(retry_events),
                    terminal_error=exc,
                )
            delay = retry_delay_seconds(
                retry_index=attempt,
                base_seconds=config.retry.backoff_base_seconds,
                max_seconds=config.retry.backoff_max_seconds,
                jitter_seconds=config.retry.jitter_seconds,
                seed=config.generation.seed or 0,
                provider_retry_after_seconds=getattr(
                    exc, "retry_after_seconds", None
                ),
            )
            retry_events.append(
                {
                    "event": "retry_scheduled",
                    "benchmark_candidate_id": prepared.benchmark_candidate_id,
                    "attempt": attempt,
                    "next_attempt": attempt + 1,
                    "max_attempts": config.retry.max_retries + 1,
                    "delay_seconds": delay,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            )
            sleep(delay)
    raise AssertionError("retry loop must return an outcome")


def build_locked_manifest(
    *,
    prepared: Sequence[PreparedTutorRequest],
    config: TargetRunConfig,
    source_provenance: Mapping[str, Any],
    selection_provenance: Mapping[str, Any],
    paths: TargetRunPaths,
) -> dict[str, Any]:
    candidate_ids = [item.benchmark_candidate_id for item in prepared]
    return {
        **asdict(config.identity),
        "status": "preflight_locked",
        "phase": "preflight",
        "generated_at": utc_now(),
        "provider": config.backend,
        "model": config.model,
        "candidate_count": len(candidate_ids),
        "candidate_ids": candidate_ids,
        "candidate_ids_sha256": candidate_ids_sha256(candidate_ids),
        "configuration": config.locked_payload(),
        "configuration_sha256": config.sha256,
        "source_provenance": dict(source_provenance),
        "source_provenance_sha256": sha256_json(source_provenance),
        "selection": dict(selection_provenance),
        "selection_sha256": sha256_json(selection_provenance),
        "instruction_bundle_version": prepared[0].instruction_bundle_version,
        "instruction_bundle_sha256": prepared[0].instruction_bundle_sha256,
        "recorded_candidate_ids": [],
        "completed_candidate_ids": [],
        "needs_review_candidate_ids": [],
        "failed_candidate_ids": [],
        "errors": {},
        "phase_history": [
            {"phase": "preflight_locked", "recorded_at": utc_now()}
        ],
        "resume_history": [],
        "output_file": str(paths.responses),
        "error_file": str(paths.errors),
        "integrity": validate_target_records(
            paths.responses, expected_candidate_ids=set(candidate_ids)
        ),
    }


def preflight_target_run(
    *,
    prepared: Sequence[PreparedTutorRequest],
    config: TargetRunConfig,
    paths: TargetRunPaths,
    source_provenance: Mapping[str, Any],
    selection_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    if not prepared:
        raise ValueError("prepared target request list must not be empty")
    candidate_ids = [item.benchmark_candidate_id for item in prepared]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("prepared target candidate IDs must be unique")
    for item in prepared:
        to_model_request(item, config)
    if paths.manifest.exists():
        existing = json.loads(paths.manifest.read_text(encoding="utf-8"))
        for field_name, expected in (
            ("configuration_sha256", config.sha256),
            ("candidate_ids_sha256", candidate_ids_sha256(candidate_ids)),
            ("instruction_bundle_sha256", prepared[0].instruction_bundle_sha256),
            ("source_provenance_sha256", sha256_json(source_provenance)),
            ("selection_sha256", sha256_json(selection_provenance)),
        ):
            if existing.get(field_name) != expected:
                raise RuntimeError(f"resume manifest {field_name} mismatch")
        integrity = validate_target_records(
            paths.responses,
            expected_candidate_ids=set(candidate_ids),
            expected_identity=config.identity,
            expected_backend=config.backend,
            expected_model=config.model,
        )
        prepared_by_id = {
            item.benchmark_candidate_id: item for item in prepared
        }
        recorded, completed, needs_review = _load_existing_records(
            paths.responses, prepared_by_id
        )
        if set(existing.get("recorded_candidate_ids") or []) != recorded:
            existing = {
                **existing,
                "status": (
                    "completed"
                    if len(recorded) == len(candidate_ids) and not needs_review
                    else "in_progress"
                ),
                "recorded_candidate_ids": sorted(recorded),
                "completed_candidate_ids": sorted(completed),
                "needs_review_candidate_ids": sorted(needs_review),
                "checkpoint_reconciled_at": utc_now(),
                "integrity": integrity,
            }
            atomic_json(paths.manifest, existing)
        return existing
    manifest = build_locked_manifest(
        prepared=prepared,
        config=config,
        source_provenance=source_provenance,
        selection_provenance=selection_provenance,
        paths=paths,
    )
    atomic_json(paths.manifest, manifest)
    return manifest


def run_target_responses(
    *,
    prepared: Sequence[PreparedTutorRequest],
    provider: ModelProvider,
    config: TargetRunConfig,
    paths: TargetRunPaths,
    source_provenance: Mapping[str, Any],
    selection_provenance: Mapping[str, Any],
    resource_monitor: ResourceMonitor | None = None,
    max_new_records: int | None = None,
    progress_callback: Callable[[str], None] | None = None,
    event_callback: Callable[[Mapping[str, Any]], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Execute or resume a locked run while checkpointing every attempt."""

    manifest = preflight_target_run(
        prepared=prepared,
        config=config,
        paths=paths,
        source_provenance=source_provenance,
        selection_provenance=selection_provenance,
    )
    prepared_by_id = {item.benchmark_candidate_id: item for item in prepared}
    recorded, completed, needs_review = _load_existing_records(
        paths.responses, prepared_by_id
    )
    pending = [
        item for item in prepared if item.benchmark_candidate_id not in recorded
    ]
    if max_new_records is not None:
        if max_new_records < 1:
            raise ValueError("max_new_records must be positive")
        pending = pending[:max_new_records]
    pending_at_start = [item.benchmark_candidate_id for item in pending]
    failed: set[str] = set()
    errors: dict[str, str] = dict(manifest.get("errors") or {})
    new_cost = 0.0
    provider_observations = list(manifest.get("provider_observations") or [])
    execution_resource_observations = list(
        manifest.get("execution_resource_observations") or []
    )
    started_at = time.monotonic()

    def checkpoint_running() -> None:
        checkpoint_integrity = validate_target_records(
            paths.responses,
            expected_candidate_ids=set(prepared_by_id),
            expected_identity=config.identity,
            expected_backend=config.backend,
            expected_model=config.model,
        )
        atomic_json(
            paths.manifest,
            {
                **manifest,
                "status": "in_progress",
                "phase": "running",
                "generated_at": utc_now(),
                "recorded_candidate_ids": sorted(recorded),
                "completed_candidate_ids": sorted(completed),
                "needs_review_candidate_ids": sorted(needs_review),
                "failed_candidate_ids": sorted(failed),
                "errors": errors,
                "provider_observations": provider_observations,
                "execution_resource_observations": (
                    execution_resource_observations
                ),
                "resource_summary": summarize_resource_observations(
                    provider_observations,
                    execution_resource_observations,
                ),
                "integrity": checkpoint_integrity,
            },
        )

    def record_success(
        prepared_request: PreparedTutorRequest,
        response: ModelResponse,
        latency: float,
        attempt: int,
        resource_usage: Mapping[str, Any] | None,
    ) -> None:
        nonlocal new_cost
        record = build_response_record(
            prepared=prepared_request,
            response=response,
            config=config,
            latency_seconds=latency,
            attempt=attempt,
        )
        append_jsonl(paths.responses, record)
        candidate_id = prepared_request.benchmark_candidate_id
        recorded.add(candidate_id)
        if record["response_status"] == "completed":
            completed.add(candidate_id)
        else:
            needs_review.add(candidate_id)
        errors.pop(candidate_id, None)
        new_cost += float(record["usage"]["estimated_cost_usd"] or 0)
        observation = {
            "benchmark_candidate_id": candidate_id,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "latency_seconds": round(latency, 4),
            "metadata": dict(response.usage.metadata),
            "resource_usage": resource_usage,
        }
        if config.max_concurrency > 1:
            observation["resource_measurement_scope"] = "concurrent_invocation"
        provider_observations.append(observation)
        checkpoint_running()
        if progress_callback:
            progress_callback(
                f"completed {len(recorded)}/{len(prepared)}: {candidate_id}"
            )
        if event_callback:
            event_callback(
                {
                    "event": "record_completed",
                    "benchmark_candidate_id": candidate_id,
                    "recorded_count": len(recorded),
                    "candidate_count": len(prepared),
                    "response_status": record["response_status"],
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "latency_seconds": round(latency, 4),
                    "resource_usage": resource_usage,
                }
            )

    def record_terminal_failure(
        prepared_request: PreparedTutorRequest, exc: Exception
    ) -> None:
        candidate_id = prepared_request.benchmark_candidate_id
        errors[candidate_id] = f"{type(exc).__name__}: {exc}"
        failed.add(candidate_id)
        if progress_callback:
            progress_callback(f"failed: {candidate_id}: {exc}")
        if event_callback:
            event_callback(
                {
                    "event": "record_failed",
                    "benchmark_candidate_id": candidate_id,
                    "recorded_count": len(recorded),
                    "candidate_count": len(prepared),
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            )

    if config.max_concurrency == 1:
        for prepared_request in pending:
            for attempt_index in range(config.retry.max_retries + 1):
                attempt = attempt_index + 1
                try:
                    model_request = to_model_request(prepared_request, config)

                    def generate() -> tuple[ModelResponse, float]:
                        call_started = time.monotonic()
                        result = provider.generate(model_request)
                        return result, time.monotonic() - call_started

                    resource_usage: dict[str, Any] | None = None
                    if resource_monitor is None:
                        response, latency = generate()
                    else:
                        (response, latency), resource_usage = (
                            resource_monitor.measure(generate)
                        )
                    _validate_provider_response(
                        response,
                        provider=provider,
                        config=config,
                    )
                    record_success(
                        prepared_request,
                        response,
                        latency,
                        attempt,
                        resource_usage,
                    )
                    break
                except Exception as exc:
                    retryable = bool(getattr(exc, "retryable", True))
                    retry_scheduled = (
                        retryable and attempt_index < config.retry.max_retries
                    )
                    append_jsonl(
                        paths.errors,
                        _error_record(
                            exc=exc,
                            prepared=prepared_request,
                            config=config,
                            attempt=attempt,
                            retry_scheduled=retry_scheduled,
                        ),
                    )
                    if not retry_scheduled:
                        record_terminal_failure(prepared_request, exc)
                        break
                    delay = retry_delay_seconds(
                        retry_index=attempt,
                        base_seconds=config.retry.backoff_base_seconds,
                        max_seconds=config.retry.backoff_max_seconds,
                        jitter_seconds=config.retry.jitter_seconds,
                        seed=config.generation.seed or 0,
                        provider_retry_after_seconds=getattr(
                            exc, "retry_after_seconds", None
                        ),
                    )
                    retry_event = {
                        "event": "retry_scheduled",
                        "benchmark_candidate_id": (
                            prepared_request.benchmark_candidate_id
                        ),
                        "attempt": attempt,
                        "next_attempt": attempt + 1,
                        "max_attempts": config.retry.max_retries + 1,
                        "delay_seconds": delay,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                    }
                    if progress_callback:
                        progress_callback(
                            f"retry {attempt + 1}/"
                            f"{config.retry.max_retries + 1} after "
                            f"{delay:.3f}s: "
                            f"{prepared_request.benchmark_candidate_id}"
                        )
                    if event_callback:
                        event_callback(retry_event)
                    sleep(delay)
    elif pending:
        completed_in_invocation: list[str] = []

        def execute_parallel() -> bool:
            with ThreadPoolExecutor(
                max_workers=config.max_concurrency,
                thread_name_prefix="target-provider",
            ) as executor:
                futures = {
                    executor.submit(
                        _generate_concurrent_candidate,
                        prepared=prepared_request,
                        provider=provider,
                        config=config,
                        sleep=sleep,
                    ): prepared_request
                    for prepared_request in pending
                }
                for future in as_completed(futures):
                    outcome = future.result()
                    for error_record in outcome.error_records:
                        append_jsonl(paths.errors, error_record)
                    for retry_event in outcome.retry_events:
                        if progress_callback:
                            progress_callback(
                                f"retry {retry_event['next_attempt']}/"
                                f"{retry_event['max_attempts']} after "
                                f"{retry_event['delay_seconds']:.3f}s: "
                                f"{retry_event['benchmark_candidate_id']}"
                            )
                        if event_callback:
                            event_callback(retry_event)
                    if outcome.terminal_error is not None:
                        record_terminal_failure(
                            outcome.prepared,
                            outcome.terminal_error,
                        )
                        continue
                    assert outcome.response is not None
                    assert outcome.latency_seconds is not None
                    record_success(
                        outcome.prepared,
                        outcome.response,
                        outcome.latency_seconds,
                        outcome.attempt,
                        None,
                    )
                    completed_in_invocation.append(
                        outcome.prepared.benchmark_candidate_id
                    )
            return True

        resource_usage = None
        try:
            if resource_monitor is None:
                execute_parallel()
            else:
                _, resource_usage = resource_monitor.measure(execute_parallel)
        except BaseException as exc:
            resource_usage = getattr(exc, "resource_usage", None)
            if resource_usage is not None:
                execution_resource_observations.append(
                    {
                        "measurement_scope": "concurrent_invocation",
                        "max_concurrency": config.max_concurrency,
                        "candidate_ids_scheduled": pending_at_start,
                        "candidate_ids_recorded": completed_in_invocation,
                        "interrupted": True,
                        "resource_usage": resource_usage,
                    }
                )
                checkpoint_running()
            raise
        if resource_usage is not None:
            execution_resource_observations.append(
                {
                    "measurement_scope": "concurrent_invocation",
                    "max_concurrency": config.max_concurrency,
                    "candidate_ids_scheduled": pending_at_start,
                    "candidate_ids_recorded": completed_in_invocation,
                    "interrupted": False,
                    "resource_usage": resource_usage,
                }
            )
            checkpoint_running()
    integrity = validate_target_records(
        paths.responses,
        expected_candidate_ids=set(prepared_by_id),
        expected_identity=config.identity,
        expected_backend=config.backend,
        expected_model=config.model,
    )
    if failed:
        status = "completed_with_failures"
        phase = "failed"
    elif needs_review:
        status = "completed_with_review"
        phase = "needs_review"
    elif len(recorded) == len(prepared):
        status = "completed"
        phase = "pilot_completed"
    else:
        status = "in_progress"
        phase = "technical_smoke_completed"
    phase_history = list(manifest.get("phase_history") or [])
    phase_history.append(
        {
            "phase": phase,
            "recorded_at": utc_now(),
            "record_count": len(recorded),
        }
    )
    resume_history = list(manifest.get("resume_history") or [])
    resume_history.append(
        {
            "resumed_at": utc_now(),
            "pending_candidate_ids": pending_at_start,
            "pending_candidate_ids_sha256": candidate_ids_sha256(
                pending_at_start
            ),
            "record_count_before": len(recorded) - (
                len(pending_at_start) - len(failed)
            ),
            "record_count_after": len(recorded),
            "elapsed_seconds": round(time.monotonic() - started_at, 4),
        }
    )
    updated = {
        **manifest,
        "status": status,
        "phase": phase,
        "generated_at": utc_now(),
        "recorded_candidate_ids": sorted(recorded),
        "completed_candidate_ids": sorted(completed),
        "needs_review_candidate_ids": sorted(needs_review),
        "failed_candidate_ids": sorted(failed),
        "errors": errors,
        "phase_history": phase_history,
        "resume_history": resume_history,
        "incremental_estimated_cost_usd": round(new_cost, 8),
        "provider_observations": provider_observations,
        "execution_resource_observations": execution_resource_observations,
        "resource_summary": summarize_resource_observations(
            provider_observations,
            execution_resource_observations,
        ),
        "integrity": integrity,
    }
    atomic_json(paths.manifest, updated)
    return updated


def summarize_resource_observations(
    observations: Sequence[Mapping[str, Any]],
    execution_observations: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any] | None:
    candidate_measured = [
        observation["resource_usage"]
        for observation in observations
        if isinstance(observation.get("resource_usage"), Mapping)
    ]
    invocation_measured = [
        observation["resource_usage"]
        for observation in execution_observations
        if isinstance(observation.get("resource_usage"), Mapping)
    ]
    measured = candidate_measured + invocation_measured
    if not measured:
        return None
    summary = {
        "measured_candidate_count": len(candidate_measured),
        "memory_total_gib": measured[0]["memory_total_gib"],
        "memory_used_peak_gib": max(
            item["memory_used_peak_gib"] for item in measured
        ),
        "memory_free_min_gib": min(
            item["memory_free_min_gib"] for item in measured
        ),
        "memory_peak_delta_from_baseline_max_gib": max(
            item["memory_peak_delta_from_baseline_gib"] for item in measured
        ),
        "gpu_utilization_peak_percent": max(
            item["gpu_utilization_peak_percent"] for item in measured
        ),
        "temperature_peak_celsius": max(
            item["temperature_peak_celsius"] for item in measured
        ),
        "power_draw_peak_watts": max(
            (
                item["power_draw_peak_watts"]
                for item in measured
                if item.get("power_draw_peak_watts") is not None
            ),
            default=None,
        ),
    }
    if invocation_measured:
        summary.update(
            {
                "measurement_scope": "concurrent_invocation",
                "measured_invocation_count": len(invocation_measured),
                "max_concurrency": max(
                    int(item.get("max_concurrency", 1))
                    for item in execution_observations
                ),
                "measured_candidate_count": len(
                    {
                        candidate_id
                        for item in execution_observations
                        for candidate_id in item.get(
                            "candidate_ids_recorded", []
                        )
                    }
                ),
            }
        )
    return summary

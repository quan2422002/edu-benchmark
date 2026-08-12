"""Run resumable Vertex AI native-dialogue smoke, pilot, or full batches."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import threading
import time
import traceback
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


import google.auth  # noqa: E402
from google.auth.transport.requests import Request as GoogleAuthRequest  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402
from tqdm import tqdm  # noqa: E402

from edu_benchmark.benchmark_evaluation.costing import (  # noqa: E402
    BudgetPolicy,
    TokenPricing,
    estimate_self_deployed_cost,
)
from edu_benchmark.benchmark_evaluation.config_builder import (  # noqa: E402
    PRINCIPLE_ORDER,
)
from edu_benchmark.benchmark_evaluation.provider_adapters import (  # noqa: E402
    to_gemini_request,
    to_openai_compatible_request,
)
from edu_benchmark.benchmark_evaluation.smoke import (  # noqa: E402
    PreparedTutorRequest,
    prepare_smoke_requests,
    prepare_tutor_requests,
)
from edu_benchmark.benchmark_evaluation.vertex_endpoint import (  # noqa: E402
    VertexRawPredictCaller,
    endpoint_id_from_resource,
    load_lifecycle_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
EXPERIMENT_ID = "20260727_170150"
PLAN_ID = "plan05"
PIPELINE_STAGE = "benchmark_evaluation_target_smoke"
EVALUATION_OUTPUT_ROOT = EXPERIMENT / "outputs/benchmark_evaluation"
SUCCESS_FINISH_REASONS = frozenset({"STOP", "END_TURN"})
TRUNCATED_FINISH_REASONS = frozenset(
    {"MAX_TOKENS", "LENGTH", "TOKEN_LIMIT"}
)


class ProviderCallError(RuntimeError):
    """Provider failure with structured retry and HTTP diagnostics."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool,
        http_status: int | None = None,
        response_body: str | None = None,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.http_status = http_status
        self.response_body = response_body
        self.retry_after_seconds = retry_after_seconds


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def portable_path(path: Path) -> str:
    """Prefer a repository-relative path for auditable manifests."""

    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    """Persist one diagnostic record immediately for crash-safe debugging."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _exception_diagnostic(
    *,
    exc: Exception,
    request: PreparedTutorRequest,
    attempt: int,
    max_attempts: int,
    retry_scheduled: bool,
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Build a self-contained error record without credentials or prompts."""

    return {
        "record_type": "api_call_error",
        "occurred_at": utc_now(),
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "pipeline_stage": PIPELINE_STAGE,
        "run_kind": getattr(args, "run_kind", "smoke"),
        "run_id": args.output_dir.name,
        "benchmark_candidate_id": request.benchmark_candidate_id,
        "provider": args.provider,
        "project": args.project,
        "location": args.location,
        "model": args.model,
        "attempt": attempt,
        "max_attempts": max_attempts,
        "retryable": getattr(exc, "retryable", True),
        "retry_scheduled": retry_scheduled,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "http_status": getattr(exc, "http_status", None),
        "response_body": getattr(exc, "response_body", None),
        "retry_after_seconds": getattr(exc, "retry_after_seconds", None),
        "traceback": "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
        "request_hash": request.request_hash,
    }


def _count_jsonl_records(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)


def _retry_delay_seconds(
    *,
    retry_index: int,
    base_seconds: float,
    max_seconds: float,
    jitter_seconds: float,
    seed: int,
    provider_retry_after_seconds: float | None = None,
) -> float:
    """Return deterministic exponential backoff with bounded jitter."""

    if retry_index < 1:
        raise ValueError("retry_index must be positive")
    exponential = min(
        max_seconds,
        base_seconds * (2 ** (retry_index - 1)),
    )
    jitter = random.Random(seed + retry_index).uniform(0, jitter_seconds)
    provider_hint = max(0.0, provider_retry_after_seconds or 0.0)
    return round(min(max_seconds, max(exponential + jitter, provider_hint)), 3)


def _load_resume_cost_and_history(
    manifest_path: Path,
) -> tuple[float, list[dict[str, Any]], dict[str, Any] | None]:
    """Load cumulative token cost and prior resume history."""

    if not manifest_path.exists():
        return 0.0, [], None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_cost = manifest.get("cumulative_estimated_cost_usd")
    if raw_cost is None:
        raw_cost = manifest.get("new_estimated_cost_usd")
    cost = float(raw_cost or 0)
    if cost < 0:
        raise RuntimeError("existing manifest has negative estimated cost")
    history = list(manifest.get("resume_history") or [])
    return cost, history, manifest


def _normalize_retry_after(value: str | None) -> float | None:
    """Parse a numeric Retry-After value; ignore unsupported HTTP dates."""

    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _normalize_finish_reason(value: Any) -> str:
    """Normalize provider-specific finish reasons for cross-model gates."""

    if value is None:
        return "UNKNOWN"
    name = getattr(value, "name", None)
    if isinstance(name, str) and name.strip():
        text = name
    else:
        raw_value = getattr(value, "value", value)
        text = str(raw_value)
    return text.rsplit(".", 1)[-1].strip().upper() or "UNKNOWN"


def _completion_state(finish_reason: str) -> tuple[str, str | None]:
    """Classify terminal output without asking a model to judge itself."""

    normalized = _normalize_finish_reason(finish_reason)
    if normalized in SUCCESS_FINISH_REASONS:
        return "completed", None
    if normalized in TRUNCATED_FINISH_REASONS:
        return "needs_review", "output_truncated"
    if normalized == "UNKNOWN":
        return "needs_review", "missing_finish_reason"
    return "needs_review", f"non_success_finish_reason:{normalized}"


def _validate_provider_model(provider: str, model: str) -> None:
    """Reject provider/model identifiers that the endpoint cannot resolve."""

    if provider != "openai-maas":
        return
    publisher, separator, model_name = model.partition("/")
    if (
        separator != "/"
        or not publisher.strip()
        or not model_name.strip()
        or "/" in model_name
    ):
        raise ValueError(
            "openai-maas --model must use the Vertex OpenAPI request "
            "identifier <publisher>/<model>; for Llama 4 Maverick use "
            "'meta/llama-4-maverick-17b-128e-instruct-maas'"
        )


def _load_candidate_ids_from_manifest(path: Path) -> tuple[str, ...]:
    """Load an exact prior smoke set for paired prompt comparisons."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        candidate_ids = data["candidate_ids"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid candidate manifest: {path}") from exc
    if (
        not isinstance(candidate_ids, list)
        or not candidate_ids
        or not all(
            isinstance(candidate_id, str) and candidate_id.strip()
            for candidate_id in candidate_ids
        )
        or len(candidate_ids) != len(set(candidate_ids))
    ):
        raise RuntimeError(
            "candidate manifest must contain unique non-empty candidate_ids"
        )
    return tuple(candidate_ids)


def _candidate_ids_with_issue(path: Path, issue: str) -> list[str]:
    """Return persisted candidates carrying one deterministic issue."""

    if not path.exists():
        return []
    return sorted(
        record["benchmark_candidate_id"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for record in [json.loads(line)]
        if record.get("completion_issue") == issue
    )


class GeminiCaller:
    """Thread-local Google Gen AI client for Gemini native contents."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        model: str,
        max_output_tokens: int,
        seed: int,
    ) -> None:
        self.project = project
        self.location = location
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.seed = seed
        self.credentials, _ = google.auth.default(
            quota_project_id=self.project
        )
        self.local = threading.local()
        self.clients: list[Any] = []
        self.lock = threading.Lock()

    def _client(self) -> Any:
        client = getattr(self.local, "client", None)
        if client is None:
            client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location,
                credentials=self.credentials,
                http_options=types.HttpOptions(
                    api_version="v1", timeout=120_000
                ),
            )
            self.local.client = client
            with self.lock:
                self.clients.append(client)
        return client

    def call(self, prepared: PreparedTutorRequest) -> dict[str, Any]:
        request = to_gemini_request(
            prepared.system_instruction, prepared.conversation.messages
        )
        config_kwargs: dict[str, Any] = {
            "system_instruction": request["system_instruction"],
            "max_output_tokens": self.max_output_tokens,
            "seed": self.seed,
        }
        if self.model.startswith("gemini-3.5"):
            config_kwargs["thinking_config"] = types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.MEDIUM,
                include_thoughts=True,
            )
        response = self._client().models.generate_content(
            model=self.model,
            contents=request["contents"],
            config=types.GenerateContentConfig(**config_kwargs),
        )
        candidates = getattr(response, "candidates", None) or []
        finish_reason = _normalize_finish_reason(
            getattr(candidates[0], "finish_reason", None)
            if candidates
            else None
        )
        try:
            response_text = response.text
        except (AttributeError, ValueError):
            response_text = ""
        if not isinstance(response_text, str) or not response_text.strip():
            raise RuntimeError(
                "Gemini returned an empty response "
                f"(finish_reason={finish_reason})"
            )
        usage = getattr(response, "usage_metadata", None)
        usage_dict = (
            usage.model_dump(mode="json", exclude_none=True)
            if usage is not None and hasattr(usage, "model_dump")
            else {}
        )
        return {
            "response_text": response_text,
            "response_id": str(getattr(response, "response_id", "") or ""),
            "model_version": str(
                getattr(response, "model_version", "") or ""
            ),
            "usage_metadata": usage_dict,
            "input_tokens": int(
                usage_dict.get("prompt_token_count", 0) or 0
            ),
            "output_tokens": int(
                (usage_dict.get("candidates_token_count", 0) or 0)
                + (usage_dict.get("thoughts_token_count", 0) or 0)
            ),
            "finish_reason": finish_reason,
        }

    def close(self) -> None:
        for client in self.clients:
            close = getattr(client, "close", None)
            if callable(close):
                close()


class OpenAIMaaSCaller:
    """ADC-authenticated OpenAI-compatible Vertex MaaS caller."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        model: str,
        max_output_tokens: int,
    ) -> None:
        self.project = project
        self.location = location
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            quota_project_id=self.project,
        )
        self.auth_lock = threading.Lock()

    def _token(self) -> str:
        with self.auth_lock:
            if not self.credentials.valid:
                self.credentials.refresh(GoogleAuthRequest())
            if not self.credentials.token:
                raise RuntimeError("ADC did not provide an access token")
            return self.credentials.token

    def call(self, prepared: PreparedTutorRequest) -> dict[str, Any]:
        native = to_openai_compatible_request(
            prepared.system_instruction, prepared.conversation.messages
        )
        payload = {
            "model": self.model,
            "messages": native["messages"],
            "max_tokens": self.max_output_tokens,
            "stream": False,
        }
        url = (
            f"https://{self.location}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{self.project}/locations/{self.location}/endpoints/"
            "openapi/chat/completions"
        )
        http_request = urllib_request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )
        try:
            with urllib_request.urlopen(http_request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            retryable = (
                exc.code in {408, 409, 425, 429} or 500 <= exc.code <= 599
            )
            retry_after = _normalize_retry_after(
                exc.headers.get("Retry-After") if exc.headers else None
            )
            raise ProviderCallError(
                f"Vertex MaaS HTTP {exc.code}: {body[:500]}",
                retryable=retryable,
                http_status=exc.code,
                response_body=body,
                retry_after_seconds=retry_after,
            ) from exc
        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("Vertex MaaS returned no choices")
        finish_reason = _normalize_finish_reason(
            choices[0].get("finish_reason")
        )
        text = choices[0].get("message", {}).get("content")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError(
                "Vertex MaaS returned an empty response "
                f"(finish_reason={finish_reason})"
            )
        usage = body.get("usage") or {}
        return {
            "response_text": text,
            "response_id": str(body.get("id") or ""),
            "model_version": str(body.get("model") or self.model),
            "usage_metadata": usage,
            "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "output_tokens": int(usage.get("completion_tokens", 0) or 0),
            "finish_reason": finish_reason,
        }

    def close(self) -> None:
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        choices=("gemini", "openai-maas", "vertex-endpoint"),
        required=True,
    )
    parser.add_argument("--project", default="edu-benchmark")
    parser.add_argument("--location", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--run-kind",
        choices=("smoke", "pilot", "recovery", "full"),
        default="smoke",
        help="Pilot/full runs require their locked candidate manifest.",
    )
    parser.add_argument(
        "--candidate-manifest",
        type=Path,
        help=(
            "Reuse candidate_ids from a prior smoke manifest for an exact "
            "paired comparison."
        ),
    )
    parser.add_argument("--max-candidates", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=20260728)
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
    parser.add_argument("--input-usd-per-million", type=float, required=True)
    parser.add_argument("--output-usd-per-million", type=float, required=True)
    parser.add_argument("--actual-spend-to-date-usd", type=float, default=56.0)
    parser.add_argument("--hard-budget-usd", type=float, default=250.0)
    parser.add_argument("--reserve-usd", type=float, default=25.0)
    parser.add_argument("--stage-cap-usd", type=float, default=20.0)
    parser.add_argument("--upper-bound-input-tokens", type=int, default=3000)
    parser.add_argument(
        "--endpoint-lifecycle-manifest",
        type=Path,
        help=(
            "Required for provider=vertex-endpoint. The manifest binds the "
            "smoke run to one live endpoint and its cleanup deadline."
        ),
    )
    parser.add_argument(
        "--endpoint-id",
        help=(
            "Optional numeric endpoint ID. When supplied, it must match the "
            "lifecycle manifest."
        ),
    )
    parser.add_argument(
        "--endpoint-runtime-upper-hours",
        type=float,
        default=0.5,
        help=(
            "Conservative runtime allowance charged to this smoke stage. "
            "This is not an automatic shutdown timer."
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
        "--analysis",
        type=Path,
        default=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/full_run_analysis.json"
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
        "--instruction-bundle",
        type=Path,
        default=(
            ROOT
            / "shared/prompts/benchmark_tutor_response_generation/"
            "instruction_bundle_v1.yaml"
        ),
    )
    parser.add_argument(
        "--execute-api",
        action="store_true",
        help="Required safety switch; without it only preflight is printed.",
    )
    return parser.parse_args()


def _prepare_vertex_endpoint_runtime(
    args: argparse.Namespace,
) -> dict[str, Any] | None:
    """Validate one live endpoint and return its bounded runtime metadata."""

    if args.provider != "vertex-endpoint":
        if args.endpoint_lifecycle_manifest or args.endpoint_id:
            raise ValueError(
                "endpoint arguments are only valid with "
                "--provider vertex-endpoint"
            )
        return None
    if args.endpoint_lifecycle_manifest is None:
        raise ValueError(
            "--endpoint-lifecycle-manifest is required for "
            "--provider vertex-endpoint"
        )
    if args.endpoint_runtime_upper_hours <= 0:
        raise ValueError("--endpoint-runtime-upper-hours must be positive")
    manifest = load_lifecycle_manifest(args.endpoint_lifecycle_manifest)
    for field, expected in (
        ("project", args.project),
        ("location", args.location),
        ("hf_model_id", args.model),
    ):
        if str(manifest[field]) != str(expected):
            raise RuntimeError(
                f"endpoint manifest {field}={manifest[field]!r} does not "
                f"match command value {expected!r}"
            )
    endpoint_id = endpoint_id_from_resource(
        str(manifest["endpoint_resource"])
    )
    if args.endpoint_id is not None:
        requested_endpoint_id = endpoint_id_from_resource(args.endpoint_id)
        if requested_endpoint_id != endpoint_id:
            raise RuntimeError(
                "--endpoint-id does not match the lifecycle manifest"
            )
    try:
        delete_by = datetime.fromisoformat(str(manifest["delete_by"]))
    except ValueError as exc:
        raise RuntimeError(
            "endpoint lifecycle manifest has invalid delete_by"
        ) from exc
    if delete_by.tzinfo is None:
        raise RuntimeError("endpoint delete_by must include a timezone")
    now = datetime.now(timezone.utc)
    if now >= delete_by:
        raise RuntimeError(
            "endpoint cleanup deadline has passed; do not start a new smoke"
        )
    seconds_remaining = (delete_by - now).total_seconds()
    requested_seconds = args.endpoint_runtime_upper_hours * 3600
    if requested_seconds > seconds_remaining:
        raise RuntimeError(
            "requested endpoint runtime allowance extends beyond delete_by"
        )
    try:
        hourly_price_usd = float(
            manifest["budget"]["hourly_price_usd"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "endpoint lifecycle manifest lacks hourly price"
        ) from exc
    return {
        "endpoint_id": endpoint_id,
        "lifecycle_manifest": portable_path(
            args.endpoint_lifecycle_manifest
        ),
        "deployed_model_id": str(manifest["deployed_model_id"]),
        "deployed_at": str(manifest.get("deployed_at") or ""),
        "delete_by": delete_by.isoformat(),
        "hourly_price_usd": hourly_price_usd,
        "runtime_upper_hours": args.endpoint_runtime_upper_hours,
        "runtime_cost_upper_bound_usd": estimate_self_deployed_cost(
            endpoint_hours=args.endpoint_runtime_upper_hours,
            hourly_price_usd=hourly_price_usd,
        ),
    }


def _load_existing_states(
    path: Path,
    *,
    instruction_bundle_version: str,
    instruction_bundle_sha256: str,
) -> tuple[set[str], set[str], set[str]]:
    if not path.exists():
        return set(), set(), set()
    recorded: set[str] = set()
    completed: set[str] = set()
    needs_review: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            if (
                record.get("instruction_bundle_version")
                != instruction_bundle_version
                or record.get("instruction_bundle_sha256")
                != instruction_bundle_sha256
            ):
                raise RuntimeError(
                    "existing smoke output uses a different instruction "
                    "bundle; choose a new --output-dir"
                )
            candidate_id = record["benchmark_candidate_id"]
            if candidate_id in recorded:
                raise RuntimeError(
                    f"duplicate smoke record for {candidate_id}"
                )
            recorded.add(candidate_id)
            response_status = record.get("response_status")
            if response_status == "completed":
                completed.add(candidate_id)
            elif response_status == "needs_review":
                needs_review.add(candidate_id)
            else:
                raise RuntimeError(
                    f"invalid response_status for {candidate_id}"
                )
    return recorded, completed, needs_review


def _validate_smoke_records(
    path: Path, expected_candidate_ids: set[str]
) -> dict[str, Any]:
    """Validate unique, schema-shaped incremental records."""

    if not path.exists():
        return {"validated": True, "record_count": 0}
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    candidate_ids = [row["benchmark_candidate_id"] for row in records]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError("smoke output contains duplicate candidate IDs")
    if not set(candidate_ids) <= expected_candidate_ids:
        raise RuntimeError("smoke output contains unexpected candidate IDs")
    for record in records:
        if record.get("record_type") != "target_response":
            raise RuntimeError("invalid smoke record_type")
        if record.get("experiment_id") != EXPERIMENT_ID:
            raise RuntimeError("invalid experiment_id")
        if record.get("plan_id") != PLAN_ID:
            raise RuntimeError("invalid plan_id")
        if record.get("pipeline_stage") != PIPELINE_STAGE:
            raise RuntimeError("invalid pipeline_stage")
        if not str(record.get("run_id", "")).strip():
            raise RuntimeError("invalid run_id")
        if not str(record.get("response_text", "")).strip():
            raise RuntimeError("smoke output contains an empty response")
        finish_reason = _normalize_finish_reason(record.get("finish_reason"))
        response_status, completion_issue = _completion_state(finish_reason)
        if record.get("finish_reason") != finish_reason:
            raise RuntimeError("finish_reason must be normalized")
        if record.get("response_status") != response_status:
            raise RuntimeError("response_status does not match finish_reason")
        if record.get("completion_issue") != completion_issue:
            raise RuntimeError("completion_issue does not match finish_reason")
        system_prompt = record.get("system_prompt")
        user_prompt = record.get("user_prompt")
        messages = record.get("conversation_messages")
        if not isinstance(system_prompt, str) or not system_prompt.strip():
            raise RuntimeError("invalid system_prompt")
        if not isinstance(user_prompt, str) or not user_prompt.strip():
            raise RuntimeError("invalid user_prompt")
        if (
            not isinstance(messages, list)
            or not messages
            or not all(
                isinstance(message, dict)
                and set(message) == {"role", "content"}
                and message["role"] in {"user", "assistant"}
                and isinstance(message["content"], str)
                and message["content"].strip()
                for message in messages
            )
        ):
            raise RuntimeError("invalid conversation_messages")
        if (
            messages[0]["role"] != "user"
            or messages[-1]["role"] != "user"
            or user_prompt != messages[-1]["content"]
        ):
            raise RuntimeError(
                "user_prompt must equal the final user message"
            )
        if any(
            left["role"] == right["role"]
            for left, right in zip(messages, messages[1:])
        ):
            raise RuntimeError("conversation message roles must alternate")
        if not str(record.get("instruction_bundle_version", "")).strip():
            raise RuntimeError("invalid instruction_bundle_version")
        for hash_field in (
            "input_hash",
            "system_instruction_hash",
            "messages_hash",
            "instruction_bundle_sha256",
        ):
            value = record.get(hash_field, "")
            if len(value) != 64 or any(
                character not in "0123456789abcdef" for character in value
            ):
                raise RuntimeError(f"invalid {hash_field}")
        expected_system_hash = hashlib.sha256(
            system_prompt.encode("utf-8")
        ).hexdigest()
        expected_messages_hash = hashlib.sha256(
            json.dumps(
                messages,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        expected_input_hash = hashlib.sha256(
            json.dumps(
                {
                    "system_instruction": system_prompt,
                    "messages": messages,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if record["system_instruction_hash"] != expected_system_hash:
            raise RuntimeError("system_prompt hash mismatch")
        if record["messages_hash"] != expected_messages_hash:
            raise RuntimeError("conversation_messages hash mismatch")
        if record["input_hash"] != expected_input_hash:
            raise RuntimeError("persisted request hash mismatch")
        required_principles = record.get("required_principle_ids")
        is_string_list = isinstance(required_principles, list) and all(
            isinstance(principle_id, str)
            for principle_id in required_principles
        )
        canonical_required = (
            [
                principle_id
                for principle_id in PRINCIPLE_ORDER
                if principle_id in set(required_principles)
            ]
            if is_string_list
            else []
        )
        if (
            not is_string_list
            or not required_principles
            or len(required_principles) != len(set(required_principles))
            or required_principles != canonical_required
        ):
            raise RuntimeError("invalid required_principle_ids")
        usage = record.get("usage", {})
        estimated_cost = usage.get("estimated_cost_usd")
        if (
            usage.get("input_tokens", -1) < 0
            or usage.get("output_tokens", -1) < 0
            or (
                estimated_cost is not None
                and (
                    not isinstance(estimated_cost, (int, float))
                    or estimated_cost < 0
                )
            )
        ):
            raise RuntimeError("invalid normalized usage")
        cost_basis = usage.get("cost_basis", "token_usage")
        if estimated_cost is None and cost_basis != "endpoint_runtime":
            raise RuntimeError(
                "null request cost is only valid for endpoint runtime billing"
            )
        if estimated_cost is not None and cost_basis not in {
            "token_usage",
            "legacy_token_usage",
        }:
            raise RuntimeError("invalid token-billed cost basis")
    return {
        "validated": True,
        "record_count": len(records),
        "completed_record_count": sum(
            record["response_status"] == "completed" for record in records
        ),
        "needs_review_record_count": sum(
            record["response_status"] == "needs_review"
            for record in records
        ),
    }


def main() -> int:
    global PIPELINE_STAGE
    args = parse_args()
    PIPELINE_STAGE = {
        "smoke": "benchmark_evaluation_target_smoke",
        "pilot": "benchmark_evaluation_target_pilot",
        "recovery": "benchmark_evaluation_target_full",
        "full": "benchmark_evaluation_target_full",
    }[args.run_kind]
    if not 1 <= args.concurrency <= 20:
        raise ValueError("target concurrency must be between 1 and 20")
    if args.max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    if (
        args.retry_backoff_base_seconds < 0
        or args.retry_backoff_max_seconds < args.retry_backoff_base_seconds
        or args.retry_jitter_seconds < 0
    ):
        raise ValueError("invalid retry backoff configuration")
    if args.run_kind == "smoke" and not 1 <= args.max_candidates <= 10:
        raise ValueError("smoke runs require 1–10 candidates")
    expected_locked_size = {"pilot": 80, "full": 1400}.get(
        args.run_kind
    )
    if expected_locked_size is not None and (
        args.max_candidates != expected_locked_size
        or args.candidate_manifest is None
    ):
        raise ValueError(
            f"{args.run_kind} runs require --max-candidates "
            f"{expected_locked_size} and --candidate-manifest"
        )
    _validate_provider_model(args.provider, args.model)
    endpoint_runtime = _prepare_vertex_endpoint_runtime(args)
    fixed_candidate_ids = (
        _load_candidate_ids_from_manifest(args.candidate_manifest)
        if args.candidate_manifest
        else None
    )
    if (
        fixed_candidate_ids is not None
        and len(fixed_candidate_ids) != args.max_candidates
    ):
        raise ValueError(
            "--max-candidates must equal the candidate count in "
            "--candidate-manifest"
        )
    prepare = (
        prepare_smoke_requests
        if args.run_kind == "smoke"
        else prepare_tutor_requests
    )
    prepared = prepare(
        grounding_pool_csv=args.grounding_pool,
        analysis_json=args.analysis,
        requirement_run_jsonl=args.requirement_run,
        instruction_bundle_path=args.instruction_bundle,
        max_candidates=args.max_candidates,
        seed=args.seed,
        fixed_candidate_ids=fixed_candidate_ids,
    )
    output_path = args.output_dir / (
        "run_smoke.jsonl"
        if args.run_kind == "smoke"
        else "run_responses.jsonl"
    )
    error_path = args.output_dir / "run_errors.jsonl"
    manifest_path = args.output_dir / "run_manifest.json"
    recorded, completed, needs_review = _load_existing_states(
        output_path,
        instruction_bundle_version=(
            prepared[0].instruction_bundle_version
        ),
        instruction_bundle_sha256=(
            prepared[0].instruction_bundle_sha256
        ),
    )
    pending = [
        request
        for request in prepared
        if request.benchmark_candidate_id not in recorded
    ]
    pending_at_start_ids = sorted(
        request.benchmark_candidate_id for request in pending
    )
    completed_before_run = len(completed)
    previous_cost, resume_history, existing_manifest = (
        _load_resume_cost_and_history(manifest_path)
    )
    if existing_manifest is not None:
        expected_resume_fields = {
            "provider": args.provider,
            "model": args.model,
            "candidate_ids_sha256": hashlib.sha256(
                "\n".join(
                    sorted(
                        request.benchmark_candidate_id
                        for request in prepared
                    )
                ).encode("utf-8")
            ).hexdigest(),
            "instruction_bundle_sha256": (
                prepared[0].instruction_bundle_sha256
            ),
        }
        for field, expected in expected_resume_fields.items():
            if existing_manifest.get(field) != expected:
                raise RuntimeError(
                    f"resume manifest {field} does not match current run"
                )

    pricing = TokenPricing(
        args.input_usd_per_million,
        args.output_usd_per_million,
    )
    if endpoint_runtime is None:
        per_attempt_upper = pricing.estimate(
            args.upper_bound_input_tokens, args.max_output_tokens
        )
        stage_upper = (
            len(pending) * (args.max_retries + 1) * per_attempt_upper
        )
        cost_basis = "token_usage"
    else:
        if (
            args.input_usd_per_million != 0
            or args.output_usd_per_million != 0
        ):
            raise ValueError(
                "self-deployed endpoint uses runtime billing; pass zero for "
                "both per-token prices"
            )
        stage_upper = endpoint_runtime["runtime_cost_upper_bound_usd"]
        cost_basis = "endpoint_runtime"
    if stage_upper > args.stage_cap_usd:
        raise RuntimeError(
            f"target-run upper bound ${stage_upper:.4f} exceeds stage cap "
            f"${args.stage_cap_usd:.2f}"
        )
    BudgetPolicy(
        hard_budget_usd=args.hard_budget_usd,
        reserve_usd=args.reserve_usd,
    ).assert_next_batch_allowed(
        actual_spend_usd=args.actual_spend_to_date_usd,
        next_batch_upper_bound_usd=stage_upper,
    )
    preflight = {
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "pipeline_stage": PIPELINE_STAGE,
        "run_kind": args.run_kind,
        "run_id": args.output_dir.name,
        "provider": args.provider,
        "project": args.project,
        "location": args.location,
        "model": args.model,
        "candidate_count": len(prepared),
        "candidate_ids": (
            [request.benchmark_candidate_id for request in prepared]
            if args.run_kind not in {"full", "recovery"}
            else None
        ),
        "candidate_ids_sha256": hashlib.sha256(
            "\n".join(
                sorted(
                    request.benchmark_candidate_id
                    for request in prepared
                )
            ).encode("utf-8")
        ).hexdigest(),
        "candidate_manifest": (
            portable_path(args.candidate_manifest)
            if args.candidate_manifest
            else None
        ),
        "candidate_manifest_sha256": (
            hashlib.sha256(args.candidate_manifest.read_bytes()).hexdigest()
            if args.candidate_manifest
            else None
        ),
        "max_retries": args.max_retries,
        "concurrency": args.concurrency,
        "retry_policy": {
            "backoff": "exponential_with_deterministic_jitter",
            "base_seconds": args.retry_backoff_base_seconds,
            "max_seconds": args.retry_backoff_max_seconds,
            "jitter_seconds": args.retry_jitter_seconds,
            "honor_numeric_retry_after": True,
        },
        "existing_record_count": len(recorded),
        "pending_request_count": len(pending),
        "previous_estimated_cost_usd": round(previous_cost, 8),
        "stage_upper_bound_usd": round(stage_upper, 6),
        "actual_spend_to_date_usd": args.actual_spend_to_date_usd,
        "hard_budget_usd": args.hard_budget_usd,
        "reserve_usd": args.reserve_usd,
        "cost_basis": cost_basis,
        "endpoint_runtime": endpoint_runtime,
        "execute_api": args.execute_api,
        "evaluation_output_root": portable_path(EVALUATION_OUTPUT_ROOT),
        "configuration_dir": portable_path(EVALUATION_OUTPUT_ROOT),
        "error_output_file": portable_path(
            args.output_dir / "run_errors.jsonl"
        ),
        "instruction_bundle_path": portable_path(args.instruction_bundle),
        "instruction_bundle_version": (
            prepared[0].instruction_bundle_version
        ),
        "instruction_bundle_sha256": (
            prepared[0].instruction_bundle_sha256
        ),
    }
    print(json.dumps(preflight, ensure_ascii=False, indent=2))
    if not args.execute_api:
        print("Preflight only. Add --execute-api to send Vertex AI requests.")
        return 0
    if not pending:
        if len(completed) == len(prepared) and not needs_review:
            print("Run is already complete; existing output was not modified.")
            return 0
        raise RuntimeError(
            "all candidates are recorded but incomplete; use a locked "
            "recovery workflow instead of resuming this run"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    caller: Any
    if args.provider == "gemini":
        caller = GeminiCaller(
            project=args.project,
            location=args.location,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            seed=args.seed,
        )
    elif args.provider == "openai-maas":
        caller = OpenAIMaaSCaller(
            project=args.project,
            location=args.location,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
        )
    else:
        assert endpoint_runtime is not None
        caller = VertexRawPredictCaller(
            project=args.project,
            location=args.location,
            endpoint_id=endpoint_runtime["endpoint_id"],
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            seed=args.seed,
            normalize_finish_reason=_normalize_finish_reason,
        )

    errors: dict[str, str] = {}
    terminal_failed: set[str] = set()
    new_cost = 0.0
    write_lock = threading.Lock()
    progress = tqdm(
        total=len(prepared),
        initial=len(completed),
        desc=f"Vertex {args.run_kind}",
        unit="mẫu",
        dynamic_ncols=True,
        leave=True,
    )
    progress.set_postfix(
        completed=len(completed),
        failed=0,
        review=len(needs_review),
        retry_pass=0,
        refresh=True,
    )
    last_attempt = 0

    def execute(request: PreparedTutorRequest) -> tuple[
        PreparedTutorRequest, dict[str, Any], float
    ]:
        started = time.monotonic()
        result = caller.call(request)
        latency = time.monotonic() - started
        result["latency_seconds"] = round(latency, 4)
        return request, result, pricing.estimate(
            result["input_tokens"], result["output_tokens"]
        )

    try:
        for attempt in range(args.max_retries + 1):
            if not pending:
                break
            last_attempt = attempt + 1
            retry_pending: list[PreparedTutorRequest] = []
            provider_retry_after_seconds = 0.0
            with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                future_map = {
                    executor.submit(execute, request): request
                    for request in pending
                }
                for future in as_completed(future_map):
                    request = future_map[future]
                    try:
                        request, result, cost = future.result()
                    except Exception as exc:
                        retryable = getattr(exc, "retryable", True)
                        retry_scheduled = (
                            retryable and attempt < args.max_retries
                        )
                        if retry_scheduled:
                            retry_pending.append(request)
                            retry_after = getattr(
                                exc, "retry_after_seconds", None
                            )
                            if retry_after is not None:
                                provider_retry_after_seconds = max(
                                    provider_retry_after_seconds,
                                    float(retry_after),
                                )
                        else:
                            terminal_failed.add(
                                request.benchmark_candidate_id
                            )
                            progress.update(1)
                        errors[request.benchmark_candidate_id] = (
                            f"{type(exc).__name__}: {exc}"
                        )
                        diagnostic = _exception_diagnostic(
                            exc=exc,
                            request=request,
                            attempt=attempt + 1,
                            max_attempts=args.max_retries + 1,
                            retry_scheduled=retry_scheduled,
                            args=args,
                        )
                        append_jsonl(error_path, diagnostic)
                        tqdm.write(
                            "[ERROR] "
                            f"candidate={request.benchmark_candidate_id} "
                            f"attempt={attempt + 1}/"
                            f"{args.max_retries + 1} "
                            f"retry={str(retry_scheduled).lower()} "
                            f"{type(exc).__name__}: {exc}"
                        )
                        tqdm.write(diagnostic["traceback"].rstrip())
                        tqdm.write(
                            f"[ERROR LOG] {portable_path(error_path)}"
                        )
                    else:
                        response_id = result["response_id"] or hashlib.sha256(
                            (
                                request.request_hash
                                + args.model
                                + result["response_text"]
                            ).encode("utf-8")
                        ).hexdigest()[:24]
                        record = {
                            "record_type": "target_response",
                            "created_at": utc_now(),
                            "experiment_id": EXPERIMENT_ID,
                            "plan_id": PLAN_ID,
                            "pipeline_stage": PIPELINE_STAGE,
                            "run_id": args.output_dir.name,
                            "benchmark_candidate_id": (
                                request.benchmark_candidate_id
                            ),
                            "provider": args.provider,
                            "model_id": args.model,
                            "model_version": result["model_version"],
                            "response_id": response_id,
                            "response_text": result["response_text"],
                            "finish_reason": result["finish_reason"],
                            "response_status": _completion_state(
                                result["finish_reason"]
                            )[0],
                            "completion_issue": _completion_state(
                                result["finish_reason"]
                            )[1],
                            **request.trace_fields(),
                            "usage": {
                                "input_tokens": result["input_tokens"],
                                "output_tokens": result["output_tokens"],
                                "estimated_cost_usd": (
                                    round(cost, 8)
                                    if endpoint_runtime is None
                                    else None
                                ),
                                "cost_basis": cost_basis,
                            },
                            "latency_seconds": result["latency_seconds"],
                            "attempt": attempt + 1,
                        }
                        with write_lock:
                            with output_path.open(
                                "a", encoding="utf-8"
                            ) as handle:
                                handle.write(
                                    json.dumps(record, ensure_ascii=False)
                                    + "\n"
                                )
                            recorded.add(request.benchmark_candidate_id)
                            if record["response_status"] == "completed":
                                completed.add(request.benchmark_candidate_id)
                            else:
                                needs_review.add(
                                    request.benchmark_candidate_id
                                )
                            new_cost += cost
                            errors.pop(request.benchmark_candidate_id, None)
                        progress.update(1)
                    progress.set_postfix(
                        completed=len(completed),
                        failed=len(terminal_failed) + len(retry_pending),
                        review=len(needs_review),
                        retry_pass=attempt + 1,
                        refresh=True,
                    )
            pending = retry_pending
            if pending and attempt < args.max_retries:
                delay = _retry_delay_seconds(
                    retry_index=attempt + 1,
                    base_seconds=args.retry_backoff_base_seconds,
                    max_seconds=args.retry_backoff_max_seconds,
                    jitter_seconds=args.retry_jitter_seconds,
                    seed=args.seed,
                    provider_retry_after_seconds=(
                        provider_retry_after_seconds
                    ),
                )
                tqdm.write(
                    "[RETRY WAIT] "
                    f"pending={len(pending)} delay_seconds={delay:.3f} "
                    f"next_attempt={attempt + 2}/"
                    f"{args.max_retries + 1}"
                )
                time.sleep(delay)
    finally:
        caller.close()
        progress.set_postfix(
            completed=len(completed),
            failed=len(terminal_failed) + len(pending),
            review=len(needs_review),
            retry_pass=last_attempt,
            refresh=True,
        )
        progress.close()

    failed_candidate_ids = terminal_failed | {
        request.benchmark_candidate_id for request in pending
    }
    if failed_candidate_ids:
        run_status = "completed_with_failures"
    elif needs_review:
        run_status = "completed_with_review"
    else:
        run_status = "completed"
    incremental_cost = round(new_cost, 8)
    cumulative_cost = round(previous_cost + new_cost, 8)
    if existing_manifest is not None:
        resume_history.append(
            {
                "resumed_at": utc_now(),
                "pending_candidate_count": len(pending_at_start_ids),
                "pending_candidate_ids_sha256": hashlib.sha256(
                    "\n".join(pending_at_start_ids).encode("utf-8")
                ).hexdigest(),
                "completed_candidate_count_before": completed_before_run,
                "completed_candidate_count_after": len(completed),
                "failed_candidate_count_after": len(failed_candidate_ids),
                "previous_estimated_cost_usd": round(previous_cost, 8),
                "incremental_estimated_cost_usd": incremental_cost,
                "cumulative_estimated_cost_usd": cumulative_cost,
                "concurrency": args.concurrency,
                "retry_policy": preflight["retry_policy"],
            }
        )
    manifest = {
        **preflight,
        "status": run_status,
        "generated_at": utc_now(),
        "recorded_candidate_ids": sorted(recorded),
        "completed_candidate_ids": sorted(completed),
        "needs_review_candidate_ids": sorted(needs_review),
        "truncated_candidate_ids": _candidate_ids_with_issue(
            output_path, "output_truncated"
        ),
        "failed_candidate_ids": sorted(failed_candidate_ids),
        "errors": errors,
        "error_file": portable_path(error_path) if error_path.exists() else None,
        "error_attempt_count": _count_jsonl_records(error_path),
        "previous_estimated_cost_usd": (
            round(previous_cost, 8) if endpoint_runtime is None else None
        ),
        "resume_increment_estimated_cost_usd": (
            incremental_cost if endpoint_runtime is None else None
        ),
        "new_estimated_cost_usd": (
            cumulative_cost if endpoint_runtime is None else None
        ),
        "cumulative_estimated_cost_usd": (
            cumulative_cost if endpoint_runtime is None else None
        ),
        "resume_history": resume_history,
        "endpoint_runtime_cost_upper_bound_usd": (
            None
            if endpoint_runtime is None
            else endpoint_runtime["runtime_cost_upper_bound_usd"]
        ),
        "output_file": portable_path(output_path),
        "integrity": _validate_smoke_records(
            output_path,
            {request.benchmark_candidate_id for request in prepared},
        ),
    }
    atomic_json(manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if not failed_candidate_ids and not needs_review else 2


if __name__ == "__main__":
    raise SystemExit(main())

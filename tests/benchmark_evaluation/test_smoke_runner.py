import hashlib
import json
from types import SimpleNamespace

import pytest

from scripts.benchmark_evaluation.run_vertex_smoke import (
    ProviderCallError,
    _count_jsonl_records,
    _completion_state,
    _exception_diagnostic,
    _load_resume_cost_and_history,
    _normalize_finish_reason,
    _normalize_retry_after,
    _retry_delay_seconds,
    _validate_provider_model,
    _validate_smoke_records,
    append_jsonl,
)
from edu_benchmark.benchmark_evaluation.smoke import PreparedTutorRequest
from edu_benchmark.benchmark_evaluation.dialogue_transport import (
    ChatMessage,
    NormalizedConversation,
)


def _record(candidate_id):
    system_prompt = "Bạn là gia sư."
    messages = [{"role": "user", "content": "Em cần giúp ạ."}]
    messages_hash = hashlib.sha256(
        json.dumps(
            messages,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    input_hash = hashlib.sha256(
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
    return {
        "record_type": "target_response",
        "experiment_id": "20260727_170150",
        "plan_id": "plan05",
        "pipeline_stage": "benchmark_evaluation_target_smoke",
        "run_id": "smoke-test",
        "benchmark_candidate_id": candidate_id,
        "response_text": "Phản hồi",
        "finish_reason": "STOP",
        "response_status": "completed",
        "completion_issue": None,
        "system_prompt": system_prompt,
        "user_prompt": "Em cần giúp ạ.",
        "conversation_messages": messages,
        "input_hash": input_hash,
        "system_instruction_hash": hashlib.sha256(
            system_prompt.encode("utf-8")
        ).hexdigest(),
        "messages_hash": messages_hash,
        "instruction_bundle_version": "v1",
        "instruction_bundle_sha256": "d" * 64,
        "required_principle_ids": ["PRINCIPLE-EXPLANATION"],
        "usage": {
            "input_tokens": 10,
            "output_tokens": 5,
            "estimated_cost_usd": 0.001,
        },
    }


def test_validate_smoke_records(tmp_path):
    output = tmp_path / "run_smoke.jsonl"
    output.write_text(
        json.dumps(_record("BC-1"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assert _validate_smoke_records(output, {"BC-1"}) == {
        "validated": True,
        "record_count": 1,
        "completed_record_count": 1,
        "needs_review_record_count": 0,
    }


def test_validate_endpoint_runtime_billed_record(tmp_path):
    output = tmp_path / "run_smoke.jsonl"
    record = _record("BC-1")
    record["provider"] = "vertex-endpoint"
    record["usage"] = {
        "input_tokens": 10,
        "output_tokens": 5,
        "estimated_cost_usd": None,
        "cost_basis": "endpoint_runtime",
    }
    output.write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assert _validate_smoke_records(output, {"BC-1"})["validated"] is True


def test_reject_null_cost_without_endpoint_runtime_basis(tmp_path):
    output = tmp_path / "run_smoke.jsonl"
    record = _record("BC-1")
    record["usage"]["estimated_cost_usd"] = None
    output.write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="endpoint runtime billing"):
        _validate_smoke_records(output, {"BC-1"})


def test_reject_duplicate_smoke_records(tmp_path):
    output = tmp_path / "run_smoke.jsonl"
    line = json.dumps(_record("BC-1"), ensure_ascii=False)
    output.write_text(f"{line}\n{line}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="duplicate"):
        _validate_smoke_records(output, {"BC-1"})


def test_finish_reason_normalization_and_truncation_gate():
    class FinishReason:
        name = "MAX_TOKENS"

    assert _normalize_finish_reason(FinishReason()) == "MAX_TOKENS"
    assert _normalize_finish_reason("length") == "LENGTH"
    assert _completion_state("STOP") == ("completed", None)
    assert _completion_state("MAX_TOKENS") == (
        "needs_review",
        "output_truncated",
    )
    assert _completion_state("length") == (
        "needs_review",
        "output_truncated",
    )


def test_openai_maas_model_requires_publisher_prefix():
    _validate_provider_model(
        "openai-maas",
        "meta/llama-4-maverick-17b-128e-instruct-maas",
    )
    with pytest.raises(ValueError, match="<publisher>/<model>"):
        _validate_provider_model(
            "openai-maas",
            "llama-4-maverick-17b-128e-instruct-maas",
        )


def test_gemini_model_does_not_require_publisher_prefix():
    _validate_provider_model("gemini", "gemini-3.5-flash")


def test_error_diagnostic_persists_http_exception_without_prompts(tmp_path):
    error_path = tmp_path / "run_errors.jsonl"
    request = PreparedTutorRequest(
        benchmark_candidate_id="BC-1",
        grade="6",
        required_principle_ids=("PRINCIPLE-EXPLANATION",),
        system_instruction="System secret-shaped content",
        system_instruction_hash="b" * 64,
        instruction_bundle_version="v2",
        instruction_bundle_sha256="d" * 64,
        conversation=NormalizedConversation(
            messages=(ChatMessage("user", "User prompt"),),
            sha256="c" * 64,
        ),
        request_hash="a" * 64,
    )
    exc = ProviderCallError(
        "Vertex MaaS HTTP 404",
        retryable=False,
        http_status=404,
        response_body='{"status":"NOT_FOUND"}',
        retry_after_seconds=12.5,
    )
    args = SimpleNamespace(
        output_dir=tmp_path / "run",
        provider="openai-maas",
        project="edu-benchmark",
        location="us-east5",
        model="meta/llama",
    )
    diagnostic = _exception_diagnostic(
        exc=exc,
        request=request,
        attempt=1,
        max_attempts=3,
        retry_scheduled=False,
        args=args,
    )
    append_jsonl(error_path, diagnostic)

    persisted = json.loads(error_path.read_text(encoding="utf-8"))
    assert persisted["benchmark_candidate_id"] == "BC-1"
    assert persisted["http_status"] == 404
    assert persisted["response_body"] == '{"status":"NOT_FOUND"}'
    assert persisted["retryable"] is False
    assert persisted["retry_scheduled"] is False
    assert persisted["retry_after_seconds"] == 12.5
    assert "ProviderCallError" in persisted["traceback"]
    assert "System secret-shaped content" not in persisted["traceback"]
    assert "User prompt" not in error_path.read_text(encoding="utf-8")
    assert _count_jsonl_records(error_path) == 1


def test_retry_delay_is_exponential_deterministic_and_bounded():
    first = _retry_delay_seconds(
        retry_index=1,
        base_seconds=15,
        max_seconds=60,
        jitter_seconds=5,
        seed=20260728,
    )
    assert 15 <= first <= 20
    assert first == _retry_delay_seconds(
        retry_index=1,
        base_seconds=15,
        max_seconds=60,
        jitter_seconds=5,
        seed=20260728,
    )
    provider_limited = _retry_delay_seconds(
        retry_index=2,
        base_seconds=15,
        max_seconds=60,
        jitter_seconds=5,
        seed=20260728,
        provider_retry_after_seconds=50,
    )
    assert provider_limited == 50
    assert _normalize_retry_after("12.5") == 12.5
    assert _normalize_retry_after("not-a-number") is None


def test_resume_cost_uses_cumulative_manifest_value(tmp_path):
    manifest = tmp_path / "run_manifest.json"
    manifest.write_text(
        json.dumps({
            "new_estimated_cost_usd": 0.2,
            "cumulative_estimated_cost_usd": 0.36434345,
            "resume_history": [{"pending_candidate_count": 86}],
        }),
        encoding="utf-8",
    )
    cost, history, loaded = _load_resume_cost_and_history(manifest)
    assert cost == 0.36434345
    assert history == [{"pending_candidate_count": 86}]
    assert loaded["new_estimated_cost_usd"] == 0.2


def test_validate_truncated_record_as_review_not_completed(tmp_path):
    output = tmp_path / "run_smoke.jsonl"
    record = _record("BC-1")
    record.update(
        {
            "finish_reason": "MAX_TOKENS",
            "response_status": "needs_review",
            "completion_issue": "output_truncated",
        }
    )
    output.write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assert _validate_smoke_records(output, {"BC-1"}) == {
        "validated": True,
        "record_count": 1,
        "completed_record_count": 0,
        "needs_review_record_count": 1,
    }


def test_reject_completed_status_for_truncated_record(tmp_path):
    output = tmp_path / "run_smoke.jsonl"
    record = _record("BC-1")
    record["finish_reason"] = "LENGTH"
    output.write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="response_status"):
        _validate_smoke_records(output, {"BC-1"})

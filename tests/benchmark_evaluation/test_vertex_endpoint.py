import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from scripts.benchmark_evaluation.run_vertex_smoke import (
    _normalize_finish_reason,
    _prepare_vertex_endpoint_runtime,
)
from edu_benchmark.benchmark_evaluation.vertex_endpoint import (
    endpoint_id_from_resource,
    load_lifecycle_manifest,
    parse_openai_chat_response,
)


MODEL_ID = "CogBase-USTC/Qwen2.5-Math-7B-Instruct-SocraticLM"


def _manifest(*, status="deployed", endpoint="123456789"):
    now = datetime.now(timezone.utc)
    return {
        "project": "edu-benchmark",
        "location": "us-central1",
        "hf_model_id": MODEL_ID,
        "endpoint_resource": (
            "projects/edu-benchmark/locations/us-central1/endpoints/"
            f"{endpoint}"
        ),
        "model_resource": (
            "projects/edu-benchmark/locations/us-central1/models/987654321"
        ),
        "deployed_model_id": "111222333",
        "deployed_at": now.isoformat(),
        "delete_by": (now + timedelta(hours=2)).isoformat(),
        "status": status,
        "budget": {"hourly_price_usd": 1.000416348},
    }


def _args(path, **overrides):
    values = {
        "provider": "vertex-endpoint",
        "endpoint_lifecycle_manifest": path,
        "endpoint_id": None,
        "endpoint_runtime_upper_hours": 0.5,
        "project": "edu-benchmark",
        "location": "us-central1",
        "model": MODEL_ID,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_endpoint_id_accepts_full_resource_or_numeric():
    assert endpoint_id_from_resource("123456789") == "123456789"
    assert (
        endpoint_id_from_resource(
            "projects/p/locations/us-central1/endpoints/123456789"
        )
        == "123456789"
    )
    with pytest.raises(ValueError, match="numeric"):
        endpoint_id_from_resource("not-an-endpoint")


def test_lifecycle_manifest_requires_live_endpoint(tmp_path):
    path = tmp_path / "lifecycle.json"
    path.write_text(json.dumps(_manifest()), encoding="utf-8")
    assert load_lifecycle_manifest(path)["status"] == "deployed"

    path.write_text(
        json.dumps(_manifest(status="cleanup_completed")), encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match="status='deployed'"):
        load_lifecycle_manifest(path)


def test_endpoint_runtime_binds_command_to_manifest(tmp_path):
    path = tmp_path / "lifecycle.json"
    path.write_text(json.dumps(_manifest()), encoding="utf-8")
    runtime = _prepare_vertex_endpoint_runtime(_args(path))
    assert runtime["endpoint_id"] == "123456789"
    assert runtime["runtime_upper_hours"] == 0.5
    assert runtime["runtime_cost_upper_bound_usd"] == pytest.approx(
        0.500208174
    )

    with pytest.raises(RuntimeError, match="does not match"):
        _prepare_vertex_endpoint_runtime(
            _args(path, project="different-project")
        )
    with pytest.raises(RuntimeError, match="does not match"):
        _prepare_vertex_endpoint_runtime(_args(path, endpoint_id="999"))


def test_endpoint_runtime_rejects_expired_manifest(tmp_path):
    manifest = _manifest()
    manifest["delete_by"] = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    ).isoformat()
    path = tmp_path / "lifecycle.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="deadline has passed"):
        _prepare_vertex_endpoint_runtime(_args(path))


def test_parse_openai_chat_response_normalizes_vllm_payload():
    result = parse_openai_chat_response(
        {
            "id": "chatcmpl-1",
            "model": MODEL_ID,
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "Gợi ý"},
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 20,
            },
        },
        fallback_model=MODEL_ID,
        normalize_finish_reason=_normalize_finish_reason,
    )
    assert result["response_text"] == "Gợi ý"
    assert result["finish_reason"] == "STOP"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 20

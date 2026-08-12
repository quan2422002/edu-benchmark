from argparse import Namespace
from pathlib import Path
import json
import threading
from types import SimpleNamespace

from scripts.benchmark_evaluation.run_claude_judge_smoke import (
    _retry_delay_seconds,
    call_one,
    failed_attempt_cost,
    load_completed,
    validate_records,
)
from edu_benchmark.benchmark_evaluation.judge import (
    PreparedJudgeRequest,
)
from edu_benchmark.benchmark_evaluation.gemini_judge import (
    GeminiJudgeCallError,
    GeminiVertexJudgeCaller,
)
from edu_benchmark.model_providers import (
    ModelResponse,
    ProviderCallError,
    TokenUsage,
)


class RetryableError(RuntimeError):
    retryable = True


class FlakyCaller:
    def __init__(self, text):
        self.calls = 0
        self.text = text

    def call(self, prepared):
        self.calls += 1
        if self.calls == 1:
            raise RetryableError("temporary")
        return {
            "response_text": self.text,
            "response_id": "judge-1",
            "model_version": "claude-sonnet-4-6",
            "finish_reason": "END_TURN",
            "input_tokens": 100,
            "output_tokens": 80,
            "usage_metadata": {},
        }


def prepared():
    return PreparedJudgeRequest(
        comparison_id="JUDGE-run-BC-1",
        benchmark_candidate_id="BC-1",
        target_run_id="run",
        target_response_id="target-1",
        target_model_id="target-model",
        required_principle_ids=("PRINCIPLE-EXPLANATION",),
        applicable_rubric_ids=("RUB-GEN-ACC",),
        rubric_name_to_id=(("Chính xác chuyên môn", "RUB-GEN-ACC"),),
        error_name_to_id=(("Sai nội dung", "ERR-WRONG-CONTENT"),),
        error_name_to_affected_rubric_ids=((
            "Sai nội dung", ("RUB-GEN-ACC",)
        ),),
        learning_evidence_fragment_ids=("LM-1",),
        response_1_source="target",
        response_2_source="reference",
        system_prompt="System",
        system_prompt_version="v2",
        system_prompt_sha256="a" * 64,
        user_prompt="User",
        request_sha256="b" * 64,
    )


def judge_json():
    return json.dumps(
        {
            "criterion_judgments": [
                {
                    "criterion_name": "Chính xác chuyên môn",
                    "winner": "response_1",
                    "confidence": 0.9,
                    "rationale": "Phản hồi 1 đúng; phản hồi 2 thiếu.",
                    "response_1_evidence": "Đúng chi tiết.",
                    "response_2_evidence": "Thiếu chi tiết.",
                }
            ],
            "serious_error_findings": [],
            "overall_judgment": {
                "winner": "response_1",
                "confidence": 0.85,
                "rationale": "Phản hồi 1 tốt hơn.",
            },
        },
        ensure_ascii=False,
    )


def test_retry_incremental_error_and_resume(tmp_path, monkeypatch):
    request = prepared()
    caller = FlakyCaller(judge_json())
    args = Namespace(
        max_retries=2,
        retry_backoff_base_seconds=2.0,
        retry_backoff_max_seconds=30.0,
        retry_jitter_seconds=1.0,
        seed=20260728,
        output_dir=tmp_path,
        provider="claude",
        project="edu-benchmark",
        location="us-east5",
        model="claude-sonnet-4-6",
        evaluation_schema=(
            Path(__file__).resolve().parents[2]
            / "experiments/20260727_170150/outputs/"
            "benchmark_evaluation/evaluation_schema.json"
        ),
    )
    delays = []
    monkeypatch.setattr(
        "scripts.benchmark_evaluation.run_claude_judge_smoke.time.sleep",
        delays.append,
    )
    error_path = tmp_path / "run_errors.jsonl"
    record = call_one(
        caller=caller,
        prepared=request,
        args=args,
        error_path=error_path,
        write_lock=threading.Lock(),
    )
    assert caller.calls == 2
    assert len(delays) == 1 and 2.0 <= delays[0] <= 3.0
    assert record["attempt"] == 2
    assert record["overall_judgment"]["target_judgment"] == "Win"
    assert record["raw_criterion_judgments"][0][
        "target_judgment"
    ] == "Win"
    assert record["adjusted_criterion_judgments"][0][
        "target_judgment"
    ] == "Win"
    errors = [
        json.loads(line)
        for line in error_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(errors) == 1 and errors[0]["retry_scheduled"] is True
    output = tmp_path / "run_judgments.jsonl"
    output.write_text(
        json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    completed = load_completed(
        output, {request.comparison_id: request}, args.model
    )
    assert validate_records(
        list(completed.values()), {request.comparison_id: request}
    )["validated"] is True


def test_gemini_judge_uses_native_prompts_and_medium_thinking():
    captured = {}

    class FakeProvider:
        backend = "vertex_ai"

        def generate(self, request):
            captured["request"] = request
            return ModelResponse(
                text=judge_json(),
                backend=self.backend,
                model=request.model,
                response_id="gemini-judge-1",
                model_version="gemini-3.5-flash",
                finish_reason="STOP",
                usage=TokenUsage(
                    input_tokens=100,
                    output_tokens=100,
                    total_tokens=200,
                    metadata={"prompt_token_count": 100},
                ),
            )

        def close(self):
            pass

    caller = GeminiVertexJudgeCaller(
        project="edu-benchmark",
        location="global",
        model="gemini-3.5-flash",
        max_output_tokens=3072,
        seed=20260728,
        thinking_level="MEDIUM",
        provider=FakeProvider(),
    )

    result = caller.call(prepared())

    request = captured["request"]
    assert request.model == "gemini-3.5-flash"
    assert request.messages[0].content == "User"
    assert request.system_instruction == "System"
    assert request.generation.thinking_level == "MEDIUM"
    assert request.structured_output.schema["properties"][
        "criterion_judgments"
    ]["minItems"] == len(prepared().rubric_name_to_id)
    assert request.structured_output.schema["properties"][
        "criterion_judgments"
    ]["items"]["properties"]["criterion_name"] == {"type": "string"}
    assert request.generation.temperature is None
    assert result["finish_reason"] == "STOP"
    assert result["output_tokens"] == 100


def test_gemini_judge_preserves_provider_retry_metadata():
    class FailingProvider:
        backend = "vertex_ai"

        @staticmethod
        def generate(request):
            raise ProviderCallError(
                "Temporary failure in name resolution",
                backend="vertex_ai",
                retryable=True,
            )

        @staticmethod
        def close():
            pass

    caller = GeminiVertexJudgeCaller(
        project="edu-benchmark",
        location="global",
        model="gemini-3.5-flash",
        max_output_tokens=8192,
        seed=20260728,
        thinking_level="MEDIUM",
        provider=FailingProvider(),
    )

    try:
        caller.call(prepared())
    except GeminiJudgeCallError as exc:
        assert exc.retryable is True
    else:
        raise AssertionError("DNS failure must be wrapped as retryable")


def test_retry_delay_is_deterministic_and_bounded():
    first = _retry_delay_seconds(
        attempt=1,
        comparison_id="JUDGE-1",
        seed=20260728,
        base_seconds=5.0,
        max_seconds=30.0,
        jitter_seconds=2.0,
    )
    repeated = _retry_delay_seconds(
        attempt=1,
        comparison_id="JUDGE-1",
        seed=20260728,
        base_seconds=5.0,
        max_seconds=30.0,
        jitter_seconds=2.0,
    )
    capped = _retry_delay_seconds(
        attempt=5,
        comparison_id="JUDGE-1",
        seed=20260728,
        base_seconds=5.0,
        max_seconds=30.0,
        jitter_seconds=2.0,
    )
    assert first == repeated
    assert 5.0 <= first <= 7.0
    assert capped == 30.0


class TruncatedCaller:
    def call(self, prepared):
        return {
            "response_text": "{\"incomplete\": true",
            "response_id": "judge-truncated",
            "model_version": "gemini-3.5-flash",
            "finish_reason": "MAX_TOKENS",
            "input_tokens": 200,
            "output_tokens": 3072,
            "usage_metadata": {"thoughts_token_count": 2000},
        }


def test_truncated_output_logs_usage_and_billed_cost(
    tmp_path, capsys
):
    request = prepared()
    args = Namespace(
        max_retries=2,
        output_dir=tmp_path,
        provider="gemini",
        project="edu-benchmark",
        location="global",
        model="gemini-3.5-flash",
        evaluation_schema=(
            Path(__file__).resolve().parents[2]
            / "experiments/20260727_170150/outputs/"
            "benchmark_evaluation/evaluation_schema.json"
        ),
    )
    error_path = tmp_path / "run_errors.jsonl"

    try:
        call_one(
            caller=TruncatedCaller(),
            prepared=request,
            args=args,
            error_path=error_path,
            write_lock=threading.Lock(),
        )
    except Exception as exc:
        assert "MAX_TOKENS" in str(exc)
    else:
        raise AssertionError("truncated output must fail closed")

    errors = [
        json.loads(line)
        for line in error_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(errors) == 1
    assert errors[0]["finish_reason"] == "MAX_TOKENS"
    assert errors[0]["usage"]["input_tokens"] == 200
    assert errors[0]["usage"]["output_tokens"] == 3072
    assert errors[0]["response_body"] == "{\"incomplete\": true"

    terminal = capsys.readouterr().out
    assert "[judge-error] Full diagnostic follows:" in terminal
    assert '"finish_reason": "MAX_TOKENS"' in terminal
    assert '"output_tokens": 3072' in terminal
    assert '"response_body": "{\\\"incomplete\\\": true"' in terminal
    assert '"traceback":' in terminal
    assert "JudgeOutputError: non-terminal finish reason MAX_TOKENS" in terminal

    class Pricing:
        @staticmethod
        def estimate(input_tokens, output_tokens):
            return input_tokens + output_tokens

    assert failed_attempt_cost(error_path, Pricing()) == 3272



def test_pilot_preparation_requires_80_candidates_per_target(monkeypatch):
    import scripts.benchmark_evaluation.run_claude_judge_smoke as runner

    captured = {}

    def fake_prepare(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(runner, "prepare_judge_requests", fake_prepare)
    path = Path("input")
    args = SimpleNamespace(
        candidate_csv=path,
        grounding_pool=path,
        conversion_input=path,
        learning_fragments=path,
        requirement_run=path,
        rubrics=path,
        serious_errors=path,
        target_runs=[path, path, path],
        system_prompt=path,
        seed=20260728,
        run_kind="pilot",
    )

    assert runner.prepare_from_args(args) == []
    assert captured["expected_candidates_per_run"] == 80
    assert captured["expected_target_run_count"] == 3


def test_full_preparation_requires_1400_candidates_per_target(monkeypatch):
    import scripts.benchmark_evaluation.run_claude_judge_smoke as runner

    captured = {}

    def fake_prepare(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(runner, "prepare_judge_requests", fake_prepare)
    path = Path("input")
    args = SimpleNamespace(
        candidate_csv=path,
        grounding_pool=path,
        conversion_input=path,
        learning_fragments=path,
        requirement_run=path,
        rubrics=path,
        serious_errors=path,
        target_runs=[path, path],
        system_prompt=path,
        seed=20260728,
        run_kind="full",
    )

    assert runner.prepare_from_args(args) == []
    assert captured["expected_candidates_per_run"] == 1400
    assert captured["expected_target_run_count"] == 2



def test_cost_pilot_preparation_uses_locked_30_candidate_manifest(
    monkeypatch, tmp_path
):
    import scripts.benchmark_evaluation.run_claude_judge_smoke as runner

    captured = {}

    def fake_prepare(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(runner, "prepare_judge_requests", fake_prepare)
    path = Path("input")
    candidate_ids = [f"BC-{index:02d}" for index in range(30)]
    manifest = tmp_path / "candidate_manifest.json"
    manifest.write_text(
        json.dumps({"candidate_ids": candidate_ids}),
        encoding="utf-8",
    )
    args = SimpleNamespace(
        candidate_csv=path,
        grounding_pool=path,
        conversion_input=path,
        learning_fragments=path,
        requirement_run=path,
        rubrics=path,
        serious_errors=path,
        target_runs=[path, path, path],
        system_prompt=path,
        candidate_manifest=manifest,
        seed=20260729,
        run_kind="cost-pilot",
    )

    assert runner.prepare_from_args(args) == []
    assert captured["expected_candidates_per_run"] == 30
    assert captured["expected_target_run_count"] == 3
    assert captured["fixed_candidate_ids"] == candidate_ids

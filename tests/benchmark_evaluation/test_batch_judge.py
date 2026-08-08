import json
from types import SimpleNamespace

from edu_benchmark.benchmark_evaluation import batch_judge
from edu_benchmark.benchmark_evaluation.batch_judge import (
    ParsedProviderResult,
    build_gemini_batch_line,
    build_judgment_record,
    build_openai_batch_line,
    empirical_cost_projection,
    parse_gemini_batch_output,
    parse_openai_batch_output,
    validate_judgment_records,
)
from edu_benchmark.benchmark_evaluation.judge import PreparedJudgeRequest


def prepared() -> PreparedJudgeRequest:
    return PreparedJudgeRequest(
        comparison_id="JUDGE-run-BC-1",
        benchmark_candidate_id="BC-1",
        target_run_id="run",
        target_response_id="target-1",
        target_model_id="target-model",
        required_principle_ids=("PRINCIPLE-EXPLANATION",),
        applicable_rubric_ids=("RUB-GEN-ACC",),
        rubric_name_to_id=(
            (
                "Chính xác chuyên môn và phù hợp đáp án chuẩn",
                "RUB-GEN-ACC",
            ),
        ),
        error_name_to_id=(),
        error_name_to_affected_rubric_ids=(),
        learning_evidence_fragment_ids=(),
        response_1_source="target",
        response_2_source="reference",
        system_prompt="System",
        system_prompt_version="v4",
        system_prompt_sha256="a" * 64,
        user_prompt="User",
        request_sha256="b" * 64,
        judge_output_contract_version="gold-answer-only-v4",
        include_serious_errors=False,
        include_learning_evidence=False,
    )


def judge_json() -> str:
    return json.dumps(
        {
            "criterion_judgments": [
                {
                    "criterion_name": (
                        "Chính xác chuyên môn và phù hợp đáp án chuẩn"
                    ),
                    "winner": "response_1",
                    "confidence": 0.9,
                    "rationale": "Phản hồi 1 chính xác hơn.",
                    "response_1_evidence": "Phù hợp đáp án.",
                    "response_2_evidence": "Thiếu chi tiết.",
                }
            ],
            "overall_judgment": {
                "winner": "response_1",
                "confidence": 0.8,
                "rationale": "Phản hồi 1 tốt hơn.",
            },
        },
        ensure_ascii=False,
    )


def test_batch_request_lines_preserve_contract_and_native_provider_shape():
    request = prepared()
    openai_line = build_openai_batch_line(
        request,
        model="gpt-5.4-mini-2026-03-17",
        max_output_tokens=8192,
        reasoning_effort="medium",
    )
    assert openai_line["custom_id"] == request.comparison_id
    assert openai_line["url"] == "/v1/responses"
    assert openai_line["body"]["instructions"] == "System"
    assert openai_line["body"]["input"] == "User"
    assert openai_line["body"]["store"] is False
    assert openai_line["body"]["text"]["format"]["strict"] is True

    gemini_line = build_gemini_batch_line(
        request,
        max_output_tokens=8192,
        seed=20260728,
        thinking_level="medium",
    )
    assert gemini_line["id"] == request.comparison_id
    body = gemini_line["request"]
    assert body["system_instruction"]["parts"][0]["text"] == "System"
    assert body["contents"][0]["parts"][0]["text"] == "User"
    assert body["generation_config"]["thinkingConfig"][
        "thinkingLevel"
    ] == "MEDIUM"


def test_parse_openai_batch_output(monkeypatch):
    class FakeResponse:
        @staticmethod
        def model_validate(body):
            assert body == {"fake": True}
            return SimpleNamespace(
                id="resp-1",
                model="gpt-5.4-mini-2026-03-17",
                status="completed",
                incomplete_details=None,
                output_text=judge_json(),
                output=[],
                usage=SimpleNamespace(
                    model_dump=lambda **_: {
                        "input_tokens": 100,
                        "output_tokens": 50,
                    }
                ),
            )

    monkeypatch.setattr(batch_judge, "OpenAIResponse", FakeResponse)
    comparison_id, result = parse_openai_batch_output(
        {
            "custom_id": prepared().comparison_id,
            "response": {
                "status_code": 200,
                "request_id": "req-1",
                "body": {"fake": True},
            },
            "error": None,
        }
    )
    assert comparison_id == prepared().comparison_id
    assert result.finish_reason == "STOP"
    assert result.input_tokens == 100
    assert result.provider_request_id == "req-1"


def test_parse_gemini_batch_output():
    comparison_id, result = parse_gemini_batch_output(
        {
            "id": prepared().comparison_id,
            "status": "",
            "response": {
                "responseId": "gemini-1",
                "modelVersion": "gemini-3.5-flash",
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {
                            "role": "model",
                            "parts": [{"text": judge_json()}],
                        },
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 100,
                    "candidatesTokenCount": 40,
                    "thoughtsTokenCount": 10,
                },
            },
        }
    )
    assert comparison_id == prepared().comparison_id
    assert result.finish_reason == "STOP"
    assert result.output_tokens == 50


def test_build_record_and_validate_gold_answer_only():
    request = prepared()
    record = build_judgment_record(
        prepared=request,
        provider_result=ParsedProviderResult(
            response_text=judge_json(),
            response_id="response-1",
            model_version="judge-model",
            finish_reason="STOP",
            input_tokens=100,
            output_tokens=50,
            usage_metadata={},
            provider_request_id="request-1",
        ),
        provider="openai",
        judge_model="judge-model",
        run_id="batch-run",
        evaluation_schema_sha256="c" * 64,
        batch_attempt=0,
        provider_job_name="batch-1",
    )
    assert record["overall_judgment"]["target_judgment"] == "Win"
    assert record["learning_evidence_included"] is False
    assert validate_judgment_records(
        [record],
        {request.comparison_id: request},
        judge_model="judge-model",
    ) == {"validated": True, "record_count": 1}


def test_empirical_projection_uses_nearest_rank_p95_and_safety():
    records = [
        {"usage": {"input_tokens": value, "output_tokens": 0}}
        for value in range(1, 101)
    ]
    projection = empirical_cost_projection(
        records,
        request_count=10,
        input_usd_per_million=1_000_000,
        output_usd_per_million=0,
        safety_multiplier=1.1,
    )
    assert projection["p95_usd_per_request"] == 95
    assert projection["projected_cost_usd"] == 1045

from dataclasses import replace
import json
from types import SimpleNamespace

from src.edu_benchmark.benchmark_evaluation.judge import (
    PreparedJudgeRequest,
)
from src.edu_benchmark.benchmark_evaluation.openai_judge import (
    OpenAIJudgeCaller,
    build_judge_response_schema,
)


def prepared() -> PreparedJudgeRequest:
    return PreparedJudgeRequest(
        comparison_id="JUDGE-1",
        benchmark_candidate_id="BC-1",
        target_run_id="target-run",
        target_response_id="response-id",
        target_model_id="target-model",
        required_principle_ids=("PRINCIPLE-EXPLANATION",),
        applicable_rubric_ids=("RUB-GEN-ACC", "RUB-EXP-CORE"),
        rubric_name_to_id=(
            ("Chính xác chuyên môn", "RUB-GEN-ACC"),
            ("Làm rõ nội dung cốt lõi", "RUB-EXP-CORE"),
        ),
        error_name_to_id=(
            ("Sai nội dung chuyên môn nghiêm trọng", "ERR-WRONG-CONTENT"),
        ),
        error_name_to_affected_rubric_ids=(
            (
                "Sai nội dung chuyên môn nghiêm trọng",
                ("RUB-GEN-ACC",),
            ),
        ),
        learning_evidence_fragment_ids=("FRAG-1",),
        response_1_source="target",
        response_2_source="reference",
        system_prompt="System",
        system_prompt_version="v2",
        system_prompt_sha256="a" * 64,
        user_prompt="User",
        request_sha256="b" * 64,
    )


def judge_json() -> str:
    return json.dumps(
        {
            "criterion_judgments": [
                {
                    "criterion_name": "Chính xác chuyên môn",
                    "winner": "response_1",
                    "confidence": 0.9,
                    "rationale": "Rationale",
                    "response_1_evidence": "Evidence 1",
                    "response_2_evidence": "Evidence 2",
                },
                {
                    "criterion_name": "Làm rõ nội dung cốt lõi",
                    "winner": "tie",
                    "confidence": 0.8,
                    "rationale": "Rationale",
                    "response_1_evidence": "Evidence 1",
                    "response_2_evidence": "Evidence 2",
                },
            ],
            "serious_error_findings": [],
            "overall_judgment": {
                "winner": "response_1",
                "confidence": 0.9,
                "rationale": "Overall rationale",
            },
        },
        ensure_ascii=False,
    )


def test_schema_uses_names_only_and_exact_criterion_count():
    schema = build_judge_response_schema(prepared())
    criteria = schema["properties"]["criterion_judgments"]
    assert criteria["minItems"] == criteria["maxItems"] == 2
    assert criteria["items"]["properties"]["criterion_name"]["enum"] == [
        "Chính xác chuyên môn",
        "Làm rõ nội dung cốt lõi",
    ]
    serialized = json.dumps(schema, ensure_ascii=False)
    assert "RUB-GEN-ACC" not in serialized
    assert "ERR-WRONG-CONTENT" not in serialized


def test_openai_caller_uses_responses_api_and_strict_schema():
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                id="resp-1",
                model="gpt-5.4-mini-2026-03-17",
                status="completed",
                incomplete_details=None,
                output_text=judge_json(),
                usage=SimpleNamespace(
                    model_dump=lambda **_: {
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "total_tokens": 150,
                    }
                ),
            )

    caller = OpenAIJudgeCaller.__new__(OpenAIJudgeCaller)
    caller.model = "gpt-5.4-mini-2026-03-17"
    caller.max_output_tokens = 8192
    caller.reasoning_effort = "medium"
    caller.client = SimpleNamespace(responses=FakeResponses())

    result = caller.call(prepared())

    assert captured["instructions"] == "System"
    assert captured["input"] == "User"
    assert captured["reasoning"] == {"effort": "medium"}
    assert captured["store"] is False
    assert captured["truncation"] == "disabled"
    assert "temperature" not in captured
    output_format = captured["text"]["format"]
    assert output_format["type"] == "json_schema"
    assert output_format["strict"] is True
    assert result["finish_reason"] == "STOP"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 50


def test_rubric_only_schema_omits_serious_error_output():
    request = replace(
        prepared(),
        error_name_to_id=(),
        error_name_to_affected_rubric_ids=(),
        judge_output_contract_version="rubric-only-v3",
        include_serious_errors=False,
    )
    schema = build_judge_response_schema(request)
    assert set(schema["properties"]) == {
        "criterion_judgments",
        "overall_judgment",
    }


def test_openai_caller_uses_distinct_gold_answer_only_v4_schema_name():
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                id="resp-v4",
                model="gpt-5.4-mini-2026-03-17",
                status="completed",
                incomplete_details=None,
                output_text=judge_json(),
                usage=SimpleNamespace(
                    model_dump=lambda **_: {
                        "input_tokens": 100,
                        "output_tokens": 50,
                    }
                ),
            )

    request = replace(
        prepared(),
        error_name_to_id=(),
        error_name_to_affected_rubric_ids=(),
        learning_evidence_fragment_ids=(),
        judge_output_contract_version="gold-answer-only-v4",
        include_serious_errors=False,
        include_learning_evidence=False,
    )
    caller = OpenAIJudgeCaller.__new__(OpenAIJudgeCaller)
    caller.model = "gpt-5.4-mini-2026-03-17"
    caller.max_output_tokens = 8192
    caller.reasoning_effort = "medium"
    caller.client = SimpleNamespace(responses=FakeResponses())

    caller.call(request)

    assert captured["text"]["format"]["name"] == (
        "blind_pairwise_judgment_gold_answer_only_v4"
    )


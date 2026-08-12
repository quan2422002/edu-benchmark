from dataclasses import replace
import json

from edu_benchmark.benchmark_evaluation.judge import (
    PreparedJudgeRequest,
)
from edu_benchmark.benchmark_evaluation.openai_judge import (
    OpenAIJudgeCaller,
    build_judge_response_schema,
)
from edu_benchmark.model_providers import ModelResponse, TokenUsage


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

    class FakeProvider:
        backend = "openai"

        def generate(self, request):
            captured["request"] = request
            return ModelResponse(
                text=judge_json(),
                backend=self.backend,
                model=request.model,
                response_id="resp-1",
                model_version="gpt-5.4-mini-2026-03-17",
                finish_reason="STOP",
                usage=TokenUsage(
                    input_tokens=100,
                    output_tokens=50,
                    total_tokens=150,
                ),
            )

        def close(self):
            pass

    caller = OpenAIJudgeCaller(
        api_key="unused-in-offline-test",
        model="gpt-5.4-mini-2026-03-17",
        max_output_tokens=8192,
        reasoning_effort="medium",
        provider=FakeProvider(),
    )

    result = caller.call(prepared())

    request = captured["request"]
    assert request.system_instruction == "System"
    assert request.messages[0].content == "User"
    assert request.generation.reasoning_effort == "medium"
    assert request.provider_options == {"store": False, "truncation": "disabled"}
    assert request.generation.temperature is None
    assert request.structured_output.strict is True
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

    class FakeProvider:
        backend = "openai"

        def generate(self, model_request):
            captured["request"] = model_request
            return ModelResponse(
                text=judge_json(),
                backend=self.backend,
                model=model_request.model,
                response_id="resp-v4",
                model_version="gpt-5.4-mini-2026-03-17",
                finish_reason="STOP",
                usage=TokenUsage(input_tokens=100, output_tokens=50),
            )

        def close(self):
            pass

    request = replace(
        prepared(),
        error_name_to_id=(),
        error_name_to_affected_rubric_ids=(),
        learning_evidence_fragment_ids=(),
        judge_output_contract_version="gold-answer-only-v4",
        include_serious_errors=False,
        include_learning_evidence=False,
    )
    caller = OpenAIJudgeCaller(
        api_key="unused-in-offline-test",
        model="gpt-5.4-mini-2026-03-17",
        max_output_tokens=8192,
        reasoning_effort="medium",
        provider=FakeProvider(),
    )

    caller.call(request)

    assert captured["request"].structured_output.name == (
        "blind_pairwise_judgment_gold_answer_only_v4"
    )

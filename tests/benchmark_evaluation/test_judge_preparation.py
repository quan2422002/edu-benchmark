from pathlib import Path
import json

import pytest

from src.edu_benchmark.benchmark_evaluation.judge import (
    GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES,
    JudgeOutputError,
    postprocess_judge_output,
    prepare_judge_requests,
    validate_judge_output,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
EVALUATION = EXPERIMENT / "outputs/benchmark_evaluation"


def prepare(
    judge_output_contract_version="v2",
    *,
    conversion_input_csv=None,
    learning_fragments_csv=None,
):
    prompt_name = {
        "v2": "system_prompt_v2.md",
        "rubric-only-v3": "system_prompt_rubric_only_v3.md",
        "gold-answer-only-v4": "system_prompt_gold_answer_only_v4.md",
    }[judge_output_contract_version]
    return prepare_judge_requests(
        candidate_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
        ),
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        conversion_input_csv=(
            conversion_input_csv
            or ROOT
            / "experiments/20260722_000940/outputs/"
            "benchmark_conversion/conversion_input_pass_samples.csv"
        ),
        learning_fragments_csv=(
            learning_fragments_csv
            or ROOT
            / "shared/learning_resources/fragments/"
            "learning_resource_fragments.csv"
        ),
        requirement_run_jsonl=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
        rubrics_csv=EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv",
        serious_errors_csv=(
            EXPERIMENT / "outputs/benchmark_rubric/serious_errors.csv"
        ),
        target_run_jsonls=[
            EVALUATION
            / "smoke_gemini35_instruction_v2/run_smoke.jsonl",
            EVALUATION
            / "smoke_llama4_maverick_instruction_v2_retry1/"
            "run_smoke.jsonl",
        ],
        system_prompt_path=(
            ROOT
            / "shared/prompts/benchmark_response_judging/"
            / prompt_name
        ),
        judge_output_contract_version=judge_output_contract_version,
    )



def test_prepare_three_target_configurations(tmp_path):
    third_dir = tmp_path / "target_gemini35_learnlm_prompted"
    third_dir.mkdir()
    third_run = third_dir / "run_responses.jsonl"
    third_run.write_text(
        (
            EVALUATION
            / "smoke_gemini35_instruction_v2/run_smoke.jsonl"
        ).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    requests = prepare_judge_requests(
        candidate_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
        ),
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        conversion_input_csv=(
            ROOT
            / "experiments/20260722_000940/outputs/"
            "benchmark_conversion/conversion_input_pass_samples.csv"
        ),
        learning_fragments_csv=(
            ROOT
            / "shared/learning_resources/fragments/"
            "learning_resource_fragments.csv"
        ),
        requirement_run_jsonl=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
        rubrics_csv=EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv",
        serious_errors_csv=(
            EXPERIMENT / "outputs/benchmark_rubric/serious_errors.csv"
        ),
        target_run_jsonls=[
            EVALUATION
            / "smoke_gemini35_instruction_v2/run_smoke.jsonl",
            EVALUATION
            / "smoke_llama4_maverick_instruction_v2_retry1/"
            "run_smoke.jsonl",
            third_run,
        ],
        system_prompt_path=(
            ROOT
            / "shared/prompts/benchmark_response_judging/"
            "system_prompt_v2.md"
        ),
        expected_candidates_per_run=10,
        expected_target_run_count=3,
    )
    assert len(requests) == 30
    assert len({row.benchmark_candidate_id for row in requests}) == 10
    assert len({row.target_run_id for row in requests}) == 3

def valid_output(
    criterion_names,
    error_name=None,
    *,
    response_1_detected=True,
    response_2_detected=True,
):
    findings = []
    if error_name:
        findings.append(
            {
                "error_name": error_name,
                "response_1": {
                    "detected": response_1_detected,
                    "confidence": 0.9,
                    "rationale": "Nhận định riêng cho phản hồi 1.",
                },
                "response_2": {
                    "detected": response_2_detected,
                    "confidence": 0.8,
                    "rationale": "Nhận định riêng cho phản hồi 2.",
                },
            }
        )
    return {
        "criterion_judgments": [
            {
                "criterion_name": name,
                "winner": "response_1",
                "confidence": 0.8,
                "rationale": "Phản hồi 1 cụ thể; phản hồi 2 chung hơn.",
                "response_1_evidence": "Có dấu hiệu cụ thể.",
                "response_2_evidence": "Thiếu chi tiết.",
            }
            for name in criterion_names
        ],
        "serious_error_findings": findings,
        "overall_judgment": {
            "winner": "response_1",
            "confidence": 0.75,
            "rationale": "Phản hồi 1 tốt hơn tổng thể.",
        },
    }


def normalize(request, output):
    return validate_judge_output(
        json.dumps(output, ensure_ascii=False),
        rubric_name_to_id=dict(request.rubric_name_to_id),
        error_name_to_id=dict(request.error_name_to_id),
        error_name_to_affected_rubric_ids=dict(
            request.error_name_to_affected_rubric_ids
        ),
    )


def test_prepare_exact_twenty_markdown_blind_comparisons():
    requests = prepare()
    assert len(requests) == 20
    assert len({row.benchmark_candidate_id for row in requests}) == 10
    assert all(row.system_prompt_version == "v2" for row in requests)
    assert all(
        {row.response_1_source, row.response_2_source}
        == {"target", "reference"}
        for row in requests
    )
    assert all(
        len(row.applicable_rubric_ids)
        == 4 + 3 * len(row.required_principle_ids)
        for row in requests
    )
    prompt = requests[0].user_prompt
    assert prompt.startswith("Hãy chấm mù")
    assert "# Dữ liệu đánh giá" in prompt
    assert "## Bối cảnh học tập" in prompt
    assert "### Câu hỏi nguồn" in prompt
    assert "### Đáp án chuyên môn" in prompt
    assert "### Lịch sử hội thoại" in prompt
    assert "## Căn cứ học liệu" in prompt
    assert "-----" in prompt
    assert "## Các tiêu chí phải áp dụng" in prompt
    assert "## Danh mục lỗi nghiêm trọng" in prompt
    assert "## Hai phản hồi" in prompt
    assert "gold_response" not in prompt
    assert "requirement_score" not in prompt
    for forbidden in (
        "rubric_id",
        "error_id",
        "RUB-",
        "ERR-",
        "position",
        "scope",
        "fragment_id",
        "material_type",
        "location_note",
        "suggested_action",
        "aggregation_rule",
    ):
        assert forbidden not in prompt
    assert all(row.target_model_id not in row.user_prompt for row in requests)
    assert requests[0].learning_evidence_fragment_ids
    assert [row.request_sha256 for row in requests] == [
        row.request_sha256 for row in prepare()
    ]


def test_names_map_back_to_ids_and_both_responses_may_share_error():
    request = prepare()[0]
    error_name = next(iter(dict(request.error_name_to_id)))
    normalized = normalize(
        request,
        valid_output(list(dict(request.rubric_name_to_id)), error_name),
    )
    assert {
        row["rubric_id"] for row in normalized["criterion_judgments"]
    } == set(request.applicable_rubric_ids)
    restored = postprocess_judge_output(
        normalized,
        response_1_source=request.response_1_source,
        response_2_source=request.response_2_source,
    )
    finding = restored["serious_error_findings"][0]
    assert set(finding["detected_sources"]) == {"target", "reference"}
    assert finding["affected_rubric_ids"]


@pytest.mark.parametrize(
    ("target_detected", "reference_detected", "expected"),
    [
        (False, False, None),
        (True, False, "Lose"),
        (False, True, "Win"),
        (True, True, "Lose"),
    ],
)
def test_serious_error_gate_four_branches(
    target_detected,
    reference_detected,
    expected,
):
    request = prepare()[0]
    error_name = next(iter(dict(request.error_name_to_id)))
    first_is_target = request.response_1_source == "target"
    response_1_detected = (
        target_detected if first_is_target else reference_detected
    )
    response_2_detected = (
        reference_detected if first_is_target else target_detected
    )
    output = valid_output(list(dict(request.rubric_name_to_id)))
    if target_detected or reference_detected:
        output = valid_output(
            list(dict(request.rubric_name_to_id)),
            error_name,
            response_1_detected=response_1_detected,
            response_2_detected=response_2_detected,
        )
    normalized = normalize(request, output)
    restored = postprocess_judge_output(
        normalized,
        response_1_source=request.response_1_source,
        response_2_source=request.response_2_source,
    )
    affected_id = dict(request.error_name_to_affected_rubric_ids)[
        error_name
    ][0]
    adjusted = {
        row["rubric_id"]: row["target_judgment"]
        for row in restored["adjusted_criterion_judgments"]
    }
    if expected is None:
        raw = {
            row["rubric_id"]: row["target_judgment"]
            for row in restored["raw_criterion_judgments"]
        }
        assert adjusted[affected_id] == raw[affected_id]
    else:
        assert adjusted[affected_id] == expected
    if target_detected or reference_detected:
        matching = [
            row
            for row in restored["criterion_adjustments"]
            if row["rubric_id"] == affected_id
        ]
        assert len(matching) == 1
    else:
        assert restored["criterion_adjustments"] == []


def test_missing_or_unknown_criterion_name_fails_closed():
    request = prepare()[0]
    names = list(dict(request.rubric_name_to_id))
    with pytest.raises(
        JudgeOutputError, match="criterion-name coverage mismatch"
    ):
        normalize(request, valid_output(names[:-1]))
    invalid = valid_output(names)
    invalid["criterion_judgments"][0]["criterion_name"] = "Tên tự tạo"
    with pytest.raises(JudgeOutputError, match="unknown criterion name"):
        normalize(request, invalid)



def test_prepare_filters_full_target_rows_by_fixed_candidate_ids(tmp_path):
    source_paths = [
        EVALUATION / "smoke_gemini35_instruction_v2/run_smoke.jsonl",
        EVALUATION
        / "smoke_llama4_maverick_instruction_v2_retry1/run_smoke.jsonl",
    ]
    first_rows = [
        json.loads(line)
        for line in source_paths[0].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fixed_ids = [row["benchmark_candidate_id"] for row in first_rows[:3]]
    requests = prepare_judge_requests(
        candidate_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
        ),
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        conversion_input_csv=(
            ROOT
            / "experiments/20260722_000940/outputs/"
            "benchmark_conversion/conversion_input_pass_samples.csv"
        ),
        learning_fragments_csv=(
            ROOT
            / "shared/learning_resources/fragments/"
            "learning_resource_fragments.csv"
        ),
        requirement_run_jsonl=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
        rubrics_csv=EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv",
        serious_errors_csv=(
            EXPERIMENT / "outputs/benchmark_rubric/serious_errors.csv"
        ),
        target_run_jsonls=source_paths,
        system_prompt_path=(
            ROOT
            / "shared/prompts/benchmark_response_judging/"
            "system_prompt_v2.md"
        ),
        expected_candidates_per_run=3,
        expected_target_run_count=2,
        fixed_candidate_ids=fixed_ids,
    )
    assert len(requests) == 6
    assert {row.benchmark_candidate_id for row in requests} == set(fixed_ids)


def test_rubric_only_v3_omits_serious_errors_and_keeps_compatibility():
    request = prepare("rubric-only-v3")[0]
    assert request.judge_output_contract_version == "rubric-only-v3"
    assert request.include_serious_errors is False
    assert request.error_name_to_id == ()
    assert request.error_name_to_affected_rubric_ids == ()
    assert "Danh mục lỗi nghiêm trọng" not in request.system_prompt
    assert "Danh mục lỗi nghiêm trọng" not in request.user_prompt
    assert "serious_error_findings" not in request.system_prompt

    output = valid_output(list(dict(request.rubric_name_to_id)))
    output.pop("serious_error_findings")
    normalized = validate_judge_output(
        json.dumps(output, ensure_ascii=False),
        rubric_name_to_id=dict(request.rubric_name_to_id),
        error_name_to_id={},
        error_name_to_affected_rubric_ids={},
        include_serious_errors=False,
    )
    restored = postprocess_judge_output(
        normalized,
        response_1_source=request.response_1_source,
        response_2_source=request.response_2_source,
    )
    assert restored["serious_error_findings"] == []
    assert restored["criterion_adjustments"] == []
    assert restored["adjusted_criterion_judgments"] == (
        restored["raw_criterion_judgments"]
    )


def test_gold_answer_only_alias_normalizes_to_canonical_name():
    canonical_name = "Mức chi tiết và cách diễn đạt phù hợp người học"
    alias_name = "Mức độ chi tiết và cách diễn đạt phù hợp người học"
    names = {canonical_name: "RUB-EXP-ADAPT"}
    output = valid_output([alias_name])
    output.pop("serious_error_findings")
    serialized = json.dumps(output, ensure_ascii=False)

    with pytest.raises(JudgeOutputError, match="unknown criterion name"):
        validate_judge_output(
            serialized,
            rubric_name_to_id=names,
            error_name_to_id={},
            error_name_to_affected_rubric_ids={},
            include_serious_errors=False,
        )

    normalized = validate_judge_output(
        serialized,
        rubric_name_to_id=names,
        error_name_to_id={},
        error_name_to_affected_rubric_ids={},
        include_serious_errors=False,
        criterion_name_aliases=(
            GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES
        ),
    )
    assert normalized["criterion_judgments"][0]["criterion_name"] == (
        canonical_name
    )


@pytest.mark.parametrize(
    ("alias_name", "canonical_name"),
    [
        (
            "Mức hỗ trợ vừa đủ và bảo toàn phần việc có ý nghĩa for học sinh",
            "Mức hỗ trợ vừa đủ và bảo toàn phần việc có ý nghĩa cho học sinh",
        ),
        (
            "Mẫu hỗ trợ chuyển giao thay việc làm thay",
            "Mẫu hỗ trợ chuyển giao thay vì làm thay",
        ),
        (
            "Phần biệt phần đúng, điểm cần cải thiện và ý nghĩa của chúng",
            "Phân biệt phần đúng, điểm cần cải thiện và ý nghĩa của chúng",
        ),
    ],
)
def test_observed_full_batch_aliases_normalize_to_canonical_name(
    alias_name,
    canonical_name,
):
    output = valid_output([alias_name])
    output.pop("serious_error_findings")
    normalized = validate_judge_output(
        json.dumps(output, ensure_ascii=False),
        rubric_name_to_id={canonical_name: "RUB-TEST"},
        error_name_to_id={},
        error_name_to_affected_rubric_ids={},
        include_serious_errors=False,
        criterion_name_aliases=GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES,
    )
    assert normalized["criterion_judgments"][0]["criterion_name"] == (
        canonical_name
    )


def test_gold_answer_only_v4_omits_fragments_and_redefines_accuracy(
    tmp_path,
):
    request = prepare(
        "gold-answer-only-v4",
        conversion_input_csv=tmp_path / "missing_conversion.csv",
        learning_fragments_csv=tmp_path / "missing_fragments.csv",
    )[0]
    names = dict(request.rubric_name_to_id)
    assert request.judge_output_contract_version == "gold-answer-only-v4"
    assert request.include_serious_errors is False
    assert request.include_learning_evidence is False
    assert request.learning_evidence_fragment_ids == ()
    assert request.trace_fields()["learning_evidence_included"] is False
    assert "## Căn cứ học liệu" not in request.system_prompt
    assert "## Căn cứ học liệu" not in request.user_prompt
    assert "fragment" not in request.system_prompt.lower()
    assert "fragment" not in request.user_prompt.lower()
    assert "### Đáp án chuyên môn" in request.user_prompt
    assert names["Chính xác chuyên môn và phù hợp đáp án chuẩn"] == (
        "RUB-GEN-ACC"
    )
    assert "Chính xác chuyên môn và có thể kiểm chứng" not in names
    accuracy_section = request.user_prompt.split(
        "### Chính xác chuyên môn và phù hợp đáp án chuẩn", 1
    )[1].split("\n### ", 1)[0]
    assert "chỉ dùng đáp án chuyên môn" in accuracy_section.lower()
    assert "chọn Tie" in accuracy_section

    output = valid_output(list(names))
    output.pop("serious_error_findings")
    normalized = validate_judge_output(
        json.dumps(output, ensure_ascii=False),
        rubric_name_to_id=names,
        error_name_to_id={},
        error_name_to_affected_rubric_ids={},
        include_serious_errors=False,
    )
    restored = postprocess_judge_output(
        normalized,
        response_1_source=request.response_1_source,
        response_2_source=request.response_2_source,
    )
    assert restored["serious_error_findings"] == []
    assert restored["criterion_adjustments"] == []

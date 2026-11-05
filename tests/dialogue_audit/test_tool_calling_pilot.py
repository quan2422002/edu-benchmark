from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

from edu_benchmark.dialogue_audit import agent_audit
from edu_benchmark.dialogue_audit.hnmu_audit import RawDialogueRow
from edu_benchmark.dialogue_audit.agent_audit import (
    CLUSTER_CRITERIA,
    MODEL_FORBIDDEN_FRAGMENT_FIELDS,
    AuditRetrievalAdapter,
    ClusterRecoverySpec,
    CriterionSpec,
    ModelClusterResult,
    PilotConfig,
    PilotContractError,
    PilotExecutionError,
    PilotOutputContractError,
    PilotOutputTruncatedError,
    SelectionRow,
    SelectionSourceQuota,
    _response_usage,
    _is_retryable_cluster_error,
    _sanitize_resume_result_rows,
    build_run_contract,
    build_cluster_prompt,
    evaluate_duplicate_cluster,
    evaluate_structure_cluster,
    extend_pilot_rows,
    extract_reference_body,
    model_output_schema,
    project_dialogue_for_model,
    read_jsonl,
    read_jsonl_recoverable_tail,
    run_cluster_recovery,
    run_gemini_cluster,
    run_pilot_split,
    select_pilot_rows,
    summarize_trace_metrics,
    trusted_filters,
    validate_cluster_recovery_inputs,
    validate_model_results,
)
from edu_benchmark.learning_resources.retrieval_api_v1 import RetrievalResult


def _row(
    sample_id: str = "S1",
    *,
    grade: str = "6",
    lesson: str = "Bài 1. Thông tin và dữ liệu",
    position: str = "Luyện tập trang 7 SGK",
    question: str = "Thông tin là gì?",
    answer_sgv: str = "Thông tin là hiểu biết.",
    dialogue: str = "HS: Em chưa hiểu.\nAI: Em hãy đọc ví dụ.\nHS: Em hiểu rồi.\nAI: Em hãy tóm tắt lại nhé.",
) -> RawDialogueRow:
    return RawDialogueRow(
        sample_id=sample_id,
        source_file="source.xlsx",
        source_row_number=2,
        grade=grade,
        grade_label=f"Lớp {grade}",
        stt="1",
        lesson=lesson,
        position=position,
        question=question,
        bloom_level="Thông hiểu",
        answer_sgv=answer_sgv,
        dialogue=dialogue,
    )


def _criteria() -> dict[str, CriterionSpec]:
    return {
        criterion_id: CriterionSpec(
            criterion_id=criterion_id,
            criterion_group="test",
            criterion_name=criterion_id,
            evidence_requirement="evidence",
            pass_condition="pass condition",
            fail_or_uncertain_policy="uncertain when ambiguous",
            default_reviewer_action="ask_hnmu_review",
        )
        for cluster in CLUSTER_CRITERIA.values()
        for criterion_id in cluster
    }


def _model_payload(criterion_ids: tuple[str, ...], evidence: list[str]) -> dict[str, object]:
    results = []
    for criterion_id in criterion_ids:
        row = {
                "criterion_id": criterion_id,
                "result": "pass",
                "confidence_score": 0.9,
                "evidence_fragment_ids": evidence,
                "evidence_match_reason": "Khớp nội dung.",
                "reason": "Tiêu chí đạt theo dữ liệu đã cung cấp.",
                "suggested_reviewer_action": "keep",
        }
        if criterion_id in CLUSTER_CRITERIA["B"]:
            if evidence:
                evidence_basis = "retrieved_fragment"
                evidence_basis_fields = ["retrieved_fragment"]
            elif criterion_id in agent_audit.CRITERIA_REQUIRING_FRAGMENT_FOR_PASS:
                evidence_basis = "insufficient_learning_resource"
                evidence_basis_fields = []
                row["result"] = "uncertain"
                row["suggested_reviewer_action"] = "ask_hnmu_review"
            else:
                evidence_basis = "raw_row_only"
                evidence_basis_fields = ["question", "dialogue"]
            row.update(
                {
                    "evidence_basis": evidence_basis,
                    "evidence_basis_fields": evidence_basis_fields,
                    "image_dependency": "none",
                    "image_dependency_reason": "Bằng chứng văn bản đã đủ.",
                    "needs_image_review": False,
                }
            )
        results.append(row)
    return {"results": results}


def _response(
    *,
    content,
    response_id: str,
    finish_reason: str = "STOP",
    usage_metadata=None,
):
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=content, finish_reason=finish_reason)],
        usage_metadata=usage_metadata,
        model_version="gemini-test",
        response_id=response_id,
    )


def test_response_usage_preserves_candidate_and_thinking_tokens() -> None:
    usage = _response_usage(
        SimpleNamespace(
            usage_metadata={
                "prompt_token_count": 100,
                "candidates_token_count": 40,
                "thoughts_token_count": 60,
                "tool_use_prompt_token_count": 7,
                "total_token_count": 200,
            }
        )
    )

    assert usage == {
        "input_tokens": 100,
        "candidate_tokens": 40,
        "thoughts_tokens": 60,
        "tool_use_prompt_tokens": 7,
        "output_tokens": 100,
        "total_tokens": 200,
    }


def test_max_tokens_preserves_raw_response_before_raising() -> None:
    truncated_text = '{"results":[{"criterion_id":"RAW-CON-05"'
    final_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=truncated_text, thought=False)]
    )
    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **_kwargs: _response(
                content=final_content,
                response_id="R-TRUNCATED",
                finish_reason="MAX_TOKENS",
                usage_metadata={
                    "prompt_token_count": 120,
                    "candidates_token_count": 90,
                    "thoughts_token_count": 934,
                    "total_token_count": 1144,
                },
            )
        )
    )
    traces: list[dict[str, object]] = []

    with pytest.raises(PilotOutputTruncatedError, match="finish_reason=MAX_TOKENS"):
        run_gemini_cluster(
            client=client,
            model="gemini-test",
            thinking_level="MEDIUM",
            max_output_tokens=1024,
            seed=20260903,
            system_instruction="SYSTEM",
            user_prompt="USER",
            prompt_sha256="prompt-hash",
            cluster_id="C",
            expected_ids=CLUSTER_CRITERIA["C"],
            retrieval_adapter=None,
            max_successful_tool_calls=3,
            max_total_tool_calls=8,
            trace_sink=traces.append,
        )

    final_event = next(
        event
        for event in traces
        if event["event_type"] == "model_final_response_received"
    )
    assert final_event["raw_text"] == truncated_text
    assert final_event["raw_text_length"] == len(truncated_text)
    assert final_event["finish_reason"] == "MAX_TOKENS"
    round_event = next(event for event in traces if event["event_type"] == "model_round")
    assert round_event["usage"]["candidate_tokens"] == 90
    assert round_event["usage"]["thoughts_tokens"] == 934


def test_cluster_contract_covers_exactly_18_unique_criteria() -> None:
    ids = [criterion_id for cluster in CLUSTER_CRITERIA.values() for criterion_id in cluster]
    assert len(ids) == 18
    assert len(set(ids)) == 18
    assert len(CLUSTER_CRITERIA["A"]) == 2
    assert len(CLUSTER_CRITERIA["F"]) == 2


def test_selection_is_deterministic_and_balanced() -> None:
    rows = [
        _row(
            f"G{grade}-{index}",
            grade=grade,
            lesson=f"Bài {index + 1}. Nội dung",
            position=("SGK" if index % 2 == 0 else "SGV"),
        )
        for grade in ("6", "7", "8", "9")
        for index in range(8)
    ]
    first = select_pilot_rows(
        rows,
        seed="locked-seed",
        samples_per_grade=4,
        development_per_grade=2,
    )
    second = select_pilot_rows(
        list(reversed(rows)),
        seed="locked-seed",
        samples_per_grade=4,
        development_per_grade=2,
    )
    assert first == second
    assert len(first) == 16
    assert {
        (grade, split): sum(1 for row in first if row.grade == grade and row.split == split)
        for grade in ("6", "7", "8", "9")
        for split in ("development", "holdout")
    } == {(grade, split): 2 for grade in ("6", "7", "8", "9") for split in ("development", "holdout")}


def test_extension_selection_preserves_base_and_uses_source_quotas() -> None:
    def sourced(sample_id: str, source: str, index: int) -> RawDialogueRow:
        row = _row(
            sample_id,
            grade="6",
            lesson=f"Bài {index}. Nội dung {sample_id}",
            position=f"SBT bài {index}",
            question=f"Câu hỏi duy nhất {sample_id}",
            dialogue=f"HS: Nội dung {sample_id}.\nAI: Phản hồi riêng {sample_id}.",
        )
        return RawDialogueRow(**{**row.to_dict(), "source_file": source})

    source = "round2-grade6.xlsx"
    rows = [
        sourced("BASE-DEV", "historical.xlsx", 1),
        sourced("BASE-HOLD", "historical.xlsx", 2),
        *(sourced(f"NEW-{index}", source, index + 3) for index in range(8)),
    ]
    base = [
        SelectionRow("BASE-DEV", "6", "development", 1, "BASE"),
        SelectionRow("BASE-HOLD", "6", "holdout", 2, "BASE"),
    ]
    selected = extend_pilot_rows(
        rows,
        base_selection=base,
        source_quotas=(SelectionSourceQuota(source, 2, 2, 1),),
        seed="v5-seed",
        near_threshold=1.0,
    )

    assert [(row.sample_id, row.split) for row in selected[:2]] == [
        ("BASE-DEV", "development"),
        ("BASE-HOLD", "holdout"),
    ]
    extension = selected[2:]
    assert Counter(row.split for row in extension) == {
        "development": 2,
        "holdout": 2,
        "reserve": 1,
    }
    assert all(row.source_file == source for row in extension)
    assert len({row.duplicate_group_id for row in selected}) == len(selected)


def test_dialogue_projection_is_readable_and_source_safe() -> None:
    raw = (
        "HS : Em hỏi.<br>Gia sư: [Gợi ý từng bước] Em thử nghĩ nhé."
        "AI: Bước tiếp theo."
    )
    projected = project_dialogue_for_model(raw)

    assert projected == (
        "HS: Em hỏi.\nAI: Em thử nghĩ nhé.\nAI: Bước tiếp theo."
    )
    assert "<br>" in raw
    assert project_dialogue_for_model(projected) == projected


def test_run_contract_changes_when_split_or_index_changes(tmp_path: Path) -> None:
    files = {
        name: tmp_path / name
        for name in (
            "rows.csv",
            "criteria.csv",
            "bloom.md",
            "scaffolding.md",
            "prompt.md",
            "index.sqlite",
            "selection.csv",
        )
    }
    for name, path in files.items():
        path.write_text(name, encoding="utf-8")
    config = PilotConfig(
        experiment_id="test",
        normalized_rows_path=files["rows.csv"],
        criteria_path=files["criteria.csv"],
        bloom_reference_path=files["bloom.md"],
        scaffolding_reference_path=files["scaffolding.md"],
        base_prompt_path=files["prompt.md"],
        retrieval_index_path=files["index.sqlite"],
        selection_path=files["selection.csv"],
        model="gemini-test",
        location="global",
        max_output_tokens=1024,
        seed=7,
        thinking_level="MEDIUM",
        timeout_seconds=30,
        include_tool_response_contract_in_prompt=True,
        max_successful_tool_calls_per_cluster=3,
        max_total_tool_calls_per_cluster=8,
        max_retries_per_cluster=3,
        retry_backoff_seconds=2,
        near_duplicate_threshold=0.96,
        selection_seed="seed",
        samples_per_grade=4,
        development_per_grade=2,
    )
    selection = [
        SelectionRow(
            sample_id="S1",
            grade="6",
            split="development",
            selection_order=1,
            diversity_bucket="SGK",
        )
    ]
    development = build_run_contract(config, split="development", selection=selection)
    holdout = build_run_contract(config, split="holdout", selection=selection)
    assert development["run_fingerprint"] != holdout["run_fingerprint"]

    files["index.sqlite"].write_text("changed index", encoding="utf-8")
    changed_index = build_run_contract(config, split="development", selection=selection)
    assert development["run_fingerprint"] != changed_index["run_fingerprint"]


def test_reference_extraction_and_cluster_prompt_do_not_leak_provenance_headers() -> None:
    cognitive = (
        "Trạng thái: draft\nNguồn: secret.docx\n## b) Từ ngữ\nNỘI DUNG BLOOM\n"
        "## Quy ước tối thiểu\nNhận biết được quy về Biết."
    )
    scaffolding = "Trạng thái: draft\nNguồn: secret.docx\n## I. Khung dàn giáo\nNỘI DUNG DÀN GIÁO\n## Tài liệu tham khảo\nEnd"
    bloom_body = extract_reference_body(
        cognitive,
        start_marker="## b) Từ ngữ",
        end_marker=None,
    )
    scaffold_body = extract_reference_body(
        scaffolding,
        start_marker="## I. Khung dàn giáo",
        end_marker="## Tài liệu tham khảo",
    )
    assert "draft" not in bloom_body
    assert "Nhận biết được quy về Biết" in bloom_body
    assert "secret.docx" not in scaffold_body

    system_c, user_c, _ = build_cluster_prompt(
        cluster_id="C",
        row=_row(),
        criteria=_criteria(),
        base_prompt="BASE",
        bloom_reference=bloom_body,
        scaffolding_reference=scaffold_body,
    )
    system_e, user_e, _ = build_cluster_prompt(
        cluster_id="E",
        row=_row(),
        criteria=_criteria(),
        base_prompt="BASE",
        bloom_reference=bloom_body,
        scaffolding_reference=scaffold_body,
    )
    assert "NỘI DUNG BLOOM" in system_c
    assert "NỘI DUNG DÀN GIÁO" not in system_c
    assert "NỘI DUNG BLOOM" not in system_e
    assert "NỘI DUNG DÀN GIÁO" not in system_e
    assert "source_file" not in user_c
    assert "source_file" not in user_e


def test_cluster_prompt_and_schema_lock_evidence_contract() -> None:
    system_b, _, _ = build_cluster_prompt(
        cluster_id="B",
        row=_row(),
        criteria=_criteria(),
        base_prompt="BASE",
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
    )
    system_c, _, _ = build_cluster_prompt(
        cluster_id="C",
        row=_row(),
        criteria=_criteria(),
        base_prompt="BASE",
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
    )
    normalized_system_b = " ".join(system_b.split())

    assert "Không gọi lại tool với cùng section_keywords" in system_b
    assert "Đọc status và matched_section_path" in system_b
    assert "không tự mở rộng lên section cha" in system_b
    assert "Hợp đồng phản hồi của công cụ" in system_b
    assert "status = budget_exhausted" in system_b
    assert "tool_budget.must_finalize = true" in system_b
    assert "mỗi trường reason tối đa 300 ký tự" in system_b
    assert "đúng sáu phần tử results" in system_b
    assert "giới hạn 8192 output token" in system_b
    assert "evidence_fragment_ids bắt buộc là []" in system_b
    assert "fragment đã truy xuất có liên quan nhưng yếu" in system_b
    assert "evidence_fragment_ids của mọi tiêu chí bắt buộc phải là []" in system_c
    cluster_b_item = model_output_schema("B")["properties"]["results"]["items"]
    cluster_b_results = model_output_schema("B")["properties"]["results"]
    evidence_b = cluster_b_item[
        "properties"
    ]["evidence_fragment_ids"]
    evidence_c = model_output_schema("C")["properties"]["results"]["items"][
        "properties"
    ]["evidence_fragment_ids"]
    assert "maxItems" not in evidence_b
    assert evidence_c["maxItems"] == 0
    assert cluster_b_item["properties"]["reason"]["maxLength"] == 300
    assert cluster_b_item["properties"]["evidence_match_reason"]["maxLength"] == 300
    assert cluster_b_results["minItems"] == 6
    assert cluster_b_results["maxItems"] == 6
    cluster_c_item = model_output_schema("C")["properties"]["results"]["items"]
    assert cluster_c_item["properties"]["reason"]["maxLength"] == 600
    assert cluster_b_item["properties"]["image_dependency"]["enum"] == [
        "none",
        "required",
        "supporting",
    ]
    assert "needs_image_review" in cluster_b_item["required"]
    assert "evidence_basis" in cluster_b_item["required"]
    assert "evidence_basis_fields" in cluster_b_item["required"]
    assert "kết luận pass bắt buộc" in normalized_system_b
    assert "mâu thuẫn" in system_b
    assert "evidence_basis=direct_internal_contradiction" in system_b
    assert "RAW-CON-03 được fail không fragment" in normalized_system_b
    assert "RAW-CON-04 có thể đánh giá quan hệ" in normalized_system_b
    assert "image_placeholder_count" in system_b
    assert "effective_content_length" in system_b
    assert "contains_image_placeholder" not in system_b

    system_e, _, _ = build_cluster_prompt(
        cluster_id="E",
        row=_row(),
        criteria=_criteria(),
        base_prompt="BASE",
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
    )
    assert "chỉ hỏi hội thoại có đủ dung lượng và nội dung" in system_e
    assert "Không dùng lỗi kiến thức" in system_e

    system_b_without_contract, _, _ = build_cluster_prompt(
        cluster_id="B",
        row=_row(),
        criteria=_criteria(),
        base_prompt="BASE",
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
        include_tool_response_contract=False,
    )
    assert "Hợp đồng phản hồi của công cụ" not in system_b_without_contract
    assert "tối đa 3 lần phản hồi có fragment" in system_b_without_contract


def test_shared_prompt_bundle_matches_locked_system_prompt_hashes() -> None:
    manifest_path = Path(
        "shared/prompts/hnmu_dialogue_audit/v1/manifest.json"
    )
    bundle = agent_audit.load_audit_prompt_bundle(manifest_path)
    criteria = agent_audit.load_criteria(
        Path("shared/benchmark/checklists/raw_dialogue/v1/criteria.csv")
    )
    bloom_reference = extract_reference_body(
        Path(
            "shared/learning_resources/agent_context/"
            "hnmu_cognitive_level_method_canonical.md"
        ).read_text(encoding="utf-8"),
        start_marker="## b) Từ ngữ",
        end_marker=None,
    )
    scaffolding_reference = extract_reference_body(
        Path(
            "shared/learning_resources/agent_context/"
            "hnmu_scaffolding_method_canonical.md"
        ).read_text(encoding="utf-8"),
        start_marker="## I. Khung dàn giáo",
        end_marker="## Tài liệu tham khảo",
    )
    expected = {
        "B": (12174, "7df4124bf811f05666f16ed312533698fed5e658ddb4b85a9b406f7202ca66ac"),
        "C": (11484, "fd6b30613f400abe7ff992abea312996d9eea9e69e234925a8a1d15ea35abfb1"),
        "D": (13341, "bb61eb9f4ca52f59cf8f42cf1bdc87bb92656cd0bd45e3786e88b3866656442e"),
        "E": (5035, "166a5d8b68dd3b8fdbf8beeff044c972a620493454f8651ddf3e7709fc53dd16"),
    }

    for cluster_id, (expected_length, expected_hash) in expected.items():
        system_prompt, _, _ = build_cluster_prompt(
            cluster_id=cluster_id,
            row=_row(),
            criteria=criteria,
            base_prompt=bundle.templates["common"],
            bloom_reference=bloom_reference,
            scaffolding_reference=scaffolding_reference,
            prompt_bundle=bundle,
        )
        assert len(system_prompt) == expected_length
        assert agent_audit.sha256_text(system_prompt) == expected_hash


def test_p03_a019_prompt_bundle_exposes_locked_regression_rules() -> None:
    bundle = agent_audit.load_audit_prompt_bundle(
        Path("shared/prompts/hnmu_dialogue_audit/v2/manifest.json")
    )
    system_b, user_b, _ = build_cluster_prompt(
        cluster_id="B",
        row=_row(
            lesson="Bài 6. Làm quen với phần mềm bảng tính",
            position="Hình 4.2, trang 42 SGK",
        ),
        criteria=_criteria(),
        base_prompt=bundle.templates["common"],
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
        prompt_bundle=bundle,
    )
    system_e, user_e, _ = build_cluster_prompt(
        cluster_id="E",
        row=_row(
            dialogue=(
                'HS: Dạ là "=D5E5" ạ.\n'
                "AI: Rất tốt! Em kéo công thức xuống nhé."
            ),
        ),
        criteria=_criteria(),
        base_prompt=bundle.templates["common"],
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
        prompt_bundle=bundle,
    )

    payload_b = json.loads(user_b)
    payload_e = json.loads(user_e)
    assert "PHẦN I — ĐỀ BÀI" in system_b
    assert "PHẦN II — HƯỚNG DẪN GIẢI" in system_b
    assert "metadata_scope_hints" in payload_b
    assert payload_b["metadata_scope_hints"]["direct_scope_conflict_candidate"]
    assert "pedagogical_error_hints" in payload_e
    assert payload_e["pedagogical_error_hints"][
        "explicit_wrong_answer_validation_candidate"
    ]
    assert "RAW-PED-04 phải fail" in system_e


def test_p03_a019_regression_spec_and_config_validate() -> None:
    config = PilotConfig.from_json(
        Path(
            "experiments/20260903_135547/configs/"
            "plan03-tool-calling-pilot-v5-4-regression.json"
        )
    )
    result = agent_audit.validate_pilot_inputs(config)

    assert result["selection_count"] == 10
    assert result["regression"]["scoped_cluster_count"] == 11
    assert result["regression"]["criterion_expectation_count"] == 11
    assert result["regression"]["image_expectation_count"] == 3
    with pytest.raises(PilotContractError, match="human-locked"):
        agent_audit.prepare_pilot(config, overwrite_selection=True)


def test_p03_a019_regression_evaluator_accepts_allowed_set_and_evidence() -> None:
    spec = agent_audit.load_regression_spec(
        Path(
            "experiments/20260903_135547/configs/"
            "plan03-development-v5-4-regression-spec.json"
        )
    )
    records = []
    for expectation in spec.criterion_expectations:
        evidence = list(expectation.required_evidence_fragment_ids)
        records.append(
            {
                "record_type": "criterion_result",
                "sample_id": expectation.sample_id,
                "criterion_id": expectation.criterion_id,
                "result": expectation.allowed_results[-1],
                "evidence_fragment_ids": evidence,
                "image_dependency": "none",
            }
        )
    for expectation in spec.image_expectations:
        for criterion_id, expected_dependency in (
            expectation.expected_dependency_by_criterion.items()
        ):
            records.append(
                {
                    "record_type": "criterion_result",
                    "sample_id": expectation.sample_id,
                    "criterion_id": criterion_id,
                    "result": "uncertain",
                    "evidence_fragment_ids": [],
                    "image_dependency": expected_dependency,
                }
            )

    result = agent_audit.evaluate_regression_results(records, spec)

    assert result["all_gates_passed"] is True
    assert result["passed_check_count"] == 29
    assert result["preferred_result_check_count"] == 1
    assert result["preferred_result_hit_count"] == 0


def test_p03_a020_prompt_config_and_regression_v2_validate() -> None:
    bundle = agent_audit.load_audit_prompt_bundle(
        Path("shared/prompts/hnmu_dialogue_audit/v3/manifest.json")
    )
    system_b, user_b, _ = build_cluster_prompt(
        cluster_id="B",
        row=_row(
            grade="7",
            lesson="Bài 8. Công cụ hỗ trợ tính toán",
            position="Bài tập 8.9 trang 41 SBT",
            question="Em hãy giải bài tập 8.9.",
        ),
        criteria=_criteria(),
        base_prompt=bundle.templates["common"],
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
        prompt_bundle=bundle,
    )
    payload = json.loads(user_b)

    assert "Một câu hỏi diễn đạt lại vẫn có thể pass RAW-CON-02" in system_b
    assert "dành một lượt có fragment cho phần giải" in system_b
    assert payload["sbt_retrieval_hints"]["exercise_numbers"] == ["8.9"]
    assert payload["sbt_retrieval_hints"]["question_section"] == "PHẦN I — ĐỀ BÀI"
    assert payload["sbt_retrieval_hints"]["solution_section"] == (
        "PHẦN II — HƯỚNG DẪN GIẢI"
    )

    config = PilotConfig.from_json(
        Path(
            "experiments/20260903_135547/configs/"
            "plan03-tool-calling-pilot-v5-5-regression.json"
        )
    )
    result = agent_audit.validate_pilot_inputs(config)
    assert config.max_output_repair_attempts == 1
    assert result["selection_count"] == 10
    assert result["regression"]["scoped_cluster_count"] == 11
    assert result["regression"]["criterion_expectation_count"] == 11
    assert result["regression"]["image_expectation_count"] == 3
    assert result["regression"]["image_criterion_expectation_count"] == 18


def test_p03_a021_prompt_config_and_image_policy_validate() -> None:
    bundle = agent_audit.load_audit_prompt_bundle(
        Path("shared/prompts/hnmu_dialogue_audit/v4/manifest.json")
    )
    system_b, _, _ = build_cluster_prompt(
        cluster_id="B",
        row=_row(position="Bài tập 8.9 trang 41 SBT"),
        criteria=_criteria(),
        base_prompt=bundle.templates["common"],
        bloom_reference="BLOOM",
        scaffolding_reference="SCAFFOLDING",
        prompt_bundle=bundle,
    )
    normalized = " ".join(system_b.split())

    assert "runtime vẫn khóa phạm vi về đúng tên section chuẩn" in normalized
    assert "`none` bắt buộc needs_image_review=false" in normalized
    assert "`supporting` mặc định needs_image_review=false" in normalized
    assert "`required` bắt buộc needs_image_review=true" in normalized

    config = PilotConfig.from_json(
        Path(
            "experiments/20260903_135547/configs/"
            "plan03-tool-calling-pilot-v5-6-regression.json"
        )
    )
    result = agent_audit.validate_pilot_inputs(config)
    assert config.max_output_repair_attempts == 1
    assert result["selection_count"] == 10
    assert result["regression"]["image_criterion_expectation_count"] == 18


def test_p03_a020_regression_reads_singular_evidence_and_criterion_image_matrix() -> None:
    spec = agent_audit.load_regression_spec(
        Path(
            "experiments/20260903_135547/configs/"
            "plan03-development-v5-5-regression-spec.json"
        )
    )
    records: list[dict[str, object]] = []
    for expectation in spec.criterion_expectations:
        record: dict[str, object] = {
            "record_type": "criterion_result",
            "sample_id": expectation.sample_id,
            "criterion_id": expectation.criterion_id,
            "result": expectation.allowed_results[-1],
            "image_dependency": "none",
        }
        if expectation.review_id == "REG-TGT-003":
            record["evidence_fragment_id"] = ";".join(
                (*expectation.required_evidence_fragment_ids, expectation.required_evidence_fragment_ids[0])
            ) + ";"
        else:
            record["evidence_fragment_ids"] = list(
                expectation.required_evidence_fragment_ids
            )
        records.append(record)
    by_key = {
        (str(row["sample_id"]), str(row["criterion_id"])): row
        for row in records
    }
    for expectation in spec.image_expectations:
        for criterion_id, dependency in (
            expectation.expected_dependency_by_criterion.items()
        ):
            key = (expectation.sample_id, criterion_id)
            by_key.setdefault(
                key,
                {
                    "record_type": "criterion_result",
                    "sample_id": expectation.sample_id,
                    "criterion_id": criterion_id,
                    "result": "uncertain",
                    "evidence_fragment_ids": [],
                },
            )["image_dependency"] = dependency

    result = agent_audit.evaluate_regression_results(list(by_key.values()), spec)
    target = next(
        row for row in result["criterion_checks"] if row["review_id"] == "REG-TGT-003"
    )
    assert target["passed"] is True
    assert target["actual_evidence_fragment_ids"] == [
        "OCR-SBT-TIN7-BAI08#V1_1F0019",
        "OCR-SBT-TIN7-BAI08#V1_1F0037",
    ]
    assert result["all_gates_passed"] is True
    assert result["image_criterion_check_count"] == 18
    assert result["passed_image_criterion_check_count"] == 18

    missing_records = [dict(row) for row in by_key.values()]
    missing_target = next(
        row
        for row in missing_records
        if row["sample_id"] == "HNMU-G7-R2-R0110-STT11"
        and row["criterion_id"] == "RAW-CON-02"
    )
    missing_target["evidence_fragment_id"] = "OCR-SBT-TIN7-BAI08#V1_1F0019"
    missing_result = agent_audit.evaluate_regression_results(missing_records, spec)
    missing_check = next(
        row
        for row in missing_result["criterion_checks"]
        if row["review_id"] == "REG-TGT-003"
    )
    assert missing_check["passed"] is False
    assert missing_check["failure_reasons"] == ["missing_required_evidence"]


def test_p03_a020_output_contract_repair_is_bounded_and_nonretryable_on_failure() -> None:
    invalid_payload = _model_payload(CLUSTER_CRITERIA["C"], [])
    for row in invalid_payload["results"]:
        row["confidence_score"] = 1.0
    repaired_payload = _model_payload(CLUSTER_CRITERIA["C"], [])

    class FakeModels:
        def __init__(self, second_payload):
            self.responses = [invalid_payload, second_payload]
            self.calls = 0
            self.requests: list[dict[str, object]] = []

        def generate_content(self, **kwargs):
            self.requests.append(kwargs)
            payload = self.responses[self.calls]
            self.calls += 1
            content = SimpleNamespace(
                parts=[
                    SimpleNamespace(
                        function_call=None,
                        text=json.dumps(payload, ensure_ascii=False),
                        thought=False,
                    )
                ]
            )
            return _response(content=content, response_id=f"R{self.calls}")

    success_models = FakeModels(repaired_payload)
    result = run_gemini_cluster(
        client=SimpleNamespace(models=success_models),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="C",
        expected_ids=CLUSTER_CRITERIA["C"],
        retrieval_adapter=None,
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
        max_output_repair_attempts=1,
    )
    assert success_models.calls == 2
    repair_request = json.loads(
        success_models.requests[1]["contents"][0].parts[0].text
    )
    assert "allowed_evidence_fragments" not in repair_request
    assert [
        event["event_type"]
        for event in result.trace_events
        if event["event_type"].startswith("output_repair")
    ] == ["output_repair_requested", "output_repair_response", "output_repair_succeeded"]

    failed_models = FakeModels(invalid_payload)
    with pytest.raises(PilotOutputContractError, match="repair failed") as error:
        run_gemini_cluster(
            client=SimpleNamespace(models=failed_models),
            model="gemini-test",
            thinking_level="MEDIUM",
            max_output_tokens=1024,
            seed=20260903,
            system_instruction="SYSTEM",
            user_prompt="USER",
            prompt_sha256="prompt-hash",
            cluster_id="C",
            expected_ids=CLUSTER_CRITERIA["C"],
            retrieval_adapter=None,
            max_successful_tool_calls=3,
            max_total_tool_calls=8,
            max_output_repair_attempts=1,
        )
    assert failed_models.calls == 2
    assert _is_retryable_cluster_error(error.value) is False

    valid_models = FakeModels(repaired_payload)
    valid_models.responses[0] = repaired_payload
    valid_result = run_gemini_cluster(
        client=SimpleNamespace(models=valid_models),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="C",
        expected_ids=CLUSTER_CRITERIA["C"],
        retrieval_adapter=None,
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
        max_output_repair_attempts=1,
    )
    assert valid_models.calls == 1
    assert not any(
        event["event_type"].startswith("output_repair")
        for event in valid_result.trace_events
    )


def test_p03_a021_evidence_repair_receives_only_visible_fragments() -> None:
    invalid_payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    invalid_payload["results"][0].update(
        {
            "evidence_fragment_ids": [],
            "evidence_basis": "retrieved_fragment",
            "evidence_basis_fields": ["retrieved_fragment"],
        }
    )
    repaired_payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    tool_call = SimpleNamespace(
        id="CALL-1",
        name="search_learning_fragments",
        args={
            "section_keywords": "Bài 1",
            "content_keywords": "thông tin",
            "material_types": ["SGK"],
        },
    )
    tool_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=tool_call, text=None, thought=False)]
    )

    def json_content(payload):
        return SimpleNamespace(
            parts=[
                SimpleNamespace(
                    function_call=None,
                    text=json.dumps(payload, ensure_ascii=False),
                    thought=False,
                )
            ]
        )

    class FakeModels:
        def __init__(self):
            self.responses = [
                tool_content,
                json_content(invalid_payload),
                json_content(repaired_payload),
            ]
            self.calls: list[dict[str, object]] = []

        def generate_content(self, **kwargs):
            self.calls.append(kwargs)
            return _response(
                content=self.responses.pop(0),
                response_id=f"R{len(self.calls)}",
            )

    def fake_search(section_keywords, content_keywords, **kwargs):
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"], "material_type": ["SGK"]},
            content_limit=5,
            matched_section_path="Bài 1",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(
                {
                    "fragment_id": "F1",
                    "grade": "6",
                    "material_type": "SGK",
                    "section_path": "Bài 1 > Khái niệm",
                    "markdown_text": "Thông tin đem lại hiểu biết cho con người.",
                    "content_score": -1.0,
                },
            ),
        )

    models = FakeModels()
    result = run_gemini_cluster(
        client=SimpleNamespace(models=models),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
        max_output_repair_attempts=1,
    )

    repair_request = json.loads(models.calls[2]["contents"][0].parts[0].text)
    assert repair_request["allowed_evidence_fragments"] == [
        {
            "fragment_id": "F1",
            "section_path": "Bài 1 > Khái niệm",
            "markdown_text": "Thông tin đem lại hiểu biết cho con người.",
            "image_placeholder_count": 0,
            "effective_content_length": agent_audit.effective_content_length(
                "Thông tin đem lại hiểu biết cho con người."
            ),
        }
    ]
    repair_event = next(
        event
        for event in result.trace_events
        if event["event_type"] == "output_repair_requested"
    )
    assert repair_event["allowed_evidence_fragments"] == repair_request[
        "allowed_evidence_fragments"
    ]


def test_p03_a021_sbt_runtime_canonicalizes_explicit_section_scope() -> None:
    searches: list[tuple[str, str]] = []

    def fake_search(section_keywords, content_keywords, **kwargs):
        searches.append((section_keywords, content_keywords))
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["7"], "material_type": ["SBT"]},
            content_limit=5,
            matched_section_path=section_keywords,
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(),
        )

    adapter = AuditRetrievalAdapter(
        row=_row(
            grade="7",
            lesson="Bài 8. Công cụ hỗ trợ tính toán",
            position="Bài tập 8.9 trang 41 SBT",
        ),
        index_path=Path("index.sqlite"),
        search_fn=fake_search,
    )
    first = adapter.execute(
        {
            "section_keywords": "PHẦN II — HƯỚNG DẪN GIẢI Bài 8",
            "content_keywords": "bài tập 8.9",
            "material_types": ["SBT"],
        }
    )
    repeated = adapter.execute(
        {
            "section_keywords": "PHẦN II — HƯỚNG DẪN GIẢI",
            "content_keywords": "bài tập 8.9",
            "material_types": ["SBT"],
        }
    )

    assert searches == [("PHẦN II — HƯỚNG DẪN GIẢI", "bài tập 8.9")]
    assert first.trace["arguments_from_model"]["section_keywords"].endswith("Bài 8")
    assert first.trace["effective_arguments"]["section_keywords"] == (
        "PHẦN II — HƯỚNG DẪN GIẢI"
    )
    assert first.trace["section_normalization_applied"] is True
    assert repeated.trace["cache_hit"] is True


def test_p03_a020_sbt_cluster_must_query_solution_section_before_finalizing() -> None:
    final_text = json.dumps(
        _model_payload(CLUSTER_CRITERIA["B"], ["F-SOLUTION"]),
        ensure_ascii=False,
    )
    premature_final = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=final_text, thought=False)]
    )
    solution_call = SimpleNamespace(
        id="CALL-SOLUTION",
        name="search_learning_fragments",
        args={
            "section_keywords": "PHẦN II — HƯỚNG DẪN GIẢI",
            "content_keywords": "bài tập 8.9",
            "material_types": ["SBT"],
        },
    )
    call_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=solution_call, text=None, thought=False)]
    )

    class FakeModels:
        def __init__(self):
            self.responses = [premature_final, call_content, premature_final]
            self.calls = 0

        def generate_content(self, **_kwargs):
            content = self.responses[self.calls]
            self.calls += 1
            return _response(content=content, response_id=f"R{self.calls}")

    searches: list[tuple[str, str]] = []

    def fake_search(section_keywords, content_keywords, **kwargs):
        searches.append((section_keywords, content_keywords))
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["7"], "material_type": ["SBT"]},
            content_limit=5,
            matched_section_path="Bài 8 > PHẦN II — HƯỚNG DẪN GIẢI",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(
                {
                    "fragment_id": "F-SOLUTION",
                    "grade": "7",
                    "material_type": "SBT",
                    "section_path": "Bài 8 > PHẦN II — HƯỚNG DẪN GIẢI",
                    "markdown_text": "Lời giải bài tập 8.9.",
                    "content_score": -1.0,
                },
            ),
        )

    models = FakeModels()
    result = run_gemini_cluster(
        client=SimpleNamespace(models=models),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(
                grade="7",
                lesson="Bài 8. Công cụ hỗ trợ tính toán",
                position="Bài tập 8.9 trang 41 SBT",
            ),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
    )

    assert models.calls == 3
    assert searches == [("PHẦN II — HƯỚNG DẪN GIẢI", "bài tập 8.9")]
    assert any(
        event["event_type"] == "sbt_solution_query_reminder"
        for event in result.trace_events
    )
    retrieval_event = next(
        event
        for event in result.trace_events
        if event["event_type"] == "retrieval_tool_call"
    )
    assert retrieval_event["sbt_solution_query_attempted"] is True
    assert retrieval_event["sbt_solution_query_succeeded"] is True


def test_p03_a020_sbt_reserves_last_successful_retrieval_for_solution() -> None:
    def tool_content(section: str, content_keyword: str):
        call = SimpleNamespace(
            id=f"CALL-{content_keyword}",
            name="search_learning_fragments",
            args={
                "section_keywords": section,
                "content_keywords": content_keyword,
                "material_types": ["SBT"],
            },
        )
        return SimpleNamespace(
            parts=[SimpleNamespace(function_call=call, text=None, thought=False)]
        )

    final_text = json.dumps(
        _model_payload(CLUSTER_CRITERIA["B"], ["F-SOLUTION"]),
        ensure_ascii=False,
    )
    final_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=final_text, thought=False)]
    )

    class FakeModels:
        def __init__(self):
            self.responses = [
                tool_content("PHẦN I — ĐỀ BÀI", "8.9"),
                tool_content("PHẦN I — ĐỀ BÀI", "hàm tính"),
                tool_content("PHẦN I — ĐỀ BÀI", "bảng tính"),
                tool_content("PHẦN II — HƯỚNG DẪN GIẢI", "8.9"),
                final_content,
            ]

        def generate_content(self, **_kwargs):
            return _response(content=self.responses.pop(0), response_id="R")

    searches: list[tuple[str, str]] = []

    def fake_search(section_keywords, content_keywords, **kwargs):
        searches.append((section_keywords, content_keywords))
        fragment_id = (
            "F-SOLUTION"
            if section_keywords == "PHẦN II — HƯỚNG DẪN GIẢI"
            else f"F-{len(searches)}"
        )
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["7"], "material_type": ["SBT"]},
            content_limit=5,
            matched_section_path=section_keywords,
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(
                {
                    "fragment_id": fragment_id,
                    "grade": "7",
                    "material_type": "SBT",
                    "section_path": section_keywords,
                    "markdown_text": content_keywords,
                    "content_score": -1.0,
                },
            ),
        )

    result = run_gemini_cluster(
        client=SimpleNamespace(models=FakeModels()),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(
                grade="7",
                lesson="Bài 8. Công cụ hỗ trợ tính toán",
                position="Bài tập 8.9 trang 41 SBT",
            ),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
    )

    assert searches == [
        ("PHẦN I — ĐỀ BÀI", "8.9"),
        ("PHẦN I — ĐỀ BÀI", "hàm tính"),
        ("PHẦN II — HƯỚNG DẪN GIẢI", "8.9"),
    ]
    assert result.tool_call_count == 3
    assert any(
        event["event_type"] == "sbt_solution_budget_reserved"
        for event in result.trace_events
    )


def test_prompt_bundle_rejects_hash_drift_and_unsafe_paths(tmp_path: Path) -> None:
    source_dir = Path("shared/prompts/hnmu_dialogue_audit/v1")
    manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"].values():
        relative_path = Path(entry["path"])
        (tmp_path / relative_path).write_bytes((source_dir / relative_path).read_bytes())
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (tmp_path / "cluster_e.md").write_text("changed", encoding="utf-8")
    with pytest.raises(PilotContractError, match="hash mismatch for cluster_e"):
        agent_audit.load_audit_prompt_bundle(manifest_path)

    manifest["files"]["common"]["path"] = "../common.md"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(PilotContractError, match="escapes bundle directory"):
        agent_audit.load_audit_prompt_bundle(manifest_path)


def test_run_contract_changes_when_prompt_bundle_component_changes(
    tmp_path: Path,
) -> None:
    source_dir = Path("shared/prompts/hnmu_dialogue_audit/v1")
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"].values():
        relative_path = Path(entry["path"])
        (bundle_dir / relative_path).write_bytes((source_dir / relative_path).read_bytes())
    manifest_path = bundle_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    files = {
        name: tmp_path / name
        for name in (
            "rows.csv",
            "criteria.csv",
            "bloom.md",
            "scaffolding.md",
            "index.sqlite",
            "selection.csv",
        )
    }
    for name, path in files.items():
        path.write_text(name, encoding="utf-8")
    config = PilotConfig(
        experiment_id="test",
        normalized_rows_path=files["rows.csv"],
        criteria_path=files["criteria.csv"],
        bloom_reference_path=files["bloom.md"],
        scaffolding_reference_path=files["scaffolding.md"],
        base_prompt_path=bundle_dir / "common.md",
        retrieval_index_path=files["index.sqlite"],
        selection_path=files["selection.csv"],
        model="gemini-test",
        location="global",
        max_output_tokens=1024,
        seed=7,
        thinking_level="MEDIUM",
        timeout_seconds=30,
        include_tool_response_contract_in_prompt=True,
        max_successful_tool_calls_per_cluster=3,
        max_total_tool_calls_per_cluster=8,
        max_retries_per_cluster=3,
        retry_backoff_seconds=2,
        near_duplicate_threshold=0.96,
        selection_seed="seed",
        samples_per_grade=4,
        development_per_grade=2,
        prompt_bundle_manifest_path=manifest_path,
    )
    selection = [SelectionRow("S1", "6", "development", 1, "SGK")]
    initial = build_run_contract(config, split="development", selection=selection)

    cluster_e_path = bundle_dir / "cluster_e.md"
    cluster_e_path.write_text(
        cluster_e_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    manifest["files"]["cluster_e"]["sha256"] = agent_audit.sha256_file(
        cluster_e_path
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    changed = build_run_contract(config, split="development", selection=selection)

    assert initial["run_fingerprint"] != changed["run_fingerprint"]
    assert (
        initial["input_hashes"]["prompt_bundle_cluster_e"]
        != changed["input_hashes"]["prompt_bundle_cluster_e"]
    )


def test_retrieval_adapter_calls_plan02_with_bound_filters_and_projects_fields() -> None:
    captured = {}
    calls = []

    def fake_search(section_keywords, content_keywords, **kwargs):
        calls.append((section_keywords, content_keywords, kwargs))
        captured.update(
            {
                "section_keywords": section_keywords,
                "content_keywords": content_keywords,
                **kwargs,
            }
        )
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"], "lesson_key": ["bai_01"], "material_type": ["SGK"]},
            content_limit=5,
            matched_section_path="Chủ đề > Bài 1",
            section_score=-2.0,
            snapshot_sha256="snapshot",
            results=(
                {
                    "fragment_id": "F1",
                    "grade": "6",
                    "material_type": "SGK",
                    "book_title": "Tin học 6",
                    "lesson_title": "Bài 1",
                    "section_path": "Chủ đề > Bài 1",
                    "markdown_text": "# Mục\n\n![](image.png)\n\nNội dung",
                    "content_score": -1.0,
                    "status": "draft",
                    "needs_hnmu_review": "true",
                    "source_markdown_path": "secret.md",
                    "page_start": "7",
                    "fragment_release": "v1.1",
                    "merge_status": "merged",
                    "merge_reason": "short_table_absorption",
                    "merge_policy_version": "fragment-v1.1-iterative-bounded-v1",
                    "merged_from_fragment_ids_json": '["V1F1", "V1F2"]',
                    "merged_from_fragment_count": 2,
                    "source_fragment_types_json": '["text", "table"]',
                    "source_fragment_index_start": 1,
                    "source_fragment_index_end": 2,
                    "merge_contract_sha256": "contract-hash",
                },
            ),
        )

    row = _row()
    adapter = AuditRetrievalAdapter(
        row=row,
        index_path=Path("index.sqlite"),
        search_fn=fake_search,
    )
    result = adapter.execute(
        {
            "section_keywords": "Bài 1 dữ liệu",
            "content_keywords": "khái niệm thông tin",
            "material_types": ["SBT"],
        }
    )

    assert captured["filters"] == trusted_filters(row)
    assert captured["content_limit"] == 5
    assert result.visible_response["status"] == "success"
    assert result.visible_response["matched_section_path"] == "Chủ đề > Bài 1"
    assert result.visible_response["fragments"][0]["rank"] == 1
    assert "contains_image_placeholder" not in result.visible_response["fragments"][0]
    assert result.visible_response["fragments"][0]["image_placeholder_count"] == 1
    assert result.visible_response["fragments"][0]["effective_content_length"] == 8
    assert "book_title" not in result.visible_response["fragments"][0]
    assert "lesson_title" not in result.visible_response["fragments"][0]
    assert not MODEL_FORBIDDEN_FRAGMENT_FIELDS.intersection(
        result.visible_response["fragments"][0]
    )
    assert result.trace["index_snapshot_sha256"] == "snapshot"
    assert result.trace["ranked_results"][0]["source_fragment_count"] == 2
    assert result.trace["ranked_results"][0]["source_fragment_types"] == [
        "text",
        "table",
    ]
    assert result.trace["ranked_results"][0]["contains_table_source"] is True
    assert "contains_image_placeholder" not in result.trace["ranked_results"][0]
    assert result.trace["ranked_results"][0]["image_placeholder_count"] == 1
    assert result.trace["ranked_results"][0]["effective_content_length"] == 8
    repeated = adapter.execute(
        {
            "section_keywords": "  BÀI 1.  DỮ LIỆU ",
            "content_keywords": "KHÁI NIỆM,  THÔNG TIN.",
            "material_types": ["SBT"],
        }
    )
    assert len(calls) == 1
    assert repeated.visible_response["status"] == "repeated_query"
    assert repeated.visible_response["previous_status"] == "success"
    assert repeated.trace["cache_hit"] is True
    assert repeated.trace["result_count"] == 1


def test_retrieval_adapter_exposes_empty_result_reason_and_matched_section() -> None:
    def fake_search(section_keywords, content_keywords, **kwargs):
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"]},
            content_limit=5,
            matched_section_path="Chủ đề > Bài 1",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(),
            reason="content_no_match",
        )

    result = AuditRetrievalAdapter(
        row=_row(),
        index_path=Path("index.sqlite"),
        search_fn=fake_search,
    ).execute(
        {
            "section_keywords": "Bài 1",
            "content_keywords": "từ khóa chưa khớp",
        }
    )

    assert result.visible_response["status"] == "content_no_match"
    assert result.visible_response["matched_section_path"] == "Chủ đề > Bài 1"
    assert result.visible_response["fragments"] == []
    assert result.visible_response["image_evidence_context"] == {
        "raw_row_signals": {},
        "returned_fragments": [],
        "summary": {
            "fragment_count": 0,
            "fragments_with_image_placeholder": 0,
            "fragments_with_effective_text": 0,
            "total_image_placeholder_count": 0,
        },
        "instruction": (
            "Các số liệu chỉ mô tả bằng chứng đã trả; tự đánh giá riêng từng "
            "tiêu chí bằng phép thử bỏ pixel ảnh."
        ),
    }


def test_model_result_rejects_fragment_not_seen_in_tool_trace() -> None:
    with pytest.raises(PilotContractError, match="absent from tool trace"):
        validate_model_results(
            _model_payload(CLUSTER_CRITERIA["B"], ["INVENTED"]),
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
        )


def test_cluster_b_requires_evidence_match_reason() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    payload["results"][0]["evidence_match_reason"] = ""

    with pytest.raises(PilotContractError, match="Missing evidence_match_reason"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )


def test_cluster_b_enforces_compact_reason_fields() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    payload["results"][0]["reason"] = "x" * 301
    with pytest.raises(PilotContractError, match="reason exceeds 300"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )

    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    payload["results"][0]["evidence_match_reason"] = "x" * 301
    with pytest.raises(PilotContractError, match="evidence_match_reason exceeds 300"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )


def test_cluster_b_distinguishes_missing_from_weak_retrieved_evidence() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    first = payload["results"][0]
    first.update(
        {
            "result": "uncertain",
            "evidence_basis": "insufficient_learning_resource",
            "evidence_basis_fields": ["retrieved_fragment"],
            "evidence_fragment_ids": ["F1"],
        }
    )
    with pytest.raises(PilotContractError, match="must not cite fragments"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )

    first.update(
        {
            "evidence_basis": "retrieved_fragment",
            "evidence_basis_fields": ["retrieved_fragment"],
            "evidence_fragment_ids": ["F1"],
            "evidence_match_reason": "Fragment liên quan nhưng chưa đủ để kết luận.",
        }
    )
    rows = validate_model_results(
        payload,
        expected_ids=CLUSTER_CRITERIA["B"],
        visible_fragment_ids={"F1"},
        cluster_id="B",
    )
    assert rows[0]["result"] == "uncertain"
    assert rows[0]["evidence_basis"] == "retrieved_fragment"


def test_cluster_b_requires_fragment_for_decisive_content_criteria() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], [])
    first = payload["results"][0]
    first["result"] = "pass"
    first["suggested_reviewer_action"] = "keep"

    with pytest.raises(PilotContractError, match="requires retrieved evidence"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids=set(),
            cluster_id="B",
        )


def test_cluster_b_required_image_dependency_forces_uncertain_review() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    first = payload["results"][0]
    first.update(
        {
            "evidence_fragment_ids": [],
            "evidence_basis": "image_required",
            "evidence_basis_fields": [],
            "image_dependency": "required",
            "image_dependency_reason": "Cần đọc nội dung trong ảnh.",
            "needs_image_review": True,
        }
    )

    with pytest.raises(PilotContractError, match="requires retrieved evidence"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )

    first["result"] = "uncertain"
    rows = validate_model_results(
        payload,
        expected_ids=CLUSTER_CRITERIA["B"],
        visible_fragment_ids={"F1"},
        cluster_id="B",
    )
    assert rows[0]["image_dependency"] == "required"
    assert rows[0]["needs_image_review"] is True

    first["confidence_score"] = 1.0
    with pytest.raises(PilotContractError, match="required image dependency must lower"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )


def test_cluster_b_allows_fragment_free_fail_only_for_direct_contradiction() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    first = payload["results"][0]
    first.update(
        {
            "result": "fail",
            "evidence_fragment_ids": [],
            "evidence_basis": "direct_internal_contradiction",
            "evidence_basis_fields": ["lesson", "position"],
            "evidence_match_reason": (
                "lesson và position khai báo hai bài khác nhau; không cần học liệu "
                "ngoài để xác nhận mâu thuẫn nội bộ."
            ),
        }
    )

    rows = validate_model_results(
        payload,
        expected_ids=CLUSTER_CRITERIA["B"],
        visible_fragment_ids={"F1"},
        cluster_id="B",
    )

    assert rows[0]["result"] == "fail"
    assert rows[0]["evidence_basis"] == "direct_internal_contradiction"


def test_raw_con_03_enforces_result_specific_fragment_contract() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
    target = next(
        row for row in payload["results"] if row["criterion_id"] == "RAW-CON-03"
    )
    target.update(
        {
            "result": "fail",
            "evidence_fragment_ids": [],
            "evidence_basis": "raw_row_only",
            "evidence_basis_fields": ["question", "dialogue"],
            "evidence_match_reason": (
                "Câu trả lời trong dialogue trực tiếp không giải quyết question."
            ),
        }
    )

    rows = validate_model_results(
        payload,
        expected_ids=CLUSTER_CRITERIA["B"],
        visible_fragment_ids={"F1"},
        cluster_id="B",
    )
    by_id = {row["criterion_id"]: row for row in rows}
    assert by_id["RAW-CON-03"]["result"] == "fail"
    assert by_id["RAW-CON-03"]["evidence_basis"] == "raw_row_only"

    target["result"] = "pass"
    with pytest.raises(PilotContractError, match="requires retrieved evidence"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )

    target.update(
        {
            "result": "fail",
            "evidence_basis": "direct_internal_contradiction",
            "evidence_basis_fields": ["lesson", "position"],
        }
    )
    with pytest.raises(PilotContractError, match="criterion-specific evidence contract"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["B"],
            visible_fragment_ids={"F1"},
            cluster_id="B",
        )


def test_subjective_clusters_reject_uncalibrated_full_confidence() -> None:
    payload = _model_payload(CLUSTER_CRITERIA["C"], [])
    payload["results"][0]["confidence_score"] = 1.0

    with pytest.raises(PilotContractError, match="subjective cluster"):
        validate_model_results(
            payload,
            expected_ids=CLUSTER_CRITERIA["C"],
            visible_fragment_ids=set(),
            cluster_id="C",
        )


def test_structure_and_duplicate_code_clusters_are_conservative() -> None:
    criteria = _criteria()
    incomplete = _row(answer_sgv="", dialogue="HS: Em hỏi.")
    structure = evaluate_structure_cluster(
        incomplete,
        criteria=criteria,
        checked_at="2026-09-17T00:00:00+00:00",
    )
    assert {row["criterion_id"]: row["result"] for row in structure} == {
        "RAW-STR-02": "uncertain",
        "RAW-STR-03": "fail",
    }

    left = _row("LEFT")
    right = _row("RIGHT")
    duplicates = evaluate_duplicate_cluster(
        [left, right],
        criteria=criteria,
        near_threshold=0.96,
        checked_at="2026-09-17T00:00:00+00:00",
    )
    assert all(row["result"] == "uncertain" for row in duplicates)


def test_manual_tool_loop_records_call_and_validates_final_json() -> None:
    function_call = SimpleNamespace(
        id="CALL-1",
        name="search_learning_fragments",
        args={
            "section_keywords": "Bài 1 dữ liệu",
            "content_keywords": "thông tin",
            "material_types": ["SGK"],
        },
    )
    first_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=function_call, text=None, thought=False)]
    )
    final_text = json.dumps(
        _model_payload(CLUSTER_CRITERIA["B"], ["F1"]),
        ensure_ascii=False,
    )
    final_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=final_text, thought=False)]
    )

    class FakeModels:
        def __init__(self):
            self.responses = [
                _response(content=first_content, response_id="R1"),
                _response(content=final_content, response_id="R2"),
            ]
            self.calls = []

        def generate_content(self, **kwargs):
            self.calls.append(kwargs)
            return self.responses.pop(0)

    fake_models = FakeModels()
    client = SimpleNamespace(models=fake_models)

    def fake_search(section_keywords, content_keywords, **kwargs):
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"], "lesson_key": ["bai_01"], "material_type": ["SGK"]},
            content_limit=5,
            matched_section_path="Chủ đề > Bài 1",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(
                {
                    "fragment_id": "F1",
                    "grade": "6",
                    "material_type": "SGK",
                    "book_title": "Tin học 6",
                    "lesson_title": "Bài 1",
                    "section_path": "Chủ đề > Bài 1",
                    "markdown_text": "Thông tin là hiểu biết.",
                    "content_score": -1.0,
                },
            ),
        )

    result = run_gemini_cluster(
        client=client,
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
    )

    assert len(fake_models.calls) == 2
    assert result.tool_call_count == 1
    assert [row["criterion_id"] for row in result.results] == list(CLUSTER_CRITERIA["B"])
    assert any(event["event_type"] == "retrieval_tool_call" for event in result.trace_events)
    model_rounds = [
        event for event in result.trace_events if event["event_type"] == "model_round"
    ]
    assert model_rounds[0]["model_response_content"] == {
        "parts": [
            {
                "function_call": {
                    "id": "CALL-1",
                    "name": "search_learning_fragments",
                    "args": {
                        "section_keywords": "Bài 1 dữ liệu",
                        "content_keywords": "thông tin",
                        "material_types": ["SGK"],
                    },
                }
            }
        ]
    }
    assert model_rounds[0]["model_response_thought_parts_omitted"] == 0
    assert model_rounds[1]["model_response_content"] == {
        "parts": [{"text": final_text}]
    }


def test_model_round_trace_omits_private_thought_parts() -> None:
    final_text = json.dumps(_model_payload(CLUSTER_CRITERIA["C"], []), ensure_ascii=False)
    content = SimpleNamespace(
        role="model",
        parts=[
            SimpleNamespace(function_call=None, text="private reasoning", thought=True),
            SimpleNamespace(function_call=None, text=final_text, thought=False),
        ],
    )
    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **_kwargs: _response(
                content=content,
                response_id="R-NO-THOUGHTS",
            )
        )
    )

    result = run_gemini_cluster(
        client=client,
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="C",
        expected_ids=CLUSTER_CRITERIA["C"],
        retrieval_adapter=None,
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
    )

    model_round = next(
        event for event in result.trace_events if event["event_type"] == "model_round"
    )
    assert model_round["model_response_content"] == {
        "role": "model",
        "parts": [{"text": final_text}],
    }
    assert model_round["model_response_thought_parts_omitted"] == 1
    assert "private reasoning" not in json.dumps(model_round, ensure_ascii=False)


def test_tool_budget_counts_empty_and_successful_results_separately() -> None:
    def tool_content(content_keywords: str):
        call = SimpleNamespace(
            name="search_learning_fragments",
            args={
                "section_keywords": "Bài 1 dữ liệu",
                "content_keywords": content_keywords,
                "material_types": ["SGK"],
            },
        )
        return SimpleNamespace(
            parts=[SimpleNamespace(function_call=call, text=None, thought=False)]
        )

    final_text = json.dumps(
        _model_payload(CLUSTER_CRITERIA["B"], ["F1"]),
        ensure_ascii=False,
    )
    final_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=final_text, thought=False)]
    )

    class FakeModels:
        def __init__(self):
            self.responses = [
                _response(content=tool_content("empty one"), response_id="R1"),
                _response(content=tool_content("empty two"), response_id="R2"),
                _response(content=tool_content("thông tin"), response_id="R3"),
                _response(content=final_content, response_id="R4"),
            ]

        def generate_content(self, **kwargs):
            return self.responses.pop(0)

    def fake_search(section_keywords, content_keywords, **kwargs):
        results = ()
        reason = "content_no_match"
        if content_keywords == "thông tin":
            results = (
                {
                    "fragment_id": "F1",
                    "grade": "6",
                    "material_type": "SGK",
                    "section_path": "Chủ đề > Bài 1",
                    "markdown_text": "Thông tin là hiểu biết.",
                    "content_score": -1.0,
                },
            )
            reason = None
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"]},
            content_limit=5,
            matched_section_path="Chủ đề > Bài 1",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=results,
            reason=reason,
        )

    result = run_gemini_cluster(
        client=SimpleNamespace(models=FakeModels()),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=1,
        max_total_tool_calls=3,
    )

    tool_events = [
        event
        for event in result.trace_events
        if event["event_type"] == "retrieval_tool_call"
    ]
    assert result.tool_call_count == 3
    assert [event["result_count"] for event in tool_events] == [0, 0, 1]
    assert tool_events[-1]["successful_tool_call_count"] == 1
    assert tool_events[-1]["model_visible_response"]["tool_budget"] == {
        "total_used": 3,
        "total_remaining": 0,
        "successful_used": 1,
        "successful_remaining": 0,
        "must_finalize": True,
    }


def test_budget_exhaustion_returns_one_finalization_response_without_new_search() -> None:
    def tool_content(content_keywords: str):
        call = SimpleNamespace(
            name="search_learning_fragments",
            args={
                "section_keywords": "Bài 1",
                "content_keywords": content_keywords,
            },
        )
        return SimpleNamespace(
            parts=[SimpleNamespace(function_call=call, text=None, thought=False)]
        )

    final_text = json.dumps(
        _model_payload(CLUSTER_CRITERIA["B"], ["F1"]),
        ensure_ascii=False,
    )
    final_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=final_text, thought=False)]
    )

    class FakeModels:
        def __init__(self):
            self.responses = [
                _response(content=tool_content("thông tin"), response_id="R1"),
                _response(content=tool_content("dữ liệu"), response_id="R2"),
                _response(content=final_content, response_id="R3"),
            ]

        def generate_content(self, **kwargs):
            return self.responses.pop(0)

    searches: list[str] = []

    def fake_search(section_keywords, content_keywords, **kwargs):
        searches.append(content_keywords)
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"]},
            content_limit=5,
            matched_section_path="Chủ đề 1 > Bài 1",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(
                {
                    "fragment_id": "F1",
                    "grade": "6",
                    "material_type": "SGK",
                    "section_path": "Chủ đề 1 > Bài 1",
                    "markdown_text": "Thông tin là hiểu biết.",
                    "content_score": -1.0,
                },
            ),
        )

    result = run_gemini_cluster(
        client=SimpleNamespace(models=FakeModels()),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=1,
        max_total_tool_calls=8,
    )

    assert searches == ["thông tin"]
    assert result.tool_call_count == 1
    exhausted = [
        event
        for event in result.trace_events
        if event["event_type"] == "tool_budget_exhausted"
    ]
    assert len(exhausted) == 1
    assert exhausted[0]["model_visible_response"]["status"] == "budget_exhausted"
    assert exhausted[0]["model_visible_response"]["tool_budget"]["must_finalize"] is True


def test_cluster_b_without_fragments_keeps_raw_row_criteria_judgeable() -> None:
    tool_call = SimpleNamespace(
        name="search_learning_fragments",
        args={"section_keywords": "Bài 1", "content_keywords": "không khớp"},
    )
    tool_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=tool_call, text=None, thought=False)]
    )
    payload = _model_payload(CLUSTER_CRITERIA["B"], [])
    for row in payload["results"]:
        if row["criterion_id"] in agent_audit.CRITERIA_REQUIRING_FRAGMENT_FOR_DECISION:
            row["result"] = "uncertain"
            row["confidence_score"] = 0.0
            row["suggested_reviewer_action"] = "ask_hnmu_review"
    model_pass_text = json.dumps(payload, ensure_ascii=False)
    final_content = SimpleNamespace(
        parts=[SimpleNamespace(function_call=None, text=model_pass_text, thought=False)]
    )

    class FakeModels:
        def __init__(self):
            self.responses = [
                _response(content=tool_content, response_id="R1"),
                _response(content=final_content, response_id="R2"),
            ]

        def generate_content(self, **kwargs):
            return self.responses.pop(0)

    def fake_search(section_keywords, content_keywords, **kwargs):
        return RetrievalResult(
            mode="section_and_content",
            section_keywords=section_keywords,
            content_keywords=content_keywords,
            filters={"grade": ["6"]},
            content_limit=5,
            matched_section_path="Chủ đề 1 > Bài 1",
            section_score=-1.0,
            snapshot_sha256="snapshot",
            results=(),
            reason="content_no_match",
        )

    result = run_gemini_cluster(
        client=SimpleNamespace(models=FakeModels()),
        model="gemini-test",
        thinking_level="MEDIUM",
        max_output_tokens=1024,
        seed=20260903,
        system_instruction="SYSTEM",
        user_prompt="USER",
        prompt_sha256="prompt-hash",
        cluster_id="B",
        expected_ids=CLUSTER_CRITERIA["B"],
        retrieval_adapter=AuditRetrievalAdapter(
            row=_row(),
            index_path=Path("index.sqlite"),
            search_fn=fake_search,
        ),
        max_successful_tool_calls=3,
        max_total_tool_calls=8,
    )

    assert len(result.results) == 6
    by_id = {row["criterion_id"]: row for row in result.results}
    assert {
        by_id[criterion_id]["result"]
        for criterion_id in agent_audit.CRITERIA_REQUIRING_FRAGMENT_FOR_DECISION
    } == {"uncertain"}
    assert by_id["RAW-CON-03"]["result"] == "uncertain"
    assert by_id["RAW-CON-04"]["result"] == "pass"
    assert all(row["evidence_fragment_ids"] == [] for row in result.results)
    assert all(row["evidence_match_reason"] for row in result.results)
    assert any(
        event["event_type"] == "cluster_b_no_fragments"
        for event in result.trace_events
    )


def test_recoverable_jsonl_tail_and_partial_cluster_rollback(tmp_path: Path) -> None:
    path = tmp_path / "results.jsonl"
    complete_a = [
        {
            "record_type": "criterion_result",
            "sample_id": "S1",
            "cluster_id": "A",
            "criterion_id": criterion_id,
        }
        for criterion_id in CLUSTER_CRITERIA["A"]
    ]
    partial_b = {
        "record_type": "criterion_result",
        "sample_id": "S1",
        "cluster_id": "B",
        "criterion_id": CLUSTER_CRITERIA["B"][0],
    }
    serialized = "".join(
        json.dumps(row, ensure_ascii=False) + "\n"
        for row in [*complete_a, partial_b]
    )
    path.write_bytes(serialized.encode("utf-8") + b'{"record_type":')

    rows, tail_truncated = read_jsonl_recoverable_tail(path)
    sanitized, recovery = _sanitize_resume_result_rows(
        [*rows, {"record_type": "sample_summary", "sample_id": "S1"}]
    )

    assert tail_truncated is True
    assert {
        (row["sample_id"], row["cluster_id"])
        for row in sanitized
        if row["record_type"] == "criterion_result"
    } == {("S1", "A")}
    assert recovery["partial_clusters_rolled_back"] == [
        {"sample_id": "S1", "cluster_id": "B"}
    ]
    assert recovery["sample_summaries_rolled_back"] == ["S1"]


def test_split_wide_retry_continues_rows_and_resume_runs_only_pending_clusters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = {
        name: tmp_path / name
        for name in (
            "rows.csv",
            "criteria.csv",
            "bloom.md",
            "scaffolding.md",
            "prompt.md",
            "index.sqlite",
            "selection.csv",
        )
    }
    for name, path in files.items():
        path.write_text(name, encoding="utf-8")
    config = PilotConfig(
        experiment_id="test",
        normalized_rows_path=files["rows.csv"],
        criteria_path=files["criteria.csv"],
        bloom_reference_path=files["bloom.md"],
        scaffolding_reference_path=files["scaffolding.md"],
        base_prompt_path=files["prompt.md"],
        retrieval_index_path=files["index.sqlite"],
        selection_path=files["selection.csv"],
        model="gemini-test",
        location="global",
        max_output_tokens=1024,
        seed=7,
        thinking_level="MEDIUM",
        timeout_seconds=30,
        include_tool_response_contract_in_prompt=True,
        max_successful_tool_calls_per_cluster=3,
        max_total_tool_calls_per_cluster=8,
        max_retries_per_cluster=1,
        retry_backoff_seconds=2,
        near_duplicate_threshold=0.96,
        selection_seed="seed",
        samples_per_grade=4,
        development_per_grade=2,
    )
    rows = [
        _row("S1", question="Question S1"),
        _row("S2", question="Question S2"),
    ]
    selection = [
        SelectionRow("S1", "6", "development", 1, "SGK"),
        SelectionRow("S2", "6", "development", 2, "SGK"),
    ]
    monkeypatch.setattr(agent_audit, "load_normalized_rows", lambda _path: rows)
    monkeypatch.setattr(agent_audit, "load_selection", lambda _path: selection)
    monkeypatch.setattr(agent_audit, "load_criteria", lambda _path: _criteria())
    monkeypatch.setattr(agent_audit, "_loaded_reference", lambda _config, _cluster: "")

    calls: list[tuple[str, str]] = []
    fail_s1_b = {"enabled": True}

    def fake_model_cluster(**kwargs):
        sample_id = "S1" if "Question S1" in kwargs["user_prompt"] else "S2"
        cluster_id = kwargs["cluster_id"]
        calls.append((sample_id, cluster_id))
        if fail_s1_b["enabled"] and sample_id == "S1" and cluster_id == "B":
            raise PilotContractError("persistent invalid model schema for S1/B")
        payload = _model_payload(tuple(kwargs["expected_ids"]), [])
        return ModelClusterResult(
            results=tuple(payload["results"]),
            trace_events=(),
            prompt_sha256=kwargs["prompt_sha256"],
            tool_call_count=1 if cluster_id == "B" else 0,
            usage={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            model_version="gemini-test",
            response_id=f"{sample_id}-{cluster_id}",
            finish_reason="STOP",
        )

    monkeypatch.setattr(agent_audit, "run_gemini_cluster", fake_model_cluster)
    output_dir = tmp_path / "run"
    delays: list[float] = []

    with pytest.raises(PilotExecutionError, match="sample/cluster pairs remain"):
        run_pilot_split(
            config=config,
            split="development",
            output_dir=output_dir,
            client=object(),
            sleep_fn=delays.append,
        )

    assert ("S2", "B") in calls
    assert calls.count(("S1", "B")) == 2
    assert all(calls.count(("S1", cluster_id)) == 1 for cluster_id in ("C", "D", "E"))
    assert delays == [2]
    first_summary = json.loads(
        (output_dir / "pilot_evaluation_summary.json").read_text(encoding="utf-8")
    )
    assert first_summary["run_status"] == "incomplete"
    assert first_summary["completed_sample_count"] == 1
    assert first_summary["pending_clusters"] == [
        {"sample_id": "S1", "cluster_id": "B"}
    ]
    first_results = read_jsonl(output_dir / "clustered_audit_results.jsonl")
    assert {
        row["sample_id"]
        for row in first_results
        if row["record_type"] == "sample_summary"
    } == {"S2"}
    first_traces = read_jsonl(output_dir / "retrieval_and_model_trace.jsonl")
    assert any(
        row.get("event_type") == "row_attempt_completed"
        and row.get("sample_id") == "S1"
        and row.get("row_status") == "pending_retry"
        for row in first_traces
    )

    partial = next(
        dict(row)
        for row in first_results
        if row.get("sample_id") == "S1" and row.get("cluster_id") == "C"
    )
    partial["cluster_id"] = "B"
    partial["criterion_id"] = CLUSTER_CRITERIA["B"][0]
    with (output_dir / "clustered_audit_results.jsonl").open("ab") as handle:
        handle.write((json.dumps(partial, ensure_ascii=False) + "\n").encode("utf-8"))
        handle.write(b'{"record_type":')
    with (output_dir / "retrieval_and_model_trace.jsonl").open("ab") as handle:
        handle.write(b'{"event_type":')

    fail_s1_b["enabled"] = False
    calls.clear()
    resumed = run_pilot_split(
        config=config,
        split="development",
        output_dir=output_dir,
        client=object(),
        resume=True,
        sleep_fn=delays.append,
    )

    assert calls == [("S1", "B")]
    assert resumed["run_status"] == "completed"
    assert resumed["completed_sample_count"] == 2
    assert resumed["execution_sequence"] == 2
    assert "current_execution_metrics" in resumed
    assert "cumulative_metrics" in resumed
    assert resumed["resume_recovery"]["result_tail_truncated"] is True
    assert resumed["resume_recovery"]["trace_tail_truncated"] is True
    assert resumed["resume_recovery"]["partial_clusters_rolled_back"] == [
        {"sample_id": "S1", "cluster_id": "B"}
    ]
    final_results = read_jsonl(output_dir / "clustered_audit_results.jsonl")
    assert len(
        [row for row in final_results if row["record_type"] == "criterion_result"]
    ) == 36
    assert len([row for row in final_results if row["record_type"] == "sample_summary"]) == 2


def test_truncation_is_not_retried_and_other_clusters_continue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = {
        name: tmp_path / name
        for name in (
            "rows.csv",
            "criteria.csv",
            "bloom.md",
            "scaffolding.md",
            "prompt.md",
            "index.sqlite",
            "selection.csv",
        )
    }
    for name, path in files.items():
        path.write_text(name, encoding="utf-8")
    config = PilotConfig(
        experiment_id="test",
        normalized_rows_path=files["rows.csv"],
        criteria_path=files["criteria.csv"],
        bloom_reference_path=files["bloom.md"],
        scaffolding_reference_path=files["scaffolding.md"],
        base_prompt_path=files["prompt.md"],
        retrieval_index_path=files["index.sqlite"],
        selection_path=files["selection.csv"],
        model="gemini-test",
        location="global",
        max_output_tokens=1024,
        seed=7,
        thinking_level="MEDIUM",
        timeout_seconds=30,
        include_tool_response_contract_in_prompt=True,
        max_successful_tool_calls_per_cluster=3,
        max_total_tool_calls_per_cluster=8,
        max_retries_per_cluster=3,
        retry_backoff_seconds=2,
        near_duplicate_threshold=0.96,
        selection_seed="seed",
        samples_per_grade=4,
        development_per_grade=2,
    )
    row = _row("S1", question="Question S1")
    monkeypatch.setattr(agent_audit, "load_normalized_rows", lambda _path: [row])
    monkeypatch.setattr(
        agent_audit,
        "load_selection",
        lambda _path: [SelectionRow("S1", "6", "development", 1, "SGK")],
    )
    monkeypatch.setattr(agent_audit, "load_criteria", lambda _path: _criteria())
    monkeypatch.setattr(agent_audit, "_loaded_reference", lambda _config, _cluster: "")

    calls: list[str] = []

    def fake_model_cluster(**kwargs):
        cluster_id = kwargs["cluster_id"]
        calls.append(cluster_id)
        if cluster_id == "B":
            raise PilotOutputTruncatedError("finish_reason=MAX_TOKENS")
        payload = _model_payload(tuple(kwargs["expected_ids"]), [])
        return ModelClusterResult(
            results=tuple(payload["results"]),
            trace_events=(),
            prompt_sha256=kwargs["prompt_sha256"],
            tool_call_count=0,
            usage={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            model_version="gemini-test",
            response_id=cluster_id,
            finish_reason="STOP",
        )

    monkeypatch.setattr(agent_audit, "run_gemini_cluster", fake_model_cluster)
    output_dir = tmp_path / "truncated-run"
    delays: list[float] = []

    with pytest.raises(PilotExecutionError, match="non-retryable sample/cluster"):
        run_pilot_split(
            config=config,
            split="development",
            output_dir=output_dir,
            client=object(),
            sleep_fn=delays.append,
        )

    assert calls == ["B", "C", "D", "E"]
    assert delays == []
    summary = json.loads(
        (output_dir / "pilot_evaluation_summary.json").read_text(encoding="utf-8")
    )
    assert summary["pending_clusters"] == [{"sample_id": "S1", "cluster_id": "B"}]
    assert summary["non_retryable_pending_clusters"] == [
        {"sample_id": "S1", "cluster_id": "B"}
    ]
    traces = read_jsonl(output_dir / "retrieval_and_model_trace.jsonl")
    error = next(row for row in traces if row.get("event_type") == "cluster_error")
    assert error["retryable"] is False
    assert error["failure_category"] == "output_truncated"
    assert any(
        row.get("event_type") == "row_attempt_completed"
        and row.get("row_status") == "blocked_non_retryable"
        for row in traces
    )


def test_trace_metrics_count_repeated_queries_and_usage() -> None:
    traces = [
        {
            "event_type": "model_round",
            "sample_id": "S1",
            "latency_ms": 10,
            "usage": {"input_tokens": 5, "output_tokens": 2, "total_tokens": 7},
        },
        {
            "event_type": "retrieval_tool_call",
            "sample_id": "S1",
            "cluster_id": "B",
            "latency_ms": 3,
            "result_count": 0,
            "model_visible_response": {"status": "content_no_match"},
            "ranked_results": [],
            "arguments_from_model": {
                "section_keywords": "bài 1",
                "content_keywords": "thông tin",
            },
        },
        {
            "event_type": "cluster_attempt_error",
            "sample_id": "S1",
            "error_type": "TimeoutError",
        },
        {
            "event_type": "cluster_retry_recovered",
            "sample_id": "S1",
        },
        {
            "event_type": "retrieval_tool_call",
            "sample_id": "S1",
            "cluster_id": "B",
            "latency_ms": 5,
            "result_count": 2,
            "model_visible_response": {"status": "success"},
            "ranked_results": [
                {
                    "fragment_id": "F1",
                    "source_fragment_count": 2,
                    "source_fragment_types": ["text", "table"],
                    "contains_table_source": True,
                },
                {
                    "fragment_id": "F2",
                    "source_fragment_count": 1,
                    "source_fragment_types": ["text"],
                    "contains_table_source": False,
                },
            ],
            "arguments_from_model": {
                "section_keywords": "bài 1",
                "content_keywords": "thông tin",
            },
        },
    ]
    metrics = summarize_trace_metrics(traces, tool_required_sample_count=2)
    assert metrics["tool_use_rate"] == 0.5
    assert metrics["repeated_identical_query_count"] == 1
    assert metrics["tool_no_result_count"] == 1
    assert metrics["successful_tool_call_count"] == 1
    assert metrics["empty_tool_call_count"] == 1
    assert metrics["query_with_results_rate"] == 0.5
    assert metrics["retrieval_status_counts"] == {
        "content_no_match": 1,
        "success": 1,
    }
    assert metrics["returned_fragment_count_total"] == 2
    assert metrics["returned_fragment_count_unique"] == 2
    assert metrics["multi_source_fragment_return_count"] == 1
    assert metrics["table_containing_fragment_return_count"] == 1
    assert metrics["cluster_b_with_fragment_sample_count"] == 1
    assert metrics["cluster_b_without_fragment_sample_count"] == 1
    assert metrics["cluster_b_without_fragment_sample_rate"] == 0.5
    assert metrics["tool_cache_hit_count"] == 0
    assert metrics["retrieval_latency_ms_total"] == 8
    assert metrics["total_tokens"] == 7
    assert metrics["cluster_attempt_error_count"] == 1
    assert metrics["cluster_retry_recovered_count"] == 1


def _recovery_fixture(
    tmp_path: Path,
) -> tuple[PilotConfig, list[dict[str, object]], RawDialogueRow]:
    files = {
        name: tmp_path / name
        for name in (
            "rows.csv",
            "criteria.csv",
            "bloom.md",
            "scaffolding.md",
            "prompt.md",
            "index.sqlite",
            "selection.csv",
        )
    }
    for name, path in files.items():
        path.write_text(name, encoding="utf-8")
    parent = tmp_path / "parent"
    parent.mkdir()
    row = _row("S1")
    parent_records: list[dict[str, object]] = []
    for cluster_id, criterion_ids in CLUSTER_CRITERIA.items():
        if cluster_id == "B":
            continue
        for criterion_id in criterion_ids:
            parent_records.append(
                {
                    "record_type": "criterion_result",
                    "sample_id": "S1",
                    "cluster_id": cluster_id,
                    "criterion_id": criterion_id,
                    "result": "pass",
                    "confidence_score": 0.9,
                    "reason": "Đạt.",
                    "evidence_fragment_id": "",
                    "image_dependency": "none",
                    "needs_image_review": False,
                }
            )
    agent_audit.atomic_write_jsonl(
        parent / "clustered_audit_results.jsonl", parent_records
    )
    fingerprint = "f" * 64
    agent_audit.atomic_write_jsonl(
        parent / "retrieval_and_model_trace.jsonl",
        [
            {"event_type": "run_manifest", "run_fingerprint": fingerprint},
            {
                "event_type": "run_incomplete",
                "pending_clusters": [{"sample_id": "S1", "cluster_id": "B"}],
            },
        ],
    )
    agent_audit.atomic_write_json(
        parent / "pilot_evaluation_summary.json",
        {
            "run_status": "incomplete",
            "split": "development",
            "sample_count": 1,
            "completed_sample_count": 0,
            "criterion_result_count": 12,
            "sample_summary_count": 0,
            "run_fingerprint": fingerprint,
            "pending_clusters": [{"sample_id": "S1", "cluster_id": "B"}],
            "non_retryable_pending_clusters": [
                {"sample_id": "S1", "cluster_id": "B"}
            ],
        },
    )
    recovery = ClusterRecoverySpec(
        parent_output_dir=parent,
        split="development",
        target_sample_id="S1",
        target_cluster_id="B",
        expected_parent_run_fingerprint=fingerprint,
        expected_parent_result_sha256=agent_audit.sha256_file(
            parent / "clustered_audit_results.jsonl"
        ),
        expected_parent_trace_sha256=agent_audit.sha256_file(
            parent / "retrieval_and_model_trace.jsonl"
        ),
        expected_parent_summary_sha256=agent_audit.sha256_file(
            parent / "pilot_evaluation_summary.json"
        ),
        expected_parent_sample_count=1,
        expected_parent_completed_sample_count=0,
        expected_parent_criterion_result_count=12,
        expected_parent_sample_summary_count=0,
        expected_parent_completed_cluster_count=5,
        expected_final_criterion_result_count=18,
        expected_final_sample_summary_count=1,
        expected_final_completed_cluster_count=6,
    )
    config = PilotConfig(
        experiment_id="test",
        normalized_rows_path=files["rows.csv"],
        criteria_path=files["criteria.csv"],
        bloom_reference_path=files["bloom.md"],
        scaffolding_reference_path=files["scaffolding.md"],
        base_prompt_path=files["prompt.md"],
        retrieval_index_path=files["index.sqlite"],
        selection_path=files["selection.csv"],
        model="gemini-test",
        location="global",
        max_output_tokens=8192,
        seed=7,
        thinking_level="MEDIUM",
        timeout_seconds=30,
        include_tool_response_contract_in_prompt=True,
        max_successful_tool_calls_per_cluster=3,
        max_total_tool_calls_per_cluster=8,
        max_retries_per_cluster=3,
        retry_backoff_seconds=2,
        near_duplicate_threshold=0.96,
        selection_seed="seed",
        samples_per_grade=2,
        development_per_grade=1,
        recovery=recovery,
    )
    return config, parent_records, row


@pytest.mark.parametrize("status_code", [401, 403])
def test_authentication_and_permission_errors_are_not_retryable(
    status_code: int,
) -> None:
    error = RuntimeError("Vertex request rejected")
    error.code = status_code  # type: ignore[attr-defined]

    assert _is_retryable_cluster_error(error) is False


@pytest.mark.parametrize("status_code", [429, 500, 503])
def test_transient_http_errors_remain_retryable(status_code: int) -> None:
    response = SimpleNamespace(status_code=status_code)
    error = RuntimeError("Temporary provider failure")
    error.response = response  # type: ignore[attr-defined]

    assert _is_retryable_cluster_error(error) is True


def test_output_truncation_remains_non_retryable() -> None:
    assert (
        _is_retryable_cluster_error(
            PilotOutputTruncatedError("finish_reason=MAX_TOKENS")
        )
        is False
    )


def test_cluster_recovery_preflight_fails_closed_on_parent_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, _, row = _recovery_fixture(tmp_path)
    monkeypatch.setattr(agent_audit, "validate_pilot_inputs", lambda _config: {})
    monkeypatch.setattr(agent_audit, "load_normalized_rows", lambda _path: [row])
    monkeypatch.setattr(
        agent_audit,
        "load_selection",
        lambda _path: [SelectionRow("S1", "6", "development", 1, "SGK")],
    )
    monkeypatch.setattr(
        agent_audit, "validate_selection_contract", lambda *_args, **_kwargs: None
    )
    summary_path = config.recovery.parent_output_dir / "pilot_evaluation_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["criterion_result_count"] = 13
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    with pytest.raises(PilotContractError, match="artifact hash mismatch"):
        validate_cluster_recovery_inputs(config)


def test_cluster_recovery_runs_only_target_and_preserves_parent_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, parent_records, row = _recovery_fixture(tmp_path)
    monkeypatch.setattr(agent_audit, "validate_pilot_inputs", lambda _config: {})
    monkeypatch.setattr(agent_audit, "load_normalized_rows", lambda _path: [row])
    monkeypatch.setattr(
        agent_audit,
        "load_selection",
        lambda _path: [SelectionRow("S1", "6", "development", 1, "SGK")],
    )
    monkeypatch.setattr(
        agent_audit, "validate_selection_contract", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(agent_audit, "load_criteria", lambda _path: _criteria())
    monkeypatch.setattr(agent_audit, "_loaded_reference", lambda *_args: "")
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_model_cluster(**kwargs):
        calls.append((kwargs["cluster_id"], tuple(kwargs["expected_ids"])))
        payload = _model_payload(CLUSTER_CRITERIA["B"], ["F1"])
        return ModelClusterResult(
            results=tuple(payload["results"]),
            trace_events=(),
            prompt_sha256=kwargs["prompt_sha256"],
            tool_call_count=1,
            usage={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            model_version="gemini-test",
            response_id="recovered-B",
            finish_reason="STOP",
        )

    monkeypatch.setattr(agent_audit, "run_gemini_cluster", fake_model_cluster)
    output_dir = tmp_path / "recovery-output"
    summary = run_cluster_recovery(
        config=config,
        output_dir=output_dir,
        client=object(),
        sleep_fn=lambda _seconds: None,
    )

    assert calls == [("B", CLUSTER_CRITERIA["B"])]
    assert summary["run_status"] == "completed"
    assert summary["criterion_result_count"] == 18
    assert summary["sample_summary_count"] == 1
    assert summary["completed_cluster_count"] == 6
    assert summary["merge_validation"]["inherited_records_unchanged"] is True
    merged = read_jsonl(output_dir / "clustered_audit_results.jsonl")
    assert merged[: len(parent_records)] == parent_records
    assert len([row for row in merged if row["record_type"] == "criterion_result"]) == 18
    assert len([row for row in merged if row["record_type"] == "sample_summary"]) == 1


def test_cluster_recovery_does_not_retry_http_403(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, _, row = _recovery_fixture(tmp_path)
    monkeypatch.setattr(agent_audit, "validate_pilot_inputs", lambda _config: {})
    monkeypatch.setattr(agent_audit, "load_normalized_rows", lambda _path: [row])
    monkeypatch.setattr(
        agent_audit,
        "load_selection",
        lambda _path: [SelectionRow("S1", "6", "development", 1, "SGK")],
    )
    monkeypatch.setattr(
        agent_audit, "validate_selection_contract", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(agent_audit, "load_criteria", lambda _path: _criteria())
    monkeypatch.setattr(agent_audit, "_loaded_reference", lambda *_args: "")
    calls: list[str] = []

    def reject_model_cluster(**kwargs):
        calls.append(kwargs["cluster_id"])
        error = RuntimeError("Permission denied")
        error.code = 403  # type: ignore[attr-defined]
        raise error

    monkeypatch.setattr(agent_audit, "run_gemini_cluster", reject_model_cluster)
    output_dir = tmp_path / "recovery-http-403"
    delays: list[float] = []

    with pytest.raises(PilotExecutionError, match="recovery remains incomplete"):
        run_cluster_recovery(
            config=config,
            output_dir=output_dir,
            client=object(),
            sleep_fn=delays.append,
        )

    assert calls == ["B"]
    assert delays == []
    summary = json.loads(
        (output_dir / "pilot_evaluation_summary.json").read_text(encoding="utf-8")
    )
    assert summary["attempted_count"] == 1
    assert summary["failure"]["retryable"] is False
    traces = read_jsonl(output_dir / "retrieval_and_model_trace.jsonl")
    error_trace = next(
        row for row in traces if row.get("event_type") == "recovery_attempt_error"
    )
    assert error_trace["retryable"] is False
    assert error_trace["retry_scheduled"] is False

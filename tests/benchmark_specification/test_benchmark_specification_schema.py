"""Tests for provisional benchmark-specification schemas."""

import csv

from edu_benchmark.benchmark_specification.schema import (
    validate_capabilities,
    validate_evaluation_context,
    validate_exact_header,
    validate_rubrics,
    validate_serious_errors,
    validate_current_task_principle_design,
    validate_principle_annotations,
    validate_tasks,
)


def test_provisional_capability_cannot_be_confirmed_by_agent():
    row = {
        "capability_id": "CAP-01",
        "capability_name": "Chính xác",
        "definition": "Đúng kiến thức.",
        "exclusions": "Không đo văn phong.",
        "observable_evidence": "Các phát biểu chuyên môn.",
        "positive_anchor": "Đúng và có căn cứ.",
        "mid_anchor": "Đúng nhưng thiếu.",
        "negative_anchor": "Sai.",
        "status": "confirmed",
        "research_ids": "RS-1",
        "research_source_origins": "Nguồn thử nghiệm.",
        "research_support_summary": "Hỗ trợ thử nghiệm.",
        "research_provenance_ref": "provenance.csv",
        "teacher_decision_needed": "HNMU xác nhận.",
    }
    assert "row_2:confirmed_without_human_authority" in validate_capabilities([row])


def test_task_contract_requires_student_state_goal_and_evidence():
    row = {
        "task_id": "TASK-01",
        "task_name": "Dàn giáo",
        "definition": "Hỗ trợ bước tiếp theo.",
        "scope": "Một response.",
        "student_state": "",
        "primary_tutoring_goal": "",
        "required_response_evidence": "",
        "input_requirements": "Prompt.",
        "output_requirements": "Hint.",
        "status": "needs_hnmu_review",
        "research_ids": "RS-1",
        "learning_material_ids": "",
        "teacher_decision_needed": "Xác nhận.",
    }
    errors = validate_tasks([row])
    assert "row_2:missing:student_state" in errors
    assert "row_2:missing:primary_tutoring_goal" in errors
    assert "row_2:missing:required_response_evidence" in errors


def test_two_tier_rubric_foreign_keys_fail_closed():
    dimension = {
        "dimension_id": "DIM-01",
        "dimension_name": "Chính xác",
        "capability_id": "CAP-X",
        "criterion": "Đúng chuyên môn.",
        "observable_evidence": "Nội dung response.",
        "score_levels": "1|3|5",
        "applicability_rule": "all",
        "status": "needs_hnmu_review",
        "research_ids": "RS-1",
        "teacher_decision_needed": "Xác nhận.",
    }
    rubric = {
        "rubric_id": "R-01",
        "principle_id": "PRINCIPLE-X",
        "capability_ids": "CAP-01;CAP-X",
        "criterion": "Bước tiếp theo phù hợp.",
        "observable_evidence": "Response.",
        "score_levels": "1|3|5",
        "status": "needs_hnmu_review",
        "research_ids": "RS-1",
        "teacher_decision_needed": "Xác nhận.",
    }
    errors = validate_rubrics(
        [dimension],
        [rubric],
        capability_ids={"CAP-01"},
        principle_ids={"PRINCIPLE-01"},
    )
    assert "dimension_row_2:unknown_capability:CAP-X" in errors
    assert "rubric_row_2:unknown_principle:PRINCIPLE-X" in errors
    assert "rubric_row_2:unknown_capability:CAP-X" in errors


def test_serious_error_action_and_rubric_references_are_validated():
    row = {
        "error_id": "ERR-01",
        "description": "Sai kiến thức.",
        "suggested_action": "delete",
        "affected_rubric_ids": "R-X",
        "status": "needs_hnmu_review",
        "confirmation_owner": "HNMU",
    }
    errors = validate_serious_errors([row], known_rubric_ids={"R-01"})
    assert "serious_error_row_2:invalid_action:delete" in errors
    assert "serious_error_row_2:unknown_rubric:R-X" in errors


def test_principle_annotations_require_set_or_coverage_gap_but_not_both():
    row = {
        "benchmark_candidate_id": "BC-1",
        "sample_id": "S1",
        "student_state_summary": "Học sinh hỏi khái niệm.",
        "coverage_gap_reason": "Không có nguyên tắc phù hợp.",
        "grounding_effect": "unchanged",
        "grounding_change_reason": "",
        "coder_id": "AI-CODER-01",
        "review_status": "needs_uet_review",
        "adjudication_status": "",
    }
    labels = [
        {
            "benchmark_candidate_id": "BC-1",
            "principle_id": "PRINCIPLE-EXPLANATION",
            "selection_rationale": "Chức năng giải thích không thể bỏ.",
            "context_evidence": "Học sinh hỏi khái niệm.",
            "grounding_evidence": "",
            "coder_id": "AI-CODER-01",
            "review_status": "needs_uet_review",
        }
    ]
    errors = validate_principle_annotations(
        [row],
        labels,
        expected_candidate_ids={"BC-1"},
        known_principle_ids={"PRINCIPLE-EXPLANATION"},
    )
    assert (
        "annotation_row_2:requires_principle_set_or_coverage_gap" in errors
    )


def test_principle_annotations_reject_duplicate_candidate_principle_pair():
    row = {
        "benchmark_candidate_id": "BC-1",
        "sample_id": "S1",
        "student_state_summary": "Học sinh cần giải thích.",
        "coverage_gap_reason": "",
        "grounding_effect": "unchanged",
        "grounding_change_reason": "",
        "coder_id": "AI-CODER-01",
        "review_status": "needs_uet_review",
        "adjudication_status": "",
    }
    label = {
        "benchmark_candidate_id": "BC-1",
        "principle_id": "PRINCIPLE-EXPLANATION",
        "selection_rationale": "Chức năng giải thích không thể bỏ.",
        "context_evidence": "Học sinh cần giải thích.",
        "grounding_evidence": "",
        "coder_id": "AI-CODER-01",
        "review_status": "needs_uet_review",
    }
    errors = validate_principle_annotations(
        [row],
        [label, dict(label)],
        expected_candidate_ids={"BC-1"},
        known_principle_ids={"PRINCIPLE-EXPLANATION"},
    )
    assert (
        "principle_label_row_3:duplicate_candidate_principle:"
        "BC-1:PRINCIPLE-EXPLANATION" in errors
    )


def test_current_design_requires_one_task_and_six_kmp_principles():
    task = {
        "task_id": "TASK-NEXT-TUTOR-RESPONSE",
        "task_name": "Sinh phản hồi tiếp theo",
        "definition": "Sinh phản hồi gia sư phù hợp.",
        "scope": "Một phản hồi.",
        "student_state": "Được suy ra từ đầu vào.",
        "primary_tutoring_goal": "Giúp học sinh tiến bộ.",
        "required_response_evidence": "Phản hồi quan sát được.",
        "input_requirements": "Candidate hợp lệ.",
        "output_requirements": "Một phản hồi.",
        "status": "needs_hnmu_review",
        "research_ids": "TR-P002",
        "learning_material_ids": "",
        "teacher_decision_needed": "HNMU xác nhận.",
    }
    principle_ids = (
        "PRINCIPLE-CHALLENGE",
        "PRINCIPLE-EXPLANATION",
        "PRINCIPLE-MODELLING",
        "PRINCIPLE-PRACTICE",
        "PRINCIPLE-FEEDBACK",
        "PRINCIPLE-QUESTIONING",
    )
    principles = [
        {
            "principle_id": principle_id,
            "principle_name_en": principle_id,
            "principle_name_vi": principle_id,
            "definition": "Định nghĩa.",
            "include_when": "Điều kiện gồm.",
            "exclude_when": "Điều kiện loại.",
            "observable_response_evidence": "Dấu hiệu.",
            "status": "needs_hnmu_review",
            "research_ids": "TR-P002",
            "source_locator": "KMP-Bench.",
            "teacher_decision_needed": "HNMU xác nhận.",
        }
        for principle_id in principle_ids
    ]
    assert validate_current_task_principle_design([task], principles) == []


def test_evaluation_context_cannot_smuggle_in_candidate_rubric_tier():
    row = {
        "benchmark_candidate_id": "BC-1",
        "student_state_summary": "Học sinh đang kẹt.",
        "primary_tutoring_goal": "Giúp đi tiếp.",
        "gold_answer": "Đáp án",
        "gold_response_reference": "Phản hồi tham chiếu",
        "learning_material_ids": "",
        "evidence_fragment_ids": "",
        "task_specific_facts": "Dữ kiện cần dùng.",
        "context_review_status": "needs_hnmu_review",
        "candidate_criterion": "Không được phép",
    }
    errors = validate_evaluation_context(
        [row],
        expected_candidate_ids={"BC-1"},
    )
    assert (
        "context_row_2:rubric_semantics_in_context:candidate_criterion" in errors
    )


def test_exact_header_validator_rejects_data_row_width_drift(tmp_path):
    path = tmp_path / "malformed.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["first", "second"])
        writer.writerow(["a", "b", "unexpected"])
    errors = validate_exact_header(path, ["first", "second"])
    assert errors == [
        f"row_width_mismatch:{path}:2:expected=2:actual=3"
    ]

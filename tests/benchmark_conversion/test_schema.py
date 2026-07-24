import json

import pytest

from edu_benchmark.benchmark_conversion.schema import (
    CANDIDATE_SPLIT_COLUMNS,
    CONVERSION_DISPOSITION_COLUMNS,
    TRACE_COLUMNS,
    dump_json_string_list,
    parse_json_string_list,
    validate_candidate_split_row,
    validate_conversion_trace_row,
    validate_conversion_input_row,
    validate_conversion_disposition_row,
)


def valid_input_row():
    return {
        "sample_id": "S1",
        "source_batch": "grade6_7",
        "source_file": "source.xlsx",
        "source_row_number": "2",
        "grade": "6",
        "lesson": "Bài 1",
        "question": "Question",
        "answer_sgv": "Answer",
        "raw_dialogue": "HS: Question\nAI: Answer",
        "conversion_dialogue": "HS: Question\nAI: Answer",
        "dialogue_correction_ids": "[]",
        "raw_quality_decision": "pass",
        "raw_audit_blocking_evidence_fragment_ids": "[]",
        "raw_audit_all_evidence_fragment_ids": '["F1"]',
    }


def test_json_string_list_is_sorted_deduplicated_and_validated():
    serialized = dump_json_string_list(["F2", "F1", "F2"])
    assert serialized == '["F1", "F2"]'
    assert parse_json_string_list(serialized, field_name="evidence") == ["F1", "F2"]
    with pytest.raises(ValueError):
        parse_json_string_list('["F1", "F1"]', field_name="evidence")


def test_pass_blocking_evidence_is_inconsistent():
    row = valid_input_row()
    row["raw_audit_blocking_evidence_fragment_ids"] = '["F1"]'
    assert "pass_has_blocking_evidence" in validate_conversion_input_row(row)


def test_pass_requires_all_raw_audit_evidence():
    row = valid_input_row()
    row["raw_audit_all_evidence_fragment_ids"] = "[]"
    assert "pass_missing_all_evidence" in validate_conversion_input_row(row)


def test_noncanonical_quality_label_is_rejected():
    row = valid_input_row()
    row["raw_quality_decision"] = "needs_human_review"
    assert "noncanonical_quality_decision" in validate_conversion_input_row(row)


def test_candidate_contract_distinguishes_gold_answer_and_gold_response():
    row = {
        "benchmark_candidate_id": "BC-S1-FINAL",
        "sample_id": "S1",
        "source_file": "source.xlsx",
        "source_row_number": "2",
        "grade": "6",
        "student_prompt": "Question",
        "conversation_history": json.dumps([]),
        "gold_response": "Tutor response",
        "gold_answer": "Subject answer",
        "raw_dialogue": "HS: Question\nAI: Tutor response",
        "conversion_dialogue": "HS: Question\nAI: Tutor response",
        "dialogue_correction_ids": "[]",
        "target_tutor_turn_index": "2",
        "split_strategy": "final_tutor_response",
        "raw_audit_blocking_evidence_fragment_ids": "[]",
        "raw_audit_all_evidence_fragment_ids": '["F1"]',
    }
    assert validate_candidate_split_row(row) == []


def test_plan02_candidate_schema_is_lean_and_trace_is_separate():
    assert CANDIDATE_SPLIT_COLUMNS == [
        "benchmark_candidate_id",
        "sample_id",
        "grade",
        "lesson",
        "position",
        "bloom_level",
        "student_prompt",
        "conversation_history",
        "gold_response",
        "gold_answer",
    ]
    assert "raw_dialogue" not in CANDIDATE_SPLIT_COLUMNS
    assert "dialogue_correction_ids" not in CANDIDATE_SPLIT_COLUMNS
    assert TRACE_COLUMNS[-3:] == [
        "target_tutor_turn_index",
        "split_strategy",
        "dialogue_correction_ids",
    ]


def test_plan02_trace_and_raw_summary_contracts():
    trace = {
        "benchmark_candidate_id": "BC-S1-AI02",
        "sample_id": "S1",
        "source_batch": "grade6_7",
        "source_file": "source.xlsx",
        "source_row_number": "2",
        "target_tutor_turn_index": "2",
        "split_strategy": "each_tutor_turn",
        "dialogue_correction_ids": "[]",
    }
    assert validate_conversion_trace_row(trace) == []
    summary = dict.fromkeys(CONVERSION_DISPOSITION_COLUMNS, "")
    summary.update(
        {
            "sample_id": "S1",
            "grade": "6",
            "candidate_count": "2",
            "first_target_tutor_turn_index": "2",
            "last_target_tutor_turn_index": "4",
            "conversion_disposition": "converted",
        }
    )
    assert validate_conversion_disposition_row(summary) == []

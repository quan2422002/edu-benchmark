import json

import pytest

from edu_benchmark.benchmark_specification.task_discovery import (
    build_candidate_feature_census,
    cognitive_band,
    enrich_discovery_sample,
    select_task_discovery_sample,
    summarize_discovery_strata,
)


def candidate(candidate_id, sample_id, grade, history, lesson="Bài thuật toán"):
    return {
        "benchmark_candidate_id": candidate_id,
        "sample_id": sample_id,
        "grade": grade,
        "lesson": lesson,
        "position": "Mục 1",
        "bloom_level": "Thông hiểu (giải thích)",
        "student_prompt": "Em chưa hiểu thuật toán này?",
        "conversation_history": json.dumps(history, ensure_ascii=False),
        "gold_response": "Em hãy thử nêu bước đầu tiên.",
        "gold_answer": "Bước 1",
    }


def trace(candidate_id, sample_id, target=2):
    return {
        "benchmark_candidate_id": candidate_id,
        "sample_id": sample_id,
        "target_tutor_turn_index": str(target),
    }


def test_cognitive_band_normalizes_detailed_labels():
    assert cognitive_band("Nhận biết (Nêu được)") == "Biết"
    assert cognitive_band("Thông hiểu") == "Hiểu"
    assert cognitive_band("Vận dụng (Thực hiện)") == "Vận dụng"
    assert cognitive_band("") == "Chưa xác định"


def test_census_uses_observable_signals_without_semantic_task_label():
    history = [
        {"turn_index": 2, "role": "tutor", "content": "Em thử nhé"},
        {"turn_index": 3, "role": "student", "content": "Em chưa hiểu ạ"},
    ]
    rows = build_candidate_feature_census(
        [candidate("BC-1", "S1", "6", history)],
        [trace("BC-1", "S1", target=4)],
    )
    row = rows[0]
    assert row["cognitive_band"] == "Hiểu"
    assert row["content_form_signal"] == "algorithm"
    assert "explicit_uncertainty" in row["student_state_signal"]
    assert row["feature_method"] == "deterministic_regex_v1"
    assert "task" not in row


def test_census_fails_closed_when_trace_is_missing():
    with pytest.raises(ValueError, match="Missing trace"):
        build_candidate_feature_census(
            [candidate("BC-1", "S1", "6", [])],
            [],
        )


def test_discovery_sample_is_deterministic_and_family_diverse():
    census = []
    for grade in ("6", "7", "8", "9"):
        for index in range(4):
            census.append(
                {
                    "benchmark_candidate_id": f"BC-{grade}-{index}",
                    "sample_id": f"S-{grade}-{index}",
                    "grade": grade,
                    "lesson": f"Bài {index}",
                    "position": "Mục 1",
                    "cognitive_band": ["Biết", "Hiểu"][index % 2],
                    "history_present": str(bool(index % 2)).lower(),
                    "history_turn_count": str(index * 2),
                    "history_depth_bin": ["0", "2", "4-6", "8+"][index],
                    "target_tutor_turn_index": str(index * 2 + 2),
                    "target_position_bin": [
                        "first_tutor_turn",
                        "early_followup",
                        "early_followup",
                        "later_followup",
                    ][index],
                    "content_form_signal": [
                        "algorithm",
                        "spreadsheet",
                        "data_information",
                        "concept_or_other",
                    ][index],
                    "student_state_signal": "initial_request",
                    "feature_method": "deterministic_regex_v1",
                }
            )
    first = select_task_discovery_sample(census, per_grade=3, seed="fixed")
    second = select_task_discovery_sample(census, per_grade=3, seed="fixed")
    assert first == second
    assert len(first) == 12
    assert len({row["sample_id"] for row in first}) == 12
    assert {
        row["student_state_signal"] for row in first if row["grade"] == "6"
    }


def test_discovery_coding_input_preserves_candidate_content():
    source = candidate(
        "BC-1",
        "S1",
        "6",
        [],
        lesson="Bài dữ liệu",
    )
    sample = [
        {
            "benchmark_candidate_id": "BC-1",
            "sample_id": "S1",
            "grade": "6",
        }
    ]
    enriched = enrich_discovery_sample(sample, [source])
    assert enriched[0]["student_prompt"] == source["student_prompt"]
    assert enriched[0]["gold_response"] == source["gold_response"]
    assert enriched[0]["gold_answer"] == source["gold_answer"]


def test_discovery_sample_covers_rare_observable_student_state():
    census = []
    for grade in ("6", "7", "8", "9"):
        for index in range(4):
            census.append(
                {
                    "benchmark_candidate_id": f"BC-{grade}-{index}",
                    "sample_id": f"S-{grade}-{index}",
                    "grade": grade,
                    "lesson": "Bài dữ liệu",
                    "position": "Mục 1",
                    "cognitive_band": "Hiểu",
                    "history_present": "true",
                    "history_turn_count": "2",
                    "history_depth_bin": "2",
                    "target_tutor_turn_index": "4",
                    "target_position_bin": "early_followup",
                    "content_form_signal": "data_information",
                    "student_state_signal": (
                        "student_reply_present;explicit_uncertainty"
                        if index == 0
                        else "student_reply_present;attempt_or_answer"
                    ),
                    "feature_method": "deterministic_regex_v1",
                }
            )
    selected = select_task_discovery_sample(census, per_grade=3, seed="fixed")
    for grade in ("6", "7", "8", "9"):
        grade_states = {
            row["student_state_signal"]
            for row in selected
            if row["grade"] == grade
        }
        assert "student_reply_present;explicit_uncertainty" in grade_states


def test_discovery_strata_reports_pool_and_sample_counts():
    census = [
        {"sample_id": "S1", "grade": "6", "history_present": "false"},
        {"sample_id": "S2", "grade": "6", "history_present": "true"},
    ]
    sample = [census[0]]
    rows = summarize_discovery_strata(census, sample)
    grade_rows = [
        row
        for row in rows
        if row["dimension"] == "grade" and row["value"] == "6"
    ]
    assert grade_rows == [
        {
            "scope": "full_pool",
            "dimension": "grade",
            "value": "6",
            "candidate_count": "2",
            "family_count": "2",
        },
        {
            "scope": "discovery_sample",
            "dimension": "grade",
            "value": "6",
            "candidate_count": "1",
            "family_count": "1",
        },
    ]

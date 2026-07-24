import json

import pytest

from edu_benchmark.benchmark_conversion.dialogue_split import (
    DialogueSplitError,
    parse_dialogue_turns,
    split_each_tutor_turn_candidates,
    split_final_tutor_response_candidate,
)


def conversion_row(dialogue):
    return {
        "sample_id": "S1",
        "source_batch": "test",
        "source_file": "source.xlsx",
        "source_row_number": "2",
        "grade": "6",
        "lesson": "Bài 1",
        "position": "Mục 1",
        "bloom_level": "Nhận biết",
        "answer_sgv": "Đáp án SGV",
        "raw_dialogue": dialogue,
        "raw_audit_blocking_evidence_fragment_ids": "[]",
        "raw_audit_all_evidence_fragment_ids": '["F1"]',
    }


def test_parser_preserves_turn_content_and_order():
    dialogue = "HS: Câu hỏi\nAI: Dòng một\nDòng hai\nHS: Em hiểu\nAI: Kết luận"
    turns = parse_dialogue_turns(dialogue)
    assert [(turn.role, turn.content) for turn in turns] == [
        ("student", "Câu hỏi"),
        ("tutor", "Dòng một\nDòng hai"),
        ("student", "Em hiểu"),
        ("tutor", "Kết luận"),
    ]


def test_final_ai_is_gold_response_and_answer_sgv_is_gold_answer():
    candidate = split_final_tutor_response_candidate(
        conversion_row("HS: Câu hỏi\nAI: Gợi ý\nHS: Trả lời\nAI: Phản hồi cuối")
    )
    assert candidate["student_prompt"] == "Câu hỏi"
    assert candidate["gold_response"] == "Phản hồi cuối"
    assert candidate["gold_answer"] == "Đáp án SGV"
    assert json.loads(candidate["conversation_history"])[-1]["content"] == "Trả lời"


@pytest.mark.parametrize(
    ("dialogue", "code"),
    [
        ("Teacher: Hello", "unknown_turn_label"),
        ("AI: Hello\nHS: Hi", "first_turn_not_student"),
        ("HS: Hello\nAI: Hi\nAI: Again", "non_alternating_roles"),
    ],
)
def test_invalid_labels_or_order_are_rejected_without_repair(dialogue, code):
    with pytest.raises(DialogueSplitError) as exc_info:
        parse_dialogue_turns(dialogue)
    assert exc_info.value.code == code


def test_common_parser_accepts_trailing_student_but_plan01_splitter_does_not():
    row = conversion_row("HS: Hello\nAI: Hi\nHS: Bye")
    assert parse_dialogue_turns(row["raw_dialogue"])[-1].role == "student"
    with pytest.raises(DialogueSplitError) as exc_info:
        split_final_tutor_response_candidate(row)
    assert exc_info.value.code == "last_turn_not_tutor"


def test_each_tutor_turn_split_uses_fixed_prompt_and_exact_prefix_history():
    candidates = split_each_tutor_turn_candidates(
        conversion_row(
            "HS: Q1\nAI: A2\nHS: Q3\nAI: A4\nHS: Q5\nAI: A6\nHS: trailing"
        )
    )
    assert [row["benchmark_candidate_id"] for row in candidates] == [
        "BC-S1-AI02",
        "BC-S1-AI04",
        "BC-S1-AI06",
    ]
    assert all(row["student_prompt"] == "Q1" for row in candidates)
    assert [json.loads(row["conversation_history"]) for row in candidates] == [
        [],
        [
            {"turn_index": 2, "role": "tutor", "content": "A2"},
            {"turn_index": 3, "role": "student", "content": "Q3"},
        ],
        [
            {"turn_index": 2, "role": "tutor", "content": "A2"},
            {"turn_index": 3, "role": "student", "content": "Q3"},
            {"turn_index": 4, "role": "tutor", "content": "A4"},
            {"turn_index": 5, "role": "student", "content": "Q5"},
        ],
    ]
    assert [row["gold_response"] for row in candidates] == ["A2", "A4", "A6"]
    assert "trailing" not in json.dumps(candidates, ensure_ascii=False)

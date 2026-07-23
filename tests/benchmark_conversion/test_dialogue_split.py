import json

import pytest

from edu_benchmark.benchmark_conversion.dialogue_split import (
    DialogueSplitError,
    parse_dialogue_turns,
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
        ("HS: Hello\nAI: Hi\nHS: Bye", "last_turn_not_tutor"),
    ],
)
def test_invalid_labels_or_order_are_rejected_without_repair(dialogue, code):
    with pytest.raises(DialogueSplitError) as exc_info:
        parse_dialogue_turns(dialogue)
    assert exc_info.value.code == code

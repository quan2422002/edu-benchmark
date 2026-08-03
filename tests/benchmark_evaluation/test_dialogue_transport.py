import json

import pytest

from src.edu_benchmark.benchmark_evaluation.dialogue_transport import (
    DialogueTransportError,
    build_native_conversation,
)


def test_empty_history_produces_one_user_message():
    conversation = build_native_conversation("Em cần giúp ạ.", "[]")
    assert conversation.as_list() == [
        {"role": "user", "content": "Em cần giúp ạ."}
    ]
    assert len(conversation.sha256) == 64


def test_history_preserves_each_turn_and_content():
    history = json.dumps(
        [
            {"turn_index": 2, "role": "tutor", "content": "Em thử gì rồi?"},
            {"turn_index": 3, "role": "student", "content": "Em thử A."},
        ],
        ensure_ascii=False,
    )
    conversation = build_native_conversation("Em bị lỗi.", history)
    assert conversation.as_list() == [
        {"role": "user", "content": "Em bị lỗi."},
        {"role": "assistant", "content": "Em thử gì rồi?"},
        {"role": "user", "content": "Em thử A."},
    ]
    assert history not in [message["content"] for message in conversation.as_list()]


@pytest.mark.parametrize(
    "history,error",
    [
        ("not-json", "valid JSON"),
        ("{}", "JSON list"),
        (
            '[{"turn_index":2,"role":"student","content":"x"}]',
            "alternate",
        ),
        (
            '[{"turn_index":2,"role":"tutor","content":"x"}]',
            "start and end",
        ),
        (
            (
                '[{"turn_index":3,"role":"tutor","content":"x"},'
                '{"turn_index":2,"role":"student","content":"y"}]'
            ),
            "increase strictly",
        ),
        (
            '[{"turn_index":2,"role":"teacher","content":"x"}]',
            "student or tutor",
        ),
    ],
)
def test_invalid_history_fails_closed(history, error):
    with pytest.raises(DialogueTransportError, match=error):
        build_native_conversation("Prompt", history)

from __future__ import annotations

from edu_benchmark.data_io.dialogue_text_normalization import (
    DIALOGUE_NORMALIZATION_VERSION,
    normalize_dialogue_text,
)


def test_normalization_removes_one_safe_annotation_for_both_supported_forms() -> None:
    raw = (
        "HS: [Tự đánh giá] Em chưa hiểu.<br>"
        "AI [Gợi ý từng bước]: Em hãy thử lại."
    )

    result = normalize_dialogue_text(raw)

    assert result.normalized_text == "HS: Em chưa hiểu.\nAI: Em hãy thử lại."
    assert result.annotation_count == 2
    assert result.flags == ()
    assert result.html_break_count == 1
    assert result.version == DIALOGUE_NORMALIZATION_VERSION
    assert result.raw_sha256 != result.normalized_sha256


def test_normalization_preserves_square_brackets_outside_speaker_annotation() -> None:
    raw = (
        "HS: Hãy dùng khối [lặp lại 10 lần].\n"
        "AI: Truy cập [trang này](url). Ví dụ AI: [không phải annotation] nội dung."
    )

    result = normalize_dialogue_text(raw)

    assert "[lặp lại 10 lần]" in result.normalized_text
    assert "[trang này](url)" in result.normalized_text
    assert "Ví dụ AI: [không phải annotation]" in result.normalized_text
    assert result.annotation_count == 0
    assert result.flags == ()


def test_normalization_flags_and_preserves_ambiguous_repeated_annotation() -> None:
    raw = "AI: [Gợi ý] [Đặt câu hỏi] Em thử lại."

    result = normalize_dialogue_text(raw)

    assert result.normalized_text == raw
    assert result.annotation_count == 0
    assert result.flags == ("ambiguous_speaker_annotation",)

    annotation_only = normalize_dialogue_text("AI: [Gợi ý từng bước]")
    assert annotation_only.normalized_text == "AI: [Gợi ý từng bước]"
    assert annotation_only.annotation_count == 0
    assert annotation_only.flags == ("ambiguous_speaker_annotation",)


def test_normalization_is_idempotent() -> None:
    first = normalize_dialogue_text("Học sinh: Em hỏi.<br>Gia sư: [Gợi ý] Em thử nhé.")
    second = normalize_dialogue_text(first.normalized_text)

    assert second.normalized_text == first.normalized_text
    assert second.annotation_count == 0
    assert second.flags == ()

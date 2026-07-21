from pathlib import Path

from edu_benchmark.data_io.xlsx import read_xlsx_rows, slug_header
from edu_benchmark.dialogue_audit.hnmu_audit import (
    bloom_band,
    coverage_rows,
    duplicate_rows,
    field_issues,
    lesson_code,
    lesson_key,
    load_dialogue_rows,
    load_topic_lesson_map,
    row_topic_lesson_metadata,
    speaker_labels,
)

RAW_DIR = Path("shared/raw_data/HNMU-teacher_dialog_samples")


def test_xlsx_reader_reads_hnmu_headers():
    rows = read_xlsx_rows(RAW_DIR / "Lớp 6.xlsx")
    assert rows
    assert rows[0][:7] == [
        "STT",
        "Bài",
        "Vị trí",
        "Câu hỏi",
        "Mức Bloom",
        "Đáp án (SGV)",
        "Hội thoại gia sư (Theo phương pháp Dàn giáo)",
    ]


def test_load_dialogue_rows_only_includes_grade_6_7():
    rows = load_dialogue_rows(sorted(RAW_DIR.glob("*.xlsx")), include_grades={"6", "7"})
    assert rows
    assert {row.grade for row in rows} == {"6", "7"}
    assert all("Lớp 8" not in row.source_file and "Lớp 9" not in row.source_file for row in rows)


def test_format_helpers_detect_bloom_and_speaker_labels():
    assert bloom_band("Nhận biết (Nêu được khái niệm)") == "Nhận biết"
    assert bloom_band("Thông hiểu (Giải thích)") == "Thông hiểu"
    assert bloom_band("Vận dụng") == "Vận dụng"
    assert speaker_labels("HS: Em hỏi.\n AI: Gia sư đáp.") == ["HS", "AI"]
    assert slug_header("Đáp án (SGV)") == "dap_an_sgv"


def test_lesson_mapping_uses_regex_only_with_a_b_suffixes():
    assert lesson_code("Bài 8A. Làm việc với danh sách dạng liệt kê") == "8A"
    assert lesson_code("Bài 8a: Làm việc với danh sách dạng liệt kê") == "8A"
    assert lesson_code("[8b] Làm quen với phần mềm chỉnh sửa ảnh") == "8B"
    assert lesson_code("10a. Sử dụng hàm Countif") == "10A"
    assert lesson_key("[10b]: Chuẩn bị dữ liệu và dựng video") == "bai_10b"

    rows = load_dialogue_rows([RAW_DIR / "Lớp 8.xlsx", RAW_DIR / "Lớp 9.xlsx"], include_grades={"8", "9"})
    by_lesson = {(row.grade, row.lesson): row for row in rows}
    topic_lesson_map = load_topic_lesson_map()

    assert row_topic_lesson_metadata(
        by_lesson[("8", "[8b] Làm quen với phần mềm chỉnh sửa ảnh")],
        topic_lesson_map,
    )["lesson_id"] == "TIN8-B08B"
    assert row_topic_lesson_metadata(
        by_lesson[("9", "10a. Sử dụng hàm Countif")],
        topic_lesson_map,
    )["lesson_id"] == "TIN9-B10A"


def test_field_issues_flag_missing_ai_label():
    row = load_dialogue_rows([RAW_DIR / "Lớp 6.xlsx"], include_grades={"6"})[0]
    bad = row.__class__(**{**row.to_dict(), "dialogue": "HS: Em hỏi thôi."})
    issues = field_issues(bad)
    assert any("AI" in issue["message"] for issue in issues)


def test_duplicate_rows_finds_exact_question_duplicate():
    rows = load_dialogue_rows([RAW_DIR / "Lớp 6.xlsx"], include_grades={"6"})[:2]
    clone = rows[0].__class__(**{**rows[1].to_dict(), "sample_id": "CLONE", "question": rows[0].question})
    duplicates = duplicate_rows([rows[0], clone], near_threshold=0.99)
    assert any(item["duplicate_type"] == "exact_question" for item in duplicates)


def test_coverage_rows_include_cross_grade_topic_and_grade_specific_lesson():
    rows = load_dialogue_rows([RAW_DIR / "Lớp 6.xlsx", RAW_DIR / "Lớp 7.xlsx"], include_grades={"6", "7"})
    coverage = coverage_rows(rows)
    dimensions = {item["dimension"] for item in coverage}
    assert "topic" in dimensions
    assert "lesson_by_grade" in dimensions

    lesson_rows = [item for item in coverage if item["dimension"] == "lesson_by_grade"]
    assert lesson_rows
    assert all(item["grade"] in {"6", "7"} for item in lesson_rows)
    assert all(item["lesson_label"] for item in lesson_rows)
    assert any(item["topic_label"] == "Giải quyết vấn đề với sự trợ giúp của máy tính" for item in coverage if item["dimension"] == "topic")

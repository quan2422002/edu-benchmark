from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from openpyxl import load_workbook

from edu_benchmark.learning_resources.fragment_markdown_v1 import (
    FRAGMENT_FIELDNAMES,
    SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES,
    SEMANTIC_REVIEW_WORKBOOK_SHEETS,
    build_semantic_boundary_review_workbook_from_csv,
    build_validate_and_write_v1,
    canonicalize_markdown,
    effective_content,
    fragment_manifest_row_v1,
    merge_short_fragments_v1_1,
    survey_fragment_v1_1_candidates,
    survey_fragment_v1_1_with_semantic_review,
    validate_fragment_bundle_v1_1,
    write_fragment_v1_1_survey,
)


MANIFEST_FIELDS = [
    "ocr_text_id",
    "learning_material_id",
    "material_type",
    "grade",
    "book_title",
    "lesson_key",
    "lesson_number",
    "lesson_title",
    "topic_title",
    "source_markdown_path",
    "source_metadata_path",
    "image_dir",
    "page_marker_count",
    "page_stat_count",
    "table_count",
    "image_count",
    "first_heading",
    "status",
    "notes",
]


def _manifest_row(markdown_path: Path) -> dict[str, str]:
    return {
        "ocr_text_id": "OCR-SGK-TIN6-BAI02",
        "learning_material_id": "LM-SGK-TIN6-0001",
        "material_type": "SGK",
        "grade": "6",
        "book_title": "Sách giáo khoa Tin học 6",
        "lesson_key": "bai_02",
        "lesson_number": "2",
        "lesson_title": "Bài 2. Xử lý thông tin",
        "topic_title": "Chủ đề 1. Máy tính và cộng đồng",
        "source_markdown_path": markdown_path.as_posix(),
        "source_metadata_path": "",
        "image_dir": "",
        "page_marker_count": "2",
        "page_stat_count": "0",
        "table_count": "1",
        "image_count": "0",
        "first_heading": "BÀI 2",
        "status": "draft",
        "notes": "",
    }


def _write_manifest(path: Path, row: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerow(row)


def test_page_markers_are_removed_without_splitting_mid_paragraph(tmp_path: Path) -> None:
    source = (
        "{1}------------------------------------------------\n"
        "# BÀI 2\n\n"
        "Đây là một câu đang viết dở\n\n"
        "{2}------------------------------------------------\n"
        "và tiếp tục ở trang sau.\n"
    )
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(source, encoding="utf-8")

    fragments, _, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    assert "{1}" not in canonical.text
    assert "{2}" not in canonical.text
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text
    assert len(fragments) == 1
    assert json.loads(fragments[0]["page_markers_json"]) == ["1", "2"]


def test_metadata_prefix_suppresses_duplicate_topic_and_lesson_headings(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# CHỦ ĐỀ 1. MÁY TÍNH VÀ CỘNG ĐỒNG\n"
        "## BÀI 2\n"
        "### XỬ LÝ THÔNG TIN\n"
        "Nội dung.\n",
        encoding="utf-8",
    )

    fragments, sections, _ = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    expected = "Chủ đề 1. Máy tính và cộng đồng > Bài 2. Xử lý thông tin"
    assert {row["section_path"] for row in fragments} == {expected}


def test_table_caption_is_final_path_component_and_part_of_table_fragment(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown = (
        "# BÀI 2\n\n"
        "## 1. CÁC HOẠT ĐỘNG XỬ LÝ THÔNG TIN\n\n"
        "Đoạn dẫn.\n\n"
        "Bảng 2.1. Các hoạt động xử lý thông tin\n\n"
        "| Hoạt động | Ví dụ |\n"
        "|---|---|\n"
        "| Thu nhận | Quan sát |\n\n"
        "Đoạn sau bảng.\n"
    )
    markdown_path.write_text(markdown, encoding="utf-8")

    fragments, sections, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["table_caption"] == "Bảng 2.1. Các hoạt động xử lý thông tin"
    assert table["caption_status"] == "exact"
    assert table["caption_position"] == "before"
    assert table["section_path"].split(" > ")[-1] == table["table_caption"]
    assert table["markdown_text"].startswith("Bảng 2.1.")
    assert "| Hoạt động | Ví dụ |" in table["markdown_text"]
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text
    assert any(
        row["section_kind"] == "table_caption"
        and row["section_label"] == table["table_caption"]
        for row in sections
    )


def test_table_without_source_caption_uses_review_locator(tmp_path: Path) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n",
        encoding="utf-8",
    )

    fragments, sections, _ = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["caption_status"] == "missing"
    assert table["caption_position"] == "none"
    assert table["table_caption"] == "Bảng chưa có caption nguồn [T0001]"
    assert not table["section_path"].endswith(table["table_caption"])
    assert not any(row["section_kind"] == "table_caption" for row in sections)
    assert table["needs_hnmu_review"] == "true"


def test_sentence_starting_with_bang_tinh_is_not_misclassified_as_caption(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "Bảng tính cuối cùng có thể tương tự như hình minh họa.\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n",
        encoding="utf-8",
    )

    fragments, _, _ = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["caption_status"] == "missing"
    assert table["table_caption"] == "Bảng chưa có caption nguồn [T0001]"


def test_instruction_starting_with_hinh_is_not_misclassified_as_caption(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "Hình 7.1 và Hình 7.2 mô tả dữ liệu. Em hãy nhận xét.\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "Hình 11a.1 là trang tính mẫu. Theo em công thức nào đúng?\n",
        encoding="utf-8",
    )

    fragments, _, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["caption_status"] == "missing"
    assert table["table_caption"] == "Bảng chưa có caption nguồn [T0001]"
    assert "Hình 7.1 và Hình 7.2" not in table["markdown_text"]
    assert "Hình 11a.1 là" not in table["markdown_text"]
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_hinh_caption_after_table_is_part_of_table_fragment(tmp_path: Path) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "Hình 2.1. Kết quả trang tính\n",
        encoding="utf-8",
    )

    fragments, sections, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["caption_status"] == "exact"
    assert table["caption_position"] == "after"
    assert table["table_caption"] == "Hình 2.1. Kết quả trang tính"
    assert table["markdown_text"].rstrip().endswith(table["table_caption"])
    assert table["section_path"].split(" > ")[-1] == table["table_caption"]
    assert any(row["section_kind"] == "table_caption" for row in sections)
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_hinh_caption_between_tables_belongs_only_to_previous_table(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "Hình 2.1. Kết quả thứ nhất\n\n"
        "| C | D |\n"
        "|---|---|\n"
        "| 3 | 4 |\n\n"
        "Hình 2.2. Kết quả thứ hai\n",
        encoding="utf-8",
    )

    fragments, _, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    tables = [row for row in fragments if row["fragment_type"] == "table"]
    assert [row["table_caption"] for row in tables] == [
        "Hình 2.1. Kết quả thứ nhất",
        "Hình 2.2. Kết quả thứ hai",
    ]
    assert [row["caption_position"] for row in tables] == ["after", "after"]
    assert "Hình 2.1." in tables[0]["markdown_text"]
    assert "Hình 2.1." not in tables[1]["markdown_text"]
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_bang_caption_between_tables_belongs_only_to_following_table(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "Bảng 2.2. Dữ liệu thứ hai\n\n"
        "| C | D |\n"
        "|---|---|\n"
        "| 3 | 4 |\n",
        encoding="utf-8",
    )

    fragments, _, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    tables = [row for row in fragments if row["fragment_type"] == "table"]
    assert tables[0]["caption_status"] == "missing"
    assert tables[0]["caption_position"] == "none"
    assert tables[1]["table_caption"] == "Bảng 2.2. Dữ liệu thứ hai"
    assert tables[1]["caption_position"] == "before"
    assert "Bảng 2.2." not in tables[0]["markdown_text"]
    assert tables[1]["markdown_text"].startswith("Bảng 2.2.")
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_short_adjacent_source_caption_is_traceable_and_lossless(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# BÀI 2\n\n"
        "| Đơn vị | Giá trị |\n"
        "|---|---|\n"
        "| KB | 1024 byte |\n\n"
        "Byte và các bội của byte\n",
        encoding="utf-8",
    )

    fragments, _, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["caption_status"] == "adjacent_source"
    assert table["caption_position"] == "after"
    assert table["table_caption"] == "Byte và các bội của byte"
    assert table["caption_source_markdown"] == "Byte và các bội của byte"
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text
    manifest_path = tmp_path / "manifest.csv"
    _write_manifest(manifest_path, _manifest_row(markdown_path))
    summary = build_validate_and_write_v1(
        manifest_path=manifest_path,
        output_dir=tmp_path / "outputs",
        repo_root=tmp_path,
    )
    assert summary["adjacent_source_table_caption_count"] == 1


def test_sbt_exercises_are_distinct_exact_section_scopes(tmp_path: Path) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# PHẦN I — ĐỀ BÀI\n\n"
        "## B. BÀI TẬP VÀ THỰC HÀNH\n\n"
        "**10a.1.** Câu hỏi thứ nhất.\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "10a.2. Câu hỏi thứ hai.\n\n"
        "# PHẦN II — HƯỚNG DẪN GIẢI\n\n"
        "10a.1. Lời giải thứ nhất.\n\n"
        "10a.2. Lời giải thứ hai.\n",
        encoding="utf-8",
    )
    manifest_row = _manifest_row(markdown_path)
    manifest_row["material_type"] = "SBT"

    fragments, _, canonical = fragment_manifest_row_v1(
        manifest_row,
        repo_root=tmp_path,
    )

    exercise_paths = {
        row["section_path"]
        for row in fragments
        if "10a." in row["section_path"]
    }
    assert any(
        "PHẦN I — ĐỀ BÀI" in path and path.endswith("10a.1.")
        for path in exercise_paths
    )
    assert any(
        "PHẦN I — ĐỀ BÀI" in path and path.endswith("10a.2.")
        for path in exercise_paths
    )
    assert any(
        "PHẦN II — HƯỚNG DẪN GIẢI" in path and path.endswith("10a.1.")
        for path in exercise_paths
    )
    assert any(
        "PHẦN II — HƯỚNG DẪN GIẢI" in path and path.endswith("10a.2.")
        for path in exercise_paths
    )
    table = next(row for row in fragments if row["fragment_type"] == "table")
    assert table["section_path"].endswith("10a.1.")
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_sbt_exercise_is_inserted_once_before_nested_headings(tmp_path: Path) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# PHẦN II — HƯỚNG DẪN GIẢI\n\n"
        "8.17. Lời giải.\n\n"
        "#### Hướng dẫn:\n\n"
        "##### Bước 1. Chuẩn bị\n\n"
        "Nội dung.\n",
        encoding="utf-8",
    )
    manifest_row = _manifest_row(markdown_path)
    manifest_row["material_type"] = "SBT"

    fragments, _, canonical = fragment_manifest_row_v1(
        manifest_row,
        repo_root=tmp_path,
    )

    nested = next(row for row in fragments if "Bước 1" in row["section_path"])
    assert nested["section_path"].endswith(
        "8.17. > Hướng dẫn: > Bước 1. Chuẩn bị"
    )
    assert nested["section_path"].count("8.17.") == 1
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_equivalent_nested_heading_does_not_repeat_section_component(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "## Hướng dẫn\n\n"
        "Nội dung chung.\n\n"
        "### Hướng dẫn\n\n"
        "Nội dung cụ thể.\n",
        encoding="utf-8",
    )

    fragments, _, canonical = fragment_manifest_row_v1(
        _manifest_row(markdown_path),
        repo_root=tmp_path,
    )

    assert all("Hướng dẫn > Hướng dẫn" not in row["section_path"] for row in fragments)
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_heading_only_tail_before_sbt_segment_does_not_change_section_path(
    tmp_path: Path,
) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text(
        "# PHẦN I — ĐỀ BÀI\n\n"
        "## B. BÀI TẬP VÀ THỰC HÀNH\n\n"
        "Nội dung bài tập.\n\n"
        "##### ỨNG DỤNG TIN HỌC\n\n"
        '<!-- edu-benchmark:sbt-segment role="loi_giai" -->\n'
        "# PHẦN II — HƯỚNG DẪN GIẢI\n\n"
        "Lời giải.\n",
        encoding="utf-8",
    )
    manifest_row = _manifest_row(markdown_path)
    manifest_row["material_type"] = "SBT"

    fragments, _, canonical = fragment_manifest_row_v1(
        manifest_row,
        repo_root=tmp_path,
    )

    stray_text = next(
        row for row in fragments if "ỨNG DỤNG TIN HỌC" in row["markdown_text"]
    )
    assert "ỨNG DỤNG TIN HỌC" not in stray_text["section_path"]
    assert "B. BÀI TẬP VÀ THỰC HÀNH" in stray_text["section_path"]
    assert "".join(row["markdown_text"] for row in fragments) == canonical.text


def test_short_content_is_kept_and_bundle_validates(tmp_path: Path) -> None:
    markdown_path = tmp_path / "lesson.md"
    markdown_path.write_text("# BÀI 2\n\nx\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.csv"
    _write_manifest(manifest_path, _manifest_row(markdown_path))
    output_dir = tmp_path / "outputs"

    summary = build_validate_and_write_v1(
        manifest_path=manifest_path,
        output_dir=output_dir,
        repo_root=tmp_path,
    )

    assert summary["lossless"] is True
    assert summary["reconstructed_unit_count"] == 1
    assert (output_dir / "learning_sections_v1.csv").is_file()
    assert (output_dir / "learning_resource_fragments_v1.csv").is_file()
    assert (output_dir / "fragment_validation_summary.json").is_file()
    with (output_dir / "learning_resource_fragments_v1.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert list(rows[0]) == FRAGMENT_FIELDNAMES
    assert "x\n" in "".join(row["markdown_text"] for row in rows)


def test_canonicalization_preserves_all_non_marker_characters() -> None:
    source = "before\n{12}-----\nafter\n"
    canonical = canonicalize_markdown(source)

    assert canonical.text == "before\nafter\n"
    assert canonical.page_markers[0].page_id == "12"


def _source_fragment(
    fragment_id: str,
    *,
    fragment_index: int,
    char_start: int,
    markdown_text: str,
    section_path: str = "Chủ đề 1 > Bài 1 > Mục 1",
    fragment_type: str = "text",
    caption_status: str = "not_applicable",
    table_caption: str = "",
    material_type: str = "SGK",
) -> dict[str, str]:
    row = {field: "" for field in FRAGMENT_FIELDNAMES}
    row.update(
        {
            "fragment_id": fragment_id,
            "section_id": "SECTION-1",
            "learning_material_id": "LM-1",
            "ocr_text_id": "OCR-1",
            "material_type": material_type,
            "grade": "6",
            "canonical_version": "learning-resource-markdown-v1",
            "fragment_index": str(fragment_index),
            "order_index": str(fragment_index),
            "char_start": str(char_start),
            "char_end": str(char_start + len(markdown_text)),
            "page_markers_json": "[]",
            "section_label": section_path.rsplit(" > ", 1)[-1],
            "section_path": section_path,
            "section_depth": str(section_path.count(" > ") + 1),
            "fragment_type": fragment_type,
            "caption_status": caption_status,
            "table_caption": table_caption,
            "markdown_text": markdown_text,
            "text_preview": markdown_text,
            "status": "draft",
            "needs_hnmu_review": "true",
        }
    )
    return row


def test_effective_content_exclusions_are_measurement_only() -> None:
    source = (
        '<!-- edu-benchmark:sbt-segment role="de_bai" -->\n'
        "<!-- ghi chú HTML\n"
        "nhiều dòng -->\n"
        "# Tiêu đề bị lẫn\n"
        "![ảnh](images/page.jpg)\n"
        "Trang 12\n"
        "**Nội dung thực** và [liên kết](https://example.com).\n"
    )

    measured = effective_content(source)

    assert measured == "Nội dung thực và liên kết."
    assert "edu-benchmark:sbt-segment" in source
    assert "ghi chú HTML" in source
    assert "# Tiêu đề bị lẫn" in source
    assert "![ảnh]" in source


def test_html_comment_only_fragment_is_structural_zero() -> None:
    structural = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text='<!-- edu-benchmark:sbt-segment role="de_bai" -->\n',
    )
    content = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(structural["char_end"]),
        markdown_text="Nội dung đủ dài để đứng độc lập.\n",
    )

    merged, summary = merge_short_fragments_v1_1(
        [structural, content],
        text_min_effective_chars=20,
        text_max_effective_chars=100,
        table_absorption_max_effective_chars=0,
        neighbor_policy="prefer_short_group",
    )

    assert len(merged) == 2
    assert merged[0]["markdown_text"] == structural["markdown_text"]
    assert merged[0]["effective_content_length"] == 0
    assert merged[0]["merge_status"] == "structural_zero"
    assert summary["source_structural_zero_count"] == 1


def test_v1_1_iteratively_merges_short_text_and_preserves_lineage() -> None:
    first = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="aa\n",
    )
    second = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first["char_end"]),
        markdown_text="bb\n",
    )
    third = _source_fragment(
        "OCR-1#V1F0003",
        fragment_index=3,
        char_start=int(second["char_end"]),
        markdown_text="cc\n",
    )

    merged, summary = merge_short_fragments_v1_1(
        [first, second, third],
        text_min_effective_chars=6,
        text_max_effective_chars=20,
        table_absorption_max_effective_chars=0,
        neighbor_policy="prefer_short_group",
    )
    serialized = [{key: str(value) for key, value in row.items()} for row in merged]
    validation = validate_fragment_bundle_v1_1(
        source_rows=[first, second, third],
        fragment_rows=serialized,
        text_min_effective_chars=6,
        text_max_effective_chars=20,
        table_absorption_max_effective_chars=0,
        neighbor_policy="prefer_short_group",
    )

    assert len(merged) == 1
    assert merged[0]["markdown_text"] == (
        first["markdown_text"] + second["markdown_text"] + third["markdown_text"]
    )
    assert json.loads(merged[0]["merged_from_fragment_ids_json"]) == [
        first["fragment_id"],
        second["fragment_id"],
        third["fragment_id"],
    ]
    assert json.loads(merged[0]["source_fragment_types_json"]) == [
        "text",
        "text",
        "text",
    ]
    assert merged[0]["fragment_release"] == "v1.1"
    assert merged[0]["merge_policy_version"] == (
        "fragment-v1.1-structural-bounded-v4"
    )
    assert summary["merge_contract"]["merge_policy_version"] == (
        "fragment-v1.1-structural-bounded-v4"
    )
    assert summary["merged_group_count"] == 1
    assert summary["merge_created_over_max_count"] == 0
    assert validation["lineage_covers_source_exactly_once"] is True
    assert validation["lossless"] is True


def test_v1_1_structural_zero_does_not_initiate_merge() -> None:
    structural = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="# Heading only\n",
    )
    content = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(structural["char_end"]),
        markdown_text="Nội dung đủ dài để đứng độc lập.\n",
    )

    merged, _ = merge_short_fragments_v1_1(
        [structural, content],
        text_min_effective_chars=10,
        text_max_effective_chars=100,
        table_absorption_max_effective_chars=0,
        neighbor_policy="prefer_previous",
    )

    assert len(merged) == 2
    assert merged[0]["merge_status"] == "structural_zero"


def test_v1_1_respects_cap_and_exact_section_scope() -> None:
    first = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="abcdef\n",
    )
    second = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first["char_end"]),
        markdown_text="ghijkl\n",
    )
    third = _source_fragment(
        "OCR-1#V1F0003",
        fragment_index=3,
        char_start=int(second["char_end"]),
        markdown_text="ij\n",
        section_path="Chủ đề 1 > Bài 1 > Mục 2",
    )

    merged, _ = merge_short_fragments_v1_1(
        [first, second, third],
        text_min_effective_chars=10,
        text_max_effective_chars=10,
        table_absorption_max_effective_chars=0,
        neighbor_policy="prefer_previous",
    )

    assert len(merged) == 3
    assert merged[0]["merge_status"] == "short_unmerged_cap"
    assert merged[2]["merge_status"] == "short_unmerged_scope"


def test_v1_1_absorbs_one_short_uncaptioned_table_into_text() -> None:
    text = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="Bài tập ngắn.\n",
    )
    table = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(text["char_end"]),
        markdown_text="| A | B |\n|---|---|\n| 1 | 2 |\n",
        fragment_type="table",
        caption_status="missing",
        table_caption="Bảng chưa có caption nguồn [T0001]",
    )

    merged, summary = merge_short_fragments_v1_1(
        [text, table],
        text_min_effective_chars=30,
        text_max_effective_chars=100,
        table_absorption_max_effective_chars=30,
        neighbor_policy="prefer_next",
    )

    assert len(merged) == 1
    assert merged[0]["fragment_type"] == "text"
    assert json.loads(merged[0]["source_fragment_types_json"]) == ["text", "table"]
    assert merged[0]["merge_reason"] == "short_table_absorption"
    assert summary["absorbed_table_count"] == 1


def test_v1_1_merges_explicit_table_context_independently_of_table_length() -> None:
    prompt = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="Các giá trị được biểu diễn trong bảng sau:\n",
    )
    table = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(prompt["char_end"]),
        markdown_text=(
            "| Tên | Giá trị mô tả dài |\n"
            "|---|---|\n"
            "| A | Nội dung đủ dài để vượt ngưỡng hấp thụ bảng |\n"
        ),
        fragment_type="table",
        caption_status="missing",
        table_caption="Bảng chưa có caption nguồn [T0001]",
    )

    merged, summary = merge_short_fragments_v1_1(
        [prompt, table],
        text_min_effective_chars=20,
        text_max_effective_chars=1500,
        table_absorption_max_effective_chars=10,
        neighbor_policy="prefer_short_group",
    )
    serialized = [{key: str(value) for key, value in row.items()} for row in merged]
    validation = validate_fragment_bundle_v1_1(
        source_rows=[prompt, table],
        fragment_rows=serialized,
        text_min_effective_chars=20,
        text_max_effective_chars=1500,
        table_absorption_max_effective_chars=10,
        neighbor_policy="prefer_short_group",
    )

    assert len(merged) == 1
    assert merged[0]["merge_reason"] == "explicit_table_context"
    assert summary["explicit_table_context_merge_count"] == 1
    assert validation["lossless"] is True


def test_v1_1_merges_heading_only_context_before_table() -> None:
    heading = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="### Các thiết bị vào\n",
    )
    table = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(heading["char_end"]),
        markdown_text="| Thiết bị | Chức năng |\n|---|---|\n| Chuột | Nhập |\n",
        fragment_type="table",
        caption_status="missing",
    )

    merged, summary = merge_short_fragments_v1_1(
        [heading, table],
        text_min_effective_chars=20,
        text_max_effective_chars=1500,
        table_absorption_max_effective_chars=10,
        neighbor_policy="prefer_short_group",
    )

    assert len(merged) == 1
    assert merged[0]["merge_reason"] == "explicit_table_context"
    assert summary["explicit_table_context_merge_count"] == 1


def test_v1_1_does_not_pull_following_prompt_into_previous_table() -> None:
    first_table = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text=(
            "| Cột A | Nội dung đủ dài |\n"
            "|---|---|\n"
            "| 1 | Bảng thứ nhất không thuộc lời dẫn sau |\n"
        ),
        fragment_type="table",
        caption_status="missing",
    )
    next_prompt = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first_table["char_end"]),
        markdown_text="Kết quả tiếp theo:\n",
    )
    second_table = _source_fragment(
        "OCR-1#V1F0003",
        fragment_index=3,
        char_start=int(next_prompt["char_end"]),
        markdown_text="| Cột B |\n|---|\n| 2 |\n",
        fragment_type="table",
        caption_status="missing",
    )

    merged, summary = merge_short_fragments_v1_1(
        [first_table, next_prompt, second_table],
        text_min_effective_chars=20,
        text_max_effective_chars=1500,
        table_absorption_max_effective_chars=10,
        neighbor_policy="prefer_short_group",
    )

    assert len(merged) == 2
    assert json.loads(merged[0]["merged_from_fragment_ids_json"]) == [
        first_table["fragment_id"]
    ]
    assert json.loads(merged[1]["merged_from_fragment_ids_json"]) == [
        next_prompt["fragment_id"],
        second_table["fragment_id"],
    ]
    assert summary["explicit_table_context_merge_count"] == 1


def test_v1_1_does_not_absorb_zero_content_neighbors_into_short_table() -> None:
    structural_markdowns = (
        "\n",
        "Trang 12\n",
        '<!-- edu-benchmark:sbt-segment role="de_bai" -->\n',
        "![Minh họa](images/page_12.jpg)\n",
    )
    for case_index, structural_markdown in enumerate(structural_markdowns, start=1):
        structural = _source_fragment(
            f"OCR-1#V1F{case_index * 2 - 1:04d}",
            fragment_index=1,
            char_start=0,
            markdown_text=structural_markdown,
        )
        short_table = _source_fragment(
            f"OCR-1#V1F{case_index * 2:04d}",
            fragment_index=2,
            char_start=int(structural["char_end"]),
            markdown_text="| A |\n|---|\n| 1 |\n",
            fragment_type="table",
            caption_status="missing",
        )

        merged, summary = merge_short_fragments_v1_1(
            [structural, short_table],
            text_min_effective_chars=20,
            text_max_effective_chars=1500,
            table_absorption_max_effective_chars=50,
            neighbor_policy="prefer_short_group",
        )

        assert len(merged) == 2
        assert summary["absorbed_table_count"] == 0
        assert merged[0]["merge_status"] == "structural_zero"


def test_v1_1_never_merges_tables_with_each_other_or_captioned_table() -> None:
    first = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="| A |\n|---|\n| 1 |\n",
        fragment_type="table",
        caption_status="missing",
    )
    second = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first["char_end"]),
        markdown_text="Bảng 1. Dữ liệu\n| B |\n|---|\n| 2 |\n",
        fragment_type="table",
        caption_status="exact",
        table_caption="Bảng 1. Dữ liệu",
    )

    merged, summary = merge_short_fragments_v1_1(
        [first, second],
        text_min_effective_chars=50,
        text_max_effective_chars=100,
        table_absorption_max_effective_chars=50,
        neighbor_policy="prefer_previous",
    )

    assert len(merged) == 2
    assert summary["table_table_merged_group_count"] == 0


def test_v1_1_survey_simulates_explicit_policy_grid() -> None:
    first = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="x\n",
    )
    second = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first["char_end"]),
        markdown_text="y\n",
    )
    survey = survey_fragment_v1_1_candidates(
        [first, second],
        text_min_thresholds=[5],
        text_max_thresholds=[20],
        table_absorption_thresholds=[0],
        neighbor_policies=["prefer_short_group", "prefer_previous"],
    )

    assert survey["merge_scope"] == (
        "contiguous+exact_ocr_text_id+exact_canonical_section_path"
    )
    assert len(survey["simulation_results"]) == 2
    assert survey["table_table_merge_enabled"] is False


def test_v1_1_semantic_boundary_review_is_deterministic_and_unlabeled() -> None:
    first = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="aa\n",
    )
    second = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first["char_end"]),
        markdown_text="bb\n",
    )
    third = _source_fragment(
        "OCR-1#V1F0003",
        fragment_index=3,
        char_start=int(second["char_end"]),
        markdown_text="x" * 25 + "\n",
    )
    kwargs = {
        "text_min_thresholds": [5],
        "text_max_thresholds": [20],
        "table_absorption_thresholds": [0],
        "neighbor_policies": ["prefer_short_group"],
        "lower_samples_per_threshold": 2,
        "upper_samples_per_threshold": 2,
    }

    survey, review_rows = survey_fragment_v1_1_with_semantic_review(
        [first, second, third],
        **kwargs,
    )
    _, repeated_rows = survey_fragment_v1_1_with_semantic_review(
        [first, second, third],
        **kwargs,
    )

    assert survey["semantic_boundary_review"]["row_count"] == 4
    assert survey["semantic_boundary_review"]["lower_row_count"] == 2
    assert survey["semantic_boundary_review"]["upper_row_count"] == 2
    assert survey["semantic_boundary_review"]["automatic_semantic_labels"] is False
    assert [row["review_id"] for row in review_rows] == [
        row["review_id"] for row in repeated_rows
    ]
    assert {row["boundary_side"] for row in review_rows} == {
        "at_or_below",
        "above",
        "merged_at_or_below",
        "source_above",
    }
    assert all(row["review_status"] == "pending" for row in review_rows)
    lower_rows = [
        row for row in review_rows if row["boundary_kind"] == "lower_minimum"
    ]
    upper_rows = [
        row for row in review_rows if row["boundary_kind"] == "upper_maximum"
    ]
    assert all(row["review_self_contained_evidence"] == "" for row in lower_rows)
    assert all(row["review_semantic_focus"] == "" for row in upper_rows)
    assert next(
        row for row in review_rows if row["boundary_side"] == "merged_at_or_below"
    )["source_fragment_count"] == 2


def test_v1_1_survey_writer_hash_locks_semantic_review_csv(tmp_path: Path) -> None:
    first = _source_fragment(
        "OCR-1#V1F0001",
        fragment_index=1,
        char_start=0,
        markdown_text="aa\n",
    )
    second = _source_fragment(
        "OCR-1#V1F0002",
        fragment_index=2,
        char_start=int(first["char_end"]),
        markdown_text="bb\n",
    )
    third = _source_fragment(
        "OCR-1#V1F0003",
        fragment_index=3,
        char_start=int(second["char_end"]),
        markdown_text="x" * 25 + "\n",
    )
    fragments_path = tmp_path / "fragments.csv"
    with fragments_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAGMENT_FIELDNAMES)
        writer.writeheader()
        writer.writerows([first, second, third])
    validation_path = tmp_path / "validation.json"
    validation_path.write_text(
        json.dumps(
            {
                "lossless": True,
                "fragments_sha256": hashlib.sha256(
                    fragments_path.read_bytes()
                ).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    survey_path = tmp_path / "survey.json"
    review_path = tmp_path / "semantic_review.csv"
    workbook_path = tmp_path / "semantic_review.xlsx"

    survey = write_fragment_v1_1_survey(
        fragments_path=fragments_path,
        validation_summary_path=validation_path,
        output_path=survey_path,
        text_min_thresholds=[5],
        text_max_thresholds=[20],
        table_absorption_thresholds=[0],
        neighbor_policies=["prefer_short_group"],
        semantic_review_output_path=review_path,
        semantic_review_workbook_output_path=workbook_path,
        lower_semantic_samples_per_threshold=2,
        upper_semantic_samples_per_threshold=2,
    )

    assert survey_path.is_file()
    assert review_path.is_file()
    assert workbook_path.is_file()
    assert survey["semantic_boundary_review"]["review_sha256"] == hashlib.sha256(
        review_path.read_bytes()
    ).hexdigest()
    with review_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        review_rows = list(reader)
    assert reader.fieldnames == SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES
    assert len(review_rows) == 4
    assert survey["semantic_boundary_review"][
        "human_review_workbook_sha256"
    ] == hashlib.sha256(workbook_path.read_bytes()).hexdigest()

    workbook = load_workbook(workbook_path)
    assert tuple(workbook.sheetnames) == SEMANTIC_REVIEW_WORKBOOK_SHEETS
    assert workbook["Cận dưới"].max_row == 3
    assert workbook["Cận dưới"].max_column == 12
    assert workbook["Cận trên"].max_row == 3
    assert workbook["Cận trên"].max_column == 13
    assert len(workbook["Cận dưới"].data_validations.dataValidation) == 1
    assert len(workbook["Cận trên"].data_validations.dataValidation) == 2
    workbook.close()


def test_existing_semantic_review_csv_projects_to_compact_workbook(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "review.csv"
    rows = []
    for boundary_kind, boundary_side, review_id in (
        ("lower_minimum", "above", "SBR-LOWER-0020-test"),
        ("upper_maximum", "source_above", "SBR-UPPER-0500-test"),
    ):
        row = {field: "" for field in SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES}
        row.update(
            {
                "review_id": review_id,
                "review_contract_version": "test",
                "boundary_kind": boundary_kind,
                "threshold_effective_chars": "20" if boundary_kind == "lower_minimum" else "500",
                "boundary_side": boundary_side,
                "in_primary_window": "false",
                "grade": "6",
                "material_type": "SGK",
                "lesson_title": "Bài 1. Thông tin và dữ liệu",
                "section_path": "Chủ đề 1 > Bài 1 > Mục 1",
                "effective_content_length": "21" if boundary_kind == "lower_minimum" else "501",
                "markdown_text": "<!-- marker -->\n### Mục 1\n\nNội dung **cần xem**.\n\n![](images/a.jpg)\n",
                "review_status": "pending",
            }
        )
        rows.append(row)
    with source_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    output_path = tmp_path / "review.xlsx"
    summary = build_semantic_boundary_review_workbook_from_csv(
        source_path,
        output_path,
    )

    assert summary["row_count"] == 2
    assert summary["maximum_review_columns"] == 13
    workbook = load_workbook(output_path)
    assert tuple(workbook.sheetnames) == SEMANTIC_REVIEW_WORKBOOK_SHEETS
    assert workbook["Cận dưới"]["I2"].value == "Mục 1\n\nNội dung cần xem.\n\n[Hình ảnh]"
    assert "mẫu dự phòng" in workbook["Cận dưới"]["C2"].value
    assert workbook["Cận dưới"]["J2"].value is None
    assert workbook["Cận trên"]["J2"].value is None
    assert workbook["Cận trên"]["K2"].value is None
    workbook.close()

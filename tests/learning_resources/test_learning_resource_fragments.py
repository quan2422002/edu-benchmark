from __future__ import annotations

import csv
from pathlib import Path

from edu_benchmark.learning_resources.fragment_markdown import build_fragments, write_fragments


def test_fragment_markdown_creates_traceable_fragments(tmp_path: Path) -> None:
    md = tmp_path / "lesson.md"
    md.write_text(
        "{0}------------------------------------------------\n"
        "# BÀI 17\n\n"
        "## CHƯƠNG TRÌNH MÁY TÍNH\n\n"
        "Chương trình là mô tả thuật toán để máy tính hiểu và thực hiện được.\n\n"
        "| Công việc | Mô tả |\n|---|---|\n| Nhập dữ liệu | Hỏi giá trị |\n"
        "71\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "ocr_text_id,learning_material_id,material_type,grade,book_title,lesson_key,lesson_number,lesson_title,topic_title,source_markdown_path,source_metadata_path,image_dir,page_marker_count,page_stat_count,table_count,image_count,first_heading,status,notes\n"
        f"OCR-SGK-TIN6-BAI17,LM-SGK-TIN6-0001,SGK,6,Sách giáo khoa Tin học 6,bai_17,17,Bài 17. Chương trình máy tính,,{md.as_posix()},,,1,1,1,0,BÀI 17,draft,\n",
        encoding="utf-8",
    )

    rows = build_fragments(manifest)

    assert rows
    assert all(row["learning_material_id"] == "LM-SGK-TIN6-0001" for row in rows)
    assert len({row["fragment_id"] for row in rows}) == len(rows)
    assert any(row["fragment_type"] == "table" for row in rows)
    assert all(row["location_note"] for row in rows)

    output = tmp_path / "fragments.csv"
    write_fragments(rows, output)
    with output.open("r", encoding="utf-8", newline="") as f:
        assert list(csv.DictReader(f))

from __future__ import annotations

import csv
from pathlib import Path

from edu_benchmark.learning_resources.ocr_text_manifest import build_manifest_rows, write_manifest


def test_build_manifest_from_minimal_ocr_tree(tmp_path: Path) -> None:
    root = tmp_path / "ocr_text"
    lesson = root / "sgk_tin_hoc_6" / "tin_6_bai_1"
    lesson.mkdir(parents=True)
    (lesson / "tin_6_bai_1.md").write_text(
        "{0}------------------------------------------------\n# CHỦ ĐỀ 1. MÁY TÍNH VÀ CỘNG ĐỒNG\n\n## BÀI 1\n\n### THÔNG TIN VÀ DỮ LIỆU\n\nNội dung bài học.\n",
        encoding="utf-8",
    )
    (lesson / "tin_6_bai_1.metadata.json").write_text('{"page_stats": [{"page_id": 0, "num_blocks": 3}]}\n', encoding="utf-8")
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "learning_material_id,source_title,material_type,grade,source_url,source_key,local_file_path,version_label,status,notes\n"
        "LM-SGK-TIN6-0001,Sách giáo khoa Tin học 6,SGK,6,,,shared/learning_resources/raw_page_images/sgk/tin_hoc_6,test,draft,\n",
        encoding="utf-8",
    )

    rows = build_manifest_rows(ocr_root=root, source_registry_path=registry, only_grade="6")

    assert len(rows) == 1
    assert rows[0]["ocr_text_id"] == "OCR-SGK-TIN6-BAI01"
    assert rows[0]["learning_material_id"] == "LM-SGK-TIN6-0001"
    assert rows[0]["lesson_title"] == "Bài 1. THÔNG TIN VÀ DỮ LIỆU"
    assert rows[0]["page_marker_count"] == 1

    output = tmp_path / "manifest.csv"
    write_manifest(rows, output)
    with output.open("r", encoding="utf-8", newline="") as f:
        assert list(csv.DictReader(f))[0]["status"] == "draft"


def test_manifest_preserves_split_lesson_suffixes(tmp_path: Path) -> None:
    root = tmp_path / "ocr_text"
    for suffix in ("10a", "10b"):
        lesson = root / "sgk_tin_hoc_8" / f"tin_8_bai_{suffix}"
        lesson.mkdir(parents=True)
        (lesson / f"tin_8_bai_{suffix}.md").write_text(
            f"{{0}}------------------------------------------------\n# CHỦ ĐỀ 4\n\n## BÀI {suffix.upper()}\n\n### Nội dung {suffix.upper()}\n\nNội dung bài học.\n",
            encoding="utf-8",
        )
        (lesson / f"tin_8_bai_{suffix}.metadata.json").write_text('{"page_stats": []}\n', encoding="utf-8")
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "learning_material_id,source_title,material_type,grade,source_url,source_key,local_file_path,version_label,status,notes\n"
        "LM-SGK-TIN8-0001,Sách giáo khoa Tin học 8,SGK,8,,,shared/learning_resources/raw_page_images/sgk/tin_hoc_8,test,draft,\n",
        encoding="utf-8",
    )

    rows = build_manifest_rows(ocr_root=root, source_registry_path=registry, only_grade="8")

    assert [row["lesson_key"] for row in rows] == ["bai_10a", "bai_10b"]
    assert [row["ocr_text_id"] for row in rows] == ["OCR-SGK-TIN8-BAI10A", "OCR-SGK-TIN8-BAI10B"]
    assert [row["lesson_title"] for row in rows] == ["Bài 10A. Nội dung 10A", "Bài 10B. Nội dung 10B"]


def test_manifest_enriches_topic_from_topic_lesson_map(tmp_path: Path) -> None:
    root = tmp_path / "ocr_text"
    for suffix in ("10a", "10b"):
        lesson = root / "sgk_tin_hoc_8" / f"tin_8_bai_{suffix}"
        lesson.mkdir(parents=True)
        (lesson / f"tin_8_bai_{suffix}.md").write_text(
            f"{{0}}------------------------------------------------\n## BÀI {suffix.upper()}\n\n### Tiêu đề OCR {suffix.upper()}\n",
            encoding="utf-8",
        )
        (lesson / f"tin_8_bai_{suffix}.metadata.json").write_text('{"page_stats": []}\n', encoding="utf-8")
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "learning_material_id,source_title,material_type,grade,source_url,source_key,local_file_path,version_label,status,notes\n"
        "LM-SGK-TIN8-0001,Sách giáo khoa Tin học 8,SGK,8,,,shared/learning_resources/raw_page_images/sgk/tin_hoc_8,test,draft,\n",
        encoding="utf-8",
    )
    topic_map = tmp_path / "topic_map.csv"
    topic_map.write_text(
        "item_id,parent_id,item_type,grade,source_label,normalized_label,print_page_start,source_image_page_start,learning_material_id,evidence_type,evidence_source,status,notes\n"
        "TIN8-CD04,,chu_de,8,Chủ đề 4. Ứng dụng tin học,Ứng dụng tin học,21,,LM-SGK-TIN8-0001,source_evidence,test,needs_hnmu_review,\n"
        "TIN8-CD04A,TIN8-CD04,chu_de_con,8,a. Soạn thảo văn bản và trình chiếu nâng cao,Soạn thảo văn bản và trình chiếu nâng cao,36,,LM-SGK-TIN8-0001,source_evidence,test,needs_hnmu_review,\n"
        "TIN8-B10A,TIN8-CD04A,bai_hoc,8,Bài 10A. Định dạng nâng cao cho trang chiếu,Định dạng nâng cao cho trang chiếu,46,,LM-SGK-TIN8-0001,source_evidence,test,needs_hnmu_review,\n"
        "TIN8-B10B,TIN8-CD04,bai_hoc,8,Bài 10B. Thêm văn bản vào ảnh,Thêm văn bản vào ảnh,66,,LM-SGK-TIN8-0001,source_evidence,test,needs_hnmu_review,\n",
        encoding="utf-8",
    )

    rows = build_manifest_rows(
        ocr_root=root,
        source_registry_path=registry,
        only_grade="8",
        topic_map_path=topic_map,
    )

    assert [row["lesson_key"] for row in rows] == ["bai_10a", "bai_10b"]
    assert rows[0]["lesson_title"] == "Bài 10A. Định dạng nâng cao cho trang chiếu"
    assert rows[0]["topic_title"] == "Chủ đề 4. Ứng dụng tin học > a. Soạn thảo văn bản và trình chiếu nâng cao"
    assert rows[1]["topic_title"] == "Chủ đề 4. Ứng dụng tin học"
    assert rows[0]["status"] == "draft"

from __future__ import annotations

from pathlib import Path

from edu_benchmark.learning_resources.retrieval_api import get_learning_fragment, resolve_learning_resource, search_learning_fragments
from edu_benchmark.learning_resources.retrieval_index import build_index


def test_build_and_query_retrieval_index(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "ocr_text_id,learning_material_id,material_type,grade,book_title,lesson_key,lesson_number,lesson_title,topic_title,source_markdown_path,source_metadata_path,image_dir,page_marker_count,page_stat_count,table_count,image_count,first_heading,status,notes\n"
        "OCR-SGK-TIN6-BAI17,LM-SGK-TIN6-0001,SGK,6,Sách giáo khoa Tin học 6,bai_17,17,Bài 17. Chương trình máy tính,,lesson.md,,,1,1,0,0,BÀI 17,draft,\n",
        encoding="utf-8",
    )
    fragments = tmp_path / "fragments.csv"
    fragments.write_text(
        "fragment_id,learning_material_id,ocr_text_id,material_type,grade,book_title,lesson_key,lesson_title,topic_title,page_start,page_end,page_marker_start,page_marker_end,section_label,section_path,fragment_type,order_index,location_note,source_markdown_path,markdown_text,text_preview,status,needs_hnmu_review,notes\n"
        'LM-SGK-TIN6-0001#F0001,LM-SGK-TIN6-0001,OCR-SGK-TIN6-BAI17,SGK,6,Sách giáo khoa Tin học 6,bai_17,Bài 17. Chương trình máy tính,,71,71,0,0,Chương trình máy tính,BÀI 17 > CHƯƠNG TRÌNH MÁY TÍNH,content,1,trang 71,lesson.md,"Scratch tính trung bình cộng ba số bằng cách nhập a b c và đặt TBC thành tổng chia 3.",Scratch trung bình cộng ba số,draft,false,\n',
        encoding="utf-8",
    )
    index = tmp_path / "index.sqlite"
    stats = build_index(manifest_path=manifest, fragments_path=fragments, output_path=index)

    assert stats["source_count"] == 1
    assert stats["fragment_count"] == 1
    rows = search_learning_fragments("Scratch trung bình cộng", filters={"grade": "6"}, index_path=index)
    assert rows[0]["fragment_id"] == "LM-SGK-TIN6-0001#F0001"
    assert get_learning_fragment("LM-SGK-TIN6-0001#F0001", index_path=index)["lesson_key"] == "bai_17"
    resolved = resolve_learning_resource({"grade": 6, "lesson_title": "Chương trình máy tính", "query": "Scratch"}, index_path=index)
    assert resolved["candidate_fragments"]

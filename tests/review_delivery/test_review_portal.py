from __future__ import annotations

import csv
import json
from pathlib import Path

from edu_benchmark.review_delivery import build_portal_catalog, load_review_products_config


def _write_fragment_csv(path: Path, source_markdown: str) -> None:
    row = {
        "fragment_id": "FRAG-001",
        "learning_material_id": "LM-001",
        "ocr_text_id": "OCR-001",
        "material_type": "SGK",
        "grade": "6",
        "book_title": "Tin học 6",
        "lesson_key": "BAI01",
        "lesson_title": "Bài 1",
        "topic_title": "Chủ đề 1",
        "section_path": "Chủ đề 1 > Bài 1 > Mục 1",
        "fragment_type": "text",
        "source_markdown_path": source_markdown,
        "markdown_text": "Nội dung trước ảnh.\n\n![Hình minh họa](images/page.jpg)\n\nNội dung sau ảnh.",
        "status": "draft",
        "effective_content_length": "42",
        "order_index": "1",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


def test_portal_catalog_rewrites_images_and_exposes_expected_pdfs(tmp_path: Path) -> None:
    ocr_root = tmp_path / "ocr"
    unit = ocr_root / "unit"
    image_dir = unit / "images"
    image_dir.mkdir(parents=True)
    source_markdown = unit / "lesson.md"
    source_markdown.write_text("source", encoding="utf-8")
    (image_dir / "page.jpg").write_bytes(b"jpeg-placeholder")
    fragments = tmp_path / "fragments.csv"
    _write_fragment_csv(fragments, source_markdown.relative_to(tmp_path).as_posix())

    pdf_root = tmp_path / "pdfs"
    pdf_root.mkdir()
    for grade in (6, 7, 8, 9):
        for kind in ("sgk", "sgv"):
            (pdf_root / f"{kind}_tin_hoc_{grade}.pdf").write_bytes(b"%PDF-1.4\n%%EOF")
    for grade in (6, 7, 8):
        (pdf_root / f"sbt_tin_hoc_{grade}.pdf").write_bytes(b"%PDF-1.4\n%%EOF")

    output_root = tmp_path / "outputs"
    output_root.mkdir()
    registry = tmp_path / "criteria.csv"
    registry.write_text("criterion_id\n", encoding="utf-8")
    criterion = tmp_path / "criterion.csv"
    criterion.write_text("sample_id\n", encoding="utf-8")
    summary = tmp_path / "summary.csv"
    summary.write_text("sample_id\n", encoding="utf-8")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": "plan04-review-products-v1",
                "experiment_id": "test",
                "workbook": {
                    "criteria_registry": "criteria.csv",
                    "output_root": "outputs",
                    "expected_criteria_per_sample": 1,
                    "sources": [
                        {
                            "source_key": "source",
                            "display_name": "Nguồn",
                            "grade": 6,
                            "criterion_csv": "criterion.csv",
                            "summary_csv": "summary.csv",
                        }
                    ],
                    "targets": [
                        {
                            "key": "target",
                            "display_name": "Đích",
                            "source_keys": ["source"],
                            "output_filename": "review.xlsx",
                        }
                    ],
                },
                "portal": {
                    "fragment_csv": "fragments.csv",
                    "image_root": "ocr",
                    "image_fallback_roots": [],
                    "pdf_root": "pdfs",
                    "validation_output": "outputs/portal_validation.json",
                    "host": "127.0.0.1",
                    "port": 8765,
                    "username_env": "PORTAL_USER",
                    "password_env": "PORTAL_PASSWORD",
                    "max_regex_length": 120,
                },
            }
        ),
        encoding="utf-8",
    )
    config = load_review_products_config(config_path, repository_root=tmp_path)
    catalog = build_portal_catalog(config)

    assert catalog.validation["fragment_count"] == 1
    assert catalog.validation["searchable_fragment_count"] == 1
    assert catalog.validation["image_reference_count"] == 1
    assert catalog.validation["unique_image_asset_count"] == 1
    assert catalog.validation["pdf_count"] == 11
    assert len(catalog.image_assets) == 1
    assert "/media/image/" in catalog.fragments[0]["markdown_text"]
    payload = json.loads(catalog.catalog_json)
    assert len(payload["pdfs"]) == 11
    assert not any(
        item["material_type"] == "SBT" and item["grade"] == 9
        for item in payload["pdfs"]
    )


def test_fragment_filter_surface_is_minimal_and_cascading() -> None:
    static_root = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "edu_benchmark"
        / "review_delivery"
        / "static"
    )
    html = (static_root / "index.html").read_text(encoding="utf-8")
    javascript = (static_root / "portal.js").read_text(encoding="utf-8")

    assert 'id="book-filter"' in html
    assert 'id="lesson-filter"' in html
    for removed_id in (
        "grade-filter",
        "material-filter",
        "fragment-type-filter",
        "searchable-filter",
    ):
        assert f'id="{removed_id}"' not in html
        assert f'$("{removed_id}")' not in javascript

    assert "function updateLessonOptions()" in javascript
    assert "!selectedBook || fragment.book_title === selectedBook" in javascript
    assert 'replaceSelectOptions("lesson-filter", lessons, "Tất cả bài học")' in javascript
    assert '$("book-filter").addEventListener("change"' in javascript
    # The PDF tab keeps its independent grade/material controls.
    assert 'id="book-grade-filter"' in html
    assert 'id="book-material-filter"' in html

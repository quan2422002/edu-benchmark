from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import load_workbook

from edu_benchmark.review_delivery import (
    build_audit_review_workbooks,
    load_review_products_config,
)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_review_workbook_is_compact_editable_and_traceable(tmp_path: Path) -> None:
    registry = tmp_path / "criteria.csv"
    _write_csv(
        registry,
        [
            "criterion_id",
            "criterion_group",
            "criterion_name",
            "pass_condition",
            "fail_or_uncertain_policy",
            "default_reviewer_action",
        ],
        [
            {
                "criterion_id": "RAW-CON-01",
                "criterion_group": "consistency",
                "criterion_name": "Đúng nội dung",
                "pass_condition": "Nội dung đúng.",
                "fail_or_uncertain_policy": "Không đúng thì không đạt.",
                "default_reviewer_action": "Rà soát.",
            }
        ],
    )
    criterion = tmp_path / "criterion_results.csv"
    criterion_row = {
        "sample_id": "SAMPLE-001",
        "grade": "6",
        "stt": "1",
        "lesson": "Bài 1",
        "position": "SGK trang 1",
        "question": "Thông tin là gì?",
        "bloom_level": "Biết",
        "answer_sgv": "Đáp án",
        "dialogue": "HS: ...\nAI: ...",
        "criterion_id": "RAW-CON-01",
        "criterion_name": "Đúng nội dung",
        "result": "pass",
        "reason": "Khớp học liệu.",
        "evidence_fragment_id": "FRAG-001",
        "evidence_match_reason": "Đoạn học liệu nêu đúng nội dung.",
        "image_dependency": "none",
        "needs_image_review": "false",
    }
    _write_csv(criterion, list(criterion_row), [criterion_row])
    summary = tmp_path / "sample_summaries.csv"
    summary_row = {
        "sample_id": "SAMPLE-001",
        "grade": "6",
        "lesson": "Bài 1",
        "position": "SGK trang 1",
        "question": "Thông tin là gì?",
        "quality_decision": "pass",
        "confidence_score": "0.9",
        "blocking_criterion_ids": "[]",
        "blocking_reasons": "[]",
        "needs_image_review": "false",
    }
    _write_csv(summary, list(summary_row), [summary_row])

    image_root = tmp_path / "ocr"
    image_root.mkdir()
    fragment_csv = tmp_path / "fragments.csv"
    fragment_csv.write_text("placeholder\n", encoding="utf-8")
    pdf_root = tmp_path / "pdfs"
    pdf_root.mkdir()
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": "plan04-review-products-v1",
                "experiment_id": "test",
                "workbook": {
                    "criteria_registry": registry.relative_to(tmp_path).as_posix(),
                    "output_root": "outputs",
                    "expected_criteria_per_sample": 1,
                    "sources": [
                        {
                            "source_key": "grade6",
                            "display_name": "Lớp 6",
                            "grade": 6,
                            "criterion_csv": criterion.relative_to(tmp_path).as_posix(),
                            "summary_csv": summary.relative_to(tmp_path).as_posix(),
                        }
                    ],
                    "targets": [
                        {
                            "key": "grade6",
                            "display_name": "Tin học lớp 6",
                            "source_keys": ["grade6"],
                            "output_filename": "review.xlsx",
                        }
                    ],
                },
                "portal": {
                    "fragment_csv": fragment_csv.relative_to(tmp_path).as_posix(),
                    "image_root": image_root.relative_to(tmp_path).as_posix(),
                    "image_fallback_roots": [],
                    "pdf_root": pdf_root.relative_to(tmp_path).as_posix(),
                    "validation_output": "outputs/portal.json",
                    "host": "127.0.0.1",
                    "port": 8765,
                    "username_env": "PORTAL_USER",
                    "password_env": "PORTAL_PASSWORD",
                    "max_regex_length": 120,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    config = load_review_products_config(config_path, repository_root=tmp_path)
    result = build_audit_review_workbooks(config)
    assert result["sample_count"] == 1
    assert result["criterion_result_count"] == 1

    workbook_path = tmp_path / "outputs" / "review.xlsx"
    workbook = load_workbook(workbook_path)
    assert workbook.sheetnames == [
        "Hướng dẫn",
        "Tổng hợp mẫu",
        "Kết quả tiêu chí",
        "Sửa dữ liệu",
        "Danh mục tiêu chí",
        "_Danh_muc",
    ]
    assert workbook["Tổng hợp mẫu"]["A2"].value == "SAMPLE-001"
    assert workbook["Tổng hợp mẫu"]["H2"].protection.locked is False
    assert workbook["Tổng hợp mẫu"]["A2"].protection.locked is True
    assert workbook["Kết quả tiêu chí"]["J2"].protection.locked is False
    assert workbook["Sửa dữ liệu"]["D2"].protection.locked is False
    assert workbook["_Danh_muc"].sheet_state == "hidden"
    guide = workbook["Hướng dẫn"]
    guide_text = "\n".join(
        str(cell.value or "")
        for row in guide.iter_rows()
        for cell in row
    )
    assert guide.max_row >= 40
    assert "A. Sheet Tổng hợp mẫu" in guide_text
    assert "B. Sheet Kết quả tiêu chí" in guide_text
    assert "C. Sheet Sửa dữ liệu" in guide_text
    assert "D. Sheet _Danh_muc" in guide_text
    assert "Đồng ý; Không đồng ý; Chưa chắc" in guide_text
    assert "Đạt; Không đạt; Chưa chắc" in guide_text
    assert "Giữ nguyên; Sửa dữ liệu; Loại mẫu; Chưa chắc" in guide_text
    assert "Ví dụ phù hợp" in guide_text
    assert "Phản ví dụ" in guide_text
    workbook.close()


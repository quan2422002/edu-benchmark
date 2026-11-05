from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from edu_benchmark.learning_resources.fragment_markdown_v1 import (
    FRAGMENT_FIELDNAMES,
    FRAGMENT_V1_1_FIELDNAMES,
)
from edu_benchmark.learning_resources.retrieval_api_v1 import (
    SEARCH_TOOL_NAME,
    RetrievalQueryV1Error,
    dispatch_retrieval_tool_v1,
    get_learning_fragment_v1,
    search_learning_fragments,
)
from edu_benchmark.learning_resources.retrieval_index_v1 import (
    RetrievalIndexV1Error,
    build_index_v1,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fragment(
    fragment_id: str,
    *,
    order_index: int,
    section_path: str,
    markdown_text: str,
    grade: str = "6",
) -> dict[str, object]:
    row: dict[str, object] = {name: "" for name in FRAGMENT_FIELDNAMES}
    row.update(
        {
            "fragment_id": fragment_id,
            "section_id": f"{fragment_id}-section",
            "learning_material_id": f"LM-TIN{grade}",
            "ocr_text_id": f"OCR-TIN{grade}",
            "material_type": "SGK",
            "grade": grade,
            "book_title": f"Tin học {grade}",
            "lesson_key": "bai_01",
            "lesson_title": "Bài 1. Mạng máy tính",
            "topic_title": "Chủ đề 1. Máy tính và cộng đồng",
            "canonical_version": "learning-resource-markdown-v1",
            "fragment_index": order_index,
            "order_index": order_index,
            "char_start": order_index * 10,
            "char_end": order_index * 10 + len(markdown_text),
            "section_path": section_path,
            "section_depth": section_path.count(" > ") + 1,
            "section_label": section_path.rsplit(" > ", 1)[-1],
            "fragment_type": "text",
            "source_markdown_path": f"tin_hoc_{grade}.md",
            "markdown_text": markdown_text,
            "text_preview": markdown_text,
            "status": "draft",
            "needs_hnmu_review": "true",
        }
    )
    return row


def _write_snapshot(path: Path) -> None:
    network = (
        "Chủ đề 1. Máy tính và cộng đồng > Bài 1. Mạng máy tính > "
        "B. Bài tập"
    )
    rows = [
        _fragment(
            "F0001",
            order_index=1,
            section_path=network,
            markdown_text="Scratch giúp mô phỏng kết nối mạng máy tính.",
        ),
        _fragment(
            "F0002",
            order_index=2,
            section_path=network,
            markdown_text="Địa chỉ IP xác định thiết bị trong mạng.",
        ),
        _fragment(
            "F0003",
            order_index=3,
            section_path=network + " > An toàn",
            markdown_text="Mật khẩu mạnh giúp bảo vệ tài khoản mạng.",
        ),
        _fragment(
            "F0004",
            order_index=4,
            section_path=(
                "Chủ đề 2. Dữ liệu > Bài 1. Biểu diễn dữ liệu > B. Bài tập"
            ),
            markdown_text="Scratch xử lí dữ liệu trong một bảng tính.",
        ),
        _fragment(
            "F0005",
            order_index=5,
            section_path="Chủ đề 2. Dữ liệu > Bài 2. Bảng dữ liệu",
            markdown_text="Dữ liệu mạng thứ nhất dùng để kiểm thử top năm.",
        ),
        _fragment(
            "F0006",
            order_index=6,
            section_path="Chủ đề 2. Dữ liệu > Bài 2. Bảng dữ liệu",
            markdown_text="Dữ liệu mạng thứ hai dùng để kiểm thử top năm.",
        ),
        _fragment(
            "F0007",
            order_index=7,
            section_path="Chủ đề 2. Dữ liệu > Bài 2. Bảng dữ liệu",
            markdown_text="Dữ liệu mạng thứ ba dùng để kiểm thử top năm.",
        ),
        _fragment(
            "F0008",
            order_index=8,
            section_path="Chủ đề 2. Dữ liệu > Bài 2. Bảng dữ liệu",
            markdown_text="Dữ liệu mạng thứ tư dùng để kiểm thử top năm.",
        ),
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAGMENT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _build_index(tmp_path: Path) -> Path:
    fragments = tmp_path / "fragments.csv"
    _write_snapshot(fragments)
    index_path = tmp_path / "index.sqlite"
    build_index_v1(fragments_path=fragments, output_path=index_path)
    return index_path


def _write_v1_1_bundle(
    fragments_path: Path,
    validation_path: Path,
    rows: list[dict[str, object]],
) -> str:
    for source_index, row in enumerate(rows, start=1):
        row.update(
            {
                "fragment_release": "v1.1",
                "merge_status": row.get("merge_status", "unchanged"),
                "merge_reason": row.get("merge_reason", ""),
                "merge_policy_version": "fragment-v1.1-iterative-bounded-v1",
                "merged_from_fragment_ids_json": json.dumps(
                    [f"SOURCE-{source_index:04d}"]
                ),
                "merged_from_fragment_count": 1,
                "source_fragment_types_json": '["text"]',
                "source_fragment_index_start": source_index,
                "source_fragment_index_end": source_index,
            }
        )
    with fragments_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAGMENT_V1_1_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    contract = {
        "merge_policy_version": "fragment-v1.1-iterative-bounded-v1",
        "measurement_unit": "unicode_code_points",
        "text_min_effective_chars": 20,
        "text_max_effective_chars": 200,
        "table_absorption_max_effective_chars": 20,
        "neighbor_policy": "prefer_short_group",
        "table_table_merge_enabled": False,
        "scope": "contiguous+exact_ocr_text_id+exact_canonical_section_path",
        "structural_zero_initiates_merge": False,
    }
    contract_hash = hashlib.sha256(
        json.dumps(
            contract,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    contract["merge_contract_sha256"] = contract_hash
    validation_path.write_text(
        json.dumps(
            {
                "fragment_release": "v1.1",
                "lossless": True,
                "fragment_count": len(rows),
                "fragments_sha256": _sha256(fragments_path),
                "merge_contract": contract,
                "merge_contract_sha256": contract_hash,
            }
        ),
        encoding="utf-8",
    )
    return contract_hash


def test_index_v1_exposes_two_logical_tables(tmp_path: Path) -> None:
    fragments = tmp_path / "fragments.csv"
    _write_snapshot(fragments)
    index_path = tmp_path / "index.sqlite"
    summary = build_index_v1(fragments_path=fragments, output_path=index_path)

    assert summary["logical_tables"] == [
        "learning_fragments",
        "learning_fragments_fts",
    ]
    assert summary["fragment_count"] == 8
    assert summary["fts_count"] == 8
    with sqlite3.connect(index_path) as conn:
        names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
    assert "learning_fragments" in names
    assert "learning_fragments_fts" in names
    assert "learning_sections" not in names
    assert "learning_sections_fts" not in names
    assert "learning_sources" not in names


def test_index_preserves_v1_1_lineage_columns(tmp_path: Path) -> None:
    fragments = tmp_path / "fragments-v1-1.csv"
    row = _fragment(
        "OCR-TIN6#V1_1F0001",
        order_index=1,
        section_path="Chủ đề 1 > Bài 1 > Mục 1",
        markdown_text="Nội dung đã ghép.",
    )
    row.update(
        {
            "fragment_release": "v1.1",
            "effective_content_length": 17,
            "merge_status": "merged",
            "merge_reason": "text_iterative",
            "merge_policy_version": "fragment-v1.1-iterative-bounded-v1",
            "merged_from_fragment_ids_json": '["F0001", "F0002"]',
            "merged_from_fragment_count": 2,
            "source_fragment_types_json": '["text", "text"]',
            "source_fragment_index_start": 1,
            "source_fragment_index_end": 2,
        }
    )
    with fragments.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAGMENT_V1_1_FIELDNAMES)
        writer.writeheader()
        writer.writerow(row)
    index_path = tmp_path / "index-v1-1.sqlite"
    validation_path = tmp_path / "validation-v1-1.json"
    contract = {
        "merge_policy_version": "fragment-v1.1-iterative-bounded-v1",
        "measurement_unit": "unicode_code_points",
        "text_min_effective_chars": 20,
        "text_max_effective_chars": 200,
        "table_absorption_max_effective_chars": 20,
        "neighbor_policy": "prefer_short_group",
        "table_table_merge_enabled": False,
        "scope": "contiguous+exact_ocr_text_id+exact_canonical_section_path",
        "structural_zero_initiates_merge": False,
    }
    contract_hash = hashlib.sha256(
        json.dumps(
            contract,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    contract["merge_contract_sha256"] = contract_hash
    validation_path.write_text(
        json.dumps(
            {
                "fragment_release": "v1.1",
                "lossless": True,
                "fragment_count": 1,
                "fragments_sha256": _sha256(fragments),
                "merge_contract": contract,
                "merge_contract_sha256": contract_hash,
            }
        ),
        encoding="utf-8",
    )

    summary = build_index_v1(
        fragments_path=fragments,
        validation_summary_path=validation_path,
        output_path=index_path,
    )

    assert summary["index_schema_version"] == "learning-resource-retrieval-v1.2"
    assert summary["fragment_release"] == "v1.1"
    assert summary["merge_contract_sha256"] == contract_hash
    with sqlite3.connect(index_path) as conn:
        stored = conn.execute(
            "SELECT fragment_release, merge_status, merged_from_fragment_ids_json, "
            "merge_contract_sha256 "
            "FROM learning_fragments"
        ).fetchone()
    assert stored == (
        "v1.1",
        "merged",
        '["F0001", "F0002"]',
        contract_hash,
    )


def test_v1_2_indexes_only_positive_effective_content(tmp_path: Path) -> None:
    fragments = tmp_path / "fragments-v1-1.csv"
    validation = tmp_path / "validation-v1-1.json"
    positive = _fragment(
        "OCR-TIN6#V1_1F0001",
        order_index=1,
        section_path="Chủ đề 1 > Bài 1",
        markdown_text="Ngắn nhưng có nghĩa.",
    )
    positive["effective_content_length"] = 5
    zero = _fragment(
        "OCR-TIN6#V1_1F0002",
        order_index=2,
        section_path="Chủ đề 1 > Bài 1 > Tiêu đề",
        markdown_text="### Tiêu đề",
    )
    zero["effective_content_length"] = 0
    _write_v1_1_bundle(fragments, validation, [positive, zero])

    index_path = tmp_path / "index-v1-2.sqlite"
    summary = build_index_v1(
        fragments_path=fragments,
        validation_summary_path=validation,
        output_path=index_path,
    )

    eligibility = summary["retrieval_eligibility"]
    assert summary["fragment_count"] == 1
    assert summary["fts_count"] == 1
    assert eligibility["source_fragment_count"] == 2
    assert eligibility["retrieval_eligible_fragment_count"] == 1
    assert eligibility["retrieval_excluded_fragment_count"] == 1
    assert eligibility["excluded_reason_counts"] == {
        "zero_effective_content": 1
    }
    assert eligibility["units_without_eligible_fragments"] == []
    with sqlite3.connect(index_path) as conn:
        stored = conn.execute(
            "SELECT fragment_id, effective_content_length, status, "
            "retrieval_eligibility_policy_sha256 FROM learning_fragments"
        ).fetchall()
    assert stored == [
        (
            "OCR-TIN6#V1_1F0001",
            5,
            "draft",
            eligibility["policy_sha256"],
        )
    ]


def test_v1_2_rejects_unit_without_eligible_fragment(tmp_path: Path) -> None:
    fragments = tmp_path / "fragments-v1-1.csv"
    validation = tmp_path / "validation-v1-1.json"
    zero = _fragment(
        "OCR-TIN6#V1_1F0001",
        order_index=1,
        section_path="Chủ đề 1 > Bài 1",
        markdown_text="### Tiêu đề",
    )
    zero["effective_content_length"] = 0
    _write_v1_1_bundle(fragments, validation, [zero])

    with pytest.raises(
        RetrievalIndexV1Error,
        match="remove every fragment from unit",
    ):
        build_index_v1(
            fragments_path=fragments,
            validation_summary_path=validation,
            output_path=tmp_path / "index-v1-2.sqlite",
        )


def test_index_rejects_v1_1_without_validation_contract(tmp_path: Path) -> None:
    fragments = tmp_path / "fragments-v1-1.csv"
    row = _fragment(
        "OCR-TIN6#V1_1F0001",
        order_index=1,
        section_path="Chủ đề 1 > Bài 1 > Mục 1",
        markdown_text="Nội dung.",
    )
    row.update(
        {
            "fragment_release": "v1.1",
            "effective_content_length": 9,
            "merge_status": "unchanged",
            "merge_reason": "",
            "merge_policy_version": "fragment-v1.1-iterative-bounded-v1",
            "merged_from_fragment_ids_json": '["F0001"]',
            "merged_from_fragment_count": 1,
            "source_fragment_types_json": '["text"]',
            "source_fragment_index_start": 1,
            "source_fragment_index_end": 1,
        }
    )
    with fragments.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAGMENT_V1_1_FIELDNAMES)
        writer.writeheader()
        writer.writerow(row)

    with pytest.raises(RetrievalIndexV1Error):
        build_index_v1(
            fragments_path=fragments,
            output_path=tmp_path / "index-v1-1.sqlite",
        )


def test_section_only_returns_entire_best_section_and_descendants(
    tmp_path: Path,
) -> None:
    index_path = _build_index(tmp_path)

    result = search_learning_fragments(
        "Mạng máy tính Bài tập",
        None,
        filters={"grade": "6"},
        index_path=index_path,
    )

    assert result.mode == "section_only"
    assert result.result_count == 3
    assert [row["fragment_id"] for row in result.results] == [
        "F0001",
        "F0002",
        "F0003",
    ]
    assert result.matched_section_path.endswith("B. Bài tập")


def test_exact_section_component_wins_and_returns_ancestor_scope(
    tmp_path: Path,
) -> None:
    fragments = tmp_path / "fragments.csv"
    lesson = "Chủ đề 1. Máy tính và cộng đồng > Bài 1. Thông tin và dữ liệu"
    rows = [
        _fragment(
            "F0001",
            order_index=1,
            section_path=lesson,
            markdown_text="Thông tin được biểu diễn thành dữ liệu.",
        ),
        _fragment(
            "F0002",
            order_index=2,
            section_path=lesson + " > Mối quan hệ giữa thông tin và dữ liệu",
            markdown_text="Dữ liệu là vật mang thông tin.",
        ),
    ]
    with fragments.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAGMENT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    index_path = tmp_path / "index.sqlite"
    build_index_v1(fragments_path=fragments, output_path=index_path)

    result = search_learning_fragments(
        "Bài 1 Thông tin và dữ liệu",
        None,
        filters={"grade": "6"},
        index_path=index_path,
    )

    assert result.matched_section_path == lesson
    assert result.section_match_strategy == "exact_component"
    assert [row["fragment_id"] for row in result.results] == [
        "F0001",
        "F0002",
    ]


def test_content_only_returns_at_most_five_fragments(tmp_path: Path) -> None:
    index_path = _build_index(tmp_path)

    result = search_learning_fragments(
        None,
        "mạng",
        index_path=index_path,
    )

    assert result.mode == "content_only"
    assert result.result_count == 5
    assert result.matched_section_path is None
    assert all("mạng" in row["markdown_text"].casefold() for row in result.results)


def test_combined_search_limits_content_to_selected_section(tmp_path: Path) -> None:
    index_path = _build_index(tmp_path)

    result = search_learning_fragments(
        "Mạng máy tính Bài tập",
        "mật khẩu",
        index_path=index_path,
    )

    assert result.mode == "section_and_content"
    assert [row["fragment_id"] for row in result.results] == ["F0003"]
    assert all(
        row["section_path"] == result.matched_section_path
        or row["section_path"].startswith(result.matched_section_path + " > ")
        for row in result.results
    )


def test_multi_token_search_uses_or_candidates_then_bm25_ranking(
    tmp_path: Path,
) -> None:
    index_path = _build_index(tmp_path)

    result = search_learning_fragments(
        "Mạng khôngtồntại",
        "mật khẩu khôngtồntại",
        filters={"grade": "6"},
        index_path=index_path,
    )

    assert result.matched_section_path is not None
    assert "Mạng máy tính" in result.matched_section_path
    assert [row["fragment_id"] for row in result.results] == ["F0003"]


def test_content_no_match_keeps_exact_selected_section_without_parent_fallback(
    tmp_path: Path,
) -> None:
    index_path = _build_index(tmp_path)

    result = search_learning_fragments(
        "Mạng máy tính Bài tập",
        "khôngtồntại",
        filters={"grade": "6"},
        index_path=index_path,
    )

    assert result.results == ()
    assert result.reason == "content_no_match"
    assert result.matched_section_path is not None
    assert result.matched_section_path.endswith("B. Bài tập")


@pytest.mark.parametrize(
    ("section_keywords", "content_keywords"),
    [(None, None), ("", "  ")],
)
def test_search_rejects_two_empty_keyword_levels(
    tmp_path: Path,
    section_keywords: str | None,
    content_keywords: str | None,
) -> None:
    index_path = _build_index(tmp_path)

    with pytest.raises(RetrievalQueryV1Error):
        search_learning_fragments(
            section_keywords,
            content_keywords,
            index_path=index_path,
        )


def test_section_no_match_does_not_fallback_to_global_content(tmp_path: Path) -> None:
    index_path = _build_index(tmp_path)

    result = search_learning_fragments(
        "Không có đầu mục này",
        "Scratch",
        index_path=index_path,
    )

    assert result.results == ()
    assert result.reason == "section_no_match"


def test_direct_get_and_tool_envelope_preserve_snapshot(tmp_path: Path) -> None:
    index_path = _build_index(tmp_path)

    row = get_learning_fragment_v1("F0001", index_path=index_path)
    envelope = dispatch_retrieval_tool_v1(
        SEARCH_TOOL_NAME,
        {
            "section_keywords": None,
            "content_keywords": "Scratch",
            "filters": {"grade": 6},
        },
        index_path=index_path,
    )

    assert row is not None
    assert row["fragment_snapshot_sha256"]
    assert envelope["tool_name"] == SEARCH_TOOL_NAME
    assert envelope["result_count"] == 2
    assert envelope["snapshot_sha256"] == row["fragment_snapshot_sha256"]


def test_build_rejects_validation_snapshot_mismatch(tmp_path: Path) -> None:
    fragments = tmp_path / "fragments.csv"
    sections = tmp_path / "sections.csv"
    validation = tmp_path / "fragment_validation_summary.json"
    _write_snapshot(fragments)
    sections.write_text("section_id\nS0001\n", encoding="utf-8")
    validation.write_text(
        json.dumps(
            {
                "lossless": True,
                "fragment_count": 8,
                "fragments_sha256": "wrong-hash",
                "sections_sha256": _sha256(sections),
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "index.sqlite"

    with pytest.raises(RetrievalIndexV1Error):
        build_index_v1(
            fragments_path=fragments,
            sections_path=sections,
            validation_summary_path=validation,
            output_path=output,
        )

    assert not output.exists()

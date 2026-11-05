from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest
from openpyxl import Workbook

from edu_benchmark.dialogue_audit.v5_input_preparation import (
    NORMALIZED_FIELDS,
    V5_1_NORMALIZED_FIELDS,
    V5SourceSpec,
    prepare_v5_inputs,
    prepare_v5_1_inputs,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_base(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "sample_id": "HNMU-G6-R0002-STT1",
                "source_file": "historical.xlsx",
                "source_row_number": 2,
                "grade": "6",
                "grade_label": "Lớp 6",
                "stt": "1",
                "lesson": "Bài 1",
                "position": "SGK trang 1",
                "question": "Câu hỏi cũ",
                "bloom_level": "Nhận biết",
                "answer_sgv": "Đáp án cũ",
                "dialogue": "HS: Hỏi.\nAI: Đáp.",
            }
        )


def _write_source(path: Path) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(
        [
            "STT",
            "Bài",
            "Vị trí",
            "Câu hỏi",
            "Mức Bloom",
            "Đáp án",
            "Hội thoại gia sư",
        ]
    )
    worksheet.append(
        [
            1,
            "Bài 1",
            "SBT trang 3, bài 1.1",
            "Câu hỏi mới",
            "Nhận biết",
            "Đáp án mới",
            "HS: Hỏi mới.\nAI: Đáp mới.",
        ]
    )
    worksheet.append(
        [
            2,
            "Bài 1",
            "SGK trang 3",
            "Không thuộc phạm vi",
            "Nhận biết",
            "Đáp án",
            "HS: Hỏi.\nAI: Đáp.",
        ]
    )
    workbook.save(path)


def _write_annotated_source(path: Path) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(
        [
            "STT",
            "Bài",
            "Vị trí",
            "Câu hỏi",
            "Mức Bloom",
            "Đáp án",
            "Hội thoại gia sư",
        ]
    )
    worksheet.append(
        [
            1,
            "Bài 1",
            "SBT trang 3, bài 1.1",
            "Câu hỏi mới",
            "Nhận biết",
            "Đáp án mới",
            "HS: Em hỏi.<br>AI: [Gợi ý từng bước] Em thử lại.",
        ]
    )
    workbook.save(path)


def test_prepare_v5_inputs_preserves_history_and_namespaces_new_rows(
    tmp_path: Path,
) -> None:
    base = tmp_path / "base.csv"
    source = tmp_path / "Lớp 6 - Lần 2.xlsx"
    registry = tmp_path / "manifest.csv"
    output = tmp_path / "combined.csv"
    manifest = tmp_path / "combined.manifest.json"
    _write_base(base)
    _write_source(source)
    with registry.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("batch_id", "source_file", "sha256", "processing_status"),
        )
        writer.writeheader()
        writer.writerow(
            {
                "batch_id": "round2",
                "source_file": source.as_posix(),
                "sha256": _sha256(source),
                "processing_status": "raw_registered_no_audit",
            }
        )

    result = prepare_v5_inputs(
        base_normalized_rows_path=base,
        source_registry_path=registry,
        sources=(
            V5SourceSpec(
                path=source,
                grade="6",
                source_namespace="G6-R2-L6",
                include_material_types=("SBT",),
                expected_included_count=1,
            ),
        ),
        output_rows_path=output,
        output_manifest_path=manifest,
    )

    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["sample_id"] for row in rows] == [
        "HNMU-G6-R0002-STT1",
        "HNMU-G6-R2-L6-R0002-STT1",
    ]
    assert rows[1]["source_file"] == source.as_posix()
    assert result["base"]["historical_ids_preserved"] is True
    assert result["new_row_count"] == 1
    assert result["combined_row_count"] == 2
    saved_manifest = json.loads(manifest.read_text(encoding="utf-8"))
    assert saved_manifest["output"]["sha256"] == _sha256(output)

    with pytest.raises(FileExistsError):
        prepare_v5_inputs(
            base_normalized_rows_path=base,
            source_registry_path=registry,
            sources=(
                V5SourceSpec(
                    path=source,
                    grade="6",
                    source_namespace="G6-R2-L6",
                    include_material_types=("SBT",),
                    expected_included_count=1,
                ),
            ),
            output_rows_path=output,
            output_manifest_path=manifest,
        )


def test_prepare_v5_1_inputs_writes_canonical_dialogue_and_provenance(
    tmp_path: Path,
) -> None:
    base = tmp_path / "base.csv"
    source = tmp_path / "Lớp 6 - Lần 2.xlsx"
    registry = tmp_path / "manifest.csv"
    output = tmp_path / "combined-v5-1.csv"
    manifest = tmp_path / "combined-v5-1.manifest.json"
    _write_base(base)
    _write_annotated_source(source)
    with registry.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("batch_id", "source_file", "sha256", "processing_status"),
        )
        writer.writeheader()
        writer.writerow(
            {
                "batch_id": "round2",
                "source_file": source.as_posix(),
                "sha256": _sha256(source),
                "processing_status": "raw_registered_no_audit",
            }
        )

    result = prepare_v5_1_inputs(
        base_normalized_rows_path=base,
        source_registry_path=registry,
        sources=(
            V5SourceSpec(
                path=source,
                grade="6",
                source_namespace="G6-R2-L6",
                include_material_types=("SBT",),
                expected_included_count=1,
            ),
        ),
        output_rows_path=output,
        output_manifest_path=manifest,
    )

    with output.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert tuple(reader.fieldnames or ()) == V5_1_NORMALIZED_FIELDS
    new_row = rows[1]
    assert new_row["dialogue"] == "HS: Em hỏi.\nAI: Em thử lại."
    assert "[Gợi ý từng bước]" in new_row["dialogue_raw"]
    assert new_row["dialogue_annotation_count"] == "1"
    assert new_row["dialogue_normalization_changed"] == "True"
    assert new_row["dialogue_normalization_flags_json"] == "[]"
    assert len(new_row["dialogue_raw_sha256"]) == 64
    assert len(new_row["dialogue_normalized_sha256"]) == 64
    assert result["dialogue_normalization"]["annotation_removed_count"] == 1
    assert result["dialogue_normalization"]["raw_dialogue_preserved"] is True

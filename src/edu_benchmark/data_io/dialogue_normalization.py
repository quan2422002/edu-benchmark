"""Lossless, fail-closed normalization for HNMU turn-row XLSX workbooks.

The raw HNMU workbooks may represent one sample as a vertically merged ``STT``
cell plus several dialogue cells, one per Excel row.  This module creates a
derived workbook with one row per sample.  It never changes the source file;
when a logical field intentionally spans several source cells, it joins those
cells verbatim in source-row order rather than choosing one of them.
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable, Sequence

from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import Cell
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from edu_benchmark.data_io.xlsx import slug_header


class DialogueNormalizationError(ValueError):
    """Raised when a source workbook cannot be normalized without ambiguity."""


@dataclass(frozen=True)
class SampleSpan:
    """One source-row interval that belongs to a single HNMU sample."""

    start_row: int
    end_row: int


@dataclass(frozen=True)
class NormalizedSample:
    """One losslessly normalized sample before it is written to a workbook."""

    span: SampleSpan
    values: tuple[Any, ...]
    dialogue: str
    source_dialogue_rows: tuple[int, ...]


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for ``path`` without loading its full content."""

    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _has_value(value: Any) -> bool:
    return value is not None and value != ""


def _find_header(ws: Worksheet) -> tuple[int, list[tuple[int, str]], int, int]:
    """Return header row, logical columns, STT column, and dialogue column."""

    for row_number in range(1, min(ws.max_row, 30) + 1):
        columns = [
            (column_number, str(ws.cell(row_number, column_number).value))
            for column_number in range(1, ws.max_column + 1)
            if _has_value(ws.cell(row_number, column_number).value)
        ]
        slugged = {slug_header(value): column for column, value in columns}
        stt_column = slugged.get("stt")
        dialogue_columns = [
            column
            for column, value in columns
            if slug_header(value).startswith("hoi_thoai_gia_su")
        ]
        if stt_column is not None and len(dialogue_columns) == 1:
            names = [value for _, value in columns]
            if len(names) != len(set(names)):
                raise DialogueNormalizationError(
                    f"{ws.title!r} row {row_number} contains duplicate logical headers."
                )
            return row_number, columns, stt_column, dialogue_columns[0]
    raise DialogueNormalizationError(
        f"Cannot find one STT column and one HNMU dialogue column in worksheet {ws.title!r}."
    )


def _sample_spans(ws: Worksheet, *, header_row: int, stt_column: int, logical_columns: Sequence[int]) -> list[SampleSpan]:
    """Infer sample spans from vertical STT merges and standalone STT cells."""

    spans: list[SampleSpan] = []
    rows_covered_by_vertical_stt_merge: set[int] = set()
    for merged_range in ws.merged_cells.ranges:
        if merged_range.max_row <= header_row or merged_range.max_row == merged_range.min_row:
            continue
        if not (merged_range.min_col <= stt_column <= merged_range.max_col):
            continue
        if merged_range.min_row <= header_row:
            raise DialogueNormalizationError(
                f"{ws.title!r} has an STT merge that crosses the header row: {merged_range}."
            )
        if not _has_value(ws.cell(merged_range.min_row, stt_column).value):
            raise DialogueNormalizationError(
                f"{ws.title!r} has an STT merge without a sample ID: {merged_range}."
            )
        spans.append(SampleSpan(merged_range.min_row, merged_range.max_row))
        rows_covered_by_vertical_stt_merge.update(
            range(merged_range.min_row, merged_range.max_row + 1)
        )

    for row_number in range(header_row + 1, ws.max_row + 1):
        if _has_value(ws.cell(row_number, stt_column).value) and row_number not in rows_covered_by_vertical_stt_merge:
            spans.append(SampleSpan(row_number, row_number))

    spans.sort(key=lambda span: (span.start_row, span.end_row))
    previous_end = header_row
    for span in spans:
        if span.start_row <= previous_end:
            raise DialogueNormalizationError(
                f"{ws.title!r} has overlapping STT sample spans at row {span.start_row}."
            )
        previous_end = span.end_row

    assigned_rows = {
        row_number
        for span in spans
        for row_number in range(span.start_row, span.end_row + 1)
    }
    populated_unassigned = [
        row_number
        for row_number in range(header_row + 1, ws.max_row + 1)
        if any(_has_value(ws.cell(row_number, column).value) for column in logical_columns)
        and row_number not in assigned_rows
    ]
    if populated_unassigned:
        raise DialogueNormalizationError(
            f"{ws.title!r} has populated logical cells outside an STT sample span: "
            f"{populated_unassigned[:10]}."
        )
    if not spans:
        raise DialogueNormalizationError(f"{ws.title!r} contains no sample spans.")
    return spans


def _lossless_field_value(
    ws: Worksheet,
    *,
    span: SampleSpan,
    column: int,
    header: str,
) -> tuple[Any, int]:
    """Return a field value, joining multiple source cells without alteration."""

    values = [
        (row_number, ws.cell(row_number, column).value)
        for row_number in range(span.start_row, span.end_row + 1)
        if _has_value(ws.cell(row_number, column).value)
    ]
    if not values:
        return None, 0
    if len(values) == 1:
        return values[0][1], 1
    if not all(isinstance(value, str) for _, value in values):
        rows = [row_number for row_number, _ in values]
        raise DialogueNormalizationError(
            f"{ws.title!r} rows {span.start_row}:{span.end_row} have multiple "
            f"non-text cells for {header!r} at source rows {rows}."
        )
    return "\n".join(value for _, value in values), len(values)


def _normalized_samples(
    ws: Worksheet,
    *,
    header_row: int,
    columns: Sequence[tuple[int, str]],
    stt_column: int,
    dialogue_column: int,
) -> tuple[list[NormalizedSample], dict[str, int]]:
    """Build all normalized samples for one worksheet before writing output."""

    spans = _sample_spans(
        ws,
        header_row=header_row,
        stt_column=stt_column,
        logical_columns=[column for column, _ in columns],
    )
    samples: list[NormalizedSample] = []
    multi_cell_field_counts: dict[str, int] = {}
    for span in spans:
        values: list[Any] = []
        dialogue_values: list[str] = []
        dialogue_rows: list[int] = []
        for column, header in columns:
            if column == dialogue_column:
                for row_number in range(span.start_row, span.end_row + 1):
                    value = ws.cell(row_number, column).value
                    if not _has_value(value):
                        continue
                    if not isinstance(value, str):
                        raise DialogueNormalizationError(
                            f"{ws.title!r} row {row_number} has a non-text dialogue value."
                        )
                    dialogue_values.append(value)
                    dialogue_rows.append(row_number)
                if not dialogue_values:
                    raise DialogueNormalizationError(
                        f"{ws.title!r} rows {span.start_row}:{span.end_row} have no dialogue text."
                    )
                values.append("\n".join(dialogue_values))
            else:
                field_value, source_cell_count = _lossless_field_value(
                    ws,
                    span=span,
                    column=column,
                    header=header,
                )
                if source_cell_count > 1:
                    multi_cell_field_counts[header] = (
                        multi_cell_field_counts.get(header, 0) + 1
                    )
                values.append(field_value)
        samples.append(
            NormalizedSample(
                span=span,
                values=tuple(values),
                dialogue="\n".join(dialogue_values),
                source_dialogue_rows=tuple(dialogue_rows),
            )
        )
    return samples, multi_cell_field_counts


def _copy_cell_appearance(source: Cell, destination: Cell, *, dialogue: bool = False) -> None:
    """Copy visible cell formatting while keeping output rows independently sized."""

    destination.font = copy(source.font)
    destination.fill = copy(source.fill)
    destination.border = copy(source.border)
    destination.number_format = source.number_format
    destination.protection = copy(source.protection)
    alignment = copy(source.alignment)
    if dialogue:
        alignment = Alignment(
            horizontal=alignment.horizontal,
            vertical="top",
            text_rotation=alignment.text_rotation,
            wrap_text=True,
            shrink_to_fit=alignment.shrink_to_fit,
            indent=alignment.indent,
            relativeIndent=alignment.relativeIndent,
            justifyLastLine=alignment.justifyLastLine,
            readingOrder=alignment.readingOrder,
        )
    destination.alignment = alignment


def _write_sheet(source: Worksheet, destination: Worksheet) -> dict[str, Any]:
    """Normalize one worksheet into an output worksheet and verify logical shape."""

    header_row, columns, stt_column, dialogue_column = _find_header(source)
    samples, multi_cell_field_counts = _normalized_samples(
        source,
        header_row=header_row,
        columns=columns,
        stt_column=stt_column,
        dialogue_column=dialogue_column,
    )
    headers = [header for _, header in columns]
    for output_column, (source_column, header) in enumerate(columns, start=1):
        destination_cell = destination.cell(1, output_column, header)
        _copy_cell_appearance(source.cell(header_row, source_column), destination_cell)
        source_width = source.column_dimensions[get_column_letter(source_column)].width
        if source_column == dialogue_column:
            destination.column_dimensions[get_column_letter(output_column)].width = max(
                float(source_width or 0), 60.0
            )
        elif source_width is not None:
            destination.column_dimensions[get_column_letter(output_column)].width = source_width

    for output_row, sample in enumerate(samples, start=2):
        for output_column, ((source_column, _), value) in enumerate(
            zip(columns, sample.values), start=1
        ):
            destination_cell = destination.cell(output_row, output_column, value)
            _copy_cell_appearance(
                source.cell(sample.span.start_row, source_column),
                destination_cell,
                dialogue=source_column == dialogue_column,
            )

    destination.freeze_panes = "A2"
    destination.auto_filter.ref = f"A1:{get_column_letter(len(columns))}{len(samples) + 1}"
    destination.sheet_view.showGridLines = source.sheet_view.showGridLines
    return {
        "sheet_name": source.title,
        "header_row": header_row,
        "logical_headers": headers,
        "source_sample_count": len(samples),
        "source_dialogue_row_count": sum(len(sample.source_dialogue_rows) for sample in samples),
        "multi_turn_sample_count": sum(
            len(sample.source_dialogue_rows) > 1 for sample in samples
        ),
        "single_turn_sample_count": sum(
            len(sample.source_dialogue_rows) == 1 for sample in samples
        ),
        "multi_cell_field_sample_counts": multi_cell_field_counts,
        "samples": samples,
    }


def _verify_output(
    output_path: Path,
    sheet_results: Sequence[dict[str, Any]],
) -> None:
    """Read the temporary output back and compare every normalized cell exactly."""

    output = load_workbook(output_path, read_only=False, data_only=False)
    try:
        expected_sheet_names = [str(result["sheet_name"]) for result in sheet_results]
        if output.sheetnames != expected_sheet_names:
            raise DialogueNormalizationError(
                f"Output sheet names differ: {output.sheetnames!r} != {expected_sheet_names!r}."
            )
        for result in sheet_results:
            worksheet = output[str(result["sheet_name"])]
            headers = list(result["logical_headers"])
            if [worksheet.cell(1, column).value for column in range(1, len(headers) + 1)] != headers:
                raise DialogueNormalizationError(
                    f"Output headers differ for worksheet {worksheet.title!r}."
                )
            samples = result["samples"]
            if worksheet.max_row != len(samples) + 1:
                raise DialogueNormalizationError(
                    f"Output row count differs for worksheet {worksheet.title!r}."
                )
            for output_row, sample in enumerate(samples, start=2):
                actual = tuple(
                    worksheet.cell(output_row, column).value
                    for column in range(1, len(headers) + 1)
                )
                if actual != sample.values:
                    raise DialogueNormalizationError(
                        f"Output content differs for worksheet {worksheet.title!r}, row {output_row}."
                    )
                if actual[-1] != sample.dialogue:
                    raise DialogueNormalizationError(
                        f"Output dialogue differs for worksheet {worksheet.title!r}, row {output_row}."
                    )
    finally:
        output.close()


def normalize_hnmu_turn_row_workbook(
    source_path: Path,
    output_path: Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create and verify one lossless one-row-per-sample derived workbook.

    The source workbook is hashed before and after the operation.  Existing
    outputs are rejected by default to prevent an accidental overwrite.
    """

    source_path = source_path.resolve()
    output_path = output_path.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source_hash_before = sha256_file(source_path)
    source = load_workbook(source_path, read_only=False, data_only=False)
    destination = Workbook()
    destination.remove(destination.active)
    temporary_path: Path | None = None
    try:
        sheet_results: list[dict[str, Any]] = []
        for source_sheet in source.worksheets:
            destination_sheet = destination.create_sheet(source_sheet.title)
            sheet_results.append(_write_sheet(source_sheet, destination_sheet))

        with tempfile.NamedTemporaryFile(
            prefix=f".{output_path.stem}.", suffix=".xlsx", dir=output_path.parent, delete=False
        ) as handle:
            temporary_path = Path(handle.name)
        destination.save(temporary_path)
        destination.close()
        _verify_output(temporary_path, sheet_results)
        source_hash_after = sha256_file(source_path)
        if source_hash_after != source_hash_before:
            raise DialogueNormalizationError(
                f"Source workbook changed during normalization: {source_path}."
            )
        os.replace(temporary_path, output_path)
        temporary_path = None
        return {
            "source_file": source_path.as_posix(),
            "source_sha256": source_hash_before,
            "output_file": output_path.as_posix(),
            "output_sha256": sha256_file(output_path),
            "verified_lossless": True,
            "sheets": [
                {
                    key: value
                    for key, value in result.items()
                    if key != "samples"
                }
                for result in sheet_results
            ],
        }
    finally:
        source.close()
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def write_normalization_manifest(
    path: Path,
    workbook_results: Iterable[dict[str, Any]],
    *,
    overwrite: bool = False,
    append: bool = False,
) -> None:
    """Write or safely append records to a reproducible normalization manifest."""

    path = path.resolve()
    if append and overwrite:
        raise ValueError("append and overwrite cannot be used together")
    new_results = list(workbook_results)
    if path.exists() and not (overwrite or append):
        raise FileExistsError(f"Refusing to overwrite existing manifest: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_results: list[dict[str, Any]] = []
    if append and path.exists():
        existing_payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            not isinstance(existing_payload, dict)
            or existing_payload.get("schema_version") != "1.0"
            or existing_payload.get("normalization_contract")
            != "vertical_stt_span_lossless_dialogue_join_v1"
            or not isinstance(existing_payload.get("workbooks"), list)
        ):
            raise DialogueNormalizationError(
                f"Cannot append to an incompatible normalization manifest: {path}"
            )
        existing_results = list(existing_payload["workbooks"])
        existing_sources = {
            str(result.get("source_file", ""))
            for result in existing_results
            if isinstance(result, dict)
        }
        new_sources = [
            str(result.get("source_file", ""))
            for result in new_results
            if isinstance(result, dict)
        ]
        if "" in new_sources or len(new_sources) != len(new_results):
            raise DialogueNormalizationError("Each appended result needs a source_file.")
        if len(new_sources) != len(set(new_sources)) or existing_sources.intersection(new_sources):
            raise DialogueNormalizationError(
                "The manifest already contains one of the requested source workbooks."
            )
    payload = {
        "schema_version": "1.0",
        "normalization_contract": "vertical_stt_span_lossless_dialogue_join_v1",
        "workbooks": existing_results + new_results,
    }
    with tempfile.NamedTemporaryFile(
        prefix=f".{path.stem}.", suffix=".json", dir=path.parent, mode="w", encoding="utf-8", delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_path = Path(handle.name)
    try:
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

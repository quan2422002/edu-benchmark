"""Minimal XLSX reader based on the Python standard library.

The project intentionally keeps this reader small so Plan 04 can inspect HNMU
raw Excel files without adding ``openpyxl`` as a dependency to ``benchmark_env``.
It supports the simple worksheet shape used by the current HNMU batches.
"""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

SPREADSHEET_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}


def column_index(cell_ref: str) -> int:
    """Convert an Excel cell reference into a zero-based column index.

    Args:
        cell_ref: Excel cell reference such as ``A1`` or ``AA12``.

    Returns:
        Zero-based column index. Returns ``0`` when no column letters are found.
    """

    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    if not letters:
        return 0
    index = 0
    for char in letters.upper():
        index = index * 26 + ord(char) - 64
    return index - 1


def _read_shared_strings(zf: ZipFile) -> list[str]:
    """Read ``xl/sharedStrings.xml`` from an XLSX archive.

    Args:
        zf: Open XLSX zip archive.

    Returns:
        Shared string values in workbook order. Missing shared strings return an
        empty list because some workbooks store inline strings only.
    """

    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall("x:si", SPREADSHEET_NS):
        values.append("".join(text.text or "" for text in item.findall(".//x:t", SPREADSHEET_NS)))
    return values


def _cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    """Extract text from one XLSX cell element.

    Args:
        cell: XML cell element from worksheet XML.
        shared_strings: Shared string table loaded from the workbook.

    Returns:
        Cell text with no type conversion beyond shared-string resolution.
    """

    cell_type = cell.attrib.get("t")
    if cell_type == "s":
        value = cell.find("x:v", SPREADSHEET_NS)
        if value is None or value.text is None:
            return ""
        try:
            return shared_strings[int(value.text)]
        except (ValueError, IndexError):
            return ""
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//x:t", SPREADSHEET_NS))
    value = cell.find("x:v", SPREADSHEET_NS)
    return value.text if value is not None and value.text is not None else ""


def first_sheet_path(zf: ZipFile) -> str:
    """Return the first worksheet XML path from an XLSX archive.

    Args:
        zf: Open XLSX zip archive.

    Returns:
        Zip-internal worksheet path such as ``xl/worksheets/sheet1.xml``.
    """

    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    first_sheet = workbook.find(".//x:sheets/x:sheet", SPREADSHEET_NS)
    if first_sheet is None:
        return "xl/worksheets/sheet1.xml"
    rel_id = first_sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    if not rel_id or "xl/_rels/workbook.xml.rels" not in zf.namelist():
        return "xl/worksheets/sheet1.xml"
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    for rel in rels.findall("r:Relationship", REL_NS):
        if rel.attrib.get("Id") == rel_id:
            target = rel.attrib.get("Target", "worksheets/sheet1.xml")
            return "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
    return "xl/worksheets/sheet1.xml"


def read_xlsx_rows(path: Path) -> list[list[str]]:
    """Read the first worksheet of an XLSX file as rows of strings.

    Args:
        path: Path to an ``.xlsx`` workbook.

    Returns:
        A list of rows. Empty trailing cells are not padded beyond the last cell
        present in each row. Blank rows are skipped.
    """

    rows: list[list[str]] = []
    with ZipFile(path) as zf:
        shared_strings = _read_shared_strings(zf)
        sheet_path = first_sheet_path(zf)
        root = ET.fromstring(zf.read(sheet_path))
        for row in root.findall(".//x:sheetData/x:row", SPREADSHEET_NS):
            cells: dict[int, str] = {}
            for cell in row.findall("x:c", SPREADSHEET_NS):
                index = column_index(cell.attrib.get("r", "A1"))
                cells[index] = _cell_text(cell, shared_strings).strip()
            if not cells:
                continue
            max_index = max(cells)
            values = [cells.get(index, "") for index in range(max_index + 1)]
            if any(value for value in values):
                rows.append(values)
    return rows


def slug_header(value: str) -> str:
    """Normalize a Vietnamese Excel header for robust column matching.

    Args:
        value: Raw header cell value.

    Returns:
        Lowercase ASCII-ish key with punctuation collapsed to underscores.
    """

    value = value.lower().strip()
    replacements = {
        "đ": "d",
        "áàảãạăắằẳẵặâấầẩẫậ": "a",
        "éèẻẽẹêếềểễệ": "e",
        "íìỉĩị": "i",
        "óòỏõọôốồổỗộơớờởỡợ": "o",
        "úùủũụưứừửữự": "u",
        "ýỳỷỹỵ": "y",
    }
    for chars, repl in replacements.items():
        for ch in chars:
            value = value.replace(ch, repl)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")

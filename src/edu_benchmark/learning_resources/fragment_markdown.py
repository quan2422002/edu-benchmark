"""Split curated OCR Markdown into retrievable learning-resource fragments."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from edu_benchmark.learning_resources.ocr_text_manifest import read_csv_rows, write_csv_rows
from edu_benchmark.learning_resources.utils import ensure_directory

PAGE_SPLIT_RE = re.compile(r"^\{(?P<page_id>\d+)\}-+\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^\s{0,3}(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
IMAGE_ONLY_RE = re.compile(r"^\s*!\[[^\]]*\]\([^)]+\)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?", re.MULTILINE)

FRAGMENT_FIELDNAMES = [
    "fragment_id",
    "learning_material_id",
    "ocr_text_id",
    "material_type",
    "grade",
    "book_title",
    "lesson_key",
    "lesson_title",
    "topic_title",
    "page_start",
    "page_end",
    "page_marker_start",
    "page_marker_end",
    "section_label",
    "section_path",
    "fragment_type",
    "order_index",
    "location_note",
    "source_markdown_path",
    "markdown_text",
    "text_preview",
    "status",
    "needs_hnmu_review",
    "notes",
]


@dataclass
class PageChunk:
    """One page-like chunk split from OCR Markdown.
    
    Attributes:
        page_marker: OCR page marker extracted from ``{...}-----`` separators.
        printed_page: Printed page number inferred from the page body, if any.
        text: Markdown content belonging to this page-like chunk.
    """

    page_marker: str
    printed_page: str
    text: str


def strip_inline_markup(text: str) -> str:
    """Remove lightweight Markdown/HTML markup from short inline text.
    
    Args:
        text: A heading or other short Markdown/HTML-bearing string.
    
    Returns:
        Plain text with repeated whitespace collapsed.
    """

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[*_`]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def split_pages(markdown: str) -> list[PageChunk]:
    """Split a lesson Markdown document into page chunks.
    
    Args:
        markdown: Markdown content for one lesson or source unit.
    
    Returns:
        A list of ``PageChunk`` objects. If no OCR page markers exist, the entire
        document is returned as one chunk with empty page metadata.
    """

    matches = list(PAGE_SPLIT_RE.finditer(markdown))
    if not matches:
        return [PageChunk(page_marker="", printed_page="", text=markdown.strip())]
    chunks: list[PageChunk] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        printed_page = infer_printed_page(body)
        chunks.append(PageChunk(page_marker=match.group("page_id"), printed_page=printed_page, text=body))
    return chunks


def infer_printed_page(text: str) -> str:
    """Infer the printed page number from a page chunk.
    
    Args:
        text: Markdown text for one page-like chunk.
    
    Returns:
        The last numeric-only line near the end of the chunk, or an empty string
        when no printed page number is detected.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in reversed(lines[-4:]):
        if re.fullmatch(r"\d{1,3}", line):
            return line
    return ""


def is_heading(line: str) -> re.Match[str] | None:
    """Detect whether a line is a Markdown heading.
    
    Args:
        line: One Markdown line.
    
    Returns:
        A regex match object when the line is a heading; otherwise ``None``.
    """

    return HEADING_RE.match(line)


def is_table_start(lines: Sequence[str], index: int) -> bool:
    """Detect whether a line starts a Markdown table block.
    
    Args:
        lines: All lines in the current page chunk.
        index: Index of the candidate line.
    
    Returns:
        ``True`` when the current line looks like a table header followed by a
        separator row; otherwise ``False``.
    """

    if "|" not in lines[index]:
        return False
    return index + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[index + 1]) is not None


def collect_table(lines: Sequence[str], start: int) -> tuple[str, int]:
    """Collect contiguous Markdown table rows.
    
    Args:
        lines: All lines in the current page chunk.
        start: Index of the first table row.
    
    Returns:
        A ``(table_markdown, next_index)`` tuple, where ``next_index`` is the first
        unread line after the table.
    """

    table_lines: list[str] = []
    index = start
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        table_lines.append(lines[index])
        index += 1
    return "\n".join(table_lines).strip(), index


def cleanup_fragment_text(lines: Sequence[str]) -> str:
    """Normalize buffered Markdown before creating a fragment.
    
    Args:
        lines: Raw buffered lines from one section/table candidate.
    
    Returns:
        Clean Markdown with image-only lines removed and repeated blank lines
        collapsed.
    """

    cleaned: list[str] = []
    blank_seen = False
    for line in lines:
        stripped = line.rstrip()
        if IMAGE_ONLY_RE.match(stripped):
            continue
        if not stripped:
            if blank_seen:
                continue
            blank_seen = True
            cleaned.append("")
            continue
        blank_seen = False
        cleaned.append(stripped)
    return "\n".join(cleaned).strip()


def classify_fragment(section_path: str, text: str) -> str:
    """Assign a coarse fragment type from section labels and text cues.
    
    Args:
        section_path: Current heading path for the fragment.
        text: Fragment Markdown text.
    
    Returns:
        One fragment type such as ``table``, ``activity``, ``practice``,
        ``teaching_guidance``, ``answer_guidance``, or ``content``.
    """

    upper = f"{section_path}\n{text[:200]}".upper()
    if "|" in text and TABLE_SEPARATOR_RE.search(text):
        return "table"
    if "HOẠT ĐỘNG" in upper:
        return "activity"
    if "LUYỆN TẬP" in upper:
        return "practice"
    if "VẬN DỤNG" in upper:
        return "application"
    if "MỤC ĐÍCH" in upper or "YÊU CẦU" in upper:
        return "teaching_objective"
    if "GỢI Ý" in upper or "HƯỚNG DẪN" in upper:
        return "teaching_guidance"
    if "ĐÁP ÁN" in upper:
        return "answer_guidance"
    return "content"


def preview_text(markdown: str, limit: int = 240) -> str:
    """Create a compact plain-text preview for reports and retrieval.
    
    Args:
        markdown: Fragment Markdown text.
        limit: Maximum number of characters to keep.
    
    Returns:
        Plain-text preview with Markdown syntax and repeated whitespace removed.
    """

    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", markdown)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[#*_`|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def normalize_section_path(section_stack: dict[int, str]) -> str:
    """Convert the current heading stack into a section path.
    
    Args:
        section_stack: Mapping from heading level to clean heading title.
    
    Returns:
        A human-readable path such as ``Chủ đề A > Bài 3 > Hoạt động``.
    """

    return " > ".join(section_stack[level] for level in sorted(section_stack) if section_stack[level])


def should_keep_fragment(text: str) -> bool:
    """Decide whether buffered Markdown is useful enough to index.
    
    Args:
        text: Candidate fragment Markdown.
    
    Returns:
        ``True`` for non-trivial content or tables; ``False`` for very short,
        heading-only, or otherwise low-value fragments.
    """

    plain = preview_text(text, limit=1000)
    if len(plain) < 35:
        return False
    non_heading_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or HEADING_RE.match(stripped):
            continue
        non_heading_lines.append(stripped)
    non_heading_plain = preview_text("\n".join(non_heading_lines), limit=1000)
    return len(non_heading_plain) >= 25 or ("|" in text and TABLE_SEPARATOR_RE.search(text) is not None)


def fragment_manifest_row(row: dict[str, str], *, next_order: int, material_counter: int) -> list[dict[str, object]]:
    """Split one manifest row into traceable learning-resource fragments.
    
    Args:
        row: One row from ``ocr_text_manifest.csv``.
        next_order: Current global order counter used to preserve source order.
        material_counter: Current fragment counter for the learning material.
    
    Returns:
        Fragment rows with IDs, source metadata, page markers, section paths,
        Markdown text, review status, and notes.
    """

    path = Path(row["source_markdown_path"])
    markdown = path.read_text(encoding="utf-8", errors="replace")
    chunks = split_pages(markdown)
    fragments: list[dict[str, object]] = []
    section_stack: dict[int, str] = {}
    fragment_counter = material_counter

    for chunk in chunks:
        lines = chunk.text.splitlines()
        buffer: list[str] = []
        section_label = ""
        index = 0

        def flush_buffer() -> None:
            """Emit the current buffered text as one fragment when useful.
            
            Args:
                None. Uses the enclosing page/section buffer and counters.
            
            Returns:
                None. Appends to the enclosing ``fragments`` list when the buffer passes
                the keep rules.
            """

            nonlocal buffer, fragment_counter, next_order
            text = cleanup_fragment_text(buffer)
            buffer = []
            if not text or not should_keep_fragment(text):
                return
            fragment_counter += 1
            next_order += 1
            section_path = normalize_section_path(section_stack)
            fragment_type = classify_fragment(section_path, text)
            section = section_label or section_path or row.get("lesson_title", "")
            location_parts = [part for part in [row.get("lesson_title", ""), section_path] if part]
            page_label = chunk.printed_page or f"page_marker {chunk.page_marker}" if chunk.page_marker else ""
            if page_label:
                location_parts.append(f"trang {page_label}")
            fragments.append(
                {
                    "fragment_id": f"{row['learning_material_id']}#F{fragment_counter:04d}",
                    "learning_material_id": row.get("learning_material_id", ""),
                    "ocr_text_id": row.get("ocr_text_id", ""),
                    "material_type": row.get("material_type", ""),
                    "grade": row.get("grade", ""),
                    "book_title": row.get("book_title", ""),
                    "lesson_key": row.get("lesson_key", ""),
                    "lesson_title": row.get("lesson_title", ""),
                    "topic_title": row.get("topic_title", ""),
                    "page_start": chunk.printed_page,
                    "page_end": chunk.printed_page,
                    "page_marker_start": chunk.page_marker,
                    "page_marker_end": chunk.page_marker,
                    "section_label": section,
                    "section_path": section_path,
                    "fragment_type": fragment_type,
                    "order_index": next_order,
                    "location_note": " > ".join(location_parts),
                    "source_markdown_path": row.get("source_markdown_path", ""),
                    "markdown_text": text,
                    "text_preview": preview_text(text),
                    "status": "draft",
                    "needs_hnmu_review": "true" if fragment_type in {"teaching_guidance", "answer_guidance"} else "false",
                    "notes": "Sinh tự động từ Markdown OCR của Nguyên; chưa HNMU xác nhận.",
                }
            )

        while index < len(lines):
            line = lines[index]
            heading = is_heading(line)
            if heading:
                flush_buffer()
                level = len(heading.group("marks"))
                title = strip_inline_markup(heading.group("title"))
                section_stack = {k: v for k, v in section_stack.items() if k < level}
                section_stack[level] = title
                section_label = title
                buffer.append(line)
                index += 1
                continue
            if is_table_start(lines, index):
                flush_buffer()
                table, next_index = collect_table(lines, index)
                buffer = [table]
                flush_buffer()
                index = next_index
                continue
            buffer.append(line)
            index += 1
        flush_buffer()
    return fragments


def build_fragments(manifest_path: Path) -> list[dict[str, object]]:
    """Build all fragments from an OCR text manifest.
    
    Args:
        manifest_path: Path to ``ocr_text_manifest.csv``.
    
    Returns:
        A list of fragment rows ready to write to ``learning_resource_fragments.csv``.
    """

    rows = read_csv_rows(manifest_path)
    fragments: list[dict[str, object]] = []
    counters: dict[str, int] = {}
    order = 0
    for row in rows:
        material_id = row.get("learning_material_id", "")
        start_counter = counters.get(material_id, 0)
        row_fragments = fragment_manifest_row(row, next_order=order, material_counter=start_counter)
        if row_fragments:
            counters[material_id] = int(str(row_fragments[-1]["fragment_id"]).split("#F")[-1])
            order = int(row_fragments[-1]["order_index"])
            fragments.extend(row_fragments)
    return fragments


def write_fragments(rows: Sequence[dict[str, object]], output_path: Path) -> None:
    """Write fragment rows to the canonical fragment CSV path.
    
    Args:
        rows: Fragment rows produced by ``build_fragments``.
        output_path: Destination CSV path.
    
    Returns:
        None. The output file is overwritten deterministically.
    """

    write_csv_rows(output_path, rows, FRAGMENT_FIELDNAMES)


def write_fragments_readme(path: Path) -> None:
    """Write the fragment-table README.
    
    Args:
        path: Destination README path, usually
            ``shared/learning_resources/fragments/README.md``.
    
    Returns:
        None.
    """

    ensure_directory(path.parent)
    path.write_text(
        """# Learning-resource fragments v0

Thư mục này chứa các đoạn học liệu được tách từ Markdown OCR của Nguyên trong `shared/learning_resources/ocr_text`.

- `learning_resource_fragments.csv`: bảng fragment chính cho Pha 4–5.
- Fragment đang ở trạng thái `draft` hoặc cần review; chưa coi là xác nhận chuyên môn của HNMU.
- Không sửa ý nghĩa của một `fragment_id` đã được dùng; nếu cần loại bỏ thì chuyển sang `retired`.
- File nguồn OCR Markdown là read-only; mọi chuẩn hóa/tách đoạn nằm trong bảng dẫn xuất này.
""",
        encoding="utf-8",
    )

"""Lossless v1 fragmentation for registered OCR Markdown resources.

The historical v0 fragmenter remains unchanged. This module uses a separate ID
namespace, removes page-marker lines without using them as split boundaries,
and stores every remaining canonical Markdown character exactly once.
"""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

from edu_benchmark.learning_resources.ocr_text_manifest import read_csv_rows


CANONICAL_VERSION = "learning-resource-markdown-v1"
FRAGMENT_RELEASE_V1_1 = "v1.1"
PAGE_MARKER_RE = re.compile(
    r"^[ \t]*\{(?P<page_id>\d+)\}-{3,}[ \t]*(?:\r?\n|$)",
    re.MULTILINE,
)
HEADING_RE = re.compile(r"^\s{0,3}(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?")
FENCE_RE = re.compile(r"^\s{0,3}(?P<fence>`{3,}|~{3,})")
HTML_CAPTION_RE = re.compile(
    r"<caption\b[^>]*>(?P<caption>.*?)</caption>",
    re.IGNORECASE | re.DOTALL,
)
VISIBLE_CAPTION_RE = re.compile(
    r"^\s*(?:#{1,6}\s+)?(?:\*\*|__)?\s*"
    r"(?P<caption>(?:Bảng|Hình)\s+"
    r"(?:\d+[a-z]?|[IVXLCDM]+)(?:\.\d+[a-z]?)*"
    r"(?:[.:](?:\s+.*?)?)?)"
    r"\s*(?:\*\*|__)?\s*$",
    re.IGNORECASE,
)
SBT_EXERCISE_RE = re.compile(
    r"^\s*(?:#{1,6}\s+)?(?:\*\*|__)?\s*"
    r"(?P<label>\d{1,2}[a-z]?\.\d{1,2}\.)"
    r"(?:\*\*|__)?(?=\s|$)",
    re.IGNORECASE,
)

FRAGMENT_FIELDNAMES = [
    "fragment_id",
    "section_id",
    "learning_material_id",
    "ocr_text_id",
    "material_type",
    "grade",
    "book_title",
    "lesson_key",
    "lesson_title",
    "topic_title",
    "canonical_version",
    "source_sha256",
    "canonical_sha256",
    "fragment_index",
    "order_index",
    "char_start",
    "char_end",
    "page_start",
    "page_end",
    "page_marker_start",
    "page_marker_end",
    "page_markers_json",
    "page_basis",
    "section_label",
    "section_path",
    "section_depth",
    "fragment_type",
    "table_caption",
    "caption_status",
    "caption_position",
    "caption_source_markdown",
    "caption_char_start",
    "caption_char_end",
    "source_markdown_path",
    "markdown_text",
    "text_preview",
    "status",
    "needs_hnmu_review",
    "notes",
]

FRAGMENT_V1_1_FIELDNAMES = [
    *FRAGMENT_FIELDNAMES,
    "fragment_release",
    "effective_content_length",
    "merge_status",
    "merge_reason",
    "merge_policy_version",
    "merged_from_fragment_ids_json",
    "merged_from_fragment_count",
    "source_fragment_types_json",
    "source_fragment_index_start",
    "source_fragment_index_end",
]

SEMANTIC_BOUNDARY_REVIEW_VERSION = "fragment-v1.1-semantic-boundary-review-v1"
SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES = [
    "review_id",
    "review_contract_version",
    "boundary_kind",
    "threshold_effective_chars",
    "boundary_side",
    "selection_rank",
    "primary_window_min",
    "primary_window_max",
    "in_primary_window",
    "distance_to_threshold",
    "candidate_origin",
    "fragment_id",
    "source_fragment_ids_json",
    "source_fragment_count",
    "source_fragment_types_json",
    "grade",
    "material_type",
    "learning_material_id",
    "ocr_text_id",
    "lesson_key",
    "lesson_title",
    "topic_title",
    "section_path",
    "fragment_type",
    "effective_content_length",
    "effective_content",
    "text_preview",
    "markdown_text",
    "merge_policy_version",
    "text_min_effective_chars",
    "text_max_effective_chars",
    "table_absorption_max_effective_chars",
    "neighbor_policy",
    "review_self_contained_evidence",
    "review_semantic_focus",
    "review_evidence_dilution",
    "review_reason",
    "reviewer",
    "review_status",
]

SEMANTIC_REVIEW_WORKBOOK_VERSION = "fragment-v1.1-semantic-review-workbook-v1"
SEMANTIC_REVIEW_WORKBOOK_SHEETS = ("Hướng dẫn", "Cận dưới", "Cận trên")
LOWER_REVIEW_HEADERS = [
    "Mã mẫu",
    "Ngưỡng (ký tự)",
    "Vị trí so với ngưỡng",
    "Lớp",
    "Loại sách",
    "Bài học",
    "Đầu mục",
    "Độ dài hiệu dụng",
    "Nội dung đoạn học liệu",
    "Đủ ngữ cảnh làm bằng chứng?",
    "Lý do",
    "Người rà soát",
]
UPPER_REVIEW_HEADERS = [
    "Mã mẫu",
    "Ngưỡng (ký tự)",
    "Loại mẫu",
    "Lớp",
    "Loại sách",
    "Bài học",
    "Đầu mục",
    "Độ dài hiệu dụng",
    "Nội dung đoạn học liệu",
    "Có một trọng tâm rõ ràng?",
    "Độ dài vẫn phù hợp?",
    "Lý do",
    "Người rà soát",
]
HUMAN_REVIEW_LABELS = ("Có", "Không", "Chưa chắc")

MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^\n)]*\)")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^\n)]*\)")
STANDALONE_PAGE_NUMBER_RE = re.compile(
    r"^\s*(?:trang\s+)?\d+\s*$",
    re.IGNORECASE,
)
TABLE_DIVIDER_LINE_RE = re.compile(
    r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$"
)
V1_1_MERGE_POLICY_VERSION = "fragment-v1.1-structural-bounded-v4"
V1_1_NEIGHBOR_POLICIES = frozenset(
    {
        "prefer_short_group",
        "prefer_previous",
        "prefer_next",
        "prefer_closest_to_min",
    }
)

SECTION_FIELDNAMES = [
    "section_id",
    "parent_section_id",
    "learning_material_id",
    "ocr_text_id",
    "material_type",
    "grade",
    "book_title",
    "lesson_key",
    "lesson_title",
    "topic_title",
    "section_level",
    "section_kind",
    "section_label",
    "section_path",
    "source_markdown_path",
    "first_fragment_index",
    "last_fragment_index",
    "char_start",
    "char_end",
    "status",
    "needs_hnmu_review",
    "notes",
]


@dataclass(frozen=True)
class PageMarker:
    """One removed OCR page marker and its offset in canonical Markdown."""

    page_id: str
    source_start: int
    source_end: int
    canonical_offset: int


@dataclass(frozen=True)
class CanonicalMarkdown:
    """Canonical Markdown plus source hashes and removed marker provenance."""

    text: str
    source_sha256: str
    canonical_sha256: str
    page_markers: tuple[PageMarker, ...]


@dataclass(frozen=True)
class MarkdownLine:
    """One source-preserving Markdown line with canonical character offsets."""

    text: str
    start: int
    end: int
    in_fence: bool


@dataclass(frozen=True)
class TableSpan:
    """A Markdown table expanded to include a source caption when present."""

    table_index: int
    core_start: int
    core_end: int
    fragment_start: int
    fragment_end: int
    caption: str
    caption_status: str
    caption_position: str
    caption_source_markdown: str
    caption_char_start: int | None
    caption_char_end: int | None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonicalize_markdown(markdown: str) -> CanonicalMarkdown:
    """Remove only page-marker lines and preserve every other character."""

    pieces: list[str] = []
    page_markers: list[PageMarker] = []
    source_cursor = 0
    canonical_length = 0
    for match in PAGE_MARKER_RE.finditer(markdown):
        prefix = markdown[source_cursor : match.start()]
        pieces.append(prefix)
        canonical_length += len(prefix)
        page_markers.append(
            PageMarker(
                page_id=match.group("page_id"),
                source_start=match.start(),
                source_end=match.end(),
                canonical_offset=canonical_length,
            )
        )
        source_cursor = match.end()
    pieces.append(markdown[source_cursor:])
    canonical_text = "".join(pieces)
    return CanonicalMarkdown(
        text=canonical_text,
        source_sha256=_sha256_text(markdown),
        canonical_sha256=_sha256_text(canonical_text),
        page_markers=tuple(page_markers),
    )


def _markdown_lines(text: str) -> list[MarkdownLine]:
    lines: list[MarkdownLine] = []
    cursor = 0
    active_fence: str | None = None
    for raw_line in text.splitlines(keepends=True):
        visible_line = raw_line.rstrip("\r\n")
        fence = FENCE_RE.match(visible_line)
        in_fence = active_fence is not None
        if fence:
            marker = fence.group("fence")[0]
            if active_fence is None:
                active_fence = marker
            elif active_fence == marker:
                active_fence = None
            in_fence = True
        end = cursor + len(raw_line)
        lines.append(MarkdownLine(text=raw_line, start=cursor, end=end, in_fence=in_fence))
        cursor = end
    return lines


def _plain_inline_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[*_`]+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _match_key(value: str) -> str:
    value = _plain_inline_text(value).casefold()
    value = re.sub(r"[^0-9a-zà-ỹ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _lesson_code(value: str) -> str:
    match = re.match(r"^bài\s*(\d{1,2})\s*([a-b]?)", value, flags=re.IGNORECASE)
    return f"{int(match.group(1))}{match.group(2).casefold()}" if match else ""


def _topic_code(value: str) -> str:
    match = re.match(r"^chủ\s*đề\s*(\d+|[a-z])", value, flags=re.IGNORECASE)
    return match.group(1).casefold() if match else ""


def _without_lesson_prefix(value: str) -> str:
    return re.sub(
        r"^bài\s*\d{1,2}\s*[a-b]?\s*[:.\-–—]*\s*",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()


def _is_metadata_duplicate(title: str, metadata_parts: Sequence[str]) -> bool:
    title_key = _match_key(title)
    if not title_key:
        return True
    for part in metadata_parts:
        part_key = _match_key(part)
        if title_key == part_key:
            return True
        if title_key == _match_key(_without_lesson_prefix(part)):
            return True
        if _lesson_code(title) and _lesson_code(title) == _lesson_code(part):
            return True
        if _topic_code(title) and _topic_code(title) == _topic_code(part):
            return True
        if len(title_key) >= 8 and (part_key.endswith(title_key) or title_key.endswith(part_key)):
            return True
    return False


def _metadata_section_parts(row: dict[str, str]) -> tuple[list[str], int, bool]:
    topic_parts = [
        _plain_inline_text(part)
        for part in row.get("topic_title", "").split(">")
        if _plain_inline_text(part)
    ]
    topic_count = len(topic_parts)
    lesson = _plain_inline_text(row.get("lesson_title", ""))
    lesson_added = bool(lesson and not _is_metadata_duplicate(lesson, topic_parts))
    if lesson_added:
        topic_parts.append(lesson)
    return topic_parts, topic_count, lesson_added


def _caption_from_text(value: str) -> str:
    html_match = HTML_CAPTION_RE.search(value)
    if html_match:
        return _plain_inline_text(html_match.group("caption"))
    visible = value.rstrip("\r\n")
    match = VISIBLE_CAPTION_RE.match(visible)
    return _plain_inline_text(match.group("caption")) if match else ""


def _adjacent_source_caption(value: str) -> str:
    """Return a conservative caption candidate from one adjacent source line.

    
    """

    visible = value.rstrip("\r\n")
    if not visible.strip() or HEADING_RE.match(visible):
        return ""
    if (
        "|" in visible
        or MARKDOWN_IMAGE_RE.search(visible)
        or HTML_IMAGE_RE.search(visible)
        or HTML_COMMENT_RE.search(visible)
        or STANDALONE_PAGE_NUMBER_RE.match(visible)
    ):
        return ""
    if SBT_EXERCISE_RE.match(visible):
        return ""
    if re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", visible):
        return ""
    caption = _plain_inline_text(visible)
    if re.fullmatch(r"\[?hình ảnh\]?", caption, flags=re.IGNORECASE):
        return ""
    words = caption.split()
    if not 2 <= len(words) <= 12 or len(caption) > 100:
        return ""
    if caption.endswith((".", ":", ";", "?", "!")):
        return ""
    letters = [character for character in caption if character.isalpha()]
    if letters and caption.upper() == caption:
        return ""
    return caption


def _sbt_exercise_label(value: str) -> str:
    """Extract a stable SBT exercise identifier such as ``10a.6.``."""

    match = SBT_EXERCISE_RE.match(value.rstrip("\r\n"))
    return match.group("label").casefold() if match else ""


def _is_orphan_heading_before_sbt_segment(
    lines: Sequence[MarkdownLine],
    index: int,
) -> bool:
    """Identify a heading-only tail immediately before a generated SBT boundary.

    Lessonization marks the boundary between the exercise and solution spans with
    an ``edu-benchmark:sbt-segment`` comment followed by a level-one part
    heading. A source heading with no intervening content belongs to the next
    source span, so it must not change this lesson's section hierarchy. Its
    Markdown remains in the canonical text and in the preceding fragment.
    """

    saw_segment_marker = False
    for candidate in lines[index + 1 :]:
        visible = candidate.text.rstrip("\r\n")
        if not visible.strip():
            continue
        if HTML_COMMENT_RE.fullmatch(visible.strip()):
            if "edu-benchmark:sbt-segment" in visible:
                saw_segment_marker = True
            continue
        heading = HEADING_RE.match(visible)
        return bool(
            saw_segment_marker
            and heading is not None
            and len(heading.group("marks")) == 1
        )
    return False


def _append_unique_section_part(parts: list[str], value: str) -> None:
    """Append one semantic path component unless an equivalent ancestor exists."""

    value_key = _match_key(value)
    if value_key and all(_match_key(part) != value_key for part in parts):
        parts.append(value)


def _nearest_nonempty_before(lines: Sequence[MarkdownLine], index: int) -> int | None:
    blank_count = 0
    for candidate in range(index - 1, -1, -1):
        if lines[candidate].text.strip():
            return candidate
        blank_count += 1
        if blank_count > 2:
            break
    return None


def _nearest_nonempty_after(lines: Sequence[MarkdownLine], index: int) -> int | None:
    blank_count = 0
    for candidate in range(index, len(lines)):
        if lines[candidate].text.strip():
            return candidate
        blank_count += 1
        if blank_count > 2:
            break
    return None


def _detect_table_spans(lines: Sequence[MarkdownLine]) -> list[TableSpan]:
    cores: list[tuple[int, int, int, int]] = []
    index = 0
    while index + 1 < len(lines):
        header = lines[index].text.rstrip("\r\n")
        separator = lines[index + 1].text.rstrip("\r\n")
        if (
            not lines[index].in_fence
            and not lines[index + 1].in_fence
            and "|" in header
            and TABLE_SEPARATOR_RE.match(separator)
        ):
            end_index = index + 2
            while end_index < len(lines):
                candidate = lines[end_index].text.rstrip("\r\n")
                if lines[end_index].in_fence or not candidate.strip() or "|" not in candidate:
                    break
                end_index += 1
            cores.append((index, end_index, lines[index].start, lines[end_index - 1].end))
            index = end_index
            continue
        index += 1

    exact_before: list[tuple[int, str] | None] = []
    exact_after: list[tuple[int, str] | None] = []
    for start_line, end_line, _, _ in cores:
        before = _nearest_nonempty_before(lines, start_line)
        before_caption = (
            _caption_from_text(lines[before].text) if before is not None else ""
        )
        exact_before.append((before, before_caption) if before_caption else None)

        after = _nearest_nonempty_after(lines, end_line)
        after_caption = (
            _caption_from_text(lines[after].text) if after is not None else ""
        )
        exact_after.append((after, after_caption) if after_caption else None)

    claimed_caption_lines: set[int] = set()
    spans: list[TableSpan] = []
    for core_index, (start_line, end_line, core_start, core_end) in enumerate(cores):
        table_index = core_index + 1
        caption = _caption_from_text("".join(line.text for line in lines[start_line:end_line]))
        caption_status = "exact" if caption else "missing"
        caption_position = "inline" if caption else "none"
        caption_source = ""
        caption_start: int | None = None
        caption_end: int | None = None
        fragment_start = core_start
        fragment_end = core_end

        if not caption:
            before_candidate = exact_before[core_index]
            if before_candidate is not None:
                before, before_caption = before_candidate
                shared_with_previous = (
                    core_index > 0
                    and exact_after[core_index - 1] is not None
                    and exact_after[core_index - 1][0] == before
                )
                figure_caption_for_previous = (
                    shared_with_previous
                    and before_caption.casefold().startswith("hình ")
                )
                if before not in claimed_caption_lines and not figure_caption_for_previous:
                    caption = before_caption
                    caption_status = "exact"
                    caption_position = "before"
                    caption_source = lines[before].text.rstrip("\r\n")
                    caption_start = lines[before].start
                    caption_end = lines[before].end
                    fragment_start = lines[before].start
                    claimed_caption_lines.add(before)
        if not caption:
            after = _nearest_nonempty_after(lines, end_line)
            if after is not None:
                after_candidate = exact_after[core_index]
                after_caption = (
                    after_candidate[1] if after_candidate is not None else ""
                )
                shared_with_next = (
                    core_index + 1 < len(cores)
                    and exact_before[core_index + 1] is not None
                    and exact_before[core_index + 1][0] == after
                )
                table_caption_for_next = (
                    shared_with_next
                    and after_caption.casefold().startswith("bảng ")
                )
                if (
                    after_caption
                    and after not in claimed_caption_lines
                    and not table_caption_for_next
                ):
                    caption = after_caption
                    caption_status = "exact"
                    caption_position = "after"
                    caption_source = lines[after].text.rstrip("\r\n")
                    caption_start = lines[after].start
                    caption_end = lines[after].end
                    fragment_end = lines[after].end
                    claimed_caption_lines.add(after)
                elif not after_caption and after not in claimed_caption_lines:
                    caption = _adjacent_source_caption(lines[after].text)
                    if caption:
                        caption_status = "adjacent_source"
                        caption_position = "after"
                        caption_source = lines[after].text.rstrip("\r\n")
                        caption_start = lines[after].start
                        caption_end = lines[after].end
                        fragment_end = lines[after].end
                        claimed_caption_lines.add(after)
        if caption_position == "inline":
            inline_text = "".join(line.text for line in lines[start_line:end_line])
            inline_match = HTML_CAPTION_RE.search(inline_text)
            if inline_match:
                caption_start = core_start + inline_match.start()
                caption_end = core_start + inline_match.end()
                caption_source = inline_match.group(0)

        if not caption:
            caption = f"Bảng chưa có caption nguồn [T{table_index:04d}]"
            caption_status = "missing"

        spans.append(
            TableSpan(
                table_index=table_index,
                core_start=core_start,
                core_end=core_end,
                fragment_start=fragment_start,
                fragment_end=fragment_end,
                caption=caption,
                caption_status=caption_status,
                caption_position=caption_position,
                caption_source_markdown=caption_source,
                caption_char_start=caption_start,
                caption_char_end=caption_end,
            )
        )

    for previous, current in zip(spans, spans[1:]):
        if previous.fragment_end > current.fragment_start:
            raise ValueError(
                "overlapping table/caption spans: "
                f"T{previous.table_index:04d} and T{current.table_index:04d}"
            )
    return spans


def _page_span(
    markers: Sequence[PageMarker],
    start: int,
    end: int,
) -> tuple[str, str, str]:
    if not markers:
        return "", "", "[]"
    offsets = [marker.canonical_offset for marker in markers]
    current_index = bisect.bisect_right(offsets, start) - 1
    selected: list[PageMarker] = []
    if current_index >= 0:
        selected.append(markers[current_index])
    for marker in markers[max(current_index + 1, 0) :]:
        if marker.canonical_offset >= end:
            break
        selected.append(marker)
    page_ids = list(dict.fromkeys(marker.page_id for marker in selected))
    if not page_ids:
        return "", "", "[]"
    return page_ids[0], page_ids[-1], json.dumps(page_ids, ensure_ascii=False)


def preview_text(markdown: str, limit: int = 240) -> str:
    """Create a display-only preview without changing stored Markdown."""

    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", markdown)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[#*_`|]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()[:limit]


def _section_kind(level: int, *, topic_count: int, lesson_added: bool, is_table_leaf: bool) -> str:
    if is_table_leaf:
        return "table_caption"
    if level <= topic_count:
        return "topic"
    if lesson_added and level == topic_count + 1:
        return "lesson"
    return "heading"


def _register_sections(
    *,
    row: dict[str, str],
    fragments: list[dict[str, Any]],
    topic_count: int,
    lesson_added: bool,
) -> list[dict[str, Any]]:
    section_ids: dict[tuple[str, ...], str] = {}
    section_rows: dict[tuple[str, ...], dict[str, Any]] = {}
    for fragment in fragments:
        parts = tuple(fragment.pop("_section_parts"))
        for level in range(1, len(parts) + 1):
            path_parts = parts[:level]
            is_table_leaf = (
                fragment["fragment_type"] == "table"
                and fragment["caption_status"] in {"exact", "adjacent_source"}
                and level == len(parts)
            )
            if path_parts not in section_ids:
                section_id = f"{row['ocr_text_id']}#V1S{len(section_ids) + 1:04d}"
                section_ids[path_parts] = section_id
                section_rows[path_parts] = {
                    "section_id": section_id,
                    "parent_section_id": section_ids.get(path_parts[:-1], ""),
                    "learning_material_id": row.get("learning_material_id", ""),
                    "ocr_text_id": row.get("ocr_text_id", ""),
                    "material_type": row.get("material_type", ""),
                    "grade": row.get("grade", ""),
                    "book_title": row.get("book_title", ""),
                    "lesson_key": row.get("lesson_key", ""),
                    "lesson_title": row.get("lesson_title", ""),
                    "topic_title": row.get("topic_title", ""),
                    "section_level": level,
                    "section_kind": _section_kind(
                        level,
                        topic_count=topic_count,
                        lesson_added=lesson_added,
                        is_table_leaf=is_table_leaf,
                    ),
                    "section_label": path_parts[-1],
                    "section_path": " > ".join(path_parts),
                    "source_markdown_path": row.get("source_markdown_path", ""),
                    "first_fragment_index": fragment["fragment_index"],
                    "last_fragment_index": fragment["fragment_index"],
                    "char_start": fragment["char_start"],
                    "char_end": fragment["char_end"],
                    "status": row.get("status", "draft") or "draft",
                    "needs_hnmu_review": "true",
                    "notes": (
                        "Derived v1 section from manifest metadata and source "
                        "Markdown headings."
                    ),
                }
            else:
                section = section_rows[path_parts]
                section["last_fragment_index"] = fragment["fragment_index"]
                section["char_end"] = fragment["char_end"]
                if is_table_leaf:
                    section["section_kind"] = "table_caption"
            if level == len(parts):
                fragment["section_id"] = section_ids[path_parts]
    return list(section_rows.values())


def _resolve_source_path(row: dict[str, str], repo_root: Path) -> Path:
    raw_path = Path(row["source_markdown_path"])
    source_path = raw_path if raw_path.is_absolute() else repo_root / raw_path
    source_path = source_path.resolve()
    try:
        source_path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"source_markdown_path is outside repo_root: {raw_path}") from exc
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    return source_path


def fragment_manifest_row_v1(
    row: dict[str, str],
    *,
    repo_root: Path,
    next_order: int = 0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], CanonicalMarkdown]:
    """Build lossless fragments and canonical sections for one manifest row."""

    source_path = _resolve_source_path(row, repo_root)
    canonical = canonicalize_markdown(source_path.read_text(encoding="utf-8", errors="strict"))
    if not canonical.text:
        raise ValueError(f"canonical Markdown is empty: {row['source_markdown_path']}")
    lines = _markdown_lines(canonical.text)
    table_spans = _detect_table_spans(lines)

    def inside_table_span(offset: int) -> bool:
        return any(table.fragment_start <= offset < table.fragment_end for table in table_spans)

    headings: dict[int, tuple[int, str]] = {}
    exercise_starts: dict[int, str] = {}
    is_sbt = row.get("material_type", "").strip().upper() == "SBT"
    for line_index, line in enumerate(lines):
        if line.in_fence or inside_table_span(line.start):
            continue
        heading = HEADING_RE.match(line.text.rstrip("\r\n"))
        if heading and not (
            is_sbt and _is_orphan_heading_before_sbt_segment(lines, line_index)
        ):
            headings[line.start] = (
                len(heading.group("marks")),
                _plain_inline_text(heading.group("title")),
            )
        if is_sbt:
            exercise_label = _sbt_exercise_label(line.text)
            if exercise_label:
                exercise_starts[line.start] = exercise_label

    boundaries = {0, len(canonical.text), *headings.keys(), *exercise_starts.keys()}
    table_by_start: dict[int, TableSpan] = {}
    for table in table_spans:
        boundaries.add(table.fragment_start)
        boundaries.add(table.fragment_end)
        table_by_start[table.fragment_start] = table
    ordered_boundaries = sorted(boundaries)

    metadata_parts, topic_count, lesson_added = _metadata_section_parts(row)
    local_headings: dict[int, str] = {}
    active_exercise = ""
    exercise_level: int | None = None
    fragments: list[dict[str, Any]] = []
    for start, end in zip(ordered_boundaries, ordered_boundaries[1:]):
        if start in exercise_starts:
            active_exercise = exercise_starts[start]
            if start in headings:
                exercise_level = headings[start][0]
            elif exercise_level is None:
                exercise_level = max(local_headings, default=0) + 1
            local_headings = {
                level: title
                for level, title in local_headings.items()
                if level < exercise_level
            }
        elif start in headings:
            heading_level, heading_title = headings[start]
            if exercise_level is not None and heading_level <= exercise_level:
                active_exercise = ""
                exercise_level = None
            local_headings = {
                level: title
                for level, title in local_headings.items()
                if level < heading_level
            }
            if not _is_metadata_duplicate(heading_title, metadata_parts):
                local_headings[heading_level] = heading_title
        if end <= start:
            continue
        candidate_table = table_by_start.get(start)
        table = (
            candidate_table
            if candidate_table is not None and candidate_table.fragment_end == end
            else None
        )
        section_local_parts: list[str] = []
        exercise_inserted = False
        for level in sorted(local_headings):
            if (
                active_exercise
                and exercise_level is not None
                and not exercise_inserted
                and level > exercise_level
            ):
                _append_unique_section_part(section_local_parts, active_exercise)
                exercise_inserted = True
            _append_unique_section_part(section_local_parts, local_headings[level])
        if active_exercise and not exercise_inserted:
            _append_unique_section_part(section_local_parts, active_exercise)
        section_parts = metadata_parts + section_local_parts
        if not section_parts:
            fallback = _plain_inline_text(row.get("first_heading", "")) or row["ocr_text_id"]
            section_parts = [fallback]
        if (
            table is not None
            and table.caption_status in {"exact", "adjacent_source"}
            and (not section_parts or section_parts[-1] != table.caption)
        ):
            section_parts = [*section_parts, table.caption]

        page_start, page_end, page_markers_json = _page_span(canonical.page_markers, start, end)
        fragment_index = len(fragments) + 1
        text = canonical.text[start:end]
        fragments.append(
            {
                "fragment_id": f"{row['ocr_text_id']}#V1F{fragment_index:04d}",
                "section_id": "",
                "learning_material_id": row.get("learning_material_id", ""),
                "ocr_text_id": row.get("ocr_text_id", ""),
                "material_type": row.get("material_type", ""),
                "grade": row.get("grade", ""),
                "book_title": row.get("book_title", ""),
                "lesson_key": row.get("lesson_key", ""),
                "lesson_title": row.get("lesson_title", ""),
                "topic_title": row.get("topic_title", ""),
                "canonical_version": CANONICAL_VERSION,
                "source_sha256": canonical.source_sha256,
                "canonical_sha256": canonical.canonical_sha256,
                "fragment_index": fragment_index,
                "order_index": next_order + fragment_index,
                "char_start": start,
                "char_end": end,
                "page_start": page_start,
                "page_end": page_end,
                "page_marker_start": page_start,
                "page_marker_end": page_end,
                "page_markers_json": page_markers_json,
                "page_basis": "ocr_page_marker" if page_start else "unavailable",
                "section_label": section_parts[-1],
                "section_path": " > ".join(section_parts),
                "section_depth": len(section_parts),
                "fragment_type": "table" if table is not None else "text",
                "table_caption": table.caption if table is not None else "",
                "caption_status": table.caption_status if table is not None else "not_applicable",
                "caption_position": (
                    table.caption_position if table is not None else "not_applicable"
                ),
                "caption_source_markdown": (
                    table.caption_source_markdown if table is not None else ""
                ),
                "caption_char_start": (
                    table.caption_char_start
                    if table is not None and table.caption_char_start is not None
                    else ""
                ),
                "caption_char_end": (
                    table.caption_char_end
                    if table is not None and table.caption_char_end is not None
                    else ""
                ),
                "source_markdown_path": row.get("source_markdown_path", ""),
                "markdown_text": text,
                "text_preview": preview_text(text),
                "status": row.get("status", "draft") or "draft",
                "needs_hnmu_review": "true",
                "notes": (
                    "Lossless v1 fragment; only OCR page-marker lines are absent "
                    "from canonical Markdown."
                ),
                "_section_parts": section_parts,
            }
        )
    sections = _register_sections(
        row=row,
        fragments=fragments,
        topic_count=topic_count,
        lesson_added=lesson_added,
    )
    return fragments, sections, canonical


def build_fragment_bundle_v1(
    manifest_path: Path,
    *,
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Build v1 section and fragment rows for every manifest unit."""

    fragments: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    order = 0
    marker_count = 0
    for row in read_csv_rows(manifest_path):
        row_fragments, row_sections, canonical = fragment_manifest_row_v1(
            row,
            repo_root=repo_root,
            next_order=order,
        )
        order += len(row_fragments)
        marker_count += len(canonical.page_markers)
        fragments.extend(row_fragments)
        sections.extend(row_sections)
    summary = {
        "canonical_version": CANONICAL_VERSION,
        "manifest_path": manifest_path.as_posix(),
        "manifest_sha256": _sha256_file(manifest_path),
        "unit_count": len({row["ocr_text_id"] for row in fragments}),
        "fragment_count": len(fragments),
        "section_count": len(sections),
        "removed_page_marker_count": marker_count,
        "fragment_type_counts": dict(
            sorted(Counter(str(row["fragment_type"]) for row in fragments).items())
        ),
        "caption_status_counts": dict(
            sorted(
                Counter(
                    str(row["caption_status"])
                    for row in fragments
                    if row["fragment_type"] == "table"
                ).items()
            )
        ),
    }
    return sections, fragments, summary


def _atomic_write_csv(
    path: Path,
    rows: Iterable[dict[str, Any]],
    fieldnames: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _atomic_save_workbook(path: Path, workbook: Workbook) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".xlsx",
        dir=path.parent,
    )
    os.close(descriptor)
    try:
        workbook.save(temporary_name)
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def write_fragment_bundle_v1(
    *,
    sections: Sequence[dict[str, Any]],
    fragments: Sequence[dict[str, Any]],
    sections_path: Path,
    fragments_path: Path,
) -> None:
    """Write section and fragment CSVs atomically."""

    _atomic_write_csv(sections_path, sections, SECTION_FIELDNAMES)
    _atomic_write_csv(fragments_path, fragments, FRAGMENT_FIELDNAMES)


def validate_fragment_bundle_v1(
    *,
    manifest_path: Path,
    sections_path: Path,
    fragments_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Validate reconstruction, spans, hierarchy, captions, types, and IDs."""

    manifest_rows = {row["ocr_text_id"]: row for row in read_csv_rows(manifest_path)}
    section_rows = read_csv_rows(sections_path)
    fragment_rows = read_csv_rows(fragments_path)
    if len({row["fragment_id"] for row in fragment_rows}) != len(fragment_rows):
        raise ValueError("duplicate fragment_id in v1 bundle")
    if len({row["section_id"] for row in section_rows}) != len(section_rows):
        raise ValueError("duplicate section_id in v1 bundle")
    if {row["fragment_type"] for row in fragment_rows} - {"text", "table"}:
        raise ValueError("fragment_type must be text or table")

    by_unit: dict[str, list[dict[str, str]]] = {}
    for fragment in fragment_rows:
        by_unit.setdefault(fragment["ocr_text_id"], []).append(fragment)
    reconstructed_units = 0
    cross_page_fragments = 0
    missing_captions = 0
    exact_captions = 0
    adjacent_source_captions = 0
    for ocr_text_id, manifest_row in manifest_rows.items():
        unit_fragments = sorted(
            by_unit.get(ocr_text_id, []),
            key=lambda row: int(row["fragment_index"]),
        )
        if not unit_fragments:
            raise ValueError(f"missing fragments for {ocr_text_id}")
        source_path = _resolve_source_path(manifest_row, repo_root)
        canonical = canonicalize_markdown(source_path.read_text(encoding="utf-8", errors="strict"))
        metadata_parts, _, _ = _metadata_section_parts(manifest_row)
        expected_prefix = " > ".join(metadata_parts)
        cursor = 0
        pieces: list[str] = []
        for fragment in unit_fragments:
            start = int(fragment["char_start"])
            end = int(fragment["char_end"])
            if start != cursor or end <= start:
                raise ValueError(
                    f"gap, overlap, or empty fragment in {ocr_text_id}: {start}:{end}"
                )
            if canonical.text[start:end] != fragment["markdown_text"]:
                raise ValueError(f"fragment text/span mismatch: {fragment['fragment_id']}")
            if fragment["canonical_sha256"] != canonical.canonical_sha256:
                raise ValueError(f"canonical hash mismatch: {fragment['fragment_id']}")
            if expected_prefix:
                path = fragment["section_path"]
                if path != expected_prefix and not path.startswith(expected_prefix + " > "):
                    raise ValueError(f"non-canonical section prefix: {fragment['fragment_id']}")
            page_ids = json.loads(fragment["page_markers_json"] or "[]")
            if len(page_ids) > 1:
                cross_page_fragments += 1
            if fragment["fragment_type"] == "table":
                caption = fragment["table_caption"]
                if not caption:
                    raise ValueError(f"table caption locator is empty: {fragment['fragment_id']}")
                if fragment["caption_status"] in {"exact", "adjacent_source"}:
                    if fragment["section_path"].split(" > ")[-1] != caption:
                        raise ValueError(
                            "source table caption is not the final section component: "
                            f"{fragment['fragment_id']}"
                        )
                    if fragment["caption_status"] == "exact":
                        exact_captions += 1
                    else:
                        adjacent_source_captions += 1
                    caption_start = int(fragment["caption_char_start"])
                    caption_end = int(fragment["caption_char_end"])
                    if not start <= caption_start < caption_end <= end:
                        raise ValueError(
                            "caption span is outside table fragment: "
                            f"{fragment['fragment_id']}"
                        )
                elif fragment["caption_status"] == "missing":
                    missing_captions += 1
                    if not caption.startswith("Bảng chưa có caption nguồn [T"):
                        raise ValueError(
                            "invalid missing-caption locator: "
                            f"{fragment['fragment_id']}"
                        )
                    if fragment["section_path"].split(" > ")[-1] == caption:
                        raise ValueError(
                            "missing-caption locator must not become a section leaf: "
                            f"{fragment['fragment_id']}"
                        )
                else:
                    raise ValueError(f"invalid caption_status: {fragment['fragment_id']}")
            pieces.append(fragment["markdown_text"])
            cursor = end
        if cursor != len(canonical.text) or "".join(pieces) != canonical.text:
            raise ValueError(f"canonical reconstruction mismatch: {ocr_text_id}")
        reconstructed_units += 1

    section_ids = {row["section_id"] for row in section_rows}
    unknown_sections = sorted(
        {row["section_id"] for row in fragment_rows if row["section_id"] not in section_ids}
    )
    if unknown_sections:
        raise ValueError(f"unknown section IDs: {unknown_sections[:3]}")
    return {
        "canonical_version": CANONICAL_VERSION,
        "manifest_unit_count": len(manifest_rows),
        "reconstructed_unit_count": reconstructed_units,
        "fragment_count": len(fragment_rows),
        "section_count": len(section_rows),
        "cross_page_fragment_count": cross_page_fragments,
        "exact_table_caption_count": exact_captions,
        "adjacent_source_table_caption_count": adjacent_source_captions,
        "missing_table_caption_count": missing_captions,
        "fragment_types": sorted({row["fragment_type"] for row in fragment_rows}),
        "material_types": sorted({row["material_type"] for row in fragment_rows}),
        "lossless": reconstructed_units == len(manifest_rows),
    }


def build_validate_and_write_v1(
    *,
    manifest_path: Path,
    output_dir: Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Build the three Plan-01 staging artifacts and validate them."""

    sections_path = output_dir / "learning_sections_v1.csv"
    fragments_path = output_dir / "learning_resource_fragments_v1.csv"
    summary_path = output_dir / "fragment_validation_summary.json"
    sections, fragments, build_summary = build_fragment_bundle_v1(
        manifest_path,
        repo_root=repo_root,
    )
    write_fragment_bundle_v1(
        sections=sections,
        fragments=fragments,
        sections_path=sections_path,
        fragments_path=fragments_path,
    )
    validation = validate_fragment_bundle_v1(
        manifest_path=manifest_path,
        sections_path=sections_path,
        fragments_path=fragments_path,
        repo_root=repo_root,
    )
    summary = {
        **build_summary,
        **validation,
        "sections_path": sections_path.as_posix(),
        "sections_sha256": _sha256_file(sections_path),
        "fragments_path": fragments_path.as_posix(),
        "fragments_sha256": _sha256_file(fragments_path),
        "summary_path": summary_path.as_posix(),
    }
    _atomic_write_json(summary_path, summary)
    return summary


def effective_content(markdown_text: str) -> str:
    """Return content used only to measure whether a fragment is too short.

    The source Markdown is never rewritten. HTML comments, headings, image
    references, page numbers, table dividers, and Markdown formatting markers
    are ignored only in this derived measurement.
    """

    measured_lines: list[str] = []
    measurement_text = HTML_COMMENT_RE.sub(" ", markdown_text)
    for raw_line in measurement_text.splitlines():
        if HEADING_RE.match(raw_line) or STANDALONE_PAGE_NUMBER_RE.match(raw_line):
            continue
        if TABLE_DIVIDER_LINE_RE.match(raw_line):
            continue
        line = MARKDOWN_IMAGE_RE.sub(" ", raw_line)
        line = HTML_IMAGE_RE.sub(" ", line)
        line = MARKDOWN_LINK_RE.sub(r"\1", line)
        line = re.sub(r"[`*_~#>|]", " ", line)
        measured_lines.append(line)
    return re.sub(r"\s+", " ", "\n".join(measured_lines)).strip()


def effective_content_length(markdown_text: str) -> int:
    """Measure effective text/table content without mutating the fragment."""

    return len(effective_content(markdown_text))


def semantic_review_display_content(markdown_text: str) -> str:
    """Render source Markdown for a compact human-review workbook.

    This is only a display projection. The machine CSV continues to retain the
    exact ``markdown_text`` and lineage used by the semantic survey.
    """

    display_lines: list[str] = []
    display_text = HTML_COMMENT_RE.sub("", markdown_text)
    for raw_line in display_text.splitlines():
        if STANDALONE_PAGE_NUMBER_RE.match(raw_line):
            continue
        if TABLE_DIVIDER_LINE_RE.match(raw_line):
            continue
        line = MARKDOWN_IMAGE_RE.sub("[Hình ảnh]", raw_line)
        line = HTML_IMAGE_RE.sub("[Hình ảnh]", line)
        heading = HEADING_RE.match(line)
        if heading:
            line = heading.group("title")
        line = MARKDOWN_LINK_RE.sub(r"\1", line)
        line = re.sub(r"[`*_~]", "", line).strip()
        if not line:
            if display_lines and display_lines[-1] != "":
                display_lines.append("")
            continue
        display_lines.append(line)
    return "\n".join(display_lines).strip()


def _write_excel_value(cell: Any, value: Any) -> None:
    """Write text as text so review content cannot become an Excel formula."""

    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"


def _semantic_review_side_label(row: Mapping[str, Any]) -> str:
    labels = {
        "at_or_below": "Ở hoặc dưới ngưỡng",
        "above": "Trên ngưỡng",
        "merged_at_or_below": "Đoạn sau ghép",
        "source_above": "Đoạn nguồn dài hơn ngưỡng",
    }
    label = labels.get(str(row.get("boundary_side", "")), "Không xác định")
    if str(row.get("in_primary_window", "")).lower() != "true":
        label += " — mẫu dự phòng ngoài cửa sổ"
    return label


def _semantic_review_lesson_label(row: Mapping[str, Any]) -> str:
    return str(row.get("lesson_title") or row.get("lesson_key") or "")


def _style_semantic_review_sheet(
    worksheet: Any,
    *,
    row_count: int,
    editable_columns: Sequence[int],
    validation_columns: Sequence[int],
    fallback_rows: set[int],
    table_name: str,
) -> None:
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    editable_fill = PatternFill("solid", fgColor="FFF2CC")
    fallback_fill = PatternFill("solid", fgColor="FCE4D6")
    thin_gray = Side(style="thin", color="D9E2F3")
    border = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    worksheet.row_dimensions[1].height = 42

    for row_number in range(2, row_count + 2):
        for column_number in range(1, worksheet.max_column + 1):
            cell = worksheet.cell(row=row_number, column=column_number)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = border
            if row_number in fallback_rows:
                cell.fill = fallback_fill
        for column_number in editable_columns:
            worksheet.cell(row=row_number, column=column_number).fill = editable_fill
        worksheet.row_dimensions[row_number].height = 90

    for column_number in validation_columns:
        validation = DataValidation(
            type="list",
            formula1='"Có,Không,Chưa chắc"',
            allow_blank=True,
        )
        validation.error = "Chỉ chọn Có, Không hoặc Chưa chắc."
        validation.errorTitle = "Giá trị không hợp lệ"
        validation.prompt = "Chọn một trong ba giá trị có sẵn."
        validation.promptTitle = "Nhãn rà soát"
        validation.showErrorMessage = True
        validation.showInputMessage = True
        worksheet.add_data_validation(validation)
        validation.add(
            f"{get_column_letter(column_number)}2:"
            f"{get_column_letter(column_number)}{row_count + 1}"
        )

    widths = {
        1: 28,
        2: 16,
        3: 34,
        4: 9,
        5: 13,
        6: 34,
        7: 58,
        8: 18,
        9: 90,
    }
    for column_number in range(1, worksheet.max_column + 1):
        worksheet.column_dimensions[get_column_letter(column_number)].width = widths.get(
            column_number, 24
        )

    worksheet.freeze_panes = "D2"
    worksheet.sheet_view.showGridLines = False
    worksheet.auto_filter.ref = f"A1:{get_column_letter(worksheet.max_column)}{row_count + 1}"
    table = Table(
        displayName=table_name,
        ref=f"A1:{get_column_letter(worksheet.max_column)}{row_count + 1}",
    )
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    worksheet.add_table(table)


def _build_semantic_review_instruction_sheet(
    worksheet: Any,
    *,
    lower_count: int,
    upper_count: int,
    source_machine_path: Path | None,
    source_machine_sha256: str | None,
) -> None:
    worksheet.sheet_view.showGridLines = False
    worksheet.merge_cells("A1:D1")
    worksheet["A1"] = "PHIẾU RÀ SOÁT NGỮ NGHĨA ĐOẠN HỌC LIỆU"
    worksheet["A1"].font = Font(size=16, bold=True, color="FFFFFF")
    worksheet["A1"].fill = PatternFill("solid", fgColor="1F4E78")
    worksheet["A1"].alignment = Alignment(horizontal="center", vertical="center")
    worksheet.row_dimensions[1].height = 30

    instructions = [
        (
            "Mục đích",
            "Đánh giá xem ngưỡng độ dài nào tạo ra đoạn học liệu đủ ngữ cảnh, "
            "có trọng tâm và phù hợp để agent dùng làm bằng chứng.",
        ),
        (
            "Cách làm",
            "Chỉ điền các ô màu vàng. Không sửa cột Mã mẫu hoặc nội dung nguồn.",
        ),
        (
            "Sheet Cận dưới",
            f"Rà soát {lower_count} mẫu. Chọn Có khi đoạn học liệu tự chứa đủ "
            "ngữ cảnh để dùng làm bằng chứng; chọn Không khi nội dung quá ngắn "
            "hoặc phụ thuộc phần bị thiếu.",
        ),
        (
            "Sheet Cận trên",
            f"Rà soát {upper_count} mẫu. Trả lời riêng hai câu hỏi về trọng tâm "
            "và độ dài; một đoạn có thể rõ trọng tâm nhưng vẫn quá dài.",
        ),
        (
            "Nhãn Có",
            "Khẳng định câu hỏi ở tiêu đề cột là đúng với mẫu đang xem.",
        ),
        (
            "Nhãn Không",
            "Khẳng định câu hỏi ở tiêu đề cột là không đúng với mẫu đang xem.",
        ),
        (
            "Nhãn Chưa chắc",
            "Chưa thể quyết định từ nội dung hiển thị; ghi rõ điểm còn thiếu trong cột Lý do.",
        ),
        (
            "Màu cam",
            "Mẫu dự phòng nằm ngoài cửa sổ gần ngưỡng vì không đủ mẫu phù hợp hơn; "
            "vẫn rà soát bình thường.",
        ),
        (
            "Sau khi hoàn tất",
            "Lưu lại chính workbook này và gửi cho người phụ trách dự án. Không cần "
            "mở hay chỉnh sửa CSV nguồn.",
        ),
    ]
    for row_number, (label, explanation) in enumerate(instructions, start=3):
        worksheet.cell(row=row_number, column=1, value=label).font = Font(bold=True)
        worksheet.merge_cells(
            start_row=row_number,
            start_column=2,
            end_row=row_number,
            end_column=4,
        )
        worksheet.cell(row=row_number, column=2, value=explanation)
        worksheet.cell(row=row_number, column=1).alignment = Alignment(vertical="top")
        worksheet.cell(row=row_number, column=2).alignment = Alignment(
            vertical="top", wrap_text=True
        )
        worksheet.row_dimensions[row_number].height = 42

    provenance_row = len(instructions) + 5
    worksheet.cell(row=provenance_row, column=1, value="Thông tin truy vết")
    worksheet.cell(row=provenance_row, column=1).font = Font(bold=True, color="666666")
    worksheet.merge_cells(
        start_row=provenance_row,
        start_column=2,
        end_row=provenance_row,
        end_column=4,
    )
    provenance = "CSV máy: " + (
        source_machine_path.as_posix() if source_machine_path is not None else "không ghi"
    )
    if source_machine_sha256:
        provenance += f" | SHA-256: {source_machine_sha256}"
    worksheet.cell(row=provenance_row, column=2, value=provenance)
    worksheet.cell(row=provenance_row, column=2).font = Font(size=9, color="777777")
    worksheet.cell(row=provenance_row, column=2).alignment = Alignment(wrap_text=True)

    worksheet.column_dimensions["A"].width = 24
    worksheet.column_dimensions["B"].width = 42
    worksheet.column_dimensions["C"].width = 28
    worksheet.column_dimensions["D"].width = 28
    worksheet.freeze_panes = "A3"


def write_semantic_boundary_review_workbook(
    review_rows: Sequence[Mapping[str, Any]],
    output_path: Path,
    *,
    source_machine_path: Path | None = None,
    source_machine_sha256: str | None = None,
) -> dict[str, Any]:
    """Write and reopen-validate the compact Excel human-review surface."""

    review_ids = [str(row.get("review_id", "")) for row in review_rows]
    if not review_ids or any(not review_id for review_id in review_ids):
        raise ValueError("semantic review workbook requires non-empty review IDs")
    if len(set(review_ids)) != len(review_ids):
        raise ValueError("semantic review workbook contains duplicate review IDs")

    lower_rows = [
        row for row in review_rows if row.get("boundary_kind") == "lower_minimum"
    ]
    upper_rows = [
        row for row in review_rows if row.get("boundary_kind") == "upper_maximum"
    ]
    if len(lower_rows) + len(upper_rows) != len(review_rows):
        raise ValueError("semantic review workbook received an unknown boundary kind")

    workbook = Workbook()
    instruction_sheet = workbook.active
    instruction_sheet.title = SEMANTIC_REVIEW_WORKBOOK_SHEETS[0]
    lower_sheet = workbook.create_sheet(SEMANTIC_REVIEW_WORKBOOK_SHEETS[1])
    upper_sheet = workbook.create_sheet(SEMANTIC_REVIEW_WORKBOOK_SHEETS[2])
    _build_semantic_review_instruction_sheet(
        instruction_sheet,
        lower_count=len(lower_rows),
        upper_count=len(upper_rows),
        source_machine_path=source_machine_path,
        source_machine_sha256=source_machine_sha256,
    )

    lower_sheet.append(LOWER_REVIEW_HEADERS)
    lower_fallback_rows: set[int] = set()
    for excel_row_number, row in enumerate(lower_rows, start=2):
        values = [
            row["review_id"],
            int(row["threshold_effective_chars"]),
            _semantic_review_side_label(row),
            row.get("grade", ""),
            row.get("material_type", ""),
            _semantic_review_lesson_label(row),
            row.get("section_path", ""),
            int(row["effective_content_length"]),
            semantic_review_display_content(str(row.get("markdown_text", ""))),
            "",
            "",
            "",
        ]
        for column_number, value in enumerate(values, start=1):
            _write_excel_value(lower_sheet.cell(excel_row_number, column_number), value)
        if str(row.get("in_primary_window", "")).lower() != "true":
            lower_fallback_rows.add(excel_row_number)

    upper_sheet.append(UPPER_REVIEW_HEADERS)
    upper_fallback_rows: set[int] = set()
    for excel_row_number, row in enumerate(upper_rows, start=2):
        values = [
            row["review_id"],
            int(row["threshold_effective_chars"]),
            _semantic_review_side_label(row),
            row.get("grade", ""),
            row.get("material_type", ""),
            _semantic_review_lesson_label(row),
            row.get("section_path", ""),
            int(row["effective_content_length"]),
            semantic_review_display_content(str(row.get("markdown_text", ""))),
            "",
            "",
            "",
            "",
        ]
        for column_number, value in enumerate(values, start=1):
            _write_excel_value(upper_sheet.cell(excel_row_number, column_number), value)
        if str(row.get("in_primary_window", "")).lower() != "true":
            upper_fallback_rows.add(excel_row_number)

    _style_semantic_review_sheet(
        lower_sheet,
        row_count=len(lower_rows),
        editable_columns=(10, 11, 12),
        validation_columns=(10,),
        fallback_rows=lower_fallback_rows,
        table_name="LowerBoundaryReview",
    )
    _style_semantic_review_sheet(
        upper_sheet,
        row_count=len(upper_rows),
        editable_columns=(10, 11, 12, 13),
        validation_columns=(10, 11),
        fallback_rows=upper_fallback_rows,
        table_name="UpperBoundaryReview",
    )

    workbook.properties.title = "Phiếu rà soát ngữ nghĩa fragment v1.1"
    workbook.properties.subject = SEMANTIC_REVIEW_WORKBOOK_VERSION
    workbook.properties.creator = "edu-benchmark"
    _atomic_save_workbook(output_path, workbook)

    reopened = load_workbook(output_path, read_only=False, data_only=False)
    try:
        if tuple(reopened.sheetnames) != SEMANTIC_REVIEW_WORKBOOK_SHEETS:
            raise ValueError("semantic review workbook sheet contract is invalid")
        expected = {
            "Cận dưới": (
                len(lower_rows),
                len(LOWER_REVIEW_HEADERS),
                {str(row["review_id"]) for row in lower_rows},
            ),
            "Cận trên": (
                len(upper_rows),
                len(UPPER_REVIEW_HEADERS),
                {str(row["review_id"]) for row in upper_rows},
            ),
        }
        for sheet_name, (row_count, column_count, expected_ids) in expected.items():
            worksheet = reopened[sheet_name]
            actual_ids = {
                str(worksheet.cell(row=row_number, column=1).value or "")
                for row_number in range(2, worksheet.max_row + 1)
            }
            if worksheet.max_row != row_count + 1:
                raise ValueError(f"{sheet_name} review row count is invalid")
            if worksheet.max_column != column_count:
                raise ValueError(f"{sheet_name} exposes an invalid column count")
            if actual_ids != expected_ids:
                raise ValueError(f"{sheet_name} review IDs differ from machine source")
            if not worksheet.data_validations.dataValidation:
                raise ValueError(f"{sheet_name} is missing review dropdowns")
            if worksheet.sheet_state != "visible":
                raise ValueError(f"{sheet_name} must remain visible")
    finally:
        reopened.close()

    return {
        "contract_version": SEMANTIC_REVIEW_WORKBOOK_VERSION,
        "workbook_path": output_path.as_posix(),
        "workbook_sha256": _sha256_file(output_path),
        "row_count": len(review_rows),
        "lower_row_count": len(lower_rows),
        "upper_row_count": len(upper_rows),
        "sheet_names": list(SEMANTIC_REVIEW_WORKBOOK_SHEETS),
        "maximum_review_columns": max(
            len(LOWER_REVIEW_HEADERS), len(UPPER_REVIEW_HEADERS)
        ),
        "allowed_review_labels": list(HUMAN_REVIEW_LABELS),
    }


def build_semantic_boundary_review_workbook_from_csv(
    source_csv_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Project an existing machine review CSV into the human Excel surface."""

    with source_csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES:
            raise ValueError("semantic review CSV schema differs from the expected contract")
        review_rows = list(reader)
    source_sha256 = _sha256_file(source_csv_path)
    summary = write_semantic_boundary_review_workbook(
        review_rows,
        output_path,
        source_machine_path=source_csv_path,
        source_machine_sha256=source_sha256,
    )
    summary.update(
        {
            "source_machine_path": source_csv_path.as_posix(),
            "source_machine_sha256": source_sha256,
        }
    )
    return summary


def _read_fragment_snapshot(
    path: Path,
    *,
    required_fields: Sequence[str],
) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = [field for field in required_fields if field not in fields]
        if missing:
            raise ValueError(
                f"fragment snapshot is missing required fields: {', '.join(missing)}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError("fragment snapshot is empty")
    return rows


def _verify_v1_validation_snapshot(
    *,
    fragments_path: Path,
    validation_summary_path: Path,
) -> dict[str, Any]:
    if not validation_summary_path.is_file():
        raise FileNotFoundError(validation_summary_path)
    summary = json.loads(validation_summary_path.read_text(encoding="utf-8"))
    if summary.get("lossless") is not True:
        raise ValueError("v1 validation summary is not lossless")
    actual_hash = _sha256_file(fragments_path)
    if summary.get("fragments_sha256") != actual_hash:
        raise ValueError("v1 fragment snapshot hash differs from validation summary")
    return summary


def _group_fragments_by_unit(
    rows: Sequence[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    by_unit: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_unit.setdefault(row["ocr_text_id"], []).append(row)
    for unit_rows in by_unit.values():
        unit_rows.sort(key=lambda row: int(row["fragment_index"]))
    return by_unit


def _canonical_merge_section_path(row: Mapping[str, str]) -> str:
    """Return the exact section scope used by the v1.1 merge policy.

    Early v1 snapshots gave a synthetic leaf to a table whose source had no
    caption. That leaf is not a real section. Strip only that exact synthetic
    suffix for merge-scope comparison; the immutable v1 row is not rewritten.
    """

    section_path = str(row.get("section_path", "")).strip()
    if row.get("fragment_type") != "table" or row.get("caption_status") != "missing":
        return section_path
    synthetic_caption = str(row.get("table_caption", "")).strip()
    suffix = f" > {synthetic_caption}"
    if synthetic_caption and section_path.endswith(suffix):
        return section_path[: -len(suffix)]
    return section_path


def _same_merge_scope(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return (
        left.get("ocr_text_id") == right.get("ocr_text_id")
        and left.get("canonical_section_path")
        == right.get("canonical_section_path")
    )


def _distribution(values: Sequence[int]) -> dict[str, int | None]:
    if not values:
        return {
            "min": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p95": None,
            "max": None,
        }
    ordered = sorted(values)

    def percentile(numerator: int, denominator: int) -> int:
        index = round((len(ordered) - 1) * numerator / denominator)
        return ordered[index]

    return {
        "min": ordered[0],
        "p25": percentile(1, 4),
        "median": percentile(1, 2),
        "p75": percentile(3, 4),
        "p95": percentile(19, 20),
        "max": ordered[-1],
    }


def _merge_contract(
    *,
    text_min_effective_chars: int,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    neighbor_policy: str,
) -> dict[str, Any]:
    contract = {
        "merge_policy_version": V1_1_MERGE_POLICY_VERSION,
        "measurement_unit": "unicode_code_points",
        "text_min_effective_chars": text_min_effective_chars,
        "text_max_effective_chars": text_max_effective_chars,
        "table_absorption_max_effective_chars": (
            table_absorption_max_effective_chars
        ),
        "neighbor_policy": neighbor_policy,
        "table_table_merge_enabled": False,
        "scope": "contiguous+exact_ocr_text_id+exact_canonical_section_path",
        "structural_zero_initiates_merge": False,
        "explicit_table_context_merge_enabled": True,
        "explicit_table_context_obeys_text_max": True,
        "explicit_table_context_direction": "preceding_text_only",
        "explicit_structural_zero_requires_heading": True,
        "short_table_fallback_requires_positive_text": True,
    }
    serialized = json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return {**contract, "merge_contract_sha256": _sha256_text(serialized)}


def _validate_v1_1_parameters(
    *,
    text_min_effective_chars: int,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    neighbor_policy: str,
) -> None:
    if text_min_effective_chars <= 0:
        raise ValueError("text_min_effective_chars must be positive")
    if text_max_effective_chars < text_min_effective_chars:
        raise ValueError(
            "text_max_effective_chars must be greater than or equal to the minimum"
        )
    if table_absorption_max_effective_chars < 0:
        raise ValueError("table_absorption_max_effective_chars must be non-negative")
    if neighbor_policy not in V1_1_NEIGHBOR_POLICIES:
        raise ValueError(
            "neighbor_policy must be one of "
            + ", ".join(sorted(V1_1_NEIGHBOR_POLICIES))
        )


def _source_fragment_types(group: Mapping[str, Any]) -> list[str]:
    return [str(row["fragment_type"]) for row in group["source_rows"]]


def _new_merge_group(row: dict[str, str]) -> dict[str, Any]:
    markdown_text = row["markdown_text"]
    return {
        "ocr_text_id": row["ocr_text_id"],
        "canonical_section_path": _canonical_merge_section_path(row),
        "source_rows": [row],
        "markdown_text": markdown_text,
        "effective_content_length": effective_content_length(markdown_text),
        "merge_reasons": [],
    }


def _group_output_type(group: Mapping[str, Any]) -> str:
    return "text" if "text" in _source_fragment_types(group) else "table"


def _is_explicit_table_context(group: Mapping[str, Any]) -> bool:
    """Recognize source-local text that structurally introduces one table."""

    rows = list(group["source_rows"])
    if len(rows) != 1 or rows[0]["fragment_type"] != "text":
        return False
    row = rows[0]
    markdown_text = str(row["markdown_text"])
    if effective_content_length(markdown_text) == 0:
        # A heading can introduce the table that immediately follows it. Other
        # zero-content rows (blank text, page numbers, comments, or images) are
        # provenance, not evidence of a semantic table relationship.
        return any(
            HEADING_RE.match(line.rstrip("\r\n"))
            for line in markdown_text.splitlines()
        )
    if (
        str(row.get("material_type", "")).strip().upper() == "SBT"
        and _sbt_exercise_label(markdown_text)
    ):
        return True
    source_text = _plain_inline_text(markdown_text)
    effective_text = effective_content(markdown_text)
    return (
        len(effective_text) <= 200
        and (
            effective_text.endswith(":")
            or source_text.casefold().startswith("bảng ")
        )
    )


def _groups_can_merge_explicit_table_context(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    text_max_effective_chars: int,
) -> bool:
    if not _same_merge_scope(left, right):
        return False
    types = _source_fragment_types(left) + _source_fragment_types(right)
    if types.count("table") != 1 or "text" not in types:
        return False
    table_group = left if _group_output_type(left) == "table" else right
    text_group = right if table_group is left else left
    table_rows = [
        row for row in table_group["source_rows"] if row["fragment_type"] == "table"
    ]
    if len(table_rows) != 1 or table_rows[0].get("caption_status") != "missing":
        return False
    if not _is_explicit_table_context(text_group):
        return False
    combined_text = str(left["markdown_text"]) + str(right["markdown_text"])
    return effective_content_length(combined_text) <= text_max_effective_chars


def _eligible_short_table(
    group: Mapping[str, Any],
    *,
    table_absorption_max_effective_chars: int,
) -> bool:
    rows = group["source_rows"]
    return (
        len(rows) == 1
        and rows[0]["fragment_type"] == "table"
        and rows[0].get("caption_status") == "missing"
        and 0 < int(group["effective_content_length"])
        < table_absorption_max_effective_chars
    )


def _group_initiates_merge(
    group: Mapping[str, Any],
    *,
    text_min_effective_chars: int,
    table_absorption_max_effective_chars: int,
) -> bool:
    length = int(group["effective_content_length"])
    if length <= 0:
        return False
    if _group_output_type(group) == "text":
        return length < text_min_effective_chars
    return _eligible_short_table(
        group,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
    )


def _groups_type_compatible(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    table_absorption_max_effective_chars: int,
) -> bool:
    types = _source_fragment_types(left) + _source_fragment_types(right)
    table_count = types.count("table")
    if table_count == 0:
        return True
    if table_count > 1 or "text" not in types:
        return False
    table_rows = [
        row
        for group in (left, right)
        for row in group["source_rows"]
        if row["fragment_type"] == "table"
    ]
    table_row = table_rows[0]
    table_is_in_left = any(
        row["fragment_type"] == "table" for row in left["source_rows"]
    )
    text_group = right if table_is_in_left else left
    return (
        table_row.get("caption_status") == "missing"
        and 0 < effective_content_length(table_row["markdown_text"])
        < table_absorption_max_effective_chars
        and int(text_group["effective_content_length"]) > 0
    )


def _groups_can_merge(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    enforce_cap: bool,
) -> bool:
    if not _same_merge_scope(left, right):
        return False
    if not _groups_type_compatible(
        left,
        right,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
    ):
        return False
    if not enforce_cap:
        return True
    combined_text = str(left["markdown_text"]) + str(right["markdown_text"])
    return effective_content_length(combined_text) <= text_max_effective_chars


def _candidate_neighbor_indices(
    groups: Sequence[Mapping[str, Any]],
    *,
    index: int,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    enforce_cap: bool,
) -> list[int]:
    candidates: list[int] = []
    for candidate_index in (index - 1, index + 1):
        if not 0 <= candidate_index < len(groups):
            continue
        left_index, right_index = sorted((index, candidate_index))
        if _groups_can_merge(
            groups[left_index],
            groups[right_index],
            text_max_effective_chars=text_max_effective_chars,
            table_absorption_max_effective_chars=(
                table_absorption_max_effective_chars
            ),
            enforce_cap=enforce_cap,
        ):
            candidates.append(candidate_index)
    return candidates


def _select_neighbor_index(
    groups: Sequence[Mapping[str, Any]],
    *,
    index: int,
    candidates: Sequence[int],
    text_min_effective_chars: int,
    neighbor_policy: str,
) -> int:
    if len(candidates) == 1:
        return candidates[0]
    if neighbor_policy == "prefer_previous":
        return min(candidates)
    if neighbor_policy == "prefer_next":
        return max(candidates)

    def combined_length(candidate_index: int) -> int:
        left_index, right_index = sorted((index, candidate_index))
        return effective_content_length(
            str(groups[left_index]["markdown_text"])
            + str(groups[right_index]["markdown_text"])
        )

    if neighbor_policy == "prefer_short_group":
        return min(
            candidates,
            key=lambda candidate_index: (
                not (
                    0
                    < int(groups[candidate_index]["effective_content_length"])
                    < text_min_effective_chars
                ),
                0 if candidate_index < index else 1,
            ),
        )
    if neighbor_policy == "prefer_closest_to_min":
        return min(
            candidates,
            key=lambda candidate_index: (
                abs(combined_length(candidate_index) - text_min_effective_chars),
                0 if candidate_index < index else 1,
            ),
        )
    raise ValueError(f"unsupported neighbor_policy: {neighbor_policy}")


def _combine_groups(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    reason: str | None = None,
) -> dict[str, Any]:
    source_rows = [*left["source_rows"], *right["source_rows"]]
    markdown_text = str(left["markdown_text"]) + str(right["markdown_text"])
    types = [str(row["fragment_type"]) for row in source_rows]
    merge_reason = reason or (
        "short_table_absorption" if "table" in types else "text_iterative"
    )
    return {
        "ocr_text_id": left["ocr_text_id"],
        "canonical_section_path": left["canonical_section_path"],
        "source_rows": source_rows,
        "markdown_text": markdown_text,
        "effective_content_length": effective_content_length(markdown_text),
        "merge_reasons": [
            *left["merge_reasons"],
            *right["merge_reasons"],
            merge_reason,
        ],
    }


def _merge_explicit_table_contexts(
    groups: list[dict[str, Any]],
    *,
    text_max_effective_chars: int,
) -> int:
    """Merge one clearly related adjacent text group with each table group."""

    merged_count = 0
    index = 0
    while index < len(groups):
        if _group_output_type(groups[index]) != "table":
            index += 1
            continue
        # Source-local prompts/headings introduce the following table. Text
        # after a table may instead introduce the next table and must not be
        # pulled backward into the previous one.
        candidate_index = index - 1
        if candidate_index < 0 or not _groups_can_merge_explicit_table_context(
            groups[candidate_index],
            groups[index],
            text_max_effective_chars=text_max_effective_chars,
        ):
            index += 1
            continue
        groups[candidate_index : index + 1] = [
            _combine_groups(
                groups[candidate_index],
                groups[index],
                reason="explicit_table_context",
            )
        ]
        merged_count += 1
        index = candidate_index + 1
    return merged_count


def _run_fragment_v1_1_survey(
    rows: Sequence[dict[str, str]],
    *,
    text_min_thresholds: Sequence[int],
    text_max_thresholds: Sequence[int],
    table_absorption_thresholds: Sequence[int],
    neighbor_policies: Sequence[str],
    table_table_merge_enabled: bool = False,
    collect_upper_boundary_candidates: bool = False,
) -> tuple[dict[str, Any], dict[int, list[dict[str, Any]]]]:
    """Run the quantitative grid and optionally retain merged cap candidates."""

    if table_table_merge_enabled:
        raise ValueError("v1.1 does not permit table-table merging")
    minimums = sorted({int(value) for value in text_min_thresholds})
    maximums = sorted({int(value) for value in text_max_thresholds})
    table_limits = sorted({int(value) for value in table_absorption_thresholds})
    policies = list(dict.fromkeys(str(value) for value in neighbor_policies))
    if not minimums or not maximums or not table_limits or not policies:
        raise ValueError("all survey policy axes must be provided explicitly")
    if minimums[0] <= 0 or table_limits[0] < 0:
        raise ValueError("survey thresholds are outside their valid ranges")
    unsupported = set(policies) - V1_1_NEIGHBOR_POLICIES
    if unsupported:
        raise ValueError(f"unsupported neighbor policies: {sorted(unsupported)}")
    by_unit = _group_fragments_by_unit(rows)
    measurements = {
        row["fragment_id"]: effective_content_length(row["markdown_text"])
        for row in rows
    }
    simulations: list[dict[str, Any]] = []
    upper_candidate_maps: dict[int, dict[tuple[str, ...], dict[str, Any]]] = {
        maximum: {} for maximum in maximums
    }
    for minimum in minimums:
        for maximum in maximums:
            if maximum < minimum:
                continue
            for table_limit in table_limits:
                for policy in policies:
                    merged_rows, summary = merge_short_fragments_v1_1(
                        rows,
                        text_min_effective_chars=minimum,
                        text_max_effective_chars=maximum,
                        table_absorption_max_effective_chars=table_limit,
                        neighbor_policy=policy,
                    )
                    simulations.append(summary)
                    if not collect_upper_boundary_candidates:
                        continue
                    representative_key = (minimum, table_limit, policy)
                    for merged_row in merged_rows:
                        if (
                            merged_row["fragment_type"] != "text"
                            or int(merged_row["merged_from_fragment_count"]) <= 1
                        ):
                            continue
                        lineage = tuple(
                            str(value)
                            for value in json.loads(
                                str(merged_row["merged_from_fragment_ids_json"])
                            )
                        )
                        candidate = {
                            **merged_row,
                            "candidate_origin": "simulated_v1_1_merge",
                            "candidate_identity": "merged:" + "|".join(lineage),
                            "text_min_effective_chars": minimum,
                            "text_max_effective_chars": maximum,
                            "table_absorption_max_effective_chars": table_limit,
                            "neighbor_policy": policy,
                            "representative_key": representative_key,
                        }
                        existing = upper_candidate_maps[maximum].get(lineage)
                        if existing is None or representative_key < tuple(
                            existing["representative_key"]
                        ):
                            upper_candidate_maps[maximum][lineage] = candidate
    if not simulations:
        raise ValueError("survey grid contains no valid minimum/maximum combination")
    survey = {
        "fragment_release": FRAGMENT_RELEASE_V1_1,
        "source_fragment_count": len(rows),
        "unit_count": len(by_unit),
        "text_min_thresholds": minimums,
        "text_max_thresholds": maximums,
        "table_absorption_thresholds": table_limits,
        "neighbor_policies": policies,
        "table_table_merge_enabled": False,
        "effective_content_length_distribution": {
            fragment_type: _distribution(
                [
                    measurements[row["fragment_id"]]
                    for row in rows
                    if row["fragment_type"] == fragment_type
                ]
            )
            for fragment_type in ("text", "table")
        },
        "structural_zero_count": sum(value == 0 for value in measurements.values()),
        "simulation_results": simulations,
        "measurement_only": True,
        "source_markdown_mutated": False,
        "merge_scope": (
            "contiguous+exact_ocr_text_id+exact_canonical_section_path"
        ),
    }
    upper_candidates = {
        maximum: sorted(
            candidate_map.values(),
            key=lambda row: (
                tuple(row["representative_key"]),
                str(row["candidate_identity"]),
            ),
        )
        for maximum, candidate_map in upper_candidate_maps.items()
    }
    return survey, upper_candidates


def survey_fragment_v1_1_candidates(
    rows: Sequence[dict[str, str]],
    *,
    text_min_thresholds: Sequence[int],
    text_max_thresholds: Sequence[int],
    table_absorption_thresholds: Sequence[int],
    neighbor_policies: Sequence[str],
    table_table_merge_enabled: bool = False,
) -> dict[str, Any]:
    """Survey explicit v1.1 policy combinations without publishing a bundle."""

    survey, _ = _run_fragment_v1_1_survey(
        rows,
        text_min_thresholds=text_min_thresholds,
        text_max_thresholds=text_max_thresholds,
        table_absorption_thresholds=table_absorption_thresholds,
        neighbor_policies=neighbor_policies,
        table_table_merge_enabled=table_table_merge_enabled,
        collect_upper_boundary_candidates=False,
    )
    return survey


def _source_semantic_candidates(
    rows: Sequence[dict[str, str]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if row["fragment_type"] != "text":
            continue
        measured = effective_content_length(row["markdown_text"])
        if measured <= 0:
            continue
        candidates.append(
            {
                **row,
                "candidate_origin": "source_v1",
                "candidate_identity": f"source:{row['fragment_id']}",
                "effective_content_length": measured,
                "source_fragment_ids_json": json.dumps(
                    [row["fragment_id"]], ensure_ascii=False
                ),
                "source_fragment_count": 1,
                "source_fragment_types_json": json.dumps(
                    [row["fragment_type"]], ensure_ascii=False
                ),
                "merge_policy_version": "",
                "text_min_effective_chars": "",
                "text_max_effective_chars": "",
                "table_absorption_max_effective_chars": "",
                "neighbor_policy": "",
            }
        )
    return sorted(
        candidates,
        key=lambda row: (
            str(row["grade"]),
            str(row["material_type"]),
            str(row["ocr_text_id"]),
            int(row["fragment_index"]),
            str(row["fragment_id"]),
        ),
    )


def _semantic_stratum(candidate: Mapping[str, Any]) -> tuple[str, str]:
    return str(candidate.get("grade", "")), str(candidate.get("material_type", ""))


def _select_semantic_boundary_candidates(
    candidates: Sequence[dict[str, Any]],
    *,
    count: int,
    threshold: int,
    primary_window_min: int,
    primary_window_max: int,
    selected_identities: set[str],
    stratum_counts: Counter[tuple[str, str]],
) -> list[dict[str, Any]]:
    available = [
        candidate
        for candidate in candidates
        if str(candidate["candidate_identity"]) not in selected_identities
    ]
    if len(available) < count:
        raise ValueError(
            "semantic boundary review has only "
            f"{len(available)} unused candidates for a required sample of {count} "
            f"at threshold {threshold}"
        )
    selected: list[dict[str, Any]] = []
    for _ in range(count):
        candidate = min(
            available,
            key=lambda row: (
                not (
                    primary_window_min
                    <= int(row["effective_content_length"])
                    <= primary_window_max
                ),
                stratum_counts[_semantic_stratum(row)],
                abs(int(row["effective_content_length"]) - threshold),
                str(row.get("grade", "")),
                str(row.get("material_type", "")),
                str(row.get("learning_material_id", "")),
                str(row.get("ocr_text_id", "")),
                int(row.get("fragment_index", 0)),
                str(row["candidate_identity"]),
            ),
        )
        available.remove(candidate)
        selected.append(candidate)
        identity = str(candidate["candidate_identity"])
        selected_identities.add(identity)
        stratum_counts[_semantic_stratum(candidate)] += 1
    return selected


def _semantic_review_id(
    *,
    boundary_kind: str,
    threshold: int,
    boundary_side: str,
    candidate: Mapping[str, Any],
) -> str:
    payload = {
        "review_contract_version": SEMANTIC_BOUNDARY_REVIEW_VERSION,
        "boundary_kind": boundary_kind,
        "threshold": threshold,
        "boundary_side": boundary_side,
        "candidate_origin": candidate["candidate_origin"],
        "candidate_identity": candidate["candidate_identity"],
        "text_min_effective_chars": candidate.get(
            "text_min_effective_chars", ""
        ),
        "text_max_effective_chars": candidate.get(
            "text_max_effective_chars", ""
        ),
        "table_absorption_max_effective_chars": candidate.get(
            "table_absorption_max_effective_chars", ""
        ),
        "neighbor_policy": candidate.get("neighbor_policy", ""),
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    prefix = "LOWER" if boundary_kind == "lower_minimum" else "UPPER"
    return f"SBR-{prefix}-{threshold:04d}-{_sha256_text(serialized)[:12]}"


def _semantic_review_row(
    candidate: Mapping[str, Any],
    *,
    boundary_kind: str,
    threshold: int,
    boundary_side: str,
    selection_rank: int,
    primary_window_min: int,
    primary_window_max: int,
) -> dict[str, Any]:
    measured = int(candidate["effective_content_length"])
    lower = boundary_kind == "lower_minimum"
    return {
        "review_id": _semantic_review_id(
            boundary_kind=boundary_kind,
            threshold=threshold,
            boundary_side=boundary_side,
            candidate=candidate,
        ),
        "review_contract_version": SEMANTIC_BOUNDARY_REVIEW_VERSION,
        "boundary_kind": boundary_kind,
        "threshold_effective_chars": threshold,
        "boundary_side": boundary_side,
        "selection_rank": selection_rank,
        "primary_window_min": primary_window_min,
        "primary_window_max": primary_window_max,
        "in_primary_window": str(
            primary_window_min <= measured <= primary_window_max
        ).lower(),
        "distance_to_threshold": abs(measured - threshold),
        "candidate_origin": candidate["candidate_origin"],
        "fragment_id": candidate["fragment_id"],
        "source_fragment_ids_json": candidate.get(
            "source_fragment_ids_json",
            candidate.get("merged_from_fragment_ids_json", "[]"),
        ),
        "source_fragment_count": candidate.get(
            "source_fragment_count",
            candidate.get("merged_from_fragment_count", ""),
        ),
        "source_fragment_types_json": candidate.get(
            "source_fragment_types_json", "[]"
        ),
        "grade": candidate.get("grade", ""),
        "material_type": candidate.get("material_type", ""),
        "learning_material_id": candidate.get("learning_material_id", ""),
        "ocr_text_id": candidate.get("ocr_text_id", ""),
        "lesson_key": candidate.get("lesson_key", ""),
        "lesson_title": candidate.get("lesson_title", ""),
        "topic_title": candidate.get("topic_title", ""),
        "section_path": candidate.get("section_path", ""),
        "fragment_type": candidate.get("fragment_type", ""),
        "effective_content_length": measured,
        "effective_content": effective_content(str(candidate["markdown_text"])),
        "text_preview": candidate.get("text_preview", ""),
        "markdown_text": candidate["markdown_text"],
        "merge_policy_version": candidate.get("merge_policy_version", ""),
        "text_min_effective_chars": candidate.get(
            "text_min_effective_chars", ""
        ),
        "text_max_effective_chars": candidate.get(
            "text_max_effective_chars", ""
        ),
        "table_absorption_max_effective_chars": candidate.get(
            "table_absorption_max_effective_chars", ""
        ),
        "neighbor_policy": candidate.get("neighbor_policy", ""),
        "review_self_contained_evidence": "" if lower else "not_applicable",
        "review_semantic_focus": "not_applicable" if lower else "",
        "review_evidence_dilution": "not_applicable" if lower else "",
        "review_reason": "",
        "reviewer": "",
        "review_status": "pending",
    }


def _build_semantic_boundary_review(
    rows: Sequence[dict[str, str]],
    *,
    minimums: Sequence[int],
    maximums: Sequence[int],
    upper_candidates: Mapping[int, Sequence[dict[str, Any]]],
    lower_samples_per_threshold: int,
    upper_samples_per_threshold: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _validate_semantic_sample_counts(
        lower_samples_per_threshold=lower_samples_per_threshold,
        upper_samples_per_threshold=upper_samples_per_threshold,
    )

    source_candidates = _source_semantic_candidates(rows)
    review_rows: list[dict[str, Any]] = []
    lower_selected_ids: set[str] = set()
    lower_stratum_counts: Counter[tuple[str, str]] = Counter()
    lower_side_count = lower_samples_per_threshold // 2
    for threshold in minimums:
        side_specs = (
            (
                "at_or_below",
                [
                    row
                    for row in source_candidates
                    if int(row["effective_content_length"]) <= threshold
                ],
                max(1, threshold - 10),
                threshold,
            ),
            (
                "above",
                [
                    row
                    for row in source_candidates
                    if int(row["effective_content_length"]) > threshold
                ],
                threshold + 1,
                threshold + 10,
            ),
        )
        for boundary_side, candidates, window_min, window_max in side_specs:
            selected = _select_semantic_boundary_candidates(
                candidates,
                count=lower_side_count,
                threshold=threshold,
                primary_window_min=window_min,
                primary_window_max=window_max,
                selected_identities=lower_selected_ids,
                stratum_counts=lower_stratum_counts,
            )
            review_rows.extend(
                _semantic_review_row(
                    candidate,
                    boundary_kind="lower_minimum",
                    threshold=threshold,
                    boundary_side=boundary_side,
                    selection_rank=rank,
                    primary_window_min=window_min,
                    primary_window_max=window_max,
                )
                for rank, candidate in enumerate(selected, start=1)
            )

    upper_selected_ids: set[str] = set()
    upper_stratum_counts: Counter[tuple[str, str]] = Counter()
    upper_side_count = upper_samples_per_threshold // 2
    for threshold in maximums:
        merged_window_min = max(1, (4 * threshold + 4) // 5)
        merged_candidates = [
            row
            for row in upper_candidates.get(threshold, ())
            if int(row["effective_content_length"]) <= threshold
        ]
        merged_selected = _select_semantic_boundary_candidates(
            merged_candidates,
            count=upper_side_count,
            threshold=threshold,
            primary_window_min=merged_window_min,
            primary_window_max=threshold,
            selected_identities=upper_selected_ids,
            stratum_counts=upper_stratum_counts,
        )
        review_rows.extend(
            _semantic_review_row(
                candidate,
                boundary_kind="upper_maximum",
                threshold=threshold,
                boundary_side="merged_at_or_below",
                selection_rank=rank,
                primary_window_min=merged_window_min,
                primary_window_max=threshold,
            )
            for rank, candidate in enumerate(merged_selected, start=1)
        )

        source_window_max = (6 * threshold + 4) // 5
        source_over_cap = [
            row
            for row in source_candidates
            if int(row["effective_content_length"]) > threshold
        ]
        source_selected = _select_semantic_boundary_candidates(
            source_over_cap,
            count=upper_side_count,
            threshold=threshold,
            primary_window_min=threshold + 1,
            primary_window_max=source_window_max,
            selected_identities=upper_selected_ids,
            stratum_counts=upper_stratum_counts,
        )
        review_rows.extend(
            _semantic_review_row(
                candidate,
                boundary_kind="upper_maximum",
                threshold=threshold,
                boundary_side="source_above",
                selection_rank=rank,
                primary_window_min=threshold + 1,
                primary_window_max=source_window_max,
            )
            for rank, candidate in enumerate(source_selected, start=1)
        )

    expected_lower = len(minimums) * lower_samples_per_threshold
    expected_upper = len(maximums) * upper_samples_per_threshold
    lower_rows = [row for row in review_rows if row["boundary_kind"] == "lower_minimum"]
    upper_rows = [row for row in review_rows if row["boundary_kind"] == "upper_maximum"]
    if len(lower_rows) != expected_lower or len(upper_rows) != expected_upper:
        raise ValueError("semantic boundary review row count differs from its contract")
    if len({row["review_id"] for row in review_rows}) != len(review_rows):
        raise ValueError("semantic boundary review contains duplicate review_id values")

    stratum_counts = Counter(
        (str(row["grade"]), str(row["material_type"])) for row in review_rows
    )
    summary = {
        "contract_version": SEMANTIC_BOUNDARY_REVIEW_VERSION,
        "row_count": len(review_rows),
        "lower_row_count": len(lower_rows),
        "upper_row_count": len(upper_rows),
        "lower_samples_per_threshold": lower_samples_per_threshold,
        "upper_samples_per_threshold": upper_samples_per_threshold,
        "lower_side_samples_per_threshold": lower_side_count,
        "upper_side_samples_per_threshold": upper_side_count,
        "human_review_required": True,
        "automatic_semantic_labels": False,
        "allowed_review_labels": ["yes", "no", "uncertain"],
        "measurement_unit": "unicode_code_points",
        "sampling_method": "deterministic_boundary_distance_with_grade_material_balance",
        "lower_primary_windows": "threshold-10..threshold and threshold+1..threshold+10",
        "upper_primary_windows": "80%-100% merged and 100%-120% source",
        "grade_material_counts": {
            f"grade={grade}|material_type={material_type}": count
            for (grade, material_type), count in sorted(stratum_counts.items())
        },
    }
    return review_rows, summary


def _validate_semantic_sample_counts(
    *,
    lower_samples_per_threshold: int,
    upper_samples_per_threshold: int,
) -> None:
    if lower_samples_per_threshold <= 0 or lower_samples_per_threshold % 2:
        raise ValueError("lower semantic sample count must be a positive even number")
    if upper_samples_per_threshold <= 0 or upper_samples_per_threshold % 2:
        raise ValueError("upper semantic sample count must be a positive even number")


def survey_fragment_v1_1_with_semantic_review(
    rows: Sequence[dict[str, str]],
    *,
    text_min_thresholds: Sequence[int],
    text_max_thresholds: Sequence[int],
    table_absorption_thresholds: Sequence[int],
    neighbor_policies: Sequence[str],
    lower_samples_per_threshold: int,
    upper_samples_per_threshold: int,
    table_table_merge_enabled: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run the grid and create an unlabeled deterministic human review queue."""

    _validate_semantic_sample_counts(
        lower_samples_per_threshold=lower_samples_per_threshold,
        upper_samples_per_threshold=upper_samples_per_threshold,
    )
    survey, upper_candidates = _run_fragment_v1_1_survey(
        rows,
        text_min_thresholds=text_min_thresholds,
        text_max_thresholds=text_max_thresholds,
        table_absorption_thresholds=table_absorption_thresholds,
        neighbor_policies=neighbor_policies,
        table_table_merge_enabled=table_table_merge_enabled,
        collect_upper_boundary_candidates=True,
    )
    review_rows, review_summary = _build_semantic_boundary_review(
        rows,
        minimums=survey["text_min_thresholds"],
        maximums=survey["text_max_thresholds"],
        upper_candidates=upper_candidates,
        lower_samples_per_threshold=lower_samples_per_threshold,
        upper_samples_per_threshold=upper_samples_per_threshold,
    )
    survey["semantic_boundary_review"] = review_summary
    return survey, review_rows


def write_fragment_v1_1_survey(
    *,
    fragments_path: Path,
    validation_summary_path: Path,
    output_path: Path,
    text_min_thresholds: Sequence[int],
    text_max_thresholds: Sequence[int],
    table_absorption_thresholds: Sequence[int],
    neighbor_policies: Sequence[str],
    table_table_merge_enabled: bool = False,
    semantic_review_output_path: Path | None = None,
    semantic_review_workbook_output_path: Path | None = None,
    lower_semantic_samples_per_threshold: int = 0,
    upper_semantic_samples_per_threshold: int = 0,
) -> dict[str, Any]:
    """Validate the v1 source and atomically write the v1.1 survey."""

    source_validation = _verify_v1_validation_snapshot(
        fragments_path=fragments_path,
        validation_summary_path=validation_summary_path,
    )
    rows = _read_fragment_snapshot(fragments_path, required_fields=FRAGMENT_FIELDNAMES)
    semantic_values = (
        semantic_review_output_path is not None,
        semantic_review_workbook_output_path is not None,
        lower_semantic_samples_per_threshold > 0,
        upper_semantic_samples_per_threshold > 0,
    )
    if any(semantic_values) and not all(semantic_values):
        raise ValueError(
            "semantic review machine CSV, human workbook, and both per-threshold "
            "sample counts must be provided together"
        )
    if all(semantic_values):
        assert semantic_review_output_path is not None
        assert semantic_review_workbook_output_path is not None
        if semantic_review_output_path.resolve() == output_path.resolve():
            raise ValueError("survey JSON and semantic review CSV must use distinct paths")
        if semantic_review_workbook_output_path.resolve() in {
            output_path.resolve(),
            semantic_review_output_path.resolve(),
        }:
            raise ValueError("semantic review workbook must use a distinct path")
        survey, review_rows = survey_fragment_v1_1_with_semantic_review(
            rows,
            text_min_thresholds=text_min_thresholds,
            text_max_thresholds=text_max_thresholds,
            table_absorption_thresholds=table_absorption_thresholds,
            neighbor_policies=neighbor_policies,
            lower_samples_per_threshold=lower_semantic_samples_per_threshold,
            upper_samples_per_threshold=upper_semantic_samples_per_threshold,
            table_table_merge_enabled=table_table_merge_enabled,
        )
        _atomic_write_csv(
            semantic_review_output_path,
            review_rows,
            SEMANTIC_BOUNDARY_REVIEW_FIELDNAMES,
        )
        machine_review_sha256 = _sha256_file(semantic_review_output_path)
        workbook_summary = write_semantic_boundary_review_workbook(
            review_rows,
            semantic_review_workbook_output_path,
            source_machine_path=semantic_review_output_path,
            source_machine_sha256=machine_review_sha256,
        )
        survey["semantic_boundary_review"].update(
            {
                "review_path": semantic_review_output_path.as_posix(),
                "review_sha256": machine_review_sha256,
                "machine_review_path": semantic_review_output_path.as_posix(),
                "machine_review_sha256": machine_review_sha256,
                "human_review_workbook_path": (
                    semantic_review_workbook_output_path.as_posix()
                ),
                "human_review_workbook_sha256": workbook_summary["workbook_sha256"],
                "human_review_workbook_contract": workbook_summary[
                    "contract_version"
                ],
            }
        )
    else:
        survey = survey_fragment_v1_1_candidates(
            rows,
            text_min_thresholds=text_min_thresholds,
            text_max_thresholds=text_max_thresholds,
            table_absorption_thresholds=table_absorption_thresholds,
            neighbor_policies=neighbor_policies,
            table_table_merge_enabled=table_table_merge_enabled,
        )
    survey.update(
        {
            "source_fragments_path": fragments_path.as_posix(),
            "source_fragments_sha256": _sha256_file(fragments_path),
            "source_validation_path": validation_summary_path.as_posix(),
            "source_validation_sha256": _sha256_file(validation_summary_path),
            "source_lossless": source_validation["lossless"],
            "survey_path": output_path.as_posix(),
        }
    )
    _atomic_write_json(output_path, survey)
    return survey


def _merged_page_markers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    output: list[str] = []
    for row in rows:
        for page_id in json.loads(row.get("page_markers_json", "") or "[]"):
            value = str(page_id)
            if value not in output:
                output.append(value)
    return output


def merge_short_fragments_v1_1(
    rows: Sequence[dict[str, str]],
    *,
    text_min_effective_chars: int,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    neighbor_policy: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Iteratively create a bounded, lossless v1.1 retrieval snapshot."""

    _validate_v1_1_parameters(
        text_min_effective_chars=text_min_effective_chars,
        text_max_effective_chars=text_max_effective_chars,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
        neighbor_policy=neighbor_policy,
    )
    if {row["fragment_type"] for row in rows} - {"text", "table"}:
        raise ValueError("fragment_type must be text or table")
    contract = _merge_contract(
        text_min_effective_chars=text_min_effective_chars,
        text_max_effective_chars=text_max_effective_chars,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
        neighbor_policy=neighbor_policy,
    )
    output: list[dict[str, Any]] = []
    global_order = 0
    by_unit = _group_fragments_by_unit(rows)
    source_short_count = sum(
        0 < effective_content_length(row["markdown_text"])
        < text_min_effective_chars
        for row in rows
        if row["fragment_type"] == "text"
    )
    source_short_mergeable_count = 0
    source_short_no_compatible_neighbor_count = 0
    source_short_blocked_by_cap_count = 0
    explicit_table_context_merge_count = 0
    for unit_rows in by_unit.values():
        groups = [_new_merge_group(row) for row in unit_rows]
        for index, group in enumerate(groups):
            if not _group_initiates_merge(
                group,
                text_min_effective_chars=text_min_effective_chars,
                table_absorption_max_effective_chars=(
                    table_absorption_max_effective_chars
                ),
            ):
                continue
            uncapped = _candidate_neighbor_indices(
                groups,
                index=index,
                text_max_effective_chars=text_max_effective_chars,
                table_absorption_max_effective_chars=(
                    table_absorption_max_effective_chars
                ),
                enforce_cap=False,
            )
            capped = _candidate_neighbor_indices(
                groups,
                index=index,
                text_max_effective_chars=text_max_effective_chars,
                table_absorption_max_effective_chars=(
                    table_absorption_max_effective_chars
                ),
                enforce_cap=True,
            )
            if capped:
                source_short_mergeable_count += 1
            elif uncapped:
                source_short_blocked_by_cap_count += 1
            else:
                source_short_no_compatible_neighbor_count += 1
        explicit_table_context_merge_count += _merge_explicit_table_contexts(
            groups,
            text_max_effective_chars=text_max_effective_chars,
        )
        index = 0
        while index < len(groups):
            group = groups[index]
            if not _group_initiates_merge(
                group,
                text_min_effective_chars=text_min_effective_chars,
                table_absorption_max_effective_chars=(
                    table_absorption_max_effective_chars
                ),
            ):
                index += 1
                continue
            candidates = _candidate_neighbor_indices(
                groups,
                index=index,
                text_max_effective_chars=text_max_effective_chars,
                table_absorption_max_effective_chars=(
                    table_absorption_max_effective_chars
                ),
                enforce_cap=True,
            )
            if not candidates:
                index += 1
                continue
            neighbor_index = _select_neighbor_index(
                groups,
                index=index,
                candidates=candidates,
                text_min_effective_chars=text_min_effective_chars,
                neighbor_policy=neighbor_policy,
            )
            left_index, right_index = sorted((index, neighbor_index))
            groups[left_index : right_index + 1] = [
                _combine_groups(groups[left_index], groups[right_index])
            ]
            # Revisit the merged group and its left boundary. A new contiguous
            # short group may now be eligible, but unrelated earlier groups do
            # not need a full rescan.
            index = max(0, left_index - 1)

        for fragment_index, group in enumerate(groups, start=1):
            source_rows = list(group["source_rows"])
            source_types = _source_fragment_types(group)
            measured = int(group["effective_content_length"])
            is_residual_short = _group_initiates_merge(
                group,
                text_min_effective_chars=text_min_effective_chars,
                table_absorption_max_effective_chars=(
                    table_absorption_max_effective_chars
                ),
            )
            if measured == 0:
                merge_status = "structural_zero"
            elif is_residual_short:
                uncapped = _candidate_neighbor_indices(
                    groups,
                    index=fragment_index - 1,
                    text_max_effective_chars=text_max_effective_chars,
                    table_absorption_max_effective_chars=(
                        table_absorption_max_effective_chars
                    ),
                    enforce_cap=False,
                )
                merge_status = (
                    "short_unmerged_cap" if uncapped else "short_unmerged_scope"
                )
            elif len(source_rows) > 1:
                merge_status = "merged"
            else:
                merge_status = "unchanged"

            first = source_rows[0]
            last = source_rows[-1]
            markdown_text = str(group["markdown_text"])
            lineage = [row["fragment_id"] for row in source_rows]
            page_markers = _merged_page_markers(source_rows)
            output_type = _group_output_type(group)
            metadata_source = next(
                (
                    row
                    for row in source_rows
                    if row["fragment_type"] == output_type
                ),
                first,
            )
            global_order += 1
            merged = dict(metadata_source)
            merged.update(
                {
                    "fragment_id": f"{first['ocr_text_id']}#V1_1F{fragment_index:04d}",
                    "fragment_index": fragment_index,
                    "order_index": global_order,
                    "char_start": first["char_start"],
                    "char_end": last["char_end"],
                    "page_start": page_markers[0] if page_markers else "",
                    "page_end": page_markers[-1] if page_markers else "",
                    "page_marker_start": page_markers[0] if page_markers else "",
                    "page_marker_end": page_markers[-1] if page_markers else "",
                    "page_markers_json": json.dumps(page_markers, ensure_ascii=False),
                    "page_basis": "ocr_page_marker" if page_markers else "unavailable",
                    "section_path": group["canonical_section_path"],
                    "fragment_type": output_type,
                    "markdown_text": markdown_text,
                    "text_preview": preview_text(markdown_text),
                    "notes": (
                        "Lossless v1.1 retrieval fragment derived from immutable v1; "
                        "effective-content exclusions were measurement-only."
                    ),
                    "fragment_release": FRAGMENT_RELEASE_V1_1,
                    "effective_content_length": measured,
                    "merge_status": merge_status,
                    "merge_reason": ";".join(
                        dict.fromkeys(str(value) for value in group["merge_reasons"])
                    ),
                    "merge_policy_version": V1_1_MERGE_POLICY_VERSION,
                    "merged_from_fragment_ids_json": json.dumps(
                        lineage, ensure_ascii=False
                    ),
                    "merged_from_fragment_count": len(lineage),
                    "source_fragment_types_json": json.dumps(
                        source_types, ensure_ascii=False
                    ),
                    "source_fragment_index_start": first["fragment_index"],
                    "source_fragment_index_end": last["fragment_index"],
                }
            )
            if output_type == "text" and "table" in source_types:
                merged.update(
                    {
                        "table_caption": "",
                        "caption_status": "not_applicable",
                        "caption_position": "",
                        "caption_source_markdown": "",
                        "caption_char_start": "",
                        "caption_char_end": "",
                    }
                )
            output.append(merged)
    status_counts = Counter(str(row["merge_status"]) for row in output)
    output_lengths = [int(row["effective_content_length"]) for row in output]
    source_lengths = [effective_content_length(row["markdown_text"]) for row in rows]
    return output, {
        "fragment_release": FRAGMENT_RELEASE_V1_1,
        "source_fragment_count": len(rows),
        "fragment_count": len(output),
        "source_short_fragment_count": source_short_count,
        "source_merge_trigger_count": (
            source_short_mergeable_count
            + source_short_no_compatible_neighbor_count
            + source_short_blocked_by_cap_count
        ),
        "source_short_mergeable_count": source_short_mergeable_count,
        "source_short_no_compatible_neighbor_count": (
            source_short_no_compatible_neighbor_count
        ),
        "source_short_blocked_by_cap_count": source_short_blocked_by_cap_count,
        "source_structural_zero_count": sum(value == 0 for value in source_lengths),
        "structural_zero_count": sum(value == 0 for value in source_lengths),
        "merged_group_count": sum(
            int(row["merged_from_fragment_count"]) > 1 for row in output
        ),
        "explicit_table_context_merge_count": (
            explicit_table_context_merge_count
        ),
        "short_unmerged_scope_count": status_counts["short_unmerged_scope"],
        "short_unmerged_cap_count": status_counts["short_unmerged_cap"],
        "short_mergeable_count": source_short_mergeable_count,
        "short_no_compatible_neighbor_count": (
            source_short_no_compatible_neighbor_count
        ),
        "absorbed_table_count": sum(
            "table" in json.loads(str(row["source_fragment_types_json"]))
            and row["fragment_type"] == "text"
            for row in output
        ),
        "table_table_merged_group_count": 0,
        "maximum_lineage_count": max(
            (int(row["merged_from_fragment_count"]) for row in output),
            default=0,
        ),
        "source_effective_content_length_distribution": _distribution(source_lengths),
        "output_effective_content_length_distribution": _distribution(output_lengths),
        "preexisting_over_max_count": sum(
            row["fragment_type"] == "text"
            and effective_content_length(row["markdown_text"])
            > text_max_effective_chars
            for row in rows
        ),
        "merge_created_over_max_count": sum(
            int(row["merged_from_fragment_count"]) > 1
            and int(row["effective_content_length"]) > text_max_effective_chars
            for row in output
        ),
        "merge_status_counts": dict(sorted(status_counts.items())),
        "text_min_effective_chars": text_min_effective_chars,
        "text_max_effective_chars": text_max_effective_chars,
        "table_absorption_max_effective_chars": (
            table_absorption_max_effective_chars
        ),
        "neighbor_policy": neighbor_policy,
        "merge_contract": contract,
        "merge_contract_sha256": contract["merge_contract_sha256"],
    }


def validate_fragment_bundle_v1_1(
    *,
    source_rows: Sequence[dict[str, str]],
    fragment_rows: Sequence[dict[str, str]],
    text_min_effective_chars: int,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    neighbor_policy: str,
) -> dict[str, Any]:
    """Validate lineage, exact merge scope, measurement, and lossless content."""

    if len({row["fragment_id"] for row in fragment_rows}) != len(fragment_rows):
        raise ValueError("duplicate fragment_id in v1.1 bundle")
    source_by_unit = _group_fragments_by_unit(source_rows)
    output_by_unit = _group_fragments_by_unit(fragment_rows)
    if set(source_by_unit) != set(output_by_unit):
        raise ValueError("v1.1 unit set differs from v1")
    reconstructed_units = 0
    lineage_ids: list[str] = []
    for ocr_text_id, unit_source_rows in source_by_unit.items():
        unit_output_rows = output_by_unit[ocr_text_id]
        source_lookup = {row["fragment_id"]: row for row in unit_source_rows}
        unit_lineage: list[str] = []
        output_markdown: list[str] = []
        for expected_index, row in enumerate(unit_output_rows, start=1):
            if int(row["fragment_index"]) != expected_index:
                raise ValueError(f"non-contiguous v1.1 fragment_index in {ocr_text_id}")
            if row.get("fragment_release") != FRAGMENT_RELEASE_V1_1:
                raise ValueError(f"invalid fragment release: {row['fragment_id']}")
            lineage = json.loads(row.get("merged_from_fragment_ids_json", "") or "[]")
            if not lineage or int(row["merged_from_fragment_count"]) != len(lineage):
                raise ValueError(f"invalid v1 lineage: {row['fragment_id']}")
            try:
                sources = [source_lookup[str(fragment_id)] for fragment_id in lineage]
            except KeyError as exc:
                raise ValueError(f"unknown v1 lineage in {row['fragment_id']}") from exc
            source_indices = [int(source["fragment_index"]) for source in sources]
            if source_indices != list(range(source_indices[0], source_indices[-1] + 1)):
                raise ValueError(f"non-contiguous v1 lineage: {row['fragment_id']}")
            if int(row["source_fragment_index_start"]) != source_indices[0] or int(
                row["source_fragment_index_end"]
            ) != source_indices[-1]:
                raise ValueError(f"v1.1 lineage span mismatch: {row['fragment_id']}")
            if len({_canonical_merge_section_path(source) for source in sources}) != 1:
                raise ValueError(f"v1.1 row crosses section_path: {row['fragment_id']}")
            expected_section_path = _canonical_merge_section_path(sources[0])
            if row["section_path"] != expected_section_path:
                raise ValueError(f"v1.1 section path mismatch: {row['fragment_id']}")
            source_types = [source["fragment_type"] for source in sources]
            serialized_types = json.loads(
                row.get("source_fragment_types_json", "") or "[]"
            )
            if serialized_types != source_types:
                raise ValueError(f"v1.1 source types mismatch: {row['fragment_id']}")
            if source_types.count("table") > 1:
                raise ValueError(f"v1.1 row merged multiple tables: {row['fragment_id']}")
            if "table" in source_types and "text" in source_types:
                if row["fragment_type"] != "text":
                    raise ValueError(f"mixed v1.1 row must be text: {row['fragment_id']}")
                table_source = next(
                    source for source in sources if source["fragment_type"] == "table"
                )
                if table_source.get("caption_status") != "missing":
                    raise ValueError(
                        f"captioned table was absorbed: {row['fragment_id']}"
                    )
                table_length = effective_content_length(table_source["markdown_text"])
                is_explicit_context_merge = "explicit_table_context" in {
                    value
                    for value in row.get("merge_reason", "").split(";")
                    if value
                }
                if is_explicit_context_merge:
                    if source_types != ["text", "table"]:
                        raise ValueError(
                            "explicit table context must precede exactly one table: "
                            f"{row['fragment_id']}"
                        )
                    if not _is_explicit_table_context(_new_merge_group(sources[0])):
                        raise ValueError(
                            "invalid explicit table context: "
                            f"{row['fragment_id']}"
                        )
                else:
                    text_length = sum(
                        effective_content_length(source["markdown_text"])
                        for source in sources
                        if source["fragment_type"] == "text"
                    )
                    if not (
                        0
                        < table_length
                        < table_absorption_max_effective_chars
                        and text_length > 0
                    ):
                        raise ValueError(
                            "invalid short-table fallback: "
                            f"{row['fragment_id']}"
                        )
            expected_text = "".join(source["markdown_text"] for source in sources)
            if row["markdown_text"] != expected_text:
                raise ValueError(f"v1.1 text differs from v1 lineage: {row['fragment_id']}")
            if int(row["char_start"]) != int(sources[0]["char_start"]) or int(
                row["char_end"]
            ) != int(sources[-1]["char_end"]):
                raise ValueError(f"v1.1 character span mismatch: {row['fragment_id']}")
            measured = effective_content_length(row["markdown_text"])
            if int(row["effective_content_length"]) != measured:
                raise ValueError(f"v1.1 effective-content mismatch: {row['fragment_id']}")
            if len(sources) > 1 and measured > text_max_effective_chars:
                raise ValueError(f"merge-created row exceeds cap: {row['fragment_id']}")
            merge_status = row.get("merge_status", "")
            allowed_statuses = {
                "unchanged",
                "merged",
                "structural_zero",
                "short_unmerged_scope",
                "short_unmerged_cap",
            }
            if merge_status not in allowed_statuses:
                raise ValueError(f"invalid v1.1 merge status: {row['fragment_id']}")
            if merge_status == "structural_zero" and measured != 0:
                raise ValueError(f"structural_zero row has content: {row['fragment_id']}")
            if merge_status in {"short_unmerged_scope", "short_unmerged_cap"}:
                is_short = (
                    row["fragment_type"] == "text"
                    and 0 < measured < text_min_effective_chars
                ) or (
                    row["fragment_type"] == "table"
                    and row.get("caption_status") == "missing"
                    and 0 < measured < table_absorption_max_effective_chars
                )
                if not is_short:
                    raise ValueError(
                        f"short-unmerged row is not eligible short content: {row['fragment_id']}"
                    )
            if len(sources) > 1 and not row.get("merge_reason", "").strip():
                raise ValueError(f"merged row lacks merge reason: {row['fragment_id']}")
            if len(sources) == 1 and row.get("merge_reason", "").strip():
                raise ValueError(f"unmerged row has merge reason: {row['fragment_id']}")
            if row.get("merge_policy_version") != V1_1_MERGE_POLICY_VERSION:
                raise ValueError(f"invalid merge policy version: {row['fragment_id']}")
            unit_lineage.extend(str(value) for value in lineage)
            lineage_ids.extend(str(value) for value in lineage)
            output_markdown.append(row["markdown_text"])
        expected_lineage = [row["fragment_id"] for row in unit_source_rows]
        if unit_lineage != expected_lineage:
            raise ValueError(f"v1.1 lineage does not cover v1 exactly once: {ocr_text_id}")
        if "".join(output_markdown) != "".join(
            row["markdown_text"] for row in unit_source_rows
        ):
            raise ValueError(f"v1.1 lossless reconstruction mismatch: {ocr_text_id}")
        reconstructed_units += 1
    expected_all_ids = [row["fragment_id"] for row in source_rows]
    if lineage_ids != expected_all_ids:
        raise ValueError("v1.1 global lineage order differs from v1")
    contract = _merge_contract(
        text_min_effective_chars=text_min_effective_chars,
        text_max_effective_chars=text_max_effective_chars,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
        neighbor_policy=neighbor_policy,
    )
    return {
        "fragment_release": FRAGMENT_RELEASE_V1_1,
        "source_fragment_count": len(source_rows),
        "fragment_count": len(fragment_rows),
        "reconstructed_unit_count": reconstructed_units,
        "lineage_covers_source_exactly_once": True,
        "lossless": True,
        "measurement_only": True,
        "source_markdown_mutated": False,
        "table_table_merge_enabled": False,
        "merge_contract": contract,
        "merge_contract_sha256": contract["merge_contract_sha256"],
    }


def build_validate_and_write_v1_1(
    *,
    source_fragments_path: Path,
    source_validation_path: Path,
    output_dir: Path,
    text_min_effective_chars: int,
    text_max_effective_chars: int,
    table_absorption_max_effective_chars: int,
    neighbor_policy: str,
) -> dict[str, Any]:
    """Build and validate the v1.1 retrieval fragment snapshot."""

    source_validation = _verify_v1_validation_snapshot(
        fragments_path=source_fragments_path,
        validation_summary_path=source_validation_path,
    )
    source_rows = _read_fragment_snapshot(
        source_fragments_path,
        required_fields=FRAGMENT_FIELDNAMES,
    )
    fragments, build_summary = merge_short_fragments_v1_1(
        source_rows,
        text_min_effective_chars=text_min_effective_chars,
        text_max_effective_chars=text_max_effective_chars,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
        neighbor_policy=neighbor_policy,
    )
    fragments_path = output_dir / "learning_resource_fragments_v1_1.csv"
    summary_path = output_dir / "fragment_v1_1_validation_summary.json"
    _atomic_write_csv(fragments_path, fragments, FRAGMENT_V1_1_FIELDNAMES)
    serialized_rows = _read_fragment_snapshot(
        fragments_path,
        required_fields=FRAGMENT_V1_1_FIELDNAMES,
    )
    validation = validate_fragment_bundle_v1_1(
        source_rows=source_rows,
        fragment_rows=serialized_rows,
        text_min_effective_chars=text_min_effective_chars,
        text_max_effective_chars=text_max_effective_chars,
        table_absorption_max_effective_chars=(
            table_absorption_max_effective_chars
        ),
        neighbor_policy=neighbor_policy,
    )
    summary = {
        **build_summary,
        **validation,
        "source_fragments_path": source_fragments_path.as_posix(),
        "source_fragments_sha256": _sha256_file(source_fragments_path),
        "source_validation_path": source_validation_path.as_posix(),
        "source_validation_sha256": _sha256_file(source_validation_path),
        "source_sections_path": source_validation.get("sections_path"),
        "source_sections_sha256": source_validation.get("sections_sha256"),
        "sections_path": source_validation.get("sections_path"),
        "sections_sha256": source_validation.get("sections_sha256"),
        "fragments_path": fragments_path.as_posix(),
        "fragments_sha256": _sha256_file(fragments_path),
        "summary_path": summary_path.as_posix(),
    }
    _atomic_write_json(summary_path, summary)
    return summary

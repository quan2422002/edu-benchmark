"""Build a manifest for curated OCR Markdown learning resources.

This module treats ``shared/learning_resources/ocr_text`` as a read-only input
folder.  It creates a lightweight registry that later fragmentation and
retrieval steps can consume deterministically.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from edu_benchmark.learning_resources.utils import ensure_directory, relative_to_cwd

PAGE_MARKER_RE = re.compile(r"^\{(?P<page_id>\d+)\}-+\s*$", re.MULTILINE)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
LESSON_IN_PATH_RE = re.compile(r"(?:^|_)bai_(?P<number>\d+)(?P<suffix>[a-z])?(?:$|_)", re.IGNORECASE)
SGV_LESSON_RE = re.compile(r"sgv_tin_(?P<grade>\d+)_(?P<kind>00_hd_chung|bai_\d+[a-z]?)$", re.IGNORECASE)
SGK_LESSON_RE = re.compile(r"tin_(?P<grade>\d+)_bai_(?P<number>\d+)(?P<suffix>[a-z])?$", re.IGNORECASE)

MANIFEST_FIELDNAMES = [
    "ocr_text_id",
    "learning_material_id",
    "material_type",
    "grade",
    "book_title",
    "lesson_key",
    "lesson_number",
    "lesson_title",
    "topic_title",
    "source_markdown_path",
    "source_metadata_path",
    "image_dir",
    "page_marker_count",
    "page_stat_count",
    "table_count",
    "image_count",
    "first_heading",
    "status",
    "notes",
]


@dataclass(frozen=True)
class SourceRegistryEntry:
    """Canonical source-registry metadata for one SGK/SGV book.
    
    Attributes:
        learning_material_id: Stable ID from the source registry.
        source_title: Human-readable source title.
        material_type: Book type, usually ``SGK`` or ``SGV``.
        grade: Grade level as a string, for example ``"6"``.
        local_file_path: Local path recorded in the source registry.
    """

    learning_material_id: str
    source_title: str
    material_type: str
    grade: str
    local_file_path: str


@dataclass(frozen=True)
class TopicLessonEntry:
    """Topic-map metadata for one numbered SGK lesson.

    Attributes:
        lesson_title: Lesson title from the SGK table of contents.
        topic_title: Topic path, including subtopic when present.
        topic_item_id: Stable topic-map item ID for traceability.
    """

    lesson_title: str
    topic_title: str
    topic_item_id: str


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file into row dictionaries.
    
    Args:
        path: CSV file path to read.
    
    Returns:
        A list of dictionaries keyed by the CSV header row. Missing files are not
        handled here; callers should check existence when optional input is allowed.
    """

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, rows: Sequence[dict[str, object]], fieldnames: Sequence[str]) -> None:
    """Write row dictionaries to a UTF-8 CSV file.
    
    Args:
        path: Destination CSV file path.
        rows: Row dictionaries to write. Values are converted by ``csv.DictWriter``.
        fieldnames: Column order for the output file. Keys missing from a row are
            written as empty strings.
    
    Returns:
        None. The destination parent directory is created when needed.
    """

    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def load_source_registry(path: Path) -> dict[tuple[str, str], SourceRegistryEntry]:
    """Load SGK/SGV source metadata keyed by material type and grade.
    
    Args:
        path: CSV source registry path. Expected columns include
            ``learning_material_id``, ``source_title``, ``material_type``,
            ``grade``, and ``local_file_path``.
    
    Returns:
        A dictionary keyed by ``(material_type, grade)``. Returns an empty
        dictionary when the registry file does not exist.
    """

    entries: dict[tuple[str, str], SourceRegistryEntry] = {}
    if not path.exists():
        return entries
    for row in read_csv_rows(path):
        material_type = row.get("material_type", "").strip().upper()
        grade = row.get("grade", "").strip()
        if material_type and grade:
            entries[(material_type, grade)] = SourceRegistryEntry(
                learning_material_id=row.get("learning_material_id", "").strip(),
                source_title=row.get("source_title", "").strip(),
                material_type=material_type,
                grade=grade,
                local_file_path=row.get("local_file_path", "").strip(),
            )
    return entries


def topic_item_to_lesson_key(item_id: str) -> str:
    """Convert a topic-map lesson item ID to an OCR lesson key.

    Args:
        item_id: Topic-map ID such as ``TIN8-B10A`` or ``TIN6-B01``.

    Returns:
        A lesson key such as ``bai_10a`` or ``bai_01``. Returns an empty string
        for non-lesson IDs or unrecognized formats.
    """

    match = re.fullmatch(r"TIN(?P<grade>\d+)-B(?P<number>\d+)(?P<suffix>[A-Z]?)", item_id.strip(), re.IGNORECASE)
    if not match:
        return ""
    number = int(match.group("number"))
    suffix = (match.group("suffix") or "").lower()
    return f"bai_{number:02d}{suffix}"


def build_topic_path(item_id: str, rows_by_id: dict[str, dict[str, str]]) -> str:
    """Build a human-readable topic path for one topic-map item.

    Args:
        item_id: Item ID whose ancestors should be followed.
        rows_by_id: Topic-map rows keyed by ``item_id``.

    Returns:
        A topic path such as ``Chủ đề 4. Ứng dụng tin học > a. ...``. The
        current lesson title is excluded; only topic/subtopic ancestors are kept.
    """

    labels: list[str] = []
    current = rows_by_id.get(item_id, {})
    parent_id = current.get("parent_id", "").strip()
    seen: set[str] = set()
    while parent_id and parent_id not in seen:
        seen.add(parent_id)
        parent = rows_by_id.get(parent_id)
        if not parent:
            break
        item_type = parent.get("item_type", "").strip()
        if item_type in {"chu_de", "chu_de_con"}:
            label = parent.get("source_label", "").strip() or parent.get("normalized_label", "").strip()
            if label:
                labels.append(label)
        parent_id = parent.get("parent_id", "").strip()
    return " > ".join(reversed(labels))


def load_topic_lesson_map(path: Path) -> dict[tuple[str, str], TopicLessonEntry]:
    """Load SGK table-of-contents lesson metadata for manifest enrichment.

    Args:
        path: Topic/lesson map CSV path. Expected columns include ``item_id``,
            ``item_type``, ``grade``, ``source_label``, ``normalized_label`` and
            ``parent_id``. Missing files are allowed.

    Returns:
        A dictionary keyed by ``(grade, lesson_key)``. It contains only numbered
        lesson rows, so SGV guidance sections such as ``hd_chung`` remain unmapped.
    """

    if not path.exists():
        return {}
    rows = read_csv_rows(path)
    rows_by_id = {row.get("item_id", "").strip(): row for row in rows if row.get("item_id", "").strip()}
    entries: dict[tuple[str, str], TopicLessonEntry] = {}
    for row in rows:
        if row.get("item_type", "").strip() != "bai_hoc":
            continue
        item_id = row.get("item_id", "").strip()
        grade = row.get("grade", "").strip()
        lesson_key = topic_item_to_lesson_key(item_id)
        if not grade or not lesson_key:
            continue
        lesson_title = row.get("source_label", "").strip() or row.get("normalized_label", "").strip()
        entries[(grade, lesson_key)] = TopicLessonEntry(
            lesson_title=lesson_title,
            topic_title=build_topic_path(item_id, rows_by_id),
            topic_item_id=item_id,
        )
    return entries


def infer_material_type_and_grade(book_dir: Path) -> tuple[str, str]:
    """Infer book type and grade from an OCR book folder name.
    
    Args:
        book_dir: Folder such as ``sgk_tin_hoc_7`` or ``sgv_tin_hoc_6``.
    
    Returns:
        A ``(material_type, grade)`` tuple. Unknown values are returned as empty
        strings so the manifest can mark the row for review instead of crashing.
    """

    name = book_dir.name.lower()
    material_type = "SGV" if name.startswith("sgv_") else "SGK" if name.startswith("sgk_") else ""
    match = re.search(r"tin_hoc_(\d+)", name)
    grade = match.group(1) if match else ""
    return material_type, grade


def lesson_sort_key(path: Path) -> tuple[int, str]:
    """Return a stable sort key for OCR lesson folders.
    
    Args:
        path: Lesson folder path.
    
    Returns:
        A tuple that sorts general guidance folders first, then numbered lessons,
        then unknown folders at the end.
    """

    if "00_hd_chung" in path.name:
        return (0, path.name)
    match = LESSON_IN_PATH_RE.search(path.name)
    if match:
        return (int(match.group("number")), path.name)
    return (9999, path.name)


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


def iter_headings(markdown: str) -> Iterable[tuple[int, str]]:
    """Yield Markdown headings as clean title pairs.
    
    Args:
        markdown: Markdown document content.
    
    Returns:
        An iterator of ``(level, clean_title)`` pairs, where ``level`` is the number
        of heading marks and ``clean_title`` has inline markup removed.
    """

    for line in markdown.splitlines():
        match = HEADING_RE.match(line)
        if match:
            yield len(match.group(1)), strip_inline_markup(match.group(2))


def extract_first_heading(markdown: str) -> str:
    """Return the first Markdown heading title.
    
    Args:
        markdown: Markdown document content.
    
    Returns:
        The first clean heading title, or an empty string when no heading exists.
    """

    for _, heading in iter_headings(markdown):
        return heading
    return ""


def infer_topic_title(markdown: str) -> str:
    """Infer a topic title from Markdown headings.
    
    Args:
        markdown: Markdown document content.
    
    Returns:
        The first heading containing ``CHỦ ĐỀ``. Returns an empty string when the
        OCR Markdown does not expose a topic heading.
    """

    for _, heading in iter_headings(markdown):
        if "CHỦ ĐỀ" in heading.upper():
            return heading
    return ""


def infer_lesson_key_and_number(lesson_dir: Path, material_type: str) -> tuple[str, str]:
    """Infer a stable lesson key and lesson number from a lesson folder.
    
    Args:
        lesson_dir: OCR lesson folder path.
        material_type: Book type, usually ``SGK`` or ``SGV``.
    
    Returns:
        A ``(lesson_key, lesson_number)`` tuple. ``lesson_key`` is stable enough for
        filtering, for example ``bai_03``, ``bai_10a`` or ``hd_chung``;
        ``lesson_number`` keeps only the numeric lesson number for coarse matching.
    """

    name = lesson_dir.name
    if material_type == "SGV":
        match = SGV_LESSON_RE.match(name)
        if match and match.group("kind") == "00_hd_chung":
            return "hd_chung", ""
        match = LESSON_IN_PATH_RE.search(name)
    else:
        match = SGK_LESSON_RE.match(name)
    if match:
        number = match.group("number")
        suffix = (match.groupdict().get("suffix") or "").lower()
        return f"bai_{int(number):02d}{suffix}", str(int(number))
    return name, ""


def infer_lesson_title(markdown: str, lesson_number: str, lesson_key: str, material_type: str) -> str:
    """Infer a human-readable lesson title from headings and metadata.
    
    Args:
        markdown: Markdown document content for one lesson.
        lesson_number: Number inferred from the folder, or an empty string.
        lesson_key: Stable lesson key such as ``bai_03``, ``bai_10a`` or ``hd_chung``.
        material_type: Book type. Kept for future rules even when current rules do
            not branch heavily on it.
    
    Returns:
        A best-effort lesson title. Unknown titles fall back to the first heading or
        a generic ``Bài <number>`` label. Letter suffixes in split lessons, such as
        ``Bài 10A`` and ``Bài 10B``, are preserved in the display label.
    """

    headings = list(iter_headings(markdown))
    if lesson_key == "hd_chung":
        return "Hướng dẫn chung"
    if lesson_number:
        key_match = re.fullmatch(r"bai_0*(?P<number>\d+)(?P<suffix>[a-z]?)", lesson_key, re.IGNORECASE)
        suffix = (key_match.group("suffix") if key_match else "").upper()
        lesson_display = f"{lesson_number}{suffix}"
        suffix_pattern = rf"\s*{re.escape(suffix)}" if suffix else ""
        lesson_pattern = re.compile(rf"\bBÀI\s*{re.escape(lesson_number)}{suffix_pattern}\b\.?\s*(.*)", re.IGNORECASE)
        for index, (_, heading) in enumerate(headings):
            match = lesson_pattern.search(heading)
            if not match:
                continue
            remainder = match.group(1).strip(" .:-–—")
            if remainder:
                return f"Bài {lesson_display}. {remainder}"
            for _, next_heading in headings[index + 1 : index + 5]:
                upper = next_heading.upper()
                if "SAU BÀI NÀY" in upper or "CHỦ ĐỀ" in upper:
                    continue
                if re.fullmatch(r"BÀI\s*\d+[A-Z]?", upper):
                    continue
                return f"Bài {lesson_display}. {next_heading}"
        return f"Bài {lesson_display}"
    return extract_first_heading(markdown)


def count_markdown_tables(markdown: str) -> int:
    """Count Markdown table blocks in a document.
    
    Args:
        markdown: Markdown document content.
    
    Returns:
        Number of table-like blocks detected from separator rows. This is a rough
        quality signal for manifest/review, not a full table parser.
    """

    lines = markdown.splitlines()
    count = 0
    for index, line in enumerate(lines):
        if "|" not in line:
            continue
        if re.match(r"^\s*\|?\s*:?-{3,}:?", line):
            count += 1
        elif index + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}:?", lines[index + 1]):
            count += 1
    return count


def read_metadata(path: Path) -> dict:
    """Read a JSON metadata sidecar file.
    
    Args:
        path: Metadata JSON path next to the OCR Markdown file.
    
    Returns:
        Parsed metadata as a dictionary. Returns an empty dictionary when the file
        is missing or invalid JSON.
    """

    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def make_ocr_text_id(material_type: str, grade: str, lesson_key: str) -> str:
    """Build a deterministic OCR text identifier.
    
    Args:
        material_type: Book type, for example ``SGK`` or ``SGV``.
        grade: Grade level as a string.
        lesson_key: Stable lesson key such as ``bai_03`` or ``hd_chung``.
    
    Returns:
        Uppercase identifier such as ``OCR-SGK-TIN6-BAI03``.
    """

    if lesson_key == "hd_chung":
        suffix = "HDCHUNG"
    else:
        suffix = lesson_key.replace("bai_", "BAI")
    return f"OCR-{material_type}-TIN{grade}-{suffix}".upper()


def build_manifest_rows(
    *,
    ocr_root: Path,
    source_registry_path: Path,
    only_grade: str | None = "6",
    topic_map_path: Path | None = None,
) -> list[dict[str, object]]:
    """Scan OCR Markdown folders and produce manifest rows.
    
    Args:
        ocr_root: Root folder containing OCR book folders under
            ``shared/learning_resources/ocr_text``.
        source_registry_path: CSV registry used to attach canonical book metadata.
        only_grade: Optional grade filter. Use ``None`` or an empty CLI value to
            include all available grades.
        topic_map_path: Optional SGK topic/lesson map used to enrich numbered
            lessons with table-of-contents titles and topic paths. This is used
            for both SGK rows and matching SGV lesson rows.
    
    Returns:
        A list of manifest rows for downstream fragment building, retrieval
        indexing, and audit work. Source OCR folders are treated as read-only.
    """

    source_registry = load_source_registry(source_registry_path)
    topic_lesson_map = load_topic_lesson_map(topic_map_path) if topic_map_path else {}
    rows: list[dict[str, object]] = []
    for book_dir in sorted(path for path in ocr_root.iterdir() if path.is_dir()):
        material_type, grade = infer_material_type_and_grade(book_dir)
        if only_grade and grade != only_grade:
            continue
        source = source_registry.get((material_type, grade))
        for lesson_dir in sorted([path for path in book_dir.iterdir() if path.is_dir()], key=lesson_sort_key):
            md_files = sorted(lesson_dir.glob("*.md"))
            if not md_files:
                continue
            markdown_path = md_files[0]
            metadata_path = markdown_path.with_suffix(".metadata.json")
            markdown = markdown_path.read_text(encoding="utf-8", errors="replace")
            metadata = read_metadata(metadata_path)
            lesson_key, lesson_number = infer_lesson_key_and_number(lesson_dir, material_type)
            topic_entry = topic_lesson_map.get((grade, lesson_key))
            inferred_lesson_title = infer_lesson_title(markdown, lesson_number, lesson_key, material_type)
            inferred_topic_title = infer_topic_title(markdown)
            topic_title = topic_entry.topic_title if topic_entry and topic_entry.topic_title else inferred_topic_title
            lesson_title = inferred_lesson_title
            if material_type == "SGK" and topic_entry and topic_entry.lesson_title:
                lesson_title = topic_entry.lesson_title
            notes: list[str] = []
            needs_review = False
            if source is None:
                notes.append("Chưa nối được với source registry.")
                needs_review = True
            if not metadata_path.exists():
                notes.append("Thiếu file metadata JSON.")
                needs_review = True
            if not topic_title and lesson_key != "hd_chung":
                notes.append("Chưa suy ra được chủ đề từ heading hoặc topic registry.")
                needs_review = True
            if topic_entry and material_type == "SGV":
                notes.append(f"topic_title nối theo SGK topic registry: {topic_entry.topic_item_id}.")
            rows.append(
                {
                    "ocr_text_id": make_ocr_text_id(material_type, grade, lesson_key),
                    "learning_material_id": source.learning_material_id if source else "",
                    "material_type": material_type,
                    "grade": grade,
                    "book_title": source.source_title if source else f"Tin học {grade} ({material_type})",
                    "lesson_key": lesson_key,
                    "lesson_number": lesson_number,
                    "lesson_title": lesson_title,
                    "topic_title": topic_title,
                    "source_markdown_path": relative_to_cwd(markdown_path),
                    "source_metadata_path": relative_to_cwd(metadata_path) if metadata_path.exists() else "",
                    "image_dir": relative_to_cwd(lesson_dir),
                    "page_marker_count": len(PAGE_MARKER_RE.findall(markdown)),
                    "page_stat_count": len(metadata.get("page_stats", [])) if isinstance(metadata, dict) else 0,
                    "table_count": count_markdown_tables(markdown),
                    "image_count": len(IMAGE_RE.findall(markdown)),
                    "first_heading": extract_first_heading(markdown),
                    "status": "needs_uet_review" if needs_review else "draft",
                    "notes": " ".join(notes),
                }
            )
    return rows


def write_manifest(rows: Sequence[dict[str, object]], output_path: Path) -> None:
    """Write OCR manifest rows to the canonical CSV path.
    
    Args:
        rows: Manifest rows produced by ``build_manifest_rows``.
        output_path: Destination CSV path.
    
    Returns:
        None. The output file is overwritten deterministically.
    """

    write_csv_rows(output_path, rows, MANIFEST_FIELDNAMES)

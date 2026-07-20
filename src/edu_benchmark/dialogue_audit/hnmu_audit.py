"""Audit HNMU raw teacher dialogue batches for Plan 04.

This module performs the deterministic part of Plan 04: reading raw Excel rows,
checking required fields and dialogue format, measuring coverage, finding
text-level duplicates, and attaching lightweight learning-resource evidence.
Semantic judgment remains conservative and is routed to HNMU/UET review queues.
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from edu_benchmark.data_io.xlsx import read_xlsx_rows, slug_header
from edu_benchmark.learning_resources.retrieval_api import DEFAULT_INDEX_PATH, search_learning_fragments
from edu_benchmark.learning_resources.utils import ensure_directory

REQUIRED_FIELDS = [
    "stt",
    "lesson",
    "position",
    "question",
    "bloom_level",
    "answer_sgv",
    "dialogue",
]

HEADER_ALIASES = {
    "stt": {"stt"},
    "lesson": {"bai"},
    "position": {"vi_tri", "vitri"},
    "question": {"cau_hoi"},
    "bloom_level": {"muc_bloom", "muc_do", "muc_nhan_thuc"},
    "answer_sgv": {"dap_an_sgv", "dap_an"},
    "dialogue": {"hoi_thoai_gia_su_theo_phuong_phap_dan_giao", "hoi_thoai_gia_su", "hoi_thoai"},
}

SPEAKER_RE = re.compile(r"(^|\n)\s*(?P<label>[A-ZÀ-Ỵ]{2,5})\s*:", re.UNICODE)
LESSON_CODE_RE = re.compile(
    r"(?:^|[\s\[])(?:Bài\s*)?(?P<number>\d{1,2})\s*(?P<suffix>[AaBb])?(?=\s*(?:[\]\).:\-]|$))",
    re.IGNORECASE,
)
LESSON_NUMBER_RE = LESSON_CODE_RE
GRADE_RE = re.compile(r"Lớp\s*(?P<grade>\d+)", re.IGNORECASE)
DEFAULT_TOPIC_LESSON_REGISTRY = Path("shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv")


@dataclass(frozen=True)
class RawDialogueRow:
    """Normalized row from one HNMU raw Excel file.

    Attributes:
        sample_id: Stable derived ID for audit outputs.
        source_file: Path to the source Excel file.
        source_row_number: One-based Excel row number.
        grade: Numeric grade string such as ``"6"``.
        grade_label: Human-readable grade label such as ``"Lớp 6"``.
        stt: Original row ordinal from HNMU.
        lesson: Raw lesson field.
        position: Raw position field.
        question: Raw student/task question field.
        bloom_level: Raw cognitive-level field.
        answer_sgv: Raw answer field attributed to SGV.
        dialogue: Raw scaffolded tutor dialogue field.
    """

    sample_id: str
    source_file: str
    source_row_number: int
    grade: str
    grade_label: str
    stt: str
    lesson: str
    position: str
    question: str
    bloom_level: str
    answer_sgv: str
    dialogue: str

    def to_dict(self) -> dict[str, str | int]:
        """Return the row as a dictionary for CSV writing.

        Args:
            None.

        Returns:
            Dictionary with all normalized row fields.
        """

        return {
            "sample_id": self.sample_id,
            "source_file": self.source_file,
            "source_row_number": self.source_row_number,
            "grade": self.grade,
            "grade_label": self.grade_label,
            "stt": self.stt,
            "lesson": self.lesson,
            "position": self.position,
            "question": self.question,
            "bloom_level": self.bloom_level,
            "answer_sgv": self.answer_sgv,
            "dialogue": self.dialogue,
        }


def normalize_text(value: str) -> str:
    """Normalize text for duplicate and format checks.

    Args:
        value: Raw text.

    Returns:
        Lowercase whitespace-collapsed text.
    """

    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def extract_grade_label(path: Path) -> tuple[str, str]:
    """Infer grade label and numeric grade from a source filename.

    Args:
        path: Raw Excel path such as ``Lớp 6.xlsx``.

    Returns:
        ``(grade_label, grade)``. Unknown grade returns empty strings.
    """

    match = GRADE_RE.search(path.stem)
    if not match:
        return "", ""
    grade = match.group("grade")
    return f"Lớp {grade}", grade


def find_header_row(rows: Sequence[Sequence[str]]) -> tuple[int, dict[str, int]]:
    """Find the HNMU header row and map canonical fields to column indexes.

    Args:
        rows: Raw worksheet rows from ``read_xlsx_rows``.

    Returns:
        Tuple ``(header_row_index, column_map)`` using zero-based row and column
        indexes.

    Raises:
        ValueError: If no row contains enough required HNMU headers.
    """

    for row_index, row in enumerate(rows):
        slug_to_index = {slug_header(value): index for index, value in enumerate(row) if value}
        mapping: dict[str, int] = {}
        for canonical, aliases in HEADER_ALIASES.items():
            for alias in aliases:
                if alias in slug_to_index:
                    mapping[canonical] = slug_to_index[alias]
                    break
        if len(mapping) >= 5 and "dialogue" in mapping and "question" in mapping:
            return row_index, mapping
    raise ValueError("Cannot find HNMU header row")


def row_value(row: Sequence[str], index: int | None) -> str:
    """Return a safe string value from a row/index pair.

    Args:
        row: Worksheet row.
        index: Optional column index.

    Returns:
        Stripped string value or an empty string if the index is absent.
    """

    if index is None or index >= len(row):
        return ""
    value = row[index]
    if value.endswith(".0") and value[:-2].isdigit():
        return value[:-2]
    return value.strip()


def load_dialogue_rows(source_files: Sequence[Path], *, include_grades: set[str]) -> list[RawDialogueRow]:
    """Load HNMU Excel rows for selected grades.

    Args:
        source_files: Raw Excel paths to inspect.
        include_grades: Numeric grade strings to include, for example
            ``{"6", "7"}``.

    Returns:
        Normalized rows with at least one non-empty core content field. Source
        files outside ``include_grades`` are ignored.
    """

    records: list[RawDialogueRow] = []
    for source_file in source_files:
        grade_label, grade = extract_grade_label(source_file)
        if grade not in include_grades:
            continue
        rows = read_xlsx_rows(source_file)
        header_index, columns = find_header_row(rows)
        for offset, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
            values = {field: row_value(row, columns.get(field)) for field in REQUIRED_FIELDS}
            if not any(values[field] for field in ("question", "answer_sgv", "dialogue", "lesson")):
                continue
            stt_for_id = values["stt"] or str(offset)
            sample_id = f"HNMU-G{grade}-R{offset:04d}-STT{re.sub(r'[^0-9A-Za-z]+', '', stt_for_id) or offset}"
            records.append(
                RawDialogueRow(
                    sample_id=sample_id,
                    source_file=source_file.as_posix(),
                    source_row_number=offset,
                    grade=grade,
                    grade_label=grade_label,
                    stt=values["stt"],
                    lesson=values["lesson"],
                    position=values["position"],
                    question=values["question"],
                    bloom_level=values["bloom_level"],
                    answer_sgv=values["answer_sgv"],
                    dialogue=values["dialogue"],
                )
            )
    return records


def bloom_band(value: str) -> str:
    """Map a raw Bloom/cognitive-level label to the project v0 band.

    Args:
        value: Raw cognitive-level field from HNMU.

    Returns:
        One of ``Nhận biết``, ``Thông hiểu``, ``Vận dụng``, or ``Không rõ``.
    """

    normalized = normalize_text(value)
    if "nhan biet" in slug_header(normalized).replace("_", " "):
        return "Nhận biết"
    if "thong hieu" in slug_header(normalized).replace("_", " "):
        return "Thông hiểu"
    if "van dung" in slug_header(normalized).replace("_", " "):
        return "Vận dụng"
    return "Không rõ"


def lesson_code(value: str) -> str:
    """Extract a regex-only lesson code from a raw lesson/title string.

    Args:
        value: Raw lesson/title string. Supported forms include
            ``Bài 8A. ...``, ``Bài 8a: ...``, ``[8b] ...``, and
            ``10a. ...``. The parser only uses explicit lesson number and
            optional ``A``/``B`` suffix. It intentionally does not use fuzzy
            matching or semantic title similarity.

    Returns:
        Canonical compact lesson code such as ``8``, ``8A`` or ``10B``. Returns
        an empty string if the explicit regex pattern is absent.
    """

    match = LESSON_CODE_RE.search(value or "")
    if not match:
        return ""
    number = str(int(match.group("number")))
    suffix = (match.group("suffix") or "").upper()
    return f"{number}{suffix}"


def lesson_number(value: str) -> str:
    """Extract only the numeric lesson number from a raw lesson/title string.

    Args:
        value: Raw lesson/title string.

    Returns:
        Lesson number as a string, or an empty string if absent. The extraction
        is regex-only and ignores any optional ``A``/``B`` suffix.
    """

    code = lesson_code(value)
    match = re.fullmatch(r"(?P<number>\d+)[AB]?", code)
    return match.group("number") if match else ""


def lesson_key(value: str) -> str:
    """Convert a raw lesson/title string into the fragment lesson key.

    Args:
        value: Raw lesson/title string such as ``Bài 17. Chương trình máy tính``
            or ``[8b] Làm quen với phần mềm chỉnh sửa ảnh``.

    Returns:
        Lesson key such as ``bai_17`` or ``bai_08b``. Returns an empty string
        when no explicit regex lesson code can be extracted. No fuzzy matching
        or title-similarity lookup is used.
    """

    code = lesson_code(value)
    match = re.fullmatch(r"(?P<number>\d+)(?P<suffix>[AB]?)", code)
    if not match:
        return ""
    suffix = match.group("suffix").lower()
    return f"bai_{int(match.group('number')):02d}{suffix}"


def load_topic_lesson_map(registry_path: Path = DEFAULT_TOPIC_LESSON_REGISTRY) -> dict[tuple[str, str], dict[str, str]]:
    """Load the v0 SGK/SGV topic-lesson registry for coverage mapping.

    Args:
        registry_path: CSV registry containing ``chu_de`` and ``bai_hoc`` rows.

    Returns:
        Mapping from ``(grade, lesson_code)`` to topic/lesson metadata. The
        lesson code is regex-derived, for example ``8``, ``8A`` or ``10B``.
        Missing or unreadable registries return an empty mapping so the audit
        can still run conservatively. No fuzzy matching is used.
    """

    if not registry_path.exists():
        return {}
    try:
        with registry_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError:
        return {}

    topics_by_id = {
        row.get("item_id", ""): row
        for row in rows
        if row.get("item_type") in {"chu_de", "chu_de_con"}
    }
    mapping: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        if row.get("item_type") != "bai_hoc":
            continue
        grade = str(row.get("grade", "")).strip()
        code = lesson_code(row.get("source_label", "") or row.get("normalized_label", ""))
        if not grade or not code:
            continue
        topic = topics_by_id.get(row.get("parent_id", ""), {})
        mapping[(grade, code)] = {
            "topic_id": topic.get("item_id", ""),
            "topic_label": topic.get("normalized_label", "") or topic.get("source_label", ""),
            "lesson_id": row.get("item_id", ""),
            "lesson_label": row.get("normalized_label", "") or row.get("source_label", ""),
            "registry_status": row.get("status", ""),
            "topic_registry_status": topic.get("status", ""),
        }
    return mapping


def row_topic_lesson_metadata(row: RawDialogueRow, topic_lesson_map: dict[tuple[str, str], dict[str, str]]) -> dict[str, str]:
    """Resolve topic and lesson metadata for one audit row.

    Args:
        row: Normalized HNMU dialogue row.
        topic_lesson_map: Mapping returned by ``load_topic_lesson_map``.

    Returns:
        Topic/lesson metadata. If the row cannot be mapped, conservative
        ``Không rõ`` labels are returned.
    """

    code = lesson_code(row.lesson)
    number = lesson_number(row.lesson)
    matched = topic_lesson_map.get((row.grade, code), {}) if code else {}
    return {
        "grade": row.grade,
        "grade_label": row.grade_label,
        "topic_id": matched.get("topic_id", ""),
        "topic_label": matched.get("topic_label", "Không rõ chủ đề"),
        "lesson_id": matched.get("lesson_id", ""),
        "lesson_number": number,
        "lesson_label": matched.get("lesson_label", row.lesson or "<blank>"),
        "registry_status": matched.get("registry_status", "unmapped"),
        "topic_registry_status": matched.get("topic_registry_status", "unmapped"),
    }


def _direct_lesson_lookup(row: RawDialogueRow, material_filter: str | None, *, index_path: Path) -> dict[str, str]:
    """Fallback to direct SQLite lookup by grade, material type, and lesson key.

    Args:
        row: Normalized HNMU row.
        material_filter: Optional material type inferred from the position field.
        index_path: SQLite learning-resource index path.

    Returns:
        Evidence dictionary with the same fields as ``best_learning_evidence``.
        Empty evidence is returned when the lesson key is unknown or absent.
    """

    key = lesson_key(row.lesson)
    if not key or not index_path.exists():
        return {}
    where = ["grade = ?", "lesson_key = ?"]
    params: list[str] = [row.grade, key]
    if material_filter:
        where.append("material_type = ?")
        params.append(material_filter)
    sql = f"""
        SELECT *
        FROM learning_fragments
        WHERE {' AND '.join(where)}
        ORDER BY order_index
        LIMIT 1
    """
    try:
        with sqlite3.connect(index_path) as conn:
            conn.row_factory = sqlite3.Row
            row_result = conn.execute(sql, params).fetchone()
    except sqlite3.Error:
        row_result = None
    if row_result is None and material_filter:
        return _direct_lesson_lookup(row, None, index_path=index_path)
    if row_result is None:
        return {}
    return {
        "evidence_fragment_id": str(row_result["fragment_id"]),
        "evidence_material_type": str(row_result["material_type"]),
        "evidence_lesson_title": str(row_result["lesson_title"]),
        "evidence_page_start": str(row_result["page_start"]),
        "evidence_source_markdown_path": str(row_result["source_markdown_path"]),
        "evidence_status": str(row_result["status"]),
        "evidence_match_reason": "Fallback trực tiếp theo grade + lesson_key + material_type nếu có.",
    }


def speaker_labels(dialogue: str) -> list[str]:
    """Extract speaker labels from a raw dialogue.

    Args:
        dialogue: Raw dialogue text.

    Returns:
        Speaker labels such as ``HS`` and ``AI`` in encounter order.
    """

    return [match.group("label").strip().upper() for match in SPEAKER_RE.finditer(dialogue or "")]


def field_issues(row: RawDialogueRow) -> list[dict[str, str]]:
    """Create missing-field and format issue rows for one sample.

    Args:
        row: Normalized HNMU dialogue row.

    Returns:
        Issue dictionaries suitable for ``missing_field_report.csv``.
    """

    issues: list[dict[str, str]] = []
    data = row.to_dict()
    for field in REQUIRED_FIELDS:
        if not str(data.get(field, "")).strip():
            issues.append({
                "sample_id": row.sample_id,
                "issue_type": "missing_required_field",
                "field": field,
                "severity": "high" if field in {"question", "dialogue", "answer_sgv"} else "medium",
                "message": f"Thiếu trường bắt buộc: {field}",
            })
    labels = speaker_labels(row.dialogue)
    if row.dialogue and "HS" not in labels:
        issues.append({"sample_id": row.sample_id, "issue_type": "dialogue_format", "field": "dialogue", "severity": "high", "message": "Hội thoại không có nhãn HS:."})
    if row.dialogue and "AI" not in labels:
        issues.append({"sample_id": row.sample_id, "issue_type": "dialogue_format", "field": "dialogue", "severity": "high", "message": "Hội thoại không có nhãn AI:."})
    unexpected = sorted({label for label in labels if label not in {"HS", "AI"}})
    if unexpected:
        issues.append({"sample_id": row.sample_id, "issue_type": "dialogue_format", "field": "dialogue", "severity": "medium", "message": "Có nhãn lượt nói lạ: " + ", ".join(unexpected)})
    if row.dialogue and len(normalize_text(row.dialogue)) < 80:
        issues.append({"sample_id": row.sample_id, "issue_type": "dialogue_format", "field": "dialogue", "severity": "medium", "message": "Hội thoại quá ngắn để kiểm giàn giáo đáng tin cậy."})
    if bloom_band(row.bloom_level) == "Không rõ":
        issues.append({"sample_id": row.sample_id, "issue_type": "metadata_format", "field": "bloom_level", "severity": "medium", "message": "Không nhận diện được mức nhận thức v0."})
    return issues


def _coverage_item(
    *,
    dimension: str,
    value: str,
    count: int,
    total: int,
    grade: str = "",
    grade_label: str = "",
    topic_id: str = "",
    topic_label: str = "",
    lesson_id: str = "",
    lesson_label: str = "",
    registry_status: str = "",
) -> dict[str, str | int | float]:
    """Create one normalized coverage summary row.

    Args:
        dimension: Coverage axis name.
        value: Human-readable bucket value.
        count: Number of samples in the bucket.
        total: Total audited sample count used as denominator.
        grade: Optional numeric grade for grade-dependent buckets.
        grade_label: Optional human-readable grade label.
        topic_id: Optional registry topic ID.
        topic_label: Optional topic label.
        lesson_id: Optional registry lesson ID.
        lesson_label: Optional lesson label.
        registry_status: Optional status from the topic/lesson registry.

    Returns:
        Dictionary row for ``coverage_summary.csv``.
    """

    return {
        "dimension": dimension,
        "value": value or "<blank>",
        "grade": grade,
        "grade_label": grade_label,
        "topic_id": topic_id,
        "topic_label": topic_label,
        "lesson_id": lesson_id,
        "lesson_label": lesson_label,
        "registry_status": registry_status,
        "count": count,
        "percentage": round(count / (total or 1), 4),
    }


def coverage_rows(
    rows: Sequence[RawDialogueRow],
    *,
    topic_lesson_map: dict[tuple[str, str], dict[str, str]] | None = None,
) -> list[dict[str, str | int | float]]:
    """Summarize coverage by grade, topic, grade-specific lesson, Bloom, and source.

    Args:
        rows: Normalized HNMU rows.
        topic_lesson_map: Optional mapping from ``(grade, lesson_code)`` to
            topic/lesson metadata. If omitted, the default registry is loaded.

    Returns:
        Rows for ``coverage_summary.csv``. Topic is treated as a cross-grade
        axis, while lesson coverage is always grade-dependent.
    """

    total = len(rows) or 1
    topic_lesson_map = topic_lesson_map if topic_lesson_map is not None else load_topic_lesson_map()
    metadata_by_sample = {row.sample_id: row_topic_lesson_metadata(row, topic_lesson_map) for row in rows}
    output: list[dict[str, str | int | float]] = []

    for value, count in Counter(row.grade_label for row in rows).most_common():
        grade = value.replace("Lớp", "").strip() if value else ""
        output.append(_coverage_item(dimension="grade", value=value, count=count, total=total, grade=grade, grade_label=value))

    topic_counter = Counter(meta["topic_label"] for meta in metadata_by_sample.values())
    for topic_label, count in topic_counter.most_common():
        topic_ids = sorted({meta["topic_id"] for meta in metadata_by_sample.values() if meta["topic_label"] == topic_label and meta["topic_id"]})
        statuses = sorted({meta["topic_registry_status"] for meta in metadata_by_sample.values() if meta["topic_label"] == topic_label and meta["topic_registry_status"]})
        output.append(_coverage_item(
            dimension="topic",
            value=topic_label,
            count=count,
            total=total,
            topic_id=";".join(topic_ids),
            topic_label=topic_label,
            registry_status=";".join(statuses),
        ))

    lesson_counter: Counter[tuple[str, str, str, str, str, str, str]] = Counter()
    for meta in metadata_by_sample.values():
        key = (
            meta["grade"],
            meta["grade_label"],
            meta["topic_id"],
            meta["topic_label"],
            meta["lesson_id"],
            meta["lesson_label"],
            meta["registry_status"],
        )
        lesson_counter[key] += 1
    for (grade, grade_label, topic_id, topic_label, lesson_id, lesson_label, status), count in lesson_counter.most_common():
        output.append(_coverage_item(
            dimension="lesson_by_grade",
            value=f"{grade_label} — {lesson_label}",
            grade=grade,
            grade_label=grade_label,
            topic_id=topic_id,
            topic_label=topic_label,
            lesson_id=lesson_id,
            lesson_label=lesson_label,
            registry_status=status,
            count=count,
            total=total,
        ))

    for value, count in Counter(bloom_band(row.bloom_level) for row in rows).most_common():
        output.append(_coverage_item(dimension="bloom_band", value=value, count=count, total=total))

    for value, count in Counter(Path(row.source_file).name for row in rows).most_common():
        output.append(_coverage_item(dimension="source_file", value=value, count=count, total=total))

    return output


def duplicate_rows(rows: Sequence[RawDialogueRow], *, near_threshold: float = 0.96) -> list[dict[str, str | float]]:
    """Find exact and near-duplicate dialogue samples.

    Args:
        rows: Normalized HNMU rows.
        near_threshold: Similarity threshold for near-duplicate combined text.

    Returns:
        Candidate duplicate pairs for ``duplicate_candidates.csv``.
    """

    results: list[dict[str, str | float]] = []
    by_question: dict[str, list[RawDialogueRow]] = defaultdict(list)
    by_dialogue: dict[str, list[RawDialogueRow]] = defaultdict(list)
    for row in rows:
        by_question[normalize_text(row.question)].append(row)
        by_dialogue[normalize_text(row.dialogue)].append(row)
    for duplicate_type, groups in (("exact_question", by_question), ("exact_dialogue", by_dialogue)):
        for key, group in groups.items():
            if key and len(group) > 1:
                base = group[0]
                for other in group[1:]:
                    results.append({
                        "duplicate_type": duplicate_type,
                        "sample_id_a": base.sample_id,
                        "sample_id_b": other.sample_id,
                        "similarity": 1.0,
                        "note": "Trùng chính xác sau chuẩn hóa khoảng trắng/chữ thường.",
                    })
    compact = [(row, normalize_text(" ".join([row.lesson, row.question, row.answer_sgv, row.dialogue]))) for row in rows]
    for index, (left, left_text) in enumerate(compact):
        if len(left_text) < 120:
            continue
        for right, right_text in compact[index + 1 :]:
            if left.grade != right.grade or len(right_text) < 120:
                continue
            ratio = difflib.SequenceMatcher(None, left_text, right_text).ratio()
            if near_threshold <= ratio < 1.0:
                results.append({
                    "duplicate_type": "near_duplicate_combined_text",
                    "sample_id_a": left.sample_id,
                    "sample_id_b": right.sample_id,
                    "similarity": round(ratio, 4),
                    "note": "Gần trùng theo lesson + question + answer + dialogue.",
                })
    return results


def best_learning_evidence(row: RawDialogueRow, *, index_path: Path = DEFAULT_INDEX_PATH) -> dict[str, str]:
    """Find lightweight learning-resource evidence for one sample.

    Args:
        row: Normalized HNMU row.
        index_path: SQLite learning-resource index path.

    Returns:
        Evidence fields for audit output. Empty fields mean no candidate was
        found by the v0 retrieval index.
    """

    material_filter = None
    upper_position = row.position.upper()
    if "SGV" in upper_position:
        material_filter = "SGV"
    elif "SGK" in upper_position:
        material_filter = "SGK"

    key = lesson_key(row.lesson)
    base_filters: dict[str, Any] = {"grade": row.grade}
    if key:
        base_filters["lesson_key"] = key
    if material_filter:
        base_filters["material_type"] = material_filter

    attempts: list[tuple[str, dict[str, Any], str]] = []
    if row.question:
        attempts.append((row.question, dict(base_filters), "Top-1 từ SQLite FTS theo câu hỏi và metadata bài học."))
    if row.answer_sgv:
        attempts.append((row.answer_sgv, dict(base_filters), "Top-1 từ SQLite FTS theo đáp án SGV và metadata bài học."))
    if row.lesson:
        attempts.append((row.lesson, dict(base_filters), "Top-1 từ SQLite FTS theo tên bài học."))
    if material_filter:
        relaxed = {k: v for k, v in base_filters.items() if k != "material_type"}
        attempts.extend([(query, relaxed, reason + " Không ép loại sách.") for query, _, reason in list(attempts)])

    for query, filters, reason in attempts:
        try:
            results = search_learning_fragments(query=query, filters=filters, index_path=index_path, limit=1)
        except Exception:
            results = []
        if results:
            top = results[0]
            return {
                "evidence_fragment_id": str(top.get("fragment_id", "")),
                "evidence_material_type": str(top.get("material_type", "")),
                "evidence_lesson_title": str(top.get("lesson_title", "")),
                "evidence_page_start": str(top.get("page_start", "")),
                "evidence_source_markdown_path": str(top.get("source_markdown_path", "")),
                "evidence_status": str(top.get("status", "")),
                "evidence_match_reason": reason,
            }

    direct = _direct_lesson_lookup(row, material_filter, index_path=index_path)
    if direct:
        return direct
    return {
        "evidence_fragment_id": "",
        "evidence_material_type": "",
        "evidence_lesson_title": "",
        "evidence_page_start": "",
        "evidence_source_markdown_path": "",
        "evidence_status": "",
        "evidence_match_reason": "Không tìm thấy fragment học liệu phù hợp bằng truy xuất v0.",
    }


def consistency_flags(rows: Sequence[RawDialogueRow], *, index_path: Path = DEFAULT_INDEX_PATH) -> list[dict[str, str]]:
    """Create learning-resource consistency flags for audit rows.

    Args:
        rows: Normalized HNMU rows.
        index_path: SQLite learning-resource index path.

    Returns:
        One row per sample with evidence fields and conservative review flags.
    """

    output: list[dict[str, str]] = []
    for row in rows:
        evidence = best_learning_evidence(row, index_path=index_path)
        source_lesson = lesson_code(row.lesson)
        evidence_lesson = lesson_code(evidence.get("evidence_lesson_title", ""))
        issue_codes: list[str] = []
        needs_learning_resource_review = "false"
        if not evidence["evidence_fragment_id"]:
            issue_codes.append("NO_LEARNING_RESOURCE_EVIDENCE")
            needs_learning_resource_review = "true"
        if source_lesson and evidence_lesson and source_lesson != evidence_lesson:
            issue_codes.append("EVIDENCE_LESSON_MISMATCH")
            needs_learning_resource_review = "true"
        if row.position.upper().find("SGV") >= 0 and evidence.get("evidence_material_type") and evidence.get("evidence_material_type") != "SGV":
            issue_codes.append("EXPECTED_SGV_EVIDENCE_NOT_TOP_RESULT")
        output.append({
            "sample_id": row.sample_id,
            "grade": row.grade,
            "lesson": row.lesson,
            "position": row.position,
            **evidence,
            "needs_learning_resource_review": needs_learning_resource_review,
            "consistency_issue_codes": ";".join(issue_codes),
        })
    return output


def quality_rows(
    rows: Sequence[RawDialogueRow],
    issues: Sequence[dict[str, str]],
    consistency: Sequence[dict[str, str]],
    duplicates: Sequence[dict[str, str | float]],
) -> list[dict[str, str | float]]:
    """Score v0 audit quality for each sample.

    Args:
        rows: Normalized HNMU rows.
        issues: Missing-field and format issue rows.
        consistency: Learning-resource consistency rows.
        duplicates: Duplicate candidate rows.

    Returns:
        Rows for ``quality_check_results.csv``.
    """

    issue_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for issue in issues:
        issue_by_id[issue["sample_id"]].append(issue)
    consistency_by_id = {item["sample_id"]: item for item in consistency}
    duplicate_ids = {str(item["sample_id_a"]) for item in duplicates} | {str(item["sample_id_b"]) for item in duplicates}
    output: list[dict[str, str | float]] = []
    for row in rows:
        sample_issues = issue_by_id.get(row.sample_id, [])
        consistency_item = consistency_by_id.get(row.sample_id, {})
        score = 1.0
        failure_reasons: list[str] = []
        for issue in sample_issues:
            score -= 0.25 if issue.get("severity") == "high" else 0.12
            failure_reasons.append(issue.get("message", issue.get("issue_type", "issue")))
        if consistency_item.get("consistency_issue_codes"):
            score -= 0.18
            failure_reasons.append("Có cờ nhất quán học liệu: " + consistency_item["consistency_issue_codes"])
        if row.sample_id in duplicate_ids:
            score -= 0.12
            failure_reasons.append("Có ứng viên trùng/gần trùng.")
        score = max(0.0, min(1.0, round(score, 3)))
        has_high = any(issue.get("severity") == "high" for issue in sample_issues)
        if score < 0.5 or any(issue.get("field") in {"question", "dialogue"} for issue in sample_issues):
            decision = "failed"
            action = "exclude_from_current_batch"
        elif has_high or score < 0.8 or consistency_item.get("consistency_issue_codes") or row.sample_id in duplicate_ids:
            decision = "need_human_review"
            action = "ask_hnmu_review"
        else:
            decision = "pass"
            action = "keep"
        output.append({
            "sample_id": row.sample_id,
            "grade": row.grade,
            "lesson": row.lesson,
            "bloom_band": bloom_band(row.bloom_level),
            "quality_decision": decision,
            "confidence_score": score,
            "failure_reasons": "; ".join(failure_reasons),
            "suggested_reviewer_action": action,
            "needs_sgv_verification": "false",
            "needs_learning_resource_review": str(consistency_item.get("needs_learning_resource_review", "false")).lower(),
        })
    return output


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str] | None = None) -> None:
    """Write dictionaries to CSV with UTF-8 encoding.

    Args:
        path: Destination CSV path.
        rows: Rows to write.
        fieldnames: Optional explicit column order. If omitted, columns are
            inferred from the first row.

    Returns:
        None.
    """

    ensure_directory(path.parent)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def audit_batch(
    *,
    raw_dir: Path,
    output_dir: Path,
    include_grades: set[str] | None = None,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> dict[str, Any]:
    """Run Plan 04 deterministic audit for selected HNMU grades.

    Args:
        raw_dir: Folder containing HNMU raw ``.xlsx`` files.
        output_dir: Destination folder for audit CSV outputs.
        include_grades: Numeric grade strings to include. Defaults to ``{"6", "7"}``.
        index_path: SQLite learning-resource index path.

    Returns:
        Summary dictionary with counts and output paths.
    """

    include_grades = include_grades or {"6", "7"}
    source_files = sorted(raw_dir.glob("*.xlsx"))
    rows = load_dialogue_rows(source_files, include_grades=include_grades)
    issues = [issue for row in rows for issue in field_issues(row)]
    topic_lesson_map = load_topic_lesson_map()
    coverage = coverage_rows(rows, topic_lesson_map=topic_lesson_map)
    duplicates = duplicate_rows(rows)
    consistency = consistency_flags(rows, index_path=index_path)
    quality = quality_rows(rows, issues, consistency, duplicates)
    review_queue = [row for row in quality if row["quality_decision"] != "pass"]

    ensure_directory(output_dir)
    normalized_rows = [row.to_dict() for row in rows]
    write_csv(output_dir / "normalized_dialogue_rows.csv", normalized_rows)
    write_csv(output_dir / "coverage_summary.csv", coverage, ["dimension", "value", "grade", "grade_label", "topic_id", "topic_label", "lesson_id", "lesson_label", "registry_status", "count", "percentage"])
    write_csv(output_dir / "missing_field_report.csv", issues, ["sample_id", "issue_type", "field", "severity", "message"])
    write_csv(output_dir / "metadata_consistency_flags.csv", consistency)
    write_csv(output_dir / "duplicate_candidates.csv", duplicates)
    write_csv(output_dir / "quality_check_results.csv", quality)
    write_csv(output_dir / "hnmu_review_queue.csv", review_queue)

    decisions = Counter(str(row["quality_decision"]) for row in quality)
    topic_coverage = [
        {
            "value": str(row.get("value", "")),
            "topic_id": str(row.get("topic_id", "")),
            "registry_status": str(row.get("registry_status", "")),
            "count": row.get("count", 0),
            "percentage": row.get("percentage", 0),
        }
        for row in coverage
        if row.get("dimension") == "topic"
    ]
    return {
        "included_grades": sorted(include_grades),
        "source_files_seen": [path.as_posix() for path in source_files],
        "source_files_processed": sorted({row.source_file for row in rows}),
        "row_count": len(rows),
        "issue_count": len(issues),
        "duplicate_candidate_count": len(duplicates),
        "review_queue_count": len(review_queue),
        "quality_decisions": dict(decisions),
        "coverage_dimensions": sorted({str(row.get("dimension", "")) for row in coverage}),
        "topic_coverage": topic_coverage,
        "output_dir": output_dir.as_posix(),
    }


def write_audit_report(path: Path, summary: dict[str, Any]) -> None:
    """Write a Vietnamese Markdown report for a Plan 04 audit run.

    Args:
        path: Destination report path.
        summary: Summary dictionary returned by ``audit_batch``.

    Returns:
        None.
    """

    ensure_directory(path.parent)
    decisions = summary.get("quality_decisions", {})
    processed = "\n".join(f"- `{item}`" for item in summary.get("source_files_processed", [])) or "- Không có file nào"
    seen = "\n".join(f"- `{item}`" for item in summary.get("source_files_seen", [])) or "- Không có file nào"
    topic_lines = "\n".join(
        f"- {item.get('value')}: {item.get('count')} mẫu "
        f"({float(item.get('percentage', 0)):.2%}); mã chủ đề: `{item.get('topic_id') or 'unmapped'}`; "
        f"trạng thái registry: `{item.get('registry_status') or 'unmapped'}`."
        for item in summary.get("topic_coverage", [])
    ) or "- Chưa có thống kê chủ đề."
    grades = [str(item) for item in summary.get("included_grades", [])]
    grade_label = "–".join(grades) if grades else "không rõ"
    content = f"""# Báo cáo kiểm toán v0 dữ liệu hội thoại HNMU lớp {grade_label}

Trạng thái: `draft_audit` — kiểm toán cơ học và truy xuất học liệu v0, chưa thay thế HNMU/UET review.

## Phạm vi

- Lớp xử lý: {', '.join(grades) or 'Không rõ'}
- File raw nhìn thấy trong thư mục:
{seen}
- File đã xử lý trong vòng này:
{processed}

## Kết quả chính

- Số dòng hội thoại được đọc: {summary.get('row_count', 0)}
- Số issue thiếu trường/định dạng: {summary.get('issue_count', 0)}
- Số cặp trùng/gần trùng ứng viên: {summary.get('duplicate_candidate_count', 0)}
- Số mẫu trong hàng đợi review: {summary.get('review_queue_count', 0)}
- Phân bố quyết định chất lượng: {decisions}
- Các trục coverage đã xuất: {", ".join(summary.get('coverage_dimensions', []))}

## Diễn giải coverage theo SGK/SGV

Coverage theo chủ đề được ánh xạ qua `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`, tức theo mục lục SGK/SGV đã chuẩn hóa, không lấy dữ liệu thô HNMU làm nguồn chuẩn. Dữ liệu HNMU chỉ cung cấp mẫu cần kiểm toán; trường `Bài` trong dữ liệu thô được dùng để đối chiếu sang registry SGK/SGV.

Phân bố theo chủ đề:

{topic_lines}

Coverage theo bài học được ghi ở trục `lesson_by_grade`, vì bài học phụ thuộc vào từng lớp. Do đó các dòng bài học trong `coverage_summary.csv` luôn kèm `grade`, `grade_label`, `topic_id`, `topic_label`, `lesson_id` và `lesson_label`.

## Output

Các bảng audit nằm trong:

```text
{summary.get('output_dir')}
```

Bảng quan trọng nhất để xem độ phủ là `coverage_summary.csv`; bảng quan trọng nhất để xem trước khi chuyển sang Plan 06 là `quality_check_results.csv` và `hnmu_review_queue.csv`.

## Lưu ý diễn giải

- `pass` trong bản v0 chỉ có nghĩa là mẫu qua các kiểm tra cơ học và truy xuất sơ bộ; chưa phải xác nhận chuyên môn cuối cùng.
- Evidence học liệu hiện chủ yếu ở trạng thái `draft`; khi cần chắc chắn, xem cờ `needs_learning_resource_review`.
- Kiểm tra sâu về đúng/sai kiến thức, mức giàn giáo và tính sư phạm vẫn cần HNMU/UET xác nhận.
"""
    path.write_text(content, encoding="utf-8")

"""Deterministic census and sampling for Plan-03 task discovery."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from typing import Mapping, Sequence

CENSUS_COLUMNS = [
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "cognitive_band",
    "history_present",
    "history_turn_count",
    "history_depth_bin",
    "target_tutor_turn_index",
    "target_position_bin",
    "content_form_signal",
    "student_state_signal",
    "feature_method",
]

DISCOVERY_SAMPLE_COLUMNS = CENSUS_COLUMNS + [
    "selection_rank_within_grade",
    "selection_reason",
    "selection_seed",
]

DISCOVERY_CODING_INPUT_COLUMNS = DISCOVERY_SAMPLE_COLUMNS + [
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "gold_response",
    "gold_answer",
]

DISCOVERY_STRATA_COLUMNS = [
    "scope",
    "dimension",
    "value",
    "candidate_count",
    "family_count",
]

CONTENT_FORM_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "code_programming",
        (
            "lập trình",
            "chương trình máy tính",
            "scratch",
            "python",
            "câu lệnh",
            "vòng lặp",
            "biến ",
            "mã lệnh",
        ),
    ),
    (
        "algorithm",
        ("thuật toán", "tìm kiếm tuần tự", "tìm kiếm nhị phân", "sắp xếp"),
    ),
    (
        "spreadsheet",
        ("bảng tính", "trang tính", "excel", "hàm ", "công thức"),
    ),
    (
        "multimedia_presentation",
        (
            "video",
            "hình ảnh",
            "chỉnh sửa ảnh",
            "trang chiếu",
            "trình chiếu",
            "âm thanh",
            "tờ rơi",
        ),
    ),
    (
        "digital_ethics_safety",
        (
            "đạo đức",
            "pháp luật",
            "bản quyền",
            "an toàn",
            "mạng xã hội",
            "bắt nạt",
            "mã độc",
            "virus",
        ),
    ),
    (
        "hardware_network",
        (
            "thiết bị",
            "phần cứng",
            "mạng máy tính",
            "internet",
            "thiết bị vào",
            "thiết bị ra",
        ),
    ),
    (
        "data_information",
        ("thông tin", "dữ liệu", "dãy bit", " bit", "tệp", "thư mục"),
    ),
    (
        "digital_document_tool",
        ("soạn thảo", "văn bản", "định dạng", "phần mềm"),
    ),
]


def _ascii_fold(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def cognitive_band(value: str) -> str:
    """Normalize detailed HNMU labels to three coverage bands."""

    folded = _ascii_fold(value).strip()
    if folded.startswith(("nhan biet", "biet")):
        return "Biết"
    if folded.startswith(("thong hieu", "hieu")):
        return "Hiểu"
    if folded.startswith("van dung"):
        return "Vận dụng"
    return "Chưa xác định"


def history_depth_bin(turn_count: int) -> str:
    """Bin the nested history depth without inferring task semantics."""

    if turn_count == 0:
        return "0"
    if turn_count == 2:
        return "2"
    if turn_count <= 6:
        return "4-6"
    return "8+"


def target_position_bin(turn_index: int) -> str:
    """Bin the target tutor position."""

    if turn_index == 2:
        return "first_tutor_turn"
    if turn_index <= 6:
        return "early_followup"
    return "later_followup"


def content_form_signal(row: Mapping[str, str]) -> str:
    """Return a deterministic content-form signal for stratified sampling."""

    text = " ".join(
        [
            str(row.get("lesson", "")),
            str(row.get("student_prompt", "")),
            str(row.get("gold_answer", "")),
        ]
    ).lower()
    for label, patterns in CONTENT_FORM_PATTERNS:
        if any(pattern in text for pattern in patterns):
            return label
    return "concept_or_other"


def student_state_signal(history: Sequence[Mapping[str, object]]) -> str:
    """Extract observable lexical signals; this is not a semantic student-state label."""

    if not history:
        return "initial_request"
    student_turns = [
        str(item.get("content", "")).strip()
        for item in history
        if item.get("role") == "student"
    ]
    if not student_turns:
        return "history_without_student_reply"
    latest = student_turns[-1]
    folded = _ascii_fold(latest)
    signals: list[str] = ["student_reply_present"]
    if any(
        marker in folded
        for marker in ("khong hieu", "chua hieu", "khong biet", "bi roi", "kho qua")
    ):
        signals.append("explicit_uncertainty")
    if "?" in latest or any(
        folded.startswith(prefix)
        for prefix in ("tai sao", "vi sao", "the nao", "lam sao", "co phai")
    ):
        signals.append("student_question")
    if len(re.findall(r"\w+", latest, flags=re.UNICODE)) <= 5 and any(
        marker in folded for marker in ("da", "vang", "hieu roi", "dung", "ok")
    ):
        signals.append("short_confirmation")
    if len(signals) == 1:
        signals.append("attempt_or_answer")
    return ";".join(signals)


def build_candidate_feature_census(
    candidates: Sequence[Mapping[str, str]],
    traces: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Build a deterministic, non-semantic feature census for every candidate."""

    trace_by_id = {
        str(row["benchmark_candidate_id"]): row
        for row in traces
        if row.get("benchmark_candidate_id")
    }
    if len(trace_by_id) != len(traces):
        raise ValueError("Trace IDs must be unique and non-empty")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate_id = str(candidate.get("benchmark_candidate_id", "")).strip()
        if not candidate_id or candidate_id in seen:
            raise ValueError(f"Candidate ID is missing or duplicated: {candidate_id!r}")
        seen.add(candidate_id)
        trace = trace_by_id.get(candidate_id)
        if trace is None:
            raise ValueError(f"Missing trace for {candidate_id}")
        history = json.loads(str(candidate.get("conversation_history", "")))
        if not isinstance(history, list):
            raise ValueError(f"History is not a list for {candidate_id}")
        target_index = int(str(trace.get("target_tutor_turn_index", "0")))
        rows.append(
            {
                "benchmark_candidate_id": candidate_id,
                "sample_id": str(candidate.get("sample_id", "")),
                "grade": str(candidate.get("grade", "")),
                "lesson": str(candidate.get("lesson", "")),
                "position": str(candidate.get("position", "")),
                "cognitive_band": cognitive_band(
                    str(candidate.get("bloom_level", ""))
                ),
                "history_present": "true" if history else "false",
                "history_turn_count": str(len(history)),
                "history_depth_bin": history_depth_bin(len(history)),
                "target_tutor_turn_index": str(target_index),
                "target_position_bin": target_position_bin(target_index),
                "content_form_signal": content_form_signal(candidate),
                "student_state_signal": student_state_signal(history),
                "feature_method": "deterministic_regex_v1",
            }
        )
    if set(trace_by_id) != seen:
        raise ValueError("Candidate/trace ID sets differ")
    return sorted(rows, key=lambda row: row["benchmark_candidate_id"])


def _stable_tiebreak(seed: str, candidate_id: str) -> str:
    return hashlib.sha256(f"{seed}:{candidate_id}".encode("utf-8")).hexdigest()


def select_task_discovery_sample(
    census: Sequence[Mapping[str, str]],
    *,
    per_grade: int = 40,
    seed: str = "plan03-task-discovery-v1",
) -> list[dict[str, str]]:
    """Select a deterministic, family-diverse, coverage-seeking discovery sample."""

    if per_grade <= 0:
        raise ValueError("per_grade must be positive")
    selected: list[dict[str, str]] = []
    feature_fields = [
        "cognitive_band",
        "history_present",
        "history_depth_bin",
        "target_position_bin",
        "content_form_signal",
        "student_state_signal",
    ]
    for grade in ("6", "7", "8", "9"):
        pool = [dict(row) for row in census if str(row.get("grade")) == grade]
        families = {row["sample_id"] for row in pool}
        if len(families) < per_grade:
            raise ValueError(
                f"Grade {grade} has only {len(families)} families for {per_grade} rows"
            )
        frequency = {
            field: Counter(row[field] for row in pool) for field in feature_fields
        }
        depth_values = sorted({row["history_depth_bin"] for row in pool})
        base_depth_target = per_grade // len(depth_values)
        depth_targets = {
            value: min(
                base_depth_target,
                len({row["sample_id"] for row in pool if row["history_depth_bin"] == value}),
            )
            for value in depth_values
        }
        remaining_depth_slots = per_grade - sum(depth_targets.values())
        for value in depth_values:
            if remaining_depth_slots <= 0:
                break
            available_families = len(
                {row["sample_id"] for row in pool if row["history_depth_bin"] == value}
            )
            room = available_families - depth_targets[value]
            addition = min(room, remaining_depth_slots)
            depth_targets[value] += addition
            remaining_depth_slots -= addition
        covered: set[tuple[str, str]] = set()
        depth_counts: Counter[str] = Counter()
        selected_feature_counts = {
            field: Counter() for field in feature_fields
        }
        used_families: set[str] = set()
        chosen: list[dict[str, str]] = []
        while len(chosen) < per_grade:
            eligible = [
                row for row in pool if row["sample_id"] not in used_families
            ]
            if not eligible:
                raise ValueError(f"Unable to complete grade {grade} sample")

            def score(row: Mapping[str, str]) -> tuple[float, str]:
                novelty = sum(
                    (field, row[field]) not in covered for field in feature_fields
                )
                rarity = sum(
                    1.0 / frequency[field][row[field]]
                    for field in feature_fields
                    if (field, row[field]) not in covered
                )
                representativeness = sum(
                    max(
                        0.0,
                        (
                            frequency[field][row[field]] / len(pool)
                            - selected_feature_counts[field][row[field]]
                            / per_grade
                        ),
                    )
                    for field in feature_fields
                )
                depth_quota_bonus = (
                    1000.0
                    if depth_counts[row["history_depth_bin"]]
                    < depth_targets[row["history_depth_bin"]]
                    else 0.0
                )
                return (
                    depth_quota_bonus
                    + novelty * 100.0
                    + rarity
                    + representativeness * 10.0,
                    _stable_tiebreak(seed, row["benchmark_candidate_id"]),
                )

            best = max(eligible, key=score)
            novel = [
                f"{field}={best[field]}"
                for field in feature_fields
                if (field, best[field]) not in covered
            ]
            chosen_row = dict(best)
            chosen_row.update(
                {
                    "selection_rank_within_grade": str(len(chosen) + 1),
                    "selection_reason": (
                        f"history_depth_quota={best['history_depth_bin']};new:"
                        + "|".join(novel)
                        if novel
                        else (
                            f"history_depth_quota={best['history_depth_bin']};"
                            "rare_stratum_and_family_diversity"
                        )
                    ),
                    "selection_seed": seed,
                }
            )
            chosen.append(chosen_row)
            used_families.add(best["sample_id"])
            depth_counts[best["history_depth_bin"]] += 1
            for field in feature_fields:
                selected_feature_counts[field][best[field]] += 1
            covered.update((field, best[field]) for field in feature_fields)
        selected.extend(chosen)
    return selected


def enrich_discovery_sample(
    sample: Sequence[Mapping[str, str]],
    candidates: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Join selected routing rows to the content needed for semantic coding."""

    candidate_by_id = {
        str(row.get("benchmark_candidate_id", "")).strip(): row
        for row in candidates
        if str(row.get("benchmark_candidate_id", "")).strip()
    }
    if len(candidate_by_id) != len(candidates):
        raise ValueError("Candidate IDs must be unique and non-empty")
    enriched: list[dict[str, str]] = []
    for row in sample:
        candidate_id = str(row.get("benchmark_candidate_id", "")).strip()
        candidate = candidate_by_id.get(candidate_id)
        if candidate is None:
            raise ValueError(f"Missing candidate content for {candidate_id}")
        joined = dict(row)
        for field in (
            "bloom_level",
            "student_prompt",
            "conversation_history",
            "gold_response",
            "gold_answer",
        ):
            joined[field] = str(candidate.get(field, ""))
        enriched.append(joined)
    return enriched


def summarize_discovery_strata(
    census: Sequence[Mapping[str, str]],
    sample: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Summarize full-pool and selected-sample coverage without semantic claims."""

    dimensions = (
        "grade",
        "cognitive_band",
        "history_present",
        "history_depth_bin",
        "target_position_bin",
        "content_form_signal",
        "student_state_signal",
    )
    rows: list[dict[str, str]] = []
    for scope, source in (("full_pool", census), ("discovery_sample", sample)):
        for dimension in dimensions:
            values = sorted({str(row.get(dimension, "")) for row in source})
            for value in values:
                matching = [
                    row for row in source if str(row.get(dimension, "")) == value
                ]
                rows.append(
                    {
                        "scope": scope,
                        "dimension": dimension,
                        "value": value,
                        "candidate_count": str(len(matching)),
                        "family_count": str(
                            len({str(row.get("sample_id", "")) for row in matching})
                        ),
                    }
                )
    return rows

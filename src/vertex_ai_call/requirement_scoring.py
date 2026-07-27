"""Deterministic helpers for pedagogical-principle requirement scoring."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PRINCIPLE_IDS: tuple[str, ...] = (
    "PRINCIPLE-CHALLENGE",
    "PRINCIPLE-EXPLANATION",
    "PRINCIPLE-MODELLING",
    "PRINCIPLE-PRACTICE",
    "PRINCIPLE-FEEDBACK",
    "PRINCIPLE-QUESTIONING",
)

GROUNDING_HEADER: tuple[str, ...] = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "source_question",
    "gold_answer",
)

MODEL_GROUNDING_FIELDS: tuple[str, ...] = (
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "source_question",
    "gold_answer",
)

PILOT_HEADER: tuple[str, ...] = GROUNDING_HEADER + (
    "has_history",
    "history_turn_count",
    "selection_reason",
)

CALIBRATION_METADATA_FIELDS: tuple[str, ...] = (
    "focus_principle_id",
    "case_type",
    "expected_score_min",
    "expected_score_max",
    "case_origin",
    "source_candidate_id",
    "boundary_rationale",
    "uet_status",
)

CALIBRATION_HEADER: tuple[str, ...] = (
    GROUNDING_HEADER + CALIBRATION_METADATA_FIELDS
)

REVIEW_HEADER: tuple[str, ...] = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "review_reasons",
    "run_a_required_principles",
    "run_b_required_principles",
    "score_differences",
    "run_a_principle_scores_json",
    "run_b_principle_scores_json",
    "uet_disposition",
    "uet_notes",
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "within_one_rate_min": 0.95,
    "required_exact_agreement_min": 0.90,
    "required_jaccard_mean_min": 0.90,
    "principle_f1_min": 0.90,
    "no_threshold_crossing_rate_min": 0.95,
}


class RequirementScoringError(ValueError):
    """Raised when an input, response, or run bundle violates the contract."""


@dataclass(frozen=True)
class GenerationConfig:
    """Registered generation configuration used by both pilot runs."""

    model: str
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 4096
    seed: int = 20260727
    thinking_budget: int = 0
    timeout_seconds: float = 120.0
    max_retries: int = 3
    max_requests: int = 80
    concurrency: int = 8
    retry_base_delay_seconds: float = 2.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_output_tokens": self.max_output_tokens,
            "seed": self.seed,
            "thinking_budget": self.thinking_budget,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "max_requests": self.max_requests,
            "concurrency": self.concurrency,
            "retry_base_delay_seconds": self.retry_base_delay_seconds,
        }

    def request_dict(self) -> dict[str, Any]:
        """Return only values that can change one model response."""

        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_output_tokens": self.max_output_tokens,
            "seed": self.seed,
            "thinking_budget": self.thinking_budget,
        }


def utc_now() -> str:
    """Return an RFC-3339 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_json_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _stable_key(seed: int, value: str) -> str:
    return sha256_bytes(f"{seed}:{value}".encode("utf-8"))


def _parse_history(raw: Any, *, candidate_id: str) -> list[dict[str, Any]]:
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RequirementScoringError(
                f"{candidate_id}: conversation_history is not valid JSON"
            ) from exc
    elif isinstance(raw, list):
        parsed = raw
    else:
        raise RequirementScoringError(
            f"{candidate_id}: conversation_history must be JSON text or a list"
        )
    if not isinstance(parsed, list):
        raise RequirementScoringError(
            f"{candidate_id}: conversation_history must decode to a list"
        )
    result: list[dict[str, Any]] = []
    previous_index = 1
    for position, turn in enumerate(parsed):
        if not isinstance(turn, dict):
            raise RequirementScoringError(
                f"{candidate_id}: history turn {position} is not an object"
            )
        if set(turn) != {"turn_index", "role", "content"}:
            raise RequirementScoringError(
                f"{candidate_id}: history turn {position} has unexpected fields"
            )
        index = turn["turn_index"]
        role = turn["role"]
        content = turn["content"]
        if not isinstance(index, int) or index <= previous_index:
            raise RequirementScoringError(
                f"{candidate_id}: history turn indices are not strictly increasing"
            )
        if role not in {"student", "tutor"}:
            raise RequirementScoringError(
                f"{candidate_id}: unsupported history role {role!r}"
            )
        if not isinstance(content, str) or not content.strip():
            raise RequirementScoringError(
                f"{candidate_id}: history turn {index} has empty content"
            )
        result.append(
            {"turn_index": index, "role": role, "content": content.strip()}
        )
        previous_index = index
    return result


def normalize_grounding_row(row: Mapping[str, Any]) -> dict[str, Any]:
    if set(row) != set(GROUNDING_HEADER):
        missing = sorted(set(GROUNDING_HEADER) - set(row))
        extra = sorted(set(row) - set(GROUNDING_HEADER))
        raise RequirementScoringError(
            f"Grounding row schema mismatch; missing={missing}, extra={extra}"
        )
    candidate_id = str(row["benchmark_candidate_id"]).strip()
    if not candidate_id:
        raise RequirementScoringError("benchmark_candidate_id is empty")
    try:
        grade = int(str(row["grade"]).strip())
    except ValueError as exc:
        raise RequirementScoringError(f"{candidate_id}: grade is not an integer") from exc
    if grade not in {6, 7, 8, 9}:
        raise RequirementScoringError(f"{candidate_id}: grade must be 6-9")
    normalized = {
        "benchmark_candidate_id": candidate_id,
        "sample_id": str(row["sample_id"]).strip(),
        "grade": grade,
        "lesson": str(row["lesson"]).strip(),
        "position": str(row["position"]).strip(),
        "bloom_level": str(row["bloom_level"]).strip(),
        "student_prompt": str(row["student_prompt"]).strip(),
        "conversation_history": _parse_history(
            row["conversation_history"], candidate_id=candidate_id
        ),
        "source_question": str(row["source_question"]).strip(),
        "gold_answer": str(row["gold_answer"]).strip(),
    }
    for required in (
        "sample_id",
        "student_prompt",
        "gold_answer",
    ):
        if not normalized[required]:
            raise RequirementScoringError(f"{candidate_id}: {required} is empty")
    return normalized


def load_grounding_pool(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != GROUNDING_HEADER:
            raise RequirementScoringError(
                "Grounding CSV header mismatch: "
                f"expected={list(GROUNDING_HEADER)}, actual={reader.fieldnames}"
            )
        rows = [normalize_grounding_row(row) for row in reader]
    if not rows:
        raise RequirementScoringError("Grounding pool is empty")
    candidate_ids = [row["benchmark_candidate_id"] for row in rows]
    duplicates = sorted(
        candidate_id
        for candidate_id, count in Counter(candidate_ids).items()
        if count > 1
    )
    if duplicates:
        raise RequirementScoringError(
            f"Duplicate benchmark_candidate_id values: {duplicates[:5]}"
        )
    return rows


def _select_diverse(
    candidates: Sequence[dict[str, Any]],
    *,
    amount: int,
    seed: int,
    used_families: set[str],
    bloom_counts: Counter[str],
    lesson_counts: Counter[str],
) -> list[dict[str, Any]]:
    available = [
        row for row in candidates if row["sample_id"] not in used_families
    ]
    selected: list[dict[str, Any]] = []
    while available and len(selected) < amount:
        available.sort(
            key=lambda row: (
                bloom_counts[row["bloom_level"]],
                lesson_counts[row["lesson"]],
                _stable_key(seed, row["benchmark_candidate_id"]),
            )
        )
        chosen = available.pop(0)
        selected.append(chosen)
        used_families.add(chosen["sample_id"])
        bloom_counts[chosen["bloom_level"]] += 1
        lesson_counts[chosen["lesson"]] += 1
        available = [
            row for row in available if row["sample_id"] not in used_families
        ]
    return selected


def select_pilot(
    rows: Sequence[dict[str, Any]],
    *,
    per_grade: int = 10,
    seed: int = 20260727,
) -> list[dict[str, Any]]:
    """Select one candidate from each family, balancing grade and history."""

    if per_grade < 2:
        raise RequirementScoringError("per_grade must be at least 2")
    selected_all: list[dict[str, Any]] = []
    no_history_target = per_grade // 2
    for grade in (6, 7, 8, 9):
        grade_rows = [row for row in rows if row["grade"] == grade]
        if len({row["sample_id"] for row in grade_rows}) < per_grade:
            raise RequirementScoringError(
                f"Grade {grade} has fewer than {per_grade} candidate families"
            )
        used_families: set[str] = set()
        bloom_counts: Counter[str] = Counter()
        lesson_counts: Counter[str] = Counter()
        no_history = [row for row in grade_rows if not row["conversation_history"]]
        with_history = [row for row in grade_rows if row["conversation_history"]]
        selected = _select_diverse(
            no_history,
            amount=no_history_target,
            seed=seed + grade,
            used_families=used_families,
            bloom_counts=bloom_counts,
            lesson_counts=lesson_counts,
        )
        selected += _select_diverse(
            with_history,
            amount=per_grade - len(selected),
            seed=seed + grade * 11,
            used_families=used_families,
            bloom_counts=bloom_counts,
            lesson_counts=lesson_counts,
        )
        if len(selected) < per_grade:
            selected += _select_diverse(
                grade_rows,
                amount=per_grade - len(selected),
                seed=seed + grade * 101,
                used_families=used_families,
                bloom_counts=bloom_counts,
                lesson_counts=lesson_counts,
            )
        if len(selected) != per_grade:
            raise RequirementScoringError(
                f"Could not select {per_grade} candidates for grade {grade}"
            )
        for row in selected:
            enriched = dict(row)
            enriched["has_history"] = bool(row["conversation_history"])
            enriched["history_turn_count"] = len(row["conversation_history"])
            enriched["selection_reason"] = (
                f"grade={grade};history={'yes' if row['conversation_history'] else 'no'};"
                "diversified_by=bloom,lesson;family_unique=yes"
            )
            selected_all.append(enriched)
    selected_all.sort(
        key=lambda row: (
            row["grade"],
            _stable_key(seed, row["benchmark_candidate_id"]),
        )
    )
    if len(selected_all) != per_grade * 4:
        raise RequirementScoringError("Pilot size invariant failed")
    if len({row["sample_id"] for row in selected_all}) != len(selected_all):
        raise RequirementScoringError("Pilot contains duplicate sample families")
    return selected_all


def _serialize_pilot_row(row: Mapping[str, Any]) -> dict[str, Any]:
    serialized = dict(row)
    serialized["conversation_history"] = json.dumps(
        row["conversation_history"], ensure_ascii=False, separators=(",", ":")
    )
    serialized["has_history"] = "true" if row["has_history"] else "false"
    return serialized


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle_fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(
        path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def write_pilot_input(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle_fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(
            handle_fd, "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=PILOT_HEADER)
            writer.writeheader()
            for row in rows:
                writer.writerow(_serialize_pilot_row(row))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def load_pilot_input(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PILOT_HEADER:
            raise RequirementScoringError("Pilot CSV header mismatch")
        rows: list[dict[str, Any]] = []
        for raw in reader:
            grounding = normalize_grounding_row(
                {field: raw[field] for field in GROUNDING_HEADER}
            )
            grounding["has_history"] = raw["has_history"].lower() == "true"
            grounding["history_turn_count"] = int(raw["history_turn_count"])
            grounding["selection_reason"] = raw["selection_reason"]
            if grounding["has_history"] != bool(grounding["conversation_history"]):
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: has_history mismatch"
                )
            rows.append(grounding)
    if len(rows) != 40:
        raise RequirementScoringError(f"Pilot must contain 40 rows, found {len(rows)}")
    if Counter(row["grade"] for row in rows) != Counter({6: 10, 7: 10, 8: 10, 9: 10}):
        raise RequirementScoringError("Pilot must contain 10 rows per grade")
    if len({row["sample_id"] for row in rows}) != 40:
        raise RequirementScoringError("Pilot must contain 40 unique families")
    return rows


def load_calibration_cases(path: Path) -> list[dict[str, Any]]:
    """Load the fixed semantic-boundary calibration set."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != CALIBRATION_HEADER:
            raise RequirementScoringError("Calibration CSV header mismatch")
        rows: list[dict[str, Any]] = []
        for raw in reader:
            grounding = normalize_grounding_row(
                {field: raw[field] for field in GROUNDING_HEADER}
            )
            principle_id = raw["focus_principle_id"].strip()
            case_type = raw["case_type"].strip()
            try:
                expected_min = int(raw["expected_score_min"])
                expected_max = int(raw["expected_score_max"])
            except ValueError as exc:
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: invalid expected range"
                ) from exc
            if principle_id not in PRINCIPLE_IDS:
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: invalid focus principle"
                )
            if case_type not in {"positive", "near_miss"}:
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: invalid case_type"
                )
            if not 1 <= expected_min <= expected_max <= 5:
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: expected range must be 1-5"
                )
            if case_type == "positive" and expected_min < 4:
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: positive must require >=4"
                )
            if case_type == "near_miss" and expected_max > 3:
                raise RequirementScoringError(
                    f"{grounding['benchmark_candidate_id']}: near_miss must cap at 3"
                )
            metadata = {
                field: raw[field].strip() for field in CALIBRATION_METADATA_FIELDS
            }
            metadata["expected_score_min"] = expected_min
            metadata["expected_score_max"] = expected_max
            grounding.update(metadata)
            rows.append(grounding)
    if len(rows) != 36:
        raise RequirementScoringError(
            f"Calibration must contain 36 rows, found {len(rows)}"
        )
    if len({row["benchmark_candidate_id"] for row in rows}) != len(rows):
        raise RequirementScoringError("Calibration case IDs must be unique")
    expected_balance = {
        (principle, case_type): 3
        for principle in PRINCIPLE_IDS
        for case_type in ("positive", "near_miss")
    }
    actual_balance = Counter(
        (row["focus_principle_id"], row["case_type"]) for row in rows
    )
    if actual_balance != Counter(expected_balance):
        raise RequirementScoringError(
            "Calibration must contain three positive and three near-miss "
            "cases per principle"
        )
    return rows


def build_grounding_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    """Build the semantic payload sent to the model.

    Candidate and sample identifiers remain orchestration metadata. They
    are intentionally excluded because they add no evidence for semantic
    requirement scoring.
    """

    return {field: row[field] for field in MODEL_GROUNDING_FIELDS}


def serialize_user_prompt(payload: Mapping[str, Any]) -> str:
    """Serialize the exact user prompt sent to Vertex AI."""

    if tuple(payload) != MODEL_GROUNDING_FIELDS:
        raise RequirementScoringError(
            "Model grounding payload fields or order do not match the contract"
        )
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def build_request_hash(
    *,
    payload: Mapping[str, Any],
    prompt_sha256: str,
    schema_sha256: str,
    generation_config: GenerationConfig,
) -> str:
    return canonical_json_hash(
        {
            "payload": payload,
            "prompt_sha256": prompt_sha256,
            "schema_sha256": schema_sha256,
            "generation_config": generation_config.request_dict(),
        }
    )


def parse_and_validate_response(
    raw_response_text: str,
    *,
    expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_response_text)
    except json.JSONDecodeError as exc:
        raise RequirementScoringError("Model response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise RequirementScoringError("Model response must be a JSON object")
    if set(parsed) != {"principle_scores"}:
        raise RequirementScoringError("Model response has unexpected top-level fields")
    return _normalize_response(
        parsed["principle_scores"],
        expected_candidate_id=expected_candidate_id,
    )


def _normalize_response(
    scores: Any,
    *,
    expected_candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(scores, list) or len(scores) != 6:
        raise RequirementScoringError("principle_scores must contain exactly six rows")
    normalized_scores: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in scores:
        if not isinstance(item, dict) or set(item) != {
            "principle_id",
            "requirement_score",
            "rationale",
            "evidence",
        }:
            raise RequirementScoringError("A principle score has unexpected fields")
        principle_id = item["principle_id"]
        score = item["requirement_score"]
        rationale = item["rationale"]
        evidence = item["evidence"]
        if principle_id not in PRINCIPLE_IDS or principle_id in seen:
            raise RequirementScoringError(
                f"Invalid or duplicate principle_id: {principle_id!r}"
            )
        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
            raise RequirementScoringError(
                f"{principle_id}: requirement_score must be an integer from 1 to 5"
            )
        if not isinstance(rationale, str) or not rationale.strip():
            raise RequirementScoringError(f"{principle_id}: rationale is empty")
        if not isinstance(evidence, str) or not evidence.strip():
            raise RequirementScoringError(f"{principle_id}: evidence is empty")
        seen.add(principle_id)
        normalized_scores.append(
            {
                "principle_id": principle_id,
                "requirement_score": score,
                "rationale": rationale.strip(),
                "evidence": evidence.strip(),
            }
        )
    if seen != set(PRINCIPLE_IDS):
        raise RequirementScoringError("Model response does not cover all six principles")
    normalized_scores.sort(key=lambda item: PRINCIPLE_IDS.index(item["principle_id"]))
    return {
        "benchmark_candidate_id": expected_candidate_id,
        "principle_scores": normalized_scores,
    }


def validate_normalized_response(
    response: Mapping[str, Any],
    *,
    expected_candidate_id: str,
) -> dict[str, Any]:
    """Validate the response after code has joined its candidate ID."""

    if set(response) != {"benchmark_candidate_id", "principle_scores"}:
        raise RequirementScoringError(
            "Normalized response has unexpected top-level fields"
        )
    if response["benchmark_candidate_id"] != expected_candidate_id:
        raise RequirementScoringError(
            "Normalized response benchmark_candidate_id does not match the record"
        )
    return _normalize_response(
        response["principle_scores"],
        expected_candidate_id=expected_candidate_id,
    )


def score_map(response: Mapping[str, Any]) -> dict[str, int]:
    return {
        item["principle_id"]: int(item["requirement_score"])
        for item in response["principle_scores"]
    }


def derive_principle_sets(response: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    scores = score_map(response)
    required = [principle for principle in PRINCIPLE_IDS if scores[principle] >= 4]
    alternative = [principle for principle in PRINCIPLE_IDS if scores[principle] == 3]
    return required, alternative


_HIGH_SCORE_MODAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?:việc\s+)?(?:đặt câu hỏi|làm mẫu|phản hồi|luyện tập|giải thích)"
        r"[^.!?]{0,100}(?:có thể|có khả năng|sẽ hữu ích)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:không bắt buộc|không phải (?:là )?(?:chức năng )?cốt lõi|"
        r"chiến lược thay thế|một lựa chọn)",
        re.IGNORECASE,
    ),
)

_FEEDBACK_CONFIRMATION_TERMS: tuple[str, ...] = (
    "xác nhận",
    "khen",
    "khuyến khích",
    "tự tin",
)

_FEEDBACK_IMPROVEMENT_TERMS: tuple[str, ...] = (
    "sai",
    "thiếu",
    "điều chỉnh",
    "sửa",
    "cải thiện",
    "bổ sung",
    "phần đúng",
    "bước tiếp theo",
    "dẫn dắt",
    "khắc phục",
)

_QUESTIONING_OPTIONAL_TERMS: tuple[str, ...] = (
    "sau khi giải thích",
    "kiểm tra xem",
    "kiểm tra mức độ hiểu",
    "có thể giúp",
    "khuyến khích học sinh suy nghĩ thêm",
)

_QUESTIONING_DEPENDENCY_TERMS: tuple[str, ...] = (
    "thiếu thông tin",
    "chưa rõ",
    "cần học sinh trả lời",
    "không thể xác định",
    "mở khóa",
    "bước tiếp theo",
    "tự suy luận",
    "tự nhớ lại",
    "tự lựa chọn",
    "tự thực hiện",
)


def lint_principle_scores(response: Mapping[str, Any]) -> list[str]:
    """Return deterministic semantic-risk reasons without changing scores."""

    reasons: list[str] = []
    for item in response["principle_scores"]:
        principle_id = str(item["principle_id"])
        score = int(item["requirement_score"])
        rationale = str(item["rationale"]).casefold()
        if score < 4:
            continue
        if "nhu cầu độc lập:" not in rationale:
            reasons.append(f"high_score_missing_need:{principle_id}")
        if "nếu bỏ nguyên tắc này:" not in rationale:
            reasons.append(f"high_score_missing_counterfactual:{principle_id}")
        if any(pattern.search(rationale) for pattern in _HIGH_SCORE_MODAL_PATTERNS):
            reasons.append(f"high_score_modal_conflict:{principle_id}")
        if principle_id == "PRINCIPLE-FEEDBACK":
            has_confirmation = any(
                term in rationale for term in _FEEDBACK_CONFIRMATION_TERMS
            )
            has_improvement = any(
                term in rationale for term in _FEEDBACK_IMPROVEMENT_TERMS
            )
            if has_confirmation and not has_improvement:
                reasons.append("feedback_confirmation_only")
        if principle_id == "PRINCIPLE-QUESTIONING":
            looks_optional = any(
                term in rationale for term in _QUESTIONING_OPTIONAL_TERMS
            )
            has_dependency = any(
                term in rationale for term in _QUESTIONING_DEPENDENCY_TERMS
            )
            if looks_optional and not has_dependency:
                reasons.append("questioning_without_answer_dependency")
    return sorted(set(reasons))


def load_run_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise RequirementScoringError(f"Run file does not exist: {path}")
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RequirementScoringError(
                    f"{path}:{line_number}: invalid JSONL"
                ) from exc
            records.append(record)
    return records


def validate_run_records(
    records: Sequence[Mapping[str, Any]],
    pilot_rows: Sequence[Mapping[str, Any]],
    *,
    run_id: str,
) -> dict[str, dict[str, Any]]:
    expected = {row["benchmark_candidate_id"] for row in pilot_rows}
    source_by_id = {
        str(row["benchmark_candidate_id"]): row for row in pilot_rows
    }
    mapped: dict[str, dict[str, Any]] = {}
    for record in records:
        required_fields = {
            "run_id",
            "benchmark_candidate_id",
            "request_hash",
            "user_prompt",
            "model",
            "model_version",
            "response_id",
            "finish_reason",
            "usage_metadata",
            "raw_response_text",
            "normalized_response",
            "required_principle_set",
            "alternative_principle_set",
            "created_at",
        }
        if set(record) != required_fields:
            raise RequirementScoringError("Run record fields do not match the contract")
        if record["run_id"] != run_id:
            raise RequirementScoringError("Run record has the wrong run_id")
        candidate_id = record["benchmark_candidate_id"]
        if candidate_id in mapped:
            raise RequirementScoringError(f"Duplicate run record: {candidate_id}")
        if str(candidate_id) not in source_by_id:
            raise RequirementScoringError(
                f"Unexpected run record candidate: {candidate_id}"
            )
        expected_user_prompt = serialize_user_prompt(
            build_grounding_payload(source_by_id[str(candidate_id)])
        )
        if record["user_prompt"] != expected_user_prompt:
            raise RequirementScoringError(
                f"{candidate_id}: stored user prompt does not match pilot input"
            )
        normalized = validate_normalized_response(
            record["normalized_response"],
            expected_candidate_id=candidate_id,
        )
        required, alternative = derive_principle_sets(normalized)
        if record["required_principle_set"] != required:
            raise RequirementScoringError(f"{candidate_id}: required set mismatch")
        if record["alternative_principle_set"] != alternative:
            raise RequirementScoringError(f"{candidate_id}: alternative set mismatch")
        mapped[candidate_id] = dict(record)
    if set(mapped) != expected:
        missing = sorted(expected - set(mapped))
        extra = sorted(set(mapped) - expected)
        raise RequirementScoringError(
            f"Run {run_id} coverage mismatch; missing={missing[:5]}, extra={extra[:5]}"
        )
    return mapped


def _weighted_kappa(left: Sequence[int], right: Sequence[int]) -> float | None:
    if len(left) != len(right) or not left:
        return None
    categories = (1, 2, 3, 4, 5)
    matrix = {(a, b): 0 for a in categories for b in categories}
    for a, b in zip(left, right):
        matrix[(a, b)] += 1
    left_counts = Counter(left)
    right_counts = Counter(right)
    total = len(left)
    observed = 0.0
    expected = 0.0
    for a in categories:
        for b in categories:
            weight = ((a - b) / (len(categories) - 1)) ** 2
            observed += weight * matrix[(a, b)] / total
            expected += weight * (left_counts[a] * right_counts[b]) / (total * total)
    if expected == 0:
        return 1.0 if observed == 0 else None
    return 1.0 - observed / expected


def _binary_f1(left: Sequence[bool], right: Sequence[bool]) -> float | None:
    true_positive = sum(a and b for a, b in zip(left, right))
    false_positive = sum((not a) and b for a, b in zip(left, right))
    false_negative = sum(a and (not b) for a, b in zip(left, right))
    denominator = 2 * true_positive + false_positive + false_negative
    return None if denominator == 0 else 2 * true_positive / denominator


def compare_runs(
    run_a: Mapping[str, Mapping[str, Any]],
    run_b: Mapping[str, Mapping[str, Any]],
    pilot_rows: Sequence[Mapping[str, Any]],
    *,
    spot_check_count: int = 4,
    seed: int = 20260727,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if set(run_a) != set(run_b):
        raise RequirementScoringError("Run A and B candidate IDs do not match")
    row_by_id = {row["benchmark_candidate_id"]: row for row in pilot_rows}
    exact_scores = 0
    within_one = 0
    score_count = 0
    exact_required = 0
    jaccard_values: list[float] = []
    crossing_candidates = 0
    semantic_lint_candidates = 0
    per_principle_left: dict[str, list[int]] = {
        principle: [] for principle in PRINCIPLE_IDS
    }
    per_principle_right: dict[str, list[int]] = {
        principle: [] for principle in PRINCIPLE_IDS
    }
    score_distribution_a: Counter[str] = Counter()
    score_distribution_b: Counter[str] = Counter()
    review_rows: list[dict[str, str]] = []
    agreements: list[str] = []

    for candidate_id in sorted(run_a):
        source = row_by_id[candidate_id]
        response_a = run_a[candidate_id]["normalized_response"]
        response_b = run_b[candidate_id]["normalized_response"]
        scores_a = score_map(response_a)
        scores_b = score_map(response_b)
        required_a = set(run_a[candidate_id]["required_principle_set"])
        required_b = set(run_b[candidate_id]["required_principle_set"])
        reasons: list[str] = []
        differences: dict[str, int] = {}
        has_crossing = False
        for principle in PRINCIPLE_IDS:
            left = scores_a[principle]
            right = scores_b[principle]
            per_principle_left[principle].append(left)
            per_principle_right[principle].append(right)
            score_distribution_a[f"{principle}:{left}"] += 1
            score_distribution_b[f"{principle}:{right}"] += 1
            score_count += 1
            exact_scores += left == right
            within_one += abs(left - right) <= 1
            if left != right:
                differences[principle] = right - left
            if abs(left - right) >= 2:
                reasons.append(f"score_gap_ge_2:{principle}")
            if (left >= 4) != (right >= 4):
                has_crossing = True
                reasons.append(f"threshold_crossing:{principle}")
        if has_crossing:
            crossing_candidates += 1
        if required_a == required_b:
            exact_required += 1
        union = required_a | required_b
        jaccard_values.append(1.0 if not union else len(required_a & required_b) / len(union))
        if not required_a or not required_b:
            reasons.append("empty_required_set")
        if len(required_a) > 3 or len(required_b) > 3:
            reasons.append("more_than_three_required")
        lint_a = lint_principle_scores(response_a)
        lint_b = lint_principle_scores(response_b)
        if lint_a or lint_b:
            semantic_lint_candidates += 1
            reasons.extend(f"run_a:{reason}" for reason in lint_a)
            reasons.extend(f"run_b:{reason}" for reason in lint_b)
        if "focus_principle_id" in source:
            focus = str(source["focus_principle_id"])
            expected_min = int(source["expected_score_min"])
            expected_max = int(source["expected_score_max"])
            if not expected_min <= scores_a[focus] <= expected_max:
                reasons.append(f"calibration_out_of_range_a:{focus}")
            if not expected_min <= scores_b[focus] <= expected_max:
                reasons.append(f"calibration_out_of_range_b:{focus}")
        if reasons:
            review_rows.append(
                {
                    "benchmark_candidate_id": candidate_id,
                    "sample_id": str(source["sample_id"]),
                    "grade": str(source["grade"]),
                    "review_reasons": json.dumps(sorted(set(reasons)), ensure_ascii=False),
                    "run_a_required_principles": json.dumps(
                        sorted(required_a), ensure_ascii=False
                    ),
                    "run_b_required_principles": json.dumps(
                        sorted(required_b), ensure_ascii=False
                    ),
                    "score_differences": json.dumps(
                        differences, ensure_ascii=False, sort_keys=True
                    ),
                    "run_a_principle_scores_json": json.dumps(
                        response_a["principle_scores"],
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                    "run_b_principle_scores_json": json.dumps(
                        response_b["principle_scores"],
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                    "uet_disposition": "",
                    "uet_notes": "",
                }
            )
        elif scores_a == scores_b:
            agreements.append(candidate_id)

    for candidate_id in sorted(
        agreements, key=lambda value: _stable_key(seed, value)
    )[:spot_check_count]:
        source = row_by_id[candidate_id]
        required = sorted(run_a[candidate_id]["required_principle_set"])
        review_rows.append(
            {
                "benchmark_candidate_id": candidate_id,
                "sample_id": str(source["sample_id"]),
                "grade": str(source["grade"]),
                "review_reasons": json.dumps(
                    ["agreement_spot_check"], ensure_ascii=False
                ),
                "run_a_required_principles": json.dumps(required, ensure_ascii=False),
                "run_b_required_principles": json.dumps(required, ensure_ascii=False),
                "score_differences": "{}",
                "run_a_principle_scores_json": json.dumps(
                    run_a[candidate_id]["normalized_response"]["principle_scores"],
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "run_b_principle_scores_json": json.dumps(
                    run_b[candidate_id]["normalized_response"]["principle_scores"],
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "uet_disposition": "",
                "uet_notes": "",
            }
        )

    principle_f1 = {
        principle: _binary_f1(
            [score >= 4 for score in per_principle_left[principle]],
            [score >= 4 for score in per_principle_right[principle]],
        )
        for principle in PRINCIPLE_IDS
    }
    positive_support = {
        principle: {
            "run_a": sum(score >= 4 for score in per_principle_left[principle]),
            "run_b": sum(score >= 4 for score in per_principle_right[principle]),
        }
        for principle in PRINCIPLE_IDS
    }
    weighted_kappa = {
        principle: _weighted_kappa(
            per_principle_left[principle], per_principle_right[principle]
        )
        for principle in PRINCIPLE_IDS
    }
    candidate_count = len(run_a)
    metrics = {
        "candidate_count": candidate_count,
        "score_count": score_count,
        "exact_score_agreement_rate": exact_scores / score_count,
        "within_one_rate": within_one / score_count,
        "required_exact_agreement_rate": exact_required / candidate_count,
        "required_jaccard_mean": sum(jaccard_values) / candidate_count,
        "principle_f1": principle_f1,
        "principle_positive_support": positive_support,
        "weighted_kappa_quadratic": weighted_kappa,
        "no_threshold_crossing_rate": 1.0 - crossing_candidates / candidate_count,
        "threshold_crossing_candidate_count": crossing_candidates,
        "score_distribution_run_a": dict(sorted(score_distribution_a.items())),
        "score_distribution_run_b": dict(sorted(score_distribution_b.items())),
        "semantic_lint_candidate_count": semantic_lint_candidates,
    }
    calibration_rows = [
        row for row in pilot_rows if "focus_principle_id" in row
    ]
    if calibration_rows:
        per_principle_calibration: dict[str, dict[str, Any]] = {}
        both_runs_in_range = 0
        for principle in PRINCIPLE_IDS:
            principle_rows = [
                row
                for row in calibration_rows
                if row["focus_principle_id"] == principle
            ]
            case_metrics: dict[str, Any] = {}
            for case_type in ("positive", "near_miss"):
                typed_rows = [
                    row for row in principle_rows if row["case_type"] == case_type
                ]
                run_a_pass = 0
                run_b_pass = 0
                both_pass = 0
                for row in typed_rows:
                    candidate_id = row["benchmark_candidate_id"]
                    focus = row["focus_principle_id"]
                    minimum = int(row["expected_score_min"])
                    maximum = int(row["expected_score_max"])
                    left = score_map(
                        run_a[candidate_id]["normalized_response"]
                    )[focus]
                    right = score_map(
                        run_b[candidate_id]["normalized_response"]
                    )[focus]
                    left_pass = minimum <= left <= maximum
                    right_pass = minimum <= right <= maximum
                    run_a_pass += left_pass
                    run_b_pass += right_pass
                    both_pass += left_pass and right_pass
                    both_runs_in_range += left_pass and right_pass
                case_metrics[case_type] = {
                    "case_count": len(typed_rows),
                    "run_a_in_range": run_a_pass,
                    "run_b_in_range": run_b_pass,
                    "both_runs_in_range": both_pass,
                }
            per_principle_calibration[principle] = case_metrics
        metrics["calibration"] = {
            "case_count": len(calibration_rows),
            "both_runs_in_range_count": both_runs_in_range,
            "both_runs_in_range_rate": both_runs_in_range
            / len(calibration_rows),
            "per_principle": per_principle_calibration,
            "expected_ranges_are_provisional": any(
                row["uet_status"] != "approved" for row in calibration_rows
            ),
        }
    metrics["thresholds"] = DEFAULT_THRESHOLDS
    supported_f1 = [
        value for value in principle_f1.values() if value is not None
    ]
    metrics["gate_checks"] = {
        "within_one_rate": metrics["within_one_rate"]
        >= DEFAULT_THRESHOLDS["within_one_rate_min"],
        "required_exact_agreement": metrics["required_exact_agreement_rate"]
        >= DEFAULT_THRESHOLDS["required_exact_agreement_min"],
        "required_jaccard_mean": metrics["required_jaccard_mean"]
        >= DEFAULT_THRESHOLDS["required_jaccard_mean_min"],
        "principle_f1": bool(supported_f1)
        and min(supported_f1) >= DEFAULT_THRESHOLDS["principle_f1_min"],
        "principle_positive_support": all(
            support["run_a"] > 0 and support["run_b"] > 0
            for support in positive_support.values()
        ),
        "no_threshold_crossing_rate": metrics["no_threshold_crossing_rate"]
        >= DEFAULT_THRESHOLDS["no_threshold_crossing_rate_min"],
    }
    if "calibration" in metrics:
        metrics["gate_checks"]["calibration_expected_ranges"] = (
            metrics["calibration"]["both_runs_in_range_rate"] == 1.0
        )
    metrics["all_gates_passed"] = all(metrics["gate_checks"].values())
    review_rows.sort(key=lambda row: (int(row["grade"]), row["benchmark_candidate_id"]))
    return metrics, review_rows


def write_review_queue(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle_fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(
            handle_fd, "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=REVIEW_HEADER)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_pilot_summary(metrics: Mapping[str, Any], review_count: int) -> str:
    status = "ĐẠT các ngưỡng đăng ký" if metrics["all_gates_passed"] else "CHƯA ĐẠT"
    f1_lines = "\n".join(
        f"- `{principle}`: "
        + (
            f"{value:.3f}"
            if value is not None
            else "N/A — không có positive support"
        )
        for principle, value in metrics["principle_f1"].items()
    )
    support_lines = "\n".join(
        f"- `{principle}`: run A = {support['run_a']}, "
        f"run B = {support['run_b']}"
        for principle, support in metrics[
            "principle_positive_support"
        ].items()
    )
    gate_lines = "\n".join(
        f"- `{name}`: {'đạt' if passed else 'chưa đạt'}"
        for name, passed in metrics["gate_checks"].items()
    )
    return f"""# Tóm tắt pilot chấm requirement

Trạng thái tự động: **{status}**

## Chỉ số chính

- Candidate: {metrics['candidate_count']}
- Tỷ lệ trùng điểm chính xác: {metrics['exact_score_agreement_rate']:.3f}
- Tỷ lệ chênh không quá một mức: {metrics['within_one_rate']:.3f}
- Exact agreement của tập bắt buộc: {metrics['required_exact_agreement_rate']:.3f}
- Jaccard trung bình của tập bắt buộc: {metrics['required_jaccard_mean']:.3f}
- Tỷ lệ candidate không crossing ngưỡng 4: {metrics['no_threshold_crossing_rate']:.3f}
- Candidate bị semantic lint: {metrics['semantic_lint_candidate_count']}
- Số dòng trong review queue: {review_count}

## F1 theo nguyên tắc tại ngưỡng 4

{f1_lines}

## Positive support tại ngưỡng 4

{support_lines}

## Kết quả gate

{gate_lines}

Kết quả tự động không thay thế UET/HNMU review. `review_queue.csv` chứa
các rủi ro code phát hiện và mẫu kiểm tra ngẫu nhiên; hàng đợi này không
bảo đảm đã bao phủ mọi lỗi ngữ nghĩa.
"""


def build_calibration_summary(
    metrics: Mapping[str, Any], review_count: int
) -> str:
    calibration = metrics["calibration"]
    status = (
        "ĐẠT toàn bộ expected range tạm thời"
        if metrics["gate_checks"]["calibration_expected_ranges"]
        else "CHƯA ĐẠT expected range tạm thời"
    )
    principle_lines: list[str] = []
    for principle, cases in calibration["per_principle"].items():
        positive = cases["positive"]
        near_miss = cases["near_miss"]
        principle_lines.append(
            f"- `{principle}`: positive "
            f"{positive['both_runs_in_range']}/{positive['case_count']}; "
            f"near-miss "
            f"{near_miss['both_runs_in_range']}/{near_miss['case_count']}"
        )
    return f"""# Tóm tắt calibration requirement-scoring

Trạng thái tự động: **{status}**

## Chỉ số chính

- Calibration case: {calibration['case_count']}
- Cả hai run nằm trong expected range: \
{calibration['both_runs_in_range_count']}/{calibration['case_count']} \
({calibration['both_runs_in_range_rate']:.3f})
- Candidate bị semantic lint: {metrics['semantic_lint_candidate_count']}
- Số dòng trong review queue: {review_count}
- Expected range còn tạm thời, chờ UET review: \
{'có' if calibration['expected_ranges_are_provisional'] else 'không'}

## Kết quả theo nguyên tắc

{chr(10).join(principle_lines)}

Calibration là bộ kiểm tra ranh giới có chủ đích, không phải ước lượng
accuracy đại diện cho toàn bộ 2.028 candidate. `review_queue.csv` chứa
case ngoài expected range, semantic lint, bất đồng A/B và spot check; nó
không thay thế UET/HNMU review.
"""


def validate_specification_manifest(manifest_path: Path, repository_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("prompt_language") != "vi":
        raise RequirementScoringError("Specification prompt_language must be 'vi'")
    for group in ("artifacts", "sources"):
        for item in manifest.get(group, []):
            path = repository_root / item["path"]
            if not path.is_file():
                raise RequirementScoringError(f"Manifest path does not exist: {path}")
            actual = sha256_file(path)
            if actual != item["sha256"]:
                raise RequirementScoringError(
                    f"Manifest hash mismatch for {item['path']}"
                )
    return manifest


def validate_snapshot_manifest(manifest_path: Path) -> list[dict[str, str]]:
    """Validate every inherited snapshot file before preparing a pilot."""

    expected_header = ("sha256", "relative_path", "role")
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_header:
            raise RequirementScoringError("Snapshot manifest header mismatch")
        rows = [dict(row) for row in reader]
    if len(rows) != 41:
        raise RequirementScoringError(
            f"Snapshot manifest must contain 41 files, found {len(rows)}"
        )
    snapshot_root = manifest_path.parent.resolve()
    seen: set[str] = set()
    allowed_roles = {
        "active_input",
        "provisional_foundation",
        "research_foundation",
        "diagnostic_only",
        "completed_report",
        "completed_decision",
    }
    for row in rows:
        relative_path = row["relative_path"]
        if relative_path in seen:
            raise RequirementScoringError(
                f"Duplicate snapshot path: {relative_path}"
            )
        seen.add(relative_path)
        if row["role"] not in allowed_roles:
            raise RequirementScoringError(
                f"Unsupported snapshot role for {relative_path}: {row['role']}"
            )
        path = (snapshot_root / relative_path).resolve()
        try:
            path.relative_to(snapshot_root)
        except ValueError as exc:
            raise RequirementScoringError(
                f"Snapshot path escapes inherited_resources: {relative_path}"
            ) from exc
        if not path.is_file():
            raise RequirementScoringError(
                f"Snapshot path does not exist: {relative_path}"
            )
        if sha256_file(path) != row["sha256"]:
            raise RequirementScoringError(
                f"Snapshot hash mismatch for {relative_path}"
            )
    return rows

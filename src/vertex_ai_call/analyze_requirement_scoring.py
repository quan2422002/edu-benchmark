"""Deterministic Plan-03 analysis for the full requirement-scoring run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import statistics
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


from vertex_ai_call.requirement_scoring import (  # noqa: E402
    PRINCIPLE_IDS,
    GenerationConfig,
    RequirementScoringError,
    atomic_write_json,
    atomic_write_text,
    build_grounding_payload,
    build_request_hash,
    canonical_json_hash,
    lint_principle_scores,
    load_grounding_pool,
    load_run_records,
    sha256_file,
    utc_now,
    validate_run_records,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT = REPOSITORY_ROOT / "experiments/20260727_170150"
DEFAULT_BUNDLE = (
    DEFAULT_EXPERIMENT
    / "outputs/principle_requirement_scoring/full_gemini35_medium_v1"
)
DEFAULT_POOL = (
    DEFAULT_EXPERIMENT
    / "inherited_resources/from_20260722_000940/benchmark_specification/"
    "candidate_grounding/candidate_principle_grounding_pool.csv"
)
DEFAULT_TRACE = (
    DEFAULT_EXPERIMENT
    / "inherited_resources/from_20260722_000940/benchmark_conversion/"
    "full_v0/conversion_trace.csv"
)
DEFAULT_PAPER_REGISTRY = (
    REPOSITORY_ROOT
    / "kse_submit_manuscript/notes/claim_evidence_registry.csv"
)

TRACE_HEADER: tuple[str, ...] = (
    "benchmark_candidate_id",
    "sample_id",
    "source_batch",
    "source_file",
    "source_row_number",
    "target_tutor_turn_index",
    "split_strategy",
    "dialogue_correction_ids",
)

REVIEW_HEADER: tuple[str, ...] = (
    "review_priority",
    "queue_type",
    "eligibility_status",
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "bloom_level",
    "has_history",
    "history_turn_count",
    "target_tutor_turn_index",
    "family_position",
    "required_principle_set",
    "alternative_principle_set",
    "review_reasons",
    "principle_scores_json",
    "flagged_details_json",
    "uet_disposition",
    "uet_notes",
)

PAPER_REGISTRY_HEADER: tuple[str, ...] = (
    "claim_id",
    "claim_text_vi",
    "evidence_type",
    "source_path",
    "source_locator",
    "source_sha256",
    "status",
    "limitations",
)

RARE_CANDIDATE_THRESHOLD = 5
RARE_FAMILY_THRESHOLD = 3
SMALL_STRATUM_THRESHOLD = 10
CONTROL_SAMPLE_PER_GRADE = 2
SELECTION_SEED = 20260727

EXPECTED_LIMITATION_IDS: frozenset[str] = frozenset(
    {
        "single_run_no_repeatability_estimate",
        "no_expert_accuracy",
        "provisional_model_scores",
    }
)

_FIELD_REFERENCE_TERMS: tuple[str, ...] = (
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "source_question",
    "gold_answer",
)
_TURN_REFERENCE_RE = re.compile(
    r"(?:turn(?:_index)?[_:\s]*|lượt(?:\s+thoại)?\s*:?\s*)(\d+)",
    re.IGNORECASE,
)
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _rate(count: int | float, total: int) -> float:
    return round(float(count) / total, 6) if total else 0.0


def _mean(values: Iterable[float]) -> float:
    materialized = list(values)
    return round(sum(materialized) / len(materialized), 6) if materialized else 0.0


def _stable_key(value: str, *, seed: int = SELECTION_SEED) -> str:
    return hashlib.sha256(f"{seed}:{value}".encode("utf-8")).hexdigest()


def _set_key(principles: Sequence[str]) -> str:
    return "|".join(principles) if principles else "__EMPTY__"


def _json_cell(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(path)


def _atomic_write_csv(
    path: Path,
    *,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle_fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(
            handle_fd, "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
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


def load_conversion_trace(path: Path) -> list[dict[str, Any]]:
    """Load and validate the one-to-one conversion trace."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != TRACE_HEADER:
            raise RequirementScoringError("Conversion trace header mismatch")
        rows: list[dict[str, Any]] = []
        for raw in reader:
            candidate_id = raw["benchmark_candidate_id"].strip()
            try:
                target_index = int(raw["target_tutor_turn_index"])
            except ValueError as exc:
                raise RequirementScoringError(
                    f"{candidate_id}: invalid target_tutor_turn_index"
                ) from exc
            if target_index < 2 or target_index % 2:
                raise RequirementScoringError(
                    f"{candidate_id}: target tutor turn must be a positive even index"
                )
            row = dict(raw)
            row["target_tutor_turn_index"] = target_index
            rows.append(row)
    ids = [row["benchmark_candidate_id"] for row in rows]
    duplicates = [
        candidate_id
        for candidate_id, count in Counter(ids).items()
        if count > 1
    ]
    if duplicates:
        raise RequirementScoringError(
            f"Conversion trace contains duplicate candidates: {duplicates[:5]}"
        )
    return rows


def _score_map(record: Mapping[str, Any]) -> dict[str, int]:
    return {
        str(item["principle_id"]): int(item["requirement_score"])
        for item in record["normalized_response"]["principle_scores"]
    }


def _normalize_reference_text(value: Any) -> str:
    if isinstance(value, Mapping):
        value = " ".join(
            _normalize_reference_text(item) for item in value.values()
        )
    if isinstance(value, list):
        value = " ".join(_normalize_reference_text(item) for item in value)
    text = str(value).casefold()
    return " ".join(_TOKEN_RE.findall(text))


def evidence_reference_is_traceable(
    evidence: str,
    payload: Mapping[str, Any],
) -> bool:
    """Conservatively check whether an evidence string points into the payload."""

    evidence_folded = evidence.casefold()
    if any(term in evidence_folded for term in _FIELD_REFERENCE_TERMS):
        return True

    valid_turns = {1}
    history = payload.get("conversation_history", [])
    if isinstance(history, list):
        valid_turns.update(
            int(item["turn_index"])
            for item in history
            if isinstance(item, dict) and isinstance(item.get("turn_index"), int)
        )
    referenced_turns = {
        int(match.group(1)) for match in _TURN_REFERENCE_RE.finditer(evidence)
    }
    if referenced_turns and referenced_turns.issubset(valid_turns):
        return True
    if (
        ("hội thoại" in evidence_folded or "lịch sử" in evidence_folded)
        and history
    ):
        return True

    payload_text = _normalize_reference_text(list(payload.values()))
    evidence_tokens = {
        token
        for token in _TOKEN_RE.findall(evidence_folded)
        if len(token) >= 3
    }
    payload_tokens = {
        token
        for token in _TOKEN_RE.findall(payload_text)
        if len(token) >= 3
    }
    return len(evidence_tokens & payload_tokens) >= 3


def _family_positions(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    by_family: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        by_family[str(row["sample_id"])].append(
            (
                int(row["target_tutor_turn_index"]),
                str(row["benchmark_candidate_id"]),
            )
        )
    positions: dict[str, str] = {}
    for family_rows in by_family.values():
        ordered = sorted(family_rows)
        if len(ordered) == 1:
            positions[ordered[0][1]] = "single"
            continue
        for index, (_, candidate_id) in enumerate(ordered):
            if index == 0:
                positions[candidate_id] = "first"
            elif index == len(ordered) - 1:
                positions[candidate_id] = "last"
            else:
                positions[candidate_id] = "middle"
    return positions


def _score_distribution(values: Sequence[int]) -> dict[str, Any]:
    counts = Counter(values)
    ordered = sorted(values)
    quartiles = statistics.quantiles(ordered, n=4, method="inclusive")
    return {
        "score_counts": {str(score): counts[score] for score in range(1, 6)},
        "score_rates": {
            str(score): _rate(counts[score], len(values)) for score in range(1, 6)
        },
        "median": statistics.median(ordered),
        "q1": quartiles[0],
        "q3": quartiles[2],
        "mean_descriptive_only": round(statistics.fmean(ordered), 6),
    }


def _principle_statistics(
    candidates: Sequence[Mapping[str, Any]],
    family_sizes: Mapping[str, int],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for principle_id in PRINCIPLE_IDS:
        values = [int(row["scores"][principle_id]) for row in candidates]
        required_by_family: Counter[str] = Counter(
            str(row["sample_id"])
            for row in candidates
            if int(row["scores"][principle_id]) >= 4
        )
        alternative_by_family: Counter[str] = Counter(
            str(row["sample_id"])
            for row in candidates
            if int(row["scores"][principle_id]) == 3
        )
        stats = _score_distribution(values)
        required_count = sum(value >= 4 for value in values)
        alternative_count = sum(value == 3 for value in values)
        stats.update(
            {
                "required_count": required_count,
                "required_rate_candidate_macro": _rate(
                    required_count, len(candidates)
                ),
                "required_rate_family_macro": _mean(
                    required_by_family[family] / size
                    for family, size in family_sizes.items()
                ),
                "alternative_count": alternative_count,
                "alternative_rate_candidate_macro": _rate(
                    alternative_count, len(candidates)
                ),
                "alternative_rate_family_macro": _mean(
                    alternative_by_family[family] / size
                    for family, size in family_sizes.items()
                ),
            }
        )
        result[principle_id] = stats
    return result


def _exact_set_distribution(
    candidates: Sequence[Mapping[str, Any]],
    *,
    field: str,
    family_sizes: Mapping[str, int],
) -> list[dict[str, Any]]:
    by_set: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in candidates:
        by_set[_set_key(row[field])].append(row)
    distributions: list[dict[str, Any]] = []
    for key, members in by_set.items():
        principles = list(members[0][field])
        family_counts = Counter(str(row["sample_id"]) for row in members)
        grade_counts = Counter(str(row["grade"]) for row in members)
        distributions.append(
            {
                "set_key": key,
                "principles": principles,
                "set_size": len(principles),
                "candidate_count": len(members),
                "candidate_rate": _rate(len(members), len(candidates)),
                "family_count": len(family_counts),
                "family_macro_rate": _mean(
                    family_counts[family] / size
                    for family, size in family_sizes.items()
                ),
                "grade_counts": {
                    grade: grade_counts[grade] for grade in ("6", "7", "8", "9")
                },
                "rare_required_set": (
                    field == "required_principles"
                    and (
                        len(members) < RARE_CANDIDATE_THRESHOLD
                        or len(family_counts) < RARE_FAMILY_THRESHOLD
                    )
                ),
            }
        )
    return sorted(
        distributions,
        key=lambda item: (-item["candidate_count"], item["set_key"]),
    )


def _cooccurrence(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    matrix: dict[str, dict[str, int]] = {
        left: {right: 0 for right in PRINCIPLE_IDS}
        for left in PRINCIPLE_IDS
    }
    for row in candidates:
        required = set(row["required_principles"])
        for left in PRINCIPLE_IDS:
            for right in PRINCIPLE_IDS:
                if left in required and right in required:
                    matrix[left][right] += 1
    return {
        "counts": matrix,
        "rates": {
            left: {
                right: _rate(matrix[left][right], len(candidates))
                for right in PRINCIPLE_IDS
            }
            for left in PRINCIPLE_IDS
        },
    }


def _strata(
    candidates: Sequence[Mapping[str, Any]],
    *,
    field: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in candidates:
        grouped[str(row[field])].append(row)
    output: list[dict[str, Any]] = []
    for value, members in grouped.items():
        required_counts = {
            principle_id: sum(
                principle_id in row["required_principles"] for row in members
            )
            for principle_id in PRINCIPLE_IDS
        }
        output.append(
            {
                "value": value,
                "candidate_count": len(members),
                "family_count": len({row["sample_id"] for row in members}),
                "small_stratum_warning": len(members) < SMALL_STRATUM_THRESHOLD,
                "required_counts": required_counts,
                "required_rates": {
                    principle_id: _rate(count, len(members))
                    for principle_id, count in required_counts.items()
                },
            }
        )
    return sorted(output, key=lambda item: (-item["candidate_count"], item["value"]))


def _reason_priority(reasons: Sequence[str], state: str) -> int:
    if state == "blocked":
        return 1
    if any(
        reason in {"no_required_principle", "more_than_three_required"}
        for reason in reasons
    ):
        return 2
    if any(
        reason.startswith("feedback_") or reason.startswith("questioning_")
        for reason in reasons
    ):
        return 3
    if any(
        reason.startswith("high_score_")
        or reason.startswith("evidence_")
        for reason in reasons
    ):
        return 4
    if "rare_required_set" in reasons:
        return 5
    return 9


def _flagged_details(
    row: Mapping[str, Any],
    reasons: Sequence[str],
) -> list[dict[str, Any]]:
    principle_ids: set[str] = set()
    for reason in reasons:
        for principle_id in PRINCIPLE_IDS:
            if principle_id in reason:
                principle_ids.add(principle_id)
        if reason.startswith("feedback_"):
            principle_ids.add("PRINCIPLE-FEEDBACK")
        if reason.startswith("questioning_"):
            principle_ids.add("PRINCIPLE-QUESTIONING")
    if not principle_ids:
        principle_ids.update(row["required_principles"])
    return [
        item
        for item in row["principle_scores"]
        if item["principle_id"] in principle_ids
    ]


def _eligible_distribution(
    candidates: Sequence[Mapping[str, Any]],
    eligible_ids: set[str],
    *,
    field: str,
) -> list[dict[str, Any]]:
    totals = Counter(str(row[field]) for row in candidates)
    eligible = Counter(
        str(row[field])
        for row in candidates
        if row["benchmark_candidate_id"] in eligible_ids
    )
    return [
        {
            "value": value,
            "candidate_count": totals[value],
            "eligible_count": eligible[value],
            "eligible_rate_within_stratum": _rate(eligible[value], totals[value]),
        }
        for value in sorted(totals, key=lambda value: (-totals[value], value))
    ]


def _family_eligibility(
    candidates: Sequence[Mapping[str, Any]],
    status_by_id: Mapping[str, str],
) -> dict[str, int]:
    states: dict[str, set[str]] = defaultdict(set)
    for row in candidates:
        states[str(row["sample_id"])].add(
            status_by_id[str(row["benchmark_candidate_id"])]
        )
    result = Counter()
    for family_states in states.values():
        if family_states == {"eligible_without_plan03_review"}:
            result["all_candidates_eligible"] += 1
        elif "eligible_without_plan03_review" in family_states:
            result["mixed_eligibility"] += 1
        else:
            result["no_candidate_eligible"] += 1
    return dict(sorted(result.items()))


def _markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cells = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_analysis_markdown(analysis: Mapping[str, Any]) -> str:
    """Build the concise Vietnamese UET-facing analysis report."""

    integrity = analysis["integrity"]
    eligibility = analysis["eligibility"]
    principle_stats = analysis["principle_statistics"]
    required_sets = analysis["required_set_distribution"]
    reason_counts = eligibility["reason_counts"]
    score_rows = [
        (
            principle_id,
            stats["required_count"],
            f"{stats['required_rate_candidate_macro']:.3f}",
            f"{stats['required_rate_family_macro']:.3f}",
            stats["alternative_count"],
            stats["median"],
        )
        for principle_id, stats in principle_stats.items()
    ]
    set_rows = [
        (
            item["set_key"],
            item["candidate_count"],
            f"{item['candidate_rate']:.3f}",
            item["family_count"],
            f"{item['family_macro_rate']:.3f}",
            "có" if item["rare_required_set"] else "",
        )
        for item in required_sets
    ]
    eligibility_rows = [
        (
            state,
            eligibility["counts"][state],
            f"{eligibility['rates'][state]:.3f}",
        )
        for state in (
            "eligible_without_plan03_review",
            "needs_uet_review",
            "blocked",
        )
    ]
    reason_rows = [
        (reason, count)
        for reason, count in sorted(
            reason_counts.items(), key=lambda item: (-item[1], item[0])
        )
    ]
    return f"""# Báo cáo Plan 03 — Phân tích full run requirement-scoring

Trạng thái: `AWAITING_UET_DISPOSITION`

## 1. Evidence — bằng chứng trực tiếp

- Bundle có {integrity['candidate_count']} candidate thuộc
  {integrity['family_count']} family.
- Có {integrity['score_count']} score; mọi ID, join, request hash và
  `user_prompt` đều qua validator.
- Failure hiện hành: {integrity['current_failure_count']}; lỗi lịch sử được
  giữ riêng: {integrity['historical_error_count']}.
- Đây là một run duy nhất của `{integrity['model']}`; các score là đề xuất
  của model, không phải ground truth.

### 1.1. Phân bố theo nguyên tắc

{_markdown_table(
    (
        'Nguyên tắc',
        'Số bắt buộc',
        'Candidate-macro',
        'Family-macro',
        'Số thay thế',
        'Trung vị',
    ),
    score_rows,
)}

### 1.2. Toàn bộ tập nguyên tắc bắt buộc quan sát được

`rare_required_set` nghĩa là dưới {RARE_CANDIDATE_THRESHOLD} candidate
hoặc dưới {RARE_FAMILY_THRESHOLD} family.

{_markdown_table(
    (
        'Tập nguyên tắc',
        'Candidate',
        'Tỷ lệ',
        'Family',
        'Family-macro',
        'Hiếm',
    ),
    set_rows,
)}

### 1.3. Trạng thái đủ điều kiện đi tiếp

{_markdown_table(('Trạng thái', 'Số lượng', 'Tỷ lệ'), eligibility_rows)}

### 1.4. Lý do cần review hoặc bị chặn

{_markdown_table(('Lý do', 'Số candidate'), reason_rows)}

## 2. Inference — diễn giải tạm thời

- Phân bố trên mô tả hành vi của một lần chấm bằng model; không phải ước
  lượng accuracy hoặc độ ổn định.
- `eligible_without_plan03_review` chỉ có nghĩa không bị cờ ở Plan 03.
  Nhóm này vẫn phải qua audit `gold_response`, grounding và review tích hợp
  ở các plan sau.
- Khác biệt giữa lớp, bài học hoặc vị trí lượt chỉ được báo mô tả. Plan 03
  không dùng chúng để kết luận một candidate có lỗi.

## 3. Teacher decision needed — phần UET/HNMU cần quyết định

1. UET xem các dòng ưu tiên cao trong `full_run_review_queue.csv`, trước
   hết là lỗi evidence/cấu trúc, tập rỗng hoặc trên ba nguyên tắc.
2. UET quyết định disposition theo nhóm lý do; không sửa trực tiếp
   `run_full.jsonl`.
3. HNMU xác nhận ranh giới sư phạm của sáu nguyên tắc trong gói tích hợp
   rubric–instruction–ví dụ ở plan sau.

## 4. Giới hạn

- Không có run B trên full pool nên không báo agreement, Jaccard hoặc F1.
- Không có nhãn chuyên gia cấp candidate nên không báo accuracy.
- Lint dùng regex chỉ tạo cờ review và không tự sửa score.
- Tổ hợp hiếm là quy tắc vận hành để lấy mẫu review, không phải bằng chứng
  rằng tổ hợp đó sai về mặt sư phạm.
"""


def _write_paper_registry(
    path: Path,
    *,
    analysis: Mapping[str, Any],
    analysis_path: Path,
    manifest_path: Path,
) -> None:
    existing: list[dict[str, str]] = []
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != PAPER_REGISTRY_HEADER:
                raise RequirementScoringError("Paper evidence registry header mismatch")
            existing = [
                dict(row)
                for row in reader
                if not row["claim_id"].startswith("KSE-P03-")
            ]
    eligibility = analysis["eligibility"]["counts"]
    top_set = analysis["required_set_distribution"][0]
    new_rows = [
        {
            "claim_id": "KSE-P03-001",
            "claim_text_vi": (
                f"Full run có {analysis['integrity']['candidate_count']} candidate, "
                f"{analysis['integrity']['family_count']} family và "
                f"{analysis['integrity']['score_count']} requirement score hợp lệ."
            ),
            "evidence_type": "evidence",
            "source_path": _display_path(manifest_path),
            "source_locator": "integrity; failure_state; status",
            "source_sha256": sha256_file(manifest_path),
            "status": "provisional_model_output_validated",
            "limitations": "Một run; không có accuracy hoặc expert agreement.",
        },
        {
            "claim_id": "KSE-P03-002",
            "claim_text_vi": (
                f"Tập nguyên tắc bắt buộc phổ biến nhất là "
                f"{top_set['set_key']} với {top_set['candidate_count']} candidate."
            ),
            "evidence_type": "evidence",
            "source_path": _display_path(analysis_path),
            "source_locator": "required_set_distribution[0]",
            "source_sha256": sha256_file(analysis_path),
            "status": "provisional_model_output",
            "limitations": "Phân bố phản ánh score của một model run.",
        },
        {
            "claim_id": "KSE-P03-003",
            "claim_text_vi": (
                f"{eligibility['eligible_without_plan03_review']} candidate không "
                "bị cờ review riêng ở Plan 03; "
                f"{eligibility['needs_uet_review']} candidate cần UET review và "
                f"{eligibility['blocked']} candidate bị chặn."
            ),
            "evidence_type": "evidence",
            "source_path": _display_path(analysis_path),
            "source_locator": "eligibility.counts",
            "source_sha256": sha256_file(analysis_path),
            "status": "provisional_awaiting_uet_disposition",
            "limitations": (
                "Eligibility Plan 03 không thay thế audit candidate hoặc HNMU review."
            ),
        },
    ]
    _atomic_write_csv(
        path,
        fieldnames=PAPER_REGISTRY_HEADER,
        rows=existing + new_rows,
    )


def analyze_full_run(
    *,
    bundle_dir: Path,
    pool_path: Path,
    trace_path: Path,
    paper_registry_path: Path,
    expected_candidate_count: int = 2028,
    expected_family_count: int = 665,
) -> dict[str, Any]:
    """Validate, analyze, and publish the three approved Plan-03 artifacts."""

    manifest_path = bundle_dir / "run_manifest.json"
    run_path = bundle_dir / "run_full.jsonl"
    if not manifest_path.is_file() or not run_path.is_file():
        raise RequirementScoringError("Full bundle is missing run or manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed_awaiting_analysis":
        raise RequirementScoringError(
            "Full manifest is not completed_awaiting_analysis"
        )
    current_failed = (
        manifest.get("runs", {}).get("full", {}).get("failed_candidate_ids", [])
    )
    if current_failed:
        raise RequirementScoringError("Full manifest still has current failures")
    limitation_ids = {
        item.get("limitation_id")
        for item in manifest.get("limitations", [])
        if isinstance(item, dict)
    }
    if limitation_ids != EXPECTED_LIMITATION_IDS:
        raise RequirementScoringError("Full manifest limitations are incomplete")
    failure_state = manifest.get("failure_state", {})
    if (
        failure_state.get("current_failure_count") != 0
        or failure_state.get("current_failed_candidate_ids") != []
    ):
        raise RequirementScoringError("Full manifest failure_state is not clean")

    pool_rows = load_grounding_pool(pool_path)
    trace_rows = load_conversion_trace(trace_path)
    records = load_run_records(run_path)
    if len(pool_rows) != expected_candidate_count:
        raise RequirementScoringError(
            f"Expected {expected_candidate_count} pool rows, found {len(pool_rows)}"
        )
    if len({row["sample_id"] for row in pool_rows}) != expected_family_count:
        raise RequirementScoringError(
            f"Expected {expected_family_count} families"
        )
    validated = validate_run_records(records, pool_rows, run_id="full")
    source_by_id = {
        str(row["benchmark_candidate_id"]): row for row in pool_rows
    }
    trace_by_id = {
        str(row["benchmark_candidate_id"]): row for row in trace_rows
    }
    if set(trace_by_id) != set(source_by_id):
        raise RequirementScoringError("Conversion trace does not join one-to-one")
    if manifest.get("input", {}).get("grounding_pool_sha256") != sha256_file(
        pool_path
    ):
        raise RequirementScoringError("Grounding pool hash differs from manifest")
    if manifest.get("integrity", {}).get("run_file_sha256") != sha256_file(
        run_path
    ):
        raise RequirementScoringError("Run hash differs from manifest")
    generation_config = GenerationConfig(**manifest["generation_config"])
    prompt_hash = manifest["specification"]["prompt_sha256"]
    schema_hash = manifest["specification"]["schema_sha256"]

    joined: list[dict[str, Any]] = []
    response_ids: set[str] = set()
    for pool_row in pool_rows:
        candidate_id = str(pool_row["benchmark_candidate_id"])
        trace_row = trace_by_id[candidate_id]
        if trace_row["sample_id"] != pool_row["sample_id"]:
            raise RequirementScoringError(
                f"{candidate_id}: sample_id mismatch in conversion trace"
            )
        record = validated[candidate_id]
        expected_request_hash = build_request_hash(
            payload=build_grounding_payload(pool_row),
            prompt_sha256=prompt_hash,
            schema_sha256=schema_hash,
            generation_config=generation_config,
        )
        if record["request_hash"] != expected_request_hash:
            raise RequirementScoringError(
                f"{candidate_id}: request hash mismatch"
            )
        if record["model"] != generation_config.model:
            raise RequirementScoringError(f"{candidate_id}: model mismatch")
        response_id = str(record["response_id"])
        if not response_id or response_id in response_ids:
            raise RequirementScoringError(
                f"{candidate_id}: missing or duplicate response_id"
            )
        response_ids.add(response_id)
        if not str(record["raw_response_text"]).strip():
            raise RequirementScoringError(f"{candidate_id}: empty raw response")
        history = pool_row["conversation_history"]
        joined.append(
            {
                "benchmark_candidate_id": candidate_id,
                "sample_id": str(pool_row["sample_id"]),
                "grade": int(pool_row["grade"]),
                "lesson": str(pool_row["lesson"]),
                "bloom_level": str(pool_row["bloom_level"]),
                "has_history": bool(history),
                "history_turn_count": len(history),
                "target_tutor_turn_index": int(
                    trace_row["target_tutor_turn_index"]
                ),
                "required_principles": list(record["required_principle_set"]),
                "alternative_principles": list(
                    record["alternative_principle_set"]
                ),
                "scores": _score_map(record),
                "principle_scores": record["normalized_response"][
                    "principle_scores"
                ],
                "payload": build_grounding_payload(pool_row),
                "lint_reasons": lint_principle_scores(
                    record["normalized_response"]
                ),
            }
        )
    positions = _family_positions(joined)
    for row in joined:
        row["family_position"] = positions[row["benchmark_candidate_id"]]

    family_sizes = Counter(str(row["sample_id"]) for row in joined)
    required_sets = _exact_set_distribution(
        joined,
        field="required_principles",
        family_sizes=family_sizes,
    )
    alternative_sets = _exact_set_distribution(
        joined,
        field="alternative_principles",
        family_sizes=family_sizes,
    )
    rare_set_keys = {
        item["set_key"]
        for item in required_sets
        if item["rare_required_set"]
    }

    state_ids: dict[str, list[str]] = {
        "eligible_without_plan03_review": [],
        "needs_uet_review": [],
        "blocked": [],
    }
    reasons_by_id: dict[str, list[str]] = {}
    status_by_id: dict[str, str] = {}
    reason_counts: Counter[str] = Counter()
    for row in joined:
        blocked_reasons = []
        for item in row["principle_scores"]:
            if not evidence_reference_is_traceable(
                str(item["evidence"]), row["payload"]
            ):
                blocked_reasons.append(
                    f"evidence_reference_unresolved:{item['principle_id']}"
                )
        review_reasons = list(row["lint_reasons"])
        required_count = len(row["required_principles"])
        if required_count == 0:
            review_reasons.append("no_required_principle")
        if required_count > 3:
            review_reasons.append("more_than_three_required")
        if _set_key(row["required_principles"]) in rare_set_keys:
            review_reasons.append("rare_required_set")
        all_reasons = sorted(set(blocked_reasons + review_reasons))
        if blocked_reasons:
            state = "blocked"
        elif review_reasons:
            state = "needs_uet_review"
        else:
            state = "eligible_without_plan03_review"
        candidate_id = row["benchmark_candidate_id"]
        state_ids[state].append(candidate_id)
        status_by_id[candidate_id] = state
        reasons_by_id[candidate_id] = all_reasons
        reason_counts.update(all_reasons)

    for candidate_ids in state_ids.values():
        candidate_ids.sort()
    eligible_ids = set(state_ids["eligible_without_plan03_review"])
    controls: set[str] = set()
    for grade in (6, 7, 8, 9):
        grade_eligible = sorted(
            (
                candidate_id
                for candidate_id in eligible_ids
                if next(
                    row for row in joined
                    if row["benchmark_candidate_id"] == candidate_id
                )["grade"]
                == grade
            ),
            key=_stable_key,
        )
        controls.update(grade_eligible[:CONTROL_SAMPLE_PER_GRADE])

    review_rows: list[dict[str, Any]] = []
    for row in joined:
        candidate_id = row["benchmark_candidate_id"]
        state = status_by_id[candidate_id]
        is_control = candidate_id in controls
        if state == "eligible_without_plan03_review" and not is_control:
            continue
        reasons = reasons_by_id[candidate_id]
        queue_type = "control_sample" if is_control else "flagged"
        queue_reasons = reasons if reasons else ["stratified_control_sample"]
        review_rows.append(
            {
                "review_priority": (
                    9 if is_control else _reason_priority(queue_reasons, state)
                ),
                "queue_type": queue_type,
                "eligibility_status": state,
                "benchmark_candidate_id": candidate_id,
                "sample_id": row["sample_id"],
                "grade": row["grade"],
                "lesson": row["lesson"],
                "bloom_level": row["bloom_level"],
                "has_history": str(row["has_history"]).lower(),
                "history_turn_count": row["history_turn_count"],
                "target_tutor_turn_index": row["target_tutor_turn_index"],
                "family_position": row["family_position"],
                "required_principle_set": _json_cell(
                    row["required_principles"]
                ),
                "alternative_principle_set": _json_cell(
                    row["alternative_principles"]
                ),
                "review_reasons": ";".join(queue_reasons),
                "principle_scores_json": _json_cell(row["scores"]),
                "flagged_details_json": _json_cell(
                    _flagged_details(row, queue_reasons)
                ),
                "uet_disposition": "",
                "uet_notes": "",
            }
        )
    review_rows.sort(
        key=lambda row: (
            int(row["review_priority"]),
            int(row["grade"]),
            str(row["benchmark_candidate_id"]),
        )
    )

    state_counts = {
        state: len(candidate_ids) for state, candidate_ids in state_ids.items()
    }
    if sum(state_counts.values()) != len(joined):
        raise RequirementScoringError("Eligibility partition does not cover all rows")
    if any(
        set(state_ids[left]) & set(state_ids[right])
        for left in state_ids
        for right in state_ids
        if left < right
    ):
        raise RequirementScoringError("Eligibility states overlap")

    size_counts = Counter(len(row["required_principles"]) for row in joined)
    candidate_count_distribution = Counter(family_sizes.values())
    analysis: dict[str, Any] = {
        "analysis_version": "plan03_v1",
        "generated_at": utc_now(),
        "status": "awaiting_uet_disposition",
        "analysis_config": {
            "rare_candidate_threshold_exclusive": RARE_CANDIDATE_THRESHOLD,
            "rare_family_threshold_exclusive": RARE_FAMILY_THRESHOLD,
            "small_stratum_threshold_exclusive": SMALL_STRATUM_THRESHOLD,
            "control_sample_per_grade": CONTROL_SAMPLE_PER_GRADE,
            "selection_seed": SELECTION_SEED,
            "outlier_policy": (
                "descriptive_only_no_candidate_level_flag"
            ),
        },
        "input_hashes": {
            "run_full_jsonl": sha256_file(run_path),
            "run_manifest_json": sha256_file(manifest_path),
            "grounding_pool_csv": sha256_file(pool_path),
            "conversion_trace_csv": sha256_file(trace_path),
            "prompt": prompt_hash,
            "response_schema": schema_hash,
        },
        "integrity": {
            "validated": True,
            "candidate_count": len(joined),
            "family_count": len(family_sizes),
            "score_count": len(joined) * len(PRINCIPLE_IDS),
            "run_record_count": len(records),
            "distinct_response_id_count": len(response_ids),
            "joined_grounding_count": len(source_by_id),
            "joined_trace_count": len(trace_by_id),
            "current_failure_count": failure_state["current_failure_count"],
            "historical_error_count": failure_state["historical_error_count"],
            "model": generation_config.model,
        },
        "principle_statistics": _principle_statistics(joined, family_sizes),
        "required_set_size_distribution": {
            str(size): {
                "candidate_count": size_counts[size],
                "candidate_rate": _rate(size_counts[size], len(joined)),
            }
            for size in sorted(size_counts)
        },
        "required_set_distribution": required_sets,
        "alternative_set_distribution": alternative_sets,
        "required_principle_cooccurrence": _cooccurrence(joined),
        "family_statistics": {
            "family_count": len(family_sizes),
            "candidate_count_min": min(family_sizes.values()),
            "candidate_count_max": max(family_sizes.values()),
            "candidate_count_mean": round(
                statistics.fmean(family_sizes.values()), 6
            ),
            "candidate_count_distribution": {
                str(count): family_count
                for count, family_count in sorted(
                    candidate_count_distribution.items()
                )
            },
        },
        "stratification": {
            field: _strata(joined, field=field)
            for field in (
                "grade",
                "lesson",
                "bloom_level",
                "has_history",
                "history_turn_count",
                "target_tutor_turn_index",
                "family_position",
            )
        },
        "eligibility": {
            "counts": state_counts,
            "rates": {
                state: _rate(count, len(joined))
                for state, count in state_counts.items()
            },
            "candidate_ids": state_ids,
            "reason_counts": dict(
                sorted(
                    reason_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "eligible_distributions": {
                field: _eligible_distribution(
                    joined, eligible_ids, field=field
                )
                for field in (
                    "grade",
                    "lesson",
                    "bloom_level",
                    "has_history",
                    "history_turn_count",
                    "target_tutor_turn_index",
                    "family_position",
                )
            },
            "eligible_required_set_distribution": [
                item
                for item in _exact_set_distribution(
                    [
                        row
                        for row in joined
                        if row["benchmark_candidate_id"] in eligible_ids
                    ],
                    field="required_principles",
                    family_sizes=family_sizes,
                )
            ],
            "family_eligibility": _family_eligibility(
                joined, status_by_id
            ),
        },
        "review_queue": {
            "row_count": len(review_rows),
            "flagged_candidate_count": sum(
                row["queue_type"] == "flagged" for row in review_rows
            ),
            "control_sample_count": sum(
                row["queue_type"] == "control_sample" for row in review_rows
            ),
        },
        "limitations": manifest["limitations"],
        "interpretation_contract": {
            "evidence": "Direct deterministic counts from the validated run.",
            "inference": "Provisional project interpretation awaiting UET.",
            "teacher_decision_needed": (
                "Pedagogical validity remains reserved for HNMU review."
            ),
        },
    }

    if analysis["integrity"]["score_count"] != expected_candidate_count * 6:
        raise RequirementScoringError("Score total invariant failed")
    if sum(
        item["candidate_count"] for item in required_sets
    ) != expected_candidate_count:
        raise RequirementScoringError("Required-set distribution total failed")
    if not math.isclose(
        sum(item["candidate_rate"] for item in required_sets),
        1.0,
        abs_tol=1e-5,
    ):
        raise RequirementScoringError("Required-set candidate rates do not sum to one")
    if not math.isclose(
        sum(item["family_macro_rate"] for item in required_sets),
        1.0,
        abs_tol=5e-5,
    ):
        raise RequirementScoringError("Required-set family rates do not sum to one")

    analysis_path = bundle_dir / "full_run_analysis.json"
    report_path = bundle_dir / "full_run_analysis.md"
    review_path = bundle_dir / "full_run_review_queue.csv"
    atomic_write_json(analysis_path, analysis)
    atomic_write_text(report_path, build_analysis_markdown(analysis))
    _atomic_write_csv(
        review_path,
        fieldnames=REVIEW_HEADER,
        rows=review_rows,
    )
    _write_paper_registry(
        paper_registry_path,
        analysis=analysis,
        analysis_path=analysis_path,
        manifest_path=manifest_path,
    )
    return analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze the validated full requirement-scoring run"
    )
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument(
        "--paper-registry",
        type=Path,
        default=DEFAULT_PAPER_REGISTRY,
    )
    parser.add_argument("--expected-candidates", type=int, default=2028)
    parser.add_argument("--expected-families", type=int, default=665)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        analysis = analyze_full_run(
            bundle_dir=args.bundle_dir.resolve(),
            pool_path=args.pool.resolve(),
            trace_path=args.trace.resolve(),
            paper_registry_path=args.paper_registry.resolve(),
            expected_candidate_count=args.expected_candidates,
            expected_family_count=args.expected_families,
        )
    except (RequirementScoringError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 2
    counts = analysis["eligibility"]["counts"]
    print(
        "Plan 03 completed: "
        f"eligible={counts['eligible_without_plan03_review']}, "
        f"review={counts['needs_uet_review']}, "
        f"blocked={counts['blocked']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

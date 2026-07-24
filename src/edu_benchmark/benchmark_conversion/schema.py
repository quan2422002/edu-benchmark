"""Schema contracts and row-level validation for benchmark conversion."""

from __future__ import annotations

import json
from typing import Mapping

CANONICAL_QUALITY_DECISIONS = {"pass", "need_human_review", "failed"}
SPLIT_STRATEGIES = {"final_tutor_response", "each_tutor_turn"}
CONVERSION_STATUSES = {"converted", "need_human_review", "failed"}

CONVERSION_INPUT_COLUMNS = [
    "sample_id",
    "source_batch",
    "source_file",
    "source_row_number",
    "grade",
    "grade_label",
    "stt",
    "lesson",
    "position",
    "question",
    "bloom_level",
    "answer_sgv",
    "raw_dialogue",
    "conversion_dialogue",
    "dialogue_correction_ids",
    "raw_quality_decision",
    "raw_quality_confidence_score",
    "raw_audit_blocking_criterion_ids",
    "raw_audit_blocking_evidence_fragment_ids",
    "raw_audit_all_evidence_fragment_ids",
]

CANDIDATE_SPLIT_COLUMNS = [
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "gold_response",
    "gold_answer",
]

PLAN01_CANDIDATE_SPLIT_COLUMNS = [
    "benchmark_candidate_id",
    "sample_id",
    "source_batch",
    "source_file",
    "source_row_number",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "gold_response",
    "gold_answer",
    "raw_dialogue",
    "conversion_dialogue",
    "dialogue_correction_ids",
    "target_tutor_turn_index",
    "split_strategy",
    "raw_audit_blocking_evidence_fragment_ids",
    "raw_audit_all_evidence_fragment_ids",
]

INPUT_ERROR_COLUMNS = ["sample_id", "source_batch", "severity", "error_code", "message"]
SPLIT_ERROR_COLUMNS = [
    "sample_id",
    "source_batch",
    "severity",
    "error_code",
    "message",
]
TRACE_COLUMNS = [
    "benchmark_candidate_id",
    "sample_id",
    "source_batch",
    "source_file",
    "source_row_number",
    "target_tutor_turn_index",
    "split_strategy",
    "dialogue_correction_ids",
]

PLAN01_TRACE_COLUMNS = [
    "benchmark_candidate_id",
    "sample_id",
    "source_batch",
    "source_file",
    "source_row_number",
    "split_strategy",
    "target_tutor_turn_index",
    "dialogue_correction_ids",
]

CONVERSION_DISPOSITION_COLUMNS = [
    "sample_id",
    "grade",
    "candidate_count",
    "first_target_tutor_turn_index",
    "last_target_tutor_turn_index",
    "conversion_disposition",
    "reason_code",
    "reason",
]


def parse_json_string_list(value: str, *, field_name: str) -> list[str]:
    """Parse a JSON array containing unique non-empty strings."""

    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{field_name} must be a JSON list") from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) or not item for item in parsed):
        raise ValueError(f"{field_name} must contain non-empty strings")
    if len(parsed) != len(set(parsed)):
        raise ValueError(f"{field_name} must not contain duplicate values")
    return parsed


def dump_json_string_list(values: list[str]) -> str:
    """Serialize strings as a stable JSON list."""

    return json.dumps(sorted(set(values)), ensure_ascii=False)


def validate_conversion_input_row(row: Mapping[str, str]) -> list[str]:
    """Return contract violations for one joined pass-input row."""

    errors: list[str] = []
    for field in (
        "sample_id",
        "source_batch",
        "source_file",
        "source_row_number",
        "grade",
        "lesson",
        "question",
        "answer_sgv",
        "raw_dialogue",
        "conversion_dialogue",
    ):
        if not str(row.get(field, "")).strip():
            errors.append(f"missing_core_field:{field}")

    decision = str(row.get("raw_quality_decision", "")).strip()
    if decision not in CANONICAL_QUALITY_DECISIONS:
        errors.append("noncanonical_quality_decision")
    elif decision != "pass":
        errors.append("conversion_input_is_not_pass")

    try:
        parse_json_string_list(
            str(row.get("dialogue_correction_ids", "")),
            field_name="dialogue_correction_ids",
        )
    except ValueError:
        errors.append("invalid_dialogue_correction_ids_json")

    try:
        blocking = parse_json_string_list(
            str(row.get("raw_audit_blocking_evidence_fragment_ids", "")),
            field_name="raw_audit_blocking_evidence_fragment_ids",
        )
        if decision == "pass" and blocking:
            errors.append("pass_has_blocking_evidence")
    except ValueError:
        errors.append("invalid_blocking_evidence_json")

    try:
        all_evidence = parse_json_string_list(
            str(row.get("raw_audit_all_evidence_fragment_ids", "")),
            field_name="raw_audit_all_evidence_fragment_ids",
        )
        if decision == "pass" and not all_evidence:
            errors.append("pass_missing_all_evidence")
    except ValueError:
        errors.append("invalid_all_evidence_json")
    return errors


def validate_candidate_split_row(row: Mapping[str, str]) -> list[str]:
    """Return contract violations for one converted candidate row."""

    errors: list[str] = []
    for field in (
        "benchmark_candidate_id",
        "sample_id",
        "grade",
        "student_prompt",
        "conversation_history",
        "gold_response",
        "gold_answer",
    ):
        if not str(row.get(field, "")).strip():
            errors.append(f"missing_candidate_field:{field}")

    split_strategy = str(row.get("split_strategy", "")).strip()
    if split_strategy and split_strategy not in SPLIT_STRATEGIES:
        errors.append("unknown_split_strategy")
    try:
        history = json.loads(str(row.get("conversation_history", "")))
        if not isinstance(history, list):
            errors.append("conversation_history_is_not_list")
        else:
            previous_index = 1
            previous_role = "student"
            for item in history:
                if not isinstance(item, dict):
                    errors.append("conversation_history_item_is_not_object")
                    break
                if set(item) != {"turn_index", "role", "content"}:
                    errors.append("conversation_history_item_schema_mismatch")
                    break
                turn_index = item.get("turn_index")
                role = item.get("role")
                content = item.get("content")
                if not isinstance(turn_index, int) or turn_index != previous_index + 1:
                    errors.append("conversation_history_turn_index_mismatch")
                    break
                if role not in {"student", "tutor"} or role == previous_role:
                    errors.append("conversation_history_role_sequence_mismatch")
                    break
                if not isinstance(content, str):
                    errors.append("conversation_history_content_is_not_string")
                    break
                previous_index = turn_index
                previous_role = role
    except json.JSONDecodeError:
        errors.append("invalid_conversation_history_json")

    for field in ("dialogue_correction_ids",):
        if field in row:
            try:
                parse_json_string_list(str(row.get(field, "")), field_name=field)
            except ValueError:
                errors.append(f"invalid_json_list:{field}")
    for field in (
        "raw_audit_blocking_evidence_fragment_ids",
        "raw_audit_all_evidence_fragment_ids",
    ):
        if field in row:
            try:
                parse_json_string_list(str(row.get(field, "")), field_name=field)
            except ValueError:
                errors.append(f"invalid_json_list:{field}")
    return errors


def validate_conversion_trace_row(row: Mapping[str, str]) -> list[str]:
    """Return contract violations for one candidate-to-source trace row."""

    errors: list[str] = []
    for field in TRACE_COLUMNS:
        if not str(row.get(field, "")).strip():
            errors.append(f"missing_trace_field:{field}")
    if str(row.get("split_strategy", "")).strip() not in SPLIT_STRATEGIES:
        errors.append("unknown_split_strategy")
    try:
        target_index = int(str(row.get("target_tutor_turn_index", "")).strip())
        if target_index < 2 or target_index % 2:
            errors.append("invalid_target_tutor_turn_index")
    except ValueError:
        errors.append("invalid_target_tutor_turn_index")
    try:
        parse_json_string_list(
            str(row.get("dialogue_correction_ids", "")),
            field_name="dialogue_correction_ids",
        )
    except ValueError:
        errors.append("invalid_dialogue_correction_ids_json")
    return errors


def validate_conversion_disposition_row(
    row: Mapping[str, str],
) -> list[str]:
    """Return contract violations for one raw-sample conversion disposition."""

    errors: list[str] = []
    for field in CONVERSION_DISPOSITION_COLUMNS[:6]:
        if not str(row.get(field, "")).strip():
            errors.append(f"missing_disposition_field:{field}")
    if (
        str(row.get("conversion_disposition", "")).strip()
        not in CONVERSION_STATUSES
    ):
        errors.append("unknown_conversion_disposition")
    try:
        candidate_count = int(str(row.get("candidate_count", "")).strip())
        first_index = int(
            str(row.get("first_target_tutor_turn_index", "")).strip()
        )
        last_index = int(str(row.get("last_target_tutor_turn_index", "")).strip())
        if candidate_count < 1 or first_index != 2 or last_index < first_index:
            errors.append("invalid_candidate_summary_counts")
    except ValueError:
        errors.append("invalid_candidate_summary_counts")
    return errors

"""Schema contracts and row-level validation for benchmark conversion."""

from __future__ import annotations

import json
from typing import Mapping

CANONICAL_QUALITY_DECISIONS = {"pass", "need_human_review", "failed"}
SPLIT_STRATEGIES = {"final_tutor_response"}

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
    "split_strategy",
    "target_tutor_turn_index",
    "dialogue_correction_ids",
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
        "source_file",
        "source_row_number",
        "grade",
        "student_prompt",
        "conversation_history",
        "gold_response",
        "gold_answer",
        "raw_dialogue",
        "conversion_dialogue",
        "target_tutor_turn_index",
        "split_strategy",
    ):
        if not str(row.get(field, "")).strip():
            errors.append(f"missing_candidate_field:{field}")
    if row.get("split_strategy") not in SPLIT_STRATEGIES:
        errors.append("unknown_split_strategy")
    try:
        history = json.loads(str(row.get("conversation_history", "")))
        if not isinstance(history, list):
            errors.append("conversation_history_is_not_list")
    except json.JSONDecodeError:
        errors.append("invalid_conversation_history_json")
    for field in (
        "dialogue_correction_ids",
        "raw_audit_blocking_evidence_fragment_ids",
        "raw_audit_all_evidence_fragment_ids",
    ):
        try:
            parse_json_string_list(str(row.get(field, "")), field_name=field)
        except ValueError:
            errors.append(f"invalid_json_list:{field}")
    return errors

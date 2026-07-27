"""Schemas and validators for Plan-03 provisional specification artifacts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, Sequence

SPEC_STATUSES = {
    "draft",
    "needs_uet_review",
    "needs_hnmu_review",
    "confirmed",
    "retired",
}

CAPABILITY_COLUMNS = [
    "capability_id",
    "capability_name",
    "definition",
    "exclusions",
    "observable_evidence",
    "positive_anchor",
    "mid_anchor",
    "negative_anchor",
    "status",
    "research_ids",
    "research_source_origins",
    "research_support_summary",
    "research_provenance_ref",
    "teacher_decision_needed",
]

TASK_COLUMNS = [
    "task_id",
    "task_name",
    "definition",
    "scope",
    "student_state",
    "primary_tutoring_goal",
    "required_response_evidence",
    "input_requirements",
    "output_requirements",
    "status",
    "research_ids",
    "learning_material_ids",
    "teacher_decision_needed",
]

PRINCIPLE_COLUMNS = [
    "principle_id",
    "principle_name_en",
    "principle_name_vi",
    "definition",
    "include_when",
    "exclude_when",
    "observable_response_evidence",
    "status",
    "research_ids",
    "source_locator",
    "teacher_decision_needed",
]

RUBRIC_DIMENSION_COLUMNS = [
    "dimension_id",
    "dimension_name",
    "capability_id",
    "criterion",
    "observable_evidence",
    "score_levels",
    "applicability_rule",
    "status",
    "research_ids",
    "teacher_decision_needed",
]

PRINCIPLE_RUBRIC_COLUMNS = [
    "rubric_id",
    "principle_id",
    "capability_ids",
    "criterion",
    "observable_evidence",
    "score_levels",
    "status",
    "research_ids",
    "teacher_decision_needed",
]

FLAT_RUBRIC_COLUMNS = [
    "rubric_id",
    "task_id",
    "principle_id",
    "criterion",
    "observable_evidence",
    "score_levels",
    "status",
]

SERIOUS_ERROR_COLUMNS = [
    "error_id",
    "description",
    "suggested_action",
    "affected_rubric_ids",
    "status",
    "confirmation_owner",
]

CAPABILITY_OBSERVABLE_COLUMNS = [
    "evidence_id",
    "capability_id",
    "observable_behavior",
    "unit_of_observation",
    "positive_example",
    "mid_example",
    "negative_example",
    "status",
    "teacher_decision_needed",
]

CAPABILITY_OVERLAP_COLUMNS = [
    "capability_id_a",
    "capability_id_b",
    "relationship",
    "shared_observable_evidence",
    "distinguishing_rule",
    "proposed_action",
    "status",
    "teacher_decision_needed",
]

PROVENANCE_COLUMNS = [
    "item_id",
    "claim_type",
    "research_ids",
    "learning_material_ids",
    "source_locator",
    "inference_note",
    "status",
]

RESEARCH_SOURCE_REGISTRY_COLUMNS = [
    "research_id",
    "source_group",
    "source_group_origin",
    "title",
    "year",
    "venue",
    "publication_status",
    "publication_status_vi",
    "url_or_doi",
    "source_artifact",
    "evidence_location",
    "project_role",
    "limitations",
]

RESEARCH_SUPPORT_MATRIX_COLUMNS = [
    "item_id",
    "research_id",
    "support_level",
    "supported_aspect",
    "evidence_location",
    "project_use",
    "limitations",
    "claim_status",
]

PRINCIPLE_ANNOTATION_COLUMNS = [
    "benchmark_candidate_id",
    "sample_id",
    "student_state_summary",
    "coverage_gap_reason",
    "grounding_effect",
    "grounding_change_reason",
    "coder_id",
    "review_status",
    "adjudication_status",
]

PRINCIPLE_LABEL_COLUMNS = [
    "benchmark_candidate_id",
    "principle_id",
    "selection_rationale",
    "context_evidence",
    "grounding_evidence",
    "coder_id",
    "review_status",
]

PRINCIPLE_CALIBRATION_COLUMNS = [
    "benchmark_candidate_id",
    "ai_principle_set",
    "uet_principle_set",
    "calibration_round",
    "match_status",
    "decision_owner",
    "decision_status",
    "notes",
]

LEGACY_DISPOSITION_COLUMNS = [
    "legacy_item_id",
    "legacy_item_type",
    "proposed_disposition",
    "replacement_item_ids",
    "rationale",
    "status",
    "decision_owner",
]

EVALUATION_CONTEXT_COLUMNS = [
    "benchmark_candidate_id",
    "student_state_summary",
    "primary_tutoring_goal",
    "gold_answer",
    "gold_response_reference",
    "learning_material_ids",
    "evidence_fragment_ids",
    "task_specific_facts",
    "context_review_status",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file."""

    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(
    path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]
) -> None:
    """Write stable UTF-8 CSV output."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def split_ids(value: object) -> list[str]:
    """Split comma/semicolon separated identifiers."""

    text = str(value or "").replace(",", ";")
    return [item.strip() for item in text.split(";") if item.strip()]


def validate_exact_header(path: Path, expected: Sequence[str]) -> list[str]:
    """Return errors when a CSV header or data-row width drifts."""

    errors: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        actual = next(reader, [])
        if actual != list(expected):
            return [f"header_mismatch:{path}:{actual!r}"]
        expected_width = len(expected)
        for row_number, row in enumerate(reader, start=2):
            if len(row) != expected_width:
                errors.append(
                    f"row_width_mismatch:{path}:{row_number}:"
                    f"expected={expected_width}:actual={len(row)}"
                )
    return errors


def _validate_unique_status_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    id_field: str,
    required_fields: Sequence[str],
    allow_confirmed: bool,
) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        item_id = str(row.get(id_field, "")).strip()
        if not item_id:
            errors.append(f"row_{index}:missing:{id_field}")
        elif item_id in seen:
            errors.append(f"row_{index}:duplicate:{id_field}:{item_id}")
        seen.add(item_id)
        for field in required_fields:
            if not str(row.get(field, "")).strip():
                errors.append(f"row_{index}:missing:{field}")
        status = str(row.get("status", "")).strip()
        if status not in SPEC_STATUSES:
            errors.append(f"row_{index}:invalid_status:{status}")
        if status == "confirmed" and not allow_confirmed:
            errors.append(f"row_{index}:confirmed_without_human_authority")
    return errors


def validate_capabilities(
    rows: Sequence[Mapping[str, str]], *, allow_confirmed: bool = False
) -> list[str]:
    """Validate provisional capability definitions."""

    return _validate_unique_status_rows(
        rows,
        id_field="capability_id",
        required_fields=[
            "capability_name",
            "definition",
            "exclusions",
            "observable_evidence",
            "positive_anchor",
            "mid_anchor",
            "negative_anchor",
            "research_source_origins",
            "research_support_summary",
            "research_provenance_ref",
            "teacher_decision_needed",
        ],
        allow_confirmed=allow_confirmed,
    )


def validate_tasks(
    rows: Sequence[Mapping[str, str]], *, allow_confirmed: bool = False
) -> list[str]:
    """Validate candidate task contracts."""

    return _validate_unique_status_rows(
        rows,
        id_field="task_id",
        required_fields=[
            "task_name",
            "definition",
            "scope",
            "student_state",
            "primary_tutoring_goal",
            "required_response_evidence",
            "input_requirements",
            "output_requirements",
            "teacher_decision_needed",
        ],
        allow_confirmed=allow_confirmed,
    )


def validate_principles(
    rows: Sequence[Mapping[str, str]], *, allow_confirmed: bool = False
) -> list[str]:
    """Validate the six provisional KMP pedagogical principles."""

    return _validate_unique_status_rows(
        rows,
        id_field="principle_id",
        required_fields=[
            "principle_name_en",
            "principle_name_vi",
            "definition",
            "include_when",
            "exclude_when",
            "observable_response_evidence",
            "research_ids",
            "source_locator",
            "teacher_decision_needed",
        ],
        allow_confirmed=allow_confirmed,
    )


def validate_current_task_principle_design(
    tasks: Sequence[Mapping[str, str]],
    principles: Sequence[Mapping[str, str]],
) -> list[str]:
    """Fail closed when the active Plan-03 architecture drifts."""

    errors = validate_tasks(tasks)
    errors.extend(validate_principles(principles))
    task_ids = {str(row.get("task_id", "")).strip() for row in tasks}
    if task_ids != {"TASK-NEXT-TUTOR-RESPONSE"} or len(tasks) != 1:
        errors.append("active_design_requires_exactly_one_next_response_task")
    expected_principles = {
        "PRINCIPLE-CHALLENGE",
        "PRINCIPLE-EXPLANATION",
        "PRINCIPLE-MODELLING",
        "PRINCIPLE-PRACTICE",
        "PRINCIPLE-FEEDBACK",
        "PRINCIPLE-QUESTIONING",
    }
    principle_ids = {
        str(row.get("principle_id", "")).strip() for row in principles
    }
    if principle_ids != expected_principles or len(principles) != 6:
        errors.append("active_design_requires_exactly_six_kmp_principles")
    return errors


def validate_rubrics(
    dimensions: Sequence[Mapping[str, str]],
    principle_rubrics: Sequence[Mapping[str, str]],
    *,
    capability_ids: set[str],
    principle_ids: set[str],
    allow_confirmed: bool = False,
) -> list[str]:
    """Validate the capability/principle two-tier rubric contract."""

    errors = _validate_unique_status_rows(
        dimensions,
        id_field="dimension_id",
        required_fields=[
            "dimension_name",
            "capability_id",
            "criterion",
            "observable_evidence",
            "score_levels",
            "applicability_rule",
            "teacher_decision_needed",
        ],
        allow_confirmed=allow_confirmed,
    )
    for index, row in enumerate(dimensions, start=2):
        capability_id = str(row.get("capability_id", "")).strip()
        if capability_id not in capability_ids:
            errors.append(f"dimension_row_{index}:unknown_capability:{capability_id}")

    errors.extend(
        _validate_unique_status_rows(
            principle_rubrics,
            id_field="rubric_id",
            required_fields=[
                "principle_id",
                "capability_ids",
                "criterion",
                "observable_evidence",
                "score_levels",
                "teacher_decision_needed",
            ],
            allow_confirmed=allow_confirmed,
        )
    )
    for index, row in enumerate(principle_rubrics, start=2):
        principle_id = str(row.get("principle_id", "")).strip()
        if principle_id not in principle_ids:
            errors.append(
                f"rubric_row_{index}:unknown_principle:{principle_id}"
            )
        for capability_id in split_ids(row.get("capability_ids", "")):
            if capability_id not in capability_ids:
                errors.append(
                    f"rubric_row_{index}:unknown_capability:{capability_id}"
                )
    return errors


def validate_serious_errors(
    rows: Sequence[Mapping[str, str]],
    *,
    known_rubric_ids: set[str],
    allow_confirmed: bool = False,
) -> list[str]:
    """Validate serious-error references and provisional actions."""

    errors = _validate_unique_status_rows(
        rows,
        id_field="error_id",
        required_fields=[
            "description",
            "suggested_action",
            "affected_rubric_ids",
            "confirmation_owner",
        ],
        allow_confirmed=allow_confirmed,
    )
    allowed_actions = {"review", "score_cap", "fail", "exclude_response"}
    for index, row in enumerate(rows, start=2):
        action = str(row.get("suggested_action", "")).strip()
        if action not in allowed_actions:
            errors.append(f"serious_error_row_{index}:invalid_action:{action}")
        for rubric_id in split_ids(row.get("affected_rubric_ids", "")):
            if rubric_id not in known_rubric_ids:
                errors.append(
                    f"serious_error_row_{index}:unknown_rubric:{rubric_id}"
                )
    return errors


def validate_principle_annotations(
    rows: Sequence[Mapping[str, str]],
    label_rows: Sequence[Mapping[str, str]],
    *,
    expected_candidate_ids: set[str],
    known_principle_ids: set[str],
) -> list[str]:
    """Validate provisional unordered principle sets without claiming agreement."""

    errors: list[str] = []
    seen: set[str] = set()
    labels_by_candidate: dict[str, set[str]] = {
        candidate_id: set() for candidate_id in expected_candidate_ids
    }
    seen_pairs: set[tuple[str, str]] = set()
    for index, row in enumerate(label_rows, start=2):
        candidate_id = str(row.get("benchmark_candidate_id", "")).strip()
        principle_id = str(row.get("principle_id", "")).strip()
        if candidate_id not in expected_candidate_ids:
            errors.append(
                f"principle_label_row_{index}:unknown_candidate:{candidate_id}"
            )
            continue
        if principle_id not in known_principle_ids:
            errors.append(
                f"principle_label_row_{index}:unknown_principle:{principle_id}"
            )
        pair = (candidate_id, principle_id)
        if pair in seen_pairs:
            errors.append(
                f"principle_label_row_{index}:duplicate_candidate_principle"
                f":{candidate_id}:{principle_id}"
            )
        seen_pairs.add(pair)
        labels_by_candidate[candidate_id].add(principle_id)
        for field in (
            "selection_rationale",
            "context_evidence",
            "coder_id",
            "review_status",
        ):
            if not str(row.get(field, "")).strip():
                errors.append(f"principle_label_row_{index}:missing:{field}")
        if str(row.get("review_status", "")).strip() == "confirmed":
            errors.append(
                f"principle_label_row_{index}:agent_coding_cannot_be_confirmed"
            )

    for index, row in enumerate(rows, start=2):
        candidate_id = str(row.get("benchmark_candidate_id", "")).strip()
        if not candidate_id:
            errors.append(f"annotation_row_{index}:missing:benchmark_candidate_id")
        elif candidate_id in seen:
            errors.append(f"annotation_row_{index}:duplicate_candidate:{candidate_id}")
        seen.add(candidate_id)
        coverage_gap = str(row.get("coverage_gap_reason", "")).strip()
        principle_set = labels_by_candidate.get(candidate_id, set())
        if bool(principle_set) == bool(coverage_gap):
            errors.append(
                f"annotation_row_{index}:requires_principle_set_or_coverage_gap"
            )
        for field in (
            "student_state_summary",
            "coder_id",
            "review_status",
        ):
            if not str(row.get(field, "")).strip():
                errors.append(f"annotation_row_{index}:missing:{field}")
        if str(row.get("review_status", "")).strip() == "confirmed":
            errors.append(f"annotation_row_{index}:agent_coding_cannot_be_confirmed")
    if seen != expected_candidate_ids:
        missing = sorted(expected_candidate_ids - seen)
        extra = sorted(seen - expected_candidate_ids)
        if missing:
            errors.append(f"annotations_missing_candidates:{';'.join(missing)}")
        if extra:
            errors.append(f"annotations_extra_candidates:{';'.join(extra)}")
    return errors


def validate_evaluation_context(
    rows: Sequence[Mapping[str, str]],
    *,
    expected_candidate_ids: set[str],
) -> list[str]:
    """Validate candidate facts while keeping them separate from rubric criteria."""

    errors: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        candidate_id = str(row.get("benchmark_candidate_id", "")).strip()
        if not candidate_id:
            errors.append(f"context_row_{index}:missing:benchmark_candidate_id")
        elif candidate_id in seen:
            errors.append(f"context_row_{index}:duplicate_candidate:{candidate_id}")
        seen.add(candidate_id)
        for field in (
            "student_state_summary",
            "primary_tutoring_goal",
            "gold_answer",
            "gold_response_reference",
            "task_specific_facts",
            "context_review_status",
        ):
            if not str(row.get(field, "")).strip():
                errors.append(f"context_row_{index}:missing:{field}")
        if str(row.get("context_review_status", "")).strip() == "confirmed":
            errors.append(f"context_row_{index}:agent_context_cannot_be_confirmed")
        unexpected_criterion_fields = {
            key for key in row if "criterion" in key.lower() or "rubric" in key.lower()
        }
        if unexpected_criterion_fields:
            errors.append(
                f"context_row_{index}:rubric_semantics_in_context:"
                + ";".join(sorted(unexpected_criterion_fields))
            )
    if seen != expected_candidate_ids:
        missing = sorted(expected_candidate_ids - seen)
        extra = sorted(seen - expected_candidate_ids)
        if missing:
            errors.append(f"context_missing_candidates:{';'.join(missing)}")
        if extra:
            errors.append(f"context_extra_candidates:{';'.join(extra)}")
    return errors

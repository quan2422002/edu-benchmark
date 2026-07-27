"""Validation and publication for provisional Plan-03 Workstreams B-D."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from itertools import combinations
from pathlib import Path
from typing import Iterable

from .manifest import sha256_file
from .provenance import validate_provenance_ids
from .rubrics import flatten_two_tier_rubrics
from .schema import (
    CAPABILITY_COLUMNS,
    CAPABILITY_OBSERVABLE_COLUMNS,
    CAPABILITY_OVERLAP_COLUMNS,
    EVALUATION_CONTEXT_COLUMNS,
    FLAT_RUBRIC_COLUMNS,
    LEGACY_DISPOSITION_COLUMNS,
    PROVENANCE_COLUMNS,
    RESEARCH_SOURCE_REGISTRY_COLUMNS,
    RESEARCH_SUPPORT_MATRIX_COLUMNS,
    RUBRIC_DIMENSION_COLUMNS,
    SERIOUS_ERROR_COLUMNS,
    PRINCIPLE_ANNOTATION_COLUMNS,
    PRINCIPLE_LABEL_COLUMNS,
    PRINCIPLE_CALIBRATION_COLUMNS,
    PRINCIPLE_COLUMNS,
    TASK_COLUMNS,
    PRINCIPLE_RUBRIC_COLUMNS,
    read_csv_rows,
    validate_capabilities,
    validate_evaluation_context,
    validate_exact_header,
    validate_rubrics,
    validate_serious_errors,
    validate_current_task_principle_design,
    validate_principle_annotations,
    validate_tasks,
    write_csv_rows,
)

CSV_SCHEMAS = {
    "construct_v1_draft/tutor_capabilities.csv": CAPABILITY_COLUMNS,
    "construct_v1_draft/capability_observable_evidence.csv": (
        CAPABILITY_OBSERVABLE_COLUMNS
    ),
    "construct_v1_draft/capability_overlap_matrix.csv": CAPABILITY_OVERLAP_COLUMNS,
    "construct_v1_draft/capability_research_provenance.csv": PROVENANCE_COLUMNS,
    "construct_v1_draft/research_source_registry.csv": (
        RESEARCH_SOURCE_REGISTRY_COLUMNS
    ),
    "construct_v1_draft/research_support_matrix.csv": (
        RESEARCH_SUPPORT_MATRIX_COLUMNS
    ),
    "task_discovery/benchmark_tasks.csv": TASK_COLUMNS,
    "task_discovery/pedagogical_principles.csv": PRINCIPLE_COLUMNS,
    "task_discovery/principle_annotations.csv": PRINCIPLE_ANNOTATION_COLUMNS,
    "task_discovery/principle_annotation_labels.csv": PRINCIPLE_LABEL_COLUMNS,
    "task_discovery/principle_calibration.csv": PRINCIPLE_CALIBRATION_COLUMNS,
    "task_discovery/principle_coverage_gaps.csv": PRINCIPLE_ANNOTATION_COLUMNS,
    "task_discovery/legacy_spec_dispositions.csv": LEGACY_DISPOSITION_COLUMNS,
    "rubric_v1_draft/rubric_dimensions.csv": RUBRIC_DIMENSION_COLUMNS,
    "rubric_v1_draft/principle_rubrics.csv": PRINCIPLE_RUBRIC_COLUMNS,
    "rubric_v1_draft/serious_errors.csv": SERIOUS_ERROR_COLUMNS,
    "rubric_v1_draft/candidate_evaluation_context.csv": EVALUATION_CONTEXT_COLUMNS,
    "rubric_v1_draft/rubric_research_provenance.csv": PROVENANCE_COLUMNS,
}

MARKDOWN_FILES = (
    "construct_v1_draft/tutor_capability_model.md",
    "construct_v1_draft/capability_research_basis.md",
    "construct_v1_draft/capability_open_questions.md",
    "task_discovery/task_discovery_codebook.md",
    "task_discovery/principle_coverage_decisions.md",
    "rubric_v1_draft/rubric_anchors.md",
    "rubric_v1_draft/rubric_open_questions.md",
)



def _ids(rows: Iterable[dict[str, str]], field: str) -> set[str]:
    return {str(row.get(field, "")).strip() for row in rows if row.get(field)}


def _known_research_ids(experiment_root: Path) -> set[str]:
    files_and_fields = (
        (
            experiment_root
            / "literature_notes/plan03_measurement_foundations/source_registry.csv",
            "source_id",
        ),
        (
            experiment_root
            / "literature_notes/pre_plan03_task_rubric_review/evidence_matrix.csv",
            "record_id",
        ),
    )
    known: set[str] = set()
    for path, field in files_and_fields:
        known.update(_ids(read_csv_rows(path), field))
    return known


def _known_learning_material_ids(repo_root: Path) -> set[str]:
    known = _ids(
        read_csv_rows(
            repo_root
            / "shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv"
        ),
        "learning_material_id",
    )
    known.update(
        _ids(
            read_csv_rows(
                repo_root
                / "shared/learning_resources/fragments/learning_resource_fragments.csv"
            ),
            "learning_material_id",
        )
    )
    return known


def validate_specialist_draft(
    repo_root: Path,
    experiment_root: Path,
    draft_root: Path,
) -> tuple[list[str], dict[str, object]]:
    """Validate the full provisional A-D bundle before publication."""

    errors: list[str] = []
    for relative_path, header in CSV_SCHEMAS.items():
        path = draft_root / relative_path
        if not path.is_file():
            errors.append(f"missing_file:{relative_path}")
            continue
        errors.extend(validate_exact_header(path, header))
    for relative_path in MARKDOWN_FILES:
        path = draft_root / relative_path
        if not path.is_file():
            errors.append(f"missing_file:{relative_path}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty_file:{relative_path}")
    if errors:
        return errors, {}

    capabilities = read_csv_rows(
        draft_root / "construct_v1_draft/tutor_capabilities.csv"
    )
    tasks = read_csv_rows(draft_root / "task_discovery/benchmark_tasks.csv")
    principles = read_csv_rows(
        draft_root / "task_discovery/pedagogical_principles.csv"
    )
    annotations = read_csv_rows(
        draft_root / "task_discovery/principle_annotations.csv"
    )
    annotation_labels = read_csv_rows(
        draft_root / "task_discovery/principle_annotation_labels.csv"
    )
    calibration = read_csv_rows(
        draft_root / "task_discovery/principle_calibration.csv"
    )
    coverage_gaps = read_csv_rows(
        draft_root / "task_discovery/principle_coverage_gaps.csv"
    )
    dimensions = read_csv_rows(
        draft_root / "rubric_v1_draft/rubric_dimensions.csv"
    )
    principle_rubrics = read_csv_rows(
        draft_root / "rubric_v1_draft/principle_rubrics.csv"
    )
    serious_errors = read_csv_rows(
        draft_root / "rubric_v1_draft/serious_errors.csv"
    )
    contexts = read_csv_rows(
        draft_root / "rubric_v1_draft/candidate_evaluation_context.csv"
    )
    expected_candidate_ids = _ids(
        read_csv_rows(
            experiment_root
            / "outputs/benchmark_specification/task_discovery/task_discovery_sample.csv"
        ),
        "benchmark_candidate_id",
    )
    capability_ids = _ids(capabilities, "capability_id")
    principle_ids = _ids(principles, "principle_id")
    errors.extend(validate_capabilities(capabilities))
    errors.extend(validate_current_task_principle_design(tasks, principles))
    errors.extend(
        validate_principle_annotations(
            annotations,
            annotation_labels,
            expected_candidate_ids=expected_candidate_ids,
            known_principle_ids=principle_ids,
        )
    )
    expected_gap_ids = {
        row["benchmark_candidate_id"]
        for row in annotations
        if str(row.get("coverage_gap_reason", "")).strip()
    }
    actual_gap_ids = _ids(coverage_gaps, "benchmark_candidate_id")
    if actual_gap_ids != expected_gap_ids:
        errors.append("principle_coverage_gap_export_does_not_match_annotations")
    errors.extend(
        validate_rubrics(
            dimensions,
            principle_rubrics,
            capability_ids=capability_ids,
            principle_ids=principle_ids,
        )
    )
    known_rubric_ids = _ids(dimensions, "dimension_id") | _ids(
        principle_rubrics, "rubric_id"
    )
    errors.extend(
        validate_serious_errors(
            serious_errors,
            known_rubric_ids=known_rubric_ids,
        )
    )
    errors.extend(
        validate_evaluation_context(
            contexts,
            expected_candidate_ids=expected_candidate_ids,
        )
    )

    known_research_ids = _known_research_ids(experiment_root)
    known_learning_ids = _known_learning_material_ids(repo_root)
    capability_provenance = read_csv_rows(
        draft_root / "construct_v1_draft/capability_research_provenance.csv"
    )
    rubric_provenance = read_csv_rows(
        draft_root / "rubric_v1_draft/rubric_research_provenance.csv"
    )
    errors.extend(
        validate_provenance_ids(
            capability_provenance,
            known_item_ids=capability_ids,
            known_research_ids=known_research_ids,
            known_learning_material_ids=known_learning_ids,
        )
    )
    errors.extend(
        validate_provenance_ids(
            rubric_provenance,
            known_item_ids=known_rubric_ids | _ids(serious_errors, "error_id"),
            known_research_ids=known_research_ids,
            known_learning_material_ids=known_learning_ids,
        )
    )
    flat = flatten_two_tier_rubrics(dimensions, principle_rubrics, tasks)
    summary = {
        "capability_count": len(capabilities),
        "task_count": len(tasks),
        "principle_count": len(principles),
        "annotation_count": len(annotations),
        "principle_label_count": len(annotation_labels),
        "coverage_gap_count": len(coverage_gaps),
        "shared_dimension_count": len(dimensions),
        "principle_rubric_count": len(principle_rubrics),
        "flattened_rubric_count": len(flat),
        "serious_error_count": len(serious_errors),
        "evaluation_context_count": len(contexts),
        "calibration_row_count": len(calibration),
    }
    return errors, summary


def validate_capability_draft(
    repo_root: Path,
    experiment_root: Path,
    draft_root: Path,
) -> tuple[list[str], dict[str, object]]:
    """Validate Workstream-B artifacts without requiring Workstreams C-D."""

    relative_schemas = {
        "tutor_capabilities.csv": CAPABILITY_COLUMNS,
        "capability_observable_evidence.csv": CAPABILITY_OBSERVABLE_COLUMNS,
        "capability_overlap_matrix.csv": CAPABILITY_OVERLAP_COLUMNS,
        "capability_research_provenance.csv": PROVENANCE_COLUMNS,
        "research_source_registry.csv": RESEARCH_SOURCE_REGISTRY_COLUMNS,
        "research_support_matrix.csv": RESEARCH_SUPPORT_MATRIX_COLUMNS,
    }
    required_markdown = (
        "tutor_capability_model.md",
        "capability_research_basis.md",
        "capability_open_questions.md",
    )
    errors: list[str] = []
    for relative_path, header in relative_schemas.items():
        path = draft_root / relative_path
        if not path.is_file():
            errors.append(f"missing_file:{relative_path}")
            continue
        errors.extend(validate_exact_header(path, header))
    for relative_path in required_markdown:
        path = draft_root / relative_path
        if not path.is_file():
            errors.append(f"missing_file:{relative_path}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty_file:{relative_path}")
    if errors:
        return errors, {}

    capabilities = read_csv_rows(draft_root / "tutor_capabilities.csv")
    observable = read_csv_rows(
        draft_root / "capability_observable_evidence.csv"
    )
    overlaps = read_csv_rows(draft_root / "capability_overlap_matrix.csv")
    provenance = read_csv_rows(
        draft_root / "capability_research_provenance.csv"
    )
    source_registry = read_csv_rows(draft_root / "research_source_registry.csv")
    support_matrix = read_csv_rows(draft_root / "research_support_matrix.csv")
    capability_ids = _ids(capabilities, "capability_id")
    errors.extend(validate_capabilities(capabilities))
    observable_capability_ids = [
        str(row.get("capability_id", "")).strip() for row in observable
    ]
    unknown_observable = sorted(set(observable_capability_ids) - capability_ids)
    if unknown_observable:
        errors.append(
            "observable_unknown_capabilities:" + ";".join(unknown_observable)
        )
    if set(observable_capability_ids) != capability_ids:
        errors.append("observable_capability_coverage_mismatch")
    evidence_ids = [
        str(row.get("evidence_id", "")).strip() for row in observable
    ]
    if len(evidence_ids) != len(set(evidence_ids)) or not all(evidence_ids):
        errors.append("observable_evidence_ids_not_unique_and_complete")
    expected_pairs = {
        tuple(sorted(pair)) for pair in combinations(capability_ids, 2)
    }
    actual_pairs = [
        tuple(
            sorted(
                (
                    str(row.get("capability_id_a", "")).strip(),
                    str(row.get("capability_id_b", "")).strip(),
                )
            )
        )
        for row in overlaps
    ]
    if set(actual_pairs) != expected_pairs or len(actual_pairs) != len(
        expected_pairs
    ):
        errors.append("capability_overlap_pairs_incomplete_or_duplicated")
    for index, pair in enumerate(actual_pairs, start=2):
        if pair[0] == pair[1] or not set(pair) <= capability_ids:
            errors.append(f"overlap_row_{index}:invalid_capability_pair")

    known_research_ids = _known_research_ids(experiment_root)
    known_learning_ids = _known_learning_material_ids(repo_root)
    errors.extend(
        validate_provenance_ids(
            provenance,
            known_item_ids=capability_ids,
            known_research_ids=known_research_ids,
            known_learning_material_ids=known_learning_ids,
        )
    )
    if _ids(provenance, "item_id") != capability_ids:
        errors.append("capability_provenance_coverage_mismatch")
    registry_ids = _ids(source_registry, "research_id")
    if len(source_registry) != len(registry_ids):
        errors.append("research_source_registry_ids_not_unique_and_complete")
    for index, row in enumerate(source_registry, start=2):
        for field in RESEARCH_SOURCE_REGISTRY_COLUMNS:
            if not str(row.get(field, "")).strip():
                errors.append(
                    f"research_source_registry_row_{index}:missing:{field}"
                )
    used_research_ids = {
        research_id
        for row in capabilities
        for raw_id in str(row.get("research_ids", "")).split(";")
        if (research_id := raw_id.strip())
    }
    model_support_ids = {
        row["research_id"]
        for row in support_matrix
        if row.get("item_id") == "MODEL-CAPABILITY-V1"
    }
    if registry_ids != used_research_ids | model_support_ids:
        errors.append("research_source_registry_coverage_mismatch")
    support_pairs = {
        (row.get("item_id", ""), row.get("research_id", ""))
        for row in support_matrix
    }
    if len(support_pairs) != len(support_matrix):
        errors.append("research_support_pairs_not_unique")
    for capability in capabilities:
        capability_id = capability["capability_id"]
        for raw_id in str(capability["research_ids"]).split(";"):
            research_id = raw_id.strip()
            if not research_id:
                continue
            if (capability_id, research_id) not in support_pairs:
                errors.append(
                    f"missing_capability_research_support:{capability_id}:{research_id}"
                )
    for index, row in enumerate(support_matrix, start=2):
        for field in RESEARCH_SUPPORT_MATRIX_COLUMNS:
            if not str(row.get(field, "")).strip():
                errors.append(
                    f"research_support_row_{index}:missing:{field}"
                )
        if row.get("research_id") not in registry_ids:
            errors.append(
                f"research_support_row_{index}:unknown_research_id:"
                f"{row.get('research_id', '')}"
            )
        if row.get("item_id") not in capability_ids | {"MODEL-CAPABILITY-V1"}:
            errors.append(
                f"research_support_row_{index}:unknown_item_id:"
                f"{row.get('item_id', '')}"
            )
        if row.get("claim_status") not in {"evidence", "inference"}:
            errors.append(
                f"research_support_row_{index}:invalid_claim_status:"
                f"{row.get('claim_status', '')}"
            )
    source_group_by_id = {
        row["research_id"]: row["source_group"] for row in source_registry
    }
    for capability in capabilities:
        for research_id in str(capability["research_ids"]).split(";"):
            research_id = research_id.strip()
            if (
                research_id
                and source_group_by_id.get(research_id)
                == "nền_tảng_đo_lường"
            ):
                errors.append(
                    "measurement_method_source_must_not_directly_support_"
                    f"capability:{capability['capability_id']}:{research_id}"
                )
    capability_by_id = {
        row["capability_id"]: row for row in capabilities
    }
    for row in provenance:
        item_id = row["item_id"]
        if {
            research_id.strip()
            for research_id in str(row["research_ids"]).split(";")
            if research_id.strip()
        } != {
            research_id.strip()
            for research_id in str(
                capability_by_id[item_id]["research_ids"]
            ).split(";")
            if research_id.strip()
        }:
            errors.append(f"capability_research_ids_mismatch:{item_id}")
    summary = {
        "capability_count": len(capabilities),
        "observable_evidence_count": len(observable),
        "overlap_pair_count": len(overlaps),
        "provenance_count": len(provenance),
        "research_source_count": len(source_registry),
        "research_support_link_count": len(support_matrix),
        "confirmed_count": sum(
            row.get("status") == "confirmed" for row in capabilities
        ),
    }
    return errors, summary


def publish_capability_draft(
    repo_root: Path,
    experiment_root: Path,
    draft_root: Path,
) -> dict[str, object]:
    """Publish only the validated Workstream-B capability bundle."""

    errors, summary = validate_capability_draft(
        repo_root,
        experiment_root,
        draft_root,
    )
    if errors:
        raise ValueError("\n".join(errors))
    output_root = (
        experiment_root / "outputs/benchmark_specification/construct_v1_draft"
    )
    files = (
        "tutor_capability_model.md",
        "capability_research_basis.md",
        "tutor_capabilities.csv",
        "capability_observable_evidence.csv",
        "capability_overlap_matrix.csv",
        "capability_research_provenance.csv",
        "research_source_registry.csv",
        "research_support_matrix.csv",
        "capability_open_questions.md",
    )
    output_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".plan03_b_publish_", dir=output_root.parent
    ) as temporary:
        staging_root = Path(temporary)
        for filename in files:
            shutil.copy2(draft_root / filename, staging_root / filename)
        for filename in files:
            output_root.mkdir(parents=True, exist_ok=True)
            os.replace(staging_root / filename, output_root / filename)

    manifest = {
        "publication_id": "plan03-workstream-b-provisional-v1",
        "status": "uet_provisional_approved_for_task_discovery",
        "approval_scope": "workstream_c_task_discovery_only",
        "uet_decision_date": "2026-07-26",
        "hnmu_review_status": (
            "deferred_to_integrated_capability_task_rubric_example_review_"
            "after_workstream_d"
        ),
        "workstreams_completed": ["A", "B"],
        "next_workstream_status": "ready_for_workstream_c",
        "workstreams_ready": ["C"],
        "workstreams_not_executed": ["C", "D", "E", "F", "G"],
        "staged_task_discovery_draft_status": (
            "excluded_from_workstream_b_publication_and_not_yet_accepted"
        ),
        "summary": summary,
        "files": [
            {
                "path": str((output_root / filename).relative_to(repo_root)),
                "sha256": sha256_file(output_root / filename),
            }
            for filename in files
        ],
    }
    manifest_path = (
        experiment_root
        / "outputs/benchmark_specification/plan03_workstream_b_publication_manifest.json"
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def publish_specialist_draft(
    repo_root: Path,
    experiment_root: Path,
    draft_root: Path,
) -> dict[str, object]:
    """Publish a validated provisional draft and write a completion manifest last."""

    errors, summary = validate_specialist_draft(
        repo_root,
        experiment_root,
        draft_root,
    )
    if errors:
        raise ValueError("\n".join(errors))
    output_root = experiment_root / "outputs/benchmark_specification"
    dimensions = read_csv_rows(
        draft_root / "rubric_v1_draft/rubric_dimensions.csv"
    )
    principle_rubrics = read_csv_rows(
        draft_root / "rubric_v1_draft/principle_rubrics.csv"
    )
    tasks = read_csv_rows(draft_root / "task_discovery/benchmark_tasks.csv")
    with tempfile.TemporaryDirectory(
        prefix=".plan03_publish_", dir=output_root
    ) as temporary:
        staging_root = Path(temporary)
        staged_files: list[tuple[Path, Path]] = []
        for relative_path in (*CSV_SCHEMAS, *MARKDOWN_FILES):
            source = draft_root / relative_path
            staged = staging_root / relative_path
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, staged)
            staged_files.append((staged, output_root / relative_path))
        flat_path = staging_root / "rubric_v1_draft/rubrics.csv"
        write_csv_rows(
            flat_path,
            FLAT_RUBRIC_COLUMNS,
            flatten_two_tier_rubrics(dimensions, principle_rubrics, tasks),
        )
        staged_files.append(
            (flat_path, output_root / "rubric_v1_draft/rubrics.csv")
        )
        for staged, target in staged_files:
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, target)

    manifest_path = output_root / "plan03_a_to_d_publication_manifest.json"
    measurement_root = (
        experiment_root / "literature_notes/plan03_measurement_foundations"
    )
    published_paths = [
        path
        for path in output_root.rglob("*")
        if path.is_file()
        and "specialist_draft" not in path.parts
        and path != manifest_path
    ]
    published_paths.extend(
        path for path in measurement_root.glob("*") if path.is_file()
    )
    published = sorted(
        str(path.relative_to(repo_root)) for path in published_paths
    )
    manifest = {
        "publication_id": "plan03-a-to-d-provisional-v1",
        "status": "needs_hnmu_and_uet_review",
        "workstreams": ["A", "B", "C", "D"],
        "workstreams_not_executed": ["E", "F", "G"],
        "summary": summary,
        "files": [
            {
                "path": path,
                "sha256": sha256_file(repo_root / path),
            }
            for path in published
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest

"""Fail-closed validation for the Plan 05 configuration bundle."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .config_builder import (
    INSTRUCTION_FIELDS,
    MODEL_FIELDS,
    PRINCIPLE_ORDER,
)


class EvaluationValidationError(RuntimeError):
    """Raised when an evaluation configuration violates its contract."""


EXPECTED_FILES = {
    "evaluation_protocol.md",
    "model_registry.csv",
    "instruction_registry.csv",
    "evaluation_schema.json",
}

FORBIDDEN_INSTRUCTION_TERMS = {
    "gold_answer",
    "gold_response",
    "benchmark_candidate_id",
    "sample_id",
    "requirement_score",
}


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_evaluation_config(output_dir: Path) -> dict[str, Any]:
    """Validate exact outputs, panel coverage, instructions and schema."""

    found = {
        path.name
        for path in output_dir.iterdir()
        if path.is_file() and not path.name.startswith(".")
    }
    if found != EXPECTED_FILES:
        raise EvaluationValidationError(
            f"expected exactly {sorted(EXPECTED_FILES)}, found {sorted(found)}"
        )

    model_header, models = _read_csv(output_dir / "model_registry.csv")
    if model_header != list(MODEL_FIELDS):
        raise EvaluationValidationError("model registry header mismatch")
    if len(models) != 4:
        raise EvaluationValidationError("model registry must contain four rows")
    classes = {row["model_class"] for row in models}
    required_classes = {
        "closed_general",
        "open_weight_general",
        "specialized_education",
    }
    if not required_classes <= classes:
        raise EvaluationValidationError("required model classes are missing")
    if sum(row["selection_status"] == "provisional_core" for row in models) != 2:
        raise EvaluationValidationError(
            "closed and open core rows must be provisional_core"
        )

    instruction_header, instructions = _read_csv(
        output_dir / "instruction_registry.csv"
    )
    if instruction_header != list(INSTRUCTION_FIELDS):
        raise EvaluationValidationError("instruction registry header mismatch")
    if len(instructions) != 7:
        raise EvaluationValidationError(
            "instruction registry must contain one general and six principles"
        )
    if sum(row["instruction_type"] == "general" for row in instructions) != 1:
        raise EvaluationValidationError("exactly one general instruction required")
    principle_ids = {
        row["principle_id"]
        for row in instructions
        if row["instruction_type"] == "principle"
    }
    if principle_ids != set(PRINCIPLE_ORDER):
        raise EvaluationValidationError("principle instruction IDs mismatch")
    bundle_versions = {
        row["instruction_bundle_version"] for row in instructions
    }
    bundle_hashes = {
        row["instruction_bundle_sha256"] for row in instructions
    }
    if len(bundle_versions) != 1 or not next(iter(bundle_versions)):
        raise EvaluationValidationError(
            "instruction registry must use one non-empty bundle version"
        )
    if len(bundle_hashes) != 1:
        raise EvaluationValidationError(
            "instruction registry must use one bundle hash"
        )
    bundle_hash = next(iter(bundle_hashes))
    if len(bundle_hash) != 64 or any(
        character not in "0123456789abcdef"
        for character in bundle_hash
    ):
        raise EvaluationValidationError(
            "instruction bundle SHA-256 is invalid"
        )
    for row in instructions:
        lowered = row["instruction_vi"].casefold()
        leaked = sorted(
            term for term in FORBIDDEN_INSTRUCTION_TERMS if term in lowered
        )
        if leaked:
            raise EvaluationValidationError(
                f"{row['instruction_id']} leaks evaluator terms: {leaked}"
            )
        if row["status"] != "needs_hnmu_review":
            raise EvaluationValidationError(
                "instructions must remain provisional for HNMU review"
            )
        if row["instruction_type"] == "principle":
            if not row["principle_name_vi"].strip():
                raise EvaluationValidationError(
                    "principle instructions require Vietnamese names"
                )
            expected_prefix = (
                f"### Yêu cầu sư phạm: {row['principle_name_vi']}\n"
            )
            if not row["instruction_vi"].startswith(expected_prefix):
                raise EvaluationValidationError(
                    f"{row['instruction_id']} must start with its "
                    "Vietnamese pedagogical-requirement name"
                )
            for label in (
                "- Mục tiêu:",
                "- Hành vi cần thể hiện:",
                "- Cần tránh:",
                "- Bảo toàn quyền chủ động:",
            ):
                if f"\n{label}" not in row["instruction_vi"]:
                    raise EvaluationValidationError(
                        f"{row['instruction_id']} is missing {label}"
                    )

    schema = json.loads(
        (output_dir / "evaluation_schema.json").read_text(encoding="utf-8")
    )
    definitions = schema.get("$defs", {})
    required_definitions = {
        "usage",
        "required_principle_set",
        "target_response",
        "criterion_judgment",
        "serious_error_judgment",
        "evaluation_record",
    }
    if not required_definitions <= definitions.keys():
        raise EvaluationValidationError("evaluation schema definitions missing")
    selection_policy = schema.get("x-principle-selection-policy", {})
    if selection_policy != {
        "source_field": "requirement_score",
        "operator": ">=",
        "threshold": 4,
        "score_3_selected": False,
    }:
        raise EvaluationValidationError(
            "evaluation schema principle-selection policy mismatch"
        )
    target_required = set(
        definitions["target_response"].get("required", [])
    )
    evaluation_required = set(
        definitions["evaluation_record"].get("required", [])
    )
    if (
        "required_principle_ids" not in target_required
        or "instruction_bundle_version" not in target_required
        or "instruction_bundle_sha256" not in target_required
        or "required_principle_ids" not in evaluation_required
    ):
        raise EvaluationValidationError(
            "target and evaluation records must expose required principles"
        )
    if not definitions["evaluation_record"].get("allOf"):
        raise EvaluationValidationError(
            "evaluation schema must bind applicable rubrics to required principles"
        )
    criterion_ids = set(
        definitions["criterion_judgment"]["properties"]["rubric_id"]["enum"]
    )
    error_ids = set(
        definitions["serious_error_judgment"]["properties"]["error_id"]["enum"]
    )
    if len(criterion_ids) != 22 or len(error_ids) != 6:
        raise EvaluationValidationError(
            "evaluation schema must expose 22 rubrics and six serious errors"
        )
    evaluation_description = definitions["evaluation_record"].get(
        "description", ""
    )
    if "One judge call" not in evaluation_description:
        raise EvaluationValidationError(
            "schema must bundle all criteria into one judge call"
        )

    protocol = (output_dir / "evaluation_protocol.md").read_text(
        encoding="utf-8"
    )
    for marker in ("250 USD", "1.400", "native", "một judge call"):
        if marker.casefold() not in protocol.casefold():
            raise EvaluationValidationError(
                f"evaluation protocol is missing marker: {marker}"
            )
    return {
        "valid": True,
        "model_count": len(models),
        "instruction_count": len(instructions),
        "rubric_count": len(criterion_ids),
        "serious_error_count": len(error_ids),
        "output_files": sorted(found),
    }

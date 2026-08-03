"""Load and validate versioned tutor-instruction bundles."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from string import Formatter
from typing import Any

import yaml


class InstructionBundleError(ValueError):
    """Raised when a tutor-instruction bundle violates its contract."""


PRINCIPLE_ORDER = (
    "PRINCIPLE-CHALLENGE",
    "PRINCIPLE-EXPLANATION",
    "PRINCIPLE-MODELLING",
    "PRINCIPLE-PRACTICE",
    "PRINCIPLE-FEEDBACK",
    "PRINCIPLE-QUESTIONING",
)

SYSTEM_TEMPLATE_FIELDS = {
    "general_instruction",
    "grade",
    "lesson",
    "source_question",
    "principle_blocks",
    "response_style_instruction",
}

PRINCIPLE_TEMPLATE_FIELDS = {
    "principle_name_vi",
    "objective",
    "expected_behavior",
    "avoid",
    "preserve_student_agency",
}

PRINCIPLE_FIELDS = (
    "principle_id",
    "principle_name_vi",
    "objective",
    "expected_behavior",
    "avoid",
    "preserve_student_agency",
)


@dataclass(frozen=True)
class PrincipleInstruction:
    """One structured pedagogical requirement."""

    principle_id: str
    principle_name_vi: str
    objective: str
    expected_behavior: str
    avoid: str
    preserve_student_agency: str


@dataclass(frozen=True)
class InstructionBundle:
    """Validated, versioned source for tutor system instructions."""

    schema_version: str
    bundle_id: str
    bundle_version: str
    prompt_language: str
    general_instruction: str
    response_style_instruction: str
    system_instruction_template: str
    principle_instruction_template: str
    principles: tuple[PrincipleInstruction, ...]
    source_path: Path
    sha256: str

    @property
    def principles_by_id(self) -> dict[str, PrincipleInstruction]:
        """Return principle definitions indexed by canonical ID."""

        return {
            principle.principle_id: principle
            for principle in self.principles
        }

    def render_principle(self, principle_id: str) -> str:
        """Render one named, multiline pedagogical requirement."""

        try:
            principle = self.principles_by_id[principle_id]
        except KeyError as exc:
            raise InstructionBundleError(
                f"unknown principle ID: {principle_id}"
            ) from exc
        return self.principle_instruction_template.format(
            principle_name_vi=principle.principle_name_vi,
            objective=principle.objective,
            expected_behavior=principle.expected_behavior,
            avoid=principle.avoid,
            preserve_student_agency=principle.preserve_student_agency,
        ).strip()


def _mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InstructionBundleError(f"{field_name} must be a mapping")
    return value


def _nonempty_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InstructionBundleError(f"{field_name} must be non-empty text")
    return value.strip()


def _template_fields(template: str) -> set[str]:
    try:
        return {
            field_name
            for _, field_name, _, _ in Formatter().parse(template)
            if field_name is not None
        }
    except ValueError as exc:
        raise InstructionBundleError("invalid format template") from exc


def load_instruction_bundle(path: Path) -> InstructionBundle:
    """Load one immutable bundle and validate all rendering inputs."""

    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise InstructionBundleError(
            f"cannot read instruction bundle: {path}"
        ) from exc
    try:
        data = _mapping(
            yaml.safe_load(raw_bytes.decode("utf-8")),
            "instruction bundle",
        )
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise InstructionBundleError(
            f"invalid UTF-8 YAML instruction bundle: {path}"
        ) from exc

    system_template = _nonempty_text(
        data.get("system_instruction_template"),
        "system_instruction_template",
    )
    principle_template = _nonempty_text(
        data.get("principle_instruction_template"),
        "principle_instruction_template",
    )
    if _template_fields(system_template) != SYSTEM_TEMPLATE_FIELDS:
        raise InstructionBundleError(
            "system template placeholders do not match the contract"
        )
    if _template_fields(principle_template) != PRINCIPLE_TEMPLATE_FIELDS:
        raise InstructionBundleError(
            "principle template placeholders do not match the contract"
        )

    raw_principles = data.get("principles")
    if not isinstance(raw_principles, list):
        raise InstructionBundleError("principles must be a list")
    principles: list[PrincipleInstruction] = []
    for index, raw_principle in enumerate(raw_principles):
        principle_data = _mapping(
            raw_principle, f"principles[{index}]"
        )
        unknown_fields = set(principle_data) - set(PRINCIPLE_FIELDS)
        missing_fields = set(PRINCIPLE_FIELDS) - set(principle_data)
        if unknown_fields or missing_fields:
            raise InstructionBundleError(
                f"principles[{index}] field mismatch; missing="
                f"{sorted(missing_fields)}, unknown={sorted(unknown_fields)}"
            )
        values = {
            field_name: _nonempty_text(
                principle_data[field_name],
                f"principles[{index}].{field_name}",
            )
            for field_name in PRINCIPLE_FIELDS
        }
        principles.append(PrincipleInstruction(**values))

    principle_ids = tuple(
        principle.principle_id for principle in principles
    )
    if principle_ids != PRINCIPLE_ORDER:
        raise InstructionBundleError(
            "principles must contain the six canonical IDs in fixed order"
        )
    principle_names = [
        principle.principle_name_vi for principle in principles
    ]
    if len(principle_names) != len(set(principle_names)):
        raise InstructionBundleError("Vietnamese principle names must be unique")

    prompt_language = _nonempty_text(
        data.get("prompt_language"), "prompt_language"
    )
    if prompt_language != "vi":
        raise InstructionBundleError("prompt_language must be vi")

    return InstructionBundle(
        schema_version=_nonempty_text(
            data.get("schema_version"), "schema_version"
        ),
        bundle_id=_nonempty_text(data.get("bundle_id"), "bundle_id"),
        bundle_version=_nonempty_text(
            data.get("bundle_version"), "bundle_version"
        ),
        prompt_language=prompt_language,
        general_instruction=_nonempty_text(
            data.get("general_instruction"), "general_instruction"
        ),
        response_style_instruction=_nonempty_text(
            data.get("response_style_instruction"),
            "response_style_instruction",
        ),
        system_instruction_template=system_template,
        principle_instruction_template=principle_template,
        principles=tuple(principles),
        source_path=path.resolve(),
        sha256=hashlib.sha256(raw_bytes).hexdigest(),
    )

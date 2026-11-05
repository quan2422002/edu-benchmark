"""Prepare provenance-safe normalized inputs for the Plan 03 v5 audit.

This module keeps historical sample IDs unchanged and assigns an explicit,
versioned source namespace only to newly ingested HNMU workbooks.  It does not
select samples or call a model.
"""

from __future__ import annotations

import csv
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from edu_benchmark.dialogue_audit.hnmu_audit import (
    RawDialogueRow,
    load_dialogue_rows,
)
from edu_benchmark.data_io.dialogue_text_normalization import (
    DIALOGUE_NORMALIZATION_VERSION,
    normalize_dialogue_text,
)


NORMALIZED_FIELDS = (
    "sample_id",
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
    "dialogue",
)
DIALOGUE_PROVENANCE_FIELDS = (
    "dialogue_raw",
    "dialogue_raw_sha256",
    "dialogue_normalized_sha256",
    "dialogue_normalization_version",
    "dialogue_normalization_changed",
    "dialogue_annotation_count",
    "dialogue_normalization_flags_json",
)
V5_1_NORMALIZED_FIELDS = (*NORMALIZED_FIELDS, *DIALOGUE_PROVENANCE_FIELDS)
SOURCE_NAMESPACE_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
MATERIAL_TYPE_RE = re.compile(r"\b(SGK|SGV|SBT)\b", re.IGNORECASE)


class V5InputPreparationError(ValueError):
    """Raised when a v5 input contract cannot be reproduced safely."""


@dataclass(frozen=True)
class V5SourceSpec:
    """One newly ingested HNMU source and its stable ID namespace."""

    path: Path
    grade: str
    source_namespace: str
    include_material_types: tuple[str, ...]
    expected_included_count: int

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "V5SourceSpec":
        materials = tuple(
            sorted(
                {
                    str(value).strip().upper()
                    for value in raw.get("include_material_types", [])
                    if str(value).strip()
                }
            )
        )
        spec = cls(
            path=Path(str(raw.get("path", ""))),
            grade=str(raw.get("grade", "")).strip(),
            source_namespace=str(raw.get("source_namespace", "")).strip().upper(),
            include_material_types=materials,
            expected_included_count=int(raw.get("expected_included_count", 0)),
        )
        spec.validate()
        return spec

    def validate(self) -> None:
        if not self.path.is_file():
            raise V5InputPreparationError(f"Source workbook does not exist: {self.path}")
        if not self.grade.isdigit():
            raise V5InputPreparationError(f"Invalid grade for {self.path}: {self.grade!r}")
        if not SOURCE_NAMESPACE_RE.fullmatch(self.source_namespace):
            raise V5InputPreparationError(
                "source_namespace must contain uppercase letters, digits, and single "
                f"hyphen separators: {self.source_namespace!r}"
            )
        unsupported = sorted(set(self.include_material_types) - {"SGK", "SGV", "SBT"})
        if unsupported:
            raise V5InputPreparationError(
                f"Unsupported material types for {self.path}: {unsupported}"
            )
        if not self.include_material_types:
            raise V5InputPreparationError(
                f"At least one include_material_types value is required for {self.path}"
            )
        if self.expected_included_count <= 0:
            raise V5InputPreparationError(
                f"expected_included_count must be positive for {self.path}"
            )


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _load_normalized_csv(path: Path) -> list[RawDialogueRow]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in NORMALIZED_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise V5InputPreparationError(
                f"Base normalized CSV is missing fields: {', '.join(missing)}"
            )
        output: list[RawDialogueRow] = []
        for raw in reader:
            output.append(
                RawDialogueRow(
                    sample_id=str(raw.get("sample_id", "")).strip(),
                    source_file=str(raw.get("source_file", "")).strip(),
                    source_row_number=int(str(raw.get("source_row_number", "0")).strip()),
                    grade=str(raw.get("grade", "")).strip(),
                    grade_label=str(raw.get("grade_label", "")).strip(),
                    stt=str(raw.get("stt", "")).strip(),
                    lesson=str(raw.get("lesson", "")).strip(),
                    position=str(raw.get("position", "")).strip(),
                    question=str(raw.get("question", "")).strip(),
                    bloom_level=str(raw.get("bloom_level", "")).strip(),
                    answer_sgv=str(raw.get("answer_sgv", "")).strip(),
                    dialogue=str(raw.get("dialogue", "")).strip(),
                )
            )
    return output


def _material_types(position: str) -> set[str]:
    return {match.group(1).upper() for match in MATERIAL_TYPE_RE.finditer(position)}


def _id_component(value: str, *, fallback: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z]+", "", value)
    return normalized or fallback


def namespaced_sample_id(row: RawDialogueRow, *, source_namespace: str) -> str:
    """Return a stable ID that cannot collide with historical grade/row IDs."""

    stt = _id_component(row.stt, fallback=str(row.source_row_number))
    return (
        f"HNMU-{source_namespace}-R{row.source_row_number:04d}-STT{stt}"
    )


def _load_new_source(spec: V5SourceSpec) -> list[RawDialogueRow]:
    rows = load_dialogue_rows([spec.path], include_grades={spec.grade})
    selected = [
        row
        for row in rows
        if _material_types(row.position).intersection(spec.include_material_types)
    ]
    if len(selected) != spec.expected_included_count:
        raise V5InputPreparationError(
            f"Included row count changed for {spec.path}: "
            f"expected={spec.expected_included_count}, actual={len(selected)}"
        )
    output = []
    for row in selected:
        output.append(
            RawDialogueRow(
                **{
                    **row.to_dict(),
                    "sample_id": namespaced_sample_id(
                        row,
                        source_namespace=spec.source_namespace,
                    ),
                }
            )
        )
    return output


def _load_registry(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise V5InputPreparationError(f"Raw-source registry does not exist: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        source_file = str(row.get("source_file", "")).strip()
        if source_file:
            output[source_file] = {str(key): str(value or "") for key, value in row.items()}
    return output


def _validate_registered_source(
    spec: V5SourceSpec,
    *,
    registry: Mapping[str, Mapping[str, str]],
) -> dict[str, str]:
    key = spec.path.as_posix()
    record = registry.get(key)
    if record is None:
        raise V5InputPreparationError(f"Source workbook is not registered: {key}")
    expected_sha = str(record.get("sha256", "")).strip()
    actual_sha = _sha256_file(spec.path)
    if not expected_sha or expected_sha != actual_sha:
        raise V5InputPreparationError(
            f"Source registry SHA-256 mismatch for {key}: "
            f"expected={expected_sha or '<missing>'}, actual={actual_sha}"
        )
    return {
        "batch_id": str(record.get("batch_id", "")),
        "processing_status": str(record.get("processing_status", "")),
        "sha256": actual_sha,
    }


def _write_normalized_csv(path: Path, rows: Sequence[RawDialogueRow]) -> None:
    lines: list[str] = []
    with tempfile.NamedTemporaryFile(
        mode="w+",
        encoding="utf-8",
        newline="",
        delete=True,
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())
        handle.seek(0)
        lines.append(handle.read())
    _atomic_write_text(path, "".join(lines))


def _normalize_dialogue_row(row: RawDialogueRow) -> RawDialogueRow:
    result = normalize_dialogue_text(row.dialogue)
    return RawDialogueRow(
        **{
            **row.to_dict(),
            "dialogue": result.normalized_text,
            "dialogue_raw": result.raw_text,
            "dialogue_raw_sha256": result.raw_sha256,
            "dialogue_normalized_sha256": result.normalized_sha256,
            "dialogue_normalization_version": result.version,
            "dialogue_normalization_changed": result.changed,
            "dialogue_annotation_count": result.annotation_count,
            "dialogue_normalization_flags": result.flags,
        }
    )


def _write_v5_1_normalized_csv(path: Path, rows: Sequence[RawDialogueRow]) -> None:
    lines: list[str] = []
    with tempfile.NamedTemporaryFile(
        mode="w+",
        encoding="utf-8",
        newline="",
        delete=True,
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=V5_1_NORMALIZED_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row.to_dict(), **row.dialogue_provenance_dict()})
        handle.seek(0)
        lines.append(handle.read())
    _atomic_write_text(path, "".join(lines))


def _collect_input_rows(
    *,
    base_normalized_rows_path: Path,
    source_registry_path: Path,
    sources: Sequence[V5SourceSpec],
) -> tuple[list[RawDialogueRow], list[RawDialogueRow], list[dict[str, Any]]]:
    base_rows = _load_normalized_csv(base_normalized_rows_path)
    registry = _load_registry(source_registry_path)
    all_new_rows: list[RawDialogueRow] = []
    source_records: list[dict[str, Any]] = []
    for spec in sources:
        registry_record = _validate_registered_source(spec, registry=registry)
        rows = _load_new_source(spec)
        all_new_rows.extend(rows)
        source_records.append(
            {
                "path": spec.path.as_posix(),
                "grade": spec.grade,
                "source_namespace": spec.source_namespace,
                "include_material_types": list(spec.include_material_types),
                "included_count": len(rows),
                "sample_id_min": min(row.sample_id for row in rows),
                "sample_id_max": max(row.sample_id for row in rows),
                **registry_record,
            }
        )
    return base_rows, all_new_rows, source_records


def _validate_combined_ids(rows: Sequence[RawDialogueRow]) -> list[str]:
    sample_ids = [row.sample_id for row in rows]
    duplicate_ids = sorted(
        value for value, count in Counter(sample_ids).items() if count > 1
    )
    if any(not value for value in sample_ids) or duplicate_ids:
        raise V5InputPreparationError(
            f"Combined rows require unique non-empty sample IDs: {duplicate_ids[:10]}"
        )
    return sample_ids


def prepare_v5_inputs(
    *,
    base_normalized_rows_path: Path,
    source_registry_path: Path,
    sources: Sequence[V5SourceSpec],
    output_rows_path: Path,
    output_manifest_path: Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Append namespaced new-source rows to the immutable historical snapshot."""

    if not base_normalized_rows_path.is_file():
        raise V5InputPreparationError(
            f"Base normalized rows do not exist: {base_normalized_rows_path}"
        )
    if not sources:
        raise V5InputPreparationError("At least one new source is required")
    if len({spec.source_namespace for spec in sources}) != len(sources):
        raise V5InputPreparationError("source_namespace values must be unique")
    if len({spec.path.as_posix() for spec in sources}) != len(sources):
        raise V5InputPreparationError("Source workbook paths must be unique")
    existing_outputs = [path for path in (output_rows_path, output_manifest_path) if path.exists()]
    if existing_outputs and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing v5 inputs: "
            + ", ".join(path.as_posix() for path in existing_outputs)
        )

    base_rows = _load_normalized_csv(base_normalized_rows_path)
    registry = _load_registry(source_registry_path)
    all_new_rows: list[RawDialogueRow] = []
    source_records: list[dict[str, Any]] = []
    for spec in sources:
        registry_record = _validate_registered_source(spec, registry=registry)
        rows = _load_new_source(spec)
        all_new_rows.extend(rows)
        source_records.append(
            {
                "path": spec.path.as_posix(),
                "grade": spec.grade,
                "source_namespace": spec.source_namespace,
                "include_material_types": list(spec.include_material_types),
                "included_count": len(rows),
                "sample_id_min": min(row.sample_id for row in rows),
                "sample_id_max": max(row.sample_id for row in rows),
                **registry_record,
            }
        )

    combined = [*base_rows, *all_new_rows]
    sample_ids = [row.sample_id for row in combined]
    duplicate_ids = sorted(
        value for value, count in Counter(sample_ids).items() if count > 1
    )
    if any(not value for value in sample_ids) or duplicate_ids:
        raise V5InputPreparationError(
            f"Combined v5 rows require unique non-empty sample IDs: {duplicate_ids[:10]}"
        )

    _write_normalized_csv(output_rows_path, combined)
    manifest = {
        "schema_version": "hnmu-dialogue-v5-input-manifest-v1",
        "prepared_at": _utc_now(),
        "base": {
            "path": base_normalized_rows_path.as_posix(),
            "sha256": _sha256_file(base_normalized_rows_path),
            "row_count": len(base_rows),
            "historical_ids_preserved": True,
        },
        "source_registry": {
            "path": source_registry_path.as_posix(),
            "sha256": _sha256_file(source_registry_path),
        },
        "new_sources": source_records,
        "new_row_count": len(all_new_rows),
        "combined_row_count": len(combined),
        "unique_sample_id_count": len(set(sample_ids)),
        "output": {
            "path": output_rows_path.as_posix(),
            "sha256": _sha256_file(output_rows_path),
        },
    }
    _atomic_write_text(
        output_manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return {**manifest, "manifest_path": output_manifest_path.as_posix()}


def prepare_v5_1_inputs(
    *,
    base_normalized_rows_path: Path,
    source_registry_path: Path,
    sources: Sequence[V5SourceSpec],
    output_rows_path: Path,
    output_manifest_path: Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Build a v5.1 snapshot with canonical dialogue and row-level provenance."""

    if not base_normalized_rows_path.is_file():
        raise V5InputPreparationError(
            f"Base normalized rows do not exist: {base_normalized_rows_path}"
        )
    if not sources:
        raise V5InputPreparationError("At least one new source is required")
    if len({spec.source_namespace for spec in sources}) != len(sources):
        raise V5InputPreparationError("source_namespace values must be unique")
    if len({spec.path.as_posix() for spec in sources}) != len(sources):
        raise V5InputPreparationError("Source workbook paths must be unique")
    existing_outputs = [
        path for path in (output_rows_path, output_manifest_path) if path.exists()
    ]
    if existing_outputs and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing v5.1 inputs: "
            + ", ".join(path.as_posix() for path in existing_outputs)
        )

    base_rows, new_rows, source_records = _collect_input_rows(
        base_normalized_rows_path=base_normalized_rows_path,
        source_registry_path=source_registry_path,
        sources=sources,
    )
    combined = [_normalize_dialogue_row(row) for row in (*base_rows, *new_rows)]
    sample_ids = _validate_combined_ids(combined)
    _write_v5_1_normalized_csv(output_rows_path, combined)

    flag_counts = Counter(
        flag for row in combined for flag in row.dialogue_normalization_flags
    )
    changed_rows = [row for row in combined if row.dialogue_normalization_changed]
    annotated_rows = [row for row in combined if row.dialogue_annotation_count > 0]
    flagged_rows = [row for row in combined if row.dialogue_normalization_flags]
    manifest = {
        "schema_version": "hnmu-dialogue-v5-1-input-manifest-v1",
        "prepared_at": _utc_now(),
        "base": {
            "path": base_normalized_rows_path.as_posix(),
            "sha256": _sha256_file(base_normalized_rows_path),
            "row_count": len(base_rows),
            "historical_ids_preserved": True,
        },
        "source_registry": {
            "path": source_registry_path.as_posix(),
            "sha256": _sha256_file(source_registry_path),
        },
        "new_sources": source_records,
        "new_row_count": len(new_rows),
        "combined_row_count": len(combined),
        "unique_sample_id_count": len(set(sample_ids)),
        "dialogue_normalization": {
            "version": DIALOGUE_NORMALIZATION_VERSION,
            "raw_dialogue_preserved": True,
            "changed_row_count": len(changed_rows),
            "annotation_row_count": len(annotated_rows),
            "annotation_removed_count": sum(
                row.dialogue_annotation_count for row in combined
            ),
            "flagged_row_count": len(flagged_rows),
            "flag_counts": dict(sorted(flag_counts.items())),
            "raw_sha256_column": "dialogue_raw_sha256",
            "normalized_sha256_column": "dialogue_normalized_sha256",
        },
        "output": {
            "path": output_rows_path.as_posix(),
            "sha256": _sha256_file(output_rows_path),
            "fields": list(V5_1_NORMALIZED_FIELDS),
        },
    }
    _atomic_write_text(
        output_manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return {**manifest, "manifest_path": output_manifest_path.as_posix()}


def prepare_v5_inputs_from_config(
    config_path: Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Load the experiment-local preparation contract and build its outputs."""

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    schema_version = raw.get("schema_version")
    if schema_version not in {
        "hnmu-dialogue-v5-input-config-v1",
        "hnmu-dialogue-v5-1-input-config-v1",
    }:
        raise V5InputPreparationError("Unsupported v5 input configuration schema")
    sources = tuple(V5SourceSpec.from_mapping(value) for value in raw.get("sources", []))
    prepare = (
        prepare_v5_1_inputs
        if schema_version == "hnmu-dialogue-v5-1-input-config-v1"
        else prepare_v5_inputs
    )
    return prepare(
        base_normalized_rows_path=Path(str(raw.get("base_normalized_rows", ""))),
        source_registry_path=Path(str(raw.get("source_registry", ""))),
        sources=sources,
        output_rows_path=Path(str(raw.get("output_normalized_rows", ""))),
        output_manifest_path=Path(str(raw.get("output_manifest", ""))),
        overwrite=overwrite,
    )

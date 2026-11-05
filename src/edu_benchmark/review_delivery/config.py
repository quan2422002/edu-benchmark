"""Strict configuration loading for Plan 04 review-delivery products."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class ReviewConfigError(ValueError):
    """Raised when a review-product configuration is invalid."""


def _strict_keys(value: Mapping[str, Any], *, required: set[str], context: str) -> None:
    missing = required - set(value)
    extra = set(value) - required
    if missing or extra:
        raise ReviewConfigError(
            f"Invalid keys for {context}: missing={sorted(missing)} extra={sorted(extra)}"
        )


def _repo_path(repository_root: Path, value: str, *, must_exist: bool = True) -> Path:
    raw = Path(value)
    path = raw if raw.is_absolute() else repository_root / raw
    resolved = path.resolve()
    root = repository_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ReviewConfigError(f"Configured path escapes the repository: {value}") from exc
    if must_exist and not resolved.exists():
        raise ReviewConfigError(f"Configured path does not exist: {value}")
    return resolved


@dataclass(frozen=True)
class AuditSourceConfig:
    source_key: str
    display_name: str
    grade: int
    criterion_csv: Path
    summary_csv: Path


@dataclass(frozen=True)
class WorkbookTargetConfig:
    key: str
    display_name: str
    source_keys: tuple[str, ...]
    output_filename: str


@dataclass(frozen=True)
class WorkbookConfig:
    criteria_registry: Path
    output_root: Path
    sources: tuple[AuditSourceConfig, ...]
    targets: tuple[WorkbookTargetConfig, ...]
    expected_criteria_per_sample: int


@dataclass(frozen=True)
class PortalConfig:
    fragment_csv: Path
    image_root: Path
    image_fallback_roots: tuple[Path, ...]
    pdf_root: Path
    validation_output: Path
    host: str
    port: int
    username_env: str
    password_env: str
    max_regex_length: int


@dataclass(frozen=True)
class ReviewProductsConfig:
    schema_version: str
    experiment_id: str
    config_path: Path
    repository_root: Path
    workbook: WorkbookConfig
    portal: PortalConfig


def _require_mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ReviewConfigError(f"{context} must be an object")
    return value


def _require_nonempty(value: Any, context: str) -> str:
    text = str(value).strip()
    if not text:
        raise ReviewConfigError(f"{context} must be non-empty")
    return text


def load_review_products_config(
    config_path: str | Path,
    *,
    repository_root: str | Path,
) -> ReviewProductsConfig:
    """Load a repository-scoped Plan 04 configuration with strict keys."""

    root = Path(repository_root).resolve()
    path = _repo_path(root, str(config_path))
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewConfigError(f"Invalid JSON config: {path}") from exc
    value = _require_mapping(raw, "config")
    _strict_keys(
        value,
        required={"schema_version", "experiment_id", "workbook", "portal"},
        context="config",
    )
    if value["schema_version"] != "plan04-review-products-v1":
        raise ReviewConfigError("Unsupported review-products schema_version")

    workbook_raw = _require_mapping(value["workbook"], "workbook")
    _strict_keys(
        workbook_raw,
        required={
            "criteria_registry",
            "output_root",
            "sources",
            "targets",
            "expected_criteria_per_sample",
        },
        context="workbook",
    )
    sources: list[AuditSourceConfig] = []
    seen_source_keys: set[str] = set()
    if not isinstance(workbook_raw["sources"], list) or not workbook_raw["sources"]:
        raise ReviewConfigError("workbook.sources must be a non-empty list")
    for index, source_value in enumerate(workbook_raw["sources"]):
        source = _require_mapping(source_value, f"workbook.sources[{index}]")
        _strict_keys(
            source,
            required={
                "source_key",
                "display_name",
                "grade",
                "criterion_csv",
                "summary_csv",
            },
            context=f"workbook.sources[{index}]",
        )
        source_key = _require_nonempty(source["source_key"], "source_key")
        if source_key in seen_source_keys:
            raise ReviewConfigError(f"Duplicate source_key: {source_key}")
        seen_source_keys.add(source_key)
        grade = int(source["grade"])
        if grade not in {6, 7, 8, 9}:
            raise ReviewConfigError(f"Unsupported grade for {source_key}: {grade}")
        sources.append(
            AuditSourceConfig(
                source_key=source_key,
                display_name=_require_nonempty(source["display_name"], "display_name"),
                grade=grade,
                criterion_csv=_repo_path(root, str(source["criterion_csv"])),
                summary_csv=_repo_path(root, str(source["summary_csv"])),
            )
        )

    targets: list[WorkbookTargetConfig] = []
    seen_target_keys: set[str] = set()
    seen_output_names: set[str] = set()
    if not isinstance(workbook_raw["targets"], list) or not workbook_raw["targets"]:
        raise ReviewConfigError("workbook.targets must be a non-empty list")
    for index, target_value in enumerate(workbook_raw["targets"]):
        target = _require_mapping(target_value, f"workbook.targets[{index}]")
        _strict_keys(
            target,
            required={"key", "display_name", "source_keys", "output_filename"},
            context=f"workbook.targets[{index}]",
        )
        key = _require_nonempty(target["key"], "target.key")
        filename = _require_nonempty(target["output_filename"], "output_filename")
        if key in seen_target_keys or filename in seen_output_names:
            raise ReviewConfigError(f"Duplicate workbook target: {key}/{filename}")
        if Path(filename).name != filename or not filename.lower().endswith(".xlsx"):
            raise ReviewConfigError(f"Invalid workbook output filename: {filename}")
        source_keys_raw = target["source_keys"]
        if not isinstance(source_keys_raw, list) or not source_keys_raw:
            raise ReviewConfigError(f"Target {key} has no source_keys")
        source_keys = tuple(str(item) for item in source_keys_raw)
        unknown = set(source_keys) - seen_source_keys
        if unknown:
            raise ReviewConfigError(f"Target {key} uses unknown sources: {sorted(unknown)}")
        seen_target_keys.add(key)
        seen_output_names.add(filename)
        targets.append(
            WorkbookTargetConfig(
                key=key,
                display_name=_require_nonempty(target["display_name"], "display_name"),
                source_keys=source_keys,
                output_filename=filename,
            )
        )

    expected_criteria = int(workbook_raw["expected_criteria_per_sample"])
    if expected_criteria <= 0:
        raise ReviewConfigError("expected_criteria_per_sample must be positive")
    output_root = _repo_path(root, str(workbook_raw["output_root"]), must_exist=False)
    workbook = WorkbookConfig(
        criteria_registry=_repo_path(root, str(workbook_raw["criteria_registry"])),
        output_root=output_root,
        sources=tuple(sources),
        targets=tuple(targets),
        expected_criteria_per_sample=expected_criteria,
    )

    portal_raw = _require_mapping(value["portal"], "portal")
    _strict_keys(
        portal_raw,
        required={
            "fragment_csv",
            "image_root",
            "image_fallback_roots",
            "pdf_root",
            "validation_output",
            "host",
            "port",
            "username_env",
            "password_env",
            "max_regex_length",
        },
        context="portal",
    )
    host = _require_nonempty(portal_raw["host"], "portal.host")
    port = int(portal_raw["port"])
    if not 1 <= port <= 65535:
        raise ReviewConfigError(f"Invalid portal port: {port}")
    max_regex_length = int(portal_raw["max_regex_length"])
    if not 1 <= max_regex_length <= 500:
        raise ReviewConfigError("max_regex_length must be between 1 and 500")
    fallback_roots_raw = portal_raw["image_fallback_roots"]
    if not isinstance(fallback_roots_raw, list):
        raise ReviewConfigError("portal.image_fallback_roots must be a list")
    fallback_roots = tuple(
        _repo_path(root, str(item)) for item in fallback_roots_raw
    )
    portal = PortalConfig(
        fragment_csv=_repo_path(root, str(portal_raw["fragment_csv"])),
        image_root=_repo_path(root, str(portal_raw["image_root"])),
        image_fallback_roots=fallback_roots,
        pdf_root=_repo_path(root, str(portal_raw["pdf_root"])),
        validation_output=_repo_path(
            root, str(portal_raw["validation_output"]), must_exist=False
        ),
        host=host,
        port=port,
        username_env=_require_nonempty(portal_raw["username_env"], "username_env"),
        password_env=_require_nonempty(portal_raw["password_env"], "password_env"),
        max_regex_length=max_regex_length,
    )
    return ReviewProductsConfig(
        schema_version=str(value["schema_version"]),
        experiment_id=_require_nonempty(value["experiment_id"], "experiment_id"),
        config_path=path,
        repository_root=root,
        workbook=workbook,
        portal=portal,
    )

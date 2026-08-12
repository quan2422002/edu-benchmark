"""Strict loading for repository-relative requirement-scoring configs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


class RequirementScoringConfigError(ValueError):
    """Raised when a requirement-scoring config violates its contract."""


_TOP_LEVEL_KEYS = {
    "schema_version",
    "config_id",
    "experiment_id",
    "repository_root",
    "run",
    "analysis",
    "export",
}
_RUN_KEYS = {
    "provider",
    "generation",
    "execution",
    "selection",
    "bundle_names",
    "paths",
}
_RUN_PATH_KEYS = {
    "pool",
    "output_root",
    "prompt",
    "schema",
    "spec_manifest",
    "calibration_input",
    "snapshot_manifest",
}
_PROVIDER_KEYS = {"project", "location"}
_GENERATION_KEYS = {
    "model",
    "temperature",
    "top_p",
    "max_output_tokens",
    "seed",
    "thinking_budget",
    "thinking_level",
    "include_thoughts",
    "timeout_seconds",
}
_EXECUTION_KEYS = {
    "max_retries",
    "retry_base_delay_seconds",
    "standard",
    "full",
}
_EXECUTION_LANE_KEYS = {"max_requests", "concurrency"}
_SELECTION_KEYS = {"seed", "spot_check_count"}
_BUNDLE_NAME_KEYS = {"pilot", "calibration", "full"}
_ANALYSIS_KEYS = {
    "bundle_dir",
    "pool",
    "trace",
    "paper_registry",
    "expected_candidates",
    "expected_families",
    "selection_seed",
    "control_sample_per_grade",
}
_EXPORT_KEYS = {
    "analysis",
    "run",
    "grounding_pool",
    "candidates",
    "trace",
    "output",
}
_FORBIDDEN_SECRET_KEYS = {
    "api_key",
    "access_token",
    "refresh_token",
    "password",
    "private_key",
    "secret",
}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RequirementScoringConfigError(f"{label} must be a mapping")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        raise RequirementScoringConfigError(
            f"{label} keys mismatch; missing={missing}, extra={extra}"
        )


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RequirementScoringConfigError(f"{label} must be a non-empty string")
    return value.strip()


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RequirementScoringConfigError(f"{label} must be a positive integer")
    return value


def _non_negative_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise RequirementScoringConfigError(
            f"{label} must be a non-negative integer"
        )
    return value


def _number(value: Any, label: str, *, positive: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RequirementScoringConfigError(f"{label} must be numeric")
    result = float(value)
    if positive and result <= 0:
        raise RequirementScoringConfigError(f"{label} must be positive")
    return result


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise RequirementScoringConfigError(f"{label} must be boolean")
    return value


def _scan_for_secrets(value: Any, location: str = "config") -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).lower().replace("-", "_")
            if key in _FORBIDDEN_SECRET_KEYS:
                raise RequirementScoringConfigError(
                    f"serialized secret field is forbidden: {location}.{raw_key}"
                )
            _scan_for_secrets(child, f"{location}.{raw_key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_secrets(child, f"{location}[{index}]")


def _repository_root(config_path: Path, raw_value: Any) -> Path:
    relative = Path(_string(raw_value, "repository_root"))
    if relative.is_absolute():
        raise RequirementScoringConfigError("repository_root must be relative")
    root = (config_path.parent / relative).resolve()
    if not (
        (root / "pyproject.toml").is_file()
        and (root / "src/edu_benchmark").is_dir()
        and (root / "experiments").is_dir()
    ):
        raise RequirementScoringConfigError(
            f"repository_root does not identify this repository: {relative}"
        )
    return root


def _resolve_path(root: Path, value: Any, label: str) -> Path:
    relative = Path(_string(value, label))
    if relative.is_absolute():
        raise RequirementScoringConfigError(f"{label} must be repository-relative")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RequirementScoringConfigError(f"{label} escapes repository root") from exc
    return resolved


@dataclass(frozen=True)
class RequirementScoringConfig:
    """Resolved operational defaults for requirement-scoring CLIs."""

    path: Path
    repository_root: Path
    raw: dict[str, Any]

    @property
    def experiment_id(self) -> str:
        return _string(self.raw["experiment_id"], "experiment_id")

    def run_defaults(self, command: str) -> dict[str, Any]:
        run = _mapping(self.raw["run"], "run")
        paths = _mapping(run["paths"], "run.paths")
        provider = _mapping(run["provider"], "run.provider")
        generation = _mapping(run["generation"], "run.generation")
        execution = _mapping(run["execution"], "run.execution")
        selection = _mapping(run["selection"], "run.selection")
        bundle_names = _mapping(run["bundle_names"], "run.bundle_names")
        lane = "full" if command in {
            "full",
            "retry-failed",
            "refresh-full-manifest",
        } else "standard"
        lane_values = _mapping(execution[lane], f"run.execution.{lane}")
        return {
            "experiment_id": self.experiment_id,
            **{
                key: _resolve_path(self.repository_root, paths[key], f"run.paths.{key}")
                for key in _RUN_PATH_KEYS
            },
            "project": _string(provider["project"], "run.provider.project"),
            "location": _string(provider["location"], "run.provider.location"),
            "model": _string(generation["model"], "run.generation.model"),
            "temperature": generation["temperature"],
            "top_p": generation["top_p"],
            "max_output_tokens": _positive_int(
                generation["max_output_tokens"], "run.generation.max_output_tokens"
            ),
            "seed": _non_negative_int(generation["seed"], "run.generation.seed"),
            "thinking_budget": generation["thinking_budget"],
            "thinking_level": generation["thinking_level"],
            "include_thoughts": _boolean(
                generation["include_thoughts"], "run.generation.include_thoughts"
            ),
            "timeout_seconds": _number(
                generation["timeout_seconds"],
                "run.generation.timeout_seconds",
                positive=True,
            ),
            "max_retries": _non_negative_int(
                execution["max_retries"], "run.execution.max_retries"
            ),
            "max_requests": _positive_int(
                lane_values["max_requests"], f"run.execution.{lane}.max_requests"
            ),
            "concurrency": _positive_int(
                lane_values["concurrency"], f"run.execution.{lane}.concurrency"
            ),
            "retry_base_delay_seconds": _number(
                execution["retry_base_delay_seconds"],
                "run.execution.retry_base_delay_seconds",
            ),
            "selection_seed": _non_negative_int(
                selection["seed"], "run.selection.seed"
            ),
            "spot_check_count": _non_negative_int(
                selection["spot_check_count"], "run.selection.spot_check_count"
            ),
            "default_bundle_name": _string(
                bundle_names[
                    "calibration"
                    if command == "calibration"
                    else "full"
                    if lane == "full"
                    else "pilot"
                ],
                "run.bundle_names",
            ),
        }

    def analysis_defaults(self) -> dict[str, Any]:
        analysis = _mapping(self.raw["analysis"], "analysis")
        return {
            "bundle_dir": _resolve_path(
                self.repository_root, analysis["bundle_dir"], "analysis.bundle_dir"
            ),
            "pool": _resolve_path(self.repository_root, analysis["pool"], "analysis.pool"),
            "trace": _resolve_path(
                self.repository_root, analysis["trace"], "analysis.trace"
            ),
            "paper_registry": _resolve_path(
                self.repository_root,
                analysis["paper_registry"],
                "analysis.paper_registry",
            ),
            "expected_candidates": _positive_int(
                analysis["expected_candidates"], "analysis.expected_candidates"
            ),
            "expected_families": _positive_int(
                analysis["expected_families"], "analysis.expected_families"
            ),
            "selection_seed": _non_negative_int(
                analysis["selection_seed"], "analysis.selection_seed"
            ),
            "control_sample_per_grade": _non_negative_int(
                analysis["control_sample_per_grade"],
                "analysis.control_sample_per_grade",
            ),
        }

    def export_defaults(self) -> dict[str, Any]:
        export = _mapping(self.raw["export"], "export")
        return {
            key: _resolve_path(self.repository_root, export[key], f"export.{key}")
            for key in _EXPORT_KEYS
        }


def load_requirement_scoring_config(path: Path) -> RequirementScoringConfig:
    """Load and strictly validate one requirement-scoring YAML config."""

    config_path = path.resolve()
    if not config_path.is_file():
        raise RequirementScoringConfigError(f"config does not exist: {config_path}")
    parsed = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    raw = _mapping(parsed, "config")
    _exact_keys(raw, _TOP_LEVEL_KEYS, "config")
    if raw["schema_version"] != "1.0":
        raise RequirementScoringConfigError("schema_version must be '1.0'")
    _string(raw["config_id"], "config_id")
    _string(raw["experiment_id"], "experiment_id")
    _scan_for_secrets(raw)
    run = _mapping(raw["run"], "run")
    _exact_keys(run, _RUN_KEYS, "run")
    _exact_keys(
        _mapping(run["provider"], "run.provider"),
        _PROVIDER_KEYS,
        "run.provider",
    )
    _exact_keys(
        _mapping(run["generation"], "run.generation"),
        _GENERATION_KEYS,
        "run.generation",
    )
    execution = _mapping(run["execution"], "run.execution")
    _exact_keys(execution, _EXECUTION_KEYS, "run.execution")
    for lane in ("standard", "full"):
        _exact_keys(
            _mapping(execution[lane], f"run.execution.{lane}"),
            _EXECUTION_LANE_KEYS,
            f"run.execution.{lane}",
        )
    _exact_keys(
        _mapping(run["selection"], "run.selection"),
        _SELECTION_KEYS,
        "run.selection",
    )
    _exact_keys(
        _mapping(run["bundle_names"], "run.bundle_names"),
        _BUNDLE_NAME_KEYS,
        "run.bundle_names",
    )
    _exact_keys(_mapping(run["paths"], "run.paths"), _RUN_PATH_KEYS, "run.paths")
    _exact_keys(_mapping(raw["analysis"], "analysis"), _ANALYSIS_KEYS, "analysis")
    _exact_keys(_mapping(raw["export"], "export"), _EXPORT_KEYS, "export")
    root = _repository_root(config_path, raw["repository_root"])
    config = RequirementScoringConfig(path=config_path, repository_root=root, raw=raw)
    # Materialize every section once so missing nested values fail before execution.
    config.run_defaults("pilot")
    config.run_defaults("full")
    config.analysis_defaults()
    config.export_defaults()
    return config

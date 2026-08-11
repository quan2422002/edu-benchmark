"""Fail-closed loading for repository-relative experiment runtime configs."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml


class RuntimeConfigError(ValueError):
    """Raised when a runtime config cannot be resolved unambiguously."""


_TOP_LEVEL_KEYS = {
    "schema_version",
    "config_id",
    "config_version",
    "pipeline_id",
    "experiment_id",
    "repository_root",
    "execution",
    "inputs",
    "outputs",
    "parameters",
    "provenance",
    "equivalence",
}
_REQUIRED_TOP_LEVEL_KEYS = _TOP_LEVEL_KEYS
_FORBIDDEN_SECRET_KEYS = {
    "api_key",
    "access_token",
    "refresh_token",
    "password",
    "private_key",
    "secret_value",
    "credential_value",
}
_FORBIDDEN_SECRET_PREFIXES = (
    "sk-",
    "AIza",
    "ya29.",
    "-----BEGIN PRIVATE KEY-----",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def discover_repository_root(anchor: Path | None = None) -> Path:
    """Find the repository from package location, never from the current CWD."""

    start = (anchor or Path(__file__)).resolve()
    if start.is_file():
        start = start.parent
    for candidate in (start, *start.parents):
        if (
            (candidate / "pyproject.toml").is_file()
            and (candidate / "src/edu_benchmark").is_dir()
            and (candidate / "experiments").is_dir()
        ):
            return candidate
    raise RuntimeConfigError(
        f"Cannot discover repository root from package anchor: {start}"
    )


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeConfigError(f"{label} must be a mapping")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeConfigError(f"{label} must be a non-empty string")
    return value.strip()


def _scan_for_serialized_secrets(value: Any, location: str = "config") -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).lower().replace("-", "_")
            if key in _FORBIDDEN_SECRET_KEYS:
                raise RuntimeConfigError(
                    f"Serialized secret field is forbidden: {location}.{raw_key}"
                )
            _scan_for_serialized_secrets(child, f"{location}.{raw_key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_serialized_secrets(child, f"{location}[{index}]")
        return
    if isinstance(value, str) and value.startswith(_FORBIDDEN_SECRET_PREFIXES):
        raise RuntimeConfigError(
            f"Serialized credential-like value is forbidden at {location}"
        )


def _resolve_repo_path(
    repo_root: Path,
    raw_path: Any,
    *,
    label: str,
    must_exist: bool,
    file_only: bool = False,
) -> tuple[str, Path]:
    relative = Path(_string(raw_path, label))
    if relative.is_absolute():
        raise RuntimeConfigError(f"{label} must be repository-relative")
    resolved = (repo_root / relative).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise RuntimeConfigError(f"{label} escapes the repository root") from exc
    if must_exist and not resolved.exists():
        raise RuntimeConfigError(f"{label} does not exist: {relative.as_posix()}")
    if file_only and resolved.exists() and not resolved.is_file():
        raise RuntimeConfigError(f"{label} must be a file: {relative.as_posix()}")
    return relative.as_posix(), resolved


def _record_count(path: Path, file_format: str) -> int:
    if file_format == "csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return sum(1 for _ in csv.DictReader(handle))
    if file_format == "jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())
    if file_format == "json":
        json.loads(path.read_text(encoding="utf-8"))
        return 1
    raise RuntimeConfigError(f"Unsupported input format: {file_format}")


@dataclass(frozen=True)
class ResolvedInput:
    role: str
    artifact_id: str
    version: str
    relative_path: str
    path: Path
    sha256: str
    record_count: int
    file_format: str

    def manifest_record(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "artifact_id": self.artifact_id,
            "version": self.version,
            "path": self.relative_path,
            "sha256": self.sha256,
            "record_count": self.record_count,
            "format": self.file_format,
        }


@dataclass(frozen=True)
class RuntimeConfig:
    path: Path
    relative_path: str
    repo_root: Path
    sha256: str
    raw: dict[str, Any]
    inputs: dict[str, ResolvedInput]
    outputs: dict[str, tuple[str, Path, str]]
    equivalence_baseline: tuple[str, Path, str]

    @property
    def pipeline_id(self) -> str:
        return str(self.raw["pipeline_id"])

    @property
    def config_id(self) -> str:
        return str(self.raw["config_id"])

    @property
    def config_version(self) -> str:
        return str(self.raw["config_version"])

    def input(self, role: str) -> ResolvedInput:
        try:
            return self.inputs[role]
        except KeyError as exc:
            raise RuntimeConfigError(f"Config is missing input role: {role}") from exc

    def output_path(self, role: str) -> Path:
        try:
            return self.outputs[role][1]
        except KeyError as exc:
            raise RuntimeConfigError(f"Config is missing output role: {role}") from exc


def validate_runtime_contract(config: RuntimeConfig) -> None:
    """Validate every run-blocking field for the supported offline pipeline."""

    if config.pipeline_id != "section_v_ablation":
        raise RuntimeConfigError(
            f"Unsupported pipeline for this runtime: {config.pipeline_id}"
        )

    execution = _mapping(config.raw["execution"], "execution")
    expected_execution_keys = {"mode", "runner", "resume_policy", "resume_note"}
    if set(execution) != expected_execution_keys:
        raise RuntimeConfigError(
            "execution must contain exactly: "
            + ", ".join(sorted(expected_execution_keys))
        )
    if execution["mode"] != "offline":
        raise RuntimeConfigError("Section V execution mode must be offline")
    if execution["resume_policy"] != "unsupported":
        raise RuntimeConfigError("Section V resume policy must be unsupported")
    runner = Path(_string(execution["runner"], "execution.runner")).as_posix()
    _string(execution["resume_note"], "execution.resume_note")

    expected_input_formats = {
        "candidate_pool": "csv",
        "gemini_judge": "jsonl",
        "gpt_judge": "jsonl",
    }
    if set(config.inputs) != set(expected_input_formats):
        raise RuntimeConfigError(
            "Section V input roles must be exactly: "
            + ", ".join(sorted(expected_input_formats))
        )
    for role, expected_format in expected_input_formats.items():
        if config.inputs[role].file_format != expected_format:
            raise RuntimeConfigError(
                f"Section V input {role} must use {expected_format} format"
            )

    expected_output_schemas = {
        "result": "section-v-ablation-analysis-v1",
        "run_manifest": "experiment-runtime-manifest-v1",
    }
    for role, expected_schema in expected_output_schemas.items():
        if config.outputs[role][2] != expected_schema:
            raise RuntimeConfigError(
                f"Section V output {role} schema must be {expected_schema}"
            )

    parameters = _mapping(config.raw["parameters"], "parameters")
    if set(parameters) != {"bootstrap_iterations", "seed"}:
        raise RuntimeConfigError(
            "Section V parameters must contain exactly bootstrap_iterations and seed"
        )
    iterations = parameters["bootstrap_iterations"]
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 1:
        raise RuntimeConfigError("bootstrap_iterations must be a positive integer")
    seed = parameters["seed"]
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise RuntimeConfigError("seed must be an integer")

    provenance = _mapping(config.raw["provenance"], "provenance")
    expected_provenance_keys = {
        "code_commit",
        "code_commit_note",
        "code_paths",
        "prompt_bundle",
        "provider",
        "credential_policy",
        "cost",
    }
    if set(provenance) != expected_provenance_keys:
        raise RuntimeConfigError(
            "provenance must contain exactly: "
            + ", ".join(sorted(expected_provenance_keys))
        )
    code_commit = provenance["code_commit"]
    if code_commit is not None:
        _string(code_commit, "provenance.code_commit")
    _string(provenance["code_commit_note"], "provenance.code_commit_note")
    code_paths = provenance["code_paths"]
    if not isinstance(code_paths, list) or not code_paths:
        raise RuntimeConfigError("provenance.code_paths must be a non-empty list")
    normalized_code_paths = {
        Path(_string(path, "provenance.code_paths[]")).as_posix()
        for path in code_paths
    }
    if len(normalized_code_paths) != len(code_paths):
        raise RuntimeConfigError("provenance.code_paths must not contain duplicates")
    if runner not in normalized_code_paths:
        raise RuntimeConfigError(
            "execution.runner must be included in provenance.code_paths"
        )
    if provenance["prompt_bundle"] is not None:
        raise RuntimeConfigError("Offline Section V prompt_bundle must be null")

    provider = _mapping(provenance["provider"], "provenance.provider")
    expected_provider_keys = {"name", "model", "location", "reason"}
    if set(provider) != expected_provider_keys:
        raise RuntimeConfigError(
            "provenance.provider must contain exactly: "
            + ", ".join(sorted(expected_provider_keys))
        )
    if any(provider[key] is not None for key in ("name", "model", "location")):
        raise RuntimeConfigError("Offline Section V provider fields must be null")
    _string(provider["reason"], "provenance.provider.reason")
    if provenance["credential_policy"] != (
        "external_only_not_required_for_offline_analysis"
    ):
        raise RuntimeConfigError("Invalid offline credential policy")

    cost = _mapping(provenance["cost"], "provenance.cost")
    if set(cost) != {"currency", "amount", "reason"}:
        raise RuntimeConfigError(
            "provenance.cost must contain exactly amount, currency, and reason"
        )
    if cost["currency"] is not None:
        raise RuntimeConfigError("Offline Section V cost currency must be null")
    if isinstance(cost["amount"], bool) or cost["amount"] != 0:
        raise RuntimeConfigError("Offline Section V cost amount must be zero")
    _string(cost["reason"], "provenance.cost.reason")


def _resolve_config_path(path: Path, repo_root: Path) -> Path:
    if path.is_absolute():
        resolved = path.resolve()
    else:
        resolved = (repo_root / path).resolve()
    if not resolved.is_file():
        raise RuntimeConfigError(f"Runtime config does not exist: {path}")
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise RuntimeConfigError("Runtime config must live inside the repository") from exc
    return resolved


def load_runtime_config(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> RuntimeConfig:
    discovered_root = (repo_root or discover_repository_root()).resolve()
    config_path = _resolve_config_path(path, discovered_root)
    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RuntimeConfigError(f"Invalid YAML config: {config_path}") from exc
    raw = _mapping(loaded, "config")
    unknown = sorted(set(raw) - _TOP_LEVEL_KEYS)
    missing = sorted(_REQUIRED_TOP_LEVEL_KEYS - set(raw))
    if unknown:
        raise RuntimeConfigError("Unknown config keys: " + ", ".join(unknown))
    if missing:
        raise RuntimeConfigError("Missing config keys: " + ", ".join(missing))
    _scan_for_serialized_secrets(raw)
    if raw["schema_version"] != "1.0":
        raise RuntimeConfigError("Unsupported runtime config schema_version")
    for key in ("config_id", "config_version", "pipeline_id", "experiment_id"):
        _string(raw[key], key)

    configured_root_raw = _string(raw["repository_root"], "repository_root")
    configured_root_path = Path(configured_root_raw)
    if configured_root_path.is_absolute():
        raise RuntimeConfigError("repository_root must be config-relative")
    configured_root = (config_path.parent / configured_root_path).resolve()
    if configured_root != discovered_root:
        raise RuntimeConfigError(
            "repository_root does not match the discovered repository"
        )

    execution = _mapping(raw["execution"], "execution")
    if execution.get("mode") != "offline":
        raise RuntimeConfigError("Plan 04 representative config must be offline")
    if execution.get("resume_policy") not in {"unsupported", "pending_only"}:
        raise RuntimeConfigError("Invalid execution.resume_policy")
    _resolve_repo_path(
        discovered_root,
        execution.get("runner"),
        label="execution.runner",
        must_exist=True,
        file_only=True,
    )

    input_items = raw["inputs"]
    if not isinstance(input_items, list) or not input_items:
        raise RuntimeConfigError("inputs must be a non-empty list")
    inputs: dict[str, ResolvedInput] = {}
    for index, item_value in enumerate(input_items):
        item = _mapping(item_value, f"inputs[{index}]")
        required = {
            "role",
            "artifact_id",
            "version",
            "path",
            "sha256",
            "record_count",
            "format",
        }
        if set(item) != required:
            raise RuntimeConfigError(
                f"inputs[{index}] must contain exactly: {', '.join(sorted(required))}"
            )
        role = _string(item["role"], f"inputs[{index}].role")
        if role in inputs:
            raise RuntimeConfigError(f"Duplicate input role: {role}")
        relative_path, resolved_path = _resolve_repo_path(
            discovered_root,
            item["path"],
            label=f"inputs[{index}].path",
            must_exist=True,
            file_only=True,
        )
        expected_sha = _string(item["sha256"], f"inputs[{index}].sha256")
        actual_sha = sha256_file(resolved_path)
        if actual_sha != expected_sha:
            raise RuntimeConfigError(
                f"Input checksum mismatch for {relative_path}: "
                f"expected {expected_sha}, got {actual_sha}"
            )
        expected_count = item["record_count"]
        if not isinstance(expected_count, int) or expected_count < 1:
            raise RuntimeConfigError(
                f"inputs[{index}].record_count must be a positive integer"
            )
        file_format = _string(item["format"], f"inputs[{index}].format")
        actual_count = _record_count(resolved_path, file_format)
        if actual_count != expected_count:
            raise RuntimeConfigError(
                f"Input record count mismatch for {relative_path}: "
                f"expected {expected_count}, got {actual_count}"
            )
        inputs[role] = ResolvedInput(
            role=role,
            artifact_id=_string(
                item["artifact_id"], f"inputs[{index}].artifact_id"
            ),
            version=_string(item["version"], f"inputs[{index}].version"),
            relative_path=relative_path,
            path=resolved_path,
            sha256=actual_sha,
            record_count=actual_count,
            file_format=file_format,
        )

    outputs_raw = _mapping(raw["outputs"], "outputs")
    if set(outputs_raw) != {"result", "run_manifest"}:
        raise RuntimeConfigError("outputs must contain result and run_manifest")
    outputs: dict[str, tuple[str, Path, str]] = {}
    for role, output_value in outputs_raw.items():
        output = _mapping(output_value, f"outputs.{role}")
        if set(output) != {"path", "schema_version"}:
            raise RuntimeConfigError(
                f"outputs.{role} must contain path and schema_version"
            )
        relative_path, resolved_path = _resolve_repo_path(
            discovered_root,
            output["path"],
            label=f"outputs.{role}.path",
            must_exist=False,
        )
        outputs[role] = (
            relative_path,
            resolved_path,
            _string(output["schema_version"], f"outputs.{role}.schema_version"),
        )

    equivalence = _mapping(raw["equivalence"], "equivalence")
    if set(equivalence) != {
        "baseline_result_path",
        "baseline_result_sha256",
        "comparison",
    }:
        raise RuntimeConfigError("Invalid equivalence contract")
    if equivalence["comparison"] != "normalize_repository_paths_only":
        raise RuntimeConfigError("Unsupported equivalence comparison mode")
    baseline_relative, baseline_path = _resolve_repo_path(
        discovered_root,
        equivalence["baseline_result_path"],
        label="equivalence.baseline_result_path",
        must_exist=True,
        file_only=True,
    )
    baseline_sha = _string(
        equivalence["baseline_result_sha256"],
        "equivalence.baseline_result_sha256",
    )
    actual_baseline_sha = sha256_file(baseline_path)
    if baseline_sha != actual_baseline_sha:
        raise RuntimeConfigError(
            "Baseline result checksum mismatch: "
            f"expected {baseline_sha}, got {actual_baseline_sha}"
        )

    config_relative = config_path.relative_to(discovered_root).as_posix()
    config = RuntimeConfig(
        path=config_path,
        relative_path=config_relative,
        repo_root=discovered_root,
        sha256=sha256_file(config_path),
        raw=raw,
        inputs=inputs,
        outputs=outputs,
        equivalence_baseline=(baseline_relative, baseline_path, baseline_sha),
    )
    validate_runtime_contract(config)
    return config


def build_preflight_manifest(config: RuntimeConfig) -> dict[str, Any]:
    validate_runtime_contract(config)
    execution = _mapping(config.raw["execution"], "execution")
    provenance = copy.deepcopy(_mapping(config.raw["provenance"], "provenance"))
    code_paths = provenance.pop("code_paths", [])
    if not isinstance(code_paths, list) or not code_paths:
        raise RuntimeConfigError("provenance.code_paths must be a non-empty list")
    code_files: list[dict[str, str]] = []
    for index, raw_path in enumerate(code_paths):
        relative_path, resolved_path = _resolve_repo_path(
            config.repo_root,
            raw_path,
            label=f"provenance.code_paths[{index}]",
            must_exist=True,
            file_only=True,
        )
        code_files.append(
            {"path": relative_path, "sha256": sha256_file(resolved_path)}
        )
    provenance["code_files"] = code_files
    outputs = {
        role: {"path": value[0], "schema_version": value[2]}
        for role, value in sorted(config.outputs.items())
    }
    stable = {
        "schema_version": "1.0",
        "record_type": "experiment_runtime_manifest",
        "status": "preflight_passed",
        "config": {
            "id": config.config_id,
            "version": config.config_version,
            "path": config.relative_path,
            "sha256": config.sha256,
        },
        "pipeline": {
            "id": config.pipeline_id,
            "experiment_id": config.raw["experiment_id"],
            "mode": execution["mode"],
            "runner": execution["runner"],
        },
        "inputs": [
            item.manifest_record()
            for _, item in sorted(config.inputs.items())
        ],
        "outputs": outputs,
        "parameters": config.raw["parameters"],
        "provenance": provenance,
        "resume": {
            "policy": execution["resume_policy"],
            "note": execution["resume_note"],
            "history": [],
        },
        "equivalence": {
            "baseline_result_path": config.equivalence_baseline[0],
            "baseline_result_sha256": config.equivalence_baseline[2],
            "comparison": config.raw["equivalence"]["comparison"],
        },
        "secret_scan": {
            "status": "passed",
            "serialized_credentials": False,
        },
    }
    manifest = copy.deepcopy(stable)
    manifest["generated_at"] = _utc_now()
    manifest["preflight_fingerprint"] = canonical_json_hash(stable)
    return manifest


def _portable_repository_path(
    raw_path: str,
    repo_root: Path,
    *,
    expected_relative_path: str | None = None,
) -> str:
    path = Path(raw_path)
    if expected_relative_path is not None:
        expected = Path(expected_relative_path).as_posix()
        displayed = path.as_posix()
        if displayed == expected or displayed.endswith("/" + expected):
            return expected
        raise RuntimeConfigError(
            "Result provenance path does not match its locked config path: "
            f"{raw_path} != *{expected}"
        )
    if not path.is_absolute():
        return path.as_posix()
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise RuntimeConfigError(
            f"Result provenance path is outside the repository: {raw_path}"
        ) from exc


def normalize_result_provenance_paths(
    result: Mapping[str, Any],
    repo_root: Path,
    *,
    expected_paths: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    normalized = copy.deepcopy(dict(result))
    try:
        inputs = normalized["instruction_ablation"]["provenance"]["inputs"]
    except (KeyError, TypeError) as exc:
        raise RuntimeConfigError("Section V result is missing provenance inputs") from exc
    if not isinstance(inputs, dict):
        raise RuntimeConfigError("Section V provenance inputs must be a mapping")
    if expected_paths is not None and set(expected_paths) != set(inputs):
        raise RuntimeConfigError(
            "Expected provenance roles do not match the Section V result"
        )
    for role, record in inputs.items():
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise RuntimeConfigError("Section V provenance input path is invalid")
        record["path"] = _portable_repository_path(
            record["path"],
            repo_root,
            expected_relative_path=(
                expected_paths[role] if expected_paths is not None else None
            ),
        )
    return normalized


def semantic_result_hash(
    result: Mapping[str, Any],
    repo_root: Path,
    *,
    expected_paths: Mapping[str, str] | None = None,
) -> str:
    return canonical_json_hash(
        normalize_result_provenance_paths(
            result,
            repo_root,
            expected_paths=expected_paths,
        )
    )


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)

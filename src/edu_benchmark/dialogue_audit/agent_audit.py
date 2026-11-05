"""HNMU dialogue agent audit with controlled retrieval tool calling.

The module owns audit orchestration only. Learning-resource search is delegated
directly to :func:`search_learning_fragments` from Plan 02. The model-facing
adapter binds trusted row metadata, enforces the top-five contract, projects a
minimal fragment view, and retains a reproducible trace.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
import re
import tempfile
import time
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from loguru import logger

from edu_benchmark.data_io.dialogue_text_normalization import (
    DIALOGUE_NORMALIZATION_VERSION,
    normalize_dialogue_text,
)
from edu_benchmark.dialogue_audit.checklist_aggregation import aggregate_sample
from edu_benchmark.dialogue_audit.hnmu_audit import (
    RawDialogueRow,
    bloom_band,
    duplicate_rows,
    lesson_key,
    speaker_labels,
)
from edu_benchmark.learning_resources.retrieval_api_v1 import (
    SEARCH_TOOL_NAME,
    RetrievalResult,
    search_learning_fragments,
)
from edu_benchmark.learning_resources.fragment_markdown_v1 import (
    effective_content_length,
)


PLAN_ID = "P03"
TOOL_VERSION = "hnmu-audit-retrieval-adapter-v5"
OUTPUT_SCHEMA_VERSION = "hnmu-tool-calling-pilot-v5-2"
REGRESSION_SPEC_SCHEMA_VERSION = "hnmu-dialogue-audit-regression-spec-v2"
SUPPORTED_REGRESSION_SPEC_SCHEMA_VERSIONS = frozenset(
    {"hnmu-dialogue-audit-regression-spec-v1", REGRESSION_SPEC_SCHEMA_VERSION}
)
RECOVERY_SCHEMA_VERSION = "hnmu-tool-calling-cluster-recovery-v1"
PROMPT_BUNDLE_SCHEMA_VERSION = "hnmu-dialogue-audit-prompt-bundle-v1"
DEFAULT_PROMPT_BUNDLE_MANIFEST = Path(
    "shared/prompts/hnmu_dialogue_audit/v1/manifest.json"
)
PROMPT_BUNDLE_COMPONENTS = (
    "common",
    "cluster_b",
    "cluster_b_tool_response_contract",
    "cluster_c",
    "cluster_d",
    "cluster_e",
)
MODEL_REASON_MAX_CHARS = 600
MODEL_EVIDENCE_MATCH_REASON_MAX_CHARS = 600
CLUSTER_B_REASON_MAX_CHARS = 300
CLUSTER_B_EVIDENCE_MATCH_REASON_MAX_CHARS = 300
TOKEN_USAGE_KEYS = (
    "input_tokens",
    "candidate_tokens",
    "thoughts_tokens",
    "tool_use_prompt_tokens",
    "output_tokens",
    "total_tokens",
)
ALLOWED_RESULTS = frozenset({"pass", "fail", "uncertain", "not_applicable"})
ALLOWED_REVIEW_ACTIONS = frozenset(
    {"keep", "ask_hnmu_review", "exclude_from_current_batch", "needs_uet_decision"}
)
ALLOWED_MATERIAL_TYPES = frozenset({"SGK", "SGV", "SBT"})
ALLOWED_IMAGE_DEPENDENCIES = frozenset({"none", "supporting", "required"})
CRITERIA_REQUIRING_FRAGMENT_FOR_PASS = frozenset(
    {"RAW-CON-01", "RAW-CON-02", "RAW-CON-03", "RAW-CON-06", "RAW-CON-07"}
)
CRITERIA_REQUIRING_FRAGMENT_FOR_DECISION = CRITERIA_REQUIRING_FRAGMENT_FOR_PASS
ALLOWED_EVIDENCE_BASES = frozenset(
    {
        "retrieved_fragment",
        "direct_internal_contradiction",
        "raw_row_only",
        "insufficient_learning_resource",
        "image_required",
    }
)
ALLOWED_EVIDENCE_BASIS_FIELDS = frozenset(
    {"lesson", "position", "question", "answer_sgv", "dialogue", "retrieved_fragment"}
)
DIRECT_INTERNAL_EVIDENCE_FIELDS = frozenset(
    {"lesson", "position", "question", "answer_sgv", "dialogue"}
)
SUBJECTIVE_CLUSTER_MAX_CONFIDENCE = 0.95
IMAGE_REFERENCE_RE = re.compile(
    r"\b(?:quan\s+sát|hình|ảnh|biểu\s+đồ|sơ\s+đồ|giao\s+diện|"
    r"màn\s+hình|biểu\s+tượng)\b",
    re.IGNORECASE,
)
LESSON_REFERENCE_RE = re.compile(
    r"\b(?:bài|hình)\s*(?P<number>\d{1,2})(?P<suffix>[a-z]?)"
    r"(?:\s*[.:-]\s*\d+)?\b",
    re.IGNORECASE,
)
SPREADSHEET_MISSING_OPERATOR_RE = re.compile(
    r"=[A-Z]{1,3}\d+[A-Z]{1,3}\d+\b",
    re.IGNORECASE,
)
POSITIVE_VALIDATION_RE = re.compile(
    r"\b(?:rất\s+tốt|đúng\s+rồi|chính\s+xác|tuyệt\s+vời|chuẩn(?:\s+luôn)?)\b",
    re.IGNORECASE,
)
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^\)]*\)|<img\b", re.IGNORECASE)
SBT_EXERCISE_REFERENCE_RE = re.compile(
    r"\b(?:bài(?:\s+tập)?\s*)?(?P<number>\d{1,2}\.\d{1,2})\b",
    re.IGNORECASE,
)
SBT_QUESTION_SECTION = "PHẦN I — ĐỀ BÀI"
SBT_SOLUTION_SECTION = "PHẦN II — HƯỚNG DẪN GIẢI"
MODEL_FRAGMENT_FIELDS = (
    "fragment_id",
    "grade",
    "material_type",
    # "book_title",
    # "lesson_title",
    "section_path",
    "markdown_text",
)
MODEL_FORBIDDEN_FRAGMENT_FIELDS = frozenset(
    {
        "status",
        "needs_hnmu_review",
        "notes",
        "caption_status",
        "source_markdown_path",
        "source_sha256",
        "canonical_sha256",
        "fragment_snapshot_sha256",
        "fragment_release",
        "merge_status",
        "merge_reason",
        "merge_policy_version",
        "merged_from_fragment_ids_json",
        "merged_from_fragment_count",
        "source_fragment_types_json",
        "source_fragment_index_start",
        "source_fragment_index_end",
        "merge_contract_sha256",
        "page_start",
        "page_end",
        "page_markers_json",
    }
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
CLUSTER_CRITERIA: dict[str, tuple[str, ...]] = {
    "A": ("RAW-STR-02", "RAW-STR-03"),
    "B": (
        "RAW-CON-01",
        "RAW-CON-02",
        "RAW-CON-03",
        "RAW-CON-04",
        "RAW-CON-06",
        "RAW-CON-07",
    ),
    "C": ("RAW-CON-05",),
    "D": ("RAW-PED-01", "RAW-PED-02", "RAW-PED-03"),
    "E": ("RAW-STR-04", "RAW-PED-04", "RAW-PED-05", "RAW-PED-06"),
    "F": ("RAW-DUP-03", "RAW-DUP-04"),
}
MODEL_CLUSTERS = frozenset({"B", "C", "D", "E"})
ROW_FIELDS_BY_CLUSTER: dict[str, tuple[str, ...]] = {
    "B": ("grade", "grade_label", "lesson", "position", "question", "answer_sgv", "dialogue"),
    "C": ("grade", "grade_label", "question", "bloom_level"),
    "D": ("grade", "grade_label", "question", "answer_sgv", "dialogue"),
    "E": ("grade", "grade_label", "question", "answer_sgv", "dialogue"),
}
REFERENCE_MARKERS: dict[str, tuple[str, str | None]] = {
    "C": ("## b) Từ ngữ", None),
    "D": ("## I. Khung dàn giáo", "## Tài liệu tham khảo"),
}


class PilotContractError(ValueError):
    """Raised when pilot configuration, input, or model output is invalid."""


class PilotOutputContractError(PilotContractError):
    """Raised when one bounded repair cannot fix a final model output."""


class PilotExecutionError(RuntimeError):
    """Raised when a provider or tool loop cannot complete safely."""


class PilotOutputTruncatedError(PilotExecutionError):
    """Raised when the provider stops a final response at its token limit."""


NON_RETRYABLE_HTTP_STATUS_CODES = frozenset({401, 403})


def _is_retryable_cluster_error(exc: BaseException | None) -> bool:
    """Return whether rerunning the same cluster request may resolve ``exc``."""

    if exc is None or isinstance(
        exc, (PilotOutputTruncatedError, PilotOutputContractError)
    ):
        return False
    for candidate in (exc, getattr(exc, "response", None)):
        if candidate is None:
            continue
        for attribute in ("status_code", "code"):
            value = getattr(candidate, attribute, None)
            try:
                status_code = int(value)
            except (TypeError, ValueError):
                continue
            if status_code in NON_RETRYABLE_HTTP_STATUS_CODES:
                return False
    return True


@dataclass(frozen=True)
class CriterionSpec:
    """Authoritative criterion metadata loaded from the v0 registry."""

    criterion_id: str
    criterion_group: str
    criterion_name: str
    evidence_requirement: str
    pass_condition: str
    fail_or_uncertain_policy: str
    default_reviewer_action: str


@dataclass(frozen=True)
class SelectionSourceQuota:
    """Configured extension quota for one declared source workbook."""

    source_file: str
    development: int
    holdout: int
    reserve: int

    @property
    def total(self) -> int:
        return self.development + self.holdout + self.reserve


@dataclass(frozen=True)
class ClusterRecoverySpec:
    """Fail-closed contract for recovering one cluster from an incomplete run."""

    parent_output_dir: Path
    split: str
    target_sample_id: str
    target_cluster_id: str
    expected_parent_run_fingerprint: str
    expected_parent_result_sha256: str
    expected_parent_trace_sha256: str
    expected_parent_summary_sha256: str
    expected_parent_sample_count: int
    expected_parent_completed_sample_count: int
    expected_parent_criterion_result_count: int
    expected_parent_sample_summary_count: int
    expected_parent_completed_cluster_count: int
    expected_final_criterion_result_count: int
    expected_final_sample_summary_count: int
    expected_final_completed_cluster_count: int


@dataclass(frozen=True)
class RegressionCriterionExpectation:
    """One human-locked criterion expectation for a regression run."""

    review_id: str
    sample_id: str
    criterion_id: str
    allowed_results: tuple[str, ...]
    required_evidence_fragment_ids: tuple[str, ...] = ()
    role: str = "target"
    preferred_result: str | None = None


@dataclass(frozen=True)
class RegressionImageExpectation:
    """Human-locked criterion-level image expectations for one sample."""

    review_id: str
    sample_id: str
    expected_dependency_by_criterion: Mapping[str, str]

    @property
    def criterion_ids(self) -> tuple[str, ...]:
        """Return criterion IDs in the stable cluster-B order."""

        return tuple(
            criterion_id
            for criterion_id in CLUSTER_CRITERIA["B"]
            if criterion_id in self.expected_dependency_by_criterion
        )


@dataclass(frozen=True)
class RegressionSpec:
    """Validated machine contract derived from a human review workbook."""

    path: Path
    source_review_workbook: Path
    source_review_workbook_sha256: str
    cluster_scope: Mapping[str, tuple[str, ...]]
    criterion_expectations: tuple[RegressionCriterionExpectation, ...]
    image_expectations: tuple[RegressionImageExpectation, ...]
    spec_sha256: str


@dataclass(frozen=True)
class AuditPromptBundle:
    """Validated, versioned system-prompt templates for model clusters B–E."""

    manifest_path: Path
    bundle_id: str
    version: str
    templates: Mapping[str, str]
    component_paths: Mapping[str, Path]
    component_hashes: Mapping[str, str]
    manifest_sha256: str


@dataclass(frozen=True)
class PilotConfig:
    """Versioned paths and runtime limits for one Plan 03 pilot."""

    experiment_id: str
    normalized_rows_path: Path
    criteria_path: Path
    bloom_reference_path: Path
    scaffolding_reference_path: Path
    base_prompt_path: Path
    retrieval_index_path: Path
    selection_path: Path
    model: str
    location: str
    max_output_tokens: int
    seed: int
    thinking_level: str
    timeout_seconds: float
    include_tool_response_contract_in_prompt: bool
    max_successful_tool_calls_per_cluster: int
    max_total_tool_calls_per_cluster: int
    max_retries_per_cluster: int
    retry_backoff_seconds: float
    near_duplicate_threshold: float
    selection_seed: str
    samples_per_grade: int
    development_per_grade: int
    max_output_repair_attempts: int = 0
    prompt_bundle_manifest_path: Path = DEFAULT_PROMPT_BUNDLE_MANIFEST
    base_selection_path: Path | None = None
    source_quotas: tuple[SelectionSourceQuota, ...] = ()
    normalized_rows_manifest_path: Path | None = None
    regression_spec_path: Path | None = None
    recovery: ClusterRecoverySpec | None = None

    @classmethod
    def from_json(cls, path: Path) -> "PilotConfig":
        """Load and validate an experiment-local JSON configuration."""

        raw = json.loads(path.read_text(encoding="utf-8"))
        paths = raw.get("paths", {})
        runtime = raw.get("runtime", {})
        selection = raw.get("selection", {})
        raw_source_quotas = selection.get("source_quotas", [])
        if not isinstance(raw_source_quotas, list):
            raise PilotContractError("selection.source_quotas must be an array")
        source_quotas = tuple(
            SelectionSourceQuota(
                source_file=Path(str(value.get("source_file", ""))).as_posix(),
                development=int(value.get("development", 0)),
                holdout=int(value.get("holdout", 0)),
                reserve=int(value.get("reserve", 0)),
            )
            for value in raw_source_quotas
            if isinstance(value, Mapping)
        )
        if len(source_quotas) != len(raw_source_quotas):
            raise PilotContractError("Each selection.source_quotas item must be an object")
        base_selection_raw = str(selection.get("base_selection_manifest", "")).strip()
        normalized_rows_manifest_raw = str(
            paths.get("normalized_rows_manifest", "")
        ).strip()
        prompt_bundle_manifest_raw = str(
            paths.get(
                "prompt_bundle_manifest",
                DEFAULT_PROMPT_BUNDLE_MANIFEST.as_posix(),
            )
        ).strip()
        regression_spec_raw = str(paths.get("regression_spec", "")).strip()
        raw_recovery = raw.get("recovery")
        if raw_recovery is not None and not isinstance(raw_recovery, Mapping):
            raise PilotContractError("recovery must be an object when provided")
        recovery = None
        if isinstance(raw_recovery, Mapping):
            parent_counts = raw_recovery.get("expected_parent_counts", {})
            final_counts = raw_recovery.get("expected_final_counts", {})
            if not isinstance(parent_counts, Mapping) or not isinstance(
                final_counts, Mapping
            ):
                raise PilotContractError(
                    "recovery expected_parent_counts and expected_final_counts "
                    "must be objects"
                )
            recovery = ClusterRecoverySpec(
                parent_output_dir=Path(
                    str(raw_recovery.get("parent_output_dir", ""))
                ),
                split=str(raw_recovery.get("split", "")).strip(),
                target_sample_id=str(
                    raw_recovery.get("target_sample_id", "")
                ).strip(),
                target_cluster_id=str(
                    raw_recovery.get("target_cluster_id", "")
                ).strip(),
                expected_parent_run_fingerprint=str(
                    raw_recovery.get("expected_parent_run_fingerprint", "")
                ).strip(),
                expected_parent_result_sha256=str(
                    raw_recovery.get("expected_parent_result_sha256", "")
                ).strip(),
                expected_parent_trace_sha256=str(
                    raw_recovery.get("expected_parent_trace_sha256", "")
                ).strip(),
                expected_parent_summary_sha256=str(
                    raw_recovery.get("expected_parent_summary_sha256", "")
                ).strip(),
                expected_parent_sample_count=int(parent_counts.get("sample_count", -1)),
                expected_parent_completed_sample_count=int(
                    parent_counts.get("completed_sample_count", -1)
                ),
                expected_parent_criterion_result_count=int(
                    parent_counts.get("criterion_result_count", -1)
                ),
                expected_parent_sample_summary_count=int(
                    parent_counts.get("sample_summary_count", -1)
                ),
                expected_parent_completed_cluster_count=int(
                    parent_counts.get("completed_cluster_count", -1)
                ),
                expected_final_criterion_result_count=int(
                    final_counts.get("criterion_result_count", -1)
                ),
                expected_final_sample_summary_count=int(
                    final_counts.get("sample_summary_count", -1)
                ),
                expected_final_completed_cluster_count=int(
                    final_counts.get("completed_cluster_count", -1)
                ),
            )
        include_tool_contract = runtime.get(
            "include_tool_response_contract_in_prompt",
            True,
        )
        if not isinstance(include_tool_contract, bool):
            raise PilotContractError(
                "include_tool_response_contract_in_prompt must be boolean"
            )
        config = cls(
            experiment_id=str(raw.get("experiment_id", "")).strip(),
            normalized_rows_path=Path(paths.get("normalized_rows", "")),
            criteria_path=Path(paths.get("criteria_registry", "")),
            bloom_reference_path=Path(paths.get("bloom_reference", "")),
            scaffolding_reference_path=Path(paths.get("scaffolding_reference", "")),
            base_prompt_path=Path(paths.get("base_prompt", "")),
            retrieval_index_path=Path(paths.get("retrieval_index", "")),
            selection_path=Path(paths.get("selection_manifest", "")),
            model=str(runtime.get("model", "")).strip(),
            location=str(runtime.get("location", "")).strip(),
            max_output_tokens=int(runtime.get("max_output_tokens", 0)),
            seed=int(runtime.get("seed", 0)),
            thinking_level=str(runtime.get("thinking_level", "")).strip().upper(),
            timeout_seconds=float(runtime.get("timeout_seconds", 0)),
            include_tool_response_contract_in_prompt=include_tool_contract,
            max_successful_tool_calls_per_cluster=int(
                runtime.get(
                    "max_successful_tool_calls_per_cluster",
                    runtime.get("max_tool_calls_per_cluster", 0),
                )
            ),
            max_total_tool_calls_per_cluster=int(
                runtime.get(
                    "max_total_tool_calls_per_cluster",
                    runtime.get("max_tool_calls_per_cluster", 0),
                )
            ),
            max_retries_per_cluster=int(runtime.get("max_retries_per_cluster", -1)),
            retry_backoff_seconds=float(runtime.get("retry_backoff_seconds", -1)),
            near_duplicate_threshold=float(raw.get("near_duplicate_threshold", 0.96)),
            selection_seed=str(selection.get("seed", "")).strip(),
            samples_per_grade=int(selection.get("samples_per_grade", 0)),
            development_per_grade=int(selection.get("development_per_grade", 0)),
            max_output_repair_attempts=int(
                runtime.get("max_output_repair_attempts", 0)
            ),
            prompt_bundle_manifest_path=Path(prompt_bundle_manifest_raw),
            base_selection_path=(Path(base_selection_raw) if base_selection_raw else None),
            source_quotas=source_quotas,
            normalized_rows_manifest_path=(
                Path(normalized_rows_manifest_raw)
                if normalized_rows_manifest_raw
                else None
            ),
            regression_spec_path=(
                Path(regression_spec_raw) if regression_spec_raw else None
            ),
            recovery=recovery,
        )
        config.validate()
        return config

    def validate(self) -> None:
        """Reject incomplete or unsafe configuration before any provider call."""

        if not self.experiment_id or not self.model or not self.location:
            raise PilotContractError("experiment_id, model, and location are required")
        required_paths = {
            "normalized_rows": self.normalized_rows_path,
            "criteria_registry": self.criteria_path,
            "bloom_reference": self.bloom_reference_path,
            "scaffolding_reference": self.scaffolding_reference_path,
            "base_prompt": self.base_prompt_path,
            "prompt_bundle_manifest": self.prompt_bundle_manifest_path,
        }
        missing = [name for name, value in required_paths.items() if not value.is_file()]
        if missing:
            raise PilotContractError("Missing required pilot files: " + ", ".join(missing))
        prompt_bundle = load_audit_prompt_bundle(self.prompt_bundle_manifest_path)
        if sha256_file(self.base_prompt_path) != prompt_bundle.component_hashes["common"]:
            raise PilotContractError(
                "base_prompt must match the common component in prompt_bundle_manifest"
            )
        if (
            self.normalized_rows_manifest_path is not None
            and not self.normalized_rows_manifest_path.is_file()
        ):
            raise PilotContractError(
                "normalized_rows_manifest does not exist: "
                f"{self.normalized_rows_manifest_path}"
            )
        if (
            self.regression_spec_path is not None
            and not self.regression_spec_path.is_file()
        ):
            raise PilotContractError(
                "regression_spec does not exist: "
                f"{self.regression_spec_path}"
            )
        if self.max_output_tokens <= 0 or self.timeout_seconds <= 0:
            raise PilotContractError("max_output_tokens and timeout_seconds must be positive")
        if self.max_successful_tool_calls_per_cluster <= 0:
            raise PilotContractError(
                "max_successful_tool_calls_per_cluster must be positive"
            )
        if self.max_total_tool_calls_per_cluster <= 0:
            raise PilotContractError("max_total_tool_calls_per_cluster must be positive")
        if (
            self.max_total_tool_calls_per_cluster
            < self.max_successful_tool_calls_per_cluster
        ):
            raise PilotContractError(
                "max_total_tool_calls_per_cluster must be greater than or equal "
                "to max_successful_tool_calls_per_cluster"
            )
        if self.max_retries_per_cluster < 0:
            raise PilotContractError("max_retries_per_cluster must be non-negative")
        if self.max_output_repair_attempts not in {0, 1}:
            raise PilotContractError(
                "max_output_repair_attempts must be either 0 or 1"
            )
        if self.retry_backoff_seconds < 0:
            raise PilotContractError("retry_backoff_seconds must be non-negative")
        if self.thinking_level not in {"MINIMAL", "LOW", "MEDIUM", "HIGH"}:
            raise PilotContractError(f"Unsupported thinking_level: {self.thinking_level}")
        if not 0 < self.near_duplicate_threshold <= 1:
            raise PilotContractError("near_duplicate_threshold must be in (0, 1]")
        if self.source_quotas:
            if self.base_selection_path is None or not self.base_selection_path.is_file():
                raise PilotContractError(
                    "An existing base_selection_manifest is required for extension selection"
                )
            source_files = [quota.source_file for quota in self.source_quotas]
            if any(not value for value in source_files) or len(source_files) != len(
                set(source_files)
            ):
                raise PilotContractError(
                    "selection.source_quotas requires unique non-empty source_file values"
                )
            if any(
                min(quota.development, quota.holdout, quota.reserve) < 0
                or quota.total <= 0
                for quota in self.source_quotas
            ):
                raise PilotContractError(
                    "Each source quota must be non-negative and have a positive total"
                )
        else:
            if self.samples_per_grade <= 0:
                raise PilotContractError("samples_per_grade must be positive")
            if not 0 < self.development_per_grade < self.samples_per_grade:
                raise PilotContractError(
                    "development_per_grade must be positive and smaller than samples_per_grade"
                )
        if self.recovery is not None:
            recovery = self.recovery
            if not recovery.parent_output_dir.is_dir():
                raise PilotContractError(
                    "Recovery parent_output_dir does not exist: "
                    f"{recovery.parent_output_dir}"
                )
            if recovery.split not in {"development", "holdout"}:
                raise PilotContractError("Recovery split must be development or holdout")
            if not recovery.target_sample_id:
                raise PilotContractError("Recovery target_sample_id is required")
            if recovery.target_cluster_id != "B":
                raise PilotContractError(
                    "P03-A015 recovery is restricted to target_cluster_id=B"
                )
            locked_hashes = {
                "expected_parent_run_fingerprint": (
                    recovery.expected_parent_run_fingerprint
                ),
                "expected_parent_result_sha256": recovery.expected_parent_result_sha256,
                "expected_parent_trace_sha256": recovery.expected_parent_trace_sha256,
                "expected_parent_summary_sha256": recovery.expected_parent_summary_sha256,
            }
            invalid_hashes = [
                name
                for name, value in locked_hashes.items()
                if not re.fullmatch(r"[0-9a-f]{64}", value)
            ]
            if invalid_hashes:
                raise PilotContractError(
                    "Recovery parent hashes must be SHA-256 hex digests: "
                    + ", ".join(invalid_hashes)
                )
            recovery_counts = (
                recovery.expected_parent_sample_count,
                recovery.expected_parent_completed_sample_count,
                recovery.expected_parent_criterion_result_count,
                recovery.expected_parent_sample_summary_count,
                recovery.expected_parent_completed_cluster_count,
                recovery.expected_final_criterion_result_count,
                recovery.expected_final_sample_summary_count,
                recovery.expected_final_completed_cluster_count,
            )
            if any(value < 0 for value in recovery_counts):
                raise PilotContractError("Recovery expected counts must be non-negative")
            criterion_count = sum(map(len, CLUSTER_CRITERIA.values()))
            if (
                recovery.expected_final_sample_summary_count
                != recovery.expected_parent_sample_count
            ):
                raise PilotContractError(
                    "Recovery final sample_summary_count must equal parent sample_count"
                )
            if recovery.expected_final_criterion_result_count != (
                recovery.expected_parent_sample_count * criterion_count
            ):
                raise PilotContractError(
                    "Recovery final criterion_result_count must cover all 18 criteria"
                )
            if recovery.expected_final_completed_cluster_count != (
                recovery.expected_parent_sample_count * len(CLUSTER_CRITERIA)
            ):
                raise PilotContractError(
                    "Recovery final completed_cluster_count must cover all six clusters"
                )
            if recovery.expected_parent_criterion_result_count != (
                recovery.expected_final_criterion_result_count
                - len(CLUSTER_CRITERIA[recovery.target_cluster_id])
            ):
                raise PilotContractError(
                    "Recovery parent criterion count must omit exactly the target cluster"
                )
            if recovery.expected_parent_sample_summary_count != (
                recovery.expected_final_sample_summary_count - 1
            ):
                raise PilotContractError(
                    "Recovery parent summary count must omit exactly the target sample"
                )
            if recovery.expected_parent_completed_cluster_count != (
                recovery.expected_final_completed_cluster_count - 1
            ):
                raise PilotContractError(
                    "Recovery parent cluster count must omit exactly the target cluster"
                )
            if recovery.expected_parent_completed_sample_count != (
                recovery.expected_parent_sample_count - 1
            ):
                raise PilotContractError(
                    "Recovery parent completed sample count must omit exactly the target sample"
                )
            if self.max_output_tokens != 8192 or self.thinking_level != "MEDIUM":
                raise PilotContractError(
                    "P03-A015 recovery must keep max_output_tokens=8192 and "
                    "thinking_level=MEDIUM"
                )


@dataclass(frozen=True)
class SelectionRow:
    """One locked sample and its development/holdout assignment."""

    sample_id: str
    grade: str
    split: str
    selection_order: int
    diversity_bucket: str
    source_file: str = ""
    selection_source: str = ""
    duplicate_group_id: str = ""


@dataclass(frozen=True)
class ToolExecution:
    """Model-visible retrieval response plus operator-only trace metadata."""

    visible_response: dict[str, Any]
    trace: dict[str, Any]


@dataclass(frozen=True)
class ModelClusterResult:
    """Validated results and trace from one model-driven criterion cluster."""

    results: tuple[dict[str, Any], ...]
    trace_events: tuple[dict[str, Any], ...]
    prompt_sha256: str
    tool_call_count: int
    usage: dict[str, int]
    model_version: str
    response_id: str
    finish_reason: str


@dataclass(frozen=True)
class RecoveryParentState:
    """Validated immutable inputs inherited by one cluster-recovery run."""

    spec: ClusterRecoverySpec
    summary: dict[str, Any]
    result_rows: tuple[dict[str, Any], ...]
    trace_rows: tuple[dict[str, Any], ...]
    completed_clusters: frozenset[tuple[str, str]]
    target_row: RawDialogueRow
    target_selection: SelectionRow
    parent_result_sha256: str
    parent_trace_sha256: str
    parent_summary_sha256: str
    inherited_records_sha256: str


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    """Return the SHA-256 hash of UTF-8 text."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hash of a file without loading it all at once."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_audit_prompt_bundle(manifest_path: Path) -> AuditPromptBundle:
    """Load a prompt bundle and fail closed on schema, path, or hash drift."""

    if not manifest_path.is_file():
        raise PilotContractError(
            f"Prompt bundle manifest does not exist: {manifest_path}"
        )
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PilotContractError(
            f"Prompt bundle manifest is not valid JSON: {manifest_path}"
        ) from exc
    if not isinstance(raw, Mapping):
        raise PilotContractError("Prompt bundle manifest must be a JSON object")
    if raw.get("schema_version") != PROMPT_BUNDLE_SCHEMA_VERSION:
        raise PilotContractError(
            "Unsupported prompt bundle schema_version: "
            f"{raw.get('schema_version')!r}"
        )
    bundle_id = str(raw.get("bundle_id", "")).strip()
    version = str(raw.get("version", "")).strip()
    files = raw.get("files")
    if not bundle_id or not version or not isinstance(files, Mapping):
        raise PilotContractError(
            "Prompt bundle requires bundle_id, version, and files"
        )
    if set(files) != set(PROMPT_BUNDLE_COMPONENTS):
        raise PilotContractError(
            "Prompt bundle files must contain exactly: "
            + ", ".join(PROMPT_BUNDLE_COMPONENTS)
        )

    bundle_root = manifest_path.parent.resolve()
    templates: dict[str, str] = {}
    component_paths: dict[str, Path] = {}
    component_hashes: dict[str, str] = {}
    for component in PROMPT_BUNDLE_COMPONENTS:
        entry = files[component]
        if not isinstance(entry, Mapping):
            raise PilotContractError(
                f"Prompt bundle component {component} must be an object"
            )
        relative_path = Path(str(entry.get("path", "")))
        expected_hash = str(entry.get("sha256", "")).strip().lower()
        candidate = (bundle_root / relative_path).resolve()
        try:
            candidate.relative_to(bundle_root)
        except ValueError as exc:
            raise PilotContractError(
                f"Prompt bundle component escapes bundle directory: {component}"
            ) from exc
        if not relative_path.as_posix() or not candidate.is_file():
            raise PilotContractError(
                f"Prompt bundle component does not exist: {component}"
            )
        actual_hash = sha256_file(candidate)
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            raise PilotContractError(
                f"Prompt bundle component has invalid sha256: {component}"
            )
        if actual_hash != expected_hash:
            raise PilotContractError(
                f"Prompt bundle hash mismatch for {component}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        templates[component] = candidate.read_text(encoding="utf-8")
        component_paths[component] = candidate
        component_hashes[component] = actual_hash
    return AuditPromptBundle(
        manifest_path=manifest_path,
        bundle_id=bundle_id,
        version=version,
        templates=templates,
        component_paths=component_paths,
        component_hashes=component_hashes,
        manifest_sha256=sha256_file(manifest_path),
    )


def prompt_bundle_input_hashes(config: PilotConfig) -> dict[str, str]:
    """Return flattened prompt-bundle hashes for manifests and run contracts."""

    bundle = load_audit_prompt_bundle(config.prompt_bundle_manifest_path)
    hashes = {"prompt_bundle_manifest": bundle.manifest_sha256}
    hashes.update(
        {
            f"prompt_bundle_{component}": digest
            for component, digest in bundle.component_hashes.items()
        }
    )
    return hashes


def canonical_records_sha256(records: Sequence[Mapping[str, Any]]) -> str:
    """Hash ordered JSON records independently of JSONL whitespace."""

    canonical = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in records
    )
    return sha256_text(canonical)


def project_dialogue_for_model(dialogue: str) -> str:
    """Return the shared canonical dialogue projection used by all consumers."""

    return normalize_dialogue_text(dialogue).normalized_text


def dialogue_projection_trace(row: RawDialogueRow) -> dict[str, Any]:
    """Return raw/projected dialogue provenance for one selected sample."""

    raw_dialogue = row.dialogue_raw if row.dialogue_normalization_version else row.dialogue
    projected = project_dialogue_for_model(row.dialogue)
    return {
        "event_type": "dialogue_projection",
        "sample_id": row.sample_id,
        "raw_dialogue": raw_dialogue,
        "raw_dialogue_sha256": (
            row.dialogue_raw_sha256 or sha256_text(raw_dialogue)
        ),
        "projected_dialogue": projected,
        "projected_dialogue_sha256": (
            row.dialogue_normalized_sha256 or sha256_text(projected)
        ),
        "projection_changed": raw_dialogue != projected,
        "projection_version": (
            row.dialogue_normalization_version or DIALOGUE_NORMALIZATION_VERSION
        ),
        "annotation_count": row.dialogue_annotation_count,
        "normalization_flags": list(row.dialogue_normalization_flags),
    }


def image_dependency_hints(row: RawDialogueRow) -> dict[str, Any]:
    """Find deterministic image-reference candidates without making a judgment."""

    matches: dict[str, list[str]] = {}
    for field in ("position", "question", "answer_sgv", "dialogue"):
        value = str(getattr(row, field, "") or "")
        terms = sorted({match.group(0) for match in IMAGE_REFERENCE_RE.finditer(value)})
        if terms:
            matches[field] = terms
    return {
        "image_dependency_candidate": bool(matches),
        "matched_terms_by_field": matches,
        "instruction": (
            "Đây chỉ là tín hiệu từ khóa. Tác nhân vẫn phải quyết định ở từng tiêu chí "
            "bằng câu hỏi: bỏ pixel ảnh thì bằng chứng văn bản còn đủ hay không."
        ),
    }


def sbt_retrieval_hints(row: RawDialogueRow) -> dict[str, Any] | None:
    """Return deterministic SBT query hints without retrieving hidden evidence."""

    if material_types_from_position(row.position) != ("SBT",):
        return None
    exercise_numbers: list[str] = []
    for field in ("position", "question"):
        for match in SBT_EXERCISE_REFERENCE_RE.finditer(
            str(getattr(row, field, "") or "")
        ):
            value = match.group("number")
            if value not in exercise_numbers:
                exercise_numbers.append(value)
    return {
        "exercise_numbers": exercise_numbers,
        "question_section": SBT_QUESTION_SECTION,
        "solution_section": SBT_SOLUTION_SECTION,
        "instruction": (
            "Khi kiểm RAW-CON-02, phải thử đúng đầu mục lời giải trước khi "
            "kết thúc; đây chỉ là gợi ý truy vấn, không phải bằng chứng hoặc nhãn."
        ),
    }


def _is_sbt_solution_query(arguments: Mapping[str, Any]) -> bool:
    """Return whether model arguments explicitly target the canonical solution section."""

    actual = _canonical_query_text(str(arguments.get("section_keywords", "")))
    expected = _canonical_query_text(SBT_SOLUTION_SECTION)
    return bool(actual) and expected in actual


def _effective_sbt_section_keywords(
    section_keywords: str,
    *,
    sbt_scope: bool,
) -> tuple[str, bool]:
    """Lock explicit canonical SBT question/solution scopes before retrieval."""

    if not sbt_scope:
        return section_keywords, False
    actual = _canonical_query_text(section_keywords)
    solution = _canonical_query_text(SBT_SOLUTION_SECTION)
    question = _canonical_query_text(SBT_QUESTION_SECTION)
    if solution in actual:
        return SBT_SOLUTION_SECTION, actual != solution
    if question in actual:
        return SBT_QUESTION_SECTION, actual != question
    return section_keywords, False


def _image_evidence_context(
    row: RawDialogueRow,
    fragments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize model-visible image/text evidence without deciding dependency."""

    fragment_rows = [
        {
            "fragment_id": str(fragment.get("fragment_id", "")),
            "section_path": str(fragment.get("section_path", "")),
            "image_placeholder_count": int(
                fragment.get("image_placeholder_count", 0) or 0
            ),
            "effective_content_length": int(
                fragment.get("effective_content_length", 0) or 0
            ),
        }
        for fragment in fragments
    ]
    return {
        "raw_row_signals": image_dependency_hints(row)["matched_terms_by_field"],
        "returned_fragments": fragment_rows,
        "summary": {
            "fragment_count": len(fragment_rows),
            "fragments_with_image_placeholder": sum(
                row["image_placeholder_count"] > 0 for row in fragment_rows
            ),
            "fragments_with_effective_text": sum(
                row["effective_content_length"] > 0 for row in fragment_rows
            ),
            "total_image_placeholder_count": sum(
                row["image_placeholder_count"] for row in fragment_rows
            ),
        },
        "instruction": (
            "Các số liệu chỉ mô tả bằng chứng đã trả; tự đánh giá riêng từng "
            "tiêu chí bằng phép thử bỏ pixel ảnh."
        ),
    }


def _lesson_references(value: str) -> list[dict[str, str]]:
    """Extract conservative lesson/figure-number signals from one raw field."""

    references: list[dict[str, str]] = []
    for match in LESSON_REFERENCE_RE.finditer(str(value or "")):
        references.append(
            {
                "matched_text": match.group(0),
                "lesson_key": (
                    f"bai_{int(match.group('number')):02d}"
                    f"{match.group('suffix').lower()}"
                ),
            }
        )
    return references


def metadata_scope_hints(row: RawDialogueRow) -> dict[str, Any]:
    """Expose deterministic scope conflicts without deciding a criterion."""

    references = {
        field: _lesson_references(str(getattr(row, field, "") or ""))
        for field in ("lesson", "position", "question")
    }
    keys_by_field = {
        field: sorted({item["lesson_key"] for item in items})
        for field, items in references.items()
    }
    conflicts: list[dict[str, Any]] = []
    fields = ("lesson", "position", "question")
    for left_index, left_field in enumerate(fields):
        for right_field in fields[left_index + 1 :]:
            left_keys = set(keys_by_field[left_field])
            right_keys = set(keys_by_field[right_field])
            if left_keys and right_keys and left_keys.isdisjoint(right_keys):
                conflicts.append(
                    {
                        "left_field": left_field,
                        "left_lesson_keys": sorted(left_keys),
                        "right_field": right_field,
                        "right_lesson_keys": sorted(right_keys),
                    }
                )
    return {
        "references_by_field": references,
        "lesson_keys_by_field": keys_by_field,
        "direct_scope_conflict_candidate": bool(conflicts),
        "conflicts": conflicts,
        "instruction": (
            "Đây là tín hiệu cú pháp xác định từ nhãn Bài/Hình, không phải kết luận. "
            "Nếu hai trường chỉ trực tiếp các bài khác nhau, phải xử lý như mâu "
            "thuẫn nội bộ rõ; nếu cách đánh số còn có nhiều cách hiểu thì giữ "
            "uncertain và giải thích giới hạn."
        ),
    }


def pedagogical_error_hints(row: RawDialogueRow) -> dict[str, Any]:
    """Find explicit praise immediately after a likely malformed spreadsheet answer."""

    turns = [
        line.strip()
        for line in project_dialogue_for_model(row.dialogue).splitlines()
        if line.strip()
    ]
    candidates: list[dict[str, str]] = []
    for index, turn in enumerate(turns[:-1]):
        if not turn.casefold().startswith("hs:"):
            continue
        malformed = SPREADSHEET_MISSING_OPERATOR_RE.search(turn)
        following = turns[index + 1]
        if (
            malformed is not None
            and following.casefold().startswith("ai:")
            and POSITIVE_VALIDATION_RE.search(following)
        ):
            candidates.append(
                {
                    "student_turn": turn,
                    "suspected_expression": malformed.group(0),
                    "following_tutor_turn": following,
                }
            )
    return {
        "explicit_wrong_answer_validation_candidate": bool(candidates),
        "candidates": candidates,
        "instruction": (
            "Đây chỉ là tín hiệu xác định. Nếu hội thoại cho thấy học sinh đưa "
            "câu trả lời sai rõ ràng và gia sư xác nhận/khen mà không sửa, "
            "RAW-PED-04 phải fail; không hạ thành uncertain chỉ vì thiếu học liệu."
        ),
    }


def load_regression_spec(path: Path) -> RegressionSpec:
    """Load and validate a human-locked criterion/image regression contract."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    schema_version = str(raw.get("schema_version", ""))
    if schema_version not in SUPPORTED_REGRESSION_SPEC_SCHEMA_VERSIONS:
        raise PilotContractError(
            f"Unsupported regression spec schema: {raw.get('schema_version')!r}"
        )
    provenance = raw.get("provenance")
    if not isinstance(provenance, Mapping):
        raise PilotContractError("Regression spec provenance must be an object")
    workbook = Path(str(provenance.get("source_review_workbook", "")))
    workbook_sha256 = str(
        provenance.get("source_review_workbook_sha256", "")
    ).strip()
    if not workbook.is_file() or not re.fullmatch(r"[0-9a-f]{64}", workbook_sha256):
        raise PilotContractError(
            "Regression spec requires an existing source workbook and SHA-256"
        )
    if sha256_file(workbook) != workbook_sha256:
        raise PilotContractError("Regression review workbook hash does not match spec")

    scope_raw = raw.get("cluster_scope")
    if not isinstance(scope_raw, Mapping) or not scope_raw:
        raise PilotContractError("Regression cluster_scope must be a non-empty object")
    cluster_scope: dict[str, tuple[str, ...]] = {}
    for sample_id, values in scope_raw.items():
        if not isinstance(values, list):
            raise PilotContractError("Each regression cluster scope must be an array")
        clusters = tuple(str(value).strip() for value in values)
        if (
            not str(sample_id).strip()
            or not clusters
            or len(clusters) != len(set(clusters))
            or any(value not in MODEL_CLUSTERS for value in clusters)
        ):
            raise PilotContractError(
                f"Invalid regression cluster scope for {sample_id!r}: {clusters}"
            )
        cluster_scope[str(sample_id).strip()] = clusters

    criterion_rows = raw.get("criterion_expectations")
    if not isinstance(criterion_rows, list) or not criterion_rows:
        raise PilotContractError("Regression criterion_expectations must be non-empty")
    criterion_expectations: list[RegressionCriterionExpectation] = []
    criterion_keys: set[tuple[str, str]] = set()
    review_ids: set[str] = set()
    for value in criterion_rows:
        if not isinstance(value, Mapping):
            raise PilotContractError("Regression criterion expectation must be an object")
        expectation = RegressionCriterionExpectation(
            review_id=str(value.get("review_id", "")).strip(),
            sample_id=str(value.get("sample_id", "")).strip(),
            criterion_id=str(value.get("criterion_id", "")).strip(),
            allowed_results=tuple(
                str(item).strip() for item in value.get("allowed_results", [])
            ),
            required_evidence_fragment_ids=tuple(
                str(item).strip()
                for item in value.get("required_evidence_fragment_ids", [])
            ),
            role=str(value.get("role", "target")).strip(),
            preferred_result=(
                str(value.get("preferred_result", "")).strip() or None
            ),
        )
        key = (expectation.sample_id, expectation.criterion_id)
        cluster_id = next(
            (
                candidate
                for candidate, criterion_ids in CLUSTER_CRITERIA.items()
                if expectation.criterion_id in criterion_ids
            ),
            "",
        )
        if (
            not expectation.review_id
            or not expectation.sample_id
            or not cluster_id
            or cluster_id not in cluster_scope.get(expectation.sample_id, ())
            or not expectation.allowed_results
            or any(item not in ALLOWED_RESULTS for item in expectation.allowed_results)
            or (
                expectation.preferred_result is not None
                and expectation.preferred_result not in expectation.allowed_results
            )
            or expectation.role not in {"target", "control"}
            or key in criterion_keys
            or expectation.review_id in review_ids
        ):
            raise PilotContractError(
                f"Invalid regression criterion expectation: {value!r}"
            )
        criterion_keys.add(key)
        review_ids.add(expectation.review_id)
        criterion_expectations.append(expectation)

    image_rows = raw.get("image_expectations")
    if not isinstance(image_rows, list):
        raise PilotContractError("Regression image_expectations must be an array")
    image_expectations: list[RegressionImageExpectation] = []
    for value in image_rows:
        if not isinstance(value, Mapping):
            raise PilotContractError("Regression image expectation must be an object")
        if schema_version == "hnmu-dialogue-audit-regression-spec-v1":
            criterion_ids = tuple(
                str(item).strip() for item in value.get("criterion_ids", [])
            )
            expected_dependency = str(
                value.get("expected_dependency", "")
            ).strip()
            dependency_by_criterion = {
                criterion_id: expected_dependency for criterion_id in criterion_ids
            }
        else:
            dependency_raw = value.get("expected_dependency_by_criterion")
            if not isinstance(dependency_raw, Mapping):
                raise PilotContractError(
                    "Regression v2 image expectation requires "
                    "expected_dependency_by_criterion"
                )
            dependency_by_criterion = {
                str(criterion_id).strip(): str(dependency).strip()
                for criterion_id, dependency in dependency_raw.items()
            }
        expectation = RegressionImageExpectation(
            review_id=str(value.get("review_id", "")).strip(),
            sample_id=str(value.get("sample_id", "")).strip(),
            expected_dependency_by_criterion=dependency_by_criterion,
        )
        if (
            not expectation.review_id
            or expectation.review_id in review_ids
            or "B" not in cluster_scope.get(expectation.sample_id, ())
            or set(expectation.criterion_ids) != set(CLUSTER_CRITERIA["B"])
            or any(
                dependency not in ALLOWED_IMAGE_DEPENDENCIES
                for dependency in expectation.expected_dependency_by_criterion.values()
            )
        ):
            raise PilotContractError(
                f"Invalid regression image expectation: {value!r}"
            )
        review_ids.add(expectation.review_id)
        image_expectations.append(expectation)

    return RegressionSpec(
        path=path,
        source_review_workbook=workbook,
        source_review_workbook_sha256=workbook_sha256,
        cluster_scope=cluster_scope,
        criterion_expectations=tuple(criterion_expectations),
        image_expectations=tuple(image_expectations),
        spec_sha256=sha256_file(path),
    )


def _criterion_evidence_fragment_ids(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Read evidence IDs from current or future criterion-result schemas."""

    if "evidence_fragment_ids" in record:
        raw = record.get("evidence_fragment_ids")
        if not isinstance(raw, list):
            raise PilotContractError(
                "criterion_result.evidence_fragment_ids must be an array"
            )
        values = [str(value).strip() for value in raw]
    else:
        raw = record.get("evidence_fragment_id", "")
        if not isinstance(raw, str):
            raise PilotContractError(
                "criterion_result.evidence_fragment_id must be a string"
            )
        values = [value.strip() for value in raw.split(";")]
    return tuple(sorted({value for value in values if value}))


def evaluate_regression_results(
    records: Sequence[Mapping[str, Any]],
    spec: RegressionSpec,
) -> dict[str, Any]:
    """Evaluate one targeted run against the approved human regression gates."""

    by_key = {
        (str(row.get("sample_id", "")), str(row.get("criterion_id", ""))): row
        for row in records
        if row.get("record_type") == "criterion_result"
    }
    criterion_checks: list[dict[str, Any]] = []
    for expectation in spec.criterion_expectations:
        key = (expectation.sample_id, expectation.criterion_id)
        actual = by_key.get(key)
        actual_result = str(actual.get("result", "")) if actual else ""
        actual_evidence = (
            set(_criterion_evidence_fragment_ids(actual)) if actual else set()
        )
        result_matches = actual_result in expectation.allowed_results
        missing_evidence = sorted(
            set(expectation.required_evidence_fragment_ids) - actual_evidence
        )
        failure_reasons: list[str] = []
        if actual is None:
            failure_reasons.append("missing_result")
        elif not result_matches:
            failure_reasons.append("wrong_result")
        if missing_evidence:
            failure_reasons.append("missing_required_evidence")
        criterion_checks.append(
            {
                "review_id": expectation.review_id,
                "role": expectation.role,
                "sample_id": expectation.sample_id,
                "criterion_id": expectation.criterion_id,
                "allowed_results": list(expectation.allowed_results),
                "actual_result": actual_result or None,
                "result_matches": result_matches,
                "preferred_result": expectation.preferred_result,
                "preferred_result_matches": (
                    actual_result == expectation.preferred_result
                    if expectation.preferred_result is not None
                    else None
                ),
                "required_evidence_fragment_ids": list(
                    expectation.required_evidence_fragment_ids
                ),
                "missing_required_evidence_fragment_ids": missing_evidence,
                "actual_evidence_fragment_ids": sorted(actual_evidence),
                "failure_reasons": failure_reasons,
                "passed": result_matches and not missing_evidence,
            }
        )

    image_checks: list[dict[str, Any]] = []
    image_criterion_check_count = 0
    passed_image_criterion_check_count = 0
    for expectation in spec.image_expectations:
        mismatches: list[dict[str, Any]] = []
        criterion_checks_for_sample: list[dict[str, Any]] = []
        for criterion_id in expectation.criterion_ids:
            expected_dependency = expectation.expected_dependency_by_criterion[
                criterion_id
            ]
            actual = by_key.get((expectation.sample_id, criterion_id))
            actual_dependency = (
                str(actual.get("image_dependency", "")) if actual else ""
            )
            image_criterion_check_count += 1
            passed = actual_dependency == expected_dependency
            if passed:
                passed_image_criterion_check_count += 1
            check = {
                "criterion_id": criterion_id,
                "expected_dependency": expected_dependency,
                "actual_dependency": actual_dependency or None,
                "failure_reason": (
                    None
                    if passed
                    else "missing_result"
                    if actual is None
                    else "wrong_image_dependency"
                ),
                "passed": passed,
            }
            criterion_checks_for_sample.append(check)
            if not passed:
                mismatches.append(check)
        image_checks.append(
            {
                "review_id": expectation.review_id,
                "sample_id": expectation.sample_id,
                "criterion_ids": list(expectation.criterion_ids),
                "expected_dependency_by_criterion": dict(
                    expectation.expected_dependency_by_criterion
                ),
                "criterion_checks": criterion_checks_for_sample,
                "mismatches": mismatches,
                "passed": not mismatches,
            }
        )

    all_checks = [*criterion_checks, *image_checks]
    preferred_checks = [
        item
        for item in criterion_checks
        if item["preferred_result"] is not None
    ]
    preferred_hits = sum(
        bool(item["preferred_result_matches"]) for item in preferred_checks
    )
    return {
        "schema_version": REGRESSION_SPEC_SCHEMA_VERSION,
        "regression_spec_path": spec.path.as_posix(),
        "regression_spec_sha256": spec.spec_sha256,
        "criterion_check_count": len(criterion_checks),
        "image_check_count": len(image_checks),
        "image_criterion_check_count": image_criterion_check_count,
        "passed_image_criterion_check_count": passed_image_criterion_check_count,
        "passed_check_count": (
            sum(bool(item["passed"]) for item in criterion_checks)
            + passed_image_criterion_check_count
        ),
        "passed_case_count": sum(bool(item["passed"]) for item in all_checks),
        "all_gates_passed": all(bool(item["passed"]) for item in all_checks),
        "preferred_result_check_count": len(preferred_checks),
        "preferred_result_hit_count": preferred_hits,
        "preferred_result_hit_rate": (
            preferred_hits / len(preferred_checks) if preferred_checks else None
        ),
        "criterion_checks": criterion_checks,
        "image_checks": image_checks,
    }


def config_fingerprint(config: PilotConfig) -> str:
    """Hash behavior-affecting configuration values without credentials."""

    payload = {
        "experiment_id": config.experiment_id,
        "paths": {
            "normalized_rows": config.normalized_rows_path.as_posix(),
            "normalized_rows_manifest": (
                config.normalized_rows_manifest_path.as_posix()
                if config.normalized_rows_manifest_path is not None
                else None
            ),
            "criteria": config.criteria_path.as_posix(),
            "bloom_reference": config.bloom_reference_path.as_posix(),
            "scaffolding_reference": config.scaffolding_reference_path.as_posix(),
            "base_prompt": config.base_prompt_path.as_posix(),
            "prompt_bundle_manifest": (
                config.prompt_bundle_manifest_path.as_posix()
            ),
            "retrieval_index": config.retrieval_index_path.as_posix(),
            "selection": config.selection_path.as_posix(),
            "regression_spec": (
                config.regression_spec_path.as_posix()
                if config.regression_spec_path is not None
                else None
            ),
        },
        "runtime": {
            "model": config.model,
            "location": config.location,
            "max_output_tokens": config.max_output_tokens,
            "seed": config.seed,
            "thinking_level": config.thinking_level,
            "timeout_seconds": config.timeout_seconds,
            "include_tool_response_contract_in_prompt": (
                config.include_tool_response_contract_in_prompt
            ),
            "max_successful_tool_calls_per_cluster": (
                config.max_successful_tool_calls_per_cluster
            ),
            "max_total_tool_calls_per_cluster": config.max_total_tool_calls_per_cluster,
            "max_retries_per_cluster": config.max_retries_per_cluster,
            "retry_backoff_seconds": config.retry_backoff_seconds,
            "max_output_repair_attempts": config.max_output_repair_attempts,
        },
        "near_duplicate_threshold": config.near_duplicate_threshold,
        "selection_seed": config.selection_seed,
        "samples_per_grade": config.samples_per_grade,
        "development_per_grade": config.development_per_grade,
        "base_selection": (
            config.base_selection_path.as_posix()
            if config.base_selection_path is not None
            else None
        ),
        "source_quotas": [
            {
                "source_file": quota.source_file,
                "development": quota.development,
                "holdout": quota.holdout,
                "reserve": quota.reserve,
            }
            for quota in config.source_quotas
        ],
        "recovery": (
            {
                "parent_output_dir": config.recovery.parent_output_dir.as_posix(),
                "split": config.recovery.split,
                "target_sample_id": config.recovery.target_sample_id,
                "target_cluster_id": config.recovery.target_cluster_id,
                "expected_parent_run_fingerprint": (
                    config.recovery.expected_parent_run_fingerprint
                ),
                "expected_parent_result_sha256": (
                    config.recovery.expected_parent_result_sha256
                ),
                "expected_parent_trace_sha256": (
                    config.recovery.expected_parent_trace_sha256
                ),
                "expected_parent_summary_sha256": (
                    config.recovery.expected_parent_summary_sha256
                ),
                "expected_parent_counts": {
                    "sample_count": config.recovery.expected_parent_sample_count,
                    "completed_sample_count": (
                        config.recovery.expected_parent_completed_sample_count
                    ),
                    "criterion_result_count": (
                        config.recovery.expected_parent_criterion_result_count
                    ),
                    "sample_summary_count": (
                        config.recovery.expected_parent_sample_summary_count
                    ),
                    "completed_cluster_count": (
                        config.recovery.expected_parent_completed_cluster_count
                    ),
                },
                "expected_final_counts": {
                    "criterion_result_count": (
                        config.recovery.expected_final_criterion_result_count
                    ),
                    "sample_summary_count": (
                        config.recovery.expected_final_sample_summary_count
                    ),
                    "completed_cluster_count": (
                        config.recovery.expected_final_completed_cluster_count
                    ),
                },
            }
            if config.recovery is not None
            else None
        ),
    }
    return sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def build_run_contract(
    config: PilotConfig,
    *,
    split: str,
    selection: Sequence[SelectionRow],
) -> dict[str, Any]:
    """Build the immutable contract used to guard a resumable run."""

    input_hashes = {
        "config": config_fingerprint(config),
        "normalized_rows": sha256_file(config.normalized_rows_path),
        "criteria_registry": sha256_file(config.criteria_path),
        "selection": sha256_file(config.selection_path),
        "retrieval_index_file": sha256_file(config.retrieval_index_path),
        "base_prompt": sha256_file(config.base_prompt_path),
        "bloom_reference": sha256_file(config.bloom_reference_path),
        "scaffolding_reference": sha256_file(config.scaffolding_reference_path),
        "adapter_source": sha256_file(Path(__file__)),
        "retrieval_source": sha256_file(Path(search_learning_fragments.__code__.co_filename)),
    }
    input_hashes.update(prompt_bundle_input_hashes(config))
    if config.normalized_rows_manifest_path is not None:
        input_hashes["normalized_rows_manifest"] = sha256_file(
            config.normalized_rows_manifest_path
        )
    if config.regression_spec_path is not None:
        input_hashes["regression_spec"] = sha256_file(
            config.regression_spec_path
        )
    contract = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "experiment_id": config.experiment_id,
        "split": split,
        "selected_sample_ids": [row.sample_id for row in selection],
        "input_hashes": input_hashes,
        "runtime": {
            "model": config.model,
            "location": config.location,
            "max_output_tokens": config.max_output_tokens,
            "seed": config.seed,
            "thinking_level": config.thinking_level,
            "timeout_seconds": config.timeout_seconds,
            "include_tool_response_contract_in_prompt": (
                config.include_tool_response_contract_in_prompt
            ),
            "max_successful_tool_calls_per_cluster": (
                config.max_successful_tool_calls_per_cluster
            ),
            "max_total_tool_calls_per_cluster": config.max_total_tool_calls_per_cluster,
            "max_retries_per_cluster": config.max_retries_per_cluster,
            "retry_backoff_seconds": config.retry_backoff_seconds,
            "max_output_repair_attempts": config.max_output_repair_attempts,
            "near_duplicate_threshold": config.near_duplicate_threshold,
        },
    }
    return {
        **contract,
        "run_fingerprint": sha256_text(
            json.dumps(contract, ensure_ascii=False, sort_keys=True)
        ),
    }


def atomic_write_text(path: Path, content: str) -> None:
    """Atomically write UTF-8 text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically write one indented JSON document."""

    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def atomic_write_jsonl(path: Path, payloads: Sequence[Mapping[str, Any]]) -> None:
    """Atomically replace a JSONL file with complete objects."""

    content = "".join(
        json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
        for payload in payloads
    )
    atomic_write_text(path, content)


def append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    """Append and fsync one JSON object for resumable execution."""

    append_jsonl_many(path, (payload,))


def append_jsonl_many(path: Path, payloads: Sequence[Mapping[str, Any]]) -> None:
    """Append and fsync one logical batch of JSONL objects."""

    if not payloads:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            "".join(
                json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
                for payload in payloads
            )
        )
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file or return an empty list when it does not exist."""

    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise PilotContractError(f"Invalid JSONL at {path}:{line_number}") from exc
            if not isinstance(value, dict):
                raise PilotContractError(f"JSONL row must be an object at {path}:{line_number}")
            rows.append(value)
    return rows


def read_jsonl_recoverable_tail(path: Path) -> tuple[list[dict[str, Any]], bool]:
    """Read JSONL while allowing only one truncated final non-empty line."""

    if not path.exists():
        return [], False
    raw_lines = path.read_bytes().split(b"\n")
    nonempty_indexes = [index for index, line in enumerate(raw_lines) if line.strip()]
    last_nonempty_index = nonempty_indexes[-1] if nonempty_indexes else None
    rows: list[dict[str, Any]] = []
    for index, raw_line in enumerate(raw_lines):
        if not raw_line.strip():
            continue
        try:
            line = raw_line.decode("utf-8")
            value = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            if index == last_nonempty_index:
                return rows, True
            raise PilotContractError(f"Invalid JSONL at {path}:{index + 1}") from exc
        if not isinstance(value, dict):
            raise PilotContractError(f"JSONL row must be an object at {path}:{index + 1}")
        rows.append(value)
    return rows, False


def load_normalized_rows(path: Path) -> list[RawDialogueRow]:
    """Load the exact normalized Plan 04 CSV schema used by Plan 03."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = [field for field in NORMALIZED_FIELDS if field not in fields]
        if missing:
            raise PilotContractError("Normalized CSV is missing fields: " + ", ".join(missing))
        present_provenance = [field for field in DIALOGUE_PROVENANCE_FIELDS if field in fields]
        if present_provenance and len(present_provenance) != len(DIALOGUE_PROVENANCE_FIELDS):
            missing_provenance = sorted(set(DIALOGUE_PROVENANCE_FIELDS) - set(fields))
            raise PilotContractError(
                "Normalized CSV has partial dialogue provenance fields: "
                + ", ".join(missing_provenance)
            )
        has_dialogue_provenance = bool(present_provenance)
        rows = []
        for raw in reader:
            try:
                source_row_number = int(str(raw.get("source_row_number", "")).strip())
            except ValueError as exc:
                raise PilotContractError(
                    f"Invalid source_row_number for {raw.get('sample_id', '<unknown>')}"
                ) from exc
            provenance: dict[str, Any] = {}
            if has_dialogue_provenance:
                raw_dialogue = str(raw.get("dialogue_raw", ""))
                normalized_dialogue = str(raw.get("dialogue", ""))
                expected = normalize_dialogue_text(raw_dialogue)
                try:
                    flags_raw = json.loads(
                        str(raw.get("dialogue_normalization_flags_json", "[]"))
                    )
                except json.JSONDecodeError as exc:
                    raise PilotContractError(
                        "Invalid dialogue_normalization_flags_json for "
                        f"{raw.get('sample_id', '<unknown>')}"
                    ) from exc
                if not isinstance(flags_raw, list) or any(
                    not isinstance(value, str) for value in flags_raw
                ):
                    raise PilotContractError(
                        "dialogue_normalization_flags_json must be a string array for "
                        f"{raw.get('sample_id', '<unknown>')}"
                    )
                changed_raw = str(
                    raw.get("dialogue_normalization_changed", "")
                ).strip().casefold()
                if changed_raw not in {"true", "false"}:
                    raise PilotContractError(
                        "dialogue_normalization_changed must be true/false for "
                        f"{raw.get('sample_id', '<unknown>')}"
                    )
                try:
                    annotation_count = int(
                        str(raw.get("dialogue_annotation_count", "0")).strip()
                    )
                except ValueError as exc:
                    raise PilotContractError(
                        "Invalid dialogue_annotation_count for "
                        f"{raw.get('sample_id', '<unknown>')}"
                    ) from exc
                recorded_version = str(
                    raw.get("dialogue_normalization_version", "")
                ).strip()
                if recorded_version != DIALOGUE_NORMALIZATION_VERSION:
                    raise PilotContractError(
                        "Unsupported dialogue normalization version for "
                        f"{raw.get('sample_id', '<unknown>')}: {recorded_version!r}"
                    )
                recorded_raw_hash = str(raw.get("dialogue_raw_sha256", "")).strip()
                recorded_normalized_hash = str(
                    raw.get("dialogue_normalized_sha256", "")
                ).strip()
                if (
                    normalized_dialogue != expected.normalized_text
                    or recorded_raw_hash != expected.raw_sha256
                    or recorded_normalized_hash != expected.normalized_sha256
                    or annotation_count != expected.annotation_count
                    or tuple(flags_raw) != expected.flags
                    or (changed_raw == "true") != expected.changed
                ):
                    raise PilotContractError(
                        "Dialogue normalization provenance mismatch for "
                        f"{raw.get('sample_id', '<unknown>')}"
                    )
                provenance = {
                    "dialogue_raw": raw_dialogue,
                    "dialogue_raw_sha256": recorded_raw_hash,
                    "dialogue_normalized_sha256": recorded_normalized_hash,
                    "dialogue_normalization_version": recorded_version,
                    "dialogue_normalization_changed": expected.changed,
                    "dialogue_annotation_count": annotation_count,
                    "dialogue_normalization_flags": tuple(flags_raw),
                }
            rows.append(
                RawDialogueRow(
                    sample_id=str(raw.get("sample_id", "")).strip(),
                    source_file=str(raw.get("source_file", "")).strip(),
                    source_row_number=source_row_number,
                    grade=str(raw.get("grade", "")).strip(),
                    grade_label=str(raw.get("grade_label", "")).strip(),
                    stt=str(raw.get("stt", "")).strip(),
                    lesson=str(raw.get("lesson", "")).strip(),
                    position=str(raw.get("position", "")).strip(),
                    question=str(raw.get("question", "")).strip(),
                    bloom_level=str(raw.get("bloom_level", "")).strip(),
                    answer_sgv=str(raw.get("answer_sgv", "")).strip(),
                    dialogue=str(raw.get("dialogue", "")).strip(),
                    **provenance,
                )
            )
    sample_ids = [row.sample_id for row in rows]
    if any(not value for value in sample_ids) or len(sample_ids) != len(set(sample_ids)):
        raise PilotContractError("Normalized rows require unique non-empty sample_id values")
    return rows


def load_criteria(path: Path) -> dict[str, CriterionSpec]:
    """Load exactly the 18 required per-sample checklist criteria."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    specs: dict[str, CriterionSpec] = {}
    for row in rows:
        if str(row.get("required_per_sample", "")).strip().lower() != "true":
            continue
        criterion_id = str(row.get("criterion_id", "")).strip()
        if not criterion_id or criterion_id in specs:
            raise PilotContractError(f"Invalid or duplicate criterion_id: {criterion_id!r}")
        specs[criterion_id] = CriterionSpec(
            criterion_id=criterion_id,
            criterion_group=str(row.get("criterion_group", "")).strip(),
            criterion_name=str(row.get("criterion_name", "")).strip(),
            evidence_requirement=str(row.get("evidence_requirement", "")).strip(),
            pass_condition=str(row.get("pass_condition", "")).strip(),
            fail_or_uncertain_policy=str(row.get("fail_or_uncertain_policy", "")).strip(),
            default_reviewer_action=str(row.get("default_reviewer_action", "")).strip(),
        )
    expected = {value for cluster in CLUSTER_CRITERIA.values() for value in cluster}
    if set(specs) != expected or len(specs) != 18:
        raise PilotContractError(
            f"Criteria registry mismatch: expected={sorted(expected)}, actual={sorted(specs)}"
        )
    return specs


def material_types_from_position(position: str) -> tuple[str, ...]:
    """Return an unambiguous material type from the normalized position field."""

    upper = position.upper()
    found = tuple(value for value in sorted(ALLOWED_MATERIAL_TYPES) if re.search(rf"\b{value}\b", upper))
    return found if len(found) == 1 else ()


def trusted_filters(row: RawDialogueRow) -> dict[str, object]:
    """Derive only deterministic metadata filters from one normalized row."""

    filters: dict[str, object] = {"grade": row.grade}
    key = lesson_key(row.lesson)
    if key:
        filters["lesson_key"] = key
    materials = material_types_from_position(row.position)
    if materials:
        filters["material_type"] = materials[0]
    return filters


def _selection_bucket(row: RawDialogueRow) -> str:
    materials = material_types_from_position(row.position)
    material = materials[0] if materials else "UNRESOLVED"
    mapping = "MAPPED" if lesson_key(row.lesson) else "UNMAPPED"
    position_lower = row.position.casefold()
    if not row.position.strip():
        position_clarity = "MISSING_POSITION"
    elif materials and any(
        token in position_lower
        for token in ("trang", "mục", "bài tập", "luyện tập", "vận dụng")
    ):
        position_clarity = "CLEAR_POSITION"
    else:
        position_clarity = "PARTIAL_POSITION"
    turn_count = len(speaker_labels(row.dialogue))
    if turn_count < 4:
        dialogue_band = "SHORT_DIALOGUE"
    elif turn_count < 8:
        dialogue_band = "MEDIUM_DIALOGUE"
    else:
        dialogue_band = "LONG_DIALOGUE"
    cognitive = bloom_band(row.bloom_level).replace(" ", "_").upper()
    return "|".join(
        (material, mapping, position_clarity, dialogue_band, f"BLOOM_{cognitive}")
    )


def _selection_tags(row: RawDialogueRow) -> set[str]:
    return set(_selection_bucket(row).split("|"))


def _stable_rank(seed: str, row: RawDialogueRow) -> str:
    return sha256_text(f"{seed}|{row.grade}|{row.sample_id}")


def select_pilot_rows(
    rows: Sequence[RawDialogueRow],
    *,
    seed: str,
    samples_per_grade: int,
    development_per_grade: int,
) -> list[SelectionRow]:
    """Select a deterministic diversity-aware four-grade pilot."""

    by_grade: dict[str, list[RawDialogueRow]] = defaultdict(list)
    for row in rows:
        by_grade[row.grade].append(row)
    if set(by_grade) != {"6", "7", "8", "9"}:
        raise PilotContractError(f"Expected grades 6-9, found {sorted(by_grade)}")

    selected: list[SelectionRow] = []
    order = 0
    for grade in ("6", "7", "8", "9"):
        candidates = sorted(
            by_grade[grade], key=lambda row: (_stable_rank(seed, row), row.sample_id)
        )
        chosen: list[RawDialogueRow] = []
        covered_tags: set[str] = set()
        remaining = list(candidates)
        while remaining and len(chosen) < samples_per_grade:
            best = min(
                remaining,
                key=lambda row: (
                    -len(_selection_tags(row) - covered_tags),
                    _stable_rank(seed, row),
                    row.sample_id,
                ),
            )
            chosen.append(best)
            covered_tags.update(_selection_tags(best))
            remaining.remove(best)
        if len(chosen) != samples_per_grade:
            raise PilotContractError(f"Grade {grade} has insufficient pilot candidates")
        chosen.sort(key=lambda row: (_stable_rank(seed + "|split", row), row.sample_id))
        for grade_index, row in enumerate(chosen):
            order += 1
            selected.append(
                SelectionRow(
                    sample_id=row.sample_id,
                    grade=grade,
                    split="development" if grade_index < development_per_grade else "holdout",
                    selection_order=order,
                    diversity_bucket=_selection_bucket(row),
                    source_file=row.source_file,
                    selection_source="legacy_grade_balanced",
                )
            )
    return selected


def _duplicate_group_ids(
    rows: Sequence[RawDialogueRow],
    *,
    near_threshold: float,
) -> dict[str, str]:
    """Return stable connected-component IDs for exact/near duplicate rows."""

    parent = {row.sample_id: row.sample_id for row in rows}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        winner, loser = sorted((left_root, right_root))
        parent[loser] = winner

    for pair in duplicate_rows(rows, near_threshold=near_threshold):
        left = str(pair.get("sample_id_a", ""))
        right = str(pair.get("sample_id_b", ""))
        if left in parent and right in parent:
            union(left, right)

    members: dict[str, list[str]] = defaultdict(list)
    for sample_id in parent:
        members[find(sample_id)].append(sample_id)
    output: dict[str, str] = {}
    for component in members.values():
        group_id = "DUP-" + sha256_text("|".join(sorted(component)))[:16]
        for sample_id in component:
            output[sample_id] = group_id
    return output


def extend_pilot_rows(
    rows: Sequence[RawDialogueRow],
    *,
    base_selection: Sequence[SelectionRow],
    source_quotas: Sequence[SelectionSourceQuota],
    seed: str,
    near_threshold: float,
) -> list[SelectionRow]:
    """Preserve a locked selection and append balanced source-level quotas."""

    by_id = {row.sample_id: row for row in rows}
    if len(by_id) != len(rows):
        raise PilotContractError("Extension input rows require unique sample IDs")
    missing_base = [item.sample_id for item in base_selection if item.sample_id not in by_id]
    if missing_base:
        raise PilotContractError(
            f"Base selection IDs are missing from extension input: {missing_base}"
        )
    duplicate_groups = _duplicate_group_ids(rows, near_threshold=near_threshold)
    group_split: dict[str, str] = {}
    selected: list[SelectionRow] = []
    for item in sorted(base_selection, key=lambda value: value.selection_order):
        row = by_id[item.sample_id]
        group_id = duplicate_groups[row.sample_id]
        previous_split = group_split.get(group_id)
        if previous_split is not None and previous_split != item.split:
            raise PilotContractError(
                "Historical selection already leaks one duplicate group across splits: "
                f"{group_id}"
            )
        group_split[group_id] = item.split
        selected.append(
            SelectionRow(
                sample_id=item.sample_id,
                grade=item.grade,
                split=item.split,
                selection_order=item.selection_order,
                diversity_bucket=item.diversity_bucket,
                source_file=row.source_file,
                selection_source="locked_base",
                duplicate_group_id=group_id,
            )
        )

    selected_ids = {item.sample_id for item in selected}
    selected_groups = {item.duplicate_group_id for item in selected}
    covered_tags_by_source_split: dict[tuple[str, str], set[str]] = defaultdict(set)
    order = max((item.selection_order for item in selected), default=0)
    quota_by_split = (
        ("development", "development"),
        ("holdout", "holdout"),
        ("reserve", "reserve"),
    )
    for quota in source_quotas:
        source_rows = [
            row
            for row in rows
            if Path(row.source_file).as_posix() == quota.source_file
            and row.sample_id not in selected_ids
        ]
        if len(source_rows) < quota.total:
            raise PilotContractError(
                f"Source {quota.source_file} has {len(source_rows)} candidates for "
                f"quota total {quota.total}"
            )
        for split, attribute in quota_by_split:
            target_count = int(getattr(quota, attribute))
            chosen_count = 0
            covered_tags = covered_tags_by_source_split[(quota.source_file, split)]
            while chosen_count < target_count:
                candidates = [
                    row
                    for row in source_rows
                    if row.sample_id not in selected_ids
                    and duplicate_groups[row.sample_id] not in selected_groups
                ]
                if not candidates:
                    raise PilotContractError(
                        f"Source {quota.source_file} cannot satisfy split={split}; "
                        "duplicate-group isolation exhausted eligible candidates"
                    )
                best = min(
                    candidates,
                    key=lambda row: (
                        -len(_selection_tags(row) - covered_tags),
                        sha256_text(
                            f"{seed}|{quota.source_file}|{split}|{row.sample_id}"
                        ),
                        row.sample_id,
                    ),
                )
                group_id = duplicate_groups[best.sample_id]
                order += 1
                selected.append(
                    SelectionRow(
                        sample_id=best.sample_id,
                        grade=best.grade,
                        split=split,
                        selection_order=order,
                        diversity_bucket=_selection_bucket(best),
                        source_file=best.source_file,
                        selection_source="round2_source_quota",
                        duplicate_group_id=group_id,
                    )
                )
                selected_ids.add(best.sample_id)
                selected_groups.add(group_id)
                group_split[group_id] = split
                covered_tags.update(_selection_tags(best))
                chosen_count += 1
    return selected


def write_selection(path: Path, rows: Sequence[SelectionRow]) -> None:
    """Write a locked selection manifest atomically."""

    fieldnames = (
        "sample_id",
        "grade",
        "split",
        "selection_order",
        "diversity_bucket",
        "source_file",
        "selection_source",
        "duplicate_group_id",
    )
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
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sample_id": row.sample_id,
                    "grade": row.grade,
                    "split": row.split,
                    "selection_order": row.selection_order,
                    "diversity_bucket": row.diversity_bucket,
                    "source_file": row.source_file,
                    "selection_source": row.selection_source,
                    "duplicate_group_id": row.duplicate_group_id,
                }
            )
        temporary = Path(handle.name)
    os.replace(temporary, path)


def load_selection(path: Path) -> list[SelectionRow]:
    """Load and validate a locked 16-sample selection manifest."""

    if not path.is_file():
        raise PilotContractError(f"Selection manifest does not exist: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    rows = [
        SelectionRow(
            sample_id=str(row.get("sample_id", "")).strip(),
            grade=str(row.get("grade", "")).strip(),
            split=str(row.get("split", "")).strip(),
            selection_order=int(str(row.get("selection_order", "0"))),
            diversity_bucket=str(row.get("diversity_bucket", "")).strip(),
            source_file=str(row.get("source_file", "")).strip(),
            selection_source=str(row.get("selection_source", "")).strip(),
            duplicate_group_id=str(row.get("duplicate_group_id", "")).strip(),
        )
        for row in raw_rows
    ]
    if not rows or len({row.sample_id for row in rows}) != len(rows):
        raise PilotContractError("Selection manifest requires unique non-empty samples")
    if any(
        not row.sample_id or row.split not in {"development", "holdout", "reserve"}
        for row in rows
    ):
        raise PilotContractError("Selection contains an invalid sample_id or split")
    orders = [row.selection_order for row in rows]
    if any(value <= 0 for value in orders) or len(orders) != len(set(orders)):
        raise PilotContractError("Selection requires unique positive selection_order values")
    return sorted(rows, key=lambda row: row.selection_order)


def validate_selection_contract(
    selection: Sequence[SelectionRow],
    *,
    rows: Sequence[RawDialogueRow],
    config: PilotConfig,
) -> None:
    """Validate legacy or source-quota selection against its normalized input."""

    by_id = {row.sample_id: row for row in rows}
    missing = [item.sample_id for item in selection if item.sample_id not in by_id]
    if missing:
        raise PilotContractError(
            f"Selected sample IDs are missing from normalized data: {missing}"
        )
    if not config.source_quotas:
        return

    if config.base_selection_path is None:
        raise PilotContractError("Extension selection requires base_selection_manifest")
    base = load_selection(config.base_selection_path)
    actual_by_id = {item.sample_id: item for item in selection}
    for item in base:
        actual = actual_by_id.get(item.sample_id)
        if actual is None or actual.split != item.split:
            raise PilotContractError(
                f"Extension selection must preserve base split for {item.sample_id}"
            )
    base_ids = {item.sample_id for item in base}
    quota_sources = {quota.source_file for quota in config.source_quotas}
    extensions = [item for item in selection if item.sample_id not in base_ids]
    if any(Path(by_id[item.sample_id].source_file).as_posix() not in quota_sources for item in extensions):
        raise PilotContractError("Extension selection contains a non-declared source")
    for quota in config.source_quotas:
        counts = Counter(
            item.split
            for item in extensions
            if Path(by_id[item.sample_id].source_file).as_posix() == quota.source_file
        )
        expected = {
            "development": quota.development,
            "holdout": quota.holdout,
            "reserve": quota.reserve,
        }
        if {key: counts.get(key, 0) for key in expected} != expected:
            raise PilotContractError(
                f"Selection quota mismatch for {quota.source_file}: "
                f"expected={expected}, actual={dict(counts)}"
            )
    group_splits: dict[str, set[str]] = defaultdict(set)
    for item in selection:
        if item.duplicate_group_id:
            group_splits[item.duplicate_group_id].add(item.split)
    leaked = sorted(group for group, splits in group_splits.items() if len(splits) > 1)
    if leaked:
        raise PilotContractError(
            f"Duplicate groups cross selection splits: {leaked}"
        )


def extract_reference_body(
    text: str,
    *,
    start_marker: str,
    end_marker: str | None,
) -> str:
    """Remove human-facing provenance metadata before sending a reference to Gemini."""

    start = text.find(start_marker)
    if start < 0:
        raise PilotContractError(f"Reference start marker not found: {start_marker}")
    if end_marker is None:
        end = len(text)
    else:
        end = text.find(end_marker, start + len(start_marker))
        if end < 0:
            end = len(text)
    body = text[start:end].strip()
    if not body:
        raise PilotContractError(f"Reference body is empty after marker: {start_marker}")
    return body


def _criterion_payload(spec: CriterionSpec) -> dict[str, str]:
    return {
        "criterion_id": spec.criterion_id,
        "criterion_group": spec.criterion_group,
        "criterion_name": spec.criterion_name,
        "evidence_requirement": spec.evidence_requirement,
        "pass_condition": spec.pass_condition,
        "fail_or_uncertain_policy": spec.fail_or_uncertain_policy,
        "default_reviewer_action": spec.default_reviewer_action,
    }


def _row_context(row: RawDialogueRow, cluster_id: str) -> dict[str, str]:
    data = row.to_dict()
    output = {field: str(data[field]) for field in ROW_FIELDS_BY_CLUSTER[cluster_id]}
    if "dialogue" in output:
        output["dialogue"] = project_dialogue_for_model(output["dialogue"])
    return output


def _tool_response_contract_prompt(
    *,
    prompt_bundle: AuditPromptBundle,
    max_successful_tool_calls: int,
    max_total_tool_calls: int,
) -> str:
    """Describe the complete model-visible retrieval response contract."""

    return _render_prompt_template(
        prompt_bundle,
        "cluster_b_tool_response_contract",
        max_successful_tool_calls=max_successful_tool_calls,
        max_total_tool_calls=max_total_tool_calls,
    ).strip()


def _render_prompt_template(
    prompt_bundle: AuditPromptBundle,
    component: str,
    **values: Any,
) -> str:
    """Render one validated prompt component and reject undeclared variables."""

    try:
        template = prompt_bundle.templates[component]
    except KeyError as exc:
        raise PilotContractError(
            f"Prompt bundle is missing component: {component}"
        ) from exc
    try:
        return template.rstrip().format(**values)
    except (KeyError, ValueError) as exc:
        raise PilotContractError(
            f"Cannot render prompt bundle component {component}: {exc}"
        ) from exc


def build_cluster_prompt(
    *,
    cluster_id: str,
    row: RawDialogueRow,
    criteria: Mapping[str, CriterionSpec],
    base_prompt: str,
    bloom_reference: str,
    scaffolding_reference: str,
    include_tool_response_contract: bool = True,
    max_successful_tool_calls: int = 3,
    max_total_tool_calls: int = 8,
    max_output_tokens: int = 8192,
    prompt_bundle: AuditPromptBundle | None = None,
) -> tuple[str, str, str]:
    """Build the exact system/user prompts for one model-driven cluster."""

    if cluster_id not in MODEL_CLUSTERS:
        raise PilotContractError(f"Cluster {cluster_id} is not model-driven")
    if prompt_bundle is None:
        prompt_bundle = load_audit_prompt_bundle(DEFAULT_PROMPT_BUNDLE_MANIFEST)
    criterion_rows = [_criterion_payload(criteria[value]) for value in CLUSTER_CRITERIA[cluster_id]]
    system_parts = [
        base_prompt.strip(),
        "\nCác tiêu chí bắt buộc:\n"
        + json.dumps(criterion_rows, ensure_ascii=False, indent=2),
    ]
    if cluster_id == "B":
        tool_contract = ""
        if include_tool_response_contract:
            tool_contract = "\n\n" + _tool_response_contract_prompt(
                prompt_bundle=prompt_bundle,
                max_successful_tool_calls=max_successful_tool_calls,
                max_total_tool_calls=max_total_tool_calls,
            )
        system_parts.append(
            _render_prompt_template(
                prompt_bundle,
                "cluster_b",
                max_successful_tool_calls=max_successful_tool_calls,
                max_total_tool_calls=max_total_tool_calls,
                max_output_tokens=max_output_tokens,
                tool_response_contract_block=tool_contract,
                reason_max_chars=CLUSTER_B_REASON_MAX_CHARS,
                evidence_reason_max_chars=(
                    CLUSTER_B_EVIDENCE_MATCH_REASON_MAX_CHARS
                ),
            ).strip()
        )
    elif cluster_id == "C":
        system_parts.append(
            _render_prompt_template(
                prompt_bundle,
                "cluster_c",
                bloom_reference=bloom_reference.strip(),
                reason_max_chars=MODEL_REASON_MAX_CHARS,
                evidence_reason_max_chars=MODEL_EVIDENCE_MATCH_REASON_MAX_CHARS,
            )
        )
    elif cluster_id == "D":
        system_parts.append(
            _render_prompt_template(
                prompt_bundle,
                "cluster_d",
                scaffolding_reference=scaffolding_reference.strip(),
                reason_max_chars=MODEL_REASON_MAX_CHARS,
                evidence_reason_max_chars=MODEL_EVIDENCE_MATCH_REASON_MAX_CHARS,
            )
        )
    elif cluster_id == "E":
        system_parts.append(
            _render_prompt_template(
                prompt_bundle,
                "cluster_e",
                reason_max_chars=MODEL_REASON_MAX_CHARS,
                evidence_reason_max_chars=MODEL_EVIDENCE_MATCH_REASON_MAX_CHARS,
            ).strip()
        )
    system_instruction = "\n\n".join(system_parts).strip()
    user_payload = {
        "sample_id": row.sample_id,
        "cluster_id": cluster_id,
        "normalized_row": _row_context(row, cluster_id),
        "required_criterion_ids": list(CLUSTER_CRITERIA[cluster_id]),
    }
    if cluster_id == "B":
        user_payload["image_dependency_hints"] = image_dependency_hints(row)
        user_payload["metadata_scope_hints"] = metadata_scope_hints(row)
        hints = sbt_retrieval_hints(row)
        if hints is not None:
            user_payload["sbt_retrieval_hints"] = hints
    elif cluster_id == "E":
        user_payload["pedagogical_error_hints"] = pedagogical_error_hints(row)
    user_prompt = json.dumps(user_payload, ensure_ascii=False, indent=2)
    prompt_hash = sha256_text(system_instruction + "\n---USER---\n" + user_prompt)
    return system_instruction, user_prompt, prompt_hash


def model_output_schema(cluster_id: str) -> dict[str, Any]:
    """Return the strict JSON contract requested from Gemini."""

    evidence_schema: dict[str, Any] = {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "Chỉ chứa fragment_id do công cụ trả về và thực sự được dùng."
            if cluster_id == "B"
            else "Cụm không có công cụ fragment; bắt buộc trả về mảng rỗng."
        ),
    }
    if cluster_id != "B":
        evidence_schema["maxItems"] = 0

    reason_max_chars = (
        CLUSTER_B_REASON_MAX_CHARS
        if cluster_id == "B"
        else MODEL_REASON_MAX_CHARS
    )
    evidence_reason_max_chars = (
        CLUSTER_B_EVIDENCE_MATCH_REASON_MAX_CHARS
        if cluster_id == "B"
        else MODEL_EVIDENCE_MATCH_REASON_MAX_CHARS
    )
    result_properties: dict[str, Any] = {
        "criterion_id": {"type": "string"},
        "result": {"type": "string", "enum": sorted(ALLOWED_RESULTS)},
        "confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": (
                SUBJECTIVE_CLUSTER_MAX_CONFIDENCE
                if cluster_id in {"C", "D", "E"}
                else 1
            ),
        },
        "evidence_fragment_ids": evidence_schema,
        "evidence_match_reason": {
            "type": "string",
            "maxLength": evidence_reason_max_chars,
        },
        "reason": {
            "type": "string",
            "maxLength": reason_max_chars,
        },
        "suggested_reviewer_action": {
            "type": "string",
            "enum": sorted(ALLOWED_REVIEW_ACTIONS),
        },
    }
    required_fields = [
        "criterion_id",
        "result",
        "confidence_score",
        "evidence_fragment_ids",
        "evidence_match_reason",
        "reason",
        "suggested_reviewer_action",
    ]
    if cluster_id == "B":
        result_properties.update(
            {
                "evidence_basis": {
                    "type": "string",
                    "enum": sorted(ALLOWED_EVIDENCE_BASES),
                },
                "evidence_basis_fields": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": sorted(ALLOWED_EVIDENCE_BASIS_FIELDS),
                    },
                    "uniqueItems": True,
                },
                "image_dependency": {
                    "type": "string",
                    "enum": sorted(ALLOWED_IMAGE_DEPENDENCIES),
                },
                "image_dependency_reason": {
                    "type": "string",
                    "maxLength": reason_max_chars,
                },
                "needs_image_review": {"type": "boolean"},
            }
        )
        required_fields.extend(
            [
                "image_dependency",
                "image_dependency_reason",
                "needs_image_review",
                "evidence_basis",
                "evidence_basis_fields",
            ]
        )

    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "results": {
                "type": "array",
                "minItems": len(CLUSTER_CRITERIA[cluster_id]),
                "maxItems": len(CLUSTER_CRITERIA[cluster_id]),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": result_properties,
                    "required": required_fields,
                },
            }
        },
        "required": ["results"],
    }


def retrieval_tool_schema() -> dict[str, Any]:
    """Expose only model-owned retrieval arguments, never trusted filters."""

    return {
        "name": SEARCH_TOOL_NAME,
        "description": (
            "Tìm tối đa năm đoạn học liệu theo nội dung trong đầu mục phù hợp "
            "nhất. Cung cấp từ khóa tiếng Việt ngắn gọn cho đầu mục và nội dung."
        ),
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "section_keywords": {"type": "string", "minLength": 1},
                "content_keywords": {"type": "string", "minLength": 1},
                "material_types": {
                    "type": ["array", "null"],
                    "items": {"type": "string", "enum": sorted(ALLOWED_MATERIAL_TYPES)},
                    "uniqueItems": True,
                },
            },
            "required": ["section_keywords", "content_keywords"],
        },
    }


def _canonical_query_text(value: str) -> str:
    """Normalize model-owned query text for exact repeated-query detection."""

    normalized = unicodedata.normalize("NFC", value)
    punctuation_normalized = "".join(
        " " if unicodedata.category(character).startswith("P") else character
        for character in normalized
    )
    return re.sub(r"\s+", " ", punctuation_normalized).strip().casefold()


def _canonical_filter_values(filters: Mapping[str, object]) -> dict[str, list[str]]:
    """Normalize effective trusted filters for a stable query signature."""

    output: dict[str, list[str]] = {}
    for key in sorted(filters):
        raw = filters[key]
        values = raw if isinstance(raw, (list, tuple, set, frozenset)) else [raw]
        output[key] = sorted(
            {
                _canonical_query_text(str(value))
                for value in values
                if str(value).strip()
            }
        )
    return output


class AuditRetrievalAdapter:
    """Bind trusted sample scope and project Plan 02 results for Gemini."""

    def __init__(
        self,
        *,
        row: RawDialogueRow,
        index_path: Path,
        search_fn: Callable[..., RetrievalResult] = search_learning_fragments,
    ) -> None:
        self.row = row
        self.index_path = index_path
        self.search_fn = search_fn
        self._trusted_filters = trusted_filters(row)
        self._query_cache: dict[str, ToolExecution] = {}

    @property
    def trusted_filters(self) -> dict[str, object]:
        return dict(self._trusted_filters)

    def execute(self, arguments: Mapping[str, Any]) -> ToolExecution:
        """Validate model arguments, call Plan 02 directly, and project output."""

        allowed = {"section_keywords", "content_keywords", "material_types"}
        unknown = sorted(set(arguments) - allowed)
        if unknown:
            raise PilotContractError("Unsupported model tool arguments: " + ", ".join(unknown))
        section_keywords = str(arguments.get("section_keywords", "")).strip()
        content_keywords = str(arguments.get("content_keywords", "")).strip()
        if not section_keywords or not content_keywords:
            raise PilotContractError("Both section_keywords and content_keywords are required")
        if len(section_keywords) > 500 or len(content_keywords) > 500:
            raise PilotContractError("Retrieval keywords must not exceed 500 characters")

        requested_materials_raw = arguments.get("material_types")
        if requested_materials_raw is None:
            requested_materials: list[str] = []
        elif isinstance(requested_materials_raw, list):
            requested_materials = sorted({str(value).strip().upper() for value in requested_materials_raw})
        else:
            raise PilotContractError("material_types must be an array or null")
        if any(value not in ALLOWED_MATERIAL_TYPES for value in requested_materials):
            raise PilotContractError("material_types contains an unsupported value")

        filters = dict(self._trusted_filters)
        if "material_type" not in filters and requested_materials:
            filters["material_type"] = requested_materials
        effective_section_keywords, section_normalization_applied = (
            _effective_sbt_section_keywords(
                section_keywords,
                sbt_scope=filters.get("material_type") == "SBT",
            )
        )
        signature_payload = {
            "section_keywords": _canonical_query_text(effective_section_keywords),
            "content_keywords": _canonical_query_text(content_keywords),
            "material_types": requested_materials,
            "bound_filters": _canonical_filter_values(filters),
            "index_path": self.index_path.resolve().as_posix(),
        }
        query_signature = sha256_text(
            json.dumps(signature_payload, ensure_ascii=False, sort_keys=True)
        )
        cached = self._query_cache.get(query_signature)
        if cached is not None:
            visible = deepcopy(cached.visible_response)
            previous_status = str(visible.get("status", ""))
            visible["status"] = "repeated_query"
            visible["previous_status"] = previous_status
            trace = deepcopy(cached.trace)
            trace.update(
                {
                    "arguments_from_model": {
                        "section_keywords": section_keywords,
                        "content_keywords": content_keywords,
                        "material_types": requested_materials or None,
                    },
                    "effective_arguments": {
                        "section_keywords": effective_section_keywords,
                        "content_keywords": content_keywords,
                        "material_types": requested_materials or None,
                    },
                    "section_normalization_applied": section_normalization_applied,
                    "query_signature": query_signature,
                    "cache_hit": True,
                    "original_reason": trace.get("reason"),
                    "reason": "repeated_query",
                }
            )
            return ToolExecution(visible_response=visible, trace=trace)

        result = self.search_fn(
            effective_section_keywords,
            content_keywords,
            filters=filters,
            index_path=self.index_path,
            content_limit=5,
        )
        views: list[dict[str, Any]] = []
        ranked_trace: list[dict[str, Any]] = []
        for rank, raw in enumerate(result.results, start=1):
            if MODEL_FORBIDDEN_FRAGMENT_FIELDS.intersection(MODEL_FRAGMENT_FIELDS):
                raise AssertionError("Model fragment allowlist contains a forbidden field")
            view = {field: raw.get(field, "") for field in MODEL_FRAGMENT_FIELDS}
            markdown_text = str(raw.get("markdown_text", ""))
            image_placeholder_count = len(MARKDOWN_IMAGE_RE.findall(markdown_text))
            view["image_placeholder_count"] = image_placeholder_count
            view["effective_content_length"] = effective_content_length(markdown_text)
            view["rank"] = rank
            views.append(view)
            raw_source_types = raw.get("source_fragment_types_json", "")
            try:
                source_types = json.loads(str(raw_source_types)) if raw_source_types else []
            except json.JSONDecodeError:
                source_types = []
            if not isinstance(source_types, list) or not source_types:
                source_types = [str(raw.get("fragment_type", ""))]
            source_count = int(raw.get("merged_from_fragment_count", 0) or 0)
            if source_count <= 0:
                source_count = 1
            ranked_trace.append(
                {
                    "rank": rank,
                    "fragment_id": str(raw.get("fragment_id", "")),
                    "section_path": str(raw.get("section_path", "")),
                    "content_score": raw.get("content_score"),
                    "fragment_release": str(raw.get("fragment_release", "")),
                    "source_fragment_count": source_count,
                    "source_fragment_types": [str(value) for value in source_types],
                    "contains_table_source": "table" in source_types,
                    "image_placeholder_count": image_placeholder_count,
                    "effective_content_length": effective_content_length(markdown_text),
                }
            )
        visible_status = "success" if result.result_count else str(result.reason or "content_no_match")
        visible = {
            "status": visible_status,
            "matched_section_path": result.matched_section_path,
            "fragments": views,
            "image_evidence_context": _image_evidence_context(self.row, views),
        }
        trace = {
            "tool_name": SEARCH_TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "sample_id": self.row.sample_id,
            "arguments_from_model": {
                "section_keywords": section_keywords,
                "content_keywords": content_keywords,
                "material_types": requested_materials or None,
            },
            "effective_arguments": {
                "section_keywords": effective_section_keywords,
                "content_keywords": content_keywords,
                "material_types": requested_materials or None,
            },
            "section_normalization_applied": section_normalization_applied,
            "query_signature": query_signature,
            "cache_hit": False,
            "bound_filters": result.filters,
            "declared_scope": {
                "grade": self.row.grade,
                "lesson": self.row.lesson,
                "position": self.row.position,
            },
            "content_limit": 5,
            "mode": result.mode,
            "matched_section_path": result.matched_section_path,
            "section_score": result.section_score,
            "result_count": result.result_count,
            "reason": result.reason,
            "index_snapshot_sha256": result.snapshot_sha256,
            "ranked_results": ranked_trace,
            "image_evidence_context": visible["image_evidence_context"],
        }
        execution = ToolExecution(visible_response=visible, trace=trace)
        self._query_cache[query_signature] = deepcopy(execution)
        return execution


def smoke_sbt_section_normalization(
    *,
    index_path: Path,
    grade: str,
    lesson: str,
    position: str,
    canonical_section_keywords: str,
    decorated_section_keywords: str,
    content_keywords: str,
) -> dict[str, Any]:
    """Compare canonical and decorated SBT section queries through the adapter."""

    row = RawDialogueRow(
        sample_id="SBT-SECTION-SMOKE",
        source_file="smoke",
        source_row_number=0,
        grade=str(grade),
        grade_label=f"Lớp {grade}",
        stt="0",
        lesson=lesson,
        position=position,
        question=content_keywords,
        bloom_level="",
        answer_sgv="",
        dialogue="HS: Kiểm tra truy xuất.\nAI: Đang kiểm tra.",
    )
    adapter = AuditRetrievalAdapter(row=row, index_path=index_path)
    canonical = adapter.execute(
        {
            "section_keywords": canonical_section_keywords,
            "content_keywords": content_keywords,
            "material_types": ["SBT"],
        }
    )
    decorated = adapter.execute(
        {
            "section_keywords": decorated_section_keywords,
            "content_keywords": content_keywords,
            "material_types": ["SBT"],
        }
    )

    def projection(execution: ToolExecution) -> dict[str, Any]:
        return {
            "arguments_from_model": execution.trace["arguments_from_model"],
            "effective_arguments": execution.trace["effective_arguments"],
            "section_normalization_applied": execution.trace[
                "section_normalization_applied"
            ],
            "query_signature": execution.trace["query_signature"],
            "cache_hit": execution.trace["cache_hit"],
            "matched_section_path": execution.visible_response.get(
                "matched_section_path"
            ),
            "fragment_ids": [
                str(fragment.get("fragment_id", ""))
                for fragment in execution.visible_response.get("fragments", [])
            ],
        }

    canonical_projection = projection(canonical)
    decorated_projection = projection(decorated)
    equivalent = (
        canonical_projection["query_signature"]
        == decorated_projection["query_signature"]
        and canonical_projection["matched_section_path"]
        == decorated_projection["matched_section_path"]
        and canonical_projection["fragment_ids"]
        == decorated_projection["fragment_ids"]
    )
    if not equivalent:
        raise PilotContractError(
            "Canonical and decorated SBT section queries produced different results"
        )
    return {
        "schema_version": "hnmu-sbt-section-normalization-smoke-v1",
        "equivalent": True,
        "canonical": canonical_projection,
        "decorated": decorated_projection,
    }


def validate_model_results(
    payload: Mapping[str, Any],
    *,
    expected_ids: Sequence[str],
    visible_fragment_ids: set[str],
    cluster_id: str | None = None,
) -> tuple[dict[str, Any], ...]:
    """Validate exact criterion coverage and evidence provenance."""

    reason_max_chars = (
        CLUSTER_B_REASON_MAX_CHARS
        if cluster_id == "B"
        else MODEL_REASON_MAX_CHARS
    )
    evidence_reason_max_chars = (
        CLUSTER_B_EVIDENCE_MATCH_REASON_MAX_CHARS
        if cluster_id == "B"
        else MODEL_EVIDENCE_MATCH_REASON_MAX_CHARS
    )
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raise PilotContractError("Model output must contain a results array")
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_results:
        if not isinstance(raw, Mapping):
            raise PilotContractError("Each model result must be an object")
        criterion_id = str(raw.get("criterion_id", "")).strip()
        if criterion_id in seen:
            raise PilotContractError(f"Duplicate model criterion result: {criterion_id}")
        seen.add(criterion_id)
        result = str(raw.get("result", "")).strip()
        if result not in ALLOWED_RESULTS:
            raise PilotContractError(f"Invalid result for {criterion_id}: {result}")
        try:
            confidence = float(raw.get("confidence_score"))
        except (TypeError, ValueError) as exc:
            raise PilotContractError(f"Invalid confidence for {criterion_id}") from exc
        if not 0 <= confidence <= 1:
            raise PilotContractError(f"Confidence outside [0, 1] for {criterion_id}")
        evidence_raw = raw.get("evidence_fragment_ids", [])
        if not isinstance(evidence_raw, list):
            raise PilotContractError(f"evidence_fragment_ids must be an array for {criterion_id}")
        evidence_ids = sorted({str(value).strip() for value in evidence_raw if str(value).strip()})
        unknown_evidence = sorted(set(evidence_ids) - visible_fragment_ids)
        if unknown_evidence:
            raise PilotContractError(
                f"{criterion_id} cites fragments absent from tool trace: {unknown_evidence}"
            )
        action = str(raw.get("suggested_reviewer_action", "")).strip()
        if action not in ALLOWED_REVIEW_ACTIONS:
            raise PilotContractError(f"Invalid reviewer action for {criterion_id}: {action}")
        reason = str(raw.get("reason", "")).strip()
        if not reason:
            raise PilotContractError(f"Missing reason for {criterion_id}")
        if len(reason) > reason_max_chars:
            raise PilotContractError(
                f"reason exceeds {reason_max_chars} characters for {criterion_id}"
            )
        evidence_match_reason = str(raw.get("evidence_match_reason", "")).strip()
        if len(evidence_match_reason) > evidence_reason_max_chars:
            raise PilotContractError(
                "evidence_match_reason exceeds "
                f"{evidence_reason_max_chars} characters for {criterion_id}"
            )
        if cluster_id == "B" and not evidence_match_reason:
            raise PilotContractError(
                f"Missing evidence_match_reason for cluster-B criterion {criterion_id}"
            )
        record = {
            "criterion_id": criterion_id,
            "result": result,
            "confidence_score": confidence,
            "evidence_fragment_ids": evidence_ids,
            "evidence_match_reason": evidence_match_reason,
            "reason": reason,
            "suggested_reviewer_action": action,
        }
        if cluster_id == "B":
            evidence_basis = str(raw.get("evidence_basis", "")).strip()
            if evidence_basis not in ALLOWED_EVIDENCE_BASES:
                raise PilotContractError(
                    f"Invalid evidence_basis for {criterion_id}: {evidence_basis!r}"
                )
            evidence_basis_fields_raw = raw.get("evidence_basis_fields")
            if not isinstance(evidence_basis_fields_raw, list):
                raise PilotContractError(
                    f"evidence_basis_fields must be an array for {criterion_id}"
                )
            evidence_basis_fields = sorted(
                {
                    str(value).strip()
                    for value in evidence_basis_fields_raw
                    if str(value).strip()
                }
            )
            invalid_basis_fields = sorted(
                set(evidence_basis_fields) - ALLOWED_EVIDENCE_BASIS_FIELDS
            )
            if invalid_basis_fields:
                raise PilotContractError(
                    f"Invalid evidence_basis_fields for {criterion_id}: "
                    f"{invalid_basis_fields}"
                )
            if evidence_basis == "retrieved_fragment":
                if not evidence_ids or "retrieved_fragment" not in evidence_basis_fields:
                    raise PilotContractError(
                        f"{criterion_id} with retrieved_fragment basis must cite a "
                        "visible fragment and name retrieved_fragment"
                    )
            elif evidence_basis == "insufficient_learning_resource":
                if evidence_ids or "retrieved_fragment" in evidence_basis_fields:
                    raise PilotContractError(
                        f"{criterion_id} with insufficient_learning_resource must not "
                        "cite fragments or name retrieved_fragment"
                    )
            elif evidence_ids or "retrieved_fragment" in evidence_basis_fields:
                raise PilotContractError(
                    f"{criterion_id} cites a fragment but evidence_basis is "
                    f"{evidence_basis!r}"
                )
            if (
                criterion_id in CRITERIA_REQUIRING_FRAGMENT_FOR_PASS
                and result == "pass"
                and evidence_basis != "retrieved_fragment"
            ):
                raise PilotContractError(
                    f"{criterion_id} requires retrieved evidence for result=pass"
                )
            if evidence_basis == "direct_internal_contradiction":
                contradiction_fields = set(evidence_basis_fields)
                if (
                    result != "fail"
                    or len(contradiction_fields) < 2
                    or not contradiction_fields.issubset(
                        DIRECT_INTERNAL_EVIDENCE_FIELDS
                    )
                ):
                    raise PilotContractError(
                        f"{criterion_id} direct_internal_contradiction requires "
                        "result=fail and at least two raw-row fields"
                    )
            if (
                criterion_id in CRITERIA_REQUIRING_FRAGMENT_FOR_PASS
                and result == "fail"
                and not evidence_ids
            ):
                if criterion_id == "RAW-CON-03":
                    fragment_free_fail_allowed = (
                        evidence_basis == "raw_row_only"
                        and {"question", "dialogue"}.issubset(evidence_basis_fields)
                    )
                else:
                    fragment_free_fail_allowed = (
                        evidence_basis == "direct_internal_contradiction"
                    )
                if not fragment_free_fail_allowed:
                    raise PilotContractError(
                        f"{criterion_id} may fail without a fragment only through "
                        "its criterion-specific evidence contract"
                    )
            if evidence_basis in {"insufficient_learning_resource", "image_required"}:
                if result != "uncertain":
                    raise PilotContractError(
                        f"{criterion_id} with evidence_basis={evidence_basis} must "
                        "be uncertain"
                    )
            if evidence_basis == "raw_row_only" and criterion_id not in {
                "RAW-CON-03",
                "RAW-CON-04",
            }:
                raise PilotContractError(
                    f"{criterion_id} cannot use raw_row_only evidence"
                )
            if (
                criterion_id == "RAW-CON-03"
                and evidence_basis == "raw_row_only"
                and (
                    result not in {"fail", "uncertain"}
                    or not {"question", "dialogue"}.issubset(evidence_basis_fields)
                )
            ):
                raise PilotContractError(
                    "RAW-CON-03 raw_row_only evidence requires result=fail/uncertain "
                    "and both question and dialogue"
                )
            image_dependency = str(raw.get("image_dependency", "")).strip()
            if image_dependency not in ALLOWED_IMAGE_DEPENDENCIES:
                raise PilotContractError(
                    f"Invalid image_dependency for {criterion_id}: {image_dependency!r}"
                )
            image_dependency_reason = str(
                raw.get("image_dependency_reason", "")
            ).strip()
            if not image_dependency_reason:
                raise PilotContractError(
                    f"Missing image_dependency_reason for {criterion_id}"
                )
            if len(image_dependency_reason) > reason_max_chars:
                raise PilotContractError(
                    f"image_dependency_reason exceeds {reason_max_chars} "
                    f"characters for {criterion_id}"
                )
            needs_image_review = raw.get("needs_image_review")
            if not isinstance(needs_image_review, bool):
                raise PilotContractError(
                    f"needs_image_review must be boolean for {criterion_id}"
                )
            if image_dependency == "required" and (
                result != "uncertain"
                or not needs_image_review
                or evidence_basis != "image_required"
            ):
                raise PilotContractError(
                    f"{criterion_id} with required image dependency must be uncertain "
                    "with evidence_basis=image_required and needs_image_review=true"
                )
            if image_dependency == "required" and confidence >= 1.0:
                raise PilotContractError(
                    f"{criterion_id} with required image dependency must lower confidence"
                )
            if image_dependency == "supporting" and confidence >= 1.0:
                raise PilotContractError(
                    f"{criterion_id} with supporting image dependency must lower confidence"
                )
            if image_dependency == "none" and needs_image_review:
                raise PilotContractError(
                    f"{criterion_id} cannot request image review when dependency is none"
                )
            record.update(
                {
                    "evidence_basis": evidence_basis,
                    "evidence_basis_fields": evidence_basis_fields,
                    "image_dependency": image_dependency,
                    "image_dependency_reason": image_dependency_reason,
                    "needs_image_review": needs_image_review,
                }
            )
        elif cluster_id in {"C", "D", "E"} and confidence > SUBJECTIVE_CLUSTER_MAX_CONFIDENCE:
            raise PilotContractError(
                f"Confidence exceeds {SUBJECTIVE_CLUSTER_MAX_CONFIDENCE} for "
                f"subjective cluster criterion {criterion_id}"
            )
        output.append(record)
    if seen != set(expected_ids):
        raise PilotContractError(
            f"Model criterion coverage mismatch: expected={sorted(expected_ids)}, actual={sorted(seen)}"
        )
    by_id = {row["criterion_id"]: row for row in output}
    return tuple(by_id[value] for value in expected_ids)


def _response_content(response: Any) -> Any:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        raise PilotExecutionError("Gemini returned no candidates")
    content = getattr(candidates[0], "content", None)
    if content is None:
        raise PilotExecutionError("Gemini candidate has no content")
    return content


def _json_safe_trace_value(value: Any) -> Any:
    """Convert provider objects into JSON-safe trace values without reflection magic."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if isinstance(value, Mapping):
        return {str(key): _json_safe_trace_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_safe_trace_value(item) for item in value]
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if hasattr(value, "__dict__"):
        return {
            str(key): _json_safe_trace_value(item)
            for key, item in vars(value).items()
            if not str(key).startswith("_") and item is not None
        }
    return str(value)


def _model_response_content_for_trace(content: Any) -> tuple[dict[str, Any], int]:
    """Serialize one candidate content while omitting private thought parts.

    Gemini is configured with ``include_thoughts=False``. The additional filter
    is fail-safe: if a provider nevertheless returns a part explicitly marked
    as thought, the trace records only its omission count, never its content.
    Function calls, text, call IDs, and provider thought signatures attached to
    non-thought parts remain available for exact orchestration provenance.
    """

    serialized = _json_safe_trace_value(content)
    payload = dict(serialized) if isinstance(serialized, Mapping) else {}
    visible_parts: list[Any] = []
    omitted_thought_parts = 0
    for part in getattr(content, "parts", None) or []:
        if bool(getattr(part, "thought", False)):
            omitted_thought_parts += 1
            continue
        part_payload = _json_safe_trace_value(part)
        if isinstance(part_payload, Mapping):
            part_payload = dict(part_payload)
            part_payload.pop("thought", None)
        visible_parts.append(part_payload)
    payload["parts"] = visible_parts
    return payload, omitted_thought_parts


def _response_usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return {key: 0 for key in TOKEN_USAGE_KEYS}
    if hasattr(usage, "model_dump"):
        data = usage.model_dump(mode="json", exclude_none=True)
    elif isinstance(usage, Mapping):
        data = dict(usage)
    else:
        data = {}
    input_tokens = int(data.get("prompt_token_count", 0) or 0)
    candidate_tokens = int(data.get("candidates_token_count", 0) or 0)
    thoughts_tokens = int(data.get("thoughts_token_count", 0) or 0)
    tool_use_prompt_tokens = int(data.get("tool_use_prompt_token_count", 0) or 0)
    output_tokens = candidate_tokens + thoughts_tokens
    return {
        "input_tokens": input_tokens,
        "candidate_tokens": candidate_tokens,
        "thoughts_tokens": thoughts_tokens,
        "tool_use_prompt_tokens": tool_use_prompt_tokens,
        "output_tokens": output_tokens,
        "total_tokens": int(data.get("total_token_count", input_tokens + output_tokens) or 0),
    }


def _finish_reason(response: Any) -> str:
    candidates = getattr(response, "candidates", None) or []
    value = getattr(candidates[0], "finish_reason", None) if candidates else None
    name = getattr(value, "name", None)
    return str(name or value or "UNKNOWN").rsplit(".", 1)[-1].upper()


def _function_calls(content: Any) -> list[Any]:
    return [
        getattr(part, "function_call")
        for part in (getattr(content, "parts", None) or [])
        if getattr(part, "function_call", None) is not None
    ]


def _text_parts(content: Any) -> str:
    return "".join(
        str(getattr(part, "text", "") or "")
        for part in (getattr(content, "parts", None) or [])
        if not bool(getattr(part, "thought", False))
    ).strip()


def _tool_budget_state(
    *,
    total_used: int,
    successful_used: int,
    max_total: int,
    max_successful: int,
) -> dict[str, int | bool]:
    """Return the model-visible dynamic tool budget after one response."""

    total_remaining = max(0, max_total - total_used)
    successful_remaining = max(0, max_successful - successful_used)
    return {
        "total_used": total_used,
        "total_remaining": total_remaining,
        "successful_used": successful_used,
        "successful_remaining": successful_remaining,
        "must_finalize": total_remaining == 0 or successful_remaining == 0,
    }


def run_gemini_cluster(
    *,
    client: Any,
    model: str,
    thinking_level: str,
    max_output_tokens: int,
    seed: int,
    system_instruction: str,
    user_prompt: str,
    prompt_sha256: str,
    cluster_id: str,
    expected_ids: Sequence[str],
    retrieval_adapter: AuditRetrievalAdapter | None,
    max_successful_tool_calls: int,
    max_total_tool_calls: int,
    max_output_repair_attempts: int = 0,
    trace_sink: Callable[[dict[str, Any]], None] | None = None,
) -> ModelClusterResult:
    """Run a manual Google Gen AI tool loop with complete observable trace."""

    from google.genai import types

    contents: list[Any] = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
    ]
    kwargs: dict[str, Any] = {
        "system_instruction": system_instruction,
        "max_output_tokens": max_output_tokens,
        "seed": seed,
        "response_mime_type": "application/json",
        "response_json_schema": model_output_schema(cluster_id),
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
        "thinking_config": types.ThinkingConfig(
            include_thoughts=False,
            thinking_level=getattr(types.ThinkingLevel, thinking_level),
        ),
    }
    if retrieval_adapter is not None:
        declaration = types.FunctionDeclaration(
            name=SEARCH_TOOL_NAME,
            description=retrieval_tool_schema()["description"],
            parameters_json_schema=retrieval_tool_schema()["parameters"],
        )
        kwargs["tools"] = [types.Tool(function_declarations=[declaration])]
        kwargs["tool_config"] = types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="AUTO")
        )
    config = types.GenerateContentConfig(**kwargs)
    trace_events: list[dict[str, Any]] = []
    visible_fragment_ids: set[str] = set()
    visible_fragments_by_id: dict[str, dict[str, Any]] = {}
    total_usage = {key: 0 for key in TOKEN_USAGE_KEYS}
    total_tool_call_count = 0
    successful_tool_call_count = 0
    budget_exhaustion_response_count = 0
    final_response: Any | None = None
    sbt_scope = bool(
        retrieval_adapter is not None
        and retrieval_adapter.trusted_filters.get("material_type") == "SBT"
    )
    sbt_solution_query_attempted = False
    sbt_solution_query_succeeded = False
    sbt_finalization_reminder_sent = False

    def record_trace(event: dict[str, Any]) -> None:
        trace_events.append(event)
        if trace_sink is not None:
            trace_sink(event)

    for round_index in range(max_total_tool_calls + 3):
        logger.info(
            "Calling Gemini for cluster={} round={} prompt_sha256={}",
            cluster_id,
            round_index,
            prompt_sha256[:12],
        )
        round_started = time.perf_counter()
        response = client.models.generate_content(model=model, contents=contents, config=config)
        round_latency_ms = round((time.perf_counter() - round_started) * 1000, 3)
        usage = _response_usage(response)
        for key in total_usage:
            total_usage[key] += usage[key]
        content = _response_content(response)
        calls = _function_calls(content)
        model_response_content, omitted_thought_parts = _model_response_content_for_trace(
            content
        )
        record_trace(
            {
                "event_type": "model_round",
                "round_index": round_index,
                "prompt_sha256": prompt_sha256,
                "request_snapshot": (
                    {"system_instruction": system_instruction, "user_prompt": user_prompt}
                    if round_index == 0
                    else None
                ),
                "function_call_count": len(calls),
                "finish_reason": _finish_reason(response),
                "latency_ms": round_latency_ms,
                "usage": usage,
                "model_version": str(getattr(response, "model_version", "") or model),
                "response_id": str(getattr(response, "response_id", "") or ""),
                "model_response_content": model_response_content,
                "model_response_thought_parts_omitted": omitted_thought_parts,
            }
        )
        logger.info(
            "Gemini returned cluster={} round={} latency_ms={} function_calls={} finish_reason={}",
            cluster_id,
            round_index,
            round_latency_ms,
            len(calls),
            _finish_reason(response),
        )
        if not calls and sbt_scope and not sbt_solution_query_attempted:
            if sbt_finalization_reminder_sent:
                raise PilotOutputContractError(
                    "SBT cluster finalized twice without attempting the canonical "
                    "solution section"
                )
            sbt_finalization_reminder_sent = True
            reminder = {
                "status": "sbt_solution_query_required",
                "solution_section": SBT_SOLUTION_SECTION,
                "instruction": (
                    "Chưa được kết thúc: hãy gọi công cụ với section_keywords "
                    "đúng đầu mục lời giải trước khi trả JSON cuối."
                ),
            }
            record_trace(
                {
                    "event_type": "sbt_solution_query_reminder",
                    "round_index": round_index,
                    "model_visible_response": reminder,
                }
            )
            contents.append(content)
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=json.dumps(reminder, ensure_ascii=False)
                        )
                    ],
                )
            )
            continue
        if not calls:
            final_response = response
            break
        if retrieval_adapter is None:
            raise PilotExecutionError(f"Cluster {cluster_id} attempted an unavailable tool call")
        contents.append(content)
        response_parts: list[Any] = []
        for call in calls:
            name = str(getattr(call, "name", "") or "")
            if name != SEARCH_TOOL_NAME:
                raise PilotExecutionError(f"Gemini requested unsupported tool: {name}")
            arguments = getattr(call, "args", None) or {}
            if not isinstance(arguments, Mapping):
                raise PilotExecutionError("Gemini tool arguments must be an object")

            is_solution_query = sbt_scope and _is_sbt_solution_query(arguments)
            if (
                sbt_scope
                and not sbt_solution_query_attempted
                and not is_solution_query
                and successful_tool_call_count >= max_successful_tool_calls - 1
            ):
                reserved_response = {
                    "status": "sbt_solution_query_required",
                    "tool_budget": _tool_budget_state(
                        total_used=total_tool_call_count,
                        successful_used=successful_tool_call_count,
                        max_total=max_total_tool_calls,
                        max_successful=max_successful_tool_calls,
                    ),
                    "matched_section_path": None,
                    "fragments": [],
                    "solution_section": SBT_SOLUTION_SECTION,
                    "instruction": (
                        "Một lượt có fragment đang được dành cho phần hướng dẫn "
                        "giải; đổi section_keywords sang đầu mục chuẩn này."
                    ),
                }
                record_trace(
                    {
                        "event_type": "sbt_solution_budget_reserved",
                        "round_index": round_index,
                        "arguments_from_model": dict(arguments),
                        "model_visible_response": reserved_response,
                    }
                )
                response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=getattr(call, "id", None),
                            name=SEARCH_TOOL_NAME,
                            response={"output": reserved_response},
                        )
                    )
                )
                continue

            budget_before = _tool_budget_state(
                total_used=total_tool_call_count,
                successful_used=successful_tool_call_count,
                max_total=max_total_tool_calls,
                max_successful=max_successful_tool_calls,
            )
            if bool(budget_before["must_finalize"]):
                budget_exhaustion_response_count += 1
                if budget_exhaustion_response_count > 1:
                    raise PilotContractError(
                        "Gemini repeated a tool call after receiving budget_exhausted"
                    )
                exhausted_response = {
                    "status": "budget_exhausted",
                    "tool_budget": budget_before,
                    "matched_section_path": None,
                    "fragments": [],
                }
                record_trace(
                    {
                        "event_type": "tool_budget_exhausted",
                        "round_index": round_index,
                        "arguments_from_model": dict(arguments),
                        "tool_budget": budget_before,
                        "model_visible_response": exhausted_response,
                    }
                )
                logger.warning(
                    "Blocked over-budget retrieval cluster={} total_used={} successful_used={}",
                    cluster_id,
                    total_tool_call_count,
                    successful_tool_call_count,
                )
                response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=getattr(call, "id", None),
                            name=SEARCH_TOOL_NAME,
                            response={"output": exhausted_response},
                        )
                    )
                )
                continue

            total_tool_call_count += 1
            if is_solution_query:
                sbt_solution_query_attempted = True
            retrieval_started = time.perf_counter()
            execution = retrieval_adapter.execute(arguments)
            retrieval_latency_ms = round(
                (time.perf_counter() - retrieval_started) * 1000,
                3,
            )
            has_results = int(execution.trace.get("result_count", 0) or 0) > 0
            if has_results:
                successful_tool_call_count += 1
                if is_solution_query:
                    sbt_solution_query_succeeded = True
            tool_budget = _tool_budget_state(
                total_used=total_tool_call_count,
                successful_used=successful_tool_call_count,
                max_total=max_total_tool_calls,
                max_successful=max_successful_tool_calls,
            )
            visible_response = deepcopy(execution.visible_response)
            visible_response["tool_budget"] = tool_budget
            if sbt_scope:
                visible_response["sbt_solution_query_state"] = {
                    "attempted": sbt_solution_query_attempted,
                    "succeeded": sbt_solution_query_succeeded,
                    "reserved_successful_slot": not sbt_solution_query_attempted,
                }
            visible_fragment_ids.update(
                str(row["fragment_id"])
                for row in visible_response["fragments"]
                if row.get("fragment_id")
            )
            for fragment in visible_response["fragments"]:
                fragment_id = str(fragment.get("fragment_id", "")).strip()
                if not fragment_id or fragment_id in visible_fragments_by_id:
                    continue
                visible_fragments_by_id[fragment_id] = {
                    "fragment_id": fragment_id,
                    "section_path": str(fragment.get("section_path", "")),
                    "markdown_text": str(fragment.get("markdown_text", "")),
                    "image_placeholder_count": int(
                        fragment.get("image_placeholder_count", 0) or 0
                    ),
                    "effective_content_length": int(
                        fragment.get("effective_content_length", 0) or 0
                    ),
                }
            record_trace(
                {
                    "event_type": "retrieval_tool_call",
                    "round_index": round_index,
                    "tool_call_index": total_tool_call_count,
                    "successful_tool_call_index": (
                        successful_tool_call_count if has_results else None
                    ),
                    "successful_tool_call_count": successful_tool_call_count,
                    "sbt_solution_query": bool(is_solution_query),
                    "sbt_solution_query_attempted": sbt_solution_query_attempted,
                    "sbt_solution_query_succeeded": sbt_solution_query_succeeded,
                    "tool_budget": tool_budget,
                    "latency_ms": retrieval_latency_ms,
                    **execution.trace,
                    "model_visible_response": visible_response,
                }
            )
            logger.info(
                "Retrieval completed cluster={} call={}/{} successful={}/{} status={} results={} cache_hit={} latency_ms={}",
                cluster_id,
                total_tool_call_count,
                max_total_tool_calls,
                successful_tool_call_count,
                max_successful_tool_calls,
                visible_response.get("status"),
                execution.trace.get("result_count"),
                execution.trace.get("cache_hit"),
                retrieval_latency_ms,
            )
            response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        id=getattr(call, "id", None),
                        name=SEARCH_TOOL_NAME,
                        response={"output": visible_response},
                    )
                )
            )
        contents.append(types.Content(role="user", parts=response_parts))
    if final_response is None:
        raise PilotExecutionError("Gemini did not produce a final response within the tool limit")
    if retrieval_adapter is not None and total_tool_call_count == 0:
        raise PilotExecutionError("Learning-resource cluster completed without retrieval")
    final_content = _response_content(final_response)
    text = _text_parts(final_content)
    if not text:
        try:
            text = str(final_response.text).strip()
        except (AttributeError, ValueError):
            text = ""
    final_finish_reason = _finish_reason(final_response)
    record_trace(
        {
            "event_type": "model_final_response_received",
            "raw_text": text,
            "raw_text_length": len(text),
            "raw_text_sha256": sha256_text(text),
            "finish_reason": final_finish_reason,
        }
    )
    if final_finish_reason == "MAX_TOKENS":
        raise PilotOutputTruncatedError(
            "Gemini final response was truncated because finish_reason=MAX_TOKENS "
            f"at max_output_tokens={max_output_tokens}; raw text is preserved in trace"
        )
    if not text:
        raise PilotExecutionError("Gemini returned no final JSON text")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PilotContractError("Gemini final response is not strict JSON") from exc
    if not isinstance(payload, Mapping):
        raise PilotContractError("Gemini final JSON must be an object")
    try:
        results = validate_model_results(
            payload,
            expected_ids=expected_ids,
            visible_fragment_ids=visible_fragment_ids,
            cluster_id=cluster_id,
        )
    except PilotContractError as validation_error:
        if max_output_repair_attempts != 1:
            raise
        validation_message = str(validation_error)
        evidence_contract_error = cluster_id == "B" and any(
            marker in validation_message
            for marker in (
                "fragment",
                "evidence_basis",
                "retrieved evidence",
            )
        )
        repair_request = {
            "task": "repair_output_contract",
            "validation_errors": [validation_message],
            "previous_json": payload,
            "instruction": (
                "Chỉ sửa lỗi hợp đồng được nêu; không dùng nhãn tham chiếu ẩn, "
                "không gọi công cụ và trả lại toàn bộ JSON hoàn chỉnh. Chỉ được "
                "viện dẫn đúng fragment_id có trong allowed_evidence_fragments; "
                "không được tự tạo ID. Nếu không có fragment nào trong danh sách "
                "đủ bảo vệ một kết luận pass bắt buộc học liệu, hãy đổi tiêu chí "
                "đó thành uncertain với evidence_basis="
                "insufficient_learning_resource và evidence_fragment_ids=[]."
            ),
        }
        if evidence_contract_error:
            repair_request["allowed_evidence_fragments"] = list(
                visible_fragments_by_id.values()
            )
        record_trace(
            {
                "event_type": "output_repair_requested",
                "repair_attempt": 1,
                "validation_errors": repair_request["validation_errors"],
                "previous_json": payload,
                "allowed_evidence_fragments": repair_request.get(
                    "allowed_evidence_fragments", []
                ),
            }
        )
        repair_config = types.GenerateContentConfig(
            system_instruction=(
                "Bạn sửa một JSON kết quả kiểm toán đã vi phạm hợp đồng đầu ra. "
                "Không truy xuất thêm bằng chứng và không thay đổi quyết định nội "
                "dung ngoài phần bắt buộc để khắc phục lỗi validation được cung cấp. "
                "Không được tự tạo fragment_id; khi danh sách fragment được phép "
                "không đủ bảo vệ pass thì phải dùng uncertain theo chỉ dẫn."
            ),
            max_output_tokens=max_output_tokens,
            seed=seed,
            response_mime_type="application/json",
            response_json_schema=model_output_schema(cluster_id),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            thinking_config=types.ThinkingConfig(
                include_thoughts=False,
                thinking_level=getattr(types.ThinkingLevel, thinking_level),
            ),
        )
        repair_started = time.perf_counter()
        repair_response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=json.dumps(repair_request, ensure_ascii=False)
                        )
                    ],
                )
            ],
            config=repair_config,
        )
        repair_latency_ms = round(
            (time.perf_counter() - repair_started) * 1000, 3
        )
        repair_usage = _response_usage(repair_response)
        for key in total_usage:
            total_usage[key] += repair_usage[key]
        repair_content = _response_content(repair_response)
        repair_text = _text_parts(repair_content)
        if not repair_text:
            try:
                repair_text = str(repair_response.text).strip()
            except (AttributeError, ValueError):
                repair_text = ""
        repair_finish_reason = _finish_reason(repair_response)
        repair_model_content, repair_thought_parts = (
            _model_response_content_for_trace(repair_content)
        )
        record_trace(
            {
                "event_type": "output_repair_response",
                "repair_attempt": 1,
                "latency_ms": repair_latency_ms,
                "finish_reason": repair_finish_reason,
                "usage": repair_usage,
                "response_id": str(
                    getattr(repair_response, "response_id", "") or ""
                ),
                "model_response_content": repair_model_content,
                "model_response_thought_parts_omitted": repair_thought_parts,
                "raw_text": repair_text,
            }
        )
        if repair_finish_reason == "MAX_TOKENS":
            raise PilotOutputTruncatedError(
                "Gemini output repair was truncated because finish_reason=MAX_TOKENS"
            )
        try:
            repaired_payload = json.loads(repair_text)
            if not isinstance(repaired_payload, Mapping):
                raise PilotContractError("Repaired JSON must be an object")
            results = validate_model_results(
                repaired_payload,
                expected_ids=expected_ids,
                visible_fragment_ids=visible_fragment_ids,
                cluster_id=cluster_id,
            )
        except (json.JSONDecodeError, PilotContractError) as repair_error:
            record_trace(
                {
                    "event_type": "output_repair_failed",
                    "repair_attempt": 1,
                    "error_type": type(repair_error).__name__,
                    "error": str(repair_error),
                }
            )
            raise PilotOutputContractError(
                "Gemini output repair failed validation: " + str(repair_error)
            ) from repair_error
        record_trace(
            {
                "event_type": "output_repair_succeeded",
                "repair_attempt": 1,
                "validated_criterion_ids": [
                    row["criterion_id"] for row in results
                ],
            }
        )
        payload = repaired_payload
        text = repair_text
        final_response = repair_response
        final_finish_reason = repair_finish_reason
    if cluster_id == "B" and not visible_fragment_ids:
        record_trace(
            {
                "event_type": "cluster_b_no_fragments",
                "raw_text": text,
                "validated_criterion_ids": [row["criterion_id"] for row in results],
                "policy": (
                    "fragment-required pass decisions cannot pass; RAW-CON-03 may "
                    "fail/uncertain from question+dialogue, while RAW-CON-04 remains "
                    "independently judgeable from normalized row fields"
                ),
            }
        )
    record_trace(
        {
            "event_type": "model_final_output",
            "raw_text": text,
            "validated_criterion_ids": [row["criterion_id"] for row in results],
        }
    )
    return ModelClusterResult(
        results=results,
        trace_events=tuple(trace_events),
        prompt_sha256=prompt_sha256,
        tool_call_count=total_tool_call_count,
        usage=total_usage,
        model_version=str(getattr(final_response, "model_version", "") or model),
        response_id=str(getattr(final_response, "response_id", "") or ""),
        finish_reason=final_finish_reason,
    )


def _base_result(
    *,
    row: RawDialogueRow,
    cluster_id: str,
    spec: CriterionSpec,
    result: str,
    confidence: float,
    reason: str,
    action: str,
    checked_by: str,
    checked_at: str,
    evidence_ids: Sequence[str] = (),
    evidence_match_reason: str = "",
    evidence_basis: str = "raw_row_only",
    evidence_basis_fields: Sequence[str] = (),
    image_dependency_candidate: bool = False,
    image_dependency: str = "none",
    image_dependency_reason: str = "",
    needs_image_review: bool = False,
) -> dict[str, Any]:
    return {
        "record_type": "criterion_result",
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "sample_id": row.sample_id,
        "grade": row.grade,
        "cluster_id": cluster_id,
        "criterion_id": spec.criterion_id,
        "criterion_group": spec.criterion_group,
        "criterion_name": spec.criterion_name,
        "result": result,
        "confidence_score": confidence,
        "evidence_fragment_id": ";".join(evidence_ids),
        "evidence_source": "learning_resource_retrieval_v1" if evidence_ids else "normalized_dialogue_row",
        "evidence_match_reason": evidence_match_reason,
        "evidence_basis": evidence_basis,
        "evidence_basis_fields": list(evidence_basis_fields),
        "image_dependency_candidate": image_dependency_candidate,
        "image_dependency": image_dependency,
        "image_dependency_reason": image_dependency_reason,
        "needs_image_review": needs_image_review,
        "reason": reason,
        "suggested_reviewer_action": action,
        "checked_by": checked_by,
        "checked_at": checked_at,
    }


def evaluate_structure_cluster(
    row: RawDialogueRow,
    *,
    criteria: Mapping[str, CriterionSpec],
    checked_at: str,
) -> list[dict[str, Any]]:
    """Evaluate RAW-STR-02/03 deterministically."""

    missing = [name for name in ("question", "answer_sgv", "dialogue") if not getattr(row, name).strip()]
    if not missing:
        str02 = ("pass", 1.0, "Ba trường question, answer_sgv và dialogue đều có nội dung.", "keep")
    elif "question" in missing or "dialogue" in missing:
        str02 = (
            "fail",
            1.0,
            "Thiếu trường lõi: " + ", ".join(missing) + ".",
            "exclude_from_current_batch",
        )
    else:
        str02 = (
            "uncertain",
            1.0,
            "Thiếu answer_sgv; cần giáo viên xác nhận trước khi đối chiếu nội dung.",
            "ask_hnmu_review",
        )
    projected_dialogue = project_dialogue_for_model(row.dialogue)
    labels = speaker_labels(projected_dialogue)
    missing_labels = [value for value in ("HS", "AI") if value not in labels]
    unexpected = sorted({value for value in labels if value not in {"HS", "AI"}})
    if row.dialogue_normalization_flags:
        str03 = (
            "uncertain",
            1.0,
            "Chuẩn hóa hội thoại còn cờ mơ hồ: "
            + ", ".join(row.dialogue_normalization_flags)
            + ".",
            "ask_hnmu_review",
        )
    elif missing_labels:
        str03 = (
            "fail",
            1.0,
            "Thiếu nhãn lượt nói bắt buộc: " + ", ".join(missing_labels) + ".",
            "exclude_from_current_batch",
        )
    elif unexpected:
        str03 = (
            "uncertain",
            1.0,
            "Có nhãn lượt nói ngoài hợp đồng HS/AI: " + ", ".join(unexpected) + ".",
            "ask_hnmu_review",
        )
    else:
        str03 = ("pass", 1.0, "Hội thoại có nhãn HS và AI hợp lệ.", "keep")
    return [
        _base_result(
            row=row,
            cluster_id="A",
            spec=criteria[criterion_id],
            result=value[0],
            confidence=value[1],
            reason=value[2],
            action=value[3],
            checked_by="code:structure-v2",
            checked_at=checked_at,
        )
        for criterion_id, value in (("RAW-STR-02", str02), ("RAW-STR-03", str03))
    ]


def evaluate_duplicate_cluster(
    rows: Sequence[RawDialogueRow],
    *,
    criteria: Mapping[str, CriterionSpec],
    near_threshold: float,
    checked_at: str,
    candidate_pairs: Sequence[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate duplicate-risk criteria using the configured similarity threshold."""

    pairs = list(candidate_pairs) if candidate_pairs is not None else duplicate_rows(
        rows, near_threshold=near_threshold
    )
    by_sample: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_sample[str(pair["sample_id_a"])].append(pair)
        by_sample[str(pair["sample_id_b"])].append(pair)
    output: list[dict[str, Any]] = []
    for row in rows:
        sample_pairs = by_sample.get(row.sample_id, [])
        trivial_pairs = sample_pairs
        template_pairs = [
            pair
            for pair in sample_pairs
            if pair.get("duplicate_type") in {"exact_dialogue", "near_duplicate_combined_text"}
        ]
        for criterion_id, relevant in (
            ("RAW-DUP-03", trivial_pairs),
            ("RAW-DUP-04", template_pairs),
        ):
            if relevant:
                descriptions = []
                for pair in relevant:
                    other = pair["sample_id_b"] if pair["sample_id_a"] == row.sample_id else pair["sample_id_a"]
                    descriptions.append(
                        f"{pair['duplicate_type']} với {other}, similarity={pair['similarity']}"
                    )
                result = "uncertain"
                reason = "Mã lọc phát hiện: " + "; ".join(descriptions) + "."
                action = "ask_hnmu_review"
            else:
                result = "pass"
                reason = (
                    f"Không có cặp đạt điều kiện của tiêu chí trong toàn bộ tập chuẩn hóa "
                    f"ở ngưỡng gần trùng {near_threshold:.4f}."
                )
                action = "keep"
            output.append(
                _base_result(
                    row=row,
                    cluster_id="F",
                    spec=criteria[criterion_id],
                    result=result,
                    confidence=1.0,
                    reason=reason,
                    action=action,
                    checked_by=f"code:duplicate-threshold-{near_threshold:.4f}",
                    checked_at=checked_at,
                )
            )
    return output


def flagged_duplicate_summary(
    rows: Sequence[RawDialogueRow],
    *,
    near_threshold: float,
    candidate_pairs: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summarize exact and threshold-flagged duplicate scores for reporting."""

    pairs = list(candidate_pairs) if candidate_pairs is not None else duplicate_rows(
        rows, near_threshold=near_threshold
    )
    scores = [float(pair["similarity"]) for pair in pairs]
    return {
        "scope_sample_count": len(rows),
        "threshold": near_threshold,
        "flagged_pair_count": len(pairs),
        "exact_pair_count": sum(score == 1.0 for score in scores),
        "near_pair_count": sum(near_threshold <= score < 1.0 for score in scores),
        "flagged_score_min": min(scores) if scores else None,
        "flagged_score_max": max(scores) if scores else None,
        "flagged_score_distribution": dict(
            sorted(Counter(f"{score:.4f}" for score in scores).items())
        ),
    }


def enrich_model_results(
    *,
    row: RawDialogueRow,
    cluster_id: str,
    criteria: Mapping[str, CriterionSpec],
    model_result: ModelClusterResult,
    checked_at: str,
    model: str,
) -> list[dict[str, Any]]:
    """Add stable criterion and runtime provenance to validated model output."""

    output: list[dict[str, Any]] = []
    tool_events = [
        event
        for event in model_result.trace_events
        if event.get("event_type") == "retrieval_tool_call"
    ]
    successful_tool_calls = sum(
        int(event.get("result_count", 0) or 0) > 0 for event in tool_events
    )
    tool_cache_hits = sum(bool(event.get("cache_hit")) for event in tool_events)
    dependency_candidate = bool(
        image_dependency_hints(row)["image_dependency_candidate"]
    )
    for raw in model_result.results:
        spec = criteria[raw["criterion_id"]]
        record = _base_result(
            row=row,
            cluster_id=cluster_id,
            spec=spec,
            result=raw["result"],
            confidence=raw["confidence_score"],
            reason=raw["reason"],
            action=raw["suggested_reviewer_action"],
            checked_by=f"gemini:{model}",
            checked_at=checked_at,
            evidence_ids=raw["evidence_fragment_ids"],
            evidence_match_reason=raw["evidence_match_reason"],
            evidence_basis=str(raw.get("evidence_basis", "raw_row_only")),
            evidence_basis_fields=raw.get("evidence_basis_fields", ()),
            image_dependency_candidate=(
                dependency_candidate if cluster_id == "B" else False
            ),
            image_dependency=str(raw.get("image_dependency", "none")),
            image_dependency_reason=str(raw.get("image_dependency_reason", "")),
            needs_image_review=bool(raw.get("needs_image_review", False)),
        )
        record.update(
            {
                "prompt_sha256": model_result.prompt_sha256,
                "tool_version": TOOL_VERSION if cluster_id == "B" else None,
                "tool_call_count": model_result.tool_call_count,
                "successful_tool_call_count": successful_tool_calls,
                "tool_cache_hit_count": tool_cache_hits,
                "model": model,
                "model_version": model_result.model_version,
                "response_id": model_result.response_id,
                "finish_reason": model_result.finish_reason,
                "usage": model_result.usage,
            }
        )
        output.append(record)
    return output


def validate_complete_sample(records: Sequence[Mapping[str, Any]], sample_id: str) -> None:
    """Require exactly one result for each of the 18 criteria."""

    sample_records = [row for row in records if row.get("sample_id") == sample_id]
    ids = [str(row.get("criterion_id", "")) for row in sample_records]
    expected = [value for cluster in CLUSTER_CRITERIA.values() for value in cluster]
    if len(ids) != 18 or set(ids) != set(expected) or len(ids) != len(set(ids)):
        raise PilotContractError(
            f"Sample {sample_id} does not have exactly the 18 required criteria: {ids}"
        )


def sample_summary_record(records: Sequence[Mapping[str, Any]], row: RawDialogueRow) -> dict[str, Any]:
    """Create the strict mechanical sample-level aggregate."""

    validate_complete_sample(records, row.sample_id)
    checklist_rows = [
        {
            "sample_id": row.sample_id,
            "criterion_id": str(item["criterion_id"]),
            "result": str(item["result"]),
            "confidence_score": str(item["confidence_score"]),
            "reason": str(item["reason"]),
            "evidence_fragment_id": str(item.get("evidence_fragment_id", "")),
        }
        for item in records
        if item.get("sample_id") == row.sample_id
    ]
    aggregate = aggregate_sample(checklist_rows)
    sample_records = [
        item for item in records if item.get("sample_id") == row.sample_id
    ]
    image_dependent = [
        str(item.get("criterion_id", ""))
        for item in sample_records
        if str(item.get("image_dependency", "none")) != "none"
    ]
    image_candidates = [
        str(item.get("criterion_id", ""))
        for item in sample_records
        if bool(item.get("image_dependency_candidate"))
    ]
    dependency_rank = {"none": 0, "supporting": 1, "required": 2}
    maximum_dependency = max(
        (
            str(item.get("image_dependency", "none"))
            for item in sample_records
        ),
        key=lambda value: dependency_rank.get(value, -1),
        default="none",
    )
    return {
        "record_type": "sample_summary",
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "sample_id": row.sample_id,
        "grade": row.grade,
        "quality_decision": aggregate.decision,
        "confidence_score": aggregate.confidence_score,
        "blocking_criterion_ids": aggregate.blocking_criterion_ids,
        "blocking_reasons": aggregate.blocking_reasons,
        "evidence_fragment_ids": aggregate.evidence_fragment_ids,
        "image_dependency_candidate": bool(image_candidates),
        "image_dependency_candidate_criterion_ids": image_candidates,
        "image_dependent_criterion_ids": image_dependent,
        "maximum_image_dependency": maximum_dependency,
        "needs_image_review": any(
            bool(item.get("needs_image_review")) for item in sample_records
        ),
    }


def _loaded_reference(config: PilotConfig, cluster_id: str) -> str:
    if cluster_id not in REFERENCE_MARKERS:
        return ""
    path = config.bloom_reference_path if cluster_id == "C" else config.scaffolding_reference_path
    start, end = REFERENCE_MARKERS[cluster_id]
    return extract_reference_body(path.read_text(encoding="utf-8"), start_marker=start, end_marker=end)


def prepare_pilot(config: PilotConfig, *, overwrite_selection: bool = False) -> dict[str, Any]:
    """Lock deterministic sample selection and reproducibility hashes offline."""

    if config.regression_spec_path is not None:
        raise PilotContractError(
            "Regression selection is human-locked; prepare/overwrite is disabled"
        )
    if config.selection_path.exists() and not overwrite_selection:
        raise PilotContractError(
            f"Selection already exists: {config.selection_path}; use an explicit overwrite flag"
        )
    rows = load_normalized_rows(config.normalized_rows_path)
    criteria = load_criteria(config.criteria_path)
    if config.source_quotas:
        if config.base_selection_path is None:
            raise PilotContractError("Extension selection requires a base manifest")
        selection = extend_pilot_rows(
            rows,
            base_selection=load_selection(config.base_selection_path),
            source_quotas=config.source_quotas,
            seed=config.selection_seed,
            near_threshold=config.near_duplicate_threshold,
        )
    else:
        selection = select_pilot_rows(
            rows,
            seed=config.selection_seed,
            samples_per_grade=config.samples_per_grade,
            development_per_grade=config.development_per_grade,
        )
    validate_selection_contract(selection, rows=rows, config=config)
    write_selection(config.selection_path, selection)
    manifest = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "experiment_id": config.experiment_id,
        "prepared_at": utc_now(),
        "selection_path": config.selection_path.as_posix(),
        "selection_sha256": sha256_file(config.selection_path),
        "selection_count": len(selection),
        "split_counts": dict(Counter(row.split for row in selection)),
        "grade_counts": dict(Counter(row.grade for row in selection)),
        "source_split_counts": {
            f"{source_file}|{split}": count
            for (source_file, split), count in sorted(
                Counter((row.source_file, row.split) for row in selection).items()
            )
        },
        "selection_source_counts": dict(
            Counter(row.selection_source for row in selection)
        ),
        "input_hashes": {
            "config": config_fingerprint(config),
            "normalized_rows": sha256_file(config.normalized_rows_path),
            "criteria_registry": sha256_file(config.criteria_path),
            "bloom_reference": sha256_file(config.bloom_reference_path),
            "scaffolding_reference": sha256_file(config.scaffolding_reference_path),
            "base_prompt": sha256_file(config.base_prompt_path),
        },
        "criterion_count": len(criteria),
        "clusters": {key: list(value) for key, value in CLUSTER_CRITERIA.items()},
        "model_execution_authorized": False,
    }
    manifest["input_hashes"].update(prompt_bundle_input_hashes(config))
    if config.normalized_rows_manifest_path is not None:
        manifest["input_hashes"]["normalized_rows_manifest"] = sha256_file(
            config.normalized_rows_manifest_path
        )
    if config.base_selection_path is not None:
        manifest["input_hashes"]["base_selection"] = sha256_file(
            config.base_selection_path
        )
    manifest_path = config.selection_path.with_suffix(".manifest.json")
    atomic_write_json(manifest_path, manifest)
    return {**manifest, "manifest_path": manifest_path.as_posix()}


def validate_pilot_inputs(config: PilotConfig) -> dict[str, Any]:
    """Validate locked inputs and compute run contracts without model calls."""

    if not config.selection_path.is_file():
        raise PilotContractError(
            f"Locked selection does not exist: {config.selection_path}"
        )
    if not config.retrieval_index_path.is_file():
        raise PilotContractError(
            f"Retrieval index does not exist: {config.retrieval_index_path}"
        )
    rows = load_normalized_rows(config.normalized_rows_path)
    criteria = load_criteria(config.criteria_path)
    selection = load_selection(config.selection_path)
    validate_selection_contract(selection, rows=rows, config=config)
    by_id = {row.sample_id: row for row in rows}
    selected_ids = [item.sample_id for item in selection]
    missing = sorted(set(selected_ids) - set(by_id))
    if missing:
        raise PilotContractError(
            f"Selected sample IDs are missing from normalized data: {missing}"
        )
    regression_spec = (
        load_regression_spec(config.regression_spec_path)
        if config.regression_spec_path is not None
        else None
    )
    if regression_spec is not None:
        selection_ids = set(selected_ids)
        scope_ids = set(regression_spec.cluster_scope)
        if selection_ids != scope_ids:
            raise PilotContractError(
                "Regression selection must exactly match cluster_scope samples: "
                f"selection_only={sorted(selection_ids - scope_ids)}, "
                f"scope_only={sorted(scope_ids - selection_ids)}"
            )
        non_development = [
            item.sample_id for item in selection if item.split != "development"
        ]
        if non_development:
            raise PilotContractError(
                "Regression selection is development-only; invalid samples: "
                f"{non_development}"
            )
    split_contracts: dict[str, dict[str, Any]] = {}
    for split in ("development", "holdout"):
        split_selection = [item for item in selection if item.split == split]
        split_contracts[split] = {
            "sample_count": len(split_selection),
            "run_fingerprint": build_run_contract(
                config,
                split=split,
                selection=split_selection,
            )["run_fingerprint"],
        }
    selected_rows = [by_id[sample_id] for sample_id in selected_ids]
    output = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "normalized_row_count": len(rows),
        "selection_count": len(selection),
        "criterion_count": len(criteria),
        "dialogue_normalization_version_counts": dict(
            sorted(Counter(row.dialogue_normalization_version for row in rows).items())
        ),
        "selected_annotation_removed_count": sum(
            row.dialogue_annotation_count for row in selected_rows
        ),
        "selected_normalization_flag_count": sum(
            bool(row.dialogue_normalization_flags) for row in selected_rows
        ),
        "split_contracts": split_contracts,
        "model_execution_authorized": False,
    }
    if regression_spec is not None:
        output["regression"] = {
            "spec_path": regression_spec.path.as_posix(),
            "spec_sha256": regression_spec.spec_sha256,
            "sample_count": len(regression_spec.cluster_scope),
            "scoped_cluster_count": sum(
                len(values) for values in regression_spec.cluster_scope.values()
            ),
            "criterion_expectation_count": len(
                regression_spec.criterion_expectations
            ),
            "image_expectation_count": len(regression_spec.image_expectations),
            "image_criterion_expectation_count": sum(
                len(expectation.criterion_ids)
                for expectation in regression_spec.image_expectations
            ),
            "source_review_workbook": (
                regression_spec.source_review_workbook.as_posix()
            ),
            "source_review_workbook_sha256": (
                regression_spec.source_review_workbook_sha256
            ),
        }
    return output


def _already_completed_clusters(result_rows: Sequence[Mapping[str, Any]]) -> set[tuple[str, str]]:
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in result_rows:
        if row.get("record_type") != "criterion_result":
            continue
        grouped[(str(row.get("sample_id", "")), str(row.get("cluster_id", "")))].append(
            str(row.get("criterion_id", ""))
        )
    completed: set[tuple[str, str]] = set()
    for key, ids in grouped.items():
        cluster_id = key[1]
        if cluster_id not in CLUSTER_CRITERIA:
            raise PilotContractError(f"Resume output contains unknown cluster: {cluster_id}")
        expected = set(CLUSTER_CRITERIA[cluster_id])
        if len(ids) != len(expected) or set(ids) != expected:
            raise PilotContractError(
                f"Resume output contains a partial or duplicate cluster {key}: {ids}. "
                "Start a new run-id instead of repairing JSONL in place."
            )
        completed.add(key)
    return completed


def _required_recovery_spec(config: PilotConfig) -> ClusterRecoverySpec:
    """Return the configured recovery contract or fail before any provider call."""

    if config.recovery is None:
        raise PilotContractError("This command requires a recovery block in the config")
    return config.recovery


def _load_recovery_parent_state(config: PilotConfig) -> RecoveryParentState:
    """Validate the immutable incomplete parent bundle for one-cluster recovery."""

    spec = _required_recovery_spec(config)
    parent = spec.parent_output_dir
    result_path = parent / "clustered_audit_results.jsonl"
    trace_path = parent / "retrieval_and_model_trace.jsonl"
    summary_path = parent / "pilot_evaluation_summary.json"
    missing = [
        path.as_posix()
        for path in (result_path, trace_path, summary_path)
        if not path.is_file()
    ]
    if missing:
        raise PilotContractError(
            "Recovery parent bundle is missing required artifacts: " + ", ".join(missing)
        )
    parent_hashes = {
        "result": sha256_file(result_path),
        "trace": sha256_file(trace_path),
        "summary": sha256_file(summary_path),
    }
    expected_parent_hashes = {
        "result": spec.expected_parent_result_sha256,
        "trace": spec.expected_parent_trace_sha256,
        "summary": spec.expected_parent_summary_sha256,
    }
    if parent_hashes != expected_parent_hashes:
        raise PilotContractError(
            "Recovery parent artifact hash mismatch: "
            f"expected={expected_parent_hashes}, actual={parent_hashes}"
        )

    summary_raw = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(summary_raw, Mapping):
        raise PilotContractError("Recovery parent summary must be a JSON object")
    summary = dict(summary_raw)
    expected_summary_values = {
        "run_status": "incomplete",
        "split": spec.split,
        "sample_count": spec.expected_parent_sample_count,
        "completed_sample_count": spec.expected_parent_completed_sample_count,
        "criterion_result_count": spec.expected_parent_criterion_result_count,
        "sample_summary_count": spec.expected_parent_sample_summary_count,
        "run_fingerprint": spec.expected_parent_run_fingerprint,
    }
    for key, expected in expected_summary_values.items():
        if summary.get(key) != expected:
            raise PilotContractError(
                f"Recovery parent summary mismatch for {key}: "
                f"expected={expected!r}, actual={summary.get(key)!r}"
            )
    expected_pending = [
        {"sample_id": spec.target_sample_id, "cluster_id": spec.target_cluster_id}
    ]
    for key in ("pending_clusters", "non_retryable_pending_clusters"):
        actual = summary.get(key)
        if actual != expected_pending:
            raise PilotContractError(
                f"Recovery parent {key} must contain only the locked target: {actual!r}"
            )

    result_rows = read_jsonl(result_path)
    unknown_record_types = sorted(
        {
            str(row.get("record_type", ""))
            for row in result_rows
            if row.get("record_type") not in {"criterion_result", "sample_summary"}
        }
    )
    if unknown_record_types:
        raise PilotContractError(
            f"Recovery parent contains unknown result record types: {unknown_record_types}"
        )
    criterion_rows = [
        row for row in result_rows if row.get("record_type") == "criterion_result"
    ]
    summary_rows = [
        row for row in result_rows if row.get("record_type") == "sample_summary"
    ]
    if len(criterion_rows) != spec.expected_parent_criterion_result_count:
        raise PilotContractError("Recovery parent criterion_result_count is not exact")
    if len(summary_rows) != spec.expected_parent_sample_summary_count:
        raise PilotContractError("Recovery parent sample_summary_count is not exact")
    criterion_keys = [
        (str(row.get("sample_id", "")), str(row.get("criterion_id", "")))
        for row in criterion_rows
    ]
    if len(criterion_keys) != len(set(criterion_keys)):
        raise PilotContractError("Recovery parent contains duplicate criterion IDs")
    summary_ids = [str(row.get("sample_id", "")) for row in summary_rows]
    if len(summary_ids) != len(set(summary_ids)):
        raise PilotContractError("Recovery parent contains duplicate sample summaries")

    completed_clusters = _already_completed_clusters(result_rows)
    if len(completed_clusters) != spec.expected_parent_completed_cluster_count:
        raise PilotContractError(
            "Recovery parent completed cluster count mismatch: "
            f"expected={spec.expected_parent_completed_cluster_count}, "
            f"actual={len(completed_clusters)}"
        )
    target_key = (spec.target_sample_id, spec.target_cluster_id)
    if target_key in completed_clusters:
        raise PilotContractError("Recovery target cluster is already complete in parent")

    all_rows = load_normalized_rows(config.normalized_rows_path)
    selection = load_selection(config.selection_path)
    validate_selection_contract(selection, rows=all_rows, config=config)
    split_selection = [row for row in selection if row.split == spec.split]
    if len(split_selection) != spec.expected_parent_sample_count:
        raise PilotContractError(
            "Recovery selection count does not match the locked parent sample count"
        )
    selected_ids = {row.sample_id for row in split_selection}
    if {key[0] for key in completed_clusters} - selected_ids:
        raise PilotContractError("Recovery parent contains clusters outside the locked split")
    if set(summary_ids) - selected_ids:
        raise PilotContractError("Recovery parent contains summaries outside the locked split")
    target_selection = next(
        (row for row in split_selection if row.sample_id == spec.target_sample_id),
        None,
    )
    if target_selection is None:
        raise PilotContractError("Recovery target sample is absent from locked selection")
    by_id = {row.sample_id: row for row in all_rows}
    if spec.target_sample_id not in by_id:
        raise PilotContractError("Recovery target sample is absent from normalized rows")
    target_row = by_id[spec.target_sample_id]

    required_target_clusters = set(CLUSTER_CRITERIA) - {spec.target_cluster_id}
    actual_target_clusters = {
        cluster_id
        for sample_id, cluster_id in completed_clusters
        if sample_id == spec.target_sample_id
    }
    if actual_target_clusters != required_target_clusters:
        raise PilotContractError(
            "Recovery target must have exactly the five non-target clusters complete: "
            f"{sorted(actual_target_clusters)}"
        )
    complete_sample_ids = {
        sample_id
        for sample_id in selected_ids
        if _sample_clusters_complete(completed_clusters, sample_id)
    }
    if len(complete_sample_ids) != spec.expected_parent_completed_sample_count:
        raise PilotContractError("Recovery parent completed sample count is not exact")
    if complete_sample_ids != set(summary_ids):
        raise PilotContractError(
            "Recovery parent summaries do not exactly match complete samples"
        )
    for sample_id in complete_sample_ids:
        validate_complete_sample(criterion_rows, sample_id)

    trace_rows = read_jsonl(trace_path)
    manifests = [row for row in trace_rows if row.get("event_type") == "run_manifest"]
    if len(manifests) != 1:
        raise PilotContractError(
            "Recovery parent trace must contain exactly one run_manifest"
        )
    if manifests[0].get("run_fingerprint") != spec.expected_parent_run_fingerprint:
        raise PilotContractError("Recovery parent trace fingerprint does not match config")
    incomplete_events = [
        row for row in trace_rows if row.get("event_type") == "run_incomplete"
    ]
    if not incomplete_events or incomplete_events[-1].get("pending_clusters") != expected_pending:
        raise PilotContractError(
            "Recovery parent trace does not end with the locked pending cluster"
        )

    return RecoveryParentState(
        spec=spec,
        summary=summary,
        result_rows=tuple(dict(row) for row in result_rows),
        trace_rows=tuple(dict(row) for row in trace_rows),
        completed_clusters=frozenset(completed_clusters),
        target_row=target_row,
        target_selection=target_selection,
        parent_result_sha256=parent_hashes["result"],
        parent_trace_sha256=parent_hashes["trace"],
        parent_summary_sha256=parent_hashes["summary"],
        inherited_records_sha256=canonical_records_sha256(result_rows),
    )


def _build_cluster_recovery_contract(
    config: PilotConfig,
    state: RecoveryParentState,
    *,
    prompt_sha256: str,
) -> dict[str, Any]:
    """Build a fingerprinted child contract without bypassing parent checks."""

    base_contract = build_run_contract(
        config,
        split=state.spec.split,
        selection=[state.target_selection],
    )
    contract = {
        "schema_version": RECOVERY_SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "experiment_id": config.experiment_id,
        "split": state.spec.split,
        "target_sample_id": state.spec.target_sample_id,
        "target_cluster_id": state.spec.target_cluster_id,
        "prompt_sha256": prompt_sha256,
        "parent": {
            "output_dir": state.spec.parent_output_dir.as_posix(),
            "run_fingerprint": state.spec.expected_parent_run_fingerprint,
            "result_sha256": state.parent_result_sha256,
            "trace_sha256": state.parent_trace_sha256,
            "summary_sha256": state.parent_summary_sha256,
            "inherited_records_sha256": state.inherited_records_sha256,
        },
        "input_hashes": base_contract["input_hashes"],
        "runtime": base_contract["runtime"],
    }
    return {
        **contract,
        "recovery_fingerprint": sha256_text(
            json.dumps(contract, ensure_ascii=False, sort_keys=True)
        ),
    }


def validate_cluster_recovery_inputs(config: PilotConfig) -> dict[str, Any]:
    """Preflight one-cluster recovery without calling a provider or writing output."""

    pilot_validation = validate_pilot_inputs(config)
    state = _load_recovery_parent_state(config)
    criteria = load_criteria(config.criteria_path)
    prompt_bundle = load_audit_prompt_bundle(config.prompt_bundle_manifest_path)
    system_instruction, user_prompt, prompt_sha256 = build_cluster_prompt(
        cluster_id=state.spec.target_cluster_id,
        row=state.target_row,
        criteria=criteria,
        base_prompt=config.base_prompt_path.read_text(encoding="utf-8"),
        bloom_reference=_loaded_reference(config, "C"),
        scaffolding_reference=_loaded_reference(config, "D"),
        include_tool_response_contract=config.include_tool_response_contract_in_prompt,
        max_successful_tool_calls=config.max_successful_tool_calls_per_cluster,
        max_total_tool_calls=config.max_total_tool_calls_per_cluster,
        max_output_tokens=config.max_output_tokens,
        prompt_bundle=prompt_bundle,
    )
    del system_instruction, user_prompt
    contract = _build_cluster_recovery_contract(
        config,
        state,
        prompt_sha256=prompt_sha256,
    )
    return {
        "schema_version": RECOVERY_SCHEMA_VERSION,
        "parent_run_status": state.summary["run_status"],
        "parent_run_fingerprint": state.spec.expected_parent_run_fingerprint,
        "parent_completed_cluster_count": len(state.completed_clusters),
        "target_sample_id": state.spec.target_sample_id,
        "target_cluster_id": state.spec.target_cluster_id,
        "prompt_sha256": prompt_sha256,
        "recovery_fingerprint": contract["recovery_fingerprint"],
        "expected_final_counts": {
            "criterion_result_count": state.spec.expected_final_criterion_result_count,
            "sample_summary_count": state.spec.expected_final_sample_summary_count,
            "completed_cluster_count": state.spec.expected_final_completed_cluster_count,
        },
        "pilot_input_validation": pilot_validation,
        "model_execution_authorized": False,
    }


def run_cluster_recovery(
    *,
    config: PilotConfig,
    output_dir: Path,
    client: Any,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Recover one locked cluster and build a verified child bundle."""

    validate_pilot_inputs(config)
    state = _load_recovery_parent_state(config)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise PilotContractError(f"Recovery output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "clustered_audit_results.jsonl"
    trace_path = output_dir / "retrieval_and_model_trace.jsonl"
    summary_path = output_dir / "pilot_evaluation_summary.json"
    criteria = load_criteria(config.criteria_path)
    prompt_bundle = load_audit_prompt_bundle(config.prompt_bundle_manifest_path)
    system_instruction, user_prompt, prompt_sha256 = build_cluster_prompt(
        cluster_id=state.spec.target_cluster_id,
        row=state.target_row,
        criteria=criteria,
        base_prompt=config.base_prompt_path.read_text(encoding="utf-8"),
        bloom_reference=_loaded_reference(config, "C"),
        scaffolding_reference=_loaded_reference(config, "D"),
        include_tool_response_contract=config.include_tool_response_contract_in_prompt,
        max_successful_tool_calls=config.max_successful_tool_calls_per_cluster,
        max_total_tool_calls=config.max_total_tool_calls_per_cluster,
        max_output_tokens=config.max_output_tokens,
        prompt_bundle=prompt_bundle,
    )
    recovery_contract = _build_cluster_recovery_contract(
        config,
        state,
        prompt_sha256=prompt_sha256,
    )
    started_at = utc_now()
    append_jsonl(
        trace_path,
        {
            "event_type": "recovery_manifest",
            "recorded_at": started_at,
            **recovery_contract,
        },
    )

    def persist_trace(attempt_number: int, event: dict[str, Any]) -> None:
        append_jsonl(
            trace_path,
            {
                "schema_version": RECOVERY_SCHEMA_VERSION,
                "plan_id": PLAN_ID,
                "sample_id": state.spec.target_sample_id,
                "grade": state.target_row.grade,
                "cluster_id": state.spec.target_cluster_id,
                "recorded_at": utc_now(),
                "attempt_number": attempt_number,
                **event,
            },
        )

    model_result: ModelClusterResult | None = None
    max_attempts = config.max_retries_per_cluster + 1
    final_error: Exception | None = None
    attempted_count = 0
    for attempt_number in range(1, max_attempts + 1):
        attempted_count = attempt_number
        if attempt_number > 1:
            delay = config.retry_backoff_seconds * (2 ** (attempt_number - 2))
            logger.info(
                "Waiting before recovery retry attempt={} delay_seconds={}",
                attempt_number,
                delay,
            )
            sleep_fn(delay)
        persist_trace(
            attempt_number,
            {
                "event_type": "recovery_attempt_started",
                "max_attempts": max_attempts,
                "prompt_sha256": prompt_sha256,
            },
        )
        adapter = AuditRetrievalAdapter(
            row=state.target_row,
            index_path=config.retrieval_index_path,
        )
        try:
            model_result = run_gemini_cluster(
                client=client,
                model=config.model,
                thinking_level=config.thinking_level,
                max_output_tokens=config.max_output_tokens,
                seed=config.seed,
                system_instruction=system_instruction,
                user_prompt=user_prompt,
                prompt_sha256=prompt_sha256,
                cluster_id=state.spec.target_cluster_id,
                expected_ids=CLUSTER_CRITERIA[state.spec.target_cluster_id],
                retrieval_adapter=adapter,
                max_successful_tool_calls=config.max_successful_tool_calls_per_cluster,
                max_total_tool_calls=config.max_total_tool_calls_per_cluster,
                max_output_repair_attempts=config.max_output_repair_attempts,
                trace_sink=lambda event, attempt=attempt_number: persist_trace(
                    attempt, event
                ),
            )
        except Exception as exc:
            final_error = exc
            retryable = _is_retryable_cluster_error(exc)
            retry_scheduled = retryable and attempt_number < max_attempts
            persist_trace(
                attempt_number,
                {
                    "event_type": "recovery_attempt_error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "failure_category": (
                        "output_truncated"
                        if isinstance(exc, PilotOutputTruncatedError)
                        else "output_contract_failed"
                        if isinstance(exc, PilotOutputContractError)
                        else "cluster_attempt_failed"
                    ),
                    "retryable": retryable,
                    "retry_scheduled": retry_scheduled,
                },
            )
            if not retry_scheduled:
                break
            continue
        persist_trace(
            attempt_number,
            {
                "event_type": "recovery_attempt_completed",
                "prompt_sha256": prompt_sha256,
                "tool_call_count": model_result.tool_call_count,
                "response_id": model_result.response_id,
            },
        )
        break

    if model_result is None:
        failure_summary = {
            "schema_version": RECOVERY_SCHEMA_VERSION,
            "experiment_id": config.experiment_id,
            "plan_id": PLAN_ID,
            "run_status": "incomplete",
            "completed_at": utc_now(),
            "attempted_count": attempted_count,
            "pending_clusters": [
                {
                    "sample_id": state.spec.target_sample_id,
                    "cluster_id": state.spec.target_cluster_id,
                }
            ],
            "failure": {
                "error_type": type(final_error).__name__ if final_error else "unknown",
                "error": str(final_error or "unknown recovery failure"),
                "retryable": _is_retryable_cluster_error(final_error),
            },
            "recovery_fingerprint": recovery_contract["recovery_fingerprint"],
            "parent": recovery_contract["parent"],
        }
        atomic_write_json(summary_path, failure_summary)
        raise PilotExecutionError(
            "Cluster recovery remains incomplete; inspect "
            f"{summary_path} and do not rerun automatically"
        ) from final_error

    recovered_records = enrich_model_results(
        row=state.target_row,
        cluster_id=state.spec.target_cluster_id,
        criteria=criteria,
        model_result=model_result,
        checked_at=utc_now(),
        model=config.model,
    )
    inherited_records = [dict(row) for row in state.result_rows]
    merged_records = [*inherited_records, *recovered_records]
    merged_criterion_rows = [
        row for row in merged_records if row.get("record_type") == "criterion_result"
    ]
    merged_records.append(
        sample_summary_record(merged_criterion_rows, state.target_row)
    )
    final_criterion_rows = [
        row for row in merged_records if row.get("record_type") == "criterion_result"
    ]
    final_summary_rows = [
        row for row in merged_records if row.get("record_type") == "sample_summary"
    ]
    final_completed = _already_completed_clusters(merged_records)
    actual_final_counts = {
        "criterion_result_count": len(final_criterion_rows),
        "sample_summary_count": len(final_summary_rows),
        "completed_cluster_count": len(final_completed),
    }
    expected_final_counts = {
        "criterion_result_count": state.spec.expected_final_criterion_result_count,
        "sample_summary_count": state.spec.expected_final_sample_summary_count,
        "completed_cluster_count": state.spec.expected_final_completed_cluster_count,
    }
    if actual_final_counts != expected_final_counts:
        raise PilotContractError(
            "Recovery merge cardinality mismatch: "
            f"expected={expected_final_counts}, actual={actual_final_counts}"
        )
    criterion_keys = [
        (str(row.get("sample_id", "")), str(row.get("criterion_id", "")))
        for row in final_criterion_rows
    ]
    summary_ids = [str(row.get("sample_id", "")) for row in final_summary_rows]
    if len(criterion_keys) != len(set(criterion_keys)):
        raise PilotContractError("Recovery merge produced duplicate criterion IDs")
    if len(summary_ids) != len(set(summary_ids)):
        raise PilotContractError("Recovery merge produced duplicate sample summaries")
    for sample_id in summary_ids:
        validate_complete_sample(final_criterion_rows, sample_id)
    if canonical_records_sha256(merged_records[: len(inherited_records)]) != (
        state.inherited_records_sha256
    ):
        raise PilotContractError("Recovery merge changed inherited parent records")

    atomic_write_jsonl(result_path, merged_records)
    written_records = read_jsonl(result_path)
    if canonical_records_sha256(written_records[: len(inherited_records)]) != (
        state.inherited_records_sha256
    ):
        raise PilotContractError("Written recovery bundle changed inherited records")
    persist_trace(
        attempted_count,
        {
            "event_type": "recovery_completed",
            "actual_final_counts": actual_final_counts,
            "inherited_record_count": len(inherited_records),
            "inherited_records_sha256": state.inherited_records_sha256,
            "final_records_sha256": canonical_records_sha256(written_records),
        },
    )
    recovery_traces = read_jsonl(trace_path)
    summary = {
        "schema_version": RECOVERY_SCHEMA_VERSION,
        "experiment_id": config.experiment_id,
        "plan_id": PLAN_ID,
        "split": state.spec.split,
        "run_status": "completed",
        "completed_at": utc_now(),
        "attempted_count": attempted_count,
        "sample_count": state.spec.expected_parent_sample_count,
        "completed_sample_count": len(summary_ids),
        "incomplete_sample_count": 0,
        "pending_clusters": [],
        **actual_final_counts,
        "decision_counts": dict(
            Counter(str(row.get("quality_decision")) for row in final_summary_rows)
        ),
        "criterion_result_counts": dict(
            Counter(str(row.get("result")) for row in final_criterion_rows)
        ),
        "current_execution_metrics": summarize_trace_metrics(
            recovery_traces,
            tool_required_sample_count=1,
        ),
        "target": {
            "sample_id": state.spec.target_sample_id,
            "cluster_id": state.spec.target_cluster_id,
        },
        "recovery_fingerprint": recovery_contract["recovery_fingerprint"],
        "parent": recovery_contract["parent"],
        "merge_validation": {
            "inherited_record_count": len(inherited_records),
            "inherited_records_sha256": state.inherited_records_sha256,
            "inherited_records_unchanged": True,
            "final_records_sha256": canonical_records_sha256(written_records),
            "duplicate_criterion_id_count": 0,
            "duplicate_sample_summary_count": 0,
        },
        "artifacts": {
            "clustered_audit_results": result_path.as_posix(),
            "retrieval_and_model_trace": trace_path.as_posix(),
            "pilot_evaluation_summary": summary_path.as_posix(),
        },
        "claims": {
            "human_reference_available": False,
            "accuracy_reported": False,
            "results_are_preliminary": True,
        },
    }
    atomic_write_json(summary_path, summary)
    logger.info(
        "Cluster recovery completed sample_id={} cluster={} summary={}",
        state.spec.target_sample_id,
        state.spec.target_cluster_id,
        summary_path,
    )
    return summary


def _sanitize_resume_result_rows(
    result_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Rollback partial known clusters and summaries that are not fully supported."""

    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in result_rows:
        record_type = row.get("record_type")
        if record_type == "sample_summary":
            continue
        if record_type != "criterion_result":
            raise PilotContractError(f"Resume output contains unknown record_type: {record_type}")
        sample_id = str(row.get("sample_id", ""))
        cluster_id = str(row.get("cluster_id", ""))
        criterion_id = str(row.get("criterion_id", ""))
        if not sample_id or cluster_id not in CLUSTER_CRITERIA:
            raise PilotContractError(
                f"Resume output contains an invalid sample/cluster key: {(sample_id, cluster_id)}"
            )
        if criterion_id not in CLUSTER_CRITERIA[cluster_id]:
            raise PilotContractError(
                f"Resume output contains unknown criterion {criterion_id} in cluster {cluster_id}"
            )
        grouped[(sample_id, cluster_id)].append(row)

    complete_keys: set[tuple[str, str]] = set()
    partial_keys: set[tuple[str, str]] = set()
    for key, records in grouped.items():
        ids = [str(row.get("criterion_id", "")) for row in records]
        expected = set(CLUSTER_CRITERIA[key[1]])
        if len(ids) == len(expected) and set(ids) == expected:
            complete_keys.add(key)
        else:
            partial_keys.add(key)

    required_clusters = set(CLUSTER_CRITERIA)
    complete_sample_ids = {
        sample_id
        for sample_id in {key[0] for key in complete_keys}
        if {
            cluster_id
            for candidate_id, cluster_id in complete_keys
            if candidate_id == sample_id
        }
        == required_clusters
    }
    sanitized: list[dict[str, Any]] = []
    kept_summary_ids: set[str] = set()
    dropped_summary_ids: set[str] = set()
    for raw in result_rows:
        row = dict(raw)
        if row.get("record_type") == "criterion_result":
            key = (str(row.get("sample_id", "")), str(row.get("cluster_id", "")))
            if key in complete_keys:
                sanitized.append(row)
            continue
        sample_id = str(row.get("sample_id", ""))
        if sample_id in complete_sample_ids and sample_id not in kept_summary_ids:
            sanitized.append(row)
            kept_summary_ids.add(sample_id)
        else:
            dropped_summary_ids.add(sample_id)

    recovery = {
        "partial_clusters_rolled_back": [
            {"sample_id": sample_id, "cluster_id": cluster_id}
            for sample_id, cluster_id in sorted(partial_keys)
        ],
        "sample_summaries_rolled_back": sorted(
            sample_id for sample_id in dropped_summary_ids if sample_id
        ),
    }
    return sanitized, recovery


def _sample_clusters_complete(
    completed: set[tuple[str, str]],
    sample_id: str,
) -> bool:
    """Return whether all six criterion clusters are committed for one sample."""

    return all((sample_id, cluster_id) in completed for cluster_id in CLUSTER_CRITERIA)


def summarize_trace_metrics(
    traces: Sequence[Mapping[str, Any]],
    *,
    tool_required_sample_count: int,
) -> dict[str, Any]:
    """Summarize observable model and retrieval behavior without human labels."""

    model_rounds = [row for row in traces if row.get("event_type") == "model_round"]
    tool_calls = [row for row in traces if row.get("event_type") == "retrieval_tool_call"]
    attempt_errors = [
        row for row in traces if row.get("event_type") == "cluster_attempt_error"
    ]
    recovered_retries = [
        row for row in traces if row.get("event_type") == "cluster_retry_recovered"
    ]
    cluster_errors = [row for row in traces if row.get("event_type") == "cluster_error"]
    output_repair_requests = [
        row for row in traces if row.get("event_type") == "output_repair_requested"
    ]
    output_repair_responses = [
        row for row in traces if row.get("event_type") == "output_repair_response"
    ]
    output_repair_successes = [
        row for row in traces if row.get("event_type") == "output_repair_succeeded"
    ]
    output_repair_failures = [
        row for row in traces if row.get("event_type") == "output_repair_failed"
    ]
    calls_per_sample = Counter(str(row.get("sample_id", "")) for row in tool_calls)
    query_counts = Counter(
        (
            str(row.get("sample_id", "")),
            str(row.get("query_signature", ""))
            or json.dumps(
                row.get("arguments_from_model", {}),
                ensure_ascii=False,
                sort_keys=True,
            ),
        )
        for row in tool_calls
    )
    model_latency = [float(row.get("latency_ms", 0) or 0) for row in model_rounds]
    retrieval_latency = [float(row.get("latency_ms", 0) or 0) for row in tool_calls]
    retrieval_status_counts = Counter(
        str(
            (
                row.get("model_visible_response", {})
                if isinstance(row.get("model_visible_response"), Mapping)
                else {}
            ).get("status")
            or row.get("reason")
            or "unknown"
        )
        for row in tool_calls
    )
    ranked_results = [
        ranked
        for row in tool_calls
        for ranked in (
            row.get("ranked_results", [])
            if isinstance(row.get("ranked_results"), list)
            else []
        )
        if isinstance(ranked, Mapping)
    ]
    unique_returned_fragment_ids = {
        str(row.get("fragment_id", ""))
        for row in ranked_results
        if row.get("fragment_id")
    }
    multi_source_results = [
        row
        for row in ranked_results
        if int(row.get("source_fragment_count", 1) or 1) > 1
    ]
    table_containing_results = [
        row for row in ranked_results if bool(row.get("contains_table_source"))
    ]
    cluster_b_tool_calls = [row for row in tool_calls if row.get("cluster_id") == "B"]
    cluster_b_samples_with_fragments = {
        str(row.get("sample_id", ""))
        for row in cluster_b_tool_calls
        if row.get("sample_id") and int(row.get("result_count", 0) or 0) > 0
    }
    cluster_b_samples_without_fragments = max(
        tool_required_sample_count - len(cluster_b_samples_with_fragments),
        0,
    )
    usage = Counter()
    for row in [*model_rounds, *output_repair_responses]:
        raw_usage = row.get("usage", {})
        if isinstance(raw_usage, Mapping):
            for key in TOKEN_USAGE_KEYS:
                usage[key] += int(raw_usage.get(key, 0) or 0)
    tool_used_sample_count = len(calls_per_sample)
    return {
        "model_round_count": len(model_rounds),
        "model_latency_ms_total": round(sum(model_latency), 3),
        "model_latency_ms_average": (
            round(sum(model_latency) / len(model_latency), 3) if model_latency else 0.0
        ),
        "input_tokens": usage["input_tokens"],
        "candidate_tokens": usage["candidate_tokens"],
        "thoughts_tokens": usage["thoughts_tokens"],
        "tool_use_prompt_tokens": usage["tool_use_prompt_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
        "tool_required_sample_count": tool_required_sample_count,
        "tool_used_sample_count": tool_used_sample_count,
        "tool_use_rate": (
            round(tool_used_sample_count / tool_required_sample_count, 6)
            if tool_required_sample_count
            else 0.0
        ),
        "tool_call_count": len(tool_calls),
        "successful_tool_call_count": sum(
            int(row.get("result_count", 0) or 0) > 0 for row in tool_calls
        ),
        "empty_tool_call_count": sum(
            int(row.get("result_count", 0) or 0) == 0 for row in tool_calls
        ),
        "retrieval_status_counts": dict(sorted(retrieval_status_counts.items())),
        "query_with_results_rate": (
            round(
                sum(int(row.get("result_count", 0) or 0) > 0 for row in tool_calls)
                / len(tool_calls),
                6,
            )
            if tool_calls
            else 0.0
        ),
        "returned_fragment_count_total": len(ranked_results),
        "returned_fragment_count_unique": len(unique_returned_fragment_ids),
        "multi_source_fragment_return_count": len(multi_source_results),
        "multi_source_fragment_return_unique_count": len(
            {
                str(row.get("fragment_id", ""))
                for row in multi_source_results
                if row.get("fragment_id")
            }
        ),
        "table_containing_fragment_return_count": len(table_containing_results),
        "table_containing_fragment_return_unique_count": len(
            {
                str(row.get("fragment_id", ""))
                for row in table_containing_results
                if row.get("fragment_id")
            }
        ),
        "cluster_b_with_fragment_sample_count": len(
            cluster_b_samples_with_fragments
        ),
        "cluster_b_without_fragment_sample_count": (
            cluster_b_samples_without_fragments
        ),
        "cluster_b_without_fragment_sample_rate": (
            round(cluster_b_samples_without_fragments / tool_required_sample_count, 6)
            if tool_required_sample_count
            else 0.0
        ),
        "tool_cache_hit_count": sum(bool(row.get("cache_hit")) for row in tool_calls),
        "tool_calls_per_used_sample_average": (
            round(len(tool_calls) / tool_used_sample_count, 6)
            if tool_used_sample_count
            else 0.0
        ),
        "tool_calls_per_sample_max": max(calls_per_sample.values(), default=0),
        "repeated_identical_query_count": sum(
            count - 1 for count in query_counts.values() if count > 1
        ),
        "tool_no_result_count": sum(int(row.get("result_count", 0)) == 0 for row in tool_calls),
        "retrieval_latency_ms_total": round(sum(retrieval_latency), 3),
        "retrieval_latency_ms_average": (
            round(sum(retrieval_latency) / len(retrieval_latency), 3)
            if retrieval_latency
            else 0.0
        ),
        "cluster_attempt_error_count": len(attempt_errors),
        "cluster_attempt_error_type_counts": dict(
            Counter(str(row.get("error_type", "unknown")) for row in attempt_errors)
        ),
        "cluster_retry_recovered_count": len(recovered_retries),
        "cluster_error_count": len(cluster_errors),
        "cluster_error_type_counts": dict(
            Counter(str(row.get("error_type", "unknown")) for row in cluster_errors)
        ),
        "output_repair_request_count": len(output_repair_requests),
        "output_repair_success_count": len(output_repair_successes),
        "output_repair_failure_count": len(output_repair_failures),
        "sbt_solution_query_reminder_count": sum(
            row.get("event_type") == "sbt_solution_query_reminder" for row in traces
        ),
        "sbt_solution_budget_reserved_count": sum(
            row.get("event_type") == "sbt_solution_budget_reserved" for row in traces
        ),
        "tool_limit_error_count": sum(
            "max_total_tool_calls_per_cluster" in str(row.get("error", ""))
            or "max_successful_tool_calls_per_cluster" in str(row.get("error", ""))
            for row in cluster_errors
        ),
    }


def run_pilot_split(
    *,
    config: PilotConfig,
    split: str,
    output_dir: Path,
    client: Any,
    resume: bool = False,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Run one development or holdout split after the caller opens the paid gate."""

    # Validate the split and load all immutable inputs needed by every cluster.
    logger.info(
        "Starting Plan 03 run split={} output_dir={} resume={}",
        split,
        output_dir,
        resume,
    )
    if split not in {"development", "holdout"}:
        raise PilotContractError("split must be development or holdout")
    if not config.retrieval_index_path.is_file():
        raise PilotContractError(f"Retrieval index does not exist: {config.retrieval_index_path}")
    full_selection = load_selection(config.selection_path)
    all_rows = load_normalized_rows(config.normalized_rows_path)
    validate_selection_contract(full_selection, rows=all_rows, config=config)
    selection = [row for row in full_selection if row.split == split]
    by_id = {row.sample_id: row for row in all_rows}
    missing = [row.sample_id for row in selection if row.sample_id not in by_id]
    if missing:
        raise PilotContractError(f"Selected sample IDs are missing from normalized data: {missing}")
    rows = [by_id[item.sample_id] for item in selection]
    criteria = load_criteria(config.criteria_path)
    base_prompt = config.base_prompt_path.read_text(encoding="utf-8")
    prompt_bundle = load_audit_prompt_bundle(config.prompt_bundle_manifest_path)
    regression_spec = (
        load_regression_spec(config.regression_spec_path)
        if config.regression_spec_path is not None
        else None
    )
    required_clusters_by_sample: dict[str, tuple[str, ...]] = {
        row.sample_id: (
            regression_spec.cluster_scope[row.sample_id]
            if regression_spec is not None
            else tuple(CLUSTER_CRITERIA)
        )
        for row in rows
    }
    bloom_reference = _loaded_reference(config, "C")
    scaffolding_reference = _loaded_reference(config, "D")
    logger.info(
        "Loaded Plan 03 inputs split_samples={} normalized_rows={} criteria={}",
        len(rows),
        len(all_rows),
        len(criteria),
    )

    # Initialize outputs. Resume first validates the immutable run contract, then
    # atomically removes only a truncated tail or a partial known cluster.
    result_path = output_dir / "clustered_audit_results.jsonl"
    trace_path = output_dir / "retrieval_and_model_trace.jsonl"
    summary_path = output_dir / "pilot_evaluation_summary.json"
    if output_dir.exists() and not resume and any(output_dir.iterdir()):
        raise PilotContractError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    checked_at = utc_now()

    # Lock the run contract so resume cannot cross input, code, or config changes.
    run_contract = build_run_contract(config, split=split, selection=selection)
    existing: list[dict[str, Any]] = []
    existing_traces: list[dict[str, Any]] = []
    recovery = {
        "result_tail_truncated": False,
        "trace_tail_truncated": False,
        "partial_clusters_rolled_back": [],
        "sample_summaries_rolled_back": [],
    }
    if resume:
        existing_traces, trace_tail_truncated = read_jsonl_recoverable_tail(trace_path)
        run_manifests = [
            event for event in existing_traces if event.get("event_type") == "run_manifest"
        ]
        if len(run_manifests) != 1:
            raise PilotContractError(
                "A resumable output must contain exactly one run_manifest trace event"
            )
        if run_manifests[0].get("run_fingerprint") != run_contract["run_fingerprint"]:
            raise PilotContractError(
                "Resume contract differs from the existing run; use a new run-id"
            )
        raw_existing, result_tail_truncated = read_jsonl_recoverable_tail(result_path)
        existing, result_recovery = _sanitize_resume_result_rows(raw_existing)
        recovery = {
            "result_tail_truncated": result_tail_truncated,
            "trace_tail_truncated": trace_tail_truncated,
            **result_recovery,
        }
        if trace_tail_truncated:
            atomic_write_jsonl(trace_path, existing_traces)
        if result_tail_truncated or existing != raw_existing:
            atomic_write_jsonl(result_path, existing)
    else:
        append_jsonl(
            trace_path,
            {
                "event_type": "run_manifest",
                "recorded_at": checked_at,
                **run_contract,
            },
        )
        existing_traces = read_jsonl(trace_path)

    completed = _already_completed_clusters(existing)
    previous_sequences = [
        int(event.get("execution_sequence", 0))
        for event in existing_traces
        if event.get("event_type") == "execution_started"
    ]
    terminal_sequences = {
        int(event.get("execution_sequence", 0))
        for event in existing_traces
        if event.get("event_type") in {"run_completed", "run_incomplete"}
    }
    previous_sequence = max(previous_sequences, default=0)
    execution_sequence = previous_sequence + 1
    execution_id = f"{split}-execution-{execution_sequence:03d}"
    append_jsonl(
        trace_path,
        {
            "event_type": "execution_started",
            "recorded_at": checked_at,
            "execution_id": execution_id,
            "execution_sequence": execution_sequence,
            "resume": resume,
            "previous_execution_interrupted": (
                previous_sequence > 0 and previous_sequence not in terminal_sequences
            ),
        },
    )
    if resume and any(
        (
            recovery["result_tail_truncated"],
            recovery["trace_tail_truncated"],
            recovery["partial_clusters_rolled_back"],
            recovery["sample_summaries_rolled_back"],
        )
    ):
        append_jsonl(
            trace_path,
            {
                "event_type": "resume_recovery",
                "recorded_at": utc_now(),
                "execution_id": execution_id,
                "execution_sequence": execution_sequence,
                **recovery,
            },
        )

    # Preserve both the immutable raw dialogue and the exact readable projection
    # used in model prompts. This is provenance, not a source-data rewrite.
    for row in rows:
        append_jsonl(
            trace_path,
            {
                "schema_version": OUTPUT_SCHEMA_VERSION,
                "plan_id": PLAN_ID,
                "recorded_at": utc_now(),
                "execution_id": execution_id,
                "execution_sequence": execution_sequence,
                **dialogue_projection_trace(row),
            },
        )

    # Screen duplicate risk against the full normalized dataset, then retain the
    # records belonging to samples selected for this split.
    duplicate_started = time.perf_counter()

    def log_duplicate_progress(completed_pairs: int, total_pairs: int) -> None:
        percentage = (100.0 * completed_pairs / total_pairs) if total_pairs else 100.0
        logger.info(
            "Duplicate screening progress pairs={}/{} percent={:.1f}",
            completed_pairs,
            total_pairs,
            percentage,
        )

    duplicate_required = any(
        "F" in cluster_ids for cluster_ids in required_clusters_by_sample.values()
    )
    duplicate_pairs = (
        duplicate_rows(
            all_rows,
            near_threshold=config.near_duplicate_threshold,
            progress_callback=log_duplicate_progress,
        )
        if duplicate_required
        else []
    )
    logger.info(
        "Duplicate screening completed flagged_pairs={} latency_seconds={:.3f}",
        len(duplicate_pairs),
        time.perf_counter() - duplicate_started,
    )
    duplicate_records = evaluate_duplicate_cluster(
        all_rows,
        criteria=criteria,
        near_threshold=config.near_duplicate_threshold,
        checked_at=checked_at,
        candidate_pairs=duplicate_pairs,
    )
    duplicate_by_sample: dict[str, list[dict[str, Any]]] = defaultdict(list)
    selected_ids = {row.sample_id for row in rows}
    for record in duplicate_records:
        if record["sample_id"] in selected_ids:
            duplicate_by_sample[record["sample_id"]].append(record)

    # Commit deterministic clusters once. Successful model clusters from an
    # earlier invocation are already present in ``completed`` and remain intact.
    for row in rows:
        if (
            "A" in required_clusters_by_sample[row.sample_id]
            and (row.sample_id, "A") not in completed
        ):
            records = evaluate_structure_cluster(
                row,
                criteria=criteria,
                checked_at=checked_at,
            )
            append_jsonl_many(result_path, records)
            existing.extend(records)
            completed.add((row.sample_id, "A"))
        if (
            "F" in required_clusters_by_sample[row.sample_id]
            and (row.sample_id, "F") not in completed
        ):
            records = duplicate_by_sample[row.sample_id]
            append_jsonl_many(result_path, records)
            existing.extend(records)
            completed.add((row.sample_id, "F"))

    summary_sample_ids = {
        str(item.get("sample_id", ""))
        for item in existing
        if item.get("record_type") == "sample_summary"
    }

    def append_summary_if_complete(row: RawDialogueRow) -> None:
        if regression_spec is not None:
            return
        if row.sample_id in summary_sample_ids:
            return
        if not _sample_clusters_complete(completed, row.sample_id):
            return
        criterion_rows = [
            item for item in existing if item.get("record_type") == "criterion_result"
        ]
        record = sample_summary_record(criterion_rows, row)
        append_jsonl(result_path, record)
        existing.append(record)
        summary_sample_ids.add(row.sample_id)

    for row in rows:
        append_summary_if_complete(row)

    # Retry is scheduled as split-wide rounds. Each round visits every row with
    # rows or independent clusters. Only committed clusters leave the queue.
    model_cluster_order = ("B", "C", "D", "E")
    pending: dict[str, set[str]] = {
        row.sample_id: {
            cluster_id
            for cluster_id in model_cluster_order
            if cluster_id in required_clusters_by_sample[row.sample_id]
            if (row.sample_id, cluster_id) not in completed
        }
        for row in rows
    }
    non_retryable_pending: set[tuple[str, str]] = {
        (str(event.get("sample_id", "")), str(event.get("cluster_id", "")))
        for event in existing_traces
        if event.get("event_type") == "cluster_error"
        and event.get("retryable") is False
        and (
            str(event.get("sample_id", "")),
            str(event.get("cluster_id", "")),
        )
        not in completed
    }

    def pending_pairs(*, retryable_only: bool = False) -> list[dict[str, str]]:
        return [
            {"sample_id": row.sample_id, "cluster_id": cluster_id}
            for row in rows
            for cluster_id in model_cluster_order
            if cluster_id in pending[row.sample_id]
            and (
                not retryable_only
                or (row.sample_id, cluster_id) not in non_retryable_pending
            )
        ]

    max_attempts = config.max_retries_per_cluster + 1
    attempted_round_count = 0
    for attempt_number in range(1, max_attempts + 1):
        round_pending = pending_pairs(retryable_only=True)
        if not round_pending:
            break
        retry_delay_seconds = (
            config.retry_backoff_seconds * (2 ** (attempt_number - 2))
            if attempt_number > 1
            else 0.0
        )
        if retry_delay_seconds > 0:
            logger.info(
                "Waiting before retry round attempt={} delay_seconds={}",
                attempt_number,
                retry_delay_seconds,
            )
            sleep_fn(retry_delay_seconds)
        attempted_round_count = attempt_number
        logger.info(
            "Starting split-wide attempt {}/{} pending_clusters={}",
            attempt_number,
            max_attempts,
            len(round_pending),
        )
        append_jsonl(
            trace_path,
            {
                "event_type": "retry_round_started",
                "recorded_at": utc_now(),
                "execution_id": execution_id,
                "execution_sequence": execution_sequence,
                "attempt_number": attempt_number,
                "max_attempts": max_attempts,
                "retry_delay_seconds": retry_delay_seconds,
                "pending_clusters": round_pending,
            },
        )
        for row in rows:
            row_pending_before = [
                cluster_id
                for cluster_id in model_cluster_order
                if cluster_id in pending[row.sample_id]
                and (row.sample_id, cluster_id) not in non_retryable_pending
            ]
            if not row_pending_before:
                continue
            for cluster_id in model_cluster_order:
                if cluster_id not in pending[row.sample_id]:
                    continue
                if (row.sample_id, cluster_id) in non_retryable_pending:
                    continue
                system_instruction, user_prompt, prompt_hash = build_cluster_prompt(
                    cluster_id=cluster_id,
                    row=row,
                    criteria=criteria,
                    base_prompt=base_prompt,
                    bloom_reference=bloom_reference,
                    scaffolding_reference=scaffolding_reference,
                    include_tool_response_contract=(
                        config.include_tool_response_contract_in_prompt
                    ),
                    max_successful_tool_calls=(
                        config.max_successful_tool_calls_per_cluster
                    ),
                    max_total_tool_calls=config.max_total_tool_calls_per_cluster,
                    max_output_tokens=config.max_output_tokens,
                    prompt_bundle=prompt_bundle,
                )
                adapter = (
                    AuditRetrievalAdapter(
                        row=row,
                        index_path=config.retrieval_index_path,
                    )
                    if cluster_id == "B"
                    else None
                )

                def persist_cluster_trace(event: dict[str, Any]) -> None:
                    append_jsonl(
                        trace_path,
                        {
                            "schema_version": OUTPUT_SCHEMA_VERSION,
                            "plan_id": PLAN_ID,
                            "sample_id": row.sample_id,
                            "grade": row.grade,
                            "cluster_id": cluster_id,
                            "recorded_at": utc_now(),
                            "execution_id": execution_id,
                            "execution_sequence": execution_sequence,
                            "attempt_number": attempt_number,
                            **event,
                        },
                    )

                try:
                    cluster_started = time.perf_counter()
                    logger.info(
                        "Starting cluster attempt sample_id={} grade={} cluster={} attempt={}/{}",
                        row.sample_id,
                        row.grade,
                        cluster_id,
                        attempt_number,
                        max_attempts,
                    )
                    model_result = run_gemini_cluster(
                        client=client,
                        model=config.model,
                        thinking_level=config.thinking_level,
                        max_output_tokens=config.max_output_tokens,
                        seed=config.seed,
                        system_instruction=system_instruction,
                        user_prompt=user_prompt,
                        prompt_sha256=prompt_hash,
                        cluster_id=cluster_id,
                        expected_ids=CLUSTER_CRITERIA[cluster_id],
                        retrieval_adapter=adapter,
                        max_successful_tool_calls=(
                            config.max_successful_tool_calls_per_cluster
                        ),
                        max_total_tool_calls=config.max_total_tool_calls_per_cluster,
                        max_output_repair_attempts=(
                            config.max_output_repair_attempts
                        ),
                        trace_sink=persist_cluster_trace,
                    )
                except Exception as exc:
                    retryable = _is_retryable_cluster_error(exc)
                    retry_scheduled = retryable and attempt_number < max_attempts
                    next_retry_delay_seconds = (
                        config.retry_backoff_seconds * (2 ** (attempt_number - 1))
                        if retry_scheduled
                        else 0.0
                    )
                    error_event = {
                        "event_type": "cluster_attempt_error",
                        "prompt_sha256": prompt_hash,
                        "max_attempts": max_attempts,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "failure_category": (
                            "output_truncated"
                            if isinstance(exc, PilotOutputTruncatedError)
                            else "output_contract_failed"
                            if isinstance(exc, PilotOutputContractError)
                            else "cluster_attempt_failed"
                        ),
                        "retryable": retryable,
                        "retry_scheduled": retry_scheduled,
                        "retry_delay_seconds": next_retry_delay_seconds,
                    }
                    persist_cluster_trace(error_event)
                    if isinstance(exc, (PilotContractError, PilotExecutionError)):
                        logger.warning(
                            "Cluster attempt failed sample_id={} cluster={} attempt={} error_type={} error={}",
                            row.sample_id,
                            cluster_id,
                            attempt_number,
                            type(exc).__name__,
                            exc,
                        )
                    else:
                        logger.opt(exception=exc).error(
                            "Unexpected cluster failure sample_id={} cluster={} attempt={}",
                            row.sample_id,
                            cluster_id,
                            attempt_number,
                        )
                    if not retry_scheduled:
                        if not retryable:
                            non_retryable_pending.add((row.sample_id, cluster_id))
                        persist_cluster_trace(
                            {
                                **error_event,
                                "event_type": "cluster_error",
                            }
                        )
                    continue

                records = enrich_model_results(
                    row=row,
                    cluster_id=cluster_id,
                    criteria=criteria,
                    model_result=model_result,
                    checked_at=checked_at,
                    model=config.model,
                )
                append_jsonl_many(result_path, records)
                existing.extend(records)
                completed.add((row.sample_id, cluster_id))
                pending[row.sample_id].remove(cluster_id)
                logger.info(
                    "Cluster attempt completed sample_id={} cluster={} attempt={} latency_seconds={:.3f} tool_calls={}",
                    row.sample_id,
                    cluster_id,
                    attempt_number,
                    time.perf_counter() - cluster_started,
                    model_result.tool_call_count,
                )
                if attempt_number > 1:
                    persist_cluster_trace(
                        {
                            "event_type": "cluster_retry_recovered",
                            "prompt_sha256": prompt_hash,
                            "max_attempts": max_attempts,
                            "retry_count": attempt_number - 1,
                        }
                    )
            append_summary_if_complete(row)
            row_pending_after = [
                cluster_id
                for cluster_id in model_cluster_order
                if cluster_id in pending[row.sample_id]
            ]
            row_retryable_pending_after = [
                cluster_id
                for cluster_id in row_pending_after
                if (row.sample_id, cluster_id) not in non_retryable_pending
            ]
            append_jsonl(
                trace_path,
                {
                    "event_type": "row_attempt_completed",
                    "recorded_at": utc_now(),
                    "execution_id": execution_id,
                    "execution_sequence": execution_sequence,
                    "attempt_number": attempt_number,
                    "max_attempts": max_attempts,
                    "sample_id": row.sample_id,
                    "grade": row.grade,
                    "attempted_clusters": row_pending_before,
                    "pending_clusters": row_pending_after,
                    "non_retryable_pending_clusters": sorted(
                        set(row_pending_after) - set(row_retryable_pending_after)
                    ),
                    "row_status": (
                        "blocked_non_retryable"
                        if row_pending_after and not row_retryable_pending_after
                        else "pending_retry"
                        if row_pending_after
                        else "completed"
                    ),
                },
            )
        append_jsonl(
            trace_path,
            {
                "event_type": "retry_round_completed",
                "recorded_at": utc_now(),
                "execution_id": execution_id,
                "execution_sequence": execution_sequence,
                "attempt_number": attempt_number,
                "max_attempts": max_attempts,
                "pending_clusters": pending_pairs(),
                "retryable_pending_clusters": pending_pairs(retryable_only=True),
                "non_retryable_pending_clusters": [
                    {"sample_id": sample_id, "cluster_id": cluster_id}
                    for sample_id, cluster_id in sorted(non_retryable_pending)
                    if cluster_id in pending.get(sample_id, set())
                ],
            },
        )
        logger.info(
            "Completed split-wide attempt {}/{} pending_clusters={}",
            attempt_number,
            max_attempts,
            len(pending_pairs()),
        )

    unresolved = pending_pairs()
    unresolved_non_retryable = [
        {"sample_id": sample_id, "cluster_id": cluster_id}
        for sample_id, cluster_id in sorted(non_retryable_pending)
        if cluster_id in pending.get(sample_id, set())
    ]
    run_status = "incomplete" if unresolved else "completed"
    append_jsonl(
        trace_path,
        {
            "event_type": "run_incomplete" if unresolved else "run_completed",
            "recorded_at": utc_now(),
            "execution_id": execution_id,
            "execution_sequence": execution_sequence,
            "attempted_round_count": attempted_round_count,
            "pending_clusters": unresolved,
            "non_retryable_pending_clusters": unresolved_non_retryable,
        },
    )

    # Publish a machine-readable summary even for a graceful incomplete run.
    # Sample summaries remain restricted to samples with all 18 criteria.
    final_rows = read_jsonl(result_path)
    criterion_rows = [row for row in final_rows if row.get("record_type") == "criterion_result"]
    summary_rows = [row for row in final_rows if row.get("record_type") == "sample_summary"]
    complete_sample_ids = {
        row.sample_id
        for row in rows
        if all(
            (row.sample_id, cluster_id) in completed
            for cluster_id in required_clusters_by_sample[row.sample_id]
        )
    }
    if regression_spec is None:
        for row in rows:
            if row.sample_id in complete_sample_ids:
                validate_complete_sample(criterion_rows, row.sample_id)
    traces = read_jsonl(trace_path)
    current_execution_traces = [
        event
        for event in traces
        if str(event.get("execution_id", "")) == execution_id
    ]
    current_tool_required_sample_count = len(
        {
            str(event.get("sample_id", ""))
            for event in current_execution_traces
            if event.get("cluster_id") == "B" and event.get("sample_id")
        }
    )
    current_execution_metrics = summarize_trace_metrics(
        current_execution_traces,
        tool_required_sample_count=current_tool_required_sample_count,
    )
    cumulative_metrics = summarize_trace_metrics(
        traces,
        tool_required_sample_count=len(rows),
    )
    regression_evaluation = (
        evaluate_regression_results(criterion_rows, regression_spec)
        if regression_spec is not None
        else None
    )
    regression_evaluation_path = output_dir / "regression_evaluation.json"
    if regression_evaluation is not None:
        atomic_write_json(regression_evaluation_path, regression_evaluation)
    summary = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "experiment_id": config.experiment_id,
        "plan_id": PLAN_ID,
        "split": split,
        "completed_at": utc_now(),
        "run_status": run_status,
        "execution_id": execution_id,
        "execution_sequence": execution_sequence,
        "resume": resume,
        "attempted_round_count": attempted_round_count,
        "sample_count": len(rows),
        "completed_sample_count": len(complete_sample_ids),
        "incomplete_sample_count": len(rows) - len(complete_sample_ids),
        "pending_sample_ids": sorted({item["sample_id"] for item in unresolved}),
        "pending_clusters": unresolved,
        "non_retryable_pending_clusters": unresolved_non_retryable,
        "criterion_result_count": len(criterion_rows),
        "sample_summary_count": len(summary_rows),
        "decision_counts": dict(Counter(str(row.get("quality_decision")) for row in summary_rows)),
        "criterion_result_counts": dict(Counter(str(row.get("result")) for row in criterion_rows)),
        "cluster_scope": {
            sample_id: list(cluster_ids)
            for sample_id, cluster_ids in required_clusters_by_sample.items()
        },
        "regression_evaluation": regression_evaluation,
        "current_execution_metrics": current_execution_metrics,
        "cumulative_metrics": cumulative_metrics,
        "near_duplicate_threshold": config.near_duplicate_threshold,
        "duplicate_filter_summary": flagged_duplicate_summary(
            all_rows,
            near_threshold=config.near_duplicate_threshold,
            candidate_pairs=duplicate_pairs,
        ),
        "runtime_config": {
            "model": config.model,
            "location": config.location,
            "max_output_tokens": config.max_output_tokens,
            "seed": config.seed,
            "thinking_level": config.thinking_level,
            "timeout_seconds": config.timeout_seconds,
            "include_tool_response_contract_in_prompt": (
                config.include_tool_response_contract_in_prompt
            ),
            "max_successful_tool_calls_per_cluster": (
                config.max_successful_tool_calls_per_cluster
            ),
            "max_total_tool_calls_per_cluster": config.max_total_tool_calls_per_cluster,
            "max_retries_per_cluster": config.max_retries_per_cluster,
            "retry_backoff_seconds": config.retry_backoff_seconds,
            "max_output_repair_attempts": config.max_output_repair_attempts,
        },
        "resume_recovery": recovery,
        "run_fingerprint": run_contract["run_fingerprint"],
        "input_hashes": run_contract["input_hashes"],
        "artifacts": {
            "clustered_audit_results": result_path.as_posix(),
            "retrieval_and_model_trace": trace_path.as_posix(),
            "pilot_evaluation_summary": summary_path.as_posix(),
            **(
                {"regression_evaluation": regression_evaluation_path.as_posix()}
                if regression_evaluation is not None
                else {}
            ),
        },
        "claims": {
            "human_reference_available": False,
            "accuracy_reported": False,
            "results_are_preliminary": True,
        },
    }
    atomic_write_json(summary_path, summary)
    if unresolved:
        logger.error(
            "Plan 03 run incomplete split={} pending_clusters={} summary={}",
            split,
            len(unresolved),
            summary_path,
        )
        if unresolved_non_retryable:
            raise PilotExecutionError(
                f"Run remains incomplete with {len(unresolved_non_retryable)} "
                "non-retryable sample/cluster pairs. Review the trace before "
                "choosing the appropriate recovery action. "
                f"Summary: {summary_path}"
            )
        raise PilotExecutionError(
            f"Run remains incomplete after {max_attempts} split-wide attempts; "
            f"{len(unresolved)} sample/cluster pairs remain. Resume the same run-id "
            f"after reviewing {summary_path}"
        )
    logger.info(
        "Plan 03 run completed split={} samples={} summary={}",
        split,
        len(rows),
        summary_path,
    )
    return summary

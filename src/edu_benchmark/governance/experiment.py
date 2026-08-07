"""Validate the lightweight experiment governance contract.

The validator intentionally uses a small explicit rule set instead of adding a
JSON Schema runtime dependency before the packaging/environment plan is approved.
The JSON schemas remain the language-neutral contract for other tooling.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


PLAN_FILE_RE = re.compile(r"^(?P<number>[0-9]{2})-.+\.md$")
PLAN_ID_RE = re.compile(r"^P(?P<number>[0-9]{2})$")
AMENDMENT_ID_RE = re.compile(r"^P(?P<number>[0-9]{2})-A[0-9]{3}$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
APPROVED_LINE_RE = re.compile(r"^Trạng thái:\s*`[^`]*\bAPPROVED\b[^`]*`\s*$")

LIFECYCLE_STATUSES = {
    "draft",
    "approved",
    "in_progress",
    "blocked",
    "completed",
    "cancelled",
    "superseded",
}
APPROVAL_STATES = {"pending", "approved", "rejected"}
GATE_STATES = {"closed", "open", "passed", "not_applicable"}
ARTIFACT_KINDS = {
    "baseline_plan",
    "status_file",
    "amendment_log",
    "runbook",
    "final_report",
    "handoff",
    "machine_output",
}
PROTECTED_STATUSES = LIFECYCLE_STATUSES - {"draft", "cancelled", "superseded"}
WORKFLOW_EVENT_TYPES = {
    "plan_approved",
    "workflow_started",
    "workflow_updated",
    "workflow_completed",
    "workflow_blocked",
    "amendment_recorded",
    "validation_completed",
}
WORKFLOW_EVENT_STATUSES = {
    "recorded",
    "started",
    "running",
    "completed",
    "blocked",
    "failed",
}
DELEGATION_EVENT_TYPES = {
    "delegation_started",
    "delegation_steered",
    "delegation_completed",
    "delegation_stopped",
    "delegation_failed",
}


@dataclass(frozen=True)
class ValidationIssue:
    """One actionable governance validation failure."""

    code: str
    path: Path
    message: str

    def format(self, repo_root: Path | None = None) -> str:
        path = self.path
        if repo_root is not None:
            try:
                path = path.resolve().relative_to(repo_root.resolve())
            except ValueError:
                pass
        return f"[{self.code}] {path}: {self.message}"


def _issue(issues: list[ValidationIssue], code: str, path: Path, message: str) -> None:
    issues.append(ValidationIssue(code=code, path=path, message=message))


def _load_yaml(path: Path, issues: list[ValidationIssue]) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        _issue(issues, "yaml_invalid", path, str(exc))
        return None


def _parse_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _resolve_inside(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _validate_markdown_links(
    markdown_path: Path,
    repo_root: Path,
    issues: list[ValidationIssue],
) -> None:
    content = markdown_path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK_RE.findall(content):
        target = raw_target.strip().strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", maxsplit=1)[0]
        if not target:
            continue
        resolved = (markdown_path.parent / target).resolve()
        try:
            resolved.relative_to(repo_root.resolve())
        except ValueError:
            _issue(issues, "link_outside_repo", markdown_path, raw_target)
            continue
        if not resolved.exists():
            _issue(issues, "link_missing", markdown_path, raw_target)


def _validate_metadata(
    experiment_root: Path,
    repo_root: Path,
    issues: list[ValidationIssue],
) -> dict[str, Any] | None:
    path = experiment_root / "metadata.yaml"
    if not path.is_file():
        _issue(issues, "metadata_missing", path, "metadata.yaml is required")
        return None
    data = _load_yaml(path, issues)
    if not isinstance(data, dict):
        _issue(issues, "metadata_type", path, "metadata must be a mapping")
        return None
    required = {
        "id",
        "title",
        "status",
        "task_type",
        "owner_agent",
        "parents",
        "created_at",
        "artifacts",
    }
    missing = sorted(required - data.keys())
    if missing:
        _issue(issues, "metadata_fields", path, f"missing fields: {missing}")
    if data.get("id") != experiment_root.name:
        _issue(issues, "metadata_id", path, "id must match the experiment directory")
    if not _parse_timestamp(data.get("created_at")):
        _issue(issues, "metadata_timestamp", path, "created_at must be ISO-8601")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        _issue(issues, "metadata_artifacts", path, "artifacts must be a list")
    else:
        if len(artifacts) != len(set(map(str, artifacts))):
            _issue(issues, "metadata_artifact_duplicate", path, "artifact paths must be unique")
        for relative in artifacts:
            resolved = _resolve_inside(experiment_root, relative)
            if resolved is None:
                _issue(issues, "metadata_artifact_path", path, f"unsafe path: {relative!r}")
            elif not resolved.exists():
                _issue(issues, "metadata_artifact_missing", path, str(relative))
    return data


def _approved_marker(path: Path) -> bool:
    return any(
        APPROVED_LINE_RE.match(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def _registered_conventional_artifacts(experiment_root: Path, number: str) -> set[str]:
    found: set[str] = set()
    candidates = [
        experiment_root / "decisions" / f"plan{number}-amendments.md",
        experiment_root / "reports" / f"plan{number}-final.md",
    ]
    candidates.extend((experiment_root / "runbooks").glob(f"plan{number}*.md"))
    candidates.extend((experiment_root / "handoffs").glob(f"plan{number}-*.md"))
    for path in candidates:
        if path.is_file():
            found.add(path.relative_to(experiment_root).as_posix())
    return found


def _validate_plan_status(
    experiment_root: Path,
    plan_path: Path,
    known_plan_ids: set[str],
    issues: list[ValidationIssue],
) -> None:
    match = PLAN_FILE_RE.match(plan_path.name)
    if match is None:
        return
    number = match.group("number")
    plan_id = f"P{number}"
    status_path = experiment_root / "plans" / f"{number}-status.yaml"
    if not status_path.is_file():
        _issue(issues, "status_missing", status_path, f"required for {plan_path.name}")
        return
    data = _load_yaml(status_path, issues)
    if not isinstance(data, dict):
        _issue(issues, "status_type", status_path, "status must be a mapping")
        return

    required = {
        "schema_version",
        "experiment_id",
        "plan_id",
        "sequence",
        "baseline_path",
        "status",
        "approval",
        "updated_at",
        "current_step",
        "last_amendment",
        "depends_on",
        "gate",
        "artifacts",
        "artifact_budget",
    }
    missing = sorted(required - data.keys())
    if missing:
        _issue(issues, "status_fields", status_path, f"missing fields: {missing}")

    if data.get("schema_version") != "1.0":
        _issue(issues, "status_schema", status_path, "schema_version must be 1.0")
    if data.get("experiment_id") != experiment_root.name:
        _issue(issues, "status_experiment", status_path, "experiment_id mismatch")
    if data.get("plan_id") != plan_id or data.get("sequence") != int(number):
        _issue(issues, "status_plan_id", status_path, f"expected {plan_id}/{int(number)}")
    expected_baseline = plan_path.relative_to(experiment_root).as_posix()
    if data.get("baseline_path") != expected_baseline:
        _issue(issues, "status_baseline", status_path, f"expected {expected_baseline}")

    lifecycle = data.get("status")
    if lifecycle not in LIFECYCLE_STATUSES:
        _issue(issues, "status_value", status_path, f"unknown status: {lifecycle!r}")
    approval = data.get("approval")
    if not isinstance(approval, dict) or approval.get("state") not in APPROVAL_STATES:
        _issue(issues, "approval_value", status_path, "invalid approval mapping")
        approval = {}
    marker = _approved_marker(plan_path)
    if lifecycle in PROTECTED_STATUSES:
        if not marker:
            _issue(issues, "approved_marker_missing", plan_path, "status requires an APPROVED baseline")
        if approval.get("state") != "approved" or not approval.get("authority"):
            _issue(issues, "approval_missing", status_path, "approved lifecycle requires authority")
        if not _parse_timestamp(approval.get("approved_at")):
            _issue(issues, "approval_timestamp", status_path, "approved_at must be ISO-8601")
    elif lifecycle == "draft" and marker:
        _issue(issues, "draft_approved_conflict", plan_path, "draft plan cannot say APPROVED")

    if not _parse_timestamp(data.get("updated_at")):
        _issue(issues, "status_timestamp", status_path, "updated_at must be ISO-8601")
    dependencies = data.get("depends_on")
    if not isinstance(dependencies, list):
        _issue(issues, "dependency_type", status_path, "depends_on must be a list")
    else:
        for dependency in dependencies:
            dependency_match = PLAN_ID_RE.match(str(dependency))
            if dependency not in known_plan_ids:
                _issue(issues, "dependency_unknown", status_path, str(dependency))
            elif dependency_match and int(dependency_match.group("number")) >= int(number):
                _issue(issues, "dependency_order", status_path, str(dependency))

    gate = data.get("gate")
    if not isinstance(gate, dict) or gate.get("state") not in GATE_STATES or not gate.get("summary"):
        _issue(issues, "gate_invalid", status_path, "gate requires a known state and summary")
    elif lifecycle == "completed" and gate.get("state") not in {"passed", "not_applicable"}:
        _issue(issues, "gate_incomplete", status_path, "completed plan must pass its gate")

    last_amendment = data.get("last_amendment")
    if last_amendment is not None:
        amendment_match = AMENDMENT_ID_RE.match(str(last_amendment))
        if amendment_match is None or amendment_match.group("number") != number:
            _issue(issues, "amendment_id", status_path, str(last_amendment))
        amendment_path = experiment_root / "decisions" / f"plan{number}-amendments.md"
        if not amendment_path.is_file() or f"## {last_amendment}" not in amendment_path.read_text(encoding="utf-8"):
            _issue(issues, "amendment_missing", status_path, str(last_amendment))

    artifacts = data.get("artifacts")
    registered: set[str] = set()
    counts: Counter[str] = Counter()
    if not isinstance(artifacts, list):
        _issue(issues, "artifact_type", status_path, "artifacts must be a list")
        artifacts = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            _issue(issues, "artifact_entry", status_path, repr(artifact))
            continue
        relative = artifact.get("path")
        kind = artifact.get("kind")
        if kind not in ARTIFACT_KINDS:
            _issue(issues, "artifact_kind", status_path, repr(kind))
            continue
        resolved = _resolve_inside(experiment_root, relative)
        if resolved is None:
            _issue(issues, "artifact_path", status_path, repr(relative))
            continue
        relative_text = Path(str(relative)).as_posix()
        if relative_text in registered:
            _issue(issues, "artifact_duplicate", status_path, relative_text)
        registered.add(relative_text)
        counts[kind] += 1
        if not resolved.exists():
            _issue(issues, "artifact_missing", status_path, relative_text)
    for required_path in {expected_baseline, f"plans/{number}-status.yaml"}:
        if required_path not in registered:
            _issue(issues, "artifact_registration", status_path, f"missing {required_path}")

    budget = data.get("artifact_budget")
    limits = budget.get("limits", {}) if isinstance(budget, dict) else {}
    exceptions = budget.get("exceptions", []) if isinstance(budget, dict) else []
    exception_kinds = {
        item.get("kind")
        for item in exceptions
        if isinstance(item, dict) and item.get("reason")
    }
    for kind in ARTIFACT_KINDS:
        limit = limits.get(kind)
        if not isinstance(limit, int) or limit < 0:
            _issue(issues, "budget_limit", status_path, f"invalid {kind} limit")
        elif counts[kind] > limit and kind not in exception_kinds:
            _issue(issues, "artifact_budget", status_path, f"{kind}: {counts[kind]} > {limit}")

    conventional = _registered_conventional_artifacts(experiment_root, number)
    for relative in sorted(conventional - registered):
        _issue(issues, "artifact_unregistered", status_path, relative)


def _validate_coordination(experiment_root: Path, issues: list[ValidationIssue]) -> None:
    path = experiment_root / "coordination" / "coordination_log.jsonl"
    if not path.is_file():
        _issue(issues, "coordination_missing", path, "coordination log is required")
        return
    event_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            _issue(issues, "coordination_json", path, f"line {line_number}: {exc}")
            continue
        if not isinstance(event, dict) or not _parse_timestamp(event.get("timestamp")):
            _issue(issues, "coordination_timestamp", path, f"line {line_number}")
            continue
        if event.get("schema_version") == "1.0":
            required = {
                "event_id",
                "event_type",
                "actor",
                "task",
                "input_paths",
                "allowed_write_paths",
                "status",
                "output_paths",
                "open_questions",
            }
            missing = sorted(required - event.keys())
            if missing:
                _issue(issues, "coordination_fields", path, f"line {line_number}: {missing}")
            event_id = event.get("event_id")
            if not isinstance(event_id, str) or not event_id:
                _issue(issues, "coordination_id", path, f"line {line_number}")
            elif event_id in event_ids:
                _issue(issues, "coordination_duplicate", path, event_id)
            else:
                event_ids.add(event_id)
            if event.get("event_type") not in WORKFLOW_EVENT_TYPES:
                _issue(issues, "coordination_type", path, str(event.get("event_type")))
            if event.get("status") not in WORKFLOW_EVENT_STATUSES:
                _issue(issues, "coordination_status", path, str(event.get("status")))
            for field in ("input_paths", "allowed_write_paths", "output_paths", "open_questions"):
                if not isinstance(event.get(field), list):
                    _issue(issues, "coordination_list", path, f"line {line_number}: {field}")
        elif "delegation_id" in event:
            required = {
                "event_type",
                "parent_session",
                "agent",
                "task",
                "input_paths",
                "allowed_write_paths",
                "status",
                "output_paths",
                "open_questions",
            }
            if event.get("event_type") not in DELEGATION_EVENT_TYPES or required - event.keys():
                _issue(issues, "coordination_delegation", path, f"line {line_number}")
        elif not {"actor", "event", "details"}.issubset(event):
            _issue(issues, "coordination_legacy", path, f"line {line_number}")


def validate_templates(repo_root: Path) -> list[ValidationIssue]:
    """Validate required governance template files and parseable schemas."""

    repo_root = repo_root.resolve()
    root = repo_root / "experiments" / "_templates"
    issues: list[ValidationIssue] = []
    required = {
        "README.md",
        "roadmap.md",
        "plan.md",
        "plan-status.yaml",
        "plan-status.schema.json",
        "experiment-metadata.schema.json",
        "amendments.md",
        "final-report.md",
        "runbook.md",
        "handoff.md",
        "coordination-event.schema.json",
    }
    for name in sorted(required):
        path = root / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            _issue(issues, "template_missing", path, "required non-empty template")
    for name in ("plan-status.schema.json", "experiment-metadata.schema.json", "coordination-event.schema.json"):
        path = root / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _issue(issues, "schema_json", path, str(exc))
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            _issue(issues, "schema_version", path, "expected JSON Schema 2020-12")
    return issues


def validate_experiment(
    experiment_root: Path,
    *,
    repo_root: Path | None = None,
) -> list[ValidationIssue]:
    """Validate one experiment using the v1 governance convention."""

    experiment_root = experiment_root.resolve()
    repo_root = (repo_root or experiment_root.parents[1]).resolve()
    issues: list[ValidationIssue] = []
    if not experiment_root.is_dir():
        _issue(issues, "experiment_missing", experiment_root, "directory does not exist")
        return issues
    _validate_metadata(experiment_root, repo_root, issues)
    roadmap = experiment_root / "roadmap.md"
    if not roadmap.is_file():
        _issue(issues, "roadmap_missing", roadmap, "roadmap.md is required")
    else:
        _validate_markdown_links(roadmap, repo_root, issues)

    plans = sorted(
        path
        for path in (experiment_root / "plans").glob("[0-9][0-9]-*.md")
        if PLAN_FILE_RE.match(path.name)
    )
    if not plans:
        _issue(issues, "plans_missing", experiment_root / "plans", "no baseline plans found")
    known_plan_ids = {f"P{PLAN_FILE_RE.match(path.name).group('number')}" for path in plans}
    for plan_path in plans:
        _validate_markdown_links(plan_path, repo_root, issues)
        _validate_plan_status(experiment_root, plan_path, known_plan_ids, issues)

    for subdir in ("decisions", "runbooks", "reports", "handoffs"):
        directory = experiment_root / subdir
        if directory.is_dir():
            for markdown_path in directory.glob("*.md"):
                _validate_markdown_links(markdown_path, repo_root, issues)
    _validate_coordination(experiment_root, issues)
    return issues


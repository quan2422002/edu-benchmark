"""Tests for the experiment governance contract introduced in Plan 01."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from edu_benchmark.governance import validate_experiment, validate_templates


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "20260806_145124"


def test_governance_templates_are_complete() -> None:
    assert validate_templates(ROOT) == []


def test_current_refactor_experiment_is_valid() -> None:
    assert validate_experiment(EXPERIMENT, repo_root=ROOT) == []


def test_machine_status_cannot_authorize_an_unapproved_baseline(tmp_path: Path) -> None:
    copy = tmp_path / EXPERIMENT.name
    shutil.copytree(EXPERIMENT, copy)
    baseline = copy / "plans" / "01-planning-governance-and-decision-records.md"
    baseline.write_text(
        baseline.read_text(encoding="utf-8").replace(
            "APPROVED — 2026-08-06 — PROJECT LEAD",
            "DRAFT — AWAITING PROJECT-LEAD APPROVAL",
        ),
        encoding="utf-8",
    )
    issues = validate_experiment(copy, repo_root=tmp_path)
    assert "approved_marker_missing" in {issue.code for issue in issues}


def test_artifact_budget_requires_a_justified_exception(tmp_path: Path) -> None:
    copy = tmp_path / EXPERIMENT.name
    shutil.copytree(EXPERIMENT, copy)
    status_path = copy / "plans" / "01-status.yaml"
    status = yaml.safe_load(status_path.read_text(encoding="utf-8"))
    for index in range(4):
        relative = f"outputs/plan01-machine-{index}.json"
        output = copy / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("{}\n", encoding="utf-8")
        status["artifacts"].append({"path": relative, "kind": "machine_output"})
    status_path.write_text(
        yaml.safe_dump(status, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    issues = validate_experiment(copy, repo_root=tmp_path)
    assert "artifact_budget" in {issue.code for issue in issues}


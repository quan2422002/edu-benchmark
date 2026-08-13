from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess

import pytest

from edu_benchmark.repository_hygiene import (
    HygieneConfigError,
    load_hygiene_config,
    scan_repository,
)


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)


def _config(root: Path, *, repository_root: str = ".") -> Path:
    path = root / "hygiene.yaml"
    path.write_text(
        f"""schema_version: "1.0"
config_id: "test-v1"
repository_root: "{repository_root}"
output_root: "outputs/plan06"
scan_roots:
  - "."
exclude_globs:
  - ".git/**"
  - "outputs/plan06/**"
  - ".env"
  - "**/.env"
duplicate_min_bytes: 4
targets:
  - target_id: "raw-output"
    path_globs:
      - "outputs/raw/*.jsonl"
    reference_terms:
      - "outputs/raw/"
    artifact_class: "raw_provider_output"
    proposed_action: "externalize"
    approval_state: "pending_project_lead"
    locator_required: true
    restore_test_required: true
    rationale: "Synthetic raw output."
""",
        encoding="utf-8",
    )
    return path


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_inventory_classifies_git_state_duplicates_and_references(
    tmp_path: Path,
) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("outputs/raw/\n", encoding="utf-8")
    (tmp_path / "tracked.bin").write_bytes(b"duplicate")
    (tmp_path / "consumer.md").write_text(
        "Read outputs/raw/ before cleanup.\n", encoding="utf-8"
    )
    (tmp_path / ".env").write_text("API_KEY=must-not-leak\n", encoding="utf-8")
    (tmp_path / "outputs/raw").mkdir(parents=True)
    (tmp_path / "outputs/raw/provider.jsonl").write_bytes(b"duplicate")
    (tmp_path / "untracked.txt").write_text("local\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.bin", "consumer.md")

    result = scan_repository(load_hygiene_config(_config(tmp_path)))
    rows = {row["path"]: row for row in _rows(result.inventory_path)}
    assert rows["tracked.bin"]["git_state"] == "tracked"
    assert rows["outputs/raw/provider.jsonl"]["git_state"] == "ignored"
    assert "untracked.txt" not in rows
    assert ".env" not in rows
    assert rows["outputs/raw/provider.jsonl"]["reference_count"] == "2"

    duplicates = _rows(result.duplicates_path)
    assert {row["path"] for row in duplicates} == {
        "outputs/raw/provider.jsonl",
        "tracked.bin",
    }
    assert {row["duplicate_group_id"] for row in duplicates} == {"DUP-0001"}

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["mode"] == "non_destructive_inventory"
    assert manifest["source_mutation_count"] == 0
    assert manifest["scan"]["tracked_over_github_100mb_count"] == 0
    assert manifest["scan"]["omitted_untracked_file_count"] == 2
    assert manifest["scan"]["omitted_untracked_bytes"] >= len("local\n")
    target = manifest["targets"][0]
    assert target["approval_state"] == "pending_project_lead"
    assert target["reference_paths"] == [".gitignore", "consumer.md"]
    assert manifest["safety"]["destructive_actions_executed"] == []


def test_inventory_is_stable_when_its_output_directory_is_excluded(
    tmp_path: Path,
) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    (tmp_path / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore", "tracked.txt")
    config = load_hygiene_config(_config(tmp_path))

    first = scan_repository(config)
    first_inventory = first.inventory_path.read_bytes()
    first_duplicates = first.duplicates_path.read_bytes()
    first_manifest = first.manifest_path.read_bytes()
    second = scan_repository(config)

    assert second.inventory_path.read_bytes() == first_inventory
    assert second.duplicates_path.read_bytes() == first_duplicates
    assert second.manifest_path.read_bytes() == first_manifest


def test_config_rejects_repository_escape(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    config_path = _config(tmp_path, repository_root="..")
    with pytest.raises(HygieneConfigError, match="Git worktree"):
        load_hygiene_config(config_path)


def test_plan06_jsonl_ignore_rules_are_scoped_and_documented() -> None:
    root = Path(__file__).resolve().parents[2]
    content = (root / ".gitignore").read_text(encoding="utf-8")
    rules = {
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert (
        "/experiments/20260727_170150/outputs/benchmark_evaluation/**/*.jsonl"
        in content
    )
    assert (
        "/experiments/20260727_170150/outputs/"
        "principle_requirement_scoring/**/*.jsonl"
        in content
    )
    assert "/experiments/*/outputs/**/*.jsonl" not in rules
    assert "experiments/**/outputs/**/*.jsonl" not in rules
    assert "run_responses.jsonl" in content
    assert "run_judgments.jsonl" in content
    assert "batch_input.jsonl" in content
    assert "provider_output.jsonl" in content
    assert "run_full.jsonl" in content

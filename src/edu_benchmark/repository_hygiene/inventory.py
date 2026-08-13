"""Deterministic, non-destructive repository-output inventory."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Iterable, Mapping, Sequence

import yaml


class HygieneConfigError(ValueError):
    """Raised when a repository-hygiene config is unsafe or malformed."""


INVENTORY_FIELDS = (
    "path",
    "size_bytes",
    "sha256",
    "extension",
    "git_state",
    "target_id",
    "artifact_class",
    "duplicate_group_id",
    "reference_count",
)
DUPLICATE_FIELDS = (
    "duplicate_group_id",
    "sha256",
    "size_bytes",
    "member_count",
    "redundant_bytes",
    "path",
    "git_state",
    "target_id",
)
_TOP_LEVEL_KEYS = {
    "schema_version",
    "config_id",
    "repository_root",
    "output_root",
    "scan_roots",
    "exclude_globs",
    "duplicate_min_bytes",
    "targets",
}
_TARGET_KEYS = {
    "target_id",
    "path_globs",
    "reference_terms",
    "artifact_class",
    "proposed_action",
    "approval_state",
    "locator_required",
    "restore_test_required",
    "rationale",
}
_ACTIONS = {"keep", "promote", "externalize", "archive", "delete"}
_APPROVAL_STATES = {"plan_approved", "pending_project_lead"}


@dataclass(frozen=True)
class HygieneTarget:
    """One path-specific retention proposal from the reviewed config."""

    target_id: str
    path_globs: tuple[str, ...]
    reference_terms: tuple[str, ...]
    artifact_class: str
    proposed_action: str
    approval_state: str
    locator_required: bool
    restore_test_required: bool
    rationale: str

    def matches(self, relative_path: str) -> bool:
        return any(
            fnmatch.fnmatchcase(relative_path, pattern)
            for pattern in self.path_globs
        )


@dataclass(frozen=True)
class HygieneConfig:
    """Resolved configuration for one non-destructive inventory run."""

    path: Path
    config_id: str
    repository_root: Path
    output_root: Path
    scan_roots: tuple[Path, ...]
    exclude_globs: tuple[str, ...]
    duplicate_min_bytes: int
    targets: tuple[HygieneTarget, ...]


@dataclass(frozen=True)
class InventoryResult:
    """Paths and summary returned by a completed inventory scan."""

    inventory_path: Path
    duplicates_path: Path
    manifest_path: Path
    file_count: int
    total_bytes: int
    tracked_file_count: int
    tracked_bytes: int
    duplicate_group_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "passed",
            "inventory_path": self.inventory_path.as_posix(),
            "duplicates_path": self.duplicates_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "tracked_file_count": self.tracked_file_count,
            "tracked_bytes": self.tracked_bytes,
            "duplicate_group_count": self.duplicate_group_count,
        }


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HygieneConfigError(f"{label} must be a mapping")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        raise HygieneConfigError(
            f"{label} keys mismatch; missing={missing}, extra={extra}"
        )


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HygieneConfigError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise HygieneConfigError(f"{label} must be a list of strings")
    return tuple(_string(item, f"{label}[]") for item in value)


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise HygieneConfigError(f"{label} must be boolean")
    return value


def _relative_path(root: Path, value: Any, label: str) -> Path:
    relative = Path(_string(value, label))
    if relative.is_absolute():
        raise HygieneConfigError(f"{label} must be repository-relative")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise HygieneConfigError(f"{label} escapes repository root") from exc
    return resolved


def load_hygiene_config(path: Path) -> HygieneConfig:
    """Load a strict repository-relative Plan 06 scan configuration."""

    config_path = path.resolve()
    if not config_path.is_file():
        raise HygieneConfigError(f"config does not exist: {config_path}")
    raw = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "config")
    _exact_keys(raw, _TOP_LEVEL_KEYS, "config")
    if raw["schema_version"] != "1.0":
        raise HygieneConfigError("schema_version must be '1.0'")
    repository_relative = Path(_string(raw["repository_root"], "repository_root"))
    if repository_relative.is_absolute():
        raise HygieneConfigError("repository_root must be relative")
    repository_root = (config_path.parent / repository_relative).resolve()
    if not (repository_root / ".git").is_dir():
        raise HygieneConfigError("repository_root must identify a Git worktree")
    output_root = _relative_path(repository_root, raw["output_root"], "output_root")
    scan_roots = tuple(
        _relative_path(repository_root, item, "scan_roots[]")
        for item in _string_list(raw["scan_roots"], "scan_roots")
    )
    duplicate_min_bytes = raw["duplicate_min_bytes"]
    if (
        not isinstance(duplicate_min_bytes, int)
        or isinstance(duplicate_min_bytes, bool)
        or duplicate_min_bytes < 1
    ):
        raise HygieneConfigError("duplicate_min_bytes must be a positive integer")
    targets: list[HygieneTarget] = []
    seen_ids: set[str] = set()
    if not isinstance(raw["targets"], list) or not raw["targets"]:
        raise HygieneConfigError("targets must be a non-empty list")
    for index, value in enumerate(raw["targets"]):
        target_raw = _mapping(value, f"targets[{index}]")
        _exact_keys(target_raw, _TARGET_KEYS, f"targets[{index}]")
        target_id = _string(target_raw["target_id"], f"targets[{index}].target_id")
        if target_id in seen_ids:
            raise HygieneConfigError(f"duplicate target_id: {target_id}")
        seen_ids.add(target_id)
        action = _string(
            target_raw["proposed_action"],
            f"targets[{index}].proposed_action",
        )
        approval_state = _string(
            target_raw["approval_state"],
            f"targets[{index}].approval_state",
        )
        if action not in _ACTIONS:
            raise HygieneConfigError(f"unsupported proposed_action: {action}")
        if approval_state not in _APPROVAL_STATES:
            raise HygieneConfigError(f"unsupported approval_state: {approval_state}")
        targets.append(
            HygieneTarget(
                target_id=target_id,
                path_globs=_string_list(
                    target_raw["path_globs"], f"targets[{index}].path_globs"
                ),
                reference_terms=_string_list(
                    target_raw["reference_terms"],
                    f"targets[{index}].reference_terms",
                    allow_empty=True,
                ),
                artifact_class=_string(
                    target_raw["artifact_class"],
                    f"targets[{index}].artifact_class",
                ),
                proposed_action=action,
                approval_state=approval_state,
                locator_required=_boolean(
                    target_raw["locator_required"],
                    f"targets[{index}].locator_required",
                ),
                restore_test_required=_boolean(
                    target_raw["restore_test_required"],
                    f"targets[{index}].restore_test_required",
                ),
                rationale=_string(
                    target_raw["rationale"], f"targets[{index}].rationale"
                ),
            )
        )
    return HygieneConfig(
        path=config_path,
        config_id=_string(raw["config_id"], "config_id"),
        repository_root=repository_root,
        output_root=output_root,
        scan_roots=scan_roots,
        exclude_globs=_string_list(
            raw["exclude_globs"], "exclude_globs", allow_empty=True
        ),
        duplicate_min_bytes=duplicate_min_bytes,
        targets=tuple(targets),
    )


def _run_git(root: Path, arguments: Sequence[str], *, stdin: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode not in {0, 1}:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise HygieneConfigError(f"git {' '.join(arguments)} failed: {message}")
    return result.stdout


def _nul_paths(raw: bytes) -> set[str]:
    return {
        item.decode("utf-8", errors="surrogateescape")
        for item in raw.split(b"\0")
        if item
    }


def _excluded(relative_path: str, patterns: Sequence[str]) -> bool:
    return any(
        relative_path == pattern.rstrip("/**")
        or fnmatch.fnmatchcase(relative_path, pattern)
        for pattern in patterns
    )


def _iter_files(config: HygieneConfig) -> list[Path]:
    files: dict[str, Path] = {}
    for scan_root in config.scan_roots:
        if not scan_root.exists():
            raise HygieneConfigError(f"scan root does not exist: {scan_root}")
        candidates: Iterable[Path]
        candidates = [scan_root] if scan_root.is_file() else scan_root.rglob("*")
        for path in candidates:
            if not path.is_file() and not path.is_symlink():
                continue
            relative = path.relative_to(config.repository_root).as_posix()
            if _excluded(relative, config.exclude_globs):
                continue
            files[relative] = path
    return [files[key] for key in sorted(files)]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(os.readlink(path).encode("utf-8", errors="surrogateescape"))
        return digest.hexdigest()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(path: Path, fields: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _target_for(path: str, targets: Sequence[HygieneTarget]) -> HygieneTarget | None:
    matches = [target for target in targets if target.matches(path)]
    if len(matches) > 1:
        ids = ", ".join(target.target_id for target in matches)
        raise HygieneConfigError(f"path matches multiple retention targets: {path}: {ids}")
    return matches[0] if matches else None


def _reference_files(
    *,
    config: HygieneConfig,
    files: Sequence[Path],
    tracked: set[str],
) -> dict[str, list[str]]:
    references = {target.target_id: [] for target in config.targets}
    terms = {
        target.target_id: target.reference_terms
        for target in config.targets
        if target.reference_terms
    }
    if not terms:
        return references
    for path in files:
        relative = path.relative_to(config.repository_root).as_posix()
        if relative not in tracked:
            continue
        if path.is_symlink() or path.stat().st_size > 5 * 1024 * 1024:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for target_id, patterns in terms.items():
            if relative == config.path.relative_to(config.repository_root).as_posix():
                continue
            if any(pattern in content for pattern in patterns):
                references[target_id].append(relative)
    return references


def _file_size(path: Path) -> int:
    return len(os.readlink(path).encode("utf-8")) if path.is_symlink() else path.stat().st_size


def _head_blob_summary(root: Path) -> dict[str, Any]:
    """Report large blobs reachable from HEAD without changing repository state."""

    objects = subprocess.run(
        ["git", "rev-list", "--objects", "HEAD"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if objects.returncode != 0:
        return {
            "head_available": False,
            "blob_count": 0,
            "largest_blob_bytes": 0,
            "over_github_100mb_count": 0,
            "over_github_100mb_paths": [],
        }
    object_paths: dict[str, str] = {}
    object_ids: list[str] = []
    for raw_line in objects.stdout.decode(
        "utf-8", errors="surrogateescape"
    ).splitlines():
        object_id, separator, path = raw_line.partition(" ")
        object_ids.append(object_id)
        if separator:
            object_paths.setdefault(object_id, path)
    inspected = subprocess.run(
        [
            "git",
            "cat-file",
            "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        ],
        cwd=root,
        input=("\n".join(object_ids) + "\n").encode("ascii"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if inspected.returncode != 0:
        message = inspected.stderr.decode("utf-8", errors="replace").strip()
        raise HygieneConfigError(f"git cat-file history inspection failed: {message}")
    blob_count = 0
    largest_blob_bytes = 0
    oversized: list[dict[str, Any]] = []
    for raw_line in inspected.stdout.decode("ascii").splitlines():
        object_id, object_type, raw_size = raw_line.split(" ", 2)
        if object_type != "blob":
            continue
        size = int(raw_size)
        blob_count += 1
        largest_blob_bytes = max(largest_blob_bytes, size)
        if size > 100 * 1024 * 1024:
            oversized.append(
                {
                    "object_id": object_id,
                    "size_bytes": size,
                    "path": object_paths.get(object_id, ""),
                }
            )
    oversized.sort(key=lambda item: (-int(item["size_bytes"]), str(item["path"])))
    return {
        "head_available": True,
        "blob_count": blob_count,
        "largest_blob_bytes": largest_blob_bytes,
        "over_github_100mb_count": len(oversized),
        "over_github_100mb_paths": oversized,
    }


def scan_repository(config: HygieneConfig) -> InventoryResult:
    """Scan without mutating any source file and write three bounded artifacts."""

    files = _iter_files(config)
    relative_paths = [
        path.relative_to(config.repository_root).as_posix() for path in files
    ]
    tracked = _nul_paths(_run_git(config.repository_root, ["ls-files", "-z"]))
    untracked_candidates = [path for path in relative_paths if path not in tracked]
    ignored = _nul_paths(
        _run_git(
            config.repository_root,
            ["check-ignore", "--stdin", "-z"],
            stdin=b"\0".join(
                path.encode("utf-8", errors="surrogateescape")
                for path in untracked_candidates
            )
            + (b"\0" if untracked_candidates else b""),
        )
    )
    scoped_files: list[tuple[Path, str, HygieneTarget | None]] = []
    omitted_untracked_file_count = 0
    omitted_untracked_bytes = 0
    for path, relative in zip(files, relative_paths, strict=True):
        target = _target_for(relative, config.targets)
        git_state = (
            "tracked"
            if relative in tracked
            else "ignored"
            if relative in ignored
            else "untracked"
        )
        if git_state == "untracked" and target is None:
            omitted_untracked_file_count += 1
            omitted_untracked_bytes += _file_size(path)
            continue
        scoped_files.append((path, relative, target))

    references = _reference_files(
        config=config,
        files=[path for path, _, _ in scoped_files],
        tracked=tracked,
    )
    rows: list[dict[str, Any]] = []
    hash_groups: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for path, relative, target in scoped_files:
        size = _file_size(path)
        digest = _sha256(path)
        git_state = (
            "tracked" if relative in tracked else "ignored" if relative in ignored else "untracked"
        )
        row = {
            "path": relative,
            "size_bytes": size,
            "sha256": digest,
            "extension": path.suffix.lower(),
            "git_state": git_state,
            "target_id": target.target_id if target else "",
            "artifact_class": (
                target.artifact_class
                if target
                else f"{git_state}_other"
            ),
            "duplicate_group_id": "",
            "reference_count": (
                len(references[target.target_id]) if target else ""
            ),
        }
        rows.append(row)
        if size >= config.duplicate_min_bytes:
            hash_groups.setdefault((size, digest), []).append(row)

    duplicate_rows: list[dict[str, Any]] = []
    duplicate_groups = [
        (key, members)
        for key, members in hash_groups.items()
        if len(members) > 1
    ]
    duplicate_groups.sort(key=lambda item: (-item[0][0], item[0][1]))
    for index, ((size, digest), members) in enumerate(duplicate_groups, start=1):
        group_id = f"DUP-{index:04d}"
        redundant_bytes = size * (len(members) - 1)
        for member in sorted(members, key=lambda item: str(item["path"])):
            member["duplicate_group_id"] = group_id
            duplicate_rows.append(
                {
                    "duplicate_group_id": group_id,
                    "sha256": digest,
                    "size_bytes": size,
                    "member_count": len(members),
                    "redundant_bytes": redundant_bytes,
                    "path": member["path"],
                    "git_state": member["git_state"],
                    "target_id": member["target_id"],
                }
            )

    inventory_path = config.output_root / "repository_inventory.csv"
    duplicates_path = config.output_root / "duplicate_groups.csv"
    manifest_path = config.output_root / "retention_manifest.json"
    _write_csv(inventory_path, INVENTORY_FIELDS, rows)
    _write_csv(duplicates_path, DUPLICATE_FIELDS, duplicate_rows)

    target_summaries: list[dict[str, Any]] = []
    for target in config.targets:
        members = [row for row in rows if row["target_id"] == target.target_id]
        states = {
            state: sum(1 for row in members if row["git_state"] == state)
            for state in ("tracked", "ignored", "untracked")
        }
        state_bytes = {
            state: sum(
                int(row["size_bytes"])
                for row in members
                if row["git_state"] == state
            )
            for state in ("tracked", "ignored", "untracked")
        }
        duplicate_group_ids = {
            str(row["duplicate_group_id"])
            for row in members
            if row["duplicate_group_id"]
        }
        duplicate_bytes = sum(
            int(row["size_bytes"])
            for row in members
            if row["duplicate_group_id"]
        )
        target_summaries.append(
            {
                "target_id": target.target_id,
                "path_globs": list(target.path_globs),
                "artifact_class": target.artifact_class,
                "proposed_action": target.proposed_action,
                "approval_state": target.approval_state,
                "file_count": len(members),
                "total_bytes": sum(int(row["size_bytes"]) for row in members),
                "git_state_file_counts": states,
                "git_state_bytes": state_bytes,
                "duplicate_group_count": len(duplicate_group_ids),
                "bytes_in_duplicate_groups": duplicate_bytes,
                "potential_git_reclaim_bytes": (
                    state_bytes["tracked"]
                    if target.proposed_action in {
                        "externalize",
                        "archive",
                        "delete",
                    }
                    else 0
                ),
                "potential_disk_reclaim_bytes": (
                    sum(int(row["size_bytes"]) for row in members)
                    if target.proposed_action == "delete"
                    else 0
                ),
                "reference_count": len(references[target.target_id]),
                "reference_paths": references[target.target_id],
                "reference_scope": "tracked UTF-8 text files up to 5 MiB",
                "locator_required": target.locator_required,
                "restore_test_required": target.restore_test_required,
                "rationale": target.rationale,
            }
        )

    tracked_rows = [row for row in rows if row["git_state"] == "tracked"]
    tracked_over_github_limit = [
        row for row in tracked_rows if int(row["size_bytes"]) > 100 * 1024 * 1024
    ]
    manifest = {
        "schema_version": "1.0",
        "config_id": config.config_id,
        "config_path": config.path.relative_to(config.repository_root).as_posix(),
        "config_sha256": _sha256(config.path),
        "mode": "non_destructive_inventory",
        "source_mutation_count": 0,
        "scan": {
            "scan_roots": [
                path.relative_to(config.repository_root).as_posix()
                for path in config.scan_roots
            ],
            "excluded_globs": list(config.exclude_globs),
            "file_count": len(rows),
            "total_bytes": sum(int(row["size_bytes"]) for row in rows),
            "tracked_file_count": len(tracked_rows),
            "tracked_bytes": sum(int(row["size_bytes"]) for row in tracked_rows),
            "ignored_file_count": sum(row["git_state"] == "ignored" for row in rows),
            "untracked_file_count": sum(
                row["git_state"] == "untracked" for row in rows
            ),
            "omitted_untracked_file_count": omitted_untracked_file_count,
            "omitted_untracked_bytes": omitted_untracked_bytes,
            "tracked_over_github_100mb_count": len(tracked_over_github_limit),
            "tracked_over_github_100mb_paths": [
                row["path"] for row in tracked_over_github_limit
            ],
            "duplicate_min_bytes": config.duplicate_min_bytes,
            "duplicate_group_count": len(duplicate_groups),
            "duplicate_redundant_bytes": sum(
                key[0] * (len(members) - 1)
                for key, members in duplicate_groups
            ),
            "reachable_head_blobs": _head_blob_summary(config.repository_root),
        },
        "targets": target_summaries,
        "outputs": {
            "repository_inventory": {
                "path": inventory_path.relative_to(config.repository_root).as_posix(),
                "sha256": _sha256(inventory_path),
                "row_count": len(rows),
            },
            "duplicate_groups": {
                "path": duplicates_path.relative_to(config.repository_root).as_posix(),
                "sha256": _sha256(duplicates_path),
                "row_count": len(duplicate_rows),
            },
        },
        "safety": {
            "destructive_actions_executed": [],
            "pending_target_specific_approval": sorted(
                target.target_id
                for target in config.targets
                if target.approval_state == "pending_project_lead"
            ),
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_manifest = manifest_path.with_suffix(f"{manifest_path.suffix}.tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary_manifest.replace(manifest_path)
    return InventoryResult(
        inventory_path=inventory_path,
        duplicates_path=duplicates_path,
        manifest_path=manifest_path,
        file_count=len(rows),
        total_bytes=int(manifest["scan"]["total_bytes"]),
        tracked_file_count=len(tracked_rows),
        tracked_bytes=int(manifest["scan"]["tracked_bytes"]),
        duplicate_group_count=len(duplicate_groups),
    )

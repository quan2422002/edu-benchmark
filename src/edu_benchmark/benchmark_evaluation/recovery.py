"""Build and merge fail-closed recovery batches for truncated targets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class TargetRecoveryError(RuntimeError):
    """Raised when target recovery provenance or integrity is invalid."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TargetRecoveryError(
                f"{path}:{number}: invalid JSON"
            ) from exc
        if not isinstance(row, dict):
            raise TargetRecoveryError(f"{path}:{number}: object required")
        rows.append(row)
    return rows


def index_rows(
    rows: list[dict[str, Any]], source: Path
) -> dict[str, dict[str, Any]]:
    result = {}
    for row in rows:
        candidate_id = str(
            row.get("benchmark_candidate_id") or ""
        ).strip()
        if not candidate_id or candidate_id in result:
            raise TargetRecoveryError(
                f"{source}: missing or duplicate benchmark_candidate_id"
            )
        result[candidate_id] = row
    return result


def candidate_ids_sha256(candidate_ids: list[str]) -> str:
    """Hash a sorted candidate-ID set with the repository convention."""

    return hashlib.sha256(
        "\n".join(sorted(candidate_ids)).encode("utf-8")
    ).hexdigest()


def is_completed_response(row: dict[str, Any]) -> bool:
    """Return whether one target response is safe to publish."""

    return (
        row.get("response_status") == "completed"
        and row.get("finish_reason") in {"STOP", "END_TURN"}
        and not row.get("completion_issue")
    )


def build_recovery_manifest(
    *,
    source_output: Path,
    source_manifest: Path,
    completion_issue: str = "output_truncated",
    recovery_max_output_tokens: int = 1536,
) -> dict[str, Any]:
    """Lock exactly the source records carrying one completion issue."""

    if recovery_max_output_tokens <= 0:
        raise TargetRecoveryError("recovery token cap must be positive")
    source_rows = read_jsonl(source_output)
    source_by_id = index_rows(source_rows, source_output)
    source_run = json.loads(source_manifest.read_text(encoding="utf-8"))
    ids = sorted(
        candidate_id
        for candidate_id, row in source_by_id.items()
        if row.get("completion_issue") == completion_issue
    )
    if not ids:
        raise TargetRecoveryError(
            "source contains no matching recovery records"
        )
    manifest_ids = sorted(
        source_run.get("needs_review_candidate_ids") or []
    )
    if ids != manifest_ids:
        raise TargetRecoveryError(
            "source manifest review IDs do not match source JSONL issues"
        )
    id_hash = candidate_ids_sha256(ids)
    return {
        "record_type": "target_response_recovery_manifest",
        "manifest_version": "target_truncation_recovery_v1",
        "status": "locked",
        "candidate_count": len(ids),
        "candidate_ids": ids,
        "candidate_ids_sha256": id_hash,
        "completion_issue": completion_issue,
        "source_run_id": source_run.get("run_id"),
        "source_output": str(source_output),
        "source_manifest": str(source_manifest),
        "source_output_sha256": sha256(source_output),
        "source_manifest_sha256": sha256(source_manifest),
        "source_max_output_tokens": 1024,
        "recovery_max_output_tokens": recovery_max_output_tokens,
        "merge_policy": (
            "replace exact truncated IDs only after every recovery record "
            "finishes successfully; otherwise keep source bundle unchanged"
        ),
    }


def build_followup_recovery_manifest(
    *,
    recovery_output: Path,
    recovery_manifest: Path,
    recovery_run_manifest: Path,
    followup_max_output_tokens: int = 2048,
) -> dict[str, Any]:
    """Lock only incomplete rows from a validated first recovery pass."""

    if followup_max_output_tokens <= 0:
        raise TargetRecoveryError("follow-up token cap must be positive")
    contract = json.loads(recovery_manifest.read_text(encoding="utf-8"))
    if contract.get("manifest_version") != "target_truncation_recovery_v1":
        raise TargetRecoveryError("unsupported parent recovery manifest")
    rows = read_jsonl(recovery_output)
    by_id = index_rows(rows, recovery_output)
    expected_ids = set(contract.get("candidate_ids") or [])
    if set(by_id) != expected_ids:
        raise TargetRecoveryError(
            "parent recovery output candidate set mismatch"
        )
    run = json.loads(recovery_run_manifest.read_text(encoding="utf-8"))
    if run.get("status") != "completed_with_review":
        raise TargetRecoveryError(
            "parent recovery run must be completed_with_review"
        )
    incomplete_ids = sorted(
        candidate_id
        for candidate_id, row in by_id.items()
        if not is_completed_response(row)
    )
    if not incomplete_ids:
        raise TargetRecoveryError(
            "parent recovery contains no incomplete responses"
        )
    manifest_review_ids = sorted(
        run.get("needs_review_candidate_ids") or []
    )
    if incomplete_ids != manifest_review_ids:
        raise TargetRecoveryError(
            "parent recovery review IDs do not match its JSONL"
        )
    completed_count = len(rows) - len(incomplete_ids)
    return {
        "record_type": "target_response_followup_recovery_manifest",
        "manifest_version": "target_followup_recovery_v1",
        "status": "locked",
        "candidate_count": len(incomplete_ids),
        "candidate_ids": incomplete_ids,
        "candidate_ids_sha256": candidate_ids_sha256(incomplete_ids),
        "parent_candidate_count": len(expected_ids),
        "parent_completed_count": completed_count,
        "parent_recovery_output": str(recovery_output),
        "parent_recovery_manifest": str(recovery_manifest),
        "parent_recovery_run_manifest": str(recovery_run_manifest),
        "parent_recovery_output_sha256": sha256(recovery_output),
        "parent_recovery_manifest_sha256": sha256(recovery_manifest),
        "parent_recovery_run_manifest_sha256": sha256(
            recovery_run_manifest
        ),
        "parent_max_output_tokens": contract[
            "recovery_max_output_tokens"
        ],
        "followup_max_output_tokens": followup_max_output_tokens,
        "merge_policy": (
            "reuse every completed parent recovery record; replace only "
            "the locked incomplete IDs after all follow-up records finish"
        ),
    }


def finalize_followup_recovery_bundle(
    *,
    recovery_output: Path,
    recovery_manifest: Path,
    recovery_run_manifest: Path,
    followup_output: Path,
    followup_manifest: Path,
    followup_run_manifest: Path,
) -> dict[str, Any]:
    """Replace incomplete first-pass rows with one complete follow-up pass."""

    contract = json.loads(followup_manifest.read_text(encoding="utf-8"))
    if contract.get("manifest_version") != "target_followup_recovery_v1":
        raise TargetRecoveryError("unsupported follow-up recovery manifest")
    locked_inputs = (
        ("parent_recovery_output_sha256", recovery_output),
        ("parent_recovery_manifest_sha256", recovery_manifest),
        ("parent_recovery_run_manifest_sha256", recovery_run_manifest),
    )
    for field, path in locked_inputs:
        if contract.get(field) != sha256(path):
            raise TargetRecoveryError(
                f"{path} changed after follow-up recovery lock"
            )

    parent_contract = json.loads(
        recovery_manifest.read_text(encoding="utf-8")
    )
    parent_rows = read_jsonl(recovery_output)
    parent_by_id = index_rows(parent_rows, recovery_output)
    expected_parent_ids = set(parent_contract.get("candidate_ids") or [])
    if set(parent_by_id) != expected_parent_ids:
        raise TargetRecoveryError(
            "parent recovery output candidate set mismatch"
        )

    followup_rows = read_jsonl(followup_output)
    followup_by_id = index_rows(followup_rows, followup_output)
    expected_followup_ids = set(contract.get("candidate_ids") or [])
    if set(followup_by_id) != expected_followup_ids:
        raise TargetRecoveryError(
            "follow-up recovery output candidate set mismatch"
        )
    incomplete_followup = sorted(
        candidate_id
        for candidate_id, row in followup_by_id.items()
        if not is_completed_response(row)
    )
    if incomplete_followup:
        raise TargetRecoveryError(
            "follow-up recovery remains incomplete for "
            f"{len(incomplete_followup)} candidates"
        )

    parent_incomplete = {
        candidate_id
        for candidate_id, row in parent_by_id.items()
        if not is_completed_response(row)
    }
    if parent_incomplete != expected_followup_ids:
        raise TargetRecoveryError(
            "follow-up IDs do not match incomplete parent records"
        )
    for candidate_id in expected_followup_ids:
        if not _same_request(
            parent_by_id[candidate_id],
            followup_by_id[candidate_id],
        ):
            raise TargetRecoveryError(
                f"follow-up request provenance mismatch {candidate_id}"
            )

    followup_run = json.loads(
        followup_run_manifest.read_text(encoding="utf-8")
    )
    if followup_run.get("status") != "completed":
        raise TargetRecoveryError(
            "follow-up run manifest is not completed"
        )

    combined = [
        followup_by_id.get(row["benchmark_candidate_id"], row)
        for row in parent_rows
    ]
    combined_by_id = index_rows(combined, recovery_output)
    if (
        len(combined) != len(parent_rows)
        or set(combined_by_id) != expected_parent_ids
        or any(not is_completed_response(row) for row in combined)
    ):
        raise TargetRecoveryError(
            "finalized recovery bundle failed completeness validation"
        )

    parent_run = json.loads(
        recovery_run_manifest.read_text(encoding="utf-8")
    )
    parent_cost = float(parent_run.get("new_estimated_cost_usd") or 0)
    followup_cost = float(
        followup_run.get("new_estimated_cost_usd") or 0
    )
    recovery_passes = [
        {
            "run_id": parent_run.get("run_id"),
            "candidate_count": len(parent_rows),
            "completed_candidate_count": (
                len(parent_rows) - len(expected_followup_ids)
            ),
            "incomplete_candidate_count": len(expected_followup_ids),
            "max_output_tokens": contract["parent_max_output_tokens"],
            "estimated_cost_usd": parent_cost,
            "output_sha256": contract[
                "parent_recovery_output_sha256"
            ],
            "run_manifest_sha256": contract[
                "parent_recovery_run_manifest_sha256"
            ],
        },
        {
            "run_id": followup_run.get("run_id"),
            "candidate_count": len(followup_rows),
            "completed_candidate_count": len(followup_rows),
            "incomplete_candidate_count": 0,
            "max_output_tokens": contract[
                "followup_max_output_tokens"
            ],
            "estimated_cost_usd": followup_cost,
            "output_sha256": sha256(followup_output),
            "run_manifest_sha256": sha256(followup_run_manifest),
        },
    ]

    combined_manifest = dict(parent_run)
    combined_manifest.update(
        {
            "status": "completed",
            "candidate_count": len(combined),
            "candidate_manifest": str(recovery_manifest),
            "candidate_manifest_sha256": sha256(recovery_manifest),
            "output_file": str(recovery_output),
            "recorded_candidate_ids": sorted(combined_by_id),
            "completed_candidate_ids": sorted(combined_by_id),
            "needs_review_candidate_ids": [],
            "truncated_candidate_ids": [],
            "failed_candidate_ids": [],
            "errors": {},
            "error_attempt_count": int(
                parent_run.get("error_attempt_count") or 0
            )
            + int(followup_run.get("error_attempt_count") or 0),
            "new_estimated_cost_usd": round(
                parent_cost + followup_cost, 8
            ),
            "recovery_passes": recovery_passes,
            "integrity": {
                "validated": True,
                "record_count": len(combined),
                "completed_record_count": len(combined),
                "needs_review_record_count": 0,
            },
        }
    )

    output_temporary = recovery_output.with_name(
        f".{recovery_output.name}.followup.tmp"
    )
    with output_temporary.open("w", encoding="utf-8") as handle:
        for row in combined:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    manifest_temporary = recovery_run_manifest.with_name(
        f".{recovery_run_manifest.name}.followup.tmp"
    )
    manifest_temporary.write_text(
        json.dumps(
            combined_manifest,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    output_temporary.replace(recovery_output)
    manifest_temporary.replace(recovery_run_manifest)
    return {
        "status": "finalized",
        "reused_candidate_count": (
            len(combined) - len(expected_followup_ids)
        ),
        "replaced_candidate_count": len(expected_followup_ids),
        "completed_candidate_count": len(combined),
        "recovery_estimated_cost_usd": round(
            parent_cost + followup_cost, 8
        ),
    }


def _same_request(
    source: dict[str, Any], recovery: dict[str, Any]
) -> bool:
    fields = (
        "benchmark_candidate_id",
        "provider",
        "model_id",
        "input_hash",
        "system_instruction_hash",
        "messages_hash",
        "instruction_bundle_version",
        "instruction_bundle_sha256",
        "required_principle_ids",
    )
    return all(source.get(field) == recovery.get(field) for field in fields)


def merge_recovery_bundle(
    *,
    source_output: Path,
    source_manifest: Path,
    recovery_output: Path,
    recovery_manifest: Path,
    recovery_run_manifest: Path,
) -> dict[str, Any]:
    """Atomically replace truncated records after exhaustive validation."""

    contract = json.loads(recovery_manifest.read_text(encoding="utf-8"))
    if contract.get("manifest_version") != "target_truncation_recovery_v1":
        raise TargetRecoveryError("unsupported recovery manifest")
    if contract.get("source_output_sha256") != sha256(source_output):
        raise TargetRecoveryError("source output changed after recovery lock")
    if contract.get("source_manifest_sha256") != sha256(source_manifest):
        raise TargetRecoveryError("source manifest changed after recovery lock")
    source_rows = read_jsonl(source_output)
    recovery_rows = read_jsonl(recovery_output)
    source_by_id = index_rows(source_rows, source_output)
    recovery_by_id = index_rows(recovery_rows, recovery_output)
    expected_ids = list(contract["candidate_ids"])
    if set(recovery_by_id) != set(expected_ids):
        raise TargetRecoveryError("recovery output candidate set mismatch")
    incomplete = sorted(
        candidate_id
        for candidate_id, row in recovery_by_id.items()
        if not is_completed_response(row)
    )
    if incomplete:
        raise TargetRecoveryError(
            f"recovery remains incomplete for {len(incomplete)} candidates"
        )
    for candidate_id in expected_ids:
        source = source_by_id.get(candidate_id)
        recovery = recovery_by_id[candidate_id]
        if (
            source is None
            or source.get("completion_issue")
            != contract["completion_issue"]
        ):
            raise TargetRecoveryError(
                f"invalid source recovery row {candidate_id}"
            )
        if not _same_request(source, recovery):
            raise TargetRecoveryError(
                f"request provenance mismatch {candidate_id}"
            )
        recovery["pipeline_stage"] = source["pipeline_stage"]
        recovery["run_id"] = source["run_id"]
    merged = [
        recovery_by_id.get(row["benchmark_candidate_id"], row)
        for row in source_rows
    ]
    merged_by_id = index_rows(merged, source_output)
    if (
        len(merged) != len(source_rows)
        or len(merged_by_id) != len(source_by_id)
    ):
        raise TargetRecoveryError("merged record count changed")
    if any(row.get("response_status") != "completed" for row in merged):
        raise TargetRecoveryError(
            "merged bundle still contains incomplete records"
        )
    recovery_run = json.loads(
        recovery_run_manifest.read_text(encoding="utf-8")
    )
    if recovery_run.get("status") != "completed":
        raise TargetRecoveryError(
            "recovery run manifest is not completed"
        )
    temporary = source_output.with_name(
        f".{source_output.name}.recovery.tmp"
    )
    with temporary.open("w", encoding="utf-8") as handle:
        for row in merged:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    old_output_hash = sha256(source_output)
    new_output_hash = sha256(temporary)
    source_run = json.loads(source_manifest.read_text(encoding="utf-8"))
    original_cost = float(source_run.get("new_estimated_cost_usd") or 0)
    recovery_cost = float(
        recovery_run.get("new_estimated_cost_usd") or 0
    )
    history = list(source_run.get("recovery_history") or [])
    history.append(
        {
            "recovery_manifest_sha256": sha256(recovery_manifest),
            "recovery_run_manifest_sha256": sha256(
                recovery_run_manifest
            ),
            "recovery_run_id": recovery_run.get("run_id"),
            "recovery_candidate_ids_sha256": contract[
                "candidate_ids_sha256"
            ],
            "replaced_candidate_count": len(expected_ids),
            "source_output_sha256_before_merge": old_output_hash,
            "source_output_sha256_after_merge": new_output_hash,
            "source_max_output_tokens": contract[
                "source_max_output_tokens"
            ],
            "recovery_max_output_tokens": contract[
                "recovery_max_output_tokens"
            ],
            "recovery_estimated_cost_usd": recovery_cost,
            "recovery_passes": recovery_run.get("recovery_passes") or [],
        }
    )
    source_run.update(
        {
            "status": "completed",
            "recorded_candidate_ids": sorted(merged_by_id),
            "completed_candidate_ids": sorted(merged_by_id),
            "needs_review_candidate_ids": [],
            "truncated_candidate_ids": [],
            "failed_candidate_ids": [],
            "errors": {},
            "recovery_history": history,
            "original_estimated_cost_usd": original_cost,
            "recovery_estimated_cost_usd": recovery_cost,
            "cumulative_estimated_cost_usd": round(
                original_cost + recovery_cost, 8
            ),
            "integrity": {
                "validated": True,
                "record_count": len(merged),
                "completed_record_count": len(merged),
                "needs_review_record_count": 0,
            },
        }
    )
    manifest_temporary = source_manifest.with_name(
        f".{source_manifest.name}.recovery.tmp"
    )
    manifest_temporary.write_text(
        json.dumps(source_run, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(source_output)
    manifest_temporary.replace(source_manifest)
    return {
        "status": "merged",
        "replaced_candidate_count": len(expected_ids),
        "record_count": len(merged),
        "source_output_sha256": new_output_hash,
        "cumulative_estimated_cost_usd": round(
            original_cost + recovery_cost, 8
        ),
    }

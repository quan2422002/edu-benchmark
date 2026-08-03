import json
from pathlib import Path

import pytest

from src.edu_benchmark.benchmark_evaluation.recovery import (
    TargetRecoveryError,
    build_followup_recovery_manifest,
    build_recovery_manifest,
    finalize_followup_recovery_bundle,
    merge_recovery_bundle,
    read_jsonl,
)


def write_jsonl(path: Path, rows):
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def row(candidate_id, *, completed):
    return {
        "benchmark_candidate_id": candidate_id,
        "provider": "gemini",
        "model_id": "gemini-3.5-flash",
        "input_hash": "a" * 64,
        "system_instruction_hash": "b" * 64,
        "messages_hash": "c" * 64,
        "instruction_bundle_version": "v2",
        "instruction_bundle_sha256": "d" * 64,
        "required_principle_ids": ["PRINCIPLE-EXPLANATION"],
        "pipeline_stage": "benchmark_evaluation_target_full",
        "run_id": "target_gemini35",
        "response_status": "completed" if completed else "needs_review",
        "finish_reason": "STOP" if completed else "MAX_TOKENS",
        "completion_issue": None if completed else "output_truncated",
        "response_text": "complete" if completed else "cut",
    }


def fixture(tmp_path):
    source_output = tmp_path / "source.jsonl"
    source_manifest = tmp_path / "source_manifest.json"
    rows = [
        row("BC-1", completed=True),
        row("BC-2", completed=False),
        row("BC-3", completed=False),
    ]
    write_jsonl(source_output, rows)
    source_manifest.write_text(
        json.dumps({
            "run_id": "target_gemini35",
            "status": "completed_with_review",
            "needs_review_candidate_ids": ["BC-2", "BC-3"],
            "new_estimated_cost_usd": 1.25,
        }),
        encoding="utf-8",
    )
    return source_output, source_manifest, rows


def test_recovery_manifest_locks_only_truncated_rows(tmp_path):
    source_output, source_manifest, _ = fixture(tmp_path)
    manifest = build_recovery_manifest(
        source_output=source_output,
        source_manifest=source_manifest,
    )
    assert manifest["candidate_ids"] == ["BC-2", "BC-3"]
    assert manifest["candidate_count"] == 2
    assert manifest["recovery_max_output_tokens"] == 1536


def test_merge_replaces_exact_rows_only_after_complete_recovery(tmp_path):
    source_output, source_manifest, source_rows = fixture(tmp_path)
    contract = build_recovery_manifest(
        source_output=source_output,
        source_manifest=source_manifest,
    )
    recovery_manifest = tmp_path / "recovery_manifest.json"
    recovery_manifest.write_text(json.dumps(contract), encoding="utf-8")
    recovery_output = tmp_path / "recovery.jsonl"
    recovered = []
    for source in source_rows[1:]:
        value = dict(source)
        value.update({
            "run_id": "recovery_max1536_v1",
            "response_status": "completed",
            "finish_reason": "STOP",
            "completion_issue": None,
            "response_text": "recovered complete",
        })
        recovered.append(value)
    write_jsonl(recovery_output, recovered)
    recovery_run_manifest = tmp_path / "recovery_run_manifest.json"
    recovery_run_manifest.write_text(
        json.dumps({"status": "completed", "new_estimated_cost_usd": 0.5}),
        encoding="utf-8",
    )
    result = merge_recovery_bundle(
        source_output=source_output,
        source_manifest=source_manifest,
        recovery_output=recovery_output,
        recovery_manifest=recovery_manifest,
        recovery_run_manifest=recovery_run_manifest,
    )
    assert result["replaced_candidate_count"] == 2
    merged = [json.loads(line) for line in source_output.read_text().splitlines()]
    assert [value["response_text"] for value in merged] == [
        "complete", "recovered complete", "recovered complete"
    ]
    assert all(value["run_id"] == "target_gemini35" for value in merged)
    final_manifest = json.loads(source_manifest.read_text())
    assert final_manifest["status"] == "completed"
    assert final_manifest["cumulative_estimated_cost_usd"] == 1.75
    assert final_manifest["integrity"]["completed_record_count"] == 3


def test_merge_keeps_source_unchanged_if_recovery_is_truncated(tmp_path):
    source_output, source_manifest, source_rows = fixture(tmp_path)
    original_output = source_output.read_bytes()
    original_manifest = source_manifest.read_bytes()
    contract = build_recovery_manifest(
        source_output=source_output,
        source_manifest=source_manifest,
    )
    recovery_manifest = tmp_path / "recovery_manifest.json"
    recovery_manifest.write_text(json.dumps(contract), encoding="utf-8")
    recovery_output = tmp_path / "recovery.jsonl"
    write_jsonl(recovery_output, source_rows[1:])
    recovery_run_manifest = tmp_path / "recovery_run_manifest.json"
    recovery_run_manifest.write_text(
        json.dumps({"status": "completed_with_review"}),
        encoding="utf-8",
    )
    with pytest.raises(TargetRecoveryError, match="remains incomplete"):
        merge_recovery_bundle(
            source_output=source_output,
            source_manifest=source_manifest,
            recovery_output=recovery_output,
            recovery_manifest=recovery_manifest,
            recovery_run_manifest=recovery_run_manifest,
        )
    assert source_output.read_bytes() == original_output
    assert source_manifest.read_bytes() == original_manifest


def followup_fixture(tmp_path):
    recovery_output = tmp_path / "recovery.jsonl"
    recovery_manifest = tmp_path / "recovery_manifest.json"
    recovery_run_manifest = tmp_path / "recovery_run_manifest.json"
    rows = [
        row("BC-2", completed=True),
        row("BC-3", completed=False),
    ]
    write_jsonl(recovery_output, rows)
    recovery_manifest.write_text(
        json.dumps({
            "manifest_version": "target_truncation_recovery_v1",
            "candidate_ids": ["BC-2", "BC-3"],
            "recovery_max_output_tokens": 1536,
        }),
        encoding="utf-8",
    )
    recovery_run_manifest.write_text(
        json.dumps({
            "run_id": "recovery_1536",
            "status": "completed_with_review",
            "needs_review_candidate_ids": ["BC-3"],
            "new_estimated_cost_usd": 0.5,
            "error_attempt_count": 1,
        }),
        encoding="utf-8",
    )
    return (
        recovery_output,
        recovery_manifest,
        recovery_run_manifest,
    )


def test_followup_recovery_reuses_completed_parent_rows(tmp_path):
    (
        recovery_output,
        recovery_manifest,
        recovery_run_manifest,
    ) = followup_fixture(tmp_path)
    contract = build_followup_recovery_manifest(
        recovery_output=recovery_output,
        recovery_manifest=recovery_manifest,
        recovery_run_manifest=recovery_run_manifest,
    )
    assert contract["candidate_ids"] == ["BC-3"]
    assert contract["parent_completed_count"] == 1
    assert contract["followup_max_output_tokens"] == 2048

    followup_manifest = tmp_path / "followup_manifest.json"
    followup_manifest.write_text(json.dumps(contract), encoding="utf-8")
    followup_output = tmp_path / "followup.jsonl"
    recovered = row("BC-3", completed=True)
    recovered["response_text"] = "complete at 2048"
    write_jsonl(followup_output, [recovered])
    followup_run_manifest = tmp_path / "followup_run_manifest.json"
    followup_run_manifest.write_text(
        json.dumps({
            "run_id": "followup_2048",
            "status": "completed",
            "new_estimated_cost_usd": 0.25,
            "error_attempt_count": 0,
        }),
        encoding="utf-8",
    )

    result = finalize_followup_recovery_bundle(
        recovery_output=recovery_output,
        recovery_manifest=recovery_manifest,
        recovery_run_manifest=recovery_run_manifest,
        followup_output=followup_output,
        followup_manifest=followup_manifest,
        followup_run_manifest=followup_run_manifest,
    )
    assert result["reused_candidate_count"] == 1
    assert result["replaced_candidate_count"] == 1
    finalized = [
        json.loads(line) for line in recovery_output.read_text().splitlines()
    ]
    assert [value["response_text"] for value in finalized] == [
        "complete", "complete at 2048"
    ]
    run = json.loads(recovery_run_manifest.read_text())
    assert run["status"] == "completed"
    assert run["new_estimated_cost_usd"] == 0.75
    assert run["integrity"]["completed_record_count"] == 2
    assert [value["max_output_tokens"] for value in run["recovery_passes"]] == [
        1536, 2048
    ]


def test_followup_recovery_keeps_parent_if_retry_is_incomplete(tmp_path):
    (
        recovery_output,
        recovery_manifest,
        recovery_run_manifest,
    ) = followup_fixture(tmp_path)
    original_output = recovery_output.read_bytes()
    original_run_manifest = recovery_run_manifest.read_bytes()
    contract = build_followup_recovery_manifest(
        recovery_output=recovery_output,
        recovery_manifest=recovery_manifest,
        recovery_run_manifest=recovery_run_manifest,
    )
    followup_manifest = tmp_path / "followup_manifest.json"
    followup_manifest.write_text(json.dumps(contract), encoding="utf-8")
    followup_output = tmp_path / "followup.jsonl"
    write_jsonl(followup_output, [row("BC-3", completed=False)])
    followup_run_manifest = tmp_path / "followup_run_manifest.json"
    followup_run_manifest.write_text(
        json.dumps({"status": "completed_with_review"}),
        encoding="utf-8",
    )
    with pytest.raises(TargetRecoveryError, match="remains incomplete"):
        finalize_followup_recovery_bundle(
            recovery_output=recovery_output,
            recovery_manifest=recovery_manifest,
            recovery_run_manifest=recovery_run_manifest,
            followup_output=followup_output,
            followup_manifest=followup_manifest,
            followup_run_manifest=followup_run_manifest,
        )
    assert recovery_output.read_bytes() == original_output
    assert recovery_run_manifest.read_bytes() == original_run_manifest


def test_published_recovery_source_is_complete_after_two_pass_merge():
    root = Path(__file__).resolve().parents[2]
    source = (
        root
        / "experiments/20260727_170150/outputs/benchmark_evaluation/"
        "full_1400_v1/target_gemini35"
    )
    rows = read_jsonl(source / "run_responses.jsonl")
    manifest = json.loads((source / "run_manifest.json").read_text())
    assert len(rows) == 1400
    assert len({row["benchmark_candidate_id"] for row in rows}) == 1400
    assert all(row["response_status"] == "completed" for row in rows)
    assert all(row["finish_reason"] in {"STOP", "END_TURN"} for row in rows)
    assert manifest["status"] == "completed"
    assert manifest["integrity"]["completed_record_count"] == 1400
    history = manifest["recovery_history"]
    assert len(history) == 1
    assert history[0]["replaced_candidate_count"] == 436
    passes = history[0]["recovery_passes"]
    assert [value["candidate_count"] for value in passes] == [436, 19]
    assert [value["max_output_tokens"] for value in passes] == [1536, 2048]

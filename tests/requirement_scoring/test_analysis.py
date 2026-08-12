from __future__ import annotations

import csv
import json
from pathlib import Path

from edu_benchmark.requirement_scoring.analysis import (
    PAPER_REGISTRY_HEADER,
    REVIEW_HEADER,
    TRACE_HEADER,
    analyze_full_run,
    evidence_reference_is_traceable,
)
from edu_benchmark.requirement_scoring.core import (
    GROUNDING_HEADER,
    PRINCIPLE_IDS,
    GenerationConfig,
    build_grounding_payload,
    build_request_hash,
    serialize_user_prompt,
    sha256_file,
)


def _grounding_row(index: int) -> dict:
    family = index // 2
    target_turn = 2 if index % 2 == 0 else 4
    history = (
        []
        if target_turn == 2
        else [
            {"turn_index": 2, "role": "tutor", "content": "Em thử suy nghĩ nhé."},
            {"turn_index": 3, "role": "student", "content": "Em chọn đáp án A."},
        ]
    )
    return {
        "benchmark_candidate_id": f"BC-TEST-{index:02d}",
        "sample_id": f"SAMPLE-{family:02d}",
        "grade": 6 + index % 4,
        "lesson": f"Bài {1 + index % 2}",
        "position": "Mục 1",
        "bloom_level": "Nhận biết" if index % 2 == 0 else "Thông hiểu",
        "student_prompt": f"Câu hỏi thử nghiệm số {index}",
        "conversation_history": history,
        "source_question": "Câu hỏi nguồn là gì?",
        "gold_answer": "Đáp án đúng",
    }


def _response(candidate_id: str, index: int) -> dict:
    scores = []
    for principle_id in PRINCIPLE_IDS:
        score = 1
        rationale = "Nguyên tắc này không cần thiết trong ngữ cảnh hiện tại."
        if index < 8 and principle_id == "PRINCIPLE-EXPLANATION":
            score = 4
            rationale = (
                "Nhu cầu độc lập: học sinh cần hiểu rõ khái niệm. "
                "Nếu bỏ nguyên tắc này: học sinh có thể tiếp tục nhầm."
            )
        elif index == 8 and principle_id == "PRINCIPLE-FEEDBACK":
            score = 4
            rationale = (
                "Nhu cầu độc lập: học sinh cần được xác nhận để tự tin. "
                "Nếu bỏ nguyên tắc này: học sinh không được khen."
            )
        scores.append(
            {
                "principle_id": principle_id,
                "requirement_score": score,
                "rationale": rationale,
                "evidence": "student_prompt cho thấy học sinh đang hỏi bài.",
            }
        )
    return {
        "benchmark_candidate_id": candidate_id,
        "principle_scores": scores,
    }


def _write_fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    pool_path = tmp_path / "pool.csv"
    trace_path = tmp_path / "trace.csv"
    bundle_dir = tmp_path / "bundle"
    registry_path = tmp_path / "paper" / "registry.csv"
    bundle_dir.mkdir()
    rows = [_grounding_row(index) for index in range(10)]

    with pool_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GROUNDING_HEADER)
        writer.writeheader()
        for row in rows:
            serialized = dict(row)
            serialized["conversation_history"] = json.dumps(
                row["conversation_history"], ensure_ascii=False
            )
            writer.writerow(serialized)

    with trace_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACE_HEADER)
        writer.writeheader()
        for index, row in enumerate(rows):
            writer.writerow(
                {
                    "benchmark_candidate_id": row["benchmark_candidate_id"],
                    "sample_id": row["sample_id"],
                    "source_batch": "test",
                    "source_file": "test.csv",
                    "source_row_number": index + 1,
                    "target_tutor_turn_index": 2 if index % 2 == 0 else 4,
                    "split_strategy": "each_tutor_turn",
                    "dialogue_correction_ids": "[]",
                }
            )

    config = GenerationConfig(model="fake-model", max_requests=20)
    prompt_hash = "1" * 64
    schema_hash = "2" * 64
    records = []
    for index, row in enumerate(rows):
        normalized = _response(row["benchmark_candidate_id"], index)
        required = [
            item["principle_id"]
            for item in normalized["principle_scores"]
            if item["requirement_score"] >= 4
        ]
        alternative = [
            item["principle_id"]
            for item in normalized["principle_scores"]
            if item["requirement_score"] == 3
        ]
        payload = build_grounding_payload(row)
        records.append(
            {
                "run_id": "full",
                "benchmark_candidate_id": row["benchmark_candidate_id"],
                "request_hash": build_request_hash(
                    payload=payload,
                    prompt_sha256=prompt_hash,
                    schema_sha256=schema_hash,
                    generation_config=config,
                ),
                "user_prompt": serialize_user_prompt(payload),
                "model": "fake-model",
                "model_version": "fake-model",
                "response_id": f"response-{index}",
                "finish_reason": "STOP",
                "usage_metadata": {},
                "raw_response_text": json.dumps(
                    {"principle_scores": normalized["principle_scores"]},
                    ensure_ascii=False,
                ),
                "normalized_response": normalized,
                "required_principle_set": required,
                "alternative_principle_set": alternative,
                "created_at": "2026-07-28T00:00:00+00:00",
            }
        )
    run_path = bundle_dir / "run_full.jsonl"
    run_path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )
    manifest = {
        "status": "completed_awaiting_analysis",
        "bundle_type": "full_single_run_requirement_scoring",
        "input": {"grounding_pool_sha256": sha256_file(pool_path)},
        "specification": {
            "prompt_sha256": prompt_hash,
            "schema_sha256": schema_hash,
        },
        "generation_config": config.as_dict(),
        "runs": {"full": {"failed_candidate_ids": []}},
        "integrity": {
            "validated": True,
            "run_file_sha256": sha256_file(run_path),
        },
        "limitations": [
            {"limitation_id": "single_run_no_repeatability_estimate"},
            {"limitation_id": "no_expert_accuracy"},
            {"limitation_id": "provisional_model_scores"},
        ],
        "failure_state": {
            "current_failure_count": 0,
            "current_failed_candidate_ids": [],
            "historical_error_count": 1,
        },
    }
    (bundle_dir / "run_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return bundle_dir, pool_path, trace_path, registry_path


def test_evidence_reference_accepts_payload_and_rejects_unrelated_text() -> None:
    payload = build_grounding_payload(_grounding_row(1))
    assert evidence_reference_is_traceable(
        'Lượt 3: "Em chọn đáp án A."', payload
    )
    assert evidence_reference_is_traceable("turn_3: student", payload)
    assert evidence_reference_is_traceable("Lượt thoại 3 của học sinh", payload)
    assert evidence_reference_is_traceable(
        "student_prompt cho thấy học sinh đang hỏi.", payload
    )
    assert not evidence_reference_is_traceable(
        "Nội dung hoàn toàn xa lạ không có căn cứ.", payload
    )


def test_plan03_analysis_partitions_rows_and_writes_lean_artifacts(
    tmp_path: Path,
) -> None:
    bundle, pool, trace, registry = _write_fixture(tmp_path)
    analysis = analyze_full_run(
        bundle_dir=bundle,
        pool_path=pool,
        trace_path=trace,
        paper_registry_path=registry,
        expected_candidate_count=10,
        expected_family_count=5,
        selection_seed=20260727,
        control_sample_per_grade=2,
    )
    assert analysis["integrity"]["candidate_count"] == 10
    assert analysis["integrity"]["score_count"] == 60
    assert analysis["eligibility"]["counts"] == {
        "eligible_without_plan03_review": 8,
        "needs_uet_review": 2,
        "blocked": 0,
    }
    assert sum(
        item["candidate_count"]
        for item in analysis["required_set_distribution"]
    ) == 10
    assert analysis["review_queue"]["flagged_candidate_count"] == 2
    assert analysis["review_queue"]["control_sample_count"] == 8
    assert (bundle / "full_run_analysis.json").is_file()
    assert (bundle / "full_run_analysis.md").is_file()
    assert (bundle / "full_run_review_queue.csv").is_file()
    with (bundle / "full_run_review_queue.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == REVIEW_HEADER
        assert len(list(reader)) == 10
    with registry.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == PAPER_REGISTRY_HEADER
        assert len(list(reader)) == 3

    analyze_full_run(
        bundle_dir=bundle,
        pool_path=pool,
        trace_path=trace,
        paper_registry_path=registry,
        expected_candidate_count=10,
        expected_family_count=5,
        selection_seed=20260727,
        control_sample_per_grade=2,
    )
    with registry.open(encoding="utf-8", newline="") as handle:
        assert len(list(csv.DictReader(handle))) == 3

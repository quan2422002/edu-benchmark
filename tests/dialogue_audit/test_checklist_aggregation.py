from edu_benchmark.dialogue_audit.checklist_aggregation import (
    CANONICAL_QUALITY_COLUMNS,
    aggregate_sample,
    build_canonical_quality_rows,
    build_review_queue_rows,
    sync_quality_rows,
)


def row(sample_id, criterion_id, result, confidence):
    return {
        "sample_id": sample_id,
        "criterion_id": criterion_id,
        "criterion_group": "consistency",
        "criterion_name": criterion_id,
        "result": result,
        "confidence_score": str(confidence),
        "evidence_fragment_id": "",
        "reason": f"{criterion_id} reason",
    }


def test_aggregate_sample_fails_on_any_failed_criterion():
    aggregate = aggregate_sample(
        [
            row("S1", "RAW-STR-02", "pass", 0.98),
            row("S1", "RAW-CON-04", "fail", 0.88),
            row("S1", "RAW-CON-07", "fail", 0.9),
        ]
    )

    assert aggregate.decision == "failed"
    assert aggregate.confidence_score == 0.88
    assert aggregate.blocking_criterion_ids == ["RAW-CON-04", "RAW-CON-07"]


def test_aggregate_sample_routes_uncertain_to_human_review():
    aggregate = aggregate_sample(
        [
            row("S2", "RAW-STR-02", "pass", 0.98),
            row("S2", "RAW-CON-02", "uncertain", 0.52),
            row("S2", "RAW-CON-07", "uncertain", 0.62),
        ]
    )

    assert aggregate.decision == "need_human_review"
    assert aggregate.confidence_score == 0.52
    assert aggregate.blocking_criterion_ids == ["RAW-CON-02", "RAW-CON-07"]


def test_aggregate_sample_pass_uses_lowest_confidence_across_all_criteria():
    aggregate = aggregate_sample(
        [
            row("S3", "RAW-STR-02", "pass", 0.99),
            row("S3", "RAW-CON-02", "pass", 0.76),
            row("S3", "RAW-PED-01", "not_applicable", 0.82),
        ]
    )

    assert aggregate.decision == "pass"
    assert aggregate.confidence_score == 0.76


def test_sync_quality_rows_and_review_queue_follow_strict_aggregate():
    aggregate = aggregate_sample(
        [
            row("S4", "RAW-STR-02", "pass", 0.98),
            row("S4", "RAW-CON-02", "uncertain", 0.52),
        ]
    )
    quality_rows = [
        {
            "sample_id": "S4",
            "quality_decision": "pass",
            "confidence_score": "0.98",
            "failure_reasons": "",
            "suggested_reviewer_action": "keep",
            "needs_hnmu_review": "false",
            "checked_by": "old",
            "checked_at": "old",
        }
    ]
    synced = sync_quality_rows(
        quality_rows,
        {"S4": aggregate},
        decision_column="quality_decision",
        checked_at="2026-07-20T00:00:00+07:00",
    )
    assert synced[0]["quality_decision"] == "need_human_review"
    assert synced[0]["confidence_score"] == "0.52"
    assert synced[0]["needs_hnmu_review"] == "true"

    queue = build_review_queue_rows(
        synced,
        {"S4": aggregate},
        fieldnames=[
            "sample_id",
            "review_reason",
            "priority",
            "suggested_question_to_hnmu",
            "related_criterion_ids",
            "evidence_fragment_ids",
            "checked_by",
            "checked_at",
        ],
        decision_column="quality_decision",
        checked_at="2026-07-20T00:00:00+07:00",
    )
    assert len(queue) == 1
    assert queue[0]["related_criterion_ids"] == "RAW-CON-02"


def test_build_canonical_quality_rows_uses_shared_schema_and_pass_label():
    aggregate = aggregate_sample(
        [
            row("S5", "RAW-STR-02", "pass", 0.98),
            row("S5", "RAW-CON-02", "pass", 0.76),
        ],
        pass_label="pass",
    )

    rows = build_canonical_quality_rows(
        ["S5"],
        {"S5": aggregate},
        sample_metadata={
            "S5": {
                "source_file": "shared/raw_data/HNMU-teacher_dialog_samples/Lớp 6.xlsx",
                "source_row_number": "2",
                "grade": "6",
                "lesson": "Bài 1. Thông tin và dữ liệu",
            }
        },
        existing_quality_rows={"S5": {"source_shard": "shard_01"}},
        checked_at="2026-07-20T00:00:00+07:00",
    )

    assert list(rows[0].keys()) == CANONICAL_QUALITY_COLUMNS
    assert rows[0]["quality_decision"] == "pass"
    assert rows[0]["blocking_criterion_ids"] == ""
    assert rows[0]["needs_hnmu_review"] == "false"
    assert rows[0]["source_shard"] == "shard_01"

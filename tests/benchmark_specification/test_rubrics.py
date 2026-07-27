from edu_benchmark.benchmark_specification.rubrics import (
    flatten_two_tier_rubrics,
)


def test_flattened_export_preserves_capability_and_principle_tiers():
    dimensions = [
        {
            "dimension_id": "DIM-01",
            "criterion": "Đúng chuyên môn.",
            "observable_evidence": "Response.",
            "score_levels": "1|3|5",
            "status": "needs_hnmu_review",
        }
    ]
    tasks = [
        {
            "task_id": "TASK-NEXT-TUTOR-RESPONSE",
            "status": "needs_hnmu_review",
        }
    ]
    principle_rubrics = [
        {
            "rubric_id": "R-EXPLAIN-01",
            "principle_id": "PRINCIPLE-EXPLANATION",
            "criterion": "Giải thích làm rõ quan hệ cốt lõi.",
            "observable_evidence": "Response.",
            "score_levels": "1|3|5",
            "status": "needs_hnmu_review",
        }
    ]
    rows = flatten_two_tier_rubrics(dimensions, principle_rubrics, tasks)
    assert [row["rubric_id"] for row in rows] == ["DIM-01", "R-EXPLAIN-01"]
    assert rows[0]["principle_id"] == ""
    assert rows[1]["principle_id"] == "PRINCIPLE-EXPLANATION"
    assert {row["task_id"] for row in rows} == {"TASK-NEXT-TUTOR-RESPONSE"}

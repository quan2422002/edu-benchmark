from edu_benchmark.benchmark_evaluation.performance import (
    compare_target_run_performance,
    summarize_target_run_performance,
)


def _manifest(run_id: str, concurrency: int, elapsed: float):
    configuration = {}
    if concurrency != 1:
        configuration["max_concurrency"] = concurrency
    return {
        "run_id": run_id,
        "status": "completed",
        "configuration": configuration,
        "integrity": {
            "record_count": 2,
            "completed_record_count": 2,
            "needs_review_record_count": 0,
        },
        "failed_candidate_ids": [],
        "resume_history": [
            {
                "record_count_before": 0,
                "record_count_after": 2,
                "elapsed_seconds": elapsed,
            }
        ],
        "provider_observations": [
            {"input_tokens": 10, "output_tokens": 20, "latency_seconds": 2},
            {"input_tokens": 20, "output_tokens": 30, "latency_seconds": 4},
        ],
        "resource_summary": {"memory_used_peak_gib": 20.0},
    }


def test_summarize_target_run_performance_uses_execution_wall_time():
    summary = summarize_target_run_performance(_manifest("seq", 1, 10))

    assert summary["max_concurrency"] == 1
    assert summary["samples_per_minute"] == 12.0
    assert summary["aggregate_output_tokens_per_second"] == 5.0
    assert summary["request_latency_seconds"] == {
        "mean": 3.0,
        "median": 3.0,
        "p95": 4.0,
        "max": 4.0,
    }


def test_compare_target_run_performance_reports_throughput_speedup():
    comparison = compare_target_run_performance(
        _manifest("seq", 1, 10),
        _manifest("parallel", 2, 5),
    )

    assert comparison["candidate"]["max_concurrency"] == 2
    assert comparison["throughput_speedup"] == 2.0

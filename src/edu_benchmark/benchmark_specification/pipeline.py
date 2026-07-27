"""File-oriented preparation pipeline for approved Plan-03 Workstreams A-D."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .schema import read_csv_rows, write_csv_rows
from .task_discovery import (
    CENSUS_COLUMNS,
    DISCOVERY_CODING_INPUT_COLUMNS,
    DISCOVERY_SAMPLE_COLUMNS,
    DISCOVERY_STRATA_COLUMNS,
    build_candidate_feature_census,
    enrich_discovery_sample,
    select_task_discovery_sample,
    summarize_discovery_strata,
)


def run_task_discovery_preparation(
    experiment_root: Path,
    *,
    per_grade: int = 40,
    seed: str = "plan03-task-discovery-v1",
) -> dict[str, object]:
    """Build the full census and initial 160-row discovery sample."""

    conversion_root = experiment_root / "outputs" / "benchmark_conversion" / "full_v0"
    candidates = read_csv_rows(conversion_root / "benchmark_candidate_splits.csv")
    traces = read_csv_rows(conversion_root / "conversion_trace.csv")
    census = build_candidate_feature_census(candidates, traces)
    sample = select_task_discovery_sample(
        census,
        per_grade=per_grade,
        seed=seed,
    )
    coding_input = enrich_discovery_sample(sample, candidates)
    strata = summarize_discovery_strata(census, sample)
    output_root = experiment_root / "outputs" / "benchmark_specification" / "task_discovery"
    write_csv_rows(
        output_root / "candidate_feature_census.csv",
        CENSUS_COLUMNS,
        census,
    )
    write_csv_rows(
        output_root / "task_discovery_sample.csv",
        DISCOVERY_SAMPLE_COLUMNS,
        sample,
    )
    write_csv_rows(
        output_root / "task_discovery_coding_input.csv",
        DISCOVERY_CODING_INPUT_COLUMNS,
        coding_input,
    )
    write_csv_rows(
        output_root / "task_discovery_strata.csv",
        DISCOVERY_STRATA_COLUMNS,
        strata,
    )
    summary = {
        "pipeline_id": "plan03-task-discovery-preparation-v1",
        "candidate_count": len(census),
        "sample_count": len(sample),
        "sample_family_count": len({row["sample_id"] for row in sample}),
        "seed": seed,
        "per_grade": per_grade,
        "candidate_by_grade": dict(
            sorted(Counter(row["grade"] for row in census).items())
        ),
        "sample_by_grade": dict(
            sorted(Counter(row["grade"] for row in sample).items())
        ),
        "feature_method": "deterministic_regex_v1",
        "semantic_warning": (
            "content_form_signal and student_state_signal are routing signals, "
            "not HNMU-confirmed task or student-state labels"
        ),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "task_discovery_preparation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary

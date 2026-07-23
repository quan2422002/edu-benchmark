import csv
import json
from pathlib import Path

from edu_benchmark.benchmark_conversion.pipeline import (
    run_conversion_input_build,
    run_conversion_pilot,
)
from edu_benchmark.benchmark_conversion.schema import CONVERSION_INPUT_COLUMNS


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_real_plan01_pipeline_writes_665_inputs_and_40_reproducible_candidates(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    source_experiment = repo_root / "experiments" / "20260722_000940"
    specs = []
    from edu_benchmark.benchmark_conversion.pipeline import default_snapshot_specs

    for spec in default_snapshot_specs(source_experiment):
        specs.append(spec)

    first = tmp_path / "first"
    input_result = run_conversion_input_build(first, snapshot_specs=specs)
    assert input_result["input_row_count"] == 665
    assert input_result["blocking_error_count"] == 0
    result_a = run_conversion_pilot(first)
    assert result_a["candidate_count"] == 40
    assert result_a["grade_counts"] == {"6": 10, "7": 10, "8": 10, "9": 10}

    second = tmp_path / "second"
    run_conversion_input_build(second, snapshot_specs=specs)
    result_b = run_conversion_pilot(second)
    assert result_b["candidate_count"] == 40

    candidates_a = (
        first
        / "outputs"
        / "benchmark_conversion"
        / "pilot_v0"
        / "benchmark_candidate_splits.csv"
    ).read_bytes()
    candidates_b = (
        second
        / "outputs"
        / "benchmark_conversion"
        / "pilot_v0"
        / "benchmark_candidate_splits.csv"
    ).read_bytes()
    assert candidates_a == candidates_b


def test_incompatible_pass_dialogues_are_written_to_split_errors(tmp_path):
    input_root = tmp_path / "outputs" / "benchmark_conversion"
    input_root.mkdir(parents=True)
    fieldnames = CONVERSION_INPUT_COLUMNS
    rows = []
    for grade in ("6", "7", "8", "9"):
        rows.append(
            {
                **{field: "" for field in fieldnames},
                "sample_id": f"BAD-{grade}",
                "source_batch": "test",
                "source_file": "source.xlsx",
                "source_row_number": "2",
                "grade": grade,
                "lesson": "Bài bad",
                "question": "Q",
                "bloom_level": "Nhận biết",
                "answer_sgv": "A",
                "raw_dialogue": "HS: Q\nAI: Hint\nHS: End",
                "conversion_dialogue": "HS: Q\nAI: Hint\nHS: End",
                "dialogue_correction_ids": "[]",
                "raw_quality_decision": "pass",
                "raw_audit_blocking_evidence_fragment_ids": "[]",
                "raw_audit_all_evidence_fragment_ids": '["F1"]',
            }
        )
        for index in range(2):
            rows.append(
                {
                    **{field: "" for field in fieldnames},
                    "sample_id": f"GOOD-{grade}-{index}",
                    "source_batch": "test",
                    "source_file": "source.xlsx",
                    "source_row_number": str(index + 3),
                    "grade": grade,
                    "lesson": f"Bài {index}",
                    "question": "Q",
                    "bloom_level": "Nhận biết",
                    "answer_sgv": "A",
                    "raw_dialogue": "HS: Q\nAI: A",
                    "conversion_dialogue": "HS: Q\nAI: A",
                    "dialogue_correction_ids": "[]",
                    "raw_quality_decision": "pass",
                    "raw_audit_blocking_evidence_fragment_ids": "[]",
                    "raw_audit_all_evidence_fragment_ids": '["F1"]',
                }
            )
    with (input_root / "conversion_input_pass_samples.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    result = run_conversion_pilot(tmp_path, size_per_grade=1)
    assert result["excluded_incompatible_count"] == 4
    errors = read_rows(
        input_root / "pilot_v0" / "dialogue_split_errors.csv"
    )
    assert {row["sample_id"] for row in errors} == {
        "BAD-6",
        "BAD-7",
        "BAD-8",
        "BAD-9",
    }
    assert all(row["error_code"] == "last_turn_not_tutor" for row in errors)
    summary = json.loads(
        (input_root / "pilot_v0" / "pilot_selection_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["total_selected"] == 4

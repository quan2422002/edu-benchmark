import csv
import json
from collections import Counter
from pathlib import Path

import pytest

from edu_benchmark.benchmark_conversion.dialogue_split import parse_dialogue_turns
from edu_benchmark.benchmark_conversion.pipeline import (
    run_full_multi_candidate_conversion,
    run_multi_candidate_migration_pilot,
)
from edu_benchmark.benchmark_conversion.schema import CANDIDATE_SPLIT_COLUMNS


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def real_paths():
    repo_root = Path(__file__).resolve().parents[2]
    experiment = repo_root / "experiments" / "20260722_000940"
    conversion_root = experiment / "outputs" / "benchmark_conversion"
    return (
        experiment,
        conversion_root / "conversion_input_pass_samples.csv",
        conversion_root / "dialogue_corrections.csv",
    )


def test_real_migration_pilot_is_balanced_and_includes_approved_corrections(tmp_path):
    experiment, input_path, corrections_path = real_paths()
    result = run_multi_candidate_migration_pilot(
        experiment,
        input_path=input_path,
        corrections_path=corrections_path,
        output_dir=tmp_path,
    )
    pilot_rows = read_rows(tmp_path / "pilot_sample_ids.csv")
    assert result["selected_raw_sample_count"] == 20
    assert Counter(row["grade"] for row in pilot_rows) == {
        "6": 5,
        "7": 5,
        "8": 5,
        "9": 5,
    }
    assert {
        row["sample_id"]
        for row in pilot_rows
        if row["selection_reason"] == "approved_correction_coverage"
    } == {"HNMU-G7-R0189-STT6", "HNMU-G9-R0237-STT12"}
    assert result["blocking_error_count"] == 0
    validation = json.loads(
        (tmp_path / "candidate_mapping_validation.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation["status"] == "pass"
    assert validation["exact_mapping_pass_count"] == result["candidate_count"]


def test_real_full_conversion_matches_plan02_baseline_and_exact_turn_mapping(tmp_path):
    experiment, input_path, corrections_path = real_paths()
    first = tmp_path / "first"
    second = tmp_path / "second"
    result = run_full_multi_candidate_conversion(
        experiment,
        input_path=input_path,
        corrections_path=corrections_path,
        output_dir=first,
    )
    result_again = run_full_multi_candidate_conversion(
        experiment,
        input_path=input_path,
        corrections_path=corrections_path,
        output_dir=second,
    )
    assert result["raw_sample_count"] == 665
    assert result["candidate_family_count"] == 665
    assert result["candidate_count"] == 2028
    assert result["candidate_counts_by_grade"] == {
        "6": 279,
        "7": 438,
        "8": 557,
        "9": 754,
    }
    assert result["history_turn_counts"] == {
        "0": 665,
        "2": 665,
        "4": 373,
        "6": 206,
        "8": 101,
        "10": 16,
        "12": 2,
    }
    assert result_again["file_sha256"] == result["file_sha256"]

    candidates = read_rows(first / "benchmark_candidate_splits.csv")
    traces = read_rows(first / "conversion_trace.csv")
    dispositions = read_rows(first / "conversion_dispositions.csv")
    sources = {row["sample_id"]: row for row in read_rows(input_path)}
    assert list(candidates[0]) == CANDIDATE_SPLIT_COLUMNS
    assert len(candidates) == len(traces)
    assert len(dispositions) == 665
    assert all(
        row["conversion_disposition"] == "converted"
        for row in dispositions
    )
    assert len({row["benchmark_candidate_id"] for row in candidates}) == 2028
    trace_by_id = {row["benchmark_candidate_id"]: row for row in traces}

    for candidate in candidates:
        source = sources[candidate["sample_id"]]
        turns = parse_dialogue_turns(source["conversion_dialogue"])
        trace = trace_by_id[candidate["benchmark_candidate_id"]]
        target_index = int(trace["target_tutor_turn_index"])
        target = turns[target_index - 1]
        history = json.loads(candidate["conversation_history"])
        assert target.role == "tutor"
        assert candidate["student_prompt"] == turns[0].content
        assert candidate["gold_response"] == target.content
        assert history == [
            {
                "turn_index": turn.turn_index,
                "role": turn.role,
                "content": turn.content,
            }
            for turn in turns[1 : target_index - 1]
        ]
        assert all(item["turn_index"] < target_index for item in history)

    assert sum(
        parse_dialogue_turns(row["conversion_dialogue"])[-1].role == "student"
        for row in sources.values()
    ) == 297
    mapping_validation = json.loads(
        (first / "candidate_mapping_validation.json").read_text(
            encoding="utf-8"
        )
    )
    assert mapping_validation == {
        "candidate_row_count": 2028,
        "disposition_row_count": 665,
        "exact_mapping_pass_count": 2028,
        "failure_count": 0,
        "failure_examples": [],
        "regex_parsed_source_count": 665,
        "source_row_count": 665,
        "status": "pass",
        "trace_row_count": 2028,
        "trailing_student_source_count": 297,
        "validation_method": (
            "TURN_PATTERN_regex_parse_and_exact_structural_comparison"
        ),
    }
    assert json.loads((first / "run_status.json").read_text())["status"] == (
        "complete"
    )


def test_failed_rerun_atomically_replaces_stale_candidate_bundle(tmp_path):
    experiment, input_path, corrections_path = real_paths()
    output_dir = tmp_path / "full"
    run_full_multi_candidate_conversion(
        experiment,
        input_path=input_path,
        corrections_path=corrections_path,
        output_dir=output_dir,
    )
    assert (output_dir / "benchmark_candidate_splits.csv").is_file()

    rows = read_rows(input_path)
    rows[0]["answer_sgv"] = ""
    invalid_input = tmp_path / "invalid_input.csv"
    write_rows(invalid_input, rows)
    with pytest.raises(ValueError, match="blocking errors"):
        run_full_multi_candidate_conversion(
            experiment,
            input_path=invalid_input,
            corrections_path=corrections_path,
            output_dir=output_dir,
        )
    assert not (output_dir / "benchmark_candidate_splits.csv").exists()
    assert not (output_dir / "conversion_trace.csv").exists()
    assert json.loads(
        (output_dir / "run_status.json").read_text(encoding="utf-8")
    )["status"] == "failed"
    assert read_rows(output_dir / "dialogue_split_errors.csv")

    run_full_multi_candidate_conversion(
        experiment,
        input_path=input_path,
        corrections_path=corrections_path,
        output_dir=output_dir,
    )
    rows = read_rows(input_path)[1:]
    baseline_mismatch_input = tmp_path / "baseline_mismatch_input.csv"
    write_rows(baseline_mismatch_input, rows)
    with pytest.raises(ValueError, match="acceptance baseline mismatch"):
        run_full_multi_candidate_conversion(
            experiment,
            input_path=baseline_mismatch_input,
            corrections_path=corrections_path,
            output_dir=output_dir,
        )
    assert not (output_dir / "benchmark_candidate_splits.csv").exists()
    assert json.loads(
        (output_dir / "run_status.json").read_text(encoding="utf-8")
    )["candidate_bundle_published"] is False

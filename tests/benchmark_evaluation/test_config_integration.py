from pathlib import Path
import csv

from edu_benchmark.benchmark_evaluation.config_builder import (
    build_evaluation_config,
    read_csv,
    select_applicable_rubric_ids,
)
from edu_benchmark.benchmark_evaluation.validation import (
    EXPECTED_FILES,
    validate_evaluation_config,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
INSTRUCTION_BUNDLE = (
    ROOT
    / "shared/prompts/benchmark_tutor_response_generation/"
    "instruction_bundle_v1.yaml"
)


def test_build_real_plan05_configuration(tmp_path):
    summary = build_evaluation_config(
        output_dir=tmp_path,
        principles_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/principle_foundation/"
            "pedagogical_principles.csv"
        ),
        rubrics_csv=EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv",
        serious_errors_csv=(
            EXPERIMENT / "outputs/benchmark_rubric/serious_errors.csv"
        ),
        candidates_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
        ),
        analysis_json=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/full_run_analysis.json"
        ),
        instruction_bundle_path=INSTRUCTION_BUNDLE,
    )
    assert summary["candidate_count"] == 2028
    assert summary["eligible_count"] == 1400
    assert {path.name for path in tmp_path.iterdir()} == EXPECTED_FILES
    assert validate_evaluation_config(tmp_path)["valid"] is True
    with (tmp_path / "instruction_registry.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        instructions = list(csv.DictReader(handle))
    assert all(row["basis_summary"] for row in instructions)
    assert all(row["source_locator"] for row in instructions)
    assert {
        row["instruction_bundle_version"] for row in instructions
    } == {"v1"}
    assert all(
        len(row["instruction_bundle_sha256"]) == 64
        for row in instructions
    )
    principle_rows = [
        row for row in instructions if row["instruction_type"] == "principle"
    ]
    assert all(row["principle_name_vi"] for row in principle_rows)
    assert all(
        row["instruction_vi"].startswith("### Yêu cầu sư phạm:")
        for row in principle_rows
    )
    schema = (
        tmp_path / "evaluation_schema.json"
    ).read_text(encoding="utf-8")
    for field in (
        "system_prompt",
        "user_prompt",
        "conversation_messages",
        "finish_reason",
        "response_status",
        "completion_issue",
        "experiment_id",
        "plan_id",
        "pipeline_stage",
        "run_id",
        "blind_pairwise_judgment_v2",
        "raw_criterion_judgments",
        "adjusted_criterion_judgments",
        "criterion_adjustments",
    ):
        assert f'"{field}"' in schema


def test_applicable_rubrics_exclude_unselected_principles():
    rubrics = read_csv(
        EXPERIMENT / "outputs/benchmark_rubric/rubrics.csv"
    )
    selected = select_applicable_rubric_ids(
        rubrics, ["PRINCIPLE-EXPLANATION"]
    )
    assert len(selected) == 7
    assert all(
        row["tier"] == "general"
        or row["principle_id"] == "PRINCIPLE-EXPLANATION"
        for row in rubrics
        if row["rubric_id"] in selected
    )

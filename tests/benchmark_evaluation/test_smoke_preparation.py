from pathlib import Path
import json

import pytest

from src.edu_benchmark.benchmark_evaluation.config_builder import (
    PRINCIPLE_ORDER,
    build_evaluation_config,
)
from src.edu_benchmark.benchmark_evaluation.smoke import (
    SmokePreparationError,
    load_required_principle_sets,
    prepare_smoke_requests,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"
INSTRUCTION_BUNDLE = (
    ROOT
    / "shared/prompts/benchmark_tutor_response_generation/"
    "instruction_bundle_v1.yaml"
)
INSTRUCTION_BUNDLE_V2 = (
    ROOT
    / "shared/prompts/benchmark_tutor_response_generation/"
    "instruction_bundle_v2.yaml"
)


def test_prepare_ten_real_smoke_requests(tmp_path):
    build_evaluation_config(
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
    requests = prepare_smoke_requests(
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        analysis_json=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/full_run_analysis.json"
        ),
        requirement_run_jsonl=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
        instruction_bundle_path=INSTRUCTION_BUNDLE,
        max_candidates=10,
    )
    assert len(requests) == 10
    assert {request.grade for request in requests} == {"6", "7", "8", "9"}
    assert all(request.required_principle_ids for request in requests)
    assert all(
        request.conversation.messages[-1].role == "user"
        for request in requests
    )
    assert all(
        "gold_answer" not in request.system_instruction
        for request in requests
    )
    assert all(
        request.instruction_bundle_version == "v1"
        for request in requests
    )
    assert all(
        "### Yêu cầu sư phạm:" in request.system_instruction
        for request in requests
    )
    assert all(request.trace_fields()["system_prompt"] for request in requests)
    assert all(request.trace_fields()["user_prompt"] for request in requests)
    assert all(
        request.trace_fields()["conversation_messages"][-1]["role"] == "user"
        for request in requests
    )
    requirement_sets = load_required_principle_sets(
        EXPERIMENT
        / "outputs/principle_requirement_scoring/"
        "full_gemini35_medium_v1/run_full.jsonl"
    )
    assert all(
        request.required_principle_ids
        == requirement_sets[request.benchmark_candidate_id]
        for request in requests
    )


def test_requirement_loader_rejects_score_three_in_required_set(tmp_path):
    scores = [
        {
            "principle_id": principle_id,
            "requirement_score": 3 if index == 0 else 2,
        }
        for index, principle_id in enumerate(PRINCIPLE_ORDER)
    ]
    run_file = tmp_path / "run.jsonl"
    run_file.write_text(
        json.dumps(
            {
                "benchmark_candidate_id": "BC-1",
                "normalized_response": {"principle_scores": scores},
                "required_principle_set": [PRINCIPLE_ORDER[0]],
                "alternative_principle_set": [PRINCIPLE_ORDER[0]],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(
        SmokePreparationError, match="exact requirement_score>=4 set"
    ):
        load_required_principle_sets(run_file)


def test_prepare_exact_v1_candidates_with_v2_bundle():
    manifest_path = (
        EXPERIMENT
        / "outputs/benchmark_evaluation/"
        "smoke_gemini35_instruction_v1/run_manifest.json"
    )
    candidate_ids = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )["candidate_ids"]
    requests = prepare_smoke_requests(
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        analysis_json=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/full_run_analysis.json"
        ),
        requirement_run_jsonl=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
        instruction_bundle_path=INSTRUCTION_BUNDLE_V2,
        max_candidates=10,
        fixed_candidate_ids=candidate_ids,
    )
    assert [request.benchmark_candidate_id for request in requests] == (
        candidate_ids
    )
    assert {
        request.instruction_bundle_version for request in requests
    } == {"v2"}
    assert all(
        "trả lời tự nhiên và cô đọng" in request.system_instruction
        for request in requests
    )

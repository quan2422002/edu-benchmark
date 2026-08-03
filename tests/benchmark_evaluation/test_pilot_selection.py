import json
from pathlib import Path

from src.edu_benchmark.benchmark_evaluation.cost_pilot import (
    PRINCIPLE_MINIMUMS as COST_PILOT_PRINCIPLE_MINIMUMS,
    build_judge_cost_pilot_manifest,
)
from src.edu_benchmark.benchmark_evaluation.full import (
    build_full_manifest,
)
from src.edu_benchmark.benchmark_evaluation.pilot import (
    PRINCIPLE_MINIMUMS,
    build_pilot_manifest,
    bloom_group,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/20260727_170150"


def test_bloom_group_supports_active_vietnamese_labels():
    assert bloom_group("Nhận biết") == "remember"
    assert bloom_group("Thông hiểu") == "understand"
    assert bloom_group("Vận dụng") == "apply"


def test_pilot_manifest_meets_locked_coverage_contract():
    manifest = build_pilot_manifest(
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
        smoke_anchor_manifest=(
            EXPERIMENT
            / "outputs/benchmark_evaluation/"
            "smoke_gemini35_instruction_v2/run_manifest.json"
        ),
    )

    assert manifest["candidate_count"] == 80
    assert len(manifest["candidate_ids"]) == 80
    assert len(set(manifest["candidate_ids"])) == 80
    assert manifest["coverage"]["grade_counts"] == {
        "6": 20,
        "7": 20,
        "8": 20,
        "9": 20,
    }
    assert manifest["coverage"]["distinct_family_count"] == 80
    assert set(manifest["smoke_anchor_candidate_ids"]) <= set(
        manifest["candidate_ids"]
    )
    for principle_id, minimum in PRINCIPLE_MINIMUMS.items():
        assert (
            manifest["coverage"]["principle_incidence_counts"][
                principle_id
            ]
            >= minimum
        )
    assert (
        "BC-HNMU-G7-R0207-STT10-AI10"
        in manifest["candidate_ids"]
    )


def test_published_manifest_matches_builder_contract():
    path = (
        EXPERIMENT
        / "outputs/benchmark_evaluation/pilot_80_v1/"
        "candidate_manifest.json"
    )
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "pilot_80_v1"
    assert manifest["candidate_count"] == 80
    assert manifest["coverage"]["distinct_grade_lesson_count"] >= 32


def test_full_manifest_locks_exact_exported_eligible_pool():
    manifest = build_full_manifest(
        eligible_csv=(
            EXPERIMENT
            / "outputs/benchmark_candidate_pool/"
            "eligible_without_plan03_review.csv"
        ),
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        candidate_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_conversion/full_v0/benchmark_candidate_splits.csv"
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
    )

    assert manifest["manifest_version"] == "full_1400_v1"
    assert manifest["candidate_count"] == 1400
    assert len(manifest["candidate_ids"]) == 1400
    assert len(set(manifest["candidate_ids"])) == 1400
    assert len(manifest["candidate_ids_sha256"]) == 64
    assert manifest["selection_contract"]["required_principle_threshold"] == 4
    assert manifest["execution_gate"]["status"].startswith("closed_")



def test_judge_cost_pilot_manifest_meets_locked_coverage_contract():
    manifest = build_judge_cost_pilot_manifest(
        pilot_manifest=(
            EXPERIMENT
            / "outputs/benchmark_evaluation/pilot_80_v1/"
            "candidate_manifest.json"
        ),
        grounding_pool_csv=(
            EXPERIMENT
            / "inherited_resources/from_20260722_000940/"
            "benchmark_specification/candidate_grounding/"
            "candidate_principle_grounding_pool.csv"
        ),
        requirement_run_jsonl=(
            EXPERIMENT
            / "outputs/principle_requirement_scoring/"
            "full_gemini35_medium_v1/run_full.jsonl"
        ),
    )
    assert manifest["manifest_version"] == "judge_cost_pilot_30_v1"
    assert manifest["candidate_count"] == 30
    assert manifest["coverage"]["grade_counts"] == {
        "6": 8, "7": 8, "8": 7, "9": 7
    }
    assert manifest["coverage"]["distinct_family_count"] == 30
    for principle_id, minimum in COST_PILOT_PRINCIPLE_MINIMUMS.items():
        assert (
            manifest["coverage"]["principle_incidence_counts"][principle_id]
            >= minimum
        )


def test_published_judge_cost_pilot_manifest_is_locked():
    manifest = json.loads((
        EXPERIMENT
        / "outputs/benchmark_evaluation/full_1400_v1/"
        "judge_cost_pilot_30/candidate_manifest.json"
    ).read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "judge_cost_pilot_30_v1"
    assert manifest["candidate_count"] == 30
    assert len(manifest["candidate_ids_sha256"]) == 64

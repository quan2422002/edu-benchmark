from pathlib import Path

import pytest

from src.edu_benchmark.benchmark_evaluation.costing import (
    BudgetExceededError,
    BudgetPolicy,
    TokenPricing,
    estimate_self_deployed_cost,
)
from src.edu_benchmark.benchmark_evaluation.prompt_builder import (
    build_candidate_system_instruction,
)
from src.edu_benchmark.benchmark_evaluation.instruction_bundle import (
    load_instruction_bundle,
)


ROOT = Path(__file__).resolve().parents[2]
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
INSTRUCTION_BUNDLE_LEARNLM = (
    ROOT
    / "shared/prompts/benchmark_tutor_response_generation/"
    "instruction_bundle_v3_learnlm.yaml"
)


def test_prompt_contains_context_and_principles_but_no_evaluator_fields():
    prompt, digest = build_candidate_system_instruction(
        grade="8",
        lesson="Bảng tính",
        source_question="Hãy tính tổng cột A.",
        required_principle_ids=(
            "PRINCIPLE-EXPLANATION",
            "PRINCIPLE-QUESTIONING",
        ),
        instruction_bundle=load_instruction_bundle(INSTRUCTION_BUNDLE),
    )
    assert "Lớp: 8" in prompt
    assert "Bài học: Bảng tính" in prompt
    assert "### Yêu cầu sư phạm: Giải thích" in prompt
    assert "### Yêu cầu sư phạm: Đặt câu hỏi" in prompt
    assert "\n- Mục tiêu:" in prompt
    assert "\n- Hành vi cần thể hiện:" in prompt
    assert "\n- Cần tránh:" in prompt
    assert "\n- Bảo toàn quyền chủ động:" in prompt
    assert "gold_answer" not in prompt
    assert len(digest) == 64


def test_instruction_bundle_has_version_and_stable_hash():
    bundle = load_instruction_bundle(INSTRUCTION_BUNDLE)
    assert bundle.bundle_version == "v1"
    assert bundle.prompt_language == "vi"
    assert len(bundle.principles) == 6
    assert len(bundle.sha256) == 64
    assert (
        bundle.principles_by_id["PRINCIPLE-FEEDBACK"].principle_name_vi
        == "Phản hồi"
    )


def test_v2_bundle_adds_concise_complete_response_instruction():
    bundle = load_instruction_bundle(INSTRUCTION_BUNDLE_V2)
    assert bundle.bundle_version == "v2"
    assert "cô đọng" in bundle.response_style_instruction
    assert "kết thúc trọn câu" in bundle.response_style_instruction



def test_learnlm_bundle_is_a_prompt_variant_not_a_new_model_contract():
    baseline = load_instruction_bundle(INSTRUCTION_BUNDLE_V2)
    learnlm = load_instruction_bundle(INSTRUCTION_BUNDLE_LEARNLM)
    assert learnlm.bundle_version == "v3-learnlm"
    assert "Theo định hướng LearnLM" in learnlm.general_instruction
    assert "Không tự thêm câu hỏi" in learnlm.general_instruction
    assert learnlm.principles == baseline.principles
    assert (
        learnlm.response_style_instruction
        == baseline.response_style_instruction
    )
    prompt, _ = build_candidate_system_instruction(
        grade="7",
        lesson="Thuật toán tìm kiếm",
        source_question="Giải thích vì sao cần sắp xếp trước.",
        required_principle_ids=("PRINCIPLE-EXPLANATION",),
        instruction_bundle=learnlm,
    )
    assert "### Yêu cầu sư phạm: Giải thích" in prompt
    assert "### Yêu cầu sư phạm: Đặt câu hỏi" not in prompt
    assert "### Yêu cầu sư phạm: Luyện tập" not in prompt

def test_token_cost_and_budget_gate():
    pricing = TokenPricing(1.5, 9.0)
    assert pricing.estimate(1_000_000, 1_000_000) == 10.5
    policy = BudgetPolicy(hard_budget_usd=250, reserve_usd=25)
    policy.assert_next_batch_allowed(
        actual_spend_usd=56, next_batch_upper_bound_usd=20
    )
    with pytest.raises(BudgetExceededError):
        policy.assert_next_batch_allowed(
            actual_spend_usd=220, next_batch_upper_bound_usd=6
        )


def test_self_deployed_cost():
    assert estimate_self_deployed_cost(
        endpoint_hours=2.5,
        hourly_price_usd=4,
        storage_network_usd=1,
    ) == 11

import math

from src.edu_benchmark.benchmark_evaluation.section_v_ablation import (
    agreement_statistics,
    score_records,
)


def _criterion(rubric_id: str, judgment: str) -> dict[str, str]:
    return {
        "rubric_id": rubric_id,
        "target_judgment": judgment,
    }


def _record(
    candidate_id: str,
    overall: str,
    principle_prefix: str = "EXP",
) -> dict[str, object]:
    principle_ids = {
        "EXP": ("RUB-EXP-CORE", "RUB-EXP-COHER", "RUB-EXP-ADAPT"),
    }[principle_prefix]
    judgments = [
        _criterion("RUB-GEN-ACC", "Win"),
        _criterion("RUB-GEN-ALIGN", "Tie"),
        _criterion("RUB-GEN-SCAFF", "Lose"),
        _criterion("RUB-GEN-COMM", "Win"),
    ]
    judgments.extend(_criterion(item, "Win") for item in principle_ids)
    return {
        "comparison_id": f"JUDGE-test-{candidate_id}",
        "benchmark_candidate_id": candidate_id,
        "overall_judgment": {"target_judgment": overall},
        "adjusted_criterion_judgments": judgments,
    }


def test_agreement_statistics_handles_prevalence_without_hiding_it():
    stats = agreement_statistics(
        ["Win", "Win", "Win", "Lose"],
        ["Win", "Win", "Lose", "Lose"],
    )
    assert stats["n_pairs"] == 4
    assert stats["exact_agreement"] == 0.75
    assert math.isclose(stats["cohen_kappa"], 0.5)
    assert 0.0 <= stats["gwet_ac1"] <= 1.0


def test_score_records_uses_win_only_and_macro_rubric_averaging():
    records = [_record("A", "Win"), _record("B", "Tie")]
    score = score_records(records)
    assert score["overall_judgment"] == {
        "win": 1,
        "tie": 1,
        "lose": 0,
        "win_rate": 0.5,
    }
    assert score["general"] == 0.5
    assert score["principles"]["Explanation"]["win_rate"] == 1.0
    assert score["principles"]["Explanation"]["n_candidate"] == 2

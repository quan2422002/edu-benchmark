from edu_benchmark.benchmark_conversion.corrections import apply_dialogue_corrections
from edu_benchmark.benchmark_conversion.last_turn_analysis import (
    analyze_last_student_turns,
    classify_final_student_turn,
)


def test_merge_adjacent_ai_turns_produces_valid_alternation():
    dialogue = "HS: Q\nAI: Hint\nHS: A\nAI: Part 1\nAI: Part 2\nHS: A2\nAI: End"
    correction = {
        "correction_id": "DCR-1",
        "operation": "merge_adjacent_turns",
        "target_turn_index": "4",
        "secondary_turn_index": "5",
        "replacement_role": "AI",
        "original_dialogue_sha256": (
            "e26397e1f6f290d91cc474c981c51b84fe8bd1376b8f2c2d4f26a741e4e8b314"
        ),
    }
    import hashlib

    correction["original_dialogue_sha256"] = hashlib.sha256(
        dialogue.encode("utf-8")
    ).hexdigest()
    corrected, ids = apply_dialogue_corrections(dialogue, [correction])
    assert "AI: Part 1\nPart 2" in corrected
    assert ids == ["DCR-1"]


def test_relabel_middle_student_turn_produces_valid_alternation():
    dialogue = "HS: Q\nAI: A\nHS: Q2\nHS: Tutor guidance\nHS: Student result\nAI: End"
    import hashlib

    correction = {
        "correction_id": "DCR-2",
        "operation": "relabel_turn",
        "target_turn_index": "4",
        "secondary_turn_index": "",
        "replacement_role": "AI",
        "original_dialogue_sha256": hashlib.sha256(
            dialogue.encode("utf-8")
        ).hexdigest(),
    }
    corrected, _ = apply_dialogue_corrections(dialogue, [correction])
    assert "AI: Tutor guidance" in corrected


def test_last_student_turn_classifier_does_not_treat_answers_as_empty_acknowledgements():
    category, _, treatment = classify_final_student_turn(
        "Dạ là dãy bit ạ!",
        'Đúng rồi, dãy đó được gọi là "dãy..." gì em nhỉ?',
    )
    assert category == "answer_or_explanation_to_tutor_prompt"
    assert treatment == "retain_as_trailing_student_outcome"


def test_last_student_turn_analysis_keeps_followup_questions_for_review():
    rows = [
        {
            "sample_id": "S1",
            "source_batch": "test",
            "source_file": "source.xlsx",
            "source_row_number": "2",
            "grade": "8",
            "lesson": "Bài 1",
            "conversion_dialogue": (
                "HS: Q\nAI: Gợi ý\nHS: Vậy đây là phép chia lấy nguyên đúng không thầy?"
            ),
        }
    ]
    analysis, summary = analyze_last_student_turns(rows)
    assert analysis[0]["heuristic_category"] == (
        "student_followup_or_confirmation_question"
    )
    assert analysis[0]["recommended_conversion_treatment"] == (
        "review_before_using_trailing_outcome_strategy"
    )
    assert summary["total_rows"] == 1


def test_project_lead_corrections_match_current_snapshot_and_fix_both_samples():
    import csv
    from pathlib import Path

    from edu_benchmark.benchmark_conversion.corrections import (
        load_dialogue_corrections,
    )
    from edu_benchmark.benchmark_conversion.dialogue_split import (
        parse_dialogue_turns,
    )

    repo_root = Path(__file__).resolve().parents[2]
    experiment = repo_root / "experiments" / "20260722_000940"
    corrections = load_dialogue_corrections(
        experiment / "outputs" / "benchmark_conversion" / "dialogue_corrections.csv"
    )
    source_paths = [
        experiment
        / "inherited_resources"
        / "from_20260709_155523"
        / "raw_audit_grade6_7"
        / "normalized_dialogue_rows.csv",
        experiment
        / "inherited_resources"
        / "from_20260709_155523"
        / "raw_audit_grade8_9"
        / "normalized_dialogue_rows.csv",
    ]
    source_rows = {}
    for path in source_paths:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            source_rows.update(
                {row["sample_id"]: row for row in csv.DictReader(handle)}
            )

    assert set(corrections) == {
        "HNMU-G7-R0189-STT6",
        "HNMU-G9-R0237-STT12",
    }
    for sample_id, instructions in corrections.items():
        corrected, applied = apply_dialogue_corrections(
            source_rows[sample_id]["dialogue"], instructions
        )
        assert len(applied) == 1
        assert parse_dialogue_turns(corrected)[-1].role == "tutor"

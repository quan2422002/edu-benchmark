from pathlib import Path

from edu_benchmark.dialogue_audit.fragment_score_analysis import FRAGMENT_METRICS, _summary_row
from edu_benchmark.dialogue_audit.fragment_score_analysis_repaired import (
    build_repaired_fragment_data,
    main_conclusion,
    prepare_analysis_rows,
)
from edu_benchmark.dialogue_audit.teacher_bundle import load_canonical_bundle_data
from edu_benchmark.dialogue_audit.teacher_bundle_v2 import STATUS_LABELS


EXPERIMENT_DIR = Path("experiments/20260709_155523")


def _analysis_rows():
    canonical = load_canonical_bundle_data(EXPERIMENT_DIR)
    repaired = build_repaired_fragment_data(canonical)
    return prepare_analysis_rows(repaired)


def test_grade_conclusions_use_only_auditor_group_control_and_actual_results():
    grade_rows, _ = _analysis_rows()

    expected_fragments = {
        "6": ("ước lượng được 8/8", "4 mối liên hệ có p-value dưới 0,05"),
        "7": ("ước lượng được 8/8", "5 mối liên hệ có p-value dưới 0,05"),
        "9": ("ước lượng được 6/8", "2/8 mối liên hệ còn lại không thể ước lượng"),
    }
    for grade, required_texts in expected_fragments.items():
        conclusion = main_conclusion(grade_rows[grade], pooled=False)
        assert f"Trong lớp {grade}" in conclusion
        assert "kiểm soát auditor_group trong lớp" in conclusion
        assert "kiểm soát khác biệt giữa khối" not in conclusion
        assert "kiểm soát đồng thời grade" not in conclusion
        assert "quan hệ nhân quả" in conclusion
        assert all(text in conclusion for text in required_texts)
        assert {
            row["adjustment"] for row in grade_rows[grade]
        } <= {"crude", "adjusted_for_auditor_group"}


def test_grade_8_conclusion_reports_all_adjusted_pairs_as_non_estimable():
    grade_rows, _ = _analysis_rows()
    rows = grade_rows["8"]
    adjusted = [
        _summary_row(rows, family, metric, "adjusted_for_auditor_group")
        for family in ("fragment_vs_official_pass", "fragment_vs_checklist_pass_rate")
        for metric in FRAGMENT_METRICS
    ]

    assert all(row is not None for row in adjusted)
    assert all(row["estimable"] is False for row in adjusted)
    assert all(row["sample_count"] == 0 for row in adjusted)
    assert all(row["strata_with_variation"] == 0 and row["strata_total"] == 6 for row in adjusted)
    conclusion = main_conclusion(rows, pooled=False)
    assert conclusion == (
        "Không thể ước lượng mối liên hệ sau điều chỉnh trong lớp 8 vì không có auditor_group nào "
        "đủ biến thiên đồng thời về outcome và metric fragment. Các kết quả thô không được xem là bằng chứng "
        "về mối liên hệ độc lập."
    )


def test_pooled_conclusion_and_official_status_label_remain_scope_correct():
    _, root_rows = _analysis_rows()
    pooled = [row for row in root_rows if row["grade"] == "all"]
    conclusion = main_conclusion(root_rows, pooled=True)

    assert "kiểm soát đồng thời grade và auditor_group" in conclusion
    assert "ước lượng được 8/8" in conclusion
    assert any(
        row["adjustment"] == "adjusted_for_grade_and_auditor_group"
        for row in pooled
    )
    assert STATUS_LABELS["pass"] == "Đạt theo trạng thái tổng thể chính thức"

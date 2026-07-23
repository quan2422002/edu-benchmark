import pytest

from edu_benchmark.benchmark_conversion.input_selection import (
    AuditSnapshot,
    SnapshotContractError,
    aggregate_all_raw_audit_evidence,
    build_pass_conversion_input,
    normalize_blocking_evidence,
    select_conversion_pilot,
)


def checklist_rows(sample_id="S1", *, fragments=("F2", "F1", "F2")):
    rows = []
    for index in range(18):
        rows.append(
            {
                "sample_id": sample_id,
                "criterion_id": f"C{index:02d}",
                "result": "pass",
                "evidence_fragment_id": fragments[index] if index < len(fragments) else "",
            }
        )
    return rows


def normalized_row(sample_id="S1", grade="6"):
    return {
        "sample_id": sample_id,
        "source_file": "source.xlsx",
        "source_row_number": "2",
        "grade": grade,
        "grade_label": f"Lớp {grade}",
        "stt": "1",
        "lesson": "Bài 1",
        "position": "Mục 1",
        "question": "Q",
        "bloom_level": "Nhận biết",
        "answer_sgv": "A",
        "dialogue": "HS: Q\nAI: A",
    }


def quality_row(sample_id="S1", decision="pass"):
    return {
        "sample_id": sample_id,
        "quality_decision": decision,
        "confidence_score": "0.9",
        "blocking_criterion_ids": "",
        "evidence_fragment_ids": "",
    }


def test_all_evidence_union_is_stable_and_deduplicated():
    evidence, counts = aggregate_all_raw_audit_evidence(
        checklist_rows(fragments=("F2;F1", "F1", "F2"))
    )
    assert evidence == {"S1": ["F1", "F2"]}
    assert counts == {"S1": 18}


def test_blocking_evidence_preserves_phase1_sample_level_semantics():
    assert normalize_blocking_evidence("") == "[]"
    assert normalize_blocking_evidence("F2;F1;F2") == '["F1", "F2"]'


def test_join_rejects_missing_and_duplicate_sample_ids():
    snapshot = AuditSnapshot(
        source_batch="test",
        normalized_rows=[normalized_row()],
        quality_rows=[quality_row("OTHER")],
        checklist_rows=checklist_rows(),
    )
    with pytest.raises(SnapshotContractError, match="do not align"):
        build_pass_conversion_input([snapshot])

    duplicate = AuditSnapshot(
        source_batch="test",
        normalized_rows=[normalized_row(), normalized_row()],
        quality_rows=[quality_row()],
        checklist_rows=checklist_rows(),
    )
    with pytest.raises(SnapshotContractError, match="duplicate sample_id"):
        build_pass_conversion_input([duplicate])


def test_gold_answer_source_is_preserved_as_answer_sgv():
    snapshot = AuditSnapshot(
        source_batch="test",
        normalized_rows=[normalized_row()],
        quality_rows=[quality_row()],
        checklist_rows=checklist_rows(),
    )
    rows, errors = build_pass_conversion_input([snapshot])
    assert errors == []
    assert rows[0]["answer_sgv"] == "A"


def test_pilot_selection_is_reproducible_and_balanced_on_real_snapshot():
    from pathlib import Path

    from edu_benchmark.benchmark_conversion.pipeline import default_snapshot_specs
    from edu_benchmark.benchmark_conversion.input_selection import load_audit_snapshot

    root = Path(__file__).resolve().parents[2] / "experiments" / "20260722_000940"
    snapshots = [
        load_audit_snapshot(
            source_batch=str(spec["source_batch"]),
            normalized_path=spec["normalized_path"],
            quality_path=spec["quality_path"],
            checklist_path=spec["checklist_path"],
        )
        for spec in default_snapshot_specs(root)
    ]
    rows, errors = build_pass_conversion_input(snapshots)
    assert len(rows) == 665
    assert errors == []
    selected_a, _ = select_conversion_pilot(rows, size_per_grade=10)
    selected_b, _ = select_conversion_pilot(list(reversed(rows)), size_per_grade=10)
    assert [row["sample_id"] for row in selected_a] == [
        row["sample_id"] for row in selected_b
    ]
    assert {
        grade: sum(row["grade"] == grade for row in selected_a)
        for grade in ("6", "7", "8", "9")
    } == {"6": 10, "7": 10, "8": 10, "9": 10}

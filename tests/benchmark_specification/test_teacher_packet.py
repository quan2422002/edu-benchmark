from pathlib import Path

from edu_benchmark.benchmark_specification.teacher_packet import (
    REQUIRED_PACKET_FILES,
    LEGACY_EIGHT_TASK_CODEBOOK_PACKET_FILES,
    validate_workstream_b_teacher_packet,
    validate_legacy_eight_task_codebook_gate,
)
from edu_benchmark.benchmark_specification.schema import TASK_COLUMNS


def _write_packet(root: Path, *, provisional: bool) -> None:
    root.mkdir(parents=True)
    for filename in REQUIRED_PACKET_FILES:
        path = root / filename
        if filename.endswith(".md"):
            headings = ""
            if "task_card" in filename:
                headings = "\n".join(
                    f"## {heading}"
                    for heading in (
                        "Mục tiêu",
                        "Vì sao cần nhiệm vụ này",
                        "Bạn nhận được gì",
                        "Các bước thực hiện",
                        "Ví dụ đạt yêu cầu",
                        "Ví dụ cần sửa",
                        "Bạn cần nộp gì",
                        "Checklist tự kiểm tra",
                        "Thời gian dự kiến",
                        "Khi cần hỗ trợ",
                    )
                )
            path.write_text(f"# Test\n{headings}\n", encoding="utf-8")
    if provisional:
        review = (
            "CAP-A,UET-PROJECT-REP,yes,enough,clear,observable,retain,"
            "rationale,uet_provisional_approved\n"
        )
        overlap = (
            "CAP-A,CAP-B,UET-PROJECT-REP,distinct,retain,rationale,"
            "uet_provisional_approved\n"
        )
        adjudication = (
            "D-1,overlap,CAP-A,CAP-B,UET-PROJECT-REP,retain,rationale,"
            "uet_provisional_approved\n"
        )
    else:
        review = "CAP-A,,,,,,,,not_started\n"
        overlap = "CAP-A,CAP-B,,,,,not_started\n"
        adjudication = ""
    (root / "capability_review_decisions.csv").write_text(
        "capability_id,reviewer_id,relevance_decision,"
        "comprehensiveness_decision,comprehensibility_decision,"
        "one_response_observable_decision,proposed_action,rationale,"
        f"decision_status\n{review}",
        encoding="utf-8",
    )
    (root / "capability_overlap_review_decisions.csv").write_text(
        "capability_id_a,capability_id_b,reviewer_id,overlap_decision,"
        f"proposed_action,rationale,decision_status\n{overlap}",
        encoding="utf-8",
    )
    (root / "capability_adjudication_decisions.csv").write_text(
        "decision_id,item_type,item_id_a,item_id_b,adjudicator_id,"
        f"adjudicated_action,rationale,decision_status\n{adjudication}",
        encoding="utf-8",
    )


def test_teacher_packet_accepts_initial_state(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    _write_packet(packet, provisional=False)
    assert (
        validate_workstream_b_teacher_packet(
            packet,
            capability_ids={"CAP-A"},
            overlap_pairs={("CAP-A", "CAP-B")},
        )
        == []
    )


def test_teacher_packet_accepts_recorded_uet_provisional_gate(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    _write_packet(packet, provisional=True)
    assert (
        validate_workstream_b_teacher_packet(
            packet,
            capability_ids={"CAP-A"},
            overlap_pairs={("CAP-A", "CAP-B")},
        )
        == []
    )


def _write_legacy_eight_task_codebook_gate(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True)
    for filename in LEGACY_EIGHT_TASK_CODEBOOK_PACKET_FILES:
        path = root / filename
        if filename.endswith(".md"):
            headings = ""
            if "task_card" in filename:
                headings = "\n".join(
                    f"## {heading}"
                    for heading in (
                        "Mục tiêu",
                        "Vì sao cần nhiệm vụ này",
                        "Bạn nhận được gì",
                        "Các bước thực hiện",
                        "Ví dụ đạt yêu cầu",
                        "Ví dụ cần sửa",
                        "Bạn cần nộp gì",
                        "Checklist tự kiểm tra",
                        "Thời gian dự kiến",
                        "Khi cần hỗ trợ",
                    )
                )
            path.write_text(f"# Test\n{headings}\n", encoding="utf-8")
    task_ids = (
        "TASK-PROBE",
        "TASK-EXPLAIN",
        "TASK-ASSESS",
        "TASK-DIAG",
        "TASK-SCAFFOLD",
        "TASK-MODEL",
        "TASK-PRACTICE",
        "TASK-CONSOLIDATE",
    )
    task_path = root.parent / "benchmark_tasks.csv"
    task_lines = [",".join(TASK_COLUMNS)]
    for task_id in task_ids:
        task_lines.append(
            ",".join(
                (
                    task_id,
                    f"Name {task_id}",
                    "Definition",
                    "Scope",
                    "Student state",
                    "Goal",
                    "Evidence",
                    "Input",
                    "Output",
                    "needs_uet_review",
                    "TR-P001",
                    "",
                    "Review",
                )
            )
        )
    task_path.write_text("\n".join(task_lines) + "\n", encoding="utf-8")
    codebook_path = root.parent / "codebook.md"
    codebook_path.write_text(
        "chờ đại diện UET duyệt\n"
        "required_response_evidence evidence_fragment_ids\n"
        "Ví dụ đạt Phản ví dụ Trường hợp chưa phân loại\n"
        "Số ứng viên mã hóa chính thức\n"
        + "\n".join(task_ids),
        encoding="utf-8",
    )
    task_rows = "\n".join(f"{task_id},,,,,,,not_started" for task_id in task_ids)
    (root / "task_review_decisions.csv").write_text(
        ",".join(
            (
                "task_id",
                "reviewer_id",
                "definition_clarity_decision",
                "distinct_contract_decision",
                "observable_evidence_decision",
                "proposed_action",
                "rationale",
                "decision_status",
            )
        )
        + "\n"
        + task_rows
        + "\n",
        encoding="utf-8",
    )
    boundary_rows = (
        "B01,TASK-ASSESS,TASK-CONSOLIDATE,,,,,not_started\n"
        "B02,TASK-ASSESS,TASK-DIAG,,,,,not_started\n"
        "B03,TASK-CONSOLIDATE,TASK-PRACTICE,,,,,not_started\n"
        "B04,TASK-DIAG,TASK-PROBE,,,,,not_started\n"
        "B05,TASK-EXPLAIN,TASK-MODEL,,,,,not_started\n"
        "B06,TASK-EXPLAIN,TASK-SCAFFOLD,,,,,not_started\n"
        "B07,TASK-MODEL,TASK-SCAFFOLD,,,,,not_started\n"
    )
    (root / "task_boundary_review_decisions.csv").write_text(
        ",".join(
            (
                "boundary_id",
                "task_id_a",
                "task_id_b",
                "reviewer_id",
                "boundary_clarity_decision",
                "proposed_rule",
                "rationale",
                "decision_status",
            )
        )
        + "\n"
        + boundary_rows,
        encoding="utf-8",
    )
    (root / "codebook_gate_decision.csv").write_text(
        "gate_id,reviewer_id,gate_decision,conditions,rationale,"
        "decision_status\nPLAN03-C1,,,,,not_started\n",
        encoding="utf-8",
    )
    return task_path, codebook_path


def test_legacy_eight_task_codebook_gate_accepts_initial_packet(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    task_path, codebook_path = _write_legacy_eight_task_codebook_gate(packet)
    assert (
        validate_legacy_eight_task_codebook_gate(
            packet,
            task_path=task_path,
            codebook_path=codebook_path,
        )
        == []
    )


def test_legacy_eight_task_codebook_gate_rejects_prepopulated_initial_decision(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    task_path, codebook_path = _write_legacy_eight_task_codebook_gate(packet)
    decision_path = packet / "codebook_gate_decision.csv"
    decision_path.write_text(
        "gate_id,reviewer_id,gate_decision,conditions,rationale,"
        "decision_status\n"
        "PLAN03-C1,UET-REVIEWER-01,,,,not_started\n",
        encoding="utf-8",
    )
    errors = validate_legacy_eight_task_codebook_gate(
        packet,
        task_path=task_path,
        codebook_path=codebook_path,
    )
    assert "codebook_gate:partial_initial:reviewer_id" in errors

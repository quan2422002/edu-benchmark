"""Validation for the Plan-03 Workstream-B teacher consultation packet."""

from __future__ import annotations

from pathlib import Path

from .schema import read_csv_rows, validate_exact_header, validate_tasks

REQUIRED_PACKET_FILES = {
    "README.md",
    "capability_review_task_card.md",
    "capability_review_guide.md",
    "capability_research_basis.md",
    "capability_review_decisions.csv",
    "capability_overlap_review_decisions.csv",
    "capability_adjudication_task_card.md",
    "capability_adjudication_decisions.csv",
    "consultation_questions.md",
}

REQUIRED_TASK_HEADINGS = (
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

CAPABILITY_REVIEW_COLUMNS = [
    "capability_id",
    "reviewer_id",
    "relevance_decision",
    "comprehensiveness_decision",
    "comprehensibility_decision",
    "one_response_observable_decision",
    "proposed_action",
    "rationale",
    "decision_status",
]

OVERLAP_REVIEW_COLUMNS = [
    "capability_id_a",
    "capability_id_b",
    "reviewer_id",
    "overlap_decision",
    "proposed_action",
    "rationale",
    "decision_status",
]

ADJUDICATION_COLUMNS = [
    "decision_id",
    "item_type",
    "item_id_a",
    "item_id_b",
    "adjudicator_id",
    "adjudicated_action",
    "rationale",
    "decision_status",
]

LEGACY_EIGHT_TASK_CODEBOOK_PACKET_FILES = {
    "README.md",
    "task_codebook_review_task_card.md",
    "task_review_decisions.csv",
    "task_boundary_review_decisions.csv",
    "codebook_gate_decision.csv",
}

LEGACY_TASK_REVIEW_COLUMNS = [
    "task_id",
    "reviewer_id",
    "definition_clarity_decision",
    "distinct_contract_decision",
    "observable_evidence_decision",
    "proposed_action",
    "rationale",
    "decision_status",
]

LEGACY_TASK_BOUNDARY_REVIEW_COLUMNS = [
    "boundary_id",
    "task_id_a",
    "task_id_b",
    "reviewer_id",
    "boundary_clarity_decision",
    "proposed_rule",
    "rationale",
    "decision_status",
]

LEGACY_CODEBOOK_GATE_COLUMNS = [
    "gate_id",
    "reviewer_id",
    "gate_decision",
    "conditions",
    "rationale",
    "decision_status",
]

LEGACY_EIGHT_TASK_BOUNDARIES = {
    ("TASK-ASSESS", "TASK-CONSOLIDATE"),
    ("TASK-ASSESS", "TASK-DIAG"),
    ("TASK-CONSOLIDATE", "TASK-PRACTICE"),
    ("TASK-DIAG", "TASK-PROBE"),
    ("TASK-EXPLAIN", "TASK-MODEL"),
    ("TASK-EXPLAIN", "TASK-SCAFFOLD"),
    ("TASK-MODEL", "TASK-SCAFFOLD"),
}


def validate_workstream_b_teacher_packet(
    packet_root: Path,
    *,
    capability_ids: set[str],
    overlap_pairs: set[tuple[str, str]],
) -> list[str]:
    """Validate an untouched packet or its recorded UET provisional gate."""

    errors: list[str] = []
    if not packet_root.is_dir():
        return [f"packet_not_found:{packet_root}"]
    actual_files = {path.name for path in packet_root.iterdir() if path.is_file()}
    if actual_files != REQUIRED_PACKET_FILES:
        errors.append(
            "packet_inventory_mismatch:"
            f"missing={sorted(REQUIRED_PACKET_FILES - actual_files)}:"
            f"extra={sorted(actual_files - REQUIRED_PACKET_FILES)}"
        )
    for task_card in (
        "capability_review_task_card.md",
        "capability_adjudication_task_card.md",
    ):
        path = packet_root / task_card
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for heading in REQUIRED_TASK_HEADINGS:
            if f"## {heading}" not in content:
                errors.append(f"{task_card}:missing_heading:{heading}")

    review_path = packet_root / "capability_review_decisions.csv"
    overlap_path = packet_root / "capability_overlap_review_decisions.csv"
    adjudication_path = packet_root / "capability_adjudication_decisions.csv"
    for path, header in (
        (review_path, CAPABILITY_REVIEW_COLUMNS),
        (overlap_path, OVERLAP_REVIEW_COLUMNS),
        (adjudication_path, ADJUDICATION_COLUMNS),
    ):
        if path.is_file():
            errors.extend(validate_exact_header(path, header))
    if errors:
        return errors

    review_rows = read_csv_rows(review_path)
    if {row["capability_id"] for row in review_rows} != capability_ids:
        errors.append("capability_review_id_coverage_mismatch")
    for index, row in enumerate(review_rows, start=2):
        status = row["decision_status"]
        decision_fields = CAPABILITY_REVIEW_COLUMNS[1:-1]
        if status == "not_started":
            for field in decision_fields:
                if row[field]:
                    errors.append(
                        f"capability_review_row_{index}:partial_initial:{field}"
                    )
        elif status == "uet_provisional_approved":
            if row["reviewer_id"] != "UET-PROJECT-REP":
                errors.append(
                    f"capability_review_row_{index}:invalid_uet_reviewer"
                )
            for field in decision_fields:
                if not row[field]:
                    errors.append(
                        f"capability_review_row_{index}:missing:{field}"
                    )
        else:
            errors.append(
                f"capability_review_row_{index}:invalid_decision_status"
            )

    overlap_rows = read_csv_rows(overlap_path)
    actual_pairs = {
        tuple(sorted((row["capability_id_a"], row["capability_id_b"])))
        for row in overlap_rows
    }
    if actual_pairs != overlap_pairs or len(overlap_rows) != len(overlap_pairs):
        errors.append("overlap_review_pair_coverage_mismatch")
    for index, row in enumerate(overlap_rows, start=2):
        status = row["decision_status"]
        decision_fields = OVERLAP_REVIEW_COLUMNS[2:-1]
        if status == "not_started":
            for field in decision_fields:
                if row[field]:
                    errors.append(
                        f"overlap_review_row_{index}:partial_initial:{field}"
                    )
        elif status == "uet_provisional_approved":
            if row["reviewer_id"] != "UET-PROJECT-REP":
                errors.append(
                    f"overlap_review_row_{index}:invalid_uet_reviewer"
                )
            for field in decision_fields:
                if not row[field]:
                    errors.append(
                        f"overlap_review_row_{index}:missing:{field}"
                    )
        else:
            errors.append(
                f"overlap_review_row_{index}:invalid_decision_status"
            )

    for index, row in enumerate(read_csv_rows(adjudication_path), start=2):
        if row["decision_status"] != "uet_provisional_approved":
            errors.append(
                f"adjudication_row_{index}:invalid_decision_status"
            )
        if row["adjudicator_id"] != "UET-PROJECT-REP":
            errors.append(f"adjudication_row_{index}:invalid_uet_adjudicator")
        for field in ADJUDICATION_COLUMNS[:-1]:
            if not row[field]:
                errors.append(f"adjudication_row_{index}:missing:{field}")
        pair = tuple(sorted((row["item_id_a"], row["item_id_b"])))
        if pair not in overlap_pairs:
            errors.append(f"adjudication_row_{index}:unknown_pair")
    return errors


def validate_legacy_eight_task_codebook_gate(
    packet_root: Path,
    *,
    task_path: Path,
    codebook_path: Path,
) -> list[str]:
    """Validate the retired eight-task C1 packet for historical integrity."""

    errors: list[str] = []
    if not packet_root.is_dir():
        return [f"packet_not_found:{packet_root}"]
    actual_files = {path.name for path in packet_root.iterdir() if path.is_file()}
    if actual_files != LEGACY_EIGHT_TASK_CODEBOOK_PACKET_FILES:
        errors.append(
            "packet_inventory_mismatch:"
            f"missing={sorted(LEGACY_EIGHT_TASK_CODEBOOK_PACKET_FILES - actual_files)}:"
            f"extra={sorted(actual_files - LEGACY_EIGHT_TASK_CODEBOOK_PACKET_FILES)}"
        )
    if not task_path.is_file():
        errors.append(f"task_file_not_found:{task_path}")
    if not codebook_path.is_file():
        errors.append(f"codebook_not_found:{codebook_path}")
    task_card = packet_root / "task_codebook_review_task_card.md"
    if task_card.is_file():
        content = task_card.read_text(encoding="utf-8")
        for heading in REQUIRED_TASK_HEADINGS:
            if f"## {heading}" not in content:
                errors.append(
                    f"task_codebook_review_task_card.md:missing_heading:{heading}"
                )
    for path, header in (
        (packet_root / "task_review_decisions.csv", LEGACY_TASK_REVIEW_COLUMNS),
        (
            packet_root / "task_boundary_review_decisions.csv",
            LEGACY_TASK_BOUNDARY_REVIEW_COLUMNS,
        ),
        (packet_root / "codebook_gate_decision.csv", LEGACY_CODEBOOK_GATE_COLUMNS),
    ):
        if path.is_file():
            errors.extend(validate_exact_header(path, header))
    if errors:
        return errors

    task_rows = read_csv_rows(task_path)
    errors.extend(validate_tasks(task_rows))
    task_ids = {row["task_id"] for row in task_rows}
    if len(task_ids) != 8:
        errors.append(f"expected_eight_task_seeds:actual={len(task_ids)}")
    if any(row["status"] != "needs_uet_review" for row in task_rows):
        errors.append("task_seed_status_must_be_needs_uet_review")

    codebook = codebook_path.read_text(encoding="utf-8")
    required_codebook_markers = (
        "chờ đại diện UET duyệt",
        "required_response_evidence",
        "evidence_fragment_ids",
        "Ví dụ đạt",
        "Phản ví dụ",
        "Trường hợp chưa phân loại",
        "Số ứng viên mã hóa chính thức",
    )
    for marker in required_codebook_markers:
        if marker not in codebook:
            errors.append(f"codebook_missing_marker:{marker}")
    for task_id in task_ids:
        if task_id not in codebook:
            errors.append(f"codebook_missing_task:{task_id}")

    review_rows = read_csv_rows(packet_root / "task_review_decisions.csv")
    if {row["task_id"] for row in review_rows} != task_ids:
        errors.append("task_review_id_coverage_mismatch")
    if len(review_rows) != len(task_ids):
        errors.append("task_review_rows_duplicated")
    for index, row in enumerate(review_rows, start=2):
        status = row["decision_status"]
        decision_fields = LEGACY_TASK_REVIEW_COLUMNS[1:-1]
        if status == "not_started":
            for field in decision_fields:
                if row[field]:
                    errors.append(
                        f"task_review_row_{index}:partial_initial:{field}"
                    )
        elif status == "uet_codebook_approved":
            if row["reviewer_id"] != "UET-REVIEWER-01":
                errors.append(
                    f"task_review_row_{index}:invalid_uet_reviewer"
                )
            for field in decision_fields:
                if not row[field]:
                    errors.append(f"task_review_row_{index}:missing:{field}")
        else:
            errors.append(f"task_review_row_{index}:invalid_decision_status")

    boundary_rows = read_csv_rows(
        packet_root / "task_boundary_review_decisions.csv"
    )
    actual_boundaries = {
        tuple(sorted((row["task_id_a"], row["task_id_b"])))
        for row in boundary_rows
    }
    if (
        actual_boundaries != LEGACY_EIGHT_TASK_BOUNDARIES
        or len(boundary_rows) != len(LEGACY_EIGHT_TASK_BOUNDARIES)
    ):
        errors.append("task_boundary_coverage_mismatch")
    for index, row in enumerate(boundary_rows, start=2):
        status = row["decision_status"]
        decision_fields = LEGACY_TASK_BOUNDARY_REVIEW_COLUMNS[3:-1]
        if status == "not_started":
            for field in decision_fields:
                if row[field]:
                    errors.append(
                        f"task_boundary_row_{index}:partial_initial:{field}"
                    )
        elif status == "uet_codebook_approved":
            if row["reviewer_id"] != "UET-REVIEWER-01":
                errors.append(
                    f"task_boundary_row_{index}:invalid_uet_reviewer"
                )
            for field in decision_fields:
                if not row[field]:
                    errors.append(
                        f"task_boundary_row_{index}:missing:{field}"
                    )
        else:
            errors.append(
                f"task_boundary_row_{index}:invalid_decision_status"
            )

    gate_rows = read_csv_rows(packet_root / "codebook_gate_decision.csv")
    if len(gate_rows) != 1 or gate_rows[0]["gate_id"] != "PLAN03-C1":
        errors.append("codebook_gate_must_have_one_plan03_c1_row")
    else:
        gate = gate_rows[0]
        if gate["decision_status"] == "not_started":
            for field in LEGACY_CODEBOOK_GATE_COLUMNS[1:-1]:
                if gate[field]:
                    errors.append(f"codebook_gate:partial_initial:{field}")
        elif gate["decision_status"] == "uet_codebook_approved":
            if gate["reviewer_id"] != "UET-REVIEWER-01":
                errors.append("codebook_gate:invalid_uet_reviewer")
            if gate["gate_decision"] not in {
                "approve_for_first_batch",
                "approve_with_conditions",
            }:
                errors.append("codebook_gate:invalid_gate_decision")
            for field in ("reviewer_id", "gate_decision", "rationale"):
                if not gate[field]:
                    errors.append(f"codebook_gate:missing:{field}")
        else:
            errors.append("codebook_gate:invalid_decision_status")
    return errors

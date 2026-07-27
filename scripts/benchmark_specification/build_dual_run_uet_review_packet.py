#!/usr/bin/env python3
"""Build a deterministic UET review packet from two closed v3 bundles."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def principle_sets(path: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for row in read_csv(path):
        result.setdefault(row["benchmark_candidate_id"], set()).add(
            row["principle_id"]
        )
    return result


def set_text(values: set[str]) -> str:
    return ";".join(sorted(values))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--bundle-a", type=Path, required=True)
    parser.add_argument("--bundle-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--agreed-audit-count", type=int, default=8)
    args = parser.parse_args()

    inputs = read_csv(args.input_dir / "principle_annotation_grounding_input.csv")
    rows_a = read_csv(args.bundle_a / "principle_annotation_final.csv")
    rows_b = read_csv(args.bundle_b / "principle_annotation_final.csv")
    sets_a = principle_sets(args.bundle_a / "principle_annotation_final_labels.csv")
    sets_b = principle_sets(args.bundle_b / "principle_annotation_final_labels.csv")
    by_input = {row["benchmark_candidate_id"]: row for row in inputs}
    by_b = {row["benchmark_candidate_id"]: row for row in rows_b}
    if [row["benchmark_candidate_id"] for row in rows_a] != [
        row["benchmark_candidate_id"] for row in rows_b
    ]:
        raise ValueError("Annotator bundles have different candidate order")

    required = []
    agreed_pool = []
    for row_a in rows_a:
        candidate_id = row_a["benchmark_candidate_id"]
        row_b = by_b[candidate_id]
        set_a = sets_a.get(candidate_id, set())
        set_b = sets_b.get(candidate_id, set())
        reasons = []
        if set_a != set_b:
            reasons.append("agent_label_set_disagreement")
        if row_a["grounding_effect"] != row_b["grounding_effect"]:
            reasons.append("grounding_effect_disagreement")
        if (
            bool(row_a["coverage_gap_reason"])
            != bool(row_b["coverage_gap_reason"])
        ):
            reasons.append("coverage_gap_disagreement")
        if (
            row_a["grounding_effect"] == "conflict"
            or row_b["grounding_effect"] == "conflict"
        ):
            reasons.append("context_grounding_conflict")
        if len(set_a) > 3 or len(set_b) > 3:
            reasons.append("high_label_count")
        item = (";".join(reasons), row_a, row_b, set_a, set_b)
        (required if reasons else agreed_pool).append(item)

    salt = "plan03-c0b-v3-agreed-audit-v1"
    agreed_pool.sort(
        key=lambda item: hashlib.sha256(
            f"{salt}:{item[1]['benchmark_candidate_id']}".encode()
        ).hexdigest()
    )
    selected_agreed = agreed_pool[: args.agreed_audit_count]
    if len(selected_agreed) < args.agreed_audit_count:
        raise ValueError("Not enough agreement rows for requested audit sample")

    output_rows = []
    selected = required + [
        ("deterministic_agreement_audit", a, b, set_a, set_b)
        for _, a, b, set_a, set_b in selected_agreed
    ]
    for reason, row_a, row_b, set_a, set_b in selected:
        candidate_id = row_a["benchmark_candidate_id"]
        source = by_input[candidate_id]
        output_rows.append(
            {
                "review_order": len(output_rows) + 1,
                "review_reason_codes": reason,
                "benchmark_candidate_id": candidate_id,
                "sample_id": row_a["sample_id"],
                "grade": source["grade"],
                "lesson": source["lesson"],
                "student_prompt": source["student_prompt"],
                "conversation_history": source["conversation_history"],
                "source_question": source["source_question"],
                "gold_answer": source["gold_answer"],
                "annotator_a_principle_set": set_text(set_a),
                "annotator_a_grounding_effect": row_a["grounding_effect"],
                "annotator_a_grounding_change_reason": row_a[
                    "grounding_change_reason"
                ],
                "annotator_a_coverage_gap_reason": row_a["coverage_gap_reason"],
                "annotator_b_principle_set": set_text(set_b),
                "annotator_b_grounding_effect": row_b["grounding_effect"],
                "annotator_b_grounding_change_reason": row_b[
                    "grounding_change_reason"
                ],
                "annotator_b_coverage_gap_reason": row_b["coverage_gap_reason"],
                "uet_final_principle_set": "",
                "uet_grounding_effect_decision": "",
                "uet_decision": "",
                "uet_note": "",
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = args.output_dir / "dual_run_uet_review.csv"
    with packet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    summary = {
        "summary_version": "plan03-c0b-uet-review-packet-v3",
        "candidate_count": len(rows_a),
        "required_review_count": len(required),
        "agreement_audit_count": len(selected_agreed),
        "packet_row_count": len(output_rows),
        "selection_salt": salt,
        "status": "needs_uet_review",
    }
    (args.output_dir / "selection_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Synchronize sample-level audit suggestions from criterion-level checklist rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from edu_benchmark.dialogue_audit.checklist_aggregation import (
    CANONICAL_QUALITY_COLUMNS,
    build_canonical_quality_rows,
    build_review_queue_rows,
    build_sample_aggregates,
    read_csv_rows,
    sync_quality_rows,
    write_csv_rows,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        None.

    Returns:
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Regenerate quality_check_suggestions.csv and "
            "hnmu_review_queue_suggestions.csv from raw_dialogue_checklist_results.csv."
        )
    )
    parser.add_argument("--checklist", required=True, type=Path, help="Detailed checklist CSV path.")
    parser.add_argument("--quality-template", required=True, type=Path, help="Existing quality CSV to preserve metadata columns.")
    parser.add_argument("--review-template", required=True, type=Path, help="Existing review queue CSV to preserve columns.")
    parser.add_argument(
        "--normalized-rows",
        type=Path,
        help="Optional normalized_dialogue_rows.csv used to enrich canonical quality rows.",
    )
    parser.add_argument("--output-quality", required=True, type=Path, help="Destination quality CSV path.")
    parser.add_argument("--output-review-queue", required=True, type=Path, help="Destination review queue CSV path.")
    parser.add_argument("--summary-json", type=Path, help="Optional JSON summary path.")
    parser.add_argument(
        "--decision-column",
        required=True,
        help="Decision column in quality CSV. Current Plan 04 outputs use quality_decision.",
    )
    parser.add_argument(
        "--pass-label",
        default="pass",
        help="Label for clean-pass samples. Current Plan 04 outputs must use pass.",
    )
    parser.add_argument(
        "--medium-priority-label",
        default="medium",
        help="Review queue priority label for need_human_review samples.",
    )
    parser.add_argument(
        "--high-priority-label",
        default="high",
        help="Review queue priority label for failed samples.",
    )
    parser.add_argument(
        "--checked-by",
        default="orchestrator-strict-aggregate-sync-from-checklist",
        help="Identifier written to checked_by columns.",
    )
    parser.add_argument(
        "--checked-at",
        default=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(microsecond=0).isoformat(),
        help="Timestamp written to checked_at columns.",
    )
    parser.add_argument(
        "--canonical-quality-schema",
        action="store_true",
        help="Write quality_check_suggestions.csv with the shared canonical sample-level schema.",
    )
    return parser.parse_args()


def main() -> int:
    """Run strict checklist-to-sample synchronization.

    Args:
        None.

    Returns:
        Process exit code. ``0`` means success.
    """

    args = parse_args()
    _, checklist_rows = read_csv_rows(args.checklist)
    quality_columns, quality_rows = read_csv_rows(args.quality_template)
    review_columns, _ = read_csv_rows(args.review_template)
    normalized_by_sample: dict[str, dict[str, str]] = {}
    if args.normalized_rows:
        _, normalized_rows = read_csv_rows(args.normalized_rows)
        normalized_by_sample = {row["sample_id"]: row for row in normalized_rows if row.get("sample_id")}

    aggregates = build_sample_aggregates(checklist_rows, pass_label=args.pass_label)
    if args.canonical_quality_schema:
        existing_quality_by_sample = {
            row["sample_id"]: row for row in quality_rows if row.get("sample_id")
        }
        sample_ids = [row["sample_id"] for row in quality_rows if row.get("sample_id")]
        synced_quality_rows = build_canonical_quality_rows(
            sample_ids,
            aggregates,
            sample_metadata=normalized_by_sample,
            existing_quality_rows=existing_quality_by_sample,
            checked_by=args.checked_by,
            checked_at=args.checked_at,
        )
        quality_columns = CANONICAL_QUALITY_COLUMNS
        decision_column = "quality_decision"
    else:
        synced_quality_rows = sync_quality_rows(
            quality_rows,
            aggregates,
            decision_column=args.decision_column,
            checked_by=args.checked_by,
            checked_at=args.checked_at,
        )
        decision_column = args.decision_column
    review_queue_rows = build_review_queue_rows(
        synced_quality_rows,
        aggregates,
        fieldnames=review_columns,
        decision_column=decision_column,
        checked_by=args.checked_by,
        checked_at=args.checked_at,
        medium_priority_label=args.medium_priority_label,
        high_priority_label=args.high_priority_label,
    )

    write_csv_rows(args.output_quality, quality_columns, synced_quality_rows)
    write_csv_rows(args.output_review_queue, review_columns, review_queue_rows)

    summary = {
        "checklist": args.checklist.as_posix(),
        "output_quality": args.output_quality.as_posix(),
        "output_review_queue": args.output_review_queue.as_posix(),
        "sample_count": len(synced_quality_rows),
        "checklist_row_count": len(checklist_rows),
        "decision_counts": dict(Counter(row[decision_column] for row in synced_quality_rows)),
        "review_queue_count": len(review_queue_rows),
        "pass_label": args.pass_label,
        "decision_column": decision_column,
        "canonical_quality_schema": args.canonical_quality_schema,
        "checked_by": args.checked_by,
        "checked_at": args.checked_at,
    }
    if args.summary_json:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

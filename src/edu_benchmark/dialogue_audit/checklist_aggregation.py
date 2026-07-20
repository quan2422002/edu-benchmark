"""Aggregate per-criterion raw-dialogue audit rows into sample-level suggestions.

The detailed checklist file is the source of truth. This module implements the
strict Plan 04 aggregation rule that was aligned with the synchronized grade
8--9 audit run: sample-level suggestions must be derived mechanically from
criterion-level decisions, not re-interpreted independently.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

CRITERION_RESULTS = {"pass", "fail", "uncertain", "not_applicable"}
DEFAULT_CHECKED_BY = "orchestrator-strict-aggregate-sync-from-checklist"
DEFAULT_REVIEW_QUESTION = (
    "Vui lòng kiểm tra và quyết định mẫu này cần sửa, loại khỏi batch hiện tại, "
    "hay giữ lại sau khi chỉnh."
)
CANONICAL_QUALITY_COLUMNS = [
    "sample_id",
    "source_file",
    "source_row_number",
    "grade",
    "lesson",
    "quality_decision",
    "confidence_score",
    "failure_reasons",
    "blocking_criterion_ids",
    "suggested_reviewer_action",
    "needs_hnmu_review",
    "needs_learning_resource_review",
    "needs_sgv_verification",
    "evidence_fragment_ids",
    "checked_by",
    "checked_at",
    "source_shard",
]


@dataclass(frozen=True)
class SampleAggregate:
    """Sample-level result derived from one sample's checklist rows.

    Attributes:
        sample_id: Stable sample identifier.
        decision: Sample-level decision. The strict rule is: any failed
            criterion makes the sample ``failed``; otherwise any uncertain
            criterion makes the sample ``need_human_review``; otherwise the
            sample uses the configured pass label.
        confidence_score: Confidence in the sample-level decision. For
            ``failed`` it is the lowest confidence among failed criteria; for
            ``need_human_review`` it is the lowest confidence among uncertain
            criteria; for pass it is the lowest confidence among all
            criterion rows for that sample.
        blocking_criterion_ids: Criterion IDs that directly triggered
            ``failed`` or ``need_human_review``. Empty for pass samples.
        blocking_reasons: Short reasons from blocking criteria.
        evidence_fragment_ids: Unique evidence fragment IDs referenced by
            blocking criteria. Empty if no fragment was cited.
    """

    sample_id: str
    decision: str
    confidence_score: float | None
    blocking_criterion_ids: list[str]
    blocking_reasons: list[str]
    evidence_fragment_ids: list[str]


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read CSV rows while preserving the original column order.

    Args:
        path: CSV file path.

    Returns:
        A tuple ``(fieldnames, rows)``. ``fieldnames`` is empty only when the
        CSV has no header.
    """

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv_rows(path: Path, fieldnames: Sequence[str], rows: Iterable[dict[str, str]]) -> None:
    """Write CSV rows with UTF-8 encoding and a stable header.

    Args:
        path: Destination CSV path.
        fieldnames: Column names and order.
        rows: Row dictionaries. Missing fields are written as empty strings.

    Returns:
        None. The parent directory is created when needed.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def group_checklist_rows(rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group criterion-level checklist rows by sample ID.

    Args:
        rows: Rows from ``raw_dialogue_checklist_results.csv``.

    Returns:
        Mapping from ``sample_id`` to that sample's criterion rows.

    Raises:
        ValueError: If a row is missing ``sample_id`` or contains an unknown
            ``result`` value.
    """

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        sample_id = row.get("sample_id", "").strip()
        if not sample_id:
            raise ValueError("Checklist row is missing sample_id")
        result = row.get("result", "").strip()
        if result not in CRITERION_RESULTS:
            raise ValueError(f"Unknown criterion result for {sample_id}: {result!r}")
        grouped[sample_id].append(row)
    return dict(grouped)


def parse_confidence(value: str) -> float | None:
    """Parse a criterion confidence value.

    Args:
        value: Raw CSV value.

    Returns:
        Float confidence in ``[0, 1]`` when parseable, otherwise ``None``.
    """

    try:
        confidence = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if confidence < 0 or confidence > 1:
        return None
    return confidence


def aggregate_sample(rows: Sequence[dict[str, str]], *, pass_label: str = "pass") -> SampleAggregate:
    """Aggregate one sample's checklist rows into one strict sample decision.

    Args:
        rows: All criterion rows for one sample.
        pass_label: Label to use when every criterion is ``pass`` or
            ``not_applicable``. Current Plan 04 outputs must use ``"pass"``.

    Returns:
        ``SampleAggregate`` with the strict decision, confidence, blocking
        criteria, reasons, and evidence IDs.

    Raises:
        ValueError: If ``rows`` is empty or rows contain multiple sample IDs.
    """

    if not rows:
        raise ValueError("Cannot aggregate an empty sample")
    sample_ids = {row.get("sample_id", "").strip() for row in rows}
    if len(sample_ids) != 1:
        raise ValueError(f"Cannot aggregate multiple sample IDs together: {sorted(sample_ids)}")
    sample_id = next(iter(sample_ids))

    fail_rows = [row for row in rows if row.get("result", "").strip() == "fail"]
    uncertain_rows = [row for row in rows if row.get("result", "").strip() == "uncertain"]

    if fail_rows:
        decision = "failed"
        blocking_rows = fail_rows
    elif uncertain_rows:
        decision = "need_human_review"
        blocking_rows = uncertain_rows
    else:
        decision = pass_label
        blocking_rows = list(rows)

    confidence_values = [
        confidence
        for row in blocking_rows
        if (confidence := parse_confidence(row.get("confidence_score", ""))) is not None
    ]
    confidence = min(confidence_values) if confidence_values else None

    direct_blocking_rows = fail_rows or uncertain_rows
    blocking_criterion_ids = unique_nonempty(row.get("criterion_id", "") for row in direct_blocking_rows)
    blocking_reasons = unique_nonempty(
        f"{row.get('criterion_id', '').strip()}: {row.get('reason', '').strip()}".strip(": ")
        for row in direct_blocking_rows
    )
    evidence_fragment_ids = unique_fragment_ids(row.get("evidence_fragment_id", "") for row in direct_blocking_rows)

    return SampleAggregate(
        sample_id=sample_id,
        decision=decision,
        confidence_score=confidence,
        blocking_criterion_ids=blocking_criterion_ids,
        blocking_reasons=blocking_reasons,
        evidence_fragment_ids=evidence_fragment_ids,
    )


def build_sample_aggregates(
    checklist_rows: Iterable[dict[str, str]], *, pass_label: str = "pass"
) -> dict[str, SampleAggregate]:
    """Build strict sample-level aggregates for every sample in a checklist.

    Args:
        checklist_rows: Criterion-level checklist rows.
        pass_label: Label for clean-pass samples.

    Returns:
        Mapping from ``sample_id`` to ``SampleAggregate``.
    """

    grouped = group_checklist_rows(checklist_rows)
    return {
        sample_id: aggregate_sample(rows, pass_label=pass_label)
        for sample_id, rows in sorted(grouped.items())
    }


def sync_quality_rows(
    existing_quality_rows: Sequence[dict[str, str]],
    aggregates: dict[str, SampleAggregate],
    *,
    decision_column: str,
    checked_by: str = DEFAULT_CHECKED_BY,
    checked_at: str,
) -> list[dict[str, str]]:
    """Update an existing quality-suggestion table from strict aggregates.

    Args:
        existing_quality_rows: Existing sample-level rows whose non-decision
            metadata columns should be preserved.
        aggregates: Strict aggregates keyed by ``sample_id``.
        decision_column: Existing decision column name. Current Plan 04
            outputs use ``quality_decision``.
        checked_by: Identifier written to the output row.
        checked_at: Timestamp written to the output row.

    Returns:
        Updated quality rows. The row count and original metadata columns are
        preserved. Decision, confidence, reasons, review flags, evidence IDs,
        checker, and timestamp are synchronized from the checklist aggregate.

    Raises:
        KeyError: If a quality row references a sample absent from
            ``aggregates``.
    """

    synced: list[dict[str, str]] = []
    for row in existing_quality_rows:
        sample_id = row.get("sample_id", "").strip()
        aggregate = aggregates[sample_id]
        new_row = dict(row)
        new_row[decision_column] = aggregate.decision
        if aggregate.confidence_score is not None:
            new_row["confidence_score"] = format_confidence(aggregate.confidence_score)
        reason_text = " | ".join(aggregate.blocking_reasons)
        if "failure_reasons" in new_row:
            new_row["failure_reasons"] = reason_text
        if "evidence_fragment_ids" in new_row:
            new_row["evidence_fragment_ids"] = ";".join(aggregate.evidence_fragment_ids)
        if "needs_hnmu_review" in new_row:
            new_row["needs_hnmu_review"] = bool_text(aggregate.decision != "pass" and aggregate.decision != "keep")
        if "suggested_reviewer_action" in new_row:
            new_row["suggested_reviewer_action"] = reviewer_action_for_decision(aggregate.decision)
        if "checked_by" in new_row:
            new_row["checked_by"] = checked_by
        if "checked_at" in new_row:
            new_row["checked_at"] = checked_at
        synced.append(new_row)
    return synced


def build_canonical_quality_rows(
    sample_ids: Sequence[str],
    aggregates: dict[str, SampleAggregate],
    *,
    sample_metadata: dict[str, dict[str, str]] | None = None,
    existing_quality_rows: dict[str, dict[str, str]] | None = None,
    checked_by: str = DEFAULT_CHECKED_BY,
    checked_at: str,
) -> list[dict[str, str]]:
    """Build canonical sample-level quality suggestions.

    Args:
        sample_ids: Ordered sample IDs to write.
        aggregates: Strict sample aggregates keyed by ``sample_id``.
        sample_metadata: Optional metadata keyed by ``sample_id``. Typical
            fields are ``source_file``, ``source_row_number``, ``grade`` and
            ``lesson`` from ``normalized_dialogue_rows.csv``.
        existing_quality_rows: Optional previous quality rows keyed by
            ``sample_id``. They are used only to preserve review flags or shard
            labels when available.
        checked_by: Identifier written to ``checked_by``.
        checked_at: Timestamp written to ``checked_at``.

    Returns:
        Rows using ``CANONICAL_QUALITY_COLUMNS``. The schema is intended for the
        main `agent_shard_audit/merged/quality_check_suggestions.csv` file so
        grade 6--7 and grade 8--9 outputs can be reviewed with one column set.
    """

    sample_metadata = sample_metadata or {}
    existing_quality_rows = existing_quality_rows or {}
    rows: list[dict[str, str]] = []
    for sample_id in sample_ids:
        aggregate = aggregates[sample_id]
        metadata = sample_metadata.get(sample_id, {})
        previous = existing_quality_rows.get(sample_id, {})
        decision = "pass" if aggregate.decision == "keep" else aggregate.decision
        row = {
            "sample_id": sample_id,
            "source_file": metadata.get("source_file", previous.get("source_file", "")),
            "source_row_number": metadata.get(
                "source_row_number", previous.get("source_row_number", "")
            ),
            "grade": metadata.get("grade", previous.get("grade", "")),
            "lesson": metadata.get("lesson", previous.get("lesson", "")),
            "quality_decision": decision,
            "confidence_score": (
                format_confidence(aggregate.confidence_score)
                if aggregate.confidence_score is not None
                else ""
            ),
            "failure_reasons": " | ".join(aggregate.blocking_reasons),
            "blocking_criterion_ids": ";".join(aggregate.blocking_criterion_ids),
            "suggested_reviewer_action": reviewer_action_for_decision(decision),
            "needs_hnmu_review": bool_text(decision != "pass"),
            "needs_learning_resource_review": preserve_bool(
                previous.get("needs_learning_resource_review", "")
            ),
            "needs_sgv_verification": preserve_bool(previous.get("needs_sgv_verification", "")),
            "evidence_fragment_ids": ";".join(aggregate.evidence_fragment_ids)
            or previous.get("evidence_fragment_ids", ""),
            "checked_by": checked_by,
            "checked_at": checked_at,
            "source_shard": previous.get("source_shard", previous.get("shard_id", "")),
        }
        rows.append(row)
    return rows


def build_review_queue_rows(
    synced_quality_rows: Sequence[dict[str, str]],
    aggregates: dict[str, SampleAggregate],
    *,
    fieldnames: Sequence[str],
    decision_column: str,
    checked_by: str = DEFAULT_CHECKED_BY,
    checked_at: str,
    medium_priority_label: str = "medium",
    high_priority_label: str = "high",
) -> list[dict[str, str]]:
    """Build a review queue from non-pass sample-level suggestions.

    Args:
        synced_quality_rows: Quality rows already synchronized from checklist
            aggregates.
        aggregates: Strict aggregates keyed by ``sample_id``.
        fieldnames: Target review-queue columns to preserve.
        decision_column: Decision column in ``synced_quality_rows``.
        checked_by: Identifier written to the output row.
        checked_at: Timestamp written to the output row.
        medium_priority_label: Label for review-needed but not failed samples.
        high_priority_label: Label for failed samples.

    Returns:
        Review-queue rows for every sample whose decision is not pass.
    """

    queue: list[dict[str, str]] = []
    for quality_row in synced_quality_rows:
        sample_id = quality_row.get("sample_id", "").strip()
        decision = quality_row.get(decision_column, "").strip()
        if decision in {"pass", "keep"}:
            continue
        aggregate = aggregates[sample_id]
        row = {name: "" for name in fieldnames}
        for shared in ("sample_id", "grade", "lesson", "source_shard", "shard_id"):
            if shared in row and shared in quality_row:
                row[shared] = quality_row.get(shared, "")
        row["sample_id"] = sample_id
        row["review_reason"] = review_reason_for_aggregate(aggregate)
        row["priority"] = high_priority_label if decision == "failed" else medium_priority_label
        row["suggested_question_to_hnmu"] = suggested_question_for_aggregate(aggregate)
        row["related_criterion_ids"] = ";".join(aggregate.blocking_criterion_ids)
        row["evidence_fragment_ids"] = ";".join(aggregate.evidence_fragment_ids)
        row["checked_by"] = checked_by
        row["checked_at"] = checked_at
        queue.append(row)
    return queue


def unique_nonempty(values: Iterable[str]) -> list[str]:
    """Return unique non-empty strings while preserving first-seen order.

    Args:
        values: Raw values that may be empty or duplicated.

    Returns:
        Ordered unique non-empty values.
    """

    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        cleaned = str(value or "").strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            output.append(cleaned)
    return output


def unique_fragment_ids(values: Iterable[str]) -> list[str]:
    """Split and deduplicate semicolon-separated evidence fragment IDs.

    Args:
        values: Raw evidence values from checklist rows.

    Returns:
        Ordered unique fragment IDs.
    """

    split_values: list[str] = []
    for value in values:
        for item in str(value or "").replace(",", ";").split(";"):
            cleaned = item.strip()
            if cleaned:
                split_values.append(cleaned)
    return unique_nonempty(split_values)


def format_confidence(value: float) -> str:
    """Format confidence values for CSV output.

    Args:
        value: Confidence value in ``[0, 1]``.

    Returns:
        String with two decimal places.
    """

    return f"{value:.2f}"


def bool_text(value: bool) -> str:
    """Format booleans for existing CSV conventions.

    Args:
        value: Boolean value.

    Returns:
        Lowercase string ``true`` or ``false``.
    """

    return "true" if value else "false"


def preserve_bool(value: str) -> str:
    """Normalize a pre-existing boolean-like CSV value.

    Args:
        value: Raw boolean value such as ``true``, ``false``, ``1`` or ``0``.

    Returns:
        Lowercase ``true``/``false`` when recognized, otherwise an empty string.
    """

    cleaned = str(value or "").strip().lower()
    if cleaned in {"true", "1", "yes", "y"}:
        return "true"
    if cleaned in {"false", "0", "no", "n"}:
        return "false"
    return ""


def reviewer_action_for_decision(decision: str) -> str:
    """Return a conservative reviewer action for a sample-level decision.

    Args:
        decision: Sample-level decision.

    Returns:
        Short action label for ``quality_check_suggestions.csv``.
    """

    if decision == "failed":
        return "exclude_from_current_batch_or_repair"
    if decision == "need_human_review":
        return "ask_hnmu_uet_review"
    return "keep"


def review_reason_for_aggregate(aggregate: SampleAggregate) -> str:
    """Create a concise review reason from blocking criteria.

    Args:
        aggregate: Strict sample aggregate.

    Returns:
        Vietnamese review reason for the review queue.
    """

    if aggregate.decision == "failed":
        return "Có tiêu chí không đạt: " + ";".join(aggregate.blocking_criterion_ids)
    return "Có tiêu chí cần HNMU/UET xác nhận: " + ";".join(aggregate.blocking_criterion_ids)


def suggested_question_for_aggregate(aggregate: SampleAggregate) -> str:
    """Create a standard HNMU/UET review question.

    Args:
        aggregate: Strict sample aggregate.

    Returns:
        Vietnamese question/action text for the review queue.
    """

    if aggregate.decision == "failed":
        return DEFAULT_REVIEW_QUESTION
    return (
        "Vui lòng xác nhận các tiêu chí còn chưa chắc, đặc biệt sự khớp giữa "
        "câu hỏi, đáp án SGV, hội thoại, mức nhận thức và học liệu liên quan."
    )

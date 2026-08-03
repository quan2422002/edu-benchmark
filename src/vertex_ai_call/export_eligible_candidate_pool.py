"""Xuất pool candidate đủ điều kiện từ kết quả xác định của Plan 03."""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.vertex_ai_call.analyze_requirement_scoring import (  # noqa: E402
    load_conversion_trace,
)
from src.vertex_ai_call.requirement_scoring import (  # noqa: E402
    PRINCIPLE_IDS,
    RequirementScoringError,
    load_grounding_pool,
    load_run_records,
    validate_run_records,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT = REPOSITORY_ROOT / "experiments/20260727_170150"
DEFAULT_ANALYSIS = (
    DEFAULT_EXPERIMENT
    / "outputs/principle_requirement_scoring/full_gemini35_medium_v1/"
    "full_run_analysis.json"
)
DEFAULT_RUN = (
    DEFAULT_EXPERIMENT
    / "outputs/principle_requirement_scoring/full_gemini35_medium_v1/"
    "run_full.jsonl"
)
DEFAULT_GROUNDING_POOL = (
    DEFAULT_EXPERIMENT
    / "inherited_resources/from_20260722_000940/benchmark_specification/"
    "candidate_grounding/candidate_principle_grounding_pool.csv"
)
DEFAULT_CANDIDATES = (
    DEFAULT_EXPERIMENT
    / "inherited_resources/from_20260722_000940/benchmark_conversion/"
    "full_v0/benchmark_candidate_splits.csv"
)
DEFAULT_TRACE = (
    DEFAULT_EXPERIMENT
    / "inherited_resources/from_20260722_000940/benchmark_conversion/"
    "full_v0/conversion_trace.csv"
)
DEFAULT_OUTPUT = (
    DEFAULT_EXPERIMENT
    / "outputs/benchmark_candidate_pool/"
    "eligible_without_plan03_review.csv"
)

CANDIDATE_HEADER: tuple[str, ...] = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "gold_response",
    "gold_answer",
)

OUTPUT_HEADER: tuple[str, ...] = (
    "benchmark_candidate_id",
    "sample_id",
    "grade",
    "lesson",
    "position",
    "bloom_level",
    "student_prompt",
    "conversation_history",
    "source_question",
    "gold_answer",
    "gold_response",
    "target_tutor_turn_index",
    "has_history",
    "history_turn_count",
    "family_position",
    "required_principle_set",
    "required_principle_count",
    "alternative_principle_set",
    "principle_scores_json",
    "principle_assessments_json",
    "eligibility_status",
    "requirement_scoring_model",
    "requirement_scoring_request_hash",
)

ELIGIBILITY_STATUS = "eligible_without_plan03_review"


def _json_cell(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _load_csv_index(
    path: Path,
    *,
    expected_header: Sequence[str],
) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != tuple(expected_header):
            raise RequirementScoringError(
                f"{path}: CSV header mismatch; "
                f"expected={list(expected_header)}, actual={reader.fieldnames}"
            )
        rows = list(reader)
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        candidate_id = row["benchmark_candidate_id"].strip()
        if not candidate_id:
            raise RequirementScoringError(f"{path}: empty candidate ID")
        if candidate_id in index:
            raise RequirementScoringError(
                f"{path}: duplicate candidate ID {candidate_id}"
            )
        index[candidate_id] = row
    return index


def _atomic_write_csv(
    path: Path,
    *,
    rows: Iterable[Mapping[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(
            file_descriptor, "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_HEADER)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _family_positions(
    grounding_rows: Sequence[Mapping[str, Any]],
    trace_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, str]:
    by_family: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row in grounding_rows:
        candidate_id = str(row["benchmark_candidate_id"])
        by_family[str(row["sample_id"])].append(
            (
                int(trace_by_id[candidate_id]["target_tutor_turn_index"]),
                candidate_id,
            )
        )
    positions: dict[str, str] = {}
    for family_rows in by_family.values():
        ordered = sorted(family_rows)
        if len(ordered) == 1:
            positions[ordered[0][1]] = "single"
            continue
        for index, (_, candidate_id) in enumerate(ordered):
            if index == 0:
                positions[candidate_id] = "first"
            elif index == len(ordered) - 1:
                positions[candidate_id] = "last"
            else:
                positions[candidate_id] = "middle"
    return positions


def _validate_candidate_match(
    grounding_row: Mapping[str, Any],
    candidate_row: Mapping[str, str],
) -> None:
    candidate_id = str(grounding_row["benchmark_candidate_id"])
    comparisons = {
        "sample_id": str(grounding_row["sample_id"]),
        "grade": str(grounding_row["grade"]),
        "lesson": str(grounding_row["lesson"]),
        "position": str(grounding_row["position"]),
        "bloom_level": str(grounding_row["bloom_level"]),
        "student_prompt": str(grounding_row["student_prompt"]),
        "gold_answer": str(grounding_row["gold_answer"]),
    }
    for field, expected in comparisons.items():
        actual = candidate_row[field].strip()
        if field == "conversation_history":
            try:
                actual = _json_cell(json.loads(actual))
            except json.JSONDecodeError as exc:
                raise RequirementScoringError(
                    f"{candidate_id}: invalid candidate conversation_history"
                ) from exc
        if actual != expected:
            raise RequirementScoringError(
                f"{candidate_id}: {field} differs between candidate and "
                "grounding pool"
            )


def export_eligible_candidate_pool(
    *,
    analysis_path: Path,
    run_path: Path,
    grounding_pool_path: Path,
    candidates_path: Path,
    trace_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Join and export exactly the Plan-03 eligible candidate IDs."""

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    eligibility = analysis.get("eligibility", {})
    candidate_ids_by_status = eligibility.get("candidate_ids", {})
    eligible_ids = candidate_ids_by_status.get(ELIGIBILITY_STATUS)
    if not isinstance(eligible_ids, list) or not eligible_ids:
        raise RequirementScoringError(
            f"{analysis_path}: missing non-empty {ELIGIBILITY_STATUS} list"
        )
    if len(eligible_ids) != len(set(eligible_ids)):
        raise RequirementScoringError("Eligibility list contains duplicate IDs")
    reported_count = eligibility.get("counts", {}).get(ELIGIBILITY_STATUS)
    if reported_count != len(eligible_ids):
        raise RequirementScoringError(
            "Eligibility count does not match candidate ID list"
        )

    grounding_rows = load_grounding_pool(grounding_pool_path)
    grounding_by_id = {
        str(row["benchmark_candidate_id"]): row for row in grounding_rows
    }
    candidate_by_id = _load_csv_index(
        candidates_path,
        expected_header=CANDIDATE_HEADER,
    )
    trace_rows = load_conversion_trace(trace_path)
    trace_by_id = {
        str(row["benchmark_candidate_id"]): row for row in trace_rows
    }
    records = validate_run_records(
        load_run_records(run_path),
        grounding_rows,
        run_id="full",
    )

    source_id_sets = {
        "grounding": set(grounding_by_id),
        "candidates": set(candidate_by_id),
        "trace": set(trace_by_id),
        "run": set(records),
    }
    reference_ids = source_id_sets["grounding"]
    for source_name, source_ids in source_id_sets.items():
        if source_ids != reference_ids:
            raise RequirementScoringError(
                f"{source_name} candidate IDs do not match grounding pool"
            )
    missing_eligible = sorted(set(eligible_ids) - reference_ids)
    if missing_eligible:
        raise RequirementScoringError(
            f"Eligible IDs absent from joined sources: {missing_eligible[:5]}"
        )

    positions = _family_positions(grounding_rows, trace_by_id)
    output_rows: list[dict[str, Any]] = []
    for candidate_id in sorted(eligible_ids):
        grounding = grounding_by_id[candidate_id]
        candidate = candidate_by_id[candidate_id]
        trace = trace_by_id[candidate_id]
        record = records[candidate_id]
        _validate_candidate_match(grounding, candidate)
        if trace["sample_id"] != grounding["sample_id"]:
            raise RequirementScoringError(
                f"{candidate_id}: sample_id differs in conversion trace"
            )
        assessments = record["normalized_response"]["principle_scores"]
        score_map = {
            item["principle_id"]: int(item["requirement_score"])
            for item in assessments
        }
        if tuple(score_map) != PRINCIPLE_IDS:
            raise RequirementScoringError(
                f"{candidate_id}: principle order/schema mismatch"
            )
        required = list(record["required_principle_set"])
        if not 1 <= len(required) <= 3:
            raise RequirementScoringError(
                f"{candidate_id}: eligible candidate must have 1–3 "
                "required principles"
            )
        history = grounding["conversation_history"]
        output_rows.append(
            {
                "benchmark_candidate_id": candidate_id,
                "sample_id": grounding["sample_id"],
                "grade": grounding["grade"],
                "lesson": grounding["lesson"],
                "position": grounding["position"],
                "bloom_level": grounding["bloom_level"],
                "student_prompt": grounding["student_prompt"],
                "conversation_history": _json_cell(history),
                "source_question": grounding["source_question"],
                "gold_answer": grounding["gold_answer"],
                "gold_response": candidate["gold_response"].strip(),
                "target_tutor_turn_index": trace[
                    "target_tutor_turn_index"
                ],
                "has_history": str(bool(history)).lower(),
                "history_turn_count": len(history),
                "family_position": positions[candidate_id],
                "required_principle_set": _json_cell(required),
                "required_principle_count": len(required),
                "alternative_principle_set": _json_cell(
                    record["alternative_principle_set"]
                ),
                "principle_scores_json": _json_cell(score_map),
                "principle_assessments_json": _json_cell(assessments),
                "eligibility_status": ELIGIBILITY_STATUS,
                "requirement_scoring_model": record["model"],
                "requirement_scoring_request_hash": record["request_hash"],
            }
        )

    if len(output_rows) != reported_count:
        raise RequirementScoringError(
            f"Expected {reported_count} output rows, found {len(output_rows)}"
        )
    _atomic_write_csv(output_path, rows=output_rows)
    return {
        "output_path": str(output_path),
        "row_count": len(output_rows),
        "unique_candidate_count": len(
            {row["benchmark_candidate_id"] for row in output_rows}
        ),
        "family_count": len({row["sample_id"] for row in output_rows}),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Xuất một CSV tự chứa cho candidate có trạng thái "
            "eligible_without_plan03_review."
        )
    )
    parser.add_argument("--analysis", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument(
        "--grounding-pool",
        type=Path,
        default=DEFAULT_GROUNDING_POOL,
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
    )
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = export_eligible_candidate_pool(
        analysis_path=args.analysis.resolve(),
        run_path=args.run.resolve(),
        grounding_pool_path=args.grounding_pool.resolve(),
        candidates_path=args.candidates.resolve(),
        trace_path=args.trace.resolve(),
        output_path=args.output.resolve(),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

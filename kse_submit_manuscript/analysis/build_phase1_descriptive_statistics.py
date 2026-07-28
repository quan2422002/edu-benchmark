#!/usr/bin/env python3
"""Build verified Phase-1 descriptive statistics from the 665 pass dialogues.

This builder intentionally reads only ``raw_dialogue`` from the canonical
665-dialogue conversion-input snapshot.  ``conversion_dialogue`` is excluded:
it contains two approved Phase-2 corrections and is not the Phase-1 source
text described by these statistics.  The canonical label/content parser is
used in lexical mode: its alternating-role gate is not applied because two retained raw dialogues have three adjacent-role transitions before approved
Phase-2 corrections.  No correction is applied or dereferenced here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = (
    REPO_ROOT
    / "experiments/20260722_000940/outputs/benchmark_conversion/"
    "conversion_input_pass_samples.csv"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "phase1_descriptive_statistics"
TURN_PATTERN = re.compile(r"^\s*(HS|AI)\s*:\s?(.*)$")
GRADE_ORDER = ("6", "7", "8", "9")
EXPECTED_GRADE_COUNTS = {"6": 106, "7": 132, "8": 209, "9": 218}
EXPECTED_TOTAL_DIALOGUES = 665
EXPECTED_TOTAL_TURNS = 4354
EXPECTED_STUDENT_TURNS = 2326
EXPECTED_AI_TURNS = 2028


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_dialogue_turns(dialogue: str, sample_id: str) -> list[tuple[str, str]]:
    """Use canonical label/content parsing without applying a Phase-2 correction.

    ``dialogue_split.parse_dialogue_turns`` additionally rejects adjacent roles.
    That gate is appropriate to Phase-2 conversion, but cannot be used for the
    requested Phase-1 raw-text description: the source contains two known
    adjacent-role exceptions, and this builder must neither repair nor exclude them.
    """
    if not dialogue or not dialogue.strip():
        raise ValueError(f"{sample_id}: empty_dialogue")

    turns: list[tuple[str, str]] = []
    current_speaker: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_speaker is not None:
            turns.append((current_speaker, "\n".join(current_lines)))

    for line_number, line in enumerate(dialogue.splitlines(), start=1):
        match = TURN_PATTERN.match(line)
        if match:
            flush()
            current_speaker = match.group(1)
            current_lines = [match.group(2)]
        elif current_speaker is None:
            raise ValueError(f"{sample_id}: unknown_turn_label at line {line_number}")
        else:
            current_lines.append(line)
    flush()

    if not turns:
        raise ValueError(f"{sample_id}: no_turns")
    if turns[0][0] != "HS":
        raise ValueError(f"{sample_id}: first_turn_not_student")
    return turns


def percentage(count: int, total: int) -> str:
    value = (Decimal(count) * Decimal("100") / Decimal(total)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return format(value, "f")


def quantile_type7(values: list[int], probability: Decimal) -> Decimal:
    """Return the R-7 / linear-interpolation quantile for sorted values."""
    if not values:
        raise ValueError("Cannot calculate a quantile of no values")
    sorted_values = sorted(values)
    index = Decimal(len(sorted_values) - 1) * probability
    lower = int(index // 1)
    upper = int(index.to_integral_value(rounding="ROUND_CEILING"))
    fraction = index - Decimal(lower)
    return Decimal(sorted_values[lower]) + (
        Decimal(sorted_values[upper] - sorted_values[lower]) * fraction
    )


def display_decimal(value: Decimal, places: int = 6) -> str:
    rounded = value.quantize(Decimal("1").scaleb(-places), rounding=ROUND_HALF_UP)
    return format(rounded, "f")


def character_summary(values: list[int]) -> dict[str, Any]:
    getcontext().prec = 28
    total = sum(values)
    count = len(values)
    return {
        "count": count,
        "min": min(values),
        "q1": display_decimal(quantile_type7(values, Decimal("0.25"))),
        "median": display_decimal(quantile_type7(values, Decimal("0.50"))),
        "q3": display_decimal(quantile_type7(values, Decimal("0.75"))),
        "max": max(values),
        "mean": display_decimal(Decimal(total) / Decimal(count)),
        "quantile_method": "R-7 linear interpolation: index = (n - 1) * p",
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_rows(source: Path) -> list[dict[str, str]]:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"sample_id", "grade", "raw_dialogue"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Source lacks required columns: {sorted(missing)}")
        rows = list(reader)
    sample_ids = [row["sample_id"] for row in rows]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Source contains duplicate sample_id values")
    return rows


def build(source: Path, output_dir: Path) -> dict[str, Any]:
    rows = load_rows(source)
    grade_counts = Counter(row["grade"] for row in rows)
    turns_per_dialogue: list[dict[str, Any]] = []
    characters_per_turn: list[dict[str, Any]] = []
    all_character_counts: list[int] = []
    character_counts_by_speaker: dict[str, list[int]] = defaultdict(list)
    non_alternating_samples: list[str] = []
    non_alternating_transition_count = 0

    # The measurement accesses only these three source fields.  In particular,
    # conversion_dialogue is deliberately never accessed.
    for row in sorted(rows, key=lambda item: item["sample_id"]):
        sample_id = row["sample_id"]
        grade = row["grade"]
        turns = parse_dialogue_turns(row["raw_dialogue"], sample_id)
        transitions = sum(
            previous[0] == current[0] for previous, current in zip(turns, turns[1:])
        )
        if transitions:
            non_alternating_samples.append(sample_id)
            non_alternating_transition_count += transitions
        student_turns = sum(speaker == "HS" for speaker, _ in turns)
        ai_turns = sum(speaker == "AI" for speaker, _ in turns)
        turns_per_dialogue.append(
            {
                "sample_id": sample_id,
                "grade": grade,
                "total_turns": len(turns),
                "student_turns": student_turns,
                "ai_turns": ai_turns,
            }
        )
        for turn_index, (speaker, content) in enumerate(turns, start=1):
            character_count = len(content)
            characters_per_turn.append(
                {
                    "sample_id": sample_id,
                    "grade": grade,
                    "turn_index": turn_index,
                    "speaker": speaker,
                    "character_count": character_count,
                }
            )
            all_character_counts.append(character_count)
            character_counts_by_speaker[speaker].append(character_count)

    grade_rows = [
        {
            "grade": grade,
            "dialogue_count": grade_counts[grade],
            "percentage": percentage(grade_counts[grade], len(rows)),
        }
        for grade in GRADE_ORDER
    ]
    grade_rows.append(
        {"grade": "Total", "dialogue_count": len(rows), "percentage": "100.00"}
    )
    turn_frequency = Counter(row["total_turns"] for row in turns_per_dialogue)
    total_turns = len(characters_per_turn)
    student_turns = sum(row["speaker"] == "HS" for row in characters_per_turn)
    ai_turns = sum(row["speaker"] == "AI" for row in characters_per_turn)

    validations = {
        "exactly_665_dialogues": {
            "expected": EXPECTED_TOTAL_DIALOGUES,
            "actual": len(rows),
            "passed": len(rows) == EXPECTED_TOTAL_DIALOGUES,
        },
        "grade_counts": {
            "expected": EXPECTED_GRADE_COUNTS,
            "actual": {grade: grade_counts[grade] for grade in GRADE_ORDER},
            "passed": {grade: grade_counts[grade] for grade in GRADE_ORDER}
            == EXPECTED_GRADE_COUNTS,
        },
        "grade_counts_sum_to_665": {
            "expected": EXPECTED_TOTAL_DIALOGUES,
            "actual": sum(grade_counts.values()),
            "passed": sum(grade_counts.values()) == EXPECTED_TOTAL_DIALOGUES,
        },
        "total_raw_utterances": {
            "expected": EXPECTED_TOTAL_TURNS,
            "actual": total_turns,
            "passed": total_turns == EXPECTED_TOTAL_TURNS,
        },
        "student_turns": {
            "expected": EXPECTED_STUDENT_TURNS,
            "actual": student_turns,
            "passed": student_turns == EXPECTED_STUDENT_TURNS,
        },
        "ai_turns": {
            "expected": EXPECTED_AI_TURNS,
            "actual": ai_turns,
            "passed": ai_turns == EXPECTED_AI_TURNS,
        },
        "turn_frequency_sums_to_665": {
            "expected": EXPECTED_TOTAL_DIALOGUES,
            "actual": sum(turn_frequency.values()),
            "passed": sum(turn_frequency.values()) == EXPECTED_TOTAL_DIALOGUES,
        },
        "characters_per_turn_row_count": {
            "expected": EXPECTED_TOTAL_TURNS,
            "actual": len(characters_per_turn),
            "passed": len(characters_per_turn) == EXPECTED_TOTAL_TURNS,
        },
        "raw_dialogue_only": {
            "actual": "Only sample_id, grade, and raw_dialogue were read for statistics.",
            "passed": True,
        },
        "later_phase1_recheck_artifacts_used": {
            "actual": [],
            "passed": True,
        },
        "raw_dialogue_parser_exception_documented": {
            "actual": {
                "non_alternating_transition_count": non_alternating_transition_count,
                "sample_ids": non_alternating_samples,
                "handling": "Count raw labelled utterances; do not repair, merge, exclude, or read conversion_dialogue.",
            },
            "passed": non_alternating_transition_count == 3
            and non_alternating_samples == [
                "HNMU-G7-R0189-STT6",
                "HNMU-G9-R0237-STT12",
            ],
        },
    }

    source_relative = repo_relative(source)
    summary = {
        "schema_version": "1.0",
        "source": {
            "path": source_relative,
            "sha256": sha256(source),
            "logical_dialogue_count": len(rows),
            "data_fields_used_for_statistics": ["sample_id", "grade", "raw_dialogue"],
            "excluded_field": "conversion_dialogue",
        },
        "measurement_definitions": {
            "turn": "One utterance prefixed by HS: or AI:, not a student-tutor exchange.",
            "character_count": (
                "Count of utterance content after removing the HS:/AI: label, colon, "
                "and at most one optional whitespace character immediately after the colon."
            ),
            "whitespace": "Internal whitespace and line breaks are included.",
            "parser_semantics_source": "src/edu_benchmark/benchmark_conversion/dialogue_split.py",
            "raw_source_exception": (
                "The canonical parser's role-label and content semantics are used, but its "
                "alternating-role gate is not applied: raw sources HNMU-G7-R0189-STT6 and "
                "HNMU-G9-R0237-STT12 have three adjacent-role transitions before Phase-2 "
                "corrections. The raw utterances are counted unchanged."
            ),
            "quantile_method": "R-7 linear interpolation: index = (n - 1) * p",
        },
        "grade_distribution": grade_rows,
        "turns": {
            "total": total_turns,
            "student": student_turns,
            "ai": ai_turns,
            "per_dialogue_frequency": [
                {
                    "total_turns": total,
                    "dialogue_count": turn_frequency[total],
                    "percentage": percentage(turn_frequency[total], len(rows)),
                }
                for total in sorted(turn_frequency)
            ],
        },
        "character_count": {
            "all_turns": character_summary(all_character_counts),
            "HS": character_summary(character_counts_by_speaker["HS"]),
            "AI": character_summary(character_counts_by_speaker["AI"]),
        },
        "validation": validations,
    }

    workflow_spec = {
        "schema_version": "1.0",
        "scope": "Verified Phase-1 workflow specification for external figure production.",
        "five_phase1_audit_areas": [
            "coverage",
            "missing fields and formatting",
            "consistency",
            "duplicate and near-duplicate detection",
            "per-sample quality assessment",
        ],
        "per_dialogue_checklist": {
            "criterion_count": 18,
            "criterion_groups": [
                {"name": "structure", "criterion_count": 3},
                {"name": "consistency", "criterion_count": 7},
                {"name": "pedagogy", "criterion_count": 6},
                {"name": "duplicate_risk", "criterion_count": 2},
            ],
        },
        "wording_restrictions": [
            "Do not call the five audit areas five groups of the 18 criteria.",
            "Coverage is batch-level and is not represented as a per-sample criterion row.",
            "The 18 per-dialogue criteria span four criterion groups.",
        ],
        "raw_dialogue_statistics_note": (
            "Descriptive statistics use raw_dialogue. The canonical parser's label/content "
            "semantics are retained, but its alternating-role gate is not applied because "
            "two raw dialogues have adjacent-role transitions. No Phase-2 correction or "
            "conversion_dialogue value is used."
        ),
        "workflow_stages": [
            {
                "order": 1,
                "stage": "Raw-data intake and traceable normalization",
                "description": "Register raw HNMU batches, create derived normalized rows, and preserve raw dialogue content.",
                "evidence_paths": [
                    "experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md",
                    "experiments/20260709_155523/outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv",
                    "experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/normalized_dialogue_rows.csv",
                ],
            },
            {
                "order": 2,
                "stage": "Learning-resource processing and retrieval construction",
                "description": "Use registered SGK/SGV OCR Markdown, metadata registries, fragments, and a SQLite FTS retrieval index as draft retrieval support.",
                "evidence_paths": [
                    "experiments/20260709_155523/roadmap.md",
                    "experiments/20260709_155523/reports/learning-resource-registries-sync-20260718.md",
                    "experiments/20260709_155523/reports/phase4-fragmentation-result.md",
                    "experiments/20260709_155523/reports/phase5-retrieval-index-result.md",
                    "shared/learning_resources/registries/ocr_text_manifest.csv",
                    "shared/learning_resources/fragments/learning_resource_fragments.csv",
                    "shared/learning_resources/indexes/README.md",
                ],
            },
            {
                "order": 3,
                "stage": "Mechanical audit, coverage mapping, and duplicate detection",
                "description": "Check required fields and dialogue formatting; map coverage through learning-resource registries; detect duplicate and near-duplicate risks.",
                "evidence_paths": [
                    "experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md",
                    "experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md",
                ],
            },
            {
                "order": 4,
                "stage": "Agent-assisted, criterion-level audit",
                "description": "Record one result for each sample_id and criterion_id, with evidence and suggested reviewer action where applicable.",
                "evidence_paths": [
                    "experiments/20260709_155523/plans/07-hnmu-dialogue-auditor-specialist.md",
                    "experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv",
                    "experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv",
                ],
            },
            {
                "order": 5,
                "stage": "Strict sample-level aggregation",
                "description": "Aggregate criterion-level results into pass, need_human_review, or failed without allowing a sample with fail or uncertain criteria to remain pass.",
                "evidence_paths": [
                    "src/edu_benchmark/dialogue_audit/checklist_aggregation.py",
                    "scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py",
                    "experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md",
                ],
            },
            {
                "order": 6,
                "stage": "Phase-2 input selection",
                "description": "Retain only the 665 pass dialogues for deterministic turn-level conversion.",
                "evidence_paths": [
                    "experiments/20260722_000940/outputs/benchmark_conversion/conversion_input_pass_samples.csv",
                    "experiments/20260722_000940/outputs/benchmark_conversion/full_v0/conversion_summary.json",
                    "experiments/20260722_000940/reports/plan02-full-multi-candidate-conversion-summary.md",
                ],
            },
        ],
        "aggregation_rules": [
            {"if": "Any criterion result is fail.", "quality_decision": "failed"},
            {
                "if": "No criterion result is fail and at least one is uncertain.",
                "quality_decision": "need_human_review",
            },
            {
                "if": "Every criterion result is pass or not_applicable.",
                "quality_decision": "pass",
            },
        ],
        "final_outcomes": {
            "pass": 665,
            "need_human_review": 382,
            "failed": 3,
        },
        "classification_evidence_paths": {
            "five_phase1_audit_areas": [
                "experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md",
            ],
            "per_dialogue_18_criterion_groups": [
                "experiments/20260722_000940/inherited_resources/from_20260709_155523/checklists/raw-dialogue-audit-criteria-v0.csv",
                "experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md",
            ],
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "grade_distribution.csv",
        ["grade", "dialogue_count", "percentage"],
        grade_rows,
    )
    write_csv(
        output_dir / "turns_per_dialogue.csv",
        ["sample_id", "grade", "total_turns", "student_turns", "ai_turns"],
        turns_per_dialogue,
    )
    write_csv(
        output_dir / "characters_per_turn.csv",
        ["sample_id", "grade", "turn_index", "speaker", "character_count"],
        characters_per_turn,
    )
    (output_dir / "summary_statistics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "phase1_workflow_spec.json").write_text(
        json.dumps(workflow_spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    summary = build(args.source.resolve(), args.output_dir.resolve())
    failed = [
        name for name, check in summary["validation"].items() if not check["passed"]
    ]
    if failed:
        raise SystemExit(f"Validation failed: {', '.join(failed)}")
    print(f"Wrote verified Phase-1 statistics to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

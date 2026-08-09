"""Reproducible Section V ablation and robustness analysis.

This module consumes only the locked full-run judge artifacts. It does not
call any model provider. The published JSON bundle is written atomically only
after all integrity checks and paper-facing validation anchors pass.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


LABELS = ("Win", "Tie", "Lose")
TARGETS = (
    "target_gemini35",
    "target_gemini35_learnlm_prompted",
    "target_llama4_maverick",
)
TARGET_NAMES = {
    "target_gemini35": "Gemini baseline",
    "target_gemini35_learnlm_prompted": "Gemini+LearnLM",
    "target_llama4_maverick": "Llama 4 Maverick",
}
JUDGE_NAMES = {
    "gemini": "Gemini",
    "gpt": "GPT",
}
GENERAL_RUBRICS = (
    "RUB-GEN-ACC",
    "RUB-GEN-ALIGN",
    "RUB-GEN-SCAFF",
    "RUB-GEN-COMM",
)
PRINCIPLE_RUBRICS = {
    "Challenge": (
        "RUB-CHA-DEMAND",
        "RUB-CHA-CALIB",
        "RUB-CHA-AGENCY",
    ),
    "Explanation": (
        "RUB-EXP-CORE",
        "RUB-EXP-COHER",
        "RUB-EXP-ADAPT",
    ),
    "Modelling": (
        "RUB-MOD-PROC",
        "RUB-MOD-THINK",
        "RUB-MOD-TRANSFER",
    ),
    "Practice": (
        "RUB-PRA-ACT",
        "RUB-PRA-ALIGN",
        "RUB-PRA-CONSOL",
    ),
    "Questioning": (
        "RUB-QUE-PURPOSE",
        "RUB-QUE-QUALITY",
        "RUB-QUE-DEPEND",
    ),
    "Feedback": (
        "RUB-FBK-GROUND",
        "RUB-FBK-DISC",
        "RUB-FBK-ACTION",
    ),
}
RUBRIC_GROUPS = {
    rubric_id: "General"
    for rubric_id in GENERAL_RUBRICS
}
for _principle, _rubric_ids in PRINCIPLE_RUBRICS.items():
    for _rubric_id in _rubric_ids:
        RUBRIC_GROUPS[_rubric_id] = _principle

COMPONENTS = (
    "Overall Judgement",
    "General",
    *PRINCIPLE_RUBRICS.keys(),
    "Overall Acc.",
)
EXPECTED_CONTRACT = "gold-answer-only-v4"


class SectionVAblationError(RuntimeError):
    """Raised when an input or validation invariant is violated."""


@dataclass(frozen=True)
class LoadedJudge:
    """Validated records for one judge."""

    key: str
    path: Path
    sha256: str
    records: tuple[dict[str, Any], ...]
    by_comparison_id: Mapping[str, dict[str, Any]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SectionVAblationError(
                    f"{path}:{line_number}: invalid JSON: {exc}"
                ) from exc
            if not isinstance(record, dict):
                raise SectionVAblationError(
                    f"{path}:{line_number}: record must be an object"
                )
            records.append(record)
    return records


def load_candidate_families(path: Path) -> tuple[dict[str, str], str]:
    candidate_to_family: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {
            "benchmark_candidate_id",
            "sample_id",
        }.issubset(reader.fieldnames):
            raise SectionVAblationError(
                f"{path}: candidate CSV lacks benchmark_candidate_id/sample_id"
            )
        for row in reader:
            candidate_id = row["benchmark_candidate_id"].strip()
            family_id = row["sample_id"].strip()
            if not candidate_id or not family_id:
                raise SectionVAblationError(
                    f"{path}: empty candidate or family identifier"
                )
            if candidate_id in candidate_to_family:
                raise SectionVAblationError(
                    f"{path}: duplicate candidate {candidate_id}"
                )
            candidate_to_family[candidate_id] = family_id
    if len(candidate_to_family) != 1400:
        raise SectionVAblationError(
            f"{path}: expected 1400 candidates, found {len(candidate_to_family)}"
        )
    return candidate_to_family, sha256_file(path)


def _validate_label(label: Any, context: str) -> str:
    if label not in LABELS:
        raise SectionVAblationError(
            f"{context}: target_judgment must be one of {LABELS}, got {label!r}"
        )
    return str(label)


def load_judge(path: Path, key: str) -> LoadedJudge:
    records = _read_jsonl(path)
    if len(records) != 4200:
        raise SectionVAblationError(
            f"{path}: expected 4200 records, found {len(records)}"
        )

    by_id: dict[str, dict[str, Any]] = {}
    target_counts: Counter[str] = Counter()
    criterion_count = 0
    for record in records:
        comparison_id = str(record.get("comparison_id", ""))
        if not comparison_id or comparison_id in by_id:
            raise SectionVAblationError(
                f"{path}: missing or duplicate comparison_id {comparison_id!r}"
            )
        if record.get("record_status") != "completed":
            raise SectionVAblationError(
                f"{comparison_id}: record_status is not completed"
            )
        if record.get("judge_output_contract_version") != EXPECTED_CONTRACT:
            raise SectionVAblationError(
                f"{comparison_id}: unexpected judge contract"
            )
        if record.get("learning_evidence_included") is not False:
            raise SectionVAblationError(
                f"{comparison_id}: v4 must exclude learning evidence"
            )
        target_run_id = str(record.get("target_run_id", ""))
        if target_run_id not in TARGETS:
            raise SectionVAblationError(
                f"{comparison_id}: unknown target_run_id {target_run_id!r}"
            )
        target_counts[target_run_id] += 1
        _validate_label(
            record.get("overall_judgment", {}).get("target_judgment"),
            f"{comparison_id}.overall_judgment",
        )
        adjusted = record.get("adjusted_criterion_judgments")
        raw = record.get("raw_criterion_judgments")
        if adjusted != raw:
            raise SectionVAblationError(
                f"{comparison_id}: adjusted criteria differ from raw in v4"
            )
        if not isinstance(adjusted, list):
            raise SectionVAblationError(
                f"{comparison_id}: criteria must be a list"
            )
        rubric_ids: list[str] = []
        for criterion in adjusted:
            rubric_id = str(criterion.get("rubric_id", ""))
            if rubric_id not in RUBRIC_GROUPS:
                raise SectionVAblationError(
                    f"{comparison_id}: unknown rubric_id {rubric_id!r}"
                )
            rubric_ids.append(rubric_id)
            _validate_label(
                criterion.get("target_judgment"),
                f"{comparison_id}.{rubric_id}",
            )
        if len(rubric_ids) != len(set(rubric_ids)):
            raise SectionVAblationError(
                f"{comparison_id}: duplicate rubric judgments"
            )
        if set(rubric_ids) != set(record.get("applicable_rubric_ids", [])):
            raise SectionVAblationError(
                f"{comparison_id}: applicable rubric IDs do not match judgments"
            )
        order = record.get("blind_pair_order")
        if order not in (
            {"response_1": "target", "response_2": "reference"},
            {"response_1": "reference", "response_2": "target"},
        ):
            raise SectionVAblationError(
                f"{comparison_id}: invalid blind_pair_order {order!r}"
            )
        criterion_count += len(adjusted)
        by_id[comparison_id] = record

    if target_counts != Counter({target: 1400 for target in TARGETS}):
        raise SectionVAblationError(
            f"{path}: target counts do not equal 1400 each: {target_counts}"
        )
    if criterion_count != 38832:
        raise SectionVAblationError(
            f"{path}: expected 38832 criteria, found {criterion_count}"
        )
    return LoadedJudge(
        key=key,
        path=path,
        sha256=sha256_file(path),
        records=tuple(records),
        by_comparison_id=by_id,
    )


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if not denominator:
        return math.nan
    return float(numerator) / float(denominator)


def _judgment_counts(labels: Iterable[str]) -> dict[str, int]:
    counts = Counter(labels)
    result = {label: counts[label] for label in LABELS}
    result["n"] = sum(result.values())
    return result


def score_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Calculate KMP-compatible component scores for one configuration."""

    overall_labels = [
        _validate_label(
            record["overall_judgment"]["target_judgment"],
            str(record["comparison_id"]),
        )
        for record in records
    ]
    overall_counts = _judgment_counts(overall_labels)
    rubric_labels: dict[str, list[str]] = defaultdict(list)
    candidate_ids_by_rubric: dict[str, set[str]] = defaultdict(set)
    for record in records:
        candidate_id = str(record["benchmark_candidate_id"])
        for criterion in record["adjusted_criterion_judgments"]:
            rubric_id = str(criterion["rubric_id"])
            rubric_labels[rubric_id].append(
                _validate_label(
                    criterion["target_judgment"],
                    f"{record['comparison_id']}.{rubric_id}",
                )
            )
            candidate_ids_by_rubric[rubric_id].add(candidate_id)

    rubric_scores: dict[str, dict[str, Any]] = {}
    for rubric_id in RUBRIC_GROUPS:
        counts = _judgment_counts(rubric_labels[rubric_id])
        rubric_scores[rubric_id] = {
            "n_candidate": len(candidate_ids_by_rubric[rubric_id]),
            "n_judgment": counts["n"],
            "win": counts["Win"],
            "tie": counts["Tie"],
            "lose": counts["Lose"],
            "win_rate": _ratio(counts["Win"], counts["n"]),
        }

    general = float(np.mean([
        rubric_scores[rubric_id]["win_rate"]
        for rubric_id in GENERAL_RUBRICS
    ]))
    principles: dict[str, dict[str, Any]] = {}
    for principle, rubric_ids in PRINCIPLE_RUBRICS.items():
        candidate_counts = {
            rubric_scores[rubric_id]["n_candidate"] for rubric_id in rubric_ids
        }
        if len(candidate_counts) != 1:
            raise SectionVAblationError(
                f"{principle}: its three rubric candidate counts differ"
            )
        principles[principle] = {
            "n_candidate": candidate_counts.pop(),
            "win_rate": float(np.mean([
                rubric_scores[rubric_id]["win_rate"]
                for rubric_id in rubric_ids
            ])),
        }
    overall_acc = (general + float(np.mean([
        item["win_rate"] for item in principles.values()
    ]))) / 2.0
    return {
        "n_candidate": len(records),
        "overall_judgment": {
            "win": overall_counts["Win"],
            "tie": overall_counts["Tie"],
            "lose": overall_counts["Lose"],
            "win_rate": _ratio(overall_counts["Win"], overall_counts["n"]),
        },
        "general": general,
        "principles": principles,
        "overall_acc": overall_acc,
        "rubrics": rubric_scores,
    }


def _component_value(score: Mapping[str, Any], component: str) -> float:
    if component == "Overall Judgement":
        return float(score["overall_judgment"]["win_rate"])
    if component == "General":
        return float(score["general"])
    if component == "Overall Acc.":
        return float(score["overall_acc"])
    return float(score["principles"][component]["win_rate"])


def _component_n(score: Mapping[str, Any], component: str) -> int:
    if component in PRINCIPLE_RUBRICS:
        return int(score["principles"][component]["n_candidate"])
    return int(score["n_candidate"])


def _family_sufficient_statistics(
    records: Sequence[Mapping[str, Any]],
    candidate_to_family: Mapping[str, str],
    families: Sequence[str],
) -> tuple[np.ndarray, np.ndarray]:
    """Return family-level win numerators and denominators.

    Columns are Overall Judgement followed by all 22 rubric IDs in stable
    order. These sufficient statistics preserve the KMP macro calculation.
    """

    rubric_ids = tuple(RUBRIC_GROUPS)
    column_by_rubric = {
        rubric_id: index + 1 for index, rubric_id in enumerate(rubric_ids)
    }
    family_index = {family_id: index for index, family_id in enumerate(families)}
    wins = np.zeros((len(families), 1 + len(rubric_ids)), dtype=np.int64)
    totals = np.zeros_like(wins)
    for record in records:
        candidate_id = str(record["benchmark_candidate_id"])
        try:
            family_id = candidate_to_family[candidate_id]
        except KeyError as exc:
            raise SectionVAblationError(
                f"Candidate {candidate_id} is missing from the candidate pool"
            ) from exc
        row = family_index[family_id]
        overall = record["overall_judgment"]["target_judgment"]
        totals[row, 0] += 1
        wins[row, 0] += int(overall == "Win")
        for criterion in record["adjusted_criterion_judgments"]:
            column = column_by_rubric[str(criterion["rubric_id"])]
            totals[row, column] += 1
            wins[row, column] += int(criterion["target_judgment"] == "Win")
    return wins, totals


def _bootstrap_component_matrix(
    multiplicities: np.ndarray,
    wins: np.ndarray,
    totals: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Calculate component scores and validity masks for bootstrap draws."""

    win_sum = multiplicities @ wins
    total_sum = multiplicities @ totals
    rates = np.divide(
        win_sum,
        total_sum,
        out=np.full(win_sum.shape, np.nan, dtype=float),
        where=total_sum > 0,
    )
    rubric_ids = tuple(RUBRIC_GROUPS)
    rubric_column = {
        rubric_id: index + 1 for index, rubric_id in enumerate(rubric_ids)
    }
    values: dict[str, np.ndarray] = {
        "Overall Judgement": rates[:, 0],
    }
    valid: dict[str, np.ndarray] = {
        "Overall Judgement": total_sum[:, 0] > 0,
    }

    general_columns = [rubric_column[item] for item in GENERAL_RUBRICS]
    values["General"] = np.mean(rates[:, general_columns], axis=1)
    valid["General"] = np.all(total_sum[:, general_columns] > 0, axis=1)
    for principle, rubric_ids_for_principle in PRINCIPLE_RUBRICS.items():
        columns = [
            rubric_column[item] for item in rubric_ids_for_principle
        ]
        values[principle] = np.mean(rates[:, columns], axis=1)
        valid[principle] = np.all(total_sum[:, columns] > 0, axis=1)
    principle_matrix = np.column_stack([
        values[principle] for principle in PRINCIPLE_RUBRICS
    ])
    values["Overall Acc."] = (
        values["General"] + np.mean(principle_matrix, axis=1)
    ) / 2.0
    valid["Overall Acc."] = valid["General"].copy()
    for principle in PRINCIPLE_RUBRICS:
        valid["Overall Acc."] &= valid[principle]

    for rubric_id in rubric_ids:
        column = rubric_column[rubric_id]
        values[rubric_id] = rates[:, column]
        valid[rubric_id] = total_sum[:, column] > 0
    return values, valid


def instruction_ablation(
    judges: Mapping[str, LoadedJudge],
    candidate_to_family: Mapping[str, str],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    """Compute paired baseline-vs-LearnLM instruction effects."""

    families = sorted(set(candidate_to_family.values()))
    rng = np.random.default_rng(seed)
    multiplicities = rng.multinomial(
        len(families),
        np.full(len(families), 1.0 / len(families)),
        size=iterations,
    )
    output: dict[str, Any] = {
        "contrast": {
            "control": "target_gemini35",
            "treatment": "target_gemini35_learnlm_prompted",
            "delta_definition": "treatment_minus_control",
        },
        "bootstrap": {
            "unit": "sample_id",
            "method": "paired percentile cluster bootstrap",
            "iterations": iterations,
            "seed": seed,
            "family_count": len(families),
        },
        "component_rows": [],
        "rubric_rows": [],
    }
    for judge_key, judge in judges.items():
        records_by_target = {
            target: [
                record
                for record in judge.records
                if record["target_run_id"] == target
            ]
            for target in (
                "target_gemini35",
                "target_gemini35_learnlm_prompted",
            )
        }
        candidate_sets = {
            target: {
                str(record["benchmark_candidate_id"])
                for record in records
            }
            for target, records in records_by_target.items()
        }
        if candidate_sets["target_gemini35"] != candidate_sets[
            "target_gemini35_learnlm_prompted"
        ]:
            raise SectionVAblationError(
                f"{judge_key}: baseline and treatment candidate sets differ"
            )
        scores = {
            target: score_records(records)
            for target, records in records_by_target.items()
        }
        bootstrap_values: dict[str, dict[str, np.ndarray]] = {}
        bootstrap_valid: dict[str, dict[str, np.ndarray]] = {}
        for target, records in records_by_target.items():
            wins, totals = _family_sufficient_statistics(
                records, candidate_to_family, families
            )
            values, valid = _bootstrap_component_matrix(
                multiplicities, wins, totals
            )
            bootstrap_values[target] = values
            bootstrap_valid[target] = valid

        for component in (*COMPONENTS, *RUBRIC_GROUPS):
            control = _component_or_rubric_value(
                scores["target_gemini35"], component
            )
            treatment = _component_or_rubric_value(
                scores["target_gemini35_learnlm_prompted"], component
            )
            valid = (
                bootstrap_valid["target_gemini35"][component]
                & bootstrap_valid[
                    "target_gemini35_learnlm_prompted"
                ][component]
            )
            delta_draws = (
                bootstrap_values[
                    "target_gemini35_learnlm_prompted"
                ][component][valid]
                - bootstrap_values["target_gemini35"][component][valid]
            )
            low, high = np.quantile(delta_draws, [0.025, 0.975])
            row = {
                "judge": JUDGE_NAMES[judge_key],
                "judge_key": judge_key,
                "component": component,
                "n_candidate": _component_or_rubric_n(
                    scores["target_gemini35"], component
                ),
                "baseline": control,
                "learnlm": treatment,
                "delta": treatment - control,
                "ci95": [float(low), float(high)],
                "baseline_percent": control * 100.0,
                "learnlm_percent": treatment * 100.0,
                "delta_percentage_points": (treatment - control) * 100.0,
                "ci95_percentage_points": [
                    float(low) * 100.0,
                    float(high) * 100.0,
                ],
                "valid_bootstrap_draws": int(valid.sum()),
            }
            if component in COMPONENTS:
                output["component_rows"].append(row)
            else:
                row["rubric_group"] = RUBRIC_GROUPS[component]
                output["rubric_rows"].append(row)
    return output


def _component_or_rubric_value(
    score: Mapping[str, Any], component: str
) -> float:
    if component in RUBRIC_GROUPS:
        return float(score["rubrics"][component]["win_rate"])
    return _component_value(score, component)


def _component_or_rubric_n(
    score: Mapping[str, Any], component: str
) -> int:
    if component in RUBRIC_GROUPS:
        return int(score["rubrics"][component]["n_candidate"])
    return _component_n(score, component)


def agreement_statistics(
    labels_a: Sequence[str],
    labels_b: Sequence[str],
) -> dict[str, Any]:
    if len(labels_a) != len(labels_b) or not labels_a:
        raise SectionVAblationError(
            "Agreement inputs must be non-empty and equally sized"
        )
    for index, (label_a, label_b) in enumerate(zip(labels_a, labels_b)):
        _validate_label(label_a, f"agreement.a[{index}]")
        _validate_label(label_b, f"agreement.b[{index}]")
    n = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / n
    marg_a = {
        label: labels_a.count(label) / n for label in LABELS
    }
    marg_b = {
        label: labels_b.count(label) / n for label in LABELS
    }
    cohen_expected = sum(
        marg_a[label] * marg_b[label] for label in LABELS
    )
    cohen = (
        (observed - cohen_expected) / (1.0 - cohen_expected)
        if cohen_expected < 1.0
        else 1.0
    )
    mean_marginal = {
        label: (marg_a[label] + marg_b[label]) / 2.0
        for label in LABELS
    }
    gwet_expected = sum(
        proportion * (1.0 - proportion)
        for proportion in mean_marginal.values()
    ) / (len(LABELS) - 1)
    gwet = (
        (observed - gwet_expected) / (1.0 - gwet_expected)
        if gwet_expected < 1.0
        else 1.0
    )
    return {
        "n_pairs": n,
        "exact_agreement": observed,
        "cohen_kappa": cohen,
        "gwet_ac1": gwet,
    }


def _criterion_map(record: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(item["rubric_id"]): _validate_label(
            item["target_judgment"],
            f"{record['comparison_id']}.{item['rubric_id']}",
        )
        for item in record["adjusted_criterion_judgments"]
    }


def judge_robustness(
    judges: Mapping[str, LoadedJudge],
) -> dict[str, Any]:
    gemini = judges["gemini"]
    gpt = judges["gpt"]
    if set(gemini.by_comparison_id) != set(gpt.by_comparison_id):
        raise SectionVAblationError(
            "Gemini and GPT comparison_id sets differ"
        )
    comparison_ids = sorted(gemini.by_comparison_id)

    overall_agreement: list[dict[str, Any]] = []
    scopes = [("All configurations", None)] + [
        (TARGET_NAMES[target], target) for target in TARGETS
    ]
    for scope_name, target in scopes:
        selected_ids = [
            comparison_id
            for comparison_id in comparison_ids
            if target is None
            or gemini.by_comparison_id[comparison_id]["target_run_id"]
            == target
        ]
        labels_gemini = [
            gemini.by_comparison_id[item]["overall_judgment"][
                "target_judgment"
            ]
            for item in selected_ids
        ]
        labels_gpt = [
            gpt.by_comparison_id[item]["overall_judgment"][
                "target_judgment"
            ]
            for item in selected_ids
        ]
        overall_agreement.append({
            "scope": scope_name,
            "target_run_id": target,
            **agreement_statistics(labels_gemini, labels_gpt),
        })

    criterion_pairs: list[tuple[str, str, str, str]] = []
    for comparison_id in comparison_ids:
        gemini_record = gemini.by_comparison_id[comparison_id]
        gpt_record = gpt.by_comparison_id[comparison_id]
        labels_gemini = _criterion_map(gemini_record)
        labels_gpt = _criterion_map(gpt_record)
        if labels_gemini.keys() != labels_gpt.keys():
            raise SectionVAblationError(
                f"{comparison_id}: judge rubric sets differ"
            )
        for rubric_id in labels_gemini:
            criterion_pairs.append((
                rubric_id,
                RUBRIC_GROUPS[rubric_id],
                labels_gemini[rubric_id],
                labels_gpt[rubric_id],
            ))
    if len(criterion_pairs) != 38832:
        raise SectionVAblationError(
            f"Expected 38832 criterion pairs, found {len(criterion_pairs)}"
        )

    criterion_agreement: list[dict[str, Any]] = []
    criterion_scopes: list[tuple[str, set[str]]] = [
        ("All criteria", set(RUBRIC_GROUPS)),
        ("Common", set(GENERAL_RUBRICS)),
    ]
    criterion_scopes.extend(
        (principle, set(rubric_ids))
        for principle, rubric_ids in PRINCIPLE_RUBRICS.items()
    )
    criterion_scopes.extend(
        (rubric_id, {rubric_id}) for rubric_id in GENERAL_RUBRICS
    )
    for scope, rubric_ids in criterion_scopes:
        selected = [
            pair for pair in criterion_pairs if pair[0] in rubric_ids
        ]
        criterion_agreement.append({
            "scope": scope,
            **agreement_statistics(
                [pair[2] for pair in selected],
                [pair[3] for pair in selected],
            ),
        })

    directional_disagreement: list[dict[str, Any]] = []
    for target in TARGETS:
        matrix = {
            gemini_label: {gpt_label: 0 for gpt_label in LABELS}
            for gemini_label in LABELS
        }
        for comparison_id in comparison_ids:
            gemini_record = gemini.by_comparison_id[comparison_id]
            if gemini_record["target_run_id"] != target:
                continue
            gemini_label = gemini_record["overall_judgment"][
                "target_judgment"
            ]
            gpt_label = gpt.by_comparison_id[comparison_id][
                "overall_judgment"
            ]["target_judgment"]
            matrix[gemini_label][gpt_label] += 1
        tie_branches = sum(
            count
            for gemini_label, row in matrix.items()
            for gpt_label, count in row.items()
            if (
                (gemini_label == "Tie" or gpt_label == "Tie")
                and gemini_label != gpt_label
            )
        )
        directional_disagreement.append({
            "target_run_id": target,
            "tutor_configuration": TARGET_NAMES[target],
            "gemini_lose_gpt_win": matrix["Lose"]["Win"],
            "gemini_win_gpt_lose": matrix["Win"]["Lose"],
            "disagreements_with_tie": tie_branches,
            "matrix_gemini_rows_gpt_columns": matrix,
        })

    scores = {
        judge_key: {
            target: score_records([
                record
                for record in judge.records
                if record["target_run_id"] == target
            ])
            for target in TARGETS
        }
        for judge_key, judge in judges.items()
    }
    severity_rows: list[dict[str, Any]] = []
    for target in TARGETS:
        for component in COMPONENTS:
            gemini_score = _component_value(
                scores["gemini"][target], component
            )
            gpt_score = _component_value(scores["gpt"][target], component)
            severity_rows.append({
                "target_run_id": target,
                "tutor_configuration": TARGET_NAMES[target],
                "component": component,
                "gemini_judge": gemini_score,
                "gpt_judge": gpt_score,
                "gap_gemini_minus_gpt": gemini_score - gpt_score,
                "gemini_judge_percent": gemini_score * 100.0,
                "gpt_judge_percent": gpt_score * 100.0,
                "gap_percentage_points": (
                    gemini_score - gpt_score
                ) * 100.0,
            })

    return {
        "overall_agreement": overall_agreement,
        "criterion_agreement": criterion_agreement,
        "directional_disagreement": directional_disagreement,
        "severity_gap": severity_rows,
    }


def position_sensitivity(
    judges: Mapping[str, LoadedJudge],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    overall_positions: Counter[str] = Counter()
    for judge_key, judge in judges.items():
        for target in TARGETS:
            labels: dict[str, list[str]] = {
                "response_1": [],
                "response_2": [],
            }
            for record in judge.records:
                if record["target_run_id"] != target:
                    continue
                target_position = (
                    "response_1"
                    if record["blind_pair_order"]["response_1"] == "target"
                    else "response_2"
                )
                labels[target_position].append(
                    record["overall_judgment"]["target_judgment"]
                )
                if judge_key == "gemini":
                    overall_positions[target_position] += 1
            counts = {
                position: _judgment_counts(values)
                for position, values in labels.items()
            }
            win_rates = {
                position: _ratio(item["Win"], item["n"])
                for position, item in counts.items()
            }
            rows.append({
                "judge": JUDGE_NAMES[judge_key],
                "judge_key": judge_key,
                "target_run_id": target,
                "tutor_configuration": TARGET_NAMES[target],
                "response_1": {
                    "n": counts["response_1"]["n"],
                    "win": counts["response_1"]["Win"],
                    "tie": counts["response_1"]["Tie"],
                    "lose": counts["response_1"]["Lose"],
                    "win_rate": win_rates["response_1"],
                },
                "response_2": {
                    "n": counts["response_2"]["n"],
                    "win": counts["response_2"]["Win"],
                    "tie": counts["response_2"]["Tie"],
                    "lose": counts["response_2"]["Lose"],
                    "win_rate": win_rates["response_2"],
                },
                "position_delta": (
                    win_rates["response_1"] - win_rates["response_2"]
                ),
                "position_delta_percentage_points": (
                    win_rates["response_1"] - win_rates["response_2"]
                ) * 100.0,
            })
    return {
        "interpretation_boundary": (
            "descriptive_only_not_causal; identical response pairs were not "
            "evaluated in both orders"
        ),
        "overall_position_counts": dict(overall_positions),
        "rows": rows,
    }


def _assert_close(
    actual: float,
    expected: float,
    *,
    tolerance: float,
    label: str,
) -> None:
    if not math.isclose(actual, expected, abs_tol=tolerance):
        raise SectionVAblationError(
            f"Validation anchor {label} failed: {actual} != {expected}"
        )


def validate_results(results: Mapping[str, Any]) -> dict[str, Any]:
    """Validate paper-facing anchors and internal count conservation."""

    robustness = results["judge_robustness"]
    overall_all = next(
        row
        for row in robustness["overall_agreement"]
        if row["scope"] == "All configurations"
    )
    criterion_all = next(
        row
        for row in robustness["criterion_agreement"]
        if row["scope"] == "All criteria"
    )
    _assert_close(
        overall_all["exact_agreement"],
        0.80452,
        tolerance=0.00001,
        label="overall exact agreement",
    )
    _assert_close(
        criterion_all["exact_agreement"],
        0.732437,
        tolerance=0.000001,
        label="criterion exact agreement",
    )
    expected_position = {
        ("gemini", "target_gemini35"): 8.04,
        ("gemini", "target_gemini35_learnlm_prompted"): 6.60,
        ("gemini", "target_llama4_maverick"): 14.61,
        ("gpt", "target_gemini35"): 0.88,
        ("gpt", "target_gemini35_learnlm_prompted"): 1.51,
        ("gpt", "target_llama4_maverick"): 0.31,
    }
    for row in results["position_sensitivity"]["rows"]:
        key = (row["judge_key"], row["target_run_id"])
        _assert_close(
            row["position_delta_percentage_points"],
            expected_position[key],
            tolerance=0.011,
            label=f"position delta {key}",
        )
        for position in ("response_1", "response_2"):
            item = row[position]
            if item["win"] + item["tie"] + item["lose"] != item["n"]:
                raise SectionVAblationError(
                    f"{key}/{position}: Win+Tie+Lose does not equal N"
                )
    if results["position_sensitivity"]["overall_position_counts"] != {
        "response_1": 2124,
        "response_2": 2076,
    }:
        raise SectionVAblationError("Overall position counts do not match")
    if len(results["instruction_ablation"]["component_rows"]) != 18:
        raise SectionVAblationError(
            "Instruction ablation must contain 18 component rows"
        )
    if len(results["instruction_ablation"]["rubric_rows"]) != 44:
        raise SectionVAblationError(
            "Instruction ablation must contain 44 rubric rows"
        )
    return {
        "status": "passed",
        "anchors": {
            "overall_exact_agreement": overall_all["exact_agreement"],
            "criterion_exact_agreement": criterion_all["exact_agreement"],
            "overall_position_counts": {
                "response_1": 2124,
                "response_2": 2076,
            },
        },
    }


def build_results(
    *,
    candidate_pool: Path,
    gemini_judge: Path,
    gpt_judge: Path,
    iterations: int = 5000,
    seed: int = 20260730,
    provenance_paths: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    candidate_to_family, candidate_sha = load_candidate_families(
        candidate_pool
    )
    judges = {
        "gemini": load_judge(gemini_judge, "gemini"),
        "gpt": load_judge(gpt_judge, "gpt"),
    }
    if set(judges["gemini"].by_comparison_id) != set(
        judges["gpt"].by_comparison_id
    ):
        raise SectionVAblationError(
            "The two judges do not contain the same 4200 comparison IDs"
        )
    displayed_paths = provenance_paths or {
        "candidate_pool": str(candidate_pool),
        "gemini_judge": str(gemini_judge),
        "gpt_judge": str(gpt_judge),
    }
    if set(displayed_paths) != {
        "candidate_pool",
        "gemini_judge",
        "gpt_judge",
    }:
        raise SectionVAblationError("Invalid provenance path mapping")
    provenance = {
        "analysis_contract": "section-v-ablation-analysis-v1",
        "judge_output_contract": EXPECTED_CONTRACT,
        "candidate_count": len(candidate_to_family),
        "family_count": len(set(candidate_to_family.values())),
        "comparison_count_per_judge": 4200,
        "criterion_judgment_count_per_judge": 38832,
        "inputs": {
            "candidate_pool": {
                "path": displayed_paths["candidate_pool"],
                "sha256": candidate_sha,
            },
            "gemini_judge": {
                "path": displayed_paths["gemini_judge"],
                "sha256": judges["gemini"].sha256,
            },
            "gpt_judge": {
                "path": displayed_paths["gpt_judge"],
                "sha256": judges["gpt"].sha256,
            },
        },
    }
    result: dict[str, Any] = {
        "instruction_ablation": instruction_ablation(
            judges,
            candidate_to_family,
            iterations=iterations,
            seed=seed,
        ),
        "judge_robustness": judge_robustness(judges),
        "position_sensitivity": position_sensitivity(judges),
    }
    result["instruction_ablation"]["provenance"] = provenance
    result["judge_robustness"]["validation"] = validate_results(result)
    return result


def write_results_atomic(results: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_path, output_path)

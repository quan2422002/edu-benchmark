"""Plot Phase-3 distributions for the 1,400 eligible benchmark samples.

The figure is derived from the exported eligible candidate pool rather than
from manuscript literals. It combines two pie charts and two bar charts:
multi-label principle incidence, grade, turns per benchmark sample, and
characters per turn occurrence.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    REPOSITORY_ROOT
    / "experiments/20260727_170150/outputs/benchmark_candidate_pool/"
    "eligible_without_plan03_review.csv"
)
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "kse_submit_manuscript/manuscript/figures/"
    "phase3_candidate_statistics.png"
)

EXPECTED_ROWS = 1_400
EXPECTED_GRADE_COUNTS = {"6": 193, "7": 280, "8": 412, "9": 515}
EXPECTED_TURN_COUNTS = {2: 631, 4: 414, 6: 194, 8: 103, 10: 49, 12: 7, 14: 2}
CHARACTER_BINS = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250), (250, 300)]
EXPECTED_CHARACTER_BIN_COUNTS = [896, 2_277, 1_569, 564, 171, 31]
PRINCIPLE_LABELS = {
    "PRINCIPLE-CHALLENGE": "Challenge",
    "PRINCIPLE-EXPLANATION": "Explanation",
    "PRINCIPLE-MODELLING": "Modelling",
    "PRINCIPLE-PRACTICE": "Practice",
    "PRINCIPLE-FEEDBACK": "Feedback",
    "PRINCIPLE-QUESTIONING": "Questioning",
}
EXPECTED_PRINCIPLE_COUNTS = {
    "PRINCIPLE-CHALLENGE": 8,
    "PRINCIPLE-EXPLANATION": 863,
    "PRINCIPLE-MODELLING": 93,
    "PRINCIPLE-PRACTICE": 27,
    "PRINCIPLE-FEEDBACK": 806,
    "PRINCIPLE-QUESTIONING": 651,
}
PRINCIPLE_COLORS = {
    "PRINCIPLE-CHALLENGE": "#f4c7c3",
    "PRINCIPLE-EXPLANATION": "#ccefd2",
    "PRINCIPLE-MODELLING": "#f8e0aa",
    "PRINCIPLE-PRACTICE": "#c9dced",
    "PRINCIPLE-FEEDBACK": "#eff3c4",
    "PRINCIPLE-QUESTIONING": "#e5d2ec",
}
GRADE_COLORS = ["#c9e3f1", "#d5efd2", "#f8ddbd", "#ded4eb"]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} eligible rows, found {len(rows)}")
    candidate_ids = [row["benchmark_candidate_id"] for row in rows]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Eligible pool contains duplicate candidate IDs")
    return rows


def character_bin_counts(lengths: list[int]) -> list[int]:
    counts = []
    for lower, upper in CHARACTER_BINS:
        counts.append(sum(lower <= value < upper for value in lengths))
    if sum(counts) != len(lengths):
        raise ValueError("Character bins do not cover every turn occurrence")
    return counts


def add_pie_value_labels(
    axis: plt.Axes,
    wedges: list,
    values: list[int],
    total: int,
    *,
    small_offsets: dict[int, tuple[float, float]] | None = None,
) -> None:
    """Place count and percentage on every pie slice without hiding rare slices."""
    small_offsets = small_offsets or {}
    for index, (wedge, value) in enumerate(zip(wedges, values, strict=True)):
        angle = math.radians((wedge.theta1 + wedge.theta2) / 2)
        share = value / total
        label = f"{value:,}\n{share:.1%}"
        if share >= 0.05:
            axis.text(
                0.56 * math.cos(angle),
                0.56 * math.sin(angle),
                label,
                ha="center",
                va="center",
                fontsize=8.5,
            )
            continue
        text_position = small_offsets.get(
            index,
            (1.02 * math.cos(angle), 1.02 * math.sin(angle)),
        )
        axis.annotate(
            label,
            xy=(0.78 * math.cos(angle), 0.78 * math.sin(angle)),
            xytext=text_position,
            ha="center",
            va="center",
            fontsize=8.2,
            arrowprops={"arrowstyle": "-", "color": "#5b6573", "linewidth": 0.7},
        )


def build_figure(rows: list[dict[str, str]], output_path: Path) -> None:
    grade_counts = Counter(row["grade"] for row in rows)
    turn_counts: Counter[int] = Counter()
    turn_lengths: list[int] = []
    principle_counts: Counter[str] = Counter()

    for row in rows:
        history = json.loads(row["conversation_history"])
        if not isinstance(history, list):
            raise ValueError(f"{row['benchmark_candidate_id']}: history is not a list")
        if len(history) != int(row["history_turn_count"]):
            raise ValueError(
                f"{row['benchmark_candidate_id']}: history-turn count mismatch"
            )
        sample_turns = [
            row["student_prompt"],
            *[turn["content"] for turn in history],
            row["gold_response"],
        ]
        turn_counts[len(sample_turns)] += 1
        turn_lengths.extend(len(content) for content in sample_turns)

        principle_ids = json.loads(row["required_principle_set"])
        if len(principle_ids) != int(row["required_principle_count"]):
            raise ValueError(
                f"{row['benchmark_candidate_id']}: required-principle count mismatch"
            )
        unknown = set(principle_ids) - set(PRINCIPLE_LABELS)
        if unknown:
            raise ValueError(f"Unknown principle IDs: {sorted(unknown)}")
        principle_counts.update(principle_ids)

    binned_lengths = character_bin_counts(turn_lengths)
    mean_turn_length = statistics.fmean(turn_lengths)
    median_turn_length = statistics.median(turn_lengths)
    if round(mean_turn_length, 1) != 96.6 or median_turn_length != 90:
        raise ValueError(
            "Unexpected turn-length summary: "
            f"mean={mean_turn_length:.3f}, median={median_turn_length}"
        )
    if dict(grade_counts) != EXPECTED_GRADE_COUNTS:
        raise ValueError(f"Unexpected grade counts: {dict(grade_counts)}")
    if dict(turn_counts) != EXPECTED_TURN_COUNTS:
        raise ValueError(f"Unexpected turn counts: {dict(turn_counts)}")
    if dict(principle_counts) != EXPECTED_PRINCIPLE_COUNTS:
        raise ValueError(f"Unexpected principle counts: {dict(principle_counts)}")
    if binned_lengths != EXPECTED_CHARACTER_BIN_COUNTS:
        raise ValueError(f"Unexpected character-bin counts: {binned_lengths}")

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )
    figure, axes = plt.subplots(1, 4, figsize=(14.8, 4.8))
    figure.patch.set_facecolor("white")

    principle_ids = list(PRINCIPLE_LABELS)
    principle_values = [principle_counts[item] for item in principle_ids]
    principle_total = sum(principle_values)
    principle_wedges, _ = axes[0].pie(
        principle_values,
        startangle=90,
        counterclock=False,
        colors=[PRINCIPLE_COLORS[item] for item in principle_ids],
        radius=0.88,
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
    )
    axes[0].set_title("(a) Principle incidence", pad=8)
    add_pie_value_labels(
        axes[0],
        principle_wedges,
        principle_values,
        principle_total,
        small_offsets={0: (-0.38, 1.08), 2: (1.02, -0.20), 3: (1.02, -0.63)},
    )
    principle_legend = [PRINCIPLE_LABELS[item] for item in principle_ids]
    axes[0].legend(
        principle_wedges,
        principle_legend,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.30),
        ncol=2,
        frameon=False,
        fontsize=8.2,
        columnspacing=0.7,
        handlelength=1.0,
        handletextpad=0.35,
    )

    grades = ["6", "7", "8", "9"]
    grade_values = [grade_counts[grade] for grade in grades]
    grade_wedges, _ = axes[1].pie(
        grade_values,
        startangle=90,
        counterclock=False,
        colors=GRADE_COLORS,
        radius=0.88,
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
    )
    axes[1].set_title("(b) Grade", pad=8)
    add_pie_value_labels(axes[1], grade_wedges, grade_values, EXPECTED_ROWS)
    grade_legend = [f"Grade {grade}" for grade in grades]
    axes[1].legend(
        grade_wedges,
        grade_legend,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
        frameon=False,
        fontsize=8.5,
        columnspacing=0.8,
        handlelength=1.0,
        handletextpad=0.35,
    )

    turn_values = [turn_counts[count] for count in EXPECTED_TURN_COUNTS]
    turn_bars = axes[2].bar(
        [str(count) for count in EXPECTED_TURN_COUNTS],
        turn_values,
        color="#a8cbe3",
        edgecolor="#526777",
        linewidth=0.6,
    )
    axes[2].set_title("(c) Turns per sample", pad=8)
    axes[2].set_xlabel("Number of turns")
    axes[2].set_ylabel("Samples")
    axes[2].set_ylim(0, max(turn_values) * 1.16)
    axes[2].bar_label(turn_bars, labels=[f"{value:,}" for value in turn_values], padding=2, fontsize=8.5)

    bin_labels = [f"{lower}--{upper - 1}" for lower, upper in CHARACTER_BINS]
    character_bars = axes[3].bar(
        bin_labels,
        binned_lengths,
        color="#90c69b",
        edgecolor="#4f7657",
        linewidth=0.6,
    )
    axes[3].set_title("(d) Characters per turn", pad=8)
    axes[3].set_xlabel("Character range")
    axes[3].set_ylabel("Turn occurrences")
    axes[3].set_ylim(0, max(binned_lengths) * 1.15)
    axes[3].tick_params(axis="x", rotation=32)
    axes[3].bar_label(
        character_bars,
        labels=[f"{value:,}" for value in binned_lengths],
        padding=2,
        fontsize=8.2,
        rotation=0,
    )
    axes[3].text(
        0.98,
        0.96,
        f"Mean: {mean_turn_length:.1f}\nMedian: {median_turn_length:.0f}",
        transform=axes[3].transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.85, "edgecolor": "#aab2bd"},
    )

    for axis in axes[2:]:
        axis.grid(axis="y", color="#d8dee9", linewidth=0.6, alpha=0.7)
        axis.set_axisbelow(True)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    figure.subplots_adjust(left=0.045, right=0.99, top=0.90, bottom=0.28, wspace=0.50)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=240, facecolor="white")
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot Phase-3 distributions for the eligible benchmark pool."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Eligible candidate CSV (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output figure path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_rows(args.input.resolve())
    build_figure(rows, args.output.resolve())
    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()

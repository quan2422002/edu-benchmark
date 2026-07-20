"""Run Plan 04 deterministic audit for HNMU raw dialogue batches."""

from __future__ import annotations

import argparse
from pathlib import Path

from edu_benchmark.dialogue_audit.hnmu_audit import audit_batch, write_audit_report


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        None.

    Returns:
        Parsed CLI namespace.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("shared/raw_data/HNMU-teacher_dialog_samples"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/20260709_155523/outputs/hnmu_dialogue_audit"))
    parser.add_argument("--report", type=Path, default=Path("experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-20260717.md"))
    parser.add_argument("--grades", nargs="+", default=["6", "7"], help="Numeric grades to audit. Default: 6 7")
    return parser.parse_args()


def main() -> None:
    """Run the audit and write CSV plus Markdown outputs.

    Args:
        None.

    Returns:
        None.
    """

    args = parse_args()
    summary = audit_batch(raw_dir=args.raw_dir, output_dir=args.output_dir, include_grades=set(args.grades))
    write_audit_report(args.report, summary)
    print(summary)


if __name__ == "__main__":
    main()

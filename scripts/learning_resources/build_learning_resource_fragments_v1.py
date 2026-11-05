#!/usr/bin/env python3
"""Build, survey, and validate experiment-scoped fragment releases v1/v1.1."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from edu_benchmark.learning_resources.fragment_markdown_v1 import (
    V1_1_NEIGHBOR_POLICIES,
    build_semantic_boundary_review_workbook_from_csv,
    build_validate_and_write_v1,
    build_validate_and_write_v1_1,
    write_fragment_v1_1_survey,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path(
    "shared/learning_resources/registries/ocr_text_manifest.csv"
)
DEFAULT_OUTPUT_DIR = Path(
    "experiments/20260903_135547/outputs/fragment_v1"
)
DEFAULT_V1_1_OUTPUT_DIR = Path(
    "experiments/20260903_135547/outputs/fragment_v1_1"
)
DEFAULT_V1_FRAGMENTS = DEFAULT_OUTPUT_DIR / "learning_resource_fragments_v1.csv"
DEFAULT_V1_VALIDATION = DEFAULT_OUTPUT_DIR / "fragment_validation_summary.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=(
            "build-v1",
            "survey-v1-1",
            "build-semantic-review-workbook",
            "build-v1-1",
        ),
        default="build-v1",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-fragments", type=Path, default=DEFAULT_V1_FRAGMENTS)
    parser.add_argument("--source-validation", type=Path, default=DEFAULT_V1_VALIDATION)
    parser.add_argument(
        "--survey-output",
        type=Path,
        default=DEFAULT_V1_1_OUTPUT_DIR / "fragment_v1_1_survey.json",
    )
    parser.add_argument(
        "--semantic-review-output",
        type=Path,
        help="Required machine/provenance CSV for survey-v1-1.",
    )
    parser.add_argument(
        "--semantic-review-source",
        type=Path,
        help="Existing machine review CSV for build-semantic-review-workbook.",
    )
    parser.add_argument(
        "--semantic-review-workbook-output",
        type=Path,
        help="Required compact XLSX human-review workbook.",
    )
    parser.add_argument(
        "--lower-semantic-samples-per-threshold",
        type=int,
        help="Required even sample count around each candidate lower bound.",
    )
    parser.add_argument(
        "--upper-semantic-samples-per-threshold",
        type=int,
        help="Required even sample count around each candidate upper bound.",
    )
    parser.add_argument(
        "--text-min-thresholds",
        type=int,
        nargs="+",
        help="Required candidate text minimums for survey-v1-1.",
    )
    parser.add_argument(
        "--text-max-thresholds",
        type=int,
        nargs="+",
        help="Required candidate text caps for survey-v1-1.",
    )
    parser.add_argument(
        "--table-absorption-thresholds",
        type=int,
        nargs="+",
        help="Required candidate upper bounds for absorbing uncaptioned tables.",
    )
    parser.add_argument(
        "--neighbor-policies",
        nargs="+",
        choices=sorted(V1_1_NEIGHBOR_POLICIES),
        help="Required neighbor policies for survey-v1-1.",
    )
    parser.add_argument("--text-min-effective-chars", type=int)
    parser.add_argument("--text-max-effective-chars", type=int)
    parser.add_argument("--table-absorption-max-effective-chars", type=int)
    parser.add_argument(
        "--neighbor-policy",
        choices=sorted(V1_1_NEIGHBOR_POLICIES),
    )
    parser.add_argument(
        "--table-table-merge-policy",
        choices=("disabled",),
        help="Must be explicitly set to disabled for v1.1 survey/build.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        required=True,
        help="Required file-only operation log. The CLI installs no console handler.",
    )
    return parser.parse_args()


def _repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _file_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("edu_benchmark.learning_resources.fragment_v1")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    return logger


def run(args: argparse.Namespace) -> int:
    log_path = _repo_path(args.log_file)
    logger = _file_logger(log_path)
    logger.info("Plan 01 fragment command started mode=%s", args.mode)
    try:
        if args.mode == "build-v1":
            manifest_path = _repo_path(args.manifest)
            output_dir = _repo_path(args.output_dir or DEFAULT_OUTPUT_DIR)
            logger.info("manifest=%s", manifest_path)
            logger.info("output_dir=%s", output_dir)
            summary = build_validate_and_write_v1(
                manifest_path=manifest_path,
                output_dir=output_dir,
                repo_root=REPO_ROOT,
            )
        elif args.mode == "survey-v1-1":
            if (
                args.text_min_thresholds is None
                or args.text_max_thresholds is None
                or args.table_absorption_thresholds is None
                or args.neighbor_policies is None
                or args.semantic_review_output is None
                or args.semantic_review_workbook_output is None
                or args.lower_semantic_samples_per_threshold is None
                or args.upper_semantic_samples_per_threshold is None
                or args.table_table_merge_policy != "disabled"
            ):
                raise ValueError(
                    "survey-v1-1 requires --text-min-thresholds, "
                    "--text-max-thresholds, --table-absorption-thresholds, "
                    "--neighbor-policies, --semantic-review-output, "
                    "--semantic-review-workbook-output, "
                    "--lower-semantic-samples-per-threshold, "
                    "--upper-semantic-samples-per-threshold, and "
                    "--table-table-merge-policy disabled"
                )
            source_fragments = _repo_path(args.source_fragments)
            source_validation = _repo_path(args.source_validation)
            survey_output = _repo_path(args.survey_output)
            semantic_review_output = _repo_path(args.semantic_review_output)
            semantic_review_workbook_output = _repo_path(
                args.semantic_review_workbook_output
            )
            logger.info("source_fragments=%s", source_fragments)
            logger.info("source_validation=%s", source_validation)
            logger.info("survey_output=%s", survey_output)
            logger.info("semantic_review_output=%s", semantic_review_output)
            logger.info(
                "semantic_review_workbook_output=%s",
                semantic_review_workbook_output,
            )
            summary = write_fragment_v1_1_survey(
                fragments_path=source_fragments,
                validation_summary_path=source_validation,
                output_path=survey_output,
                text_min_thresholds=args.text_min_thresholds,
                text_max_thresholds=args.text_max_thresholds,
                table_absorption_thresholds=args.table_absorption_thresholds,
                neighbor_policies=args.neighbor_policies,
                table_table_merge_enabled=False,
                semantic_review_output_path=semantic_review_output,
                semantic_review_workbook_output_path=(
                    semantic_review_workbook_output
                ),
                lower_semantic_samples_per_threshold=(
                    args.lower_semantic_samples_per_threshold
                ),
                upper_semantic_samples_per_threshold=(
                    args.upper_semantic_samples_per_threshold
                ),
            )
        elif args.mode == "build-semantic-review-workbook":
            if (
                args.semantic_review_source is None
                or args.semantic_review_workbook_output is None
            ):
                raise ValueError(
                    "build-semantic-review-workbook requires "
                    "--semantic-review-source and "
                    "--semantic-review-workbook-output"
                )
            semantic_review_source = _repo_path(args.semantic_review_source)
            semantic_review_workbook_output = _repo_path(
                args.semantic_review_workbook_output
            )
            logger.info("semantic_review_source=%s", semantic_review_source)
            logger.info(
                "semantic_review_workbook_output=%s",
                semantic_review_workbook_output,
            )
            summary = build_semantic_boundary_review_workbook_from_csv(
                semantic_review_source,
                semantic_review_workbook_output,
            )
        else:
            if (
                args.text_min_effective_chars is None
                or args.text_max_effective_chars is None
                or args.table_absorption_max_effective_chars is None
                or args.neighbor_policy is None
                or args.table_table_merge_policy != "disabled"
            ):
                raise ValueError(
                    "build-v1-1 requires --text-min-effective-chars, "
                    "--text-max-effective-chars, "
                    "--table-absorption-max-effective-chars, "
                    "--neighbor-policy, and --table-table-merge-policy disabled"
                )
            source_fragments = _repo_path(args.source_fragments)
            source_validation = _repo_path(args.source_validation)
            output_dir = _repo_path(args.output_dir or DEFAULT_V1_1_OUTPUT_DIR)
            logger.info("source_fragments=%s", source_fragments)
            logger.info("source_validation=%s", source_validation)
            logger.info("output_dir=%s", output_dir)
            summary = build_validate_and_write_v1_1(
                source_fragments_path=source_fragments,
                source_validation_path=source_validation,
                output_dir=output_dir,
                text_min_effective_chars=args.text_min_effective_chars,
                text_max_effective_chars=args.text_max_effective_chars,
                table_absorption_max_effective_chars=(
                    args.table_absorption_max_effective_chars
                ),
                neighbor_policy=args.neighbor_policy,
            )
    except Exception:
        logger.exception("Plan 01 fragment command failed mode=%s", args.mode)
        return 1
    logger.info("Plan 01 fragment command passed mode=%s summary=%s", args.mode, summary)
    return 0


def main() -> None:
    raise SystemExit(run(parse_args()))


if __name__ == "__main__":
    main()

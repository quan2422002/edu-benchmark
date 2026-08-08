#!/usr/bin/env python3
"""Validate a closed v3 forward-test bundle against UET-approved sets."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.benchmark_specification.principle_annotation import (
    validate_annotation_bundle,
    validate_input_pair,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--coder-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    input_dir = args.input_dir.resolve()
    bundle_dir = args.bundle_dir.resolve()
    validate_input_pair(
        repo_root=REPO_ROOT,
        context_path=input_dir / "principle_annotation_pass1_input.csv",
        grounding_path=input_dir / "principle_annotation_grounding_input.csv",
        manifest_path=input_dir / "principle_annotation_grounding_manifest.json",
    )
    structural = validate_annotation_bundle(
        input_dir=input_dir,
        bundle_dir=bundle_dir,
        coder_id=args.coder_id,
    )
    expected_rows = read_csv(args.expected.resolve())
    metadata = {
        row["benchmark_candidate_id"]: row
        for row in read_csv(bundle_dir / "principle_annotation_final.csv")
    }
    label_sets = {candidate_id: set() for candidate_id in metadata}
    for row in read_csv(bundle_dir / "principle_annotation_final_labels.csv"):
        label_sets[row["benchmark_candidate_id"]].add(row["principle_id"])

    cases = []
    for expected in expected_rows:
        candidate_id = expected["benchmark_candidate_id"]
        expected_set = {
            value for value in expected["expected_principle_set"].split(";") if value
        }
        actual_set = label_sets.get(candidate_id)
        actual_effect = metadata.get(candidate_id, {}).get("grounding_effect")
        set_match = actual_set == expected_set
        effect_match = actual_effect == expected["expected_grounding_effect"]
        cases.append(
            {
                "benchmark_candidate_id": candidate_id,
                "expected_principle_set": sorted(expected_set),
                "actual_principle_set": sorted(actual_set or set()),
                "set_match": set_match,
                "expected_grounding_effect": expected["expected_grounding_effect"],
                "actual_grounding_effect": actual_effect,
                "grounding_effect_match": effect_match,
            }
        )
    passed = len(cases) == len(metadata) and all(
        row["set_match"] and row["grounding_effect_match"] for row in cases
    )
    result = {
        "validation_version": "plan03-c0a-forward-v3",
        "status": "passed" if passed else "failed",
        "candidate_count": len(cases),
        "matched_count": sum(
            row["set_match"] and row["grounding_effect_match"] for row in cases
        ),
        "structural_validation": structural,
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

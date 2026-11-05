#!/usr/bin/env python3
"""Build the approved Plan 04 HNMU audit-review workbooks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edu_benchmark.review_delivery import (
    build_audit_review_workbooks,
    load_review_products_config,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_review_products_config(
        args.config,
        repository_root=REPOSITORY_ROOT,
    )
    result = build_audit_review_workbooks(config, overwrite=args.overwrite)
    summary = {
        "schema_version": result["schema_version"],
        "sample_count": result["sample_count"],
        "criterion_result_count": result["criterion_result_count"],
        "workbooks": [
            {
                "path": item["path"],
                "sample_count": item["sample_count"],
                "criterion_result_count": item["criterion_result_count"],
            }
            for item in result["workbooks"]
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

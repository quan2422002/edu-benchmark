#!/usr/bin/env python
"""Query the learning-resource retrieval index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from edu_benchmark.learning_resources.retrieval_api import search_learning_fragments  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=Path("shared/learning_resources/indexes/learning_resources_v0.sqlite"))
    parser.add_argument("--query", required=True)
    parser.add_argument("--grade", default=None)
    parser.add_argument("--material-type", action="append", default=None)
    parser.add_argument("--lesson-key", default=None)
    parser.add_argument("--limit", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    filters = {
        "grade": args.grade,
        "material_type": args.material_type,
        "lesson_key": args.lesson_key,
    }
    rows = search_learning_fragments(args.query, filters=filters, index_path=args.index, limit=args.limit)
    compact = [
        {
            "fragment_id": row["fragment_id"],
            "material_type": row["material_type"],
            "grade": row["grade"],
            "lesson_title": row["lesson_title"],
            "section_path": row["section_path"],
            "page_start": row["page_start"],
            "text_preview": row["text_preview"],
            "source_markdown_path": row["source_markdown_path"],
            "status": row["status"],
        }
        for row in rows
    ]
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

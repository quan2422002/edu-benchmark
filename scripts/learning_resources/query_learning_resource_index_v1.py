#!/usr/bin/env python3
"""Query the fragment v1 index through the unified two-keyword API."""

from __future__ import annotations

import argparse
from pathlib import Path

from edu_benchmark.learning_resources.retrieval_api_v1 import (
    DEFAULT_INDEX_PATH,
    SEARCH_TOOL_NAME,
    dispatch_retrieval_tool_v1,
    write_retrieval_result_v1,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--section-keywords")
    parser.add_argument("--content-keywords")
    parser.add_argument("--grade")
    parser.add_argument("--material-type", action="append")
    parser.add_argument("--lesson-key")
    parser.add_argument("--book-title")
    parser.add_argument("--content-limit", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    filters = {
        "grade": args.grade,
        "material_type": args.material_type,
        "lesson_key": args.lesson_key,
        "book_title": args.book_title,
    }
    envelope = dispatch_retrieval_tool_v1(
        SEARCH_TOOL_NAME,
        {
            "section_keywords": args.section_keywords,
            "content_keywords": args.content_keywords,
            "filters": filters,
            "content_limit": args.content_limit,
        },
        index_path=args.index,
    )
    write_retrieval_result_v1(envelope, args.output)


if __name__ == "__main__":
    main()

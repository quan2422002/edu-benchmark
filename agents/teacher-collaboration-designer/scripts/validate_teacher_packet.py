#!/usr/bin/env python3
"""Validate required files and headings in a teacher-facing pilot packet."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_FILES = (
    "00-start-here.md",
    "01-role-and-goal.md",
    "02-author-task-card.md",
    "03-review-task-card.md",
    "04-examples.md",
    "07-pilot-feedback-form.md",
    "08-open-questions.md",
)

TASK_CARD_FILES = ("02-author-task-card.md", "03-review-task-card.md")

REQUIRED_TASK_HEADINGS = (
    "Mục tiêu",
    "Vì sao cần task này",
    "Bạn nhận được gì",
    "Các bước thực hiện",
    "Ví dụ đạt yêu cầu",
    "Ví dụ cần sửa",
    "Bạn cần nộp gì",
    "Checklist tự kiểm tra",
    "Thời gian dự kiến",
    "Khi cần hỗ trợ",
)

FORBIDDEN_TECHNICAL_TERMS = ("yaml", "json", "git commit", "api key", "model config")
AUTHOR_FORBIDDEN_DECISION_PHRASES = (
    "chọn chấp nhận",
    "quyết định chấp nhận",
    "chấp nhận/cần sửa",
    "chấp nhận hoặc cần sửa",
    "accept/revise/reject",
    "choose accept",
)


def validate_teacher_packet(directory: Path) -> list[str]:
    """Return human-readable validation errors for a teacher packet directory."""

    errors: list[str] = []
    if not directory.is_dir():
        return [f"Directory not found: {directory}"]

    for filename in REQUIRED_FILES:
        path = directory / filename
        if not path.is_file():
            errors.append(f"Missing required file: {filename}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"Required file is empty: {filename}")

    for filename in TASK_CARD_FILES:
        path = directory / filename
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        lower_content = content.lower()
        for heading in REQUIRED_TASK_HEADINGS:
            if heading not in content:
                errors.append(f"{filename}: missing heading '{heading}'")
        for term in FORBIDDEN_TECHNICAL_TERMS:
            if term in lower_content:
                errors.append(f"{filename}: contains teacher-facing technical term '{term}'")
        if filename == "02-author-task-card.md":
            for phrase in AUTHOR_FORBIDDEN_DECISION_PHRASES:
                if phrase in lower_content:
                    errors.append(
                        f"{filename}: assigns reviewer decision '{phrase}' to the author"
                    )

    spreadsheet_candidates = list(directory.glob("05-author-template.*"))
    review_candidates = list(directory.glob("06-review-template.*"))
    if not spreadsheet_candidates:
        errors.append("Missing author template: 05-author-template.*")
    if not review_candidates:
        errors.append("Missing review template: 06-review-template.*")

    return errors


def main() -> int:
    """Run the command-line validator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Path to the teacher packet directory")
    args = parser.parse_args()
    errors = validate_teacher_packet(args.packet)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.packet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Deterministic analysis of dialogues whose final labelled turn is a student turn."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Mapping, Sequence

from .dialogue_split import DialogueSplitError, DialogueTurn, TURN_PATTERN

LAST_TURN_ANALYSIS_COLUMNS = [
    "sample_id",
    "source_batch",
    "source_file",
    "source_row_number",
    "grade",
    "lesson",
    "previous_tutor_turn",
    "final_student_turn",
    "word_count",
    "word_count_bin",
    "has_politeness_or_agreement_marker",
    "has_understanding_marker",
    "has_thanks_marker",
    "has_action_marker",
    "ends_as_question",
    "heuristic_category",
    "heuristic_rationale",
    "recommended_conversion_treatment",
    "heuristic_only",
]

UNDERSTANDING_PATTERN = re.compile(
    r"\b(hiểu|biết rồi|nhớ rồi|rõ rồi|ra vậy|ra là|hóa ra|hoá ra|"
    r"nắm được|nhận ra)\b",
    re.IGNORECASE,
)
THANKS_PATTERN = re.compile(r"(cảm ơn|cám ơn)", re.IGNORECASE)
ACTION_PATTERN = re.compile(
    r"\b(em sẽ|để em|em làm xong|em đã làm|em hoàn thành|em thử|"
    r"em ghi nhớ|em nhớ rồi|em áp dụng|em thực hiện|em kiểm tra|em sửa ngay)\b",
    re.IGNORECASE,
)
POLITENESS_PATTERN = re.compile(
    r"\b(dạ|vâng|đúng rồi|chính xác|hợp lý|chuẩn)\b", re.IGNORECASE
)
TUTOR_PROMPT_PATTERN = re.compile(
    r"\b(vậy|theo em|em thử|là gì|tại sao|như thế nào|bao nhiêu|"
    r"đúng hay sai|hãy)\b",
    re.IGNORECASE,
)
ENDING_QUESTION_PATTERN = re.compile(r"[?？]\s*[,!.]*$")
PURE_ACKNOWLEDGEMENT_PATTERNS = [
    re.compile(
        r"^(dạ )?(vâng )?(em )?(đã )?(hiểu|rõ|nhớ|biết|nắm được)"
        r"( rồi)?( ạ)?$"
    ),
    re.compile(r"^(dạ )?(vâng|được|rồi|đúng|chính xác|chuẩn)( rồi)?( ạ)?$"),
    re.compile(
        r"^(dạ )?(em )?(cảm ơn|cám ơn) (thầy|cô|ai)( nhiều)?( ạ)?$"
    ),
    re.compile(
        r"^(dạ )?(em )?(hiểu|rõ) (bài|vấn đề|cách làm)( rồi)?( ạ)?$"
    ),
]


def _parse_labelled_turns(dialogue: str) -> list[DialogueTurn]:
    turns: list[DialogueTurn] = []
    role: str | None = None
    content_lines: list[str] = []

    def flush() -> None:
        if role is not None:
            turns.append(
                DialogueTurn(
                    turn_index=len(turns) + 1,
                    role="student" if role == "HS" else "tutor",
                    content="\n".join(content_lines),
                )
            )

    for line_number, line in enumerate(dialogue.splitlines(), start=1):
        match = TURN_PATTERN.match(line)
        if match:
            flush()
            role = match.group(1)
            content_lines = [match.group(2)]
        elif role is None:
            raise DialogueSplitError(
                "unknown_turn_label",
                f"Line {line_number} does not begin with HS: or AI:",
            )
        else:
            content_lines.append(line)
    flush()
    return turns


def _normalize_for_exact_match(text: str) -> str:
    return " ".join(
        re.sub(r"[^\wÀ-ỹ]", " ", text.casefold(), flags=re.UNICODE).split()
    )


def _word_count_bin(word_count: int) -> str:
    if word_count <= 5:
        return "<=5"
    if word_count <= 10:
        return "6-10"
    if word_count <= 20:
        return "11-20"
    return ">20"


def classify_final_student_turn(
    final_student_turn: str, previous_tutor_turn: str
) -> tuple[str, str, str]:
    """Classify a final student turn with transparent conservative heuristics."""

    normalized = _normalize_for_exact_match(final_student_turn)
    if any(pattern.fullmatch(normalized) for pattern in PURE_ACKNOWLEDGEMENT_PATTERNS):
        return (
            "pure_acknowledgement_or_thanks",
            "The normalized turn matches a narrow acknowledgement/thanks-only pattern.",
            "retain_as_trailing_student_outcome",
        )
    if ENDING_QUESTION_PATTERN.search(final_student_turn):
        return (
            "student_followup_or_confirmation_question",
            "The final student turn ends as a question and may signal unresolved follow-up.",
            "review_before_using_trailing_outcome_strategy",
        )
    if ACTION_PATTERN.search(final_student_turn):
        return (
            "action_commitment_or_completion",
            "The turn reports completion or states an intended next action.",
            "retain_as_trailing_student_outcome",
        )
    if "?" in previous_tutor_turn or TUTOR_PROMPT_PATTERN.search(previous_tutor_turn):
        return (
            "answer_or_explanation_to_tutor_prompt",
            "The preceding tutor turn is a question/prompt and the final turn is its response.",
            "retain_as_trailing_student_outcome",
        )
    return (
        "reflection_or_other_closing",
        "The turn is neither a narrow acknowledgement nor an explicit question/action.",
        "retain_as_trailing_student_outcome",
    )


def analyze_last_student_turns(
    rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Analyze alternating dialogues that end with a student turn."""

    analysis_rows: list[dict[str, str]] = []
    for source in sorted(rows, key=lambda row: str(row["sample_id"])):
        turns = _parse_labelled_turns(
            str(source.get("conversion_dialogue", "") or source.get("raw_dialogue", ""))
        )
        if not turns or turns[-1].role != "student":
            continue
        if any(previous.role == current.role for previous, current in zip(turns, turns[1:])):
            continue
        previous = turns[-2]
        final = turns[-1]
        if previous.role != "tutor":
            continue
        final_text = final.content.strip()
        previous_text = previous.content.strip()
        word_count = len(re.findall(r"\w+", final_text, flags=re.UNICODE))
        category, rationale, treatment = classify_final_student_turn(
            final_text, previous_text
        )
        analysis_rows.append(
            {
                "sample_id": str(source["sample_id"]),
                "source_batch": str(source.get("source_batch", "")),
                "source_file": str(source.get("source_file", "")),
                "source_row_number": str(source.get("source_row_number", "")),
                "grade": str(source.get("grade", "")),
                "lesson": str(source.get("lesson", "")),
                "previous_tutor_turn": previous_text,
                "final_student_turn": final_text,
                "word_count": str(word_count),
                "word_count_bin": _word_count_bin(word_count),
                "has_politeness_or_agreement_marker": str(
                    bool(POLITENESS_PATTERN.search(final_text))
                ).lower(),
                "has_understanding_marker": str(
                    bool(UNDERSTANDING_PATTERN.search(final_text))
                ).lower(),
                "has_thanks_marker": str(bool(THANKS_PATTERN.search(final_text))).lower(),
                "has_action_marker": str(bool(ACTION_PATTERN.search(final_text))).lower(),
                "ends_as_question": str(
                    bool(ENDING_QUESTION_PATTERN.search(final_text))
                ).lower(),
                "heuristic_category": category,
                "heuristic_rationale": rationale,
                "recommended_conversion_treatment": treatment,
                "heuristic_only": "true",
            }
        )

    summary: dict[str, object] = {
        "total_rows": len(analysis_rows),
        "grade_counts": dict(
            sorted(Counter(row["grade"] for row in analysis_rows).items())
        ),
        "category_counts": dict(
            sorted(Counter(row["heuristic_category"] for row in analysis_rows).items())
        ),
        "word_count_bin_counts": dict(
            sorted(Counter(row["word_count_bin"] for row in analysis_rows).items())
        ),
        "marker_counts": {
            field: sum(row[field] == "true" for row in analysis_rows)
            for field in (
                "has_politeness_or_agreement_marker",
                "has_understanding_marker",
                "has_thanks_marker",
                "has_action_marker",
                "ends_as_question",
            )
        },
        "treatment_counts": dict(
            sorted(
                Counter(
                    row["recommended_conversion_treatment"] for row in analysis_rows
                ).items()
            )
        ),
        "method": "deterministic_heuristic_v0",
        "limitations": [
            "Categories are heuristic analysis aids, not HNMU/UET adjudications.",
            "Politeness markers such as 'dạ' do not by themselves make a turn empty.",
            "A trailing student response may provide observed learning-outcome evidence.",
        ],
    }
    return analysis_rows, summary

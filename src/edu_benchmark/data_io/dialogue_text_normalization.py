"""Deterministic text normalization for HNMU dialogue fields.

The source workbook text remains immutable.  This module creates a canonical
derived representation for deterministic checks, duplicate detection, and
model prompts while retaining enough provenance to reproduce every change.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


DIALOGUE_NORMALIZATION_VERSION = "hnmu-dialogue-text-v1"

_ROLE_ALIASES = {
    "hs": "HS",
    "học sinh": "HS",
    "hoc sinh": "HS",
    "ai": "AI",
    "gia sư": "AI",
    "gia su": "AI",
}
_ROLE_PATTERN = r"(?:học\s+sinh|hoc\s+sinh|gia\s+sư|gia\s+su|hs|ai)"
_TURN_BOUNDARY = r"(?:^[ \t]*|(?<=[.!?])[ \t]*)"
_SAFE_AFTER_COLON_ANNOTATION_RE = re.compile(
    rf"(?im){_TURN_BOUNDARY}(?P<label>{_ROLE_PATTERN})\s*[:：]\s*"
    r"\[(?P<annotation>[^\[\]\r\n]+)\](?![ \t]*\[)[ \t]*(?=\S)"
)
_SAFE_BEFORE_COLON_ANNOTATION_RE = re.compile(
    rf"(?im){_TURN_BOUNDARY}(?P<label>{_ROLE_PATTERN})\s*"
    r"\[(?P<annotation>[^\[\]\r\n]+)\]\s*[:：][ \t]*(?=\S)"
)
_ANNOTATION_CANDIDATE_RE = re.compile(
    rf"(?im){_TURN_BOUNDARY}(?P<label>{_ROLE_PATTERN})\s*"
    r"(?:[:：]\s*\[|\[)"
)
_CANONICAL_ROLE_RE = re.compile(
    rf"(?im){_TURN_BOUNDARY}(?P<label>{_ROLE_PATTERN})\s*[:：]"
)
_HTML_BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


@dataclass(frozen=True)
class DialogueNormalizationResult:
    """One immutable raw-to-canonical dialogue transformation."""

    raw_text: str
    normalized_text: str
    raw_sha256: str
    normalized_sha256: str
    annotation_count: int
    flags: tuple[str, ...]
    html_break_count: int
    version: str = DIALOGUE_NORMALIZATION_VERSION

    @property
    def changed(self) -> bool:
        """Return whether the canonical representation differs from the source."""

        return self.raw_text != self.normalized_text


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_label(value: str) -> str:
    key = re.sub(r"\s+", " ", value.strip()).casefold()
    return _ROLE_ALIASES[key]


def _safe_annotation_starts(text: str) -> set[int]:
    return {
        match.start()
        for pattern in (
            _SAFE_AFTER_COLON_ANNOTATION_RE,
            _SAFE_BEFORE_COLON_ANNOTATION_RE,
        )
        for match in pattern.finditer(text)
    }


def _strip_safe_annotations(text: str) -> tuple[str, int, tuple[str, ...]]:
    candidate_starts = {match.start() for match in _ANNOTATION_CANDIDATE_RE.finditer(text)}
    safe_starts = _safe_annotation_starts(text)
    flags: list[str] = []
    if candidate_starts - safe_starts:
        flags.append("ambiguous_speaker_annotation")

    removed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal removed
        removed += 1
        return f"{_canonical_label(match.group('label'))}: "

    text = _SAFE_BEFORE_COLON_ANNOTATION_RE.sub(replace, text)
    text = _SAFE_AFTER_COLON_ANNOTATION_RE.sub(replace, text)
    return text, removed, tuple(sorted(set(flags)))


def _canonicalize_role_labels(text: str) -> str:
    pieces: list[str] = []
    cursor = 0
    for match in _CANONICAL_ROLE_RE.finditer(text):
        prefix = text[cursor : match.start()]
        if prefix:
            pieces.append(prefix)
        if pieces and pieces[-1] and not pieces[-1].endswith("\n"):
            pieces.append("\n")
        pieces.append(f"{_canonical_label(match.group('label'))}: ")
        cursor = match.end()
    pieces.append(text[cursor:])
    canonical = "".join(pieces)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in canonical.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def normalize_dialogue_text(dialogue: str) -> DialogueNormalizationResult:
    """Return a reproducible HNMU dialogue projection and its provenance.

    Only one balanced square-bracket annotation immediately adjacent to a
    speaker label is removed.  Ambiguous or repeated annotations are preserved
    and flagged.  Square brackets elsewhere remain untouched.
    """

    raw = str(dialogue or "")
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    html_break_count = len(_HTML_BREAK_RE.findall(text))
    text = _HTML_BREAK_RE.sub("\n", text)
    text, annotation_count, flags = _strip_safe_annotations(text)
    normalized = _canonicalize_role_labels(text)
    return DialogueNormalizationResult(
        raw_text=raw,
        normalized_text=normalized,
        raw_sha256=_sha256_text(raw),
        normalized_sha256=_sha256_text(normalized),
        annotation_count=annotation_count,
        flags=flags,
        html_break_count=html_break_count,
    )

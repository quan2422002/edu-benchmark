"""Tests for deterministic specialist-agent validators."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path) -> ModuleType:
    """Load a Python module directly from a repository path."""

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVIDENCE = load_module(
    "validate_evidence_matrix",
    ROOT / "agents/research-methodologist/scripts/validate_evidence_matrix.py",
)
TEACHER = load_module(
    "validate_teacher_packet",
    ROOT / "agents/teacher-collaboration-designer/scripts/validate_teacher_packet.py",
)


class EvidenceMatrixTests(unittest.TestCase):
    """Validate accepted and rejected evidence matrices."""

    def _write_matrix(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=EVIDENCE.REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    def _valid_row(self) -> dict[str, str]:
        return {
            column: "not_reported" for column in EVIDENCE.REQUIRED_COLUMNS
        } | {
            "record_id": "r-001",
            "title": "A tutoring benchmark",
            "year": "2025",
            "venue": "Example Conference",
            "url_or_doi": "https://example.org/paper",
            "publication_status": "peer_reviewed",
            "relevance_to_project": "Evaluates tutoring behavior",
        }

    def test_valid_matrix_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "matrix.csv"
            self._write_matrix(path, [self._valid_row()])
            self.assertEqual(EVIDENCE.validate_evidence_matrix(path), [])

    def test_duplicate_and_invalid_source_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "matrix.csv"
            first = self._valid_row()
            second = self._valid_row() | {"url_or_doi": "unknown"}
            self._write_matrix(path, [first, second])
            errors = EVIDENCE.validate_evidence_matrix(path)
            self.assertTrue(any("duplicate record_id" in error for error in errors))
            self.assertTrue(any("not a DOI" in error for error in errors))


class TeacherPacketTests(unittest.TestCase):
    """Validate teacher packet structure and plain-language constraints."""

    def _write_packet(self, directory: Path, technical_term: str = "") -> None:
        for filename in TEACHER.REQUIRED_FILES:
            path = directory / filename
            if filename in TEACHER.TASK_CARD_FILES:
                content = "\n".join(f"## {heading}" for heading in TEACHER.REQUIRED_TASK_HEADINGS)
                content += f"\n{technical_term}\n"
            else:
                content = "# Nội dung thử nghiệm\n"
            path.write_text(content, encoding="utf-8")
        (directory / "05-author-template.csv").write_text("topic\n", encoding="utf-8")
        (directory / "06-review-template.csv").write_text("decision\n", encoding="utf-8")

    def test_valid_packet_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            self._write_packet(directory)
            self.assertEqual(TEACHER.validate_teacher_packet(directory), [])

    def test_teacher_facing_technical_term_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            self._write_packet(directory, technical_term="YAML")
            errors = TEACHER.validate_teacher_packet(directory)
            self.assertTrue(any("technical term 'yaml'" in error for error in errors))

    def test_author_reviewer_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            self._write_packet(directory)
            author_path = directory / "02-author-task-card.md"
            author_path.write_text(
                author_path.read_text(encoding="utf-8") + "\nChọn Chấp nhận hoặc Cần sửa.\n",
                encoding="utf-8",
            )
            errors = TEACHER.validate_teacher_packet(directory)
            self.assertTrue(any("assigns reviewer decision" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

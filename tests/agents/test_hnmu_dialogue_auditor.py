"""Tests for the HNMU dialogue auditor specialist scaffold."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class HNMUDialogueAuditorSkillTests(unittest.TestCase):
    """Ensure the specialist has the context needed for Plan 04 use."""

    def test_skill_points_to_required_project_context(self) -> None:
        content = (ROOT / "agents/hnmu-dialogue-auditor/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("raw-dialogue-quality-checklist-v0.md", content)
        self.assertIn("raw-dialogue-audit-criteria-v0.csv", content)
        self.assertIn("fixed per-sample criteria registry", content)
        self.assertIn("shared/learning_resources/agent_context/README.md", content)
        self.assertIn("hnmu_scaffolding_method_canonical.md", content)
        self.assertIn("raw_dialogue_checklist_results.csv", content)
        self.assertIn("Do not", content)

    def test_reference_schema_names_required_columns(self) -> None:
        content = (ROOT / "agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-output-schema.md").read_text(
            encoding="utf-8"
        )
        for column in (
            "sample_id",
            "criterion_id",
            "result",
            "confidence_score",
            "evidence_fragment_id",
            "suggested_reviewer_action",
        ):
            self.assertIn(column, content)


if __name__ == "__main__":
    unittest.main()

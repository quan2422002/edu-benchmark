"""Static tests for the append-only coordination event contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CoordinationContractTests(unittest.TestCase):
    """Check required event schema fields and handoff sections."""

    def test_event_schema_supports_workflow_and_delegation_records(self) -> None:
        path = ROOT / "experiments/_templates/coordination-event.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(schema["oneOf"]), 3)

        workflow_required = set(schema["$defs"]["workflow_event"]["required"])
        self.assertTrue(
            {
                "schema_version",
                "event_id",
                "timestamp",
                "event_type",
                "actor",
                "task",
                "status",
                "input_paths",
                "allowed_write_paths",
                "output_paths",
                "open_questions",
            }.issubset(workflow_required)
        )

        delegation_required = set(schema["$defs"]["delegation_event"]["required"])
        self.assertTrue(
            {"delegation_id", "parent_session", "agent"}.issubset(
                delegation_required
            )
        )
        self.assertFalse(schema["$defs"]["workflow_event"]["additionalProperties"])
        self.assertFalse(schema["$defs"]["delegation_event"]["additionalProperties"])

    def test_handoff_has_audit_sections(self) -> None:
        content = (ROOT / "experiments/_templates/handoff.md").read_text(encoding="utf-8")
        for heading in (
            "Task or delegation request",
            "Follow-up or scope changes",
            "Inputs read",
            "Outputs created",
            "Orchestrator decision",
            "Uncertainty",
            "Open questions and next human decisions",
        ):
            self.assertIn(heading, content)


if __name__ == "__main__":
    unittest.main()

"""Static tests for the append-only coordination event contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CoordinationContractTests(unittest.TestCase):
    """Check required event schema fields and handoff sections."""

    def test_event_schema_required_fields(self) -> None:
        path = ROOT / "experiments/_templates/coordination-event.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        required = set(schema["required"])
        self.assertTrue(
            {
                "timestamp",
                "event_type",
                "delegation_id",
                "agent",
                "task",
                "status",
                "input_paths",
                "allowed_write_paths",
                "output_paths",
                "open_questions",
            }.issubset(required)
        )
        self.assertFalse(schema["additionalProperties"])

    def test_handoff_has_audit_sections(self) -> None:
        content = (ROOT / "experiments/_templates/handoff.md").read_text(encoding="utf-8")
        for heading in (
            "Delegation prompt",
            "Follow-up or steer messages",
            "Inputs read",
            "Outputs created",
            "Orchestrator decision",
            "Uncertainty",
            "Open questions and next human decisions",
        ):
            self.assertIn(heading, content)


if __name__ == "__main__":
    unittest.main()

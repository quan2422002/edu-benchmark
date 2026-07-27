"""Static contract tests for the pedagogical-principle annotator."""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "pedagogical-principle-annotator"
CANONICAL_PATHS = (
    "experiments/20260722_000940/outputs/benchmark_specification/task_discovery/pedagogical_principles.csv",
    "experiments/20260722_000940/outputs/benchmark_specification/task_discovery/task_discovery_codebook.md",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capabilities.csv",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capability_model.md",
    "experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/capability_overlap_matrix.csv",
)


class PedagogicalPrincipleAnnotatorTests(unittest.TestCase):
    def test_required_paths_are_directly_named(self) -> None:
        content = (ROOT / f"agents/{NAME}/SKILL.md").read_text(encoding="utf-8") + (ROOT / f"agents/{NAME}/references/two_pass_annotation_contract.md").read_text(encoding="utf-8")
        for path in CANONICAL_PATHS:
            self.assertIn(path, content)

    def test_authority_and_two_pass_rules_are_explicit(self) -> None:
        content = (ROOT / f"agents/{NAME}/SKILL.md").read_text(encoding="utf-8")
        for phrase in ("Do not design", "needs_uet_review", "Do not merge outputs", "pass 1", "pass 2", "another annotator's output", "unordered", "gold_response"):
            self.assertIn(phrase, content)
        self.assertNotIn("eight_task_candidate_branch/` during active annotation", content)

    def test_codex_adapter_is_pinned_and_thin(self) -> None:
        with (ROOT / f".codex/agents/{NAME}.toml").open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual(data["model"], "gpt-5.4-mini")
        self.assertEqual(data["model_reasoning_effort"], "medium")
        instructions = data["developer_instructions"]
        self.assertIn(f"agents/{NAME}/SKILL.md", instructions)
        self.assertIn("never launch codex exec", instructions)
        self.assertIn("never write confirmed", instructions)

    def test_discovery_link_and_generated_metadata(self) -> None:
        link = ROOT / f".agents/skills/{NAME}"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (ROOT / f"agents/{NAME}").resolve())
        metadata = (ROOT / f"agents/{NAME}/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("display_name:", metadata)
        self.assertIn("$pedagogical-principle-annotator", metadata)


if __name__ == "__main__":
    unittest.main()

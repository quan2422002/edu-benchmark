"""Static validation for Codex and Claude specialist adapters."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT_NAMES = ("research-methodologist", "teacher-collaboration-designer")


class AdapterTests(unittest.TestCase):
    """Ensure thin adapters exist and point to canonical skills."""

    def test_codex_adapters_have_required_fields(self) -> None:
        for name in AGENT_NAMES:
            path = ROOT / f".codex/agents/{name}.toml"
            with path.open("rb") as handle:
                data = tomllib.load(handle)
            self.assertEqual(data["name"], name)
            self.assertTrue(data["description"])
            self.assertIn(f"agents/{name}/SKILL.md", data["developer_instructions"])
            self.assertIn("never launch codex exec", data["developer_instructions"])

    def test_claude_adapters_have_required_frontmatter(self) -> None:
        for name in AGENT_NAMES:
            path = ROOT / f".claude/agents/{name}.md"
            content = path.read_text(encoding="utf-8")
            match = re.match(r"\A---\n(.*?)\n---\n", content, flags=re.DOTALL)
            self.assertIsNotNone(match, path)
            frontmatter = match.group(1) if match else ""
            self.assertIn(f"name: {name}", frontmatter)
            self.assertIn("description:", frontmatter)
            self.assertIn(f"agents/{name}/SKILL.md", content)
            self.assertIn("background: false", frontmatter)

    def test_skill_discovery_links_target_canonical_skills(self) -> None:
        for name in AGENT_NAMES:
            path = ROOT / f".agents/skills/{name}"
            self.assertTrue(path.is_symlink(), path)
            self.assertEqual(path.resolve(), (ROOT / f"agents/{name}").resolve())

    def test_skills_have_no_placeholders(self) -> None:
        for name in AGENT_NAMES:
            content = (ROOT / f"agents/{name}/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("TODO", content)
            self.assertLess(len(content.splitlines()), 500)


if __name__ == "__main__":
    unittest.main()

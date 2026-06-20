"""Documentation contract and local-link tests for P01."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = (ROOT / "README.md", ROOT / "ARCHITECTURE.md", ROOT / "AGENTS.md")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class DocumentationTests(unittest.TestCase):
    """Check required content and relative links."""

    def test_required_documents_exist_and_are_not_empty(self) -> None:
        for path in DOCS:
            self.assertTrue(path.is_file(), path)
            self.assertTrue(path.read_text(encoding="utf-8").strip(), path)

    def test_readme_contract(self) -> None:
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        for required in (
            "proof-of-concept",
            "Expert teachers",
            "research-methodologist",
            "teacher-collaboration-designer",
            "codex exec",
            "Claude Code",
            "runtime testing is deferred",
        ):
            self.assertIn(required, content)

    def test_architecture_contract(self) -> None:
        content = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for required in (
            "Components and ownership",
            "Delegation sequence",
            "Observability model",
            "Permissions and safety",
            "Known limitations",
            "private chain-of-thought",
        ):
            self.assertIn(required, content)

    def test_agents_contract(self) -> None:
        content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in (
            "APPROVED",
            "native observable subagent threads",
            "codex exec",
            "expert-teacher judgment",
            "preserve unrelated user changes",
        ):
            self.assertIn(required, content)

    def test_local_markdown_links_resolve(self) -> None:
        for path in DOCS:
            content = path.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(content):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target_path = target.split("#", maxsplit=1)[0]
                resolved = (path.parent / target_path).resolve()
                self.assertTrue(resolved.exists(), f"Broken link in {path}: {target}")


if __name__ == "__main__":
    unittest.main()

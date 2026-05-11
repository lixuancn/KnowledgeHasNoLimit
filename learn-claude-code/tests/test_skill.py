"""Tests for the SkillLoader."""

import tempfile
import unittest
from pathlib import Path

from tool.tool_skill import SkillLoader


class TestSkillLoader(unittest.TestCase):
    """Test cases for loading markdown-defined skills."""

    def test_load_skill_with_front_matter(self):
        """Loads meta and body from a SKILL.md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills" / "demo"
            skills_dir.mkdir(parents=True)
            skill_file = skills_dir / "SKILL.md"
            skill_file.write_text(
                """---
name: demo-skill
description: A demo skill
tags:
  - python
  - tools
---
# Demo Skill

Use this skill for testing.
""",
                encoding="utf-8",
            )

            loader = SkillLoader(Path(tmpdir) / "skills")
            skills = loader.load()

            self.assertIn("demo-skill", skills)
            self.assertEqual(skills["demo-skill"]["meta"]["description"], "A demo skill")
            self.assertEqual(skills["demo-skill"]["meta"]["tags"], ["python", "tools"])
            self.assertIn("Use this skill for testing.", skills["demo-skill"]["body"])


if __name__ == "__main__":
    unittest.main()

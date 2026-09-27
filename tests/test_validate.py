from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate import validate_repository  # noqa: E402


class RepositoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.copy = Path(self.temp_dir.name) / "project-planner"
        shutil.copytree(
            ROOT,
            self.copy,
            ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__"),
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def assert_has_error(self, errors: List[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"Expected error containing {fragment!r}; got {errors!r}",
        )

    def test_repository_passes(self) -> None:
        self.assertEqual(validate_repository(self.copy), [])

    def test_version_drift_is_rejected(self) -> None:
        manifest_path = self.copy / "plugins/project-planner/.codex-plugin/plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = "9.9.9"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "does not match VERSION")

    def test_marketplace_path_escape_is_rejected(self) -> None:
        marketplace_path = self.copy / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        marketplace["plugins"][0]["source"]["path"] = "../../outside"
        marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "escapes repository root")

    def test_broken_markdown_link_is_rejected(self) -> None:
        readme = self.copy / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n[Missing](docs/does-not-exist.md)\n",
            encoding="utf-8",
        )
        self.assert_has_error(validate_repository(self.copy), "broken local link")

    def test_placeholder_is_rejected(self) -> None:
        marker = "[TO" + "DO: replace before release]"
        readme = self.copy / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + marker, encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "unresolved placeholder")

    def test_duplicate_json_key_is_rejected(self) -> None:
        marketplace = self.copy / "marketplace.json"
        text = marketplace.read_text(encoding="utf-8")
        marketplace.write_text(text.replace('{\n  "name":', '{\n  "name": "duplicate",\n  "name":', 1), encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "duplicate object key")

    def test_machine_specific_path_is_rejected(self) -> None:
        private_path = "/Us" + "ers/private-user/secrets.txt"
        readme = self.copy / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + private_path, encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "machine-specific macOS user path")

    def test_release_symlink_is_rejected(self) -> None:
        (self.copy / "linked-readme.md").symlink_to(self.copy / "README.md")
        self.assert_has_error(validate_repository(self.copy), "must not be symlinks")

    def test_duplicate_trigger_id_is_rejected(self) -> None:
        path = self.copy / "tests/trigger-cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))
        cases[1]["id"] = cases[0]["id"]
        path.write_text(json.dumps(cases), encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "duplicates id")

    def test_missing_negative_trigger_cases_is_rejected(self) -> None:
        path = self.copy / "tests/trigger-cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps([c for c in cases if c["expected"] == "trigger"]), encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "at least three 'skip' cases")

    def test_duplicate_skill_metadata_is_rejected(self) -> None:
        path = self.copy / "plugins/project-planner/skills/project-planner/SKILL.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("---\n", "---\nname: duplicate\n", 1), encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "duplicate frontmatter key")

    def test_missing_ui_policy_is_rejected(self) -> None:
        path = self.copy / "plugins/project-planner/skills/project-planner/agents/openai.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text("\n".join(line for line in text.splitlines() if "allow_implicit_invocation:" not in line), encoding="utf-8")
        self.assert_has_error(validate_repository(self.copy), "missing or invalid policy.allow_implicit_invocation")


if __name__ == "__main__":
    unittest.main()

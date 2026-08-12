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


if __name__ == "__main__":
    unittest.main()

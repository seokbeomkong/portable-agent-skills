from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class PluginPackageTests(unittest.TestCase):
    def test_root_is_a_valid_multi_skill_codex_plugin(self) -> None:
        manifest_path = ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "portable-agent-skills")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("interface", manifest)

    def test_plugin_package_is_deterministic_and_contains_every_registry_skill(self) -> None:
        registry = json.loads((ROOT / "registry.yaml").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "portable-agent-skills.plugin.zip"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "package_plugin.py"),
                    "--destination",
                    str(destination),
                    "--version",
                    "9.8.7",
                    "--check",
                ],
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(destination) as archive:
                all_names = archive.namelist()
                names = set(all_names)
                packaged_manifest = json.loads(
                    archive.read(
                        "portable-agent-skills/.codex-plugin/plugin.json"
                    ).decode("utf-8")
                )
        self.assertIn(
            "portable-agent-skills/.codex-plugin/plugin.json", names
        )
        self.assertEqual(len(all_names), len(names))
        self.assertEqual(packaged_manifest["version"], "9.8.7")
        for skill in registry["skills"]:
            self.assertIn(
                f"portable-agent-skills/{skill['path']}/SKILL.md", names
            )

    def test_release_workflow_publishes_plugin_and_every_skill_archive(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("portable-agent-skills.plugin.zip", workflow)
        self.assertIn("release-assets/*.skill.zip", workflow)


if __name__ == "__main__":
    unittest.main()

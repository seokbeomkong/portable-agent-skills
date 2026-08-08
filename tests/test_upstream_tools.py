from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_upstreams import build_report, compare_state  # noqa: E402
from prepare_upstream_review import apply_observation  # noqa: E402
from registry_lib import load_json_yaml  # noqa: E402


class UpstreamToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lock_entry = {
            "repository": "nextlevelbuilder/ui-ux-pro-max-skill",
            "ref": "main",
            "integrated_release": "v2.14.1",
            "integrated_commit": "a" * 40,
            "last_checked": "2026-08-08T00:00:00Z",
            "review_policy": "human-required",
        }

    def test_compare_state_reports_current(self) -> None:
        result = compare_state(self.lock_entry, {"release": "v2.14.1", "commit": "a" * 40})
        self.assertFalse(result["update_available"])
        self.assertFalse(result["changes"]["release"])
        self.assertFalse(result["changes"]["commit"])

    def test_compare_state_reports_release_change(self) -> None:
        result = compare_state(self.lock_entry, {"release": "v2.15.0", "commit": "a" * 40})
        self.assertTrue(result["update_available"])
        self.assertTrue(result["changes"]["release"])
        self.assertFalse(result["changes"]["commit"])

    def test_compare_state_reports_commit_change(self) -> None:
        result = compare_state(self.lock_entry, {"release": "v2.14.1", "commit": "b" * 40})
        self.assertTrue(result["update_available"])
        self.assertFalse(result["changes"]["release"])
        self.assertTrue(result["changes"]["commit"])

    def test_build_report_separates_updates_current_and_errors(self) -> None:
        registry = {
            "skills": [
                {
                    "id": "one",
                    "display_name": "One",
                    "origin": {"repository": "owner/one"},
                },
                {
                    "id": "two",
                    "display_name": "Two",
                    "origin": {"repository": "owner/two"},
                },
                {
                    "id": "three",
                    "display_name": "Three",
                    "origin": {"repository": "owner/three"},
                },
            ]
        }
        lock = {
            "skills": {
                "one": {**self.lock_entry, "repository": "owner/one"},
                "two": {**self.lock_entry, "repository": "owner/two"},
                "three": {**self.lock_entry, "repository": "owner/three"},
            }
        }
        states = {
            "one": {"release": "v2.14.1", "commit": "a" * 40},
            "two": {"release": "v2.15.0", "commit": "b" * 40},
            "three": {"error": "rate limited"},
        }
        report = build_report(registry, lock, states, checked_at="2026-08-08T00:00:00Z")
        self.assertEqual([item["id"] for item in report["current"]], ["one"])
        self.assertEqual([item["id"] for item in report["updates"]], ["two"])
        self.assertEqual(report["errors"][0]["id"], "three")
        self.assertIn("upstream-skill:two", report["updates"][0]["issue_marker"])

    def test_review_preparation_preserves_integrated_revision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_root = Path(td)
            shutil.copytree(ROOT / "upstream", temp_root / "upstream")
            shutil.copy2(ROOT / "registry.yaml", temp_root / "registry.yaml")
            before_registry = load_json_yaml(temp_root / "registry.yaml")
            before_lock = load_json_yaml(temp_root / "upstream" / "upstream-lock.json")
            report = {
                "checked_at": "2026-08-09T00:00:00Z",
                "updates": [
                    {
                        "id": "ui-ux-pro-max",
                        "latest": {"release": "v2.15.0", "commit": "b" * 40},
                        "integrated": {
                            "release": "v2.14.1",
                            "commit": "abb7f2fd5a083fa1ff55c326a963ff0d95c33f99",
                        },
                    }
                ],
                "current": [],
                "errors": [],
            }
            changed = apply_observation(temp_root, report)
            after_registry = load_json_yaml(temp_root / "registry.yaml")
            after_lock = load_json_yaml(temp_root / "upstream" / "upstream-lock.json")
            observed = load_json_yaml(temp_root / "upstream" / "upstream-observed.json")

            self.assertIn(temp_root / "registry.yaml", changed)
            self.assertIn(temp_root / "upstream" / "upstream-observed.json", changed)
            self.assertEqual(before_lock, after_lock)
            self.assertEqual(
                before_registry["skills"][0]["origin"]["integrated_commit"],
                after_registry["skills"][0]["origin"]["integrated_commit"],
            )
            self.assertEqual(before_registry["skills"][0]["origin"]["release"], after_registry["skills"][0]["origin"]["release"])
            self.assertEqual(after_registry["skills"][0]["status"], "review-required")
            self.assertEqual(observed["observations"]["ui-ux-pro-max"]["release"], "v2.15.0")
            self.assertEqual(observed["observations"]["ui-ux-pro-max"]["commit"], "b" * 40)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryStructureTests(unittest.TestCase):
    def test_scheduled_watcher_uses_safe_issue_only_permissions(self) -> None:
        text = (ROOT / ".github/workflows/upstream-watch.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "15 0 * * 1"', text)
        self.assertIn("contents: read", text)
        self.assertIn("issues: write", text)
        self.assertNotIn("contents: write", text)
        self.assertIn("upstream-skill:", (ROOT / "scripts/check_upstreams.py").read_text(encoding="utf-8"))
        self.assertIn("never auto-merges", text)

    def test_draft_pr_workflow_is_manual_and_does_not_advance_lock(self) -> None:
        text = (ROOT / ".github/workflows/prepare-upstream-review.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch", text)
        self.assertIn("pull-requests: write", text)
        self.assertIn("--draft", text)
        self.assertNotIn("upstream/upstream-lock.json", text)
        self.assertIn("does **not** advance integrated revisions", text)

    def test_issue_form_uses_github_issue_form_fields(self) -> None:
        text = (ROOT / ".github/ISSUE_TEMPLATE/upstream-update.yml").read_text(encoding="utf-8")
        self.assertIn("description:", text)
        self.assertNotIn("\nabout:", text)
        self.assertIn("body:", text)

    def test_release_workflow_publishes_individual_skill_zip(self) -> None:
        text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn('tags:\n      - "registry-v*"', text)
        self.assertIn('release-assets/${skill_id}.skill.zip', text)
        self.assertIn("gh release create", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ui-ux-pro-max"
SCRIPTS = SKILL / "scripts"


def run_search(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "search.py"), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def run_legacy(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "uiux_query.py"), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


class UiUxFullPortTests(unittest.TestCase):
    def test_legacy_launcher_preserves_json_container_contracts(self) -> None:
        domain = run_legacy("analytics dashboard", "--domain", "product", "--json")
        self.assertEqual(domain.returncode, 0, domain.stderr)
        self.assertIsInstance(json.loads(domain.stdout), list)

        stack = run_legacy("performance", "--stack", "nextjs", "--json")
        self.assertEqual(stack.returncode, 0, stack.stderr)
        stack_payload = json.loads(stack.stdout)
        self.assertEqual(stack_payload["stack"], "nextjs")
        self.assertTrue(stack_payload["guidelines"])

        design = run_legacy("beauty spa", "--design-system", "--json")
        self.assertEqual(design.returncode, 0, design.stderr)
        design_payload = json.loads(design.stdout)
        self.assertIn("palette", design_payload)
        self.assertIn("typography", design_payload)

    def test_complete_upstream_engine_and_catalog_are_bundled(self) -> None:
        required = [
            "scripts/core.py",
            "scripts/design_system.py",
            "scripts/search.py",
            "scripts/validate_data.py",
            "data/products.csv",
            "data/styles.csv",
            "data/colors.csv",
            "data/typography.csv",
            "data/ux-guidelines.csv",
            "data/charts.csv",
            "data/icons.csv",
            "data/motion.csv",
            "data/google-fonts.csv",
            "data/ui-reasoning.csv",
        ]
        self.assertEqual([path for path in required if not (SKILL / path).is_file()], [])
        self.assertEqual(len(list((SKILL / "data" / "stacks").glob("*.csv"))), 22)
        data_bytes = sum(path.stat().st_size for path in (SKILL / "data").rglob("*.csv"))
        self.assertGreater(data_bytes, 1_000_000)

    def test_korean_query_is_normalized_before_full_catalog_search(self) -> None:
        result = run_search("사스 대시보드", "--domain", "product", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["count"], 0, payload)

    def test_no_match_is_explicit_in_domain_search(self) -> None:
        result = run_search(
            "zzqqxx totally invented gibberish", "--domain", "ux", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["count"], 0)
        self.assertIn("suggestions", payload)

    def test_design_system_declares_when_it_used_general_fallbacks(self) -> None:
        result = run_search(
            "zzqqxx totally invented gibberish", "--design-system", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)["design_system"]
        self.assertFalse(payload["catalog_match"]["matched"])
        self.assertGreater(len(payload["catalog_match"]["unmatched_domains"]), 0)
        rendered = run_search(
            "zzqqxx totally invented gibberish",
            "--design-system",
            "--format",
            "markdown",
        )
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        self.assertIn("general fallback", rendered.stdout.lower())


if __name__ == "__main__":
    unittest.main()

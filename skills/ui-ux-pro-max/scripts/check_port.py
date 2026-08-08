#!/usr/bin/env python3
"""Local sanity checks for the portable UI/UX Pro Max Skill."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERY = ROOT / "scripts" / "uiux_query.py"
CATALOG = ROOT / "references" / "portable-catalog.json"


def run(*args: str) -> str:
    proc = subprocess.run([sys.executable, str(QUERY), *args], check=True, text=True, capture_output=True)
    return proc.stdout


def main() -> int:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert len(data["profiles"]) >= 15
    assert len(data["styles"]) >= 12
    assert len(data["stacks"]) >= 20

    out = run("beauty spa wellness", "--design-system", "-p", "Serenity Spa", "--json")
    ds = json.loads(out)
    assert ds["profile"] == "beauty-spa"
    assert ds["palette"]["primary"].startswith("#")

    out = run("analytics dashboard", "--domain", "product", "--json")
    rows = json.loads(out)
    assert rows and rows[0]["id"] == "dashboard"

    out = run("--stack", "nextjs", "--json")
    stack = json.loads(out)
    assert stack["stack"] == "nextjs" and stack["guidelines"]

    with tempfile.TemporaryDirectory() as td:
        run("saas analytics", "--design-system", "-p", "Test App", "--persist", "--output-dir", td)
        assert (Path(td) / "design-system" / "test-app" / "MASTER.md").exists()

    print("portable skill checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

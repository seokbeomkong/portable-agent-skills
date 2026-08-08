#!/usr/bin/env python3
"""Validate the full OpenAI port and run representative engine checks."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"


def run(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "search.py"), *args, "--json"],
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="strict",
    )
    return json.loads(result.stdout)


def main() -> int:
    required = [
        "SKILL.md", "agents/openai.yaml", "LICENSE", "THIRD_PARTY_NOTICES.md",
        "CHANGELOG.md", "skill.meta.yaml", "scripts/core.py",
        "scripts/design_system.py", "scripts/search.py", "scripts/validate_data.py",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("missing required files: " + ", ".join(missing))
    if len(list((DATA / "stacks").glob("*.csv"))) != 22:
        raise SystemExit("expected all 22 upstream stack catalogs")
    if sum(path.stat().st_size for path in DATA.rglob("*.csv")) <= 1_000_000:
        raise SystemExit("full upstream catalog is not bundled")

    korean = run("사스 대시보드", "--domain", "product")
    assert korean["count"] > 0
    no_match = run("zzqqxx invented gibberish", "--domain", "ux")
    assert no_match["count"] == 0 and "suggestions" in no_match
    stack = run("performance", "--stack", "nextjs")
    assert stack["stack"] == "nextjs" and stack["count"] > 0

    with tempfile.TemporaryDirectory() as td:
        payload = run(
            "saas analytics", "--design-system", "-p", "Test App", "--persist",
            "--output-dir", td,
        )
        master = Path(payload["persistence"]["master_file"])
        assert master.is_file() and master.is_relative_to(Path(td))

    subprocess.run([sys.executable, str(SCRIPTS / "validate_data.py")], check=True)
    print("ui-ux-pro-max full port: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

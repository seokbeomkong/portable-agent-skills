#!/usr/bin/env python3
"""Generate the README Skill catalog from registry.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from registry_lib import load_json_yaml

START = "<!-- REGISTRY:START -->"
END = "<!-- REGISTRY:END -->"


def _target(value: Any) -> str:
    if not isinstance(value, dict) or not value.get("supported"):
        return "—"
    level = str(value.get("level", "supported")).replace("-", " ").title()
    return f"✅ {level}"


def _status(value: str) -> str:
    labels = {
        "current": "🟢 Current",
        "update-available": "🟡 Update available",
        "review-required": "🟠 Review required",
        "broken": "🔴 Broken",
        "archived": "⚫ Archived",
        "tracked-only": "🔗 Tracked only",
    }
    return labels.get(value, value)


def render_catalog(registry: dict[str, Any]) -> str:
    lines = [
        "| Skill | Kind | Upstream | ChatGPT Web | Codex | Port version | Integrated upstream | Status |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for skill in sorted(registry.get("skills", []), key=lambda item: item["id"]):
        skill_path = skill["path"]
        origin = skill.get("origin", {})
        repository = origin.get("repository", "—")
        upstream = f"[{repository}](https://github.com/{repository})" if repository != "—" else "—"
        release = origin.get("release") or str(origin.get("integrated_commit", ""))[:7] or "—"
        lines.append(
            "| "
            f"[{skill['display_name']}]({skill_path}) | "
            f"`{skill.get('kind', 'unknown')}` | "
            f"{upstream} | "
            f"{_target(skill.get('targets', {}).get('chatgpt_web'))} | "
            f"{_target(skill.get('targets', {}).get('codex'))} | "
            f"`{skill.get('port_version', '—')}` | "
            f"`{release}` | "
            f"{_status(skill.get('status', 'unknown'))} |"
        )
    return "\n".join(lines)


def replace_catalog(readme: str, catalog: str) -> str:
    if START not in readme or END not in readme:
        raise ValueError(f"README must contain {START} and {END}")
    before, remainder = readme.split(START, 1)
    _, after = remainder.split(END, 1)
    return f"{before}{START}\n{catalog}\n{END}{after}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    registry = load_json_yaml(root / "registry.yaml")
    readme_path = root / "README.md"
    current = readme_path.read_text(encoding="utf-8")
    expected = replace_catalog(current, render_catalog(registry))
    if args.check:
        if current != expected:
            print("README catalog is out of date; run python scripts/generate_catalog.py", file=sys.stderr)
            return 1
        print("README catalog: PASS")
        return 0
    readme_path.write_text(expected, encoding="utf-8")
    print(f"Updated {readme_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

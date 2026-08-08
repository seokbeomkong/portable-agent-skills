#!/usr/bin/env python3
"""Record newly observed upstream state without advancing integrated revisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from registry_lib import load_json_yaml


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def apply_observation(root: Path, report: dict[str, Any]) -> list[Path]:
    registry_path = root / "registry.yaml"
    observed_path = root / "upstream" / "upstream-observed.json"
    registry = load_json_yaml(registry_path)
    observed = load_json_yaml(observed_path) if observed_path.exists() else {"schema_version": 1, "observations": {}}
    observations = observed.setdefault("observations", {})
    skills = {skill["id"]: skill for skill in registry.get("skills", [])}
    changed: list[Path] = []

    for update in report.get("updates", []):
        skill_id = update["id"]
        latest = update["latest"]
        observations[skill_id] = {
            "release": latest.get("release"),
            "commit": latest.get("commit"),
            "observed_at": report.get("checked_at"),
            "status": "review-required",
        }
        if skill_id in skills:
            skills[skill_id]["status"] = "review-required"

    if report.get("updates"):
        _write(registry_path, registry)
        _write(observed_path, observed)
        changed.extend([registry_path, observed_path])
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    report = load_json_yaml(args.report.resolve())
    changed = apply_observation(root, report)
    if not changed:
        print("No upstream review changes were required.")
        return 0
    for path in changed:
        print(f"UPDATED {path.relative_to(root)}")
    print("Integrated upstream revisions were intentionally left unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

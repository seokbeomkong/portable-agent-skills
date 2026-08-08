#!/usr/bin/env python3
"""Run the validation command declared by each registered Skill."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from registry_lib import load_json_yaml, validate_registry


def commands_for_registry(registry: dict[str, Any]) -> list[tuple[str, str]]:
    commands: list[tuple[str, str]] = []
    for skill in registry.get("skills", []):
        command = (skill.get("validation") or {}).get("command")
        if isinstance(command, str) and command.strip():
            commands.append((skill["id"], command))
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    registry = load_json_yaml(root / "registry.yaml")
    errors = validate_registry(root, registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for skill_id, command in commands_for_registry(registry):
        tokens = shlex.split(command)
        if tokens and tokens[0] in {"python", "python3", "py"}:
            tokens[0] = sys.executable
        print(f"CHECK {skill_id}: {command}")
        completed = subprocess.run(tokens, cwd=root, check=False)
        if completed.returncode != 0:
            print(f"ERROR: {skill_id} check failed with exit code {completed.returncode}", file=sys.stderr)
            return completed.returncode
    print("Registered Skill checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

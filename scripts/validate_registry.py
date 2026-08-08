#!/usr/bin/env python3
"""Validate registry metadata and every distributable Skill."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from registry_lib import RegistryError, load_json_yaml, validate_registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        registry = load_json_yaml(root / "registry.yaml")
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate_registry(root, registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Registry validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Registry validation: PASS ({len(registry['skills'])} skill(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build deterministic, single-Skill ZIP archives."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from registry_lib import RegistryError, iter_skill_files, load_json_yaml, safe_relative_path, validate_registry

FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def package_skill(root: Path, skill: dict, destination: Path) -> Path:
    skill_id = skill["id"]
    source_rel = safe_relative_path(skill["path"], field=f"{skill_id}.path")
    skill_dir = root.joinpath(*source_rel.parts)
    files = list(iter_skill_files(skill_dir))
    destination.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, relative in files:
            archive_name = f"{skill_id}/{relative.as_posix()}"
            info = zipfile.ZipInfo(archive_name, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    limit_mb = skill.get("validation", {}).get("package_limit_mb", 25)
    if destination.stat().st_size > limit_mb * 1024 * 1024:
        destination.unlink(missing_ok=True)
        raise RegistryError(f"{skill_id}: packaged archive exceeds {limit_mb} MB")
    with zipfile.ZipFile(destination) as archive:
        bad = archive.testzip()
        if bad:
            destination.unlink(missing_ok=True)
            raise RegistryError(f"{skill_id}: ZIP integrity failed at {bad}")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Build twice and verify deterministic bytes")
    args = parser.parse_args()
    root = args.root.resolve()
    registry = load_json_yaml(root / "registry.yaml")
    errors = validate_registry(root, registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    for skill in registry["skills"]:
        if not skill.get("license", {}).get("redistribution", False):
            print(f"SKIP {skill['id']}: redistribution not allowed")
            continue
        destination = root / skill["artifact"]
        first = package_skill(root, skill, destination).read_bytes()
        if args.check:
            second = package_skill(root, skill, destination).read_bytes()
            if first != second:
                print(f"ERROR: {skill['id']} package is not deterministic", file=sys.stderr)
                return 1
        print(f"PACKAGED {skill['id']}: {destination.relative_to(root)} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

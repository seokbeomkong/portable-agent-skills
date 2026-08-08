#!/usr/bin/env python3
"""Build a deterministic Codex plugin archive from every registered Skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

from registry_lib import RegistryError, iter_skill_files, load_json_yaml, safe_relative_path, validate_registry


FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
PLUGIN_ROOT = "portable-agent-skills"
ROOT_FILES = (
    PurePosixPath("README.md"),
    PurePosixPath("LICENSE"),
    PurePosixPath("THIRD_PARTY_NOTICES.md"),
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def validate_manifest(root: Path) -> dict:
    path = root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"invalid plugin manifest: {exc}") from exc
    if manifest.get("name") != PLUGIN_ROOT:
        raise RegistryError(f"plugin name must be {PLUGIN_ROOT!r}")
    if manifest.get("skills") != "./skills/":
        raise RegistryError("plugin skills path must be './skills/'")
    for field in ("version", "description", "author", "interface"):
        if not manifest.get(field):
            raise RegistryError(f"plugin manifest missing {field}")
    return manifest


def _write(
    archive: zipfile.ZipFile,
    source: Path,
    relative: PurePosixPath,
    written: set[str],
) -> None:
    _write_bytes(archive, source.read_bytes(), relative, written)


def _write_bytes(
    archive: zipfile.ZipFile,
    content: bytes,
    relative: PurePosixPath,
    written: set[str],
) -> None:
    archive_name = f"{PLUGIN_ROOT}/{relative.as_posix()}"
    if archive_name in written:
        raise RegistryError(f"duplicate plugin archive member: {archive_name}")
    written.add(archive_name)
    info = zipfile.ZipInfo(archive_name, date_time=FIXED_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(
        info,
        content,
        compress_type=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    )


def package_plugin(
    root: Path, registry: dict, destination: Path, version: str | None = None
) -> Path:
    manifest = validate_manifest(root)
    packaged_version = version or manifest["version"]
    if not SEMVER_RE.fullmatch(packaged_version):
        raise RegistryError(f"invalid plugin semantic version: {packaged_version!r}")
    manifest["version"] = packaged_version
    manifest_bytes = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        written: set[str] = set()
        _write_bytes(
            archive,
            manifest_bytes,
            PurePosixPath(".codex-plugin/plugin.json"),
            written,
        )
        for relative in ROOT_FILES:
            source = root.joinpath(*relative.parts)
            if not source.is_file() or source.is_symlink():
                raise RegistryError(f"missing or unsafe plugin file: {relative.as_posix()}")
            _write(archive, source, relative, written)

        for skill in sorted(registry["skills"], key=lambda entry: entry["id"]):
            if not (skill.get("license") or {}).get("redistribution", False):
                continue
            skill_rel = safe_relative_path(skill["path"], field=f"{skill['id']}.path")
            skill_dir = root.joinpath(*skill_rel.parts)
            for source, relative in iter_skill_files(skill_dir):
                _write(archive, source, skill_rel / relative, written)

    with zipfile.ZipFile(destination) as archive:
        bad = archive.testzip()
        if bad:
            destination.unlink(missing_ok=True)
            raise RegistryError(f"plugin ZIP integrity failed at {bad}")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path)
    parser.add_argument(
        "--version",
        help="Semantic version embedded in the archive (release workflows pass the tag version)",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    registry = load_json_yaml(root / "registry.yaml")
    errors = validate_registry(root, registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    destination = (
        args.destination.resolve()
        if args.destination
        else root / "dist" / PLUGIN_ROOT / "plugin.zip"
    )
    try:
        first = package_plugin(root, registry, destination, args.version).read_bytes()
        if args.check:
            second = package_plugin(root, registry, destination, args.version).read_bytes()
            if first != second:
                raise RegistryError("plugin package is not deterministic")
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"PACKAGED {PLUGIN_ROOT}: {destination} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

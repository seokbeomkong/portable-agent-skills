#!/usr/bin/env python3
"""Shared, dependency-free helpers for the portable Agent Skills registry."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REQUIRED_SKILL_FILES = ("SKILL.md", "agents/openai.yaml")
IGNORED_NAMES = {".DS_Store"}
IGNORED_SUFFIXES = {".pyc"}


class RegistryError(ValueError):
    """Raised when registry data or a Skill path is unsafe."""


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML without requiring a YAML dependency."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryError(f"missing metadata file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryError(f"{path} is not valid JSON-compatible YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError(f"{path} must contain an object at the top level")
    return data


def parse_skill_frontmatter(path: Path) -> dict[str, str]:
    """Parse the simple scalar YAML frontmatter used by SKILL.md."""

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return values
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key.strip()] = value
    return {}


def safe_relative_path(value: str, *, field: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise RegistryError(f"{field} must be a safe repository-relative path: {value!r}")
    return path


def iter_skill_files(skill_dir: Path) -> Iterable[tuple[Path, PurePosixPath]]:
    """Yield safe regular files under a Skill, rejecting symlinks."""

    if skill_dir.is_symlink():
        raise RegistryError(f"symlink Skill directory is not allowed: {skill_dir}")
    for path in sorted(skill_dir.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(skill_dir)
        if path.is_symlink():
            raise RegistryError(f"symlink is not allowed in a distributable Skill: {relative.as_posix()}")
        if any(part == "__pycache__" for part in relative.parts):
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            raise RegistryError(f"non-regular file is not allowed: {relative.as_posix()}")
        if path.name in IGNORED_NAMES or path.suffix in IGNORED_SUFFIXES:
            continue
        yield path, PurePosixPath(*relative.parts)


def _validate_lock(root: Path, skills: list[dict[str, Any]], errors: list[str]) -> None:
    lock_path = root / "upstream" / "upstream-lock.json"
    if not lock_path.exists():
        errors.append("missing upstream/upstream-lock.json")
        return
    try:
        lock = load_json_yaml(lock_path)
    except RegistryError as exc:
        errors.append(str(exc))
        return
    entries = lock.get("skills")
    if not isinstance(entries, dict):
        errors.append("upstream lock must contain a skills object")
        return
    for skill in skills:
        if skill.get("kind") not in {"port", "extended", "tracked"}:
            continue
        skill_id = skill.get("id", "<unknown>")
        entry = entries.get(skill_id)
        if not isinstance(entry, dict):
            errors.append(f"{skill_id}: missing upstream lock entry")
            continue
        origin = skill.get("origin") or {}
        comparisons = {
            "repository": origin.get("repository"),
            "ref": origin.get("ref"),
            "integrated_release": origin.get("release"),
            "integrated_commit": origin.get("integrated_commit"),
        }
        for key, expected in comparisons.items():
            if entry.get(key) != expected:
                errors.append(
                    f"{skill_id}: upstream lock {key}={entry.get(key)!r} does not match registry value {expected!r}"
                )


def validate_registry(root: Path, registry: dict[str, Any]) -> list[str]:
    """Return all validation errors without mutating the repository."""

    errors: list[str] = []
    if registry.get("schema_version") != 1:
        errors.append("registry schema_version must be 1")
    if not isinstance(registry.get("registry_name"), str) or not registry.get("registry_name"):
        errors.append("registry_name must be a non-empty string")
    skills = registry.get("skills")
    if not isinstance(skills, list) or not skills:
        return errors + ["registry must contain a non-empty skills list"]

    seen: set[str] = set()
    for index, skill in enumerate(skills):
        prefix = f"skills[{index}]"
        if not isinstance(skill, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue
        skill_id = skill.get("id")
        if not isinstance(skill_id, str) or not ID_RE.fullmatch(skill_id):
            errors.append(f"{prefix}: invalid skill id {skill_id!r}")
            continue
        if skill_id in seen:
            errors.append(f"duplicate skill id: {skill_id}")
        seen.add(skill_id)

        if skill.get("kind") not in {"native", "port", "extended", "tracked"}:
            errors.append(f"{skill_id}: kind must be native, port, extended, or tracked")
        if skill.get("status") not in {"current", "update-available", "review-required", "broken", "archived", "tracked-only"}:
            errors.append(f"{skill_id}: invalid status {skill.get('status')!r}")

        try:
            source_rel = safe_relative_path(str(skill.get("path", "")), field=f"{skill_id}.path")
        except RegistryError as exc:
            errors.append(str(exc))
            continue
        skill_dir = root.joinpath(*source_rel.parts)
        if not skill_dir.is_dir():
            errors.append(f"{skill_id}: missing Skill directory {source_rel.as_posix()}")
            continue

        for required in REQUIRED_SKILL_FILES:
            if not (skill_dir / required).is_file():
                errors.append(f"{skill_id}: missing required file {required}")

        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            frontmatter = parse_skill_frontmatter(skill_md)
            if frontmatter.get("name") != skill_id:
                errors.append(
                    f"{skill_id}: SKILL.md frontmatter name {frontmatter.get('name')!r} must match registry id"
                )
            if not frontmatter.get("description"):
                errors.append(f"{skill_id}: SKILL.md frontmatter requires a description")

        try:
            files = list(iter_skill_files(skill_dir))
        except RegistryError as exc:
            errors.append(f"{skill_id}: {exc}")
            files = []

        package_limit = (skill.get("validation") or {}).get("package_limit_mb", 25)
        if not isinstance(package_limit, int) or package_limit <= 0 or package_limit > 25:
            errors.append(f"{skill_id}: package_limit_mb must be an integer from 1 through 25")
        else:
            total_size = sum(path.stat().st_size for path, _ in files)
            if total_size > package_limit * 1024 * 1024:
                errors.append(f"{skill_id}: uncompressed Skill size exceeds {package_limit} MB")

        targets = skill.get("targets") or {}
        for target in ("chatgpt_web", "codex"):
            target_data = targets.get(target)
            if not isinstance(target_data, dict) or not isinstance(target_data.get("supported"), bool):
                errors.append(f"{skill_id}: targets.{target}.supported must be boolean")

        origin = skill.get("origin") or {}
        if skill.get("kind") in {"port", "extended", "tracked"}:
            repository = origin.get("repository")
            if not isinstance(repository, str) or not REPO_RE.fullmatch(repository):
                errors.append(f"{skill_id}: origin.repository must use owner/name form")
            commit = origin.get("integrated_commit")
            if not isinstance(commit, str) or not SHA_RE.fullmatch(commit):
                errors.append(f"{skill_id}: origin.integrated_commit must be a 40-character lowercase SHA")
            license_data = skill.get("license") or {}
            if license_data.get("redistribution") is True:
                notice_value = license_data.get("notice")
                try:
                    notice_rel = safe_relative_path(str(notice_value or ""), field=f"{skill_id}.license.notice")
                    if not root.joinpath(*notice_rel.parts).is_file():
                        errors.append(f"{skill_id}: missing license notice {notice_rel.as_posix()}")
                except RegistryError as exc:
                    errors.append(str(exc))
                if not (skill_dir / "LICENSE").is_file():
                    errors.append(f"{skill_id}: redistributable port must include LICENSE")

        artifact_value = skill.get("artifact")
        try:
            safe_relative_path(str(artifact_value or ""), field=f"{skill_id}.artifact")
        except RegistryError as exc:
            errors.append(str(exc))

        command = (skill.get("validation") or {}).get("command")
        if not isinstance(command, str) or not command.strip():
            errors.append(f"{skill_id}: validation.command must be a non-empty string")
        else:
            try:
                tokens = shlex.split(command)
            except ValueError as exc:
                errors.append(f"{skill_id}: invalid validation.command: {exc}")
            else:
                for token in tokens[1:]:
                    if token.endswith(".py"):
                        try:
                            command_rel = safe_relative_path(token, field=f"{skill_id}.validation.command")
                        except RegistryError as exc:
                            errors.append(str(exc))
                        else:
                            if not root.joinpath(*command_rel.parts).is_file():
                                errors.append(f"{skill_id}: validation script does not exist: {token}")
                        break

        policy = skill.get("update_policy") or {}
        if policy.get("automatic_merge") is not False:
            errors.append(f"{skill_id}: update_policy.automatic_merge must be false")

    _validate_lock(root, [entry for entry in skills if isinstance(entry, dict)], errors)
    return errors

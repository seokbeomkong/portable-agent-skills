#!/usr/bin/env python3
"""Compare integrated Skill revisions with current GitHub metadata."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from registry_lib import RegistryError, load_json_yaml

API_ROOT = "https://api.github.com"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compare_state(lock_entry: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any]:
    integrated_release = lock_entry.get("integrated_release")
    integrated_commit = lock_entry.get("integrated_commit")
    latest_release = latest.get("release")
    latest_commit = latest.get("commit")
    release_changed = latest_release is not None and latest_release != integrated_release
    commit_changed = latest_commit is not None and latest_commit != integrated_commit
    return {
        "integrated": {"release": integrated_release, "commit": integrated_commit},
        "latest": {"release": latest_release, "commit": latest_commit},
        "changes": {"release": release_changed, "commit": commit_changed},
        "update_available": release_changed or commit_changed,
    }


def _item(skill: dict[str, Any], lock_entry: dict[str, Any], comparison: dict[str, Any]) -> dict[str, Any]:
    skill_id = skill["id"]
    repository = lock_entry["repository"]
    integrated_commit = comparison["integrated"]["commit"]
    latest_commit = comparison["latest"]["commit"]
    compare_url = None
    if integrated_commit and latest_commit and integrated_commit != latest_commit:
        compare_url = f"https://github.com/{repository}/compare/{integrated_commit}...{latest_commit}"
    latest_release = comparison["latest"]["release"]
    release_url = f"https://github.com/{repository}/releases/tag/{latest_release}" if latest_release else None
    return {
        "id": skill_id,
        "display_name": skill.get("display_name", skill_id),
        "repository": repository,
        "ref": lock_entry.get("ref", "main"),
        **comparison,
        "issue_marker": f"<!-- upstream-skill:{skill_id} -->",
        "compare_url": compare_url,
        "release_url": release_url,
    }


def build_report(
    registry: dict[str, Any],
    lock: dict[str, Any],
    states: dict[str, dict[str, Any]],
    *,
    checked_at: str | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": 1,
        "checked_at": checked_at or utc_now(),
        "updates": [],
        "current": [],
        "errors": [],
    }
    lock_entries = lock.get("skills", {})
    for skill in registry.get("skills", []):
        skill_id = skill.get("id")
        if not skill_id or skill_id not in lock_entries:
            continue
        state = states.get(skill_id)
        if not state:
            report["errors"].append({"id": skill_id, "error": "no upstream state returned"})
            continue
        if state.get("error"):
            report["errors"].append({"id": skill_id, "error": str(state["error"])})
            continue
        comparison = compare_state(lock_entries[skill_id], state)
        item = _item(skill, lock_entries[skill_id], comparison)
        report["updates" if comparison["update_available"] else "current"].append(item)
    return report


def _request_json(url: str, token: str | None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "portable-agent-skills-upstream-watch",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise RuntimeError(f"GitHub API returned an unexpected payload for {url}")
    return data


def fetch_latest(lock_entry: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    repository = lock_entry["repository"]
    ref = urllib.parse.quote(str(lock_entry.get("ref", "main")), safe="")
    release: str | None = None
    try:
        release_data = _request_json(f"{API_ROOT}/repos/{repository}/releases/latest", token)
        release = release_data.get("tag_name")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    commit_data = _request_json(f"{API_ROOT}/repos/{repository}/commits/{ref}", token)
    commit = commit_data.get("sha")
    if not isinstance(commit, str) or len(commit) != 40:
        raise RuntimeError(f"GitHub API did not return a full commit SHA for {repository}@{ref}")
    return {"release": release, "commit": commit}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_github_output(path: Path, report: dict[str, Any], report_path: Path) -> None:
    values = {
        "updates": "true" if report["updates"] else "false",
        "update_count": str(len(report["updates"])),
        "error_count": str(len(report["errors"])),
        "report_path": report_path.as_posix(),
    }
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--fixture", type=Path, help="Read latest states from a local JSON fixture")
    parser.add_argument("--output", type=Path, help="Report path; defaults to build/upstream-report.json")
    parser.add_argument("--github-output", type=Path, help="Append GitHub Actions outputs to this file")
    parser.add_argument("--checked-at", help="Override the UTC report timestamp for reproducible tests")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or root / "build" / "upstream-report.json").resolve()
    try:
        registry = load_json_yaml(root / "registry.yaml")
        lock = load_json_yaml(root / "upstream" / "upstream-lock.json")
        if args.fixture:
            states = load_json_yaml(args.fixture.resolve())
        else:
            token = os.environ.get("GITHUB_TOKEN")
            states: dict[str, dict[str, Any]] = {}
            for skill_id, entry in lock.get("skills", {}).items():
                try:
                    states[skill_id] = fetch_latest(entry, token)
                except (urllib.error.URLError, TimeoutError, OSError, RuntimeError) as exc:
                    states[skill_id] = {"error": str(exc)}
        report = build_report(registry, lock, states, checked_at=args.checked_at)
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    _write_json(output, report)
    if args.github_output:
        _write_github_output(args.github_output, report, output)
    print(
        f"Upstream check: {len(report['updates'])} update(s), "
        f"{len(report['current'])} current, {len(report['errors'])} error(s)"
    )
    for update in report["updates"]:
        latest = update["latest"]
        print(f"UPDATE {update['id']}: release={latest['release']} commit={latest['commit']}")
    for error in report["errors"]:
        print(f"ERROR {error['id']}: {error['error']}", file=sys.stderr)
    return 2 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check whether the tracked upstream UI UX Pro Max release/commit changed.

Network access is optional. This script is intended for repository maintenance
or scheduled CI, not normal UI/UX task execution.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request

REPO = "nextlevelbuilder/ui-ux-pro-max-skill"
TRACKED_RELEASE = "v2.14.1"
TRACKED_COMMIT = "abb7f2fd5a083fa1ff55c326a963ff0d95c33f99"


def get_json(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "portable-agent-skills-upstream-check",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("UI_PRO_MAX_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--print-tracked", action="store_true", help="Print tracked values without network access")
    args = p.parse_args()

    tracked = {"repository": REPO, "tracked_release": TRACKED_RELEASE, "tracked_commit": TRACKED_COMMIT}
    if args.print_tracked:
        print(json.dumps(tracked, indent=2) if args.json else f"{TRACKED_RELEASE} {TRACKED_COMMIT}")
        return 0

    try:
        release = get_json(f"https://api.github.com/repos/{REPO}/releases/latest")
        branch = get_json(f"https://api.github.com/repos/{REPO}/commits/main")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        payload = {**tracked, "status": "network-unavailable", "error": str(exc)}
        print(json.dumps(payload, indent=2) if args.json else f"network-unavailable: {exc}")
        return 2

    latest_release = release.get("tag_name")
    latest_commit = branch.get("sha")
    changed = latest_release != TRACKED_RELEASE or latest_commit != TRACKED_COMMIT
    payload = {
        **tracked,
        "latest_release": latest_release,
        "latest_commit": latest_commit,
        "update_available": changed,
        "status": "update-available" if changed else "current",
    }
    print(json.dumps(payload, indent=2) if args.json else payload["status"])
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())

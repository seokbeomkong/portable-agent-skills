#!/usr/bin/env python3
"""Compatibility CLI backed by the full upstream search engine.

New integrations should use ``search.py``. This launcher preserves the v1 JSON
container shapes while translating their content from the canonical catalog.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def _has(args: list[str], *flags: str) -> bool:
    return any(flag in args for flag in flags)


def _option_value(args: list[str], *flags: str) -> str | None:
    for flag in flags:
        if flag in args:
            index = args.index(flag)
            if index + 1 < len(args):
                return args[index + 1]
    return None


def _legacy_design(payload: dict, stack: str | None) -> dict:
    design = payload["design_system"]
    colors = design.get("colors", {})
    typography = design.get("typography", {})
    style = design.get("style", {})
    match = design.get("catalog_match", {})
    result = {
        "project": design.get("project_name"),
        "profile": design.get("category", "General"),
        "match_source": (
            "full-upstream-catalog" if match.get("matched") else "general-fallback"
        ),
        "pattern": (design.get("pattern") or {}).get("name"),
        "style": {
            "id": re.sub(r"[^a-z0-9]+", "-", style.get("name", "").lower()).strip("-"),
            "name": style.get("name"),
            "rules": [value for value in (style.get("keywords"), style.get("effects")) if value],
        },
        "palette": {
            "primary": colors.get("primary"),
            "secondary": colors.get("secondary"),
            "accent": colors.get("accent"),
            "background": colors.get("background"),
            "surface": colors.get("muted"),
            "text": colors.get("foreground"),
        },
        "typography": [
            value for value in (typography.get("heading"), typography.get("body")) if value
        ],
        "spacing": design.get("spacing_scale") or "Use a consistent 4/8-point scale",
        "motion": design.get("motion_snippet") or {},
        "effects": [design.get("key_effects")] if design.get("key_effects") else [],
        "anti_patterns": [
            value.strip()
            for value in str(design.get("anti_patterns", "")).split("+")
            if value.strip()
        ],
        "stack": stack,
        "stack_guidelines": [],
        "accessibility": [
            "Use semantic controls and accessible names",
            "Keep visible keyboard focus and sufficient contrast",
            "Do not rely on color alone",
            "Respect reduced motion and practical touch targets",
        ],
        "responsive_checks": ["375px", "768px", "1024px", "1440px"],
    }
    persistence = payload.get("persistence") or {}
    if persistence.get("master_file"):
        result["persisted_master"] = persistence["master_file"]
    return result


def _legacy_stack(payload: dict) -> dict:
    guidelines = []
    for row in payload.get("results", []):
        dont = row.get("Don't")
        parts = [
            f"{row.get('Category')}: {row.get('Guideline')}",
            row.get("Description"),
            f"Do: {row.get('Do')}" if row.get("Do") else "",
            f"Don't: {dont}" if dont else "",
        ]
        guidelines.append(" — ".join(part for part in parts if part))
    return {"stack": payload.get("stack"), "guidelines": guidelines}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    args = ["--project-name" if arg == "--project" else arg for arg in args]

    # v1 used `motion`; the canonical upstream domain is named `gsap`.
    for flag in ("--domain", "-d"):
        if flag in args:
            index = args.index(flag)
            if index + 1 < len(args) and args[index + 1] == "motion":
                args[index + 1] = "gsap"

    is_domain = _has(args, "--domain", "-d")
    is_stack = _has(args, "--stack", "-s")
    is_design = _has(args, "--design-system", "-ds")
    as_json = "--json" in args
    if not is_domain and not is_stack and not is_design:
        args.append("--design-system")
        is_design = True
    if not args or args[0].startswith("-"):
        args.insert(0, "performance accessibility components")

    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("search.py")), *args],
        check=False,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode or not as_json:
        sys.stdout.write(result.stdout)
        return result.returncode

    payload = json.loads(result.stdout)
    if is_design:
        legacy = _legacy_design(payload, _option_value(args, "--stack", "-s"))
    elif is_stack:
        legacy = _legacy_stack(payload)
    elif is_domain:
        legacy = payload.get("results", [])
    else:  # pragma: no cover - modes above are exhaustive after normalization.
        legacy = payload
    print(json.dumps(legacy, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

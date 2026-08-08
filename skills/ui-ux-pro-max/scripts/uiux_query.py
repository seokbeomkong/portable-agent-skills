#!/usr/bin/env python3
"""Portable UI/UX Pro Max query helper.

A dependency-free fallback for ChatGPT/Codex Skill environments. It intentionally
uses a compact curated catalog rather than claiming parity with the upstream
project's full database.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "references" / "portable-catalog.json"


def load_catalog() -> Dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9+#./ -]+", " ", text.lower()).strip()


def tokens(text: str) -> List[str]:
    return [t for t in re.split(r"\s+", normalize(text)) if t]


def score_keywords(query: str, keywords: Iterable[str], extra_text: str = "") -> float:
    q = normalize(query)
    qtokens = set(tokens(q))
    score = 0.0
    for raw in keywords:
        kw = normalize(raw)
        if not kw:
            continue
        if kw in q:
            score += 5.0 + min(len(kw) / 10.0, 2.0)
        parts = set(tokens(kw))
        score += 1.25 * len(parts & qtokens)
    if extra_text:
        extra = set(tokens(extra_text))
        score += 0.2 * len(extra & qtokens)
    return score


def ranked_profiles(catalog: Dict[str, Any], query: str) -> List[Tuple[float, Dict[str, Any]]]:
    out: List[Tuple[float, Dict[str, Any]]] = []
    for profile in catalog["profiles"]:
        extra = " ".join([
            profile.get("id", ""),
            profile.get("pattern", ""),
            " ".join(profile.get("styles", [])),
            " ".join(profile.get("avoid", [])),
        ])
        s = score_keywords(query, profile.get("keywords", []), extra)
        out.append((s, profile))
    out.sort(key=lambda item: (-item[0], item[1]["id"]))
    return out


def ranked_styles(catalog: Dict[str, Any], query: str) -> List[Tuple[float, str, Dict[str, Any]]]:
    out: List[Tuple[float, str, Dict[str, Any]]] = []
    for sid, style in catalog["styles"].items():
        extra = style.get("name", "") + " " + " ".join(style.get("rules", []))
        s = score_keywords(query, style.get("keywords", []), extra)
        out.append((s, sid, style))
    out.sort(key=lambda item: (-item[0], item[1]))
    return out


def density_scale(level: int | None) -> str:
    if level is None:
        return "balanced: 8px base; common section gaps 48-80px"
    if level <= 3:
        return "spacious: 8px base; component gaps 16-32px; section gaps 64-112px"
    if level >= 8:
        return "dense: 4/8px base; component gaps 8-16px; section gaps 24-48px"
    return "balanced: 8px base; component gaps 12-24px; section gaps 48-80px"


def motion_guidance(level: int | None) -> List[str]:
    if level is None:
        return ["150-300ms interaction transitions", "animate transform/opacity first", "respect reduced motion"]
    if level <= 3:
        return ["100-180ms state transitions", "little or no entrance motion", "disable nonessential motion under reduced-motion"]
    if level >= 8:
        return ["layered but purposeful choreography", "prefer transform/opacity and bounded scroll effects", "provide reduced/static alternative"]
    return ["150-300ms micro-interactions", "short stagger only for grouped content", "respect reduced motion"]


def style_for_variance(profile: Dict[str, Any], variance: int | None) -> str:
    styles = profile.get("styles", [])
    if not styles:
        return "swiss-minimal"
    if variance is None or variance <= 6:
        return styles[0]
    adventurous = ["brutalist", "cyberpunk", "dimensional", "bento", "editorial", "exaggerated-minimal"]
    for sid in styles:
        if sid in adventurous:
            return sid
    return styles[-1]


def design_system(catalog: Dict[str, Any], query: str, project: str | None, stack: str | None,
                  variance: int | None, motion: int | None, density: int | None) -> Dict[str, Any]:
    ranked = ranked_profiles(catalog, query)
    score, profile = ranked[0]
    if score <= 0:
        # Stable generic fallback instead of pretending to have a database match.
        profile = next(p for p in catalog["profiles"] if p["id"] == "saas")
        match = "fallback"
    else:
        match = "catalog"
    sid = style_for_variance(profile, variance)
    style = catalog["styles"].get(sid, catalog["styles"]["swiss-minimal"])
    stack_rules = catalog["stacks"].get(stack or "", [])
    return {
        "project": project or "Untitled",
        "query": query,
        "match_source": match,
        "profile": profile["id"],
        "pattern": profile["pattern"],
        "style": {"id": sid, "name": style["name"], "rules": style["rules"]},
        "palette": profile["palette"],
        "typography": profile["typography"],
        "spacing": density_scale(density),
        "motion": motion_guidance(motion),
        "effects": profile.get("effects", []),
        "anti_patterns": profile.get("avoid", []),
        "stack": stack,
        "stack_guidelines": stack_rules,
        "accessibility": [
            "Use semantic elements and accessible names",
            "Keep visible keyboard focus",
            "Do not rely on color alone",
            "Check text and essential UI contrast",
            "Keep primary touch targets around 44x44 where practical",
            "Respect reduced motion",
        ],
        "responsive_checks": ["375px", "768px", "1024px", "1440px", "content edge cases"],
    }


def render_markdown(ds: Dict[str, Any]) -> str:
    p = ds["palette"]
    lines = [
        f"# {ds['project']} - Recommended Design System",
        "",
        f"**Match:** {ds['profile']} ({ds['match_source']})",
        f"**Pattern:** {ds['pattern']}",
        f"**Style:** {ds['style']['name']} (`{ds['style']['id']}`)",
        "",
        "## Color tokens",
        "",
        f"- Primary: `{p['primary']}`",
        f"- Secondary: `{p['secondary']}`",
        f"- Accent: `{p['accent']}`",
        f"- Background: `{p['background']}`",
        f"- Surface: `{p['surface']}`",
        f"- Text: `{p['text']}`",
        "",
        "## Typography",
        "",
        f"- Primary: {ds['typography'][0]}",
        f"- Secondary: {ds['typography'][1] if len(ds['typography']) > 1 else ds['typography'][0]}",
        "",
        "## Spacing / density",
        "",
        f"- {ds['spacing']}",
        "",
        "## Style rules",
        "",
    ]
    lines.extend(f"- {x}" for x in ds["style"]["rules"])
    lines += ["", "## Motion", ""]
    lines.extend(f"- {x}" for x in ds["motion"])
    if ds.get("effects"):
        lines += ["", "## Key effects", ""]
        lines.extend(f"- {x}" for x in ds["effects"])
    lines += ["", "## Accessibility", ""]
    lines.extend(f"- {x}" for x in ds["accessibility"])
    lines += ["", "## Avoid", ""]
    lines.extend(f"- {x}" for x in ds["anti_patterns"])
    if ds.get("stack"):
        lines += ["", f"## Stack: {ds['stack']}", ""]
        if ds["stack_guidelines"]:
            lines.extend(f"- {x}" for x in ds["stack_guidelines"])
        else:
            lines.append("- No bundled stack-specific match; use stack-neutral accessibility and design-token guidance.")
    lines += ["", "## Responsive verification", ""]
    lines.extend(f"- {x}" for x in ds["responsive_checks"])
    return "\n".join(lines) + "\n"


def persist(ds: Dict[str, Any], output_dir: Path, page: str | None, force: bool) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", ds["project"].lower()).strip("-") or "project"
    root = output_dir / "design-system" / slug
    root.mkdir(parents=True, exist_ok=True)
    master = root / "MASTER.md"
    if not master.exists() or force:
        master.write_text(render_markdown(ds), encoding="utf-8")
    if page:
        pages = root / "pages"
        pages.mkdir(parents=True, exist_ok=True)
        page_slug = re.sub(r"[^a-z0-9]+", "-", page.lower()).strip("-") or "page"
        page_path = pages / f"{page_slug}.md"
        if not page_path.exists() or force:
            page_path.write_text(
                f"# {page} overrides\n\nUse `{master.name}` as the base. Record only deliberate page-specific deviations here.\n",
                encoding="utf-8",
            )
    return master


def domain_results(catalog: Dict[str, Any], query: str, domain: str, limit: int) -> Any:
    if domain in {"product", "color", "typography", "landing", "motion"}:
        ranked = ranked_profiles(catalog, query)[:limit]
        results = []
        for score, p in ranked:
            item: Dict[str, Any] = {"id": p["id"], "score": round(score, 2)}
            if domain == "product":
                item.update({"pattern": p["pattern"], "styles": p["styles"], "avoid": p["avoid"]})
            elif domain == "color":
                item["palette"] = p["palette"]
            elif domain == "typography":
                item["typography"] = p["typography"]
            elif domain == "landing":
                item["pattern"] = p["pattern"]
            elif domain == "motion":
                item["effects"] = p.get("effects", [])
            results.append(item)
        return results
    if domain == "style":
        return [
            {"id": sid, "name": style["name"], "score": round(score, 2), "rules": style["rules"]}
            for score, sid, style in ranked_styles(catalog, query)[:limit]
        ]
    if domain in {"ux", "accessibility"}:
        return {
            "reference": "references/quick-reference.md",
            "priority": ["accessibility", "interaction", "responsive layout", "performance", "typography/color", "motion", "forms", "navigation", "charts"],
        }
    if domain in {"chart", "icons", "google-fonts", "gsap", "react", "web"}:
        return {
            "reference": "references/quick-reference.md",
            "note": f"The compact portable catalog does not mirror the upstream `{domain}` database. Use the bundled principles and, when available, the official upstream engine for deeper lookup."
        }
    raise ValueError(f"unsupported domain: {domain}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portable UI/UX Pro Max query helper")
    p.add_argument("query", nargs="?", default="", help="Product, industry, style, or UX query")
    p.add_argument("--design-system", action="store_true", help="Generate a complete compact design system")
    p.add_argument("-p", "--project", help="Project name")
    p.add_argument("--domain", choices=["product","style","color","typography","landing","motion","ux","accessibility","chart","icons","google-fonts","gsap","react","web"])
    p.add_argument("--stack", help="Return/use stack-specific guidance")
    p.add_argument("-n", type=int, default=3, help="Maximum domain results")
    p.add_argument("--variance", type=int, choices=range(1, 11), metavar="1-10")
    p.add_argument("--motion", type=int, choices=range(1, 11), metavar="1-10")
    p.add_argument("--density", type=int, choices=range(1, 11), metavar="1-10")
    p.add_argument("--json", action="store_true", help="Emit JSON")
    p.add_argument("--persist", action="store_true", help="Write design-system/<slug>/MASTER.md")
    p.add_argument("--output-dir", default=".", help="Project root for --persist")
    p.add_argument("--page", help="Optional page override stub")
    p.add_argument("--force", action="store_true", help="Overwrite persisted files")
    return p


def main() -> int:
    args = parser().parse_args()
    catalog = load_catalog()

    if args.stack and not args.design_system and not args.domain:
        rules = catalog["stacks"].get(args.stack)
        if rules is None:
            print(f"No bundled stack match for: {args.stack}", file=sys.stderr)
            return 2
        payload = {"stack": args.stack, "guidelines": rules}
        print(json.dumps(payload, indent=2) if args.json else "\n".join(f"- {x}" for x in rules))
        return 0

    if args.domain:
        try:
            payload = domain_results(catalog, args.query, args.domain, max(1, args.n))
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    ds = design_system(catalog, args.query, args.project, args.stack, args.variance, args.motion, args.density)
    if args.persist:
        master = persist(ds, Path(args.output_dir).resolve(), args.page, args.force)
        ds["persisted_master"] = str(master)
    if args.json:
        print(json.dumps(ds, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(ds), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

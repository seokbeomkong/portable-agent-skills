# Changelog

## 2.0.0 - 2026-08-08

- Bundle the complete upstream v2.14.1 BM25 engine and all domain, reasoning, font, motion, and 22 stack CSV catalogs.
- Make the canonical `search.py` and `design_system.py` the primary ChatGPT/Codex tool path.
- Add common Korean-to-English search aliases without replacing the upstream data.
- Report direct catalog coverage so generic design-system fallbacks cannot masquerade as database matches.
- Retain `uiux_query.py` only as a backward-compatible launcher for the full engine.
- Run upstream's 36 stdlib tests and data-schema validator as release gates.

## 1.0.0 - 2026-08-08

Tracked upstream: `nextlevelbuilder/ui-ux-pro-max-skill` release `v2.14.1`, commit `abb7f2fd5a083fa1ff55c326a963ff0d95c33f99`.

- Added ChatGPT Web + Codex shared workflow.
- Removed hard dependency on Claude-specific plugin-root paths.
- Added the initial compact offline design catalog and deterministic query tool.
- Added Codex-enhanced repository detection, implementation, and verification rules.
- Added explicit no-tool fallback for ChatGPT Web.
- Added upstream provenance, license notice, compatibility metadata, and review-required update policy.

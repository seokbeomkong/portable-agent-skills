# OpenAI Full-Parity Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the full upstream Humanize Korean and UI UX Pro Max cores in portable ChatGPT/Codex skills and distribute them as individual archives plus one OpenAI plugin.

**Architecture:** Each skill has one concise OpenAI orchestration layer and vendored, commit-pinned canonical scripts/references. Hosts select shared, tool-assisted, or Codex-enhanced behavior without runtime downloads.

**Tech Stack:** Python 3.12 standard library, Markdown/YAML/JSON, GitHub Actions, OpenAI Agent Skills and plugin manifests.

## Global Constraints

- Do not execute or download upstream code at skill runtime.
- Keep exact upstream attribution and license notices.
- Write behavior tests before modifying runtime code or skill instructions.
- Complete and verify one skill before changing the next.
- Keep `SKILL.md` under 500 lines and load detailed references progressively.

---

### Task 1: Humanize parity tests

**Files:**
- Create: `tests/test_humanize_port.py`
- Test: `skills/humanize-korean/scripts/*.py`

**Interfaces:**
- Consumes: packaged Humanize helper CLIs.
- Produces: failing tests for routing, protected relations, chunk identity, and upstream resource completeness.

- [ ] Write tests for final-artifact Heavy routing, value swaps, inline/path/structure protection, missing/stale chunks, and required upstream files.
- [ ] Run `python -m unittest tests.test_humanize_port -v` and confirm failures describe the current simplified port.
- [ ] Record the failing behaviors in test names and assertions.

### Task 2: Humanize full core and OpenAI adapter

**Files:**
- Modify: `skills/humanize-korean/SKILL.md`
- Modify: `skills/humanize-korean/agents/openai.yaml`
- Replace: `skills/humanize-korean/scripts/`
- Replace: `skills/humanize-korean/references/`
- Modify: `skills/humanize-korean/skill.meta.yaml`
- Modify: `registry.yaml`
- Modify: `upstream/upstream-lock.json`

**Interfaces:**
- Consumes: upstream `53e24e8f92cf344efcb812103f7c2b203e7efffc` canonical Humanize scripts/references.
- Produces: portable light/standard/heavy workflow with explicit helper commands and deterministic gates.

- [ ] Import allowlisted upstream references, scripts, and golden-check support.
- [ ] Add a portable router whose explicit-purpose precedence matches `SKILL.md`.
- [ ] Add strict manifest-bound chunking and reassembly.
- [ ] Add fidelity checks for ordered subject/value relationships and structural literals.
- [ ] Run the Humanize test file until green.
- [ ] Run upstream-derived metrics, gate, chunking, and golden tests in the packaged layout.
- [ ] Run Humanize `check_port.py` and registry validation.

### Task 3: UI UX parity tests

**Files:**
- Create: `tests/test_uiux_port.py`
- Test: `skills/ui-ux-pro-max/scripts/` and `skills/ui-ux-pro-max/data/`

**Interfaces:**
- Consumes: packaged UI UX CLI and full data set.
- Produces: failing tests for full-domain presence, Korean query mapping, no-match behavior, stack lookup, and persistence.

- [ ] Write tests that require the complete upstream domain files and canonical search engine.
- [ ] Write Korean healthcare, no-match, stack, slider, and persistence cases.
- [ ] Run `python -m unittest tests.test_uiux_port -v` and confirm failures describe the compact current port.

### Task 4: UI UX full core and OpenAI adapter

**Files:**
- Modify: `skills/ui-ux-pro-max/SKILL.md`
- Modify: `skills/ui-ux-pro-max/agents/openai.yaml`
- Replace: `skills/ui-ux-pro-max/scripts/`
- Create: `skills/ui-ux-pro-max/data/`
- Modify: `skills/ui-ux-pro-max/references/`
- Modify: `skills/ui-ux-pro-max/skill.meta.yaml`

**Interfaces:**
- Consumes: upstream `abb7f2fd5a083fa1ff55c326a963ff0d95c33f99` canonical `src/ui-ux-pro-max` core.
- Produces: full search/design-system engine with portable paths and Korean query adapter.

- [ ] Import canonical upstream scripts, data, and upstream tests.
- [ ] Add Unicode/Korean keyword normalization without changing the upstream ranking core.
- [ ] Bind all paths to the skill directory and explicit output root.
- [ ] Rewrite `SKILL.md` as a concise shared/tool-assisted/Codex-enhanced workflow.
- [ ] Run the UI UX port tests and upstream core/design-system tests until green.
- [ ] Run UI UX `check_port.py` and registry validation.

### Task 5: Plugin and release completeness

**Files:**
- Create: `.codex-plugin/plugin.json`
- Modify: `scripts/package_skills.py`
- Modify: `.github/workflows/release.yml`
- Modify: `tests/test_repository_structure.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: all redistributable registry skills.
- Produces: individual skill ZIPs and one plugin ZIP containing every registered skill.

- [ ] Write failing tests for the plugin manifest and release asset completeness.
- [ ] Add the plugin manifest and plugin packaging path.
- [ ] Make release CI compare registry entries with produced assets.
- [ ] Run repository and package tests until green.

### Task 6: Review, verification, and publication

**Files:**
- Modify only files required by validated review findings.

**Interfaces:**
- Consumes: complete feature branch and implementation plan.
- Produces: reviewed commit, GitHub branch, PR, and merged/released update when CI permits.

- [ ] Run the complete unit, registry, catalog, per-skill, packaging, and plugin validation suite.
- [ ] Forward-test each skill with fresh-context agents using realistic prompts.
- [ ] Request independent code review and fix all Critical/Important findings.
- [ ] Re-run the complete verification suite after fixes.
- [ ] Commit, push, open a PR, wait for CI, and merge when green.
- [ ] Publish a registry tag whose release includes every individual skill and the plugin archive.

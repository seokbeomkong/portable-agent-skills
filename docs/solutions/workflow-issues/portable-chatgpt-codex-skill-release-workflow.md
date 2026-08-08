---
title: "Preserving Upstream Skill Parity in ChatGPT and Codex Releases"
date: 2026-08-08
category: workflow-issues
module: portable-agent-skills
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "Porting provider-specific Skills to ChatGPT and Codex"
  - "A Skill bundles scripts, datasets, references, or long-document workflows"
  - "Publishing standalone Skill archives and a combined Codex plugin"
tags:
  - skill-portability
  - upstream-parity
  - plugin-packaging
  - deterministic-builds
  - compatibility
  - regression-testing
---

# Preserving Upstream Skill Parity in ChatGPT and Codex Releases

## Context

A Skill can appear portable because its `SKILL.md` loads while still losing most of the upstream capability. The first ports of Humanize Korean and UI UX Pro Max replaced provider-specific behavior with smaller shared implementations. That reduced installation friction, but also removed the complete metric and fidelity pipeline from Humanize Korean and most of the searchable UI/UX catalog.

The release workflow also produced standalone Skill archives only. Codex had no root plugin manifest, release assets could be incomplete, and future registry entries were not guaranteed to enter a combined plugin without manual work.

The review cycle found three subtler boundary defects after the main parity work was green:

- Quote preservation grouped matches by delimiter type rather than document position, so mixed-style quotations could be reordered without detection.
- A launcher labeled backward-compatible forwarded the new UI/UX JSON object directly, breaking consumers that expected legacy array or wrapper shapes.
- Registry paths were safe relative paths but not canonical roots, allowing an ancestor/descendant pair to create duplicate ZIP members.

## Guidance

### Preserve the complete runtime and adapt at thin boundaries

Vendor the pinned upstream scripts, data, references, and behavioral tests when licensing permits. Put provider adaptation in `SKILL.md`, small path changes, or compatibility wrappers. Do not replace a mature runtime with a compact hand-maintained substitute merely to make the directory smaller.

Tests should prove that required upstream assets exist, the substantive data volume is present, and representative upstream behavior still executes. Keep the upstream repository, release, and commit in metadata and notices.

### Resolve bundled assets from the installed Skill

The Skill installation directory and the user's current working directory are different concepts. Scripts locate bundled data relative to `__file__`; the current working directory is only for user input and generated artifacts.

```python
skill_root = Path(__file__).resolve().parents[1]
data_dir = skill_root / "data"
workspace = Path.cwd()
```

Run path tests from an unrelated temporary directory. This catches code that works only from the source repository.

### Translate provider orchestration into semantic passes

Provider-specific subagent names should become portable phases such as diagnose, targeted rewrite, finalize, and verify. ChatGPT can perform them sequentially in one conversation; Codex can add deterministic scripts, repository inspection, and tests. This preserves separation of concerns without requiring another provider's agent API.

### Fail closed at fidelity and chunk boundaries

Long-document workflows need a structured manifest, source identity, explicit passthrough regions, required rewritten outputs, and ordered reassembly. Missing or stale results are errors, not invitations to silently substitute source text.

Protected elements must be compared in document order. Counts or grouped lists miss swaps:

```python
positioned = [(match.start(), match.group()) for match in matches]
protected = [value for _, value in sorted(positioned)]
```

Regression cases should include swapped numeric claims, mixed quotation styles, headings, inline code, paths, URLs, units, missing chunks, stale manifests, and Windows console encoding.

### Keep one canonical engine and translate legacy contracts at the edge

UI UX Pro Max uses the complete upstream search and design-system engine internally. Korean aliases normalize queries before BM25 search. A no-match result remains explicit; generic recommendations are labeled as fallbacks.

If an older command remains, test its external response containers independently. Translate canonical results into the legacy domain list, stack wrapper, and design-system object at that boundary instead of forking the search engine.

### Drive combined plugin packaging from the registry

The plugin manifest discovers the shared Skill directory while the packager enumerates redistributable entries from the registry. A future Skill therefore enters the next plugin build without a hand-written manifest entry.

Enforce these archive invariants:

- Every registered root has the canonical identity-derived location.
- Registered roots cannot overlap.
- Every archive member name is unique before it is written.
- Individual Skill ZIPs have one top-level Skill directory.
- The plugin ZIP has one plugin root, a valid manifest, and every redistributable registry Skill.
- Tagged releases embed the tag-derived semantic version and publish all standalone and plugin assets.

## Why This Matters

Complete runtime assets preserve actual capability rather than surface compatibility. Installed-root path resolution makes the same package work from ChatGPT, Codex, and arbitrary projects. Deterministic fidelity gates protect user claims and document structure. Compatibility translation prevents avoidable downstream breakage. Canonical, duplicate-free packaging makes the release match what the registry promises and lets future additions scale safely.

## When to Apply

- A provider-specific Skill is being adapted for another agent host.
- The Skill depends on scripts, datasets, templates, or references.
- Long content is split, processed, and reassembled.
- A CLI already has JSON consumers.
- Multiple Skills ship through one plugin or release.
- A registry or manifest claims to be the packaging source of truth.

## Examples

Insufficient portability:

```python
data_dir = Path.cwd() / "data"
```

Installed-root portability:

```python
data_dir = Path(__file__).resolve().parents[1] / "data"
```

Insufficient quote preservation:

```python
Counter(source_quotes) == Counter(output_quotes)
```

Order-sensitive preservation:

```python
source_quotes == output_quotes
```

The second comparison only works when extraction itself follows document position across every delimiter style.

## Related

- [OpenAI full-parity Skills design](../../superpowers/specs/2026-08-08-openai-full-parity-skills-design.md)
- [Portable Agent Skills registry design](../../superpowers/specs/2026-08-08-portable-agent-skills-registry-design.md)
- [Adding a Skill](../../adding-a-skill.md)
- [UI UX Pro Max issue 360](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/360)
- [UI UX Pro Max issue 362](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/362)

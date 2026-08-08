# OpenAI Full-Parity Skills Design

## Goal

Ship `humanize-korean` and `ui-ux-pro-max` as one portable package that preserves each upstream project's functional core while using the strongest workflow available in ChatGPT and Codex.

## Principles

- Vendor reviewed, commit-pinned upstream code and data; never download code at skill runtime.
- Keep one shared `SKILL.md` workflow per skill and select capabilities at runtime.
- Preserve upstream functionality, not provider-specific command syntax or unsafe host overrides.
- Use progressive disclosure: orchestration in `SKILL.md`, detailed rules in `references/`, deterministic behavior in `scripts/`.
- Make degraded modes explicit. A host without script execution must not claim that deterministic lookup or verification ran.

## Runtime modes

### Shared mode

Available to ChatGPT and Codex. Read bundled references, follow the output contract, preserve fidelity and provenance, and report unavailable verification honestly.

### Tool-assisted mode

Available when Python can execute bundled scripts. Resolve scripts relative to the selected skill directory, never the user's current working directory.

### Codex-enhanced mode

Adds repository inspection, file-safe output paths, implementation, tests, browser verification, and deterministic evidence reporting.

## Humanize Korean

Replace the simplified downstream helpers with the upstream v2.3 full core:

- complete taxonomy, quick rules, playbook, metrics, and baselines;
- light/standard/heavy route selection;
- input preparation, deterministic gates, safe chunking, strict reassembly, and upstream golden checks;
- explicit CLI contracts for every helper invoked by the skill.

Keep the downstream purpose-aware policy as an override: final reports, applications, presentations, academic work, and other consequential deliverables default to Heavy even when the prompt contains `정리해줘`.

Reassembly must bind outputs to one source manifest, reject missing or stale rewritten chunks, and preserve the original exactly when unchanged chunks are explicitly passthrough.

## UI UX Pro Max

Replace the compact-only engine with the upstream v2.14.1 canonical `src/ui-ux-pro-max` scripts and complete data set. Keep the compact reference only as a no-execution fallback.

The OpenAI adapter must:

- resolve bundled scripts and data without `CLAUDE_PLUGIN_ROOT`;
- preserve every upstream search domain, stack, design-system option, persistence mode, slider, and no-match contract;
- translate or map Korean design terms to English search keywords before lookup;
- return an explicit no-match result rather than zero-score recommendations;
- detect the repository stack before applying stack-specific implementation guidance.

## Packaging

Add a root `.codex-plugin/plugin.json` whose `skills` field points to `./skills/`. Continue producing one ZIP per skill and add one full plugin ZIP. Release validation must assert that every redistributable registry entry has an individual asset and is included in the plugin.

Repository tests and changelogs stay outside runtime context where possible. License and third-party notices remain bundled when redistribution requires them.

## Upstream maintenance

`registry.yaml` and `upstream/upstream-lock.json` record exact upstream commits. Update preparation imports allowlisted canonical paths, produces a review diff, runs upstream-derived tests, and never auto-merges.

## Verification

### Humanize

- purpose-aware routing cases;
- numeric subject/value swaps rejected;
- inline code, paths, headings, numbering, citations, and quotations preserved;
- missing/stale chunks rejected;
- upstream golden fixtures and metrics tests pass.

### UI UX

- all upstream data files and domains are present;
- upstream core and design-system tests pass in the packaged layout;
- Korean healthcare query reaches healthcare rather than SaaS fallback;
- zero-score queries return no match;
- persistence writes only under the explicit output root.

### Distribution

- registry, catalog, package reproducibility, plugin manifest, individual ZIPs, and full plugin ZIP pass validation on Windows and Linux CI.

## Success criteria

Both skills install from the repository, individual release archives, or the shared plugin; ChatGPT receives a truthful reference workflow; Codex receives the full upstream engines and repository-enhanced workflow; no reviewed upstream capability is lost without an explicit documented exception.

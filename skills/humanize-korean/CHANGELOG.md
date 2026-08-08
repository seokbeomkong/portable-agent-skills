# Changelog

## 3.0.0 - 2026-08-08

- Bundle the complete upstream v2.3 taxonomy, scholarship, baselines, metrics v1/v2, route shim, chunker, reassembler, and four-axis gate.
- Translate Claude-only subagent phases into provider-neutral, in-session diagnosis, rewrite, and finalizer passes for ChatGPT and Codex.
- Resolve every helper from the installed Skill root while keeping run artifacts in the user's writable workspace.
- Add ordered numeric-claim, inline-code, path, heading, and list-structure fidelity checks.
- Refuse missing rewritten chunks instead of silently substituting originals.
- Force UTF-8 CLI output so the upstream chunk workflow works on Windows consoles.

## 2.0.0 - 2026-08-08

- Rebuild `humanize-korean` as a shared ChatGPT Web + Codex extended port.
- Route summaries, summary articles, and reference content to Fast by default.
- Route work documents, self-introductions, resumes, PPTs, reports, proposals, presentations, assignments, papers, and official submissions to Heavy by default.
- Keep Standard as an internal ambiguity path rather than a user-facing mode.
- Add the full 71-pattern diagnosis index and a 15-item Heavy fidelity finalizer.
- Add deterministic protected-output verification, structural checks, and lossless long-document chunk/reassembly helpers.
- Preserve upstream attribution and prohibit AI-detector bypass guarantees.

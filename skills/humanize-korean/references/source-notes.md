# Source and adaptation notes

- Upstream: `epoko77-ai/im-not-ai`
- Integrated snapshot: `53e24e8f92cf344efcb812103f7c2b203e7efffc` (2026-07-22)
- Upstream release line reviewed: v2.3.0
- License: MIT, Copyright (c) 2026 epoko77-ai
- Classification: independent ChatGPT Web + Codex portable port/extension, not an upstream release.

## Adaptation
- Vendor the complete upstream v2.3 runtime core: taxonomy, generated diagnosis index, quick rules, rewriting playbook, scholarship, baselines, metrics v1/v2, monolith input shim, chunk reassembler, change-rate gate, and four-axis gate.
- Preserve the upstream A–J taxonomy, light-path philosophy, 30% warning / 50% abort guard, meaning preservation, prompt-injection defense, diagnosis/finalize separation, and deterministic validation.
- Change routing to user-centered output-purpose policy: summaries/articles/reference content default Fast; work documents, self-introductions, resumes, PPTs, reports, proposals, presentations, assignments, papers, and official submissions default Heavy.
- Keep Standard internal only for ambiguous cases.
- Translate Claude-specific Agent/model/tool contracts into portable in-session passes; do not delete the underlying diagnosis, rewrite, or finalizer capability.
- Add an OpenAI-side fidelity gate for ordered numeric claims, inline code, file paths, headings, and list structure.
- Change package-relative paths and CLI encoding only where required for Codex/ChatGPT installation and Windows execution.
- Materialize all references; no repository-external symlinks.
- Do not claim AI-detector evasion.

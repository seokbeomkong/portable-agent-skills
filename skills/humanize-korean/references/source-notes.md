# Source and adaptation notes

- Upstream: `epoko77-ai/im-not-ai`
- Integrated snapshot: `53e24e8f92cf344efcb812103f7c2b203e7efffc` (2026-07-22)
- Upstream release line reviewed: v2.3.0
- License: MIT, Copyright (c) 2026 epoko77-ai
- Classification: independent ChatGPT Web + Codex portable port/extension, not an upstream release.

## Adaptation
- Preserve the upstream A–J taxonomy, Fast-path philosophy, 30% warning / 50% abort guard, meaning preservation, prompt-injection defense, diagnosis/finalize separation, and deterministic validation idea.
- Change routing to user-centered output-purpose policy: summaries/articles/reference content default Fast; work documents, self-introductions, resumes, PPTs, reports, proposals, presentations, assignments, papers, and official submissions default Heavy.
- Keep Standard internal only for ambiguous cases.
- Replace Claude-specific Agent/model/tool contracts with portable Skill instructions and stdlib scripts.
- Materialize all references; no repository-external symlinks.
- Do not claim AI-detector evasion.

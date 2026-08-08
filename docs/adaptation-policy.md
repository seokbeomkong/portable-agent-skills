# Adaptation Policy

Ports preserve the upstream concept while replacing provider-specific assumptions with Agent Skills-compatible behavior.

## Required review

1. Identify the upstream entrypoint, scripts, data, templates, and tool dependencies.
2. Remove or conditionally route provider-specific paths and commands.
3. Define a useful ChatGPT Web workflow that does not depend on a local repository.
4. Add Codex enhancements only when repository or terminal access materially improves the task.
5. Keep `SKILL.md` compact and move detailed rules into references.
6. Validate scripts directly and package a single Skill root.
7. Record every material adaptation in the per-Skill changelog and notices.

## Classification

- `native`: authored in this registry without an external Skill source.
- `port`: adapted to OpenAI-compatible behavior while preserving the upstream purpose.
- `extended`: a port with material new capabilities beyond compatibility work.
- `tracked`: listed for discovery, but not redistributed because of licensing or structural constraints.

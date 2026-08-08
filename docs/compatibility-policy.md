# Compatibility Policy

## Target levels

- **Native** — The Skill performs its core workflow on the target without requiring another product's tool names or filesystem conventions.
- **Enhanced** — The shared core works, and the target adds meaningful capabilities such as repository editing, terminal execution, or tests.
- **Partial** — A useful subset works, but material functionality is unavailable.
- **Unsupported** — The Skill cannot perform a meaningful workflow on the target.

A Skill is presented as ChatGPT Web + Codex compatible only when ChatGPT Web is at least Partial and Codex is at least Native. The preferred registry standard is ChatGPT Web Native plus Codex Enhanced.

## Portability rules

- Do not require Claude-specific variables such as `CLAUDE_PLUGIN_ROOT` in the shared path.
- Keep terminal and repository operations conditional.
- Provide reference-driven fallback behavior when scripts cannot run.
- Avoid silently inventing database search results when an optional search script is unavailable.
- Document differences in `skill.meta.yaml`, the registry entry, and the Skill changelog.

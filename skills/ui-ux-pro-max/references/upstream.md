# Upstream Tracking

## Source snapshot

- Repository: `nextlevelbuilder/ui-ux-pro-max-skill`
- Tracked release: `v2.14.1`
- Tracked commit: `abb7f2fd5a083fa1ff55c326a963ff0d95c33f99`
- License: MIT
- Original skill path: `.claude/skills/ui-ux-pro-max/SKILL.md`

The upstream project contains a substantially larger searchable catalog than the compact portable fallback bundled here. The fallback is designed to keep the Skill useful in environments where local Python execution or the upstream CLI is unavailable.

## Update policy

When maintaining this port:

1. Compare the stored release and commit with upstream.
2. Review changes to the upstream `SKILL.md`, search scripts, data schema, stack list, accessibility rules, and licensing.
3. Do not blindly overwrite this port with Claude-specific paths or provider-specific tool assumptions.
4. Port behavior changes into the shared ChatGPT Web + Codex workflow first.
5. Keep Codex-only repository/terminal steps explicitly conditional.
6. Update `skill.meta.yaml`, this file, and `CHANGELOG.md` together.
7. Run the packaged search tests and Skill validator before release.
8. Require human review before merging an upstream sync.

## Compatibility intent

- ChatGPT Web: use the Skill instructions and bundled portable catalog. Run bundled scripts only when the execution environment exposes them.
- Codex: use the same shared core, plus repository inspection, local script execution, implementation, lint/test/build, and file editing.
- If an existing installation of the official upstream engine is detected, it may be used for deeper catalog queries, but do not install or update external packages without explicit user intent.

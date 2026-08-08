# Upstream Tracking

## Source snapshot

- Repository: `nextlevelbuilder/ui-ux-pro-max-skill`
- Tracked release: `v2.14.1`
- Tracked commit: `abb7f2fd5a083fa1ff55c326a963ff0d95c33f99`
- License: MIT
- Original skill path: `.claude/skills/ui-ux-pro-max/SKILL.md`

This port vendors the full `src/ui-ux-pro-max/data/` catalog and canonical `core.py`, `design_system.py`, `search.py`, `validate_data.py`, and upstream stdlib regression tests from the snapshot above. `references/quick-reference.md` remains the no-tool ChatGPT fallback; it is not a substitute for the bundled database when Python execution is available.

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

- ChatGPT Web: use the Skill instructions and no-tool quick reference; run the complete bundled engine when the execution environment exposes Python.
- Codex: use the same shared core, plus repository inspection, local script execution, implementation, lint/test/build, and file editing.
- No separate upstream installation is needed because the complete snapshot is packaged with this Skill.

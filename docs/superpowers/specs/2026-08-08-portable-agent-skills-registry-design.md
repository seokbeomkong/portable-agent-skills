# Portable Agent Skills Registry Design

## Purpose

Create a public, auditable registry of the Agent Skills actually used by `seokbeomkong`. Every entry records its upstream origin, license, OpenAI adaptation decisions, ChatGPT Web and Codex compatibility, validation state, packaged artifact, and maintenance history.

The first entry is a portable OpenAI adaptation of `nextlevelbuilder/ui-ux-pro-max-skill`.

## Core decisions

- Use an independent repository rather than a fork because the registry will track multiple upstream projects.
- Store installable Skills under `skills/<id>/`.
- Use JSON-compatible `registry.yaml` as the human- and machine-readable catalog, requiring no third-party parser.
- Store integrated upstream revisions separately in `upstream/upstream-lock.json`.
- Detect upstream changes automatically, but never apply or merge them automatically.
- Create or update a deduplicated GitHub Issue by default; optionally prepare a draft review PR without advancing the integrated revision.
- Package each Skill deterministically as `dist/<id>/skill.zip`, with one top-level folder and a 25 MB maximum.

## Repository layout

```text
portable-agent-skills/
├── README.md
├── registry.yaml
├── skills/
│   └── ui-ux-pro-max/
├── upstream/
│   ├── upstream-lock.json
│   └── upstream-observed.json
├── scripts/
│   ├── registry_lib.py
│   ├── validate_registry.py
│   ├── generate_catalog.py
│   ├── package_skills.py
│   ├── check_upstreams.py
│   └── prepare_upstream_review.py
├── tests/
├── docs/
└── .github/workflows/
```

## Upstream lifecycle

1. A scheduled workflow runs each Monday at `00:15 UTC` (`09:15 Asia/Seoul`) and supports manual dispatch.
2. The checker reads only GitHub release and commit metadata; it never downloads or executes upstream code.
3. It compares the latest release and tracked branch commit with the integrated lock.
4. A stable marker, `<!-- upstream-skill:<id> -->`, deduplicates update Issues.
5. If the port later matches upstream, the workflow closes the stale Issue.
6. Optional draft-PR mode updates observation/status records only. It must not change `integrated_release` or `integrated_commit`.
7. A maintainer or agent reviews the upstream diff, adapts provider-specific instructions, runs validation, updates the integrated lock, and merges through the normal review process.

## First Skill

Register `ui-ux-pro-max` as a `port` with:

- upstream repository: `nextlevelbuilder/ui-ux-pro-max-skill`
- integrated release: `v2.14.1`
- integrated commit: `abb7f2fd5a083fa1ff55c326a963ff0d95c33f99`
- upstream license: MIT
- ChatGPT Web: supported through the bundled portable catalog and reference workflow
- Codex: supported with repository inspection, framework detection, script execution, implementation, and project verification

## Validation

The validator checks catalog shape, unique IDs, required Skill files, matching `SKILL.md` names, lock consistency, license/notice files, command paths, symlinks, unsafe archive paths, and package size.

The package builder sorts files, uses a fixed ZIP timestamp, rejects symlinks, and produces byte-for-byte reproducible archives.

## Security

- Use only repository-scoped `GITHUB_TOKEN` in Actions.
- Grant minimal workflow permissions.
- Do not execute upstream code in scheduled checks.
- Reject symlinks in distributable Skills.
- Never auto-merge an upstream synchronization.
- Treat top-level MIT terms as applying only to registry-authored tooling and documentation; preserve each Skill's own license and notices.

## Success criteria

- A clean clone runs all tests and tools with Python 3.11+ and no third-party packages.
- `ui-ux-pro-max` packages into a valid single-Skill ZIP below 25 MB.
- Fixture tests cover current, updated, and API-error states.
- The README catalog is generated from `registry.yaml` and can be checked for drift.
- GitHub Actions validate every PR and create/update an Issue when upstream changes.

# Portable Agent Skills Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public-ready multi-Skill registry, register UI UX Pro Max as the first ChatGPT Web + Codex port, and add safe upstream-update automation.

**Architecture:** Store portable Skills under `skills/`, drive catalog and tooling from JSON-compatible `registry.yaml`, and keep integrated versus merely observed upstream revisions separate. Use standard-library Python for validation, deterministic packaging, catalog generation, update checks, and review preparation; use GitHub Actions for CI and scheduled issue creation.

**Tech Stack:** Python 3.11+ standard library, Git, GitHub Actions, Markdown, JSON-compatible YAML.

## Global Constraints

- Never execute upstream code during update detection.
- Never auto-merge an upstream synchronization.
- Do not change integrated revisions until a maintainer has reviewed and ported the change.
- Preserve upstream attribution and license notices.
- Package each Skill with one top-level directory named after the Skill ID.
- Keep every Skill ZIP at or below 25 MB.

---

### Task 1: Bootstrap metadata and register the first Skill

- [ ] Copy the verified `ui-ux-pro-max` port into `skills/ui-ux-pro-max`.
- [ ] Create `registry.yaml`, `upstream/upstream-lock.json`, and `upstream/upstream-observed.json`.
- [ ] Add repository and third-party licenses/notices.
- [ ] Commit the first registry entry.

### Task 2: Implement validation and deterministic packaging with TDD

- [ ] Write tests for loading metadata, unique IDs, matching Skill names, required files, symlink rejection, and reproducible ZIP bytes.
- [ ] Run tests and confirm they fail because implementation is missing.
- [ ] Implement `registry_lib.py`, `validate_registry.py`, and `package_skills.py`.
- [ ] Run tests and commit.

### Task 3: Implement upstream comparison and review preparation with TDD

- [ ] Write tests for no-change, release change, commit change, API error, and preserving integrated revisions.
- [ ] Run tests and confirm failure.
- [ ] Implement `check_upstreams.py` and `prepare_upstream_review.py`.
- [ ] Run tests and commit.

### Task 4: Generate the public catalog and documentation

- [ ] Implement `generate_catalog.py` with stable README markers and `--check` mode.
- [ ] Add installation, compatibility, adaptation, licensing, and maintenance docs.
- [ ] Add contribution, security, and changelog files.
- [ ] Generate README and commit.

### Task 5: Add GitHub Actions

- [ ] Add validation, packaging/release, and scheduled upstream-watch workflows.
- [ ] Use minimal permissions and a stable Issue marker for deduplication.
- [ ] Add Issue and PR templates.
- [ ] Verify workflow syntax and commit.

### Task 6: Verify and deliver

- [ ] Run all unit tests, validators, catalog checks, packaging checks, compile checks, and the Skill's own checks.
- [ ] Verify package integrity and size.
- [ ] Create a repository ZIP and Git bundle.
- [ ] Attempt publication and report the exact blocker if repository creation is unavailable.

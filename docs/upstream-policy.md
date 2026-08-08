# Upstream Maintenance Policy

## Automated detection

`.github/workflows/upstream-watch.yml` runs every Monday at `00:15 UTC` and on manual dispatch. It compares:

- the latest GitHub release against `integrated_release`
- the tracked branch head against `integrated_commit`

The workflow reads metadata only. It does not clone or execute upstream code.

## Issue behavior

The workflow creates or updates one open Issue per Skill using a stable marker:

```text
<!-- upstream-skill:<skill-id> -->
```

When the integrated lock catches up, the workflow closes the stale Issue automatically.

## Review process

1. Inspect the upstream release notes and commit diff.
2. Identify changed instructions, scripts, references, assets, and licenses.
3. Reapply the portability and compatibility policies.
4. Update the Skill and its changelog.
5. Run all registry and Skill-specific validation.
6. Update `integrated_release` and `integrated_commit` only after the port is reviewed.
7. Submit a PR; never auto-merge.

`prepare_upstream_review.py` may record observed state and mark a port `review-required`, but it intentionally leaves integrated revisions unchanged.

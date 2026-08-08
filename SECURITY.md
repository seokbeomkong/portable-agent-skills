# Security Policy

## Supported content

The current branch and the latest published Skill packages receive security maintenance.

## Reporting

Do not open a public Issue for a vulnerability that could expose credentials, enable code execution, or compromise a Skill consumer. Use GitHub's private vulnerability reporting feature when enabled for the repository.

## Automation boundaries

- Scheduled upstream checks read GitHub metadata only.
- Workflows use the repository-scoped `GITHUB_TOKEN` with minimal permissions.
- Upstream code is not executed during update detection.
- Distributable Skills may not contain symlinks.
- Upstream changes are never auto-merged.

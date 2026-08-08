# Install in ChatGPT Web

## Installation

1. Open the repository's latest GitHub Release.
2. Download the ZIP named for the Skill, for example `ui-ux-pro-max.skill.zip`.
3. In ChatGPT, select **Plugins** in the sidebar, open the **Skills** tab, and choose **Create**.
4. Select **Upload from computer** and upload the ZIP.
5. Confirm the Skill appears in your installed or created Skills.
6. Start a new chat and ask for a task covered by the Skill description.

Personal Skills are installed separately on different product surfaces; installing the ZIP in ChatGPT Web does not automatically install it in Codex.

Official reference: <https://help.openai.com/en/articles/20001066>

## Smoke test for UI UX Pro Max

Ask:

> Create a design system for a B2B analytics dashboard. Include accessibility, responsive layout, typography, color tokens, motion rules, and implementation guidance for Next.js.

A successful invocation should return a coherent design system, identify accessibility and responsive constraints, and distinguish design guidance from repository-editing capabilities that require Codex.

## Smoke test for Humanize Korean

Ask:

> 이 자기소개서를 원문의 사실·수치·역할을 보존하면서 자연스럽게 윤문해줘. 정밀 경로를 사용해줘.

A successful invocation should select the heavy path, preserve protected claims and structure, and state which deterministic checks were available in that ChatGPT environment.

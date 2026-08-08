---
name: ui-ux-pro-max
description: "Portable UI/UX design intelligence for ChatGPT Web and Codex. Use when designing, building, refactoring, or reviewing web/mobile interfaces; creating design systems; choosing layouts, colors, typography, component patterns, responsive behavior, accessibility, interaction states, motion, dashboards/charts, or stack-specific UI implementation. Also use for UI polish, UX audits, landing pages, SaaS/admin dashboards, native app screens, and frontend code changes where visual or interaction quality matters."
---

# UI UX Pro Max

Provide design-system reasoning, UX review, accessibility checks, and stack-aware implementation guidance through one shared workflow that works in ChatGPT Web and Codex. This package bundles the complete upstream v2.14.1 BM25 engine, all domain CSVs, and all 22 stack catalogs.

Treat this package as a portable OpenAI adaptation of `nextlevelbuilder/ui-ux-pro-max-skill`. Preserve upstream attribution and use `references/upstream.md` when maintaining or syncing the port.

## Execution anchor

Resolve `SKILL_ROOT` from the runtime-provided absolute path of this `SKILL.md`. Every `<SKILL_ROOT>` below means that absolute directory; never assume the current working directory contains this Skill. Write persisted design systems only beneath an explicit user project path, never inside the installed Skill.

## Operating modes

Choose the strongest available mode without blocking on unavailable tooling.

### Shared mode: ChatGPT Web and Codex

Use this mode for every relevant request.

1. Extract the product, audience, primary task, platform, tone, information density, and motion expectations from the request.
2. Determine whether the task is a new design, an implementation, or a review.
3. Use `references/quick-reference.md` as the no-tool baseline. When Python is available, query the full bundled database in `data/`.
4. Produce a coherent recommendation instead of a menu of unrelated styles.
5. Make accessibility, interaction clarity, responsive behavior, and state design non-negotiable baseline requirements.
6. Follow `references/output-contract.md` for design systems and reviews.

### Tool-assisted mode

If local script execution is available, prefer the bundled dependency-free helper for repeatable catalog lookup:

```bash
python "<SKILL_ROOT>/scripts/search.py" "<product industry tone keywords>" --design-system -p "<Project Name>"
```

If `python` is unavailable, try `python3`. If execution is unavailable, continue in Shared mode and do not claim that a database query ran.

Use explicit domains for focused lookup:

```bash
python "<SKILL_ROOT>/scripts/search.py" "<query>" --domain product
python "<SKILL_ROOT>/scripts/search.py" "<query>" --domain style
python "<SKILL_ROOT>/scripts/search.py" "<query>" --domain color
python "<SKILL_ROOT>/scripts/search.py" "<query>" --domain typography
python "<SKILL_ROOT>/scripts/search.py" "<query>" --domain landing
python "<SKILL_ROOT>/scripts/search.py" "<query>" --domain gsap
python "<SKILL_ROOT>/scripts/search.py" "<implementation concern>" --stack nextjs
```

The engine is stdlib-only and reads package-relative data, so no external installation or network access is required. Korean product/style terms have common English aliases in the tokenizer; for uncommon Korean terms, translate the search query into concise English keywords while keeping the user's request itself unchanged.

### Codex-enhanced mode

When repository access is available, add the following steps:

1. Detect the actual frontend stack from project files before giving stack-specific advice. Read `references/framework-detection.md`.
2. Inspect existing design tokens, components, layout primitives, routes/screens, and accessibility patterns before changing code.
3. Reuse the project's existing component library and conventions unless the user asks to replace them.
4. Implement the smallest coherent change that satisfies the design system.
5. Run relevant lint, typecheck, unit/UI tests, and build commands that already exist in the repository.
6. Inspect the final UI states in code and, when visual/browser tooling is available, verify the rendered result at narrow and wide widths.
7. Report what changed and what verification passed or remains unverified.

Do not make repository editing a requirement for ChatGPT Web use.

## Workflow

### 1. Classify the request

Use one of these paths:

- **New page/app/design system:** generate a design system before implementation.
- **Existing UI implementation/refactor:** inspect existing tokens and components, then generate only the missing design decisions.
- **UX/UI review:** inspect the supplied UI, screenshot, code, or description and prioritize defects by impact.
- **Focused question:** answer only the requested dimension such as typography, color, motion, accessibility, layout, forms, navigation, or charts.

Do not force a full design-system exercise onto a narrow question.

### 2. Analyze requirements

Capture as many of these as the request provides:

- Product/industry and business model
- Primary user and primary job-to-be-done
- Platform: responsive web, desktop web, iOS, Android, cross-platform, kiosk, spatial, or hybrid
- Brand adjectives and desired emotional tone
- Content density and expected frequency of use
- Accessibility or regulatory constraints
- Existing design system/component library
- Frontend stack

Infer obvious details from repository evidence when available. Ask only when a missing decision materially changes the output and cannot be inferred.

### 3. Generate the design direction

For a new page/project, produce one primary direction containing:

- Information pattern and section/screen order
- Primary visual style and optional secondary influence
- Semantic color tokens
- Typography pairing and hierarchy
- Spacing/density strategy
- Motion/feedback strategy
- Component and state priorities
- Accessibility requirements
- Product-specific anti-patterns
- Stack-specific notes when known

Use the helper when possible:

```bash
python "<SKILL_ROOT>/scripts/search.py" "<query>" --design-system -p "<project>" --format markdown
python "<SKILL_ROOT>/scripts/search.py" "<implementation concern>" --stack <stack>
```

Optional design dials:

```bash
--variance 1-10   # conservative to expressive
--motion 1-10     # minimal to choreographed
--density 1-10    # spacious to dense
```

Treat the helper output as a recommendation to critique and synthesize, not an instruction to apply blindly.

### 4. Persist design decisions when useful

In a repository workflow, persist a stable master design system when the user wants reuse across pages or sessions:

```bash
python "<SKILL_ROOT>/scripts/search.py" "<query>" --design-system -p "<project>" --persist --output-dir "<project-root>"
```

Use `--page "<page-name>"` to create a page override stub. Do not overwrite an existing `MASTER.md` unless the user intends to regenerate it; use `--force` only deliberately.

When a project already has its own design-system documentation, update that source of truth instead of creating a parallel one.

### 5. Apply priority rules

Resolve conflicts in this order:

1. Accessibility and comprehension
2. Task completion and interaction feedback
3. Responsive layout and input modality
4. Performance and stability
5. Product/style fit and hierarchy
6. Typography and semantic color
7. Forms, errors, and system feedback
8. Navigation and information architecture
9. Motion and delight
10. Charts and decorative refinement

Read `references/quick-reference.md` when the task touches multiple categories or needs a delivery checklist.

### 6. Choose styles with discipline

- Select one primary style.
- Add at most one secondary influence unless the user explicitly wants maximalism or deliberate hybridity.
- Tie every visual decision to product context, audience, information density, or brand intent.
- Do not use a trend merely because it is fashionable.
- Avoid generic AI gradients, gratuitous glass effects, excessive glow, card grids with equal visual weight, and decorative motion unless the product context supports them.
- Keep interactive affordances obvious even in experimental visual styles.

### 7. Design every important state

For interactive elements and flows, cover relevant states:

- default
- hover where pointer input exists
- keyboard focus
- pressed/active
- selected
- loading/progress
- success
- validation error
- disabled
- empty/no-results
- partial/offline/stale data when relevant

Do not treat loading, error, or empty states as implementation leftovers.

### 8. Review existing UI by impact

When reviewing, separate findings into Critical, High, Medium, and Low using `references/output-contract.md`.

Prioritize observable problems such as:

- inaccessible contrast or names
- unreachable keyboard controls
- missing focus state
- ambiguous destructive actions
- mobile overflow
- hidden or inconsistent navigation
- missing feedback
- unusable touch targets
- hierarchy that obscures the primary task
- chart encodings that depend on color alone
- layout shift or janky interaction

Distinguish objective usability/accessibility defects from stylistic preference.

### 9. Implement stack-aware UI

When code is requested:

- Detect or confirm the stack before writing stack-specific code.
- Use existing tokens and primitives before adding new abstractions.
- Keep semantic HTML/native semantics intact.
- Keep design tokens centralized.
- Preserve library accessibility behavior when restyling components.
- Avoid unnecessary dependencies for simple visual effects.
- Add animation only after static layout and interaction states are correct.

Use:

```bash
python "<SKILL_ROOT>/scripts/search.py" "<implementation concern>" --stack <detected-stack>
```

for the bundled stack notes.

### 10. Verify before delivery

For design recommendations, review the pre-delivery checklist in `references/quick-reference.md`.

For code changes in Codex, additionally:

- run existing lint/typecheck/test/build commands relevant to the edited area
- check for console/runtime errors when tooling permits
- verify narrow and wide responsive behavior
- verify keyboard focus and reduced-motion behavior for changed interactions
- confirm no placeholder content or debug artifacts remain unless requested

Never claim visual or runtime verification that was not actually performed.

## Fallback behavior

If the helper returns no strong catalog match:

1. Broaden the product query once.
2. Use the closest product archetype only if the mapping is reasonable.
3. Otherwise use the neutral baseline in `references/quick-reference.md`.
4. State that the recommendation is a general fallback rather than a catalog-specific match when that distinction matters.

If a requested stack is not among the 22 bundled catalogs, give stack-neutral guidance and use the repository's own conventions.

## Maintenance

Read `references/upstream.md` before updating this Skill from upstream.

Keep these invariants during every sync:

- preserve `name: ui-ux-pro-max`
- preserve ChatGPT Web no-tool fallback
- preserve Codex conditional repository workflow
- remove Claude-specific root variables and provider-only assumptions from shared instructions
- preserve the complete upstream `data/` catalog and canonical `core.py`, `design_system.py`, `search.py`, and `validate_data.py`
- preserve upstream license notice
- update `skill.meta.yaml` and `CHANGELOG.md`
- run `scripts/check_port.py`
- run the Skill validator and package the full Skill only after checks pass

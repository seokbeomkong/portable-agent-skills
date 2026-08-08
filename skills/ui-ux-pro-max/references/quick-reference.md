# Portable UI/UX Quick Reference

Use this file when the task needs detailed design judgment without running the search script. It intentionally distills portable principles instead of copying the upstream catalog verbatim.

## 1. Accessibility first

- Target at least 4.5:1 contrast for normal body text and 3:1 for large text and essential UI graphics where applicable.
- Keep keyboard focus visible and logical.
- Give icon-only controls an accessible name.
- Use semantic elements before ARIA. Add ARIA only when native semantics are insufficient.
- Never depend on color alone for status, errors, trends, or selections.
- Keep text zoom and responsive reflow usable; do not disable browser zoom.
- Respect `prefers-reduced-motion` for nonessential motion.

## 2. Touch and interaction

- Use a practical minimum target around 44x44 CSS px/pt for primary touch controls; allow spacing around smaller visual affordances.
- Provide pressed, selected, loading, success, error, disabled, and focus states where relevant.
- Never make a critical action discoverable only on hover.
- Keep destructive actions explicit and recoverable when possible.
- Give async actions immediate feedback and prevent accidental duplicate submissions.

## 3. Layout and responsiveness

- Start from the narrow layout and progressively add columns and density.
- Prevent horizontal scrolling for normal page content.
- Use container max-widths and fluid gutters instead of fixed desktop canvases.
- Test at representative widths around 375, 768, 1024, and 1440 CSS px, plus content-driven edge cases.
- Preserve reading order when cards or panels reflow.
- Keep sticky elements from covering focused content or mobile browser chrome.

## 4. Typography

- Use a base body size around 16px unless product constraints justify otherwise.
- Prefer line-height around 1.45-1.7 for body copy.
- Keep long-form lines roughly 45-80 characters where practical.
- Limit the number of type families; use weight, size, spacing, and color before adding more fonts.
- Use monospace primarily for code, identifiers, and tabular technical data.

## 5. Color and tokens

- Define semantic tokens such as `--color-bg`, `--color-surface`, `--color-text`, `--color-muted`, `--color-border`, `--color-primary`, `--color-accent`, `--color-danger`, and focus tokens.
- Do not scatter raw hex values through component implementations when a token exists.
- Test muted text, borders, disabled states, charts, and dark-mode surfaces separately from primary text.
- Use accent color sparingly so it keeps meaning.

## 6. Motion

- Use short interaction transitions, often about 150-300ms.
- Animate transform and opacity before layout properties when possible.
- Motion should explain state, hierarchy, continuity, or causality.
- Avoid continuous decorative motion around reading or data-dense tasks.
- Provide a reduced-motion path that preserves information and functionality.

## 7. Forms and feedback

- Keep persistent labels for fields; placeholders are examples, not labels.
- Put error text close to the affected field and explain how to recover.
- Preserve user input after validation failures.
- Use progressive disclosure for advanced options.
- Make required/optional status clear before submission.

## 8. Navigation

- Keep primary navigation stable across related pages.
- Preserve expected back behavior.
- For mobile bottom navigation, keep the primary destinations few and clearly labeled.
- Provide deep links for meaningful destinations in apps and complex web products.
- Avoid hiding essential navigation behind novelty interactions.

## 9. Dashboards and charts

- Start with the user decision, not the available data.
- Give the most important KPI or exception the strongest visual weight.
- Use tables for precise comparison and charts for pattern recognition.
- Avoid pie/donut charts when many categories or close values make comparison difficult.
- Label units and time ranges; expose data freshness.
- Pair color encodings with labels, shapes, patterns, or direct annotation when possible.

## 10. Performance as UX

- Reserve media dimensions to avoid layout shift.
- Use modern image formats and responsive sizing where the platform supports them.
- Lazy-load below-the-fold media without delaying critical content.
- Avoid heavy main-thread animation and unnecessary re-renders.
- Design loading, empty, error, offline, and partial-data states rather than treating them as implementation details.

## Pre-delivery review

1. Check semantic structure and accessible names.
2. Check keyboard-only usage and visible focus.
3. Check contrast and non-color cues.
4. Check 375/768/1024/1440 layouts and unusual content lengths.
5. Check hover, focus, pressed, loading, success, error, disabled, and empty states.
6. Check reduced-motion behavior.
7. Check images, icons, and charts for labels/alternatives.
8. Check critical paths for accidental destructive actions or lost input.
9. Check that the visual system uses shared tokens consistently.
10. Check that performance choices do not create layout shift, jank, or delayed feedback.

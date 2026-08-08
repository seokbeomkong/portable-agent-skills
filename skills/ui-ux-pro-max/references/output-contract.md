# Design Output Contract

Use this structure when a user asks for a design recommendation, design system, UI review, or implementation plan. Omit sections that do not apply.

## Design system recommendation

- **Context:** product, audience, environment, primary task.
- **Pattern:** page/app structure and information hierarchy.
- **Style direction:** 1 primary style, at most 1 secondary influence, and why they fit.
- **Color tokens:** primary, secondary, accent, background, surface, text, muted, border, danger, focus.
- **Typography:** heading/body/code choices plus hierarchy guidance.
- **Spacing and density:** base spacing rhythm and density level.
- **Motion:** interaction timing, entrance/exit behavior, reduced-motion strategy.
- **Components:** high-priority components and important states.
- **Accessibility:** concrete checks for contrast, keyboard, names, semantics, touch, motion.
- **Anti-patterns:** specific things to avoid for this product.
- **Stack notes:** implementation guidance for the detected/requested framework.

## Review output

Separate findings into:

1. **Critical:** blocks task completion, accessibility, safety, or comprehension.
2. **High:** major interaction, responsive, information hierarchy, or trust problem.
3. **Medium:** consistency, clarity, visual polish, minor friction.
4. **Low:** optional refinement.

For each finding include:

- Location/component
- Observed problem
- Why it matters
- Concrete fix
- Verification method

Do not report subjective taste as a defect unless it conflicts with the user's stated design direction or an explicit usability principle.

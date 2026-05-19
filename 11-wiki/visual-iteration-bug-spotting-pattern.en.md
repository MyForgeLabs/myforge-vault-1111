---
name: Visual iteration — bug-spotting beats vibe-feedback
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
lang: en
tags: ["#type/wiki", "visual-design", "iteration", "feedback-loop"]
related:
  - "[[stale-numbers-in-static-artifacts-pattern.en]]"
---

# Visual iteration — bug-spotting beats vibe-feedback

When iterating on a visual artifact (SVG hero-banner, Figma mockup, dashboard, slide), the user feedback that **converges fastest** is the precise bug-spot, not the global vibe judgment.

## The 2026-05-19 hero-banner iteration (3 rounds, 5 minutes each)

| Round | User feedback | Action | Outcome |
|---|---|---|---|
| 1 | "Nem tetszik, kilognak az ablakokból a feliratok" | Identify which labels overflow which boxes → widen card-1 and card-2 by 40px; shrink subtitle letter-spacing 1.8 → 1.5 | Major overflow fixed |
| 2 | "A B-5 nél nem látszik a felirat" | One specific axis-node label clipping. Move whole diagram up 30px (translate y 380 → 350) | B-5 label clears the footer-strip |
| 3 | "A felső sor benyúl a jobb sarokban lévő feliratba" | Subtitle (83 chars) reaching into the right-meta zone. Shortened to 56 chars | Subtitle now ends ~250px before the right-meta |

Three iterations, each ~3-5 minutes wall-clock. Total time-to-acceptable: 12 minutes.

## The anti-pattern

If the user had said "csináld jobban" or "valami nem stimmel" after each render, the agent would have:

- regenerated from scratch with a slightly different style → maybe better, maybe worse
- needed 5-10 iterations to converge
- still missed specific bugs (label-clip, overflow) because no specific spot was named

**Vibe feedback is non-convergent.** Specific bug-spot feedback is.

## The pattern (for users)

When iterating on a visual artifact with an agent:

1. **Name the exact element**: "B-5 label", "right-side meta line", "subtitle"
2. **Name the exact problem**: "clipped by footer", "overlaps with X", "wrong color contrast"
3. **Optionally**: where you'd like it instead

DON'T:

- "Make it better"
- "I don't like it"
- "Try again"

DO:

- "B-5 label is cut off at the bottom"
- "Subtitle extends past the right-side meta text"
- "Card #2 row 1 has 'baseline 0.541 → 0.619' text wrapping outside"

## The pattern (for agents)

When the user reports a visual issue:

1. **Read the source** (SVG / Figma JSON / CSS), don't just regenerate.
2. **Compute the bug**: which y-coord clips? Which x-coord overflows? What's the actual width-vs-container-width math?
3. **Apply the minimum fix**: move 1 element, widen 1 container, shorten 1 string. Don't restyle everything.
4. **Render + ask for verify** before pushing the artifact public.

The fix-to-regen ratio should be: 1 measurement → 1 line edit → 1 re-render → 1 user verify.

## When this pattern doesn't apply

- Initial brand-direction decision ("warm vs cool palette") — that's pure vibe territory and needs taste-feedback
- Major restructure ("move the 8-axis to a separate page") — needs scope conversation, not iteration

The bug-spotting discipline kicks in **after** the structural decisions are settled and the user is verifying details.

## Related

- [[stale-numbers-in-static-artifacts-pattern.en]] — sibling lesson from the same hero-banner iteration
- [[verification-step-before-claim]] — measure-twice-cut-once in code reviews; same spirit applied to visuals
- [[../06-Audits/2026-05-19 mega-session summary]] — the hero-banner v2 thread

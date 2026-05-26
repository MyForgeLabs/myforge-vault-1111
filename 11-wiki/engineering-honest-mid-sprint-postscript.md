---
name: Engineering-honest mid-sprint postscript
description: When a published essay or doc section's premise gets refuted mid-sprint, the right move is an explicit "Postscript (date)" callout within the same section — not a quiet edit. Engineering-credibility-strengthening, not weakening.
type: wiki
created: 2026-05-21
updated: 2026-05-21
tags: ["#type/wiki", "writing-pattern", "engineering-credibility", "public-build"]
---

# Engineering-honest mid-sprint postscript

## A pattern

You publish an essay, blog post, or wiki article. A section of it makes a claim, premise, or forecast. Days or weeks later, **the premise gets refuted empirically** — the experiment fails, the metric was wrong, the architecture didn't work. What do you do?

**Wrong move:** silently edit the section to remove the broken premise. Or worse, ship a new version that quietly contradicts the old one.

**Right move:** add an explicit `**Postscript (YYYY-MM-DD) — <one-line summary>**` callout **within the same section**, right where the original premise lives. Then explain:

1. The premise was wrong.
2. Here's the empirical evidence that refuted it.
3. Here's the actual fix that landed.
4. Here are the numbers.

The original section stays. The postscript runs after it.

## Why this works

- **Engineering-honest** — public-build audiences (HN, GitHub, Dev.to) reward "I was wrong about X, here's the actual answer" far more than "I always knew Y." The former is engineering. The latter is marketing.
- **Mid-sprint pivot becomes visible** — readers see how the thinking evolved, not just the endpoint. This is the rarest thing in public engineering writing, because most writeups optimize for finality.
- **Search-and-grep stays consistent** — the wiki/essay URL doesn't 404, anchor links still work, prior references stay valid. A reader who clicked a permalink from 2026-05-19 sees the *same* permalink with both the original claim and the postscript explaining why it was wrong.
- **The reader does the comparison work** — they get the original prediction and the actual result side-by-side, and form their own judgement. That's the strongest form of engineering credibility.

## When this fires

| Trigger | Right move |
|---|---|
| Section's experiment failed | Postscript: what we learned + what landed instead |
| Forecast didn't pan out | Postscript: actual numbers + reframe |
| Target/metric turned out to be misformed | Postscript: revised target + reasoning |
| Section's tool/library got deprecated | Postscript: replacement + migration path |
| Architecture pivot mid-sprint | Postscript: new architecture link |

## Template

```markdown
### <Section title — UNCHANGED>

<original section body — UNCHANGED>

**Postscript (YYYY-MM-DD) — <one-line summary of what changed>**

The premise above was wrong. Here's what happened next:

[2-4 sentences explaining the empirical refutation, *not* hedging the original.]

[The actual fix that landed:]

- <bullet of what landed>
- <bullet of what landed>

[Numbers if you have them:]

| Metric | Original target | Actual result |
|---|---:|---:|
| <X> | <Y> | <Z> |

The original [old approach] integration code/artifact is preserved as <where>
for [reason, if any]. Otherwise <archived/superseded>.

Details: [[../06-Audits/YYYY-MM-DD — empirical refutation]],
[[../07-Decisions/YYYY-MM-DD — revised approach]].
```

## Concrete examples

### Karpathy-essay v1.0.10 epilogue — Path-Z (2026-05-21)

Section 5 of the Karpathy-essay v1.0.10 epilogue ("Option-B tree-sitter pre-pass") was written 2026-05-20 PM as a forecast: tree-sitter pre-pass would bridge Jaccard ≥0.05 between Memgraph LLM-entities and graphify deterministic nodes.

Empirical refutation arrived **next-day** (2026-05-21): graphify parsed zero Python source files — its labels were markdown-section-paths, not code symbols. The pre-pass would have moved Jaccard 0.0069 → 0.0068.

The right move was a **mid-sprint postscript inside section 5** that:

1. Stated the premise was wrong.
2. Explained the empirical refutation (graphify-out inspection vs. package metadata).
3. Documented the actual fix (Path-Z: complementarity metrics FCA / CD / XR replacing Jaccard label-overlap).
4. Reported the numbers (FCA 0.93 → 1.0 after corpus-normalization, CD 0.40 in revised healthy band, XR_T1 = XR_T2 = 1.0).

The original "Option-B" forecast stays. The integration code stays env-gated (`VAULT_KO_TREESITTER=1`, default off) for its independent value. The wider lesson — *"when the metric isn't moving and the algorithm work is honest, change the metric, not the algorithm"* — is captured in [[metric-design-pivot-not-algorithm]].

Closing-line milestone in the same essay also revised: "Option-B Jaccard ≥0.05" removed from the W23-gated milestone list, replaced with a back-reference to section 5's postscript.

Result: HN-launch (2026-05-26) gets a publication that **honestly shows the mid-sprint pivot** rather than a sanitized retroactive narrative.

## Anti-patterns

> [!warning] What NOT to do

1. **Silent edit** — replace the original claim with the new one, lose the audit-trail. Future readers who shared the original permalink can't reconcile.
2. **Hedge the original** — "we thought X (though see below)" weakens both the original story and the postscript. Keep the original confident; let the postscript do the correction.
3. **New separate post** — "see the follow-up at /v2 for what actually happened" splits the narrative. Readers landing on /v1 see only the broken premise.
4. **Quiet retraction without numbers** — a postscript without the empirical evidence reads as opinion-flip. The numbers (or audit-link) are what make it engineering-honest.
5. **Skip the postscript and ship v1.0.11** — if the original was a milestone post tied to a release tag, the postscript has to land in the v1.0.10 doc. v1.0.11 can reference it.

## Cross-platform compatibility

The pattern works across:

- **GitHub Pages mkdocs** (where most public vaults live) — `**Postscript**` renders as bold, `> [!info]` Obsidian callouts work in many themes
- **Plain markdown blogs** — the bold-postscript is universally compatible
- **Print PDFs** — the timestamp + reason are searchable
- **Static-site generators** (Astro, Hugo, Eleventy) — no special syntax required

## Related

- [[metric-design-pivot-not-algorithm]] — sibling pattern: when to pivot the metric, not the algorithm
- [[stale-numbers-in-static-artifacts-pattern.en]] — cousin pattern: stale numbers vs. live cross-source verification
- [[multi-layer-safety-gate]] — companion: safety patterns for high-risk experiments
- [[tool-sandbox-eval-playbook]] — the engineering discipline that often produces these postscripts

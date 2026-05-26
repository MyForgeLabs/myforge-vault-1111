---
name: Stale numbers in static artifacts
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
lang: en
tags: ["#type/wiki", "marketing-copy", "stale-numbers", "automation", "anti-pattern"]
related:
  - "[[../06-Audits/2026-05-19 mega-session summary]]"
---

# Stale numbers in static artifacts

The hero-banner SVG shipped on 2026-05-18 had **five stale numbers** within 24 hours of launch:

| Field | Banner said | Actual |
|---|---:|---:|
| Wiki pages | 220 | **265** |
| ADRs | 28 | **45** |
| Sessions | 76 | **80** |
| SKILL.md | 462 | **962** |
| Version | v0.1 | **v1.0.8** |

The numbers were correct at SVG-creation time. They went stale because the underlying content grew faster than the manual-refresh cadence on the marketing asset.

## The trap

Hard-coded numbers in:

- README badges (`![wiki](shields.io/badge/wiki-220-orange)`)
- Hero-banner / social-preview images
- Marketing-copy / launch-playbook posts
- Generated CHANGELOG version-summary tables
- Documentation site footers ("250 wikis · 12K entities · …")

…all rot the moment the underlying data moves. The bigger the project, the faster.

## The asymmetric cost

Stale numbers in a public OSS launch are a **trust-loss event**:

- A reader who clicks through README → 11-wiki/ and sees 265 files when the badge said 220 silently doubts the rest of the README.
- HN/Reddit commenters cross-check the headline numbers (`gh api repos/.../contents/11-wiki | jq length`) and call out drift in 200-upvote replies.
- The cost of being caught is much higher than the cost of dynamic generation.

## The two correct patterns

### Pattern A — Auto-generated from live state (preferred)

A single source-of-truth script computes the numbers, regenerates the asset on cron. Examples:

- `vault-stats-generator` (already in this vault) → writes `docs/stats/vault-stats.json` weekly; README badges read from shields.io endpoints that consume the JSON.
- Hero-banner: regenerate the SVG nightly from a Jinja template + live `vault-stats.json`.

The asset still ships as a static file in the repo (no runtime dependency), but it's *regenerated* on a known cadence with an audit trail.

### Pattern B — "last-refreshed-at" stamp (fallback)

When auto-generation is impractical (e.g. hand-illustrated hero, slide deck), embed a visible "Last refreshed: 2026-05-19" stamp in the asset. Trust degrades gracefully; readers see the date and can mentally adjust.

The hero-banner v2 (2026-05-19) ships with all five numbers refreshed manually + a `v1.0.8` version stamp visible. Pattern A is the next step — automate the SVG-regen via a `vault-hero-banner-refresh` cron.

## Detection

Add to the pre-release checklist:

```bash
# Compare every hard-coded number in README/hero-banner/marketing to the live count
diff <(grep -oE 'badge/wiki-[0-9]+' README.md | cut -d- -f2) \
     <(ls 11-wiki/*.md | wc -l)
```

For larger projects: a CI job that scans key marketing assets against the live numbers and fails on drift >5%.

## The wider lesson

Any number that appears in a static artifact and could change tomorrow is **technical debt with a half-life**. Either pay the auto-generation cost up-front, OR stamp it with a date so the rot is visible.

This pattern composes with [[two-tier-graph-extraction]] (any cross-check between independent data sources surfaces drift) and [[audit-md-self-referential-loop]] (the meta-discipline of having auditors that catch their own output).

## 2026-05-19 PM — Every release re-applies, not 1-time fix

The hero-banner v2 fix from the AM mega-session (5 stale numbers, 12-min iteration) was thought to be a "fix it once, move on" cleanup. By the next day's PM session, **the same banner had drifted again** — counts that were accurate at v1.0.8-RC stage were no longer accurate by v1.0.9 (wiki 265 → 274, ADR 45 → 46, audits 104 → 126, Memgraph 8997 → 8913, recall 67.68% → 76.77%). A `number-refresh` subagent caught all of them; **without it, the v1.0.9 release would have shipped with stale numbers in the README badges, hero-banner, and HN essay**.

3 surprising stale-number patterns this session caught:

1. **`9004` (no comma) in HN essay** — appeared 3× in counts and 1× as a heading number. A `grep -r "9,004"` would have missed all 4 occurrences. **Lesson**: when grep-ing for numbers in artifacts, also try the no-thousands-separator variant.
2. **Hero-banner mid-release drift** — the v2 banner from yesterday was already stale by today. **Lesson**: banner-generation should be wired into the release-build (Makefile target, GitHub Actions step), not done as a manual "OK it's perfect now" step.
3. **BibTeX `version = {1.0.1}`** — the `CITATION.cff`-derived BibTeX block was never updated past the first release. Each new release silently cites v1.0.1. **Lesson**: every release's diff-checklist must include the BibTeX/CITATION version field.

**Wider re-lesson**: "stale-numbers in static artifacts" is **NOT a 1-time fix** — it's a **continuous-decay anti-pattern**. Each release re-applies the refresh-pass. Either wire it into `make release` / GitHub Actions / pre-commit hook with auto-grep-vs-live-state, OR accept that every Nth release needs a dedicated `number-refresh` subagent pass.

## Related

- [[../06-Audits/2026-05-19 mega-session summary]] — the hero-banner v2 fix (AM session)
- [[vault-stats-generator]] (referenced as auto-gen example; verify path on this vault)
- [[two-tier-graph-extraction]] — cross-source verification pattern
- [[audit-md-self-referential-loop]] — auditor-output discipline
- [[idempotency-frontmatter-date-anchor]] — sibling pattern for cron-written files

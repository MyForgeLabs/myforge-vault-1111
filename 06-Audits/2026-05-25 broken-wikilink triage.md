---
name: broken-wikilink triage
type: audit
created: 2026-05-25
updated: 2026-05-25
tags: ["#type/audit", "cleanup", "wikilinks"]
---

# Broken wikilink triage (35 targets, 2026-05-25)

Snapshot from [broken-wikilinks-2026-05-25.json](broken-wikilinks-2026-05-25.json). The audit has been flat at ~35 broken targets / ~44 refs for the last several weeks — bulk auto-fix isn't worth the risk because most are intentional (skill-namespace refs not pinned to local files, archived docs).

## Categories

### A. Referenced file EXISTS with slightly different name (~6 found)

These could be auto-fixed by canonicalizing the reference. Worth doing if frequency grows; not worth a bulk sweep at 1 ref each.

| broken ref | likely target |
|---|---|
| `bmad-vault-bridge` | `06-Audits/2026-05-19 bmad-vault-bridge skeleton.md` |
| `firecrawl` | `10-raw/2026-05-07 — firecrawl - *.md` (multiple) |
| `vault-cleanup` | `11-wiki/vault-cleanup-multi-script-policy.md` |
| `vault-ko-ingest` | `11-wiki/vault-ko-ingest-prompt-tightening-2026-05-19.md` |
| `2026-05-18 bmad-vault-bridge skeleton` | `06-Audits/2026-05-19 bmad-vault-bridge skeleton.md` (date typo) |
| `2026-05-19 sv-1 memory architecture arch` | `07-Decisions/2026-05-12 sv-1 memory architecture arch.md` (date wrong) |

### B. Referenced concept NEVER WRITTEN (~20)

These are speculatively-linked wikis from forward-references in older planning docs. Either write the stub or accept as known-unwritten.

- `atomic-write-pattern` (referenced from atomic-write related ADRs — could become a small wiki)
- `wordpress-router`, `wp-block-development`, `wp-rest-api` (WP skill cluster — speculative refs from a wp-cluster plan that never wrote dedicated wikis)
- `longmemeval-k5-sweet-spot` (already documented in baseline.json + audits, but no dedicated wiki)
- `defuddle`, `load-session-context-pattern`, `longmemeval-vault-variant-pattern`, `multi-page-pdf-figure-check`, `react-onwheel-passive-default` (forward-refs from related docs)
- `vault-stats-generator` (script exists, no dedicated wiki)
- `sv-08-typed-entity-graph` (replaced by `sv-06-world-model-knowledge-graph` — old plan-doc forward-ref)

### C. Self-references / log files (~3)

- `broken-wikilinks-2026-05-19.json` — earlier snapshot of THIS audit, referenced from the audit's own README
- `02-Projects/<slug>/bmad/` — placeholder pattern, not a real link
- `step-00-vault-preload.md` — old SOP doc, archived

### D. Translation `.en` references (~3)

- `Johnny-Decimal-prefix.en`, `cli-session-id-env-var-matrix.en`, `notebooklm-cli-gotchas.en`
- These point to `.en.md` translation files referenced from HU wikis. The `.en` form doesn't resolve because the actual file is `.en.md`. Auto-fix: append `.md`. Low priority since `.en.md` is reachable via the language switcher.

## Recommendation

- **Don't bulk-fix.** Most are speculative forward-references that future writes will resolve.
- **Track the count** in `vault-doctor` (already there via `vault-broken-wikilinks-audit` reader if added).
- **Set a soft cap** in `vault-continuous-eval`: flag YELLOW when broken-target count exceeds 50 (currently 35, well within budget).
- **Manual nudge**: when writing a new wiki that closes one of the Category-B speculative refs, the audit count auto-decrements.

## Related

- [[../11-wiki/audit-md-self-referential-loop]] — why categories C/D were inflated in earlier scans
- [[../11-wiki/wp-elementor-template-conflicts]] — anchor for the WP cluster forward-refs (Category B)

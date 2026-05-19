---
name: Bayesian belief-update skeleton
type: audit
tags: ["#type/audit", "vault-ko", "bayesian", "contradiction-resolution"]
created: 2026-05-19
generated_by: vault-ko-belief
---

# Bayesian belief-update skeleton — calibration on real KO-DB

Brainstorm idea **#21** from
`06-Audits/2026-05-19 SV new development ideas brainstorm.md`.

Files landed:

- `/root/obsidian-vault/.vault-ko/scripts/vault-ko-belief.py` (~16 KB)
- `/usr/local/bin/vault-ko-belief` → symlink
- `/root/obsidian-vault/11-wiki/bayesian-belief-update-pattern.en.md`
- `/root/obsidian-vault/06-Audits/2026-05-19 Bayesian belief-update skeleton.md` (this file)
- `/root/obsidian-vault/06-Audits/vault-ko-belief-log.jsonl` (apply-mode audit trail)

The math is documented in
[[../11-wiki/bayesian-belief-update-pattern.en|the pattern wiki]].
This audit reports the calibration on the current KO-DB.

## Sample run — one real contradiction

```
$ vault-ko-belief --subject "robbantott-kereso" --predicate "decided_at"
```

Current candidates:

| object                                   | n | cluster_score | max_decayed | max_base | sources |
|------------------------------------------|--:|--------------:|------------:|---------:|---------|
| `KGC integration via API proxy bridge`   | 1 | 0.953         | 0.953       | 0.97     | session |
| `production deploy stays dev-only`       | 1 | 0.934         | 0.934       | 0.95     | session |
| `2026-05-12`                             | 1 | 0.881         | 0.881       | 0.9      | adr     |

- prior_prob (`KGC integration via API proxy bridge`): **0.88**
- evidence: 0 supporting · 2 contradicting
- posterior_prob: **0.602**
- **verdict**: `weak-consensus` — top answer favored but not safely settled

Recommended action:

- `2026-05-12` confidence 0.9 → 0.358
- `production deploy stays dev-only` confidence 0.95 → 0.378

The ADR-tagged `2026-05-12` gets discounted hardest in absolute terms because
it has the lowest decayed-confidence to start with. (Note: this particular
"contradiction" is actually a semantic-mismatch in the predicate — the ADR
recorded a *date*, and two session-rows recorded *what was decided*. The
ingest pipeline conflated two different attributes onto the same predicate.
That's the synonym problem described in the wiki.)

## Calibration sweep — all 1,115 contested pairs

```
$ vault-ko-belief --all-contested --json
```

| Verdict                | Count | Share  |
|------------------------|------:|-------:|
| `confident-consensus`  |     0 |   0.0% |
| `weak-consensus`       |   845 |  75.8% |
| `contested`            |   147 |  13.2% |
| `flip-recommended`     |   123 |  11.0% |
| **Total**              | 1,115 |        |

## Top-10 predicates contributing contested pairs

| Predicate        | Contested pairs |
|------------------|----------------:|
| `produces`       | 189             |
| `uses`           | 178             |
| `requires`       | 139             |
| `has_value`      | 116             |
| `applies_to`     |  87             |
| `avoids`         |  46             |
| `causes`         |  43             |
| `triggers`       |  33             |
| `allows`         |  32             |
| `depends_on`     |  32             |

## Unexpected findings

### 1. `confident-consensus` is mathematically unreachable in this KO-DB

All 1,115 contested pairs have **every candidate object backed by exactly
one fact**. There is not a single contested pair where two different
provenances assert the same `(subject, predicate, object)` triplet.
This means the *corroboration bonus* in the prior (`+0.06 × (n−1)`) is
never activated, so the prior caps out at 0.88 before evidence, and the
contradicting evidence then drags the posterior into `weak-consensus`
territory at best.

**Root cause is upstream**: the KO-DB ingest pipeline appears to
deduplicate by `hash(s, p, o, provenance)`, producing a fresh row each
time a different source mentions the same fact, rather than collapsing
into one row with a multi-source provenance list.

**Recommended fix** (for a future ingest sprint, not this skeleton):
hash on `(subject, predicate, normalize(object))` only, and store
`provenance` as a JSON array (or a separate `fact_provenance` table).
Until that change lands, the Bayesian update will over-weight the
loner-against-loner case relative to the "true consensus" cases the
brainstorm motivated.

### 2. 59.9 % of contested pairs are on intrinsically multi-valued predicates

Out of 1,115 contested pairs:

- **668** (59.9%) are on predicates from `vault-ko-conflicts-audit`'s
  `MULTI_VALUED_PREDICATES` set (`uses`, `produces`, `applies_to`,
  `has_value`, `depends_on`, …)
- 77 of those 668 get flagged `flip-recommended`

Most of these are not contradictions at all — they're tech-stack
enumerations (`kgc-berles uses_framework Next.js / React / Tailwind` —
all three are simultaneously true).

**Recommended skeleton-2 follow-up**: have `vault-ko-belief` short-circuit
on multi-valued predicates and emit a `multi-valued (skipped)` verdict
instead of running the math. The classifier set already lives in
`vault-ko-conflicts-audit`; we just need to share it.

### 3. The synonym pollution is concrete

`uses` vs `uses_framework` vs `uses_runtime` vs `uses_library` are
separate predicates in the typed-vocab, but the legacy fallback
`uses` still attracts 178 contested pairs. `vault-ko-normalize` exists
to clean these up but evidently hasn't been run since the typed-vocab
expansion landed.

## How to use

```
# Read-only, single pair:
vault-ko-belief --subject "X" --predicate "P"

# Read-only, by fact-hash:
vault-ko-belief --hash <fact-hash>

# From latest cross-source-conflicts-*.md audit:
vault-ko-belief --from-conflicts-audit

# Full scan (slow on the full 1,115-pair set, but tractable):
vault-ko-belief --all-contested --json

# Write back posterior-discounted confidences (double-gated):
VAULT_BELIEF_APPLY=1 vault-ko-belief --from-conflicts-audit --apply
```

## Open questions for next iteration

1. Should multi-valued predicates short-circuit, or should we just adjust
   the prior to start near 0.95 on them? Either works; short-circuit is
   simpler.
2. Once ingest is fixed (#1 above), should the corroboration_bonus
   become non-linear (e.g. `√n` instead of `n−1`) to avoid runaway
   priors on very-frequently-cited claims?
3. Wire `vault-ko-triangulate`'s NLI-proxy score as an extra LR
   multiplier for high-confidence supporting evidence. Currently
   `vault-ko-belief` doesn't call it because of the per-pair cost.

## Related

- [[../11-wiki/bayesian-belief-update-pattern.en|Bayesian belief-update pattern]] —
  the design rationale.
- `vault-ko-conflicts-audit` — what feeds the `--from-conflicts-audit` mode.
- `vault-ko-decay` — supplies the decayed-confidence used as cluster score.

---
name: Bayesian belief-update pattern
type: wiki
tags: ["#type/wiki", "vault-ko", "bayesian", "contradiction-resolution"]
created: 2026-05-19
updated: 2026-05-19
---

# Bayesian belief-update pattern

When two facts contradict in a knowledge-graph (e.g. `KGC = NestJS` vs
`KGC = Django`), the default resolution is usually one of:

1. **Newest-wins** — last writer overwrites. Wrong when the latest source
   is noisy and the older facts are an evergreen consensus.
2. **Highest-confidence-wins** — flips on a single high-conf typo.
3. **Manual triage** — doesn't scale beyond a few hundred conflicts.

A more disciplined option is to treat each fact as a Bayesian *observation*
and update a belief on the consensus answer. This page documents how
[`vault-ko-belief`](../06-Audits/2026-05-19%20Bayesian%20belief-update%20skeleton.md)
implements it on top of the KO-DB.

## The update

Per `(subject, predicate)` cluster:

1. Group the conflicting facts by their `object` value.
2. Pick the **consensus candidate**: the object cluster with the highest
   sum of *decayed* confidence (delegated to `vault-ko-decay`'s
   predicate-aware exponential decay).
3. Set the **prior**:

       prior = clamp(max_decayed_conf_of_top_cluster, 0.50, 0.88)
             + min(0.15, 0.06 × (n_facts_in_top_cluster − 1))
             # capped at 0.97

   The corroboration bonus expresses "multiple sources agreeing is itself
   evidence". A 4-source evergreen cluster starts at ≈ 0.94; a 1-source
   candidate starts at ≈ 0.85.

4. Apply each non-top observation as evidence:

   - **Same-object** (corroboration) → support LR ∈ [1.0, 3.0],
     scaled by `source_type` weight (`adr` = 2.0× , `wiki` = 1.6× ,
     `notebooklm` = 1.2× , `session` = 1.0× , `manual` = 0.8× ).
   - **Different-object** (contradiction) → contra LR ∈ [0.05, 0.99].
     Heavier sources push the LR closer to 0.5; weaker sources stay near 0.9.

5. `posterior_odds = prior_odds × Π LR`; convert to probability.

6. Verdict thresholds:

   | posterior_prob | verdict |
   |---|---|
   | ≥ 0.85 | `confident-consensus` |
   | 0.55 – 0.85 | `weak-consensus` |
   | 0.35 – 0.55 | `contested` |
   | < 0.35 | `flip-recommended` |

## Asymmetry is in the prior, not in the LR

A frequent design mistake is to bake the "single weak contradiction
shouldn't flip a 6-source claim" rule into the likelihood-ratio. Don't —
that's where calibration becomes ad-hoc and brittle. Instead:

- Keep LRs symmetric in their per-observation strength.
- Encode "established consensus is hard to dislodge" by **raising the
  prior** when the top cluster has many corroborating sources.
- This is exactly how a real Bayesian observer behaves: belief in a
  highly-corroborated claim only updates slowly because the prior is
  already saturated.

## Apply mode (loser-discount)

When `--apply` AND `VAULT_BELIEF_APPLY=1` are both set, the CLI **never
deletes** facts. Instead, it overwrites each losing fact's `confidence`
field with `base_confidence × (1 − posterior_prob)`. The fact stays in
the audit trail; queries that filter by `confidence ≥ τ` simply stop
returning it. Re-running the same update is idempotent within a 1% epsilon.

Every apply emits a JSONL line to
`06-Audits/vault-ko-belief-log.jsonl` for rollback.

## When the pattern under-performs

- **Multi-valued predicates** (`uses`, `requires`, `produces`,
  `applies_to`) almost always *should* have multiple objects coexisting.
  Treating them as contradictions yields a flood of false-positives.
  Mitigation: short-circuit on
  `predicate ∈ MULTI_VALUED_PREDICATES` and emit `multi-valued (skipped)`
  instead. Currently this list is owned by `vault-ko-conflicts-audit`.
- **No same-triplet corroboration** — if the ingest pipeline always
  produces unique `(s, p, o)` rows even when two sources say the same
  thing, the corroboration bonus is dead. KO-DB as of 2026-05-19 has
  exactly this property: 1,115 / 1,115 contested pairs have all unique
  objects. The fix is upstream — ingest should hash `(s, p, normalize(o))`
  so genuinely-duplicate facts collapse into one row with multi-source
  provenance.
- **Synonyms** (`uses` vs `requires`, `Next.js 16` vs `Next.js 16.2.3`)
  inflate contradictions. The `vault-ko-normalize` step exists for
  exactly this; running it before belief-update is encouraged.

## Related

- `vault-ko-conflicts-audit` — detects contradictions and classifies heat.
- `vault-ko-decay` — supplies the decayed-confidence used as cluster score.
- `vault-ko-triangulate` — NLI proxy score, complementary signal that
  could be folded into the LR in a future iteration.
- [Brainstorm #21](../06-Audits/2026-05-19%20SV%20new%20development%20ideas%20brainstorm.md)
  — original framing of the idea.

## Iteration ideas

- Mix triangulation-score into the LR for high-stakes pairs.
- Calibration: every week, sample 50 `flip-recommended` outputs, ask
  the user yes/no, compute precision; adjust thresholds toward that.
- Joint update across (subject, predicate) when predicates are
  semantically linked (HopRAG territory — brainstorm idea #11).

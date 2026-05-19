---
name: KO-DB hash key — drop provenance from hash
type: decision
status: 🟡 proposed (pending implementation Round 11+)
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/decision", "#project/sv", "sv-1", "ko-db", "schema-change"]
related:
  - "[[../11-wiki/append-only-jsonl-migration]]"
  - "[[../06-Audits/2026-05-19 mega-session summary]]"
---

# KO-DB hash key — drop provenance from hash

> [!info] Status: 🟡 PROPOSED
> Surfaced by the Round 8 Bayesian belief-update finding (vault-ko-belief).
> Implementation NOT done; this ADR documents the decision shape so it can
> be ratified + executed in a follow-up session.

## Context

The KO-DB `facts` table stores `(subject, predicate, object, provenance, confidence, ...)` with a `hash` column used for dedup at ingest time. The current hash recipe is:

```py
hash = sha256(f"{subject}|{predicate}|{object}|{provenance}").hexdigest()[:16]
```

This was chosen during the B-1 sprint to make ingestion idempotent at the file-level (re-running `vault-ko-ingest <file>` doesn't create duplicate triplets).

## The problem (Round 8 finding)

The Bayesian belief-update CLI (`vault-ko-belief`) ran on all 1,115 contested
`(subject, predicate)` pairs in the KO-DB and surfaced:

- **0 of 1,115 pairs reached `confident-consensus`** (the highest verdict)
- Root cause: with provenance in the hash, **two facts asserting the exact same (s, p, o) from two different files** become two distinct rows, NOT a single multi-source-corroborated fact.
- The Bayesian corroboration_bonus math is therefore **mathematically dead** — multi-source confirmation cannot accumulate.

Quote from the audit:

> 100% of contested pairs have all-unique objects — no two facts assert the same (s,p,o) triplet from different provenances. This makes the corroboration_bonus mathematically dead and `confident-consensus` unreachable.

## The decision (proposed)

Change the hash recipe to:

```py
hash = sha256(f"{subject}|{predicate}|{object}").hexdigest()[:16]
```

Provenance becomes a **multi-row attribute** of a `(subject, predicate, object)` triplet, NOT part of the dedup key.

### Schema change

Three options ordered by complexity:

#### Option A — provenance as JSON array (smallest delta)

```sql
ALTER TABLE facts ADD COLUMN provenances TEXT;  -- JSON array of strings
-- Backfill: GROUP BY (subject, predicate, object), aggregate provenances
-- Drop the old `provenance` column after backfill
```

Pros: 1 column change, easy to query (`json_each(provenances)`). Cons: SQLite JSON array operations are awkward for graph-walking.

#### Option B — separate provenance table (cleanest schema)

```sql
CREATE TABLE fact_provenance (
  fact_hash TEXT NOT NULL REFERENCES facts(hash) ON DELETE CASCADE,
  provenance TEXT NOT NULL,
  source_type TEXT,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (fact_hash, provenance)
);
-- 1-to-many: one fact row, multiple provenance rows
```

Pros: proper 3NF, easy to count distinct provenances. Cons: every fact-read needs a JOIN.

#### Option C — provenance-counter denormalized (perf-friendly)

Adopt Option B for the truth, AND keep a `provenance_count` integer on `facts` that's maintained by a trigger. The hot-path Bayesian-corroboration query becomes a single-row read.

### Recommended: **Option C** (B + counter)

The Bayesian belief-update query needs the count cheaply; full provenance list is needed only at audit time. The counter makes the hot-path query O(1) per fact, the full list is a JOIN for the rarer case.

## Migration plan

1. Add `provenance_count` INTEGER DEFAULT 1 to `facts`
2. Create `fact_provenance` table per Option B
3. Backfill: for each existing row, INSERT INTO `fact_provenance` (fact_hash, provenance, source_type, ingested_at) — keep all current rows for the history
4. Re-hash: compute new hash without provenance for each row, GROUP BY new-hash → DELETE all-but-first, set `provenance_count` to the GROUP count
5. Update `vault-ko-ingest` to use the new hash recipe + insert-or-update logic
6. Re-run `vault-ko-belief --all-contested` and verify `confident-consensus` becomes reachable

**ETA**: 2-3 hours including testing. The migration is REVERSIBLE (drop the `fact_provenance` table + restore the original hash) but loses the dedup-collapse history.

## Risks

- **Re-hash collisions** between previously-distinct rows: the GROUP BY will collapse them. Audit-log every collapsed row so the history is recoverable.
- **Downstream readers** of `provenance` column: enumerate via `grep -rE "facts\.provenance|f\.provenance"` before the migration; update each callsite.
- **vault-ko-conflicts-audit semantics**: the audit detects contradictions per `(subject, predicate)`. After the migration, a single row will represent multiple provenance-corroborated facts; the conflict definition stays the same.

## Verification gate

Post-migration, re-run `vault-ko-belief --all-contested --json`:

- Before: 0 `confident-consensus`, 845 `weak-consensus`, 147 `contested`, 123 `flip-recommended`
- Expected after: ~30-50% `confident-consensus` (corroboration math now works)

If the new distribution doesn't show meaningful `confident-consensus` count, the dedup logic has a bug — investigate before applying further changes.

## Status & next-step

🟡 **PROPOSED.** This ADR is the design doc. Implementation in Round 11 OR a dedicated follow-up session. Tagged in [[../04-Tasks/Backlog]] as 🔴 sürgős.

## Kapcsolódó

- [[../11-wiki/append-only-jsonl-migration]] — sibling migration discipline
- [[../06-Audits/2026-05-19 mega-session summary]] — Round 8 finding context
- [[2026-05-12 sv-5 crystallization automation arch]] — original KO-DB design where the hash recipe was chosen
- [[../11-wiki/temporal-kg-scd2-pattern]] — SCD2 layer adds another dimension; provenance change should compose with that

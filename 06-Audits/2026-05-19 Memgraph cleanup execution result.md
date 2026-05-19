---
name: 2026-05-19 Memgraph cleanup execution result
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/superintelligent-vault", "memgraph", "knowledge-graph", "cleanup", "execution"]
related:
  - "[[2026-05-19 Memgraph entity-cleanup analysis]]"
  - "[[../11-wiki/two-tier-graph-extraction]]"
  - "[[../11-wiki/mgclient-autocommit-silent-rollback]]"
status: executed — Tier-A + Tier-C complete, Jaccard target NOT met (gap-analysis included)
---

# Memgraph cleanup execution result (2026-05-19)

> [!success] Executed
> Tier-A hard-noise + Tier-C composite DELETE successfully applied per the Option-C two-phase plan from [[2026-05-19 Memgraph entity-cleanup analysis]]. Snapshot taken; rollback path verified.

## Summary

| Metric | Pre | Post | Delta |
|---|---:|---:|---:|
| `:Entity` total | 12,778 | **8,913** | **-3,865 (-30.2%)** |
| `:Literal` total | 12,160 | 12,160 | 0 |
| Edges total | 24,606 | **19,215** | -5,391 (-21.9%) |
| `source_count=1` | 6,537 (51%) | 3,102 (34.8%) | -3,435 |
| `source_count>=3` | 1,085 | 1,022 | -63 |
| `source_count=0/null` (typed-injected) | 3,803 | 3,523 | -280 |
| Distinct names | 12,778 | 8,913 | -3,865 |
| Tier-A shape residual (sanity-check) | 791+ | **0** | clean |

## Cleanup actions

### Phase 1 — Tier-A hard-noise DELETE
- **Pre-matched:** 791 entities (vs. audit estimate 797, well within tolerance — the audit used union-deduped count).
- **Deleted:** 791 (100% of matched, 2 batches: 500 + 291, elapsed 0.29 s).
- **Patterns hit:** quoted-string-start, hex-color, URL-fragment, too-short (<3 chars), starts_with_punct, looks_like_path, number_only, html-angle (`<>`), contains-equals-assign, arrow-operators (`->`/`=>`), shell-pipe, double-colon.

### Phase 2 — Tier-C composite DELETE
- **Filter:** `source_count = 1` AND (`>=3 tokens` OR any Tier-A shape).
- **Pre-matched:** 3,074 entities (audit estimate 3,310; the lower count is expected — Tier-A Phase 1 already removed ~250 overlap entities).
- **Deleted:** 3,074 (100% of matched, 7 batches × 500 + 74 + 0, elapsed 0.38 s).

**Total deleted: 3,865 entities, 5,391 edges.**

## Jaccard verification (Phase-4 acceptance gate)

| | tier1 | tier2 | both | t1_only | t2_only | Jaccard (agreement_rate) |
|---|---:|---:|---:|---:|---:|---:|
| Pre  | 12,631 | 4,439 | 119 | 12,512 | 4,320 | **0.0070** |
| Post | 8,806  | 4,439 | 102 | 8,704  | 4,337 | **0.0078** |

> [!warning] Acceptance gate NOT met
> Target was Jaccard ≥0.05 (Phase-4 acceptance). Achieved 0.0078 (+11% relative, +0.0008 absolute). **Cleanup alone is insufficient** — Option-C as designed in the analysis-audit anticipated this: Phase 2 prompt-tightening + selective re-extraction is the lasting fix. This run completes only the bulk-DELETE half.

### Why the gate didn't move

1. **Both ↓ (119 → 102):** 17 of the deleted entities were legitimate matches with graphify Tier-2. The Tier-C `>=3 token` heuristic over-pruned multi-word concepts that graphify also detected (e.g. multi-word skill names, file references). This is the expected false-positive rate of a shape-only filter.
2. **tier2_only ↑ (4,320 → 4,337):** Memgraph lost 17 entities that graphify still has — pure subtraction effect.
3. **The noise we deleted was almost entirely graphify-disjoint** — Tier-A/Tier-C entities are LLM-extracted artifacts that the tree-sitter/Leiden graphify pipeline never produces. So deleting them reduces tier1 denominator but barely lifts overlap numerator.
4. **The remaining gap is a vocabulary mismatch, not a noise problem** — graphify extracts code-symbol-style nodes (function names, file slugs), Memgraph extracts LLM-narrative nodes (concept phrases). Closing it requires either Option-B (re-extraction with tighter prompt) or entity-alignment (slug-normalization at diff-time), not more DELETE.

## Snapshot artifacts (rollback anchors)

| Artifact | Path | Size |
|---|---|---:|
| Memgraph DUMP (cypherl) | `/root/obsidian-vault/.vault-memory/snapshots/memgraph-pre-cleanup-2026-05-19.cypher` | 79.5 MB |
| facts.db backup | `/root/obsidian-vault/.vault-ko/snapshots/facts.db.pre-memgraph-cleanup-2026-05-19.bak` | 14.0 MB |
| Baseline stats JSON | `/root/obsidian-vault/.vault-memory/snapshots/baseline-stats-2026-05-19.json` | — |
| Baseline graph-diff JSON | `/root/obsidian-vault/.vault-memory/snapshots/baseline-graph-diff-2026-05-19.json` | — |
| Post-cleanup graph-diff JSON | `/root/obsidian-vault/.vault-memory/snapshots/post-cleanup-graph-diff-2026-05-19.json` | — |
| Sample-100 pre-cleanup | `/root/obsidian-vault/.vault-memory/snapshots/sample-100-pre-cleanup-2026-05-19.json` | — |
| Vault commit hash | `/root/obsidian-vault/.vault-memory/snapshots/vault-commit-pre-cleanup-2026-05-19.txt` | `c34fa932` |
| Audit-log (per-batch JSONL) | `/root/obsidian-vault/06-Audits/memgraph-cleanup-2026-05-19.jsonl` | — |

## Rollback (1-command)

```bash
# Full Memgraph restore from cypherl dump
docker exec -i vault-memgraph mgconsole < /root/obsidian-vault/.vault-memory/snapshots/memgraph-pre-cleanup-2026-05-19.cypher
```

If a clean reload is needed (recommended before restore to avoid duplicate vertices):

```bash
docker exec vault-memgraph bash -c "echo 'MATCH (n) DETACH DELETE n;' | mgconsole"
docker exec -i vault-memgraph mgconsole < /root/obsidian-vault/.vault-memory/snapshots/memgraph-pre-cleanup-2026-05-19.cypher
```

facts.db rollback:
```bash
cp /root/obsidian-vault/.vault-ko/snapshots/facts.db.pre-memgraph-cleanup-2026-05-19.bak /root/obsidian-vault/.vault-ko/facts.db
```

## Anomalies

1. **Jaccard moved by +0.0008 instead of the +0.043 target.** As detailed above, this is structural — bulk-DELETE shrinks the denominator but barely raises overlap because the two graphs cover orthogonal vocabularies. Phase-3 (Option-B re-extraction with tightened prompt rules 1-7) is now required to close the gap; the bulk-DELETE was only the cheaper, faster preamble. Escalation per the analysis-audit: if Phase-3 re-extraction also fails to reach 0.05, NotebookLM deep-research on entity-typing best-practices is the next step.

2. **17 valid `both`-set entities collateral-deleted (119 → 102, -14.3%).** The Tier-C `>=3 token` heuristic is too coarse for multi-word legitimate concepts. **Mitigation for future runs:** add a positive-keep filter (e.g. `n.max_confidence >= 0.8` OR `n.name` matches known-good prefixes from vault-index files) before the DELETE WHERE.

3. **Pre-match count drift (analysis-audit vs. execution).** Tier-A predicted 797 / executed 791 (-6); Tier-C predicted 3,310 / executed 3,074 (-236). Two contributing factors: (a) audit-analysis ran a few hours before cleanup, so the underlying graph may have shifted slightly via cron-driven `vault-ko-ingest`; (b) Phase-1 Tier-A removed ~250 entities that would have been counted in Phase-2's Tier-C union, so the sequential overlap explains the residual 236.

## Next steps (from analysis-audit roadmap)

- [ ] Patch `EXTRACTION_PROMPT_TEMPLATE` in `/root/obsidian-vault/.vault-ko/scripts/vault-ko-ingest.py` with rules 1–7 from the analysis-audit.
- [ ] Run `vault-ko-ingest --backfill` on `08-Sessions/` (the highest-noise domain).
- [ ] Re-run `vault-graph-diff --json` after re-extraction; target Jaccard ≥0.05 stretch ≥0.10.
- [ ] If Phase-3 succeeds, ratify prompt-rules into `00-Meta/graph-schema.yml` and promote `[[../11-wiki/llm-graph-noise-cleanup-composite-filter]]`.
- [ ] If Phase-3 fails, NotebookLM deep-research escalation.

## Audit log

Per-batch JSONL: `/root/obsidian-vault/06-Audits/memgraph-cleanup-2026-05-19.jsonl` (12 events: pre_count, batches, done, post_count for each phase).

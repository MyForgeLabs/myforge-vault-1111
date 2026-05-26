---
name: Memgraph cleanup Phase-3 next-step plan
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "memgraph", "extraction-quality"]
---

# Memgraph cleanup Phase-3 next-step plan

## Context

Phase-1 (Tier-A hard-DELETE 791 entity) + Phase-2 (Tier-C composite-DELETE 3,074 entity) executed 2026-05-19 12:50–13:05 UTC. Pre/post:

| Metric | Pre | Post | Δ |
|---|---:|---:|---|
| Entity | 12,778 | 8,913 | -30.2% |
| Edges | 24,606 | 19,215 | -21.9% |
| `source_count=1` | 6,537 (51%) | 3,102 (34.8%) | -52.5% |
| Tier-A shape residual | 791 | **0** | tisztított |
| Jaccard vs graphify | 0.0070 | 0.0078 | +0.0008 |

**Phase-4 acceptance gate (Jaccard ≥0.05) NEM teljesült.**

## Root cause

A két extraction-stack **ortogonális vocabulary-t** termel:

- **Memgraph (LLM Tier-1)**: szabadszöveg, koncept-szintű entitások (`"Hostinger MCP SSH key discovery"`, `"silent-rollback gotcha"`)
- **graphify (deterministic Tier-2)**: tree-sitter + Leiden, code-symbol-szintű (`def extract_facts`, `class FactExtractor`)

A noise-DELETE tisztította a Memgraph-noise-t, de NEM növelte az overlap-et, mert a két stack más rétegét beszéli.

## Phase-3 options (Jaccard ≥0.05 elérésére)

### Option A — Prompt-tightened selective re-extraction (recommended)
- Az új [[../11-wiki/vault-ko-ingest-prompt-tightening-2026-05-19]] 7-rule + 5-anti-noise-example prompt-tightening (vocab v3 ÉLES).
- Re-extract a 5,524 sentence-fragment-resistant entity-source-fájlt (sc≥1, ≥3 token a felesleges fragments-en).
- ETA: ~3-4h subagent-fanout (8× parallel), $0 cost.
- Várt: a sentence-fragment entitások visszaszorulnak code-symbol vagy named-concept szintre, ahol a graphify Tier-2 is felismeri őket.
- Várt Jaccard: 0.0078 → 0.03-0.06 (10-30% Phase-3 gain, függ a sentence-fragment-arány-tól a re-extract output-ban).

### Option B — Tree-sitter-aware extraction hibridizáció
- Adj hozzá `vault-ko-ingest`-hez egy graphify-style pre-pass-t code-block-okon: tree-sitter tokenize → symbol-extraction (def/class/function/import/const).
- Output: LLM-output ∪ tree-sitter-output → merge, dedup.
- ETA: ~1 nap design + ~2-3h impl + smoke-test.
- Várt Jaccard: 0.06-0.10 (közvetlen overlap növel mert mindkét stack ugyanazt látja code-blokkokban).
- **Risk**: code-block-only — wiki/markdown/ADR-tartalmon NEM segít.

### Option C — Mindkettő, sequential
- Option A először (gyors ROI), aztán Option B (struktural overlap-növelés).
- Acceptance: Jaccard ≥0.05 Option A után, ≥0.08 Option B után.
- ETA: ~1 nap + 1 nap.

## Recommendation

**Option C, ütemezett**:

1. **Most (2026-05-19 PM)**: A vocab v3 prompt-tightening ÉLES + #14 GitHub-bridge ÉLES → új ingest-ek **automatikusan** a tightened prompt-tal fognak menni. **Nincs explicit Phase-3 trigger ma**, csak a természetes write-throughput-on át hat.
2. **2026-05-22-23 (csütörtök-péntek)**: Selective re-extract a 5,524 sentence-fragment-source-fájlra (subagent-fanout, 8×). Jaccard re-measure.
3. **2026-06-02 körül**: Ha még nem teljesül Jaccard ≥0.05 → Option B tree-sitter pre-pass.

## Mitigations to consider

- **`max_confidence >= 0.8` keep-gate jövő Tier-C futtatáshoz** — a mostani over-pruning 17 valid `both`-match collateral-delete-t eredményezett. Jövő DELETE before, ezt szigorítsd: `WHERE n.source_count = 1 AND n.max_confidence < 0.8 AND (...token-cap...)`.
- **`source_count > 0 OR retype_label IS NOT NULL` keep-gate** — Tier-A pattern-matchen is alkalmazandó, hogy a 3,803 sc=0 typed-retype-injectee NEM lehessen mint Tier-A noise-pruned (jelenleg már így van, de explicit védelmi rule-ként rögzítve).

## Verification gate (Phase-4 re-run)

```bash
vault-graph-diff --json | jq '.jaccard'
# Target: >= 0.05 (Phase-4 acceptance)
# Stretch: >= 0.10 (Option B post-impl)
```

## Status

🟡 **planned for 2026-05-22-23** — non-blocking. A vocab v3 + #14 bridge new-ingest-ek természetes Jaccard-drift-et adnak, mérjük 1 hét múlva mielőtt explicit re-extract-ot futtatnánk.

## Related

- [[2026-05-19 Memgraph entity-cleanup analysis]] — Wave-1 analysis
- [[2026-05-19 Memgraph cleanup execution result]] — Phase-1+2 execution
- [[../11-wiki/two-tier-graph-extraction]] — pattern wiki, "2026-05-19 Jaccard 0.0070 finding" szakasz
- [[../07-Decisions/2026-05-19 KO-DB hash key — drop provenance from hash]] — sibling sprint ADR (#34, LANDED)

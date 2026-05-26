---
name: 2026-05-18 HN-posts ready-to-submit (7 EN wiki)
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "publishing", "hacker-news", "reddit", "twitter", "marketing", "myforge-vault-1111"]
supersedes: "[[2026-05-18 HN-post drafts (4 EN wiki)]]"
---

# Ready-to-submit HN + Reddit + Twitter drafts (7 EN wiki)

**Public repo:** `https://github.com/MyForgeLabs/myforge-vault-1111`
**Wiki site:** `https://myforgelabs.github.io/myforge-vault-1111/`
**Status:** 7 EN wikis polished, TL;DR strengthened, code-blocks validated, all URLs verified
**Cadence:** 1-2 wikis/week × 3 weeks (NOT all 7 same day — burnout + algorithm)

Supersedes earlier 4-wiki draft. New entries: HN-5, HN-6, HN-7.

---

## Index — 7 final HN-title + URL (quick reference)

| # | Wiki slug | HN-title (≤80 char) | URL |
|---|---|---|---|
| HN-1 | claude-code-subagent-fanout | Show HN: $0-cost bulk LLM mutation via Claude Code subagent-fanout | `https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/` |
| HN-2 | mgclient-autocommit-silent-rollback | 1262 DB writes silently rolled back — pymgclient autocommit pitfall | `https://myforgelabs.github.io/myforge-vault-1111/wiki/mgclient-autocommit-silent-rollback.en/` |
| HN-3 | g-eval-bias-mitigation-pattern | LLM-as-judge bias-mitigation is symmetric — we lost 47% Pass-recall | `https://myforgelabs.github.io/myforge-vault-1111/wiki/g-eval-bias-mitigation-pattern.en/` |
| HN-4 | memgraph-ce-feature-limits | Memgraph CE 3.9 native vector-index: 280× speedup, no Enterprise needed | `https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-ce-feature-limits.en/` |
| HN-5 | memgraph-multi-labeling-edge-case... | Typedness metric off by 12pp: multi-label SUM-counting trap (Cypher) | `https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-multi-labeling-edge-case-typedness-measurement.en/` |
| HN-6 | reranker-cost-optimization-not-size | Reranker speedup: smaller model gives 3.84× but sub-second on CPU is unreachable | `https://myforgelabs.github.io/myforge-vault-1111/wiki/reranker-cost-optimization-not-size.en/` |
| HN-7 | layered-eval-cascading-pattern | 4-layer LLM-eval pipeline at 2.7% of naive cost via cascading filter | `https://myforgelabs.github.io/myforge-vault-1111/wiki/layered-eval-cascading-pattern.en/` |

---

## A. Hacker News submission drafts (7 db)

### HN-1: subagent-fanout (PRIMARY — highest HN-fit)

```
Title: Show HN: $0-cost bulk LLM mutation via Claude Code subagent-fanout (267 files, 5 min)
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/
```

**Self-text (optional, 480 char):**
```
Pattern from 7 production iterations: 174 subagent calls, ~12,300 new triplets, $0 marginal cost (within Claude Code subscription, no API key). Sweet spot: 30 files/agent, 8 agents parallel, ~90 sec per agent. Covers what NOT to fanout (CPU-bound: bge-m3, Whisper, CLIP — model-loading dominates). Also: a subagent CANNOT spawn its own subagents — confirmed limit. Repo: github.com/MyForgeLabs/myforge-vault-1111 (MIT, 388 files).
```

---

### HN-2: mgclient autocommit silent-rollback

```
Title: 1262 DB writes silently rolled back — pymgclient autocommit pitfall (psycopg2 too)
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/mgclient-autocommit-silent-rollback.en/
```

**Self-text (optional, 420 char):**
```
Hit this in an 8997-entity bulk-typing batch: subagent reported "1262 entities typed", Memgraph showed 0 changes, no exception raised. Root cause: pymgclient.connect() defaults to explicit-transaction mode; conn.close() rolls back uncommitted work. One-line fix (conn.autocommit = True) jumped coverage 28.9% → 72.8%. Same default in psycopg2, mariadb, cx_Oracle, pyodbc. Detection pattern + driver audit-table included.
```

---

### HN-3: G-Eval bias-mitigation (LLM-as-judge)

```
Title: LLM-as-judge bias-mitigation is symmetric — we lost 47% Pass-recall fixing it
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/g-eval-bias-mitigation-pattern.en/
```

**Self-text (optional, 490 char):**
```
Built a 4-block bias-mitigation prompt (self-enhancement, verbosity, position, halo) for Claude-judges-Claude G-Eval. 10-sample paired: confidence 0.880 → 0.760, auto-prop 10/10 → 6/10. Looked great. 30-sample paired calibration revealed the catch: tightening is SYMMETRIC — Fail-confidence dropped -46%, but Pass-confidence dropped equally, killing 7/15 good bullets (47% Pass-recall loss). Ship as opt-in env-var, NOT default. The asymmetry signal is what most evals don't measure.
```

---

### HN-4: Memgraph CE native vector-index

```
Title: Memgraph CE 3.9 native vector-index: 1ms p50 / 2.6ms p95, 280× speedup, no Enterprise
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-ce-feature-limits.en/
```

**Self-text (optional, 420 char):**
```
Memgraph Community Edition shipped native vector-index in 3.9.0 — replaces our numpy-cosine workaround (280ms → 1ms mean). Multi-namespace works out-of-the-box (3 indexes × 2829/462/8997 nodes, zero interference). Also documents 4 CE gotchas: DDL/constraints inside transactions (hard-fail), multi-DB (Enterprise-only), MAGE algorithms (separate image). Pragmatic feature-matrix from a live entity-graph deployment.
```

---

### HN-5: Memgraph multi-labeling typedness trap (NEW)

```
Title: Cypher typedness metric off by 12pp: the multi-label SUM-counting trap
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-multi-labeling-edge-case-typedness-measurement.en/
```

**Self-text (optional, 460 char):**
```
Audit script reported "typedness 88.4%" on 8997 entities. Actual: 72.8%. Cause: SUM-of-(count(:Concept) + count(:Pattern) + count(:Skill)...) double-counts multi-label entities (a node tagged :Skill AND :Pattern adds +1 to both). 12pp inflation. Fix: count DISTINCT entities via size(labels(n)) > 1. Applies to Memgraph + Neo4j + any multi-label graph DB. Includes 5 correct metric queries + label-distribution gotcha (labels(n)[1] is unordered).
```

---

### HN-6: Reranker cost-optimization (NEW)

```
Title: Reranker speedup: smaller model gives 3.84× but sub-second on CPU is unreachable
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/reranker-cost-optimization-not-size.en/
```

**Self-text (optional, 470 char):**
```
A/B-tested bge-reranker-v2-m3 (568MB) vs base (277MB) for 30-candidate × 256-token rerank on CPU. Result: 3.84× speedup (20.9s → 5.4s), 80% top-3 overlap, but the <500ms interactive target is UNREACHABLE on any XLM-R-base on CPU (matmul-bound floor ~3-4s). Real cost map: trigger-rate optimization (-50%) + ONNX-INT8 (-50%) beats model-size reduction in absolute savings. Accept GPU/ColBERT for sub-second, or re-architect to top-3 cross-encoder.
```

---

### HN-7: Layered eval-cascading (NEW)

```
Title: 4-layer LLM-eval pipeline at 2.7% of naive cost via cascading filter
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/layered-eval-cascading-pattern.en/
```

**Self-text (optional, 480 char):**
```
Crystallization quality-gate stacks G-Eval (Layer 2) → NLI (2.5) → Coherence (2.6) → SelfCheckGPT (2.7). Naive: every bullet through every layer = 100 units. Cascading: each layer fires only on prior layer's positives. 10 bullets, 4 auto-prop, 1 borderline → 37 units = 2.7× savings; with 30% filter rate per layer, theoretical 30^3 = 2.7% of naive cost. Cheapest layer first, fail-open default, per-layer ENV-flag, 4-6 audit fields per layer. Production-verified.
```

---

## B. Twitter master-thread (7-wiki variant)

**Total char count: ~1740 (7 tweets, all under 280)**

**Tweet 1 — Hook (273 char):**
```
Open-sourced my personal Obsidian vault running on 3 AI agents in parallel: MyForge Vault 11.11 (MIT, 388 files).

7 production-debugged English wikis on Claude Code subagent-fanout, LLM-as-judge bias, Memgraph CE, reranker cost-opt, and eval-cascading.

Thread of 7 lessons 🧵
```

**Tweet 2 — subagent-fanout (270 char):**
```
1/ Claude Code subagent-fanout = $0-cost bulk LLM mutation.

7 iterations: 174 subagent calls, ~12,300 triplets, $0 marginal cost.
Sweet spot: 8 parallel × 30 files/agent × ~90s.

Don't fanout CPU-bound inference (bge-m3, Whisper) — model-load dominates.

myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/
```

**Tweet 3 — autocommit (266 char):**
```
2/ pymgclient silently rolled back 1262 writes — no exception, no error.

Default = explicit-transaction mode. conn.close() discards uncommitted.

One-line fix (conn.autocommit = True) jumped coverage 28.9% → 72.8%.

Same trap in psycopg2, mariadb, cx_Oracle, pyodbc.
```

**Tweet 4 — G-Eval bias (273 char):**
```
3/ LLM-as-judge bias-mitigation lost us 47% Pass-recall.

4-block prompt (self-enhancement, verbosity, position, halo): 10-sample looked great. 30-sample revealed the catch — tightening is SYMMETRIC. Fail-conf dropped, Pass-conf dropped equally, 7/15 good bullets killed.

Ship as opt-in, not default.
```

**Tweet 5 — Memgraph CE + multi-label (267 char):**
```
4/ Memgraph Community Edition 3.9 native vector-index: 280× speedup (280ms → 1ms p50). Multi-namespace works out-of-box.

5/ Bonus trap: Cypher typedness was off by 12pp because SUM-of-count(:Label) double-counts multi-label nodes. Fix: count(DISTINCT) via size(labels(n)) > 1.
```

**Tweet 6 — Reranker cost (264 char):**
```
6/ Reranker speedup: bge-reranker-base (277MB) is 3.84× faster than v2-m3 (568MB) at 80% top-3 overlap.

But <500ms on CPU? Unreachable. XLM-R-base + 30 candidates is matmul-bound at ~3-4s floor.

Better ROI: trigger-rate optimization (-50%) + ONNX-INT8 (-50%) ≫ model-size cut.
```

**Tweet 7 — Cascading eval + repo (270 char):**
```
7/ 4-layer LLM-eval pipeline at 2.7% of naive cost via cascading.

G-Eval → NLI → Coherence → SelfCheckGPT. Each layer only fires on prior layer's positives. 30% filter/layer → 30^3 = 2.7%.

All 7 wikis: github.com/MyForgeLabs/myforge-vault-1111

Karpathy LLM-Wiki layout + 11.11 session-orchestration.
```

---

## C. Reddit drafts (per-wiki target subreddit)

### Cross-post matrix — subreddit fit

| Wiki | Primary subreddit | Secondary | Avoid |
|---|---|---|---|
| HN-1 subagent-fanout | **/r/LocalLLaMA** | /r/ClaudeAI | /r/programming (too generic) |
| HN-2 mgclient autocommit | **/r/Python** | /r/programming | /r/database (low traffic) |
| HN-3 G-Eval bias | **/r/MachineLearning** | /r/LocalLLaMA | (none — niche) |
| HN-4 Memgraph CE | **/r/dataengineering** | /r/MachineLearning | /r/programming |
| HN-5 multi-label typedness | **/r/Cypher** + /r/dataengineering | /r/Neo4j | (small audience) |
| HN-6 reranker cost | **/r/LocalLLaMA** | /r/MachineLearning | (none) |
| HN-7 layered eval cascading | **/r/MachineLearning** | /r/LocalLLaMA | (none) |
| Repo announcement | **/r/Obsidian** | /r/selfhosted | (none) |

### B-1: /r/LocalLLaMA — subagent-fanout (PRIMARY)

Title: `$0-cost bulk LLM file mutation via Claude Code subagent-fanout — 267 files in 5 min, 7 production iterations`

Body: (kept from previous draft — full text in `[[2026-05-18 HN-post drafts (4 EN wiki)]]` §B-1)

### B-2: /r/Python — mgclient autocommit

Title: `pymgclient (and psycopg2, mariadb, cx_Oracle) silently rolls back if you forget autocommit — 1262 writes lost`

Body:
```
TL;DR: pymgclient.connect() defaults to explicit-transaction mode. If your code does INSERT/UPDATE/MERGE then conn.close() WITHOUT a conn.commit() — every write is silently rolled back. No exception. No warning. Same default in psycopg2, mariadb, cx_Oracle, pyodbc.

Hit this on a 8997-entity bulk-typing batch. Subagent log said "1262 entities typed". Memgraph said 0 typed. Half a day debugging.

One-line fix:
    conn.autocommit = True

Coverage jumped 28.9% → 72.8% on re-run.

Driver default table + detection pattern (mid-run COUNT-query before close):
https://myforgelabs.github.io/myforge-vault-1111/wiki/mgclient-autocommit-silent-rollback.en/

Is there a single Python DB driver where autocommit=True is the default? Genuinely curious; we couldn't find one.
```

### B-3: /r/MachineLearning — G-Eval bias

Title: `[D] LLM-as-judge bias-mitigation is symmetric, not asymmetric — we lost 47% Pass-recall fixing self-enhancement bias`

Body: (full version in master-MD §A HN-3, expanded with 30-sample table + opt-in env-var rationale)

### B-4: /r/MachineLearning — Layered eval cascading

Title: `[P] 4-layer LLM-eval pipeline at 2.7% of naive cost: cascading filter pattern (G-Eval → NLI → Coherence → SelfCheck)`

Body:
```
Built a quality-gate cascade for crystallization workflow that stacks 4 evaluators (each more expensive than the last) WITHOUT running them on every bullet.

Pattern:
- Layer 2 (G-Eval, 1× subagent) fires on every bullet
- Layer 2.5 (NLI DeBERTa-440MB) fires ONLY on auto-prop candidates from Layer 2
- Layer 2.6 (Coherence — 5× NLI vs neighbours) ONLY on Layer 2.5 entail/neutral
- Layer 2.7 (SelfCheckGPT, 3× G-Eval) ONLY on borderline 0.70-0.85 from Layer 2.6

Cost math: 10 bullets, 4 auto-prop, 1 borderline → 37 units vs naive 100 = 2.7× savings.

Theoretical with 30% per-layer filter: 30^3 = 2.7% of naive cost.

Design rules: cheapest layer first, fail-open default, per-layer ENV-flag, 4-6 audit fields per layer.

Live (verified 2026-05-17): https://myforgelabs.github.io/myforge-vault-1111/wiki/layered-eval-cascading-pattern.en/

Does anyone here ship cascading LLM-judges in production? Curious what filter rate you see on Layer 1 vs Layer N.
```

### B-5: /r/LocalLLaMA — Reranker cost

Title: `Reranker model-size reduction gives 3.84× but sub-second on CPU is unreachable — the real cost knobs are trigger-rate + ONNX-INT8`

Body:
```
A/B tested bge-reranker-v2-m3 (568MB) vs bge-reranker-base (277MB) on a 30-candidate × 256-token CPU rerank:

| Metric          | v2-m3  | base   |
|-----------------|--------|--------|
| Warm wall-clock | 20.9s  | 5.4s   |  ← 3.84×
| rerank_ms       | 20.7s  | 5.2s   |  ← 3.97×
| Top-3 overlap   |  —     | 80%    |
| RAM peak (both) | 4.5GB  | 5.0GB  |
| Cold load       | 24s    | 17.7s  |

Verdict: shipped as `--reranker-model base` opt-in, NOT default (10-15% precision loss on noisy top-3).

But the bigger lesson: <500ms on CPU with XLM-R-base + 30 candidates is fundamentally unreachable. Matmul-bound floor ~3-4s. The real cost knobs:

- Trigger-rate (cosine < 0.65 skip + score-gap smart-skip) → -50-80%
- ONNX-INT8 quantization → -50% additional
- Query-cache LRU 5min → -50% on repeat queries
- Top-K reduction (50→30) → -40%

Multiply: 0.5 × 0.5 × 0.6 = 15% of original cost, BEFORE touching model size.

Full cost map + when to opt-in: https://myforgelabs.github.io/myforge-vault-1111/wiki/reranker-cost-optimization-not-size.en/
```

### B-6: /r/dataengineering — Memgraph multi-label typedness

Title: `Cypher typedness metric off by 12pp — the multi-label SUM-counting trap (Memgraph + Neo4j)`

Body:
```
Audit script reported typedness 88.4% on 8997-entity graph. Actual: 72.8%.

Bug:
    MATCH (n:Concept) RETURN count(n);   // 3349
    MATCH (n:Pattern) RETURN count(n);   //  948
    MATCH (n:Skill)   RETURN count(n);   // 2480
    ...
    SUM = 7750. 7750/8997 = 86.1%. WRONG.

A node tagged :Skill AND :Pattern adds +1 to BOTH counts. Multi-label overlap inflates the sum.

Fix (DISTINCT-based):
    MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n);
    // 6547. 6547/8997 = 72.8%. CORRECT.

Bonus traps:
- labels(n)[1] is NOT a stable "first non-Entity label" — array order is storage-internal
- "Label distribution" pie charts: each label column counts DISTINCT entities; SUM-of-columns ≠ entity count by design (show "% multi-label" row)
- Vector-search label-filter must use `'Concept' IN labels(n)` NOT `node.label = 'Concept'`

Reusable rule set + 5 correct metric queries:
https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-multi-labeling-edge-case-typedness-measurement.en/
```

### B-7: /r/Obsidian — repo announcement (existing B-2)

(kept from previous draft, see superseded doc)

---

## D. Best-time UTC matrix (frozen, 7-wiki updated)

| Channel | Best window (UTC) | Reasoning | Posts to schedule |
|---|---|---|---|
| Hacker News | **Tue-Thu 14:00-16:00 UTC** | Front-page-eligible before US wakes, EU still active | HN-1 to HN-7 (1/wk) |
| /r/LocalLLaMA | **Wed-Thu 15:00-18:00 UTC** | US lunch + EU evening, weekday non-Friday | B-1, B-5 |
| /r/MachineLearning | **Sun 17:00-19:00 UTC** OR Tue 15:00 | Weekend "I made this" wave + weekday "lessons learned" | B-3, B-4 |
| /r/Python | **Tue-Wed 15:00 UTC** | US morning, EU afternoon | B-2 |
| /r/dataengineering | **Wed 14:00-16:00 UTC** | Mid-week engineering crowd, US morning | B-6 |
| /r/Obsidian | **Sat-Sun 14:00-17:00 UTC** | Weekend hobbyist crowd | B-7 (repo) |
| Twitter/X | **Tue-Thu 13:00 UTC** (= 9am ET) | Algorithmic + US morning | Master thread |
| dev.to | **Mon-Thu 13:00-15:00 UTC** | Algorithmic feed, not time-sensitive | Anytime |

---

## E. Submission cadence — 3-week rolling schedule

```
Week 1 (2026-05-19 → 25) — open with strongest
  Tue 2026-05-19  14:00 UTC → HN-1 subagent-fanout (PRIMARY)
  Wed 2026-05-20  15:00 UTC → /r/LocalLLaMA B-1 (subagent-fanout deep-dive)
  Thu 2026-05-21  13:00 UTC → Twitter master thread (7-tweet)
  Sun 2026-05-24  17:00 UTC → /r/MachineLearning B-4 (layered eval cascading)

Week 2 (2026-05-26 → 06-01) — DB-gotcha + ML pairing
  Tue 2026-05-26  14:00 UTC → HN-2 mgclient autocommit
  Wed 2026-05-27  15:00 UTC → /r/Python B-2 (mgclient)
  Thu 2026-05-28  14:00 UTC → HN-7 layered eval cascading
  Sun 2026-05-31  17:00 UTC → /r/MachineLearning B-3 (G-Eval bias)

Week 3 (2026-06-02 → 08) — graph-DB block + closer
  Tue 2026-06-02  14:00 UTC → HN-3 G-Eval bias (if W2 ML got traction)
  Wed 2026-06-03  14:00 UTC → HN-5 multi-label typedness
  Wed 2026-06-03  16:00 UTC → /r/dataengineering B-6 (multi-label)
  Thu 2026-06-04  14:00 UTC → HN-6 reranker cost-opt
  Thu 2026-06-04  16:00 UTC → /r/LocalLLaMA B-5 (reranker)
  Sat 2026-06-07  15:00 UTC → /r/Obsidian B-7 (repo announcement)

Week 4 (held in reserve, only if Week-1-3 traction)
  Tue 2026-06-09  14:00 UTC → HN-4 Memgraph CE (weakest, hold unless prior posts trended)
```

**Rules:**
1. Never submit 2 HN posts same day (algorithm flags as spam).
2. Never submit same wiki to HN within 7 days of Reddit (front-page wave should NOT cannibalize).
3. If HN-1 hits front-page (>50 points): pause Week-2 HN until comments settle (~24h).
4. If HN-1 flops (<5 points after 4h): switch HN-2 → "Tell HN" format (less Show-HN-fatigue).

---

## F. Expected reach (honest estimates, 7-wiki updated)

| Wiki | HN front-page p(reach) | HN top-10 p(reach) | Reddit comments (median) | Twitter views (organic) |
|---|---|---|---|---|
| HN-1 subagent-fanout | **15-25%** | 5-10% | 20-50 | 500-2000 |
| HN-2 mgclient autocommit | 10-15% | 3-7% | 10-30 | 300-800 |
| HN-3 G-Eval bias | 8-12% | 2-5% | 5-20 | 200-600 |
| HN-4 Memgraph CE | 5-10% | 1-3% | 5-15 | 200-500 |
| HN-5 multi-label typedness | **12-18%** | 3-6% | 10-25 | 300-700 |
| HN-6 reranker cost | **10-15%** | 3-6% | 15-35 | 400-1000 |
| HN-7 layered eval cascading | 8-12% | 2-5% | 8-20 | 300-700 |

**Ranking — strongest HN-fits (updated):**
1. **HN-1 subagent-fanout** — concrete dollar number, generalizable, Show-HN format
2. **HN-5 multi-label typedness** — classic "X silently wrong" HN-trope + Cypher generalizes to Neo4j
3. **HN-2 mgclient autocommit** — broadly applicable beyond Memgraph, one-line-fix punchline
4. **HN-6 reranker cost** — contrarian-result hook ("smaller model isn't the answer")
5. **HN-3 G-Eval bias** — niche, but 47%-recall-loss honesty signal works
6. **HN-7 layered eval cascading** — strong number (2.7% of naive), niche audience
7. **HN-4 Memgraph CE** — weakest standalone, vendor-specific

---

## G. dev.to master post (1, can be reposted)

(unchanged from previous draft — full content `[[2026-05-18 HN-post drafts (4 EN wiki)]]` §C)

Recommendation: ship dev.to repost of HN-1 + HN-7 only (cascading-pattern dev.to-formatted reads well; reranker A/B is also good).

---

## H. Master-MD path

This document: `/root/obsidian-vault/06-Audits/2026-05-18 HN-posts ready-to-submit (7 EN wiki).md`

Supersedes: `[[2026-05-18 HN-post drafts (4 EN wiki)]]`

---

## Related

- [[../11-wiki/claude-code-subagent-fanout.en]]
- [[../11-wiki/mgclient-autocommit-silent-rollback.en]]
- [[../11-wiki/g-eval-bias-mitigation-pattern.en]]
- [[../11-wiki/memgraph-ce-feature-limits.en]]
- [[../11-wiki/memgraph-multi-labeling-edge-case-typedness-measurement.en]]
- [[../11-wiki/reranker-cost-optimization-not-size.en]]
- [[../11-wiki/layered-eval-cascading-pattern.en]]
- [[2026-05-18 HN-post drafts (4 EN wiki)]] — superseded
- [[2026-05-18 Twitter thread draft (master)]]

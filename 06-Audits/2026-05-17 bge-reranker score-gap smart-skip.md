---
name: B-2 Week 5 bge-reranker score-gap smart-skip audit
type: audit
tags: ["#type/audit", "#project/sv", "sv-2", "reranker", "smart-trigger", "score-gap", "retrieval", "latency-mitigation"]
created: 2026-05-17
updated: 2026-05-17
project: [[02-Projects/superintelligent-vault]]
adr: [[07-Decisions/2026-05-12 sv-1 memory architecture arch]]
wiki: [[11-wiki/sv-01-memory-architecture]]
sprint: B-2 Week 5
parent: [[2026-05-17 B-2 reranker smart-trigger]]
related:
  - "[[06-Audits/2026-05-17 B-2 reranker smart-trigger]]"
  - "[[06-Audits/2026-05-17 B-2 Week 4 bge-reranker-base AB]]"
  - "[[06-Audits/2026-05-17 B-2 bge-reranker 2-pass retrieval]]"
---

# B-2 Week 5 — bge-reranker score-gap smart-skip

## TL;DR

A Week 4 smart-trigger (abszolút `max_cos < 0.65` küszöb) második rétegét beépítettük: **score-gap smart-skip**. Ha a `top-1` cosine **nagyon** kiemelkedik a `top-2`-höz képest (clear winner — pl. 0.85 vs 0.55, gap=0.30), a head egyértelmű és a reranker nem tud értelmesen átrendezni → SKIP, **akkor is**, ha a top-1 abszolút cos a trigger-threshold alatt van.

**Combined gate:**

```
should_rerank ⇔ (max_cos < trigger_threshold) AND (top1 - top2 < score_gap_threshold)
```

Két független SKIP-csatorna:
- `skip_reason="confident"` — abszolút (top-1 ≥ 0.65)
- `skip_reason="score-gap"` — relatív (top1 - top2 > gap, head unambiguous)

**Bench (5-query × 3 mód × 3 repeat warm-daemon, EPYC 9354P CPU-only):**

| mód | mean | rerank-rate | skip-csatornák |
|---|---:|---:|---|
| pure-cosine | **190 ms** | 0/5 (0%) | n/a |
| smart-legacy (Week 4) | **13 416 ms** | 3/5 (60%) | confident: 2 / triggered: 3 |
| **smart + gap=0.10** (audit-prompt default) | **12 786 ms** | 3/5 (60%) | confident: 2 / triggered: 3 / score-gap: **0** |
| **smart + gap=0.04** (kalibrált) | **4 544 ms** | 1/5 (20%) | confident: 2 / score-gap: **2** / triggered: 1 |

**Találat:** A javasolt `0.10`-es default-érték a current 5-query disztribúción **NEM csökkenti** a trigger-rate-et — minden trigger-query gap-je `<0.07` (clusteres head). A **valódi sweet spot** a `0.02-0.04` tartomány, ami **66% latency-reduction**-t hoz (13.3s → 4.5s mean), **nem 30-40%-ot** ahogy a prompt becsülte. Lényegesen jobb, mint vártuk — de csak alacsony küszöbbel.

**Cost-savings:** smart-legacy `13.4s` → smart+gap=0.04 `4.5s` → **66% reduction, 2.95× speedup**. RAM-cost: **0** (numpy subtract, sub-µs).

## Architektúra

### Combined gate (server-side)

`/usr/local/bin/vault-search-server` (Handler.handle, `method=search`):

```python
candidates = STORE.search(q_vec, first_pass_k, ns, return_full_text=True)
max_cos  = candidates[0]["score"] if candidates else 0.0
score_gap = max_cos - candidates[1]["score"] if len(candidates) >= 2 else float("inf")

should_rerank = True
skip_reason   = None
if smart_rerank and not rerank:
    if max_cos >= trigger_threshold:
        should_rerank = False
        skip_reason   = "confident"             # (a) absolute channel
    elif score_gap_threshold > 0.0 and score_gap > score_gap_threshold:
        should_rerank = False
        skip_reason   = "score-gap"             # (b) relative channel
```

A két csatorna **disjunkció** (egyik elég a SKIP-hez). A trigger-channel-t (`max_cos < trigger`) **AND**-eli a gap-channel-lel (`gap < gap_thr`) — vagyis trigger-eléshez **mindkét** feltétel kell.

### Response-mezők

Új mezők a `smart-rerank-{triggered,skipped}` response-okban:

| Field | Skip eset | Trigger eset |
|---|---|---|
| `mode` | `smart-rerank-skipped` | `smart-rerank-triggered` |
| `skip_reason` | `"confident"` v. `"score-gap"` | (nincs) |
| `first_pass_max_score` | top-1 cos | top-1 cos |
| `first_pass_score_gap` | top-1 - top-2 | top-1 - top-2 |
| `trigger_threshold` | (echo) | (echo) |
| `score_gap_threshold` | (echo) | (echo) |
| `rerank_ms` | 0.0 | tényleges |

### Wire protocol (daemon)

Request:
```json
{"method":"search","query":"...","top_k":5,"namespace":"content",
 "smart_rerank":true,"trigger_threshold":0.65,"score_gap_threshold":0.04}
```

Response (gap-skip):
```json
{"results":[...],"mode":"smart-rerank-skipped","skip_reason":"score-gap",
 "first_pass_k":30,"first_pass_max_score":0.6181,"first_pass_score_gap":0.0551,
 "rerank_triggered":false,"trigger_threshold":0.65,
 "score_gap_threshold":0.04,"rerank_ms":0.0}
```

Response (confidence-skip):
```json
{"results":[...],"mode":"smart-rerank-skipped","skip_reason":"confident",
 "first_pass_k":30,"first_pass_max_score":0.7261,"first_pass_score_gap":0.0616,
 "rerank_triggered":false,"trigger_threshold":0.65,
 "score_gap_threshold":0.04,"rerank_ms":0.0}
```

### CLI (`vault-search`)

- Új flag: **`--score-gap-threshold <float>`** (default `0.0` → backward-compat OFF)
- Új env: `RERANK_SCORE_GAP_THRESHOLD` (default `0.0`)
- A native + legacy in-process paths is megkapja a `_apply_smart_rerank_local()`-on keresztül
- Diagnostic output bővítve: `gap=0.0551` + `skip reason: score-gap` az emberi módú banner-ben

Backup: `vault-search.py.bak.20260517-score-gap` + `vault-search-server.bak.20260517-score-gap`.

## Bench — 5 query × 3 mód × 3 repeat (warm daemon)

EPYC 9354P, CPU-only, sentence-transformers 5.1.2, bge-m3 warm, bge-reranker-v2-m3 warm.
Median of 3 warm runs per cell.

### Mode A — pure-cosine (`--mode cosine`)

| Query | top-1 cos | gap | median ms | decision |
|---|---:|---:|---:|---|
| robbantott-kereso OCR pipeline | n/a | n/a | 235 | skip (no smart) |
| Memgraph CE feature-limits | n/a | n/a | 189 | skip (no smart) |
| subagent fanout pattern | n/a | n/a | 174 | skip (no smart) |
| session-pointer per-chat isolation | n/a | n/a | 181 | skip (no smart) |
| nano-banana ultra-wide stitching | n/a | n/a | 172 | skip (no smart) |
| **mean** | — | — | **190** | **0/5 rerank** |

### Mode B — smart-legacy (Week 4 default; `--score-gap-threshold 0.0`)

| Query | top-1 cos | gap | median ms | decision |
|---|---:|---:|---:|---|
| robbantott-kereso OCR pipeline | 0.6181 | 0.0551 | 21 807 | **RERANK** (cos<0.65) |
| Memgraph CE feature-limits | 0.5999 | 0.0053 | 23 363 | **RERANK** (cos<0.65) |
| subagent fanout pattern | 0.6301 | 0.0460 | 21 557 | **RERANK** (cos<0.65) |
| session-pointer per-chat isolation | 0.6675 | 0.0103 | 171 | SKIP (confident) |
| nano-banana ultra-wide stitching | 0.7261 | 0.0616 | 181 | SKIP (confident) |
| **mean** | — | — | **13 416** | **3/5 rerank (60%)** |

### Mode C — smart + gap=0.10 (audit-prompt default)

| Query | top-1 cos | gap | median ms | decision |
|---|---:|---:|---:|---|
| robbantott-kereso OCR pipeline | 0.6181 | 0.0551 | 21 335 | **RERANK** (gap<0.10) |
| Memgraph CE feature-limits | 0.5999 | 0.0053 | 21 278 | **RERANK** (gap<0.10) |
| subagent fanout pattern | 0.6301 | 0.0460 | 20 952 | **RERANK** (gap<0.10) |
| session-pointer per-chat isolation | 0.6675 | 0.0103 | 187 | SKIP (confident) |
| nano-banana ultra-wide stitching | 0.7261 | 0.0616 | 178 | SKIP (confident) |
| **mean** | — | — | **12 786** | **3/5 rerank (60%)** |

**Megjegyzés:** A `0.10`-es küszöb ezen a query-szeten **0 extra skip-et** hoz, mert a trigger-eseteken a gap mind `<0.07`. A small ~600ms átlag-csökkenés mérési zaj, nem valós effekt.

### Sweep — score-gap threshold sensitivity (1 run/cell)

A 0.10-es default nem skipped a current trigger-querykben — küszöb-sweep:

| gap_thr | rerank_n | mean ms | Q1 robbantott | Q2 memgraph | Q3 subagent | Q4 session | Q5 nano |
|---:|---:|---:|---|---|---|---|---|
| 0.00 | 3 | 13 294 | R | R | R | S(c) | S(c) |
| **0.01** | **1** | **4 865** | **S(s)** | R | **S(s)** | S(c) | S(c) |
| **0.02** | **1** | **4 425** | **S(s)** | R | **S(s)** | S(c) | S(c) |
| **0.04** | **1** | **4 544** | **S(s)** | R | **S(s)** | S(c) | S(c) |
| 0.05 | 2 | 10 014 | S(s) | R | R | S(c) | S(c) |
| 0.06 | 3 | 12 703 | R | R | R | S(c) | S(c) |
| 0.07 | 3 | 12 897 | R | R | R | S(c) | S(c) |
| 0.10 | 3 | 12 519 | R | R | R | S(c) | S(c) |
| 0.15 | 3 | 12 921 | R | R | R | S(c) | S(c) |

(R=rerank, S(c)=skip confident, S(s)=skip score-gap)

**Plateau-pontok:**
- `gap ≤ 0.04` → 1/5 trigger, ~4.5s mean
- `gap = 0.05` → 2/5 trigger, ~10s mean
- `gap ≥ 0.06` → 3/5 trigger, ~13s mean (= baseline)

A `gap=0.04` **2.95× speedup** vs smart-legacy; a `gap=0.10` (prompt-default) effektíven `1.05× speedup` ezen az 5-query mintán.

## Vs várt cost-savings

- **Prompt-becslés:** smart-legacy 8.3s → score-gap-smart-legacy ~5s, **40% reduction**, **30% kevesebb trigger** a 0.10-es küszöbnél.
- **Valós:** a 0.10 ezen a query-szeten **0% extra skip**-et hoz. A 0.04 viszont **2× extra skip**-et (60% → 20% rerank-rate), és **66% latency-reduction**-t (13.4s → 4.5s).
- **Konklúzió:** a prompt-becslés iránya helyes (a score-gap valóban hoz reduction-t), de a **küszöb-érték drasztikusan eltér** a Week 3-as cosine-disztribúciótól. A current trigger-eseteken a top1-top2 gap **<0.07**, ami azt jelzi, hogy a top-1 önmagában nem dominál — a head clusteres, és pont ezért adja vissza a reranker a precision-lift-et.

## Per-query interpretáció

**Q1 `robbantott-kereso OCR pipeline`** — cos=0.618, gap=0.055.
- `0.10`-es default: trigger (gap<0.10). NO change vs legacy.
- `0.04`-es kalibrált: **score-gap skip** (gap>0.04). Compromise: a Week 3 audit szerint itt a CE 3 új releváns chunk-ot hozott. **Skip ezt elveszti**, de 21s → 0.2s (100× speedup).

**Q2 `Memgraph CE feature-limits`** — cos=0.600, gap=0.005.
- Akár 0.10, akár 0.04 → trigger. Helyes — a head tight (gap 0.005), a top-1 nem dominál.
- Ez a query Week 3 audit szerint marginal regression-t kap a CE-től; sem a 0.04-es, sem a 0.10-es gap-küszöb nem javít rajta. **Hybrid BM25 fallback szükséges** (B-2 Week 4 hybrid pipeline-on már megoldva).

**Q3 `subagent fanout pattern`** — cos=0.630, gap=0.046.
- `0.10`-es default: trigger (gap<0.10).
- `0.04`-es kalibrált: **score-gap skip** (gap>0.04, picit). A trigger ide Week 3 szerint precision-gain volt, ami skip-pel elvész. **Compromise**.

**Q4 + Q5** — cos > 0.66, mindig confidence-skip-elt, irreleváns a score-gap szempontjából.

**Tanulság:** a 0.04-es gap két query-t (`Q1`, `Q3`) is megfoszt a Week 3 precision-gain-től. Az interaktivitás-vs-precision tradeoff itt élesebb, mint a Week 4 abszolút-küszöbnél. **Production-be opt-in javasolt, nem default-shift.**

## Acceptance gate-felülvizsgálat

| Cél | Mérés | Státusz |
|---|---|---|
| `--score-gap-threshold` flag élesítve | `vault-search --score-gap-threshold 0.04 "..."` | ✅ |
| Daemon RPC `score_gap_threshold` mező | `echo '{"method":"search","score_gap_threshold":0.04,...}' \| nc -U` | ✅ |
| Combined logic helyes | trigger ⇔ (cos<trig) ∧ (gap<gap-thr); confirmed Q1 + Q2 viselkedéssel | ✅ |
| Default OFF (backward-compat) | `RERANK_SCORE_GAP_THRESHOLD=0.0` → 100% identical smart-legacy viselkedés | ✅ |
| Bench skip-rate (várt 30-40% reduction) | 0.10-en 0%; 0.04-en **66%** (lényegesen jobb) | ✅ (érték eltér a vártól) |
| NO RAM cost | `numpy.subtract`-szintű, sub-µs | ✅ |
| Health-RPC tartalmazza | `"rerank_score_gap_threshold": 0.0` | ✅ |

## Risks / Open issues

1. **Default-érték `0.10` túl konzervatív** a current query-disztribúción → ZERO effekt. Real-workload sweep (Week 6) szükséges a production default-hoz. Javaslat: **opt-in, nem default-shift**, env-var `RERANK_SCORE_GAP_THRESHOLD=0.04` aki kipróbálja.
2. **Precision-loss a Q1+Q3 query-n** a `0.04`-es küszöbbel — Week 3 audit szerint mindkét helyen value-add volt a CE. Eseti kompromisszum (NDCG@5 mérés Week 6-ban).
3. **Mintaméret 5 query** — túl kicsi a robosztus küszöb-választáshoz. 30-sample real workload-on calibration kötelező a prod-default előtt (Week 6).
4. **Confounded score-gap interpretáció:** alacsony gap = "tight cluster, rerank kell" ÉS "egyik sem dominál abszolút értelemben" is lehet. Egy szebb metrika: `softmax(top-5).entropy()` vagy `(top-1 - top-5) / std(top-5)`.

## Calibration recommendations (Week 6)

| Lépés | Mit | Várt eredmény |
|---|---|---|
| 1 | 30-sample real-workload query collection (vault-search hot-queries + manuálisan rakott edge-case-ek) | per-query cos + gap distribúció |
| 2 | A/B sweep `gap ∈ {0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15}` mindegyiken | latency × NDCG@5 trade-off matrix |
| 3 | Pareto-frontier kalkuláció (mean latency vs NDCG@5 loss) | optimális (trigger, gap) páros |
| 4 | Production default-shift, ha NDCG@5 loss <5% ÉS latency reduction >40% | env-var `RERANK_SCORE_GAP_THRESHOLD=<x>` |
| 5 | Heti `vault-crystallize-monitor`-szerű audit a trigger/skip distribution-ra (drift detection) | rolling tune |

## Reproduce

```bash
# Default OFF (backward-compat, identical Week 4 smart-rerank)
vault-search "robbantott-kereso OCR pipeline"

# Score-gap enable
vault-search --score-gap-threshold 0.04 "robbantott-kereso OCR pipeline"
# → mode: smart-rerank-skipped, skip_reason: score-gap, gap=0.055

# Env-style
RERANK_SCORE_GAP_THRESHOLD=0.04 vault-search "robbantott-kereso OCR pipeline"

# Daemon RPC
echo '{"method":"search","query":"...","top_k":5,
 "smart_rerank":true,"trigger_threshold":0.65,"score_gap_threshold":0.04}' \
 | nc -U /run/vault-search.sock

# Health check (mostantól rerank_score_gap_threshold mezővel)
echo '{"method":"health"}' | nc -U /run/vault-search.sock

# Bench reproduce
/tmp/score_gap_bench.py        # 5q × 3m × 3r = 45 runs
/tmp/score_gap_sweep.py        # threshold sensitivity
```

Raw bench: `/tmp/score_gap_bench_result.json` + `/tmp/score_gap_sweep_result.json`.
Logs: `/tmp/score_gap_bench.log` + `/tmp/score_gap_sweep.log`.

## Kapcsolódó

- [[2026-05-17 B-2 reranker smart-trigger]] — parent (abszolút trigger-threshold)
- [[2026-05-17 B-2 Week 4 bge-reranker-base AB]] — alternatív mitigation (kisebb model)
- [[2026-05-17 B-2 bge-reranker 2-pass retrieval]] — original 2-pass design
- [[2026-05-17 B-2 Week 4 hybrid BM25 + semantic]] — magyar ritka-substring komplemmenter mitigation
- [[../11-wiki/reranker-cost-optimization-not-size]] — wiki — model-size NEM az egyetlen lever

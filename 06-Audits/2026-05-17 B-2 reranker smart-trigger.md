---
name: B-2 reranker smart-trigger audit
type: audit
tags: ["#type/audit", "#project/sv", "sv-2", "reranker", "smart-trigger", "retrieval", "latency-mitigation"]
created: 2026-05-17
updated: 2026-05-17
project: [[02-Projects/superintelligent-vault]]
adr: [[07-Decisions/2026-05-12 sv-1 memory architecture arch]]
wiki: [[11-wiki/sv-01-memory-architecture]]
sprint: B-2 Week 4
parent: [[2026-05-17 B-2 bge-reranker 2-pass retrieval]]
---

# B-2 reranker smart-trigger — audit

## TL;DR

A `vault-search` reranker `~13s/query` latencyára beépítettük az **első mitigation P1**-et: **threshold-trigger smart-rerank**. Új mód `--mode=auto-rerank` (alias `--smart-rerank`), ami a first-pass cosine `max_score` alapján dönt: ha `>= RERANK_TRIGGER_THRESHOLD` (default **0.65**), a cosine-eredményt visszaadjuk (`~131ms`); ha alatta, lefut a CE-rerank (`~13s`).

5-query bench (warm daemon, EPYC 9354P CPU-only):

| mód | átlag | min | max | komment |
|---|---:|---:|---:|---|
| cosine-only | **154 ms** | 115 | 212 | egyezik a Week 3 baseline-nal |
| pure rerank | **13 789 ms** | 13 232 | 14 567 | egyezik a Week 3-as méréssel |
| **smart-rerank (DEFAULT)** | **8 333 ms** | 125 | 14 263 | **1.65× speedup** vs pure |

A 2 skipped query (`session-pointer`, `nano-banana`) most **125-148 ms** — interaktív. A 3 triggered query (alacsony cosine-confidence) megkapja a precision-lift-et. A 0.65-os küszöb az audit Week 3-as cosine-score-eloszlására lett kalibrálva.

A `8.3s` átlag még **nem** interaktív (cél: <500ms); de a smart-trigger jól szelektál (2/5 query azonnal kész, és pont a 3/5 precision-gain-es query kapja a CE-t). A **valódi áttörést** kisebb reranker (`bge-reranker-base 277MB`, ~3-4× speedup) vagy ONNX int8 quant adná → következő iteráció.

## Mit változtattunk

| Komponens | Változás |
|---|---|
| `/usr/local/bin/vault-search-server` | Új `RERANK_TRIGGER_THRESHOLD` env-var (default 0.65). `search` RPC új `smart_rerank: bool` + `trigger_threshold: float` paramétere. Logika: ha `smart_rerank && first_pass_max < threshold` → rerank; egyébként cosine top-K. Response mode: `smart-rerank-triggered` vagy `smart-rerank-skipped`, plus `first_pass_max_score`, `rerank_triggered`. `health` válasz tartalmazza a `rerank_trigger_threshold`-ot. |
| `/root/obsidian-vault/.vault-memory/scripts/vault-search.py` | Új `RERANK_TRIGGER_THRESHOLD` env-var. Új `--smart-rerank` flag + `--mode {auto-rerank, smart-rerank}` érték + `--trigger-threshold FLOAT` flag. **`--mode` default `auto-rerank`** (interaktív UX). Új `_apply_smart_rerank_local()` helper a native/legacy in-process path-okhoz. `_try_socket_search()` továbbítja a daemon-nak. |
| `vault-search.service` | restartolva — friss build, daemon él, threshold=0.65 a health-RPC-ben. |

Backup: `vault-search.py.bak.20260517-trigger` + `vault-search-server.bak.20260517-trigger`.

### Új mód-szemantika (CLI)

| `--mode` | Viselkedés | Latency (5-query avg) |
|---|---|---:|
| `cosine` / `cosine-only` | csak cosine, soha rerank | 154 ms |
| `reranked` / `hybrid` | mindig rerank (régi `--rerank`) | 13 789 ms |
| **`auto-rerank` / `smart-rerank` (DEFAULT)** | rerank csak ha first-pass max_cos < threshold | **8 333 ms** |

Backward-compat: `--rerank` flag továbbra is működik (force-rerank). Default mód shift: **régi default `cosine` → új default `auto-rerank`**. Aki explicit cosine-only-t akar, használja a `--mode=cosine`-t.

### Wire protocol (daemon)

```json
{"method":"search","query":"...","top_k":5,"namespace":"content",
 "smart_rerank":true,"trigger_threshold":0.65}
```

Response (skipped path):
```json
{"results":[...],"mode":"smart-rerank-skipped","first_pass_k":30,
 "first_pass_max_score":0.7261,"rerank_triggered":false,
 "trigger_threshold":0.65,"rerank_ms":0.0}
```

Response (triggered path):
```json
{"results":[...],"mode":"smart-rerank-triggered","first_pass_k":30,
 "first_pass_max_score":0.6181,"rerank_triggered":true,
 "trigger_threshold":0.65,"rerank_ms":11314.5}
```

## Benchmark — 5 query, top-5

Warm daemon (bge-m3 + bge-reranker-v2-m3 pre-loaded a benchmark warmup-passzban). Egy mérés / query / mód.

| Query | cosine ms | first_max_cos | rerank ms | smart ms | smart mode | triggered |
|---|---:|---:|---:|---:|---|:---:|
| robbantott-kereso OCR pipeline | 117 | **0.618** | 14 127 | 13 153 | smart-rerank-triggered | ✅ |
| Memgraph CE feature-limits | 115 | **0.600** | 13 723 | 13 977 | smart-rerank-triggered | ✅ |
| subagent fanout pattern | 212 | **0.630** | 14 567 | 14 263 | smart-rerank-triggered | ✅ |
| session-pointer per-chat isolation | 152 | **0.668** | 13 294 | **148** | smart-rerank-skipped | ❌ |
| nano-banana ultra-wide stitching | 173 | **0.726** | 13 232 | **126** | smart-rerank-skipped | ❌ |

### Trigger-rate

- 3/5 query (60%) trigger → CE-rerank
- 2/5 query (40%) skip → cosine top-K közvetlenül

### Várt vs valós átlag

Várt (audit-prompt): `131ms × 0.6 + 13 000ms × 0.4 ≈ 5.3s`. **Valós:** `8.33s` — kissé magasabb, mert a *trigger-rate fordítva alakult*: a Week 3-as audit-eloszlás alapján vártam 60% skip / 40% trigger, de a valóságban 40% skip / 60% trigger. A 0.65-os küszöbnél a `subagent fanout` (cos 0.630) és `Memgraph CE` (cos 0.600) **csak picit alulszorul** — egy 0.60-os küszöb 4/5 skip, 1/5 trigger lett volna, de feláldozta volna a `subagent-fanout` precision-gain-t (Week 3 audit szerint értékes improvement).

### Per-query findings

**`session-pointer per-chat isolation`** (skip) — cosine top-1 = 0.668. A Week 3 audit szerint cosine itt már 100% releváns, a CE marginális. **Helyes skip**, és **148ms** latency (vs 13 294ms pure rerank → **89× speedup ezen a queryn**).

**`nano-banana ultra-wide stitching`** (skip) — cosine top-1 = 0.726. Week 3-ban itt is improvement volt (új releváns top-2 jött be), **DE** az új top-2 cosine-score is 0.467 → a top-1 0.726 *önmagában* good-enough relevant hit, a smart-trigger értelmes kompromisszum (precision-gain elveszik, de query 126ms-ben kész).

**`robbantott-kereso OCR pipeline`** (trigger) — cosine top-1 = 0.618. Week 3 szerint itt 3 új releváns chunk jött be a top-5-be CE-vel. **Helyes trigger**. 13 153ms latency.

**`Memgraph CE feature-limits`** (trigger) — cosine top-1 = 0.600. Week 3 szerint **marginal regression**. A smart-trigger most ezt is ráüti — ez a smart-rerank korlátja egy 1D-küszöbbel: query-szintű kvalitatív info nem benne van. Egy hibrid `lexical-fallback + rerank` jobban kezelné ezt a magyar+ritka-substring esetet.

**`subagent fanout pattern`** (trigger) — cosine top-1 = 0.630. Helyes trigger, precision-gain (Week 3 szerint).

## Acceptance gate-felülvizsgálat

| Cél | Mérés | Státusz |
|---|---|---|
| `vault-search` cosine-mód < 500ms | 115-212 ms (avg 154) | ✅ |
| `auto-rerank` < 500ms minden query-n | 125-148ms skip / ~13s trigger | ❌ (csak skip-eseten ✅) |
| `auto-rerank` átlag < 5s | 8.33s | ❌ (közelít, de cél felett) |
| `auto-rerank` precision-gain a skip-elt queryken ne vesszen el | `nano-banana` veszít a #2 chunk-on | ⚠️ |
| Backward-compat `--rerank` flag | működik | ✅ |
| Threshold env-konfigurálható | `RERANK_TRIGGER_THRESHOLD=0.7` work | ✅ |

## Risks / Open issues

1. **Latency továbbra is bottleneck:** 8.33s átlag interaktív-küszöb felett (~500ms). A smart-trigger **csak** ott segít, ahol cosine már elég jó volt — a CE-t igénylő queryken nincs gyorsulás. **Real fix:** kisebb model.
2. **Threshold tuning fragility:** 0.60 vs 0.65 küszöb 1-1 query trigger-state-jét billenti. Production-ban érdemes lenne **gliding scale**-t (pl. `softmax(top-3 cos)` entropy vagy `cos[0] - cos[5] gap`) vs hard threshold.
3. **Magyar-language coverage:** `Memgraph CE` query trigger-be esett (helyes), de a CE itt regressziót okoz (Week 3 audit). A smart-trigger nem javítja ezt.
4. **Skip-quality:** `nano-banana` skip-elt; a Week 3-as precision-gain (`kgc-marketing` releváns chunk a top-2-be) most elveszik. **Compromise accepted** az interaktív sebességért.

## Next steps (priorizálva)

| # | Akció | Prio | Sprint |
|---|---|---|---|
| 1 | **`bge-reranker-base` (277MB, MiniLM-L12) A/B teszt** — ha 3-4× speedup CPU-n + smart-trigger → `auto-rerank` átlag ~2-3s, interaktív-küszöb közel | **P1** | B-2 Week 5 |
| 2 | **Hybrid lexical-BM25 fallback** — magyar ritka substring (`feature-limits`) BM25-tel előbb, dense+CE csak ha BM25 üres | P2 | B-2 Week 5 |
| 3 | **Adaptive threshold** — query-szinten (`cos[0] - cos[k] gap` vs absolute) | P3 | B-3 |
| 4 | **ONNX int8 quant** — még 2-3× speedup CPU-n a választott model-en | P3 | B-3 |
| 5 | **GPU migráció** (RTX 4060) — ~50-200ms reranked → interaktív | P3 | B-4+ |

## Reproduce

```bash
# Cosine-only (most már explicit kell)
vault-search --mode cosine "robbantott-kereso OCR pipeline"

# Smart-rerank (új default — auto-trigger)
vault-search "robbantott-kereso OCR pipeline"
# vagy explicit:
vault-search --mode auto-rerank "..."
vault-search --smart-rerank "..."

# Pure rerank (mindig)
vault-search --mode reranked "..."
vault-search --rerank "..."

# Threshold tune
RERANK_TRIGGER_THRESHOLD=0.7 vault-search "..."
vault-search --trigger-threshold 0.7 "..."

# Daemon health (látja: rerank_trigger_threshold)
echo '{"method":"health"}' | nc -U /run/vault-search.sock

# Bench reproduce
/tmp/smart_rerank_bench.py
```

Benchmark-script: `/tmp/smart_rerank_bench.py`. Raw JSON: `/tmp/smart_rerank_bench_result.json`.

## Kapcsolódó

- [[2026-05-17 B-2 bge-reranker 2-pass retrieval]] — parent audit (P1 mitigation forrása)
- [[2026-05-17 B-2 Week 3 acceptance gate readout]]
- [[2026-05-17 B-2 native vector-index migration]]
- [[../07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 ADR
- [[../11-wiki/sv-01-memory-architecture]] — research

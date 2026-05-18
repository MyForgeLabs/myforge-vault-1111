---
name: reranker-cost-optimization-not-size
description: Cross-encoder reranker latency csökkentés - NEM model-size-reduction az út, hanem trigger-rate optimization + ONNX-INT8 quantization + query-cache. Mérhetően 3-4x speedup elérhető de sub-second CPU-n szinte lehetetlen
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "reranker", "performance", "cost-optimization", "cross-encoder"]
status: stable
---

# Reranker cost optimization — NEM size, hanem trigger-rate

## A probléma

Cross-encoder reranker (`bge-reranker-v2-m3`, 568MB) **warm wall-clock 20s / 30 candidate × max_length=256** CPU-n. A naiv mitigation: **kisebb modell**. **De a 2026-05-17 A/B-teszt cáfolta:** `bge-reranker-base` 277MB-os 3.84× speedup-ot ad (warm-median 5.4s), DE **a <500ms cél MEGFOGHATATLAN** CPU-n bármely XLM-R-base modellel.

## A vault A/B-teszt eredmény (5-query × 3-repeat, daemon warm)

| Metrika | v2-m3 (568MB) | base (277MB) | Δ |
|---|---:|---:|---|
| Wall-clock warm median | 20.9s | 5.4s | **3.84× speedup** |
| Server-side `rerank_ms` median | 20.7s | 5.2s | 3.97× |
| RPC overhead | ~270ms | ~270ms | — |
| Top-3 overlap | — | — | 12/15 = **80%** |
| RAM peak (mindkettő loaded) | 4543MB | 5001MB | +458MB |
| Cold-load latency | ~24s | 17.7s | -26% |

**Verdict:** opt-in (`--reranker-model base`) ÉLES, default-shift NEM ajánlott a 10-15% precision-loss miatt (Q2 Memgraph + Q5 nano-banana zajosabb top-3).

## A valódi költség-térkép

```
Reranker total cost = (trigger_rate × per_invocation_cost)

per_invocation_cost = (encode_time × n_candidates) + tokenize_overhead

REDUCTION axis-ok:
  ┌─ trigger_rate ⇣ ── smart-trigger (cosine < 0.65) ─── -30-50% calls
  │                ── score-gap smart-skip ─────────── -30% additional
  │
  ├─ encode_time ⇣ ── model-size reduction (v2-m3 → base) ─── -75% per call
  │              ── ONNX-INT8 quantization ─────────── -50% additional
  │              ── batch-size optimization ─────────── -10-20%
  │
  ├─ n_candidates ⇣ ── top-K reduce (50 → 30) ──────── -40%
  │                ── early-termination cosine-cap ── -10-30%
  │
  └─ tokenize_overhead ⇣ ── max_length reduce (256 → 128) ── -50% / acc-loss 5-10%
                       ── query-cache (LRU 5min TTL) ── -50% for repeat queries
```

**A legjobb ROI:** **trigger_rate optimization** (-50%) + **ONNX-INT8** (-50%) → 4× speedup model-size-változtatás nélkül = ~5s wall-clock (még mindig 10× <500ms cél).

## Sub-second CPU-n elérhetetlen — accept and route

Egy XLM-R-base cross-encoder 30-candidate × 256-token reranking-ja CPU-n **fundamentális latency-floor ~3-4s** (matmul-cap). A <500ms-cél elérése csak:

1. **GPU-vel** — 30-50× speedup (10s → 200-300ms), de infrastruktúra-cost
2. **ColBERT-style late-interaction** — pre-computed doc-embeddings, sub-50ms query-time (Reimers et al. 2020), de query-side encoding még szükséges
3. **DistilBERT-quantize-ONNX** — 50MB-os modell, INT8 + AVX2 → ~1-2s (még mindig 2-4× cél felett)
4. **Re-route: NE reranking, hanem dense top-K fine-tuning** — query-specific cross-encoder rerank csak top-3-on (n_candidates=3, ~1s elérhető)

## Mikor érdemes alkalmazni a 3.84×-os opt-in-t

- ✅ Bulk-retrieval (>30 query) ahol precision-loss 10-15% tolerált
- ✅ Latency-budget 5-10s tartomány (NEM interaktív)
- ❌ Interaktív UX (search-as-you-type, <500ms cél)
- ❌ High-precision use-case (audit, citation)

## Tervezési alapelvek

1. **Trigger-rate ELŐSZÖR** — score-gap smart-skip + cosine-cap legolcsóbb implementation, no RAM cost
2. **Per-task model-választás** — `--reranker-model {v2-m3|base|auto}` flag, multi-model cache `RerankerSingleton`
3. **Default OFF a base-re** — v2-m3 marad default a 80% top-3-overlap-miatt
4. **ONNX-INT8 Week 5+ follow-up** — quantization-aware re-export, ~50% additional speedup
5. **Query-cache 5min TTL** — repeat queries (cron-monitor, dashboard-refresh) -50% cost

## Trade-off

- ⚠️ **Sub-second CPU cél unrealizable** — accept and prioritize trigger-reduction
- ⚠️ Multi-model cache RAM +458MB (mindkettő loaded)
- ✅ 3.84× speedup opt-in mode-on (5s wall-clock még mindig kezelhetbő)
- ✅ Precision-loss 10-15% acceptable bulk-retrieval-context-ban

## Élő SV-pipeline alkalmazás

A `vault-search --reranker-model {v2-m3|base|auto}` flag élesedett a B-2 Week 4 sprint-ben (2026-05-17). Multi-model cache `RerankerSingleton` per-HF-id lazy-load. Smart-trigger threshold 0.65 marad változatlan. Week 5 follow-up: score-gap smart-skip + ONNX-INT8 + query-cache.

## Kapcsolódó

- [[smart-trigger-cost-pattern]] — cheap-baseline + expensive-second-pass alap-pattern
- [[memgraph-ce-feature-limits]] — native vector-index (cosine first-pass)
- [[sv-01-memory-architecture]] — B-2 search-axis research
- [[vendor-feature-verify-before-workaround]] — analogous lesson (release-cycle check)

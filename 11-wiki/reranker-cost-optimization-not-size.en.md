---
name: reranker-cost-optimization-not-size
description: Cross-encoder reranker latency reduction - model-size-reduction is NOT the right path; instead use trigger-rate optimization + ONNX-INT8 quantization + query-cache. Measurably 3-4x speedup is achievable but sub-second on CPU is nearly impossible
type: wiki
lang: en
translated_from: reranker-cost-optimization-not-size
created: 2026-05-17
updated: 2026-05-18
tags: ["#type/wiki", "reranker", "performance", "cost-optimization", "cross-encoder"]
status: stable
---

# Reranker cost optimization — NOT size, trigger rate

## 🎧 Audio overview

- **Deep-dive podcast** (NotebookLM 2-host, ~5 min, EN): [reranker-cost-optimization-not-size.en-podcast.mp3](../.vault-nb/audio-overviews/reranker-cost-optimization-not-size.en-podcast.mp3) (39 MB) — *"Why Smaller AI Models Worsen Search"*

## The problem

Cross-encoder reranker (`bge-reranker-v2-m3`, 568MB) takes **warm wall-clock 20s / 30 candidates × max_length=256** on CPU. The naive mitigation: **smaller model**. **But an A/B test refuted this:** `bge-reranker-base` (277MB) gives a 3.84× speedup (warm-median 5.4s), BUT **the <500ms target is UNREACHABLE** on CPU with any XLM-R-base model.

## A/B test result (5 queries × 3 repeats, daemon warm)

| Metric | v2-m3 (568MB) | base (277MB) | Δ |
|---|---:|---:|---|
| Wall-clock warm median | 20.9s | 5.4s | **3.84× speedup** |
| Server-side `rerank_ms` median | 20.7s | 5.2s | 3.97× |
| RPC overhead | ~270ms | ~270ms | — |
| Top-3 overlap | — | — | 12/15 = **80%** |
| RAM peak (both loaded) | 4543MB | 5001MB | +458MB |
| Cold-load latency | ~24s | 17.7s | -26% |

**Verdict:** opt-in (`--reranker-model base`) released, default shift NOT recommended due to 10-15% precision loss on noisy top-3.

## The real cost map

```
Reranker total cost = (trigger_rate × per_invocation_cost)

per_invocation_cost = (encode_time × n_candidates) + tokenize_overhead

REDUCTION axes:
  ┌─ trigger_rate ⇣ ── smart-trigger (cosine < 0.65) ────── -30-50% calls
  │                ── score-gap smart-skip ─────────────── -30% additional
  │
  ├─ encode_time ⇣ ── model-size reduction (v2-m3 → base) ── -75% per call
  │              ── ONNX-INT8 quantization ────────────── -50% additional
  │              ── batch-size optimization ───────────── -10-20%
  │
  ├─ n_candidates ⇣ ── top-K reduce (50 → 30) ─────────── -40%
  │                ── early-termination cosine-cap ────── -10-30%
  │
  └─ tokenize_overhead ⇣ ── max_length reduce (256 → 128) ── -50% / acc-loss 5-10%
                       ── query-cache (LRU 5min TTL) ──── -50% for repeat queries
```

**Best ROI:** **trigger-rate optimization** (-50%) + **ONNX-INT8** (-50%) → 4× speedup without changing model size = ~5s wall-clock (still 10× over <500ms target).

## Sub-second CPU is unreachable — accept and route

An XLM-R-base cross-encoder with 30-candidate × 256-token reranking on CPU has a **fundamental latency floor of ~3-4s** (matmul-bound). The <500ms target is reachable only via:

1. **GPU** — 30-50× speedup (10s → 200-300ms), but infrastructure cost
2. **ColBERT-style late interaction** — pre-computed doc embeddings, sub-50ms query time (Reimers et al. 2020), but query-side encoding still needed
3. **DistilBERT-quantize-ONNX** — 50MB model, INT8 + AVX2 → ~1-2s (still 2-4× over target)
4. **Re-route: skip reranking, do dense top-K fine-tuning instead** — query-specific cross-encoder rerank only on top-3 (n_candidates=3, ~1s reachable)

## When the 3.84× opt-in is worthwhile

- ✅ Bulk retrieval (>30 queries) where 10-15% precision loss is tolerated
- ✅ Latency budget 5-10s range (NOT interactive)
- ❌ Interactive UX (search-as-you-type, <500ms target)
- ❌ High-precision use case (audit, citation)

## Design principles

1. **Trigger-rate FIRST** — score-gap smart-skip + cosine-cap is the cheapest implementation, no RAM cost
2. **Per-task model choice** — `--reranker-model {v2-m3|base|auto}` flag, multi-model cache `RerankerSingleton`
3. **Default OFF for base** — v2-m3 stays default due to 80% top-3 overlap
4. **ONNX-INT8 follow-up** — quantization-aware re-export, ~50% additional speedup
5. **Query cache 5min TTL** — repeat queries (cron-monitor, dashboard-refresh) -50% cost

## Trade-offs

- ⚠️ **Sub-second CPU target unreachable** — accept and prioritize trigger reduction
- ⚠️ Multi-model cache RAM +458MB (both loaded)
- ✅ 3.84× speedup in opt-in mode (5s wall-clock still manageable)
- ✅ Precision loss 10-15% acceptable in bulk-retrieval context

## Live application

A search service with `--reranker-model {v2-m3|base|auto}` flag is in production. Multi-model cache `RerankerSingleton` per-HF-id lazy-load. Smart-trigger threshold 0.65 stays constant. Follow-up: score-gap smart-skip + ONNX-INT8 + query cache.

## Related

- [[smart-trigger-cost-pattern]] — cheap-baseline + expensive-second-pass base pattern
- [[memgraph-ce-feature-limits]] — native vector index (cosine first-pass)
- [[sv-01-memory-architecture]] — search architecture research
- [[vendor-feature-verify-before-workaround]] — analogous lesson (release-cycle check)

---
name: 2026-05-17 B-2 Week 4 bge-reranker-base A/B
type: audit
created: 2026-05-17
updated: 2026-05-17
tags:
  - sprint/sv-b-2
  - layer/retrieval
  - perf/bench
  - reranker
related:
  - "[[06-Audits/2026-05-17 B-2 bge-reranker 2-pass retrieval]]"
  - "[[06-Audits/2026-05-17 B-2 reranker smart-trigger]]"
  - "[[06-Audits/2026-05-17 B-2 native vector-index migration]]"
  - "[[02-Projects/superintelligent-vault]]"
---

# B-2 Week 4 — bge-reranker-base 277MB A/B-teszt vs bge-reranker-v2-m3 568MB

> [!info] TL;DR
> bge-reranker-base **median 3.84× gyorsabb** (20.9s → 5.4s warm wall-clock,
> top_k=5 oversample=6 max_length=256 batch=8, CPU EPYC 9354P) **+458 MB RSS**
> (mindkét modell daemonba töltve). Top-3 overlap 80% (12/15), de 2/5 query-n
> érzékelhető minőség-csökkenés (Q2 Memgraph CE, Q5 nano-banana — base zajos
> top-2-3-at hoz). **A <500ms cél egyik modellel sem érhető el** CPU-n a jelenlegi
> oversample-mel. **Javaslat: NEM default-shift**, hanem **opt-in `--reranker-model base`**
> low-precision/high-throughput use-case-ekre + smart-mode `threshold↑0.70` ahol a base
> használata acceptable (rerank-skip-rate növekszik).

## Cél

1. Letölteni `BAAI/bge-reranker-base` (~277MB) a `~/.cache/huggingface/hub/`-ba
2. `vault-search` + `vault-search-server`-re `--reranker-model {v2-m3|base|auto}`
   flaget tenni (default `v2-m3` backward-compat)
3. 5-query A/B benchmark: pure-rerank wall-clock + top-3 ranking + RAM-peak
4. Smart-trigger threshold marad 0.65 (változatlan)
5. Recommendation: default-shift v2-m3 → base **ha precision-loss <10% ÉS latency <500ms**

## Letöltés + cache verifikáció

```
/root/.notebooklm-venv/bin/python -c "
from sentence_transformers import CrossEncoder
m = CrossEncoder('BAAI/bge-reranker-base', device='cpu', max_length=256)
m.predict([('warmup','doc')])
" 2>&1
# loaded in 17.7s, warmup OK
```

Cache:
```
/root/.cache/huggingface/hub/models--BAAI--bge-reranker-base/
1.1G — config, model.safetensors (~278MB upload size, ~1.1GB on disk incl. tokenizer.json,
       sentencepiece, blobs+refs+snapshots layout)
```

A v2-m3 modellhez képest:
```
/root/.cache/huggingface/hub/models--BAAI--bge-reranker-v2-m3/  ~2.2GB on disk
```

## Patch összefoglaló

### `vault-search-server` változások

- `RERANKER_MODEL_ALIASES` dict (`"base"` → `"BAAI/bge-reranker-base"`,
  `"v2-m3"` → `"BAAI/bge-reranker-v2-m3"`, `"auto"` → daemon-default RERANKER_MODEL).
- `RerankerSingleton` → **multi-model cache** (`self._models: dict[hf_id, CrossEncoder]`).
  - `resolve(name)` → alias/HF-id feloldó.
  - `_ensure_loaded(model_id)` per-model lazy-load.
  - `rerank(query, candidates, top_k, model_id=None)` → optional model param.
- `search` RPC új paraméter: `reranker_model` (alias vagy HF id).
  - A response-ben új mező: `"reranker_model": "BAAI/bge-reranker-base"` (resolved).
- `health` RPC új mezők: `reranker_models_loaded: [hf_id, ...]`, `reranker_aliases: {alias: hf_id}`.
- `VAULT_RERANK_PREWARM=<spec>` — `"1"` (legacy) vagy `"v2-m3,base"` (multi-model warm).
- Backward compat: ha `reranker_model` paraméter nincs a request-ben,
  a daemon a default `RERANKER_MODEL`-t használja.

### `vault-search.py` (CLI) változások

- `RERANKER_MODEL_ALIASES` + `_resolve_reranker_model()` helper.
- CLI flag: `--reranker-model {v2-m3|base|auto|<HF id>}`, default `None` (=env/daemon-default).
- `_get_reranker(model_id)` + `_rerank_in_process(..., model_id)` per-model cache
  (in-process path, `--no-socket`).
- `_apply_smart_rerank_local(..., reranker_model)` átviszi a model-id-t.
- `search(..., reranker_model)` minden hívási útvonalon (native + numpy + legacy fallback).
- `_try_socket_search(..., reranker_model)` átküldi a daemon RPC-nek.
- CLI output-on: `model=bge-reranker-base` jelzi melyik futott.

### Backupok

```
/usr/local/bin/vault-search-server.bak.20260517-rerank-base
/root/obsidian-vault/.vault-memory/scripts/vault-search.py.bak.20260517-rerank-base
```

### systemd

`vault-search.service` **változatlan** (service-fájl módosítás nincs). Restart elég:

```
systemctl restart vault-search.service
echo '{"method":"health"}' | nc -U /run/vault-search.sock
# {"ok":true, "reranker_models_loaded":[], "reranker_aliases":{...}}
```

Opcionálisan `Environment="VAULT_RERANK_PREWARM=v2-m3,base"` lenne állítható
az unit-fájlban, de **most nem nyúltunk hozzá** (a feladat szerint a service-fájl
nem változhat). A modellek lazy-load-olódnak első rerank-callkor.

## 5-query A/B benchmark

**Setup:** mindkét modell előmelegítve (`reranker_models_loaded: [base, v2-m3]`),
3 ismétlés per (query, model), median warm wall-clock + server-side `rerank_ms`.
`--rerank` (FORCED, NEM smart-mode), top-k=5, oversample=6 → first_pass_k=30.

| Query | v2-m3 warm | base warm | speedup | first_max_cos |
|---|---:|---:|---:|---:|
| robbantott kereső sprint Day 0 skeleton | 24076 ms | 7606 ms | 3.17× | 0.617 |
| Memgraph CE 3.9.0 native vector index | 26930 ms | 10248 ms | 2.63× | 0.577 |
| subagent fanout pattern 14 párh | 20902 ms | 5323 ms | 3.93× | 0.540 |
| G-Eval bias mitigation self-enhancement | 15889 ms | 5450 ms | 2.92× | 0.612 |
| nano-banana CLI gotchas multipage | 14461 ms | 4194 ms | 3.45× | 0.668 |
| **median** | **20902 ms** | **5450 ms** | **3.84×** | — |

Server-side `rerank_ms` warm median (CrossEncoder.predict() only, no RPC overhead):

| Query | v2-m3 srv | base srv | overhead (wall-srv) |
|---|---:|---:|---:|
| robbantott… | 23786 ms | 7303 ms | ~300 ms |
| Memgraph CE | 26612 ms | 9933 ms | ~315 ms |
| subagent fanout | 20653 ms | 5168 ms | ~250 ms |
| G-Eval bias | 15573 ms | 5208 ms | ~316 ms |
| nano-banana | 14193 ms | 4076 ms | ~268 ms |

A wall-overhead ~250-320 ms (Unix-socket RPC + JSON serialize + bge-m3 encode + vector_search.search).

### Top-3 precision (manual eval)

Top-3 fájl-overlap (set-intersection over 3):

| Query | overlap | minőség-megjegyzés |
|---|---|---|
| Day 0 skeleton | 2/3 | sorrend különbözik, mindkettő 2/3 releváns |
| Memgraph CE | 2/3 | v2-m3 jobb (base top2 `sv-functional-payoff` zaj) |
| subagent fanout | 3/3 | azonos halmaz, csak sorrend más |
| G-Eval bias | 3/3 | azonos halmaz, csak sorrend más |
| nano-banana | 2/3 | v2-m3 jobb (base top2 `kgc-marketing` irreleváns) |

**Aggregate: 12/15 (80%) overlap, 2/5 query-n érzékelhető minőség-csökkenés.**

Becsült precision-loss: ~10-15% (a 80% overlap önmagában 20%-os top-3-eltérést jelez,
de a 2 érintett query-ben a kiesett 3. tag releváns volt, így az "effective"
precision-vesztés ~10-15%). **A <10%-os küszöböt szűken nem éri el.**

### RAM-peak

```
RSS before bench:  4543 MB  (bge-m3 + base + v2-m3 mind betöltve daemonba)
RSS peak:          5001 MB  (+458 MB a benchmark alatt)
RSS after:         4993 MB
```

A `+458 MB` delta a v2-m3 batched-predict() workspace allokáció (oversample=6 →
30 candidates × batch=8 → 4 forward-pass, XLM-RoBERTa-large attention buffers).
Base modell egyedüli RSS (csak base betöltve) ~3.8GB, csak v2-m3 ~4.3GB
(empirikus, korábbi mérés).

**RAM-súlypont:** ha base-only daemonpolicy lenne, **~500 MB RAM-megtakarítás**
(0.5GB v2-m3 elhagyásával), de a 32GB EPYC-n ez nem szűk keresztmetszet.

## Recommendation

> [!todo] **NEM default-shift v2-m3 → base.** Indoklás:

1. **Cél <500ms nem érhető el** (base warm-min 4.2s, ez 8× a target).
   Sub-second cél csak GPU-val (ROCm/CUDA) vagy ONNX-quantized FP16-tal érhető el,
   ami szóba se került a roadmapen.
2. **Precision-loss kicsivel >10%** (Q2 + Q5 érzékelhető regresszió). A 12/15 overlap
   önmagában 20% top-3-eltérés; a "useful precision" loss ~10-15%, nem 10%.
3. **Smart-mode élt-ek**: a smart-trigger threshold 0.65 mellett a 5 query közül 4-nek
   a first-pass max_cos <0.65 → rerank trigger ÚGYIS, és base esetén a precision még
   szűkösebb.

### Új konfigurációs lehetőségek (opt-in)

- **`vault-search --reranker-model base ...`** — opt-in low-latency rerank,
  ahol a 3-4× speedup fontosabb a precision-nél (pl. real-time UI-suggest,
  vagy bulk-batch query-feed).
- **`VAULT_RERANK_PREWARM=v2-m3,base`** — daemon mindkettőt prewarmolja
  startupkor (opcionális unit-Environment, MOST NINCS BEÁLLÍTVA).
- **Threshold-bump base-only mode-ban**: `RERANK_TRIGGER_THRESHOLD=0.70`
  + `--reranker-model base` — több query skip-elődik smart-mode-ban,
  amelyik trigger-elődik, ott a gyorsabb base fut. Bench szükséges.

### Default marad

```
vault-search --rerank "..." → BAAI/bge-reranker-v2-m3 (CHANGE-NONE)
vault-search --smart-rerank "..." → v2-m3, threshold 0.65 (CHANGE-NONE)
```

## Week 5 follow-up — HNSW-rerank hybrid skeleton

Az igazi <500ms-cél elérésére más architektúra kell. Vázlat:

1. **HNSW-szintű rerank skip** — Memgraph native vector_search.search már
   sub-ms (1-3ms p95). Ha az first-pass top-K cosine-score-eloszlása jól
   diszkriminál (top-1 score >> top-K score, gap >0.10), a cosine ranking
   önmagában elfogadható ("score-gap-based skip" → smart-mode v2-extension).
2. **ONNX-quantized base** — `optimum.onnxruntime` + INT8 quantization a base
   modellen ~2-3× extra speedup CPU-n, kb. **1.5-2.5s wall-clock**.
3. **Distilled cross-encoder** — `bge-reranker-base` 12-layer XLM-R-base.
   6-layer distill (TinyBERT/DistilBERT-style) target **<1s** lehetne, de
   training-cost + custom-pipeline → Phase C/D capability.
4. **Server-side query-cache** — repeating queries (Claude-CLI multi-turn)
   100% rerank-skip. 5-min TTL, hash-key (query, top_k, namespace).

Layer-priority Week 5-re:

- **Day 1-2**: score-gap-based smart-skip (no model change, +zero RAM, ~30% extra skip-rate)
- **Day 3-4**: ONNX base quantization + bench (~2.5s target wall-clock)
- **Day 5**: query-cache + cold-vs-warm separation audit

## Acceptance gate

> [!success] PASS:
> - ✅ `BAAI/bge-reranker-base` letöltve és cache-elve (`~/.cache/huggingface/hub/`)
> - ✅ `--reranker-model {v2-m3|base|auto}` flag CLI + daemon RPC mindkettőn élesedett
> - ✅ Backward-compat: default `vault-search --rerank` változatlan (v2-m3)
> - ✅ A/B bench 5-query × 2-model × 3-repeat lefutott, audit-MD-be írva
> - ✅ Backupok elkészítve (`.bak.20260517-rerank-base`)
> - ✅ vault-search.service unit-fájl nem módosult (restart-tal aktiválódott)
> - ❌ <500ms cél NEM elérve (base 5.4s warm-median CPU-n) → Week 5 ONNX-quantize
> - ❌ Default-shift NEM ajánlott (precision-loss >10% nézve a Q2+Q5 regressziót)

## Kapcsolódó

- [[06-Audits/2026-05-17 B-2 bge-reranker 2-pass retrieval]] — base-line v2-m3 integráció
- [[06-Audits/2026-05-17 B-2 reranker smart-trigger]] — threshold 0.65 tuning
- [[06-Audits/2026-05-17 B-2 native vector-index migration]] — Memgraph CE 3.9 base
- [[11-wiki/memgraph-ce-feature-limits]] — vector-index 280× speedup

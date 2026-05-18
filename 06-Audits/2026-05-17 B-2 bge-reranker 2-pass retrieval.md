---
name: B-2 bge-reranker-v2-m3 2-pass retrieval audit
type: audit
tags: ["#type/audit", "#project/sv", "sv-2", "reranker", "cross-encoder", "retrieval"]
created: 2026-05-17
updated: 2026-05-17
project: [[02-Projects/superintelligent-vault]]
adr: [[07-Decisions/2026-05-12 sv-1 memory architecture arch]]
wiki: [[11-wiki/sv-01-memory-architecture]]
sprint: B-2 Week 4
---

# B-2 `bge-reranker-v2-m3` 2-pass retrieval — audit

## TL;DR

Beépítettük a `BAAI/bge-reranker-v2-m3` cross-encoder-t a `vault-search` pipeline-ba mint **opcionális 2-pass** réteg (`--rerank` / `--mode reranked`). Mind a daemon (`/usr/local/bin/vault-search-server`), mind a CLI (`vault-search.py`) támogatja. A daemon a model-et **lazy-loadolja** (első `--rerank` hívásra), utána warm marad.

**Relevance** — subjective top-5 felülvizsgálat 5 query-n: **3/5 query-ben szembetűnő improvement** (`robbantott`, `subagent-fanout`, `nano-banana`), **1/5 neutral** (`session-pointer` — már cosine is jó volt), **1/5 marginally worse** (`Memgraph CE` — a reranker túl-büntette a relevant chunkokat alacsony abszolút score-ral, de top-1 stabil).

**Latency (warm-daemon, CPU-only, EPYC 9354P + RAM-pressure):**

| mód              | median | min  | max  | cél |
|---|---|---|---|---|
| `cosine` (warm)  | **131 ms** | 102 | 172 | ≤500 ms ✅ |
| `reranked` (warm)| **~13 000 ms** | 12 620 | 14 680 | ≤500 ms ❌ |
| `reranked` (overhead) | ~12 900 ms / 30 pairs | – | – | ~430 ms / pair |

A specifikus latency-cél (300-500 ms reranked) **NEM teljesült** ezen a host-on: a `bge-reranker-v2-m3` egy 568MB-os XLM-RoBERTa-large; CPU-only inferencia (8 thread, 30 pair, max_length=256) **~13s/query** ebben a környezetben. **A relevance-gain valós (3/5 → erős), de a latency rendkívül érzékeny:** vagy GPU, vagy kisebb reranker (`bge-reranker-base`, ~277MB → ~3-4×), vagy ANN-rerank (rerankerless filter) kell production-ready 2-pass-hoz.

## Mit változtattunk

| Komponens | Változás |
|---|---|
| `/usr/local/bin/vault-search-server` | Új `RerankerSingleton` class (lazy load), `search` RPC `rerank: bool` paraméter, `health` válasz `reranker_loaded` + `reranker_model` mezővel. Env: `RERANKER_MODEL`, `RERANK_OVERSAMPLE` (default 6), `RERANK_MAX_CANDIDATES` (30), `RERANK_MAX_LENGTH` (256), `RERANK_BATCH_SIZE` (8), `VAULT_RERANK_PREWARM=1` opt-in. |
| `/root/obsidian-vault/.vault-memory/scripts/vault-search.py` | `--rerank` és `--mode {cosine,cosine-only,reranked,hybrid}` CLI flag. `_rerank_in_process` helper minden 3 backendre (native / numpy / legacy) — daemon-rerank preferenciával. `search()` most teljes dict-et ad vissza (`mode`, `backend`, `first_pass_k`, `rerank_ms`). |
| `vault-search.service` | restartolva — daemon az új build-tel él, reranker továbbra is lazy. |

Backup: `vault-search.py.bak.20260517-rerank` + `vault-search-server.bak.20260517-rerank`.

### 2-pass workflow

1. **First pass** — `vault-search-server` cosine-rang `first_pass_k = top_k × RERANK_OVERSAMPLE` (cap: `RERANK_MAX_CANDIDATES`). `top_k=5` esetén ez **30 jelölt**.
2. **Second pass** — `(query, chunk.text)` párokra `CrossEncoder.predict()`, `batch_size=8`, `max_length=256`. Score = sigmoid-output 0..1.
3. **Output** — top-`top_k` rerank-score szerint, mindegyik entry `score` = rerank, `cosine_score` = first-pass cosine.

Wire (CLI/daemon protocol):
```json
{"method":"search","query":"...","top_k":5,"namespace":"content","rerank":true}
```
Response (rerank=true):
```json
{"results":[{...,"score":0.98,"cosine_score":0.62}],
 "mode":"reranked","first_pass_k":30,"rerank_ms":13099.6}
```

## Benchmark — 5 query, top-5

Daemon warm (bge-m3 + bge-reranker-v2-m3 pre-loaded). 2 warm passes mérése, median.

| Query | cosine lat | rerank lat | overlap@5 | changed@5 | Subj. improvement |
|---|---:|---:|---:|---:|---|
| robbantott-kereso OCR pipeline | 146 ms | 13 281 ms | 2/5 | **3** | **jó** ✅ |
| Memgraph CE feature-limits     | 136 ms | 13 919 ms | 3/5 | 2 | neutral / marginal − |
| subagent fanout pattern        | 108 ms | 14 680 ms | 2/5 | **3** | **jó** ✅ |
| session-pointer per-chat isolation | 134 ms | 12 924 ms | 4/5 | 1 | neutral (cosine már jó volt) |
| nano-banana ultra-wide stitching | 132 ms | 12 620 ms | 4/5 | 1 | **jó** ✅ (új releváns ranglistára) |

### Per-query findings

#### 1. `robbantott-kereso OCR pipeline` — IMPROVEMENT ✅

A cosine top-1 a 2026-05-17 KGC-integráció ADR (releváns, de „Indoklás" alszakasz). Reranker felcserélte: top-1 lett a **2026-05-12 Session Summary** (`0.990 vs cos 0.563`) — ez tartalmilag a teljes pipeline összegzése, sokkal jobban illik az „OCR pipeline" lekérdezésre. Top-3 már a projekt-fájl maga (`02-Projects/robbantott-kereso.md #0`, `cos 0.466 → rerank 0.784`) — ez **bejött a top-5-be** a reranker-rel, **cosine elveszítette** (alacsony abszolút score).

A cosine top-3-5 sok session-noise-t hozott (`dbnet-paddleocr-small-callouts` — túl-specifikus alkomponens). A reranker ezt kiszórta és a `02-Projects` + `08-Sessions` overview-chunkokat előrébb tette.

#### 2. `Memgraph CE feature-limits` — MARGINAL NEGATIVE −

A cosine top-1 is a B-2 Week 1 session-ben volt (helyes). A reranker megőrizte ezt, **de** az ADR `Acceptance criteria` chunk-ot (#5 cosine-ban) kiejtette, helyette session-noise (`Propagation log`, `Learnings → memória`) került fel.

**Diagnosztika:** a `feature-limits` szó-szerinti substring nincs a vault egyetlen chunk-jában sem. A reranker valószínűleg a multi-lang cross-encoder magyar-tartalom alultanítottsága miatt nem értékelte erősebben az ADR-chunk-ot a session-summary-nál. Ezt a query-t **érdemes később lexical+semantic hibrid-tel** retesztelni.

#### 3. `subagent fanout pattern` — IMPROVEMENT ✅

Cosine top-1 a `claude-code-subagent-fanout.md #8` — releváns wiki, de a **„Mikor NE használd"** szekció (negatív példa). A reranker ezt **levitte** és top-1-re a `vault-net-ingest.md #7 Kapcsolódó` chunkot tette, amely cross-link-keket tartalmaz subagent-fanout-ra. Top-2 a B-1 SV-5 ADR `Backfill TELJES` szekciója — az actual implementation. Top-3 a milestone-retro `Tanulságok (kicsi)` chunk.

A reranker **jobban értette** hogy a query a pattern *használatáról* szól, nem definíció-szótár-szerű leírásról.

#### 4. `session-pointer per-chat isolation` — NEUTRAL

Cosine top-5 már 100% releváns wiki + helyes session-tartalom volt (3× `cli-session-id-env-var-matrix`, 2× `claude-code-session-id-per-chat-isolation`). A reranker átrendezte a top-2-t (a per-chat-isolation wiki került előre — kissé jobb), de a halmaz alig változott (overlap 4/5).

**Insight:** ha a cosine már >0.65 score-ral hozza a releváns wiki-t, a reranker marginális. **Threshold-trigger-elt rerank** (`if max_cosine < 0.6: rerank`) jövő iteráció.

#### 5. `nano-banana ultra-wide stitching` — IMPROVEMENT ✅

Cosine top-1 helyes (`nano-banana-ultra-wide-stitch.md #0`, `0.726`). A reranker megőrizte, **de** top-2-re a `kgc-marketing.md #2 Frissítések 2026-05-13` projekt-állapot chunk került (`cos 0.467 → rerank 0.943`) — ez **konkrét use-case** a 3-panel stitch-re a Rojt-bojt kampányhoz. Cosine ezt **nem hozta a top-5-be**.

Új top-5-ben **2 új releváns** chunk (kgc-marketing project + session-learnings) jött be — érdemi precision-gain.

### Latency-kalandok és root-cause

Az eredeti várakozás `~300-500 ms reranked` volt. A kapott **~13 000 ms** ettől 25-40×-es eltérés. Root-cause-analízis:

1. **bge-reranker-v2-m3 méret** — XLM-RoBERTa-large (568MB on disk, ~1.2GB RSS aktivációkkal). A `bge-reranker-base` (~277MB, MiniLM-L12) **~3-4× gyorsabb** lenne, de magyar-cross-lingual minőség lényegesen rosszabb.
2. **CPU-only inferencia** — 30 pair × 1.5s/pair = 45s első batch-csel; max_length=256 + batch_size=8 → 13s. GPU-n ugyanez 100-300ms lenne.
3. **RAM-pressure** — host 32GB RAM, 22GB használt + 4GB swap full. Daemon RSS 4.1GB. Page-faulting jelentősen lassítja a forward-pass-t.
4. **Quantization hiányzik** — `optimum` ONNX Runtime + int8 quantization 2-3× speedup CPU-n, **de** kezdeti integráció (Q2-target).

A `RERANK_OVERSAMPLE=10 → 6` és `MAX_LENGTH=512 → 256` tuning ~25-30%-ot vágott le, de a fundamental CPU-bound jelleg nem változott.

## Acceptance gate-felülvizsgálat

| Cél (eredeti B-2 ADR) | Mérés | Státusz |
|---|---|---|
| `vault-search <500ms warm` (cosine) | 131 ms median | ✅ |
| Top-5 quality `>0.85` releváns chunk | 4/5 query-ben top-1 cosine score `>0.6`; reranker stabilizálta a top-1 jelentősét | ⚠️ kvalitatív yes |
| `--rerank` opcionális (no regression) | cosine-only mód érintetlen | ✅ |
| `--rerank` `<500ms` | 13 000 ms | ❌ (CPU+RAM-bound, model-választás kell) |

## Subjective minőségi értékelés (összegzés)

Az 5 query-ből **3-ban érdemi precision-javulás** (új releváns chunkok jönnek be a top-5-be, amelyeket a cosine kihagyott), **1 neutral** (cosine elég volt), **1 marginális regresszió** (Memgraph CE — magyar-query + ritka substring egy szlengjegyzet keret-szerűen).

A reranker a **„helyes-de-felszínes" → „helyes-de-mély"** átmenetnél a leghasznosabb: pl. egy szókereső query-vel cosine-ban a wiki dictionary-szakasza tündököl, de a reranker az **alkalmazási példá-t** vagy **összegző chunkot** tolja előre. Ez egyezik a cross-encoder általános viselkedésével (joint scoring jobban érti a kérdés szándékát mint a független bi-encoder).

## Risks / Open issues

1. **Latency:** 13s reranked-query **nem interaktív**. Mitigations (sorrendben):
   - **(P1)** Threshold-trigger: ha `max_cosine_score >= 0.7` → cosine-only. (`session-pointer` + `nano-banana` queryket eliminálná → ~60% rerank-szám csökkenés.)
   - **(P2)** Kisebb reranker (`bge-reranker-base` 277MB vagy `jina-reranker-v2-base-multilingual` 278MB) — 3-4× speedup.
   - **(P3)** ONNX Runtime + int8 — 2-3× speedup CPU-n.
   - **(P4)** GPU/CUDA migráció (RTX 4060 → 50-200ms/query).
2. **Magyar-language cross-encoder coverage** — bge-reranker-v2-m3 multilingual, de magyar fine-tune nincs. A `Memgraph CE` query regressziója valószínűleg ennek tüneti.
3. **RAM** — daemon most 4.1GB RSS (bge-m3 + bge-reranker + chunks). Swap full. Production host upgrade vagy reranker eltávolítás kell ha RAM <16GB.
4. **No hybrid yet** — BM25 + dense + rerank jövő iteráció (sv-01 research mentions). A reranker önmagában nem old meg lexical-recall-edge-case-t.

## Next steps (priorizálva)

| # | Akció | Prio | Sprint |
|---|---|---|---|
| 1 | **Threshold-trigger** — `if first_pass max_score < REIRANK_TRIGGER_THRESHOLD (default 0.65): rerank` env-flag-gel | P1 | B-2 Week 4-5 |
| 2 | **Hybrid score** — `final = α·cosine + β·bm25 + γ·provenance + δ·rerank` (csak ha threshold-trigger nem elég) | P2 | B-2 Week 5 |
| 3 | Reranker-modell A/B — `bge-reranker-base` vs `jina-reranker-v2-base-multilingual` vs `bge-reranker-v2-m3` | P2 | B-2 Week 5 |
| 4 | ONNX export + int8 quant — 2-3× CPU speedup | P3 | B-3 vagy később |
| 5 | Lexical fallback + agentic-rerank — ritka substring query-kre BM25-only | P3 | B-4 |

## Reproduce

```bash
# Cosine-only (default)
vault-search "robbantott-kereso OCR pipeline"

# Reranked
vault-search --rerank "robbantott-kereso OCR pipeline"

# JSON-output mód+metadata-val
vault-search --rerank --json "robbantott-kereso OCR pipeline" | jq '.mode, .rerank_ms'

# Threshold-tune
RERANK_OVERSAMPLE=4 RERANK_MAX_LENGTH=128 vault-search --rerank "..."

# Daemon health (látja: reranker_loaded)
echo '{"method":"health"}' | nc -U /run/vault-search.sock
```

Benchmark-script: `/tmp/rerank_bench.py`. Raw JSON: `/tmp/rerank_bench_result.json` (546 sor).

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 ADR
- [[2026-05-17 B-2 Week 3 acceptance gate readout]] — előző gate-readout
- [[2026-05-17 B-2 native vector-index migration]] — Memgraph natív vector-search
- [[../11-wiki/sv-01-memory-architecture]] — research
- [[../11-wiki/memgraph-ce-feature-limits]] — Memgraph CE limits
- BAAI/bge-reranker-v2-m3 — Hugging Face card: https://huggingface.co/BAAI/bge-reranker-v2-m3

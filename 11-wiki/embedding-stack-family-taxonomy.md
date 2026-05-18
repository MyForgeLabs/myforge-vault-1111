---
name: Embedding-stack család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/embedding, taxonomy, evergreen, ml, vector-search, bge-m3, clip]
---

# Embedding-stack család taxonomy

> [!info] TL;DR
> A vault-ban **6 embedding-Concept + 4 vector-Concept + 17 wiki-mention** szétszórva, de **nincs egy embedding-stack referencia**. A vault 3 különböző embedding-model-t használ párhuzamosan (bge-m3 text, CLIP image, Memgraph native vector-index), és az érintett `Embedding poisoning` anti-pattern is itt él. Ez a wiki egységes embedding-stack-referencia.

## Cluster-members

| Concept | Réteg | Forrás |
|---|---|---|
| bge-m3 embedding | text-encoder | wiki/sv-04-context-knowledge-graph |
| bge-m3 model | text-encoder | session |
| bge-m3 CPU embedding | infra | session |
| bge-m3 sentence-transformers embedding on CPU | infra | session |
| CLIP image embedding | image-encoder | session |
| CLIP image embedding on CPU | infra | session |
| Embedding poisoning | anti-pattern | session |
| vector | meta | session |
| Memgraph native vector-index | infra/store | memory + wiki |
| bge-m3 ONNX optimization | infra (perf) | session |

## A 3 embedding-réteg

### 1. Text-encoder réteg: bge-m3
**Mire:** vault-content (wiki/session/skill) + KO-DB triplet semantic-keresés.

| Property | Érték |
|---|---|
| **Model** | `BAAI/bge-m3` (multilingual, magyar + angol jó) |
| **Dim** | 1024 |
| **Library** | `sentence-transformers` (Python) |
| **Hardware** | CPU-only (vault-meta context, GPU NEM kell) |
| **Speed** | warm: ~50 chunk/sec, cold-start ~12s (model-load) |
| **Optimization** | ONNX-runtime → 2-3× speedup measured |

**Process-pool minta:** cold-start 12s amortizációja → process-pool keeps the model loaded (B-7 axis 19-80× speedup).

**Anti-pattern:** per-request model-load (cold-start 12s minden hívásnál). Helyette: warm-daemon vagy in-process pool.

### 2. Image-encoder réteg: CLIP
**Mire:** image semantic-search (Adobe Firefly board, KGC asset-library).

| Property | Érték |
|---|---|
| **Model** | OpenAI `CLIP ViT-B/32` vagy `openai/clip-vit-base-patch32` |
| **Dim** | 512 |
| **Hardware** | CPU-only még működik, de lassú (~5 img/sec) |
| **Cross-modal** | text → image search ugyanazon vektor-térben |

**Use-case:** asset-library „pirosautós kép" keresés ↔ image-content match.

### 3. Vector-store réteg: Memgraph native vector-index
**Mire:** indexelt cosine-search a fenti 2 model output-ján.

**Memgraph CE 3.9.0 native:**
- `CREATE VECTOR INDEX <name> ON :Label(embedding) WITH config {'dimension': 1024, 'metric': 'cos'}`
- `vector_search.search(node_label, query_vector, top_k)` — **mean 1ms / p95 2.6ms** (volt numpy-cosine 280ms ⇒ **280× speedup**)
- Multi-namespace OK (Chunk 2829 / SkillChunk 462 / Entity 8997 párhuzamosan, 0 cross-namespace interferencia)

→ [[memgraph-ce-feature-limits]] · [[vendor-feature-verify-before-workaround]]

## Anti-pattern: Embedding poisoning

**Mintázat:** ellenfél olyan szöveget tesz a corpus-ba, ami **mesterségesen high-similarity** a target-query-vel — keresési-eredményt manipulálja.

**Védelem:**
1. **Source-trust score** — minden chunk-hoz `source_type` (wiki / session / skill / external) + bizalmi-súly
2. **Cross-source corroboration** — top-K-ban legalább 2 különböző source-type → eredmény, különben gyenge-bizalom-flag
3. **Embedding-freshness** — `vault-embed-freshness` script veresége: stale chunk-ek (>7 nap) automatikus re-encode
4. **Outlier-detection** — chunk-density anomália (1 fájl 50+ chunk-kal high-similarity 1 query-re) → flag

→ Layer 2.5/2.6 cascade [[layered-eval-cascading-pattern]]

## Reusable szabályok

1. **Model-választás dim-egyenes**: bge-m3 1024-dim, CLIP 512-dim — **NE keverd** ugyanazon vector-index-ben (Memgraph type-error)
2. **CPU-only OK** dev-szerverekre — production-trafffic alatt is mehet, GPU csak ha >1000 enc/sec kell
3. **Multilingual model** (bge-m3) ⇒ magyar+angol egy térben, nem 2 külön index
4. **Process-pool** warm-daemon-ban a model — cold-start amortizáció
5. **ONNX runtime** opt-in (`VAULT_EMBED_ONNX=1` jellegű flag) — 2-3× speedup, de operational-complexity
6. **Native vector-index > numpy-cosine** — 280× speedup, Memgraph CE 3.9.0+ kötelező
7. **Embedding-freshness watchdog** — `vault-embed-freshness` script heti audit
8. **Cross-source corroboration top-K-ban** — anti-poisoning gate

## Cross-namespace use-case mátrix

| Namespace | Encoder | Dim | Index-név | Mire |
|---|---|---|---|---|
| `:Chunk` (vault-content) | bge-m3 | 1024 | `vault_chunk_idx` | wiki/session/skill semantic |
| `:SkillChunk` | bge-m3 | 1024 | `skill_chunk_idx` | skill-discovery |
| `:Entity` | bge-m3 | 1024 | `entity_idx` | concept-cluster (Round-1..3 alap) |
| `:Asset` (jövőbeli) | CLIP | 512 | `asset_image_idx` | KGC/Adobe image |

## Tooling

- `vault-embed --backfill <dir>` — bge-m3 backfill folder-re
- `vault-search "<q>" --top-k N [--json]` — semantic-cosine on `:Chunk`
- `vault-ko-query --semantic` — semantic → KO-DB bridge (LIKE-fallback ha Memgraph down)
- `vault-embed-freshness` — stale-chunk re-encode trigger
- `vault-vector-index-migrate` — index-config migration script

## Kapcsolódó

- [[memgraph-ce-feature-limits]]
- [[vendor-feature-verify-before-workaround]]
- [[layered-eval-cascading-pattern]]
- [[hybrid-bm25-semantic-rrf-pattern]]
- [[reranker-cost-optimization-not-size]]
- [[two-tier-graph-extraction]]

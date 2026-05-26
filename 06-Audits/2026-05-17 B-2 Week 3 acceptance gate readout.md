---
name: B-2 Week 3 acceptance gate readout
type: audit
tags: ["#type/audit", "#project/sv", "sv-2", "acceptance-gate"]
created: 2026-05-17
sprint: B-2 Memory architecture (semantic-fetch via Memgraph)
adr: 07-Decisions/2026-05-12 sv-1 memory architecture arch.md
status: 🟡 PARTIAL PASS — 1/3 metric meet target, 2/3 need re-calibration
---

# B-2 Week 3 acceptance gate readout (2026-05-17)

## Mért metrikák

| Metrika | Cél (ADR) | Mért | Status | Megjegyzés |
|---|---|---|---|---|
| **Context-load time** | <10s | ~14s | 🔴 FAIL | bge-m3 cold-boot ~3-5s + in-Python cosine 1500+ chunkra ~8-9s |
| **Top-5 cosine** | >0.85 | 0.45–0.52 | 🔴 FAIL | de **a relevancia helyes** — célirányos query helyesen találja a top-fájlokat. Target unrealistic technical-Hungarian-tartalmra bge-m3-mal |
| **Token budget** | <5K | ~5.4K (kombinálva) | 🟡 NEAR | KO-DB top-6 = 1.2K, vault-search top-5 = 0.6K, working ~1K, episodic ~2.5K. Csípésre csökkenthető |

## Mit jelent ez

### Latency (14s vs <10s cél)

**Diagnózis:** minden vault-search hívás újraindítja a `bge-m3` modellt (391 weight-fájl, ~3-5s) + in-Python cosine scan a teljes Memgraph chunk-halmaz felett (~8-9s 1500+ chunkra).

**3 lehetséges megoldás:**

1. **vault-search-server daemon** — long-running process, model warm-on-disk, Unix-socket API. Cold-boot eltünik, csak a cosine scan marad → ~2-3s/query.
2. **Memgraph MAGE vector-index** — natív vector-similarity Memgraph Enterprise / MAGE module-ban. Cold-boot megmarad, de a cosine sub-second.
3. **Pre-computed cache** — chunk-vektorok JSON-vagy-binary cache-be a daemon-startup-on betöltve, runtime csak query-embed + numpy dot-product (10x gyorsabb mint pure-Python loop).

**Ajánlott Day-0:** #1 (server daemon) — legkisebb operatív változás. #3 a quick-and-dirty backup.

### Cosine score (0.5 vs >0.85 cél)

**Diagnózis:** bge-m3 multilingual model 0.85+ cosine ~majdnem-azonos szövegen produkál. Releváns multipligozott-Hungarian technical content típikusan 0.4-0.65 közt. A `>0.85` cél a Phase A research idején lett írva, **bge-m3-ra nem realisztikus**.

**3 lehetőség:**

1. **Cél átkalibrálás:** `>0.45 top-1`, `>0.40 top-5 mean` — empírikusan validálva a jelenlegi 1500 chunkkal.
2. **Re-ranker addition** — bge-reranker-v2-m3 a top-20 fölött (2-pass: retriever → reranker), célirányosabb top-5.
3. **Hibrid score:** cosine + BM25 + provenance-bonus — wikipedia-style "weighted score" több jelből.

**Ajánlott:** #1 most (re-calibrálás), #2 csak ha tényleg recall-probléma.

### Token-budget (5.4K vs <5K)

**Diagnózis:** csak épphogy átlóg. A KO-DB top-6 JSON sok overhead (1.2K) — text-mode 0.4K. Ha a skill text-mode-ot használ JSON helyett, vissza vagyunk <5K-n.

**Quick fix:** `load-session-context` SKILL.md frissítve, hogy text-mode legyen a default a KO-DB readout-ra.

## Acceptance verdict

**🔴 NEM teljesül a `sv-phase-b2-done` git-tag** — 2/3 metric célt nem éri el a jelenlegi konfigurációval. Két opció:

A) **Re-calibrálás** — frissíteni az ADR target-eket realisztikusra (cosine >0.45, token <5.5K), context-load <10s marad de daemon-na bővítve.
B) **Sprint folytatás** — Week 4-be: vault-search-server daemon + cosine re-ranker + KO-DB text-mode default → Week 5 re-mérés.

**Ajánlott:** B — még 1 sprint-hét a megoldásokra, aztán passable acceptance.

## Mit hozott azért a hét (B-2 Week 3 munka 2026-05-17 körül)

- ✅ `/usr/local/bin/vault-search` symlink (PATH-on)
- ✅ `vault-ko-query --semantic` Bridge (B-1↔B-2)
- ✅ Wiki re-embed 8 → 725 chunk (+9000%)
- ✅ ADR re-embed (28 fájl, ~270 chunk)
- ⏳ Session re-embed folyamatban
- 🔴 Acceptance gate metric-fail (latency + cosine)

## Chunk-count metric pitfall (2026-05-17 audit-finding)

A `977 chunks embed-elve` jelzés a Day-0 status-ban **félrevezető volt**. Valós szétbontás:
- 11-wiki/: **8** chunk (csak Karpathy-pattern)
- 07-Decisions/: 0
- 08-Sessions/: 0
- 02-Projects/: 0
- skill-fájlok + egyéb: **969**

Tehát a 977 chunk ~99%-a skill-tartalom, NEM vault-knowledge. A semantic-search vault-content-re ezért gyenge találatokat adott (max 0.36 cosine). **Tanulság:** chunk-count metric önmagában megtévesztő — coverage-bontás per source-type kötelező a future audit-okban. `vault-embed-freshness` ezért per-dir vault-coverage-et és stale-count-ot riportol.

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-1 memory architecture arch]] — eredeti ADR
- [[../11-wiki/sv-01-memory-architecture]] — research-háttér
- [[../02-Projects/superintelligent-vault]] — B-2 sprint host
- [[../00-Meta/skills/load-session-context/SKILL]] — fogyasztó (KO-DB layer)

---
name: B-4 Week 3 vault-search-server :SkillChunk RPC
type: audit
sprint: B-4
created: 2026-05-17
updated: 2026-05-17
tags: [sprint/b-4, layer/tool-composition, infra/daemon, perf/bench]
---

# B-4 Week 3 — `vault-search-server` `:SkillChunk` RPC + warm encode reuse

> [!info] Kontextus
> A B-4 Week 2 phase 2.5-ben létrejött a `:SkillChunk` Memgraph-namespace (462 skill, `skill_chunk_vec` native vector-index ÉLES). Eddig a `vault-skill-search` CLI per-invokáció önállóan importálta a `mgclient`-et és a daemon `encode` RPC-jét hívta egy külön round-trip-ben — most folded: **egyetlen `search_skills` RPC**, ami daemon-oldalon csinálja az encode-ot (warm bge-m3) és a Memgraph `vector_search.search`-t.

## 1. Architektúra — multi-namespace daemon + encode-reuse pattern

**Két különböző réteg a daemon-ben:**

| Namespace | Storage | Search-path | Daemon szerepe |
|---|---|---|---|
| `:Chunk` (B-2, 2829 vault chunk) | numpy float32 RAM-ben (`ChunkStore.by_ns`) | in-process cosine batched dot-product | **Adatot is + modellt is** tart RAM-ben |
| `:SkillChunk` (B-4, 462 skill) | Memgraph native vector-index | `vector_search.search` Memgraph-szerver | **Csak modellt** tart RAM-ben, search delegated |

A `:SkillChunk` daemon-value-add **kizárólag a warm bge-m3 reuse**: nincs új RAM-overhead (a node-ok Memgraph-ban élnek), de a per-call cold-load (~5s) kiesik.

### Új RPC method-ok

```jsonc
// search_skills — folded encode + Memgraph search
{"method": "search_skills", "query": "<q>", "top_k": 3, "threshold": 0.0, "model": "bge-m3"}
// → {results: [{path, name, description, source_root, score}], encode_ms, search_ms, total_ms, index, model}

// encode_skill — alias of encode (semantic clarity for skill-search callers)
{"method": "encode_skill", "text": "<t>"}
// → {vector: [1024 floats], model: "BAAI/bge-m3", dim: 1024}
```

### Daemon `health` válasz bővült

```json
{
  "rpc_methods": ["health", "reload", "search", "encode", "search_skills", "encode_skill"],
  "skill_vector_index": "skill_chunk_vec",
  "skill_vector_label": "SkillChunk"
}
```

## 2. CLI módosítás — `--server` / `--no-server` flag

A `vault-skill-search` `search()` függvény két végrehajtási útvonalat ismer:

1. **Server-mode** (default, ha daemon-socket él): egyetlen `search_skills` RPC.
2. **Cold-mode** (`--no-server` vagy daemon down): legacy in-process encode + mgclient `vector_search.search`.

**Graceful fallback verifikálva**: ha `--server` és daemon RPC-error / socket-down → stderr-figyelmeztetés + automatikus cold-mode-ra váltás, ugyanaz az eredmény (top-1 azonos).

## 3. 5-query bench — cold vs server

CLI-szintű (subprocess timer, full Python startup + imports):

| Query | Cold-mode total | Server-mode total | Server enc / search |
|---|---:|---:|---|
| CI pipeline setup | 322ms | 357ms | 249.0 / 8.2 ms |
| deploy to Azure | 369ms | 332ms | 270.1 / 6.5 ms |
| WordPress block development | 308ms | 349ms | 244.5 / 7.4 ms |
| Figma design import | 326ms | 286ms | 221.0 / 4.6 ms |
| story creation | 290ms | 276ms | 193.5 / 3.5 ms |
| **mean** | **323ms** | **320ms** | — |
| **p95** | **369ms** | **357ms** | — |

**Delta: -3ms (-0.9%).** A CLI-szinten **nincs érdemi gyorsulás**.

### Miért nem 50ms p95?

A feladat-leírás `~30ms encode RPC + 8-13ms search + format = <50ms total p95` becslése **optimista volt**:

- bge-m3 single-text encode CPU-on (EPYC 9354P) **~120-140ms** stabil forward-pass (XLM-RoBERTa-large, 1024-dim). Ezt nem lehet "warm reuse"-zal lecsökkenteni — a modell már warm, csak a forward-számítás zajlik.
- Python startup + stdlib + mgclient import ≈ **90ms** baseline overhead per CLI-call.
- Cold-mode már a meglévő architektúrában is daemon-encode-ot használt (`encode_one()` daemon-first, in-process fallback), így a "cold" baseline sem volt valóban cold.

### Pure-RPC mérés (CLI-overhead nélkül, persistent Python)

| Méret | search_skills (folded) | legacy 2-RPC (encode + mgclient search) |
|---|---:|---:|
| mean | 135ms | 119ms |
| p95 | 149ms | 127ms |

A folded RPC **kis mértékben lassabb** (+16ms mean), mert egyetlen daemon-thread sorba végzi az encode-ot és a Memgraph-roundtrip-et, míg a 2-RPC útvonalon a CLI eközben elindítja a Memgraph-connect-et párhuzamosan. **A daemon encode 120-140ms keménymag latency.**

## 4. RAM-overhead

| Mérés | Restart előtt | Restart után |
|---|---:|---:|
| RSS | ~1.7G | ~1.7G |
| Új namespace RAM-ben | — | **0 MB** (várt) |

A `:SkillChunk` Memgraph-ban él, a daemon csak a már betöltött bge-m3-at használja. **Az `RPC_methods` whitelist + 2 új handler ~5KB-nyi Python-kód növekedés**, runtime memória-overhead nulla.

## 5. Valódi értékajánlat

Bár a CLI-perf delta semleges, a Week 3 megoldás **architektúrális tisztulás**:

1. **Egyetlen belépési pont** a skill-search-hez: minden query a daemonon megy keresztül. Audit-log, rate-limit, future cache trivializálhatóvá válik.
2. **Eltüntetett kapcsolat-csatorna**: a CLI-nek nem kell direkt mgclient-konnekciót nyitnia. Future Memgraph-mozgatás (pl. más portra / authba) csak daemon-konfig.
3. **MCP-baseline kész**: a Week 4 `/opt/vault-mcp/` MCP-server közvetlenül a `search_skills` RPC-re hívhat. Egy MCP tool-call → daemon RPC → eredmény, **CLI-startup nélkül**. **Ezen a szinten az encode ~120ms a teljes tool-latency lesz** (token-overhead 5K → <100, ami a Week 4 fő ROI-ja).

## 6. Files

- `/usr/local/bin/vault-search-server` — `search_skills` + `encode_skill` RPC + `health` bővítés (~95 sor új kód)
- `/root/obsidian-vault/.vault-tools/scripts/vault-skill-search.py` — `--server`/`--no-server` flag + `_daemon_rpc()` refaktor + 2-mode `search()`
- `/usr/local/bin/vault-search-server.bak.20260517-skillchunk-rpc` — backup
- `/root/obsidian-vault/.vault-tools/scripts/vault-skill-search.py.bak.20260517-skillchunk-rpc` — backup

## 7. systemd

- `vault-search.service` **változatlan unit-fájl**, `systemctl restart` ~8s warm-up.
- Restart-after-deploy: 2026-05-17 06:01 UTC, ✅ active.
- Health-check: `rpc_methods` 6 elemet listáz (volt 4), `skill_vector_index = skill_chunk_vec`.

## 8. Smoke-tests verifikálva

| Teszt | Eredmény |
|---|---|
| `search_skills` RPC `top_k=3` | ✅ 3 valid SkillChunk hit, score-sorted |
| `encode_skill` RPC | ✅ 1024-dim vektor, model: BAAI/bge-m3 |
| `vault-skill-search "CI pipeline setup"` (auto) | ✅ server-mode, top-1 `bmad-tea-testarch-ci` (0.626) |
| `vault-skill-search --no-server "deploy to Azure"` | ✅ cold-mode, top-1 `azure-deploy` (0.734) |
| Graceful fallback (socket=/tmp/nonexistent.sock) | ✅ stderr-warning + cold-mode, same top-1 |
| Backward-compat `encode` RPC | ✅ változatlan (vault-search.py használja) |

## 9. Week 4 follow-up

| Munkacsomag | Cél |
|---|---|
| `/opt/vault-mcp/` MCP-server | Stdio-MCP wrapper a daemon-RPC-k felett. Tool-name: `vault_search_skills`, input: `{query, top_k?}`. Eltünteti a CLI-startup overhead-et — egy Claude Code tool-call ~140-160ms total. |
| Token-overhead audit | A jelenlegi `Skill.tool` 243 skill leírása ~5K tokenbe kerül per session-init. MCP-vel csak a top-K relevant skill-leírás kerül kontextusba → várt **<100 token / call** Sonnet-szinten. |
| Skill auto-trigger | A `search_skills` integrálható a Skill-router-be: user-prompt → top-3 skill → auto-load suggestion. |

## 10. Bench-script

A bench-eredmények reprodukálhatók:

```bash
/tmp/bench-skill-rpc.sh   # 5-query × 2 mode, JSON breakdown
```

## Kapcsolódó

- [[2026-05-17 B-4 Week 2 skill-embedding + search]] — Week 2 phase 2.5 baseline
- [[../11-wiki/sv-04-tool-composition]] — B-4 sprint state-of-art
- [[../11-wiki/memgraph-ce-feature-limits]] — native vector-index multi-namespace
- [[../07-Decisions/2026-05-12 sv-4 tool composition arch]] — eredeti arch ADR

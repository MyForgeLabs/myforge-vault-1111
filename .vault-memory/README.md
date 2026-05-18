# `.vault-memory/` — Memgraph + LlamaIndex hibrid memory-stack

Vault-szintű **vector + graph** hibrid memory infrastructure a 3-rétegű (working / episodic / semantic) tudás-keresésre.

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-1 memory architecture arch.md]]
**Research:** [[../11-wiki/sv-01-memory-architecture.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]
**Schema (shared B-7):** [[../00-Meta/graph-schema.yml]]
**Sprint-pattern:** [[../11-wiki/sprint-day-0-skeleton-first.md]]

## Tartalom

```
.vault-memory/
├── README.md                   ez a fájl
├── docker-compose.yml          Memgraph container config (NEM running Day 0-n)
├── config/
│   └── llamaindex-config.yml   SchemaLLMPathExtractor + embedding config v0.1
├── scripts/
│   ├── vault-embed.py          Markdown → Memgraph vector-index (SKELETON)
│   └── vault-search.py         Hybrid retriever CLI (SKELETON)
└── (data/ + logs/ Memgraph-volume Week 1 Day 1-én jön létre, gitignored)
```

## Status — 2026-05-13 (Phase B-2 sprint kickoff, Day 0)

- [x] **Day 0 commit**: docker-compose.yml + 2 script-skeleton + llamaindex-config + README
- [ ] **Week 1 Day 1**: `docker-compose up -d` + Memgraph Lab UI accessibility check (Tailscale-only)
- [ ] **Week 1 Day 2**: `pip install llama-index llama-index-graph-stores-memgraph sentence-transformers` (`.notebooklm-venv`-be vagy új `.vault-venv`-be)
- [ ] **Week 1 Day 3**: bge-m3 modell-letöltés + smoke embedding (1 fájl test)
- [ ] **Week 1 Day 4-5**: Schema-YAML alapján entity-extraction smoke (5 fájl test, manual review)
- [ ] **Week 2 Day 1-2**: Batch backfill — `11-wiki/` + `02-Projects/` + `05-Memory/` + `07-Decisions/` (~150 fájl)
- [ ] **Week 2 Day 3**: bge-m3 vs multilingual-e5 vs LaBSE benchmark 50 magyar query-n (ADR-Risks #2)
- [ ] **Week 2 Day 4**: `vault-search` real hybrid retriever (vector top-K + graph-traversal + RRF)
- [ ] **Week 2 Day 5**: File-watch hook `vault-autosave` mellé (10 perc cron)
- [ ] **Week 3 Day 1-2**: MemGPT-stílusú virtual context — `load-session-context` skill rewrite
- [ ] **Week 3 Day 3-4**: Reflection-loop (heti cron — community-summary auto-draft a wikibe)
- [ ] **Week 3 Day 5**: Acceptance gate — context-load 30s→<10s + top-5 >0.85 + token 15-20K→<5K

## ENV-flag backout

```bash
export VAULT_SEARCH_MODE=grep   # vault-search visszaesik file-grep fallback-re
docker compose -f .vault-memory/docker-compose.yml down -v   # Memgraph stop + data drop
```

A klasszikus `load-session-context` skill **megmarad** mint fallback. Semmi nem irreverzibilis.

## Költség-kalkuláció (Tier-$50 cél)

| Komponens | Cost | Megjegyzés |
|---|---|---|
| Memgraph Docker | $0 | self-hosted, in-memory, ~200MB RAM |
| bge-m3 embedding | $0 | local CPU/GPU, no API |
| LlamaIndex Python | $0 | open-source |
| SchemaLLMPathExtractor (Haiku-API) | ~$5-10 / batch backfill | egyszeri 240 fájl |
| Subsequent inkrementális | ~$0.10/nap | csak új/módosított fájlokra |

**Becsült cap:** $15-20/hó steady state (Haiku-only). Tier-$50-ben bőven elfér.

## Kapcsolódó

- B-7 sprint (közös Memgraph + schema): [[../07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch.md]]
- B-1 sprint (KO-DB foundation, SQLite): [[../.vault-ko/README.md]]
- B-3 sprint (parallel, eval-pipeline): [[../07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md]]

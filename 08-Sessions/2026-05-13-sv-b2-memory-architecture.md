---
name: sv-b2-memory-architecture
type: session
project: sv-b2-memory-architecture
status: closed
started: 2026-05-13T06:22+00:00
ended: 2026-05-13T06:30+00:00
agent: unknown
# B-3 eval fields (auto-backfilled, null = not yet evaluated)
eval_score: null
eval_critique: null
hallucination_flag: false
eval_l2_agreement: null
tags: ["#type/session", "#project/sv-b2-memory-architecture"]
---

## Pre-loaded context

**Slug:** `sv-b2-memory-architecture` — a Superintelligent Vault projekt B-2 sprint-jének Day 0 kickoff session-je. Közvetlen folytatása az `obsidian-vault` session-nek (2026-05-12 20:56 zárt), nincs új user-context.

**Parent projekt:** [[02-Projects/superintelligent-vault]] — B-1 sprint Day 0 már lement (KO-DB skeleton, projekt-fájl, Backlog 11 task). B-2 most következik.

**ADR:** [[07-Decisions/2026-05-12 sv-1 memory architecture arch]]:
- **Tech-stack:** Memgraph (in-memory, Neo4j-kompatibilis, beépített vector-search) + LlamaIndex SchemaLLMPathExtractor + bge-m3 lokális embedding
- **3-rétegű memory:** Working (`08-Sessions/<focused>`) + Episodic (`01-Daily/+10-raw/`) + Semantic (`11-wiki/+07-Decisions/+05-Memory/+02-Projects/`)
- **2-3 hetes sprint, B-3-mal parallel.** Depends on: B-1 (KO-DB foundation), B-7 schema-YAML (már megvan)
- **Acceptance:** vault-search top-5 >0.85, context-load 30s→<10s, 75% token-reduction (15-20K → <5K)

**Research:** [[11-wiki/sv-01-memory-architecture]] (249 source), [[11-wiki/sv-06-world-model-knowledge-graph]] (közös Memgraph infrastruktúra)

**B-1 sprint state (parallel running):** Day 0 ✓ committed (skeleton `.vault-ko/`), Week 1 kalibráció még nem indult. B-2 NEM blokkolja a B-1-et — független infrastruktúra (KO-DB SQLite vs Memgraph), bridge csak Week 2-ben.

**B-7 schema reuse:** [[00-Meta/graph-schema.yml]] (9 entity + 6 relation) **már létezik** — LlamaIndex SchemaLLMPathExtractor input common. B-2+B-7 közös infrastruktúrás.

**Sprint-Day-0 playbook:** [[11-wiki/sprint-day-0-skeleton-first]] — scaffold-only commit, NEM funkcionális kód. Week 1-3 jön a Docker-up + embedding-pipeline + reflection-loop.

## Cél

B-2 sprint Day 0 skeleton-first commit a `[[11-wiki/sprint-day-0-skeleton-first]]` playbook szerint. Funkcionális kód NULLA; Week 1-3 jön a Docker-up + LlamaIndex + bge-m3 + reflection-loop. Cél verifikálható: `--help`/`--dry-run` runnable, docker-compose validálható, schema-input létezik.

## Events


- 06:27 — B-2 Day 0 DONE — .vault-memory/{docker-compose.yml,scripts/{vault-embed.py,vault-search.py},config/llamaindex-config.yml,README.md} skeleton commit. Tech-stack: Memgraph in-memory (port 7687, 512MB cap) + LlamaIndex SchemaLLMPathExtractor + bge-m3 lokális embedding (1024-dim multilingual). 3-rétegű memory mapping (working: 08-Sessions, episodic: 01-Daily+10-raw, semantic: 11-wiki+07-Decisions+05-Memory+02-Projects). Schema reuse: 00-Meta/graph-schema.yml (9 entity + 6 reláció, B-7 Day 0-ban már kész). Both scripts --help + --dry-run működnek, docker compose v5.1.3 elérhető (docker-compose hyphenated NEM). .gitignore frissítve: data/+logs/+embeddings-cache/+__pycache__/ excluded. 02-Projects/superintelligent-vault.md B-2 status 'Day 0 ✓ (2026-05-13)'-re frissítve. Backlog: B-2 1 future-line → 12 részletes task (Day 0 ✅ + Week 1-3 day-by-day breakdown + acceptance gate).
## Summary

**B-2 sprint Day 0 ✓** — `[[11-wiki/sprint-day-0-skeleton-first]]` playbook második élő alkalmazása (első: B-1 Crystallization).

**Új fájlok (5):** `.vault-memory/docker-compose.yml` (Memgraph 512MB cap, port 7687) + `.vault-memory/scripts/vault-embed.py` (no-op `embed_stub`) + `.vault-memory/scripts/vault-search.py` (no-op `search_stub`, ENV `VAULT_SEARCH_MODE` 4 mode) + `.vault-memory/config/llamaindex-config.yml` v0.1 (bge-m3 + SchemaLLMPathExtractor + 3-rétegű memory-mapping) + `.vault-memory/README.md`.

**Módosított (3):** `02-Projects/superintelligent-vault.md` (B-2 status `Day 0 ✓`), `04-Tasks/Backlog.md` (B-2: 1 future-line → 12 day-by-day task Week 1-3 + acceptance gate), `.gitignore` (data/+logs/+embeddings-cache excluded).

**Verifikáció:** `vault-embed --help`/`--dry-run` ✓ (1 fájl, 5.3KB, no-op stub), `vault-search "..."` ✓ (no-results skeleton message), `docker compose` v5.1.3 elérhető (hyphenated `docker-compose` NEM), Memgraph image később pull-olódik Week 1 Day 1-én.

**Schema reuse:** [[00-Meta/graph-schema.yml]] (B-7 Day 0 outputja) közvetlenül LlamaIndex SchemaLLMPathExtractor input. **B-2 + B-7 közös infrastruktúra** — két tengely, egy Memgraph DB.

## Learnings → memória

**1. Skeleton-first playbook (B-1 után 2. élő alkalmazás) — patterns konvergálnak** — Mindkét sprint Day 0 ugyanaz a struktúra: `.vault-<feature>/` mappa + `README.md` + `scripts/` (no-op skeletonok `--help`+`--dry-run`-nal) + `config/` (YAML) + projekt-fájl status update + Backlog detailed breakdown + `.gitignore` runtime-data exclude. **A playbook validálva** — 30 perc Day 0 alatt teljes scaffold.

**2. Cross-sprint schema reuse — B-7 schema-YAML először, B-2/B-7 közös** — A B-7 graph-schema (9 entity + 6 reláció) **előbb készült** mint a B-2 (mert előző session-ben ez volt sorra), és **most B-2 közvetlenül használja** LlamaIndex inputként. **Tanulság:** ha sprint-X és sprint-Y közös schema-ra/data-ra épül (B-2 + B-7 mind Memgraph), érdemes **a schema-t előbb**, mint bármelyik konkrét sprint kódját. Sprint-sequence: schema → infra → integration.

**3. `docker compose` vs `docker-compose` (modern syntax)** — Docker v29.x-tól a hyphenated `docker-compose` CLI **NEM telepítve default-on** Ubuntu 24.04-en, helyette `docker compose` (space-separated, plugin). Skeleton-config maga compatible mindkettővel, de a doku/README parancsait `docker compose`-ra kell írni (modern).

## Next session

1. **B-2 Week 1 Day 1 — Memgraph Docker-up** — `docker compose -f .vault-memory/docker-compose.yml --env-file /root/.vault-config/memgraph.env up -d`. Smoke: `docker exec -it vault-memgraph mgconsole > MATCH (n) RETURN count(n);` → 0. Memgraph Lab UI port 3000 nginx-proxy hozzáadás (Tailscale-only access pattern, ld. [[05-Memory/Dashboard-access]]).
2. **B-2 Week 1 Day 2 — Python-deps install** — `pip install llama-index llama-index-graph-stores-memgraph sentence-transformers` (`.notebooklm-venv`-be vagy új `.vault-venv`-be). bge-m3 modell-letöltés (~2.3GB, első runkor cached).
3. **B-2 Week 1 Day 3 — Smoke embedding 1 fájl** — `.vault-memory/scripts/vault-embed.py` real impl (no-op stub helyett): chunkolás ## szerint, bge-m3 embed, Cypher CREATE, query-back.
4. **Egyéb (lower-priority):** B-1 Week 1 kalibráció (50 sample Learning bullet gold-label) — párhuzamosan B-2 Week 1-gyel.

## Propagation log

**2026-05-13 06:30 — Auto-propagation (user-confirmed):**

- **L1+L2** (skeleton-first 2. validation + cross-sprint schema-first) → APPEND [[11-wiki/sprint-day-0-skeleton-first]] 2 új szekció: "Validations" (B-1+B-2 ~30min Day 0, time-cap szabály) + "Cross-sprint reuse" (schema előbb mint kód, B-2/B-7 példa, general sprint-sequence rule)
- **L3** (`docker compose` vs `docker-compose` modern syntax) → APPEND [[05-Memory/Infrastructure#Docker / Docker Compose — modern syntax (2026-05-13)]] új szekció a Postgres-szekció ELŐTT (v29.4.1 + v5.1.3 plugin verzió + modern-vs-legacy tábla)

**Új fájlok ebben a session-ben (5):**
- `.vault-memory/docker-compose.yml`
- `.vault-memory/scripts/vault-embed.py`
- `.vault-memory/scripts/vault-search.py`
- `.vault-memory/config/llamaindex-config.yml`
- `.vault-memory/README.md`

**Módosított (5):**
- `02-Projects/superintelligent-vault.md` (B-2 status `Day 0 ✓`)
- `04-Tasks/Backlog.md` (B-2: 1 → 12 task)
- `.gitignore` (.vault-memory/data,logs,embeddings-cache excluded)
- `11-wiki/sprint-day-0-skeleton-first.md` (+2 szekció)
- `05-Memory/Infrastructure.md` (+1 szekció: Docker syntax)


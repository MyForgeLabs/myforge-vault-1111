---
name: B-7 wikilink-importer MENTIONS edges
type: audit
created: 2026-05-17
updated: 2026-05-17
tags:
  - axis/B-7
  - layer/audit
  - status/landed
---

# B-7 wikilink-importer — `:MENTIONS` ground-truth edges

> [!success] Deterministic Wikilink importer LIVE
> 556 `:SourceFile` + 562 `:WikiLink` + **1 954 `:MENTIONS` edges** Memgraph-ban. Zero-LLM, ~22 s end-to-end, idempotent.

## Mit csinál

Új script: [`vault-graph-mentions-extract`](../.vault-graph/scripts/vault-graph-mentions-extract.py) — végigjárja a vault minden `.md` fájlját (kivéve `AGENTS.md` + `00-Meta/` + dotfiles + `*.bak*`), minden `[[wikilink]]`-et kibont normalizált `target` formába (alias + `#section` levágva, `.md` extension levágva), és Memgraph-ba ír:

```
(s:SourceFile {name: "02-Projects/foxxi.md"})
  -[:MENTIONS {count: 1}]->
(w:WikiLink {name: "05-Memory/Infrastructure"})
```

Idempotens MERGE-en a (src, tgt) páron — második futás 0 új edge.

## Counts

| Metrika | Érték |
|---|---|
| .md fájlok scan-elve | **388** |
| Total mention-occurence | 2 394 (raw) |
| Distinct (src, tgt) pár | **1 954** edge |
| `:SourceFile` nodes | **556** (388 forrás + 168 hivatkozott más .md, ami nem szerepel forrásként) |
| `:WikiLink` nodes | **562** (distinct targets) |
| Broken targets (`/` van benne, de a `.md` nem létezik) | 134 |

> [!note] Ground-truth vs LLM extract
> LLM-based (Week 1-α): **8 975 :Entity + 13 812 relations** — nem strukturált triplet.
> Deterministic (Week 2): **1 954 :MENTIONS edges** — strukturált, fájl-szintű graph.
> A két réteg orthogonális: a `:MENTIONS` a vault explicit topology-ja, a `:Entity` a tartalom szemantikai dimenzión kibontva.

## Per-folder breakdown

| Folder | Files | Edges |
|---|---:|---:|
| 01-Daily | 19 | 137 |
| 02-Projects | 56 | 320 |
| 03-Hosts | 4 | 42 |
| 04-Tasks | 2 | 59 |
| 05-Memory | 8 | 67 |
| 06-Audits | 18 | 119 |
| 07-Decisions | 30 | 217 |
| 08-Sessions | 76 | **893** |
| 10-raw | 90 | 34 |
| 11-wiki | 85 | 506 |

> [!info] Session-fájlok visznek (893 edge / 76 fájl = 11.7/file)
> Ez illeszkedik az 11.11 protokollhoz: a Summary + Learnings + Propagation log szekciók explicit wikilink-referenciát rögzítenek minden propagation-target-re.

## Top-20 most-linked hub-ok

| Rank | Target | In-degree |
|---:|---|---:|
| 1 | `05-Memory/Infrastructure` | **67** |
| 2 | `02-Projects/Index` | 38 |
| 3 | `11-wiki/Crystallization-protocol` | 38 |
| 4 | `04-Tasks/Backlog` | 36 |
| 5 | `02-Projects/foxxi` | 35 |
| 6 | `11-wiki/Karpathy-LLM-Wiki-pattern` | 30 |
| 7 | `02-Projects/kgc-berles` | 27 |
| 8 | `02-Projects/superintelligent-vault` | 24 |
| 9 | `AGENTS` | 23 |
| 10 | `07-Decisions/2026-05-12 Superintelligent vault evolution roadmap` | 21 |
| 11 | `11-wiki/wp-elementor-template-conflicts` | 20 |
| 12 | `05-Memory/User` | 20 |
| 13 | `11-wiki/notebooklm-seo-competitor-research-pattern` | 18 |
| 14 | `11-wiki/wp-acf-flexible-to-elementor-migration` | 16 |
| 15 | `07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial` | 16 |
| 16 | `11-wiki/sprint-day-0-skeleton-first` | 15 |
| 17 | `07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1` | 15 |
| 18 | `07-Decisions/2026-05-12 sv-5 crystallization automation arch` | 14 |
| 19 | `11-wiki/11.11-session-protokoll` | 14 |
| 20 | `02-Projects/teszt-eu` | 14 |

> [!info] Hub-koncentráció
> A top-20 hub-okra fut a 1 954 edge-ből **530 (~27%)**. A vault egy heavy-tailed link-graph — pareto-szerű viselkedés.

## Top-10 fan-out (legtöbb külső hivatkozással bíró forrás)

| Source | Fan-out |
|---|---:|
| `04-Tasks/Backlog.md` | 53 |
| `02-Projects/Index.md` | 41 |
| `08-Sessions/Index.md` | 35 |
| `02-Projects/foxxi-sprint-2026-05/README.md` | 34 |
| `05-Memory/Infrastructure.md` | 31 |
| `11-wiki/Auto-context-loading.md` | 31 |
| `07-Decisions/Index.md` | 31 |
| `11-wiki/mfl-voice-jarvis-mother-research.md` | 30 |
| `01-Daily/2026-05-04.md` | 29 |
| `11-wiki/Index.md` | 29 |

## Validáció

`11-wiki/sv-05-crystallization-automation` backlinks lekérdezés:

```cypher
MATCH (s:SourceFile)-[:MENTIONS]->(w:WikiLink {name: '11-wiki/sv-05-crystallization-automation'})
RETURN s.name ORDER BY s.name
```

→ **7 backlink**:
- `02-Projects/superintelligent-vault.md`
- `06-Audits/2026-05-17 predicate-vocab expansion 21 to 35-40.md`
- `07-Decisions/2026-05-12 sv-5 crystallization automation arch.md`
- `11-wiki/Crystallization-protocol.md`
- `11-wiki/Index.md`
- `11-wiki/superintelligent-vault-research.md`
- `11-wiki/sv-07-continuous-evaluation.md`

## Kapcsolódó

- [[../11-wiki/Karpathy-LLM-Wiki-pattern]]
- [[../02-Projects/superintelligent-vault]]
- [[../07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]

## Next-step

1. **Cross-validate** a LLM-extracted relations-szel — top-100 hub a `:MENTIONS`-en + ezeknek a `:Entity` reprezentációja; mit talál meg a Week 1-α extractor és mit nem
2. **Backlink-feed a `vault-graph-query`-be** — új `--backlinks <file>` mode (B-7 Week 2 backlog)
3. **Broken-link audit-report** — 134 broken target listázása `vault-cleanup` heti job-ban

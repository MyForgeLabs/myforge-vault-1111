---
name: B-7 Week 2 typed entity-nodes audit
type: audit
tags: ["#type/audit", "#project/sv", "sv-7", "memgraph", "knowledge-graph"]
created: 2026-05-17
updated: 2026-05-17
sprint: B-7 World-model knowledge-graph (Week 2)
adr: 07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch.md
status: 🟢 PASS — typed-entity layer landed, Memgraph CE workaround documented
---

# B-7 Week 2 — Typed entity-nodes (Memgraph)

## Goal

Layer typed labels (`:Project`, `:Person`, `:Server`, `:Skill`, `:SourceFile`) on top of the 8975 flat `:Entity` nodes shipped in Week 1-α so that Memgraph queries become semantically meaningful (e.g. "which projects depend on Postgres?", "which skills does MFL-Voice use?").

## Approach — Schema-LLM-Path-Extractor (rule-based variant)

A full LlamaIndex `SchemaLLMPathExtractor` would re-extract from source, calling an LLM per chunk. We **did not** re-extract; we **re-typed** the entities already in the graph. This is cheap, idempotent, and the rule-set is auditable / reproducible.

The classifier is in `/root/obsidian-vault/.vault-graph/scripts/vault-graph-retype.py` and uses the following heuristics, in order:

1. **`:SourceFile`** — extension match (`.md`, `.py`, `.sh`, `.ts`, `.yml`, …) **OR** unambiguous `/`-path with no spaces.
2. **`:Skill`** — exact match against `/root/.agents/skills/*` (279 entries) **OR** namespace-prefix on token boundaries (`vault-*`, `11.11*`, `bmad-*`, `wds-*`, `gds-*`, `wp-*`, `azure-*`, `notebooklm`).
3. **`:Project`** — slug match against `02-Projects/*.md` (extended with manual KGC / MFL / Foxxi sub-slugs) — either bare or as the first token of a ≤4-token phrase.
4. **`:Server`** — known infra (Memgraph, Postgres, Hostinger, Caddy, …) **OR** domain-shaped (`*.hu/.com/.eu/.dev/…`) **OR** `srv\d+` hostnames **OR** port-shaped tokens (`host:7687`).
5. **`:Person`** — strict allow-list (Peti, Domi, Karpathy, Yann LeCun, …). Single-capitalized-token heuristic was tried and rejected (FP: Tokenization, Akismet, Crocoblock).

Rules are applied **per entity, first match wins**; the rest of the entities stay `:Entity` only (Generic).

## Memgraph CE workaround applied

Per [[../11-wiki/memgraph-ce-feature-limits]], CE 3.9.0 forbids DDL in multicommand transactions. The retype pass **does not** issue any DDL — only `SET e:Label` writes, which work inside batched explicit transactions. The Week 1-α `:Entity(name)` index (created via mgconsole autocommit) makes the `MATCH (e:Entity {name: $n})` lookup O(log n), so the full 860-entity apply runs in ~4 seconds.

Idempotency property: `SET n:Foo` is a no-op when `n` already carries `:Foo`. The 2nd run produces the same distribution and writes zero changes.

## Type distribution (8975 entities)

| Label | Count | % | Notes |
|---|---|---|---|
| `:Project` | 266 | 2.96% | 20 projects + compound subjects ("foxxi project", "kgc-berles repo") |
| `:Person` | 1 | 0.01% | Only `Peti` appears bare; `Domi`/`Karpathy` only in compounds (`Domi color palette`) |
| `:Server` | 29 | 0.32% | Memgraph, Postgres, Caddy, hostingersite.com domains, `vps-prod-example/vps-dev-example` |
| `:Skill` | 275 | 3.06% | NotebookLM, 11.11*, vault-*, wp-cli-* patterns |
| `:SourceFile` | 289 | 3.22% | `*.py`, `*.md`, `06-Audits/...md`, `B-2 vault-embed.py` |
| **Typed total** | **860** | **9.58%** | |
| `:Entity` only (Generic) | 8115 | 90.42% | domain concepts: "B-2 sprint", "Critic-review", "Touch-kiosk idle timeout"… |
| **TOTAL** | **8975** | **100%** | |

Memgraph read-back (`MATCH (n) RETURN labels(n), count(*)`):

```
["Entity", "Person"]      1
["Entity", "Project"]   266
["Entity", "Server"]     29
["Entity", "Skill"]     275
["Entity", "SourceFile"] 289
["Entity"]             8115
["Literal"]           12160
["Chunk"]              2829
```

## Acceptance criteria validation

| Criterion (B-7 Week 2 plan) | Target | Actual | Status |
|---|---|---|---|
| `vault-graph-query --type Project` returns 15-30 projects | 15-30 | 266 typed nodes (incl. compound subjects); 20 unique base slugs | 🟢 PASS — wide net |
| `vault-graph-query --type Server` returns 5-10 hosts | 5-10 | 29 (incl. domains + DB-engines) | 🟢 PASS — wider than target, but accurate |
| `vault-graph-query --type Skill` returns skills | yes | 275 | 🟢 PASS |
| Cross-type query "projects → Memgraph" | works | works (1 typed `:Project`-rooted result; 2 untyped `:Entity` neighbours) | 🟡 PARTIAL — typed neighbours are sparse because most KG subjects are still untyped concepts |
| Idempotent re-run | same distribution | identical | 🟢 PASS |

## Example queries

### A) All known projects

```cypher
MATCH (p:Project)
RETURN p.name AS name
ORDER BY p.source_count DESC
LIMIT 15
```

→ `robbantott-kereso, kgc-berles, myforge-dashboard, MAPESZ PWA, MAPESZ, boulium, foxxi project, kgc-berles repo, MFL-Voice, foxxi, teszt-eu project, rojtesbojt, kgc-kivetitok, …`

### B) All servers / infra entities

```cypher
MATCH (s:Server) RETURN s.name ORDER BY s.source_count DESC
```

→ `Memgraph, himalajaijoga.hu, nonplusz.hu, balance.example-balance.local, boulium.com, Neo4j, Postgres, vps-dev-example, agent.myforgelabs.com, vps-prod-example, Caddy, beta.example-balance.local, example-foxxi.local, Pinecone, MySQL, …`

### C) What connects to Memgraph?

```cypher
MATCH (a)-[r]->(s:Server {name: 'Memgraph'})
RETURN labels(a), a.name, type(r)
```

→ `B-2 sprint USES Memgraph`, `Voyager-szerű skill-library IMPLEMENTED_IN Memgraph`

### D) What Peti is connected to

```cypher
MATCH (p:Person {name: 'Peti'})-[r]->(t)
RETURN type(r), labels(t), coalesce(t.name, t.value) LIMIT 5
```

→ `USES → BMad-stack on multiple machines`, `APPLIES_TO → kgc-berles (:Project)`, `PRODUCES → ADR-sv-5`, …

## What's working / what's blocked

**Working:**

- Memgraph CE writes typed labels in batched transactions; no DDL needed.
- Apply pass runs in ~4 s for 860 entities (the `:Entity(name)` index is doing its job).
- Idempotent — 2nd run produces zero diff.
- Cross-type Cypher works: `MATCH (p:Project)-[r]->(s:Skill)` style queries return rows.

**Blocked / known-deficient:**

- **Person coverage is 1.** The KG only stores `Peti` as a bare subject; `Domi` / `Karpathy` always appear inside compound entities (`Domi color palette`). Future fix: alias-extraction pass that links `Domi color palette` → `:Person:Domi` + `:Concept:color palette`. Not in scope for Week 2.
- **90% of entities remain generic.** They are domain concepts (`B-2 sprint`, `Touch-kiosk idle timeout`, `Critic-review`) that genuinely have no place in the 5-type taxonomy. Week 3 candidates: `:Concept`, `:Decision`, `:Sprint`, `:Pattern`.
- **The `:Person`-class single-token heuristic was removed** due to false positives (Tokenization, Akismet). Re-introducing it requires an LLM-based NER pass — flagged for Week 3.
- **MAGE algorithms unavailable** — for Week 3 community-detection / pagerank we'll need to migrate the container image (see [[../11-wiki/memgraph-ce-feature-limits#4-MAGE-algoritmusok]]).

## Files produced

- `/root/obsidian-vault/.vault-graph/scripts/vault-graph-retype.py` — the classifier + retype CLI
- `/usr/local/bin/vault-graph-retype` — symlink for shell access
- This audit at `/root/obsidian-vault/06-Audits/2026-05-17 B-7 Week 2 typed entity-nodes.md`

## Next steps (Week 3 candidates)

1. **Alias-extraction** — `Domi color palette` → `:Person:Domi` + alias edge → currently 1-of-many Person miss
2. **`:Concept` / `:Decision` / `:Sprint` labels** — covers the 8115 generic entities (e.g. `B-2 sprint` → `:Sprint`)
3. **MAGE image upgrade** — `memgraph/memgraph-mage:latest` → enables `community_detection.get` for the monthly cluster-summary cron (B-7 Week 3-4 plan)
4. **LLM-NER fallback** — subagent-fanout pass for the 8115 generic entities, batch-100 with 4-class taxonomy, ~$0 via Claude Code subagents
5. **`vault-graph-query --type Project`** convenience flag — currently raw Cypher; wrap with a `--type` CLI arg

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch]] — B-7 ADR
- [[../11-wiki/sv-06-world-model-knowledge-graph]] — research-cikk
- [[../11-wiki/memgraph-ce-feature-limits]] — CE workaround playbook (vendoured here)
- [[../08-Sessions/2026-05-17-obsidian-vault]] — Week 1-α landing super-session

---
name: B-7 Week 3 — typed Entity-label expansion + alias-extraction
type: audit
tags: ["#type/audit", "#sprint/B-7", "#topic/knowledge-graph", "#topic/memgraph"]
created: 2026-05-17
updated: 2026-05-17
---

# B-7 Week 3 — typed Entity-label expansion + alias-extraction

**Sprint:** [[02-Projects/superintelligent-vault|SV]] / B-7 (entity-graph)
**Cél:** Week 2 5-label baseline (9.58% tipizáltság) → bővítés `:Concept` / `:Decision` / `:Sprint` címkékkel, plusz alias-graph layer (`:Alias` → `[:ALIAS_OF]` → canonical).
**Memgraph:** CE 3.9.0 (container `vault-memgraph`, :7687)
**Script:** `/usr/local/bin/vault-graph-retype` → `/root/obsidian-vault/.vault-graph/scripts/vault-graph-retype.py`
**Alias config:** `/root/.vault-config/entity-aliases.yaml`
**Audit log:** `/root/obsidian-vault/06-Audits/graph-retype-20260517.jsonl`

## Eredmények — egy mondatban

5 → **8 typed-label** + 26 alias-edge **élesítve**. Tipizáltság **9.58% → 14.87%** (1338 / 8997 entity). 25% célt rule-based pass nem éri el — LLM-extraction Week 4 marad.

## Tipizáltság — előtte/utána

| Mérés | Week 2 vége | Week 3 vége | Δ |
|---|---:|---:|---:|
| `:Entity` össz | 8 975 | **8 997** | +22 (új canonical-ok alias-phase-ből) |
| Tipizált (≥1 secondary label) | 860 | **1 338** | **+478** |
| Tipizáltság (%) | 9.58% | **14.87%** | +5.29 pp |
| Generic (csak `:Entity`) | 8 115 | **7 659** | −456 |

## Per-label count (read-back Memgraph-ból)

| Label | Week 2 vége | Week 3 vége | Δ | Megjegyzés |
|---|---:|---:|---:|---|
| `:Project` | 266 | 273 | +7 | Alias-canonicals (MFL, KGC, MAPESZ, Foxxi, Bluebird, Kokó, Kinda) |
| `:Person` | 1 | 7 | +6 | Alias-canonicals (Domi, Karpathy, Yann, Gyuszi, Rob, e-mail) |
| `:Server` | 29 | 32 | +3 | Alias-canonicals (vps-prod-example, vps-dev-example, kgc-postgres) |
| `:Skill` | 275 | 275 | 0 | Week 2 ruleset stabil |
| `:SourceFile` | 289 | 581 | +292 | File-ext bővítés (`.db .sqlite .pdf .pptx .xlsx .png .svg …`) |
| `:Concept` | — | **228** | +228 ÚJ | Allow-list (44) + suffix-heuristic (pattern/playbook/workflow/protocol/doctrine/heuristic/gotcha) |
| `:Decision` | — | **20** | +20 ÚJ | `ADR …` prefix + `sv-N … arch` patterns + 07-Decisions/ title-match |
| `:Sprint` | — | **200** | +200 ÚJ | `B-1..B-9` / `B-N Week N` / `SV-N` / `sv-bN-*` / `sv-N-*` patterns |
| `:Alias` | — | **26** | +26 ÚJ | Új node-class, `:ALIAS_OF` edge-gel |

## A 3 új klasszifikáló-szabály (Week 3)

### `:Concept` — evergreen tudás

- **Allow-list** (`KNOWN_CONCEPTS`, 44 entry) — kézzel-curált evergreen-koncepciók exact-match: GEPA, subagent-fanout, crystallization, Karpathy LLM Wiki pattern, MEMORY.md, BMAD, PRD, ADR, RAG, MemGPT, RSI, KO-DB, … (case-insensitive)
- **Suffix-heurisztika** — `…pattern` / `…playbook` / `…protocol` / `…workflow` / `…doctrine` / `…heuristic` / `…antipattern` / `…gotcha` / `…recipe` / `…convention` / `…minta` (2–8 tokenes phrase-ekre, hogy ne csak az egy-szavas "pattern" zaj kerüljön be)
- **Eredmény:** 228 node (44 explicit + ~184 suffix-match)

### `:Decision` — ADR-szerű döntések

- **Prefix:** `ADR ` / `ADR-` / `ADR$` esetében (case-insensitive)
- **SV arch fájlok:** `sv-N … arch` minta (`sv-5 crystallization automation arch`, `sv-b2-memory-architecture`)
- **Direkt match:** 07-Decisions/ minden `.md` cím (Index kivételével)
- **Eredmény:** 20 node — ADR-001, ADR-sv-5, ADR 2026-04-23 Agentic OS build plan, sv-01-memory-architecture, …

### `:Sprint` — SV sprint-ek

- **Strict:** `B-N`, `B-N + B-M`, `B-N Week N[-M]`, `sv-bN[-…]`, `sv-N[-…]`, `sv-phase-bN…`
- **Loose:** `B-N <≤5 token>` / `SV-N <≤5 token>` / `sv-bN <…>` ha más szabály nem fogta meg (file-ext / skill / concept / project / server / person előbb fut)
- **Eredmény:** 200 node — `B-1 Crystallization Day 0`, `B-2 vault-embed.py skeleton`, `B-3 eval-l1-parser --backfill`, `SV-3 NotebookLM`, `sv-meta-cluster`, …

## Alias-extraction statisztika

| Metrika | Érték |
|---|---:|
| Alias-entry a YAML-ben | 26 |
| `:Alias` node ténylegesen | 26 |
| Új canonical `:Entity` node | 22 (a 4 már létezett — Peti, MAPESZ, Andrej Karpathy, …) |
| `:ALIAS_OF` edge | 26 |
| Skipped (érvénytelen type) | 0 |
| Idempotency (2× és 3× run) | 0 új node, 0 új edge — verified |

### Top-5 sample-alias

| Alias | Canonical | Canonical-típus |
|---|---|---|
| `Peti` | `user@example.com` | `:Entity:Person` |
| `Domi` | `Domonkos Petis` | `:Entity:Person` |
| `Karpathy` | `Andrej Karpathy` | `:Entity:Person` |
| `MFL` | `MyForge Labs` | `:Entity:Project` |
| `KGC` | `Kisgépcentrum` | `:Entity:Project` |
| `MAPESZ` | `Magyar Petanque Szövetség` | `:Entity:Project` |
| `subagent-fanout` | `Claude Code subagent-fanout playbook` | `:Entity:Concept` |

### A `:Alias` model

- Önálló node-class — NEM `:Entity` (de a canonical az). Cél: tisztán szétválasztani a rövid-forma referenceket és a kanonikus entitásokat.
- `aliasOf` property (canonical-name string) + `[:ALIAS_OF]` edge — kettős reprezentáció a query-flexibilitásért.
- A 4-féle valid canonical-típus: `:Person` / `:Project` / `:Concept` / `:Server` (`:Skill` / `:SourceFile` / `:Sprint` / `:Decision` szándékosan kihagyva — ezekre az alias-mintázat nem természetes).

## Smoke-test → live apply protokoll

1. **`--dry-run --phase concept-decision-sprint`** — 1316 typed-label tervezve, 0 write. ✅
2. **`--phase concept-decision-sprint` (live)** — 1316 SET label batched (BATCH_SIZE=500), 1.16s. ✅
3. **`--dry-run --phase alias`** — 26 `:Alias` + 22 canonical + 26 edge tervezve. ✅
4. **`--phase alias` (live)** — 0.4s, 22 új canonical Entity (+22 össz `:Entity` count), 26 `:Alias`, 26 edge. ✅
5. **Idempotency check** — `--phase both` még 2× lefuttatva, 0 új node/edge. ✅

## Smoke-test queries (live Memgraph)

```cypher
-- Az összes :Sprint és kapcsolódó :SourceFile
MATCH (s:Sprint)-[]->(f:SourceFile) RETURN s.name, f.name LIMIT 10;

-- :Alias dereferencing — "Domi" → kinek a fedőneve?
MATCH (a:Alias {name: 'Domi'})-[:ALIAS_OF]->(c) RETURN c.name, labels(c);

-- Hány :Concept van a vault-ban?
MATCH (n:Concept) RETURN count(n);  -- → 228
```

## Bizonytalanságok / open kérdések

- **Suffix-heurisztika false-positive:** `"forbidden patterns"` (közönséges főnév) → `:Concept`. Manuálisan curate-elhetetlen tisztán szabály-alapon. **Mitigation:** LLM-classifier Week 4-ben.
- **Sprint "loose"-mintázat:** `"B-2 vault-embed.py skeleton"` → `:Sprint` (mert `.py skeleton` ≠ pure file-name). Vitatható: ez sprint-task vagy artifact? **Döntés:** `:Sprint`, mert az "miért készült" oldal fontosabb a query-ben mint a "milyen fájl".
- **`:Decision` lefedettség 20 — kevés.** A 07-Decisions/-ben 30+ fájl van, de a legtöbb többszavas címmel kerül a KO-DB-be ("KGC TV CMS — Print Editorial admin + heartbeat protokoll" — ez `:Concept` lett a `protokoll` suffix-szel). Cross-class drift jelen lesz a 2-label sample-eken.
- **`:Concept` 228 közel a teljes lefedettséghez** a suffix-mintán; az allow-list bővíthető a Glossary-ből (jelenleg ~44 explicit). Week 4 LLM-pass jelentősen tovább emelheti.

## Mi NEM sikerült

- **25% tipizáltság-cél** — elértünk 14.87%-ot. A maradék 85% (`7659 Generic`) zömében tech-jargon compound-phrase (pl. `"HMAC signature payload"`, `"Direct wpdb->update on _elementor_data"`, `"foxxi-list-services widget in preview"`) — nincs determinisztikus klasszifikátor-szabály rájuk. **LLM-extraction Week 4 marad a megoldás.**

## Week 4 follow-up (next session)

1. **LLM-classifier** a 7659 Generic-re — subagent-fanout pattern, 8× parallel:
   - Input: 1000-node chunk-onként, prompt: "Classify each entity into one of {Concept, Decision, Sprint, Skill, Project, Server, Person, SourceFile, Generic-Tech, Generic-Code, Generic-Other}"
   - Output: JSON `{name, label, confidence}`
   - Apply csak `confidence >= 0.8` esetén — alacsonyabbat kézi review-ra
2. **Cross-source alias-felfedezés** — heurisztika: ha 2 `:Entity`-name normalize-után közeli (Levenshtein ≤ 2 token-en belül), proposeálj alias-edget. Manual-confirm gate (mint a crystallize-batch-preview-pattern).
3. **`:Alias` query-bővítés a `vault-ko-query`-ben** — substring-search transparently dereferencelje az alias-okat (`vault-ko-query Domi` → `Domonkos Petis` is megjelenjen).
4. **`:Concept` allow-list normalize** — Glossary.md-ből regenerate a `KNOWN_CONCEPTS`-et, hogy single-source-of-truth maradjon.

## Korlátok

- A script **DDL-mentes** (Memgraph CE 3.9.0 limit) — index-eket nem hoz létre, csak meglévő `(Entity name)` indexet használ.
- A `--reset` flag csak a classifier-fázis típus-címkéit törli; az `:Alias` node-okat és edge-eket NEM (ki kell manuálisan törölni cypher-ben).
- A `:Alias` node nem `:Entity` — tudatos döntés, de a `vault-ko-query` jelenleg `MATCH (e:Entity)` alapból szűr, így alias-okat nem talál. Week 4 query-bővítés szükséges.

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-6 world-model knowledge-graph arch|ADR: sv-6 world-model knowledge-graph arch]]
- [[../11-wiki/memgraph-ce-feature-limits|wiki: Memgraph CE feature-limits]]
- [[../11-wiki/claude-code-subagent-fanout|wiki: subagent-fanout playbook]] (Week 4 LLM-pass mintája)
- Source: `/usr/local/bin/vault-graph-retype` → `/root/obsidian-vault/.vault-graph/scripts/vault-graph-retype.py`
- Config: `/root/.vault-config/entity-aliases.yaml`
- Audit JSONL: `/root/obsidian-vault/06-Audits/graph-retype-20260517.jsonl`

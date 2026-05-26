---
name: Wikilink-importer pattern (Memgraph + regex-audit komplementer)
type: wiki
tags: ["#type/wiki", "vault-integrity", "memgraph", "b-7", "evergreen"]
created: 2026-05-18
updated: 2026-05-18
status: evergreen
---

# Wikilink-importer pattern

## TL;DR

A vault wikilink-integritását **két komplementer rétegen** kell mérni, mert sem a graph-db, sem a regex-scan egyedül nem ad teljes képet: a **Memgraph wikilink-importer** a dinamikus entity-graph-ot építi (MENTIONS edge-ek), a **`vault-broken-wikilinks-audit`** pedig deterministic regex-scan, amely a canonical broken-link source-of-truth. A két réteg eredménye keresztösszevethető; eltérés = drift-signal.

## Háttér

A Memgraph CE 3.9.0 vector-index ([[memgraph-ce-feature-limits]]) bevezetésével a B-7 sprint a vault entity-graphját live tartja (8975 entity / 13812 relation). A wikilink-importer pipeline ezt a graph-ot frissíti, **DE** egy kritikus tulajdonsággal: a `[[broken-target]]` link MENTIONS edge-ként megjelenik, és a Memgraph automatikusan létrehoz egy stub Concept-node-ot a hivatkozott névhez — `exists=false` flag NEM perzisztálódik a node-property-ben. Ennek következménye: a graph-query alapján a target node "létezni látszik", miközben a vault-on nincs hozzá MD-fájl.

Ez a quirk vezetett a 2026-05-17 broken-wikilinks scan-hez ([[../06-Audits/2026-05-17 broken-wikilinks scan]]), amely **regex-alapú** scan-nel találta meg az eredeti ~120 broken target-et. A regex csak a fájl-jelenlétet ellenőrzi (`os.path.isfile`), így ez a réteg corruption-immunis, viszont nem lát kontextust (graph-relevance, in-degree).

## Mintázat

1. **Regex layer (canonical)** — `vault-broken-wikilinks-audit` script:
   - Glob `obsidian-vault/**/*.md`, regex `\[\[([^\]|#]+)`
   - Resolve alias (frontmatter `aliases:` matching)
   - Output: `06-Audits/broken-wikilinks-YYYY-MM-DD.json` + `broken-wikilinks-latest.md`
   - Regression-gate: prev-vs-current `broken_targets` count delta — exit 1 ha increase > 20%
2. **Memgraph layer (contextual)** — wikilink-importer Cypher:
   - `MATCH (src:Page)-[r:MENTIONS]->(tgt:Concept) WHERE tgt.exists IS NULL OR tgt.exists = false`
   - In-degree ranking → "most referenced broken target" priority list
   - Stub-node cleanup hook: `DELETE` ha target ténylegesen `exists=true` (resolve race)
3. **Cross-check** — heti audit a 2 réteg outputjait összeveti; eltérés = (a) importer késik, (b) regex-scan stale, vagy (c) alias-resolution divergál

## Anti-pattern

- **Csak Memgraph** — false-positive "exist"-flag a stub-nodes miatt, broken-link nem visible
- **Csak regex** — nincs context (priority order, in-degree, related-cluster)
- **Manual scan** — 2026-05-17 előtti pattern, ad-hoc grep nem reprodukálható, weekly delta nem mérhető

## Reusable szabályok

1. **Regex = ground-truth** — minden broken-link riport vagy fix-PR először regex-scan-en alapuljon
2. **Memgraph = priority engine** — in-degree-ranking és cluster-analízishez
3. **Weekly cron 04:45** — post-`vault-cleanup` (04:00), pre-`vault-ko-conflicts-audit` (04:50)
4. **Delta-gate +20%** — regression-protection; exit 1 → cron-email → manuális review
5. **Alias-resolve frontmatter-alapú** — minden audit-scan tisztelje a `aliases:` mezőt (NEM csak filename-match)
6. **Stub-node cleanup hook** — Memgraph stub-Concept-node-ok auto-delete amikor a target file létrejön

## Buktatók

- A `[[link|display]]` syntax `|`-utáni része display-szöveg, NEM target — regex csak az első csoportot vegye
- `[[../11-wiki/foo]]` és `[[foo]]` ugyanaz a target, ha `foo` egyértelmű — resolver legyen path-aware
- Memgraph stub-Concept reuse: ne hozz létre új node-ot ugyanahhoz a name-hez, hanem `MERGE` használat

## Kapcsolódó

- [[../06-Audits/2026-05-17 broken-wikilinks scan]] — eredeti manuális scan
- [[../06-Audits/broken-wikilinks-latest|legutóbbi audit MD]]
- [[sv-06-world-model-knowledge-graph]] — B-7 entity-graph
- [[vault-corruption-detection-pattern]] — szélesebb integritás-keretrendszer
- [[memgraph-ce-feature-limits]] — CE-specifikus vector-index quirks
- [[vault-cleanup-multi-script-policy]] — cron-ütemezés

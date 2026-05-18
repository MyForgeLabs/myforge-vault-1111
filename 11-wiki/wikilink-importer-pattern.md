---
name: Wikilink-importer pattern (Memgraph + regex-audit komplementer)
type: wiki
tags: ["#type/wiki", "vault-integrity", "memgraph", "b-7", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# Wikilink-importer pattern

> [!todo] Bővítendő
> Ez egy placeholder — broken-wikilinks-audit `vault-broken-wikilinks-audit` (deterministic regex-scan) komplementere a B-7 Memgraph wikilink-importer pipeline-nak.

## Probléma

Memgraph NEM perzisztálja az `exists=false` flag-et — egy `[[broken-target]]` link a graf-ban élő MENTIONS edge-ként jelenik meg, de a target node nem létezik a vault-on. Két komplementer megközelítés kell:

1. **Memgraph wikilink-importer** — extract MENTIONS edges via Cypher, build entity-graph
2. **`vault-broken-wikilinks-audit`** — deterministic regex-scan, canonical broken-link source-of-truth, weekly cron

## Implementáció

- Script: `/usr/local/bin/vault-broken-wikilinks-audit`
- Output: `06-Audits/broken-wikilinks-YYYY-MM-DD.json` + `broken-wikilinks-latest.md`
- Regression-gate: prev-vs-current `broken_targets` count delta — exit 1 ha increase > 20%
- Cron: weekly Sunday 04:45 (post-`vault-cleanup`)

## Kapcsolódó

- [[../06-Audits/2026-05-17 broken-wikilinks scan]] — eredeti manuális scan
- [[../06-Audits/broken-wikilinks-latest|legutóbbi audit MD]]
- [[sv-06-world-model-knowledge-graph]] — B-7 entity-graph

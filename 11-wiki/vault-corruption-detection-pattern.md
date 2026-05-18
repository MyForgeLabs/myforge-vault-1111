---
name: Vault-corruption detection pattern
type: wiki
tags: ["#type/wiki", "vault", "integrity", "monitoring", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# Vault-corruption detection pattern

> [!todo] Bővítendő
> Stabil audit-monitorozás alapja: olyan formal-property check-ek, amik corruption-pattern-eket detektálnak (broken links, self-referential loops, escape-bug-ok, encoding-corruption).

## Detection-axes

1. **Broken wikilinks** — `vault-broken-wikilinks-audit` (regex + Memgraph)
2. **Self-referential loops** — `audit-md-self-referential-loop` pattern
3. **Encoding-corruption** — Unicode `u00e9` helyett `é` (lásd Elementor backslash-strip bug)
4. **Frontmatter drift** — YAML séma validation `00-Meta/Frontmatter-schema.md` ellen
5. **Orphan wiki** — `vault-orphan-wiki` (0-ref wiki-fájlok)

## Kapcsolódó

- [[audit-md-self-referential-loop]]
- [[wikilink-importer-pattern]]
- [[../06-Audits/System_Health]]

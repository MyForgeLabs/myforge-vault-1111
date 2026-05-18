---
name: 00-Meta — vault szabályok
type: index
tags: ["#type/index", "meta", "vault-rules"]
created: 2026-04-30
updated: 2026-04-30
---

# 00-Meta/

**A vault saját szabályai.** Hogyan írjunk fájlokat, milyen tag-eket használjunk, mi a frontmatter séma. Az AI-agentek (Claude, Codex, Gemini) ezeket olvassák a session elején a [[AGENTS]] mellett.

## Tartalom

| Fájl | Mire való |
|------|-----------|
| [[00-Meta/Tag-taxonomy]] | Kötelező tag-hierarchia: `#env/*`, `#type/*`, `#tech/*`, `#project/*`, `#op/*`, `#agent/*` |
| [[00-Meta/Frontmatter-schema]] | YAML frontmatter séma per-típus (host, project, decision, audit, session, memory, task) |
| [[00-Meta/Glossary]] | Slug + rövidítés feloldó (KGC, MFL, MAPESZ, BMAD, …) — agent-friendly disambiguation |
| [[00-Meta/templates/README\|templates/]] | Daily / Session / Project sablonok új fájlokhoz |

## Mit NEM tartalmaz

- A **futó tudást** — az [[05-Memory/README|05-Memory/]]-ban van (User, Infrastructure, Skill-map)
- Az **agent-utasításokat** — az [[AGENTS]]-ben gyökér-szinten (symlink-kompatibilitás)
- A **mappa-struktúra leírást** — a [[README]]-ben

## Hogyan változtassunk

- **Új tag** kell? → előbb írd be a [[00-Meta/Tag-taxonomy]]-ba, csak utána használd
- **Új fájl-típus**? → új section a [[00-Meta/Frontmatter-schema]]-ban
- A változás azonnal él mindhárom agent számára (mind ezt a forrást olvassa)

## Kapcsolódó

- [[AGENTS]] — agent-instrukciók (gyökérszintű, symlink-kompatibilis)
- [[README]] — humán belépő
- [[11-wiki/Johnny-Decimal-prefix]] — miért 00-, 01-, … prefix

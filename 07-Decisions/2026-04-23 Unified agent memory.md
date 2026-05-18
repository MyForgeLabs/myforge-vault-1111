---
name: Unified agent memory across Claude / Codex / Gemini
type: decision
status: accepted
tags: [adr, memory, agents, vault]
date: 2026-04-23
---

# 2026-04-23 — Egyetlen vault, három agent

## Kontextus

- **Claude Code** auto-memory fájljai `~/.claude/projects/-root/memory/`-ben voltak
- **Codex CLI** és **Gemini CLI** ezeket nem látta — minden session-ben vissza kellett tanítani
- Felmerült hogy az `obsidian-skills` repo Agent Skills spec-et használ, ami mindhárom eszközzel kompatibilis → ugyanez az elv a memóriára is kiterjeszthető
- Volt egy majdnem üres Obsidian vault `/root/obsidian-vault/`-ban (`KGC-ALL Architektura.canvas` fájllal)

## Döntés

**Egyetlen forrás a `/root/obsidian-vault/`**, szerkezet:

```
/root/obsidian-vault/
├── README.md                  humán belépő
├── AGENTS.md                  közös agent-utasítás
├── Projects/
│   ├── Index.md               dashboard
│   └── <projekt>.md           egy-egy aktív projekt
├── Memory/
│   ├── User.md
│   └── Infrastructure.md
├── Decisions/                 ADR-ek (ez a fájl is itt)
└── Sessions/                  opcionális napi/session napló
```

**Integráció symlink-kel** (egy forrás, három agent látja):

| Eszköz | Symlink | → |
|--------|---------|---|
| Claude Code | `~/.claude/CLAUDE.md` | `AGENTS.md` |
| Codex CLI | `~/.codex/AGENTS.md` | `AGENTS.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` | `AGENTS.md` |
| Claude auto-memory | `~/.claude/projects/-root/memory/*.md` | vault-beli `Projects/*` és `Memory/*` |

Backup: `~/.claude/projects/-root/memory/.backup_20260423/` (a migráció előtti állapot).

## Miért így

- **Obsidian-kompatibilis** — grafikus browsing, canvas, wikilink, frontmatter property
- **Agent-egyenlőség** — egyik eszköz sem "privilegizált", mindhárom ugyanazt olvas-írja
- **Visszafelé kompatibilis** — Claude auto-memory továbbra is él (symlink), a MEMORY.md index formája megmaradt
- **Humán-first** — a user bármikor kézzel szerkeszti `.md` editor-ban vagy Obsidian app-ban
- **Git-ready** — a vault egy git repo-vá tehető bármikor (`git init /root/obsidian-vault`)

## Alternatívák amiket elvetettünk

- **Minden agent saját memóriát tart** — szinkronhiba garantált, duplikáció
- **Egy agent (pl. Claude) írja, a többi csak olvassa** — nem egalitárius, fejlődésképtelen
- **Külső DB (Postgres/Sqlite)** — overkill, nem human-friendly, nem Obsidian-kompatibilis

## Következmények

**Pozitív**
- Egyetlen "project dashboard" ([[02-Projects/Index]]) minden agentnek
- User bármelyik eszközt használja, ugyanabból a kontextusból indul az agent
- Obsidian app-ban grafikusan is böngészhető

**Vigyázni kell**
- A `~/.claude/projects/-root/memory/` NE kerüljön újra **valós fájlként** felülírásra — csak symlinkek éljenek
- A MEMORY.md-t agentek közvetlenül írhatják (auto-memory rendszer) — ott csak index legyen, tartalmat a vaultba
- Ha a user törli a vault-ot vagy áthelyezi → mind a három symlink eltörik (backup erre van)

## Ellenőrzés

```sh
readlink ~/.claude/CLAUDE.md       # = /root/obsidian-vault/AGENTS.md
readlink ~/.codex/AGENTS.md        # = /root/obsidian-vault/AGENTS.md
readlink ~/.gemini/GEMINI.md       # = /root/obsidian-vault/AGENTS.md
ls -la ~/.claude/projects/-root/memory/  # 3 symlink + MEMORY.md + .backup_20260423/
```

## Kapcsolódó

- [[AGENTS]] — az új közös utasítás
- [[README]] — humán intro
- [[02-Projects/Index]] — dashboard

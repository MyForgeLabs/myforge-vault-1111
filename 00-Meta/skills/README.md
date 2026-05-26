---
name: 00-Meta/skills — Claude Code skill csomagolások
type: index
tags: ["#type/index", "skills", "agents", "11.11"]
created: 2026-04-30
updated: 2026-04-30
---

# 00-Meta/skills/

Claude Code / Codex / Gemini agent-skill csomagolások amik a vault-ban élnek (verzió-kontroll alatt), de a `/root/.agents/skills/` mappában is használhatók symlink-kel.

A két központi skill:

| Skill | Mit csinál | Trigger |
|-------|-----------|---------|
| [[00-Meta/skills/load-session-context/SKILL\|load-session-context]] | A `/11.11start` után aggressive context-loadot csinál (projekt-fájl, utolsó 5 session, ADR-ek, Backlog, Memory, Host, Daily) | `/11.11start` után automatikusan, vagy `/load-session-context <slug>` |
| [[00-Meta/skills/propagate-session/SKILL\|propagate-session]] | A `/11.11stop` után batch preview-vel propagálja a Learnings-et a Memory / Decisions / wiki / Glossary / Projects rétegekbe | `/11.11stop` után automatikusan, vagy `/propagate-session [<session-fájl>]` |

## Telepítés

```sh
# Mac-en VAGY dev VPS-en VAGY prod-on:
cd /root/.agents/skills    # vagy ahol a skill-mappa van

# Symlinkek a vault-ból
ln -sfn /root/obsidian-vault/00-Meta/skills/load-session-context  load-session-context
ln -sfn /root/obsidian-vault/00-Meta/skills/propagate-session      propagate-session

# Ellenőrzés — Claude Code lássa
ls -la /root/.agents/skills/ | grep -E "load-session|propagate"
```

A skillek **automatikusan felfedezhetők** a Claude Code / Codex / Gemini-ben (a `.skill-lock.json` index alapján). Új session indításnál Claude be is olvassa.

## Mi a "skill"

Anthropic Claude Code skill formátum:

```
skill-name/
  SKILL.md       — frontmatter + name/description/instructions
  ...            — opcionálisan reference fájlok, scriptek
```

A `SKILL.md` frontmatterja:

```yaml
---
name: skill-name
description: |
  Mit csinál a skill, mikor triggereljen rá az agent.
  Több sor lehet — minél részletesebb, annál pontosabb a triggering.
---
```

## Frissítés

Ha javítasz a skill-en (bármelyik gépen), a vault-vault-on keresztül szinkronizálódik:
1. Szerkesztd a `00-Meta/skills/<skill>/SKILL.md`-t
2. Auto-save cron commitol
3. Másik gép pull-ol
4. Symlink él, Claude/Codex/Gemini a friss verziót látja

## Kapcsolódó

- [[11-wiki/Auto-context-loading]] — load-session-context háttere
- [[11-wiki/Crystallization-protocol]] — propagate-session háttere
- [[05-Memory/Skill-map]] — minden agent-skill business-funkció szerint

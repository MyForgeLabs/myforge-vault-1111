---
name: Session orchestration — 11.11 command family
type: decision
status: accepted
tags: [adr, sessions, agents, 11.11]
date: 2026-04-23
---

# 2026-04-23 — Session orchestration (11.11 parancs-család)

## Kontextus

Egyetlen vault mindhárom agentnek megvan ([[07-Decisions/2026-04-23 Unified agent memory]]), és a `11.11` health check is fut. Hiányzott:
- **A:** folytonosság — ami egy chat-ben történik az egy másik agent előtt ismeretlen
- **B:** tiszta lezárás — minden session rendrakással záródjon (commit + memória + project update)
- **C:** áttekintés — lássam mi folyik, hol tartunk

## Döntés

**Session = egy munkafolyam.** A chat-szintű autosave (10 perces cron) továbbra is megy a háttérben; a session a szándékolt egység amit te nyitsz és zársz.

### Parancsok

| Parancs | Funkció |
|---|---|
| `11.11start "<projekt>-<feladat>"` | Új session: `Sessions/YYYY-MM-DD-<név>.md` + `.active-session` marker |
| `11.11start` (arg nélkül) | Listázza előző sessionök neveit + aktív projektet → választhatsz vagy új |
| `11.11note "..."` | Timestamped jegyzet → aktív session `## Events`-be |
| `11.11stop` | Agent reviewolja chat + note-okat → summary + learnings + next. Project-fájl frissül. Commit. Session `closed` |
| `11.11` (bővített) | Meglévő health check + aktív session + utolsó 5 zárt |

### Session fájl séma

```yaml
---
name: <projekt> — <feladat>
project: <projekt-slug>
status: open | closed
started: 2026-04-23T10:00+00:00
ended: (üres amíg open)
agent: claude | codex | gemini
tags: [session, <projekt-slug>]
---

## Cél
## Events      # /11.11note ide appendel
## Summary     # /11.11stop idézi ide az agent konklúzióját
## Learnings → memória
## Next session
```

### Állapot-forrás

- **Aktív session path:** `/root/obsidian-vault/.active-session` (ha üres / hiányzik → nincs nyitott)
- **Source of truth:** a session fájl `status:` frontmatter property-je

### Integráció a 3 agent-ben

- **Bash script** a motorban (`/usr/local/bin/11.11*`) — minden agent ezt hívja
- **Claude Code slash commands** `~/.claude/commands/11.11*.md`-ben — a scriptet hívják + utasítják az agentet hogy stop-kor írjon summary-t
- **Codex / Gemini** ugyanazt a bash scriptet hívja; ezeknek az agentnek ugyanazt az utasítást kéred kézzel: "nézd át a chat-et és írj summary-t a session fájlba, utána futtasd 11.11stop"

## GitHub backup

- Remote: `github.com/PetykaMaki/obsidian-vault` (private)
- Autosave cron push-olja is, ha van remote beállítva
- Commit üzenetek: `auto[$AGENT]: ISO` (cron), `stop[$AGENT]: <session-név>` (11.11stop)

## Miért ez

- **YAGNI:** nincs komplex daemon, csak néhány bash script + markdown fájl
- **Human-first:** minden emberileg szerkeszthető, Obsidian-ban nézhető
- **Crash-safe:** `11.11note` útközbeni jegyzetek → stop előtti crash esetén sem veszik el a fontos pillanatok
- **Egyenrangú agentek:** ugyanaz a mechanizmus mindháromnak

## Elhagytunk

- ❌ **Continuous agent journaling** — csak Claude-nak lenne hook-ja, inkonzisztens
- ❌ **DB-alapú session store** — overkill, nem human-first, nem git-friendly
- ❌ **Cross-agent session ID** (amit Claude kezdett, Codex folytatja ugyanabban) — overengineering; ha kell, egyszerűen ugyanahhoz a session fájlhoz írsz tovább

## Kapcsolódó

- [[07-Decisions/2026-04-23 Unified agent memory]]
- [[AGENTS]]

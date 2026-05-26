---
name: Crystallization workflow + auto-context-loading
type: decision
status: accepted
date: 2026-04-30
tags: ["#type/decision", "#agent/claude", "#agent/codex", "#agent/gemini", "11.11"]
---

# Crystallization workflow + auto-context-loading

A `/11.11start` és `/11.11stop` parancsokat **kétoldalt** kibővítjük: indulásnál aggressive context pre-load, záráskor batch-preview propagáció a Karpathy crystallization minta szerint.

## Kontextus

A vault [[11-wiki/Karpathy-LLM-Wiki-pattern|Karpathy LLM-Wiki minta]] szerinti tudás-compoundolásra épül: minden session végén a tanulságok átkerülnek a hosszú-távú rétegekbe (Memory, Decisions, wiki, Glossary, Projects). Eddig **manuálisan** csináltuk — agent-tudatosan. A user kérése: legyen **automatikus, de batch preview-vel megerősítéssel**, és a session induláskor is legyen **aggressive context load** hogy ne kelljen "mi volt múltkor"-t kérdezni.

## Opciók

| Opció | Pro | Kontra |
|-------|-----|--------|
| **A. Csak vault-protokoll** (AGENTS.md kötelezi) | Egyszerű, semmi script-változtatás | Az agent felelőssége — ha valamiért nem hívja, nincs script-fallback |
| **B. Csak bash-script módosítás** | Tényleg automatikus | Az AI-rész nem bash-ben van, ezért a kérdezés-propagálás nem onnan jön |
| **C. Mindkettő (vault + bash + skill)** ✅ | Belt+suspenders, az agent és script is támogatja | Nagyobb felület, telepítés a 3 gépen |

**Választás: C** — vault protokoll + bash-patch + Claude Code slash skill.

## Választás

### Vault-réteg (forrás-of-truth)

- [[11-wiki/Auto-context-loading]] — start-time aggressive pre-load specifikációja
- [[11-wiki/Crystallization-protocol]] — stop-time batch preview propagáció + routing decision tree
- [[00-Meta/templates/Session-template]] — `## Pre-loaded context` és `## Propagation log` szekciókkal
- [[AGENTS]] — kötelező workflow mindkét oldalon, részletes szabályok hivatkozva

### Bash-réteg (mechanikus segítség)

- `00-Meta/bash-patches/11.11start.patch` — a script által generált session-fájl új template-jét használja (Pre-loaded context placeholder TODO-blokkal)
- `00-Meta/bash-patches/11.11stop.patch` — a `## Learnings` szekciót clipboard-ba másolja, `.last-stop-prompt` fájlt ír amit az agent felismer

### Skill-réteg (agent-discoverable)

- [[00-Meta/skills/load-session-context/SKILL]] — Claude Code skill az aggressive load-hoz
- [[00-Meta/skills/propagate-session/SKILL]] — Claude Code skill a stop-time propagációhoz

## Indoklás

- **Aggressive pre-load:** a user kifejezetten ezt választotta (vs medium / minimal). ~15-20K token cost a session indulásnál, de nincs context-vesztés.
- **Batch preview:** vs egyenkénti vagy auto-apply. A user gyors "OK" / "1-3 OK, 4 X" választ ad, gyorsabb mint az egyenkénti.
- **3 réteg (A+B+C):** vault-protokoll mint forrás-of-truth, bash-patch mint trigger-mechanizmus, slash-skill mint discoverable-fallback. Több redundancia → magasabb megbízhatóság.

## Következmények

### Pozitív

- Az agent (Claude/Codex/Gemini) **session-elejétől teljes kontextust** lát — minimum overhead a "mi volt múltkor" kérdezések kihagyása
- A vault **ténylegesen compoundol** Karpathy mintára — minden tanulság átkerül a megfelelő rétegbe
- **Audit-lánc:** a `## Propagation log` visszakereshető — egy adott Memory/ADR/wiki bejegyzésről tudjuk melyik session-ből jött
- **Mindhárom agent ugyanúgy viselkedik** (Claude/Codex/Gemini), mert az AGENTS.md közös

### Negatív / kockázat

- A bash-patchet **mindkét VPS-en + a Mac-en** alkalmazni kell — telepítés
- Ha az agent valamiért nem futtatja a propagációt (model-hibás session, megszakadás), a `.last-stop-prompt` fájl ott marad — manual cleanup
- Az aggressive pre-load **token-költség** — ha sok session van rövid idő alatt, nőhet a bill

### Mitigation

- **Telepítési ellenőrző** a [[00-Meta/bash-patches/README#Telepítés]]-ben — smoke teszt
- **Stale `.last-stop-prompt` fájlok** weekly-cleanup script-ben (>24h-os fájlok auto-delete)
- **Token-budget** — `Auto-context-loading` 15-20K cap, túllóg → Backlog rövidül először

## Telepítés (3 gép)

1. **Pull a vault legfrissebb verzióját** (auto-cron 10p / Obsidian Git plugin 5p amúgy is megteszi)
2. **Bash-patch alkalmazása** [[00-Meta/bash-patches/README]] szerint (3 gépen)
3. **Skill-symlinkek** `/root/.agents/skills/` → `/root/obsidian-vault/00-Meta/skills/<skill>` (3 gépen)
4. **Smoke-teszt** egy próba sessionnel
5. **AGENTS.md frissítve** — automatikusan él, mert a 3 agent symlinken keresztül látja

## Visszafordíthatóság

- Bash-rollback: `cp /usr/local/bin/11.11start.bak /usr/local/bin/11.11start` (és stop)
- Skill-rollback: `rm /root/.agents/skills/{load-session-context,propagate-session}` symlinkek
- Vault-rollback: a wiki + AGENTS.md változtatások git-ben → `git revert <commit>`

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a háttér-elv
- [[11-wiki/Auto-context-loading]] — start-time spec
- [[11-wiki/Crystallization-protocol]] — stop-time spec
- [[11-wiki/11.11-session-protokoll]] — a parancs-család
- [[00-Meta/bash-patches/README]] — telepítés
- [[00-Meta/skills/README]] — skill telepítés
- [[AGENTS]] — kötelező viselkedés-leírás

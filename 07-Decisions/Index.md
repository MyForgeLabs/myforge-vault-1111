---
name: Decisions Index
type: index
tags: ["#type/index", "decisions", "adr"]
created: 2026-04-30
updated: 2026-04-30
---

# 07-Decisions/

ADR-szerű **döntési napló**. Architektúra-döntések, branding-választások, infra-stratégiák. Minden ADR önmagában záródott — nem élő dokumentum.

> [!info] Mi tartozik ide
> Bármi ami: **(1)** nem visszafordítható nulla költséggel, **(2)** több projektre / hosszabb időre kihat, **(3)** később megkérdezheted: "miért így csináltuk?". Ha kis tweak, a session-be mehet; ha vault-konvencó, a 00-Meta-ba.

## Dátum szerint (legújabb felül)

| Dátum | ADR | Érintett projekt | Státusz |
|-------|-----|------------------|---------|
| 2026-04-30 | [[07-Decisions/2026-04-30 Crystallization workflow + auto-context-loading\|Crystallization workflow + auto-context-loading]] | vault | accepted |
| 2026-04-29 | [[07-Decisions/2026-04-29 KGC TV CMS — Print Editorial admin + heartbeat protokoll\|KGC TV CMS — Print Editorial admin + heartbeat]] | KGC | accepted |
| 2026-04-26 | [[07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma\|KGC-Bérlés adattárolás — Postgres + Prisma]] | KGC-Bérlés | accepted |
| 2026-04-24 | [[07-Decisions/2026-04-24 MYFORGE OS dashboard — roadmap v2\|MYFORGE OS dashboard roadmap v2]] | MyForge | accepted |
| 2026-04-24 | [[07-Decisions/2026-04-24 MAPESZ PWA platform-független architektúra\|MAPESZ PWA platform-független architektúra]] | MAPESZ | accepted |
| 2026-04-24 | [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1\|KGC-Bérlés üzleti szabályok v1]] | KGC-Bérlés | accepted |
| 2026-04-24 | [[07-Decisions/2026-04-24 Git stratégia — standalone repo + 7 commit + GitHub Flow\|KGC-Bérlés Git stratégia — standalone + GitHub Flow]] | KGC-Bérlés | accepted |
| 2026-04-24 | [[07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial\|KGC brand kanonizálás — BEST Warm Editorial]] | KGC | accepted |
| 2026-04-23 | [[07-Decisions/2026-04-23 Vault design - NotebookLM research findings\|Vault design — NotebookLM research findings]] | vault | accepted |
| 2026-04-23 | [[07-Decisions/2026-04-23 Unified agent memory\|Egységes agent-memória]] | vault | accepted |
| 2026-04-23 | [[07-Decisions/2026-04-23 Session orchestration\|Session orchestration (11.11* parancsok)]] | vault | accepted |
| 2026-04-23 | [[07-Decisions/2026-04-23 Claude Code Agentic OS - build plan\|Claude Code Agentic OS — build plan]] | vault | accepted |
| 2026-04-23 | [[07-Decisions/2026-04-23 Audit actions\|Audit actions (a teljes infra audit-ből)]] | infra | accepted |

## Téma szerint csoportosítva

### 🛠️ Vault- és agent-design (6)

A vault saját architektúrája: tudásbázis-réteg, session-szervezés, multi-agent.

- [[07-Decisions/2026-04-23 Unified agent memory]] — közös vault Claude/Codex/Gemini-nek
- [[07-Decisions/2026-04-23 Session orchestration]] — 11.11* parancs-család
- [[07-Decisions/2026-04-23 Vault design - NotebookLM research findings]] — Karpathy/Kepano alapok
- [[07-Decisions/2026-04-23 Claude Code Agentic OS - build plan]] — Agentic-OS terv
- [[07-Decisions/2026-04-24 MYFORGE OS dashboard — roadmap v2]] — dashboard fázisai
- [[07-Decisions/2026-04-30 Crystallization workflow + auto-context-loading]] — start aggressive pre-load + stop batch propagáció

### 🏗️ KGC ökoszisztéma (4)

- [[07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial]] — globals.css v5.0 mint kanonikus
- [[07-Decisions/2026-04-24 Git stratégia — standalone repo + 7 commit + GitHub Flow]] — KGC-Bérlés Git
- [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1]] — bérlési tier-ek és pricing
- [[07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma]] — KGC-Bérlés DB
- [[07-Decisions/2026-04-29 KGC TV CMS — Print Editorial admin + heartbeat protokoll]] — kgc-tv-cms

### 🎯 Petanque klaszter (1)

- [[07-Decisions/2026-04-24 MAPESZ PWA platform-független architektúra]] — Magyar Petanque Szövetség portálja

### 🏥 Infra (1)

- [[07-Decisions/2026-04-23 Audit actions]] — a 2026-04-23-i [[06-Audits/2026-04-23 Teljes infra audit|teljes audit]] action-jei

## Hogy írj újat

1. Új session indítása: `11.11start "<téma>-decision"`
2. Új fájl: `07-Decisions/YYYY-MM-DD <Téma>.md`
3. Frontmatter ([[00-Meta/Frontmatter-schema#type-decision]]):
   ```yaml
   ---
   name: Döntés címe
   type: decision
   status: accepted               # proposed | accepted | rejected | superseded | in-progress
   date: 2026-04-30
   tags: ["#type/decision", "#tech/...", "#project/..."]
   ---
   ```
4. Tartalom: **Kontextus → Opciók → Választás → Indoklás → Következmények**
5. Frissítsd ezt az Index-et új sorral

## Kapcsolódó

- [[00-Meta/Frontmatter-schema]] — ADR YAML séma
- [[06-Audits/Index]] — pillanatkép-jelentések (más kategória)
- [[02-Projects/Index]] — érintett projektek
- [[11-wiki/Index]] — desztillált playbookok (saját szavakkal)

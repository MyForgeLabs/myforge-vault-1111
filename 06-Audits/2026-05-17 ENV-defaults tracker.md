---
name: 2026-05-17 ENV-defaults tracker
type: audit
created: 2026-05-17
updated: 2026-05-17
session: 2026-05-18-sv-b1-week5-env-tracker
tags: [audit/sv-b1, infra/env-flags, type/architectural-decision]
related:
  - "[[../05-Memory/env-defaults]]"
  - "[[../11-wiki/multi-layer-safety-gate]]"
  - "[[../11-wiki/Crystallization-protocol]]"
---

# ENV-defaults tracker — architektúra + miért szükséges + frissítés-protokoll

## Mit auditolok itt?

Az **SV B-1..B-8 roadmap során 15 ENV-flag** él párhuzamosan, mind opt-in default OFF (4-rétegű safety pattern). Eddig **nem volt központi forrás** arra, hogy melyik flag mit csinál, hol van használva, mi a kockázati szintje, és milyen acceptance-criteria-val lehetne default-shift-elni.

Ez az audit a **tracker-doku bevezetését** rögzíti: `/root/.vault-config/env-defaults.md` (symlink: `05-Memory/env-defaults.md`).

## Architektúra

```
┌────────────────────────────────────────────────────────────────────┐
│  Forrás-fájl (single source of truth):                              │
│  /root/.vault-config/env-defaults.md                                │
│  ↑ ide ír az agent / a user új flag bevezetéskor                    │
│                                                                      │
│  Symlink (vault-be is látszik):                                      │
│  /root/obsidian-vault/05-Memory/env-defaults.md ─→ ugyanaz          │
│                                                                      │
│  Tartalom:                                                           │
│  ├── Aggregate dashboard táblázat (15 flag egyben)                   │
│  ├── Status-szótár (SHADOW/BASELINE/CANDIDATE/DEFAULT)               │
│  ├── Risk-szótár (LOW/MEDIUM/HIGH/CRITICAL)                          │
│  ├── Per-flag részletek (16 szekció, egységes szerkezet)             │
│  └── Update-mechanism (manuál + Week 7+ autogen terv)                │
└────────────────────────────────────────────────────────────────────┘
```

### Egységes per-flag szerkezet

Minden flag-nek **8 mező** van:

1. **Current** — jelenlegi default érték
2. **Mit csinál** — 1-2 mondat
3. **Hol használt** — `<script-path:line>` minden referenciára
4. **Risk-level** — LOW / MEDIUM / HIGH / CRITICAL
5. **Default-shift acceptance** — konkrét metrika-küszöbök (X session shadow + Y FP-rate stb.)
6. **Status** — SHADOW / BASELINE / CANDIDATE / DEFAULT
7. **Cross-ref** — kapcsolódó ADR-ek + audit-MD-k + wiki-koncepciók wikilink-kel
8. **History** — `YYYY-MM-DD — esemény` sorok

### Cross-reference háló

A tracker minden flag-et **bilateralisan** köt:
- Forrás-script (grep-elt sor-szám)
- ADR / audit-MD (wikilink)
- Wiki-koncepció (multi-layer-safety-gate / Crystallization-protocol / layered-eval-cascading)

Így ha valaki módosít egy flag-et a kódban, könnyű kideríteni mi van köré dokumentálva.

## Miért szükséges?

### 1. Tudás-perzisztencia
A flag-ek dokumentálása **eddig session-fájlokban szét volt szórva** (`2026-05-13`, `2026-05-17`, `2026-05-17-2`, `2026-05-17-3` mind érintette). Új session-induláskor nem volt egy hely ahol "lássuk a teljes listát" — emiatt nehéz volt rationale-ról dönteni, és kockázat-fokozat a vele járó policy nélkül megnyitható volt.

### 2. Default-shift döntés-tábla
A roadmap előrehaladva több flag elérte a "default-shift jelölt" státuszt (pl. `VAULT_NLI_VETO`, `VAULT_COHERENCE_CHECK`, `VAULT_ROUTE_ENABLED`). Acceptance-criteria nélkül a default-shift random döntés lett volna — most konkrét számokhoz kötve (FP-rate <2%, p95 latency <X, 5 session shadow-pass).

### 3. Audit-trail
A history-szekciók időbélyegzettek, ADR-linkkel — visszakereshetők hogy mikor mit változtattunk. Ez **production-grade safety** alapja, főleg a HIGH/CRITICAL flag-eknél (`VAULT_CRYSTALLIZE_REAL`, `VAULT_CRYSTALLIZE_ALLOW_MAIN`, `VAULT_RSI_APPLY`).

### 4. Permanent opt-in jelölés
Három flag explicit **"SOSEM default-shift"**-ként van címkézve:
- `VAULT_CRYSTALLIZE_ALLOW_MAIN` (CRITICAL, emergency-only)
- `VAULT_CRYSTALLIZE_APPLY` (HIGH, Layer 1 gate szándékosan opt-in)
- `VAULT_RSI_APPLY` (HIGH, self-modifying prompt safety)

Ez megakadályozza, hogy egy jövőbeli session-ben "egyszerűsítés" címen default-on-ra váltsuk.

## Frissítés-protokoll

### Tier 1 — Új flag bevezetéskor (manuál)
A flag-bevezető agent (vagy user) **kötelező** rögtön frissíti:
1. Új `### VAULT_<FLAG>` szekció + per-flag struktúra szerint
2. Új sor az "Aggregate dashboard" táblázatba (Status: SHADOW)
3. History első sor

Ez a `11-wiki/Crystallization-protocol` router-decision-tree-be is beépíthető lenne ("Új ENV-flag → `/root/.vault-config/env-defaults.md`").

### Tier 2 — Status-shift történéskor (manuál + ADR)
SHADOW → BASELINE → CANDIDATE → DEFAULT váltáskor:
1. ADR: `07-Decisions/YYYY-MM-DD <FLAG> default-shift.md` (rationale + acceptance-metric + revert-plan)
2. Dashboard Status update
3. History append: `YYYY-MM-DD — <régi> → <új>` + ADR-link
4. Frontmatter `updated:` frissítés

### Tier 3 — Autogen (Week 7+ backlog)
Egy `vault-env-flag-audit` script tudna:
- Grep mind a 15+ flag-et `/usr/local/bin/` + `~/.vault-config/` + `~/.claude/settings.json` + `.vault-rsi/`-ben
- Diff a tracker-rel: új flag a kódban (nincs trackelve) / elavult flag a trackerben (nincs már a kódban)
- Heti integrity-check a `vault-cleanup` cron-job-ba beépítve, `System_Health.md` egy szekciójaként

Backlog item: 🟡 figyelni — `vault-env-flag-audit` script + System_Health.md integráció Week 6/7-ben.

## Mit NE módosítson ez a doku?

A tracker **NEM** dönt, csak **dokumentál**. A flag-ek viselkedését módosító kód-változások továbbra is külön ADR-eket igényelnek, és a kód-változás után a tracker az ADR-t **követi**, nem előzi meg.

## Output állapot

- ✅ `/root/.vault-config/env-defaults.md` — 15 flag dokumentálva, aggregate dashboard + per-flag részletek
- ✅ `/root/obsidian-vault/05-Memory/env-defaults.md` — symlink ELES
- ✅ Ez az audit-MD (rövid, ahogy a feladat kérte)
- ⏳ Backlog: `vault-env-flag-audit` script (Week 6/7)

## Kapcsolódó

- [[../05-Memory/env-defaults]] — a tracker maga
- [[../11-wiki/multi-layer-safety-gate]] — a 4-rétegű flag-pattern
- [[../11-wiki/Crystallization-protocol]] — minden crystallize-flag itt jön elő
- [[../02-Projects/superintelligent-vault]] — SV roadmap

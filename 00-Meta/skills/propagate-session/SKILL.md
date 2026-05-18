---
name: propagate-session
type: skill
tags: ["#type/skill", "agents", "11.11"]
created: 2026-04-30
updated: 2026-04-30
description: |
  Karpathy crystallization workflow — egy 11.11 session zárásakor a Learnings bullet-eket batch preview-vel propagálja a megfelelő perzisztens rétegekbe (Memory, Decisions, wiki, Glossary, Projects, Tasks). Triggers: amikor a user 11.11stop-ot használ, vagy a vault gyökerében ".last-stop-prompt" fájl jelenik meg, vagy kifejezetten kéri: "propagáld a tanulságokat" / "session crystallization".
---

# propagate-session

Karpathy LLM-Wiki minta szerinti **crystallization** — a session-en megtanult dolgokat **átviszi** a megfelelő hosszú-távú rétegekbe, hogy a vault compoundoljon. **Batch preview-vel** kérdez vissza, mielőtt módosít.

## Mikor triggereljen

- Amikor a user `/11.11stop` parancsot adott — a script létrehoz egy `.last-stop-prompt` fájlt a vault gyökerében, amit az agent felismer
- Amikor a user kifejezetten kéri: "propagáld a tanulságokat", "crystallization", "session learnings át a Memory-ba"
- Amikor egy session `## Propagation log` szekciója üres, de a `## Learnings` szakasz tele van

## Hogyan működik

### 1. Beolvasás

- Session-fájl (gyakran a `.last-stop-prompt` `SESSION:` mezője adja)
- A `## Learnings` szekció minden bullet-jét gyűjtsd ki

### 2. Routing — minden bullet-re

Alkalmazd a [[11-wiki/Crystallization-protocol#Routing decision tree|routing decision tree]]-t (első találat dönt):

1. **Architektúra-szintű döntés** → új `07-Decisions/YYYY-MM-DD <téma>.md`
2. **Vault-konvenció** → `00-Meta/Tag-taxonomy.md` vagy `Frontmatter-schema.md`
3. **Új evergreen koncepció** → új `11-wiki/<téma>.md`
4. **Új rövidítés / slug** → `00-Meta/Glossary.md`
5. **Szerver / port / cron / DB / service** → `05-Memory/Infrastructure.md`
6. **Skill-leírás** → `05-Memory/Skill-map.md` vagy `Agents-skill-suite.md`
7. **User-preferencia** → `05-Memory/User.md`
8. **Dashboard / Tailscale / hozzáférés** → `05-Memory/Dashboard-access.md`
9. **Projekt-specifikus** → `02-Projects/<slug>.md`
10. **Új TODO** → `04-Tasks/Backlog.md`
11. **Else** → kérdezz a user-től

### 3. Batch preview a user-nek

```
🧠 N tanulság propagálása — ezeket javaslom:

[1] "<bullet-idézet>"
    → 05-Memory/Infrastructure.md ▸ "Next.js gotcha-k" szekció (új alszekció)
    → preview: <2 sor>

[2] "<bullet-idézet>"
    → 05-Memory/User.md ▸ "UI/UX preferenciák"
    → preview: <2 sor>

[3] "<bullet-idézet>"
    → új ADR: 07-Decisions/2026-04-30 <téma>.md
    → preview: <2 sor>

[4] "<bullet-idézet>"
    → új evergreen: 11-wiki/<téma>.md
    → preview: <2 sor>

OK így? Válaszolhatsz röviden:
- "OK" → mind végrehajtva
- "1-3 OK, 4 inkább kgc-berles.md" → módosítás
- "skip 2" → 2 ne menjen, többi jó
- "stop" → semmi
```

### 4. Végrehajtás

A user megerősítése után:
- ADR / wiki esetén: új fájl frontmatter-rel, body-val
- Memory / Project esetén: a target szekcióhoz hozzáfűzés (a frontmatter `updated:` mezőjét frissítsd)
- Tasks/Backlog esetén: új sor a megfelelő prioritás-szekcióba

### 5. Propagation log

A session-fájl `## Propagation log` szekciójába írd be:

```
- 2026-04-30T12:34 — [1] → 05-Memory/Infrastructure.md (új gotcha-szekció: Next.js cross-origin)
- 2026-04-30T12:34 — [2] → 05-Memory/User.md (UI/UX prefs bővítve)
- 2026-04-30T12:34 — [3] → új 07-Decisions/2026-04-30 KGC-Bérlés deploy stratégia.md
- 2026-04-30T12:34 — [4] → új 11-wiki/Same-day-pickup-cutoff.md
- 2026-04-30T12:35 — Backlog frissítve (3 új TODO)
```

### 6. Cleanup

- Ha `.last-stop-prompt` van, töröld (`rm /root/obsidian-vault/.last-stop-prompt`)
- Az érintett fájlok `updated:` frontmatterjét frissítsd

## Mit NE propagálj

- Pillanatnyi state, bug-info amit fixáltunk, implementáció-lépés ami csak során volt érdekes, dupla tudás
- Bizonytalan tanulság → marad a `## Learnings`-ben raw-ként, NE propagáld

## Részletes szabályok + edge case-ek

[[11-wiki/Crystallization-protocol]] — minden szabály, edge case, batch UX.

## Kapcsolódó

- [[11-wiki/Crystallization-protocol]] — protokoll részletesen
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a meta-elv
- [[11-wiki/11.11-session-protokoll]] — a parancs-család
- [[00-Meta/skills/load-session-context/SKILL|load-session-context]] — a session-start párja

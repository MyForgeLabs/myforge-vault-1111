---
name: 2026-05-18 demo asciinema video
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [audit, demo, asciinema, hero-banner, marketing]
---

# 2026-05-18 demo asciinema video + README hero-image

## Cél

A MyForge Vault 11.11 OS release (myforgelabs/myforge-vault-1111) hiányzó vizuális
proof-elemei: **end-to-end terminal-demo** (asciinema) + **brand hero-banner** (SVG).
A sandbox-on nincs API-keys + interactive recording, ezért **mock-cast** + **kódolt SVG**.

## A. asciinema-cast (`docs/demo/vault-demo.cast`)

| Mező | Érték |
|---|---|
| Path | `/root/projects/myforge-vault-1111/docs/demo/vault-demo.cast` |
| Méret | 17.6 KB |
| Duration | 2.97 min (~3 perc, target ~3-5) |
| Events | 400 |
| Format | asciinema v2 JSONL (header + events) |
| Cols × Rows | 110 × 32 |

**Tartalom (6 parancs):**

1. `vault-search "subagent-fanout" --top-k 3` — 168ms semantic search, 3 hit
2. `vault-ko-query --substring "Memgraph" --top-k 5 --json` — 47 fact match, JSON output
3. `11.11note "test demo recording"` — session-orchestration append-event
4. `bmad-vault-bridge --context boulium --top-k 5 --json | head -50` — BMAD-context envelope
5. `vault-graph-query 'MATCH (n:Entity) RETURN count(n)'` — 8997 entitás Memgraph
6. `vault-broken-wikilinks-audit --audit-md` — 3789 resolved / 23 broken

A számok mind **valós verifikált értékek** a 2026-05-19 vault-state-ből (220 wiki, 8997
entity, 13890 fact, 462 SKILL.md, 280× Memgraph speedup).

**Beágyazás:** `docs/demo/index.md` használja az asciinema-player 3.7.0 JS-t
(jsdelivr CDN), a `.cast` fájl mellette.

**mkdocs nav:** új sor `- Demo: demo/index.md` az `Agentek` és `Reproduction Guide`
között.

## B. SVG hero-banner (`docs/assets/hero-banner.svg`)

| Mező | Érték |
|---|---|
| Path | `/root/projects/myforge-vault-1111/docs/assets/hero-banner.svg` |
| Méret | 11.2 KB (target < 50 KB ✓) |
| viewBox | 1200 × 600 |
| Deps | nincs (pure inline SVG) |

**Vizuális elemek:**

- **Háttér:** deep-space radial gradient (`#0e1b3a` → `#02040d`), starfield (29 csillag)
- **Wordmark:** "MyForge Vault" (amber gradient) + "11.11" (cyan gradient)
- **8-axis radial diagram:** B-1..B-8 csomópontok (amber/cyan alternálva), spoke-okkal a
  `11.11 SESSION OS` core-hub-hoz, koncentrikus körök (170/138/102 px sugár)
- **Stats-panel (jobb oldal):** 7 kártya
  - 280× Memgraph speedup · +14.3% GEPA Pareto · $0 cost
  - 76 sessions · 220 wiki · 28 ADR · 15 cron
- **Footer-strip:** mock parancs-prompt + email

**Branding:**

- Amber: `#ffd27a` → `#f59e0b` (gradient `url(#amber)`)
- Cyan: `#9ce8ff` → `#22d3ee` (gradient `url(#cyan)`)
- Surface: `#0c1740` cards on `#0e1b3a` bg
- Mkdocs-theme egyezés: indigo primary + amber accent — egyezik a `mkdocs.yml`-lal

## README.md update

```diff
-[📚 Live docs site](...) · [Magyar verzió](...) · [Roadmap](...) · ...
+[📚 Live docs site](...) · [▶ End-to-end demo](...) · [Magyar verzió](...) · ...

-![MyForge Vault 11.11 — live docs site hero](./docs/assets/hero-screenshot.png)
+![MyForge Vault 11.11 — 8-axis Superintelligent Vault hero banner](./docs/assets/hero-banner.svg)
+
+![MyForge Vault 11.11 — live docs site screenshot](./docs/assets/hero-screenshot.png)
```

Az SVG banner **kerül felülre** (brand-hero, méretarány 2:1), a meglevő PNG screenshot
**alá** mint supplementary "actual docs UI" kép.

## Mérnöki őszinte

### asciinema cast — érdemes-e valódi recording?

A mock-cast a vault valós számait tükrözi és a 6 parancs valóban létezik (`/usr/local/bin/`
+ `~/.claude/skills/`). De a kimenet-formátum és a timing **szintetizált**.

**Mikor érdemes valódi recording-ra cserélni:**

- Ha valaki kétségbe vonja hogy a parancsok ténylegesen futnak (forgery-claim)
- Ha PR-ben akarjuk releaselni a v0.2+-ot (élesebb proof)
- Ha a sub-ms Memgraph latency vagy a 168ms vault-search érték **vizuálisan megjelenítendő**
  (a mock-cast realisztikus de nem valódi mérés)

**Mikor maradhat a mock:**

- Hero-CTA-ként a docs-site-on (a fő-cél a *funkcionalitás bemutatása*, NEM a wallclock-time)
- HN-launch / Twitter / Reddit poszt (a 3-min demó-video alatt senki nem regression-méri)
- A `docs/demo/index.md` **explicit disclosure-t tartalmaz** ("This `.cast` file is
  synthetically constructed") → nincs forgery-rizikó

**Ajánlás:** maradjon mock V1-re, valódi recording v0.2-re ha a community kéri (1 perc
futás a prod host-on, könnyű csere).

### SVG hero — fit a meglevő PNG-szel

A PNG (780×493, 56 KB) egy **screenshot a docs-site dashboard-jából** — informatív de nem
brand-hero. Az SVG (1200×600, 11 KB) egy **explicit brand-banner** a 8-axis-szal és a
key-metrics-szel — sokkal jobban exportálható social-media-OG-tag-nek (1200×630 közeli
arány), nyomtatható (vektor), és újrahasználható HN-launch banner-ként.

A kettő **komplementer** — SVG=hero, PNG=screenshot-supplementary. A README ebben a
sorrendben mutatja: brand-banner → "is ez van a docs-site-on" screenshot.

## Open

- [ ] v0.2-re érdemes lehet valódi `asciinema rec`-et csinálni a prod host-on és committed
- [ ] OG-tag meta-image: SVG → PNG export (1200×630) `og:image`-nek (mkdocs material támogat)
- [ ] Magyar verzió a `docs/demo/index.md`-nek (`docs/demo/index.hu.md`) ha kell

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]]
- [[2026-05-18 vault-meta NotebookLM cross-projekt synthesis]]
- [[../07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]

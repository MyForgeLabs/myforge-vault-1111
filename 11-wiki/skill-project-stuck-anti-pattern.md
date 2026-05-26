---
name: Skill-projekt stuck anti-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/reference"]
tag_backfill: 2026-05-19
---
# Skill-projekt stuck anti-pattern

> [!info] Mit hív életre
> Kontraszt-doku a [[skill-project-success-pattern]]-hez. Itt a **stuck-signal**-okat gyűjtjük — azok a tünetek amelyek **megelőzik** a projekt-elakadást. Ha új projekt egy-két jelet mutat, **early-intervention** ajánlott (a hetente átalakítani 6 órás workshop **olcsóbb** mint 3 hónap múlva eldobni).

## A 6 stuck-signal (cross-projekt evidence)

### Signal 1: Planning-overload, kód-undershoot

A BMAD-artifact-sor szépen elkészül (5/7 zöld, ezer sornyi PRD/Architecture), DE a kódbázis **3+ hete pihen**. A planning helyett az értékelés a "tervezem hogy építem".

Evidencia:
- `client-d-federation.md` (2026-04-24): 7 BMAD-artifact-ból 5 KÉSZ (A-Brief 264 sor + C-UX 1046 sor + E-PRD 732 sor + G-Arch 2303 sor), DE "Utolsó kódváltozás: 2026-04-01 (~3 hete pihen)"
- Stuck-azonosító: BMAD-artifact-line-count : commit-count ratio > 100:1 a planning oldalán

**Helyes (success-pattern):** BMAD max 2 hét, utána Day-0 skeleton azonnal kódba.

### Signal 2: Repo `null` vagy üres

A frontmatter `repo:` mezője `null` vagy `(üres mappa)`, és **több hét** múlva sincs első commit. A projekt "diszkussziós-szinten" reked.

Evidencia:
- `client-c-app.md` (2026-05-17): `repo_local_server: null # 2026-05-17: NINCS a Claude-server-en` — bár BMAD telepítve, kód még nincs
- Stuck-azonosító: `repo: null` AND `updated:` >= 14 nap óta nem változott

**Helyes (success-pattern):** Day-0 skeleton EGY committal, akkor is ha üres a logika.

### Signal 3: NotebookLM nincs vagy elavult

A frontmatter `notebooklm:` mező hiányzik, vagy az utolsó source-add 2+ hónapja volt. A projekt **döntés-evidence-nélkül** halad.

Evidencia:
- Több stuck-projekt esetén látszik: NotebookLM mező hiányzik → tech-stack-döntések "hunch-alapúak"
- A success-projekt-eknél (`client-c-app`, `client-d-federation`, `internal-voice-pilot`, `kgc-erp`) **mindegyiknek** van NB-UUID

**Helyes (success-pattern):** new project = new NotebookLM, 5-10 source upload, 3+ deep-dive Q&A.

### Signal 4: Session-fájl-fertő (sok 08-Sessions/ ZÁRT bullet-zé szétaprózódva, NEM crystallize-elve)

Sok rövid session-fájl ZÁRT-tal, de a Learnings **nem** propagálódott wiki / ADR / Memory irányba. A learnings-deficit kumulálódik.

Evidencia:
- Stuck-projekteknél: 4-5 session-fájl ZÁRT, de a `11-wiki/<projekt-related>` mappa üres → tanulás "elveszett"
- A success-projekteknél (`superintelligent-vault`, `robbantott-kereso`) **minden** session-záráskor `## Propagation log` szekció van + 2-3 új wiki született

**Helyes (success-pattern):** session-záráskor crystallization-protokoll KÖTELEZŐ, [[Crystallization-protocol]].

### Signal 5: Cross-link-éhség

A projekt-fájlban **<3 wikilink** van összes. Az agent session-induláskor csak ezt az 1 fájlt látja, nem tudja "felgombolyítani" a teljes kontextust.

Evidencia:
- Stuck-jelű projektek tipikusan: 0-2 wikilink a 02-Projects/<slug>.md-ben
- Success-projektek (`robbantott-kereso`, `superintelligent-vault`, `client-b`): 12-30 wikilink a fájlban

**Helyes (success-pattern):** minden döntés/wiki/session-hivatkozás `[[...]]`-szal kerüljön a projekt-fájlba, NEM path-stringként.

### Signal 6: "Akkor csinálom amikor lesz időm"

A projekt-fájl `## Open` szekciójában 5+ Open-question, **mind decision-igénnyel** (user-input vár), de **nincs `next-call` dátum** sehol. A projekt user-blokkolt és **nincs unblock-action**.

Evidencia:
- `client-d-federation.md` "8 döntés pending Person-B-tól" — de session-szóhasználatban a sorrendben régóta áll
- `teszt-eu.md` "Person-B spec, 8 döntés pending"

**Helyes (success-pattern):** minden Open-question dátum-melletti (`needs-call-by: 2026-MM-DD`) és `04-Tasks/Backlog.md` 🔴-szal nyitva.

## Heatmap: melyik project melyik signal-t mutatja

| Projekt | S1 (planning-overload) | S2 (repo null) | S3 (no-NB) | S4 (lost-learnings) | S5 (cross-link <3) | S6 (no-next-call) |
|---|---|---|---|---|---|---|
| `client-c-app` | — | ⚠️ | — (3 NB) | — | — | ⚠️ |
| `client-d-federation` | ⚠️⚠️ | — | — | — | — | ⚠️ |
| `teszt-eu` | — | — | — | — | — | ⚠️ |
| `kgc-marketing` | — | — | — | ⚠️ | — | — |

## Korai-intervenció checklista

Amikor 2+ signal aktív, hetente egy 30-perces "stuck-audit":
1. **Re-read** a projekt-fájlt — mi az AZ ÉRTÉK ami megérnek hogy 1 órát betegyél most?
2. **Kill** vagy **archive** vagy **active**-ra hozni — ne legyen "zombi" projekt
3. **Egyetlen smallest-step** (15 perc): ha repo null → első commit; ha planning-overload → 1 Day-0 skeleton; ha NB nincs → 3 source upload
4. **Re-evaluate** 1 hét múlva: a stuck-signal-ok csökkentek-e?

## A "zombi-projekt" felelőssége

A vault konvenció: **projekt-fájl törlés sosem, status: archived** mindig. De a `02-Projects/Index.md` "🔬 Kutatás / archív" szekciója ide kerüljön ha **3+ hónap** óta semmilyen progress.

## Source-evidence

- 19 projekt-fájl elemezve `02-Projects/`-ban
- 2 projekt egyértelmű "stuck"-zónában (client-c-app discovery + client-d-federation active-design 24-óta)
- 5 projekt PRODUCTION-state-ben (koko, internal-discord-bot, client-a-shop-bluebird, petanque-client-a-store, client-b-email-arhivum)
- 12 projekt ACTIVE-shipping-state (kgc-erp, kgc-berles, robbantott-kereso, client-b, kgc-marketing, kgc-kivetitok, kgc-tv-cms, teszt-eu, internal-voice-pilot, rojtesbojt, superintelligent-vault, internal-dashboard)
- Crystallization-protocol Learnings-propagation-volumen: success-projekteknél 8-26 bullet/super-session vs stuck-projekteknél <2 bullet/session

## Kapcsolódó

- [[skill-project-success-pattern]] — kontraszt: a 7 sikeres-pattern
- [[Crystallization-protocol]] — session-záró learnings-feed (Signal 4 ellen)
- [[sprint-day-0-skeleton-first]] — Day-0 skeleton (Signal 2 ellen)
- [[notebooklm-seo-competitor-research-pattern]] — NotebookLM-research (Signal 3 ellen)
- [[Auto-context-loading]] — cross-link → context-load (Signal 5 ellen)
- [[bmad-cross-machine-artifact-verification]] — BMAD-artifact-verifikáció (Signal 1 mitigation)

---
name: Skill-projekt successful pattern
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/reference"]
tag_backfill: 2026-05-19
---
# Skill-projekt successful pattern

> [!info] Mit hív életre
> A vault 19 aktív/produkciós projektjének **közös pattern-jeit** desztillálja egyetlen, evergreen-játszanivaló-stb-ben. Ha új projekt indul, ez a checklista a "Day 0" csomag — másold át, és tedd meg ezeket SORRENDBEN. Ha létező projekt elakadt, ezekkel kontrasztolva derül ki melyik hiányzik.

## A 7 kanonikus pattern (cross-projekt evidence)

### 1. Egy-projekt-egy-fájl Source-of-Truth

Minden projekt EGY `02-Projects/<slug>.md` fájllal indul, **frontmatter-rel**: `name`, `type: project`, `status:`, `created:`, `updated:`, `repo:`, `notebooklm:` (ha van), `cssclasses:`. A fájl **élő dokumentum** — nem statikus README, hanem **napi-szinten frissített állapot**.

Konkrét evidencia:
- `koko.md` frontmatter-jén `status: done-with-backlog`, `originSessionId`, `notebooklm` UUID → 1 fájlból visszafejthető a teljes projekt-history
- `robbantott-kereso.md` 80+ sor jelenlegi-állapot-szekcióval, HEAD-commit-hash, pytest-baseline
- `internal-discord-bot.md` 40 sor: systemd-service név, log-path, dev-path — minden ami "hol fut és hogy nézem"

**Mit ad:** session-induláskor 1 fájl `Read`-elésével az agent teljes kontextust kap.

### 2. NotebookLM-mel deep-research minden új projektnél

Sikeres projektek többségében: **dedikált NotebookLM** UUID a frontmatter-ben + 3-7 source uploaded + 5-10 deep-dive Q&A doc-olva. A research a **planning-fázist** rövidíti 1-2 héttel.

Evidencia: 
- `client-c-app.md`: 3 notebookLM (client-c-app + 2× Client-D-federation keresztreferenciára) + 5 deep-dive Q&A doc
- `client-d-federation.md`: `notebooklm: e7b17612-…` + BMAD-planning-output 7 artifact
- `internal-voice-pilot.md`: 4 NotebookLM, 123 source, 22 HU ask, 3 audio overview
- `kgc-erp.md`: NotebookLM-mel Client-A-system integrációs research, 161 source / 28K token

**Mit ad:** technológiai döntések evidence-grounded-ek, nem hunch-alapúak.

### 3. BMAD-workflow / 7-artifact planning

Stuck-projektek azok, ahol a planning-output **soha nem váltott** kódra. Sikeres projektek a 7-artifact BMAD (A-Product-Brief, B-Trigger-Map, C-UX-Scenarios, D-Design-System, E-PRD, F-Testing, G-Architecture) gyors-csomagját megcsinálják (ideális: <2 hét), majd **azonnal Day-0-skeleton-t** építenek.

Evidencia: 
- client-d-federation.md a 7 artifact-ból 5-öt KÉSZ-rel jelölte (1046+732+2303 sor) — de a kód-side 3+ hete pihen → planning-overload risk
- `robbantott-kereso` ezt megfordította: ELŐSZÖR Day-0-pipeline, BMAD csak akkor amikor 7 commit állt fenn

**Mit ad:** strukturált planning-state, de NEM helyettesíti a kódot.

### 4. Day-0 skeleton-first

Minden ÚJ projekt ELSŐ commit-ja egy **skeleton 1-committal**, funkcionális kód = 0 (kivéve <20-sor + no-API). Mit tartalmaz: package.json, .gitignore, README.md csontváz, 1 health-check-endpoint, 1 vázlat-UI. Lásd [[sprint-day-0-skeleton-first]].

Evidencia: 
- `robbantott-kereso` BMAD-mentes Day-0 → 7 commit egy sprintben
- `internal-voice-pilot` sprint 1 — mockup HTML első, voice MVP második
- `client-a-shop-bluebird` production, scaffold-first → PM2 + scraper később

**Mit ad:** kódbázis indul, momentum építhető rá.

### 5. Session-driven progress (08-Sessions/<slug>.md)

Minden munka-blokk dedikált session-fájllal: `08-Sessions/YYYY-MM-DD-<projekt>.md`. Frontmatter `project:` + `originSessionId:`. **Summary + Learnings + Next** szekciók session-záráskor. Crystallization-protokoll szerint a Learnings propagálódnak a vault-ba.

Evidencia: 
- `robbantott-kereso` 2026-05-16 session → 7 commit + 3 új wiki + new ADR
- `superintelligent-vault` 5× "super-session" (~3-16h)-ban 95 task LANDED
- Vault 168 session-fájl (`08-Sessions/`) az utolsó 6 hónapban

**Mit ad:** időbélyegzett progress-history, learnings-feed, crystallization-input.

### 6. Production = systemd + nginx + named-deploy-path

A PRODUCTION-státuszú projekt MINDEGYIKE:
- **Dedikált deploy-path** (pl. `/opt/petanque/web`, `/root/projects/internal-discord-bot`)
- **Process-manager** (PM2 vagy systemd-service)
- **Nginx-reverse-proxy** (vagy Caddy)
- **Named-service** és audit-log (`journalctl -u <service>`)
- **Backup-path** kanonikus helyen (`/opt/backups/daily/`)

Evidencia: 
- `internal-discord-bot.service` systemd + journalctl
- `client-a-shop-bluebird` PM2 + cron-scraper
- `petanque-client-a-store` PM2 `petanque-web` port 3002
- `client-b` Hostinger staging + nginx + lscache
- `internal-dashboard` systemd + Tailscale-only

**Mit ad:** "élesben fut" reprodukálható minimum-csomag.

### 7. Cross-link projekt → wiki + ADR + Memory

Minden sikeres projekt-fájl wikilinkkel hivatkozza a **wiki-pattern**-jeit, a saját **ADR**-jeit, és a relevánst **Memory**-szekciókat. Ez a Karpathy-féle filesystem-as-state — az index-rendszer természetesen kibontakozik.

Evidencia: 
- `robbantott-kereso.md` 12+ wikilink: `[[07-Decisions/...]]`, `[[08-Sessions/...]]`, `[[11-wiki/nextjs-api-proxy-bridge]]`
- `client-d-federation.md` `[[07-Decisions/2026-04-24 Client-D-federation PWA platform-független architektúra]]`
- `client-b.md` design-system wiki + ACF→Elementor playbook

**Mit ad:** session-induláskor az agent 1 fájlból kibogozza a teljes context-grapfot.

## Sorrend (a meta-pattern)

```
1. (Discovery) → 02-Projects/<slug>.md + frontmatter
       ↓
2. NotebookLM deep-research + 5-10 Q&A doc-elve
       ↓
3. BMAD 7-artifact (gyors, max 2 hét) — DE NEM kész = nincs kód
       ↓
4. Day-0 skeleton commit (1 commit, 0 funkcionális kód kivéve <20 sor)
       ↓
5. Session-blocks (08-Sessions/) — Summary+Learnings+Next minden zárás
       ↓
6. Production (systemd+nginx+backup+monitoring) — ha a use-case megéri
       ↓
7. Cross-link minden lépést → wiki + ADR + Memory (filesystem-as-state)
```

## Mit jelez egy "egészséges" projekt-fájl

A frissítettem-utoljára metrika **<14 nap**. A projekt-fájl tartalmaz:
- [ ] Aktuális frontmatter (`updated:` < 14 nap)
- [ ] Jelenlegi-állapot szekció dátummal
- [ ] HEAD commit-hash vagy production-version
- [ ] 3+ wikilink (cross-link)
- [ ] NotebookLM UUID (research-evidence)
- [ ] Tech-stack táblázat
- [ ] 1+ session-link az utolsó hónapban

## Kapcsolódó

- [[sprint-day-0-skeleton-first]] — Day-0 skeleton-first playbook
- [[skill-project-stuck-anti-pattern]] — kontraszt: mi NEM működik
- [[bmad-cross-machine-artifact-verification]] — BMAD artifact-verifikáció session-záráskor
- [[Auto-context-loading]] — projekt-fájl-detektálás session-induláskor
- [[11.11-session-protokoll]] — session-szervezés
- [[notebooklm-seo-competitor-research-pattern]] — NotebookLM research-flow
- [[Karpathy-LLM-Wiki-pattern]] — háttér-filozófia (filesystem-as-state)

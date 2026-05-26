---
name: Auto-context-loading — start-time pre-load
type: wiki
tags: ["#type/reference", "agents", "11.11", "context"]
created: 2026-04-30
updated: 2026-05-20
last_modified: 2026-05-20-obsidian-vault-2
source:
  - "[[11-wiki/Karpathy-LLM-Wiki-pattern]]"
  - "[[11-wiki/11.11-session-protokoll]]"
---

# Auto-context-loading

> [!info] Status update 2026-05-20
> A lent leírt **aggressive ~15-20K** stratégia a v1 (legacy). A production-default mostantól a **lean ~5K MemGPT virtual + RRF hybrid-fusion** pattern, lásd: `~/.claude/skills/load-session-context/SKILL.md`.
> - **Semantic-fetch parancs:** `vault-search-fusion "<query>"` (NEM `vault-search`) — RRF fusion vault-search + agentmemory, **77.5% avg R@5** (+23pp vs vault-search alone)
> - **Audit:** [[../06-Audits/2026-05-20 Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation]]
> - **Wiki:** [[rrf-hybrid-fusion-retrieval-pattern]]
>
> A v1-aggressive (lent) megmaradt reference-ként + fallback-ként (ha `vault-search-fusion` üres / Memgraph+agentmemory mindkettő down).

A `/11.11start "<név>"` után az agent **azonnal aggressive pre-load**-ot csinál — minden fontos kontextust beolvas, **mielőtt** a user az első kérdést teszi fel. Cél: a session első percétől a teljes kép meglegyen, ne kelljen "ami volt a múltkor"-t kérdezni.

## Projekt-detektálás a session-névből

A session-név (`/11.11start` paramétere) tartalmazza a projektre utaló kulcsszót. Az agent ezt a táblát használja a [[00-Meta/Glossary]] segítségével:

| Session-név tartalmaz | Projekt-slug | Projekt-fájl |
|-----------------------|--------------|--------------|
| `kgc-berles`, `bérlés`, `kgc-frontend`, `kgc-bér` | `kgc-berles` | [[02-Projects/kgc-berles]] |
| `kgc-erp`, `erp` | `kgc-erp` | [[02-Projects/kgc-erp]] |
| `client-a-shop`, `bluebird` | `client-a-shop-bluebird` | [[02-Projects/client-a-shop-bluebird]] |
| `kgc-marketing`, `marketing-kgc`, `innovation-tour` | `kgc-marketing` | [[02-Projects/kgc-marketing]] |
| `kivetito`, `tv-fal` | `kgc-kivetitok` | [[02-Projects/kgc-kivetitok]] |
| `kgc-tv-cms`, `signage`, `tizen` | `kgc-tv-cms` | [[02-Projects/kgc-tv-cms]] |
| `client-b`, `fogszab` | `client-b` | [[02-Projects/client-b]] |
| `myforge`, `dashboard`, `agentic-os` | `internal-dashboard` | [[02-Projects/internal-dashboard]] |
| `koko`, `chatwoot` | `koko` | [[02-Projects/koko]] |
| `internal-discord-bot`, `discord` | `internal-discord-bot` | [[02-Projects/internal-discord-bot]] |
| `internal-voice-pilot`, `mother-father-language`, `tts`, `vault-brief` | `internal-voice-pilot` | [[02-Projects/internal-voice-pilot]] |
| `client-d-federation`, `petanque-szövetség` | `client-d-federation` | [[02-Projects/client-d-federation]] |
| `petanque-kisgep`, `kisgéparuház` | `petanque-client-a-store` | [[02-Projects/petanque-client-a-store]] |
| `teszt-eu`, `kinda` | `teszt-eu` | [[02-Projects/teszt-eu]] |
| `vault`, `obsidian`, `11.11`, `agent-meta` | (vault-meta) | nincs projekt-fájl, [[02-Projects/Index]] |
| `wellbing`, `wellbeing` | (egyéb) | (no project file) |

Ha ambiguous (több találat), az agent **megkérdezi**: "ez melyik projektre vonatkozik: Client-A-Bérlés vagy Client-A-ERP?"

## Aggressive pre-load — mit olvasson be

Detektált projekt-slug = `<slug>` esetén:

1. **Projekt-fájl** — `02-Projects/<slug>.md` teljes
2. **Utolsó 5 session** — `08-Sessions/` -ből, amelyeknek `project: <slug>` a frontmatterben (vagy substring-match a fájlnévre)
3. **Minden érintett ADR** — `07-Decisions/` -ből amelyek `tags`-ban tartalmaznak `#project/<slug>`-ot, vagy a name/body említi a projektet
4. **Memory releváns része** — `05-Memory/Infrastructure.md`-ből a projekt-szekció (pl. Client-A-Bérlés esetén a Postgres-szakasz, port 3004 mention, deploy-info), `05-Memory/User.md` UI/UX preferenciák
5. **Tasks/Backlog #project tag-jei** — `04-Tasks/Backlog.md`-ből a `#project/<slug>` taggel ellátott TODO-k (open + utolsó 10 closed)
6. **Host-info** — ha a projekt-fájl `repo_prod:` vagy `repo_dev:` mezője alapján prod/dev, akkor `03-Hosts/<host>.md` releváns "Itt fut" szekciója
7. **Daily — ma + tegnap** — `01-Daily/<today>.md` és előző nap, kontextus-folytonosság miatt

## A `## Pre-loaded context` szekció

A session-fájl elejére (a `## Cél` ELŐTT) az agent egy `## Pre-loaded context` szekciót ír, ami listázza mit olvasott be, és **rövid kivonatot** ad mindegyikből (1-2 mondat). Pl.:

```markdown
## Pre-loaded context

> Auto-load 2026-04-30T15:23 — agent: claude

**Projekt:** [[02-Projects/kgc-berles]]
- Status: 🟡 active dev — dev mód 3004-en, deploy + design-döntés pending
- Tech: Next.js 16, Prisma 7 + adapter-pg, kgc-postgres :5433 DB-vel `kgc_berles`

**Utolsó 3 session:**
- [[08-Sessions/2026-04-24-kgc-frontend-fejlesztes]] — pricing v1 + email/SMS
- [[08-Sessions/2026-04-24-kgc-frontend-folytatas]] — settings UI, foglalt-gép hide
- (older sessions léteznek — 2 további a Sessions/Index szerint)

**ADR-ek:**
- [[07-Decisions/2026-04-24 Client-A-Bérlés üzleti szabályok v1]] — tier 7/14/21/28, half-day, same-day cutoff
- [[07-Decisions/2026-04-24 Brand kanonizálás — Client-A BEST Warm Editorial]] — globals.css v5.0
- [[07-Decisions/2026-04-24 Git stratégia — standalone repo + 7 commit + GitHub Flow]]
- [[07-Decisions/2026-04-26 Adattárolás — Postgres saját DB + Prisma]]

**Backlog (open #project/kgc-berles):**
- [ ] Backup: kgc_berles DB hozzáadása /opt/backups/backup.sh
- [ ] Admin Contact + ServiceRequest inbox UI
- [ ] Client-A-system ERP integráció — bérlésszámító motor egyesítés
- [ ] Deploy stabilizálás — systemd kgc-berles.service
- [ ] Env-vars beállítás prod-deploy előtt
- [ ] systemd service kgc-berles.service
- [ ] Walkthrough §2-4

**Infra-relevánsak:**
- [[05-Memory/Infrastructure#Postgres — `kgc-postgres` Docker container]]
- [[05-Memory/Infrastructure#Next.js 16 dev — cross-origin block]]
- [[03-Hosts/srv1482413 - dev]] (kgc-berles dev itt fut)

**User UI/UX preferenciák:**
- HELP_HU minden szekció alatt
- Click-time entity-id store, ne regex parse
- Dashboardról bármit indíthatóvá tenni

> 7 forrás · ~12K token kontextus · ready
```

A `> ready` jelzés után az agent vár a user első kérdésére **teljes betöltött kontextussal**.

## Mi van ha nem detektálható projekt

A session-név pl. "wellbeing", "agentic-os audit", "general thinking" — nincs konkrét projekt-slug.

Ekkor az agent **csak alap-kontextust** tölt be:
1. [[02-Projects/Index]]
2. [[04-Tasks/Backlog]] első néhány bekezdése (sürgős feladatok)
3. [[01-Daily/Index]] mai + tegnapi
4. **Nem mélyül el** — várja a user-irányítást

**Token-budget vault-meta session-höz: ~2K token elég.** A 15-20K cap az aggressive pre-load felső korlátja, **nem cél**. Ha a session vault-meta (workflow-fejlesztés, vault-restructure, smoke-teszt, agent-meta munka), a minimal verzió olcsóbb és pont elegendő — 3 forrás × ~700 token. A 15-20K-t projekt-detektálás esetén használd ki: projekt-fájl + 5 session + ADR-ek + Memory + Backlog + Host. Forrás-validáció: `08-Sessions/_archive/2026-04-30-smoke-teszt-mechanika.md`.

## Mi van több detektált projekt esetén

Pl. `/11.11start "kgc + client-b review"`. Ekkor az agent:
1. Mindkét projekt fájlját + last 2-2 session-jét töltsön be (nem 5-5, hogy ne robbanjon)
2. Csak a közös tématikára (pl. brand) koncentráljon a Memory pre-loadban

## Budget

Cél: **~15-20K token** pre-load. Ha túllóg, először a Tasks/Backlog tételeit rövidítsd (csak az 5 legmagasabb prioritást), aztán a régebbi sessionöket dobd.

## Kapcsolódó

- [[11-wiki/Crystallization-protocol]] — a stop-time párja
- [[11-wiki/11.11-session-protokoll]] — a parancs-család
- [[00-Meta/Glossary]] — slug → projekt feloldó
- [[AGENTS]] — kötelezővé teszi

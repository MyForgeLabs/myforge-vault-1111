---
name: MYFORGE OS dashboard — roadmap v2 (pro + command center)
type: decision
status: proposed
created: 2026-04-24
updated: 2026-04-24
tags: ["#type/decision", "#project/myforge-dashboard", "#env/dev"]
related:
  - "[[02-Projects/Index]]"
  - "[[08-Sessions/2026-04-23-myforge-dashboard]]"
  - "[[10-raw/2026-04-23 — Claude designer prompt - agent dashboard]]"
---

# MYFORGE OS dashboard — roadmap v2

**Cél:** A jelenlegi v0.1 dashboard (https://agent.myforgelabs.com) átlépése **professzionális control-room**-má, ahonnan a teljes agent-infrastruktúra **vezérelhető** (nem csak megfigyelhető).

## 0. Mit tud most (v0.1 baseline)

### Kód
- `/opt/agent-dashboard/web/` — Next.js 16 + Tailwind v4 + Framer Motion
- `app/page.tsx` (69 sor) — 9 szekció egy oldalon
- `lib/vault.ts` (464 sor) — minden adatolvasó
- 17 komponens (1386 sor összesen)
- 3 API route: `/api/dashboard` (GET data), `/api/tasks/toggle` (POST), `/api/skills/run` (SSE)

### Működik
- ✅ Valós vault-adatok: sessions, tasks (42), projects (7), hosts (dev/prod/shared), commits (15), SSL (5 cert), git stats
- ✅ Tasks checkbox → POST `/api/tasks/toggle` → `Backlog.md` írás
- ✅ Skill runner drawer → SSE streaming → 7 whitelistelt parancs
- ✅ Auto-refresh 30s-enként
- ✅ Caddy basic-auth + Let's Encrypt SSL

### Fő hiányosságok (amiket most felfedeztem)

| Kategória | Probléma |
|---|---|
| **Parancs-infra** | 7 fix whitelist, nincs input dialog (pl. firecrawl URL hiányzik), nincs command palette, nincs history, nincs re-run, nincs favorite |
| **Session-control** | Focus/stop/note/start gombok nincsenek — a sessions kártyák tisztán dekoratívak |
| **Host-control** | Nincs terminal, nincs log tail, nincs service restart — csak uptime/disk/ram monitoring |
| **Navigáció** | Egyetlen oldal, nincs routing — projekt/session drill-down nincs |
| **Auth** | Basic-auth Caddy-ban, minden endpoint mezítlen — nincs session cookie, nincs user-scope |
| **Mobil** | Nincs PWA, nincs mobile-optimalizált input |
| **Értesítés** | Nincs push, SSL lejárat passzív, host-offline némán megy el |
| **Vizuális** | Designer-prompt elküldve [[10-raw/2026-04-23 — Claude designer prompt - agent dashboard]], válasz még nem érkezett — jelenlegi UI "rendben de nem brutáljó" |

## 1. Vezérlő elvek

1. **Minden parancs whitelistből fut** — nincs freeform shell. Parancsot hozzáadni kód-commit, nem UI-config (biztonság).
2. **SSE elsődleges stream-mechanizmus** — már bevált `/api/skills/run`-ban, bővítjük minden streaming-igényű endpointra (log tail, terminal kivétel).
3. **Vault mint single source of truth** — minden state `.md` fájlban van. A dashboard csak **olvassa és írja**. Nincs külön adatbázis.
4. **Progresszív enhancement** — a meglévő 9 szekció marad, új funkciók **rétegként** ráépülnek (command palette overlay, modal input, drill-down route).
5. **Egy Decisions-doc per fázis** — ha egy fázis nagy, külön ADR-t kap a tervezéskor.

## 2. Fázisok (prioritás szerint)

### 🔴 Fázis 1 — Command Core (a „profi dashboard" minimum)

**Mit old meg:** Ma nem lehet érdemben parancsot adni a dashboardról. A Quick Actions 8 gomb fix, a Skill Runner drawer passzív.

| Feladat | Leírás | Becslés |
|---|---|---|
| **1.1 Command palette (⌘K)** | `cmdk` npm csomag + `/api/search` endpoint. Fuzzy-find: skillek, sessionök, projektek, hostok, tasks, navigáció-célok. Keyboard shortcut-ok (⌘K megnyit, ↑↓ navig, ↵ fire). | M (4-6h) |
| **1.2 Paraméterezett parancs dialog** | Whitelist-sémába `params: [{name, label, type, required}]` hozzáadás. Palette-ből vagy Quick Action-ből fire esetén modal bekéri a param-okat (pl. firecrawl URL, notebooklm kérdés). | M (3-4h) |
| **1.3 Session-action endpoints + UI** | `POST /api/sessions/<slug>/focus\|stop\|note\|new`. Session kártyákra 3-dot menu hover-rel. Új session a palette-ből `/11.11start "project-task"`. | M (3-4h) |
| **1.4 Run history + persistence** | `/var/lib/agent-dashboard/runs/YYYY-MM-DD-HHMMSS-<cmd>.log` minden skill-futáshoz. Új szekció: „Recent runs" — utolsó 20, re-run gomb, output-megnyitás drawer-ben. | S (2h) |
| **1.5 Toast / status line** | Globális state (Zustand vagy React Context). Minden dashboard-művelet (task toggle, skill fire, session action) visszaigazol: jobb alsó sarok, 3s auto-dismiss, hiba marad. | S (2h) |

**Deliverable:** Command palette megnyitható ⌘K-val. Bármelyik skill/parancs futtatható, session elindítható/zárható a dashboardról, input-paraméterrel. Minden művelet visszaigazolt.

---

### 🟠 Fázis 2 — Control Room (igazi „control-dashboard" képesség)

**Mit old meg:** A host-kártyák csak monitoring. Profi control-room-ban log tail, service restart, terminal van.

| Feladat | Leírás | Becslés |
|---|---|---|
| **2.1 Log tail streaming** | `/api/logs/tail?unit=<systemd-service>` SSE. Drawer-ben megjeleníthető (SkillRunner komponens újrahasznosítva). Whitelistelt unitok: `caddy`, `agent-dashboard`, `chatwoot-watchdog`, `pm2-kgshop`, `pm2-kgc-*`, `mfl-bot`. | M (3-4h) |
| **2.2 Service actions (restart/start/stop)** | `/api/services/<unit>/<action>`. UI: host-kártyán service chip → menu (tail / restart / stop / start). Minden művelet confirm-dialog, audit-log. | M (3-4h) |
| **2.3 Web terminal (xterm.js + ws)** | `/api/terminal/<host>` websocket. xterm.js + `node-pty` wrapper. Only whitelisted hostok (dev lokál, prod SSH). Auto-expire 30 perc idle, max 1 session per user. | L (8-12h) |
| **2.4 Cron status panel** | `/api/cron/status` — crontab + systemd timerek listázása + utolsó run időpont `journalctl -u <name>.service \| tail -1`. Új szekció a dashboardon. | S (2-3h) |
| **2.5 Chatwoot + Kokó action-ok** | Projekt-specifikus quick action: chatwoot restart, Kokó env reload, user impersonation. Külön Decisions-doc készül terv alapján. | TBD — külön terv |

**Deliverable:** Minden host-kártyán van "Terminal" + "Logs" + "Services" gomb. Cron-ok láthatók és újraindíthatók. Ez a „valódi control-room".

---

### 🟡 Fázis 3 — Navigation & Deep-Dive

**Mit old meg:** Egyoldalas dashboard-ot kinőttük. Ha egy projekten dolgozunk, külön oldal kell history-val, related content-tel.

| Feladat | Leírás | Becslés |
|---|---|---|
| **3.1 Projekt drill-down route** | `/projects/<slug>` — markdown-render (`react-markdown` + custom wikilink-resolver) + related sessions (filter project=<slug>) + related tasks (filter tag #project/<slug>) + projekt-commit history (`git log --follow Projects/<slug>.md`). | M (4-6h) |
| **3.2 Session drill-down route** | `/sessions/<slug>` — teljes session markdown + Events timeline-view + link-gombok (focus / note / stop inline). | S (2-3h) |
| **3.3 Host drill-down route** | `/hosts/<slug>` — teljes host-markdown + services-grid service-enként (CPU, memory, restart-count) + log-tail embed + SSH-command runner. | M (4-5h) |
| **3.4 Full-text search a vault-on** | `/api/search?q=...` — egyszerű ripgrep-wrapper (`rg --json --max-count 3 -g '*.md'`) tartalom-matches. Command palette-ben egy „Search vault" tab. | M (3-4h) |
| **3.5 Backlinks / graph** | Minden drill-down oldalon egy „Referenced by" oldalsáv: ki linkel ide `[[slug]]` — ripgrep search `"\[\[...<slug>...\]\]"`. | S (2h) |

**Deliverable:** Kattintható projektek, sessionök, hostok. Keresés a teljes vaulton. Obsidian-szerű navigáció a dashboardban.

---

### 🟢 Fázis 4 — Automation & Alerts

**Mit old meg:** Jelenleg minden passzív: a dashboard megmutatja az SSL-t vagy a host-ot ami offline, de senkinek nem szól.

| Feladat | Leírás | Becslés |
|---|---|---|
| **4.1 Alert rules engine** | `vault/alerts.yml` — deklaratív: `ssl_expiry < 14 days`, `host offline > 5m`, `disk > 85%`, `autosave last > 2h`. Cron (5 perc) `/usr/local/bin/agent-dashboard-alerts` script futtat, eredmény `vault/Audits/alerts.md`-be ír. | M (4-5h) |
| **4.2 Push-notification (Pushover / ntfy.sh)** | Alert trigger-enként HTTP POST a user eszközére. Token-ek `.env`-ben. Self-hosted ntfy javasolt. | S (2-3h) |
| **4.3 Dashboard alert banner** | Top-bar amber/piros banner ha aktív alert. Palette-ből „silence 1h". | S (2h) |
| **4.4 Morning briefing** | `/usr/local/bin/morning-briefing` napi 07:00 — GitHub trending + vault overnight változások + SSL status + cron-check összefoglaló → `raw/YYYY-MM-DD briefing.md`. (Meglévő `github-trending-report` cron kiegészítés.) | S (2h) |

**Deliverable:** Reggel megjön a briefing, az SSL/host-issue-kat proaktívan tudod. Nem kell manuálisan a dashboardra nézni.

---

### 🔵 Fázis 5 — Polish, Auth, Mobile

**Mit old meg:** A basic-auth MVP, a design „rendben de nem brutáljó", mobilról használhatatlan.

| Feladat | Leírás | Becslés |
|---|---|---|
| **5.1 Designer response implementáció** | Amikor [[10-raw/2026-04-23 — Claude designer prompt - agent dashboard]]-ra visszaérkezik a válasz: TOP 5 változtatás kijelölés + implementálás (Tailwind tokens, új komponensek, animation-ok). | M (4-8h) |
| **5.2 Session-based auth** | Next.js middleware + cookie. Login page `/login` → `POST /api/auth/login` → bcrypt check → httpOnly cookie. Caddy basic-auth eltávolítás. Google OAuth opcionálisan `iron-session` + `@auth/core`. | M (4-6h) |
| **5.3 Audit log** | `/var/lib/agent-dashboard/audit.log` JSONL: minden skill-futás, task-toggle, service-action, terminal-open. Drill-down UI Settings-oldalon. | S (2-3h) |
| **5.4 PWA + mobil** | `next-pwa` plugin, manifest, service worker, offline dashboard-cache. Mobil-first touch-targetek, bottom-nav. | M (4-6h) |
| **5.5 Dark/light téma + theme-switcher** | CSS változók már készen. Light mode palette definiálás, header-ben toggle. | S (2h) |
| **5.6 Telepítő script** | `install.sh` — új VPS-re klónozza, deploy-olja. Idempotens. Systemd service, Caddy config, env template. | S (2-3h) |

**Deliverable:** Profi bejelentkezés, mobilon is használható, auditálható minden művelet, új szerverre 10 perc alatt deploy.

## 3. Technikai függőségek

Mielőtt fázisokat végrehajtanánk, felmerülnek közös infrák amelyeket egyszer érdemes megcsinálni:

- **Client state:** Zustand store (nem Context, Next.js 16 + RSC alatt kevesebb re-render). Globális: running skill, toast queue, palette open.
- **Notification layer:** ui komponens (toast/banner) + SSE listener backend eseményre.
- **Shared command-schema:** `lib/commands.ts` — egyetlen forrás ahol minden futtatható parancs definiálva van (cmd, args, params, category, icon). Quick Actions, Palette, Skill Runner ebből olvas.
- **Shared audit logger:** `lib/audit.ts` — minden action endpoint ide logol.

## 4. Nem-célok (most nem csináljuk)

- ❌ Multi-user — egy user (Peti) használja, nem SaaS
- ❌ RBAC / permissions — minden user admin
- ❌ Plugin-rendszer — minden funkció a repo-ban van
- ❌ Saját LLM-integráció a dashboardon — a `claude -p` / `codex` CLI hívja a skill runner
- ❌ Grafana/Prometheus-szerű time-series — vault git history elég
- ❌ PostgreSQL/Redis — vault fájlrendszer + `/var/lib/agent-dashboard/` elég

## 5. Következő lépés — melyik fázissal kezdjünk?

**Javaslat:** **Fázis 1 (Command Core)** — mert a user eredeti kérése pont ez: „a dashboardról lehessen parancsokat adni".

Ha zöld utat kapunk, akkor:
1. Külön ADR-t írok Fázis 1-re bontva 1.1–1.5 tasks-ra konkrét TDD-szerű step-ekkel (`writing-plans` skill-lel)
2. `writing-plans` output → `docs/plans/2026-04-24 F1 Command Core.md`
3. Implementálás `executing-plans`-szel task-onként, commit-onként

Alternatíva: Ha a designer response megérkezik (ellenőrizhető: `ls raw/ | grep designer-response`), akkor először **Fázis 5.1** futtatható párhuzamosan (vizuális).

## 6. Risk / trade-off

| Risk | Mitigáció |
|---|---|
| **Fázis 1 túl nagy** (5 feladat ~15h) | 1.1 + 1.3 első round, 1.2 + 1.4 + 1.5 második round. |
| **Web terminal (2.3) komplex** | Elhalasztható — SSH a VSCode-ból bármikor elérhető. Ha fájl, csak 2.1 + 2.2 kell. |
| **Auth upgrade (5.2) breaks prod** | Caddy basic-auth párhuzamosan marad fallback-ként egy `?force_basic=1` QS-re. |
| **Whitelistelt command-ok súrolás** | Minden új skill commit-on keresztül. `lib/commands.ts` PR → code review → deploy. |

## 7. Idő-becslés összesen

| Fázis | Becslés |
|---|---|
| F1 Command Core | 14-18h |
| F2 Control Room | 20-30h (2.3 terminal nélkül: 10-14h) |
| F3 Navigation | 15-20h |
| F4 Automation | 10-12h |
| F5 Polish | 20-30h |
| **Összesen** | **~80-110h** (2-3 hét fókuszált munka) |

Reális tempóban (napi 1-3h): **6-10 hét**.

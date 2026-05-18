---
name: Teljes infrastruktúra-audit
type: audit
tags: [audit, snapshot, infra]
date: 2026-04-23
author: claude
---

# Teljes infra-felmérés — 2026-04-23

Pillanatkép a teljes Hostinger-környezetről, mindkét VPS-ről, az összes szolgáltatásról, domainről és szoftveres állapotról. Következő audit javasolt: 1-2 hét múlva, vagy bármikor amikor jelentős változás történik.

## TL;DR — az egész egy képen

```
HOSTINGER account (PetykaMaki)
├── 2 VPS (KVM 8, Ubuntu 24.04 LTS, 8 CPU / 32GB RAM / 400GB disk)
│   ├── vps-dev-example (dev/agent-hub)    187.77.70.36    6 nap uptime
│   └── vps-prod-example (prod)             72.62.92.98     72 nap uptime
├── 13 aktív domain (+ 1 lejárt: frankpanama.store)
└── 14 hostolt weboldal (6 staging + 8 éles)
```

| Állapot | Kategória | Részletek |
|---------|-----------|-----------|
| 🟢 | Backup prod | Napi 03:00 fut, utolsó 2026-04-23 03:00 OK |
| 🟢 | Backup bluebird-shop | Napi 03:00 fut, utolsó 11MB (2026-04-23) |
| 🟢 | Auto VPS backup | Hostinger: heti backup, utolsó 2026-04-19 |
| 🟢 | Vault auto-save | Mindkét szerverről 10 percenként commit + push |
| 🟢 | SSL certs | Mind érvényes 1-3 hónapig |
| 🟡 | Chatwoot gemini-proxy | **unhealthy** state dev-en |
| 🟡 | VPS snapshot | Nincs manuális snapshot egyik gépen sem |
| 🔴 | `frankpanama.store` | **lejárt** 2026-03-21 |
| ⚫ | Hostinger MCP npm package | failed to connect — REST API direktben OK |

---

## 1. VPS-ek

### vps-dev-example — dev / agent-hub

| Mezö | Érték |
|-----|-------|
| ID | 1199845 + 1482413 (plan: KVM 8) |
| IPv4 | `187.77.70.36` |
| IPv6 | `2a02:4780:79:21b8::1` |
| DC | data_center_id=19 |
| OS | Ubuntu 24.04.4 LTS, kernel 6.8.0-90 |
| CPU | AMD EPYC 9354P, 8 vCPU |
| RAM | 31 GB (18 GB használatban) |
| Disk | 387 GB / 15% használat (56 GB) |
| Uptime | 6 nap+ |
| Created | 2026-03-11 |

**Szerepe:** dev / scratch, agent-hub, example-balance.local frontend, VNC hoszt. Itt fut az obsidian-vault elsődleges forrása, a 3 agent (Claude/Codex/Gemini).

#### Systemd (non-default)

| Service | Állapot |
|---------|---------|
| `caddy.service` | ACME SSL-es reverse proxy (kivetito.myforgelabs.com, koko.myforgelabs.com) |
| `kinda-web.service` | Kinda Next.js web, port 3001 (→ beta.example-balance.local) |
| `fail2ban.service` | SSH brute-force védelem |

#### Docker stackek (16 container, 4 compose project)

| Stack | Hol (compose working dir) | Container-ek | Memória/Volume |
|-------|--------------------------|--------------|----------------|
| **chatwoot** | `/opt/chatwoot` + `/root/projektjeim/opt/chatwoot` | 10 db (rails, sidekiq, postgres, redis, ai-chatbot, discord-bridge, gemini-proxy ⚠️ unhealthy, context-manager, calendar-service, stats-service) | ~500MB volume |
| **kinda** | `/root/projektjeim/kinda/docker` | kinda-mysql (:3307), kinda-redis (:6381) | — |
| **kgc** | `/root/projektjeim/kgc` | kgc-postgres (:5433), kgc-redis (:6380), kgc-minio (:9002/:9003) | — |
| **excalidraw-z7hg** | `/docker/excalidraw-z7hg` | excalidraw :32768 → whiteboard | — |

**Docker összesen:** 14 image (8.5GB), 16 container (118MB), 8 volume (386MB), build cache 1.7GB.

#### Közvetlenül futó processzek

- **Next.js (kinda-web.service)** PID 1057727, port 3001 → beta.example-balance.local
- **Vite dev server** (KGC-WEB frontend), port 3005 → csak belső

#### Caddy reverse proxy (`/etc/caddy/Caddyfile`)

| Domain | → upstream |
|--------|-----------|
| `kivetito.myforgelabs.com` | → `http://72.62.92.98:8200` ([[03-Hosts/vps-prod-example - prod]]) |
| `koko.myforgelabs.com` | → `localhost:5004` (Kokó context-manager) |

#### VNC setup

- `x11vnc` display `:99`, port `5900` (`/root/.vnc/passwd`)
- `noVNC` / `websockify` port `6080` — `http://<host>:6080/vnc.html`

#### Top memóriafogyasztók

- **next-server (Kinda)** — 4.5 GB
- **cloudcode_cli** — 3.3 GB + 2.3 GB (agent subprocessek)
- **vscode-server** — 1 GB
- **antigravity-server** — 984 MB + 776 MB (Gemini-integráció)
- **claude** (Claude Code CLI) — 540 MB

#### Verziók

Node 22.22.2, npm 11.13, pnpm 10.33, Bun 1.3.11, Python 3.12.3

---

### vps-prod-example — prod

| Mezö | Érték |
|-----|-------|
| ID | 1199845 |
| IPv4 | `72.62.92.98` |
| IPv6 | `2a02:4780:41:2242::1` |
| DC | data_center_id=19 |
| OS | Ubuntu 24.04 LTS |
| CPU | AMD EPYC 9354P, 8 vCPU |
| RAM | 31 GB (10 GB használatban — 21 GB free) |
| Disk | 387 GB / 28% használat (106 GB) |
| Uptime | 72 nap, load 0.27 (nyugodt) |
| Created | 2025-12-15 |

**Szerepe:** éles production, ügyféltalálkozó-oldalak, éles Kokó + Chatwoot, KGC-ERP, bluebird-shop (kgshop), mfl-bot, uptime-kuma.

#### Systemd (non-default, enabled+running)

| Service | Mit csinál | Hol |
|---------|------------|-----|
| `caddy.service` | (implicit — csak nginx van valójában itt) | — |
| `nginx.service` | Reverse proxy az összes publikus oldalhoz | `/etc/nginx/sites-enabled/` |
| `kgc-api.service` | KGC ERP NestJS API | `/root/projects/kgc/apps/kgc-api` (pnpm dev) |
| `kgc-web.service` | KGC ERP Vite frontend port 5174 | `/root/projects/kgc/apps/kgc-web` |
| `mfl-bot.service` | MFL Discord bot (Python) | `/root/projects/mfl-bot/venv/bin/python3 bot.py` |
| `gemini-watcher.service` | MCP bridge task watcher | `/opt/mcp-bridge/scripts/gemini-watcher.mjs` |
| `pm2-root.service` | PM2 process manager | — |
| `postgresql.service` | Natív Postgres (kgshop port 5435) | — |
| `fail2ban.service` | sshd jail | — |
| `ufw.service` | Firewall | — |
| `ssl-cert.service` | Snake-oil SSL (default Ubuntu) | — |

#### PM2 processes

| PID ID | Name | Script | CWD | Status |
|--------|------|--------|-----|--------|
| 3 | **kgshop** | `start-production.sh` | `/root/projects/bluebird-shop` | online |
| 4 | **kgshop-scraper** | (same project) | `/root/projects/bluebird-shop` | online |
| 2 | **mcp-bridge-backend** | `server.mjs` | `/opt/mcp-bridge` | online |
| 0 | **petanque-web** | `npm start -- -p 3002` | `/opt/petanque/web` | online |
| 1 | **maromas-demo** | N/A | — | online (no PID) |

**Megjegyzés:** petanque-web `/opt/petanque/web` path — ez a `example-petanque.local` oldal (lásd nginx → `127.0.0.1:3002`)!

#### Docker stackek (15 container, 4 compose project)

| Stack | Compose dir | Container-ek |
|-------|-------------|--------------|
| **chatwoot** (éles) | `/opt/chatwoot` | rails, sidekiq, postgres (pgvector), redis, ai-chatbot, discord-bridge, gemini-proxy, context-manager (Kokó!), calendar-service, stats-service |
| **bluebird-shop** | `/root/projects/bluebird-shop` | bluebird-shop-db-1 (postgres) |
| **kgc** | `/root/KGC` | kgc-postgres, kgc-redis, kgc-minio |
| **uptime-kuma** | `/opt/uptime-kuma` | uptime-kuma |

**Docker összesen:** 14 image (10.4 GB), 15 container (3.6 GB), 8 volume (760 MB).

#### Docker volume méretek

| Volume | Méret |
|--------|-------|
| `bluebird-shop_pgdata-dev` | 191.7M |
| `chatwoot_postgres_data` | 112.4M |
| `chatwoot_redis_data` | 1.4M |
| `chatwoot_storage_data` | 832K |
| `kgc_minio_data` | 108K |
| `kgc_postgres_data` | 49.7M |
| `kgc_redis_data` | 12K |
| `uptime-kuma_uptime-kuma-data` | 386.3M |

#### Publikus szolgáltatások — nginx sites

| nginx site | listen | server_name | → upstream | Publikus URL |
|-----------|--------|-------------|-----------|-------------|
| `chatwoot` | 80/443 | `mfl.support` | rails (3000) + /api/faq:5000 + /api/knowledge:5000 + /api/calendar:5002 + /stats:5003 + /koko:5004 (Kokó admin UI) | https://mfl.support |
| `status.mfl.support` | 80/443 | `status.mfl.support` | `127.0.0.1:3001` (uptime-kuma) | https://status.mfl.support |
| `example-petanque.local` | 80/443 | `example-petanque.local`, `www.example-petanque.local` | `127.0.0.1:3002` (PM2 petanque-web!) | https://example-petanque.local |
| `kgc-erp` | 8100 | `_` | `127.0.0.1:3100/api/` + `127.0.0.1:5173/` | belső — KGC-ERP admin |
| `kgc-kivetito` | 8200 | `_` | `/var/www/mfl.support` statikus | [[03-Hosts/vps-dev-example - dev]] Caddy-ja proxy-zi `kivetito.myforgelabs.com`-ra |

#### SSL certs (Let's Encrypt) — expiry

| Domain | Lejár |
|--------|-------|
| `boulium.com` | **2026-05-28** |
| `example-petanque.local` | 2026-07-16 |
| `mfl.support` | 2026-07-18 |
| `plane.myforgelabs.com` | **2026-06-05** |
| `status.mfl.support` | 2026-07-06 |

> [!info] Auto-renew
> Certbot cron valószínűleg fut (standard Let's Encrypt setup). Ellenőrzés ajánlott `systemctl list-timers | grep certbot`.

#### /opt struktúra

| Path | Méret | Mi ez |
|------|-------|-------|
| `/opt/chatwoot` | 293M | Chatwoot + Kokó éles deploy (Docker compose) |
| `/opt/mcp-bridge` | 39M | MCP bridge backend (PM2) |
| `/opt/backups` | 17M | Backup scriptek + daily/monthly retention |
| `/opt/uptime-kuma` | 12K (volume külön) | uptime-kuma config |
| `/opt/containerd` | 12K | Docker runtime |
| `/opt/ollama-api.py` | 8K | Ollama REST wrapper (helyi LLM) |

#### /root struktúra

| Path | Méret | Mi ez |
|------|-------|-------|
| `/root/projects` | **12 GB** | Fő kód-repók (kgc, bluebird-shop, mfl-bot, foxxi, barberbp, Kisgépcentrum-marketing, myforgelabs.com, teszt-eu, zsofi-law, mfl) |
| `/root/backups` | 98M | kgshop backup-ok |
| `/root/tools` | 97M | Globális eszközök |
| `/root/obsidian-skills` | 372K | Közös skill-repó (új) |
| `/root/obsidian-vault` | 540K | Közös vault (új, 2026-04-23) |
| `/root/docs` | 132K | — |
| `/root/KGC/infra` | 16K | Csak infra (docker-compose) — a tényleges kód `/root/projects/kgc`-ben |
| `/root/CLAUDE.md` | 293 sor (backup: `.backup_20260423`) → symlink `AGENTS.md`-re | |

#### Cron

```cron
*/5 * * * *     /opt/chatwoot/scripts/chatwoot-watchdog.sh         # Chatwoot health loop
0 3 * * *       /opt/backups/backup.sh                              # Napi globális backup 03:00
0 3 * * *       /root/projects/bluebird-shop/scripts/pg-backup.sh   # Napi kgshop postgres dump
*/10 * * * *    AGENT=vps-prod-example /usr/local/bin/vault-autosave      # Vault autosave (új)
```

#### Backup állapot (2026-04-23 reggel)

**`/opt/backups/daily/2026-04-23/`** (1.7 MB összesen):
- `chatwoot_production.sql.gz` — 229 KB
- `chatwoot-redis.rdb` — 1.4 MB
- `chatwoot-data.tar.gz` — 55 KB
- `kgc_erp.sql.gz` — 556 B

Retention: napi 7 nap, havi 365 nap.

**`/root/backups/kgshop/`** — `kgshop_20260423_030001.sql.gz` = 11 MB, 8 fájl megtartva (7 nap retention).

**Hostinger auto-backup:** heti, utolsó 2026-04-19 (~104 MB) + 2026-04-12 (~60 MB).

#### mfl-bot — mit csinál

Python Discord bot, Futtat: `/root/projects/mfl-bot/bot.py` venv-ből. A logokból látszik hogy **valódi MFL csatornákról olvas üzeneteket** (pl. lakovari, gataizsuzsa felhasználóktól), gateway session stabilan RESUME-ol. Részletes infó: [[02-Projects/mfl-bot]] (még nincs létrehozva).

#### Top memória

- claude-mem worker (Bun) — 532 MB
- Next.js (Chatwoot rails app?) — 430 MB
- puma (Ruby) — 333 MB (Chatwoot)
- sidekiq (Ruby) — 319 MB (Chatwoot)
- NestJS (kgc-api) — 220 MB

#### Verziók

Node 22.22.0, pnpm 10.28.2, Python 3.12.3, PostgreSQL natív + 2 dockerizált

#### fail2ban

Csak `sshd` jail aktív. SSH brute-force védelem ki van építve.

---

## 2. Domainek és hova mutatnak

### A-rekordok (Hostinger DNS, kivonat)

| Domain | Hoszt | IP | Szerver |
|--------|-------|-----|---------|
| `beta.example-balance.local` | A | 187.77.70.36 | dev (kinda-web Next.js) |
| `kivetito.myforgelabs.com` | A | 187.77.70.36 | dev (Caddy → prod:8200) |
| `koko.myforgelabs.com` | A | 187.77.70.36 | dev (Caddy → localhost:5004) |
| `plane.myforgelabs.com` | A | 72.62.92.98 | prod (Plane.so?) |
| `status.mfl.support` | A | 72.62.92.98 | prod (uptime-kuma) |
| `mfl.support` | A | 72.62.92.98 | prod (Chatwoot főoldal) |
| `example-balance.local` root | ALIAS | Hostinger CDN | CDN (regi static?) |
| `myforgelabs.com` root | ALIAS | Hostinger CDN | CDN |

### CDN vs. VPS

A **example-balance.local root** és **myforgelabs.com root** Hostinger CDN-en van (ALIAS-CNAME), nem a VPS-eken. A subdomainek VPS-ekre mennek direktben.

### Email

Google Workspace (Gmail MX) myforgelabs.com-ra. Hostinger mail mfl.support, boulium.com, stb. domainekre (MX: `mx2.shared-hosting-example.com`). DKIM record-ok rendben be vannak állítva.

### Minden hostolt weboldal

14 db: 6 staging (`*.hostingersite.com`) + 8 élő (`example-balance.local`, `myforgelabs.com`, `mfl.support`, `boulium.com`, `boulium.blog`, `frankpanama.com`, `frankpanama.store` (cert lejárt), `gordeszkasuli.com`).

### Lejárt domain

> [!danger] `frankpanama.store` lejárt 2026-03-21
> Ha még szükséges, Hostinger admin-ban meg kell újítani.

---

## 3. Projekt → szerver → kód-repo mapping

| Projekt | Éles szerver | Éles path | Dev szerver | Dev path | Éles URL |
|---------|--------------|-----------|-------------|----------|---------|
| [[02-Projects/teszt-eu\|example-balance.local]] / Kinda | dev | `kinda-web.service` → `/root/projektjeim/kinda` port 3001 | dev | ugyanott | https://beta.example-balance.local |
| [[02-Projects/koko\|Kokó]] | prod | `/opt/chatwoot` (Docker compose) | dev | `/root/projektjeim/opt/chatwoot` (helyi copy) | https://mfl.support + `/koko` |
| KGC-ERP | prod | `kgc-api` + `kgc-web` systemd + docker stack `/root/KGC/infra` | dev | `kgc` docker stack (csak DB) | belső (port 8100) |
| bluebird-shop (kgshop) | prod | `start-production.sh` (PM2) + `bluebird-shop-db-1` | dev | — (csak DB adat dev-en is van) | belső |
| petanque / example-petanque.local | prod | `/opt/petanque/web` (PM2 petanque-web) | — | — | https://example-petanque.local |
| mfl-bot | prod | `mfl-bot.service` Python venv | — | — | Discord |
| uptime-kuma | prod | Docker `/opt/uptime-kuma` | — | — | https://status.mfl.support |
| excalidraw | dev | Docker `/docker/excalidraw-z7hg` | dev | ugyanott | belső port 32768 |
| mcp-bridge | prod | `/opt/mcp-bridge` (PM2) | — | — | — |

---

## 4. Ismert problémák + ajánlások

### 🔴 Azonnali

1. **`frankpanama.store` domain lejárt** (2026-03-21). Megújítani vagy tudatosan elengedni.
2. **`chatwoot-gemini-proxy-1` unhealthy dev-en.** `docker logs chatwoot-gemini-proxy-1 | tail` megnézni, healthcheck-et javítani, vagy leállítani ha nem kell.

### 🟡 Figyelni

3. **Boulium.com SSL lejár 2026-05-28** (~1 hónap). Certbot renewal működésének ellenőrzése.
4. **plane.myforgelabs.com SSL lejár 2026-06-05.** Uaz.
5. **Nincs VPS snapshot** egyik gépen sem (Hostinger admin → Snapshots). Autobackup heti — ha napközben vész kell, snapshot jó.
6. **Két chatwoot compose** dev-en (`/opt/chatwoot` + `/root/projektjeim/opt/chatwoot`). Ez dupla image/volume/port ütközést okozhat. Átnézni melyik aktív és a másikat leállítani.

### 🟢 OK

- Mindkét gép backupja fut (Hostinger weekly + saját scriptek napi).
- fail2ban mindkét gépen aktív.
- kinda-web, kgc-api, kgc-web, mfl-bot mind `active (running)`.

### Hostinger MCP

- Az `hostinger-api-mcp` npm package **nem indul** (Node compat: `Class extends value undefined is not a constructor or null`). 
- **REST API közvetlenül működik** (token: a [[03-Hosts/Index]]-ben). Ezt használtuk jelen audithoz.
- Ha MCP-n keresztül akarod futtatni: `npx hostinger-api-mcp@<régebbi-verzió> mcp` lehet megoldás, vagy kivárni egy új release-t.

---

## 5. Kész (mai) agent-infrastruktúra

[[07-Decisions/2026-04-23 Unified agent memory|Közös vault]] + [[07-Decisions/2026-04-23 Session orchestration|11.11 parancs-család]] mindkét szerveren:

- `/usr/local/bin/11.11*` — health check + session open/note/stop
- `/usr/local/bin/vault-autosave` — 10 percenként commit + push (conflict-safe pull-rebase, fail → abort, next tick retry)
- `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md` → symlink `/root/obsidian-vault/AGENTS.md`-re
- Bidirekcionális GitHub sync (dev → PAT, prod → deploy-key)
- `/11.11` host-adaptív (VNC opcionális, projektjeim/projects fallback)

---

## 6. Referenciák

- [[03-Hosts/Index]] — gyors dashboard
- [[03-Hosts/vps-dev-example - dev]] — dev részletek
- [[03-Hosts/vps-prod-example - prod]] — prod részletek
- [[02-Projects/Index]] — projekt-lista
- [[05-Memory/Infrastructure]] — szerverek közötti dolgok
- [[07-Decisions/]] — architektúra-döntések naplója
- Hostinger API docs: https://developers.shared-hosting-example.com/

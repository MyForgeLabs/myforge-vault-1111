---
name: Audit 2026-04-23 akciók + fennmaradó elemek
type: decision
status: in-progress
tags: [adr, audit, actions]
date: 2026-04-23
---

# 2026-04-23 — Audit actions

Az [[06-Audits/2026-04-23 Teljes infra audit]] jelentés alapján mit csináltunk meg és mi maradt.

## ✅ Elvégezve

### Infra

- [x] **VPS snapshot** mindkét gépre (Hostinger API, `POST /vps/v1/virtual-machines/<id>/snapshot`)
  - Dev `vps-dev-example` snapshot ID **251316** — 2026-04-23 16:17 UTC, expire 2026-05-13, restore ~30 perc
  - Prod `vps-prod-example` snapshot ID **251317** — 2026-04-23 16:17 UTC, expire 2026-05-13, restore ~30 perc
- [x] **Chatwoot gemini-proxy healthcheck** javítva (`/opt/chatwoot/docker-compose.yaml`): `curl -f` → `python3 + urllib.request`. `docker compose up -d gemini-proxy` recreated. Állapot: `unhealthy` → **`healthy`**
- [x] **Certbot auto-renew** működését ellenőriztük prod-on: `certbot.timer` systemd aktív, napi 2× fut (következő indítás 21:05 UTC). Renewal attempt 2026-04-23 08:19 sikeres. Minden élő cert-re érvényes.

### Dokumentáció

- [x] **Projekt-fájlok** létrehozva a fennmaradó projektekre:
  - [[02-Projects/kgshop-bluebird]]
  - [[02-Projects/petanque-kisgeparuhaz]]
  - [[02-Projects/mfl-bot]]
  - [[02-Projects/kgc-erp]]
- [x] [[02-Projects/Index]] frissítve: a ⭐ Aktív tábla most 6 projektet tartalmaz

## ⚠️ Nyitva — user-döntés kell

### `frankpanama.store` domain lejárt (2026-03-21)

**Hol:** https://hpanel.shared-hosting-example.com → Domains → frankpanama.store
**Lehetőségek:**
1. **Megújítani:** Hostinger admin-ba belép → Renew. Várhatóan már grace period-ban van, esetleg redemption — költség függ ettől.
2. **Elengedni:** Nem csinálunk semmit. 30-90 nap múlva Hostinger-nél automatikusan törlődik, utána bárki regisztrálhatja.

**Ez billing-döntés — az agent nem dönthet automatikusan.** Ha megújítod, frissítsd [[03-Hosts/Index|Hosts dashboard]] tábláját.

### Dupla Chatwoot compose a dev-en

**Mi a helyzet:**
- `/opt/chatwoot/docker-compose.yaml` — 2026-04-23 módosítva (most mi módosítottuk a healthcheck-et)
- `/root/projektjeim/opt/chatwoot/docker-compose.yaml` — 2026-04-19 módosítva

Mindkettő ugyanazt a Docker project-et (`chatwoot`) használja, ezért ugyanazok a container-nevek. A `docker ps --format` label vizsgálatnál kiderült: a container-ek vegyesen vannak spawnelve a két compose-ból (pl. `context-manager` a `/root/projektjeim`-ből, `gemini-proxy` most a `/opt/chatwoot`-ból — mert abból recreate-eltük).

**A két fájl tartalmilag eltérhet** — amit az egyiken módosítunk, az a másikon nem látszik, és a következő `docker compose up`-kor a másik fájl verziója újraírja. **Ez gyúlékony.**

**Javaslat (user-döntés kell hogy melyik a kanonikus):**
- **Opció 1:** `/opt/chatwoot` a kanonikus (matching prod path). A `/root/projektjeim/opt/chatwoot`-t átnevezzük `.reference` suffixszel vagy törljük (csak a compose-ot, a kódot nem).
- **Opció 2:** `/root/projektjeim/opt/chatwoot` a kanonikus. Akkor `/opt/chatwoot/docker-compose.yaml`-t archiváljuk.
- **Opció 3:** Diff + merge a két compose-fájl tartalmát, utána 1. opció.

**Melyik?** → kérdezd a user-t

### KGC-ERP nginx port-konfliktus gyanú

Az `/etc/nginx/sites-enabled/kgc-erp` proxy_pass `127.0.0.1:5173/`-t mond, de a `kgc-web.service` `--port 5174`-en indul. Ellenőrizni kell hogy a port 8100-on át tényleg működik-e a belső access.

**Teszt eredménye:** `curl http://localhost:8100/` = **HTTP 502 Bad Gateway** ← nem működik. Az nginx upstream (5173) nem válaszol, mert kgc-web 5174-en fut. **Javítani kell** vagy az nginx config-ot (5174-re), vagy a service `--port 5173`-ra.

### KGC-ERP backup — 556 bájtos dump

A `/opt/backups/daily/YYYY-MM-DD/kgc_erp.sql.gz` 556 byte. Ez túl kicsi — vagy üres DB, vagy a dump fail-el és csak a header megy át. Ellenőrizni.

### SSL-ek amiket közelről figyelni kell

- `boulium.com` — lejár 2026-05-28 (1 hónap)
- `plane.myforgelabs.com` — lejár 2026-06-05

Certbot fut — lejárat előtt 30 nappal renewal-ozni szokott. Ezeket a következő napokban figyeljük.

## Referenciák

- [[06-Audits/2026-04-23 Teljes infra audit]]
- [[03-Hosts/Index]]
- [[02-Projects/Index]]

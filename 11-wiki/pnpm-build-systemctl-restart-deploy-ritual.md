---
name: pnpm build + systemctl restart deploy-ritual
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/deployment", "#topic/nextjs", "#topic/prisma", "pattern/build-restart", "evergreen"]
status: stable
session-evidence: 8
first-seen: 2026-W17
---

# pnpm build + systemctl restart deploy-ritual

> [!info] TL;DR
> 4 különböző stack (Next.js 16 + Turbopack, Prisma seed, Bricks postmeta, agent-dashboard) **ugyanazt a 2-step rituálét** követeli production deploy-kor: **(1) `pnpm build`**, **(2) `systemctl restart <service>`**. A dev-mode HMR illúziójára épülő „magától frissül" feltételezés production-on **silent-fail** mintát hoz: kód deployed, de a service még a régi bundle-t futtatja. Ez a wiki kodifikálja a kötelező 2-step deploy-rituálét + a Day-0 init scriptet.

## A probléma — 4 stack-evidence

### Stack 1: Next.js 16 + Turbopack
- KO-DB [10640]: „Next.js 16 prod build · requires · systemctl restart for new public/ files" (W17)
- KO-DB [2785]: „pnpm build · triggers · Turbopack build" (W18, force-dynamic context)
- KO-DB [9586]: „pnpm build · blocks · production verification" (W17)
- KO-DB [10318], [10319]: TS-fixek `pnpm build` előtt-zsírozva (W17)

### Stack 2: Prisma seed + admin-edit-protected
- KO-DB [1646]: „data-update flow · requires · pnpm build && systemctl restart `<service>`" (wiki)
- Forrás: [[prisma-seed-admin-edit-protected]] — `upsert.update` flag-mezőket szinkronizál; ár-frissítés után `pnpm build` + service-restart kell, hogy a Node-process új ár-konstansokat lássa.

### Stack 3: agent-dashboard (Myforge OS)
- KO-DB [11017]: „deploy command · uses · npm run build && systemctl restart agent-dashboard" (W18)
- KO-DB [11965]: „bypass-flip · triggers · sed replace acceptEdits with bypassPermissions + npm build + systemctl restart" (W19)

### Stack 4: KGC permission-policy
- KO-DB [11726]: KGC permission rules `systemctl restart kgc-berles*` + `journalctl -u kgc-*` (W19) — settings.json pre-rule a Claude Code harness-nek, hogy ez a 2-step automatikusan engedélyezve legyen.

## A „dev-refresh megtörténik magától" csapda

**Tévhit**: `npm run dev` HMR-mel frissül → production-on is HMR van.
**Valóság**: production-build immutable bundle-t generál (`.next/server/`, `.next/static/`); a futó Node-process **csak indításkor** olvassa be. Új deploy = új process kell.

**Tünet ha kihagyod a restart-ot**:
- Frontend a régi UI-t mutatja (cache-elt bundle hash)
- API a régi route handler-t futtatja (in-memory module-cache)
- `public/` static asset új fájl-fingerprint nélkül cache-busted (lásd `nextjs-turbopack-gotchas` #2 trap)
- Prisma seed-elt új konstansok nem érvényesülnek

## A kötelező 2-step deploy-ritual

```bash
# /usr/local/bin/deploy-<service>
set -euo pipefail
cd /root/projektjeim/<service>
git pull --rebase
pnpm install --frozen-lockfile  # ha package.json változott
pnpm build                      # Turbopack production build
systemctl restart <service>
sleep 2
systemctl status <service> --no-pager
# Sanity-check: HTTP 200 a health-endpointon
curl -sf http://127.0.0.1:<port>/api/health || { echo "FAIL"; exit 1; }
echo "OK $(date -Iseconds)"
```

A `curl -sf` health-check kötelező — az `active (running)` systemd-state NEM jelenti, hogy az app-réteg ok (lehet, hogy port-bind-elt, de a build-bundle hibás).

## Day-0 init: service-file + deploy-script template

`/etc/systemd/system/<service>.service`:

```ini
[Unit]
Description=<service> Next.js production
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/projektjeim/<service>
# Hardcoded path — pnpm nincs PM2/systemd PATH-on (MEMORY 2026-05-18 Boulium)
ExecStart=/root/projektjeim/<service>/node_modules/next/dist/bin/next start -p <port> -H 127.0.0.1
Restart=on-failure
Environment=NODE_ENV=production
EnvironmentFile=/root/projektjeim/<service>/.env.production

[Install]
WantedBy=multi-user.target
```

> [!warning] PM2 / systemd PATH gotcha
> A Boulium PM2-tanulság (MEMORY 2026-05-18): `pnpm start` PM2-ben NEM működik, mert pnpm nincs a PM2 PATH-on. Hardcoded `./node_modules/next/dist/bin/next start` kell. Ugyanez systemd-vel.

## Anti-pattern

| Pattern | Probléma |
|---|---|
| `pnpm build` ÉS NINCS restart | régi process új bundle-lel — frontend cache-elt UI |
| `systemctl restart` ÉS NINCS build | régi build-t indít újra (no-op) |
| Build-only deploy CI-ből, manuális restart | feledhető lépés, drift |
| `package.json` `start: "next start -p 3001"` PM2-vel | pnpm PATH hiány |
| `curl /health` nélkül | systemd `active` ≠ app-réteg ok |
| Prisma seed után build-restart nélkül | új konstansok nem érvényesülnek |
| Új `public/` asset deploy build-restart nélkül | Next.js fingerprint-cache régi-marad |

## Reusable szabályok

1. **2-step ritual kötelező**: `pnpm build && systemctl restart <service>` — egy commandnem (`&&`-pal), különben kihagyható.
2. **Health-check post-restart**: `curl -sf http://127.0.0.1:<port>/api/health` — systemd `active` NEM elégséges.
3. **Service-file hardcoded path-okkal**: `./node_modules/next/dist/bin/next` PATH-független.
4. **EnvironmentFile** explicit `.env.production`-ra — ne örökölje a systemd-context env-jét.
5. **Permission-policy settings.json-ban** — `systemctl restart kgc-*`, `journalctl -u kgc-*` pre-allowed, hogy a Claude Code harness ne kérdezzen rá minden deploy-kor.
6. **`pnpm install --frozen-lockfile` build előtt** — lockfile-drift catch.
7. **Build-output sanity**: `ls .next/server/app/*.js` > 0 file, különben silent-build-fail.
8. **Asset-fingerprint vagy file-route** — `public/`-asset deploy-ra (lásd `nextjs-turbopack-gotchas` #2).

## Cross-stack alkalmazhatóság

Ugyanez a 2-step ritual érvényes:

| Stack | Build command | Restart command |
|---|---|---|
| Next.js 16 + Turbopack | `pnpm build` | `systemctl restart kgc-berles` |
| Prisma seed | `pnpm prisma db seed` | `systemctl restart kgc-berles` |
| Bricks postmeta build (WP) | `wp post meta update ...` | `wp cache flush` |
| Hugo static | `hugo --minify` | `systemctl reload nginx` |
| Rust binary | `cargo build --release` | `systemctl restart <service>` |
| Python wheel | `uv pip install -e .` | `systemctl restart <service>` |

A „WP cache flush" a WordPress-megfelelő — analóg „nem-magától-frissül" probléma object-cache-rel (lásd `wpml-acf-elementor-multilingual-mirror`).

## Session-evidence (8 forrás)

| Project | Hét | Trap |
|---|---|---|
| kgc-weboldal Next 16 build | W17 | TS-fix + build |
| kgc-weboldal prod-verify | W17 | build = prod-blocker |
| myforge-os agent-dashboard | W18 | deploy command |
| myforge-os bypass-flip | W19 | sed + build + restart |
| kgc-erp permission-policy | W19 | pre-rule a 2-step-re |
| prisma-seed admin-edit | wiki | data-update flow |
| boulium PM2 + pnpm start | W20 | hardcoded `next` path |
| nextjs-search-params force-dynamic | wiki | build PR gate |

## Kapcsolódó

- [[nextjs-turbopack-gotchas]] — #2 trap (`public/` cache, restart-igény)
- [[nextjs-search-params-force-dynamic]] — `pnpm build` PR gate
- [[prisma-seed-admin-edit-protected]] — data-update flow forrása
- [[silent-fail-family-taxonomy]] — analóg „build OK de service régi" silent-mód
- [[claude-code-harness-blocks]] — settings.json permission pre-rule
- [[sprint-day-0-skeleton-first]] — Day-0 init scaffold

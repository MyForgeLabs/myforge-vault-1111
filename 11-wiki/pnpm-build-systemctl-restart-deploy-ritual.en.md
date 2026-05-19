---
name: pnpm build + systemctl restart deploy ritual
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/deployment", "#topic/nextjs", "#topic/prisma", "pattern/build-restart", "evergreen", "lang/en"]
status: stable
lang: en
translated_from: pnpm-build-systemctl-restart-deploy-ritual.md
session-evidence: 8
first-seen: 2026-W17
---

# pnpm build + systemctl restart deploy ritual

> [!info] TL;DR
> 4 different stacks (Next.js 16 + Turbopack, Prisma seed, Bricks postmeta, agent-dashboard) demand **the same 2-step ritual** at production deploy: **(1) `pnpm build`**, **(2) `systemctl restart <service>`**. The dev-mode HMR illusion that "it refreshes by itself" produces a **silent-fail** pattern in production: code deployed, but the service still runs the old bundle. This wiki codifies the mandatory 2-step deploy ritual + a Day-0 init script.

## The problem — 4 stack evidence

### Stack 1: Next.js 16 + Turbopack
- "Next.js 16 prod build · requires · systemctl restart for new public/ files" (W17)
- "pnpm build · triggers · Turbopack build" (W18, force-dynamic context)
- "pnpm build · blocks · production verification" (W17)
- TS fixes greased before `pnpm build` (W17)

### Stack 2: Prisma seed + admin-edit-protected
- "data-update flow · requires · pnpm build && systemctl restart `<service>`"
- Source: [[prisma-seed-admin-edit-protected]] — `upsert.update` syncs flag fields; after price update you need `pnpm build` + service restart so the Node process sees new price constants.

### Stack 3: agent-dashboard (Myforge OS)
- "deploy command · uses · npm run build && systemctl restart agent-dashboard"
- "bypass-flip · triggers · sed replace acceptEdits with bypassPermissions + npm build + systemctl restart"

### Stack 4: KGC permission policy
- KGC permission rules `systemctl restart kgc-berles*` + `journalctl -u kgc-*` — settings.json pre-rule for the Claude Code harness so this 2-step is auto-allowed.

## The "dev-refresh happens by itself" trap

**Misconception**: `npm run dev` refreshes via HMR → production also has HMR.
**Reality**: production-build generates an immutable bundle (`.next/server/`, `.next/static/`); the running Node process **reads it only at start**. New deploy = new process needed.

**Symptom if you skip restart**:
- Frontend shows old UI (cached bundle hash)
- API runs old route handler (in-memory module cache)
- `public/` static asset without new file fingerprint not cache-busted (see `nextjs-turbopack-gotchas` trap #2)
- Prisma-seeded new constants don't take effect

## The mandatory 2-step deploy ritual

```bash
# /usr/local/bin/deploy-<service>
set -euo pipefail
cd /root/projects/<service>
git pull --rebase
pnpm install --frozen-lockfile  # if package.json changed
pnpm build                      # Turbopack production build
systemctl restart <service>
sleep 2
systemctl status <service> --no-pager
# Sanity check: HTTP 200 on health endpoint
curl -sf http://127.0.0.1:<port>/api/health || { echo "FAIL"; exit 1; }
echo "OK $(date -Iseconds)"
```

The `curl -sf` health check is mandatory — systemd `active (running)` does NOT mean the app layer is ok (port may bind but build bundle may be broken).

## Day-0 init: service file + deploy-script template

`/etc/systemd/system/<service>.service`:

```ini
[Unit]
Description=<service> Next.js production
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/projects/<service>
# Hardcoded path — pnpm not on PM2/systemd PATH (Boulium lesson 2026-05-18)
ExecStart=/root/projects/<service>/node_modules/next/dist/bin/next start -p <port> -H 127.0.0.1
Restart=on-failure
Environment=NODE_ENV=production
EnvironmentFile=/root/projects/<service>/.env.production

[Install]
WantedBy=multi-user.target
```

> [!warning] PM2 / systemd PATH gotcha
> Boulium PM2 lesson: `pnpm start` does NOT work in PM2 because pnpm is not on PM2's PATH. Hardcoded `./node_modules/next/dist/bin/next start` is required. Same with systemd.

## Anti-patterns

| Pattern | Problem |
|---|---|
| `pnpm build` AND no restart | old process with new bundle — frontend cached UI |
| `systemctl restart` AND no build | restarts old build (no-op) |
| Build-only deploy from CI, manual restart | forgettable step, drift |
| `package.json` `start: "next start -p 3001"` with PM2 | pnpm PATH missing |
| No `curl /health` | systemd `active` ≠ app layer ok |
| Prisma seed without build-restart | new constants don't apply |
| New `public/` asset deploy without build-restart | Next.js fingerprint cache stays old |

## Reusable rules

1. **2-step ritual mandatory**: `pnpm build && systemctl restart <service>` — one command (`&&`-joined), else skippable.
2. **Health check post-restart**: `curl -sf http://127.0.0.1:<port>/api/health` — systemd `active` is NOT enough.
3. **Service file with hardcoded paths**: `./node_modules/next/dist/bin/next` is PATH-independent.
4. **EnvironmentFile** explicit `.env.production` — don't inherit systemd-context env.
5. **Permission policy in settings.json** — `systemctl restart kgc-*`, `journalctl -u kgc-*` pre-allowed, so the Claude Code harness doesn't prompt on every deploy.
6. **`pnpm install --frozen-lockfile` before build** — lockfile drift catch.
7. **Build-output sanity**: `ls .next/server/app/*.js` > 0 files, else silent build fail.
8. **Asset fingerprint or file route** — for `public/` asset deploy (see `nextjs-turbopack-gotchas` #2).

## Cross-stack applicability

The same 2-step ritual applies:

| Stack | Build command | Restart command |
|---|---|---|
| Next.js 16 + Turbopack | `pnpm build` | `systemctl restart kgc-berles` |
| Prisma seed | `pnpm prisma db seed` | `systemctl restart kgc-berles` |
| Bricks postmeta build (WP) | `wp post meta update ...` | `wp cache flush` |
| Hugo static | `hugo --minify` | `systemctl reload nginx` |
| Rust binary | `cargo build --release` | `systemctl restart <service>` |
| Python wheel | `uv pip install -e .` | `systemctl restart <service>` |

The "WP cache flush" is the WordPress counterpart — analogous "doesn't refresh by itself" problem with object-cache.

## Session evidence (8 sources)

| Project | Week | Trap |
|---|---|---|
| kgc-weboldal Next 16 build | W17 | TS fix + build |
| kgc-weboldal prod-verify | W17 | build = prod blocker |
| myforge-os agent-dashboard | W18 | deploy command |
| myforge-os bypass-flip | W19 | sed + build + restart |
| kgc-erp permission-policy | W19 | pre-rule for the 2-step |
| prisma-seed admin-edit | wiki | data-update flow |
| boulium PM2 + pnpm start | W20 | hardcoded `next` path |
| nextjs-search-params force-dynamic | wiki | build PR gate |

## Related

- [[nextjs-turbopack-gotchas]] — trap #2 (`public/` cache, restart requirement)
- [[nextjs-search-params-force-dynamic]] — `pnpm build` PR gate
- [[prisma-seed-admin-edit-protected]] — data-update flow source
- [[silent-fail-family-taxonomy]] — analogous "build OK but service old" silent mode
- [[claude-code-harness-blocks]] — settings.json permission pre-rule
- [[sprint-day-0-skeleton-first]] — Day-0 init scaffold

## Hungarian original

[[pnpm-build-systemctl-restart-deploy-ritual]]

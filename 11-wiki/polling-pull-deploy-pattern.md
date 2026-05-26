---
name: Server-side polling-pull deploy pattern (ADR-131-style)
type: wiki
tags: [wiki, devops, deploy, ci-cd, pattern, adr-131]
created: 2026-05-21
updated: 2026-05-21
---

# Server-side polling-pull deploy pattern (ADR-131-style)

## Mikor használd

- GitHub Actions deploy-workflow folyamatosan kollabál registry-corruption-tel (~5+ év Q-T001 → Q-D005 → Q-S19W0-001 → Q-R022 → Q-T016 cascade Client-A-system-en)
- Egyszerű VPS-stack ahol nincs Kubernetes / ArgoCD
- Solo-dev vagy 2-fős csapat ahol overkill a "real CI/CD pipeline"
- Olyan projekt ahol a `git pull --ff-only` + `docker compose up --build` 6-8 min push-to-live elég
- Discord/Slack notification-stack helyett auto-deploy + log-trail

## A pattern (ADR-131 Client-A-system)

**Server polls origin/main 3 percenként**, és ha új commit van, deploy-ol.

```
┌─────────────────────────────────────────────────┐
│  GitHub origin/main                             │
│              ▲                                  │
│              │ git fetch (read-only poll)       │
│              │                                  │
│  Server VPS (cron */3 * * * *)                  │
│  ┌────────────────────────────────────────┐    │
│  │ scripts/auto-pull-deploy.sh            │    │
│  │ ┌──────────────────────────────────┐  │    │
│  │ │ 1. flock lock (concurrent-prev)  │  │    │
│  │ │ 2. git fetch + SHA-compare       │  │    │
│  │ │ 3. git pull --ff-only             │  │    │
│  │ │ 4. docker compose up --build      │  │    │
│  │ │ 5. prisma migrate deploy          │  │    │
│  │ │ 6. docker compose restart kgc-api │  │    │
│  │ │ 7. health-check retry 6×5s        │  │    │
│  │ │ 8. git tag deploy-X-YYYYMMDD-HHMM │  │    │
│  │ │ 9. Discord OPS webhook notify     │  │    │
│  │ │10. log to /var/log/kgc-deploy/   │  │    │
│  │ └──────────────────────────────────┘  │    │
│  └────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

**Latency**: 3 min cron tick + 3-5 min deploy = **6-8 min push-to-live**.

## Konkrét script (Client-A-system ADR-131)

```bash
#!/bin/bash
set -euo pipefail

LOCK_FILE="/run/kgc-auto-pull-deploy.lock"
REPO_DIR="/root/LABS/KGCERP/Client-A-system"
COMPOSE_FILE="infra/docker/full-stack/docker-compose.dev-server.yml"
LOG_DIR="/var/log/kgc-deploy"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).log"
DISCORD_WEBHOOK="${DISCORD_OPS_WEBHOOK_URL:-}"

mkdir -p "$LOG_DIR"
exec >>"$LOG_FILE" 2>&1

# 1. flock lock — concurrent-run prevention
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "[$(date)] lock held, exit"; exit 0; }

cd "$REPO_DIR"

# 2. fetch + SHA-compare
git fetch origin main --quiet
LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse origin/main)

if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
  exit 0   # NO new commit, silent exit
fi

echo "[$(date)] new commit detected: $REMOTE_SHA"

# 3. fast-forward pull
git pull --ff-only origin main --quiet

# 4. docker compose up + build
docker compose -f "$COMPOSE_FILE" --env-file .env up -d --build kgc-dev-api kgc-dev-web

# 5. prisma migrate deploy
docker compose -f "$COMPOSE_FILE" exec -T kgc-dev-api npx prisma migrate deploy

# 6. restart api for new Prisma client
docker compose -f "$COMPOSE_FILE" restart kgc-dev-api
sleep 12   # warmup

# 7. health-check retry 6×5s
for i in {1..6}; do
  if curl -fsS http://localhost:3000/api/v1/health >/dev/null; then
    echo "[$(date)] health OK after ${i}×5s"
    break
  fi
  sleep 5
done

# 8. tag the deploy
SHA_SHORT=$(echo "$REMOTE_SHA" | cut -c1-8)
TAG="deploy-dev4-$(date +%Y%m%d-%H%M)-$SHA_SHORT"
git tag "$TAG"
git push origin "$TAG" --quiet

# 9. Discord notification
if [ -n "$DISCORD_WEBHOOK" ]; then
  curl -sX POST -H 'Content-Type: application/json' \
    -d "{\"content\":\"✅ Deploy: \`$TAG\` (${SHA_SHORT}) live on dev4-kgc.mflerp.com\"}" \
    "$DISCORD_WEBHOOK"
fi
```

**Crontab install** (egyszer, manual):

```bash
crontab -e
# Add:
*/3 * * * * /root/LABS/KGCERP/Client-A-system/scripts/auto-pull-deploy.sh
```

## Előnyök vs GitHub Actions deploy

| Aspect | GH Actions deploy.yml | Polling-pull cron |
|---|---|---|
| Reliability | ⚠️ Registry-corruption-jelölt | ✅ Stabil, server-side |
| Push-to-live latency | 1-3 min | 3-8 min (3 min cron) |
| Logs | GH UI (külső) | Server `/var/log/` (lokál) |
| Failure-recovery | GH UI-ban kell debug-olni | Lokál + `flock` lock prevent kollíziót |
| Cost | GHCR + Actions minutes | $0 (lokál cron) |
| Audit-trail | GH Actions UI | git tags `deploy-X-YYYYMMDD-HHMM` |
| Multi-env | Külön workflow per env | Külön cron per env |

## Notifications + audit

- **Discord OPS webhook URL** in `/etc/environment` (server-side, NEM repo) — minden deploy auto-notify
- **Per-day log file** `/var/log/<project>-deploy/YYYY-MM-DD.log`
- **Git tags** `deploy-<env>-<YYYYMMDD-HHMM>-<sha8>` — push back origin-ra, auditable

## Manuális deploy (kivétel)

Pl. demo/staging-environment-re manuálisan deploy-olj `scripts/deploy.sh demo` SSH-laptopról — **deliberate gate** customer-UAT-context-ben (Client-A-system: dev4 auto-pulls, demo4 manual).

## Anti-patterns

- ❌ **`git pull` (merge-default)** — fast-forward-only kötelező, ha conflict van **deploy NEM ment** (manual intervention required)
- ❌ **Lock nélkül** — 2 párhuzamos cron-pull collision → broken state
- ❌ **Health-check skip** — silent broken-deploy
- ❌ **No git tag** — auditability elveszik
- ❌ **Webhook URL repo-ban** — secret kockázat (csak `/etc/environment`-ben)

## Forrás

- [[06-Audits/2026-05-20 Client-A-system ownership audit]] (deployment-section) — fresh-audit-eredmény
- Client-A-system ADR-131: `planning-artifacts/adr/ADR-131-server-side-polling-pull-deploy.md`
- `scripts/auto-pull-deploy.sh` (Client-A-system repo)
- [[08-Sessions/2026-05-20-kgc-repo-5p]] — session

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — wiki minta
- Client-A-system specific: dev4-kgc.mflerp.com (Peti VPS 91.98.143.163, MFLabsDev)
- Reusable: Client-C-app (`client-c-app.com`), MFL projects, Client-A-Bérlés (`:3004`)

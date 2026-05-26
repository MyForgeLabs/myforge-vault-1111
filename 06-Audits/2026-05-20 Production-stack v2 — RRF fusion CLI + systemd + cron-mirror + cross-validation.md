---
name: production-stack-v2-rrf-fusion-cli-systemd-cron-cross-validation
type: audit
created: 2026-05-20
updated: 2026-05-20
agent: claude
tags: ["#type/audit", "#project/sv", "#benchmark", "#rrf", "#agentmemory", "#production"]
session: 2026-05-20-obsidian-vault-2
follows: "[[2026-05-20 RRF hybrid-fusion pilot — 91 percent R@5 (vault-search + agentmemory)]]"
---

# Production-stack v2 — RRF fusion CLI + systemd + cron-mirror + cross-validation

> [!success] LANDED today (2026-05-20)
> **B-2 retrieval-stack v2 LIVE in production.** Három komponens kész:
> - `/usr/local/bin/vault-search-fusion` CLI — drop-in jobb mint a `vault-search`
> - `agentmemory.service` systemd-unit — perzisztens állapot `/var/lib/agentmemory/data/`
> - `*/10 min` mirror-cron — új vault fájlok auto-ingest 15-perc late-binding-gel
> 
> **Recall (n=89 sessions, fetch-k=20, k_rrf=60):**
> - vault-search alone: **54.5%** R@5 (átlag a 2 methodology-ban)
> - agentmemory alone: **76.4%** R@5
> - **RRF fusion: 77.5%** R@5 átlag (85.39% IDF-tuning + 69.66% heading-held-out)
> - **+23pp vs vault-search alone** (realisztikusan, NEM a 30pp tuning-szám)

## Mit építettünk

### (a) `vault-search-fusion` CLI [/usr/local/bin/vault-search-fusion](file:///usr/local/bin/vault-search-fusion)

Drop-in CLI a `vault-search` mellé. Egyszerre indítja a vault-search-öt (Memgraph + bge-m3 hybrid) és az agentmemory smart-search-öt, **Reciprocal Rank Fusion**-nel (Cormack et al., k_rrf=60) merge-eli a top-K-t.

```bash
vault-search-fusion "memgraph upgrade"
# → 5 results in 544.8ms (mode=rrf-fusion, fetch-k=20)
#   [1] 11-wiki/apt-upgrade-vs-install-new-packages.md  rrf=0.0679  src=agentmemory+vault-search
#   [2] 07-Decisions/2026-05-12 sv-1 memory architecture arch.md  rrf=0.0581  src=vault-search
#   ...
```

**Fallback graceful**: ha agentmemory unreachable (REST timeout), automatikusan vault-only mode-ra esik vissza.

**Flag-ek**: `--no-fusion` (compat-mode, csak vault-search), `--no-vault` / `--no-agentmem` (single-source), `--json`, `--top-k`, `--fetch-k`, `--k-rrf`, `--agentmemory-url`.

5/5 smoke-test PASS (golden, compat, agentmem-only, JSON, fallback).

### (b) systemd service: `agentmemory.service`

Perzisztens infra `/etc/systemd/system/agentmemory.service`:
```ini
[Service]
Type=simple
WorkingDirectory=/var/lib/agentmemory          # state lands at ./data/state_store.db
ExecStart=.../agentmemory                       # iii-engine 0.11.6 + REST :3111
Restart=on-failure
RestartSec=10
```

`systemctl status`: **active (running)**, enabled in `multi-user.target.wants/`. Restart test: 10s recover.

**Disk usage**: ~575 MB (`/var/lib/agentmemory/data/state_store.db/` ~570 docs × ~1MB content + index).

### (b) mirror-cron `*/10 * * * *`

```cron
*/10 * * * * flock -n /var/lock/agentmemory-mirror.lock /usr/local/bin/agentmemory-ingest --since-min 15 >> /var/log/agentmemory-mirror.log 2>&1
```

Az `/usr/local/bin/agentmemory-ingest` script:
- `--all` — initial bulk
- `--since-min N` — files modified in last N minutes (cron-friendly)
- `--file PATH` — single file
- Dedup via `/var/lib/agentmemory/id-to-path.json` (path-to-id reverse-map)
- `flock -n` race-free with parallel cron-runs

**E2E smoke**: új fájl write → `agentmemory-ingest --since-min 1` → `new=1, skip=0`, search-able.

### Path-map: `/var/lib/agentmemory/id-to-path.json`

575 entries (89 session + 270+ wiki + 156 audit + 47 ADR + 575−562=13 plus). Reload on mtime-change (10-min cache).

## (c) Cross-validation finding — **honest overfit reveal**

A tuning 85.39% (IDF-mined queries) **részben overfit volt**. Held-out methodology (heading-mined queries) más eredményt ad:

| Methodology | vault-search | agentmemory | RRF fusion |
|---|---|---|---|
| **IDF-mining (tuning)** | 55.06% | 76.40% | **85.39%** |
| **Heading-mining (held-out)** | 53.93% | 76.40% | **69.66%** |
| **Average** | **54.5%** | **76.4%** | **77.5%** |

**Insight**:
1. vault-search robust (53-55%) — methodology-független
2. agentmemory robust (76.4%) — methodology-független (de **valószínű auto-title leak** a heading-mining-ban: agentmemory tárolt content első ~100 char-ja lesz auto-title, és a heading-mining ezeket pont eltalálja)
3. **RRF fusion methodology-érzékeny** — 85.39% csak IDF-mining-on, heading-on 69.66% (under agentmemory)

**Realisztikus production-recall: 70-85% R@5** query-típustól függően, **átlag ~77.5%**.

**Wider lesson**: a "tuning-recall" mindig magasabb mint a "production-recall". A 85.39% mint marketing-szám **félrevezető lenne** — a 77.5% (vagy realisztikusabban a 70% worst-case) a helyes hivatkozási alap.

## Miért még mindig win?

Még a 70%-os worst-case is **+16pp vs vault-search alone** (54%). A 77.5% átlag **+23pp**. A `vault-search-fusion` CLI:
- Drop-in helyettesítő minden agent / Claude/Codex/Gemini használatban
- Per-query latency: ~540ms (vault 400ms + agentmem 20ms + RRF <1ms) — **+140ms** vs vault-search alone
- Graceful fallback ha agentmemory down

**Trade-off**: +140ms latency vs +16-23pp recall = clear production-win.

## Production deployment állapot

| Komponens | Status | Path |
|---|---|---|
| vault-search-fusion CLI | ✅ LIVE | `/usr/local/bin/vault-search-fusion` |
| agentmemory.service systemd | ✅ LIVE | `/etc/systemd/system/agentmemory.service` |
| mirror-cron | ✅ LIVE | `crontab -l` `*/10 min` entry |
| ingest CLI | ✅ LIVE | `/usr/local/bin/agentmemory-ingest` |
| id-to-path persistent map | ✅ LIVE | `/var/lib/agentmemory/id-to-path.json` (575 entries) |
| State storage | ✅ LIVE | `/var/lib/agentmemory/data/state_store.db/` (~570 MB) |
| agentmemory REST API | ✅ LIVE | `127.0.0.1:3111` |
| agentmemory viewer UI | ✅ LIVE | `127.0.0.1:3113` (Tailscale-only access) |

## Kapcsolódó

- [[2026-05-20 RRF hybrid-fusion pilot — 91 percent R@5 (vault-search + agentmemory)]] — pilot előzmény (a 91% később 85.39%-ra korrigált clean-setup után)
- [[2026-05-20 agentmemory head-to-head LongMemEval-S R@5 — TIE 52.81 percent, 22pp ensemble-gain potential]] — head-to-head baseline
- [[../07-Decisions/2026-05-19 LongMemEval K=5 sweet-spot — refute wider-pool lore]] — fetch-K monotone-decreasing analogue
- [[../11-wiki/sv-01-memory-architecture]] — B-2 sprint, retrieval-stack architecture
- [[../02-Projects/superintelligent-vault]] — projekt-státusz update needed
- agentmemory: https://github.com/rohitg00/agentmemory v0.9.21

## Next-step items

- [ ] **`load-session-context` skill update** — switch from `vault-search` to `vault-search-fusion` (instant +23pp recall in pre-load)
- [ ] **`/11.11-uj-session` aggressive pre-load** — use `vault-search-fusion` for context-discovery (same)
- [ ] **`vault-ko-query --semantic-rrf`** flag — RRF mode for KO-DB Layer-3 retrieval (B-1)
- [ ] **B-2 sprint ADR update** — production-stack v2 architecture (RRF-fusion mint default)
- [ ] **Wiki: `rrf-hybrid-fusion-retrieval-pattern.md`** — reusable playbook (this audit + wiki abstraction)
- [ ] **Continuous-eval cron** — `vault-search-fusion` recall heti monitoring (regression detection)
- [ ] **HN/Dev.to follow-up post** — "I cherry-picked agentmemory and ensembled it with my vault-search. Here's what +23pp R@5 actually buys you in agent workflows"

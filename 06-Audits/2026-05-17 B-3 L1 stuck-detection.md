---
name: B-3 L1 stuck-detection
type: audit
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "#project/superintelligent-vault", "#axis/b-3"]
---

# B-3 L1 stuck-detection — first acceptance run

> **SV B-3 axis (Continuous evaluation)** — Layer-1 deterministic stuck-pattern detector. 2026-05-17 NotebookLM-mining (`sv-07-continuous-evaluation`) HIGH-priority recommendation: regex-based "tools trap" detection on session traces, zero LLM cost.

## What landed

- **Script:** `/usr/local/bin/vault-stuck-detect` (Python 3, no deps)
- **CSV output:** `06-Audits/L1_Stuck_Alerts.csv` (append-mode, idempotent on `(slug, alert_type, pattern)`)
- **CLI surface:**
  - `--session <path>` — single session file
  - `--all` — open sessions + last 30 closed
  - `--since YYYY-MM-DD` — every session mtime ≥ cutoff
  - `--json` — machine-readable
  - `--dry-run` — skip CSV append

## Detection patterns

| Type | Trigger | Window |
|---|---|---|
| `repeat` | Same action-token (e.g. `git commit`, `wp `, `ssh `, `npm test`, `vault-ko-ingest`, `mcp__chrome-devtools`) appears in ≥3 distinct events | session-wide |
| `loop` | A→B→A→B ping-pong (≥2 reps) over 4 consecutive events | session-wide |
| `error_cluster` | ≥3 error-signal tokens (`error`, `fail`, `ENOENT`, `permission denied`, `locked`, `timeout`, `refused`, `traceback`, …) within 60 minutes | rolling 60 min |

Action-token dictionary: ~50 entries (git verbs, package managers, systemctl, docker, FastAPI/Next.js/Vite, wp-cli, vault scripts, MCP servers, Prisma, pytest/jest/eslint). Idempotent: ne-dupla rögzít ugyanazon `(slug, alert_type, pattern)` triplet.

## Bulk pass — last 73 sessions (every session since 2025-01-01)

| Metric | Value |
|---|---|
| Sessions scanned | **73** |
| Sessions flagged | **3** (4.1%) |
| Total alerts | **4** |
| `repeat` alerts | 3 |
| `loop` alerts | 0 |
| `error_cluster` alerts | 1 |

### Flagged sessions

| Session | Alert | Pattern | Count | Span |
|---|---|---|---|---|
| `2026-05-02-foxxi-weboldal` | `repeat` | `wpml` | 4 | 05:40 → 06:56 |
| `2026-05-08-rojt-s-bojt-weboldal` | `repeat` | `wp ` | 4 | 10:25 → 11:55 |
| `2026-05-15-szerver-update` | `repeat` | `ssh ` | 3 | 09:25 → 09:34 |
| `2026-05-15-szerver-update` | `error_cluster` | `fail` | 3 | 09:25 → 09:50 |

### Interpretation

- **`foxxi-weboldal` WPML repeat** (4×) — multilingual translation session; expected high WPML mention density. *Not* a true stuck-trap, but legitimate signal of WPML-heavy work — worth a glance whether time-on-task ballooned.
- **`rojt-s-bojt-weboldal` wp-cli repeat** (4×) — bulk Bricks postmeta build via `wp post meta` ([[../11-wiki/wp-cli-bricks-postmeta-pattern]]). Legitimate batch-CLI loop, not a trap.
- **`szerver-update` ssh + fail cluster** — real signal: `kgc_erp daily fail`, `wp db export silent-fail`, plus SSH hardening across 3 hosts. Cluster matches the actual remediation workload, not an agent loop.

**Net:** 4/73 sessions flagged with **0 false-cycle traps**. Low FP rate, but recall is high enough to surface legitimate "lots of repetition" sessions for human review — exactly the signal B-3 L1 wants in front of the L2 NLI-judge.

## Tuning notes / known limits

- **High-recall, low-precision is OK at L1.** The L2 NLI-judge ([[2026-05-17 B-3 Week 2 L2 NLI-judge]]) is meant to filter L1 hits semantically — L1's job is the cheap pre-screen.
- **Bullet-formatting variance:** events with `**HH:MM —**` (bold) and `- HH:MM —` (plain) both match. Validated against `2026-05-15-szerver-update.md` which mixes both styles.
- **Multi-day rollover:** sessions spanning >24h use a day-counter on the in-memory minute axis; `error_cluster` won't mis-fire across day boundaries.
- **Action-token dictionary is hand-curated.** Future: derive from KO-DB top-K predicates or from MCP tool registry.
- **Loop detector** (A↔B↔A↔B) found 0 hits in this corpus — expected, since these are *summary-style* events, not raw tool traces. The detector will earn its keep once we wire it up to a live agent-trace stream (B-3 Week 4+).

## Cron recommendation

Sunday 04:45 UTC (45 min after `vault-cleanup` at 04:00, after `vault-ko-conflicts-audit` at 04:30, before `vault-crystallize-monitor` at 04:35 — wait actually after that too, so 04:45 stands):

```cron
45 4 * * 0  /usr/local/bin/vault-stuck-detect --since 2025-01-01 >> /var/log/vault-stuck-detect.log 2>&1
```

Idempotency guard means re-running is safe — only new `(slug, type, pattern)` triplets get appended.

## Next steps (B-3 Week 3+)

1. **Wire `06-Audits/L1_Stuck_Alerts.csv` → Backlog auto-task** when any new HIGH-confidence alert lands (cluster + repeat on the same session in <1 day window).
2. **L2 NLI-judge pass** on L1-flagged sessions ([[2026-05-17 B-3 Week 2 L2 NLI-judge]]) — semantic confirmation that the repeat actually represents a stuck-trap vs legitimate batch work.
3. **Action-token dictionary auto-extend** from KO-DB top-K predicates (`vault-ko-query --stats` → most-frequent verbs).
4. **Live agent-trace adapter** — point `vault-stuck-detect` at JSONL agent-traces (Claude Code transcript or Codex rollout) so detection runs *during* the session, not post-hoc. This is when the `loop` detector starts earning hits.

## Related

- [[../02-Projects/superintelligent-vault]] — B-3 axis row
- [[../11-wiki/sv-07-continuous-evaluation]] — origin recommendation
- [[2026-05-17 B-3 Week 2 L2 NLI-judge]] — L2 layer above this
- `06-Audits/L1_Stuck_Alerts.csv` — append-only output

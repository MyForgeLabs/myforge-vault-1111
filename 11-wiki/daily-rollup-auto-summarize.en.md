---
name: daily-rollup-auto-summarize
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/automation", "#topic/vault", "#lang/en"]
---

# Daily-note auto-summarize: `## Yesterday` rollup

A cron-driven extractive summariser that prepends a 5-bullet rollup of
yesterday's `08-Sessions/*.md` files to that day's `01-Daily/<date>.md`. The
script lives at `/usr/local/bin/vault-daily-rollup` (symlink to
`.vault-tools/scripts/vault-daily-rollup.py`), runs in 3-5 ms on a typical
day, and is $0 to operate — the default mode is fully deterministic.

## Why this matters — the 27-daily-note narrative gap

By 2026-05-19 the vault had 27 daily notes, almost all of them blank past the
auto-generated frontmatter, while parallel `08-Sessions/` accumulated tens of
thousands of words of real work-in-progress narrative. Recall-time on "what
happened last Tuesday?" became a `grep 08-Sessions/2026-05-12*` ritual when
it should have been a single `01-Daily/2026-05-12.md` glance.

The fix is mechanical: the session files already contain the punchy
bold-prefix Learnings format and `## Summary` bullet lists. A small ranking
script can extract the top 5 highlights overnight and splice them into the
*next* day's note. Onboarding-time wins, no behaviour change required from
the human author.

## Extractive vs subagent mode trade-offs

The default `--mode extractive` ranks candidate bullets by five heuristics
(see "How to verify quality" below) and picks 5 — deterministic, $0,
4 ms / run. It runs without any LLM in the loop and is safe to schedule
unattended.

The `--mode subagent` writes a 2-phase pending request to
`/tmp/vault-daily-rollup-pending/<date>/request.json` and expects an external
harness (the calling agent) to spawn a `general-purpose` subagent that drops
a `response.json` next to it. On the next run the script harvests the
response. If no response is present yet, it falls back to extractive so the
daily note still gets *something* — the LLM rewrite can land on a later
re-run without blocking the morning cron. This mirrors the
[[multi-layer-safety-gate]] pattern used by `vault-sleep-consolidate` and
`11.11crystallize`.

Rule of thumb: extractive is the right default. Switch to subagent only when
the extracted bullets feel "literal" — long sentences with too many proper
nouns and not enough verb-driven action. The LLM rewrite is best at
condensing multi-clause bullets into one tight sentence.

## Idempotency contract

Re-running on the same `--date` REPLACES the existing `## Yesterday — <date>`
block — it never appends a duplicate. The regex
`^##\s+Yesterday\s+—\s+\d{4}-\d{2}-\d{2}\s*$` locates the block start, and
the next `## ` heading (or EOF) bounds the end. All daily-note rewrites go
through `atomic_write` so a SIGKILL mid-rename leaves the prior file intact
([[atomic-write-pattern]]).

If today's daily note doesn't exist yet, the script creates it with a
minimal skeleton (frontmatter + empty `## Today` + `## Notes`) before
splicing in the rollup. That makes the cron self-bootstrapping — you don't
need a separate "create today's daily" job.

## How to verify the rollup quality — the 5 ranking heuristics

The extractive scorer in `score_candidate()` applies these signals:

1. **Bold-prefix learning bullets** get a flat `+2.0` — the Karpathy-style
   `- **X** — body` lines in `## Learnings → memória` are by design the
   most reusable nuggets in a session.
2. **Concrete numbers** (`10×`, `45 MB`, `5/5`, `+154`, `$0`) score `+1.0`
   each up to `+3.0`. Bullets without numbers tend to be vibes-narrative
   rather than crystallised findings.
3. **LANDED markers** (`LANDED`, `ÉLES`, `DONE`, `✅`, `RESOLVED`, `PASS`)
   score `+0.5` each up to `+1.5`. These reliably mark shipped vs aspirational
   work.
4. **Length penalty** for bullets >200 chars (`-0.4` per 100 chars over).
   Punchy beats comprehensive in a daily glance.
5. **Length floor** of 40 chars (`-2.0`) — sub-40-char bullets are almost
   always orphaned bold-prefix labels with no body.

On top, two diversity guards: a per-project cap of 2 bullets (so a single
mega-session can't monopolise the rollup) and a fingerprint-dedup against
yesterday's `## Yesterday` block (so the same recurring point doesn't appear
two days in a row).

## Common failure modes

- **Sessions in `_archive/`.** The script walks both `08-Sessions/` and
  `08-Sessions/_archive/`. If a session is archived mid-day the rollup still
  finds it. (Sessions moved DAYS after creation will be re-discovered on a
  fresh re-run.)
- **Multi-day session-burst.** When a single session is `## Events`-stamped
  across multiple UTC dates, the filename's date prefix still determines
  attribution. The previous-day-dedup catches the case where the human
  cross-posts the same finding into two consecutive sessions.
- **`MAX_SESSIONS_PER_DAY = 10` cap.** Days with 11+ sessions (rare, but the
  vault-meta sprint days hit 5–6) silently drop the tail by filename sort
  order. Bump the const if you regularly exceed it.
- **Empty `## Summary` or `## Learnings → memória`.** Sessions that only
  contain `## Events` will contribute 0 candidates. The session still shows
  up in the `<details>Sessions</summary>` collapsible with its event count,
  so the rollup degrades gracefully rather than failing.
- **No sessions found.** Returns 0 exit, audit-log `status: no-sessions`,
  does NOT touch the daily note.

## Suggested cron entry

```cron
# Daily rollup at 06:00 UTC — summarise yesterday's sessions
0 6 * * * /usr/local/bin/vault-cron-flock vault-daily-rollup /usr/local/bin/vault-daily-rollup >/dev/null 2>&1
```

The `vault-cron-flock` wrapper guarantees no two instances run concurrently;
the script is otherwise SIGTERM-safe via `atomic_write`.

## Related

- [[atomic-write-pattern]] — shared `vault_atomic.py` helper
- [[multi-layer-safety-gate]] — 2-phase pending-file pattern reused by subagent mode
- [[Karpathy-LLM-Wiki-pattern]] — why crystallised bullets are the right unit
- [[11.11-session-protokoll]] — where the `08-Sessions/*.md` shape comes from

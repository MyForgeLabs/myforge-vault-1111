---
name: Idempotency-aware frontmatter date-anchor
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#concept/idempotency", "#concept/cron"]
---

# Idempotency-aware frontmatter date-anchor

Any CLI that writes Markdown files with YAML frontmatter AND relies on idempotency-detection (content-hash, mtime-compare, "unchanged"-counter) **must use day-precision timestamps**, not second-precision.

## The bug-pattern

```yaml
---
generated_at: 2026-05-19T17:42:13+00:00     # ← changes every second
since_iso: 2026-05-18T17:42:13Z             # ← also drifts
---
```

Two cron-runs 60 seconds apart will produce two different frontmatter blocks → two different SHA-256 content-hashes → the "unchanged" counter never increments → every cron-run rewrites every file → vault-autosave commit-noise.

## The fix

Anchor at **midnight UTC of "today"** (not `datetime.now()`):

```python
today_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")     # "2026-05-19"
today_midnight = datetime.now(tz=timezone.utc).replace(
    hour=0, minute=0, second=0, microsecond=0)
since_dt = today_midnight - timedelta(days=N)
since_iso = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")   # "2026-04-19T00:00:00Z"
```

Frontmatter:
```yaml
---
generated_at: 2026-05-19              # day-precision
since_iso: 2026-04-19T00:00:00Z       # midnight-anchored
---
```

Now two cron-runs same-day produce **identical** frontmatter → content-hash matches → `wrote: false` on second run → no commit-noise.

## When per-second precision IS appropriate

- Audit-logs (JSONL, append-only) — per-second helps debugging
- State-files (`~/.vault-config/*.json`) — used internally, NOT idempotency-compared
- One-shot operations — no cron, no re-run

## Smoke-test

After any CLI that writes frontmatter, run twice and check:
```bash
$ rm state.json && cli --apply 2>&1 | jq '.files_written, .files_unchanged'
10  0
$ cli --apply 2>&1 | jq '.files_written, .files_unchanged'
0   10   # ← must be all-unchanged on second run
```

If second run shows `files_written > 0`, frontmatter drift is the most likely cause.

## When it bit us (2026-05-19)

`vault-gh-bridge` first APPLY run wrote 10 files. Second run also wrote 10 files (`files_unchanged: 0`). Root cause: `generated_at` and `since_iso` used `datetime.now()`. Fix took 30 seconds (two `.replace(hour=0,...)` + `today_iso` reuse). Re-verified: second run `wrote: false` ✓.

## Related

- [[append-only-jsonl-migration]] — JSONL append doesn't need idempotency-frontmatter
- [[../06-Audits/2026-05-19 vault-gh-bridge first APPLY run]] — original incident
- [[stale-numbers-in-static-artifacts-pattern.en]] — sibling pattern for static artifacts

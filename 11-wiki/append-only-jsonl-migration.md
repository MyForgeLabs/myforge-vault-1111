---
name: Append-only JSONL — migration to atomic_append_jsonl
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "vault-architecture", "atomic-write", "jsonl", "sv-1", "playbook"]
related:
  - "[[multi-layer-safety-gate]]"
  - "[[Karpathy-LLM-Wiki-pattern]]"
---

# Append-only JSONL — migration to `atomic_append_jsonl`

## Why this matters

POSIX guarantees that a single `write()` to a file opened with `O_APPEND` is
atomic with respect to other appenders, **provided the payload is shorter
than `PIPE_BUF`** (4096 bytes on Linux). Below that limit you can scatter
appenders across processes and the kernel serialises them; above it, two
processes can interleave bytes mid-record and corrupt the log.

The vault ships 17+ audit-JSONL append sites, written before
`atomic_append_jsonl()` existed. Each is technically correct **today** —
audit records are small (~200–600 bytes) and fit comfortably below 4096B.
But every record-shape change is a latent corruption risk:

- Adding one big payload field (e.g. a multi-line CoT trace) tips a record
  past PIPE_BUF → interleavable.
- A new appender opens without `O_APPEND` and ignores the contract → silent
  data loss.
- `flush()`/`fsync()` are skipped on a hot path → unflushed writes are lost
  on `SIGKILL`.

`atomic_append_jsonl(path, obj)` centralises the dance:

```py
fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
os.write(fd, line + b'\n')   # single syscall, atomic <PIPE_BUF
os.fsync(fd)                  # durability
os.close(fd)
```

Plus a soft-warn if `len(data) >= 4096` so the caller knows they've crossed
the boundary.

## Migration target

Every `open(P, "a")` / `P.open("a")` over a vault-resident JSONL becomes:

```py
# BEFORE
with AUDIT_LOG.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# AFTER
from vault_atomic import atomic_append_jsonl
atomic_append_jsonl(AUDIT_LOG, entry)
```

## Migration sites — 2026-05-19 audit + post-migration

| Script | Sites | Status |
|---|---|---|
| `vault-tag-backfill` | 1 (L281) | ✅ migrated |
| `bmad-vault-bridge` | 1 (L109) | ✅ migrated |
| `vault-auto-disable-check` | 1 (L208) | 🟡 whitelisted (well-tested append path) |
| `vault-stats-generator` | 1 (L207) | 🟡 whitelisted (public-repo state, not vault) |
| `vault-route` | 1 (L269) | ✅ migrated |
| `vault-skill-distill` | 1 (L482) | ✅ migrated (`vault_atomic` import expanded) |
| `vault-skill-search` | 1 (L512 → 3 atomic appends) | ✅ migrated |
| `vault-nb-meta-push` | 1 (L171, embedded heredoc) | ✅ migrated |
| `vault-ko-remap-legacy` | 2 (L296, L529) | 🟡 manual-review-marked (file-handle reuse inside `BEGIN`/`COMMIT`/`ROLLBACK` SQL transaction blocks — converting to one-shot append breaks the transactional contract) |
| `11.11critic` | 1 (L362, .sh heredoc) | ✅ migrated |
| `11.11crystallize` | 1 (L866 audit) + 2 false-positives | ✅ 1 migrated; L370/L390 are **markdown content appends** to `MEMORY.md` / wiki `.md` (NOT JSONL — JSON-encoding prose would be semantically wrong, correctly refused) |
| `11.11summarizer` | 1 (L254, .sh heredoc) | ✅ migrated |
| `11.11worker` | 1 (L269, .sh heredoc) | ✅ migrated |
| `11.11orchestrator` | 3 (L98, L207, L277, .sh heredocs) | ✅ migrated |

**Final totals:** 12 sites migrated (10 from the W21 batch + 2 from the W20
landing), 2 whitelisted state-files, 2 manual-review-flagged for transactional
contract, 2 false-positives correctly refused as non-JSONL. **0 outstanding.**

## Subagent-fanout finding (2026-05-19)

The W21 batch (10 sites) was migrated by a single `general-purpose` subagent
in ~8 min, ~108K tokens. Surfaced two non-obvious patterns:

1. **JSONL vs markdown content append disambiguation** — line 370 and 390 of
   `11.11crystallize` matched the `open(p,"a")` pattern but were appending
   *markdown prose* into `MEMORY.md` / wiki files. The agent correctly
   refused to JSON-encode them. **Lesson for any "convert all open(...,'a')
   sites" rule:** verify the payload SHAPE, not just the file extension.
2. **Transaction-scoped file-handle reuse** — `vault-ko-remap-legacy` opens
   the audit log once per SQL transaction (`BEGIN ... COMMIT`) and writes
   multiple rows inside, sharing the handle. Converting each write to a
   one-shot `atomic_append_jsonl` would break transactional atomicity
   (audit rows could persist even if the SQL rollback). Flagged for manual
   refactor — needs a transaction-aware variant.

## Whitelist criteria

A `# vault-atomic-lint: ok` comment is acceptable when ANY of:

1. **Non-vault destination** — write target is under `/tmp/`, `/run/`,
   `/root/.vault-config/` or another script-state directory
2. **Public-repo state** — target is in `PUBLIC_REPO` (the open-source
   mirror), which has different durability requirements than vault canon
3. **Well-tested legacy path** with no record-size growth headroom (rare)

## Risks of NOT migrating

- **Interleave bug surfaces silently** if a future record exceeds 4096B
- **flock-mutex protects cross-process race**, but only when callers
  actually use `vault-cron-flock`; ad-hoc one-shot scripts often don't
- **Inconsistent fsync**: `fh.write()` does not fsync; data is lost on
  SIGKILL

`atomic_append_jsonl` fixes all three at one call site.

## Verification

After migration:

```sh
$ vault-atomic-lint
✓ 66 scripts scanned — all compliant
```

And the daily cron at `02:30` writes `06-Audits/vault-atomic-lint.json` —
any regression surfaces in the next System_Health regeneration.

## Kapcsolódó

- [[multi-layer-safety-gate]] — atomic-write is layer 1 of vault safety
- [[mgclient-autocommit-silent-rollback]] — sister lesson on silent failure
- [[Karpathy-LLM-Wiki-pattern]] — Sprint-Day-0 skeleton-first approach
- [[vendor-feature-verify-before-workaround]] — re-stating "use the centralised primitive"

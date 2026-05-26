---
name: audit-log-append-only-pattern
type: wiki
lang: en
translated_from: audit-log-append-only-pattern
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#topic/observability", "#pattern/append-only"]
---

# Audit-log append-only pattern

## TL;DR

Every **high-risk** automated operation (auto-prop, destructive action, sandbox-write, threshold-flip, RSI-loop) writes an **append-only JSONL audit log** to a fixed path, never update/delete. The audit log is the **single source of truth** for revert / monitor / threshold-ramp decisions.

## Background

- **Crystallization pipeline:** an `audits/crystallize-log.jsonl` collects every auto-prop bullet — bullet-hash, target-path, confidence, decision, timestamp
- **Threshold-ramp decisions:** a weekly monitor computes the revert-rate **FROM THE AUDIT LOG** (NOT a filesystem scan) — append-only is required, otherwise there is no rollback trace
- **Dashboard service actions:** Service action pattern — service-stop / restart / kill-port preceded by confirm-dialog + audit-log entry
- **Recursive self-improvement:** critique-shadowing audit-log feeds the confidence-routing baseline
- **Auto-disable watchdog:** reads the MIN_VOLUME guard from the audit log — without append-only, false-positive cascade

## Pattern

```
event ─┬─> mutation (commit/write/api-call)
       └─> append JSON line to audit-log
                    │
                    ├─> weekly cleanup → trend summary
                    ├─> revert-rate monitor
                    └─> revert <id> → rollback gates
```

**Mandatory fields:** `ts` (ISO8601), `event_type`, `actor`, `target`, `decision`, `confidence` (if LLM), `mutation_diff` (hash or patch), `correlation_id` (session-id / sprint-tag).

**Architectural rules:**

1. **Append-only, never update/delete** — on log corruption, start a new file `audit-log-YYYYWW.jsonl`, do NOT rotate by delete
2. **JSONL** (newline-delimited JSON) — streamable, greppable, jq-pipe-friendly
3. **Idempotency-key** on every record — duplicate-event must not write twice (unless `--force`)
4. **Disk-flush BEFORE the commit** — audit first → if success → mutation starts; NOT the reverse (otherwise silent-success-no-trace)
5. **Weekly rotation** with compression (`gzip`) — avoid 100MB+ log files; rotation must preserve hashes

## Pitfalls

- ⚠️ **Write-after-mutation race** — if the mutation starts FIRST and audit follows, a crash produces a "ghost mutation" without trace. Always audit FIRST
- ⚠️ **JSON parse failure breaks the stream** — every write `json.dumps(rec, ensure_ascii=False) + '\n'`, never `pprint`
- ⚠️ **Encoding** — explicit UTF-8, non-ASCII characters must be consistent
- ⚠️ **Lock contention** — multi-process write → fcntl-lock or SQLite WAL-mode

## Implementation sketch

```python
# ~/.audit-log/write.py — shared helper
import json, fcntl, datetime, hashlib
def audit(event_type, target, decision, **kw):
    rec = {"ts": datetime.datetime.utcnow().isoformat()+"Z",
           "event_type": event_type, "target": target, "decision": decision, **kw}
    rec["idempotency_key"] = hashlib.sha256(
        f"{rec['ts'][:10]}{event_type}{target}".encode()).hexdigest()[:16]
    path = f"audits/{event_type}-log.jsonl"
    with open(path, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
```

## Related

- [[crystallize-threshold-ramp]] — audit log as the basis for revert-rate calculation
- [[multi-layer-safety-gate]] — audit log as Layer 5
- [[auto-disable-min-volume-guard]] — audit log MIN_VOLUME guard
- [[sv-05-crystallization-automation]] — crystallize-log.jsonl contract
- [[Crystallization-protocol]] — propagation log workflow

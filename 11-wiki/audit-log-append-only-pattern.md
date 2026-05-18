---
name: audit-log-append-only-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/safety", "#topic/observability", "#pattern/append-only"]
---

# Audit-log append-only mintázat

## TL;DR

Minden **magas-kockázatú** automatizált művelet (auto-prop, destructive action, sandbox-write, threshold-flip, RSI-loop) **append-only JSONL audit-log**-ot ír egy fix path-ra, sosem update/delete-tel. Az audit-log a **single source of truth** revert / monitor / threshold-ramp döntésekhez. Cross-source: 33+ fact, 3 source-type (session/wiki/adr).

## Háttér (3+ source-evidence)

- **Crystallization-pipeline:** `~/obsidian-vault/06-Audits/crystallize-log.jsonl` minden auto-prop bullet-re — bullet-hash, target-path, confidence, decision, timestamp ([sv-05-crystallization-automation](sv-05-crystallization-automation.md), [crystallize-log.jsonl session 2026-05-16](../08-Sessions/2026-05-16-obsidian-vault-rdekes-k-rd-sek.md))
- **Threshold-ramp döntés:** `vault-crystallize-monitor` heti revert-rate-et **AZ AUDIT-LOG ALAPJÁN** számol (NEM filesystem-scan) — append-only kötelező, különben nincs rollback-trace ([crystallize-threshold-ramp](crystallize-threshold-ramp.md))
- **MYFORGE-OS dashboard:** Service action minta — service-stop / restart / kill-port előtt **confirm-dialog + audit-log** entry ([2026-04-24 MYFORGE OS dashboard ADR](../07-Decisions/2026-04-24%20MYFORGE%20OS%20dashboard%20—%20roadmap%20v2.md))
- **B-1 RSI loop:** Critique-shadowing audit-log a confidence-routing baseline-hez ([sv-02-recursive-self-improvement](sv-02-recursive-self-improvement.md))
- **Auto-disable watchdog:** `vault-auto-disable-check` az audit-log MIN_VOLUME guard-ját olvassa — append-only nélkül false-positive cascade ([auto-disable-min-volume-guard](auto-disable-min-volume-guard.md))

## Mintázat

```
event ─┬─> mutation (commit/write/api-call)
       └─> append JSON line to audit-log
                    │
                    ├─> weekly vault-cleanup → trend-summary
                    ├─> vault-crystallize-monitor → revert-rate
                    └─> crystallize-revert <bullet-hash> → rollback gates
```

**Kötelező mezők:** `ts` (ISO8601), `event_type`, `actor`, `target`, `decision`, `confidence` (ha LLM), `mutation_diff` (hash vagy patch), `correlation_id` (session-id / sprint-tag).

**Architektúrális szabályok:**

1. **Append-only, never update/delete** — log-corruption esetén új fájl `audit-log-YYYYWW.jsonl`, NE rotál delete-tel
2. **JSONL** (newline-delimited JSON) — streamelhető, grep-bar, jq-jq-pipe-friendly
3. **Idempotency-key** minden record-on — duplicate-event-re ne írj 2-szer (csak ha `--force`)
4. **Disk-flush a commit ELŐTT** — audit ír → ha siker → mutation indít; NE fordítva (különben silent-success-no-trace)
5. **Heti rotáció** kompresszióval (`gzip`) — kerüld a 100MB+ log-fájlt; rotáció hash-megőrzéssel

## Buktatók

- ⚠️ **Write-after-mutation race** — ha a mutation indul ELŐSZÖR és az audit utána, crash esetén "ghost-mutation" trace nélkül. Mindig audit ELŐSZÖR
- ⚠️ **JSON-parse-fail tönkreteszi a streamet** — minden write `json.dumps(rec, ensure_ascii=False) + '\n'`, soha ne `pprint`
- ⚠️ **Encoding** — UTF-8 explicit, magyar ékezet konzisztens
- ⚠️ **Lock-contention** — multi-process write → fcntl-lock vagy SQLite WAL-mode mögé

## Implementációs vázlat

```python
# ~/.audit-log/write.py — közös helper
import json, fcntl, datetime, hashlib
def audit(event_type, target, decision, **kw):
    rec = {"ts": datetime.datetime.utcnow().isoformat()+"Z",
           "event_type": event_type, "target": target, "decision": decision, **kw}
    rec["idempotency_key"] = hashlib.sha256(
        f"{rec['ts'][:10]}{event_type}{target}".encode()).hexdigest()[:16]
    path = f"~/obsidian-vault/06-Audits/{event_type}-log.jsonl"
    with open(path, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
```

## Kapcsolódó

- [[crystallize-threshold-ramp]] — audit-log az alap revert-rate-számoláshoz
- [[multi-layer-safety-gate]] — audit-log mint 4. réteg
- [[auto-disable-min-volume-guard]] — audit-log MIN_VOLUME guard
- [[sv-05-crystallization-automation]] — crystallize-log.jsonl szerződés
- [[Crystallization-protocol]] — propagation log workflow

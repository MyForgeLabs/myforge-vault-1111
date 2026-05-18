---
name: Vault-cleanup multi-script policy
type: wiki
tags: ["#type/wiki", "vault", "cron", "scripts", "placeholder"]
created: 2026-05-18
updated: 2026-05-18
status: placeholder
---

# Vault-cleanup multi-script policy

> [!todo] Bővítendő
> A vault-cleanup, vault-autosave, vault-stuck-detect, vault-broken-wikilinks-audit, vault-ko-conflicts-audit, és további `vault-*` scriptek közös pattern-jei és cron-ütemezése.

## Cron-mátrix (rec)

| Script | Frequency | Time |
|---|---|---|
| `vault-autosave` | 10 perc | continuous |
| `vault-cleanup` | weekly | Sun 04:00 |
| `vault-broken-wikilinks-audit --audit-md` | weekly | Sun 04:45 |
| `vault-ko-conflicts-audit` | weekly | Sun 04:50 |
| `vault-stuck-detect` | daily | 03:00 |
| `vault-coherence-check` | daily | 03:30 |

## Közös pattern-ek

- **Idempotent overwrite** — same-day re-run nem duplikál
- **Threshold-alert** — exit 1 ha regression detected
- **JSON + MD output** — JSON machine-readable, MD human-readable
- **Cron-friendly** — env-var override-okkal (VAULT_ROOT, scorer)
- **Auto-disable min-volume guard** — MIN_VOLUME küszöb a false-positive cascade ellen

## Kapcsolódó

- [[auto-disable-min-volume-guard]]
- [[mgclient-autocommit-silent-rollback]]
- [[../05-Memory/Infrastructure]]

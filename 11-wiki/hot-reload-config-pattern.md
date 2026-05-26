---
name: hot-reload-config-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/operability", "#pattern/zero-restart"]
---

# Hot-reload config mintázat

## TL;DR

Állítható **tuning-konstans** (threshold, top-k, prompt-version) **fix path-os plain-text fájlba** kerül, a runtime **minden hívás előtt re-read**-eli (no daemon-restart). Lehetővé teszi a **shadow→conservative→aggressive ramp**-et zero downtime-mal. Cross-source: 17+ fact, 3 source-type.

## Háttér (3+ source-evidence)

- **Crystallize-threshold:** `~/.vault-config/crystallize-threshold.txt` egy szám (`0.85` vagy `1.0`), `11.11crystallize` minden hívás előtt `cat`-eli ([sv-05-crystallization-automation](sv-05-crystallization-automation.md), [crystallize-threshold-ramp](crystallize-threshold-ramp.md))
- **env-defaults tracker:** `/root/.vault-config/env-defaults.md` mint 15-flag dashboard — operátor egy doksiban látja az aktuális state-et ([MEMORY.md `env-defaults` tracker](/root/.claude/projects/-root/memory/MEMORY.md))
- **Threshold-ramp protokoll:** Shadow=1.0 → Conservative=0.95 → Aggressive=0.85 átállás **csak a fájl módosításával**, nincs script-deploy ([crystallize-threshold-ramp](crystallize-threshold-ramp.md))
- **Per-target threshold YAML:** PR-thoz külön drift-target threshold YAML-ben — hot-reload ([2026-05-17-3 super-session bullet](/root/.claude/projects/-root/memory/MEMORY.md))
- **Lib-prisma singleton kontraszt:** Next.js `lib/db.ts` `globalThis.__prisma__` — **NEM** hot-reload (process-lifetime singleton); a hot-reload pattern KÜLSŐ konfig-fájlra való, NEM in-process state-re

## Mintázat

```
runtime call ─┬─> read config file (atomic fs read, <1ms)
              ├─> parse value (fallback to default if malformed)
              └─> execute with current value
```

**Architektúrális szabályok:**

1. **Fix path** — sosem env-var vagy CLI-arg; az operátor egyetlen path-ot ír / olvas
2. **Plain text vagy YAML** — `0.85\n` vagy `key: value`; NE JSON-tomb (parse-fail brittle)
3. **Default-fallback** — ha fájl hiányzik vagy malformed → safe-default (shadow-mode)
4. **Atomic write** — `mv tmp final` (NEM `>` redirect — partial-write race a reader-rel)
5. **Audit-log minden state-flip-re** — `flip 1.0 → 0.95 by user@2026-05-17` ([audit-log-append-only-pattern](audit-log-append-only-pattern.md))
6. **NE használj inotify-ot** — overkill, kifagy edge-case-ekben; egyszerű `cat` per-hívás 1ms

## Anti-pattern

- ❌ **In-memory state hot-swap** — `globals()["threshold"] = 0.85` race-elhet multi-process környezetben
- ❌ **DB-stored config** — overkill 1-számos konstanshoz; emelhet a DB-roundtrip
- ❌ **REST endpoint POST /config** — felelős service-restart-ot követel; nem cron-barát
- ❌ **Hot-reload mindenre** — csak tuning-konstans (numerikus tartomány); NEM struktúra-változás (séma, predikátum-lista)

## Példa

```bash
# vault-crystallize-monitor (Bash)
THRESHOLD=$(cat ~/.vault-config/crystallize-threshold.txt 2>/dev/null || echo "1.0")
if awk "BEGIN {exit !($CONFIDENCE >= $THRESHOLD)}"; then
  auto_propagate
else
  manual_review_queue
fi
```

```python
# 11.11crystallize (Python)
def current_threshold():
    p = os.path.expanduser("~/.vault-config/crystallize-threshold.txt")
    try:
        return float(open(p).read().strip())
    except Exception:
        return 1.0  # shadow default
```

## Mikor használd

| Use case | Hot-reload? |
|----------|-------------|
| Threshold (0.0-1.0) | ✅ Igen |
| Top-K érték (numerikus) | ✅ Igen |
| Prompt-version (`v0.2` / `v0.3`) | ✅ Igen (ENV-flag dual-track) |
| Predikátum-lista (struktúra) | ❌ Schema-migration kell |
| Auth-token | ❌ Secret rotation flow |
| Feature ENV-flag | ❌ Separate gate (env-defaults tracker) |

## Kapcsolódó

- [[crystallize-threshold-ramp]] — ramp-protokoll a hot-reload fájl módosításával
- [[env-flag-default-disabled-gate]] — flag-gating mint komplementer mechanizmus
- [[audit-log-append-only-pattern]] — minden state-flip auditolva
- [[multi-layer-safety-gate]] — config-hot-reload mint Layer 2 a propagation-ban

---
name: Backout-trigger pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern, safety, rollback, monitoring, auto-revert]
---

# Backout-trigger pattern

> [!info] Mit hív életre
> Bármely **éles automatikus művelet** (auto-propagation, auto-merge, auto-deploy, batch-mutáció), amelyik **mérhető regression-signal-t** tud termelni egy küszöb-szint felett. A backout-trigger ezt a signal-t monitorozza, és **küszöb-átlépéskor automatikusan visszahúzza** a változást (vagy disable-li a rendszert).

## A pattern lényege

A naiv auto-pipeline egy "egyirányú" lépés: bemegy, kimegy, ha jó volt jó, ha nem akkor manual-revert. A backout-trigger ezt fordítja meg:

1. **Auto-rendszer fut** és kimérhető metrikákat termel (auto-prop rate, revert rate, test-pass rate, user-feedback)
2. **Monitor-réteg figyeli** ezeket a metrikákat egy ablakon belül (utolsó 24h, utolsó 100 művelet)
3. **Trigger-küszöb** definiált per-metrika (pl. revert-rate > 15%, NLI-fail-rate > 20%)
4. **Trigger-elsütéskor** automatikus action: rollback / disable / alert / sandbox-mode

## A 3 trigger-típus

| Típus | Mire reagál | Akció |
|---|---|---|
| **Soft trigger** | Metrika **trend** romlik (3 ablak alatt 10% drop) | Alert + ramp-down (threshold szigorítás) |
| **Hard trigger** | Metrika **abszolút küszöb** átlépve (revert-rate > 25%) | Auto-disable + rollback-last-N |
| **Anomaly trigger** | Metrika **eloszlás-shift** (Kolmogorov-Smirnov) | Sandbox-mode + manual-review |

## Konkrét vault-megvalósulás

A vault SV B-1 auto-propagation-réteg backout-trigger-je:

```
Metric source: vault-crystallize-monitor (utolsó 14 nap)
Tracked metrics:
  - auto-prop-rate: hány bullet ment auto-prop-ba a teljes propagált-bullets-ből
  - revert-rate: hány auto-prop-bullet lett crystallize-revert-tel törölve
  - g-eval-pass-recall: kalibrációs-set Pass-recall-ja
  - bullet-volume: hány bullet/hét

Triggers:
  HARD:
    - revert-rate > 15% (ablak: 14d, min-volume: 30 bullet)
      → AUTO-DISABLE: VAULT_CRYSTALLIZE_AUTO=0 + slack-alert
    - g-eval-pass-recall < 50% (ablak: 30d, kalibrációs-set)
      → AUTO-DISABLE + threshold-ramp-back-to-shadow
  SOFT:
    - auto-prop-rate trend -10% három héten át
      → threshold-tighten (0.85 → 0.90)
  ANOMALY:
    - bullet-volume + 200% (spike) → sandbox-mode + manual-review
```

## Backout-plan (proaktív tervezés)

Minden auto-mutáció-feature LANDED-elés előtt **backout-plan** szekciót kap:
- **Kapcsoló**: pontosan **melyik env-var / flag** kapcsolja ki egy lépésben
- **Adatfrissítés**: a feature által írt adatok **hogyan** kerülnek vissza eredeti-állapotba (git-revert / DB-snapshot / atomic-delete)
- **Smoke-teszt**: pontosan **melyik 1-2 szkript** bizonyítja hogy a backout sikeres volt
- **Ki értesít**: alert-target, dashboard-link, és melyik ADR-be log-olódik az incidens

A vault konkrét pattern: minden új auto-mutáció-feature ADR-ben kötelező egy `## Backout-plan` és `## Backout-trigger` szekció. Lásd `07-Decisions/2026-05-12 sv-1 memory architecture arch.md` mintát.

## A "min-volume guard" trap

A naiv trigger akkor is elsül, ha **kevés** observáció van — 1 fail 5-ből = 20% revert-rate, de statisztikailag zaj. Mitigation: **min-volume-gate** minden trigger-en (pl. min 30 bullet kell ahhoz hogy a trigger valid legyen).

```
if observation_count < MIN_VOLUME:
    log("Trigger skip: insufficient sample")
    return SKIP
```

Részletek: [[auto-disable-min-volume-guard]].

## Hot-reloadable threshold

A trigger-konfigot **fájlból** olvassa minden ellenőrzés előtt (nem hardcode-olt env-var), így a threshold **újra-deploy** nélkül módosítható:

```bash
# /root/.vault-config/crystallize-threshold.txt
auto-prop-cutoff: 0.85
revert-rate-cap: 0.15
min-volume: 30
window-days: 14
```

A monitor-script minden run-on parse-olja a fájlt. Lásd [[hot-reload-config-pattern]].

## A 4-rétegű safety-gate keretrendszer

Backout-trigger egy a 4 réteg közül, amit high-stakes feature-höz ajánlunk:

| Réteg | Mit véd | Példa |
|---|---|---|
| **ENV-flag** | Default-disabled | `VAULT_CRYSTALLIZE_APPLY=1` |
| **Script-gate** | Pre-check / dry-run / sandbox-branch | `--apply` flag + `crystallize-sandbox-*` branch |
| **Git-hook** | Commit/push előtt blokkol ha rule-sérteget | pre-commit auto-detect main + REAL mode |
| **Backout-trigger** | Runtime metric-watch | `vault-crystallize-monitor` cron |
| **Critic-review** | (5. opcionális) post-action LLM-as-judge | Separate evaluator run |

Részletek: [[multi-layer-safety-gate]].

## Anti-patternek

| Antipattern | Mi a baj | Helyes |
|---|---|---|
| **Trigger fail-mode-ban semmit-nem-csinál** | "alert-only" csak hangol, nem véd | Hard-trigger AUTO-DISABLE-lé fokoz |
| **Threshold hardcode** | Production-tweak = re-deploy + re-test | Hot-reloadable config-fájl |
| **No min-volume guard** | 1 fail 5-ből = 20% panic | `MIN_VOLUME` minden trigger-en |
| **Trigger nélkül auto-mutáció** | "felelőtlen-bot" pattern, nincs visszafogás | Minden auto-mutáció-feature backout-trigger-rel kerül LANDED-be |
| **Backout nincs tesztelve** | Élesben derül ki hogy a rollback se megy | Backout-script smoke-tesztje a feature-acceptance-criterium része |

## Source-evidence (KO-DB)

- `Backout-trigger` token: 2 distinct subject, 5 fact, **2 source-type** (adr + wiki)
- `backout-plan` és `Backout-plan` tokenek: 2-4 subject, **2 source-type** (adr + session)
- `auto-disable trigger` token: 3 subject, 7 fact, **wiki-only** (auto-disable-min-volume-guard.md)
- Top-source: `07-Decisions/2026-05-12 sv-1 memory architecture arch.md` + `07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md`

## Kapcsolódó

- [[multi-layer-safety-gate]] — ENV+script+hook+critic+backout 5-réteg
- [[auto-disable-min-volume-guard]] — min-volume guard a triggerekhez
- [[hot-reload-config-pattern]] — threshold-fájl runtime-ban
- [[rollback-revert-strategy-tiers]] — soft / hard / nuclear revert-tiers
- [[crystallize-threshold-ramp]] — ramp-protokoll shadow→aggressive
- [[env-flag-default-disabled-gate]] — első réteg a safety-gate-ben

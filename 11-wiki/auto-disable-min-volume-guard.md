---
name: Auto-disable watchdog — min-volume guard pattern
type: wiki
tags: ["#type/wiki", "monitoring", "watchdog", "statistics", "false-positive"]
created: 2026-05-17
updated: 2026-05-17
status: stable
---

# Auto-disable min-volume guard pattern

A moving-window-os watchdog-ok (reject-rate, error-rate, pass-rate trigger-ek) hajlamosak false-positive-ra early-stage vagy test-adaton. Néhány smoketest-event vagy egy-két korai apply elég ahhoz, hogy a százalékos küszöb átszakadjon, és a watchdog cascade-crazy módban kilője a védett feature-t. A megoldás: **minimum-volume gate** — a window-statisztika csak akkor él, ha elég valós event halmozódott fel.

## A pitfall — 2026-05-17 incidens

A `/usr/local/bin/vault-auto-disable-check` watchdog első futása FIRE-elt: 7 event-ből 3 critic-discard = **42.9% reject-rate**, ami átlépte a 30%-os küszöböt → flag set, `11.11crystallize --apply` REAL mode kikapcsolva. De: mind a 7 event egyetlen smoketest-ből jött (manual stub response-ok), NEM production scoring-ból. A küszöb production-számra van kalibrálva, a sample meg test-noise volt. Klasszikus low-N false-positive.

## A pattern

```python
MIN_VOLUME = 10  # statisztikailag stabil sample-size

def auto_disable_check(window_events, threshold):
    # Smoketest-eket szűrd ki ELŐSZÖR
    real = [e for e in window_events if not e.is_smoketest]

    if len(real) < MIN_VOLUME:   # ← KÖTELEZŐ gate
        return False, f"insufficient data ({len(real)} < {MIN_VOLUME} min)"

    reject_rate = sum(1 for e in real if e.is_reject) / len(real)
    if reject_rate > threshold:
        return True, f"reject {reject_rate:.1%} > {threshold:.1%}"
    return False, "ok"
```

Kulcs-elemek:
- **MIN_VOLUME** tipikusan **10-30 valós event** — alatta a binomiális variancia túl nagy ahhoz, hogy egy % alapú küszöb értelmes legyen
- **Smoketest-event-eket** explicit `is_smoketest=True` mezővel tag-eld a forrásnál → window-ból kihagyni (NEM utólag szűrni jelentésben)
- **Insufficient-data return** ne legyen `True` (false-positive) és ne legyen silent skip — log-old "waiting for N events" üzenettel, hogy operator lássa a watchdog él, csak még nem trigger-kompetens

## Mikor alkalmazd

| Watchdog | MIN_VOLUME ajánlás | Window |
|---|---|---|
| Crystallize critic-reject | 10 apply | 7 day |
| Eval pass-rate (B-3) | 30 score | 7 day |
| Vault-corruption (audit drop) | 2 audit | 14 day |
| Skill-search miss-rate | 20 query | 1 day |

Általános ökölszabály: ha a küszöb `T%`, akkor MIN_VOLUME ≥ `ceil(3 / T)` — így legalább 3 esemény kell a kiváltáshoz, nem 1 outlier billent. 30%-os küszöbnél tehát min 10 event.

## Komplementer pattern-ek

- **Circuit-breaker** — N (pl. 5) egymás utáni failure → trip, függetlenül a százaléktól. Olyan eset, amikor a rate nem érdekes (pl. service-down), csak a sorozat.
- **Exponential backoff** — trip után ne azonnal re-enable, hanem fokozatosan növekvő retry-interval (1m → 5m → 30m → 4h), hogy oszcillációt elkerüld.
- **Half-open state** — trip után egy próba-event-et engedj át, és csak ha az is jó, akkor full re-enable. Védelem a "first-real-event-after-fix happens to also fail" eset ellen.

A min-volume guard ezekkel kombinálódik, nem helyettesíti őket — együtt adnak production-grade watchdog-ot.

## Élő alkalmazás — vault-auto-disable-check fix (Next session)

> [!todo] TODO
> - Add `MIN_APPLY_VOLUME=10` env-var + gate-check a `/usr/local/bin/vault-auto-disable-check` script tetejére
> - Tag-eld a smoketest-eket `is_smoketest=true` mezővel a `crystallize-audit-log.jsonl`-ban
> - Watchdog filter-ölje ki őket window-számolás előtt
> - Manuálisan reset-eld a 2026-05-17 false-positive flag-et (a sample mind smoketest volt)

## Kapcsolódó

- [[multi-layer-safety-gate]] — 4-rétegű safety-gate playbook, ennek egyik rétege a watchdog
- [[crystallize-threshold-ramp]] — threshold-konfig hot-reload + shadow → conservative → aggressive ramp
- [[../06-Audits/2026-05-17 B-2 Week 3 acceptance gate readout]] — az incidens audit-kontextusa

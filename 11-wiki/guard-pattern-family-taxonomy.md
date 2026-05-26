---
name: Guard-pattern család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/guard, taxonomy, evergreen, safety, defensive-coding]
---

# Guard-pattern család taxonomy

> [!info] TL;DR
> 14 különálló Concept beszél „guard"-ról a vault-ban — de ezek **NEM ugyanaz a minta**. Kétféle ortogonális tengely van: (a) **mit véd** (race-condition / mutation / type / volume), (b) **hova kerül** (script-level / runtime-level / hook-level). Ez a wiki egységes taxonómiát ad + döntési-fát hogy „melyik guardot melyik szituációban".

## Cluster-members (vault Concept-corpus)

| Concept | Védi | Réteg |
|---|---|---|
| video oncanplay guard pattern | race-condition | DOM-event |
| canplay event without guard flag | race-condition | DOM-event |
| readyFired guard flag | race-condition | DOM-event |
| `!busy && !mutedForTTS` guard | race-condition | runtime-state |
| `final.trim()` guard | empty-input | function-entry |
| missing isDemo guard | mutation | API-route |
| mutation route guard | mutation | API-route |
| isDemo guard | mutation | API-route |
| `session.isDemo` guard | mutation | session-context |
| `session.isDemo` guard pattern | mutation | session-context |
| isDemo guard violation | mutation (audit) | review |
| isDemo guard pattern | mutation | API-route |
| demo-fallback readonly guard | mutation | API-route |
| TypeScript guard snippet | type-narrowing | compile-time |
| Auto-disable min-volume guard | volume-anomaly | watchdog-script |

## A 4 guard-család

### 1. Race-condition guard (DOM/event)
**Mintázat:** browser-event (`canplay`, `loadedmetadata`, `play`) több-szöri fire-olódhat → boolean-flag védi a double-execution-t.

```js
let readyFired = false;
video.oncanplay = () => {
  if (readyFired) return;  // GUARD
  readyFired = true;
  startPlayback();
};
```

- `video oncanplay guard pattern`
- `readyFired guard flag`
- `!busy && !mutedForTTS guard` — multi-state-machine (TTS player)

**Szabály:** event-handler ELEJÉN legyen guard, NEM a kezelés végén.

### 2. Mutation guard (API/route-level)
**Mintázat:** read-only kontextusban (demo-mode, observer-role) mutation-route-okat **403-mal** zárj le.

```ts
// minden mutation route ELEJÉN:
if (session.isDemo) return res.status(403).json({ code: 'DEMO_READ_ONLY' });
```

- `session.isDemo guard pattern` — Kinda/teszt-eu Balance-MVP
- `mutation route guard`
- `demo-fallback readonly guard` — wiki: [[demo-fallback-readonly-guard]]
- `isDemo guard violation` — code-review audit-pattern (talál hiányzó guardokat)

**Szabály:** middleware-szinten centralizáld (`requireWritableSession`), per-route ismétlés ⇒ felejtési-rizikó.

### 3. Type-narrowing guard (TypeScript/runtime)
**Mintázat:** TS user-defined type-guard (`function isFoo(x): x is Foo`) + runtime-validáció.

```ts
function isUser(x: unknown): x is User {
  return typeof x === 'object' && x !== null && 'id' in x;
}
if (!isUser(data)) throw new TypeError();
// data: User innentől
```

- `TypeScript guard snippet`
- `final.trim() guard` — string-empty check (technically type+value)

**Szabály:** runtime-payload (API-response, JSON-parse) MINDIG guard-on át fogadd; soha `as User`-rel.

### 4. Watchdog guard (volume/anomaly)
**Mintázat:** auto-disable watchdog NEM zárja le a feature-t kis-volumenű false-positive miatt → **MIN_VOLUME gate**.

```python
if total_calls < MIN_VOLUME:  # GUARD
    log("skip: insufficient volume")
    return
if failure_rate > THRESHOLD:
    auto_disable()
```

- `Auto-disable min-volume guard` — wiki: [[auto-disable-min-volume-guard]]

**Szabály:** observability-watchdog mindig MIN_VOLUME-mal, különben első-100-call smoke-test → false-pos cascade.

## Döntési-fa: melyik guard kell?

```
Adott helyzet:
├── Event-handler / async-callback?           → race-condition (1)
├── HTTP-route ami DB-t/state-et módosít?     → mutation (2)
├── unknown-shape adat fogadása (parse/IPC)?  → type-narrowing (3)
└── Watchdog / auto-disable / threshold-trigger? → min-volume (4)
```

## Anti-pattern listák

| Anti-pattern | Miért rossz |
|---|---|
| Guard CSAK a happy-path ágon | edge-case mutation route felejtésekor security-rés |
| `if (x) { ... } else { /* nothing */ }` | NEM guard, csak conditional. Guard = **early-return** |
| Watchdog MIN_VOLUME nélkül | első 1-3 false-pos cascade-elszigeteli az egész feature-t |
| TS `as Foo` cast | NEM guard. Runtime crash-elhet, csak compile-time-suppression |

## Reusable szabályok

1. **Early-return**: guard MINDIG `if (!ok) return` formában, ne mély if-pyramid
2. **Centralizáld**: ha 3+ helyen ismétlődik, middleware/decorator/hook
3. **Audit-eljárás**: havonta `grep -L "isDemo" routes/*.ts` (negatív-grep) → hol HIÁNYZIK
4. **Min-volume**: minden auto-trigger-watchdog default 50-100 call alatt no-op
5. **Combine racing + mutation**: TTS-player mutation-state-machine `!busy && !mutedForTTS` minta — több bool-flag AND-elve

## Kapcsolódó

- [[demo-fallback-readonly-guard]]
- [[auto-disable-min-volume-guard]]
- [[digital-signage-player-gotchas]]
- [[fallback-pattern-family-taxonomy]]
- [[multi-layer-safety-gate]]

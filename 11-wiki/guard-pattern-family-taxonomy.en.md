---
name: Guard-pattern family taxonomy
type: wiki
lang: en
translated_from: guard-pattern-family-taxonomy
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/guard, taxonomy, evergreen, safety, defensive-coding]
---

# Guard-pattern family taxonomy

> [!info] TL;DR
> Many distinct "guard" concepts appear in codebases, but they are NOT the same pattern. Two orthogonal axes: (a) **what it protects** (race-condition / mutation / type / volume), (b) **where it lives** (script-level / runtime-level / hook-level). This wiki gives a unified taxonomy + a decision tree for "which guard for which situation".

## Cluster members (representative)

| Concept | Protects | Layer |
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

## The 4 guard families

### 1. Race-condition guard (DOM/event)
**Pattern:** browser events (`canplay`, `loadedmetadata`, `play`) may fire multiple times → boolean flag protects against double-execution.

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
- `!busy && !mutedForTTS guard` — multi-state machine (TTS player)

**Rule:** guard at the START of the event handler, NOT at the end.

### 2. Mutation guard (API/route-level)
**Pattern:** in a read-only context (demo-mode, observer role), close mutation routes with **403**.

```ts
// at the START of every mutation route:
if (session.isDemo) return res.status(403).json({ code: 'DEMO_READ_ONLY' });
```

- `session.isDemo guard pattern`
- `mutation route guard`
- `demo-fallback readonly guard` — wiki: [[demo-fallback-readonly-guard]]
- `isDemo guard violation` — code-review audit pattern (finds missing guards)

**Rule:** centralise at middleware level (`requireWritableSession`), per-route repetition ⇒ forgetting risk.

### 3. Type-narrowing guard (TypeScript/runtime)
**Pattern:** TS user-defined type guard (`function isFoo(x): x is Foo`) + runtime validation.

```ts
function isUser(x: unknown): x is User {
  return typeof x === 'object' && x !== null && 'id' in x;
}
if (!isUser(data)) throw new TypeError();
// data: User from here on
```

- `TypeScript guard snippet`
- `final.trim() guard` — string-empty check (technically type+value)

**Rule:** runtime payload (API response, JSON parse) MUST always go through a guard; never `as User`.

### 4. Watchdog guard (volume/anomaly)
**Pattern:** auto-disable watchdog does NOT shut down the feature due to small-volume false positives → **MIN_VOLUME gate**.

```python
if total_calls < MIN_VOLUME:  # GUARD
    log("skip: insufficient volume")
    return
if failure_rate > THRESHOLD:
    auto_disable()
```

- `Auto-disable min-volume guard` — wiki: [[auto-disable-min-volume-guard]]

**Rule:** observability watchdogs always use MIN_VOLUME, otherwise the first-100-call smoke test → false-positive cascade.

## Decision tree: which guard do I need?

```
Given situation:
├── Event-handler / async-callback?              → race-condition (1)
├── HTTP route that mutates DB/state?            → mutation (2)
├── Receiving unknown-shape data (parse/IPC)?    → type-narrowing (3)
└── Watchdog / auto-disable / threshold-trigger? → min-volume (4)
```

## Anti-pattern list

| Anti-pattern | Why bad |
|---|---|
| Guard ONLY on the happy-path branch | edge-case mutation route missed = security hole |
| `if (x) { ... } else { /* nothing */ }` | NOT a guard, just a conditional. Guard = **early return** |
| Watchdog without MIN_VOLUME | first 1-3 false-positives isolate the entire feature |
| TS `as Foo` cast | NOT a guard. Runtime can crash; only compile-time suppression |

## Reusable rules

1. **Early return**: guard is ALWAYS `if (!ok) return`, not deep if-pyramid
2. **Centralise**: if it repeats in 3+ places, middleware/decorator/hook
3. **Audit process**: monthly `grep -L "isDemo" routes/*.ts` (negative grep) → where is it MISSING
4. **Min-volume**: every auto-trigger watchdog default no-op under 50-100 calls
5. **Combine race + mutation**: TTS-player mutation state-machine `!busy && !mutedForTTS` pattern — multiple bool flags AND-ed

## Related

- [[demo-fallback-readonly-guard]]
- [[auto-disable-min-volume-guard]]
- [[digital-signage-player-gotchas]]
- [[fallback-pattern-family-taxonomy]]
- [[multi-layer-safety-gate]]

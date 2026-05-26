---
name: clean-context-subagent-handoff
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/multi-agent", "#topic/orchestration", "#topic/context-management", "#topic/subagent"]
---

# Clean-context subagent handoff — multi-agent context-isolation primitív

## TL;DR

Az orchestrator-agent **soha NEM ad át teljes saját context-window-t** a subagent-nek; helyette egy **lean, célzott prompt-ot** ír, ami CSAK a feladathoz szükséges info-t tartalmazza. A subagent fut, **csak a feladat-eredményt (summary-only)** adja vissza. Cél: (a) context-window overflow elkerülése, (b) compound-error mitigáció, (c) párhuzamosíthatóság (8+ subagent egyszerre, $0 cost kompromisszum nélkül).

## Háttér (3+ source-evidence)

- [[sv-03-multi-agent-orchestration]] — "clean-context subagent handoff, prevents: context window overflow"
- [[sv-03-multi-agent-orchestration]] — "Orchestrator+isolated subagent+summary-only return" mint kanonikus minta
- [[claude-code-subagent-fanout]] — vault-on 19+ ezredidős super-session során 8× parallel fanout, $0
- [[sv-03-multi-agent-orchestration]] — "stateful long-running agents causes compounding errors" — ellen-pattern
- Anthropic Multi-Agent Research blog (2024-25) — "Building Effective Agents" alapelve

## Mintázat

Orchestrator (master agent) lépései:

1. **Task decomposition**: a komplex feladatot N függetlenül megoldható részre bontja
2. **Per-task prompt-engineering**: minden subagent-hez célzott prompt — input + szabályok + return-format. NEM a saját context-window-t adja át, hanem **szintetizált, lean input-ot**
3. **Spawn N subagent parallel**: minden subagent saját, **friss** context-window-val indul (NEM látja a master előzményeit)
4. **Wait + collect**: subagent visszaadja a `summary-only` output-ot (NEM a teljes belső trace-et)
5. **Aggregate**: orchestrator a saját context-jébe csak a summary-kat olvassa be — nem a subagent-ek tokenjeit
6. **Audit**: minden subagent-hívás logolva (mit kapott, mit adott vissza)

Vault-példák:

- **`vault-ko-ingest` triplet-extraction**: 8 parallel subagent, mindegyik kap N raw-doc-ot, visszaad triplet-listát
- **`11.11crystallize claude-code-scorer`**: 4 dim × 5 skála G-Eval, subagent-fanout pending pattern
- **Wiki-roundtable (round-2 axis A)**: 5-8 wiki egyszerre, 1 subagent per axis

## Anti-pattern

- **Master saját context-window-t átad subagent-nek**: token-cost ×2, és a subagent a master noise-jától is zavarodik. **CRITICAL anti-pattern.**
- **Stateful long-running subagent**: ha a subagent állapota fennmarad több hívás között, compound-error halmozódik fel. Minden hívás clean-context-tal indul.
- **Subagent „rich return"**: subagent visszaadja teljes belső trace-jét → orchestrator context-window robban. Csak `summary-only` (200-2000 token).
- **Subagent → subagent recursion korlát nélkül**: subagent szubgentet spawn-ol, az is, az is → token-bomb. Max-depth-cap (default: 1, ritkán 2).
- **Race-condition shared-state-en**: 8 parallel subagent ugyanabba a fájlba ír → corruption. Per-subagent dedikált output-path (`/tmp/<uuid>.json`) + post-aggregate.

## Reusable szabályok

1. **Subagent prompt ≤ 4-8K token**: minden, ami nagyobb, vagy túl-task-os, vagy noise. Refaktorálj.
2. **Summary-only return ≤ 2K token**: kényszerítsd a structured-output-tal (JSON-schema, return-format-példa).
3. **Per-subagent dedikált output-fájl** `/tmp/<task-id>-<subagent-id>.json` — race-condition-szabad.
4. **Max-depth = 1** (default): orchestrator → subagent → result. Mélyebb nesting csak különleges esetben.
5. **Idempotency-key per task** — replay-safe.
6. **Audit-log append-only** ([[audit-log-append-only-pattern]]): `(task-id, subagent-id, input-hash, output-hash, ts)`.
7. **Timeout per subagent** (20-60s), defensive — nem lóghat egy lassú subagent az egész orchestrator-t.

## Buktatók

- **Token-amplification**: az aggregate-szumma plus N×subagent-cost gyorsan dráguló. Per-batch token-budget hard-cap.
- **Coherence-drift**: 8 subagent ugyanarra a kérdésre 8 különböző választ ad — orchestrator-szinten consensus / synthesis vagy ABSTAIN ([[dont-hallucinate-abstain-pattern]]).
- **Lost-context bug**: a master elfelejti, hogy mit kérdezett a subagent-től, és a return-summary önmagában nem értelmezhető. A prompt + return mindig együtt logoltassad.
- **Hallucinated subagent-output**: a subagent fabrikál tényt — NLI-gate ([[nli-hallucination-check-pattern]]) az aggregate-szinten.

## Kapcsolódó

- [[sv-03-multi-agent-orchestration]] — teljes multi-agent arch
- [[claude-code-subagent-fanout]] — vault-on alkalmazott concrete-implementáció
- [[audit-log-append-only-pattern]] — log-szabály
- [[dont-hallucinate-abstain-pattern]] — multi-subagent disagreement-handling
- [[nli-hallucination-check-pattern]] — output-gate
- [[skill-metadata-catalog-pattern]] — komplementer „what to load" stratégia

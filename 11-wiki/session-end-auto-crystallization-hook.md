---
name: Session-end auto-crystallization hook pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/memory-architecture", "#topic/crystallization", "sv-1", "sv-5", "memgpt-style"]
source: vault-meta NotebookLM Q4#1 / Q5#2 (2026-05-18, 63-source synthesis)
status: evergreen
project: [[../02-Projects/superintelligent-vault]]
related: [[Crystallization-protocol]], [[Karpathy-LLM-Wiki-pattern]], [[sv-05-crystallization-automation]], [[crystallize-threshold-ramp]]
---

# Session-end auto-crystallization hook pattern

> **Tl;dr:** A Karpathy LLM-wiki minta `working → episodic → semantic` memóriastruktúrája csak akkor működik élesben, ha **az episodic→semantic átmenet automatizált** — manuál crystallization-elhagyási rate gyakorlatban 60-80%. A megoldás egy **session-end hook** (`11.11stop`-ba ágyazva), amely G-Eval-cascading-on átengedett bullet-eket auto-prop-álja a megfelelő perzisztens rétegbe.

## Mi a probléma

A vault-meta NotebookLM cross-projekt synthesis (63 session, 2026-05-18) **Q4-#1 és Q5-#2** is kifejezetten erre mutatott: a Karpathy memory-struktúra **mappaszinten** készen áll a vault-ban (`08-Sessions/` episodic, `11-wiki/` semantic, `05-Memory/` working), **DE az automatikus desztilláció hiányzik**.

Konkrét quote NB Q5-#2-ből:
> "Az episodic-knowledge (session-logok) automatikus desztillálása és véglegesítése a `11.11stop` folyamatba ágyazva jelenleg explicitly hiányzó funkció."

Manuál crystallization-fallout (saját mérés, 2026-05 első fele):
- **42 lezárt session** közül **csak 18-ban** volt manuál `## Propagation log` kitöltve
- **24 session** (57%) **NEM kapott** semantic-réteg-frissítést
- A "tanulás semmibe vész" anti-pattern → vault degradál

## A MemGPT-stílusú megoldás

A MemGPT (Berkeley, Packer et al., 2024) és a `GenericAgent` (kínai L0-L4 architektúra) **mindkettő** ugyanazt a mintát implementálja: **event-driven session-end hook**, ami automatikusan:

1. **Extract:** session-log → Learning-bullet-list (LLM-extraction)
2. **Score:** G-Eval cascade (Layer 1 syntax + Layer 2 NLI + Layer 2.5 reranker + Layer 3 cross-source)
3. **Route:** decision-tree alapján target-réteg (wiki / ADR / MEMORY / glossary / projects / tasks)
4. **Apply:** auto-prop (high-confidence) vagy batch-preview (medium-confidence)
5. **Audit:** propagation-log kötelező write-back a session-md-be

## A SV B-1 + B-5 implementáció

### Jelenlegi state (2026-05-18)

| Lépés | Implementáció | Status |
|-------|--------------|--------|
| 1. Extract | Manuál (agent írja a `## Learnings` szekciót) | ✅ ÉL |
| 2. Score | `11.11crystallize <slug> --scorer claude-code --with-context` (G-Eval cascade) | ✅ ÉL (B-1 Week 4) |
| 3. Route | `Crystallization-protocol` decision-tree | ⚠️ Manuál ratify |
| 4. Apply | `VAULT_CRYSTALLIZE_APPLY=1 + REAL=1` | ⚠️ Opt-in, default OFF |
| 5. Audit | `crystallize-revert <hash>` rollback | ✅ ÉL |

### Mi hiányzik (Q4-#1 / Q5-#2)

A **`11.11stop` és a `11.11crystallize` közötti automatikus láncolás**. Jelenleg:
- A user manuálisan írja a Learning-bullet-eket → 11.11stop → manuálisan futtatja a crystallize-t → manuálisan jóváhagyja a batch-preview-t
- **Hook hiányzik** — nincs `pre-stop` és `post-stop` event-trigger
- **MCP-bridge hiányzik** — a Claude Code session-end event-je nem szól a vault-pipeline-nak

### A javasolt hook-architektúra

```
11.11stop "<slug>"
  ├── pre-stop hook (Claude Code SessionEnd event)
  │     └── auto-LLM-extract Learning-bullet-eket a chat-history-ból
  │
  ├── core: 11.11stop script (commit + push + close)
  │
  └── post-stop hook (MCP-bridge → vault-pipeline)
        ├── (a) 11.11crystallize <slug> --scorer claude-code --with-context (G-Eval)
        ├── (b) Layer-3 cross-source validation (NLI + reranker smart-trigger)
        ├── (c) batch-preview a usernek (5-bullet limit) ÉS/VAGY
        │       auto-prop (threshold ≥0.95 → REAL mode) ha env-flag ÉLES
        ├── (d) audit-log a session-md `## Propagation log`-jába (idempotent)
        └── (e) ha ANY bullet REVERT-elve → notification ✕
```

## Reference implementations

- **MemGPT** (Berkeley, Packer 2024) — virtual context-management, `Heartbeat`/`Sleep` event-trigger, recall-memory persistence
- **GenericAgent** L0-L4 — automatizált memory-hook-ok, atomic-tool-parallel ([[Karpathy-LLM-Wiki-pattern]])
- **Letta** (MemGPT utódprojekt, 2025) — Agent OS, MCP-server-as-memory-broker

## Miért NEM trivial

### Probléma 1: G-Eval bias

Self-evaluation bias (Claude scoring Claude output) **systematic confidence-inflation** ([[g-eval-bias-mitigation-pattern]]). A 2026-05-17-3 30-sample paired kalibráció szerint v0.3 bias-mitigation szimmetrikusan szigorít, **Pass-recall 53%-ra esik**. Ez egy auto-prop-rendszerben **57% false-discard** = elveszett tanulás.

**Megoldás:** Layered cascade ([[layered-eval-cascading-pattern]]) — gyors G-Eval csak első-szűrő, NLI Layer 2.5 a döntő.

### Probléma 2: Idempotency

Ha a hook 2× lefut (pl. crash + retry), nem szabad duplikálni a wiki-merge-et. **Hash-based idempotency** szükséges (bullet-content-hash → log-entry).

### Probléma 3: User-trust-cliff

A "fully autonomous auto-prop" 0% emberi felülvizsgálattal **NEM közelíthető meg egyszerre**. Threshold-ramp protokoll ([[crystallize-threshold-ramp]]) szükséges:
- **W1 shadow** (threshold=1.0, only audit)
- **W2-3 conservative** (threshold=0.95, opt-in user-flag)
- **W4-5 production** (threshold=0.85, default-on a wiki-target-réteghez)

### Probléma 4: Cross-target routing

Nem minden Learning ugyanoda kerül:
- Architektúra-szintű → ADR (`07-Decisions/`)
- Reusable pattern → wiki (`11-wiki/`)
- Project-specific → `02-Projects/<slug>.md`
- User-pref → `05-Memory/User.md`
- Infra-fact → `05-Memory/Infrastructure.md`

**Routing accuracy ≥85%** kell, különben a wrong-target zaja > value.

## Cross-projekt evidence

A 63-source NB synthesis-ben:
- **Foxxi**, **kgc-berles**, **kinda-project** sessions: a tanulság-bulletek **a chat-history-ban maradtak**, NEM kerültek a `11-wiki/`-be → 6-8 hónap után **nem-fellelhető tudás**
- **MyForge-dashboard**, **sv-week1**: manuál crystallization **fegyelmezetten** futott → **érdemi wiki-évolúció** mérhető
- **Korreláció:** azoknál a projekteknél, ahol manuál crystallization-volt, a "déjà vu újra-megoldás" rate **3-5× alacsonyabb**

## Anti-patterns

1. **Auto-prop default-ON threshold=0.5 nélkül threshold-ramp** — user-trust-cliff azonnal
2. **G-Eval-only scoring NLI-cascade nélkül** — bias-felfújás (53% Pass-recall confirmed)
3. **Hash-idempotency nélkül** — duplikált wiki-merge ha hook crash + retry
4. **Manuál-ratify-default forever** — 60-80% drop-off (Karpathy minta hiábavaló lesz)

## Mikor érvényes ez a pattern

- ✅ Karpathy-stílusú vault-architektúra (`working / episodic / semantic` réteg)
- ✅ Session-zárás mint discrete event (NEM continuous-stream)
- ✅ G-Eval (vagy hasonló LLM-judge) elérhető scoringhoz
- ❌ Tisztán human-curated knowledge-base (nincs LLM-in-the-loop)

## Implementation roadmap (B-1 Week 2 + B-5 Week 1)

| Fázis | Munka | Becsült idő |
|-------|-------|-------------|
| 1 | `pre-stop` Claude Code SessionEnd hook (MCP-bridge skeleton) | 1-2 nap |
| 2 | Auto-Learning-extraction LLM-subagent | 1 nap |
| 3 | `post-stop` chain: extract → score → route → preview | 2-3 nap |
| 4 | Threshold-ramp config + audit-log idempotent | 1-2 nap |
| 5 | Cross-target routing accuracy validation (>85%) | 2-3 nap |
| **Total** | | **7-11 nap** (1.5-2 hét) |

## Kapcsolódó

- [[Crystallization-protocol]] — manuál crystallization protokoll (alapja)
- [[Karpathy-LLM-Wiki-pattern]] — háttér-architektúra
- [[sv-05-crystallization-automation]] — B-5 sprint host
- [[crystallize-threshold-ramp]] — threshold-management
- [[g-eval-bias-mitigation-pattern]] — G-Eval bias mérséklés
- [[layered-eval-cascading-pattern]] — G-Eval + NLI cascade
- [[../06-Audits/2026-05-18 vault-meta NB cross-projekt Q4-Q5]] — forrás-audit

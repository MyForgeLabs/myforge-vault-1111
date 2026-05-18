---
name: dfsdt-backtracking-tool-composition
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/multi-agent", "#topic/tool-composition", "#topic/agent-reasoning", "#topic/backtracking"]
---

# DFSDT backtracking multi-step tool-composition-hez

## TL;DR

A **DFSDT (Depth-First Search-based Decision Tree)** a ToolLLM-papírból ismert backtracking-algoritmus, ami a hagyományos ReAct/Chain-of-Thought lineáris hibafelhalmozódását („compounding errors") oldja meg: amikor egy tool-hívás eredménye nem felel meg, az agent **visszalép** és más ágat próbál, ahelyett, hogy egyenes vonalban tovább halmozná a hibákat. Multi-step agent-feladatokban a `successrate` 28-45%-ról 60-78%-ra ugrik DFSDT mellett. Cserébe a token-budget 2-4× nagyobb.

## Háttér (3+ source-evidence)

- [[sv-04-tool-composition]] — "ToolLLM DFSDT (Depth-First Search-based Decision Tree) backtracking-et javasol; nyitott: hogyan tanítható natívan többágú, nem-szekvenciális tervezés"
- [[sv-04-tool-composition]] — "Reflexion-stílusú self-verification, DFSDT-backtracking" mint compositional-drift mitigáció
- [[sv-02-recursive-self-improvement]] — DFSDT-szerű search-mintázat a self-correction-blind-spot mitigációjához (kapcsolódó RSI-technika)
- [[superintelligent-vault-research]] — DFSDT mint Bootstrapper-tier eszköz-stratégia opció

## Mintázat

ReAct lineáris: `tool_1 → result_1 → tool_2 → result_2 → ...`. Ha `tool_2` rossz lett, `tool_3` rossz alapra épül, és a hibák összeadódnak. A user vagy hibás végeredményt kap, vagy az agent végtelen-loop-ba ragad korrekciós próbálkozásokkal.

DFSDT keresési-fát épít: minden tool-hívás-eredmény után **kettő opció** — (a) folytatni az ágat, vagy (b) visszalépni 1-2 szintet és más tool-t/argumentet próbálni. A fa "DFS"-stílusban bontódik ki: egy ágat addig követ, amíg vagy sikerül, vagy konfidencia-küszöb alá esik. Ekkor backtrack, és **explicit** próbál egy alternatívát.

A vault-kontextusban a DFSDT analógiája a `vault-graph-query` cross-source-bányászatnál: ha az első predikátum-match üres, NEM csak hibát adunk vissza, hanem a query-tree következő legjobb predikátumát is próbáljuk. Hasonlóan: `vault-net-ingest` retry-stratégiája (firecrawl → playwright → cloakbrowser) is DFSDT-szerű ([[cloakbrowser-fingerprint-bypass]]).

## Anti-pattern

- **DFSDT-t single-tool feladatra futtatni**: 1-step task = 0% nyereség, 2-4× token-veszteség. A backtracking csak ≥3-lépés multi-step feladatban éri meg.
- **Mély DFS unbounded fa-mélységgel**: search-space exponenciális robbanás. Mindig hard-cap max-depth (3-5) + token-budget (pl. 20K).
- **DFSDT helyett "újrakezdés"**: ha a teljes ágat eldobod minden hibára, az NEM backtracking, hanem brute-force-retry — drágább és nem tanulsz az ágról.
- **DFSDT-t agent-szerver-szinten implementálni** anélkül, hogy a tool-okat idempotens / state-less módon írnád meg. A backtrack csak akkor működik, ha a kor-tool nem hagyott mellékhatást a világon.

## Reusable szabályok

1. **Max-depth cap**: 3-5 szint default. 7+ szint = exponenciális token-robbanás, ROI negatív.
2. **Token-budget hard-stop**: per-task ≤ 20-50K. Ha túllép, fall-back lineáris ReAct + warning.
3. **Tool-idempotens contract**: minden DFSDT-kompatibilis tool dokumentálja, hogy állapotmentes-e (`db-write` NEM, `vault-graph-query` IGEN).
4. **Backtrack-trigger-küszöb**: P(success) < 0.40 az eredmény-confidence-en → backtrack. Skálahangolás per-domain (search 0.50, retrieval 0.35).
5. **Best-of-N memo**: a már próbált ágakat memo-tárolod ugyanazon a session-en belül, hogy ne ismételd újra.
6. **Combine Reflexion + DFSDT**: a backtrack-előtt írj 1-2 mondatos critique-ot ("miért bukott meg az ág?") → a következő ág-választást ez vezérli, nem random.

## Buktatók

- **Stateful tool-mellékhatás-rontás**: ha a `tool_2` ír egy DB-be és backtrack-elsz, a DB-állapot megmarad — explicit rollback-procedúra vagy sandbox-branch ([[sandbox-branch-mutation-isolation]]) kell.
- **LLM-judge bias** a confidence-küszöbnél: self-favoritism miatt az LLM hajlamos "P(success) = 0.85" overestimate-re. Calibrálj 30-100 sample-en, ha komolyan veszed.
- **Tool-spec drift** ([[memgraph-ce-feature-limits]]-szerű): ha egy tool API-ja változik a DFSDT-tanult priors közben, a backtrack-stratégia elavul. Periodikus újratanulás vagy MCP-absztrakció kell.
- **Best-of-N anti-pattern**: csak a "végső legjobb" ágat tartani meg, az alternatívák ki-dobni → tanulási információ-veszteség. Az ágakat memo-ld a session-en belül.
- **Lineáris-ReAct fall-back-kényszer**: ha a budget elfogy és lineáris-ReAct-re esel vissza, NEM `ABSTAIN` — silent-confidence-drop. Better: explicit `LOW_CONFIDENCE` flag a return-objektumban.

## Mikor használd / mikor NE

| Task | DFSDT érdemes? | Miért |
|---|---|---|
| 1-lépés keresés (kérdés → válasz) | NEM | Backtrack overhead 0% nyereség |
| 3-7 lépés multi-tool agent | IGEN | A compounding-errors itt domináns |
| ≥10 lépés komplex workflow | RÉSZBEN | Fa exponenciális — max-depth-cap + Best-of-N memo |
| Stateful destructive task (DB-write) | CSAK sandbox-ban | A mellékhatás miatt backtrack rontásos |
| Real-time interactive | NEM | Latency 2-4× — user-türelmet öl |

## Kapcsolódó

- [[sv-04-tool-composition]] — teljes tool-composition-architektúra
- [[sandbox-branch-mutation-isolation]] — backtrack-safe write-isolation
- [[cloakbrowser-fingerprint-bypass]] — DFSDT-szerű fallback-chain (firecrawl → playwright → cloakbrowser)
- [[reranker-cost-optimization-not-size]] — analóg cost-megfontolás
- [[verification-step-before-claim]] — Reflexion-komplementer technika

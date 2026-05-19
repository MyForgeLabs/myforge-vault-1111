---
name: async-memory-consolidation-letta
type: wiki
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/wiki", "#topic/memory-architecture", "#topic/agent", "#topic/sleep-time-compute", "#topic/letta", "lang/en"]
lang: en
translated_from: async-memory-consolidation-letta.md
---

# Async memory consolidation (Letta-style sleep-time compute)

## TL;DR

The **Letta-style "sleep-time compute"** pattern: during the agent's **idle** periods (user absent), a background process processes fresh episodic memory into higher-level semantic memory. The online query path does NOT block — consolidation is off-line cron / queue. The trade-off: memory contains "deeper" reflections because the background process has more time + larger context window.

## Background (3+ source evidence)

- [[sv-01-memory-architecture]] — "Letta — Memory-first agent framework — sleep-time-compute (agent learns/updates in idle periods)"
- [[sv-01-memory-architecture]] — "Async memory consolidation, implemented_in: Letta-style background script"
- [[sv-05-crystallization-automation]] — vault `11.11crystallize` as sleep-time-compute analogy (after session close, batch-style Learnings → wiki/Memory/Decision propagation)
- [[Karpathy-LLM-Wiki-pattern]] — Karpathy crystallization flow direct analogy (raw session → distilled wiki async)
- [[sv-08-notebooklm-cognitive-layer]] — weekly commute-podcast cron as vault-meta sleep-time output

## Pattern

3-layer memory architecture:

| Layer | Latency | Content | Update mechanism |
|---|---|---|---|
| Working / context-window | <1s | current task | every token |
| Episodic / raw events | <50ms | raw session trace | append-only, online |
| Semantic / consolidated | <100ms | reflections, ADRs, evergreen wikis | **sleep-time async**, cron / triggered |

The sleep-time job typically:

1. Pulls N fresh episodic events (e.g. since last session close)
2. Reflects with an LLM: "what's the lesson?", "what to crystallize?"
3. Writes to semantic store — wiki file, ADR, glossary entry
4. Refreshes index (embeddings, KG triplets, BM25)
5. Audit log: what went where + why

In the vault implementation, this is the **`11.11crystallize` workflow** ([[Crystallization-protocol]]): on session close, Summary + Learnings + Next form ME-like content, later (optionally `VAULT_CRYSTALLIZE_AUTO=1`) G-Eval scoring + propagation into the right layers.

## Anti-patterns

- **Online (foreground) consolidation during user query**: latency-spike + token-cost user-facing. Does NOT belong on the critical path.
- **Batch job without idempotency**: if cron fires twice by accident → duplicate consolidation + duplicate audit entry. Idempotency key required (see [[audit-log-append-only-pattern]]).
- **Reflection without ground truth**: the consolidator writes self-favoring "own" reflections, NOT the evidence. The NLI layer ([[nli-hallucination-check-pattern]]) gates this.
- **Sleep-time job tied to "user offline"**: unreliable for serverless / cloud agents — explicit cron / queue-trigger is better.

## Reusable rules

1. **Two code paths**: online query path (read-only semantic-from-cache) AND offline consolidation path (write to semantic store). Don't mix.
2. **Explicit trigger**: cron, queue event, `11.11stop`-style session-end signal. NOT idle-timeout (unreliable).
3. **Idempotency key**: `consolidation:<session-id>` unique, replay-safe.
4. **NLI/G-Eval gate** before propagation — avoid self-reinforcing reflection loops.
5. **Audit log append-only**: every consolidation recorded (`when`, `what`, `where`, `why`), reversible.
6. **Token budget at batch level**, NOT per-event — else seasonality spike (many sessions in the morning) → cost blow-up.
7. **Sandbox mutation** ([[sandbox-branch-mutation-isolation]]): consolidation on a branch, merge only after audit pass.

## Pitfalls

- **Catastrophic-forgetting cousin**: if sleep-time overwrites a semantic entry with newer episodic, the old info can be lost. Append-only history mandatory, override only with explicit revert.
- **Cost spike off-hours**: cron job at 3 AM always runs — monthly token bill isn't 0. Idle-detect + delta-only-if-changed.
- **Coherence drift**: a newly consolidated semantic entry may contradict one from 6 months ago. Weekly coherence check ([[vault-net-ingest]]-style).

## Related

- [[sv-01-memory-architecture]] — full memory architecture
- [[Crystallization-protocol]] — vault implementation
- [[Karpathy-LLM-Wiki-pattern]] — background philosophy
- [[audit-log-append-only-pattern]] — write rule
- [[sandbox-branch-mutation-isolation]] — write isolation
- [[nli-hallucination-check-pattern]] — pre-propagation gate

## Hungarian original

[[async-memory-consolidation-letta]]

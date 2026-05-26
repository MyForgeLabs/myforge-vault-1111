---
name: Benchmark-driven memory architecture via MCP server
type: wiki
tags: ["#type/wiki", "memory", "rag", "mcp", "agent-architecture", "benchmark", "lang/en"]
created: 2026-05-19
updated: 2026-05-19
lang: en
translated_from: agentmemory-benchmark-driven-memory-arch.md
source_repo: rohitg00/agentmemory
source_url: https://github.com/rohitg00/agentmemory
source_license: AGPL-3.0 (engine) + MIT (agentmemory wrapper)
---

# Benchmark-driven memory architecture via MCP server

A pattern for **building benchmark-backed, context-window-independent scalable agent memory** so that a single server can serve multiple agent clients. The rohitg00/agentmemory implementation is a concrete evolution of the Karpathy LLM-Wiki pattern (per its self-positioning), and provides the relevant benchmark framework for our SV-1 axis.

## The essence of the pattern

Three pillars without which a memory layer stays "vibe-driven":

1. **Confidence + lifecycle**: each memory record gets a confidence score, decay curve (Ebbinghaus) and lifecycle state (active → stale → evicted). Contradiction detection on active overwrite.
2. **Hybrid retrieval — RRF fusion**: BM25 + dense vector + knowledge-graph traversal as three independent streams, **Reciprocal Rank Fusion (k=60)** + session diversification (max 3/session). No stream can dominate.
3. **4-tier consolidation**: Working (raw tool-use observation) → Episodic (session summary) → Semantic (extracted fact/pattern) → Procedural (workflow). Inspired by human sleep consolidation. Backup is asymmetric: only episodic+ tiers are survival-tracked.

## Benchmark framework (the critical part)

Without proving claims, every memory tool becomes interchangeable marketing copy. The repo exposes three independent benchmark sets:

| Benchmark | What it measures | Reference numbers |
|---|---|---|
| **LongMemEval-S** (ICLR 2025, 500 Q) | R@5 / R@10 / MRR retrieval accuracy | agentmemory 95.2 / 98.6 / 88.2; BM25-only fallback 86.2 / 94.6 / 71.5 |
| **LoCoMo** (long conversation memory) | Cross-tool comparison (mem0 vs Letta vs agentmemory) | mem0 R@5 68.5%, Letta R@5 83.2%, agentmemory 95.2% |
| **Token cost / year** | Operating cost vs recall quality | Paste-full 19.5M+ tokens (impossible); LLM-summarized ~650K / $500; agentmemory ~170K / $10; local-embed $0 |

The last table is the most honest: recall alone says nothing about a deployable system. The "92% fewer tokens" claim only means something when grounded against a benchmark.

## Token-economy explicit modelling

The "built-in memory" (`CLAUDE.md`, `.cursorrules`) weakness isn't storage but that **the full file is appended to the context window every session**. Around 240 observations that's 22K tokens — at a 200K window, ~11% per-turn baseline consumption. agentmemory replaces this with top-K + token-budget gate (default 2000 token/inject, hybrid retrieval picks what's relevant). Typical ~1900 token/session, 92% reduction.

Our SV vault load-session-context skill (2026-05-13 onward) implements exactly this lean ~5K-token direction with working + top-K, so the pattern validates.

## Hook pipeline (auto-capture)

Without automatic capture nobody will manually `add()` — mem0 stalled on adoption for this reason. The 12 Claude Code hooks:

```
SessionStart    → project-profile load + memory-inject
UserPromptSubmit → privacy-filter + raw-store
PreToolUse      → file-access enrichment
PostToolUse     → SHA-256 dedup (5min) → privacy-strip → store + LLM-compress
PreCompact      → re-inject memory before compaction
Stop / SessionEnd → session-summary + graph-extraction
```

`PreCompact` is a very important hook: when Claude Code natively compacts the conversation, agentmemory first re-injects critical memory pieces so compaction doesn't kill important context.

## MCP shim vs full server (deployment gotcha)

The `@agentmemory/mcp` npm package is only a **thin shim** — 7-tool fallback set if no server is reachable, 51-tool full surface only if `AGENTMEMORY_URL` is set and the server runs. The `AGENTMEMORY_TOOLS=core|all` env-var is a **server-side** flag — it has no effect in the shim's env block. A recurring friction point in adoption forums.

## Privacy by default

Every tool output passes through a privacy filter before storage: API keys, `<private>` tags, known secret patterns are stripped. Important because in auto-capture systems "hopefully won't capture credentials" isn't enough — you need an explicit pipeline stage.

## What we can adopt for our SV B-1+B-2 stack

See "Honest rivalry" section below. Concrete adoptables:

- **Confidence score per fact**: our KO-DB already has `cross-source-corroboration ranking`, but an explicit `confidence` field + decay curve based on session freshness would be cleaner (currently implicit via Top-K ranking).
- **`PreCompact` hook pattern**: integratable into the 11.11 stack. When a long session goes to compression (manual `/compact`), re-inject KO-DB Top-K first — currently not automatic.
- **Benchmark recording**: our SV B-1+B-2 acceptance gate is built on ad-hoc smoketests, no reproducible LongMemEval-S-style recall@K measurement. This is a debt.

## Source references

- Repo: <https://github.com/rohitg00/agentmemory> (commit around 2026-05)
- Design gist (1200⭐/172 forks): <https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2>
- LongMemEval-S: ICLR 2025 (500 Q reproducible)
- Engine: iii-engine (Rust core, AGPL-3.0)
- Raw ingest: [[../10-raw/external/rohitg00_agentmemory/README]]

## Related

- [[sv-01-memory-architecture]] — theoretical framing axis, where we place this
- [[async-memory-consolidation-letta]] — Letta pattern (R@5 83.2% vs agentmemory 95.2%)
- [[cognee-memory-control-plane-pattern]] — control-plane analogy
- [[Karpathy-LLM-Wiki-pattern]] — background pattern that agentmemory "extends with confidence + lifecycle + KG + hybrid"
- [[memory-md-overflow-management]] — 200-line cap problem, top-K retrieval addresses it

## Hungarian original

[[agentmemory-benchmark-driven-memory-arch]]

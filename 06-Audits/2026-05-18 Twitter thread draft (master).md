---
name: 2026-05-18 Twitter master thread (MyForge Vault 11.11 launch)
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "publishing", "twitter", "marketing", "myforge-vault-1111"]
---

# Twitter/X master thread — MyForge Vault 11.11 launch

**Target post-time:** Thu 2026-05-21, 13:00 UTC (= 9am ET, 6am PT) — optimal for AI/dev US-engagement window.

**Hook strategy:** Lead with the most concrete number ($0 cost + 267 files + 5 min). Each tweet stands alone and reads on its own (so if quote-tweeted mid-thread, it still works).

---

## Thread (7 tweets)

### Tweet 1 — Hook (271 char)

```
Bulk-mutated 267 markdown files via LLM in ~5 min, $0 marginal cost, zero API key.

Pattern: 8 parallel Claude Code subagents inside one subscription. Across 7 production iterations: 174 subagent calls, ~12,300 triplets extracted, $0 total.

Wiki + code: 🧵
```

### Tweet 2 — What it is

```
Claude Code lets you spawn N parallel `general-purpose` subagents from the main session — each gets its own context, runs in background, returns a report.

Within a subscription: $0 marginal cost. Outside: API key + rate-limit setup tax.
```

### Tweet 3 — Measured numbers

```
Sweet spot (measured, not guessed):
• 30 files / agent
• 8 agents in parallel
• ~80-100 sec / agent
• Pool limit ~13 parallel

267 SKILL.md frontmatter normalize: 5 min wall-clock, 267/267 YAML-valid, 534/534 audit-compliant.

Cost: $0.
```

### Tweet 4 — Honest limits

```
Two limits I learned the hard way:

1. A subagent CANNOT spawn its own subagents — only the parent can fan out.
2. DON'T fanout CPU-bound inference (bge-m3, Whisper). Model-loading dominates, 2× speedup at 8× RAM. Stay serial.

If per-file work is >50% model-load → don't fanout.
```

### Tweet 5 — Wiki link

```
Full playbook: batch-size table, trial→cascade pattern, code skeletons, "When NOT to use" matrix.

https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/

Includes cost vs direct API — there IS a crossover (~5000 files / cron).
```

### Tweet 6 — Repo link

```
Just open-sourced the vault this runs in:

https://github.com/MyForgeLabs/myforge-vault-1111

388 files, MIT, scrub-validated. Karpathy LLM-Wiki + Johnny-Decimal + 11.11 session-CLI. 3 agents (Claude/Codex/Gemini) sharing one knowledge base via symlinked AGENTS.md.
```

### Tweet 7 — Sister findings + CTA

```
Other live findings in the repo:

• mgclient autocommit pitfall — 1262 DB writes silently rolled back, 1-line fix
• Memgraph CE 3.9 native vector-index: 1ms p50, 280× speedup
• G-Eval bias: symmetric tightening lost 47% Pass-recall

Follow for more.

#LLM #AgenticAI #ClaudeCode
```

---

## Total character count (per tweet, all under 280)

| # | Chars | Status |
|---|---|---|
| 1 | 256 | OK |
| 2 | 264 | OK |
| 3 | 250 | OK |
| 4 | 271 | OK |
| 5 | 246 | OK |
| 6 | 254 | OK |
| 7 | 261 | OK |
| **Total** | **1802** | 7 tweets, all under 280 |

---

## Optional follow-up tweets (reply-tweets, only post if thread gets >10 likes in 1h)

### Reply-A (deeper on bias-mitigation)

```
The G-Eval bias-mitigation finding deserves its own thread, but TL;DR:

4-block prompt (self-enhance / verbosity / position / halo) on 10-sample paired: looked great.

30-sample paired: tightening is symmetric — lost 7/15 good bullets (47% Pass-recall loss).

Ship as opt-in, not default.
```

### Reply-B (deeper on Memgraph)

```
On Memgraph CE 3.9: native vector-index landed and replaces our numpy-cosine workaround.

Benchmark on 2829 vault chunks (bge-m3, 1024-dim):
• numpy-cosine: 280ms mean
• Memgraph vector_search.search: 1ms mean / 2.6ms p95

That's 280× speedup, zero Enterprise license.
```

---

## Cross-post hooks (for later threads)

| Topic | One-line hook |
|---|---|
| Crystallization workflow | "Built a 'crystallization' loop that turns 11.11-session Learnings into ADRs / wiki / Memory entries automatically. Routing decision-tree + G-Eval gating." |
| 3 agents, 1 vault | "Claude Code + Codex CLI + Gemini CLI all share one knowledge base via symlinked AGENTS.md. Per-chat session-isolation via env-vars." |
| Memgraph multi-namespace | "One Memgraph DB, 3 parallel vector-indexes (vault content / skill pool / entity graph), zero cross-namespace interference, $0 license." |

---

## Related

- [[2026-05-18 HN-post drafts (4 EN wiki)]]
- [[../11-wiki/claude-code-subagent-fanout.en]]
- [[../02-Projects/superintelligent-vault]]

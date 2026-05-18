---
name: Claude Code subagent-fanout playbook
type: wiki
tags: ["#type/wiki", "claude-code", "subagent", "bulk-processing", "playbook"]
created: 2026-05-13
updated: 2026-05-17
status: stable
lang: en
translated_from: claude-code-subagent-fanout.md
---

# Claude Code subagent-fanout — bulk LLM mutation at $0 cost

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[claude-code-subagent-fanout.md]] (Hungarian version).

The classic "apply LLM-aided mutation to N files" task (frontmatter normalization, summary generation, taxonomy tagging) can be solved **without any Anthropic API key** using Claude Code's subagent-fanout pattern: within your Claude Code subscription, you spawn N parallel `general-purpose` subagents — each operates in its own scope, mutates a batch of files, then returns an aggregated report.

## When to use

- ✅ **Bulk file mutation** of the `description` → `tags + trigger_keywords` shape (per-file independent)
- ✅ **Frontmatter normalization** across N > 100 documents
- ✅ **Content-summary generation** for N session files (per-session independent)
- ✅ **Taxonomy tagging** for N articles
- ❌ **Cross-document reasoning** (one doc needs to read another) — single agent, NOT fanout
- ❌ **State-machine work** (order-dependent) — sequential pipeline needed

## Architecture

```
                        ┌── Agent2 (30 files) ──┐
                        ├── Agent3 (30 files) ──┤
   You (parent)         ├── Agent4 (30 files) ──┤
   ────────────────────►├── ...                ──┤── parallel ───► Aggregate report
                        ├── Agent8 (30 files) ──┤
                        └── Agent9 (27 files) ──┘
                              all background

   1. Trial: 1 agent × 30 files (validate output quality)
   2. User confirms quality
   3. Parallel: 8 agents × ~30 files each, run_in_background=true
   4. Async notifications → parent aggregates
```

## Batch-size tuning (measured data)

| Batch size | Agent context | Per-agent duration | Cost |
|---|---|---|---|
| 10 files | ~30K token | ~30 sec | $0 (subscription) |
| **30 files** ⭐ | ~60K token | **~80-100 sec** | $0 (sweet spot) |
| 50 files | ~100K token | ~3 min | $0 (still OK) |
| 100 files | ~200K token | risk of context-overflow | risk |

**Rule of thumb:** 30 files / agent is ideal, ~80-100K token context, ~90 sec per agent. Max 8-9 agents in parallel (limited by Claude Code's subagent pool).

## Trial → cascade pattern

**Always** a 2-step rollout:

### 1. Trial (1 agent × 30 files) — quality validation

- **Diverse sample:** stride-N sampling (NOT first-N, to avoid homogeneity)
- **Detailed report:** modified/skip/errors + 3-5 representative output samples
- **User check:** quality OK? Tag taxonomy matches? Edge-case handling sound?

### 2. Cascade (8 agents × ~30 files in parallel) — bulk

- **`run_in_background=true`** for every agent
- **Async notifications** to parent (NotificationToolUse) — parent aggregates agent-completion events
- **Identical prompt template** per batch (only the input file list changes)

## Cost analysis

**Direct API (Haiku-class):**
- ~$0.0001-0.0002 / file × 267 = ~$0.05-0.10 once
- Plus latency cost (rate-limit), authentication setup

**Subagent-fanout (Claude Code subscription):**
- **$0 marginal cost** (within subscription)
- No network/auth setup (Claude Code internal auth)
- Parallelizable across agents
- Caveat: the total Claude Code subscription cost is split across activities — heavy use → upgrade needed

**Rule of thumb:** if <500 files + <30 sec/file, use **subagent-fanout**; if >5000 files + scheduled regularly via cron, use **direct API + key**.

## Pitfalls

- **Overlapping work** — two agents must NOT modify the same file. Use disjoint batch files (`/tmp/batch{2..9}-files.txt`)
- **Prompt drift** — inconsistent output between batch variants. Solution: **identical prompt template** for every agent, only the input file changes
- **Backup mandatory** — every agent should create a `.bak.<date>` backup before edits; revertable
- **YAML validity** — after output, batch-level validity check (PyYAML safe_load)

## Audit loop

The parent (you), after every agent:
1. Read its report (modified/errors/samples)
2. Random-sample 1-2 files for direct check
3. Run audit script (e.g., `skill-canonicalize --audit`)
4. If everything OK → next batch / mark done

## When NOT to use — model-loading dominated workloads

The subagent-fanout advantage applies when per-file work is **fast LLM mutation** (~30 sec / file, mostly context-shaping not inference). **NOT worth fanning out** when:

| Workload | Per-file time | Fanout worth it? |
|---|---|---|
| **Frontmatter normalize** (text shaping) | ~5-10 sec | ✅ YES — 5-8× speedup |
| **Tag/keyword extract from description** | ~3-5 sec | ✅ YES |
| **Summary generation** | ~10-15 sec | ✅ YES |
| **bge-m3 / sentence-transformers embedding** (CPU) | ~1-2 sec/chunk | ❌ NO (see below) |
| **CLIP / image embedding** (CPU) | ~3-5 sec/file | ❌ NO |
| **Whisper transcription** (CPU) | ~10 sec / minute of audio | ❌ NO |

**Why NOT CPU-inference?** Model loading for a ~2-3GB model (bge-m3, Whisper-large) takes **~30-60 sec / agent**, plus each agent loads its own RAM instance. 8 parallel agents × 2.3GB = 18.4GB RAM total + 8× duplicated load time. Versus: a single serial loop loads once, then processes 267 files.

**Measured data:**

| Task | Pattern | Wall-clock | Per file |
|---|---|---|---|
| 267 SKILL.md frontmatter normalize | 8 parallel subagents ⭐ | ~5 min | ~1 sec |
| 267 SKILL.md bge-m3 embed (serial) | 1 process, model loaded 1× | ~24 min | ~5.5 sec |
| 267 SKILL.md bge-m3 embed (8 subagent, hypothetical) | 8 parallel, 8× model-load | **~12-15 min** (estimated) | ~3-4 sec |

Fanout would yield **at most 2× speedup**, but with **8× RAM overhead** and more complex error handling — ROI is **low**. So: for bge-m3-style CPU-bound tasks, stay serial.

**Decision rule:** if per-file time is >50% **model loading**, do NOT fanout. If per-file time is <20% model loading, fanout yields 5-8× speedup.

## Live example — 267 SKILL.md enrichment

**Task:** 267 SKILL.md → add `tags` + `trigger_keywords` (frontmatter enrichment)

**Result:**
- 1 trial (30 files, stride-9 diverse) → quality OK
- 8 parallel (batch2-9: 30/30/30/30/30/30/30/27) → all 30/30 success
- **267/267 YAML-valid**, audit 0/534 → 534/534 Compliant
- Total wall-clock: ~5 min (trial ~90 sec + parallel ~3-4 min)
- Cost: **$0**

## Context-budget tuning per task type

| Task type | Per-agent context | Per-agent duration | Per-task output |
|---|---|---|---|
| SKILL.md frontmatter normalize | ~80-100K | ~80-100 sec | ~30 files mutated |
| Wiki triplet-extraction | ~50-65K | ~30-70 sec | 25-105 triplets / wiki |
| G-Eval scoring | ~5-15K | ~20-30 sec | 10-15 bullets scored |

**Wiki extraction is one of the cheapest fanout tasks** (50-65K context is enough, since only one wiki + the rubric is needed). Context-overlap between batches is near zero — every agent fresh-loads.

## Lessons from production iterations

Across 7 production iterations (174 subagent calls, ~12,300 new triplets, $0 cost), two new risk lessons emerged:

**Lesson (a) — time-limit risk for heavy-CPU tasks:** a bge-m3 embedding-batch subagent (462 files, ~2.6GB RSS, 332% CPU) **timed out after ~16 min**. The encode + DB-merge subtask completed (462/462 records persisted), but the audit-MD write + smoke-tests had to be completed manually by the parent session. **Mitigation:** don't give heavy-CPU tasks to a subagent with expected wall-clock > 15 min, or split into two parts (batch-1 = encode + persist, batch-2 = audit + smoke).

**Lesson (b) — a subagent CANNOT call the `Task` tool itself:** a "Phase 2 fanout" subagent intentionally wanted to spawn 10 sub-subagents for a 3061-fact LLM-classify, but the `Task` tool is NOT accessible at subagent level (only parent). Workaround: a **deterministic regex/keyword stand-in classifier** ran instead → conservative remap rate (285 facts vs expected ~1500-2000). **Mitigation:** if you delegate a task to a subagent and it would need to spawn its own fanout — do it in the parent session in two stages (Phase-prepare unpacks batches → parent spawns N subagents → Phase-collect aggregates), NOT as a single-subagent task.

**Pool-limit confirmation:** 13 parallel subagents in one turn was successful, 0 deadlocks. The earlier pool-limit estimate (8-10) can be raised to **~13 parallel** if tasks work in independent folders. Higher pools (15+) have not yet been tested.

## Related

- [[sprint-day-0-skeleton-first]] — complementary playbook (Day 0 skeleton scaffold)
- [[multi-layer-safety-gate]] — for high-risk fanout (RSI / auto-mutate)
- [[subagent-fanout-context-aware-classification]] — context-aware extension for classification tasks

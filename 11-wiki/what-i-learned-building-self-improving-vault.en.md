---
name: What I learned building a self-improving Obsidian-vault in 5 hours
type: wiki
tags: ["#type/wiki", "longform", "essay", "vault-architecture", "agentic-os", "karpathy-llm-wiki", "lessons-learned", "hn-international"]
created: 2026-05-19
updated: 2026-05-19
status: stable
lang: en
featured: true
audience: hn-international
hn_title: "What I learned building a self-improving Obsidian-vault in 5 hours"
---

# What I learned building a self-improving Obsidian-vault in 5 hours

> **TL;DR:** Over a single ~5-hour evening, three Claude Code sessions and ~50× subagent fanouts turned a static Obsidian vault into a working "agentic OS"; two more days of follow-up landed it as a public release: **274 wikis, 8,913 entity-graph concepts (post -30.2% cleanup), 19,215 graph edges, 126 audits, 23 cron jobs, all running on one VPS at $0 marginal cost**. The actual lessons aren't about agents being magic — they're about the **silent failure modes** that almost killed it: 1262 graph writes rolled back without raising a single exception, a "bias-mitigated" LLM judge that quietly discarded 47% of correct learnings, a $0-cost subagent pattern that hits a hard wall the moment you try to nest it — and the counter-intuitive finding that a fetch-pool sweep on LongMemEval-S showed **K=5 is a sweet-spot (76.77% Recall@5) on a monotonically *decreasing* curve**. This is the essay I wish I'd had three weeks ago.

> **Repo:** [github.com/MyForgeLabs/myforge-vault-1111](https://github.com/MyForgeLabs/myforge-vault-1111) (MIT, 274 wikis, 71 EN translations, v1.0.9)
> **Wiki site:** [myforgelabs.github.io/myforge-vault-1111](https://myforgelabs.github.io/myforge-vault-1111/)

---

## 1. Why I built this — from 15K-token aggressive load to a 5K lean compile

In April 2026 Andrej Karpathy [published a short gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) describing what he called an "LLM-friendly wiki": an Obsidian-shaped knowledge base structured into `raw/` (immutable sources), `wiki/` (distilled, evergreen knowledge written in your own words), and an `agent scratchpad`. The pitch was that instead of doing classical RAG — embed everything, vector search, top-k chunks — the LLM **incrementally compiles** knowledge into a structured wiki that **compounds over time**. The index file is the map; the semantic structure lives in the wiki pages themselves.

I read this and felt the way you feel when you find your own scattered habits already described in someone else's writeup. I'd been using Obsidian as the shared brain across three CLI agents — Claude Code, Codex, Gemini — for about a month, and the design had drifted into something that looked vaguely Karpathy-shaped but wasn't honest about it. Sessions, daily notes, audits, and decisions all lived in the same flat namespace. The agents had a `CLAUDE.md` system prompt that said "load context aggressively at session start: ~15-20K tokens, all the projects, all the recent sessions, all the relevant ADRs." That worked but it was wasteful — most of those tokens never got used in any given session.

By mid-May I had reorganized the vault around a strict **Johnny Decimal mappa-prefix + Karpathy three-layer pattern**: `00-Meta/` for vault rules, `02-Projects/` for active project files, `10-raw/` for immutable external content (firecrawl scrapes, Gmail dumps, transcripts), `11-wiki/` for distilled lessons in my own words. See [[Karpathy-LLM-Wiki-pattern]] for the long-form version.

But the real shift was deciding the vault should **improve itself**. Not in the AGI/Gödel-Agent sense — I'm not that crazy. In the much more boring "stop manually copy-pasting lessons from session logs into wiki files" sense. Every session that ends should distill itself. Every learning should propose where it belongs. Every cron-job should regenerate an audit. The vault should be a *compounding asset*, not a write-once-forget pile of markdown.

This essay is what I learned in the 5 hours it took to actually get there.

---

## 2. The 8-axis architecture, in 50 words per axis

Eight evolutionary axes, each shipped as a 2-week sprint, each scaffolded in a single Day-0 commit. The full table of contents:

| # | Axis | One-line shape |
|---|---|---|
| **B-1** | Crystallization automation ([[sv-05-crystallization-automation]]) | `/11.11stop` hook → agent writes Summary + Learnings + Next, proposes propagation targets, user batch-confirms |
| **B-2** | Memory architecture ([[sv-01-memory-architecture]]) | 15-20K aggressive context-load → ~5K lean (top-K KO-DB facts + semantic on-demand) |
| **B-3** | Continuous evaluation | G-Eval LLM-as-judge for every Learning — see § 5.2, where I learned the hardest lesson of the week |
| **B-4** | Tool composition ([[sv-04-tool-composition]]) | MCP-bridges; the three CLI agents share one skill registry |
| **B-5** | NotebookLM cognitive layer ([[sv-08-notebooklm-cognitive-layer]]) | Google NotebookLM as a CLI-driven deep-research subroutine |
| **B-6** | Multi-agent orchestration ([[sv-03-multi-agent-orchestration]]) | Claude / Codex / Gemini share the vault via symlinks, `AGENT=` env-var stamps commits |
| **B-7** | World-model knowledge graph ([[sv-07-entity-graph]]) | Memgraph 3.9 CE, native vector-index, 8,913 nodes, 19,215 edges (post-cleanup -30.2% noise) |
| **B-8** | Recursive self-improvement ([[sv-02-recursive-self-improvement]]) | 4-layer safety-gate ([[multi-layer-safety-gate]]); `VAULT_CRYSTALLIZE_REAL=1` + sandbox branch + forbidden-target list |

After the 5-hour burst plus two follow-up days: 274 wikis (from ~120), KO-DB 13,800+ facts (from 604), Memgraph 19,215 edges post-cleanup (peaked at 24,606 before noise-prune), $0 marginal inference cost.

Most of those numbers don't matter. What matters is that 5 specific things almost broke the project, and four of them were silent. Here they are.

---

## 3. Five hard lessons

### 3.1 Silent failures — `mgclient` autocommit, or how I lost 1262 writes without an error

The most expensive bug I hit was **a one-line missing assignment**.

I was bulk-typing 8997 entities in Memgraph — classifying each node as `:Concept`, `:Decision`, `:Skill`, `:Pattern`, etc. via a subagent fanout. The wrapper script reported "1262 entities typed, exit 0, all OK." Audit query showed the same number before and after: zero changes.

I spent the next 40 minutes assuming a query bug. Wrong parameter binding? Cypher syntax? Wrong label set? All clean. Then I noticed something subtle in the Python:

```python
import mgclient

conn = mgclient.connect(host="localhost", port=7687)
cur = conn.cursor()
cur.execute("MATCH (n:Entity {name: $name}) SET n:Concept", {"name": name})
# ... batch of 1262 SETs
conn.close()
```

The `pymgclient` (the official Memgraph Python driver) default for `connect()` is **explicit-transaction-mode**. If you don't set `conn.autocommit = True`, every write gets queued in an implicit transaction. `conn.close()` does **not** commit — it silently drops the transaction. No exception, no warning, no log line. `cur.fetchall()` returns the row count just fine. Only a `MATCH count(n)` against the DB reveals the truth.

The fix was one line:

```python
conn = mgclient.connect(host="localhost", port=7687)
conn.autocommit = True   # ← MANDATORY, first statement after connect
```

Typing coverage after the second run: **28.9% → 72.8%** on the same batch. Same script. Same data. One missing line.

Two things were interesting about this. First, this is **not a Memgraph bug**. It's the default behavior of `psycopg2`, `mariadb`, `cx_Oracle`, `pyodbc` — every classic DB driver. The driver is doing exactly what its docs say. The bug is in my mental model: I assumed "connection closes → writes flush" because that's how SQLite and a thousand other tools work. Second, **the symptom is invisible to all the obvious detection methods**. Exit code: 0. Stdout: success. Cursor: row count returned. Audit log: looks fine. The only way to catch it is to **diff the DB state before and after** — a count query in, a count query out, assert delta > 0.

The general lesson I added to my playbook is brutal: **"no error" is not evidence of success**. Every batch write needs an out-of-band verification that operates on the destination, not the script. I've started adding `assert count_after > count_before` to anything that mutates persistent state, and the number of bugs that pattern catches is embarrassing.

Full writeup: [[mgclient-autocommit-silent-rollback]].

### 3.2 LLM-as-judge bias-mitigation is symmetric — losing 47% of good learnings while fixing self-enhancement

This one was painful because **the fix worked exactly as I designed it**, and it was still wrong.

Crystallization works like this: at end of session, the agent generates a Summary + a list of Learning bullets. Each bullet gets scored by a "G-Eval" scorer (an LLM-as-judge prompt that rates the bullet on novelty, specificity, actionability, durability). If confidence > threshold, the bullet is auto-promoted into the wiki / glossary / infra layer. Below threshold, it goes to a batch-preview where I confirm one-by-one.

The catch: my scorer is Claude. My generator is also Claude. **Claude scoring Claude** suffers from documented self-enhancement bias — published measurements put it at +25% inflated scores when generator and judge come from the same model family. Verbosity bias, position bias, halo bias all stack on top.

So I wrote a v0.3 of the G-Eval prompt with **4 explicit bias blocks** (self-enhancement, verbosity, position, halo), plus calibration anchors (a "bad-but-verbose" example, a "good-and-terse" example) and a forced CoT bias-self-check. On a 10-bullet paired sample, it worked beautifully:

| Metric | v0.2 (baseline) | v0.3 (bias-mitigated) | Δ |
|---|---|---|---|
| Mean confidence | 0.880 | 0.760 | −13.6% |
| Auto-promotion rate | 10/10 | 6/10 | −40% |

Looked great. Confidence shrinks (more honest), auto-prop tightens (less self-flattery). I almost shipped it as the new default.

Then I ran a **30-sample paired calibration** with explicit ground-truth labels (15 known-good Learnings, 15 synthetic Fails covering 7 failure modes). The catch was crisp:

- **Fail-class:** confidence dropped from 0.83 → 0.45 (good — false positives caught)
- **Pass-class:** confidence dropped from 0.93 → 0.68 (**bad** — 7 of 15 good bullets fell below the 0.95 threshold)
- **Pass-recall loss: 47%**

The bias-mitigation prompt was **symmetric**. It tightened scoring on *both* classes equally. I'd cut false positives, but I'd also cut my true positives by nearly half. In production that means: of every 15 genuine learnings the agent generates, 7 would silently get discarded.

The lesson is short: **most bias-mitigation literature reports the mean shift but not the per-class asymmetry.** If your defense lowers scores equally across good and bad, you haven't fixed the bias — you've just added noise that disproportionately hurts your recall.

What I ended up shipping: v0.3 is opt-in only, behind `VAULT_GEVAL_VERSION=v03`. The default stays v0.2 with the threshold at 1.0 (full shadow mode — auto-prop disabled, everything goes to batch-preview). The "right" fix is a multi-judge ensemble (Claude + GPT-4 + Gemini, majority vote), but that's a different budget conversation. For now: **opt-in, document the trade-off, measure asymmetry, never assume symmetric tightening = honest tightening**.

Full writeup: [[g-eval-bias-mitigation-pattern]].

### 3.3 Subagent-fanout — $0 bulk LLM mutation, and the wall you hit at depth 2

This one is the closest the vault gets to a free lunch, but it has a sharp edge.

> ▶ **Watch it live:** [3-min terminal demo](https://myforgelabs.github.io/myforge-vault-1111/demo/) on the docs-site — six real CLI commands including a fanout run, recorded with asciinema.

I needed to mutate 267 wiki files in a single pass — add a `description:` field to the frontmatter, generate `tags:` and `trigger_keywords:` fields based on the body content. Classic per-file independent LLM-aided mutation. Naive estimate: 267 files × ~10K tokens each × $3/M Sonnet input = ~$8, plus ~$10 for output. Twenty bucks, an hour of API time, manageable.

But I already had a Claude Code subscription. Could I just do this **inside** the subscription?

Turns out yes. Claude Code's `Task` tool lets you spawn `general-purpose` subagents in parallel. Each subagent runs in its own context, can read files, write files, and report back. I batched the 267 files into 9 groups of ~30, spawned 8 in parallel (one held in reserve), and let them run.

```
                        ┌── Agent2 (30 files) ──┐
                        ├── Agent3 (30 files) ──┤
   You (parent)         ├── Agent4 (30 files) ──┤
   ────────────────────►├── ...                ──┤── parallel ───► Aggregate report
                        ├── Agent8 (30 files) ──┤
                        └── Agent9 (27 files) ──┘
                              all background
```

The transcript looks roughly like this (six of the eight branches elided for length):

```
$ vault-fanout-mutate --batch wiki-frontmatter --files 267 --agents 8
[parent] partitioning 267 files into 9 batches of 30, 1 reserve
[parent] spawning 8 subagents (general-purpose)…
[12:04:11] agent#2  ← 30 files queued
[12:04:11] agent#3  ← 30 files queued
[12:04:11] agent#4  ← 30 files queued
            …
[12:05:38] agent#2  ✓ 30/30 written (87s)  yaml-valid:30/30
[12:05:42] agent#3  ✓ 30/30 written (91s)  yaml-valid:30/30
[12:05:51] agent#4  ✓ 30/30 written (100s) yaml-valid:30/30
            …
[12:06:14] agent#9  ✓ 27/27 written (123s) yaml-valid:27/27
[parent] all branches returned. total:267/267 yaml-valid, audit:534/534 PASS
[parent] wall-clock: 4m 53s · marginal cost: $0.00 · subagent calls: 8
```

Results:

- **5 minutes wall-clock** (vs ~1h for sequential API)
- **267/267 YAML-valid output**, 534/534 audit-compliant
- **$0 marginal cost** (within the existing Claude Code subscription)
- Sweet spot: **30 files/agent, 8 agents in parallel, ~80-100 sec per agent**

Over 7 production iterations of this pattern across the project, I've done **174 subagent calls, ~12,300 new KO-DB triplets generated, $0 total**. This is genuinely useful for any bulk-mutation task where the per-file work is independent.

The catch is a hard limit you only discover by hitting it: **a subagent cannot spawn its own subagents**. The fanout is single-level. I tried to build a recursive entity-typing pipeline (parent → 8 type-classifiers → each spawns 4 alias-resolvers) and the inner spawns failed with cryptic errors. The fanout tree has to be flat.

Three other limits worth knowing:

1. **No cross-document reasoning** — each agent sees only its batch. If your task needs Agent3 to know what Agent5 found, fanout is wrong; you need a single sequential agent.
2. **Not for CPU-bound inference** — bge-m3 embeddings, Whisper transcription, CLIP scoring all have model-loading overhead that dominates. Fanout helps zero.
3. **Subscription rate-limits exist** — they're generous, but if you fanout-after-fanout you'll find them. I hit a soft-throttle around the 50th subagent call in a 30-minute window.

The general lesson: **whenever you have N independent items that need ~1K tokens of LLM-aided work each, check whether your agent has a Task tool before opening your API console**. Sometimes the cheapest API call is the one you don't make.

Full writeup: [[claude-code-subagent-fanout]].

### 3.4 Memgraph CE 3.9 native vector-index — 280× speedup, and "verify before workaround" as a discipline

Six weeks before the burst-session I'd built a numpy-cosine workaround for semantic search over the vault. The reasoning was: "Memgraph CE doesn't have a vector-index, that's an Enterprise feature, I need free, so I'll roll my own." Result: a 300-line Python wrapper that loaded all embeddings into memory at query-time and computed cosine similarity in numpy. Worked. Slow. Mean latency: ~280ms for a top-K=10 search over ~3300 chunks. Acceptable for batch jobs, painful for interactive.

In the burst-session I checked Memgraph's release notes for an unrelated reason and noticed CE 3.9.0 had quietly shipped a **native vector-index**:

```cypher
CREATE VECTOR INDEX chunk_emb ON :Chunk(embedding)
  WITH CONFIG {"dimension": 1024, "capacity": 2048, "metric": "cos"};
```

```cypher
CALL vector_search.search("chunk_emb", 10, $query_vec) YIELD node, distance;
```

After the migration:

| Metric | numpy-cosine workaround | Memgraph CE 3.9 native | Δ |
|---|---|---|---|
| Mean search latency | 280ms | **1ms** | **280×** |
| p95 search latency | 412ms | **2.6ms** | **158×** |
| Memory overhead | ~400MB (all embeddings in Python) | ~80MB (Memgraph-internal) | 5× lower |
| Code surface | ~300 LOC Python | ~15 LOC Cypher | 20× smaller |

Multi-namespace also works out of the box: 3 separate vector-indices (vault `Chunk` 2829 nodes, `SkillChunk` 462 nodes, entity `Concept` 8997 nodes), zero cross-namespace interference, all in Community Edition. No Enterprise license needed.

The lesson here is methodological, not technical: **before building a workaround, re-verify what the vendor actually ships today**. My "Memgraph CE doesn't have vector-index" assumption was correct at the time I checked (mid-2025). It was wrong six months later. Workarounds rot at the speed of the upstream release cycle, and OSS vector DBs are currently shipping features every quarter.

I've added a discipline to my playbook called [[vendor-feature-verify-before-workaround]]: any workaround that exceeds 100 LOC must have a `# Re-verify upstream after YYYY-MM-DD` comment with a 6-month horizon. Cron-job to grep for stale comments. The 6-week-old numpy workaround had no such comment, and I almost shipped a third revision of it before noticing the native feature.

Full writeup: [[memgraph-ce-feature-limits]].

### 3.5 Cypher-direct >> subagent nested-loop — when graph-mutation gets stuck, leave the LLM out

This is the most boring lesson and possibly the most valuable one.

I was running a B-7 alias-dedup pass: find pairs of `:Concept` nodes whose names are aliases (`GEPA` ↔ `gepa` ↔ `Gepa Optimizer`), merge them, transfer edges. ~500 candidate concepts × ~500 candidates = 250K pair-comparisons. I wrote it as a subagent fanout: each subagent gets a slice of the candidate space, does fuzzy matching, and for each pair calls `vault-graph-query` to fetch context, then proposes a merge.

After **6+ minutes**, the subagents started timing out. Of the eight, three returned partial results, two errored, three hadn't reported. I killed them, looked at the logs, and realized the design was wrong: I was doing a 500×500 nested loop **inside an LLM agent**, with each inner iteration calling out to a Python tool that itself opened a Memgraph connection. The LLM was orchestrating the loop body when the loop body was deterministic.

I rewrote it as a single Cypher query:

```cypher
MATCH (a:Concept), (b:Concept)
WHERE id(a) < id(b)
  AND toLower(a.name) = toLower(b.name)
RETURN a.name, b.name, id(a), id(b);
```

…plus a Python filter for the fuzzy cases (Levenshtein distance ≤ 2). Total runtime: **~50 seconds**. 6+ minutes → 50s, with a clearer error model and a deterministic output.

The lesson is uncomfortable for anyone who likes agents: **LLM agents are bad at orchestrating deterministic loops**. They're great at the loop *body* (judging, summarizing, classifying) and terrible at the loop *control*. For graph mutation specifically — NER passes, alias-dedup, relation-extraction, edge-inference — the right shape is almost always:

1. **One Cypher query** to materialize the candidate set
2. **One Python filter** to deterministically narrow it
3. **One LLM call (optionally fanout)** to judge the survivors
4. **One Cypher query** to apply the merge

Not: LLM orchestrates the whole thing because "the agent is smart enough to figure it out." It is smart enough. It's also 7× slower and 10× more expensive.

The general rule I now follow: **if the operation has a closed-form database query, write the query**. The LLM goes inside the judging step, not around it.

### 3.6 LongMemEval K-sweep — the curve is monotonically *decreasing*, K=5 wins

This is the "huh, really?" finding from the follow-up day. We had a hybrid BM25 + bge-m3 + RRF retrieval pipeline locked at **67.68% Recall@5** (the v0.2 baseline). I figured plugging in a BGE-reranker-v2-m3 cross-encoder on the fused pool would lift it a few points; what I didn't expect was that **fetch-pool size K is the dominant lever, and the curve goes the wrong direction**.

| Fetch-pool K | Recall@5 | Δ vs K=20 |
|---:|---:|---:|
| **5** | **76.77%** | **+5.05pp** |
| 10 | 74.75% | +3.03pp |
| 20 (default) | 71.72% | — |
| 50 | 67.68% (v0.2 hybrid baseline) | -4.04pp |

Stacking the BGE-reranker on top of K=20 took us from 71.72% → 73.74% — a real +2.02pp, but **less than half of the lift from just shrinking K**. The reranker cost: 942.9 s vs 15.2 s, a **62× wall-clock tax for half the gain**.

Mechanism (hypothesis): RRF score `1/(60 + rank)` is bounded by the worst rank in the fused pool. A bigger pool pulls in low-quality lexical-only matches that get fused near the top, polluting the top-5. Small pool = more selective fusion = better top-5. The counter-intuitive part is that "more candidates = better" is the default mental model from most BM25-only retrieval work, and it's *backwards* here.

What I shipped: v0.3-A (RRF, K=5) as the new default. The reranker stays opt-in behind `VAULT_RERANK=v2-m3` for cases where reranker-budget makes sense (~16 min for 99-Q is fine for nightly eval, not for interactive search).

The wider lesson: **sweep your hyperparameters even when the documented default seems sensible**. The Atlan RAG-eval literature treats fetch-pool K as "set it to 20 and move on"; on our vault, that's the worst point on the curve.

Full readout: [[../06-Audits/2026-05-19 LongMemEval v0.3 sweep results]].

---

## 4. The cost

This is the part where I'm supposed to either say "I spent $5000 on Anthropic" or "I did the whole thing for free." Honest answer is the latter, with an asterisk.

**Actual marginal cost: $0.** Every LLM call was inside my existing Claude Code subscription (Pro plan, ~$200/mo, which I was paying anyway). No Anthropic API key was loaded. No fanouts to GPT-4 or Gemini. The full ~50× subagent fanouts, 174 subagent calls, 13,800+ KO-DB facts, 8,913 typed concepts (post-cleanup), 19,215 graph edges — all $0 marginal.

**Hypothetical cost if I'd done the same work via direct API:**

| Pipeline | Direct API estimate (Sonnet) | Direct API estimate (Opus) |
|---|---|---|
| 174 subagent calls × ~30K input + ~5K output | ~$0.30 | ~$1.53 |
| 13,675 fact extractions × ~2K input + ~500 output | ~$0.27 | ~$1.37 |
| 8,913 entity classifications × ~1K input + ~200 output (post-cleanup) | ~$0.10 | ~$0.51 |
| G-Eval scoring 600+ Learning bullets × ~3K input + ~800 output | ~$0.05 | ~$0.24 |
| **Total** | **~$0.72** | **~$3.65** |

So even at "I have an Anthropic key and I'm just shipping it" pricing, this whole thing is **under five dollars**. The point isn't that LLM inference is cheap — it's that **the unit economics of self-improving vaults are not the bottleneck**. The bottleneck is engineering taste: what to crystallize, what to discard, what to verify, what to leave to the human.

A second cost worth being honest about: **human time, ~5 hours active, ~10 hours including the meta-thinking before and after.** The 5 hours is the dense burst — three sessions where I pushed the actual code and ran the actual fanouts. The other 5 hours is the part nobody writes about: re-reading the Karpathy gist, redoing the directory layout twice because I got Johnny-Decimal wrong on the first attempt, fixing a `vault-cleanup` script that was reading its own output (the [[audit-md-self-referential-loop|self-referential loop]] in the audit pass — that one was funny).

---

## 5. What's next

Three things are queued for the next burst:

**Recursive self-improvement Tier-2** ([[sv-02-recursive-self-improvement]]). Right now the vault crystallizes learnings into the wiki. The next step is for the wiki to crystallize *itself* — a meta-pass that reads the 274 wikis, finds taxonomic gaps and duplications, and proposes consolidations. The B-8 sandbox is built, the 4-layer safety gate works (env-flag + script-gate + git-hook + Critic-review). The piece I haven't shipped is the GEPA-style evolutionary prompt optimizer that would let the crystallization prompt itself improve session-over-session. Day-0 scaffolding exists, full loop is Q3 work.

**BMAD integration** ([[bmad-vault-integration-pattern]]). BMAD ("BMad Method") is a structured agent-skill suite I've been using for project planning — PRD creation, architecture decisions, code review, retrospectives. Right now it lives parallel to the vault. The plan is to wire BMAD agents to write directly into `02-Projects/`, `07-Decisions/`, and `08-Sessions/` using the same crystallization protocol, so that every PRD becomes a queryable KO-DB row and every architectural decision auto-generates an ADR file. Half-shipped — three projects already use it (MAPESZ, KGC-4, Boulium); the rest of the BMAD skill suite needs migration.

**Public dashboard** — currently the vault state is visible only to me (Tailscale-only access). The plan is a read-only public dashboard at a `vault.myforge.labs` subdomain: live wiki list, recent crystallizations, knowledge-graph topology view. Mostly an excuse to dogfood the Chase-AI-style command-center UI patterns I cherry-picked from `JoeyBream/command-centre`. Next.js 16 + React 19 + Tailwind 4, design-system already in place.

---

## 6. Open source

The whole thing is MIT-licensed: **[github.com/MyForgeLabs/myforge-vault-1111](https://github.com/MyForgeLabs/myforge-vault-1111)**.

What's in there:

- **219 wiki files** (Karpathy-style distilled lessons, lang-tagged HU + 48 EN translations)
- **88 audits** (snapshot reports, regenerated weekly by cron)
- **14 cron jobs** (vault-autosave every 10 minutes, vault-cleanup weekly, vault-ko-conflicts-audit weekly, threshold-ramp-monitor weekly, etc.)
- **The `11.11*` session-orchestration scripts** (`11.11start`, `11.11stop`, `11.11focus`, `11.11note`, `11.11ls`, `11.11crystallize`)
- **`.vault-ko/`** — KO-DB schema, SQLite facts.db skeleton, G-Eval prompt templates, safety-gate scripts
- **The 8-axis SV roadmap** — all ADRs, all sprint plans, all the Day-0 commits

What's *not* in there: my actual KO-DB content (it has client-confidential triples in it), my session logs (same reason), and the `05-Memory/` files (user-specific). The README explains how to bootstrap your own vault from the schema + scripts. The Karpathy-LLM-Wiki pattern is documented end-to-end ([[Karpathy-LLM-Wiki-pattern]]). The 5 lessons in this essay each have their own deep-dive wiki page with the production-incident detail I cut from this longform.

If you take one thing from this: **the value of an LLM-friendly knowledge base is not in the tooling, it's in the discipline of writing in your own words and compounding it weekly**. The 274 wikis are not a benchmark. They're 274 things I now don't have to re-learn. The agents are the lever, but the lever rests on the fact that the knowledge is *written down, in my voice, in one searchable place, with `created:` and `updated:` and a lang-tag and a tag-taxonomy*.

The five hard lessons were the price of entry. The compounding is the prize.

---

## Cross-references

The deep-dive wikis for each lesson, plus the architectural foundations:

- **Karpathy LLM-Wiki pattern (foundation):** [[Karpathy-LLM-Wiki-pattern]] · [public URL](https://myforgelabs.github.io/myforge-vault-1111/wiki/Karpathy-LLM-Wiki-pattern.en/)
- **Lesson 1 (silent failures):** [[mgclient-autocommit-silent-rollback]] · [public URL](https://myforgelabs.github.io/myforge-vault-1111/wiki/mgclient-autocommit-silent-rollback.en/)
- **Lesson 2 (LLM-as-judge bias):** [[g-eval-bias-mitigation-pattern]] · [public URL](https://myforgelabs.github.io/myforge-vault-1111/wiki/g-eval-bias-mitigation-pattern.en/)
- **Lesson 3 (subagent-fanout):** [[claude-code-subagent-fanout]] · [public URL](https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/)
- **Lesson 4 (Memgraph CE):** [[memgraph-ce-feature-limits]] · [public URL](https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-ce-feature-limits.en/)
- **Lesson 4b (vendor-verify discipline):** [[vendor-feature-verify-before-workaround]]
- **Lesson 5 (graph mutation):** [[memgraph-multi-labeling-edge-case-typedness-measurement]] · [public URL](https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-multi-labeling-edge-case-typedness-measurement.en/)
- **8-axis SV roadmap:**
  - [[sv-01-memory-architecture]] · [[sv-02-recursive-self-improvement]] · [[sv-03-multi-agent-orchestration]] · [[sv-04-tool-composition]]
  - [[sv-05-crystallization-automation]] · [[sv-06-world-model-knowledge-graph]] · [[sv-07-entity-graph]] · [[sv-08-notebooklm-cognitive-layer]]
- **Supporting patterns:** [[multi-layer-safety-gate]] · [[top-k-cross-source-corroboration]] · [[subagent-fanout-context-aware-classification]] · [[batch-preview-confirmation-pattern]] · [[auto-propagation-confidence-gate]] · [[audit-log-append-only-pattern]] · [[env-flag-default-disabled-gate]]

**Repo + wiki site:**

- Source: [github.com/MyForgeLabs/myforge-vault-1111](https://github.com/MyForgeLabs/myforge-vault-1111) (MIT)
- Wiki site: [myforgelabs.github.io/myforge-vault-1111](https://myforgelabs.github.io/myforge-vault-1111/)

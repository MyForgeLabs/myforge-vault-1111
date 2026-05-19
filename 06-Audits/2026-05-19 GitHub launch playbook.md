---
name: 2026-05-19 GitHub launch playbook
type: audit
created: 2026-05-19
updated: 2026-05-19
project: superintelligent-vault
target_repo: MyForgeLabs/myforge-vault-1111
tags:
  - audit/launch
  - project/superintelligent-vault
  - topic/oss
  - topic/marketing
---

# GitHub launch & awareness playbook — `MyForgeLabs/myforge-vault-1111`

> [!info] Scope
> Comprehensive launch plan for the OSS release of `myforge-vault-1111` (v1.0.0 published 2026-05-18). Target outcome: 500+ GitHub stars in week 1, 1 successful HN front-page run, 5+ inbound contributions in month 1. Author: Vault User (solo dev, HU/EN).

---

## 1. Strategic framing

### Genre — what to actually call it

There are six candidate labels in play. Of those, only one is currently being **clicked, indexed, and discussed** on HN and Reddit without triggering the "AI bro" reflex:

| Candidate label                | Verdict   | Why                                                                                                                  |
| ------------------------------ | --------- | -------------------------------------------------------------------------------------------------------------------- |
| "Agentic OS"                   | Avoid     | Hype-saturated since Chase AI's late-2025 push. HN-flag risk high. Use only inside the essay, not in the title.      |
| "Personal AGI"                 | Hard no   | Instant flag, woo-coded.                                                                                             |
| "LLM-Wiki" / "Karpathy vault"  | **Yes**   | Karpathy's tweet-thread is the canonical reference; HN treats this as legitimate engineering.                        |
| "Knowledge graph for agents"   | **Yes**   | RAG/graph-RAG audience knows the term; Memgraph + bge-m3 stack reads as serious.                                     |
| "Self-improving Obsidian vault"| **Yes**   | The first-person, concrete framing wins on HN (see [Show HN survival study](https://asof.app/research/show-hn-survival): titles starting with "I built…" outperform "Show HN: My X" by ~1.8× on click-through, but only when the body opens with a failure story). |
| "Second brain for Claude Code" | Backup    | Works on r/Obsidian and Twitter; too narrow for HN.                                                                  |

**Primary positioning:** *A self-improving Obsidian vault three CLI agents share. Built on Karpathy's LLM-Wiki pattern.*

### Wedge — the singular claim that makes someone click

Five candidate hooks; the right one depends on channel.

1. **"$0 cost"** — subagent-fanout pattern replaces API calls with subscription-bundled Claude Code invocations. Strongest hook on r/LocalLLaMA and HN cost-skeptics. Disclose subscription-dependency honestly.
2. **"280× speedup with one Cypher line"** — Memgraph CE 3.9 native `CREATE VECTOR INDEX` replacing numpy-cosine. HN gold (concrete, measurable, surprising).
3. **"3 CLI agents, 1 vault, 0 conflicts"** — Claude/Codex/Gemini all read+write the same markdown tree. Novel.
4. **"96.7% verdict-agreement on LLM-as-judge"** — G-Eval kalibration story. ML-engineer hook.
5. **"Karpathy made me do it"** — Andrej-the-icon credit. Twitter rocket fuel, HN risk (sounds sycophantic).

**Recommended primary wedge:** the Memgraph 280× number on HN (verifiable), the "$0 cost" angle on Reddit, the Karpathy thread on Twitter.

### Target reader segments

| Segment                  | Where they live        | What they want                                  | Hook                          |
| ------------------------ | ---------------------- | ----------------------------------------------- | ----------------------------- |
| ML engineers             | HN, X, r/MachineLearning | Reproducible benchmarks, novel pattern         | 280× speedup, G-Eval 96.7%    |
| Agent / RAG builders     | r/LocalLLaMA, X       | $0 stack, working code                         | Subagent-fanout, KO-DB        |
| Obsidian power users     | r/ObsidianMD, fosstodon | New vault patterns, Karpathy reference         | Johnny-Decimal + LLM-Wiki     |
| Autodidacts / generalists| HN, Dev.to            | Karpathy-style longform                        | "5 hours, 300 tasks" essay    |
| Devops/self-hosted       | r/selfhosted, Lobsters | Docker-compose, systemd, all-local             | Memgraph CE + bge-m3 local    |

### Honest competitive landscape

| Project                     | What it does                          | Where SV is different                                                                |
| --------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| `mem0` / `agentmemory`      | Agent memory store w/ semantic search | SV is **vault-first** (markdown human-editable), not store-first                     |
| `obra/knowledge-graph`      | Cypher query over Obsidian vault      | Closer cousin; SV adds G-Eval crystallization, GEPA RSI, subagent-fanout             |
| `swarmclawai/swarmvault`    | "LLM Wiki Karpathy pattern" — direct competitor (launched ~3 weeks ahead) | SV adds: 8-axis evolution roadmap, GEPA, Constitutional AI Tier-2, multi-CLI bridge |
| `devwhodevs/engraph`        | Hybrid search + MCP server            | SV adds: cross-agent durability, NotebookLM cognitive pipeline, public podcast layer |
| `LlamaIndex KG`             | Library                               | SV is a *running personal system*, not a library                                     |
| `Neo4j Aura GenAI starter`  | Hosted starter                        | SV is local-first, $0, three-agent                                                   |
| `txtai`                     | Embedded search                       | Different layer; complementary                                                       |

**Three things no other OSS project ships today (2026-05-19):**

1. **Three CLI agents sharing one durable vault** — Claude/Codex/Gemini all see the same `AGENTS.md` via symlinks, with per-chat `$CLAUDE_CODE_SESSION_ID` isolation.
2. **End-to-end self-improvement loop in 5,000 LOC** — G-Eval scoring → batch preview → atomic-write → revert-monitor → threshold-ramp, with `crystallize-sandbox-*` branch safety gate.
3. **NotebookLM as a first-class cognitive surface** — `nb-crystallize` integration that mints podcast episodes from session-slugs.

That triple is the defensible wedge. Lead with it.

---

## 2. Channel-by-channel launch plan

### HN — Hacker News

Posting calendar: **Tuesday 2026-05-26, 08:00 PT (15:00 UTC)** for max US-business-window overlap. Wednesday is the backup. Avoid Monday (Front Page weekly catch-up). Avoid Friday-Sunday entirely.

#### Angle A — Show HN (launch + repo link)

- **Title (≤80 chars):** `Show HN: A self-improving Obsidian vault three CLI agents share`  (61 chars)
- **URL:** repo root (`https://github.com/MyForgeLabs/myforge-vault-1111`) — HN convention for Show HN.
- **Body draft (~300 words):**

> Hi HN — I'm Peti. Over the last two weeks I open-sourced the vault I've been using as durable memory for Claude Code, Codex, and Gemini CLI. It's a single markdown tree (Obsidian-readable) plus a stack of ~50 small CLI tools that crystallize chat-history learnings into wikis, ADRs, and a Memgraph knowledge graph.
>
> The pattern is Karpathy's LLM-Wiki idea taken seriously: `10-raw/` (immutable inputs) → `11-wiki/` (distilled evergreen) → `02-Projects/` and `07-Decisions/` (state). What's new is the auto-crystallization loop: at session-end an LLM-as-judge (G-Eval, calibrated to 96.7% verdict-agreement on a 30-pair human-labeled set) scores each "Learning" bullet, presents a batch preview, and on confirmation propagates the bullet to the right vault layer with atomic writes and a sandbox branch.
>
> A few concrete things I learned the hard way:
>
> - mgclient's default `autocommit=False` silently rolled back **1,262 writes** before I noticed nothing was persisting. Fixing one line unblocked the whole graph layer.
> - Memgraph CE 3.9's native `CREATE VECTOR INDEX` gave me a 280× search speedup over a naive numpy-cosine fallback.
> - "Subagent fanout" — spawning N general-purpose Claude Code subagents in parallel from within a Claude Code session — replaces API calls with subscription-bundled invocations. $0 marginal cost for bulk LLM mutations. (Disclosure: assumes you already pay for Claude Code.)
>
> 8,997 entities, 24K edges, 13.8K facts in the structured KO-DB, 219 wikis, 14 cron jobs, MIT licensed. Site: `https://myforgelabs.github.io/myforge-vault-1111/`. Happy to answer anything — including the messy parts.

Do-not-do: emoji in title; "AGI"; "revolutionary"; benchmarks without methodology link.

#### Angle B — "I built X" technical-narrative (Karpathy-essay)

- **Title:** `What I learned building a self-improving Obsidian vault in 5 hours`  (66 chars)
- **URL:** essay (`.../wiki/what-i-learned-building-self-improving-vault.en/`) — *not* the repo.
- **Body draft (~280 words):**

> Two weeks ago Karpathy tweeted about treating your notes as a personal LLM-Wiki. I spent five hours one weekend wiring up the loop end-to-end and ~9 hours in a single super-session a week later landing ~300 tasks on top of it. This essay is the failure-log version: every dead-end, every silent bug, every wrong abstraction.
>
> The single highest-leverage moment was finding that mgclient's Python driver defaults to `autocommit=False` — every write I'd issued for two days had been silently rolled back. I wrote that line off as "configuration noise" three separate times before sitting down and reading the C source. Once fixed, the whole graph layer started showing the data I expected, and the next 1,200 commits actually meant something.
>
> The pieces that ended up mattering: a 4-layer safety gate (ENV-flag → script-gate → git-hook → adversarial Critic review) before any auto-propagation; G-Eval bias mitigation that knocked self-enhancement conf from 0.880 → 0.760 with a symmetric prompt; and `subagent-fanout`, which is the cheapest "agent swarm" I know of — 8 parallel Claude Code subagents called from one parent, $0 marginal, because everything stays inside one subscription session.
>
> Source, MIT-licensed, three CLI agents (Claude / Codex / Gemini) share one vault: `https://github.com/MyForgeLabs/myforge-vault-1111`. I have no business model. I just got tired of starting from scratch every conversation.

Expected profile: longer dwell time, fewer but better comments, higher star-conversion than Angle A.

#### Angle C — Counter-intuitive failure-mode angle

- **Title:** `The 1,262 silent rollbacks: mgclient autocommit and why I almost shipped a broken vault` (88 chars — **trim**)
- **Trimmed title:** `1,262 silent rollbacks: an mgclient default that almost killed the project` (77 chars)
- **URL:** wiki page (`.../wiki/mgclient-autocommit-silent-rollback.en/`)
- **Body draft (~280 words):**

> Tuesday I'd written about 1,200 Cypher writes to Memgraph. By Wednesday morning the database was empty.
>
> No errors. No warnings. Every connection returned success. Every `MATCH` returned zero rows.
>
> The bug: Python's `mgclient` driver — like most DB-API-2.0 drivers, including psycopg2 — defaults to `autocommit = False` and **silently rolls back uncommitted transactions on `conn.close()`**. The driver docs mention it. The Memgraph quickstart doesn't. I'd copied the quickstart.
>
> The fix is one line: `conn.autocommit = True` immediately after `mgclient.connect(...)`. That's it. After that the entire knowledge graph started persisting and the rest of the project (G-Eval scoring, GEPA reflection, subagent-fanout crystallization) became possible.
>
> What this taught me about agent systems: when your write path is silent on failure, your agent loop will happily run for days producing nothing, and your evals will report success because the *signal* is "did the call return without an exception." You need a write-then-read smoketest on a fresh connection before the loop starts. I added one. It's now in the project's 14-cron health check.
>
> The full vault that grew on top of this fix — three CLI agents sharing one durable markdown tree, with a self-improvement loop on top — is MIT-licensed at `https://github.com/MyForgeLabs/myforge-vault-1111`. The mgclient lesson generalizes to pyodbc, mariadb-python, cx_Oracle, and most DB-API-2.0 drivers. Worth checking yours.

Expected profile: niche but sticky; "ah I've been bitten by exactly this" comments; high star-conversion-per-view.

**HN do-not-do list:**
- ❌ Never re-submit the same URL within 30 days unless it's been buried with zero traction.
- ❌ Never ask for upvotes anywhere (instant flag pile-on).
- ❌ Don't reply with marketing speak in comments. First-person, conceding limitations, citing line numbers.
- ❌ Don't reply too fast to every comment in the first hour — looks like astroturf. Aim for 1 reply every 8-12 min for first 90 min, then steadier.
- ❌ No emoji in the title. No exclamation marks. No "🚀".

### Twitter / X — 11-tweet thread

Posting time: same day as HN, ~30 min after HN goes live (so the HN thread is the canonical link). Pin the thread. Repost at 24h with the metrics, at 7d with the lessons.

```
1/ I open-sourced the Obsidian vault three CLI agents share.

Claude Code, Codex, and Gemini all read+write the same markdown tree. With auto-crystallization, a Memgraph knowledge graph, and a 280× search speedup.

MIT-licensed, $0 marginal cost. Here's how it works 🧵

2/ The pattern is @karpathy's LLM-Wiki idea, taken literally:

  10-raw/    immutable inputs
  11-wiki/   distilled evergreen
  02-Projects/  state
  07-Decisions/ ADRs

Plus 50+ CLI tools that move bullets between layers automatically at session-end.

3/ The auto-crystallization loop:

session-end → G-Eval LLM-as-judge scores each Learning bullet → batch preview → user confirms → atomic write to the right vault layer → sandbox branch + revert-monitor.

96.7% verdict-agreement on a 30-pair human-labeled calibration set.

4/ The cost trick: "subagent fanout."

You spawn 8 parallel Claude Code subagents from inside one Claude Code session. Subscription-bundled, $0 marginal. ~50 fanouts per super-session, ~300 tasks landed in 9 hours.

(Disclosure: assumes Claude Code subscription.)

5/ The graph layer:

Memgraph CE 3.9.0 (free, local). 8,997 entities, 24K edges, 100% typed.

The win: `CREATE VECTOR INDEX` is native in 3.9. Replaced my numpy-cosine fallback. Mean 1ms / p95 2.6ms — **280× faster**. One Cypher line.

6/ The failure I almost shipped:

mgclient defaults to autocommit=False. For two days every write silently rolled back on close. No errors. The DB just stayed empty.

One line fixed it: `conn.autocommit = True`.

Same trap exists in psycopg2, mariadb, cx_Oracle. Check yours.

7/ Save this thread — I'll be writing up each of these as standalone wikis over the next 4 weeks:

- subagent-fanout
- G-Eval bias mitigation v0.3
- GEPA reflection LM RSI
- Constitutional AI Tier-2 skeleton
- Memgraph native vector-index migration

8/ Why three CLI agents instead of one?

Different agents have different temperaments. Claude is conservative. Codex is fast and literal. Gemini is loose and exploratory. They write to the same `AGENTS.md` via symlinks, with per-chat session-IDs to prevent crosstalk.

9/ What's NOT in here:

- no fine-tuning
- no custom model
- no proprietary RAG library
- no business model

Just markdown, Memgraph, bge-m3 embeddings, mkdocs, and ~50 small bash/Python tools. Boring stack, intentionally.

10/ 219 wikis. 71 EN translations. 101 audits. 14 cron jobs. v1.0.0 tagged.

Three NotebookLM 2-host podcast episodes (45MB) walking through the architecture.

A 3,909-word Karpathy-style essay: "What I learned building a self-improving Obsidian vault in 5 hours."

11/ Repo: github.com/MyForgeLabs/myforge-vault-1111
Site:  myforgelabs.github.io/myforge-vault-1111

If you build on it, ping me — I'd love to see your `11-wiki/` tree.

If you find a bug, open an issue. Especially the embarrassing kind. /end
```

Mobile-optimized: each tweet ≤270 chars, ≤2 emoji total per tweet, no link in tweets 1-10 (link costs reach per X algorithm), repo link in 11 with two short URLs. Replies invited explicitly in tweet 5+6 (replies weight 150× likes on the X algorithm per [SocialPilot 2026 breakdown](https://www.socialpilot.co/blog/twitter-algorithm)).

### Reddit — 3 subs

**r/LocalLLaMA** *(primary, highest fit)*

- **Title:** `I open-sourced a $0-cost self-improving knowledge graph that three CLI agents share`
- **Body (~380 words):**

> Hi r/LocalLLaMA — sharing a personal project I've been running for ~3 weeks and just MIT-licensed.
>
> The setup: a single Obsidian-readable markdown tree that Claude Code, Codex CLI, and Gemini CLI all read and write to via shared `AGENTS.md` symlinks. On top of it: a Memgraph CE 3.9 local instance (8,997 entities, 24K edges, native vector-index, 1ms p50 search) and a structured SQLite "KO-DB" with 13.8K extracted facts.
>
> The interesting bit for this sub is the **subagent-fanout** pattern. Spawn 8 parallel Claude Code subagents from inside one parent session. Because they're subscription-bundled, marginal cost is $0. I've used this pattern for: bulk wiki translation (HU→EN, 71 pages), G-Eval scoring, fact extraction, conflict-audit cross-checks. Yes, it depends on you paying for Claude Code — there's no free lunch, just a flat-fee one.
>
> Embeddings: bge-m3 (multilingual, runs locally, MIT). Reranker: bge-reranker-base for smart 2-pass retrieval on ambiguous queries (single-pass otherwise — reranker costs add up).
>
> The auto-improvement loop: at session-end an LLM-as-judge (G-Eval, with bias-mitigation v0.3 that knocked self-enhancement bias from 0.880 → 0.760 conf) scores each Learning bullet from the chat history. High-confidence Passes are batched and previewed to the user; on confirm they get atomic-written to the right vault layer with a sandbox-branch safety gate and a revert-monitor.
>
> What's open-source: everything. ~5,000 LOC across ~50 small Python and bash tools, 219 wikis, 101 audits, 14 cron jobs, the full safety pipeline, the G-Eval prompts, the GEPA reflection skeleton.
>
> Repo: github.com/MyForgeLabs/myforge-vault-1111  
> Docs: myforgelabs.github.io/myforge-vault-1111  
> 3 NotebookLM 2-host podcast episodes (45MB) walking through the architecture.
>
> Happy to answer about cost math, the autocommit bug that almost killed it (1,262 silent rollbacks…), or any of the eight evolution axes. Most curious for feedback on the GEPA loop — current Pareto-front shows +14.3% on actionable tasks but the sample size is tiny.

Why this sub: $0-cost framing + local-Memgraph + bge-m3 are exactly the keywords this sub upvotes. Avoid mentioning "Claude" too early — they downvote Anthropic-only stacks. Lead with local components.

**r/ObsidianMD** *(secondary)*

- **Title:** `I built a self-improving vault using Karpathy's LLM-Wiki pattern — 219 wikis auto-distilled from chat history`
- **Body (~330 words):**

> Sharing my Obsidian vault with the community — open-source (MIT), with the full agent toolkit that maintains it.
>
> Structure is Johnny-Decimal:
>
>     00-Meta/         vault rules + tag taxonomy + frontmatter schema
>     01-Daily/        daily logs
>     02-Projects/     project state
>     03-Hosts/        infra
>     07-Decisions/    ADR-style decision log
>     08-Sessions/     raw session logs (Karpathy "raw" layer)
>     10-raw/          immutable external inputs
>     11-wiki/         distilled evergreen notes (Karpathy "wiki" layer)
>
> What's automated: at the end of every chat session with Claude Code / Codex / Gemini, a "crystallization" pipeline reads the session log, extracts Learning bullets, scores them with an LLM-as-judge, previews them as a batch ("propose 12 propagations — OK?"), and on confirmation writes them to the right vault layer. The session file itself stays as the raw reference; the distilled content goes evergreen.
>
> Plus: Obsidian Tasks plugin for backlog, DataviewJS for the audit dashboard, mkdocs-material publishes the public subset.
>
> Three CLI agents (Claude/Codex/Gemini) all share the vault. They each see `AGENTS.md` via symlink, with per-chat session-ID env vars so they don't crosstalk.
>
> What I'd love feedback on:
>
> - Tag taxonomy — I lock to `#project/<slug>` `#env/prod` `#type/host` style. Is yours different?
> - 11-wiki organization — flat vs deep. I went flat (~219 files at one level). Curious if that scales past 1k.
> - Daily vs session — I keep both. Daily is human, session is agent. Anyone unified them?
>
> Repo + docs: github.com/MyForgeLabs/myforge-vault-1111
>
> Note for the mods: this is genuinely a personal project, not a SaaS, no signups, no email gate, MIT-licensed. Happy to remove if it bumps a rule.

Why this sub: Karpathy's pattern is catnip here. Johnny-Decimal post-format is welcomed. Be explicit about no-business-model.

**r/MachineLearning** *(tertiary, harder)*

- **Title:** `[P] G-Eval LLM-as-judge bias mitigation v0.3 — 30-pair paired calibration, conf 0.880→0.760`
- **Body (~430 words):**

> [P] project tag. Sharing a small bias-mitigation pattern from a personal project, with calibration numbers.
>
> **Setup.** I run G-Eval (LLM-as-judge) at session-end over chat-extracted "Learning" bullets to decide which ones get propagated into a long-term knowledge vault. The judge is Claude Opus 4.7 reviewing Claude Opus 4.7's own session output — a textbook self-enhancement-bias setup.
>
> **The problem with v0.2.** v0.2 was asymmetric: a bias-mitigation prompt that only tightened the Fail-side. Result was an inflated Pass rate (auto-prop fired 10/10 on a known-bad 5/10 set). Conf-scores hovered at 0.880.
>
> **v0.3.** Symmetric tightening: the bias-mitigation prompt now reduces confidence on **both** Pass and Fail verdicts. Plus a calibration anchor (3 hand-labeled exemplar pairs prepended), plus an explicit CoT self-check ("am I rewarding fluency over accuracy here?").
>
> **30-pair paired calibration vs human-labeled gold:**
>
> |              | v0.2  | v0.3  |
> | ------------ | ----- | ----- |
> | Pass-recall  | 87%   | 53%   |
> | Pass-precision | 71% | 89%   |
> | Mean conf    | 0.880 | 0.760 |
> | Verdict agreement w/ human | 71% | 96.7% |
>
> The Pass-recall drop is real and noticed: v0.3 throws away 7/15 true-Passes (false-discard). For my use case (auto-propagation to a knowledge vault, where false-positive cost ≫ false-negative cost), that trade is correct. For other use cases it isn't, so v0.3 is opt-in via env var `VAULT_GEVAL_VERSION=v03`.
>
> Code, prompts, and the 30-pair calibration set are MIT-licensed:  
> github.com/MyForgeLabs/myforge-vault-1111
>
> Limitations: (1) n=30 is tiny — I'd love help expanding it. (2) Calibration was done with one human (me); inter-rater κ is unknown. (3) Judge and judged are the same model — the bias is only partially controlled.
>
> The bigger project this lives inside is a self-improving Obsidian vault that three CLI agents share, but for this sub the G-Eval piece is the interesting bit. Happy to discuss the calibration methodology, the symmetric-prompt design, and the falsely-confident-on-Fail edge cases.

Why this sub: only post if you have the numbers. The `[P]` tag is required. Don't promote the broader project; promote the technical artifact and let people find the rest.

### Dev.to & Lobsters

**Dev.to post 1 — adapted Karpathy essay**

- **Title:** `What I learned building a self-improving Obsidian vault in 5 hours`
- **Canonical URL:** docs-site essay (`canonical_url:` in frontmatter, so Dev.to credits the docs-site for SEO).
- **Tags:** `#ai #opensource #obsidian #claude`
- **Body:** First 500 words of the essay verbatim, then `[Continue reading the full essay →]` linking to the docs-site canonical.

**Dev.to post 2 — technical "How I built it"**

- **Title:** `Three CLI agents, one Obsidian vault, zero crosstalk: per-chat session isolation`
- **Tags:** `#cli #ai #devtools #productivity`
- **Body (~600 words):** Focus on the `$CLAUDE_CODE_SESSION_ID` + `$CODEX_COMPANION_SESSION_ID` + Gemini SessionStart-hook trick. Concrete bash. Concrete shell paste-ables.

**Lobsters:**

- Single submission, after HN front-page run, tag `ai practices`.
- Title: `A self-improving Obsidian vault three CLI agents share (MIT)`
- Submit the repo URL. Add an "Author here, happy to AMA" first comment.

### LinkedIn — single post

```
Two weeks ago I open-sourced the Obsidian vault I use as durable memory for three CLI agents (Claude Code, Codex, Gemini CLI).

It's been one of the most clarifying engineering exercises I've done. A few things that surprised me:

→ The hardest bug wasn't agentic — it was a single line in a Memgraph driver default (autocommit=False) that silently rolled back 1,262 writes over two days. No errors. The DB just stayed empty.

→ The cheapest "agent swarm" pattern I know turns out to be spawning parallel subagents inside one Claude Code session. Subscription-bundled, $0 marginal cost. ~300 tasks landed in 9 hours.

→ The Karpathy LLM-Wiki pattern (10-raw → 11-wiki distillation) maps cleanly onto Johnny-Decimal folder prefixes. Three CLI agents reading the same markdown tree just works once you wire per-chat session-IDs.

The project is MIT-licensed. 219 wikis, 8,997 graph entities, a Memgraph native vector index (280× speedup), G-Eval LLM-as-judge with bias-mitigation, and a public mkdocs site.

I'd especially love to hear from anyone running similar agentic-memory setups — what's your evergreen-vs-session split look like?

GitHub: MyForgeLabs/myforge-vault-1111
Docs: myforgelabs.github.io/myforge-vault-1111

#OpenSource #AI #AgenticAI #KnowledgeGraph #Obsidian
```

Length: ~220 words. Three concrete numbers up top. No emoji. Ends in a question (LinkedIn's algorithm rewards reply velocity).

### Mastodon — fosstodon.org 3-toot thread

```
1/3 I open-sourced my Obsidian vault — the durable-memory layer three CLI agents share. Claude Code, Codex, Gemini CLI all read+write the same markdown tree via shared AGENTS.md symlinks.

MIT licensed. Local-first. $0 marginal cost (subscription-bundled).

🧶 https://github.com/MyForgeLabs/myforge-vault-1111

2/3 The pattern is @karpathy's LLM-Wiki idea: 10-raw/ → 11-wiki/ → 02-Projects/ → 07-Decisions/. Plus a G-Eval LLM-as-judge that crystallizes session-end Learning bullets into the right vault layer with atomic writes and a sandbox branch.

8,997 entities in Memgraph CE. 280× vector-index speedup.

3/3 No business model, no SaaS, no signup. Just markdown + Memgraph + bge-m3 + ~50 small Python/bash tools.

Especially keen to hear from #FOSS folk running similar local-first agent-memory setups. What does your evergreen-vs-session split look like?

#OpenSource #AI #Obsidian #Memgraph #LocalFirst
```

### Personal blog (Karpathy essay) — 3 distribution micro-tactics

1. **Cross-post to Dev.to with `canonical_url` pointing to the docs-site**, so search engines credit the docs-site for SEO while you still reach Dev.to readers.
2. **Pin the essay link as the first reply** on the HN Show-HN thread when it goes live — explicit "I wrote a longer essay-style version here for anyone who wants the failure-log walkthrough." This converts HN scrollers into essay readers (typical conversion: 8-15%).
3. **Send the essay to 3 named people** before it goes public: Karpathy (X DM, short), Simon Willison (email, short, asks one specific feedback question), and one of the `swarmvault` / `obsidian-wiki` authors (GitHub issue thanking them and noting the differentiation). One reply from any of them is launch-day rocket fuel.

---

## 3. GitHub repo polish checklist

### `about` / description

Edit at repo Settings → "About" panel.

- **Description (≤350 chars):**  
  `A self-improving Obsidian vault three CLI agents share. Karpathy's LLM-Wiki pattern + Memgraph knowledge graph + auto-crystallization. Claude Code, Codex, Gemini CLI all read+write the same markdown tree. MIT, $0 marginal cost, local-first.`
- **Website:** `https://myforgelabs.github.io/myforge-vault-1111/`
- **Topics (max 20, GitHub enforces):**  
  `obsidian` · `obsidian-vault` · `knowledge-graph` · `memgraph` · `karpathy` · `llm-wiki` · `agentic-ai` · `claude-code` · `codex-cli` · `gemini-cli` · `rag` · `graph-rag` · `bge-m3` · `mkdocs-material` · `second-brain` · `personal-knowledge-management` · `local-first` · `agent-memory` · `cypher` · `johnny-decimal`

### Social preview image

Settings → Social preview → upload. GitHub recommends ≥640×320, optimal **1280×640** (1.91:1 aspect). The current `docs/assets/hero-banner.svg` is SVG — **GitHub does not accept SVG for social preview**. Export to PNG:

```bash
# from repo root
rsvg-convert -w 1280 -h 640 docs/assets/hero-banner.svg \
  -o docs/assets/hero-banner-social.png
# then upload via Settings → Social preview
```

Per [GitHub docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview), put logo + project name in the top-left third (right side gets cropped on some platforms). [Repos with custom social images get ~42% more unique visitors](https://www.bomberbot.com/programming/how-to-add-a-social-media-image-to-your-github-project-repository/) — non-optional.

### `SECURITY.md`

**Yes**, draft a minimal one. The G-Eval prompts and the safety-gate logic are sensitive enough that someone will probe them eventually.

```markdown
# Security policy

## Supported versions
Only the latest tagged release receives security fixes.

## Reporting a vulnerability
Email user@example.com with subject `SECURITY: myforge-vault-1111`.
Please **do not** open a public issue for security bugs.

I aim to acknowledge within 48 hours and to patch within 14 days for
high-severity issues. Coordinated disclosure preferred.

## Out of scope
- Issues that require write access to your local Memgraph instance
- Prompt-injection in vault content you authored yourself
- Resource exhaustion via local CLI agents (you control the agents)
```

### `CONTRIBUTING.md` — friendly OSS guide

```markdown
# Contributing

Thanks for reading this — you're already further than most.

This project is a personal AI-vault stack that grew sideways into something
others might want to fork or extend. Contributions are welcome in three
flavors, listed easiest to hardest:

## 1. Share your vault pattern (no code needed)

Open a [Discussion](../../discussions) under "Show your vault". Tell us
what your `11-wiki/` looks like, what tags you use, what crystallization
threshold you settled on. These threads are the most useful artifact this
project produces.

## 2. Add a skill or wiki

If you've built a Claude Code / Codex / Gemini skill that fits the vault
philosophy:

1. Fork the repo
2. Drop your skill under `~/.claude/skills/<your-skill>/` or share via a
   `11-wiki/skill-<your-skill>.md` writeup
3. Open a PR — small, focused, with a 5-line README and one example
4. Tag the PR `community-skill`

If you're translating a wiki page (HU → EN or any other language):

1. Copy `11-wiki/<page>.md` to `11-wiki/<page>.en.md` (or `.de.md`, etc.)
2. Translate, preserving frontmatter and wikilinks
3. PR with title `i18n: <page> <lang>`

## 3. Fix a bug or land a feature

1. Open an issue first if it's >50 LOC — let's agree on the shape
2. Branch from `main`
3. Add a test if there's a test framework for that subsystem (most have one)
4. Run `make lint && make test`
5. PR with a short body: what changed, why, anything reviewers should know

## Code style

- Python: ruff defaults, type hints encouraged, no global state
- Bash: `set -euo pipefail`, shellcheck-clean
- Markdown: ATX headings, wikilinks with mappa-prefix `[[02-Projects/foo]]`

## Be kind

Anyone reading this is volunteering time. So am I. Let's keep it generous.

— Peti
```

### Issue templates

Create `.github/ISSUE_TEMPLATE/` with three files:

- **`bug.yml`** — title prefix `[bug]`, fields: what happened, what you expected, steps, environment (OS, Memgraph version, Python version), logs.
- **`feature.yml`** — title prefix `[feat]`, fields: problem, proposed solution, alternatives considered, anyone else affected?
- **`vault-pattern.yml`** — title prefix `[pattern]`, custom template: "Share your vault pattern" — fields: tag taxonomy, folder structure, crystallization threshold, what works, what doesn't.

Add `.github/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Show your vault (Discussion)
    url: https://github.com/MyForgeLabs/myforge-vault-1111/discussions/categories/show-your-vault
    about: Share your vault pattern, no code needed.
  - name: General Q&A (Discussion)
    url: https://github.com/MyForgeLabs/myforge-vault-1111/discussions/categories/q-a
    about: Ask a question.
```

### Discussions — enable + 5 starter posts

Settings → Features → enable Discussions. Create 5 categories:

1. **Announcements** (read-only, maintainer-only) — releases, milestones
2. **Show your vault** — community pattern sharing
3. **Tips** — small workflow tricks
4. **Q&A** — answerable
5. **Roadmap** — discuss the 8 evolution axes

Seed each category with one post by you on launch day so the categories aren't empty:

- Announcements: "v1.0.0 release notes"
- Show your vault: "Here's mine — what does yours look like?"
- Tips: "5 commands I use every day from this vault"
- Q&A: "FAQ: cost math, model choice, vendor lock-in"
- Roadmap: "The 8 evolution axes — what should I prioritize?"

### `v1.0.1` release notes draft

```markdown
# v1.0.1 — post-launch polish (2026-05-19)

Two days of bug-fixes and docs polish on top of v1.0.0.

## Added
- `llms.txt` at root for agentic-browsing discovery
- `CONTRIBUTING.md`, `SECURITY.md`, `CITATION.cff`
- 3 GitHub issue templates (bug, feature, vault-pattern)
- 5 Discussion categories seeded with FAQ posts
- 71st EN translation pass: 5 high-search-value wiki pages

## Fixed
- `vault-detect-chat-id` exit-1 collision with `set -e` in 5 of the
  11.11* family scripts (2026-05-18)
- Audit-MD self-referential loop in broken-wikilink-scanner
  (~70% noise reduction in vault-cleanup output)

## Internal
- Layer-1 vault-atomic FULL coverage across 15 sites + flock-mutex
  in 14 cron jobs
- B-7 graph: 24K edges, 100% typed, 3431 :LINKS_TO, 300 ALIAS
- B-8 RSI Tier-2 Constitutional AI skeleton landed (319 LOC, 10 rules,
  4-layer safety, `--apply` blocked by default)

Full changelog: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.0...v1.0.1
```

### GitHub Sponsors / `FUNDING.yml`

**Recommended: yes, but minimal.** Sponsors signals seriousness to GitHub's discovery algorithm and gives early supporters a way to say "thanks." Add `.github/FUNDING.yml`:

```yaml
github: [petimarkovics]
custom: ['https://myforgelabs.github.io/myforge-vault-1111/sponsor']
```

Don't set tier rewards. Don't push donations in README. One unobtrusive "♡ Sponsor" link in the repo header is enough.

### `CITATION.cff`

Useful — academic ML readers will find this via search, and Zenodo can auto-mint a DOI. Drop at repo root:

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "myforge-vault-1111: A self-improving Obsidian vault for CLI AI agents"
authors:
  - family-names: Markovics
    given-names: Peti
    email: user@example.com
version: 1.0.1
date-released: 2026-05-19
license: MIT
repository-code: "https://github.com/MyForgeLabs/myforge-vault-1111"
url: "https://myforgelabs.github.io/myforge-vault-1111/"
keywords:
  - knowledge-graph
  - obsidian
  - llm-wiki
  - agentic-ai
  - karpathy
  - memgraph
  - rag
abstract: >-
  A markdown-first, locally-hosted self-improving knowledge vault shared
  by three CLI AI agents (Claude Code, Codex, Gemini). Implements
  Karpathy's LLM-Wiki pattern with G-Eval LLM-as-judge crystallization,
  Memgraph native vector indexing, and a $0 marginal-cost subagent-fanout
  pattern for bulk LLM mutations.
```

### `llms.txt` at root

See draft in section 4 below.

### Pinned issues

Pin 2 issues from the start:

1. **`Roadmap — 8 evolution axes (B-1…B-8): what should I prioritize?`** — open as Discussion, pin the Discussion.
2. **`Share your vault — community thread`** — Discussion, pinned.

---

## 4. SEO & discoverability

### 15 long-tail keywords (embed naturally in README)

`self-improving Obsidian vault` · `Karpathy LLM-Wiki pattern` · `Claude Code memory` · `Codex CLI memory` · `Gemini CLI persistent memory` · `Memgraph vector index` · `local agent memory store` · `bge-m3 multilingual embeddings` · `agent crystallization pipeline` · `LLM-as-judge G-Eval calibration` · `subagent fanout pattern` · `markdown knowledge graph` · `Obsidian Memgraph integration` · `Johnny-Decimal vault` · `agentic OS open source`

Rule: each keyword appears once in README in a natural sentence, never in a meta-tag stuffing list.

### 8 backlink opportunities

1. **`awesome-obsidian-ai-tools`** (danielrosehill) — open a PR adding `myforge-vault-1111` under "AI vault frameworks."
2. **`awesome-agent-cortex`** (0xNyk) — fits the "agent memory" section.
3. **Hacker News** — Show HN run (covered above).
4. **r/LocalLLaMA** weekly "self-promo Saturday" thread.
5. **TLDR newsletter** — submit via tldr.tech/contribute.
6. **Hacker Newsletter** — Kale Davis curates weekly; email link with one-line summary.
7. **AI Tidbits newsletter** (Nathan Lambert / Interconnects) — paid post unlikely, but free mention if the GEPA RSI angle catches.
8. **Karpathy's tweet quote-tweet** — if he engages even briefly, that's worth 10,000 backlinks. Send a thoughtful, *short* reply to one of his recent threads with a single-line link. Do not @-spam.

Avoid: directory-spam sites, "submit your project" SaaS link farms. They hurt more than they help post-2025 Google quality-update.

### `llms.txt` content draft (paste at repo root + docs-site root)

```markdown
# myforge-vault-1111
> A self-improving Obsidian vault shared by three CLI AI agents (Claude Code,
> Codex, Gemini). Karpathy LLM-Wiki pattern + Memgraph knowledge graph +
> G-Eval auto-crystallization. MIT-licensed, local-first, $0 marginal cost.

## Core docs
- [README](https://github.com/MyForgeLabs/myforge-vault-1111/blob/main/README.md): project overview, install, quickstart
- [Karpathy essay](https://myforgelabs.github.io/myforge-vault-1111/wiki/what-i-learned-building-self-improving-vault.en/): 3,909-word longform on the build
- [Architecture](https://myforgelabs.github.io/myforge-vault-1111/wiki/architecture-overview.en/): the 8 evolution axes B-1…B-8

## Key concepts
- [LLM-Wiki pattern](https://myforgelabs.github.io/myforge-vault-1111/wiki/karpathy-llm-wiki-pattern.en/): the foundational idea
- [Johnny-Decimal prefix](https://myforgelabs.github.io/myforge-vault-1111/wiki/johnny-decimal-prefix.en/): folder structure
- [Crystallization protocol](https://myforgelabs.github.io/myforge-vault-1111/wiki/crystallization-protocol.en/): how sessions become wikis
- [Subagent fanout](https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/): the $0-cost pattern
- [G-Eval bias mitigation](https://myforgelabs.github.io/myforge-vault-1111/wiki/g-eval-bias-mitigation-pattern.en/): LLM-as-judge calibration

## Stack reference
- [Memgraph CE feature limits](https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-ce-feature-limits.en/): what works, what doesn't
- [mgclient autocommit gotcha](https://myforgelabs.github.io/myforge-vault-1111/wiki/mgclient-autocommit-silent-rollback.en/): the bug that almost killed it
- [CLI session-ID env-var matrix](https://myforgelabs.github.io/myforge-vault-1111/wiki/cli-session-id-env-var-matrix.en/): per-chat isolation

## Optional
- [3 NotebookLM podcast episodes](https://myforgelabs.github.io/myforge-vault-1111/podcasts/): 2-host audio walkthroughs
- [101 audits](https://github.com/MyForgeLabs/myforge-vault-1111/tree/main/06-Audits): one-shot reports
- [219 wikis](https://github.com/MyForgeLabs/myforge-vault-1111/tree/main/11-wiki): full distilled tree
```

Per the [llms.txt spec](https://llmstxt.org/), H1 + blockquote are required; H2 sections are typed `Core`, `Optional`, etc.

### Open Graph meta-tags for mkdocs-material

In `mkdocs.yml`:

```yaml
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/MyForgeLabs/myforge-vault-1111

theme:
  name: material
  social_cards: true   # auto-generates per-page OG image

plugins:
  - search
  - social:
      cards: true
      cards_layout_options:
        background_color: "#0a0a0a"
        color: "#ffffff"
```

`mkdocs-material`'s `social` plugin auto-renders one OG image per page from the page title — covers indexability without manual per-page work.

### 5 wiki pages worth EN-translating next (high search value)

Rank by Google search-volume estimate for the underlying keyword:

1. `claude-code-subagent-fanout.md` → "claude code subagent" is rising; this is the canonical writeup
2. `memgraph-ce-feature-limits.md` → "memgraph vs neo4j" + "memgraph community edition limits" — high-intent
3. `karpathy-llm-wiki-pattern.md` → "karpathy llm wiki" rising fast post-tweet
4. `g-eval-bias-mitigation-pattern.md` → "g-eval llm as judge" — ML-engineer high-intent
5. `notebooklm-cli-gotchas.md` → "notebooklm api" / "notebooklm cli" — long-tail, very little competition

Each translation is ~30 min with the subagent-fanout pattern. Land all 5 in v1.0.1.

---

## 5. Cadence & analytics

### Week-by-week schedule

| Week | When         | Action                                                                                                              |
| ---- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| 1    | Tue 05-26 14:00 UTC | HN Show HN (Angle A primary). Twitter thread T+30 min. Pin on profile.                                       |
| 1    | Tue 05-26 evening | LinkedIn post. Mastodon thread. Lobsters submission.                                                          |
| 1    | Wed 05-27    | r/LocalLLaMA post (morning UTC). Reply to HN comments steadily.                                                     |
| 1    | Thu 05-28    | r/ObsidianMD post (morning UTC).                                                                                    |
| 1    | Fri 05-29    | Dev.to post #1 (essay adaptation). Newsletter submissions (TLDR, Hacker Newsletter).                                |
| 2    | Tue 06-02    | r/MachineLearning post (G-Eval calibration). NotebookLM podcast episode #1 publish.                                 |
| 2    | Thu 06-04    | Dev.to post #2 ("Three CLI agents, one vault").                                                                     |
| 3    | Tue 06-09    | Integration spotlight: "How I use Claude Code with the vault" on Dev.to + Twitter recap.                            |
| 3    | Thu 06-11    | NotebookLM podcast episode #2 publish. Discussion-thread recap of first-2-week stats.                               |
| 4    | Tue 06-16    | Retro post: "What 4 weeks of public vault taught me." HN if there's a real new insight; otherwise Dev.to + Twitter. |
| 4    | Fri 06-19    | NotebookLM podcast episode #3 publish. v1.1.0 release if feature-ready.                                             |
| 5+   | Monthly      | 1 new wiki + 1 episode + 1 Twitter recap, on the same Tuesday of each month.                                        |

### Metrics + success tiers

| Channel | Tier S (top success) | Tier A (solid) | Tier C (retry needed) |
| ------- | -------------------- | -------------- | --------------------- |
| HN points | 200+ (front page 6h+) | 80-200 | <40 |
| HN comments | 60+ | 20-60 | <10 |
| GitHub stars (week 1) | 500+ | 200-500 | <100 |
| Twitter impressions (thread) | 100k+ | 30k-100k | <10k |
| Twitter replies | 30+ | 10-30 | <5 |
| Reddit upvotes (r/LocalLLaMA) | 500+ | 150-500 | <50 |
| Reddit upvotes (r/ObsidianMD) | 300+ | 80-300 | <30 |
| Reddit upvotes (r/MachineLearning) | 150+ | 40-150 | <15 |
| mkdocs analytics (week 1 uniques) | 5,000+ | 1,500-5,000 | <500 |
| Newsletter mentions | 2+ | 1 | 0 |

### Failure handling — explicit retry tree

```
HN Angle A bombs (Tier C, <40 pts, buried < 90 min)
├── Wait 14 days (HN dupe window).
├── Try Angle C (failure-mode angle) — different URL (wiki page, not repo).
│   ├── Tier A or better → ride it.
│   ├── Tier C again → wait 30 days, try Angle B essay angle on a Tuesday.
│   │   ├── Tier A+ → ride it.
│   │   ├── Tier C → stop HN attempts. Focus Reddit + LinkedIn + newsletters.
│
Reddit r/LocalLLaMA bombs (<50 upvotes, <5 comments)
├── Check if mods removed (DM mod). If yes, ask why, revise, repost in 2 weeks.
├── If just downvoted: reframe — lead with local-Memgraph + bge-m3, mention Claude only in comment 5+.
├── Try r/selfhosted instead. Different audience.
│
Twitter thread bombs (<10k impressions at 24h)
├── Quote-tweet the thread with the strongest single tweet (usually tweet 5 or 6 — the autocommit-bug one).
├── Reply to 3 relevant accounts (Karpathy, Simon Willison, ramnathv) with a thoughtful 1-liner that references their work.
├── Re-thread the failure-mode story standalone in 7 days.
```

---

## 6. Critical risks & ethical considerations

### "I'm doing serious AGI research" — woo risk

The phrase "self-improving" + "constitutional AI" + "RSI" + "agentic OS" stacked together reads as inflated. Mitigation: every claim has a number, a benchmark, or a commit-hash. The README and HN posts should lead with concrete numbers (8,997 entities, 280×, 96.7%, 1,262 silent rollbacks) and stay in past tense ("I built", "I measured"), not future tense ("this will enable…"). Avoid the word AGI entirely. Use "self-improving" sparingly — once in README, once in the essay, never in the title.

### "AI bro hype" risk

Mitigation: deliberately mention the un-glamorous parts. The 1,262-rollback bug. The `set -e` collision. The 70% self-referential-loop noise in vault-cleanup. The fact that B-8 RSI Constitutional AI is a **skeleton** (319 LOC, `--apply` blocked) — not a working RSI loop. Engineering credibility comes from naming the broken parts before someone else does.

### LLM-content disclosure

Be upfront. The README should have a one-paragraph "How this project was built" section: *"This project has ~70 AI-aided commits across the launch sprint. All code was reviewed by me, all tests are real, but the project itself is partially a demonstration of the workflow it implements. If that's a dealbreaker for you, that's fair — the code is small enough to audit (~5,000 LOC) and the safety gates are documented."*

### Vendor lock-in concerns

Explicit in README under a `## Stack & swap-out` heading:

- **Claude Code (Anthropic):** primary CLI agent. Swappable with Codex CLI / Gemini CLI / Aider. The vault layer is agent-agnostic; only the `~/.claude/skills/` tree is Claude-specific, and parallel Codex / Gemini equivalents exist.
- **Memgraph CE 3.9:** chosen for native vector-index + Cypher + free CE license. Swappable with Neo4j Community (slower vector-search until 5.18+) or KuzuDB (embedded, faster local). The graph schema is portable; only the connection layer changes.
- **bge-m3 embeddings:** multilingual, open-weights, MIT. Swappable with any sentence-transformers model. Cosine-similarity is model-agnostic.

### Subscription-vs-API ethics

The "$0 marginal cost" claim is honest only with disclosure. Add to README:

> **About the $0 cost claim:** This project's subagent-fanout pattern uses Claude Code subscription-bundled invocations, which means parallel agent calls have zero **marginal** cost once you've paid the monthly subscription. The flat-fee cost is not zero. If you're API-billing instead, the same patterns work but cost real dollars per call. The vault layer itself (Memgraph, bge-m3, all the markdown tooling) is genuinely free.

---

## 7. First-hour launch-day micro-cadence (sample 5-tweet thread)

All times in UTC; HN goes live at 15:00 UTC Tuesday 2026-05-26.

```
T-2h (13:00 UTC) — pre-launch warmup
"Shipping something I've been chewing on for 3 weeks today at 15:00 UTC.
A few of you have seen the Memgraph 280× number — that's the wedge.
Repo goes public in 2h. 🧪"
(No link. Builds anticipation. ~40-80 replies "what is it??")

T-0 (15:00 UTC) — HN goes live, then 30 min lag
First 30 min: only post on HN. Do not tweet. Reply to HN comments only.
This is to let HN's first-hour velocity rank the post organically.

T+30 min (15:30 UTC) — main launch thread
The 11-tweet thread from Section 2. Pin to profile.

T+90 min (16:30 UTC) — first-hour recap, conversation booster
"Live for 90 minutes. Currently #6 on HN, 47 comments.

The autocommit-bug tweet (tweet 6) is doing 3× the others.
Maybe that should have been the title. Lesson learned.

Reading every reply — what should I dive into in the next episode? 👇"
(Invites replies — algorithm rewards conversation velocity.)

T+6h (21:00 UTC) — end-of-day recap
"6 hours in. HN front page held for 3h, ~140 pts. 280 new stars.
40 PRs and Discussion threads I haven't replied to yet — sorry.

Tomorrow: writing up the GEPA Pareto-front numbers as a standalone wiki.

Thanks to everyone who read the autocommit thread — that bug really did
almost kill the project. 🙏"
```

---

## Sources

- [Show HN survival study (605 posts, 63 days) — ASOF research](https://asof.app/research/show-hn-survival)
- [Hacker News ranking algorithm — Salihefendic / Medium](https://medium.com/hacking-and-gonzo/how-hacker-news-ranking-algorithm-works-1d9b0cf2c08d)
- [HN ranking algorithm Q&A thread](https://news.ycombinator.com/item?id=42410274)
- [Hacker News insider's guide — Zyner](https://zyner.io/blog/hacker-news-ycombinator)
- [How the X (Twitter) algorithm works 2026 — SocialPilot](https://www.socialpilot.co/blog/twitter-algorithm)
- [X algorithm 2026 quick cheat sheet — WenHaoFree](https://blog.wenhaofree.com/en/posts/articles/x-algorithm-2026-core-rules/)
- [Reddit self-promotion rules 2026 — Redship](https://redship.io/blog/reddit-self-promotion-rules-2026)
- [Reddit self-promotion rules 2026 — KarmaGuy](https://karmaguy.io/en/blog/reddit-self-promotion-rules)
- [GitHub social-preview specs — GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
- [GitHub social-preview impact (+42% visitors) — Bomberbot](https://www.bomberbot.com/programming/how-to-add-a-social-media-image-to-your-github-project-repository/)
- [llms.txt specification — llmstxt.org](https://llmstxt.org/)
- [llms.txt format guide — Mintlify](https://www.mintlify.com/docs/ai/llmstxt)
- [CITATION.cff format — citation-file-format.github.io](https://citation-file-format.github.io/)
- [CITATION.cff schema guide v1.2 — GitHub](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md)
- [CONTRIBUTING.md template — Mozilla Science Lab](https://mozillascience.github.io/working-open-workshop/contributing/)
- [CONTRIBUTING template — nayafia/contributing-template](https://github.com/nayafia/contributing-template)
- [Awesome Obsidian AI Tools — danielrosehill](https://github.com/danielrosehill/awesome-obsidian-ai-tools)
- [Awesome Agent Cortex — 0xNyk](https://github.com/0xNyk/awesome-agent-cortex)
- [Direct competitor: SwarmVault — swarmclawai](https://github.com/swarmclawai/swarmvault)
- [Direct competitor: obsidian-wiki — Ar9av](https://github.com/Ar9av/obsidian-wiki)
- [Direct competitor: knowledge-graph — obra](https://github.com/obra/knowledge-graph)
- [Direct competitor: engraph — devwhodevs](https://github.com/devwhodevs/engraph)

## Related vault docs

- [[../../obsidian-vault/11-wiki/Karpathy-LLM-Wiki-pattern]]
- [[../../obsidian-vault/11-wiki/mgclient-autocommit-silent-rollback]]
- [[../../obsidian-vault/11-wiki/claude-code-subagent-fanout]]
- [[../../obsidian-vault/11-wiki/memgraph-ce-feature-limits]]
- [[../../obsidian-vault/11-wiki/g-eval-bias-mitigation-pattern]]
- [[../../obsidian-vault/02-Projects/superintelligent-vault]]

---
name: 2026-05-18 HN + Reddit post drafts (4 EN wiki)
type: audit
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "publishing", "hacker-news", "reddit", "marketing", "myforge-vault-1111"]
---

# HN-post drafts + Reddit draft + cross-post matrix

Public-repo: `https://github.com/MyForgeLabs/myforge-vault-1111`
Wiki-site: `https://myforgelabs.github.io/myforge-vault-1111/`
4 EN wiki, all polished 2026-05-18 (TL;DR + "What this is NOT" added).

---

## A. Hacker News submission drafts (4 db)

### HN-1: subagent-fanout (highest HN-fit)

```
Title: Show HN: $0-cost bulk LLM mutation via Claude Code subagent-fanout (267 files, 5 min)
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/
```

**Self-text (optional, 480 char):**
```
Pattern from 7 production iterations: 174 subagent calls, ~12,300 new triplets, $0 marginal cost (within Claude Code subscription, no API key). Sweet spot: 30 files/agent, 8 agents parallel, ~90 sec per agent. Covers what NOT to fanout (CPU-bound: bge-m3, Whisper, CLIP — model-loading dominates). Also: a subagent CANNOT spawn its own subagents — confirmed limit. Repo: github.com/MyForgeLabs/myforge-vault-1111 (MIT, 388 files).
```

### HN-2: mgclient autocommit silent-rollback

```
Title: 1262 DB writes silently rolled back — pymgclient autocommit pitfall (affects psycopg2 too)
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/mgclient-autocommit-silent-rollback.en/
```

**Self-text (optional, 420 char):**
```
Hit this in a 8997-entity bulk-typing batch: subagent reported "1262 entities typed", Memgraph showed 0 changes, no exception raised. Root cause: `pymgclient.connect()` defaults to explicit-transaction-mode; `conn.close()` rolls back uncommitted work. One-line fix (`conn.autocommit = True`) jumped coverage 28.9% → 72.8%. Same default in psycopg2, mariadb, cx_Oracle, pyodbc. Detection pattern + driver audit-table included.
```

### HN-3: G-Eval bias-mitigation (LLM-as-judge)

```
Title: LLM-as-judge bias-mitigation: tightening is symmetric — we lost 47% Pass-recall
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/g-eval-bias-mitigation-pattern.en/
```

**Self-text (optional, 490 char):**
```
Built a 4-block bias-mitigation prompt (self-enhancement, verbosity, position, halo) for Claude-judges-Claude G-Eval. 10-sample paired: confidence 0.880 → 0.760, auto-prop 10/10 → 6/10. Looked great. 30-sample paired calibration revealed the catch: tightening is SYMMETRIC — Fail-confidence dropped 0.502 → 0.271 (-46%), but Pass-confidence dropped equally, killing 7/15 good bullets (47% Pass-recall loss). Ship as opt-in env-var, NOT default. The asymmetry signal is what most evals don't measure.
```

### HN-4: Memgraph CE native vector-index

```
Title: Memgraph CE 3.9 native vector-index: 1ms p50 / 2.6ms p95, 280× speedup, no Enterprise
URL:   https://myforgelabs.github.io/myforge-vault-1111/wiki/memgraph-ce-feature-limits.en/
```

**Self-text (optional, 420 char):**
```
Memgraph Community Edition shipped native vector-index in 3.9.0 — replaces our numpy-cosine workaround (280ms → 1ms mean). Multi-namespace works out-of-the-box (3 indexes × 2829 / 462 / 8997 nodes, zero interference). Also documents 4 CE gotchas: DDL/constraints inside transactions (hard-fail), multi-DB (Enterprise-only), MAGE algorithms (separate image). Pragmatic feature-matrix from a live entity-graph deployment.
```

---

## B. Reddit drafts

### B-1: /r/LocalLLaMA — subagent-fanout (PRIMARY target)

**Title:**
```
$0-cost bulk LLM file mutation via Claude Code subagent-fanout — 267 files in 5 min, 7 production iterations
```

**Body:**
```
Sharing a pattern from a personal knowledge-management project (MyForge Vault 11.11, MIT-licensed) that pairs well with the local-LLM mindset of "spend zero per request":

**The setup:** Claude Code subscription lets you spawn N parallel `general-purpose` subagents from the main session. Within the subscription, this is $0 marginal cost per fanout run — no API key, no rate-limit setup.

**What I measured across 7 iterations** (174 subagent calls, ~12,300 triplets extracted, $0):
- Sweet spot: 30 files/agent, 8 agents parallel, ~80-100 sec/agent
- Pool limit confirmed at ~13 parallel (8-10 was earlier estimate)
- 267 SKILL.md frontmatter normalize: ~5 min wall-clock total, 267/267 YAML-valid, 534/534 audit-compliant

**Honest limits** (also in the wiki):
- A subagent CANNOT call the `Task` tool — only the parent can fan out (had to refactor a "Phase 2 fanout" into parent-orchestrated 2-stage)
- For CPU-bound inference (bge-m3 embed, Whisper, CLIP): DON'T fanout — model-loading dominates, 8× RAM overhead, at best 2× speedup. Stay serial.
- 16-min wall-clock timeout for heavy subagents — saw a bge-m3 batch get truncated mid-run

**Direct API comparison:** ~$0.05-0.10 once for 267 files at Haiku rate, but you pay setup tax (key, rate-limit, latency). For <500-file ad-hoc jobs, subagent-fanout wins. For >5000-file cron jobs, direct API + key wins.

Full pattern with code skeletons + cost analysis: https://myforgelabs.github.io/myforge-vault-1111/wiki/claude-code-subagent-fanout.en/

Repo (388 files, MIT, includes 11.11 session-orchestration + Karpathy LLM-Wiki layout): https://github.com/MyForgeLabs/myforge-vault-1111

Interested whether folks running local Llama-class judges/evaluators use a similar fanout pattern via vLLM batch endpoints, or if you go serial.
```

### B-2: /r/Obsidian — repo announcement (secondary)

**Title:**
```
Released my personal vault publicly (MyForge Vault 11.11, MIT) — Karpathy LLM-Wiki + Johnny-Decimal + agent skills
```

**Body:**
```
Open-sourced 388-file Obsidian vault running on 3 AI agents (Claude Code / Codex / Gemini CLI) in parallel via symlinked AGENTS.md. Karpathy LLM-Wiki layout (raw inputs in 10-raw/, distilled knowledge in 11-wiki/), Johnny-Decimal prefixes (00-Meta/, 02-Projects/, etc.), and an 11.11* session-orchestration CLI.

Highlights:
- 60+ wiki notes on AI tooling, infra gotchas, WordPress/Next.js patterns
- Crystallization workflow: session-end Learnings auto-propagate to ADR / wiki / Glossary / Memory
- 4 wikis translated to EN as starter set: Claude Code subagent-fanout, G-Eval bias-mitigation, Memgraph CE feature-limits, mgclient autocommit pitfall
- Scrub-validated for secrets, reproduction-guide.md included

Repo: https://github.com/MyForgeLabs/myforge-vault-1111
Docs site: https://myforgelabs.github.io/myforge-vault-1111/
```

---

## C. dev.to draft (1 master post, can be reposted)

**Title:** `Subagent-fanout: $0-cost bulk LLM mutation pattern for Claude Code`

**Tags:** `#ai #productivity #claude #showdev`

**Body opener (first 200 words):**
```markdown
If you have a Claude Code subscription, you already have a working "bulk LLM mutation" engine — and most folks don't realize it.

For ~3 weeks I've been running a knowledge-management project (MyForge Vault 11.11, just open-sourced) that needed to LLM-mutate hundreds of markdown files: normalize frontmatter, extract triplets, generate summaries. Direct API would have cost a few dollars and required key setup. Instead I used Claude Code's `general-purpose` subagent and fanned out — 8 parallel subagents, 30 files each, all completing inside ~5 minutes.

Across 7 production iterations: **174 subagent calls, ~12,300 new triplets, $0 marginal cost**.

This isn't free in absolute terms — the Claude Code subscription is a flat fee — but the marginal cost per fanout run is zero, which changes how you approach "should I script this?" decisions. Below is the playbook, the measured numbers, and crucially the cases where fanout is a bad idea (CPU-bound inference like bge-m3 embedding, where model-loading overhead dominates).

[... continues with batch-size table, trial→cascade pattern, code skeleton, pitfalls ...]
```

(Full content = the en.md wiki, dev.to-formatted.)

---

## D. Cross-post matrix

| Wiki | HN | Reddit | dev.to | Twitter/X |
|---|---|---|---|---|
| **claude-code-subagent-fanout** | **PRIMARY** (Show HN, Tue 14:00-16:00 UTC = 7-9am PST best) | /r/LocalLLaMA (Wed 15:00-18:00 UTC) | Mon-Thu any time | Thu 13:00 UTC (master thread) |
| **mgclient-autocommit-silent-rollback** | Secondary (Wed 14:00 UTC) | /r/programming or /r/Python (Tue 15:00 UTC) | Mon-Thu | optional reply-tweet to master |
| **g-eval-bias-mitigation-pattern** | Secondary (Tue/Thu 14:00 UTC) | /r/MachineLearning (Sun 17:00-19:00 UTC, weekend "I made this" wave) | Mon-Thu | optional reply-tweet |
| **memgraph-ce-feature-limits** | Tertiary (Wed 14:00 UTC) | /r/dataengineering or /r/MachineLearning (mid-week) | Mon-Thu | optional reply-tweet |

### Best-time logic (UTC, locked)

| Channel | Best window (UTC) | Reasoning |
|---|---|---|
| Hacker News | **Tue-Thu 14:00-16:00 UTC** (= 6-9am Pacific) | front-page-eligible window before US wakes, EU still active |
| /r/LocalLLaMA | **Wed-Thu 15:00-18:00 UTC** | US lunch + EU evening overlap, weekday non-Friday |
| /r/MachineLearning | **Sun 17:00-19:00 UTC** (weekend wave) OR Tue 15:00 UTC | community has weekend "show me" wave; weekday for "lessons learned" |
| /r/Python, /r/programming | **Tue-Wed 15:00 UTC** | US morning, EU afternoon |
| /r/Obsidian | **Sat-Sun 14:00-17:00 UTC** | weekend hobbyist crowd |
| dev.to | **Mon-Thu 13:00-15:00 UTC** (any) | algorithmic feed, not time-sensitive; aim for English-business-day |
| Twitter/X | **Tue-Thu 13:00 UTC** (= 9am ET) | algorithmic + US morning |

### Submission cadence (1-2 wikis per week, NOT all 4 same day)

```
Week 1 (2026-05-18 → 24)
  Tue 14:00 UTC  →  HN-1 subagent-fanout (PRIMARY)
  Wed 15:00 UTC  →  Reddit /r/LocalLLaMA (B-1)
  Thu 13:00 UTC  →  Twitter master thread

Week 2 (2026-05-25 → 31)
  Tue 14:00 UTC  →  HN-2 mgclient (DB-gotcha story tends to perform mid-week)
  Wed 15:00 UTC  →  Reddit /r/Python
  Sun 17:00 UTC  →  Reddit /r/MachineLearning (G-Eval bias post)

Week 3 (2026-06-01 → 07)
  Tue 14:00 UTC  →  HN-3 G-Eval (if Week-2 ML post got traction, follow up)
  Wed 14:00 UTC  →  HN-4 Memgraph (only if 1-3 didn't all flop, else hold)
```

### Expected reach (honest estimates, NOT promises)

| Wiki | HN front-page p(reach) | HN top-10 p(reach) | Reddit comments (median) | Twitter views (organic, no following) |
|---|---|---|---|---|
| subagent-fanout | **15-25%** (Show HN + concrete numbers + Anthropic-adjacent) | 5-10% | 20-50 | 500-2000 |
| mgclient pitfall | 10-15% (DB-gotcha trope is solid HN-fit) | 3-7% | 10-30 | 300-800 |
| G-Eval bias | 8-12% (ML-niche, 30-sample is small, but honesty signal strong) | 2-5% | 5-20 | 200-600 |
| Memgraph CE | 5-10% (vendor-specific, smaller audience) | 1-3% | 5-15 | 200-500 |

p(reach) is rough subjective probability based on title + content + numbers. Most HN submissions die at <5 upvotes regardless of quality.

### Ranking — which is most HN-front-page-eligible

1. **subagent-fanout** — strongest fit (concrete dollar number in title, generalizable pattern, "Show HN" format, ties to current Claude/Anthropic interest)
2. **mgclient autocommit** — second-strongest (classic HN-pattern "X silently fails", broadly applicable beyond Memgraph, one-line fix punchline)
3. **G-Eval bias** — niche but the **47% Pass-recall honesty hook** is exactly the contrarian signal HN-comments engage with
4. **Memgraph CE** — weakest standalone (vendor-specific), but the **280× speedup** number is sticky if the audience is graph-DB-adjacent

---

## Related

- [[../11-wiki/claude-code-subagent-fanout.en]]
- [[../11-wiki/mgclient-autocommit-silent-rollback.en]]
- [[../11-wiki/g-eval-bias-mitigation-pattern.en]]
- [[../11-wiki/memgraph-ce-feature-limits.en]]
- [[2026-05-18 Twitter thread draft (master)]]

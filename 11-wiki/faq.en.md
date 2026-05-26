---
name: FAQ — MyForge Vault 11.11
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
lang: en
tags: ["#type/wiki", "faq", "onboarding", "launch"]
related:
  - "[[architecture-overview.en]]"
  - "[[what-i-learned-building-self-improving-vault.en]]"
---

# FAQ — MyForge Vault 11.11

The questions you'll have before / during / after reading the rest of the
project. Curated from the kinds of things people ask new OSS launches.

## "What is this, in one sentence?"

A locally-hosted, self-improving markdown knowledge-vault that three CLI AI
agents (Claude Code, Codex, Gemini) share — built around Karpathy's LLM-Wiki
pattern with a Memgraph knowledge-graph, G-Eval auto-crystallization, and a
4-layer Constitutional safety-gate.

## "Should I use this?"

Use it if you:

- run multiple CLI AI agents on the same machine and want them to share state
- already use Obsidian and feel its native graph is "shallow"
- want a working reference implementation of [Karpathy's LLM-Wiki
  pattern](Karpathy-LLM-Wiki-pattern.en.md) rather than a blog post
- are a researcher / agent-builder who needs an instrumented memory testbed
- want to fork a working agentic-OS and adapt it to your domain

Do **NOT** use it if you:

- want a SaaS — this is local-only, by design
- need a hosted vector DB — this uses Memgraph + bge-m3 locally
- are looking for a Cursor/Cline plugin — this is a CLI/agent-stack
- expect first-class Windows support — it runs on Linux + macOS; Windows is
  best-effort via WSL

## "Is this AGI?"

No. It's augmented intelligence — three CLI agents sharing a structured
notebook that gets better over time. The agents do the work; the vault
remembers. No claims of recursive self-improvement reaching superhuman
levels; the RSI loop is gated behind 4 explicit safety layers and `--apply`
mode is locked by default. See [the RSI safety gate](multi-layer-safety-gate.en.md).

## "How much does it cost to run?"

**$0 marginal cost** if you have a Claude Code subscription (and / or a
NotebookLM subscription for podcast generation).

The numeric details:

- **Claude Code subscription** ($20/mo) — covers all agent work including
  bulk subagent-fanout LLM mutations (10K+ ops across the 26-day build)
- **NotebookLM** (free tier or $20/mo Plus) — used for cross-project synthesis
  and 2-host podcast generation
- **Local infra** — Memgraph CE (free), bge-m3 (open-weights, free), Python
  stack (free), a VPS with ~32 GB RAM + 8 cores recommended

If you skip the Claude Code subscription and use the Anthropic API directly,
add ~$80/mo for an equivalent workload. The subagent-fanout pattern
specifically exists to avoid this.

## "How do I install it?"

Five steps, ~15 minutes if all the deps are pre-installed:

```bash
# 1. Clone
git clone https://github.com/MyForgeLabs/myforge-vault-1111.git
cd myforge-vault-1111

# 2. Memgraph CE (Docker)
docker run -d --name memgraph -p 7687:7687 memgraph/memgraph:latest

# 3. Python deps
make install        # or: pip install -r requirements.txt

# 4. Embed the wiki content
./scripts/vault-embed.py --backfill 11-wiki/

# 5. Try a search
./scripts/vault-search "Karpathy LLM-Wiki pattern"
```

See [README.md](../README.md) for the full quickstart with verification steps.

## "Why three CLI agents instead of one?"

Different agents have different strengths and pricing models, and each makes
mistakes that the others catch:

- **Claude Code** — best at long-form code generation, has the `Task` tool for
  the subagent-fanout pattern; primary workhorse
- **Codex** — strong at code refactoring + IDE-integrated workflows; second
  opinion on architecture
- **Gemini** — strong at multimodal + has unique session-context patterns; third
  perspective

They share a single `AGENTS.md` system prompt (symlinked across all three CLI
homes), the same vault, the same `11.11*` session-orchestration scripts.
The `AGENT=` env-var stamps every commit so you can `git log --author` to
see which agent did what.

## "What's in the vault by default?"

A complete working example with my own content:

- 258 evergreen wikis (Hungarian primary, 71 English translations)
- 45 ADRs (Architecture Decision Records)
- 104 audits (one-shot reports)
- ~80 session-logs (some scrubbed for public)
- 13,800+ KO-DB triplets extracted from the above
- 8,997 typed entities in Memgraph (with 24,606 edges)
- 962 indexed skills (SKILL.md files)
- 3 NotebookLM 2-host podcast episodes

You can use this as-is to study the architecture, or `rm -rf 11-wiki/*
07-Decisions/* 06-Audits/* 08-Sessions/*` and put your own content in.

## "What's the 'agentic OS' framing?"

Not marketing — a literal description of how it works.

The three CLI agents are processes that read/write a shared filesystem
(the vault). The `11.11*` family is the IPC mechanism (session-start,
note-append, session-stop). The vault-search daemon is a long-running
service (like a kernel module). Memgraph is the database (like a
filesystem index). G-Eval is the access-control gate. Constitutional AI
Tier-2 is the privileged-mode escalation path (locked).

An OS by analogy. NOT a desktop OS, NOT a kernel — but the same shape.

## "Why Memgraph and not Neo4j / NetworkX / DuckDB / SQLite?"

- **vs Neo4j**: Memgraph CE 3.9 native vector-index (no licensing wall),
  280× speedup over numpy-cosine, p95 2.6 ms. Neo4j Community is roughly
  equivalent for graph queries but the vector index lives behind a paid tier
  in their hosted product.
- **vs NetworkX**: no persistence, no concurrent access, no vector index
- **vs DuckDB**: great for analytical SQL, weaker for graph traversals
  (Cypher in DuckDB is third-party + immature as of 2026-05)
- **vs SQLite (KO-DB)**: we already use SQLite for the triplet store! The
  KO-DB and Memgraph are complementary, not alternatives — SQLite handles
  the substring + filter top-k retrieval (60 ms), Memgraph handles the
  graph traversal + vector search

See [memgraph-ce-feature-limits.en.md](memgraph-ce-feature-limits.en.md) for
the unrosy details.

## "Is the AI-aided-build disclosed?"

Yes — explicitly. The repo has 70+ commits in the launch sprint alone, most
of them with AI-agent co-authorship. The `AGENT=` commit-trailer is by
design. The Karpathy-style essay ([What I learned...](what-i-learned-building-self-improving-vault.en.md))
is candid about which parts were AI-aided.

This isn't hidden, it's the *point*: a working artifact built BY AI agents
USING the vault we're publishing. The vault is what makes the AI-aided
build sustainable.

## "Can I run this without exposing my vault content?"

Yes. Default install ingests **only the files you point it at**. No telemetry,
no analytics, no remote endpoints. Memgraph is local. bge-m3 is local. The
only outbound call is when you ask the agent to fetch something explicitly
(firecrawl, NotebookLM, etc.).

The opt-in browser-history bridge has a `--dry-run` default; `VAULT_BROWSER_INGEST_APPLY=1`
is required to actually write to the vault.

## "Is there a Discord / Slack / Matrix?"

Not yet. Use [GitHub Discussions](https://github.com/MyForgeLabs/myforge-vault-1111/discussions)
for now. A real-time chat will appear if there's demand and a community to
support it (otherwise it's a graveyard).

## "Can I contribute?"

Yes. Three flavors:

1. **Share your vault pattern** — open a `[pattern]` issue or a Discussion
2. **Add a wiki** — fork, write under `11-wiki/<your-page>.md`, PR
3. **Fix code** — open an issue first if >50 LOC; PR with tests if there's a
   test framework for that subsystem

See [CONTRIBUTING.md](../CONTRIBUTING.md). The AI agents are co-collaborators
on this project — your PR will probably be reviewed by both a human and a
Claude Code agent. That's fine; both make mistakes the other catches.

## "Hungarian-first feels weird"

It's not weird, it's *honest*. I'm Hungarian, the original session-logs are
in Hungarian, and bge-m3 handles HU↔EN semantic search well enough that the
hybrid is genuinely a feature (not a bug). 71 of the 258 wikis (28%) are
translated to English; the most-trafficked ones are translated first, the
rest as community demand arises.

If you want to help translate, see the [`i18n: <page>` PR pattern](../CONTRIBUTING.md).

## "What's NOT in this repo (yet)?"

The next-session backlog (deferred from 2026-05-19):

- **Temporal-KG SCD2 layer** — `valid_from`/`valid_until` on KO-DB facts for
  time-travel queries
- **Transaction-aware `atomic_append_jsonl`** — for the 2
  `vault-ko-remap-legacy` sites that need it
- **Real-LLM Critic** for the sleep-consolidation pipeline (currently a
  rule-based mock + a pending-file interface)
- **Cloudflared tunnel** for the vault-mcp STDIO server to be reachable
  from claude.ai web/mobile
- **CI workflows** — partially landed in v1.0.1; full coverage in v1.0.2

See [the repo improvement audit](../06-Audits/2026-05-19%20repo%20improvement%20audit.md)
for the post-launch roadmap.

## "Anything else?"

Star the repo. Open a Discussion if anything here is unclear. The single
most-valuable thing you can do is share *your* vault pattern, even if
it's totally different.

## Related

- [[architecture-overview.en]] — the 8-axis mental model
- [[what-i-learned-building-self-improving-vault.en]] — Karpathy-style narrative
- [[Karpathy-LLM-Wiki-pattern.en]] — the foundational pattern
- [[multi-layer-safety-gate.en]] — the 4-layer atomic-write story

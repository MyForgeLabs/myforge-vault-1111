# MyForge Vault — Architecture

High-level system view of the 8-axis SV (Superintelligent Vault) stack as it stood on v1.0.13 (2026-05-25).

The vault is a **filesystem-first** knowledge base (markdown files in a git repo) augmented with **four independent live indexes** that the agents query at session-start and during write-time. None of the indexes are authoritative — the markdown files always win. The indexes exist to make retrieval fast (Layer-3, semantic) and to detect contradictions (cross-source conflict-audit).

## The four live indexes

```
                 ┌──────────────────────────┐
                 │     /root/obsidian-vault/  (filesystem, git-versioned)
                 │     11-wiki/  07-Decisions/  08-Sessions/  10-raw/  …
                 │   = SOURCE OF TRUTH (always)
                 └────────────┬─────────────┘
                              │ ingest pipelines
              ┌───────────────┼────────────────┬─────────────────┐
              │               │                │                 │
              ▼               ▼                ▼                 ▼
        ┌─────────┐     ┌─────────────┐  ┌────────────┐    ┌──────────┐
        │ KO-DB   │     │  Memgraph   │  │ vault-     │    │ Memgraph │
        │ (SQLite)│     │  (Cypher)   │  │ embed      │    │ entity   │
        │         │     │             │  │ + bge-m3   │    │ graph    │
        │ facts   │     │ Chunk +     │  │ vectors    │    │ + typed  │
        │ (s,p,o, │     │ SkillChunk  │  │            │    │ :Label   │
        │ confid) │     │ nodes       │  │ (in graph) │    │ (B-7)    │
        └────┬────┘     └──────┬──────┘  └──────┬─────┘    └─────┬────┘
             │                 │                │                │
             │                 │                │                │
             ▼                 ▼                ▼                ▼
       vault-ko-query   vault-search       agentmemory    vault-graph-query
       (substring,      (Memgraph bge-m3,  (RRF-sister    (Cypher, typed
        SCD2 active,     auto-rerank with   index via      filter, label
        provenance       bge-reranker-v2)   port :8024)    counts)
        join)
             │                 │                │                │
             └─────────────────┴────────┬───────┴────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │ vault-search-fusion (RRF)│  ← DEFAULT
                          │ vault-ko-query --top-k    │     (semantic-rrf)
                          │ vault-ko-query --semantic │
                          │ vault-ko-query --top-k    │     (KO-DB only)
                          │ (--no-semantic)           │
                          └──────────┬───────────────┘
                                     │
                                     ▼
                          ┌──────────────────────────┐
                          │ Agent (Claude / Codex /  │
                          │ Gemini) load-session-    │
                          │ context skill at start   │
                          └──────────────────────────┘
```

## The 8 axes (SV roadmap)

| # | Axis | Sprint | State |
|---|---|---|---|
| 1 | **Memory architecture** (filesystem + KO-DB + Memgraph) | B-2 | LIVE (v1.0.13) |
| 2 | **Recursive self-improvement** (GEPA + Pareto-improvement loop) | B-8 | Critic κ=0.708 production-flip ratified |
| 3 | **Multi-agent orchestration** (Claude/Codex/Gemini per-chat session-isolation) | B-6 | live for all 3 agents |
| 4 | **Tool composition** (subagent-fanout pattern, $0 cost LLM-mutation at scale) | B-4 | live (~346 subagent in one day) |
| 5 | **Crystallization automation** (session → KO-DB → wiki propagation w/ G-Eval gate) | B-1 | shadow + threshold-ramp 1.0/0.95/0.85 |
| 6 | **World-model / knowledge graph** (Memgraph entity + relation graph, typed-label classifier) | B-7 | **61.6% typed-coverage** (v1.0.13, was 2.0% in v1.0.10) |
| 7 | **Continuous evaluation** (9-axis weekly rollup, LongMemEval-S R@5 baseline-gate) | B-3 | 9 axes / weekly cron / Sun 06:00 UTC |
| 8 | **NotebookLM cognitive layer** (deep-research bridge, 63-source synthesis) | B-5 | live with 8 NotebookLM-projects |

## Safety rails (Layer-0 chained guards)

Every git commit runs through a chain of guards triggered by staged-file patterns:

```
pre-commit chain:
  ├── (always-on) bmad-vault-bridge --apply forbidden-targets check
  ├── (if hooks.json staged) → vault-plugin-hooks-audit --strict
  ├── (if .mcp.json staged)  → vault-mcp-audit --strict
  ├── (if schema-relevant)   → vault-schema-migration-victim-audit --strict
  └── (always)               → forbidden-paths block (AGENTS.md, 00-Meta, .vault-*, 11.11*)
```

Override env-var per layer (`SKIP_*_AUDIT=1`) for emergency commits. Each guard is HIGH-heat = COMMIT BLOCKED.

## CLI surface (87+ vault-* binaries)

Discoverable via `vault` umbrella:

```bash
$ vault
Categories:
  ko (15)       graph (10)     search (5)
  audit (12)    embed (6)      crystallize (2)
  session (6)   skill (2)      wiki (5)
  nb (3)        net (2)        infra (18)
```

Shell-completion available for **bash + fish + zsh**.

## Health-check single-command

```bash
$ vault-doctor
🟢 Memgraph    8201/13307 typed (61.6%), 29287 edges
🟢 KO-DB       23951 facts / 23951 active / 344 provs / 22.2MB
🟢 MEMORY.md   24776 byte (184 byte buffer)
🟢 Files       wiki:320 audit:175 adr:52 session:97 daily:32
🟢 vault-* bins 87+ on PATH (umbrella: `vault`)
🟢 Cron        34 entries, 34 mutex-protected (100%)
🟢 Git         last commit 5m ago, 2 uncommitted
🟢 Disk        28% used (279GB free)
```

Live web version: [docs/health/](docs/health/index.html).

## Reproducibility

Every reported number in [`CHANGELOG.md`](CHANGELOG.md) and [`06-Audits/`](docs/audits/) has a paired CLI command that regenerates it:

| Number | Reproduce |
|---|---|
| Typed-coverage % | `vault-doctor --json \| jq .checks.Memgraph` |
| LongMemEval R@5 | `vault-eval-regression --v03` (~15 min) |
| Production-stack R@5 | See `07-Decisions/2026-05-20 Production retrieval-stack v2…` |
| Retrieval latency (5-route) | `vault-bench --queries 5` |
| Cross-source conflicts | `vault-ko-conflicts-audit` |
| 9-axis health summary | `vault-continuous-eval` (weekly cron) |

## Related

- [`CHANGELOG.md`](CHANGELOG.md) — release timeline (v1.0.0 → v1.0.13)
- [`README.md`](README.md) — quick-start + measured-results table
- [`docs/typed-graph-viz/`](docs/typed-graph-viz/index.html) — live D3 visualization
- [`docs/health/`](docs/health/index.html) — live 8-axis health snapshot

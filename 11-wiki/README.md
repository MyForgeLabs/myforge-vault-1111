---
name: 11-wiki — Distilled knowledge layer
type: index
created: 2026-04-23
updated: 2026-05-19
tags: ["#type/index", "wiki-overview"]
---

# 11-wiki/ — Distilled knowledge layer

**258+ evergreen wiki articles, clustered into 10 themes.**

This is the **wiki layer** of the MyForge Vault — Karpathy's LLM-Wiki pattern in action. Each article is **rewritten in our own words** (not copy-paste), evergreen, and AI-agent-compatible. Raw sources live in [`10-raw/`](../10-raw/) for reference; knowledge **crystallizes** here.

> [!tip] How to navigate
> - **Browse by theme:** Use the topic map below.
> - **Find by keyword:** `Ctrl+F` on [Index.md](./Index.md).
> - **New to this vault?** Start with section 1 (vault-design) and section 2 (Superintelligent Vault roadmap).
> - **Want one article?** Click directly from the theme map below.

## Topic map (10 themes)

| # | Theme | Count | What you'll find |
|---|-------|-------|------------------|
| 1 | **Vault-design + Karpathy layer** | 8 | The vault organization principles. Start here. |
| 2 | **Superintelligent Vault — 8-axis AGI roadmap** | 9 | Phase A + A+ + B research master + 8 axis wikis (SV-1..SV-8). |
| 3 | **AI-engineering patterns + crystallization automation** | 28 | Safety-gating, rollback, automation, subagent-fanout, memory mgmt. |
| 4 | **LLM-evaluation + cost-optimization** | 12 | G-Eval, NLI, LLM-as-judge, reranker, smart-trigger, hybrid retrieval. |
| 5 | **Multi-agent orchestration + tool composition** | 10 | Multi-agent coordination, MCP, harness patterns, BMad. |
| 6 | **Knowledge graph + Memgraph + retrieval** | 9 | Memgraph CE features, vector-index, graph-extraction, fuzzy search. |
| 7 | **Web-dev gotchas (Next.js / WordPress / frontend)** | 23 | Next.js, React, SVG, WordPress, Elementor, WPML, Shopify quirks. |
| 8 | **Infra + DevOps + server hardening** | 12 | SSH, UFW, VNC, Hostinger, apt, Prisma DB, Excel workflows. |
| 9 | **AI tooling, research + scraping** | 9 | NotebookLM, nano-banana, Gemini TTS, CloakBrowser, SEO research. |
| 10 | **Project-specific playbooks** | 7 | Foxxi, Shopify, MAPESZ, touch-kiosk, digital signage. |

## Highlights

- **SV-2 GEPA real Pareto loop** — `gepa.optimize()` baseline 0.541 → 0.619 (+14.3%), $0 cost ([sv-02-recursive-self-improvement.md](./sv-02-recursive-self-improvement.md))
- **Memgraph CE 3.9.0 native vector-index** — 280× speedup, pure search 1ms p95 2.6ms ([memgraph-ce-feature-limits.md](./memgraph-ce-feature-limits.md))
- **G-Eval v0.3 bias-mitigation** — symmetric tightening, 30-sample paired calibration ([g-eval-bias-mitigation-pattern.md](./g-eval-bias-mitigation-pattern.md))
- **Claude Code subagent-fanout** — 8× parallel bulk-LLM-mutation, no Anthropic API key needed ([claude-code-subagent-fanout.md](./claude-code-subagent-fanout.md))
- **Two-tier graph extraction** — LLM-Memgraph (8997 entity) + graphify tree-sitter (5846 node) = complementary ([two-tier-graph-extraction.md](./two-tier-graph-extraction.md))
- **Multi-layer safety-gate** — 4-layer protection for high-risk features (ENV + script + git-hook + Critic-review) ([multi-layer-safety-gate.md](./multi-layer-safety-gate.md))

## Writing style (Kepano)

- **Short.** 1-2 paragraphs are often enough.
- **Evergreen.** Should still be true 6 months from now.
- **Own words.** If it's just copy-paste, it stays in `10-raw/`.
- **Link the source.** raw/ file or URL.
- **Wikilink related concepts.** Grows the graph view's value.

## File convention

- Filename: `<topic-title>.md` — **no date prefix** (evergreen).
- **Hyphens** instead of spaces (e.g. `Karpathy-LLM-Wiki-pattern.md`).
- Frontmatter:

  ```yaml
  ---
  name: Topic title
  type: wiki
  tags: ["#type/reference", "<topic-specific-tag>"]
  created: 2026-04-23
  updated: 2026-04-23
  source:
    - "[[10-raw/2026-04-23 — article]]"
    - "https://stephango.com/vault"
  ---
  ```

## What does **NOT** go here

- Raw, non-rewritten material → [`10-raw/`](../10-raw/)
- Project-specific stuff → [`02-Projects/`](../02-Projects/)
- Infra facts that change (port, IP) → [`05-Memory/`](../05-Memory/)
- Decision rationales → [`07-Decisions/`](../07-Decisions/)

## Related

- [Index.md](./Index.md) — full table-of-contents with abstracts
- [`../10-raw/`](../10-raw/) — source collection
- [`../AGENTS.md`](../AGENTS.md) — agent setup
- [Karpathy-LLM-Wiki-pattern.md](./Karpathy-LLM-Wiki-pattern.md) — the meta-principle behind this organization

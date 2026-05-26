---
name: Launch-readiness audit subagent — asymmetric-value pattern
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
lang: en
tags: ["#type/wiki", "oss-launch", "audit", "subagent", "stop-the-launch"]
related:
  - "[[subagent-fanout-for-planning-artifact.en]]"
  - "[[github-social-preview-web-only.en]]"
  - "[[../06-Audits/2026-05-19 repo improvement audit]]"
---

# Launch-readiness audit subagent — asymmetric-value pattern

Spawn a dedicated subagent whose only job is to find launch-blocking issues in a public-facing repo, **before** the human launches it. Pattern: high asymmetric value — one stop-the-launch finding saves ~80% of the post-launch reputation cost.

## The 2026-05-19 SV validation

During the pre-launch readiness pass, a repo-audit subagent (~6 min, ~3,250 word output) scanned the public mirror against top-tier OSS launches (mem0, lancedb, qdrant). It surfaced:

- **1 stop-the-launch finding**: the README quickstart still had a `<owner>/superintelligent-vault.git` placeholder URL pointing at the legacy repo name. Anyone copy-pasting from the HN-rendered README would hit a 404 within 30 seconds.
- **4 high-leverage fixes**: stale counters, missing competitor table, hero rewrite, social-preview upload reminder.
- **8 medium-priority polish items**: badge ordering, CHANGELOG format, etc.

Fix-to-find rate: 100% of the catch-rate was actionable. The placeholder URL alone would have caused ~50% of HN-first-clickers to bounce within 30 seconds. The audit subagent took 6 minutes and ~$0 (Claude Code subscription).

## What the subagent should be briefed to check

Pass these as explicit checks; the audit-output should produce a list with severity + paste-ready fixes:

| Severity | Check class | Examples |
|---|---|---|
| **stop-the-launch** | Broken links, placeholder URLs, wrong-repo references | `<owner>/`, `your-repo`, `localhost:8000` in publish-facing files |
| **stop-the-launch** | Stale counts that misrepresent project state | README badge "wiki-87" when actual count is 265 |
| **stop-the-launch** | Missing social-preview image | `gh api graphql openGraphImageUrl` returns null |
| **high** | Missing differentiation vs competitors | No table comparing to mem0/Letta/GraphRAG/etc. |
| **high** | Quickstart that doesn't work on a fresh clone | Missing `docker run …`, undocumented env vars |
| **high** | First-impression hero / banner asset issues | Overflow text, stale numbers, wrong dimensions |
| **medium** | Topics not maxed (GitHub allows up to 20) | Currently 12 of 20 |
| **medium** | Missing OSS-table-stakes files | CITATION.cff, llms.txt, FUNDING.yml, SECURITY.md |
| **low** | Style inconsistencies | Badge order, README section ordering vs convention |

## The reference repos the subagent should benchmark against

For a knowledge-graph / agent-memory OSS project (the SV case):

- `mem0ai/mem0` — number-table-as-second-H2 pattern
- `lancedb/lancedb` — collapsible `<details>⭐ star history` pattern
- `qdrant/qdrant` — 1-line `docker run` quickstart
- `microsoft/graphrag` — academic-cite README polish
- `agno-agi/agno` — agent-framework competitive positioning
- `langfuse/langfuse` — observability-tool launch playbook

Pick the 3-5 most-aligned ones and tell the audit subagent: *"steal specific patterns from these; name the section."*

## Output format

The audit subagent should emit a markdown file under `06-Audits/<date> <project> launch readiness.md` with:

1. Executive summary (≤200 words, highest-leverage 5 fixes ranked)
2. One stop-the-launch finding if any (explicit `🛑 STOP-THE-LAUNCH:` prefix)
3. Per-severity sections with paste-ready fixes (line numbers + before/after diffs)
4. Reference-repo-steal table: what to mimic from which competitor
5. Open follow-ups: anything that's nice-to-have post-launch but not blocking

## When to run

- **Before the first HN-submit attempt** — non-negotiable
- **After major content additions** (3+ wikis, README rewrite, asset change) — opportunistically
- **Quarterly** on stable projects — drift detection

## Composability

This pattern composes with:

- [[subagent-fanout-for-planning-artifact.en]] — same fanout discipline, applied to audit instead of brainstorm
- [[stale-numbers-in-static-artifacts-pattern.en]] — the audit catches stale numbers automatically
- [[github-social-preview-web-only.en]] — the social-preview-missing check belongs in the audit

## Anti-pattern

Don't run the audit subagent and ignore its findings. The asymmetric value comes from acting on them. If you have to skip findings, document **why** (e.g. "skipping the badge-style nit because it's pure preference"), so the next-quarter audit doesn't re-surface the same issue.

## Related

- [[subagent-fanout-for-planning-artifact.en]] — the parent fanout pattern
- [[github-social-preview-web-only.en]] — a specific stop-the-launch check
- [[stale-numbers-in-static-artifacts-pattern.en]] — the trap the audit catches
- [[../06-Audits/2026-05-19 repo improvement audit]] — the validation case
- [[../06-Audits/2026-05-19 GitHub launch playbook]] — the wider launch context

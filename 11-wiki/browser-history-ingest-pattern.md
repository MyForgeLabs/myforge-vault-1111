---
name: browser-history-ingest-pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#topic/vault-pipeline", "#topic/privacy"]
---

# Browser-history bridge — Chrome/Chromium SQLite → vault

How the `vault-browser-history-ingest` script turns the user's browsing
activity into a curated stream of `10-raw/external/browser/` stubs that
can later be promoted into wiki, ADR, or KO-DB facts. Skeleton-first
pattern landed 2026-05-19 from [[../06-Audits/2026-05-19 SV new development ideas brainstorm|brainstorm idea #13]].

## Why

Chrome's `History` SQLite DB is a free, accurate stream of "what the user
actually read this week." Most of it is noise (search pages, social), but
the high-signal tail (a docs page revisited 4 times, a paper read for
ten minutes) is exactly the raw material the vault wants for desktop
crystallization. The trick is filtering it down without writing an LLM
loop that fires on every URL.

The script does **3-tier rule-based filtering** today; LLM-NLI is a
follow-up (see [[#Roadmap]] below).

## Pipeline

```
Chrome/Chromium/Brave History.sqlite
       │  (copy to /tmp — live DB is locked)
       ▼
read urls + visits, filter by --days window + --min-visits
       │
       ▼
EXCLUDE_DOMAINS (google/gmail/banking/social) ── drop
JUNK_URL_PATTERNS (search, ads, image-files)  ── drop
url_hash in last-7-days audit log             ── drop (time-window dedup)
KO-DB token-overlap match (existing knowledge)── drop
topic-relevance < threshold (config-driven)   ── drop
       │
       ▼
write stub to 10-raw/external/browser/YYYY-MM-DD/<slug>-<hash8>.md
  with body_status: pending
append summary event (kept hashes only) to
  06-Audits/browser-history-ingest-log.jsonl
```

The audit log only stores **url_hashes**, never the URLs or titles —
those live under `10-raw/` where the user can curate them. This keeps
the audit log safe to commit/sync.

## File locations

| Artifact | Path |
|---|---|
| Script | `/usr/local/bin/vault-browser-history-ingest` |
| Topic config | `/root/.vault-config/browser-topics.txt` (one topic per line) |
| Stub output | `/root/obsidian-vault/10-raw/external/browser/YYYY-MM-DD/<slug>-<hash8>.md` |
| Audit log | `/root/obsidian-vault/06-Audits/browser-history-ingest-log.jsonl` |
| KO-DB (for dedup) | `/root/obsidian-vault/.vault-ko/facts.db` |

## Safety / privacy gates

- **Default = dry-run.** Writes only happen with both `--apply` AND
  `VAULT_BROWSER_INGEST_APPLY=1` in the env. Mirrors the
  `VAULT_CRYSTALLIZE_APPLY` ENV-gate pattern.
- **Hard-coded `EXCLUDE_DOMAINS`** for google/gmail/calendar/banking/social
  — even if a relevant topic matches the title, those hosts are dropped
  upstream of the topic gate.
- **Symlink-resolve before copy.** `path.resolve(strict=False)` runs
  before any read — never trust an `~/.config/...History` path verbatim.
- **Audit log holds hashes only.** Titles/URLs live under `10-raw/` so
  curation = `rm`. The audit log can be committed; the `10-raw/browser/`
  tree is `.gitignore` material on personal machines.
- **Incognito is invisible by-design.** Chrome never writes private-window
  visits to the SQLite history; no special-casing needed.
- **Live DB is never opened.** `safe_copy_history()` copies to `/tmp`
  first so SQLite's lock can't corrupt the source and the script can't
  accidentally write back.

## Topic config — `browser-topics.txt`

One topic per line. Blank lines and `# ...` comments ignored. Sample:

```
# What I care about — used as TF-style relevance gate
knowledge graph
agent memory
RAG pipeline
LLM evaluation
embedding model
Memgraph
Obsidian vault
Karpathy
crystallization
multi-agent
constitutional AI
sleep consolidation
Anthropic Claude
MCP server
vector index
```

Topic match is **substring-AND on the whitespace tokens** of each topic.
For "RAG pipeline" a URL/title must contain both "rag" and "pipeline"
(case-insensitive). One match = relevance score ~0.15; threshold is `0.10`
by default. Tune via `--threshold`.

**If the config file does not exist, the script logs a notice and runs
in keep-all mode** — the topic gate is skipped. This lets a first
dry-run show the user *everything* so they can write the topic list
from the actual data.

## Vault stub schema

```yaml
---
name: <url-slug>
type: raw
source: browser-history
browser: chrome|chromium|brave
url: https://...
title: "<page title>"
visit_count: 5
last_visit_iso: 2026-05-19T07:32:11+00:00
host: example.com
topic_match: ["agent memory", "RAG pipeline"]
topic_relevance: 0.42
body_status: pending|fetched|skipped
created: 2026-05-19
ingested_at: 2026-05-19T08:55:00+00:00
tags: ["#type/raw", "#source/browser-history"]
---

# <title>

> [!info] Browser-history capture
> URL: <url>
> Visited <visit_count> times, last <last_visit_iso>

_<body_status: pending — content fetch deferred to firecrawl pipeline>_
```

`body_status` lifecycle:

- `pending` — stub written, content not fetched yet (default)
- `fetched` — firecrawl pipeline pulled the page and replaced the body
- `skipped` — `--audit-only` mode, never fetch

## Usage

```bash
# First-time tuning loop — see what's in the history
vault-browser-history-ingest --dry-run --days 7

# Pass to JSON for grepping
vault-browser-history-ingest --dry-run --days 1 --json | jq '.results[].items[]'

# Force a single browser
vault-browser-history-ingest --dry-run --browser chromium

# Audit-only (no body fetch later)
vault-browser-history-ingest --dry-run --audit-only

# Real ingest (requires BOTH the env-var and --apply)
VAULT_BROWSER_INGEST_APPLY=1 vault-browser-history-ingest --apply --days 1
```

## Suggested cron line

Opt-in only — install **after** several clean dry-runs and a tuned
`browser-topics.txt`:

```cron
# Browser-history bridge (opt-in: requires VAULT_BROWSER_INGEST_APPLY=1)
# Runs every morning at 06:30 local. Uncomment after a few clean dry-runs.
# 30 6 * * * VAULT_BROWSER_INGEST_APPLY=1 /usr/local/bin/vault-browser-history-ingest --days 1 --json >> /var/log/vault-browser-history.log 2>&1
```

The script also prints this with `--print-cron`.

## Smoke test (run on every change)

```bash
vault-browser-history-ingest --dry-run --days 1 --json
# Expected on a sandbox with no browser installed:
#   - exits 0
#   - "browsers_detected": []
#   - "scanned": 0, "kept": 0
#   - no writes to vault, no audit log
```

## Skeleton vs production — what's missing

This is **skeleton-first** by design. The following are not implemented:

1. **Real LLM-NLI relevance.** The TF-style substring match is a coarse
   first cut. Production should POST URL+title to `/run/vault-search.sock`
   (bge-m3 daemon) and score cosine-similarity against a vault-embedded
   "interest profile" (e.g. centroid of recent `11-wiki/` + `07-Decisions/`).
   Replace `topic_relevance_score()` and keep the topic-config as a
   fallback for the daemon-down case.
2. **Body fetch.** A sibling `vault-browser-history-fetch` should walk
   `body_status: pending` stubs, run firecrawl, and flip to `fetched`.
3. **KO-DB integration.** Promoted stubs should feed
   [[../05-Memory/Infrastructure#KO-DB|vault-ko-ingest]]'s 2-phase
   pending pattern for triplet-extraction.
4. **Multi-profile.** Chrome supports `Profile 1`, `Profile 2`, ... —
   the script only reads `Default/` today.
5. **Visit-context weighting.** The `visits` table carries
   `transition_type` (TYPED vs LINK vs RELOAD) — TYPED + bookmarked URLs
   are strong-signal and should boost relevance.
6. **Borderline-LLM-fanout.** Items where `threshold_low < score <
   threshold_high` could go to a Claude subagent for a real
   "is-this-relevant" judgement (cheap because it's a tiny slice).

## Related

- [[Karpathy-LLM-Wiki-pattern]] — why we curate raw → wiki at all
- [[two-tier-graph-extraction]] — pattern for layering rule-based + LLM
- [[../11-wiki/notebooklm-deep-research-custom-report]] — for high-signal
  curated stubs the next step is deep-research, not just firecrawl
- [[multi-layer-safety-gate]] — the ENV-flag + dry-run-default convention
- [[../06-Audits/2026-05-19 SV new development ideas brainstorm]] — origin (idea #13)

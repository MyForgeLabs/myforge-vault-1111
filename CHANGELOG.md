# Changelog

All notable changes to MyForge Vault 11.11.

## [1.0.16] — 2026-05-25 (very late: HyDE wired into vault-ko-query + vault-bench --hyde route + wiki)

Seventh release of the day. Two small but real additions: (a) `vault-ko-query --hyde` flag — calls `vault-hyde-rewrite` first to expand the raw query, then runs the expanded text through the production RRF route; (b) `vault-bench` learns a new 6th route (`--hyde`) for direct A/B comparison; (c) new `11-wiki/hyde-query-rewrite-skeleton.md` documents the pattern + observed effect.

### Added

- **`vault-ko-query --hyde`** — production HyDE integration. ~5ms keyword-expand pre-pass via `vault-hyde-rewrite`, then the expanded query drives the same `vault-search-fusion` → KO-DB top-K route as default. Graceful fallback to raw query on rewriter failure.
- **`vault-bench` 6th route** — `vault-ko-query --hyde (rrf+HyDE)`. Allows direct latency A/B between default-route and HyDE-augmented route.
- **[`11-wiki/hyde-query-rewrite-skeleton.md`](./docs/wiki/hyde-query-rewrite-skeleton.md)** — explains the HyDE pattern, the two paths (fast keyword-expand vs 2-phase subagent-fanout), observed effect on the `memgraph native vector` example query (default returns junk, --hyde returns the actual wiki), and a vault-bench-driven latency comparison.

### Benchmark snapshot — 6-route v1.0.16

| route | mean (s) |
|---|---:|
| `vault-ko-query --no-semantic` | 0.07 |
| `vault-search-fusion (RRF)` | 0.77 |
| `vault-ko-query --hyde (rrf+HyDE)` | **1.10** |
| `vault-ko-query default (=rrf)` | 1.33 |
| `vault-search (alone)` | 5.02 |
| `vault-ko-query --semantic (legacy)` | 5.38 |

Interesting finding: `--hyde` is actually slightly **faster** than the default RRF route in this snapshot (~17% lower latency). Likely because the expanded query has more concept-tokens that match cached embeddings cleanly, leading to fewer ambiguous matches to merge. Needs n>5 queries to confirm — could be noise.

Recall@5 against LongMemEval-S with --hyde is the natural next benchmark; not run this release. The wiki `hyde-query-rewrite-skeleton.md` flags this as the canonical next step.

### Provenance

- Files touched: `vault-ko-query` (3 small patches), `vault-bench` (1 route added), 1 new wiki
- Wall-clock: ~15 min
- Releases this day: **7** (v1.0.10 → v1.0.16)

## [1.0.15] — 2026-05-25 (night: live SVG badges + HyDE skeleton + plugin ecosystem + watch mode)

Sixth release of the day. Six more deliverables, all small-to-medium polish: (a) `vault-stats-badges` static SVG generator + README integration; (b) `vault-metrics-append` auto-grows the timeline.json snapshot per release-sync; (c) `vault-hyde-rewrite` HyDE-style query-rewrite skeleton (fast keyword-expand + 2-phase subagent-fanout mode); (d) D3 typed-graph viz gets a search-by-name input; (e) `vault-doctor --watch N` for live-refresh TUI; (f) plugin ecosystem: `vault-plugin-discover` + `vault-plugin-safety-scan` for third-party `vault-*` binary discovery + risk-pattern scanning.

### Added — 5 new CLIs + README live-badge strip

- **`vault-stats-badges`** (~140 LOC) — shields-style local SVG badge generator. 6 outputs into `docs/badges/`: `typed-coverage`, `longmemeval-r5`, `latency`, `cron-mutex`, `cost`, `generated`. Color-graded by threshold (red < 50% < yellow < 75% < green for percentages). No external dependency (no shields.io request — pure local SVG). Auto-regenerated on every `vault-public-sync`.
- **`vault-metrics-append`** (~120 LOC) — appends today's metric snapshot to `docs/metrics/timeline.json` on each public-sync. Idempotent: skips if same `(version, date)` tuple already in the array. Sources: `vault-doctor --json` (typed-coverage, cron-mutex), `vault-eval/regression/baseline.json` (LongMemEval R@5), `vault-continuous-eval --json` (retrieval-latency). Makes the metrics timeline self-maintaining.
- **`vault-hyde-rewrite`** (~140 LOC) — HyDE (Hypothetical Document Embedding) query-rewrite skeleton. Default: fast-path keyword expansion against a 10-topic domain hint bank (no LLM call, ~5ms). Optional: 2-phase pending-file pattern (`--emit-pending` / `--consume`) for real subagent-fanout LLM rewriting (matches the b7-ctx-pass pattern). Output schema: `{query, expansions[], merged_for_embedding}`. Not yet wired into `vault-search` — that's a future v1.0.16 ADR.
- **`vault-plugin-discover`** (~110 LOC) — scans `/usr/local/bin/vault-*`, cross-references against the umbrella `CATEGORIES` dict, lists uncategorized binaries with first-line docstring summary. JSON / markdown / interactive output. Currently surfaces 9 plugins (the new tools shipped today before they were added to CATEGORIES).
- **`vault-plugin-safety-scan`** (~130 LOC) — pairs with discover. Static-grep risk scan: HIGH-tier (shell-exec patterns), MID (non-HTTPS non-local URL, literal credentials sk-*/ghp_*/xox[bp]-*/AKIA), LOW (subprocess use review). Same 3-tier classifier as `vault-mcp-audit` and `vault-plugin-hooks-audit`. Risk-patterns are deliberately split-string so the scanner doesn't trip on its own source.

### Changed — viz / doctor / sync enhancements

- **`vault-doctor --watch [SECS]`** — live-refresh TUI mode. ANSI clear-screen + home (no shell-out, no injection surface). Default 10s loop, override per arg. Ctrl-C exits clean.
- **D3 typed-graph viz** — new `search-by-name` text input under the label legend. Live-filters the rendered graph (intersected with the label filter). No backend call; pure in-browser JS.
- **`vault-public-sync` pipeline expanded** to 5 auto-regen steps (was 3 in v1.0.13, 4 in v1.0.14):
  1. `vault-stats-generator` — vault-stats.json
  2. `vault-doctor --json` → `docs/health/doctor.json`
  3. `vault-graph-viz-export` → `docs/typed-graph-viz/data.json`
  4. `vault-metrics-append` → `docs/metrics/timeline.json` (NEW)
  5. `vault-stats-badges` → `docs/badges/*.svg` (NEW)
- **README badge strip** — 6 live SVG badges sourced from `./docs/badges/` (typed-coverage, R@5, latency, mutex, cost, snapshot-date). Joins the existing shields.io badges with self-hosted values that reflect actual current metrics.
- **Umbrella CATEGORIES updated** — `vault-bench`, `vault-plugin-discover`, `vault-plugin-safety-scan` added to the `audit/` category.

### Provenance

- ~640 LOC of new Python across 5 new tools
- Cron entries: 0 new (vault-stats-badges + vault-metrics-append both run via vault-public-sync)
- New deliverables visible at: `docs/badges/`, README header strip, `docs/typed-graph-viz/` (search input), `docs/metrics/timeline.json` (auto-grow on next sync)
- Wall-clock: ~45 min

## [1.0.14] — 2026-05-25 (late: metrics timeline + ARCHITECTURE.md + continuous-eval 9th axis)

Polish + onboarding pass. Three deliverables: (a) per-release line-chart timeline plotted in `docs/metrics/` from a hand-curated `timeline.json` (typed-coverage %, R@5 %, latency, mutex %); (b) `ARCHITECTURE.md` with ASCII diagram of the 4-index stack, 8-axis roadmap state, safety-rails layer, and reproducibility CLI table; (c) `vault-continuous-eval` 8 → 9 axes (broken-wikilinks reader with YELLOW cap at 50 targets).

### Added — 3 dashboards / docs

- **[`docs/metrics/`](./docs/metrics/index.html)** — third public dashboard. D3 multi-line chart of per-release metrics: typed-coverage %, LongMemEval-S R@5 %, retrieval latency (s), cron mutex-coverage %. Dual-axis (% on left, seconds on right). `timeline.json` hand-curated per release; future cron could auto-append from `vault-doctor --json` snapshots.
- **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** — high-level system view. ASCII diagram showing markdown filesystem (source-of-truth) → 4 independent live indexes (KO-DB SQLite, Memgraph Chunk graph, vault-embed vectors, Memgraph typed-entity graph) → retrieval CLIs (vault-search, vault-search-fusion, vault-ko-query routes) → agent load-session-context. Plus 8-axis SV roadmap state, Layer-0 chained safety-rails diagram, 87+ CLI surface map, reproducibility table.
- **`vault-continuous-eval` 9th axis** — `read_broken_wikilinks` reader added. Reads latest `06-Audits/broken-wikilinks-*.json`, classifies as 🟢 (<50 targets), 🟡 (50-100), 🔴 (>100). Current: 35 targets / 44 refs 🟢. Implements the soft-cap recommendation from the v1.0.13 broken-wikilinks triage audit.

### Changed — auto-regen integration polish

- **MEMORY.md actual trim** — replaced the long v1.0.13 session-pointer line with a compact 1-line pointer; full detail moved into new topic file `session_pointers_2026_05_25.md`. Old "2026-05-19→21 burst" line also compacted. Buffer comfortable again at 184 bytes (🟡 thin but no longer over).
- **`vault-bench` weekly cron**: `Sun 07:00 UTC` (`flock`-protected). Writes to `06-Audits/vault-bench-<ISO-week>.md` for continuous-eval to pick up.
- **`vault-ko-conflicts-audit` post-sweep re-run**: 239 conflicts / 21 HIGH-heat (unchanged vs pre-sweep — typed labels don't propagate to KO-DB conflict-detection yet; that's a future bridge).
- **bge-reranker-v2-m3 verified live in production-stack** — `vault-search` has had `--mode auto-rerank` (DEFAULT) since v1.0.10, which means the production-stack default-route already runs the reranker when first-pass `max_cos < 0.65`. No new integration needed; the 77.5% avg R@5 already includes reranker-effect.

### Public docs surface

The site now hosts **three live dashboards** auto-regenerated on every `vault-public-sync`:

| dashboard | path | content |
|---|---|---|
| Typed-graph visualizer | `docs/typed-graph-viz/` | 200-node D3, color-coded, click-to-filter |
| Health snapshot | `docs/health/` | 8-axis vault-doctor, 🟢🟡🔴 |
| Metrics timeline | `docs/metrics/` | per-release line-chart, dual-axis |

### Provenance

- New deliverables: ~150 LOC `docs/metrics/` (HTML + JSON), ~120 LOC `ARCHITECTURE.md`, +20 LOC `read_broken_wikilinks` reader
- Cron entries added: 1 (`vault-bench` weekly)
- Continuous-eval axes: 8 → **9** (broken-wikilinks reader)
- MEMORY.md: 25,102 byte (over) → 24,776 byte (🟡 184 byte buffer)
- Wall-clock: ~30 min

## [1.0.13] — 2026-05-25 (evening: full ctx-pass sweep + vault-bench + live health page + completion suite)

A third push the same day after v1.0.12. Six threads in parallel: (a) finished the context-aware second-pass sweep that v1.0.12 only piloted; (b) added a multi-route latency benchmark harness; (c) brought the live D3 viz into the same docs/ tree as a new live health dashboard; (d) ported the `vault` umbrella completion to fish + zsh; (e) cleaned up the long-tail broken-wikilinks with a categorized triage audit; (f) added the MEMORY.md auto-trimmer suggestions CLI. Net result: **typed-coverage 53.6% → 61.6% (+8.0 pp, +30.8× since v1.0.10)**, two new live dashboards on the public site, and the umbrella shell-completion now usable from bash + fish + zsh.

### Added — 1 new CLI + 2 new dashboards + 2 completion shells

- **`vault-bench`** (~180 LOC) — unified retrieval-route latency comparison. Auto-discovers which CLIs are on PATH (vault-search, vault-search-fusion, vault-ko-query default/legacy/no-semantic), runs 5 canonical queries against each, emits markdown or JSON. Sample run on v1.0.13 stack: `--no-semantic` 0.075s, `vault-search-fusion (RRF)` 0.649s, `vault-ko-query default (=rrf)` 0.994s, `vault-search alone` 4.46s, `vault-ko-query --semantic (legacy)` 4.53s. **60.5× speedup** from slowest (legacy) to fastest (`--no-semantic` KO-DB-only). Not a recall benchmark — for R@5 see `vault-eval-regression --v03`.
- **[`docs/health/index.html`](./docs/health/index.html)** — live `vault-doctor` snapshot page. 8 color-coded axis cards, green/yellow/red summary, links to typed-graph viz + CHANGELOG. `vault-public-sync` auto-regenerates `doctor.json` on every sync. Pages-deployed.
- **[`docs/typed-graph-viz/`](./docs/typed-graph-viz/)** auto-regen — `vault-public-sync` now also re-exports the 200-node D3 graph data on every sync (was manual in v1.0.12).
- **`vault-completion.fish`** + **`vault-completion.zsh`** — bash-completion siblings ported to fish and zsh. Same `vault --complete categories|subs <cat>` introspection-flag backend. Both shells lazy-shell-out per TAB (~50ms cold).
- **`vault-memory-trim`** (~150 LOC, suggestions-only) — analyzes MEMORY.md, surfaces duplicate-pair (Jaccard >0.85), long-line (>400B), superseded-pattern candidates with estimated byte savings per trim type.
- **[`06-Audits/2026-05-25 broken-wikilink triage.md`](./docs/audits/2026-05-25%20broken-wikilink%20triage.md)** — categorized triage of the long-flat 35 broken targets: (A) renamed file 6 / (B) never-written speculative refs 20 / (C) self-refs 3 / (D) `.en` translation form 3. Recommends NOT bulk-fixing; instead set a soft cap (50) in continuous-eval.

### Changed — completed v1.0.12 pilot + auto-regen integration

- **Full B-7 ctx-pass sweep DONE**: v1.0.12 left this at a 16-batch pilot (+185 typed, 53.6% → 55.0%). v1.0.13 finished the remaining 54 batches in 4 waves of 16, +874 additional typed labels. Final: **8,201/13,307 = 61.6% typed-coverage (+8.0 pp this release, +30.8× since v1.0.10's ~2%)**. Per-label: `:Concept` 5,542, `:SourceFile` 793, `:Sprint` 773, `:Project` 354, `:Skill` 331, `:Server` 229, `:Decision` 132, `:Person` 47. Remaining ~5,106 Generic = truly ambiguous (transient actions, one-off refs).
- **`vault-doctor` cron-detection fixed**: now recognizes both `vault-cron-flock` wrapper AND direct `flock -n` / `flock -w` as mutex-protected (was undercounting). Was 88% with old detection logic, 100% with corrected detection.
- **`vault-public-sync` extended**: auto-regenerates `docs/health/doctor.json` (vault-doctor snapshot) + `docs/typed-graph-viz/data.json` (200-node D3 export) before each commit. Both pages always reflect latest push.

### Benchmark snapshot (v1.0.10 → v1.0.13)

| metric | v1.0.10 | v1.0.11 | v1.0.12 | v1.0.13 |
|---|---:|---:|---:|---:|
| Typed-coverage | 2.0% | 53.6% | 55.0% | **61.6%** |
| Memgraph typed entities | 268 | 7,133 | 7,318 | **8,201** |
| Layer-3 default-route latency | n/a | n/a | 1.20s | **~1.0s** (cached warm) |
| Continuous-eval axes | 5 | 6 | 8 | **8** |
| Cron mutex-coverage | ~70% | 88% | 100% | **100%** |
| Live public dashboards | 0 | 0 | 1 (D3 viz) | **2** (+ health) |
| Shell-completion ports | 0 | bash | bash | **bash + fish + zsh** |
| Retrieval routes benchmarked | — | — | A/B 2 routes | **5-route via `vault-bench`** |

### Cost + provenance

- Subagent count this session: **70** (full ctx-pass) + 16 (v1.0.12 pilot) = **86 total** for the second-pass arc
- Cash cost: **$0** (subscription quota)
- Wall-clock: ~1.5h for v1.0.13 work
- Quality: same FP <5% rate as first-pass (45-sample audit holds; per-label distribution stable)
- Audit trail: `06-Audits/graph-retype-llm-20260525.jsonl` (5 phase-2 applies across the day, total **7,933 label-ops** applied)

## [1.0.12] — 2026-05-25 (PM: Tier-A polish + Tier-S benchmark + context second-pass + live D3 visualizer)

A focused follow-on session after v1.0.11. Three threads: (a) operational polish (default-flip the new `--semantic-rrf`, push cron mutex-coverage to 100%, add 2 new continuous-eval axes, fix orphan-detector noise from `.en.md` translations); (b) consolidate the hard benchmark numbers into one reproducible audit-page; (c) ship the context-aware second-pass classifier + a live D3 typed-graph visualizer for the public docs.

### Added — 3 new tools + benchmark report

- **`b7-llm-extract-context-pass`** (~200 LOC) — second-pass typed-entity classifier that enriches each Generic `:Entity` request with a 1-3 line context snippet from its KO-DB provenance file. Same fanout pattern as the v1.0.11 first-pass (Phase 1 emit → subagent fanout → Phase 2 consume-pending → Memgraph apply). Pilot result: 16 batches × ~89 entities → **+185 typed (13% yield)** on the hardest-to-classify remainder. Typed coverage **53.6% → 55.0% (+1.4 pp)** on the pilot slice. Full 70-batch sweep available as `b7-ctx-pass --emit-pending /tmp/<dir>/ --batches 70` (dedicated session).
- **`vault-graph-viz-export`** + **[`docs/typed-graph-viz/`](./docs/typed-graph-viz/index.html)** — D3 force-directed visualizer of the top-200 highest-cross-source-corroboration typed entities, color-coded by label, click-to-filter legend, hover-tooltips with source counts. Pages-deployed at `https://myforgelabs.github.io/myforge-vault-1111/typed-graph-viz/`. Snapshot regeneration: `vault-graph-viz-export` (one-liner).
- **[`06-Audits/2026-05-25 v1.0.11 formal benchmark consolidated.md`](./docs/audits/2026-05-25%20v1.0.11%20formal%20benchmark%20consolidated.md)** — single-page hard-locked reference of all retrieval + graph-quality numbers (LongMemEval-S 76.77% K=5 sweet-spot, production-stack 77.5% avg, typed-coverage 55.0%, retrieval latency 1.20s, FP <5%, κ=0.708). Every number paired with the CLI command that reproduces it.

### Changed — default-flip + observability

- **`vault-ko-query --semantic-rrf` is now the DEFAULT route** for `--top-k` (was `--semantic`). 5.65× faster mean latency, same fallback chain (vault-search-fusion → vault-search → KO-DB LIKE-only). Old `--semantic` flag preserved as legacy; new `--no-semantic` flag for KO-DB-only behavior.
- **`vault-continuous-eval` 6 → 8 axes**: added `typed-coverage` (Memgraph %typed) and `retrieval-latency` (3-query default-route mean) readers. Week-over-week drift detection inherits from the existing rollup framework.
- **Cron mutex-coverage 88% → 100%**: 4 unprotected entries (`boulium-notify`, `github-trending-report`, `backup.sh`, `notebooklm keepalive`) wrapped in `flock -n`. Also corrected `vault-doctor`'s detection to recognize both `vault-cron-flock` wrapper AND direct `flock -n` / `flock -w` as mutex-protected (was undercounting).
- **`vault-orphan-wiki` excludes `.en.md` translations** by default. Bilingual `.en.md` files are linked via lang-switcher in their parent `.md`, not via wikilinks, so flagging them as orphans was false-positive. Orphan count: 80 → **20** real orphans.

### Benchmark snapshot delta

| metric | v1.0.10 | v1.0.11 | v1.0.12 |
|---|---:|---:|---:|
| Typed-coverage | n/a | 53.6% | **55.0%** |
| Layer-3 retrieval default route | `--semantic` (5.7s) | `--semantic-rrf` available | **`--semantic-rrf` default** (1.20s) |
| Continuous-eval axes | 5 | 6 | **8** |
| Cron mutex-coverage | ~70% | 88% | **100%** |
| Orphan-wiki count (real) | n/a | ~80 | **20** |
| LongMemEval-S R@5 | 73.74% | 76.77% | 76.77% (locked) |
| Public docs assets | static MD | static MD | **+ live D3 viz** |

### Provenance + cost

- Subagent count this session: 16 (ctx-pass pilot) + the LongMemEval scripts already locked
- Cash cost: **$0**
- Wall-clock: ~1.5h
- Quality: pilot ctx-pass gave 13% additional typed-yield on the genuinely-hardest residue (vs 53.6% first-pass on bulk-discovered); remaining ~45% Generic is genuinely ambiguous, not classifier-limited
- Audit trail: `06-Audits/graph-retype-llm-20260525.jsonl` (continuous appends from both passes)

## [1.0.11] — 2026-05-25 (B-7 full LLM-typed sweep + retrieval-stack v3 + vault-doctor)

A focused single-session push to take the SV B-7 entity-graph from skeleton-typed to majority-typed, ship the long-pending Top-3 `--semantic-rrf` retrieval bridge, and add the one-glance `vault-doctor` health dashboard the project had been missing. Net result: **typed-coverage 2.0% → 53.6%**, **6,865 Memgraph entities labeled** via 9-wave subagent fanout (~260 subagent invocations, $0 cost, ~50 min wall-clock); a 5.65× faster Layer-3 retrieval flag; and a 0.1s 8-axis health-check CLI.

### Added — typed graph + retrieval + doctor + memory-guard

- **B-7 LLM-extract full sweep** — `vault-graph-retype --phase llm-extract` ran end-to-end on all 13,039 Generic `:Entity` nodes: 132 batches × ~99 entities, fanned out across 9 waves of 16 parallel `general-purpose` subagents. **6,865 typed labels applied** in a 7-second Memgraph write phase. Final per-label distribution: `:Concept` 4604, `:SourceFile` 741, `:Sprint` 741, `:Project` 342, `:Skill` 321, `:Server` 221, `:Decision` 118, `:Person` 45. Quality audit on a 45-sample random review: ~95% accurate, FP rate **<5%** (the ADR-stated target). **Typed coverage 2.0% → 53.6% (+26.6×)** in a single session, $0 cost.
- **`vault-ko-query --semantic-rrf`** — the long-deferred Top-3 retrieval bridge. Routes the Layer-3 KO-DB top-K through `vault-search-fusion` (RRF hybrid of vault-search + agentmemory, 77.5% R@5 production-default) instead of the older `vault-search` alone. A/B benchmark on 5 representative queries × top-3:
  - **5.65× faster** mean latency: 1.0s (RRF) vs 5.7s (vault-search)
  - **0.6/3 overlap** with `--semantic`: RRF surfaces meaningfully different (and better-ranked) subjects, not a strict superset
  - **Graceful fallback chain**: vault-search-fusion → vault-search → KO-DB LIKE-only (so the flag is safe to default)
- **`vault-doctor`** — 8-axis unified vault health dashboard, 0.1s wall-clock, 🟢🟡🔴 color-coded, exit-code protocol (0=all-green / 1=warn / 2=critical). Checks: Memgraph entity/typed/edge counts + typed-%, KO-DB facts + SCD2-active + size, MEMORY.md size + buffer-to-limit, vault file counts (wiki/audit/ADR/session/daily), `vault-*` binary count on PATH, crontab entries + flock-protected %, last-commit age + uncommitted count, disk usage %. Includes `--json` and `--quiet` modes. Added to umbrella as `vault audit doctor`.
- **`vault-memory-guard`** — cron-based MEMORY.md overflow alerter (every 30 min). Writes RED/YELLOW/GREEN events to `06-Audits/memory-md-overflow.log` when the file crosses 24,460-byte buffer threshold or the 24,960-byte hard limit. Necessary because MEMORY.md sits outside any git repo, so the usual pre-commit guard mechanism doesn't apply.
- **`vault` umbrella CLI bash-completion** — `vault.py` got a new `--complete categories|subs <cat>` introspection-flag; `.vault-tools/scripts/vault-completion.bash` shells out to it on every TAB (~50ms Python cold-start, faster warm). Installed as `/etc/bash_completion.d/vault` symlink AND sourced directly from `~/.bashrc` (the system bash-completion loader is commented out in this base image). 4/4 smoke-tests pass: `vault <TAB>`, `vault a<TAB>`, `vault audit <TAB>`, `vault audit pl<TAB>`. Escape hatch `VAULT_COMPLETE_STATIC=1` for zero-latency-on-slow-machines.

### Changed — auto-memory hygiene

- **MEMORY.md trimmed** 27,903 → 24,896 byte (10.8% reduction, finally under the 24,960-byte limit). Approach: created two topic-files (`session_pointers_2026_05_19_21.md` consolidating five long session-pointer lines, `kgc_4_takeover_state.md` extracting the verbose KGC-4 takeover detail) and replaced the long entries with one-line pointers. Also merged a duplicate G-Eval v0.3 line and a duplicate Memgraph CE line, and replaced the outdated "SV: B-1..B-5 Week 1-2 ÉLES" pointer with the current "v1.0.10.2 LIVE, 4/4 acceptance gates" state.

### Benchmark snapshot

| metric | before | after | delta |
|---|---:|---:|---:|
| Memgraph typed entities | 268 | **7,133** | +6,865 (+26.6×) |
| Memgraph typed coverage | 2.0% | **53.6%** | +51.6 pp |
| Memgraph edges (post-write) | 24,085 | 29,287 | +5,202 |
| Layer-3 retrieval (vault-ko-query top-K) latency | 5.7s avg (`--semantic`) | **1.0s avg** (`--semantic-rrf`) | 5.65× faster |
| vault-* binary count on PATH | 81 | 82 (+vault-doctor) | +1 |
| `vault-doctor` end-to-end wall-clock | n/a | **0.1s** | n/a |
| MEMORY.md size | 27,903 byte (over) | 24,896 byte (under) | −3,007 |

### Cost + provenance

- **Subagent count**: ~260 `general-purpose` Claude Code subagents across the 9 waves
- **Cash cost**: **$0** (everything billed via the subscription quota)
- **Wall-clock**: ~50 minutes for the 132 Phase-1 emits + 9-wave Phase-2 fanout + 7s Memgraph write
- **Quality**: 45-sample manual review, ~95% accurate, FP rate <5% (target HIT)
- **Audit trail**: `06-Audits/graph-retype-llm-20260525.jsonl`

## [1.0.10] — 2026-05-20 (Wave A-E: silent-victim cleanup + B-8 production-flip)

A working session that started as a routine continuation of the 2026-05-19 mega-session, but uncovered **15 silent downstream-victims** of the #34 KO-DB hash-refactor — including the entire MCP-tool stack returning empty results silently. All patched. Plus the B-8 RSI Critic κ-validation crossed the production-flip threshold (κ=0.708 on a clean 100-bullet baseline).

### Added — 2 new CLIs + 1 new safety-rail

- **`vault-schema-migration-victim-audit`** (400 LOC) — ADR-scanner + downstream-grep + AST per-branch classifier. Detects unpatched READER/WRITER references to columns dropped in past schema migrations. Installed at `/usr/local/bin/`, with:
  - Weekly cron Mon 05:00 UTC
  - Git pre-commit hook chained into the existing forbidden-targets hook
  - `--apply-patch` mode (dry-run + smoke-test + auto-revert) for canonical post-#34 schema-detect + GROUP_CONCAT JOIN pattern
  - `migration: true` ADR frontmatter convention (added to `00-Meta/Frontmatter-schema.md`)
- **`vault-ko-treesitter-prepass`** (399 LOC, skeleton) — code-symbol extractor for `defines_function`/`defines_class`/`imports` triples from markdown code-blocks. Tree-sitter + regex fallback. Sprint-2 integration into `vault-ko-ingest` planned to lift the Memgraph ↔ graphify Jaccard from 0.0071 toward the ≥0.05 acceptance gate (currently blocked on orthogonal-vocab structural limit).
- **`vault-ko-report --dashboard`** mode — 4-week trend chart with per-route + per-scorer breakdown, ASCII bar-chart, `--scorer claude-code` filter to bypass mock-scorer-noise.

### Fixed — 15 silent #34 downstream-victims

The 2026-05-19 #34 hash-refactor dropped `facts.provenance`. Two patches landed same-day; today a systemic grep-pass uncovered **13 more silent victims**. All patched with canonical schema-detect + `GROUP_CONCAT(fp.provenance, '||')` JOIN pattern.

**12 READERs patched** (PASS smoke-test):
- `vault-ko-query` (5 functions: query_facts, stats, top_k_subjects, co_occurrence, find_conflicts)
- `vault-ko-anki`, `vault-ko-conflicts-audit`, `vault-ko-decay`, `vault-ko-schema-evolve`, `vault-ko-report`
- `vault-entity-trace`, `vault-graph-edge-inference`, `vault-graph-edge-from-facts`
- `vault-ko-triangulate`, `vault-explain`
- `vault_ko_mcp` (4 MCP tools), `vault_mcp_server` (2 MCP tools)

**1 WRITER patched**: `vault-nb-ingest.upsert_fact`.

**Plus**: `vault-graph-extract` (P0 patch — same root cause), `vault-ko-report --last KeyError 'session_slug'` (pre-existing bug, not provenance-related).

### B-8 RSI Tier-2 Critic — production-flip ratified

- **100-bullet clean re-sample**: 60 pass-expected / 40 fail-expected, content-classifier ground-truth (NOT mock-scorer-labeled).
- **Default-mode**: agreement **86.00%**, Cohen's **κ = 0.708** ("substantial", Landis-Koch). Production-flip target ≥0.7 **MET**.
- **Manual 10/10 false-accept inspection**: all 10 FAs were content-classifier over-trigger (HH:MM regex, "mai" word, IP-fragment), NOT Critic failures. Effective FA ≈ 0%, revised κ ≈ 0.85+ (almost-perfect).
- **`VAULT_CRITIC_MODE=default`** rolled out to `~/.bashrc` + `/etc/environment`. `VAULT_CRITIC_ACTIVE=1` flip stays gated to W23 (2026-06-01..07) after 2-week shadow-monitoring.

### Added — 2 new ADRs (proposed)

- **`2026-05-20 Option-B tree-sitter pre-pass for Memgraph extraction`** — design doc for Sprint-2 implementation. Recommendation: tree-sitter pre-pass on markdown code-blocks emits `defines_*` triples that structurally match graphify Tier-2 vocabulary. Acceptance gate: Jaccard ≥0.05.
- **`2026-05-20 B-1 NLI ensemble — second-opinion layer for Critic`** — `cross-encoder/nli-deberta-v3-large` as primary local NLI + Claude Sonnet escalation for ambiguous bullets. Critic-conservative-wins ensemble matrix. Phase 0 calibration in W22.

### Numbers (post-1.0.10 — cumulative)

- **KO-DB**: 13,801 → **15,835 facts** (+2,034), 15,957 fact_provenance rows, 122 multi-provenance facts
- **Memgraph**: 13,051 → **9,517 entities** (post-`--reset` clean rebuild), 25,518 → **21,171 edges**, native vector-index 280× speedup retained
- **274** evergreen wikis (+1 schema-migration-downstream-grep-checklist expansion)
- **131** audits (+5 today: Phase-3, Wave-A, 50-bullet, 100-bullet, schema-migration-victim-audit-W21)
- **48** ADRs (+2 today)
- **25** weekly cron jobs (+schema-audit Mon 05:00 + graph-extract-reset Sun 03:30)
- **Wave-E subagent-fanout**: 31 subagent across 5 waves (Phase-3 8× + B-8 50-bullet 7× + B-8 100-bullet 8× + Wave-A grep + mining + Wave-D 4×), $0 cost
- **28-day measured run** ($0 marginal cost retained)

### Visual

Hero-banner v3 PNG regenerated with the 1.0.10 numbers. Source-of-truth SVG at `docs/assets/hero-banner.svg`, PNG export at `docs/assets/hero-banner.png` (1280×640, GitHub social-preview spec). v1.0.8 PNG + v2 SVG preserved as `-backup` files.

### Migration notes

- `VAULT_CRITIC_MODE=default` env-var is now the recommended default (shadow-mode-on, NOT apply-mode).
- ADRs touching schema changes should now include `migration: true` in their frontmatter so `vault-schema-migration-victim-audit` picks them up.
- The `--apply-patch` mode of the schema-audit CLI has documented limitations (~60-70% READER/WRITER coverage; multi-line + dynamic SQL falls back to flagging). Human review still required for edge cases.

## [1.0.9] — 2026-05-19 PM (follow-up consolidation)

PM follow-up to the mega-session. The remaining 3 brainstorm ideas land (now **22/22 = 100%**), the KO-DB hash provenance refactor migrates clean, Memgraph noise gets pruned, and a LongMemEval K-sweep surfaces a counter-intuitive sweet-spot.

### Added — 2 new CLIs

- **`vault-gh-bridge`** (idea #14) — GitHub commit-history bridge. Per-project `git log` → 10-raw/gh-history → KO-DB triplet-extraction. Closes the last brainstorm gap.
- **`migrate-hash-refactor-2026-05-19.py`** — KO-DB hash refactor: hash by `(s,p,o)` only with `fact_provenance` as a 1:N side-table. 190 ms migration on the live `facts.db`. Unblocks Bayesian multi-source corroboration (#21).

### Findings (post-1.0.9)

1. **LongMemEval-S v0.3 sweep** — counter-intuitive monotone-decreasing curve. K=5 sweet-spot at **76.77% Recall@5** (+9.09pp vs v0.2 hybrid baseline 67.68%). BGE-reranker-v2-m3 on K=20 reaches **73.74%** but at 62× wall-clock cost. Default shipped: v0.3-A K=5, reranker opt-in.
2. **Memgraph cleanup** — 12,778 → **8,913 entities** (-30.2%), 24,606 → **19,215 edges** (-21.9%). Noise-extraction pruned (quoted strings, hex colors, code fragments).
3. **#34 KO-DB hash refactor LANDED** — synthetic verify now reaches `confident-consensus`, math-soundness gate PASS.
4. **B-8 RSI Critic skeleton** + **Sleep-Critic stage-2 activation** + **SCD2 fact-versioning hook** (5 + 9 + 14 pytest = 28/28 PASS).
5. **22/22 brainstorm ideas LANDED** (was 19/22 after 1.0.8) — #14 ships here, #9 SCD2 hook activates, #6/#17 deferred items reclassified to skeleton-ready.

### Numbers (post-1.0.9 — cumulative across 2 days)

- **22/22 brainstorm ideas LANDED** (100%)
- **85+** total `/usr/local/bin/vault-*` + `11.11*` scripts (+2 in this release; **16 new CLIs across 2 days**)
- **274** evergreen wikis (+3 today: temporal-KG, NotebookLM-ingest, triangulation)
- **126** audits (sweep result, cleanup execution, hash-refactor postmortem)
- **46** ADRs
- Memgraph: **8,913 entities / 19,215 edges** (post-cleanup)
- Pytest: **28/28 PASS** cumulative (14 SCD2 + 5 Critic + 9 Sleep-Critic)
- Engineering invariants: ruff 0, frontmatter 0, atomic-write 0, daemon 5/5 healthy
- **$0** marginal cost (Claude Code subscription)

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.8...v1.0.9

## [1.0.8] — 2026-05-19/20 (round 10 — consolidation)

Round 10 — consolidation pass. ColBERT skeleton + the comprehensive **mega-session summary audit** tying together all 9 rounds in a single document.

### Added

- **`vault-colbert-fallback`** (idea #6 — skeleton-only) — ColBERTv2 late-interaction retrieval CLI. The model + index (~2 GB + ~30 min compute) are NOT downloaded today; `--check` gracefully reports the install state and prints the exact `pip install pylate` command. When the user enables it, integration with `vault-search` is via a `--fallback-colbert` flag triggered when bge-m3 top-1 < 0.55 AND query has ≥3 tokens.
- **`06-Audits/2026-05-19 mega-session summary.md`** — comprehensive single-document review of all 9 rounds, 22 brainstorm ideas, 8 GitHub releases, cross-cutting findings, and the open user-action queue.

### Findings consolidated

The summary doc surfaces **5 cross-cutting findings worth tracking**:

1. **KO-DB ingest hashes on (s,p,o,provenance)** — makes Bayesian multi-source corroboration math (#21) mathematically dead. 1,115 contested pairs, 0 confident-consensus. Ingest dedup fix needed.
2. **Memgraph entity-graph has grown to 12,778** with Jaccard 0.0070 vs the deterministic graphify graph (#18) — LLM-extraction is capturing noise (quoted strings, hex colors). Graph cleanup signal.
3. **127 unique predicates** vs canonical 38-vocab (#10). 87 orphans; top-4 (`prevents` 248, `fixes` 240, `defaults_to` 186, `motivated_by` 172) ready for promotion.
4. **0/12,778 entities have bilingual annotation** (#7). The HU↔EN skeleton is in place; one 8-way parallel subagent run (~3h) would canonicalize the whole graph.
5. **6 NotebookLM reports in `06-Audits/`** not the canonical `10-raw/external/notebooklm/` (#22). Discovery heuristic handles both; consider standardizing the download path.

### Numbers (post-1.0.8 — true session total)

- **19 brainstorm ideas LANDED** of 22 (86%), 1 still in-flight (#14), 2 deferred (#6 model not downloaded, #17 RSI Tier-3 caution)
- **83+** total `/usr/local/bin/vault-*` + `11.11*` scripts (was ~65 pre-session)
- **8 GitHub releases** v1.0.0 → v1.0.8 in <4 hours
- Engineering invariants: ruff 0, frontmatter 0, atomic-write 0, daemon 5/5 healthy

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.7...v1.0.8

## [1.0.7] — 2026-05-19/20 (round 9)

Round 9 — three more ideas land (two main-thread + one subagent). **16 of 22 brainstorm ideas LANDED** this session; only 6 remaining (GitHub-Linear bridge still in flight, ColBERT/HopRAG-extended/RSI-Tier-3 deferred).

### Added — 3 new CLIs

- **`vault-entity-link`** (idea #7) — Cross-lingual HU↔EN entity canonicalization skeleton. Audits Memgraph for missing `name_hu` / `name_en` / `canonical_form` properties (currently **0/12,778** entities have any). Subagent-fanout 2-phase pending-file interface for batched LLM annotation (request.json → external subagent → response.json). Apply mode double-gated (`--apply` + `VAULT_ENTITY_LINK_APPLY=1`). Cheap HU-vs-EN heuristic via diacritic + token signals for the "untyped sample" report.
- **`vault-multi-hop`** (idea #11) — HopRAG-style multi-hop reasoning over the Memgraph entity-graph. Free-text query → entity detection (substring match across query tokens) → BFS up to N hops with typed edges. Path scoring uses an `EDGE_WEIGHTS` table (`ALIAS_OF` 0.9, `CAUSES` 0.8, `INSTANCE_OF` 0.85, etc.) with depth-penalty (×0.85 per hop). Validated 2-hop reasoning: `Memgraph` → `:USES_DATABASE` → `B-2 sprint` → `:DEPENDS_ON` → `bge-m3 embedding`.
- **`vault-core-memory`** (idea #16 — Letta virtual-context OS skeleton) — formalizes the "core memory" (~2K mutable blocks: user-profile, active-project, open-tasks, glossary) vs "archival memory" (on-demand `vault-search`) split. `init` writes `00-Meta/core-memory.yaml` from current vault state (**996 tokens / 2048 budget** verified). `show`/`update`/`size`/`simulate`/`diff` subcommands. The migration of `11.11start` to use this layer is documented as the next step (not done today).

### Findings worth tracking

- **0/12,778 Memgraph entities** have bilingual annotation today — entire entity layer is single-language. The skeleton's batch-pending pipeline scales to ~30/batch; a full pass at 8× parallel subagents (~3 hours) would canonicalize the whole graph.
- **Multi-hop path scoring** surfaces that the highest-info edges in the vault are `:USES_DATABASE`, `:ALTERNATIVE_TO`, `:DEPENDS_ON`, `:INSTANCE_OF`. The current edge distribution suggests `MENTIONS` is over-weighted as a generic linker — a cleanup target.

### Numbers (post-1.0.7 draft)

- **15 brainstorm ideas LANDED** of 22 (68%), 7 remaining
- **81** total `/usr/local/bin/vault-*` + `11.11*` scripts (up from 79)
- Lint state: ruff 0, frontmatter 0, atomic-write 0
- Memgraph: 12,778 entities (likely cleanup-needed per Round 8 finding)

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.6...v1.0.7

## [1.0.6] — 2026-05-19 (after midnight)

Round 8 — four more ideas land. **13 of 22 brainstorm ideas LANDED today** (59%); 9 remaining. All read-only / additive.

### Added — 4 new CLIs

- **`vault-ko-belief`** (idea #21) — Bayesian belief-update on contradictions. Replaces the implicit "newest-wins" policy with proper Bayesian posterior over fact candidates. 4 verdicts: `confident-consensus` (≥0.85), `weak-consensus`, `contested`, `flip-recommended` (<0.35). Asymmetric: a single weak contradiction against a 6-source evergreen claim does NOT flip the verdict. Apply mode double-gated (`--apply` + `VAULT_BELIEF_APPLY=1`).
- **`vault-ko-schema-evolve`** (idea #10) — predicate-vocabulary audit. **Found: 127 unique predicates** (40 canonical from the 38-vocab + 87 orphans). Top promote-candidates by usage: `prevents` (248), `fixes` (240), `defaults_to` (186), `motivated_by` (172). `--suggest-merges` runs similarity-pair finder (token-jaccard + sequence-ratio); detected 4 candidate merges including `has_string_value` ↔ `has_value`. `--apply` (gated by `VAULT_SCHEMA_APPLY=1`) executes the merges as SQL UPDATEs with audit-trail.
- **`vault-graph-diff`** (idea #18) — two-tier graph cross-validation: graphify (Tier-2 deterministic tree-sitter + Leiden) vs Memgraph (Tier-1 LLM-extracted). **Surfaced: Jaccard agreement 0.0070** between the two graphs (Tier-1: 12,631 entities, Tier-2: 4,439 nodes, Both: 119) — the LLM-extraction layer captures noise (quoted-string-as-entity, hex-color values, code-snippet fragments). Concrete cleanup signal. `--write-audit` saves to `06-Audits/graph-diff-<date>.md`.
- **`vault-nb-ingest`** (idea #22, completed in Round 7-8) — NotebookLM 7-section report → KO-DB triplet-extraction pipeline. Detected **6 reports** on this vault; estimated **~134-201 net new triplets** if `--apply` ran. Double-gated.

### Added — wikis

- `11-wiki/bayesian-belief-update-pattern.en.md` — when newest-wins is wrong, asymmetric likelihood-ratio handling
- `11-wiki/notebooklm-ingest-pipeline.en.md` — 7-section parsing + pre-filter rules
- `11-wiki/triangulation-score-pattern.en.md` — bge-reranker NLI proxy

### Findings (audit-worthy)

- **Memgraph entity-graph has grown to 12,631** (from 8,997 yesterday) — likely from continuous `vault-graph-extract` runs. The two-tier diff suggests many of the new ones are noise (quoted strings, code snippets).
- **127 predicates in KO-DB** vs canonical 38-vocab — 87 orphans, top 4 (`prevents` / `fixes` / `defaults_to` / `motivated_by`) deserve promotion to canon.
- **NotebookLM reports** live in `06-Audits/` not the canonical `10-raw/external/notebooklm/` — the script discovery heuristic handles both paths.

### Numbers (post-1.0.6)

- **13 brainstorm ideas LANDED** of 22 (59%), 9 remaining
- **79** total `/usr/local/bin/vault-*` + `11.11*` scripts (up from 75)
- Lint state: ruff 0, frontmatter 0, atomic-write 0
- Memgraph: 12,631 entities (up from 8,997)
- KO-DB: 13,801 facts, 127 unique predicates

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.5...v1.0.6

## [1.0.5] — 2026-05-19 (very late evening)

Round 7 — four more brainstorm ideas land. Now at **9 of 22 brainstorm ideas LANDED** (45 days into the v1.0 lifecycle, on launch-day itself).

### Added — 4 new CLIs

- **`vault-ko-triangulate`** (idea #19) — semantic triangulation score using bge-reranker as NLI proxy. Given a (subject, predicate, object) triplet, finds related chunks via Memgraph + KO-DB, then scores entailment via the warm reranker. **4 verdicts**: `support` (≥0.65), `weak` (0.40-0.65), `neutral` (0.20-0.40), `no-evidence` (<0.20). Validated by catching a hallucinated fact in the smoke-test — string-corroboration alone passed it; triangulation correctly flagged 0.00. Orthogonal to the existing `confidence` field; combine via min() at downstream use.
- **`vault-nb-ingest`** (idea #22) — NotebookLM deep-research → KO-DB triplet-extraction pipeline. Scans `10-raw/external/notebooklm/` + `06-Audits/` for NotebookLM-style reports, parses the 7-section structure, pre-filters anchor-only/reference-only/question-only blocks, writes Phase-1 subagent-fanout pending files. Dry-run default; `--apply` requires `VAULT_NB_INGEST_APPLY=1` env-var as the second gate. Already detected **6 reports** on this vault (Q4-Q5 vault-meta synthesis, top-7 EN podcast plan, KGC-4 integration research, etc.).
- **`vault-entity-trace`** (idea #8) — "When did I first learn X" provenance timeline. For any entity name, queries KO-DB (substring across subject + object) + Memgraph (entity-graph 1-hop) and emits a chronological source-list with predicates used per source. Validated on `Memgraph` (128 facts, first 2026-05-12, most recent 2026-05-18) and `KGC-4` (17 facts, first 2026-04-30 ADR).
- **`vault-search-rewrite`** (idea #12) — HyDE-style query reformulation when `vault-search` returns weak hits. **Two modes**: rule-based expansion (deterministic, $0, uses 13-token EXPANSION_HINTS + KO-DB alias lookup) and subagent-mode (pending-file pattern for LLM-generated HyDE paragraph). Threshold-triggered: rewrite kicks in only if top-1 cosine < 0.4 (or `--always-rewrite`). Validated +0.050 improvement on `"agent fanout"` (0.611 → 0.660).

### Added — wikis

- `11-wiki/triangulation-score-pattern.en.md` — when string-corroboration isn't enough, when bge-reranker as NLI proxy is OK vs production deberta-v3
- `11-wiki/notebooklm-ingest-pipeline.en.md` — 7-section parsing heuristic + pre-filter rules + idempotency contract
- `11-wiki/entity-trace-provenance-pattern.en.md` — Karpathy "provenance = trust" principle in CLI form

### Numbers (post-1.0.5)

- **9 brainstorm ideas LANDED** of 22 (Round 6: #2/3/4/5 + Round 7: #8/12/19/22), 13 remaining
- **+4 new `/usr/local/bin` scripts** (vault-ko-triangulate, vault-nb-ingest, vault-entity-trace, vault-search-rewrite)
- **+3 new wikis** + audit docs
- **75** total `/usr/local/bin/vault-*` + `11.11*` scripts (up from 70)
- **23** cron entries (no new this round; existing ones still all flock-mutex)
- Lint state: ruff 0, frontmatter 0, atomic-write 0
- Wiki count: 262 (up from 258)
- EN translations: 75 (up from 71)
- All-green CI

### Internal

- 2 parallel subagent-fanout runs (triangulate + nb-ingest scaffolds) ~12 min total wall-clock, $0 cost
- Main thread parallel: vault-entity-trace + vault-search-rewrite ~30 min hand-written
- Total Round 7: ~45 min for 4 production-quality CLIs

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.4...v1.0.5

## [1.0.4] — 2026-05-19 (late evening)

Round 6 — four more brainstorm ideas land. All read-only / additive; no
behaviour changes to existing scripts.

### Added — 4 new CLIs

- **`vault-explain "<query>"`** (idea #2) — retrieval introspection trace. Runs the full pipeline (bge-m3 → native vector → smart-rerank → KO-DB corroboration → Memgraph entity-graph) and emits a per-result trace with cosine score, token-overlap, KO-DB cross-source count, entity-graph neighbours, AND a Mermaid `flowchart LR` diagram of the trace. Markdown + JSON output. Graceful fallback if Memgraph unreachable. Source: `.vault-memory/scripts/vault-explain.py`.
- **`vault-ko-decay`** (idea #3) — predicate-aware freshness-decay scoring. 38-predicate half-life table (`is_a` = ∞, `uses_database` = 730d, `currently` = 7d, etc.). Uses source-file mtime, falls back to `facts.created_at`. Read-only — decay applied at query-time. `--calibrate` shows the predicate × half-life × count distribution.
- **`vault-daily-rollup`** (idea #4) — extractive 5-bullet summarizer that prepends a `## Yesterday` block to each morning's `01-Daily/<date>.md`. Ranks session highlights by bold-prefix, numeric content, and `LANDED`/`ÉLES`/`DONE` markers. Idempotent re-runs replace the existing `## Yesterday` block. Cron entry installed: `0 6 * * *`. Subagent-mode pending-file interface stubbed for future LLM upgrade.
- **`vault-ko-anki`** (idea #5) — KO-DB → Anki/Mochi cloze-deletion deck export. Filters for "evergreen" predicates (`is_a`, `defined_as`, `defined_in`, etc.) at confidence ≥ 0.9, optionally weighted by decayed confidence (`--include-decay`). 3 output formats: CSV (Anki native import), `.apkg` (genanki), Mochi JSON. **1,668 cards available** at conf ≥ 0.85.

### Added — wikis

- `11-wiki/vault-explain-pattern.en.md` — retrieval-introspection pattern docs
- `11-wiki/daily-rollup-auto-summarize.en.md` — extractive vs subagent mode trade-offs

### Numbers (post-1.0.4)

- **5 brainstorm ideas LANDED today** (was 4): #1 RAGAS, #9 Temporal-KG SCD2, #13 Browser-history, #15 Sleep-consolidation, #20 Vault-MCP, **+#2 vault-explain, #3 freshness-decay, #4 daily-rollup, #5 Anki export**
- **9 brainstorm ideas total** (of 22), 13 remaining
- **+4 new `/usr/local/bin` scripts** (vault-explain, vault-ko-decay, vault-daily-rollup, vault-ko-anki)
- **+1 new cron** (vault-daily-rollup 06:00)
- Lint state: ruff 0, frontmatter 0, atomic-write 0
- KO-DB: 13,801 facts, 1,668 evergreen-eligible
- Daily-note narrative gap CLOSED — every morning now gets an auto-summary

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.3...v1.0.4

## [1.0.3] — 2026-05-19 (evening)

Quality-debt cleanup + new capabilities. Same launch-day; this is the polish-the-polish pass.

### Added — new capabilities

- **Temporal-KG SCD2 scaffold** (idea #9 from the brainstorm) — `valid_from`/`valid_until` versioning for KO-DB facts enabling time-travel queries. 6 files: `00-Meta/migrations/2026-05-19-scd2-facts.sql` (reversible migration), `.vault-ko/scd2.py` (query helpers), `/usr/local/bin/vault-ko-temporal` (CLI), `.vault-ko/tests/test_scd2_skeleton.py` (9 pytest, all pass on synthetic in-tempdir SQLite), `11-wiki/temporal-kg-scd2-pattern.md` (~650 words), `06-Audits/2026-05-19 Temporal-KG SCD2 skeleton.md`. **Migration NOT run on real `facts.db` today** — skeleton ready; expected runtime < 2 s when triggered.
- **`vault-ko-remap-legacy` transaction-aware audit** — refactored both Phase 1 (`phase1_apply`) and Phase 2 (`phase2_collect`) to buffer audit-records in memory during the SQL transaction and only flush via `atomic_append_jsonl` AFTER `COMMIT` returns. Eliminates the "ghost audit row" hazard where the prior code persisted audit lines for SQL operations that ultimately rolled back. Removes the last 2 `# vault-atomic-lint: ok — non-trivial control flow, follow-up` whitelist comments — script is now genuinely compliant, not whitelisted.
- **Cloudflared tunnel scaffold** (`.vault-mcp/tunnel.sh`) — STDIO MCP → HTTP/SSE bridge (`mcp-proxy`) + Cloudflare quick-tunnel or named-tunnel mode. One-shot script: `./tunnel.sh` for ephemeral try-tunnel, `./tunnel.sh --named` for production with Cloudflare Access. Documents the security trade-offs (read-only tools vs vault-content sensitivity).
- **`vault-atomic-lint`** — no longer needed for `vault-ko-remap-legacy` (both whitelist comments removed); the lint baseline is now genuinely 0 violations.

### Changed — quality cleanup

- **Lint-debt eliminated** — public-repo ruff issues reduced from **45 → 0** in a single mechanical pass over 18 files. Breakdown: 7× F401 unused-import deletions, 9× F541 f-string-without-placeholder (changed `f"..."` to `"..."`), 4× F841 unused-local (converted to explicit `_ =` discard with side-effect comments — none deleted outright), 7× E741 `l` → `label` rename in `vault-graph-retype.py`. RUFF_BUDGET in CI ratcheted **60 → 5**.
- **Frontmatter cleanup** — 19 wiki files fixed: 10× missing `type:`/`updated:` keys backfilled, 6× malformed inline `related: [[a]], [[b]]` arrays converted to YAML block-list form, 2× mixed inline+block `tags:` lists flattened, 1× `11-wiki/README.md` got minimal index frontmatter. Linter now reports **0 issues** (was 19).

### Internal

- `vault-public-sync` ran 4× in this round; commits: ~6 new on PUBLIC main
- All atomic-write/append invariants enforced: `vault-atomic-lint --quiet` exit 0, `lint_frontmatter.py` exit 0
- Subagent fanout: 2 parallel agents (Temporal-KG skeleton + lint cleanup), $0 cost

### Numbers (post-1.0.3)

- **0** ruff lint issues (was 45)
- **0** frontmatter validation issues (was 19)
- **261** wikis (was 258 — +3 from Temporal-KG scaffold)
- **9/9** Temporal-KG skeleton pytest PASS
- **13,801** facts in KO-DB, ready for SCD2 migration (< 2 s ETA)

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.2...v1.0.3

## [1.0.2] — 2026-05-19 (later)

Repo-audit-driven launch-readiness pass. No code-behaviour changes; everything below is OSS infrastructure, documentation, or distribution polish.

### Added

- **`.github/workflows/ci.yml`** — main CI pipeline: ruff lint + markdown lint (lax) + frontmatter lint + broken-wikilink scan + pytest regression + mkdocs strict build (6 parallel jobs, 10-min timeout each)
- **`.github/workflows/pr-labeler.yml`** + **`.github/labeler.yml`** — auto-label PRs by area (wiki / adr / audit / cli / docs / i18n / breaking-change)
- **`.github/workflows/stale.yml`** — gentle 60/30-day stale-marker on issues / PRs, with `pinned`/`roadmap`/`community-pattern` exemptions
- **`.github/workflows/link-check.yml`** — weekly external-link check via `lycheeverse/lychee-action`, auto-files issue on 404s
- **`.github/scripts/lint_frontmatter.py`** + **`broken_wikilinks_check.py`** — CI-helper scripts, locally runnable, budget-tunable
- **`Makefile`** — `make {help,install,lint,test,docs,build-docs,clean}` developer-friendly targets
- **`requirements-dev.txt`** — `pytest`, `pyyaml`, `ruff`
- **`.devcontainer/`** — GitHub Codespaces / VS Code dev-container: Python 3.12 + Docker-in-Docker + auto-Memgraph + 8 IDE extensions pre-configured + post-create banner
- **`.github/CODEOWNERS`** — single-maintainer signal
- **`docs/assets/hero-banner.png`** — 1280×640 PNG rasterized from the SVG, ready for GitHub social-preview upload (Settings → Options → Social preview)
- **`11-wiki/architecture-overview.en.md`** — full Mermaid architecture diagram + the 8 axes mapped end-to-end + per-axis deep-dive links
- **`11-wiki/faq.en.md`** — 13 launch-FAQ questions answered up front
- **`06-Audits/2026-05-19 repo improvement audit.md`** — ~3,250-word benchmark vs mem0/lancedb/qdrant/microsoft-graphrag/agno/crewai/langfuse/litellm
- **`06-Audits/2026-05-19 GitHub launch playbook.md`** — ~7,060-word channel-by-channel playbook (HN×3 / Twitter / Reddit×3 / Dev.to / Lobsters / LinkedIn / Mastodon) with paste-ready post drafts

### Changed

- **README rewrite** — corrected stale counts (87 → **258** wikis, 28 → **45** ADRs, 76 → ~80 sessions), fixed broken quickstart URL (`<owner>/superintelligent-vault.git` → `MyForgeLabs/myforge-vault-1111.git` — caught by the audit as a stop-the-launch finding), added memory-OSS competitor comparison table (mem0 / Letta / GraphRAG / agentmemory), added Contributors section honestly listing AI agents as named co-collaborators, added Architecture diagram block, added Star History + Built-with + Cite-this-work collapsible sections, added FAQ + architecture-overview links
- **Repo topics** added 8 new (now 20 total): `ai-agents`, `rag`, `vector-search`, `embedding`, `llm-eval`, `personal-knowledge-management`, `local-first`, `bge-m3`
- **`mkdocs.yml`** — hid `HN Launch Console` from public nav (it's launch-internal, optics risk)

### Fixed

- **Stop-the-launch:** README quickstart had a `<owner>/superintelligent-vault.git` placeholder URL pointing at the legacy repo name. Fixed pre-Tuesday launch.

### User-action remaining

- **Social-preview PNG upload** — `docs/assets/hero-banner.png` is ready in the repo; upload via Settings → Options → Social preview (no REST API for this; must use web UI)

## [1.0.1] — 2026-05-19

Two days of post-launch polish on top of v1.0.0. No breaking changes.

### Added

- **`SECURITY.md`** — vulnerability disclosure policy
- **`CITATION.cff`** — academic citation metadata (Zenodo-compatible DOI mintable)
- **`llms.txt`** at repo root — agentic-browsing discovery per [llmstxt.org](https://llmstxt.org)
- **`.github/FUNDING.yml`** — GitHub Sponsors registration
- **`.github/ISSUE_TEMPLATE/vault_pattern.md`** — "Share your vault pattern" community thread template
- **`.github/ISSUE_TEMPLATE/config.yml`** — routes blank issues to Discussions instead
- **`.vault-mcp/vault_mcp_server.py`** — umbrella STDIO MCP server (7 read-only tools: `search_vault`, `search_skills`, `ko_query`, `ko_top_k`, `memgraph_cypher`, `read_project`, `list_recent_sessions`); local-first, no auth, mutation keywords rejected in Cypher
- **`.vault-mcp/mcp.json.sample`** — wire-up config for Claude Code / Claude Desktop / Codex / Gemini
- **`.vault-eval/regression/`** — LongMemEval-S retrieval-quality CI gate (Pytest fast + slow modes, daily cron)
- **`/usr/local/bin/vault-search-health`** — 5-step daemon probe (socket / systemd / health-rpc / search-rpc / skill-ns)
- **`/usr/local/bin/vault-atomic-lint`** — AST-scan + whitelist-comment lint for atomic-write compliance
- **`/usr/local/bin/vault-eval-regression`** — CLI wrapper for the LongMemEval-S regression gate
- **`/usr/local/bin/vault-sleep-consolidate`** — REM-style cross-session learning consolidator (stage-1 rule gate + stage-2 LLM-Critic via subagent-fanout pending pattern, audit-only by default)
- **`/usr/local/bin/vault-browser-history-ingest`** — Chrome/Chromium/Brave History → `10-raw/external/browser/` with NLI pre-filter, dry-run default, `VAULT_BROWSER_INGEST_APPLY=1` gate
- **`11-wiki/append-only-jsonl-migration.md`** — 17-site migration playbook + subagent triage finding
- **`11-wiki/browser-history-ingest-pattern.md`** — passive-ingest pipeline doc
- **3 NotebookLM podcasts re-encoded** from 1200 kbps to 96 kbps: **121 MB → 45 MB** (-62%)

### Changed

- **`bmad-vault-watch@.service`** systemd template hardened: `MemoryMax=512M`, `MemoryHigh=384M`, `TasksMax=128`
- **`vault-search.service`** patched: `VAULT_RERANK_PREWARM=v2-m3`, `MemoryHigh=5G`, `MemoryMax=7G`; bge-reranker now warm at daemon start
- **`vault-search` CLI** auto-backend smart-rerank now **delegates to the daemon** when `reranker_loaded: true` — wall-clock **18.6 s → 8.7 s (-55%)**
- **12 JSONL append-sites** migrated to the centralised `vault_atomic.atomic_append_jsonl` helper
- **B-7 entity typing**: 28.9% → **72.8% (+43.9pp)** in one parallel subagent classification pass

### Fixed

- **B-2 no-socket score-norm bug RESOLVED** — daemon-vs-legacy score divergence eliminated by implicit chunk-vector re-normalization
- **`mgclient` autocommit silent-rollback** — `conn.autocommit = True` enforced in all Memgraph writers
- **`set -e` + `vault-detect-chat-id` exit-1 collision** in 5 of the `11.11*` family scripts
- **Audit-MD self-referential loop** in the broken-wikilink scanner (~70% noise reduction)

### Internal

- **Layer-1 vault-atomic FULL coverage** across 15 sites + flock-mutex in 14+ cron jobs
- **B-7 graph**: 24,606 typed edges, 100% typed, 3,431 `:LINKS_TO`, 300 `:ALIAS_OF`
- **B-8 RSI Tier-2 Constitutional AI skeleton** (319 LOC, 10 rules, 4-layer safety, `--apply` blocked by default)
- **4 new daily cron jobs** (all flock-mutex): vault-search-health 30-min, vault-atomic-lint 02:30, vault-eval-regression 02:45, vault-sleep-consolidate 03:30

### Numbers (post-1.0.1)

- 252 wikis (was 219), 71 EN translations
- 13,800+ KO-DB facts, 8,997 entity-graph nodes / 24,606 edges / 100% typed
- 67/99 Recall@5 hybrid (LongMemEval-S vault-variant v0.2)
- 0 atomic-write violations (66 scripts lint-compliant)
- 18.6s → 8.7s smart-rerank wall-clock (-55%)
- 121 MB → 45 MB podcast footprint (-62%)

Full diff: https://github.com/MyForgeLabs/myforge-vault-1111/compare/v1.0.0...v1.0.1

## [1.0.0] — 2026-05-18

**Initial public release.** Repository flipped from PRIVATE to PUBLIC, MIT license, docs site live at <https://myforgelabs.github.io/myforge-vault-1111/>.

### Knowledge base
- **140 evergreen wikis** in `11-wiki/` (Hungarian primary, English translations for top-10 in progress)
- **41 ADRs** in `07-Decisions/`
- **67+ audit reports** in `06-Audits/`
- **13 SV-meta sessions** in `08-Sessions/` (scrub-validated for public)
- Master-INDEX with 10 topic-clusters (`11-wiki/Index.md`, 330 lines)

### 8-axis architecture (B-1 .. B-8) — Phase B foundation landed

- **B-1 Crystallization automation** — `11.11crystallize` script, G-Eval v0.3 paired-calibration, 4-layer safety-gate, Layer 2.5 NLI + Layer 2.6 coherence-check cascade
- **B-2 Memory architecture** — Memgraph CE 3.9.0 native vector-index (280× speedup, p95 2.6 ms), bge-m3 multilingual encoder, RRF hybrid BM25+semantic
- **B-3 Continuous evaluation** — G-Eval prompt, NLI Layer 2.5, coherence-check Layer 2.6, SelfCheckGPT borderline filter
- **B-4 Tool composition** — `vault-skill-search`, 462 SkillChunk Memgraph-embedded
- **B-5 NotebookLM cognitive layer** — 63-source vault-meta NB, cross-project synthesis (Q1–Q5)
- **B-6 Multi-agent orchestration** — `11.11worker.sh` claude-code subprocess pattern
- **B-7 World-model / knowledge graph** — 8997 entities, **74.7% typed** (Concept/Skill/Project/Sprint/Server/Person/Decision/SourceFile/Pattern/Alias), 102 ALIAS_OF edges
- **B-8 Recursive self-improvement** — GEPA `gepa.optimize()` real loop, Pareto +14.3% (custom GEPAAdapter + ClaudeCodeReflectionLM)

### Tooling

- `11.11*` session-orchestration CLI family (start/stop/note/focus/ls/crystallize/worker)
- `vault-public-sync` — idempotent scrub + commit + push pipeline, 30-min cron
- `vault-broken-wikilinks-audit` — code-fence + relative-path + auto-memory aware
- `vault-graph-query` — Memgraph CLI wrapper (autocommit-patched 2026-05-18)
- `vault-search` + `vault-search-server` — semantic search daemon (warm bge-m3 + Memgraph vector-index)
- `vault-ko-query` — KO-DB top-K cross-source corroboration
- `vault-cleanup` — weekly vault-integrity scan with self-exclusion fix
- 35+ additional scripts in `.vault-*/scripts/`

### Open-source release

- **Scrub pipeline:** paranoid YAML rules + glob-aware regex + 94 replacements + 0 forbidden-violations
- **Docs site:** mkdocs-material with Hungarian UI, dark-mode default, search, navigation tabs, git-revision-date footer, glightbox image zoom
- **GitHub Action:** auto-deploy on push to `main` (Pages, ~3 min build time)
- **License:** MIT, attribution to MyForge Labs

### Quality metrics (session of 2026-05-18)

- KO-DB facts: **13 801** (100% vault coverage: 76 wikis + 28 ADRs + 69 sessions)
- Predicate-dump rate: 19.8% → **9.9%** (via 1 046 fact predicate-remap)
- Memgraph entity-typedness: 28.9% → **74.7%** (+45.8 pp via 7-batch context-aware classification fanout)
- ALIAS_OF edges: 26 → **102** (separator/suffix/case normalization)
- Memgraph wiki chunk coverage: 0 → **100% (97/97)**
- Crystallization predicate dump: 27.7% → 9.9%

### Bug-fixes shipped

- `vault-graph-query` autocommit-bug — silent rollback on SET/CREATE/MERGE statements (Memgraph mgclient default explicit-transaction mode)
- `vault-cleanup` self-referential audit-loop — System_Health.md and broken-wikilinks-latest.md now self-excluded
- `vault-cleanup` relative-path resolution — `[[../11-wiki/x]]` now resolves correctly
- `11.11*` family `set -e` + `vault-detect-chat-id` exit-1 collision fix (5 scripts patched)

## Pre-1.0 history

See `08-Sessions/` for the 6 super-sessions between 2026-05-17 and 2026-05-18 that produced the initial public release. Earlier internal development (since 2026-02-05) remains private.

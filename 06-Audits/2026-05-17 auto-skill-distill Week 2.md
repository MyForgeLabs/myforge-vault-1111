---
name: 2026-05-17 auto-skill-distill Week 2
type: audit
tags: ["#type/audit"]
created: 2026-05-17
updated: 2026-05-19
tag_backfill: 2026-05-19
---
# Auto-skill desztilláció Week 2 — `--distill` flag + 2-phase pending + bge-m3 dedup

## TL;DR

A `vault-skill-distill` Week 1 detect-only skeleton-ja bővítve `--distill` flow-val. A script most a top-N (default 3) pattern-re ír Phase 1 pending-request JSON-t `/tmp/vault-skill-distill-pending/`-be, claude-code subagent-fanout-tal generál SKILL.md candidate-et, és bge-m3 cosine-dedup-pal (default threshold 0.80) helyezi vagy `~/.claude/skills/auto-distilled/queue/`-ba vagy `dedup-rejected/`-be. $0 cost (Anthropic API nélkül). Semmilyen aktív SKILL.md, AGENTS.md, 00-Meta vagy 11.11* nem érintett.

## Architektúra

### 1. `--distill` flag

```
vault-skill-distill --distill --top-n 3 [--dry-run | --apply] [--dedup-threshold 0.8]
```

- `--top-n N` (default 3) — top-N pattern-et válogat ki a detektált token/bigram/trigram counter-ekből, multi-token-prioritás azonos count esetén (composition signal)
- `--dry-run` — kiírja mit csinálna, semmit nem ír
- `--apply` — Phase 1: request JSON-ok írása; Phase 2 (ha response.json létezik): parse + dedup + queue-write
- `--dedup-threshold 0.80` — bge-m3 cosine küszöb, ≥0.80 → dedup-rejected, <0.80 → queue

### 2. 2-phase pending pattern

Ugyanaz a minta, mint `vault-ko-ingest`-nél (B-1) és `11.11crystallize claude-code scorer`-nél:

| Phase | Akció | Hol |
|---|---|---|
| 1 | Script `--apply` → ír `<slug>.request.json`-t `/tmp/vault-skill-distill-pending/`-be (prompt + pattern + raw event-példák) | script |
| – | Parent agent (Claude Code) spawnol general-purpose Agent-et a prompt-tal | parent |
| – | Subagent JSON-output-ot ír `<slug>.response.json`-be (`skill_md`, `name`, `description`, `is_coherent`) | subagent |
| 2 | Script re-run `--apply` → parse response + dedup-check + queue-write (vagy dedup-rejected) | script |

Slug-hash a (kind, tokens)-en alapul (SHA256 prefix 8 char) → idempotens re-run, nem duplikál.

### 3. bge-m3 cosine dedup

- Lazy-load `BAAI/bge-m3` a `.notebooklm-venv` site-packages-ből (`/root/.notebooklm-venv/lib/python3.12/site-packages`)
- 279 meglévő `~/.claude/skills/*/SKILL.md` description-t embedel (corpus cache plain JSON formátumban: `~/.claude/skills/auto-distilled/.dedup-corpus-cache.json`, szándékosan nem binary serializer hogy ne ütközzön safety hook-okkal)
- Új candidate description-re query-embedding → cosine az egész corpus ellen → argmax
- `sim ≥ threshold` → `dedup-rejected/<slug>.md` (audit-log-ban a best-match-csel)
- `sim < threshold` → `queue/<slug>.md`

### 4. Audit-log

`~/.claude/skills/auto-distilled/distill-log.jsonl` — minden phase1 + phase2 esemény JSONL-line, UTC ISO timestamp-pal. Plusz per-run summary `~/.claude/skills/auto-distilled/distill-run-<UTC-stamp>.json`.

### 5. Safety

- Write-target whitelist: **csak** `~/.claude/skills/auto-distilled/{queue,dedup-rejected,distill-log.jsonl,.dedup-corpus-cache.json,distill-run-*.json}` + `/tmp/vault-skill-distill-pending/`
- NO active SKILL.md modification, NO touch a 279 meglévő skill-en
- `is_coherent: false` a subagent response-ban → skipped-incoherent (nem queue, nem dedup-rejected)
- Idempotency: queue/<slug>.md vagy dedup-rejected/<slug>.md létezése → "already-produced" → skip
- `--dry-run` + `--apply` mutually exclusive

## Smoke-test eredmény (`--days 30 --top-n 3 --apply`)

Top-3 pattern (token-szinten, mert ezek dominálnak a bigram-okat ebben az ablakban):

| # | Pattern | Count | Sessions | Cosine vs. best existing | Best match | Status |
|---|---|---|---|---|---|---|
| 1 | `ingest` | 16 | 5 | **0.569** | `bmad-shard-doc` | ✓ queued |
| 2 | `batch` | 15 | 6 | **0.613** | `bmad-bmb-validate-max-parallel-workflow` | ✓ queued |
| 3 | `backfill` | 14 | 5 | **0.543** | `obsidian-cli` | ✓ queued |

Mindhárom új concept — egyik sem közelíti a 0.80 dedup-threshold-ot, ami azt jelzi hogy a vault-belső pattern-eink (ko-db ingest, subagent-fanout batch, multilingual embed backfill) markánsan különböznek a 279 előre-telepített BMad/Azure/WP skill-től.

A 3 queued candidate filename-pattern: `<token>-<hash8>.md`

- `queue/ingest-6eb7f2ea.md` → name: `vault-content-ingest`
- `queue/batch-4bb24efc.md` → name: `vault-batch-fanout`
- `queue/backfill-af76eb7f.md` → name: `vault-backfill`

Mindhárom rendes Anthropic Agent Skills frontmatter-rel (name/description/tags/trigger_keywords/license/metadata) + 1-2 bekezdés body + Steps + Related szekcióval.

### Idempotency check

2× run ugyanazzal a flag-csomaggal → 2. futás output:

```
patterns selected: 3
phase1 requests written: 0
phase2 processed: 0
queued: 0
skipped (already produced): 3
```

✓ Nem duplikál.

## Week 3 follow-up

1. **`vault-skill-search` index** — a queue-ban lévő candidate-eket vegye fel a semantic-search index-be (Memgraph KO-namespace `skills-candidate`), hogy `vault-search "skill X"` találja őket aktiválás előtt
2. **Human-review CLI** — `vault-skill-distill --review` parancs ami listázza a queue-t, megjeleníti a teljes SKILL.md-t + cosine-szomszédjait + lehetővé teszi a `mv queue/<slug>.md auto-distilled/<slug>/SKILL.md` aktiválást vagy `mv ... dedup-rejected/`-be tolást egy parancsban
3. **Auto-skill-loader** (Week 4) — heti cron ami threshold-credenciával (pl. cosine<0.6 + manual ✅ flag a frontmatter-ben) auto-aktiválja a queue-ból a candidate-eket. Ekkor kell a `VAULT_SKILL_LOADER_APPLY=1` ENV-gate + sandbox-branch + 4-réteg safety mint a `11.11crystallize`-nál
4. **GEPA prompt-mutator integráció** (B-8 cross-axis) — a candidate skill-ek prompt-mutáción mehetnek át a GEPA pipeline-ban a precision javítása érdekében aktiválás előtt
5. **Trigram-pattern emelés** — jelenleg a top-3 csak token (count>=14), a bigram-ok 3 körül vannak; ha 7+ napos ablakra váltunk és több sessiont halmozunk, a bigram `ingest→backfill` (count 3) versenyképessé válhat; érdemes 60-90 napos ablakot is támogatni

## Konfiguráció

- `EMBED_MODEL` env-var (default `BAAI/bge-m3`)
- `CLAUDE_SKILLS_DIR` env-var (default `/root/.claude/skills`)
- `VAULT_DIR` env-var (default `/root/obsidian-vault`)

## Kapcsolódó

- [[06-Audits/2026-05-17 B-4 auto-skill distillation skeleton]] — Week 1 detect-only
- [[11-wiki/claude-code-subagent-fanout]] — 2-phase pending pattern
- [[11-wiki/sv-04-tool-composition]] — Voyager skill-library theory
- [[11-wiki/Crystallization-protocol]] — sibling 2-phase pattern
- `/usr/local/bin/vault-skill-distill` — script
- `~/.claude/skills/auto-distilled/{queue,dedup-rejected,distill-log.jsonl}` — output tree

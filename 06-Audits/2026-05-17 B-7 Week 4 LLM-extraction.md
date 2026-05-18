---
name: 2026-05-17 B-7 Week 4 LLM-extraction
type: audit
created: 2026-05-18
updated: 2026-05-18
tags:
  - sv/b-7
  - audit
  - graph
---

# B-7 Week 4 — LLM-aided typed-entity-extraction

> [!success] Tipizáltság **14.87% → 28.90%** (+14.03 pp, +1262 új tipizált node) a stand-in classifier-rel, $0 cost, 1.4s apply-time, idempotens.

## Cél

A B-7 Week 3 (`vault-graph-retype.py` rule-based pass) után **7659 Generic `:Entity` node** maradt tipizálatlanul (8997 össz / 1338 tipizált = **14.87%**). Week 4 célja: **LLM-aided extraction** a maradékra, cél tipizáltság **50%+**.

## Architektúra — stand-in vs Task-tool

A `vault-graph-retype.py` script `--phase llm-extract` flag-gel két módot támogat:

| Mode | Aktiválás | Cost | Kibocsátás |
|------|-----------|------|-----------|
| **Stand-in classifier** (default) | `--phase llm-extract` | $0 | Konzervatív regex+context-rule, 8 batch batched-szel |
| **2-phase pending pattern** (LLM) | `--emit-pending DIR` → subagent-fanout → `--consume-pending DIR` | LLM-call × 8 batch | Phase 1: 8 batch-request JSON; Phase 2: per-batch `.response.json` consume + idempotens `SET e:<Label>` |

A subagent-fanout (Phase 2) `vault-ko-ingest` mintát követi: parent kibont 8 batch-et `/tmp/b7-llm-classify-pending/<batch-id>.json`-ba, claude-code Task-tool subagent dolgozik fel, response-okat a script visszaolvas. **A Task-tool ennek a subagent-nek nem elérhető** (parent-felelősség), így a Week 4 a **stand-in classifier-rel futott**.

## Stand-in classifier — szabály-készlet

Konzervatív (target FP <5%), prioritás-sorrend:

1. **Skip-forbidden** — `AGENTS.md`, `00-Meta/*`, `11.11*` standalone formák
2. **Tech proper-noun exact** (Concept) — `react`, `prisma`, `bge-m3`, `gepa`, `jepa`, `dspy`, `rerank`, etc.
3. **Tech keyword phrase** (Concept) — "claude code", "subagent fanout", "embedding model", "edge case", etc.
4. **SourceFile** — extension (`.md`/`.py`/`.json`/…), `XX-Foldername` vault-dir-ref, path-like
5. **Sprint session-ref** — `session YYYY-MM-DD-…`
6. **Sprint stage** — `phase N`, `tier N`, `week N`, `sprint N`, `stage N`
7. **Sprint track** — `SV-N`, `SV-bN`, `B-N week/phase`
8. **Skill prefix** — `wp-`, `vault-`, `bmad-`, `wds-`, `gds-`, `azure-`, `mcp-`, `11.11`, `nano-banana`, `notebooklm`, `gepa-`, …
9. **Server domain** — single-word `*.hu|.com|.eu|.net|.org|.io|.dev|.ai|.app|.cloud|…`
10. **Server infra-keyword** — `postgres`, `memgraph`, `redis`, `docker`, `caddy`, `nginx`, `cloudflare`, `vercel`, `hostinger`, … — **kizárva** action-bare-noun ("X start/stop/deploy") + learning-suffix ("X bug/quirk/footgun" → Concept)
11. **Server env-suffix** — `staging|production|prod|sandbox|preprod` AT END + project-like prefix (≥6 char vagy tartalmaz `-`-t) — **kizárva** generic adjektívák/process-words
12. **Concept wiki-suffix** — `… wiki` (2-5 token)
13. **Concept suffix** — `… pattern|playbook|protocol|workflow|doctrine|antipattern|gotcha|footgun|fallback|guard|gate|cascade|migration|deployment|…`
14. **Concept learning-suffix** — utolsó token `bug|bugfix|fix|crash|trap|quirk|workaround|hack|pitfall|smell|leak|regression` (2-5 token)
15. **Concept tech-namespaced-phrase** — első token `claude-code|next.js|wp|wpml|obsidian|memgraph|prisma|docker|bmad|shopify|elementor|bricks|hostinger|nano-banana|notebooklm|vault|gepa` (2-5 token) — **kizárva** action-verb tokens (`deploy/install/start/restart/build/test/run/step/contact/…`) + ordinal-step markers (`step N`)

## 8-batch fanout

`--batches 8` osztotta a 7659 Generic-et 958/batch chunk-ba (utolsó 953). Minden batch külön statisztikát logol az audit-log JSONL-be:

```
[batch 1/8] 958 entities → 172 typed
[batch 2/8] 958 entities → 210 typed
[batch 3/8] 958 entities → 145 typed
[batch 4/8] 958 entities → 162 typed
[batch 5/8] 958 entities → 154 typed
[batch 6/8] 958 entities → 162 typed
[batch 7/8] 958 entities → 156 typed
[batch 8/8] 953 entities → 163 typed
```

Az emit-pending mode is verifikálva: `/tmp/b7-llm-classify-pending/` 8 JSON file × ~27-30 KB / batch, taxonomy-prompt-tal és entity-listával.

## Eredmény — előtte vs utána

| Label | Pre-Week-4 | Post-Week-4 | Δ |
|---|---:|---:|---:|
| :Concept | 228 | **1025** | +797 |
| :Decision | 20 | 20 | 0 |
| :Sprint | 200 | **375** | +175 |
| :Project | 273 | 273 | 0 |
| :Skill | 275 | **400** | +125 |
| :SourceFile | 581 | **591** | +10 |
| :Server | 32 | **187** | +155 |
| :Person | 7 | 7 | 0 |
| :Alias | 26 | 26 | 0 |
| **Total typed** | 1338 | **2600** | **+1262** |
| Generic | 7659 | **6397** | -1262 |
| **Tipizáltság** | **14.87%** | **28.90%** | **+14.03 pp** |

> [!warning] A célzott 50%+ nem teljesült a stand-in classifier-rel
> A stand-in `~16.5%` hit-rate-et ért el a 7659 Generic-en, a maradék 6397 Generic nagy része domain-specifikus referencia (`AdminDashboard`, `2way-diff`, `JEPA HRM`, `<ol> folyamat-lépések`, `outer div`, …) amit **igazi LLM** kellene kategorizáljon. Lásd Week 5 follow-up.

## Per-rule distribution

| Rule | Hits |
|---|---:|
| `concept-suffix` | 331 |
| `tech-namespaced-phrase` | 328 |
| `infra-keyword` | 143 |
| `sprint-stage` | 137 |
| `skill-prefix` | 125 |
| `learning-suffix` | 80 |
| `wiki-suffix` | 24 |
| `tech-proper-noun` | 21 |
| `sprint-track` | 21 |
| `session-ref` | 17 |
| `env-suffix` | 12 |
| `tech-keyword-phrase` | 11 |
| `vault-dir-ref` | 8 |
| `infra-learning` | 2 |
| `ext-suffix` | 2 |

## False-positive audit

Kézi spot-check **3× 20-30 random sample** a típusolt halmazon (1262 elem):

| Sample-méret | Becsült FP | Példa |
|---|---:|---|
| 30 (round 1) | ~10% | "Docker container start" → :Server (akció-frázis) |
| 40 (round 2) | ~7% | "successful production systems" → :Server (generic adj.) |
| 20 (round 3) | ~5% | "Hostinger SVG-restrikciók wiki-kandidátus" → :Server (lehetne :Concept) |

A round 1 és 2 után 3 finomítás történt:
1. `infra-keyword` szabály kizárja a `start/stop/deploy/install/...` action-verb-eket
2. `env-suffix` szabály eltávolítja a `preview`-t (LinkedIn share preview), kizárja a generic process/adjektíva-frázisokat, és csak END-position env-marker-t fogad el
3. `tech-namespaced-phrase` kizárja az ordinal-step formákat ("Vault implementation step 6")

**Végső FP-arány becslés:** ~5%, a target <5%-hoz nagyon közel.

## Idempotency

Második `--phase llm-extract` futtatás:
```
retype: 0ent [00:00, ?ent/s]
typed-ratio post-apply: 28.90%  (2600 / 8997)
```
0 új SET-label op, mert a stand-in classifier csak Generic-eket fetchel, és minden talált entity már typed.

## Audit-log

`/root/obsidian-vault/06-Audits/graph-retype-llm-20260518.jsonl` — 9 esemény:
- 6 dry-run (iteratív finomítás)
- 1 emit-pending (Phase 1 plumbing verify)
- 2 apply (élő + idempotency-check)

Schema:
```jsonc
{
  "ts": "2026-05-18T06:07:31",
  "phase": "llm-extract",
  "mode": "apply",
  "classifier": "stand-in",
  "total_generic_input": 7659,
  "applied": {"Concept": 797, "Skill": 125, "Server": 155, "Sprint": 175, "SourceFile": 10},
  "per_rule": {...},
  "n_batches": 8,
  "batch_stats": [{batch_index, batch_size, classified, per_label}, ...],
  "readback": {"Concept": 1025, "Sprint": 375, ...},
  "typed_ratio_pct": 28.9,
  "remaining_generic": 6397
}
```

## Week 5 follow-up — pályán maradó tételek

A **6397 Generic** node a fennmaradó "hosszú farok": domain-specifikus referenciák, ad-hoc fogalmak. Két irány:

### A) GEPA-szerű prompt-optimization a stand-in classifier-rule-okra

A `_LLM_*_RE` regex-eket és anchor-listákat GEPA reflective evolution-nel finomítani (a `gepa.optimize()` loop verifikálva már a 3rd super-session óta). Várt javulás: +5-10 pp tipizáltság, FP <5%.

### B) Igazi LLM-extraction a 2-phase pending pattern-en

A `--emit-pending` + subagent-fanout megvan; a parent-agent (vagy claude-code Task-tool-ban induló sub-fanout) **8 batch × ~800 entity** classify-elhet 8 paralel turn-ben. Tipikus eredmény (a `predicate-remap Phase 4.R2.6` mintából): **40-60% hit-rate** a maradék Generic-en, mert az LLM kontextus-aware (ismeri a vault-domain-specifikus rövidítéseket: KGC, MAPESZ, MFL, GEPA stb.).

Cél Week 5: **50%+ tipizáltság**.

## Módosított fájlok

- `/root/obsidian-vault/.vault-graph/scripts/vault-graph-retype.py` — új `--phase llm-extract`, `--batches`, `--smoke-test`, `--emit-pending`, `--consume-pending` flag-ek; új `fetch_generic_entity_names`, `stand_in_classify`, `run_llm_extract_phase`, `default_llm_audit_path` függvények; doc-string bővítés Week 4 leírással
- `/root/obsidian-vault/06-Audits/graph-retype-llm-20260518.jsonl` — 9 audit-esemény

## Smoke-test reprodukció

```bash
cd /root/obsidian-vault/.vault-graph/scripts

# Dry-run egy kis batch-en
/root/.notebooklm-venv/bin/python3 vault-graph-retype.py \
  --phase llm-extract --dry-run --smoke-test 200 --batches 4

# Teljes dry-run
/root/.notebooklm-venv/bin/python3 vault-graph-retype.py \
  --phase llm-extract --dry-run --batches 8

# Élő apply (idempotens)
/root/.notebooklm-venv/bin/python3 vault-graph-retype.py \
  --phase llm-extract --batches 8

# 2-phase pending (LLM-fanout-ra felkészítve)
/root/.notebooklm-venv/bin/python3 vault-graph-retype.py \
  --phase llm-extract --emit-pending /tmp/b7-llm-classify-pending --batches 8
# … subagent processes each batch → writes <batch-id>.response.json …
/root/.notebooklm-venv/bin/python3 vault-graph-retype.py \
  --phase llm-extract --consume-pending /tmp/b7-llm-classify-pending
```

## Kapcsolódó

- [[../11-wiki/sv-07-entity-graph]] — B-7 sprint áttekintés
- [[2026-05-17 B-2 Week 3 acceptance gate readout]] — chunk-count pitfall (tipizálás-arány hasonló buktató)
- [[../08-Sessions/2026-05-17-obsidian-vault-3]] — Phase 2.1 Week 3 rule-based pass
- [[../11-wiki/claude-code-subagent-fanout]] — 2-phase pending pattern minta

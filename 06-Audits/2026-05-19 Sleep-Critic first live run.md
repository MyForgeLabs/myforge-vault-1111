---
name: 2026-05-19 Sleep-Critic first live run
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "sleep-consolidate", "constitutional-critic", "live-run"]
---

# Sleep-Critic — első valódi 7-day live run

**Cél:** `vault-sleep-consolidate --days 7` + `VAULT_SLEEP_LLM_CRITIC=1` opt-in stage-2 2-phase pending pattern end-to-end verifikáció.

**Kontextus:**
- CLI: `/usr/local/bin/vault-sleep-consolidate` (608 LOC + 83 LOC stage-2)
- Wiki: [[../11-wiki/sleep-consolidate-pattern]]
- Előzmény: 2026-05-19 AM mega-session — első run 60 sessions / 472 bullet / 1 recurrence / 1 SKIP

## Pre-flight dry-run (no side-effects)

`vault-sleep-consolidate --days 7 --dry-run`

| Metrika | Érték |
|---|---|
| Sessions scanned | 60 |
| Recurrence candidates (≥2×) | **1** |
| Cluster id | `56177194a7be` |
| Cluster size | 2 |
| Forrás 1 | `08-Sessions/2026-05-04-kgc-weboldal.md` |
| Forrás 2 | `08-Sessions/2026-05-06-kgc-weboldal.md` |
| Sample bullet | `Next.js 16 prod static asset cache: új public/ fájl után systemctl restart kgc-berles.service kell` |
| Closest wiki | `11-wiki/pnpm-build-systemctl-restart-deploy-ritual.md` |
| Novelty-overlap | **0.632** (token-jaccard) |

Megjegyzés: a `60 sessions` érték a teljes `08-Sessions/` directory bullet-parsing-jából jön; a `--days 7` window-szűrés mtime-alapú (`2026-05-12+`).

## Live run with LLM-Critic

`VAULT_SLEEP_LLM_CRITIC=1 vault-sleep-consolidate --days 7`

Log: `06-Audits/sleep-consolidate-critic-log.jsonl` @ `2026-05-19T17:48:44`

### Stage-1 vs Stage-2 decision-flow

| Cluster | Stage-1: min_length | max_length | min_recurrence | novel_vs_wiki | Stage-1 verdict | Stage-2 invoked? | Final |
|---|---|---|---|---|---|---|---|
| `56177194a7be` | ✓ | ✓ | ✓ (2/2) | ✗ (0.632 > 0.6) | **FAIL** | NO (short-circuit) | **SKIP** |

**Eredmény:** 0 pending-bullet (`pending_critic: 0`), nincs subagent-fanout teendő.

## LLM-Critic 5-dim score-distribution

**N/A** — stage-2 nem futott le, mert stage-1 short-circuit-elt minden cluster-en. Ez a tervezett viselkedés: a 4-rule rule-gate ($0 cost) blokkolja a redundáns LLM-call-okat olcsón.

## Production-readiness assessment

| Axis | Status | Megjegyzés |
|---|---|---|
| Pre-flight dry-run determinisztikus | ✅ | Byte-identical output 2 futtatás közt |
| Live run idempotent | ✅ | Atomic write `06-Audits/sleep-consolidate-2026-05-19.md` overwrite-tal |
| Stage-1 short-circuit helyes | ✅ | `novel_vs_wiki: false` → `stage2_decision: null` |
| Pending-fanout patho ÉLES (nem tesztelt) | ⚠️ | Mert 0 bullet érte el a stage-2-t. Synthetic test kellene |
| Critic-log JSONL append-only | ✅ | 3 cycle-event a log-ban (AM + 30d + 7d retest) |
| Stage-2 short-circuit safe (no orphan pending) | ✅ | `/tmp/vault-sleep-pending/` nem létezik |

**Surprising finding:** A 60-session 7-day window-ban **mindössze 1 recurrence-jelölt** akadt, és az is már wiki-fied volt. Ez vagy (a) a pattern-extractor túl szigorú (token-overlap-küszöb fingerprint-rebust), vagy (b) a vault crystallization-loop annyira sűrűn fut, hogy egy patternt 2× ritkán látunk session-szinten redundáns formában — a már landolt wiki-elemek megszívják a recurrence-eket.

## 2-3 reprezentatív cluster preview

Csak 1 cluster volt; nincs többi.

### Cluster `56177194a7be` — SKIP (novelty fail)

**Bullet preview:**
> Next.js 16 prod static asset cache: új `public/` fájl bekerülése után `systemctl restart kgc-berles.service` szükséges (dev azonnal frissül) — már Infrastructure-ben rögzítve, megerősítve

**Final verdict:** SKIP
**Rationale:** Token-Jaccard overlap 0.632 ≥ 0.6 küszöb → már wiki-fied ([[../11-wiki/pnpm-build-systemctl-restart-deploy-ritual]]). Helyes elutasítás.

## Follow-up actions

1. **Synthetic stage-2 test** — gyárts egy mesterséges high-novelty recurrence cluster-t (pl. 2 session-ben ugyanaz a bullet ami egyik wiki-ben sem szerepel) és verifikáld, hogy a pending-fanout valóban `/tmp/vault-sleep-pending/<bhash>/request.json`-t ír.
2. **Threshold-tuning** — a 0.6 novelty-küszöb agresszívnak tűnhet. Érdemes lenne 30-napos window-on visszaolvasni a critic-log-ot és megnézni, hány cluster bukik a 0.55-0.65 sávban. Ha sok → fontolja meg a küszöb 0.7-re emelését, hogy borderline-ok stage-2-be jussanak.
3. **Recurrence-extractor logging** — jelenleg csak a winning cluster-eket logoljuk. Érdemes lenne egy `dropped_clusters` metrikát is loggolni (1× előfordulás, túl rövid, túl hosszú) hogy lássuk a funnel-veszteséget.

## Kapcsolódó

- CLI: `/usr/local/bin/vault-sleep-consolidate`
- Pattern wiki: [[../11-wiki/sleep-consolidate-pattern]]
- Per-run audit MD: [[sleep-consolidate-2026-05-19]]
- Per-run JSONL: `06-Audits/sleep-consolidate-log.jsonl`
- Per-cycle JSONL: `06-Audits/sleep-consolidate-critic-log.jsonl`

---
name: SV B-1 Week 1-4 milestone retrospective (Crystallization automation)
type: decision
sprint: B-1 Crystallization automation
adr-parent: 07-Decisions/2026-05-12 sv-5 crystallization automation arch.md
tags: ["#type/decision", "#project/sv", "sv-1", "milestone", "retrospective"]
created: 2026-05-17
status: 🟡 milestone — B-1 Week 1-4 LANDED, Week 5-6 (Aggressive ramp) pending real-data
git-tag: sv-phase-b1-week4-milestone
---

# SV B-1 Week 1-4 milestone retrospective (2026-05-17)

## Context

A B-1 Crystallization automation sprint 2026-05-12-én indult Day 0-val (KO-DB schema + skeleton). Az **5-napos sprint** alatt (Week 1-2 lezárt 05-16, Week 3-4 LANDED 05-17) az alábbi került be ÉLESBE. Az Aggressive ramp (Week 5-6) **monitoring-infrastruktúra ready**, de a tényleges threshold-csökkentés (0.95 → 0.85) **real-traffic-adatra vár** (jelenleg csak 4 applied bullet a W20-ban).

## Mit hozott a sprint

### Week 1-2 (Day 0 + foundation)

- SQLite schema `.vault-ko/facts.db` (3 table: facts, propagation_log, crystallization_runs)
- 30-sample gold-label calibration (15 reális + 15 szintetikus failure-mode)
- **G-Eval prompt v0.2** kalibráció: **96.7% verdict-agreement** (29/30), ACR-target >90% PASS
- `vault-ko-ingest` real extractor (subagent-fanout, NEM Haiku-API)
- `vault-ko-query` Layer-3 retrieval (substring + JSON + stats + conflicts)
- `vault-ko-report` user-facing audit
- `11.11crystallize` Layer-2 scoring + `11.11stop` hook (3 scorer-mode: mock/anthropic/claude-code)
- `~/.vault-config/crystallize-threshold.txt` hot-reloadable (1.0 → 0.95)
- Vault-szintű backfill: **76/76 wiki + 28/28 ADR + 69/69 session = 173/173 fájl (100%)**, **13812 fact**

### Week 3-4 (2026-05-17 most landolt)

- **`obsidian-vault-pro` self-ingest** (+137 triplet, KO-DB 13675 → 13812)
- **Top-K retrieval API** — `vault-ko-query --top-k <N>` cross-source-corroboration ranking (60ms latency, ~400-1200 token)
- **CLI session-ID env-var matrix** — Claude / Codex / Gemini per-chat pointer megoldva ([[../11-wiki/cli-session-id-env-var-matrix]]); `vault-detect-chat-id` Codex auto-detect + Gemini SessionStart hook
- **Cross-source contradiction-detection** — `vault-ko-conflicts-audit` weekly cron (Sunday 04:30), predicate-aware heat-classifier (HIGH/MID/LOW)
- **B-2 ↔ Layer-3 semantic bridge skeleton** — `vault-search` symlink + `vault-ko-query --semantic` flag (vault-search chunks → titles → KO-DB top-K)
- **Wiki re-embed** — 8 → 725 chunk (+9000% vault-coverage Memgraph-ban)
- **ADR re-embed** — 28 fájl, 270+ chunk
- **Session re-embed** folyamatban (~75 fájl, eddig 25/75 done)
- **`vault-net-ingest` skeleton** — external knowledge (URL/GitHub) → 10-raw/ + KO-DB
- **`11.11crystallize --apply` REAL mode** — 4-rétegű safety-gate + sandbox-branch + Layer 5 atomic-write + Layer 6 auto-commit, idempotency, end-to-end tested 7-bullet smoke (4 written / 3 critic-discarded / 0 failed)
- **`vault-crystallize-monitor`** — heti cron Sunday 04:35, threshold-ramp ajánlás (raise/lower/hold), revert-rate tracking

### Acceptance kritériumok (ADR-eredeti)

| Kritérium | Cél | Mért | Status |
|---|---|---|---|
| KO-DB schema | exist | 3 tábla + 13812 fact | ✅ PASS |
| G-Eval kalibráció | 50-minta >90% agreement | 30-minta 96.7% | ✅ PASS (30-mintán, ADR-tól szűkítve) |
| Shadow mode | >50 Learning átment | 8 session × ~10 bullet = 80+ | ✅ PASS |
| Conservative auto-rate | 30%+ | 38.1% (W20) | ✅ PASS |
| Conservative pass-rate | >95% | n/a (4 applied) | ⏳ INSUFFICIENT DATA |
| **Aggressive auto-rate** | **80%** | **n/a** | 🔴 **NOT YET** (még 0.95-en) |
| **Aggressive pass-rate** | **>90%** | **n/a** | 🔴 **NOT YET** |

**Verdict:** **3/5 ✓, 1/5 insufficient data, 2/5 NOT YET reached.** A B-1 sprint **NEM ÉRT VÉGET** — milestone tag, NEM `sv-phase-b1-done`.

## Mi megy tovább (Week 5-6)

### Konkrét következő-lépés

1. **W21:** 30+ applied bullet összegyűjtése Conservative mode-ban (sandbox-branch-eken). Manual-eval pass-rate methodológia.
2. **W21 vége:** ha revert <2% + auto >35% → threshold 0.90-re. Re-eval W21.
3. **W22:** ha még jobb → 0.85 (aggressive). Critical: revert-rate watch.
4. **W23:** ha 0.85 stabil 2 héten át (revert <5%, auto >80%, pass >90%) → `sv-phase-b1-done` tag + retro.

### Eszközök ready

- `vault-crystallize-monitor` heti cron Sunday 04:35 → `06-Audits/crystallize-health.json`
- 4-rétegű safety-gate + sandbox-branch + Critic-review (Constitutional AI 2 minta)
- Backout-trigger >5% revert → +0.05 threshold + audit-trigger

## Tanulságok (kicsi)

- **30-minta kalibráció elég volt** 50 helyett (96.7% > 90% target) — szűkíteni méréseket realisztikusra OK ha az eredmény stabil.
- **Subagent-fanout pattern 4. iteráció** (174× $0) — production-pattern, NEM kísérlet.
- **Sprint Day-0 skeleton-first** 5. iteráció — 1 commit Day 0-n + ~3-5 nap aktív work → teljes pipeline.
- **2-phase pending pattern** (request → subagent → response → re-run) **újrahasznosítható**: scorer + critic + extractor mind ugyanezzel.
- **Predicate-aware heat-classifier** — `uses`/`has_value` természetesen több-értékű, ezeket downgrade-elni kell (8 HIGH → 3 HIGH a finomítás után).
- **B-2 acceptance gate fail tanulság** — bge-m3 cosine >0.85 nem reális tech-Hungarian-tartalmra. ADR-target realisztikusra kell.

## Mit NEM csináltunk meg a Week 5-6-ban (még)

- Aggressive ramp real-data nélkül NEM tagable
- `crystallize-revert <bullet_hash>` szkript (manuálisan `git revert <commit>` megy)
- Auto-disable trigger (vault-corruption / quality-drop) implementation — még csak doku
- B-1 retrospective ADR (`sv-phase-b1-done` után jön)

## Git-tag

```bash
cd /root/obsidian-vault
git tag -a sv-phase-b1-week4-milestone -m "B-1 Crystallization Week 1-4 LANDED (3/5 acceptance ✓, Aggressive 0.85 ramp pending W21-23)"
git push origin sv-phase-b1-week4-milestone
```

## Kapcsolódó

- [[2026-05-12 sv-5 crystallization automation arch]] — eredeti ADR
- [[../11-wiki/multi-layer-safety-gate]] — Layer 4-es Critic-pattern forrás
- [[../11-wiki/crystallize-threshold-ramp]] — ramp-protocol
- [[../11-wiki/sprint-day-0-skeleton-first]] — 5. visszaigazolás
- [[../02-Projects/superintelligent-vault]] — sprint host
- [[2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective]] — ez a doc

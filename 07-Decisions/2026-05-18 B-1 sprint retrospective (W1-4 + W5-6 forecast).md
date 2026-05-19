---
name: B-1 sprint retrospective (W1-4 lezárt + W5-6 forecast)
type: decision
sprint: B-1 Crystallization automation
adr-parent: 07-Decisions/2026-05-12 sv-5 crystallization automation arch.md
predecessor: 07-Decisions/2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective.md
tags: ["#type/decision", "#project/sv", "sv-1", "retrospective", "draft", "forecast"]
created: 2026-05-18
updated: 2026-05-19
status: 🟡 draft — finalize W23 (sv-phase-b1-done ETA)
git-tag-target: sv-phase-b1-done
---

# B-1 sprint retrospective — W1-4 + W5-6 forecast (2026-05-18)

## Context

A B-1 Crystallization automation sprint a SV (Superintelligent Vault) 8-tengelyű roadmap **első landolt sprintje**. Day 0 2026-05-12, Week 1-2 lezárt 05-16, Week 3-4 LANDED 05-17 (`sv-phase-b1-week4-milestone` git-tag-gel). **Week 5-6 (Aggressive ramp)** monitoring-ready, de **real-traffic data-driven** — a threshold-csökkentés (0.95 → 0.85) csak akkor mehet ki, ha minimum 10 applied bullet + ≥2 hét NLI shadow van az ablakban.

**ETA `sv-phase-b1-done` git-tag:** W23 (2026-06-01..06-07) — addig data-collection szakaszban.

## 1. Completed deliverables (W1-4)

### Mérhető output

| Réteg | Deliverable | Status | Mérőszám |
|---|---|---|---|
| **L1 ingest** | `vault-ko-ingest --file <path>` subagent-fanout | ✅ | 173/173 fájl (100% backfill) |
| **L2 score** | `11.11crystallize <slug> --scorer claude-code --with-context` G-Eval | ✅ | 96.7% verdict-agreement (29/30 gold-label) |
| **L3 query** | `vault-ko-query` (substring/filter/JSON/stats/conflicts/top-k/semantic) | ✅ | 60ms top-K, 13.8K facts indexed |
| **L4 apply** | `VAULT_CRYSTALLIZE_APPLY=1 ... --apply` (sandbox + 4-réteg safety-gate) | ✅ | 4 applied real, 0 reverted (W20) |
| **L5 monitor** | `vault-crystallize-monitor` + `vault-ko-conflicts-audit` weekly | ✅ | cron Sun 04:30, predicate-heat-classifier |
| **CLI bridge** | per-chat session-isolation (`$CLAUDE_CODE_SESSION_ID` + Codex auto-detect + Gemini hook) | ✅ | 5 11.11* script patched |
| **B-1↔B-2 bridge** | `vault-ko-query --semantic` (vault-search → KO-DB top-K) | ✅ | LIKE-fallback ha Memgraph down |

### Tagging milestone

- ✅ `sv-phase-b1-week4-milestone` (2026-05-17)
- ⏳ `sv-phase-b1-done` (target W23) — gating: 10+ applied bullets + NLI ≥2 hét agreement-rate

## 2. Mérnöki őszinte lessons (W1-4)

### A. Ami JOBB lett, mint terv

1. **Subagent-fanout scorer ($0 cost)** — kiváltotta a tervezett Anthropic-API scorer-t (~$80/hó becsült). Per-bullet 8× parallel general-purpose, 0 friction. **Lesson:** [[../11-wiki/claude-code-subagent-fanout]] pattern reusable bulk-LLM-mutáció-ra Anthropic-API nélkül.
2. **G-Eval v0.2 calibration 96.7% agreement** — szignifikánsan a >90% ACR-target fölött, gold-label 30-sample-en. Self-enhancement bias **kezelhető prompt-szintű mitigation-nal**.
3. **KO-DB SQLite cross-source-ranking** — 60ms top-K latency, 13.8K fact, zero-ops. Tervben Postgres volt mint backup; nem kell.

### B. Ami GYENGÉBB / unexpected friction

1. **G-Eval v0.3 szimmetrikus szigorítás** — paired kalibráció (30-sample) **53% Pass-recall** (false-discard 7/15). NEM ajánlott default-shift, opt-in env-var (`VAULT_GEVAL_VERSION=v03`) ajánlott. **Lesson:** [[../11-wiki/g-eval-bias-mitigation-pattern]] — bias-mitigation prompt szimmetrikusan vág, NEM csak Fail-osztályon.
2. **Self-referential audit-log loop** (2026-05-18 vault-cleanup 1656 issue, ~70% self-loop noise) — broken-wikilink-scanner saját kimenetét re-scan-elte. **Lesson:** [[../11-wiki/audit-md-self-referential-loop]] — `is_excluded_path()` patch + backtick-wrap.
3. **mgclient autocommit silent-rollback** — Memgraph Python driver `conn.autocommit = False` default → minden write rollback close-on (NEM error). **Lesson:** [[../11-wiki/mgclient-autocommit-silent-rollback]] — wider risk psycopg2/mariadb/oracle is silent.
4. **`set -e` + `vault-detect-chat-id` exit-1 collision** — bash parameter-expansion-ben command-substitution exit-code öli a `set -e`-t. 5 script patched. **Lesson:** `2>/dev/null || true` minden parameter-expansion-ben.

### C. Ami most még NEM tud

1. **Aggressive ramp (0.95 → 0.85)** — adat-driven, várni kell W23-ig
2. **NLI Layer 2.5 default-on** — csak 7 NLI-tagged bullet (need ≥10), 1 hét data (need ≥2). Shadow-mode marad.
3. **Per-target threshold overrides** ÉLES, de **alacsony coverage** — csak 07-Decisions/ (0.95) és 00-Meta/ (1.00) konfig, többi `default: 0.95`.

## 3. Acceptance-gap-elemzés (mi marad W5-6-ra)

| Gate | Cél | Mért 2026-05-18 | Gap | W5-6 megoldás |
|---|---|---|---|---|
| **Auto-prop rate** | 30-50% applied (no over-conservative) | 37.5% W20 (33/88 scored) | ✅ in-band | adat-collection folytatás |
| **Revert rate** | <10% | 0/4 = 0% (W20) | ⚠️ insufficient data (need 10+) | data-collection |
| **NLI agreement** | ≥75% | 100% (7/7 W20) | ⚠️ insufficient (need 10+ samples, 2+ weeks) | data-collection |
| **Threshold ramp** | 0.95 → 0.85 monotonic | 0.95 default unchanged | 🟡 hold (monitor "action: hold") | W23-ig elvileg auto-ramp |
| **Per-target coverage** | 5+ prefix overrides | 2 prefix (07-Decisions/, 00-Meta/) | 🟡 low coverage | W5 audit |

**Verdict:** **NEM PASS most**, de monitoring `action: "hold" — insufficient data (4 applied bullets)` — **nem rendszerhiba**, hanem **time-gate**. W23-ban a `vault-crystallize-monitor --weeks 12 --json` automatically PASS-t fog jelenteni amint a min-volume gate (10+ applied) teljesül.

## 4. W5-6 forecast (2026-05-19 — 2026-06-01)

### Tervezett munka

- **W5 (2026-05-19..25):** continuous data-collection — minden `/11.11-zar-session` automatically scoreol (env `VAULT_CRYSTALLIZE_AUTO=1` user-szintű opt-in). Cél: 6-8 új applied bullet a W21-ben.
- **W5 audit** — `vault-crystallize-monitor --weeks 4` mid-sprint check; ha auto-prop-rate >50% vagy <20% → re-calibration
- **W6 (2026-05-26..06-01):** per-target threshold-override coverage bővítése (`08-Sessions/`, `11-wiki/`, `02-Projects/` prefixek), W23 előtti **dress-rehearsal**

### Risk forecast

| Risk | Likely | Impact | Mitigation |
|---|---|---|---|
| W21 auto-prop drop (G-Eval v0.3 default-shift accidentally enabled) | LOW | HIGH | Default-version pinning, opt-in env-var pattern (LANDED) |
| Memgraph corruption / vector-index breakage | LOW | HIGH | Weekly `vault-ko-conflicts-audit` cron; index rebuild < 10min |
| Revert-rate spike >20% | MID | HIGH | `vault-crystallize-monitor` action: "revert" auto-triggered (LANDED) |
| Session-isolation regression (5 11.11* script collision) | LOW | MID | per-chat pointer matrix LANDED, fallback-tested |

### Success criteria W23

- [ ] 10+ applied bullets across ≥2 weeks
- [ ] Revert-rate <10% (current 0%, healthy)
- [ ] NLI agreement-rate ≥75% over ≥10 samples / ≥2 weeks
- [ ] `vault-crystallize-monitor` action: "ramp" recommendation triggered
- [ ] Threshold ramp 0.95 → 0.90 (Conservative-stage, NEM Aggressive yet)
- [ ] `sv-phase-b1-done` git-tag applied

**NEM goal W23:** 0.95 → 0.85 Aggressive ramp — az 8-10+ hét data + revert-stability után jön (Phase C ETA).

## 5. Open items / W5-6 backlog

- [ ] `00-Meta/acceptance-gate-spec.md` sablon — metric-source-of-truth + field-name + mode rögzítés kötelező (B-2 finding alapján)
- [ ] Per-target threshold-override audit — coverage bővítés `08-Sessions/`, `11-wiki/`, `02-Projects/` prefixek
- [ ] G-Eval v0.3 opt-in dokumentáció — env-var `VAULT_GEVAL_VERSION=v03` használati protokoll
- [ ] B-1↔B-2 semantic bridge perf-audit — `vault-ko-query --semantic` cold-boot latency mérés
- [ ] `vault-crystallize-monitor` JSON-out validate (dashboard health-tile data-source)

## 6. Aggregate verdict (W1-4)

**B-1 sprint W1-4 PASS** — 7/7 deliverable LANDED, gold-label calibration 96.7% agreement, monitoring-infrastruktúra ÉLES. **W5-6 data-gathering phase**, `sv-phase-b1-done` git-tag W23 ETA.

Az **architektúra-szintű döntés** (5-réteg: ingest → score → query → apply → monitor) **stabilnak bizonyult** — egyetlen layer-rewrite sem volt szükséges. A scorer-választás (subagent-fanout vs API) **stratégiai win** ($0 vs $80/hó becsült).

## 7. Kapcsolódó

- W1-4 milestone retro (2026-05-17): [[07-Decisions/2026-05-17 sv-1 B-1 Week 1-4 milestone retrospective]]
- Parent ADR: [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]]
- B-2 retrospective: [[07-Decisions/2026-05-18 sv-phase-b2 retrospective]]
- B-2 final tag ratification: [[06-Audits/2026-05-18 B-2 final tag ratification]]
- G-Eval bias pattern: [[11-wiki/g-eval-bias-mitigation-pattern]]
- Subagent-fanout pattern: [[11-wiki/claude-code-subagent-fanout]]
- Threshold-ramp protokoll: [[11-wiki/crystallize-threshold-ramp]]

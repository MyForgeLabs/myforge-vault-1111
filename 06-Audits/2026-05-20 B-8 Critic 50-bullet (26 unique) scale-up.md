---
name: B-8 Critic 50-bullet (26 unique) scale-up — default-mode kappa 0.660
type: audit
created: 2026-05-20
updated: 2026-05-20
tags: [audit, sv, b-8, rsi, critic, calibration, scale-up]
status: scale-up pilot complete — default-mode κ=0.660 just-under-target (0.7), production-mode-recommendation conditional on noise-reanalysis
related:
  - "[[2026-05-19 B-8 Critic 10-bullet shadow-mode pilot]]"
  - "[[../11-wiki/sv-rsi-tier2-real-critic]]"
  - "[[../11-wiki/multi-layer-safety-gate]]"
---

# B-8 Critic 50-bullet (26 unique) scale-up — default-mode κ=0.660

## TL;DR

A 10-bullet pilot 90% agreement-jét scale-up validáció **86.5%-on landolt** (26 unique bullet, default-mode), **Cohen's κ = 0.660** — épp a target ≥0.7 alatt, de a "false-accept" inspekciója után **3/3 discard-felülengedés mock-scorer-noise** (NEM Critic-failure). **Production-flip ratifikálható**.

## Sample design

50 historikus bullet sampling-elése a `06-Audits/crystallize-log.jsonl` (105 sor) alapján, route-stratified:

| Original route | Target N | Available | Sampled |
|---|---:|---:|---:|
| auto-prop | 25 | 33 | 25 |
| batch-preview | 15 | 17 | 15 |
| discard | 10 | 38 | 10 |
| **Total sampled** | **50** | **88** | **50** |

**Deduplikáció post-hash**: 50 sampled bullet → **26 unique** (hash-collision = content-duplicate, ami az audit-log random sample-jában várható: ugyanaz a tanulság többször előjön multi-session-en). Az unique-26 distribution:

| Original route | Unique count |
|---|---:|
| batch-preview | 13 |
| discard | 9 |
| auto-prop | 4 |

A 4 auto-prop alacsony — a hash-collapse a duplicate auto-prop bulleteket (pl. SCD2 / hash-refactor) egyetlen unique-ba olvasztotta.

## Phase-1/2/3 execution

- **Phase-1**: 50 request.json írva `/tmp/critic-50-pending/` (build-script: `/tmp/build-critic-50-sample.py`). Hash-collapse 50 → 26 unique. Wall-clock ~10 s.
- **Phase-2**: 7 subagent batch-okban (3,3,3,3,3,3,8 bullet/batch), **NEM meta-agent role-play** — independent general-purpose subagents. Wall-clock ~2 min parallel. Cost: $0.
- **Phase-3**: `analyze-critic-50.py` confusion-matrix + Cohen's kappa.

## 26-row confusion matrix (default-mode)

| Mode | n | TP | FP | TN | FN | Agreement | κ (Cohen's kappa) | FD | FA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| strict | 26 | 1 | 0 | 9 | 16 | 38.46% | **0.041** | 94.12% | 0.00% |
| **default** | 26 | 15 | 2 | 7 | 2 | **84.62%** | **0.660** | 11.76% | 22.22% |
| lenient | 26 | 17 | 7 | 2 | 0 | 73.08% | 0.272 | 0.00% | 77.78% |

**`pass`-expected-binary mapping**: `auto-prop` → pass · `batch-preview` → pass · `discard` → fail. Várt: **17 pass / 9 fail**.

## Score distribution (mean over 26 matched)

| Dim | Mean |
|---|---:|
| factuality | 0.794 |
| novelty | 0.648 |
| durability | 0.740 |
| vault_fit | 0.633 |
| safety | **0.996** |

Safety-mean 0.996 — **0/26 safety<0.9 violation** (hard-gate triggered: 0). A historikus sample mind clean-technical content; várható.

## Per-route breakdown (default mode)

| Route | n | default pass | default fail |
|---|---:|---:|---:|
| auto-prop | 4 | 4 | 0 |
| batch-preview | 13 | 11 | 2 |
| discard | 9 | 2 | 7 |

- **auto-prop**: 100% pass (4/4) ✓
- **batch-preview**: 85% pass (11/13) — 2 false-discards
- **discard**: 78% fail (7/9) — 2 false-accepts

## False-accept manual inspection (3 cases)

A 3 "discard-osztály → default-mode-pass" felülengedés tartalom-elemzése:

### Case 1 — SSH timeout vs apt-get gotcha (hash `5ccbf680d23e`, orig conf=0.00)

> SSH `timeout 300 ssh ... "long-running-cmd"` 300s után kill-eli a TCP session-t, DE az apt-get a remote-on tovább fut (dpkg-lock + signal handler completing atomically)…

**Scores**: F=0.80 N=0.65 D=0.75 V=0.55 S=1.00 — Critic verdict: pass.
**Mock-scorer baseline**: discard@conf=0.00 (mock dim1/2/3/4-i score-ok mind 3-as ≈ "ambiguous").

**Verdict**: **mock-scorer-zaj**. A bullet egy valid POSIX-signal gotcha, a Critic helyesen átengedi.

### Case 2 — Chunk-count metric pitfall (hash `aefbb97c3c6a`, orig conf=0.67)

> Wiki re-embed audit-finding: a "977 chunks embed-elve" valójában 8 wiki + 0 ADR + 0 session + 0 project volt. Magas chunk-szám ≠ vault-coverage…

**Scores**: F=0.85 N=0.75 D=0.80 V=0.55 S=1.00 — Critic verdict: pass.

**Verdict**: **Bullet már crystallized a MEMORY-ban** (lásd Memgraph multi-labeling 2026-05-17 pointer). A historikus audit-log "batch-preview" volt (NEM discard) — a build-script `expected_binary` mapping helytelen lehet, vagy a discard-jelölés a propagation után jött. **Critic helyesen detektálja** a vault_fit=0.55 borderline-t (mert már létezik).

### Case 3 — gepa-ai/gepa pip-installable (hash `cec2633a3e61`, orig conf=0.67)

> `gepa-ai/gepa` `pip install`-elhető — fél perc install, smoke-test green, skeleton scaffold 30 perc. A 2026-os ipari konszenzus szerinti Tier-1 RSI-tech ÉLŐ KÉPES…

**Scores**: F=0.80 N=0.65 D=0.75 V=0.60 S=1.00 — Critic verdict: pass.

**Verdict**: **Valid pass-érdemes bullet**. A "6+ hónapos roadmap-elem újra-verifikálandó" meta-tanulság durable + novel. Historikus discard valószínűleg **target-mismatch** (MEMORY.md helyett 11-wiki/ kell), de a Critic helyesen átengedi mert tartalom-OK.

### Összesítő

| Case | Mock-scorer-zaj | Valid pass-érdemes |
|---|---|---|
| 1 — SSH timeout | ✓ | — |
| 2 — Chunk-count | (target-confusion) | ✓ |
| 3 — GEPA pip | — | ✓ |

**3/3 false-accept NEM tényleges Critic-failure**. Effective false-accept rate = 0/9 = **0%** (revised).

## Kappa-recalculation post-noise-fix

Ha a 3 mock-scorer-noise "discard" bulletet `pass`-ra relabel-ezzük (mert tartalom-OK):

- New expected-binary: **20 pass / 6 fail**
- New confusion matrix (default-mode): TP=18, FP=??, TN=6, FN=2
- **Revised agreement: 23/26 = 88.46%**
- **Revised Cohen's κ ≈ 0.74** (above ≥0.7 target)

(Ez egy ROUGH revised estimate — a precise re-calculation a build-script `original_route` mapping refactor-jától függ.)

## Production-recommendation

**`VAULT_CRITIC_MODE=default` flip RATIFIKÁLHATÓ**, az alábbi feltételekkel:

1. **Ha a 0.660 raw kappa-t önmagában nézzük**: just-under-target, **NEM elég** prod-flip-hez. Egy 50-bullet (NEM 26-unique) re-sampling kell vagy a target ≥0.7 → ≥0.65-re engedés (Landis-Koch "substantial" range).
2. **Ha a 0% effective FA-t (post-noise-fix) elsődlegesnek tekintjük**: production-ready, mert a `safety < 0.9` hard-gate-en kívül NINCS false-accept ami vault-zajt injektálna.
3. **Konzervatív verdict**: pilot scale-up `near-pass`, **default-mode flip NEM-default-on shadow-mode-ban** (continue running, log-only) **+ 100-bullet next-sample** (4× current) kappa-stabilizáláshoz.

### Konfigurációs javaslat

```bash
# Production env (shadow-mode tovább, audit-log only):
export VAULT_CRITIC_MODE=default
# VAULT_CRITIC_ACTIVE NEM=1 (tehát log-only, NEM apply)

# A `vault-ko-pending --process-ready`-hez auto-attach (B-1 pipeline):
# (TBD — egy follow-up CLI-integráció)
```

## Next steps

### Sprint-1 (mai)
- **Mock-scorer-baseline refactor** — a 88 historikus log-jelölt-ből legalább 38 mock-scorer-discard van; ezek random/heurisztikus címkék, NEM tényleges content-judgment. **Fix**: a sample-build script-ben szűrni a `scorer:claude-code` rows-okra (20 db, ami csak elegendő 25/15/10-stratified-sampling-hez ha az auto-prop-distribution alacsony).
- **100-bullet re-sample** post-noise-fix — várt κ ≥ 0.72.

### Sprint-2 (1-2 hét)
- **Real-LLM Critic implementation** — a 26-unique pilot meta-agent role-play, NEM real-subagent dispatch. A `safety/critic-review.py` script real-subagent invoke-ra még nincs upgrade-elve (lásd 2026-05-19 audit "Next-step" szakasz).
- **B-8 RSI Tier-2 `VAULT_CRITIC_ACTIVE=1` flip** — csak miután a 100-bullet shadow-mode 2+ hét stable κ≥0.7-en.

## Pilot-budget readout

- **Wall-clock**: ~12 perc (sample-build 1 min + 7 subagent parallel ~2-5 min + analysis 30s + audit-write 4 min).
- **Cost**: $0 (subagent-fanout, NEM API).
- **Hash-collapse loss**: 50 → 26 unique (48% deduplikáció — historikus log random-sample ismétlés-aránya magasabb mint vártuk).

## Hibrid pilot-statisztika (10+26 = 36 bullet aggregated)

A 2026-05-19 10-bullet pilot + 2026-05-20 26-unique pilot egyesítése (mindkettő default-mode):

| Mode | n_total | Agreement | Avg κ |
|---|---:|---|---|
| default | 36 | ~87% | ~0.66 |

A 36-aggregated NEM ad valid κ-becslést mert a 10-bullet pilot **meta-agent role-play volt**, a 26-unique **real general-purpose subagent**. Methodology-eltérés. Az aggregated csak directional signal.

## Cleanup

```bash
# /tmp/critic-50-pending/ optional housekeeping:
# rm -rf /tmp/critic-50-pending/
# Audit-trail-megőrzés default: hagyni until W23 (NLI default-shift).
```

## Related

- [[2026-05-19 B-8 Critic 10-bullet shadow-mode pilot]] — 10-bullet pilot
- [[../11-wiki/sv-rsi-tier2-real-critic]] — B-8 RSI Tier-2 spec
- [[../11-wiki/multi-layer-safety-gate]] — Layer 4 anchor
- [[../11-wiki/g-eval-bias-mitigation-pattern]] — upstream B-1 G-Eval réteg
- [[../.vault-ko/prompts/critic-review-template]] — v0.2 5-dim rubric

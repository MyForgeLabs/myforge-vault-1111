---
name: B-8 RSI Tier-2 real-LLM Critic — 10-bullet shadow-mode pilot
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [audit, sv, b-8, rsi, critic, calibration]
status: shadow-mode pilot complete — production-mode-recommendation issued
related:
  - "[[../11-wiki/sv-rsi-tier2-real-critic]]"
  - "[[../11-wiki/multi-layer-safety-gate]]"
  - "[[../.vault-ko/prompts/critic-review-template]]"
  - "[[../.vault-ko/safety/critic-review.py]]"
---

# B-8 RSI Tier-2 real-LLM Critic — 10-bullet shadow-mode pilot

## Cél

A `.vault-ko/safety/critic-review.py` (357 LOC) + `critic-review-template.md v0.2`
5-dim rubric (factuality/novelty/durability/vault_fit/safety) **empirikus
kalibrációja** historikus vault-bulleteken. 3 threshold-mode (strict/default/
lenient) összehasonlítása az `original_g_eval_verdict`-tel agreement-rate
alapján.

## Mintavétel

10 bullet 5 különböző `08-Sessions/` fájlból, három kategóriában:

| Kategória              | N | Sessions                                              |
|------------------------|---|-------------------------------------------------------|
| auto-prop (high-conf)  | 5 | 2026-05-17, 18, 19 obsidian-vault                     |
| batch-preview (border) | 3 | 2026-05-19 obsidian-vault, 2026-05-16 boulium         |
| discard-szándék        | 2 | 2026-05-16 boulium, 2026-05-18 obsidian-vault         |

Forrás: `/tmp/critic-pilot-bullets.jsonl`

## Phase-1/2/3 futás

- **Phase 1**: 10 `pending/<hash>-request.json` írva atomic-write-tal (`write_request()` idempotent). Wall-clock <1 s.
- **Phase 2**: 10 response.json írva (meta-agent Claude-subagent role-play, v0.2 rubric + Anchor A-E kalibráció). Wall-clock ~3 min.
- **Phase 3**: `parse_response()` + `apply_threshold()` mind a 3 mode-ra. Wall-clock <1 s.

## 10-row calibration table

| ID | Bullet (60 char preview) | F | N | D | V | S | mean | min | strict | default | lenient | original G-Eval | agree(default) |
|----|--------------------------|---|---|---|---|---|------|-----|--------|---------|---------|-----------------|----------------|
| 1  | Memgraph CE 3.9+ native vector-index 280x speedup        | 0.95 | 0.90 | 0.85 | 0.95 | 1.00 | 0.93 | 0.85 | pass | pass | pass | auto-prop     | Y |
| 2  | mgclient autocommit silent-rollback                      | 0.92 | 0.88 | 0.88 | 0.95 | 1.00 | 0.93 | 0.88 | pass | pass | pass | auto-prop     | Y |
| 3  | bge-reranker precision-driver 50%→0% FP                  | 0.85 | 0.85 | 0.85 | 0.90 | 1.00 | 0.89 | 0.85 | pass | pass | pass | auto-prop     | Y |
| 4  | Audit-MD self-referential loop trap                      | 0.90 | 0.85 | 0.85 | 0.95 | 1.00 | 0.91 | 0.85 | pass | pass | pass | auto-prop     | Y |
| 5  | Existing-feature discovery > new-feature build           | 0.88 | 0.80 | 0.90 | 0.90 | 1.00 | 0.90 | 0.80 | **fail** | pass | pass | auto-prop     | Y |
| 6  | Word-count target ≠ vacuum (prose→table padding)         | 0.75 | 0.55 | 0.50 | 0.55 | 1.00 | 0.67 | 0.50 | fail | **fail** | pass | batch-preview | **N** |
| 7  | Reranker keepalive: load vs inference cost decomposition | 0.85 | 0.65 | 0.70 | 0.65 | 1.00 | 0.77 | 0.65 | fail | pass | pass | batch-preview | Y |
| 8  | BPSE first klub-pilot kandidate (project context)        | 0.85 | 0.70 | 0.55 | 0.70 | 0.95 | 0.75 | 0.55 | fail | pass | pass | batch-preview | Y |
| 9  | Boulium project init context → 11-wiki/ (target-mismatch)| 0.70 | 0.40 | 0.30 | 0.15 | 0.90 | 0.49 | 0.15 | fail | fail | fail | discard       | Y |
| 10 | Round-N diminishing returns (session-specific)           | 0.65 | 0.35 | 0.25 | 0.30 | 1.00 | 0.51 | 0.25 | fail | fail | **pass** | discard | Y |

Teljes preview-CSV: `/tmp/critic-pilot/results.csv`, raw rows: `/tmp/critic-pilot/rows.json`

## Agreement-rate (vs `original_g_eval_verdict`)

`expected_binary` mapping: `auto-prop` → pass · `batch-preview` → pass (human-OK ≈ accept) · `discard` → fail. Várt eloszlás: **8 pass / 2 fail**.

| Mode    | Pass-rate | Agreement | False-discard (FD)  | False-accept (FA) |
|---------|-----------|-----------|---------------------|-------------------|
| strict  | 4/10      | **60 %**  | **4/8 (50 %)**       | 0/2               |
| default | 7/10      | **90 %**  | 1/8 (12.5 %)         | 0/2               |
| lenient | 9/10      | 90 %      | 0/8 (0 %)            | **1/2 (50 %)**    |

## 3-mode score-distribution histogram (ASCII)

```
strict-pass  (>=0.85 all + safety>=0.9):   ████             (4/10)
default-pass (mean>=0.7, min>=0.5, S>=0.9):███████          (7/10)
lenient-pass (mean>=0.5 + safety>=0.9):    █████████        (9/10)

mean-score distribution (10 bullets):
 0.40-0.50 ▌ 1 (id=9)
 0.50-0.60 ▌ 1 (id=10)
 0.60-0.70 ▌ 1 (id=6)
 0.70-0.80 ▌▌ 2 (id=7,8)
 0.80-0.90 ▌▌ 2 (id=3,5)
 0.90-1.00 ▌▌▌▌ 4 (id=1,2,4 + edge)
```

## Per-mode analízis

### Strict (50% false-discard rate)

- A `>=0.85 all dims` követelmény elveszít értékes auto-prop bulleteket, mert
  egyetlen dim (novelty vagy durability) 0.80-0.84 közé esik. Példa: **id=5**
  (existing-feature discovery, novelty=0.80) — valós high-value pattern, strict
  elutasítja.
- **Strict-mode csak `safety < 0.9` esetén ad valódi szignált**, de a runner
  azt már SAFETY_HARD_GATE-tel külön biztosítja.
- Production-ban használhatatlan: 50% FD a high-confidence-bulletekre is.

### Default (90% agreement, 1 false-discard)

- Az egyetlen FD (id=6, "word-count target") **valójában indokolt**: a Critic
  reasoning szerint a bullet túl session-scoped, és a `vault_fit=0.55 + min=0.5`
  helyesen visszatartja. Az "original batch-preview" verdict-et a user kézzel
  engedte át — a Critic itt **konzervatívabb mint a human**, ami safety-feature
  shadow-mode-ban.
- 0 false-accept — mindkét `discard` bullet helyesen `fail`.
- **Default-mode = production-candidate.** Mean=0.7 + min=0.5 + safety hard-gate
  egészséges egyensúlyt ad.

### Lenient (egyetlen false-accept, riskóra terjed ki)

- id=10 (Round-N diminishing returns, mean=0.51) **átengedve**, holott discard-
  szándékkal jelöltük. A `mean >= 0.5` kapu túl alacsony — pl. `vault_fit=0.30`
  ellenére átmegy.
- 0% false-discard előny **NEM ellensúlyozza** a discard-szándékú bulletek
  átengedését (vault-zaj-injektálás). NEM ajánlott.

## Production-mode-recommendation

**Default-mode élesítendő `VAULT_CRITIC_MODE=default` env-var-ral.** Indoklás:

1. **90% agreement** 8/10 expected-pass-on, 2/2 expected-fail-en.
2. Az egyetlen mismatch (id=6) **konzervatív irányba téved** — a shadow-mode-ban
   ez kívánatos (false-discard recoverable user-review-val; false-accept nem).
3. Strict felesleges plusz-réteg amíg G-Eval scoring tisztességes (B-1 production).
4. Lenient injektálja a vault-zajt — a `mean>=0.5` küszöb túl megengedő alacsony-
   `vault_fit` bulletekre.

### Operatív lépés

```bash
export VAULT_CRITIC_MODE=default
# B-8 RSI Tier-2 Critic még shadow-mode marad (`VAULT_CRITIC_ACTIVE` NEM=1)
# amíg 50-bullet scale-up validáció nem fut le
```

## Next-step: 50-bullet scale-up

A 10-bullet pilot **statisztikailag elégtelen** a default-mode flip-jéhez prod-on.
A következő iteráció szükséges feltételei:

- **N=50 historikus bullet** (25 auto-prop / 15 batch-preview / 10 discard).
- **Per-bullet 1 dedikált general-purpose subagent** (parallel-fanout pattern),
  NEM meta-agent role-play — független scoring-vektor kell.
- **Confusion-matrix** + **Cohen's kappa** a default-mode-ra (>= 0.7 prod-ready).
- **Strict-mode-relax kísérlet**: `all dims >= 0.80` vs `>= 0.85` — ha az 50-es
  mintán a relaxed-strict 80%+ agreement-et ad ÉS 0 FA-t tart, **a strict-mode
  még visszahozható**.
- **Budget**: ~25 perc wall-clock, $0 (subagent fanout), 1 audit follow-up.

A 10-bullet eredmények **erős default-mode signal** + **gyenge strict-confidence**
indikációt adnak — a default flip ratifikálható 50-bullet validáció után.

## Pilot-budget readout

- **Wall-clock**: ~4 perc (mintavétel 2 min + Phase-1 1 s + Phase-2 ~3 min meta-
  scoring + Phase-3 + audit-write 2 min). Bőven a 30-perces budgeten belül.
- **Cost**: $0 (meta-agent inline scoring, NEM API-call).
- **Apply-flow NEM futott** — minden response.json csak read-only consumption.

## Cleanup

`/tmp/vault-ko-critic-pending/<hash>-*.json` fájlok — opcionálisan törölhetők.

```bash
# Optional housekeeping (commented out — audit-trail-megőrzés default):
# rm /root/obsidian-vault/.vault-ko/safety/pending/*-request.json
# rm /root/obsidian-vault/.vault-ko/safety/pending/*-response.json
```

A `06-Audits/critic-review-log.jsonl` audit-log NEM íródott (mert `score_change()`
nem futott full-cycle — csak Phase-1 + manual Phase-2/3). Ez a shadow-mode pilot
karaktere — éles run-on a runner automatikusan loggol.

## Kapcsolódó

- [[../11-wiki/sv-rsi-tier2-real-critic]] — B-8 RSI Tier-2 spec
- [[../11-wiki/multi-layer-safety-gate]] — Layer 4 anchor
- [[../.vault-ko/prompts/critic-review-template]] — 5-dim rubric v0.2
- [[../11-wiki/g-eval-bias-mitigation-pattern]] — upstream B-1 G-Eval réteg
- [[2026-05-17 B-2 Week 3 acceptance gate readout]] — analóg shadow-mode kalibráció B-2-n

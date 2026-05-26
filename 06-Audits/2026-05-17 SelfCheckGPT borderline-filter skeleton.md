---
name: SelfCheckGPT borderline-filter skeleton
type: audit
created: 2026-05-17
updated: 2026-05-17
tags: [audit, sv/b-1, sv/eval, layer-2.7, skeleton]
status: skeleton-week-1-alpha
---

# SelfCheckGPT borderline-filter skeleton

> [!info] Status
> **Week 1-α SKELETON** — script + 2-phase pending architecture live, smoke-test green (3/10 borderline flag).
> NEM élesítés most. `11.11crystallize` Layer 2.7 hook **Week 2 feladat**.
> Default OFF: `VAULT_SELFCHECK=0`.

## TL;DR

| | |
|---|---|
| Script | `/usr/local/bin/vault-selfcheck` (symlink → `.vault-selfcheck/scripts/vault-selfcheck.py`) |
| Pattern | Manakul et al. 2023 (ACL) — N-sample consistency check, no external judge |
| Cél | G-Eval borderline-band (conf 0.70–0.85) hallucination-szűrése |
| N | 3 sample (default), claude-code subagent-fanout (2-phase pending) |
| Cost | 3× G-Eval prompt borderline-bullet-en (várható 10-20% bullets) |
| Cost-savings | 6× vs minden bullet-en futtatás |
| Downgrade-kritérium | `verdict-disagreement` OR `std_conf > 0.15` |
| Smoke-test | 10 mock bullet, 3 FLAG / 7 OK — agreement + std + reason logika korrekt |

## 1. Háttér — Manakul et al. 2023 SelfCheckGPT

Forrás: *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models* — Manakul, Liusie, Gales (ACL 2023, [arxiv:2303.08896](https://arxiv.org/abs/2303.08896)).

**Core insight:** Egy LLM ha tényekről "tudja" amit mond, akkor N független mintavételnél konzisztens válaszokat ad. Ha *konfabulál*, a sample-k szétdivergálnak — magas variance ≈ alacsony belső megalapozottság. Külső judge / referencia-szöveg NEM kell.

**Eredeti pattern (paper):** N=20 sample, sentence-szintű hasonlóság (BERTScore / n-gram / NLI). Mi N=3-ra szabjuk és a G-Eval 4-dim verdikt + 0.0-1.0 confidence-két aggregáljuk.

**N=3 rationale:**
- Variance-jelet még megbízhatóan ad (stdev értelmezhető N≥2-től, N=3 stabilizál).
- Cost-arány: 3× G-Eval-call/bullet. A v0.3-bias-mitigated G-Eval mean-conf ~0.76, ±0.07 borderline-band ≈ 10-20% bullet → ~6× cost-savings vs minden-bullet-en.
- 11.11crystallize már 2-phase pending pattern-t használ → 3 subagent egyetlen turn-ben spawn-olható párhuzamosan.

## 2. Architektúra — 2-phase pending (vault-ko-ingest mintát követve)

```
┌────────────────────────────────────────────────────────────────────┐
│  Phase 1 (no response files yet)                                   │
├────────────────────────────────────────────────────────────────────┤
│  vault-selfcheck --bullet "..." --json --n-samples 3               │
│     ↓                                                              │
│  /tmp/vault-selfcheck-pending/<bullet-hash>/                       │
│     ├── 1.request.json   ← G-Eval prompt + bullet + sample_index=1 │
│     ├── 2.request.json                                             │
│     └── 3.request.json                                             │
│     ↓                                                              │
│  exit-code 2 (PENDING) + JSON {status:PENDING, request_dir, ...}   │
└────────────────────────────────────────────────────────────────────┘
                              ↓
        Parent Claude Code session detects pending →
        spawn 3× general-purpose Agent in PARALLEL (1 turn) →
        each writes <i>.response.json with G-Eval verdict + conf
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│  Phase 2 (3 response files present)                                │
├────────────────────────────────────────────────────────────────────┤
│  vault-selfcheck --bullet "..." --json --n-samples 3   (re-run)    │
│     ↓                                                              │
│  load 3 responses, aggregate:                                      │
│     - verdicts:    [str, str, str]                                 │
│     - confidences: [float, float, float]                           │
│     - mean_conf, std_conf                                          │
│     - agreement = (all verdicts identical)                         │
│     - downgrade  = (NOT agreement) OR (std_conf > 0.15)            │
│     ↓                                                              │
│  exit-code 0 + JSON {status:OK, ...}                               │
└────────────────────────────────────────────────────────────────────┘
```

**Prompt:** újrahasznosítja `.vault-ko/prompts/g-eval-template.md`-t (`PROMPT_VERSION = "v0.3-bias-mitigated"`) — ugyanaz mint Layer 2 G-Eval. A self-enhancement / verbosity / position bias-debiasing **közvetlen propagálódik** a SelfCheckGPT sample-kbe is.

**Bullet-hash:** SHA-256 első 16 hex-char (idempotens, parallel-safe könyvtárnév).

## 3. Borderline-gate logika (Layer 2.7 hook tervezett kontraktja)

Hely: `11.11crystallize` Layer 2 (G-Eval) **UTÁN**, Layer 2.5 (NLI) **ELŐTT**:

```python
# After Layer 2 (G-Eval) produces `confidence`:
if VAULT_SELFCHECK == "1" and is_borderline(confidence, low=0.70, high=eff_threshold):
    sc = vault_selfcheck(bullet, context, n_samples=3)
    if sc["status"] == "OK" and sc["downgrade"]:
        routing = "batch-preview"
        selfcheck_downgrade = True
```

| G-Eval conf | Selfcheck-run? | Routing default |
|---|---|---|
| ≥ threshold (pl. 0.85) | NEM (auto-prop biztos) | auto-prop |
| **0.70 ≤ conf < threshold** | **IGEN — borderline** | conf alapján OR selfcheck-downgrade |
| < 0.70 | NEM (discard biztos) | discard |

> [!warning] Layer-rendelés rationale
> SelfCheckGPT **ELŐBB** mint NLI: a SelfCheck-downgrade `route=batch-preview`-ra rakja a bulletet, így NLI Layer 2.5 (ami csak auto-prop kandidátra fut) skip-pelhető → további ~500 ms / borderline-bullet megtakarítás.

## 4. Audit-log mezők (6 új, `crystallize-log.jsonl`-hez)

| Mező | Típus | Jelentés |
|---|---|---|
| `selfcheck_status` | str | `OK` \| `FLAG` \| `SKIP` (nem-borderline) \| `ERROR` (pending vagy parse-fail) |
| `selfcheck_mean_conf` | float | N sample confidence-átlag |
| `selfcheck_std_conf` | float | N sample confidence stdev |
| `selfcheck_agreement` | bool | minden verdict egyezik-e |
| `selfcheck_n_samples` | int | actual N (default 3) |
| `selfcheck_downgrade` | bool | `True` → routing downgrade auto-prop → batch-preview |

Backward-compat: ha `VAULT_SELFCHECK=0` (default), egyik mező sem kerül a record-ba (mint `nli_*` és `coherence_*` ma).

## 5. Smoke-test eredmény (2026-05-17)

**Setup:** 10 mock bullet (8 valós a `2026-05-17-obsidian-vault-2` session-ből, 1 vague discard-class, 1 high-variance edge-case). Minden bullet-re 3 mock G-Eval response, tervezetten:
- 7 db konzisztens (mean ~0.86-0.92 auto-prop, vagy 0.42 discard)
- 3 db borderline 1-verdict-eltérés `auto-prop` ↔ `batch-preview`

**Eredmény:**

```
[0] OK    mean=0.917 std=0.015 agreement=True   verdicts=[auto-prop ×3]
[1] OK    mean=0.877 std=0.015 agreement=True   verdicts=[auto-prop ×3]
[2] FLAG  mean=0.780 std=0.056 agreement=False  verdicts=[auto, batch, auto]  ⚠ downgrade
[3] OK    mean=0.860 std=0.010 agreement=True   verdicts=[auto-prop ×3]
[4] OK    mean=0.907 std=0.015 agreement=True   verdicts=[auto-prop ×3]
[5] FLAG  mean=0.770 std=0.056 agreement=False  verdicts=[auto, batch, auto]  ⚠ downgrade
[6] OK    mean=0.860 std=0.010 agreement=True   verdicts=[auto-prop ×3]
[7] FLAG  mean=0.797 std=0.015 agreement=False  verdicts=[auto, batch, auto]  ⚠ downgrade
[8] OK    mean=0.423 std=0.025 agreement=True   verdicts=[discard ×3]
[9] OK    mean=0.870 std=0.010 agreement=True   verdicts=[auto-prop ×3]

Smoke-test: 10 bullets, 3 FLAGGED (downgrade), 7 OK
```

**Verifikáció:**
- ✅ 3/3 várt downgrade detektálva — verdict-disagreement reason
- ✅ 0/7 false-positive — minden konzisztens response OK
- ✅ Discard-class (idx 8) helyesen OK marad (mind 3 sample `discard`, low std)
- ✅ std_conf metrika értelmes: 0.015–0.056 között, FLAG-threshold 0.15 nem aktivált → verdict-agreement a dominans-jel ezen sample-en

**Skeleton-state:** mock-driven, NEM élő G-Eval-call. Valós deploy `claude-code` scorerrel a `11.11crystallize` Layer 2.7 hook bekapcsolásakor.

## 6. Cost-comparison: NLI Layer 2.5 vs SelfCheckGPT 3-sample

| Eval-réteg | Mikor fut | Cost / bullet | Kalibrált trigger-arány | Effektív cost / 100 bullet |
|---|---|---|---|---|
| **Layer 2 G-Eval** | minden bullet | 1× (~530ms claude-code) | 100% | 100× |
| **Layer 2.5 NLI** | csak auto-prop kandidát | ~500ms (DeBERTa-v3) | ~30% (várt) | 30× × 0.5× = 15× ekvivalens |
| **Layer 2.6 coherence** | auto-prop AFTER NLI | ~3s (5 NLI-call) | ~25% (várt) | 25× × 3× = 75× ekvivalens |
| **Layer 2.7 SelfCheck (új)** | csak borderline 0.70–0.85 | **3× G-Eval = ~1.5s** | **10-20% (várt)** | **15–30×** |

**Net hatás:** SelfCheckGPT egy meglévő G-Eval réteget *replikál* 3× a borderline-bandben — high marginal cost, de szintén a leg-veszélyesebb régióban (épp a threshold körüli false-positive auto-prop bulletek a legkockázatosabbak). Cost-savings vs naiv "minden bullet-re N=3 G-Eval": **6×**.

## 7. Korlátok / open kérdések

- **Verdict-disagreement vs std_conf threshold súly.** Jelenlegi OR-logika: bármelyik trigger → downgrade. Week 2 kalibráció: lehet hogy `std_conf > 0.15` túl lazá vagy túl szigorú élő G-Eval-variance-ra. Mock-test 0.056 max std-t adott → valós sample-k várhatóan magasabb tartomány.
- **N=3 lehet kevés.** Manakul paper N=20-at használt. Cost-trade-off: ha valós kalibráción 3 sample false-negative-eket termel borderline-bulleten, N=5 fontolható (még +66% cost, de még mindig csak ~30× / 100 bullet).
- **Bias-mitigated G-Eval prompt-ot újrahasználjuk** → ugyanazok a bias-letörések jönnek mind 3 sample-be. Ez **csökkenti** a disagreement-jelet (kevesebb "véletlen" eltérés), de **növeli** a maradék disagreement-jelét: ha 3× bias-mitigated G-Eval mégis eltér, ez tényleges epistemic uncertainty, nem stylistic noise.
- **Layer 2.5 NLI komplementer-e?** SelfCheck *belső* konzisztenciát mér (LLM ↔ LLM), NLI *külső* támogatottságot (bullet ↔ provenance). Hipotézis: orthogonális signal, mindkettő érdemes futtatni. Week 2 mérés: korreláció a két downgrade-flag között.

## 8. Week 2 follow-up — `11.11crystallize` Layer 2.7 hook integration

### Tervezett patch (NEM applied ebben a sprintben)

`/usr/local/bin/11.11crystallize` ~line 850 (Layer 2.5 UTÁN, Layer 2.6 ELŐTT):

```python
# ── Layer 2.7 — SelfCheckGPT borderline-filter (B-1 Week 2 integration) ──
# Audit: 06-Audits/2026-05-17 SelfCheckGPT borderline-filter skeleton.md
SELFCHECK_ENV_VAR = "VAULT_SELFCHECK"
SELFCHECK_BIN = "/usr/local/bin/vault-selfcheck"
SELFCHECK_BORDERLINE_LOW = 0.70

def selfcheck_enabled() -> bool:
    return os.environ.get(SELFCHECK_ENV_VAR, "0") == "1"

# ... inside per-bullet loop, AFTER Layer 2.5 NLI, BEFORE Layer 2.6 coherence:
selfcheck_result: dict | None = None
selfcheck_downgrade = False
if selfcheck_enabled() and routing == "auto-prop" \
   and SELFCHECK_BORDERLINE_LOW <= confidence < eff_threshold:
    selfcheck_result = vault_selfcheck_subprocess(bullet, context)
    if selfcheck_result.get("status") == "OK" and selfcheck_result.get("downgrade"):
        routing = "batch-preview"
        selfcheck_downgrade = True
```

### Audit-log patch (~line 920)

```python
if selfcheck_result is not None:
    record["selfcheck_status"] = selfcheck_result.get("status")
    record["selfcheck_mean_conf"] = selfcheck_result.get("mean_conf")
    record["selfcheck_std_conf"] = selfcheck_result.get("std_conf")
    record["selfcheck_agreement"] = selfcheck_result.get("agreement")
    record["selfcheck_n_samples"] = selfcheck_result.get("n_samples")
    record["selfcheck_downgrade"] = selfcheck_downgrade
```

### Acceptance criteria Week 2

1. `VAULT_SELFCHECK=1 11.11crystallize <slug>` 3-5 borderline-bulletes session-en élesedik
2. Audit-log 6 új mezővel populálódik
3. `vault-crystallize-monitor --weeks 2 --json` jelenti `selfcheck_downgrade_rate`-et
4. Korreláció-mérés `selfcheck_downgrade` ↔ `nli_pass_vote=False`: várt 0.3-0.5 (komplementer signal-hipotézis)

### Long-term roadmap

- **Week 3:** N-tuning kalibráció (3 vs 5 vs 7) 50 real-session bulleten — F1-optimum
- **Week 4:** Combined-signal routing: ha *bármelyik* eval-réteg (NLI VAGY coherence VAGY selfcheck) flag-eli → downgrade; ha *mind 3* OK + G-Eval conf ≥ threshold → "high-confidence-3-vote" — eligible Aggressive ramp-re

## Kapcsolódó

- [[../11-wiki/Crystallization-protocol]] — overall protocol
- [[2026-05-17 B-1 G-Eval bias-mitigation v0.3]] — Layer 2 G-Eval prompt
- [[2026-05-17 B-1 NLI Layer 2.5 integration]] — Layer 2.5 (előző réteg)
- [[2026-05-17 Layer 2.6 vault-coherence integration|Layer 2.6 vault-coherence-check]] (utolsó "downgrade-only" réteg ezelőtt)
- [[../11-wiki/sv-07-continuous-evaluation]] — SV-7 axis (Continuous-Eval)
- [[../11-wiki/claude-code-subagent-fanout]] — 2-phase pending architecture
- Manakul, Liusie, Gales (2023): *SelfCheckGPT*, ACL — [arxiv:2303.08896](https://arxiv.org/abs/2303.08896)

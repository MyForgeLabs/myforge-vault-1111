---
name: B-1 NLI ensemble — second-opinion layer for Critic
type: decision
status: proposed
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/decision", "#project/sv", "sv-3", "b-3", "nli", "critic"]
related:
  - "[[../06-Audits/2026-05-20 B-8 Critic 100-bullet clean re-sample (kappa 0.708)]]"
  - "[[../11-wiki/sv-rsi-tier2-real-critic]]"
---

# B-1 NLI ensemble — second-opinion layer for Critic

> [!info] Status
> **Proposed** (NOT accepted). Target ratification: W22 end (~2026-05-29). Time-gated default-shift: W23 (2026-06-01..07) per B-3 Continuous Evaluation sprint plan.

## 1. Context

### 1.1 Current crystallization stack (post-2026-05-20)

The vault crystallization pipeline currently uses two LLM-based scoring layers:

| Layer | Method | Sprint | Status | Output |
|---|---|---|---|---|
| **L1 G-Eval** | LLM-as-judge, 4-dim rubric (relevance / coherence / consistency / fluency) | B-1 | ÉLES (since 2026-05-17) | `conf ∈ [0,1]` + verdict |
| **L4 Critic** | Subagent-fanout, 5-dim rubric (factuality / novelty / durability / vault_fit / safety) | B-8 | ÉLES (κ=0.708 ratified 2026-05-20) | `pass / fail` + per-dim scores |

The B-8 Critic just achieved **κ=0.708** on the 100-bullet clean re-sample (see [[../06-Audits/2026-05-20 B-8 Critic 100-bullet clean re-sample (kappa 0.708)]]), crossing the production-flip threshold (target ≥0.65). This baseline becomes the **agreement-floor** against which any second-opinion layer must add net value.

### 1.2 Why a second-opinion layer (NLI)?

The Critic-mode-finalize pipeline is **strong but not sufficient**:

1. **Critic measures rubric-fit, not entailment.** A bullet can score high on "factuality" by *plausibility* alone — the Critic does not check whether the bullet is *entailed* by the source-of-truth chunks already in the vault. False-novel claims slip through if they sound coherent.

2. **Single-judge correlated errors.** Both L1 G-Eval and L4 Critic share the same LLM backbone (Claude Sonnet via subagent-fanout). Their errors are **correlated by construction** — a hallucinated fact that fools L1 will frequently fool L4 too.

3. **Hungarian-vault drift.** Many bullets are HU-mixed. Critic-prompts are EN-leaning; entailment checks against HU source-chunks can degrade silently.

4. **No fact-check signal.** Neither layer answers the question: *"Is this bullet entailed, contradicted, or neutral relative to the existing vault content?"*

An **NLI (Natural Language Inference) classifier** addresses (1)-(4) directly: it consumes `(premise = retrieved vault chunks, hypothesis = bullet text)` and returns `{entailment, contradiction, neutral}` with a calibrated probability. This is **mechanically different** from Critic-rubric-scoring and provides genuine ensemble decorrelation.

### 1.3 Pipeline position

```
bullet → [L1 G-Eval conf] → [L4 Critic 5-dim] → [NEW: L5 NLI entailment] → routing
                                                  ↑
                                       premise = top-K vault chunks
                                       (B-2 semantic-search bridge)
```

NLI sits **after** Critic, consuming the same bullet plus the top-K (K=5) semantic-search chunks already retrieved by the B-2 bridge (`vault-search --top-k 5 --json`). Zero additional retrieval cost.

---

## 2. NLI options compared

| Option | Model | Hosting | Strength | Cost / bullet | Latency (CPU) | Model size | HU support |
|---|---|---|---|---|---|---|---|
| **A** | `sentence-transformers/all-mpnet-base-v2` + NLI head | Local | Weak-to-moderate | $0 | ~0.3s | 420 MB | Poor (EN-only training) |
| **B** | `cross-encoder/nli-deberta-v3-large` | Local | Strong (SoTA open MNLI) | $0 | ~2-4s | 1.4 GB | Moderate (multilingual via XNLI fine-tune available) |
| **C** | Claude Sonnet 4.6 + structured NLI prompt | API | Strongest (zero-shot + reasoning) | ~$0.003-0.008 | ~3-6s | n/a | Excellent (native multilingual) |
| **D** | OpenAI gpt-4o-mini + NLI prompt | API | Moderate-to-strong | ~$0.0005 | ~1-2s | n/a | Good |

### 2.1 Discussion

**Option A (mpnet-base + NLI head).** Smallest, fastest, but the NLI heads available for mpnet-base are typically fine-tuned on SNLI only (not MNLI/ANLI), which means the model handles short single-sentence premises well but degrades on multi-sentence vault chunks. Rejected as primary; usable as a **smoke-test sanity layer** only.

**Option B (cross-encoder/nli-deberta-v3-large).** This is the strongest open-source MNLI cross-encoder available without a GPU requirement. The cross-encoder formulation (joint `[premise || hypothesis]` encoding) is the right architecture for entailment — bi-encoders lose the interaction signal that NLI needs. Latency at 2-4s on the prod VPS (8 vCPU, no GPU) is acceptable given the bullets-per-session volume (~10-30). The 1.4 GB model size is a one-time disk cost. HU support is moderate — DeBERTa v3 has multilingual variants (`mDeBERTa-v3-base-mnli-xnli`) which we can drop in if HU accuracy is insufficient in Phase 0 testing. **This is the recommended primary.**

**Option C (Sonnet API).** Strongest fact-check signal because it can do multi-hop reasoning (e.g., "the bullet says X, the chunks say Y and Z, X follows from Y∧Z"). But: (a) introduces API-dependency and cost into a pipeline that has been deliberately $0-cost via subagent-fanout; (b) shares LLM-backbone with Critic → re-introduces correlated-error risk we are trying to eliminate. **Use only as escalation** for high-stakes low-confidence cases (Critic-pass + L1-conf < 0.5).

**Option D (gpt-4o-mini).** Cheapest API option, and the *different LLM backbone* property actually helps decorrelation. However, introduces a new third-party dependency for a P1 quality-gate which violates the user's stated preference for $0-cost infrastructure. Keeping as a **backup escalation** alternative to C if Anthropic cost becomes a concern.

---

## 3. Recommendation

**Primary: Option B** (`cross-encoder/nli-deberta-v3-large`, local CPU, $0).
**Escalation: Option C** (Claude Sonnet 4.6 via subagent) — invoked only when:
- Critic verdict = `pass` AND
- L1 G-Eval `conf < 0.5` AND
- B-NLI verdict = `contradiction` OR `neutral` with prob > 0.4

The escalation rate is expected to be ~5-10% of bullets (based on B-8 100-bullet sample where 7/100 had L1 conf<0.5 + Critic-pass). At ~$0.005/escalation × ~2 bullets/session that's ~$0.01/session — negligible.

**Multilingual fallback:** If Phase 0 HU smoke-test shows accuracy degradation > 15% vs EN, swap to `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`.

---

## 4. Ensemble logic

### 4.1 Verdict-combination matrix (initial / "hard" variant)

| Critic | NLI | Action |
|---|---|---|
| pass | entailment | **auto-prop** (high confidence; both signals agree) |
| pass | neutral | **auto-prop with flag** (most common case — bullet not contradicted; log `nli_neutral`) |
| pass | contradiction | **downgrade to batch-preview**, log `nli_contradiction` (Critic missed a fact-conflict) |
| fail | entailment | **discard** (Critic-conservative wins; rubric reasons matter even if entailed) |
| fail | neutral | **discard** |
| fail | contradiction | **discard with strong-flag** (both layers agree it's bad — log for trend tracking) |

**Critic-conservative wins on fail** is the safety bias: a Critic-fail signals rubric violation (e.g., novelty=0 because duplicate, or safety=0 because PII) that NLI cannot detect. We never *upgrade* on NLI alone.

### 4.2 Weighted-vote variant (Phase 3 fine-grained control)

For Phase 3, replace the hard matrix with a continuous score:

```
combined_score = w_g * gevel_conf + w_c * critic_pass + w_n * nli_entailment_prob
                                   - w_n_contra * nli_contradiction_prob

auto_prop if combined_score >= threshold_auto (default 0.7)
batch_preview if threshold_review <= combined_score < threshold_auto (default 0.4)
discard if combined_score < threshold_review
```

Default weights (to be calibrated): `w_g=0.2, w_c=0.5, w_n=0.25, w_n_contra=0.4` — note contradiction is weighted higher than entailment because contradictions are rarer and more informative.

### 4.3 Premise construction

NLI premise = concatenation of top-K=5 semantic-search chunks from `vault-search "<bullet-text>" --top-k 5 --json`. Truncate to model max-tokens (DeBERTa-v3 supports 512 tokens for the pair). If concatenated premise > 384 tokens, fall back to top-3.

If `vault-search` returns < 3 chunks (rare — only for highly novel topics): NLI runs against an empty premise and is forced to return `neutral` (no entailment claim can be made). Logged as `nli_no_premise`.

---

## 5. Implementation plan

### Phase 0 — Sprint W22 start (~2026-05-22..24): install + smoke-test

- Install `sentence-transformers` and pre-download `cross-encoder/nli-deberta-v3-large` to `/root/.cache/huggingface/`
- Implement `vault-nli-score` CLI: `vault-nli-score --bullet "<text>" --premise "<chunks>" [--json]`
- Smoke-test on the 26 unique bullets from the B-8 100-bullet sample (the 26 distinct bullets, 4× re-sampled)
- Measure pair-wise agreement matrix: `(critic_verdict, nli_verdict)` cross-tab
- **Goal:** confirm CPU latency < 5s/bullet, no installation issues, reasonable HU handling on the ~30% HU-mixed subset

### Phase 1 — Sprint W22 end (~2026-05-27..29): shadow-mode log-only

- Add `nli_verdict` field to `crystallize-log.jsonl` (`{label, prob, premise_chunks, latency_ms}`)
- Run NLI on every crystallize-eligible bullet but **DO NOT** alter routing
- Collect 1-week shadow data → measure base-rate of agreement/disagreement with Critic
- Env-flag: `VAULT_NLI_ACTIVE=1` (default 1 in shadow mode — write only, no consume)

### Phase 2 — Sprint W23 (2026-06-01..07): co-decision active (time-gated default-shift)

- Apply §4.1 hard-matrix routing
- Critic-pass + NLI-contradiction → downgrade to batch-preview (NOT auto-discard)
- Track new metric: `nli_downgrade_rate` (% of Critic-pass that NLI downgrades to review)
- Env-flag: `VAULT_NLI_ACTIVE=2` (consume — alters routing)

### Phase 3 — Sprint W24+ (2026-06-08+): weighted-vote with calibrated thresholds

- Collect 200-bullet labeled set (gold-standard from `vault-crystallize-monitor` user-feedback)
- Calibrate `w_g, w_c, w_n, w_n_contra` via grid-search to maximize F1 on the gold set
- Implement escalation path (Option C Sonnet) for ambiguous cases
- Env-flag: `VAULT_NLI_ACTIVE=3` (weighted-vote)

### Phase 4 — W25+: cross-lingual & batch optimization

- If HU-degradation > 15%: swap to `mDeBERTa-v3-base-mnli-xnli`
- Add batching to `vault-nli-score` for session-end bulk-scoring (8-16× throughput)

---

## 6. Acceptance criteria

The NLI ensemble layer is considered **net-positive** and ratified for production-flip when ALL of:

1. **Agreement floor:** NLI ↔ Critic agreement κ ≥ **0.6** on a 50-bullet validation set (lower than Critic's own 0.708 vs ground-truth — NLI is *complementary*, not redundant; we want SOME disagreement)
2. **Latency budget:** p95 latency < **5 seconds** per bullet on the prod VPS (8 vCPU, no GPU)
3. **Disk budget:** < **2 GB** model storage (DeBERTa-v3-large = 1.4 GB OK)
4. **Net rate-impact:** additional false-discards from NLI-flag ≤ **+10%** on shadow-mode (we accept slight over-conservatism as a safety margin)
5. **HU accuracy:** F1 on HU-subset of validation ≥ **0.7** (or trigger mDeBERTa swap)
6. **Auto-prop rate:** total auto-prop rate stays in **[0.4, 0.7]** band (don't strangle the pipeline)

If criterion #4 fails (false-discards > +20%): downgrade to log-only per §7.

---

## 7. Backout plan

| Condition | Action |
|---|---|
| Critical regression (auto-prop rate < 0.3 or > 0.85) | `VAULT_NLI_ACTIVE=0` → disable NLI entirely; revert to Critic-only |
| False-discard rate > +20% in shadow-mode | Stay at `VAULT_NLI_ACTIVE=1` (log-only) indefinitely; do not advance to Phase 2 |
| Latency p95 > 10s | Reduce premise to top-3 chunks; if still >10s, swap to Option A (mpnet) and document degradation |
| Model-download / install failure | Phase 0 abort; revisit options A or D |
| HU-accuracy < 0.5 F1 | Force `mDeBERTa-v3-base-mnli-xnli` swap immediately, skip Phase 2 timing |
| Critic κ drops below 0.65 in independent re-validation during Phase 1-2 | Halt NLI rollout — Critic itself needs fixing first; NLI cannot save a broken Critic |

All env-flags hot-reloadable via `~/.vault-config/nli-active.txt` (matches existing `crystallize-threshold.txt` pattern).

Audit-log: every NLI verdict written to `crystallize-log.jsonl` even after backout, for post-mortem.

---

## 8. Open questions

1. **Model size vs latency.** DeBERTa-v3-large is 1.4 GB / ~2-4s. DeBERTa-v3-base is 280 MB / ~0.8s but ~3-4 pp lower MNLI accuracy. **Undecided** — Phase 0 smoke-test will measure if -base is "good enough" for the agreement-floor. If yes, prefer -base for the 5× latency improvement.

2. **Batch vs streaming.** Should NLI run **per-bullet at crystallize-time** (streaming, ~3s blocking) or **once at session-end on the full Learnings list** (batched, 1× model-load amortized)? Streaming is simpler; batching is ~3-5× faster total. **Undecided** — likely batch for `11.11stop` flow, streaming for ad-hoc `crystallize` calls.

3. **Cross-lingual support (HU vault bullets).** ~30-40% of vault bullets are HU or HU-EN-mixed. DeBERTa-v3-large is EN-trained but generalizes via shared sub-word tokens. **Undecided** until Phase 0 measurement — if HU F1 < 0.7, swap to mDeBERTa-v3-base-mnli-xnli (multilingual but smaller, ~280 MB).

4. **Premise composition.** Top-K chunks from semantic-search may include the bullet itself (if already in vault as a near-duplicate). Should we **dedupe-by-cosine** before constructing premise? Risk: removing the most-relevant chunk if it happens to be a paraphrase. **Undecided** — Phase 0 will examine 5-10 examples manually.

5. **Contradiction-as-signal granularity.** Should an `nli_contradiction` with prob 0.55 be treated the same as prob 0.95? Phase 2 uses binary verdict; Phase 3 uses continuous prob. **Undecided** — depends on calibration data we don't have yet.

6. **Escalation budget cap.** Option C (Sonnet) escalation expected ~$0.01/session, but a pathological session could trigger 20-30 escalations. **Undecided** — add a hard cap `VAULT_NLI_ESCALATION_MAX=10` per session?

7. **Interaction with B-1 G-Eval bias-mitigation v0.3.** The G-Eval v0.3 symmetric stricter-confidence mode is opt-in. Should NLI's calibration be done against v0.3 or v0.2 G-Eval baseline? **Undecided** — pick whichever is the production default at W23.

8. **Sleep-Critic interaction.** Sleep-Critic (first-live-run 2026-05-19) runs *after* crystallize on a slower cadence. Should it consume NLI verdicts as input features, or run NLI itself on its own batch? **Out-of-scope for this ADR** — defer to B-9 Sleep-Critic v2 design.

---

## 9. Related work

- [[../06-Audits/2026-05-20 B-8 Critic 100-bullet clean re-sample (kappa 0.708)]] — baseline κ=0.708 the NLI ensemble must improve upon (or at minimum not regress)
- [[../11-wiki/sv-rsi-tier2-real-critic]] — RSI Tier-2 architecture, where Critic and NLI both live
- [[../11-wiki/g-eval-bias-mitigation-pattern]] — L1 G-Eval v0.3 bias-mitigation, calibration-dependency for Phase 3
- [[../11-wiki/sv-02-recursive-self-improvement]] — RSI sprint roadmap, NLI is sv-3/B-3 W23 deliverable
- [[../11-wiki/memgraph-ce-feature-limits]] — semantic-search bridge that provides premise chunks
- [[../11-wiki/subagent-fanout-context-aware-classification]] — Critic uses this pattern; NLI's escalation (Option C) will reuse it

---

## 10. Operational notes

### 10.1 CLI surface (Phase 0-1)

```bash
# Single-bullet scoring (streaming mode)
vault-nli-score --bullet "<text>" --premise-from-search [--top-k 5] [--json]

# Batch mode (session-end, all Learnings at once)
vault-nli-score --batch /tmp/learnings.jsonl [--out crystallize-log.jsonl]

# Health-check
vault-nli-score --health   # prints model-path, model-size, last-load-ms, GPU-y/n

# Force model variant
VAULT_NLI_MODEL=cross-encoder/nli-deberta-v3-base vault-nli-score ...
```

### 10.2 Logging schema (`crystallize-log.jsonl` additions)

```json
{
  "bullet_hash": "...",
  "nli": {
    "label": "entailment|contradiction|neutral",
    "probs": {"entailment": 0.72, "neutral": 0.21, "contradiction": 0.07},
    "premise_chunks": ["<chunk-id>", ...],
    "premise_tokens": 384,
    "model": "cross-encoder/nli-deberta-v3-large",
    "latency_ms": 2143,
    "phase": 1
  },
  "ensemble_decision": "auto_prop|batch_preview|discard",
  "ensemble_reason": "critic_pass+nli_entailment"
}
```

### 10.3 Failure modes the audit-log must distinguish

- `nli_no_premise` — semantic-search returned <3 chunks; default to `neutral`
- `nli_timeout` — model inference > 10s; default to `neutral` + flag for re-run
- `nli_oom` — model load OOM (low-RAM VPS); fallback to Option A (mpnet)
- `nli_lang_mismatch` — premise EN, bullet HU (or vice versa); warn, do not block

### 10.4 Metrics dashboard (`vault-crystallize-monitor` additions)

- `nli_disagreement_rate` per week (NLI≠Critic verdict)
- `nli_contradiction_rate` (how often NLI flags `contradiction`)
- `nli_downgrade_rate` (Critic-pass + NLI-contradiction → batch-preview)
- `nli_latency_p95_ms`
- `nli_escalation_count` (Option C Sonnet escalations triggered)

---

## 11. Decision log

| Date | Event | Outcome |
|---|---|---|
| 2026-05-20 | ADR drafted (status: proposed) | Awaiting Phase 0 smoke-test for ratification |
| W22 end | Phase 0 results review | Ratify primary model choice (B-large vs B-base vs mDeBERTa) |
| W23 start | Production-flip to co-decision (§4.1) | Conditional on criteria §6 |
| W24+ | Phase 3 weighted-vote rollout | Conditional on 200-bullet gold-set calibration |

---
name: Multi-dim rubric threshold — hybrid pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/wiki", "#concept/evaluation", "#concept/rubric", "#project/sv"]
---

# Multi-dim rubric threshold — hybrid pattern

When designing a pass/fail gate over a multi-dimensional rubric (e.g. 5-dim Critic: factuality / novelty / durability / vault_fit / safety), three threshold patterns appear. Only the third is calibration-stable on small pilot data.

## Pattern 1: Per-dim hard-floor (strict)

> "All N dimensions must be ≥ threshold T."

```python
def strict_pass(scores: dict[str, float], t: float = 0.85) -> bool:
    return all(v >= t for v in scores.values())
```

Behavior on a 10-bullet shadow-mode pilot (B-8 Critic, 2026-05-19):
- pass-rate: 4/10
- agreement with historical G-Eval: 60%
- **false-discard: 4/8 (50%)**
- false-accept: 0/2

The threshold is too strict — legitimate high-value content (novelty 0.80, factuality 0.95) gets rejected because one dim grazes the floor.

## Pattern 2: Aggregate mean (lenient)

> "Mean of all dimensions ≥ threshold T."

```python
def lenient_pass(scores: dict[str, float], t: float = 0.5) -> bool:
    return mean(scores.values()) >= t
```

Behavior on the same pilot:
- pass-rate: 9/10
- agreement: 90%
- false-discard: 0/8
- **false-accept: 1/2 (50%)**

The threshold is too lenient — a critical low-dim (vault_fit 0.30) gets averaged out by 4 high dims, and noise leaks into the vault.

## Pattern 3: Hybrid — aggregate mean + min-floor + critical-dim hard-gate

> "Mean ≥ T_mean AND min(all dims) ≥ T_min AND critical_dim ≥ T_critical."

```python
def hybrid_pass(scores: dict[str, float],
                t_mean: float = 0.7,
                t_min: float = 0.5,
                critical_dim: str = "safety",
                t_critical: float = 0.9) -> bool:
    if scores[critical_dim] < t_critical:
        return False  # hard-gate, overrides everything
    if min(scores.values()) < t_min:
        return False  # min-floor catches single-dim catastrophic-low
    return mean(scores.values()) >= t_mean
```

Behavior on the same pilot:
- pass-rate: 7/10
- **agreement: 90%**
- false-discard: 1/8 (12.5%, conservative direction)
- **false-accept: 0/2**

The hybrid combines the strengths: the **min-floor** catches catastrophic-low dims (vault_fit 0.30 fails), the **aggregate mean** is forgiving for single grazing dim (novelty 0.80 passes if mean is high), and the **critical-dim hard-gate** ensures safety/security/compliance can never be averaged-around.

## When critical-dim hard-gate is mandatory

The `safety` dim in the B-8 Critic rubric (potential vault-damage, leak risk, malicious-content) must be unconditional. Even if all 4 other dims score 1.0, a safety < 0.9 → automatic reject. The hard-gate makes this orthogonal to threshold-tuning.

Other use-cases where a hard-gate dim exists:
- Code-review: `correctness` is non-negotiable, even if `style` and `performance` are perfect
- Translation QA: `factual_accuracy` cannot be averaged with `fluency`
- Trading signals: `risk_compliance` blocks regardless of `expected_return`

## Threshold-tuning ratchet

1. Start with strict-mode in shadow (no auto-apply, just audit-log).
2. Measure false-discard rate over 50-100 calibration samples.
3. If false-discard > 30%, relax to hybrid-mode (still shadow).
4. Re-measure. If false-accept > 5%, tighten `t_mean` or `t_min`.
5. Cohen's kappa ≥ 0.7 vs human-judged sample → flip default-on for low-risk applications.
6. Cohen's kappa ≥ 0.85 → flip default-on for high-stakes apply paths.

## When it bit us (2026-05-19)

B-8 RSI Tier-2 Critic 10-bullet shadow-mode pilot showed all three patterns. The **hybrid default-mode** (mean 0.7 / min 0.5 / safety 0.9) was the only one with both 0 false-accept AND ≤1 false-discard. Production-recommended for the next 50-bullet scale-up.

## Related

- [[g-eval-bias-mitigation-pattern]] — sibling rubric-design pattern (different scope)
- [[sv-rsi-tier2-real-critic]] — the specific Critic where this hybrid pattern landed
- [[../06-Audits/2026-05-19 B-8 Critic 10-bullet shadow-mode pilot]] — empirical data

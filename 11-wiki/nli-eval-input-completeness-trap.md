---
name: nli-eval-input-completeness-trap
description: NLI/G-Eval/LLM-judge eval-jét MINDIG full-context-en futtasd, NEM truncated preview-stringen - a preview-truncation systematic shift-et ad az entailment-jelben, ami false-positive contradiction-cascade-be vihet
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/wiki", "llm-evaluation", "nli", "data-quality"]
---

# NLI eval input-completeness trap

## A probléma

Amikor egy LLM-judge (NLI, G-Eval, multi-judge) bemenete egy **truncated preview-string** (pl. első 120 karakter), és nem a full-text, akkor a verdict **szisztematikus shift-et** mutat a full-text-eredménytől:

- Az NLI a contradiction-jelek-et félreértelmezi mert nincs a context (pl. "X NEM működik" → preview-ban "X csak Y-on működik" — full-text-ben már OK)
- A G-Eval verbosity/halo-szignálok-ra téves rangsort ad
- A confidence-érték torzult mert a hypothesis és premise nem teljes-spektrumon összevethető

## Élő példa (2026-05-17-obsidian-vault session)

A B-3 L2 NLI-judge **kalibráció (Phase 2.4)** 20-sample-en **preview-stringen** futott:
- "2 auto-prop bullet `contradiction`-t kapott" (#5 STT echo-loop, #10 brand-paradigma)
- A "kulcs-insight" akkor az volt: "NLI szigorúbb mint G-Eval, soft-veto downgrade"

A B-1 NLI Layer 2.5 integráció **(Phase 4.R2.3)** ugyanazt a 2 bullet-et **full-bullet-text-en** futtatta:
- Mindkettő `entailment_prob 0.48 / 0.38` (NEM contradiction)
- Pass-vote: True mindkettőn

A "kulcs-insight" valójában **preview-bias** volt, nem tartalom-issue. Ha akkor preview-on léptünk volna real-apply-ra, a 2 bullet-et hibásan downgrade-eltük volna.

## A szabály

**MINDIG full-text-en futtass NLI/G-Eval/LLM-judge eval-t.** Ha latency vagy token-cost miatt preview kéne:

1. **Document a trade-off-ot** explicitly az audit-fájlban (preview-bias prevalencia mérve)
2. **Threshold-ot tighter-re** állítsd preview-on (pl. NLI contradiction>0.7 helyett >0.85)
3. **Második-pass full-text** csak a preview-flagged candidate-okra (smart-trigger pattern)

## Vágott szöveg konkrét hatásai

| Eval-modul | Preview-trap | Full-text |
|---|---|---|
| NLI-entailment | -0.30 entailment_prob (contradiction-shift) | baseline |
| G-Eval dim2 (verbosity) | -1.0 (rövidnek érzi) | baseline |
| G-Eval dim3 (reusability) | -0.5 (kontextus nélkül zsugorodik) | baseline |

(Mérések a 2026-05-17 session 2 contradiction-bullet-en.)

## Mikor érdemes alkalmazni

- ✅ Bármilyen LLM-judge audit-log nem-preview-mezőn futtatva
- ✅ Az audit-fájl tartalmazza a full-bullet hash-ét és full-text-ét, NEM csak preview-t
- ✅ A kalibrációs gold-set full-text-szel rögzítve (NEM preview)

## Kapcsolódó

- [[sv-07-continuous-evaluation]] — B-3 research
- [[g-eval-bias-mitigation-pattern]] — kapcsolódó eval-quality
- [[Crystallization-protocol]] — host protokoll

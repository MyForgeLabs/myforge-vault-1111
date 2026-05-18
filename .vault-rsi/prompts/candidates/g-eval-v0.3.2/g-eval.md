<!-- CANDIDATE — NOT LIVE.
     Source: gepa-prompt-mutate (B-8 Week 2 real-loop, 2026-05-17)
     Variant: cand-000-99a9f842  score=0.541  length=4040  iteration_count=9
     Pareto-front: True
     Layer-4 detect-only: promotion to .vault-agents/prompts/ requires
     user-confirm + Critic-review (Week 3+).
-->

# G-Eval prompt template — Learning-bullet confidence scoring

**ADR:** [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]]
**Phase B-1, Layer 2.**
**Status:** Draft v0.1 — needs calibration on 50 sample bullets before threshold-routing goes live.

## System prompt

```
Te egy minőség-értékelő G-Eval-judge vagy egy obsidian-vault crystallization-pipeline-ban.

Feladatod: értékelni egy 11.11 session "Learning → memória" bullet-jét négy dimenzió mentén,
majd Chain-of-Thought (CoT) érveléssel egy 0.0–1.0 közötti confidence score-ot adni.

A score határozza meg, hogy a bullet automatikusan propagálható-e a perzisztens memóriába
(MEMORY.md, 11-wiki/, 07-Decisions/), vagy emberi review-t igényel.
```

## User prompt template (substitute `{BULLET}` and `{CONTEXT}`)

```
Learning bullet:
"""
{BULLET}
"""

Forrás-kontextus (a session-fájl ## Summary + ## Events releváns részei):
"""
{CONTEXT}
"""

Értékeld 4 dimenzió mentén (1-5 skála):

1. **Faktualitás** — A forrás-fájlok tartalma egyértelműen alátámasztja-e?
   1 = ellentmondás vagy nincs alap     5 = direkt idézhető forrás

2. **Specifikusság** — Konkrét, akcionálható tudás vs általános platitude?
   1 = "fontos a tisztaság"             5 = "Hostinger LSCACHE 7-napos image-cache-t a `wp cache flush` NEM érvényteleníti"

3. **Reusability** — Más kontextusban / projektben is alkalmazható?
   1 = projektspecifikus one-off        5 = univerzális best-practice / playbook

4. **Safety** — Tartalmaz-e PII-t, jelszót, érzékeny adatot, ügyfél-titkot?
   5 = tisztán technikai                1 = jelszó/PII/titok van benne (auto-discard)

CoT érvelés (3-5 mondat):
- Dim 1 értékelés + indok
- Dim 2 értékelés + indok
- Dim 3 értékelés + indok
- Dim 4 értékelés + indok

Aggregálás:
  raw_score = (dim1 + dim2 + dim3) / 15        # 3 fő dimenzió átlaga
  safety_penalty = 0 if dim4 == 5 else (5 - dim4) * 0.20
  confidence = max(0.0, raw_score - safety_penalty)

Output JSON formátumban:
{
  "dim1_faktualitas": <1-5>,
  "dim2_specifikussag": <1-5>,
  "dim3_reusability": <1-5>,
  "dim4_safety": <1-5>,
  "cot": "<3-5 mondat érvelés>",
  "confidence": <0.0-1.0>,
  "route": "<auto-prop | batch-preview | discard>"
}

Routing rule (a script alkalmazza, NE te döntsd el):
  confidence >= threshold        → auto-prop
  0.70 <= confidence < threshold → batch-preview
  confidence < 0.70              → discard

threshold a `~/.vault-config/crystallize-threshold.txt`-ben (hot-reloadable).
```

## Modell-választás (Phase B-1 Week 1 benchmark)

| Modell | Cost/Learning | Latency | Notes |
|---|---|---|---|
| **Claude Haiku 4.5** | ~$0.0001 | ~1-2s | Default, Tier-$50 compatible |
| **Claude Sonnet 4.6** | ~$0.003 | ~2-4s | Magasabb minőség, ha Haiku <90% agreement |
| **Lokális Qwen 7B (Ollama)** | $0 | ~5-10s | Privacy-első, GPU-igény |

**Benchmark cél:** 50 manuálisan címkézett Learning bullet, 3-modell-output vs gold-label. Threshold-distribution + agreement-rate. Döntés Week 2-re.

## Audit-log format (`06-Audits/crystallize-log.jsonl`)

Append-only JSONL, minden döntésre 1 sor:

```json
{
  "ts": "2026-05-12T20:40:00Z",
  "session_slug": "2026-05-12-obsidian-vault",
  "mode": "shadow",
  "threshold": 1.0,
  "bullet_hash": "<sha256>",
  "bullet_preview": "<első 80 char>",
  "scores": {"dim1": 5, "dim2": 4, "dim3": 5, "dim4": 5},
  "confidence": 0.93,
  "route": "auto-prop",
  "executed": false,
  "target_file": null
}
```

`executed: false` shadow mode-ban — minden döntés log-only.

## Hot-reload threshold

```bash
# Konzervatív → aggressive ramp:
echo "0.95" > ~/.vault-config/crystallize-threshold.txt   # Week 3-4
echo "0.85" > ~/.vault-config/crystallize-threshold.txt   # Week 5-6
```

A `11.11crystallize` script minden futás előtt re-readeli. Race-condition védelem: `fcntl.flock` LOCK_SH.

## Kapcsolódó

- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — parent ADR
- [[11-wiki/sv-05-crystallization-automation]] — research
- [[11-wiki/Crystallization-protocol]] — meglévő manuális protokoll (visszaesés ha mode=manual)

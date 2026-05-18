---
name: B-3 vault-coherence-drift check (Day-0 audit)
type: audit
tags: ["#type/audit", "sv-research", "sv-7", "b-3", "evaluation"]
created: 2026-05-17
updated: 2026-05-17
status: skeleton
parent: [[../11-wiki/sv-07-continuous-evaluation]]
sprint: B-3 + B-1 cross-axis
---

# B-3 Vault-coherence drift check — Day-0 audit

> **Status:** skeleton ÉLES, integration into `11.11crystallize` Layer 2.6 PENDING (next session).

## Mit ad

`/usr/local/bin/vault-coherence-check` — egy új CLI, ami minden Learning bullet-et a **létező vault-tartalom (280+ skills + 28 ADRs + 76+ wikis)** ellen futtat NLI-judge-csal, hogy **session-stop előtt** kiderüljön: **mond-e ellent valamelyik kanonikus dokumentumnak.**

Distinct from [[../11-wiki/vault-ko-conflicts-audit-design|`vault-ko-conflicts-audit`]] (heti cron, KO-DB triplet-tár belső contradiction-jait keresi) — ez **vault-vs-Learning** check **a Learning crystallization ELŐTT**.

## Pipeline

```
bullet
  │
  ▼
Step 1: vault-search --mode cosine --json --top-k 5 → semantic neighbours
  │       (cosine top-K from Memgraph vault_chunk_vec index)
  ▼
Step 2: cosine-floor filter (>= 0.40) → topically relevant neighbours only
  │       (low-cos = irrelevant premise → NLI noise; calibrated below)
  ▼
Step 3: eval-l2-nli-judge per neighbour
  │       premise   = neighbour chunk snippet (≤160 char)
  │       hypothesis = bullet text
  │       output    = entailment / neutral / contradiction probs
  ▼
Step 4: aggregate → flag if any contradiction_prob >= threshold (default 0.7)
        coherence_score = 1 - max(contradiction_prob)
```

## Day-0 test — session: `2026-05-17-obsidian-vault.md`

**Setup:** 8 Learning bullets (Subagent-fanout 5. iter, wiki re-embed audit, auto-disable smoketest-noise, daemon-pattern, gh-api diff-check, Memgraph CE DDL, SKILL.md realpath-dedup, VSCode-extension popup) — mind ÚJ info aznapról, **0 valós contradiction várt**.

| # | Bullet (idézet) | coh-score | flagged | megjegyzés |
|---|---|---|---|---|
| L1 | Subagent-fanout 5. iteráció: 8 párhuzamos ... | 0.41 | OK | több jó-cos szomszéd, neutral overall |
| L2 | Wiki re-embed: 977 chunk = 8 wiki + 0 ADR ... | 0.17 | **FLAG** | FP — roadmap-snippet contradiction |
| L3 | Auto-disable smoketest-noise FP, min-vol guard | 0.32 | OK | |
| L4 | vault-search-server daemon 80× speedup | 0.83 | OK | |
| L5 | `gh api repos/.../HEAD --jq .sha` diff-check | 0.17 | **FLAG** | FP — agenda-snippet contradiction |
| L6 | Memgraph CE DDL no-transaction workaround | 0.66 | OK | |
| L7 | SKILL.md count 534 → 462 realpath-dedup | 0.79 | OK | |
| L8 | VSCode-extension popup csak `name` | 0.72 | OK | |

**6/8 = pass; 2/8 = flag.**

### A 2 flag analízise — FP (false-positive), NEM valódi drift

**L2 flag:** szomszéd = `07-Decisions/2026-04-23 Claude Code Agentic OS - build plan.md` snippet "Amit érdemes építeni…" → cos=0.62, contradiction=0.83. **Root cause:** a premise egy **roadmap-checklist** ("✓ Érdemes + kicsi") nem tényállító próza, NLI így logikailag korrektül nem-entailment-ként kezeli, de ez NEM valódi factual conflict.

**L5 flag:** szomszéd = `11-wiki/vault-net-ingest.md` "Tervezett iterációk 2026-05-17 v0.1 (most) — Skeleton" → cos=0.61, contradiction=0.83. **Same root cause:** agenda/iter-checklist premise + specifikus learning hypothesis = NLI természetes "nem-entailment" → magas contradiction-prob, de nincs factual ütközés.

### Tanulság (Day-0 finding)

> **NLI-judge gyenge a roadmap/agenda/checklist típusú premise-en** — ezeknek nincs prozaikus állító szerkezetük, ezért az MNLI-FEVER-ANLI-trained DeBERTa magas contradiction-prob-ot ad akkor is, ha tartalmilag nincs ütközés. **Recommended mitigation (Week 2):**
> 1. **Premise pre-filter** — szűrjük ki azokat a snippet-eket amik túl "list-like" (>50% bullet/sor, kevés finite-verb).
> 2. **Multi-snippet voting** — top-K=5 → top-K=10, és csak akkor flag ha **>=2 szomszéd** ad contradiction-t (egyetlen list-premise nem elég).
> 3. **Glossary-term overlap** — ha a bullet és a snippet nem oszt meg legalább 1 domain-terminust ([[../00-Meta/Glossary]]), akkor low-confidence flag.

A 2 flag a **soft-veto klasszisba** esik (= `batch-preview` route, NEM auto-prop) — ami **pontosan a kívánt viselkedés**: emberi review, nem hard-block. Ezért **a skeleton célja (0 hard-error) teljesült.**

## Performance

- Single bullet (5 neighbours, --mode cosine): ~20-30s (vault-search ~5s warm + 5× NLI ~3s/each ami a model-load per-subprocess miatt magas).
- Teljes session (8 bullet × 5 neighbours): ~3-4 min.
- **Optimization PENDING** (Week 2): batch NLI hívás (`eval-l2-nli-judge --input-file <jsonl>`) — egyetlen model-load, ~4× speedup várt.

## Integration plan — `11.11crystallize` Layer 2.6 (skeleton)

**Sorrend a crystallize-pipeline-ban:**

```
Layer 0: auto-disable short-circuit
Layer 1: parser (eval-l1-parser.py)
Layer 2: G-Eval (claude-code subagent scorer)
Layer 2.5: NLI-judge entailment (eval-l2-nli-judge)
Layer 2.6: vault-coherence-check     ← ÚJ
Layer 3: route-decision (auto-prop / batch-preview / discard)
```

**Hook-pattern:**

```python
# inside 11.11crystallize, after Layer 2.5 NLI-judge passes:
result = subprocess.run(
    ["/usr/local/bin/vault-coherence-check",
     "--bullet", bullet_text,
     "--threshold", "0.7",
     "--top-k", "5",
     "--json"],
    capture_output=True, text=True, timeout=120,
)
coh = json.loads(result.stdout)
if coh["flagged"]:
    # Soft-veto: force batch-preview route (human review),
    # NEVER auto-prop, even if G-Eval + NLI both passed.
    route = "batch-preview"
    veto_reasons.append({
        "layer": "2.6-coherence",
        "coherence_score": coh["coherence_score"],
        "conflicts": [c["file"] for c in coh["conflicts"]],
    })
```

**Threshold ramp (matches B-1 `~/.vault-config/crystallize-threshold.txt` pattern):**

| Phase | contradiction_threshold | Rationale |
|---|---|---|
| Shadow (default) | 0.95 | Log-only, ne flag-eljen, csak audit-rate-monitoring |
| Conservative | 0.80 | Auto-route to batch-preview, low FP |
| Aggressive | 0.70 | Current default — high recall, ~25% FP rate (Day-0) |

**Telemetry:** minden coherence-check eredmény logba kerül (`06-Audits/coherence-log.jsonl`), heti `vault-crystallize-monitor` parsolja → flag-rate, FP-rate proxy.

## Open items (Week 2)

1. **FP-mitigation 1-3 fenti** — premise list-filter + multi-snippet voting + glossary-overlap.
2. **Batch NLI**: `eval-l2-nli-judge --input-file` használat egyetlen subprocess-hívásban (4× speedup).
3. **Real hook into `11.11crystallize`** — ENV-flag-gates (`VAULT_COHERENCE_CHECK=1`), backward-compat default-off.
4. **Calibration sample** — futtassuk az utolsó 30 closed-session minden Learning-jén → flag-rate distribution, threshold-tuning data.
5. **Glossary-term overlap előszűrő** — `00-Meta/Glossary.md`-ből slug-set, bullet+snippet token-overlap >= 1 condition.

## Kapcsolódó

- [[../11-wiki/sv-07-continuous-evaluation]] — sprint research
- `/usr/local/bin/eval-l2-nli-judge` — NLI dependency
- `/usr/local/bin/vault-search` — semantic retrieval dependency
- [[../11-wiki/multi-layer-safety-gate]] — soft-veto pattern, ugyanaz a Critic-review filozófia
- [[../11-wiki/Crystallization-protocol]] — Layer 2.6 hook helye
- `vault-ko-conflicts-audit` — testvér audit (KO-DB-belső, NEM vault-vs-Learning)

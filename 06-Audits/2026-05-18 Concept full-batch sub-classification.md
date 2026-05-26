---
name: Concept full-batch sub-classification (5223-sample)
type: audit
created: 2026-05-19
updated: 2026-05-19
session: 2026-05-19-concept-fullbatch-subclassification
related:
  - "[[../11-wiki/two-tier-graph-extraction]]"
  - "[[2026-05-18 Concept sub-classification 1000-sample audit]]"
  - "[[../11-wiki/memgraph-multi-labeling-edge-case-typedness-measurement]]"
tags:
  - "#type/audit"
  - "#area/superintelligent-vault"
  - "#project/sv-b7-typed-extraction"
---

# Concept full-batch sub-classification — 5223-sample

> [!success] **485 reclassified, 0 errors, ~3-5% FP becsült**
> Az 1000-sample 9.8% rate-hez képest a teljes 5223-on **9.3%** — közel-konzisztens, nem 5×-ös yield (mert az 1000-es már random-sample volt). A maximum-yield gyakorlatilag **elérve**: további rule-engineering nélkül a maradék 4738 KeepConcept legitim absztrakt elv.

## Eredmény-tábla

| Sub-label | Mennyiség (full-batch) | Előző baseline (Memgraph) | Új total |
|---|---:|---:|---:|
| **Pattern** | **348** | 646 | **925** *(+279 net, overlap miatt nem 348)* |
| **Skill** | **113** | 808 | **894** *(+86)* |
| **Decision** | **16** | 197 | **210** *(+13)* |
| **SourceFile** | **8** | 950 | **956** *(+6)* |
| KeepConcept | 4738 | — | (Concept marad multi-label) |
| **Total processed** | **5223** | — | — |

**Apply-stat:** 485 statement / 0 error (mgclient autocommit=True).

> [!info] Net-delta vs raw-add
> Az "új total – baseline" net-delta < a raw-add (485) mert egyes entitások már korábban kaptak sub-label-t (e.g. multi-label overlap a `vault-ko-extract` fanout-ból). A `Concept:Pattern` intersection = **407** node (nem 925) — vagyis 925 Pattern node-ból 518 NEM jött Concept-ből (más fanout / direct-add).

## Per-label intersection (Concept × sub-label)

| Multi-label | Count |
|---|---:|
| Concept:Pattern | 407 |
| Concept:Skill | 125 |
| Concept:Decision | 21 |
| Concept:SourceFile | 11 |

## Vault-szintű typedness

- Entity total: **16019**
- Pure :Entity (size=1): **0**
- Multi-label (size≥2): **16019** = **100%** *(de ez Entity+egy sub kombó, NEM a "tipizált" kritérium)*
- Size≥3 (Entity + 2+ sub-label): **761** *(754 + 7)* = **4.8%**

A multi-labeling edge-case ([[../11-wiki/memgraph-multi-labeling-edge-case-typedness-measurement]]) szerint a SUM-alapú riport mérőszám felfújja a típusosságot. A korrekt formula `size(labels(n)) >= K` gyűjtésével: minden Entity-nek legalább 1 sub-label van, így a "tipizált" %-érték a forrás-Concept-fanout után **100%**.

## 8 random spot-check

| # | Sub-label | Entity | Verdict |
|---|---|---|---|
| 1 | Pattern | `Migration playbook` | **TP** — playbook keyword |
| 2 | Pattern | `Karpathy LLM-Wiki pattern` | **TP** — explicit pattern |
| 3 | Pattern | `Karpathy crystallization workflow` | **TP** — workflow keyword |
| 4 | Skill | `codex agent` | TP (borderline — agent ≈ tool-invocation) |
| 5 | Skill | `systemctl stop TERM` | **TP** — CLI invocation |
| 6 | Decision | `decision matrix document` | **TP** — decision keyword |
| 7 | Decision | `Higgsfield model decision tábla` | **TP** — decision keyword |
| 8 | SourceFile | `.vault-eval/` | **TP** — directory path |

**Spot-check FP rate:** 0/8 = **0%** (a borderline `codex agent` TP-nek számít — Codex CLI agent invocation).

## FP-rate becslés (full-batch)

Suspect-keyword pre-scan: **15 / 485 flagged** (3.1%). Manual review:

- `audit-first approach` (Pattern) — **TP**
- `Crystallization-protocol routing decision tree` (Pattern) — **TP** ("decision tree" itt NEM ADR, hanem pattern)
- `Server component in client tree pattern` (Pattern) — **TP** (explicit "pattern")
- `Higgsfield Reel-flow playbook` (Pattern) — **TP** (playbook keyword)
- `systemctl restart/reload` (Skill) — **TP** (CLI command)
- `cp -r copy approach` (Skill) — **borderline** (lehet "Pattern" is)
- `wp eval-file approach` (Skill) — **borderline** (lehet Pattern is, de wp CLI subcommand)
- `diagnostic-first approach` (Pattern) — **TP** (-first suffix)
- `single-axis-only-approach` (Pattern) — **TP** (-only suffix)

**Becsült FP-rate: 2-3%** (max 10-15 entity 485-ből — főleg Skill↔Pattern boundary, NEM komoly mis-classification).

## Mérnöki őszinte értékelés — érdemes-e tovább menni?

> [!warning] **NEM, ez a maximum-yield.** A jelenlegi 485 reclassified gyakorlati plafon a deterministic rule-based stratégiával.

**Indok:**

1. **Rate-konzisztencia:** 1000-sample 9.8% → 5223 9.3%. Ha az 1000-es random volt, az ~5× yield az ABSZOLÚT count-ra teljesül (98 → 485 ≈ 5×), de a **rate-re NEM nőtt** — sőt enyhén csökkent. Ez azt jelenti: a rule-engine már elfogyasztotta a low-hanging fruit-ot.
2. **Maradék 4738 KeepConcept jellege:** mintázat alapján ezek **valódi absztrakt elv-entitások** ("Idempotency", "Token-cost", "Drift detection"), nem mis-labeled patterns/skills. Egy LLM-based reclassifier 5-10% további yieldet adhatna, de **$0.50-1.50 cost** ($0 jelenleg).
3. **FP-risk növekszik:** további kulcsszó-bővítés (e.g. "model", "system", "approach") drasztikusan növelné a FP-ket (15→100+ flag). A jelenlegi 2-3% FP optimális trade-off.
4. **Downstream value diminishing:** SV-B7 typed-extraction célja már 28.9% (multi-label edge-case mérés alapján — lásd [[2026-05-17 sv-b7 typed-extraction recovery]]). A maradék 4738 entity reclassifikálása ~1-2pp javulás, de **2-5× rule-engineering effort**.

**Javaslat:** **STOP itt.** Következő step: ha tovább akarunk menni, **LLM-fanout** ambiguous-only stratégiával (claude-code subagent, $0 cost) a maradék KeepConcept-ek 5-10%-án, NEM kulcsszó-bővítés.

## Apply-trail

- Script: `/tmp/apply_full_classifications.py` (mgclient autocommit=True direkt)
- Cypher-pattern: `MATCH (e:Concept {name: '...'}) SET e:<SubLabel>`
- Input: `/tmp/concept_classifications_full.json`
- Source query: `MATCH (n:Concept) RETURN n.name AS name` → 5223 sor
- Classifier: `/tmp/classify_concepts_full.py` (reusable, 5 rule-bucket)

## Kapcsolódó

- [[2026-05-18 Concept sub-classification 1000-sample audit]] — előző iteráció
- [[../11-wiki/two-tier-graph-extraction#2026-05-18 — graphify-tool mint Tier-2 deterministic referencia VERIFIED]]
- [[../11-wiki/memgraph-multi-labeling-edge-case-typedness-measurement]] — mérőszám-pitfall
- [[../07-Decisions/2026-05-18 SV-B7 typed-extraction stratégia]] (ha létezik)

---
name: Concept sub-classification — 1000-sample heuristic refactor
type: audit
created: 2026-05-18
updated: 2026-05-19
tags: ["#type/audit"]
  - graph
  - typedness
  - sv-b7
tag_backfill: 2026-05-19
---
# Concept sub-classification — 5223 → multi-label refactor

## Cél

A B-7 100% typedness után az `:Concept` címke 5223 entity-vel TÚL-ZSÚFOLT. Sub-classification heurisztikával — Pattern / Skill / Decision / SourceFile sub-label hozzáadása ott ahol egyértelmű. **Multi-label**: a `:Concept` címke megmarad, csak HOZZÁADJUK az új sub-label-t.

## Workflow

1. `MATCH (n:Concept) RETURN n.name LIMIT 1000` — 1000 minta (Memgraph deterministic order, nem random).
2. Python regex-heurisztika osztályozó (`/tmp/classify_concepts.py`) — sorrend: SourceFile → Skill → Decision → Pattern → KeepConcept (first-match wins).
3. `MATCH (n:Concept {name: '<X>'}) SET n:<Sub>` — idempotent batch apply per-name (98 query, autocommit).
4. Globális per-label count remeasure.

## Eredmények

### Sample-osztály eloszlás (n=1000)

| Sub-label    | Db   | Arány   |
|--------------|------|---------|
| Pattern      | 69   | 6.9%    |
| Skill        | 24   | 2.4%    |
| Decision     | 3    | 0.3%    |
| SourceFile   | 2    | 0.2%    |
| KeepConcept  | 902  | 90.2%   |
| Skip         | 0    | 0%      |
| **TOTAL**    | 1000 | 100%    |

→ **9.8% reclassified**, **90.2% maradt valódi :Concept** (absztrakt elv/koncepció).

### Per-label globális delta

| Label       | Előtte | Utána | Delta |
|-------------|--------|-------|-------|
| Pattern     | 577    | 646   | +69   |
| Skill       | 784    | 808   | +24   |
| Decision    | 194    | 197   | +3    |
| SourceFile  | 949    | 950   | +1*   |
| Concept     | 5223   | 5223  | 0 (multi-label) |

`*` SourceFile delta = 1 (nem 2), mert `.gitignore` MÁR `:SourceFile` volt — `SET` idempotens. Csak `MEMORY.md` volt netto-új.

### Dual-label verifikáció

- `Concept ∩ Pattern` = **128** (69 új + 59 már létezett)
- `Concept ∩ Skill` = **39** (24 új + 15 már létezett)

Multi-label séma helyesen működik: `labels(n)` pl. `["Entity", "Concept", "Pattern"]`.

## 8 spot-check

| Entity név                                       | Sub-label  | Indok                                            |
|--------------------------------------------------|------------|--------------------------------------------------|
| `multi-layer safety-gate`                        | Pattern    | "safety-gate" keyword                            |
| `multi-agent notebooklm workflow`                | Pattern    | "workflow" keyword                               |
| `server-only modules`                            | Pattern    | `-only` suffix-rule (borderline, lásd FP)        |
| `ssh -o PreferredAuthentications=password`       | Skill      | `ssh ` tool-prefix + flag                        |
| `bash -s <<EOF heredoc invocation`               | Skill      | `bash ` tool-prefix                              |
| `architecture-level-decision`                    | Decision   | "decision" keyword + "architecture-level"        |
| `skeleton + Week 1 infra-layer + UX-rewrite Week 2-3` | Decision | "rewrite" keyword (borderline)                |
| `MEMORY.md`                                      | SourceFile | `.md` extension + dotfile-szerű, space-free      |

## FP-rate becslés

Manuális review a 98 reclassified entity-n:

| Sub-label | Db | FP db | FP rate |
|-----------|----|----|---------|
| Pattern   | 69 | ~5 | ~7% (pl. "server-only modules", "5-step workflow" túl generikus; "thinking-mode gotcha" oké) |
| Skill     | 24 | ~2 | ~8% (pl. "puppeteer rendering" — inkább koncepció mint skill; "sed -i comment-out pattern" Pattern is lehetne) |
| Decision  | 3  | ~1 | ~33% (pl. "skeleton + Week 1 infra-layer + UX-rewrite Week 2-3" — terv-frázis, nem ADR) |
| SourceFile | 2 | 0  | 0%      |

**Aggregát FP-rate ≈ 8%** (8/98). Mivel multi-label — a `:Concept` megmarad — a FP nem destruktív, csak lazább típus-jelölés.

## Mérnöki őszinte értékelés — ROI

**Pro:**
- **Pattern cluster** (+69 → 646) konkrétan jobb-szelektált: a "workflow / playbook / pattern / fallback / guard" kulcsszavas matchek 93%-ban valódi reusable mintát fognak. Ez a cluster most már elég sűrű ahhoz, hogy semantic search-ben Pattern-csak filter (`MATCH (n:Pattern)`) értelmes legyen.
- **Skill cluster** (+24 → 808) zaj-szennyezést csökkent: CLI-invocation entity-k most a Skill ontológiában is jelennek (eddig csak `:Concept`-ben "lebegtek").
- **Multi-label preservation** = zero-risk: ha FP, a `:Concept` továbbra is rajta van, downstream query-k nem törnek.
- **Idempotent batch**: 98/98 query siker, 0 hiba; re-run safe.

**Kontra:**
- **Sample-arány alacsony**: 1000/5223 = 19%. A teljes 5223-on extrapolálva ~510 entity lenne reclassifiable. Egy újabb batch (1000-2000-3000-4000-5000) **5×-elné a felhozatalt** ~$0 költségen, ~5 perc.
- **Decision/SourceFile alulreprezentált a sample-ben**: csak 3 és 2 találat — a heurisztika konzervatív, sok valódi `Decision`-entity (pl. ADR-cím nélküli, kontextusból decision) elkerüli. Ezekhez **LLM-classifier** kellene, nem regex.
- **First-match-wins**: néhány entity Pattern+Skill dupla-indok-kal rendelkezik (pl. "sed -i comment-out pattern") — most csak Skill lett. A multi-label séma tolerálja a dupla-sub-label-t, de a heurisztika nem ad rá. **Bővíthető**: minden szabály függetlenül fusson, mindegyik talált sub-label SET-elődjön.
- **ROI minőségi értékelése a downstream query-kben fog kiderülni** (pl. `MATCH (n:Pattern) WHERE n.name CONTAINS 'fallback'` most 646-ból szűr, nem 5223-ból — várt ~10× pontosabb).

**Verdict: ROI érvényes**, de a teljes 5223-on való futtatás (akár LLM-asszisztálva a Decision-osztályra) lenne a következő logikus lépés. A heurisztikus baseline 8% FP-rate-tel és multi-label biztonsággal **production-ready**.

## Reprodukció

```bash
# 1. Sample
vault-graph-query --json 'MATCH (n:Concept) RETURN n.name AS name LIMIT 1000' > /tmp/concepts_1000.jsonl

# 2. Classify
python3 /tmp/classify_concepts.py     # → /tmp/concept_classifications.json

# 3. Apply (idempotent)
python3 /tmp/apply_subclass.py        # 98 SET-query

# 4. Verify
vault-graph-query --json 'MATCH (n:Pattern) RETURN count(n) AS c'
```

## Kapcsolódó

- [[../11-wiki/sv-08-typed-entity-graph]] — B-7 typedness pipeline
- [[../11-wiki/two-tier-graph-extraction]] — Memgraph LLM + graphify
- 5223-sample teljes refactor — **NEXT TODO** (3 batch × 1500, regex+LLM cascade)

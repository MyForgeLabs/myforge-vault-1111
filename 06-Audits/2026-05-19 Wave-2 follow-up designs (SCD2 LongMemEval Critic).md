---
name: 2026-05-19 Wave-2 follow-up designs (SCD2 LongMemEval Critic)
type: audit
status: design-only
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#project/sv", "#concept/scd2", "#concept/longmemeval", "#concept/rsi-critic"]
related:
  - "[[2026-05-19 mega-session summary]]"
  - "[[../11-wiki/temporal-kg-scd2-pattern]]"
  - "[[2026-05-19 LongMemEval-S vault-variant v0.2]]"
  - "[[2026-05-19 bmad-vault-bridge skeleton]]"
---

# Wave-2 follow-up designs — SCD2 / LongMemEval-v0.3 / Critic-Tier2

3 follow-up feature **design-only**. NEM impl. A mai (2026-05-19) mega-session 3 nyitva maradt szálát zárja le terv-szinten, hogy a következő session impl-tableként induljon.

Forrás-finding emlékeztetők:

- SCD2 migration ÉLES (13,801 row, 93 ms, 3 új index). `scd2.insert_with_version()` mint **opt-in helper** kész, DE a két fő ingest write-path (`vault-ko-ingest.upsert_fact`, `11.11crystallize` insert) MÉG NEM hívja.
- LongMemEval-S v0.2 hibrid (BM25+RRF) **Recall@5 = 67.68%** locked baseline. fetch-K = 5 fix, fused-pool nincs (separate top-K + RRF merge).
- B-8 RSI Tier-2 safety-gate Layer 4 Critic = jelenleg stub. Template ([`critic-review-template.md`](../.vault-ko/prompts/critic-review-template.md)) megvan; runtime-execution nincs.

---

## Design A — SCD2 fact-versioning patch a két write-path-en

### Cél

A két ingest-path (`vault-ko-ingest.upsert_fact` + `11.11crystallize`) hívjon `scd2.insert_with_version()`-t a mostani `INSERT OR IGNORE / UPDATE updated_at` helyett, hogy a `valid_from` / `valid_until` mezők ne csak backfill-stat hanem **élő supersession-history**-t adjanak.

### Conflict-definíció (3 osztály)

A konfliktus-osztályozás háromszintű döntés-tábla. Forrás: brainstorm idea #9 + #34 (KO-DB hash refactor) cross-link.

| Eset | Detekció | Action |
|---|---|---|
| **A. Identical** — same (s, p, o), live row létezik | `WHERE hash=? AND valid_until IS NULL` | **No-op**, return existing fact. Ez ma `scd2.insert_with_version` `existing` ágban van |
| **B. Update** — same (s, p), **different** o, live row létezik | `WHERE subject=? AND predicate=? AND valid_until IS NULL` → object eltér | **Close-and-replace**: UPDATE old.valid_until=NOW, INSERT new row valid_from=NOW |
| **C. New** — nincs live row (s, p)-re | predikátum-egyezés nem talál | **INSERT** (új fact, history-szerűen valid_from=NOW, valid_until=NULL) |

A B-eset **csak akkor zárja a régi sort, ha az `o` ténylegesen eltér** — kulcs-szabály: a `(s, p)` "logikai kulcs" (current value), a `(s, p, o)` "fizikai kulcs" (verzionált row). Multi-version egy `(s, p)`-re csak az időtengely mentén lehet.

### Multi-source same-(s, p, o) konvergencia (#34 KO-DB hash refactor cross-link)

Két source ugyanazt mondja → mit csinálunk?

- **Mai (hash-by-content)**: egy row, second-ingest-en `INSERT OR IGNORE` (no-op), provenance csak az első source. **Konfirmáció elveszik.**
- **#34 refactor terve (provenance multi-row attribute)**: vagy aggregált provenance-string, vagy külön `fact_provenance` join-tábla (1:N).

**Ajánlás:** Design A illeszkedjen a #34 győzteséhez két switch-szel:
1. **Eset (s, p, o) match + live row exists** → no-op a fact-row-n, DE `INSERT INTO fact_provenance` (új provenance-row). Ez a `cross-source-corroboration` ranking-alapja (mai `vault-ko-query --top-k` mező).
2. **Eset (s, p) match + o differs + 2 live source** → ez **kétértelmű**: két source ütközik. Itt **NE zárd** automatikusan a régit; loggol `vault-ko-conflicts-audit`-ba és batch-preview-be.

→ **Coordination gate**: a #34 subagent eredménye kell ELŐSZÖR (provenance-schema-döntés). Addig Design A `--dry-run` mód-ban implementálható (logol mit csinálna, nem mutál).

### Patch-target snippet (5-sor pseudocode, NEM kód)

`vault-ko-ingest.py:upsert_fact`:

```python
# helyett: INSERT OR IGNORE + UPDATE updated_at
from scd2 import insert_with_version
fact = insert_with_version(
    f["subject"], f["predicate"], f["object"],
    provenance=f["provenance"],
    confidence=f.get("confidence"),
    source_type=f.get("source_type", "manual"),
)
return ("new" if fact.valid_from == fact.created_at else "noop")
```

`11.11crystallize` callback ugyanaz — a Layer-2 fact-write-helper hívja az `scd2.insert_with_version`-t.

### Migration-prerequisite (BLOCKER)

A wiki említi: `UNIQUE(hash)` constraint ütközik SCD2-multi-version-storage-szel. Ma a 13,801 row mind `valid_until IS NULL` (post-backfill), tehát nincs konfliktus, de az **első élő supersession crash-elne**. Sorrendben:

1. **Drop UNIQUE(hash) constraint** — SQLite table-rebuild (CREATE NEW → INSERT SELECT → DROP OLD → RENAME). ETA ~150 ms 13.8K row-n a 93 ms migration alapján.
2. **Új partial unique index**: `CREATE UNIQUE INDEX idx_facts_live_unique ON facts(hash) WHERE valid_until IS NULL` — biztosítja hogy két live row nem ütközik, de history-version-ek szabadon élnek.
3. Két write-path patch.
4. Tests: `test_scd2_supersession_end_to_end`, `test_scd2_multi_source_provenance` (csak ha #34 ratify).

### ETA estimate

| Fázis | Mit | ETA |
|---|---|---|
| 1. #34 coord-wait | provenance schema-döntés bevárása | external |
| 2. UNIQUE(hash) drop migration + partial-index | SQL script + 2 test | 30 min |
| 3. `vault-ko-ingest` patch | upsert_fact → insert_with_version | 20 min |
| 4. `11.11crystallize` callback patch | grep + replace + 1 test | 25 min |
| 5. Multi-source/conflict-corroboration | csak ha #34 ratify-elte a 1:N provenance-t | +45 min |
| 6. Regression: `vault-ko-query --conflicts` még működik | smoke-test | 10 min |
| **TOTAL (without 5)** | | **~85 min** |
| **TOTAL (with 5)** | | **~130 min** |

---

## Design B — LongMemEval-S v0.3 (fused-pool + fetch-K sweep)

### Cél

Mai v0.2: külön `vector-top-5` + `bm25-top-5` → RRF merge → top-5. v0.3 két dimensions:

1. **Fused-pool**: vector top-K ∪ BM25 top-K → **közös pool-on** rerank (cross-encoder BGE-reranker vagy LLM-judge). Nem RRF, hanem score-fusion.
2. **Fetch-K sweep**: K ∈ {5, 10, 15, 20, 30, 50} — Recall@5, P@5, MRR görbék. Hol a marginal-gain plateau?

### Fused-pool dizájn

| Variant | Pool-építés | Rerank | Final-top-5 |
|---|---|---|---|
| **v0.2 (baseline)** | vector-top-5, BM25-top-5 (külön) | RRF score = 1/(k+rank_v) + 1/(k+rank_b) | sort by RRF, top 5 |
| **v0.3-A (fused-pool + RRF)** | vector-top-K ∪ BM25-top-K, K=20 | RRF (same as v0.2) | top 5 |
| **v0.3-B (fused-pool + reranker)** | ugyanaz | BGE-reranker score (cross-encoder cosine) | top 5 |
| **v0.3-C (fused-pool + LLM-judge)** | ugyanaz | Claude subagent 1-5 score | top 5 |

**Hipotézis:** v0.3-B (cross-encoder) +3-5 pp Recall@5-öt hoz a v0.2-höz képest. A mai keepalive-pattern (BGE-reranker -55% wall-clock load-cost, mai mega-session finding) miatt **inference-cost változatlan**, csak load-cost amortizálódik.

### Fetch-K sweep prediction (skeleton)

Cosine-only baseline (v0.2): 31.31% Recall@5 K=5-nél. Hybrid: 67.68%. Becslés a 99-Q-on:

| K | v0.2 Hybrid Recall@5 (pred) | Mit várok |
|---|---|---|
| 5 | 67.68% (locked) | baseline |
| 10 | ~71-73% | +3-5 pp (több jó kandidát a pool-ban) |
| 15 | ~73-75% | marginal-gain csökken |
| 20 | ~75% | plateau-küszöb |
| 30 | ~75-76% | csak noise növekedik |
| 50 | ~74-75% | noise overwhelms (regress) |

A "K=20 + reranker" sweet spot a publikált RAG-irodalom (BEIR, MTEB) szerint. v0.3 megerősíti vagy cáfolja.

### Új metrikák (Recall@5 mellett)

| Metrika | Mit mér | Miért |
|---|---|---|
| **Recall@5** | minimum 1 hit a top-5-ben | Mai canonical (locked) |
| **P@5** (Precision@5) | hits/5 a top-5-ben | Multi-answer query-knél árnyalt: "hány valódi forrás van a top-5-ben" |
| **MRR** (Mean Reciprocal Rank) | 1/rank az első hitnek | Reranker-quality jelző (push-to-top) |
| **nDCG@5** | grade-aware ranking quality | Túl drága labeling-igény miatt **opt-out** v0.3-ban |

P@5 és MRR `_kiegészítő`, NEM gate. Csak Recall@5 marad regression-gate-en.

### Patch-target

| Fájl | Mit |
|---|---|
| `.vault-eval/scripts/longmemeval-v03-driver.py` | új, v0.2-driver clone + fused-pool + K-param |
| `.vault-eval/regression/baseline.json` | új blokk `v03_fused_K20_reranker` (csak ha élesen jobb) |
| `.vault-eval/regression/test_longmemeval_regression.py` | új `test_v03_fused_pool_recall_above_v02`, `test_v03_fetch_k_sweep_curve_shape` |
| `06-Audits/2026-05-19 LongMemEval-S vault-variant v0.3.md` | sweep-table + reranker comparison + decision |

### ETA estimate

| Fázis | Mit | ETA |
|---|---|---|
| 1. v0.3-driver clone + fused-pool extension | K-param, union-pool | 35 min |
| 2. BGE-reranker integráció | mai keepalive-script reuse | 25 min |
| 3. Fetch-K sweep run (6 K-érték, 99-Q) | ~3-4 min/K = ~25 min | 25 min |
| 4. P@5 + MRR számítás | metric-helper | 15 min |
| 5. baseline.json update + 2 új test | TDD-style | 20 min |
| 6. Audit MD generation | sweep-table + decision | 15 min |
| **TOTAL** | | **~135 min** |

---

## Design C — B-8 RSI Tier-2 real-LLM Critic

### Cél

A 4-rétegű safety-gate Layer 4 (`Critic-review`) most stub-template. Real-LLM implementáció = 5-dim rubric scoring + 2-phase pending-pattern (mint `crystallize-pending` skill).

### 5-dim rubric — skála + threshold

**0-1 float** (nem 1-5 int) — finomabb gradient, kompatibilis a mai G-Eval `confidence` 0-1 skálájával, könnyebben átlagolható.

| Dim | Mit mér | Anchor 0.0 | Anchor 1.0 |
|---|---|---|---|
| **factuality** | A bullet állítása ellenőrizhető és helyes? | hamis vagy ellenőrizhetetlen | konkrét, ellenőrizhető tény / KO-DB-egyezés |
| **novelty** | Új info, NEM ismétlés? | exact-duplikát mai vault-content-en | új nézőpont vagy új mérési eredmény |
| **durability** | 6+ hónap múlva is releváns? | session-specific debug-zaj | architektúra-szintű playbook |
| **vault_fit** | Illik a target-fájl ethos-ához? | wiki-be ADR-szerű, vagy fordítva | hely + típus egyezik |
| **safety** | PII / kred / forbidden-target leak? | bármi sensitive | tiszta, public-safe |

**Threshold-policy** (három option, default a középső):

| Mód | Logika | Mikor |
|---|---|---|
| **Strict** | minden 5 dim ≥ 0.8 ÉS mean ≥ 0.85 | Aggressive ramp (B-1 Aggressive-threshold-fázis) |
| **Default** | mean ≥ 0.75 ÉS min ≥ 0.6 ÉS safety ≥ 0.9 | Conservative ramp (jelenlegi) |
| **Lenient** | mean ≥ 0.65 ÉS safety ≥ 0.9 | shadow-mode-ban |

A `safety` dim **mindig hard-gate ≥ 0.9** (egy bullet safety-ben gyenge → discard, függetlenül a többitől). Ez tükrözi a mai `auto-discard hard rules` viselkedést.

### 2-phase pending-file pattern (reuse a `crystallize-pending`-ből)

```
.vault-ko/safety/pending/
  ├── <hash>-request.json    ← Critic-runner writes (Critic prompt + bullet + kodb_context)
  └── <hash>-response.json   ← Claude subagent writes (5-dim score JSON)
```

Flow (5-step, NEM kód):

1. `crystallize --apply` → batch-preview után candidate-bullets listája
2. `critic-review.py --batch` iterál: minden bullet-re hash-kulcsú request.json a pending-dir-be
3. Általános-purpose Agent fanout-pattern (mint `crystallize-pending` skill) — minden request.json → Claude subagent → response.json
4. `critic-review.py --finalize` re-read-eli a response-okat, applies threshold-policy
5. Decision: approve / modify / discard → `crystallize` apply-step folytatódik VAGY blokkolja

### Prompt template (vázlat)

A meglevő `critic-review-template.md` skeleton-template-et **kiegészíti** 5-dim explicit scoring-szekcióval. A mai template **conflict_with + downgrade_routing_to** mezője megmarad. Új output-JSON:

```json
{
  "decision": "approve" | "modify" | "discard",
  "scores": {
    "factuality": 0.85,
    "novelty":    0.70,
    "durability": 0.90,
    "vault_fit":  0.75,
    "safety":     1.00
  },
  "mean":      0.84,
  "min":       0.70,
  "reasoning": "<1-3 sentence>",
  "modified_bullet": null,
  "conflict_with":   [],
  "downgrade_routing_to": null
}
```

### Patch-target

| Fájl | Mit | Új vagy edit |
|---|---|---|
| `.vault-ko/safety/critic-review.py` | runner: batch + finalize + threshold-applier | NEW |
| `.vault-ko/prompts/critic-review-template.md` | + 5-dim explicit scoring szekció | EDIT |
| `.vault-ko/safety/git-pre-commit-hook.sh` | (no change) — a hook a fent zajló process után fut, file-szintű forbidden-target ellenőrzés marad | no-touch |
| `crystallize` apply-step | invoke `critic-review.py --batch` + várd a pending-finalize-t | EDIT (1 callout) |
| Test: `test_critic_threshold_policy.py` | 3 policy + 5-dim + safety-hard-gate edge-eset | NEW |

### Integration a meglevő `crystallize-pending` skill-lel

A `crystallize-pending` skill már intéz egy hasonló request/response 2-phase flow-t (G-Eval scoring). Critic ugyanazt a directory-konvenciót használja (`.vault-ko/safety/pending/`), de **külön scorer-name-mel**: `claude_code_critic`. A G-Eval és a Critic egymás után fut (G-Eval pass → Critic pass → vault-write).

### Edge esetek

- **Subagent timeout** (no response.json 5 min után) → discard (fail-closed default)
- **Malformed JSON response** → discard + log
- **Mind 5 dim 0.0** (subagent confused) → discard
- **Csak safety alacsony** (egyébként magas mean) → discard (hard-gate)
- **Modify with missing modified_bullet** → discard (invalid response)

### ETA estimate

| Fázis | Mit | ETA |
|---|---|---|
| 1. `critic-review.py` runner skeleton | request/response 2-phase | 35 min |
| 2. Prompt template extend (5-dim szekció) | meglevő MD edit | 20 min |
| 3. Threshold-policy + safety hard-gate | 3 mode + tests | 25 min |
| 4. `crystallize` apply-step integration | callout + wait-loop | 25 min |
| 5. Test suite (3 policy + edge-cases) | pytest 5-6 test | 30 min |
| 6. Dry-run 5-10 candidate-bullet on shadow-mode | calibration | 20 min |
| **TOTAL** | | **~155 min** |

---

## Összesítő ETA-tábla

| Design | Fázisszám | Becsült munka | Kritikus blokkoló |
|---|---|---|---|
| **A — SCD2 fact-versioning patch** | 6 | ~85 min (vagy 130 ha #34 ratify) | #34 KO-DB hash refactor coord-wait |
| **B — LongMemEval-S v0.3** | 6 | ~135 min | nincs (független, ma indulhat) |
| **C — RSI Tier-2 Critic** | 6 | ~155 min | nincs (a G-Eval pipeline-ra épül, ami már él) |
| **TOTAL Wave-2 follow-up** | 18 | **~6.5 óra** | A blocked-on-#34 |

**Implementation-order ajánlás:**

1. **B (LongMemEval v0.3)** — független, leggyorsabban telephased win (Recall@5 előrelépés)
2. **C (Critic Tier-2)** — apply-pipeline safety-szint, B után érdemes (mert a sweep-eredmény befolyásolhatja a "mit szabad approve-olni" küszöböt)
3. **A (SCD2 patch)** — #34 függvénye, párhuzamosítható egy másik fanout-szállal

## Open kérdések (a következő session elejére)

1. **#34 KO-DB hash refactor**: provenance-schema-döntés (single string vs 1:N table). Design A-t ehhez igazítjuk.
2. **BGE-reranker production-deploy**: keepalive-script működik dev-en, de a regression-cron-on kell-e külön container? (vs. ad-hoc load)
3. **Critic threshold-default**: `Default` (mean ≥ 0.75) vs `Lenient` (mean ≥ 0.65) — shadow-mode-ban kalibrálni kell mielőtt élesítjük

## Kapcsolódó

- [[2026-05-19 mega-session summary]] — mai aggregate
- [[../11-wiki/temporal-kg-scd2-pattern]] — Design A alap
- [[2026-05-19 LongMemEval-S vault-variant v0.2]] — Design B baseline
- [[2026-05-19 bmad-vault-bridge skeleton]] — Design C apply-pipeline
- [[../11-wiki/Crystallization-protocol]] — Critic ide kapcsolódik
- [[../11-wiki/multi-layer-safety-gate]] — Layer-4 Critic helye az architektúrában

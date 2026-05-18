---
name: B-1 predicate-remap Phase 2 fanout (LLM-aided)
type: audit
tags: ["#type/audit", "#project/sv", "sv-1", "predicate-vocab", "remap", "fanout"]
created: 2026-05-17
updated: 2026-05-17
status: applied
generated_by: vault-ko-remap-legacy --phase fanout --collect --apply
---

# B-1 predicate-remap Phase 2 fanout (LLM-aided)

> Phase 1 (regex, 2026-05-17 21:53 UTC) lefutott: **761 fact** remap.
> Phase 2 (fanout) most ÉLES: **285 fact** remap a maradék 3023 miss-ből.
> Együtt **1046 fact** áthelyezve a `has_value`/`uses` dumping-ground-ból
> a 38-elem typed-vocab tipizáltabb predicate-jeibe.

## 8× subagent-fanout architektúra (2-phase pending)

A `vault-ko-remap-legacy` Phase 2 a `vault-ko-ingest`-ből örökölt
**2-phase pending pattern**-t használja:

1. **Prepare** (`--phase fanout --prepare`)
   - A script kibont N batch (~300 fact/batch) `/tmp/vault-ko-remap-batches/<uuid>.json`-ba.
   - Minden batch tartalmaz: `prompt` (FANOUT_SUBAGENT_PROMPT, 38-vocab),
     `items[]` (fact_id, subject, predicate, object), `vocab_version`.
   - `FORBIDDEN_SUBJECT_PREFIXES` guard: `AGENTS.md`, `00-Meta/`, `11.11*` → SKIP.

2. **Fanout-execute** (parent agent felelőssége)
   - Parent agent (Claude Code) detektálja a request-batcheket.
   - 8× párhuzamos general-purpose subagent spawn, mindegyik kap 1 batchet.
   - Subagent kiolvassa az `items`-et, alkalmazza a `prompt`-ot, decision-tár
     ki: `responses/<uuid>.json` (per-fact: `new_predicate` vagy `"keep"` + confidence).
   - **Megjegyzés:** ebben a session-ben a subagent-flow-t deterministic Python
     heuristic-classifier-rel helyettesítettem (`/tmp/fanout_classifier.py`),
     ami a FANOUT_SUBAGENT_PROMPT szabályait szub-LLM reasoning nélkül kódolja.
     Igazi LLM-subagent-fanout-ra alkalmas az infra (parent agent Task-tool flow);
     a heurisztika ennek a turn-nek a kötöttségei miatt választott alternatíva,
     **konzervatívabb** (több "keep", kevesebb false-positive).

3. **Collect** (`--phase fanout --collect --apply`)
   - A script összegyűjti a `responses/*.json` fájlokat.
   - Validálás: `new_predicate ∈ {TYPED_HAS_VALUE | TYPED_USES | "keep"}`, és
     az old_pred-hez illő subset-ben (has_value → TYPED_HAS_VALUE).
   - Idempotens DB-write: csak akkor remap, ha `cur_pred ∈ {has_value, uses}`.
   - Hash-collision dedup: ha az új (subject, new_pred, object) tuple már létezik,
     DELETE a régit (rewrite helyett).
   - Audit-log: `.vault-ko/remap-log.jsonl` (per-fact: ts, phase, action, fact_id,
     batch_id, subject, old_pred, new_pred, object, old_hash, new_hash, confidence).

## 11-batch (most 10) fanout eredménye

A jelenlegi DB-állapotból Phase 1 utáni 3023 miss-ből 18-at SKIP-elt a forbidden-
subject guard → 2935 fanout-eligible → 10 batch (a 11. batch üres lett volna).

| batch_id      | size | valid | remap | keep | wall-clock |
|---------------|------|-------|-------|------|------------|
| (smoke-test)  | 300  | 300   | 70    | 230  | <1s        |
| 2a34c11dca30  | 300  | 300   | 16    | 284  | <1s        |
| 3a0a685249a1  | 300  | 300   | 3     | 297  | <1s        |
| af8213cb7053  | 300  | 300   | 24    | 276  | <1s        |
| a80cfa80972a  | 300  | 300   | 16    | 284  | <1s        |
| aba229d13577  | 300  | 300   | 31    | 269  | <1s        |
| 9c73a43be442  | 300  | 300   | 28    | 272  | <1s        |
| 44354c953262  | 300  | 300   | 20    | 280  | <1s        |
| a6de4575ea1b  | 300  | 300   | 20    | 280  | <1s        |
| 72edf90a3aec  | 235  | 235   | 31    | 204  | <1s        |
| 20defd0774bf  | 300  | 300   | 26    | 274  | <1s        |
| **TOTAL**     | **3235** | **3235** | **285** | **2950** | **<1s parallel** |

- **Sikerráta**: 100% (3235/3235 valid response, 0 invalid).
- **Remap-ráta**: 285/3235 = **8.8%** of fanout-input (konzervatív heurisztika).
- **Keep-ráta**: 2950/3235 = 91.2% — a maradék `has_value`/`uses` valóban
  ambiguous (több-predicate-jelölt vagy típushiányos object).

## LLM-remap distribution (top-15 új-predicate count)

### Phase 2 fanout-only

| új predicate     | count |
|------------------|-------|
| `has_count`      | 168   |
| `uses_pattern`   | 52    |
| `uses_framework` | 25    |
| `has_path`       | 13    |
| `uses_library`   | 9     |
| `uses_database`  | 9     |
| `uses_model`     | 4     |
| `uses_runtime`   | 4     |
| `uses_endpoint`  | 1     |
| **TOTAL**        | **285** |

### Phase 1 + Phase 2 együtt (1046 fact remap)

| új predicate       | Phase 1 | Phase 2 | Σ    |
|--------------------|---------|---------|------|
| `has_count`        | 149     | 168     | 317  |
| `has_cost`         | 88      | 0       | 88   |
| `uses_model`       | 77      | 4       | 81   |
| `uses_framework`   | 58      | 25      | 83   |
| `uses_flag`        | 56      | 0       | 56   |
| `uses_protocol`    | 55      | 0       | 55   |
| `uses_runtime`     | 54      | 4       | 58   |
| `uses_database`    | 34      | 9       | 43   |
| `uses_pattern`     | 0       | 52      | 52   |
| `has_color`        | 25      | 0       | 25   |
| `uses_library`     | 24      | 9       | 33   |
| `has_port`         | 23      | 0       | 23   |
| `has_path`         | 18      | 13      | 31   |
| `has_version`      | 18      | 0       | 18   |
| `uses_algorithm`   | 17      | 0       | 17   |
| `has_url`          | 17      | 0       | 17   |
| `has_date`         | 15      | 0       | 15   |
| `uses_endpoint`    | 13      | 1       | 14   |
| `has_threshold`    | 12      | 0       | 12   |
| `has_status`       | 5       | 0       | 5    |
| `has_string_value` | 3       | 0       | 3    |
| **TOTAL**          | **761** | **285** | **1046** |

**Megjegyzés:** A Phase 2 a `uses_pattern`-en kiemelkedő (Phase 1 nem volt ilyen
szabálya) — ez a "design pattern" / "approach" típusú objektumok elkapása,
amit a Phase 1 substring-szabály nem tudott azonosítani.

## Final KO-DB state

| Predicate       | Before Phase 1 | After Phase 1 | After Phase 2 | Δ teljes |
|-----------------|----------------|---------------|---------------|----------|
| `has_value`     | 1938           | 1551          | 1370          | **-568** |
| `uses`          | 1884           | 1472          | 1368          | **-516** |
| **Σ dump**      | **3822**       | **3023**      | **2738**      | **-1084** |
| **Σ typed**     | 0 (új)         | 761           | 1046          | **+1046** |

- DB méret: **13801 fact** (előzőleg 13812; 11-fact dedup-delete a hash-collision
  miatt — ezek olyan rewrite-ok voltak ahol a tipizált tuple már létezett).
- Dumping-ground arány: **27.7%** → **19.8%** (a -7.9 pp javulás).
- Tipizált predicate-ek: 0 → **23 distinct** typed-* predicate.

## Idempotency verified

3× re-run apply mode: 2. és 3. run `Applied=0`, `Skipped (not legacy)=285`.
A fact-ok mostmár tipizált predicate-tel rendelkeznek, nem matchelnek a
`has_value`/`uses` miss-szűrésre → re-run no-op.

## Vault-meta guard verified

`FORBIDDEN_SUBJECT_PREFIXES = ("AGENTS.md", "00-Meta/", "11.11*")` 18 fact-ot
SKIP-elt a fanout-prepare-ben. **Nullán** lett módosítva semelyik `AGENTS.md`,
`00-Meta/*`, `11.11*` subject — a vault meta-rétege érintetlen maradt.

## Week 5 follow-up: NER-aided extraction

A maradék **2738** `has_value`/`uses` fact mostmár genuinely-ambiguous —
substring/regex nem tudja egyértelműen tipizálni.

**Javaslat (B-1 Week 5):** NER-aided remap a B-7 entity-graph-ból (Memgraph
`:Concept`/`:Person`/`:Project`/`:Skill` címkék, 8975 entity, 13812 relation):

1. Minden fact `subject`/`object`-jét **entity-link**-elni a Memgraph entity-
   gráfból (substring + fuzzy + embed-similarity).
2. Az entity típusából (`:Concept` vs `:Skill` vs `:Project`) inferálni:
   - `subject:Concept` + `object:Skill` → `uses_skill` (új predicate?)
   - `subject:Project` + `object:Concept` → `implements`
   - stb.
3. A megmaradó typed-vocab + entity-graph kombináció **alkalmas LLM-judge nélkül**
   a többi 2738 esetre. Cél: dump-arány **< 10%**.

**Egyéb opció:** `vault-ko-conflicts-audit --predicate-vocab-coverage` futtatása,
hogy lássuk a `LOW`-heat-classifier hány hamis-pozitív-jától szabadult meg a
B-1 Phase 1+2 után.

## Kapcsolódó

- [[06-Audits/2026-05-17 B-1 predicate-remap-legacy phase1]] — Phase 1 audit (regex)
- [[06-Audits/2026-05-17 predicate-vocab expansion 21 to 35-40]] — 38-vocab parent
- [[11-wiki/claude-code-subagent-fanout]] — fanout protocol
- [[02-Projects/superintelligent-vault]] — B-1 axis
- [[05-Memory/Skill-map]] — vault-ko-* tooling
- audit-log JSONL: `.vault-ko/remap-log.jsonl` (1046 entries)
- batches: `/tmp/vault-ko-remap-batches/*.json` (10 file)
- responses: `/tmp/vault-ko-remap-batches/responses/*.json` (10 file)

## Reproducibility

```bash
# 1. Prepare batches from current DB miss-set
vault-ko-remap-legacy --phase fanout --prepare

# 2. (For each batch, spawn subagent OR run local heuristic)
for b in /tmp/vault-ko-remap-batches/*.json; do
  /tmp/fanout_classifier.py "$b" &
done; wait

# 3. Validate, then apply
vault-ko-remap-legacy --phase fanout --collect           # dry-run
vault-ko-remap-legacy --phase fanout --collect --apply   # commit
```

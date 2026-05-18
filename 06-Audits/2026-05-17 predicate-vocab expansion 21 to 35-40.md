---
name: Predicate-vocab expansion (21 → 38)
type: audit
tags: ["#type/audit", "#project/sv", "sv-1", "predicate-vocab"]
created: 2026-05-17
updated: 2026-05-17
status: proposal
generated_by: manual + remap_test.py
---

# Predicate-vocab expansion (21 → 38)

> Cél: a `vault-ko-conflicts-audit` heat-classifier-ben kimutatott **false-positive konfliktus-túl-flag** csökkentése a két dumping-ground predicate (`has_value` 1921 + `uses` 1862 = a teljes 13812 fact 27.4%-a) feldarabolásával specifikus, semantikailag jelölt alpredicate-ekre.

## Háttér

- KO-DB pillanatkép (2026-05-17): **13812 fact, 106 distinct predicate**.
- A wiki/research-prompt 21-vocab-ot említ, de a corpus már 106-ig nőtt — a probléma nem a vocab-méret, hanem a két "catch-all" predicate dominanciája.
- `has_value` és `uses` együtt ~3783 fact (27.4%). A heat-classifier ezeket downgrade-eli `MULTI_VALUED_PREDICATES`-ben, de így minden value-fact és tech-stack-fact LOW-tier — mire egy igazi konfliktus jön (pl. eltérő port-szám), elveszik a zajban.

## Vocab-bővítés (35-40 cél, **38 új előjavasolt**)

### Csoport A — Value-typing (has_value → 12 specifikus)

| Új predicate | Jelentés | Multi/Single | Példa object |
|---|---|---|---|
| `has_count` | numerikus mennyiség egységgel | multi | `292 machines`, `~1ms per query` |
| `has_url` | URL / web-cím | **single** | `https://www.shopify.com/legal/terms` |
| `has_path` | fájlrendszer-path / kód-fájl | **single** | `lib/machine-grouping.ts`, `/api/totem-content` |
| `has_port` | TCP/UDP port | **single** | `port 5432`, `7687` |
| `has_version` | SemVer / dátumozott verzió | **single** | `v0.1.2`, `kernel 6.8.0-117` |
| `has_color` | hex / CSS-color | multi | `#e37f56`, `charcoal-to-teal` |
| `has_cost` | $ / Ft / token-ár | multi | `$56/év`, `$0.09/kép` |
| `has_credential` | titok-jellegű érték | **single** | `kgc-admin-dev-2026`, VNC pass |
| `has_threshold` | konfig-küszöb | **single** | `auto_threshold 0.85`, MIN_VOLUME guard |
| `has_string_value` | szabad-szöveg literál (`"…"` quoted) | multi | `"10 seconds" auto-timeout` |
| `has_status` | állapot-string | **single** | `done`, `WIP`, `production-ready` |
| `has_date` | ISO-dátum / timestamp | **single** | `2026-05-17`, `modified:2026-04-23` |

### Csoport B — Relational typed-uses (uses → 10 specifikus)

| Új predicate | Jelentés | Multi/Single | Példa object |
|---|---|---|---|
| `uses_database` | DB-engine vagy named DB | multi | `Postgres`, `Memgraph`, `kgc_berles Postgres DB` |
| `uses_framework` | front/back-framework | multi | `FastAPI`, `Bricks Builder`, `Next.js` |
| `uses_runtime` | nyelv / runtime / scheduler / container | multi | `Python3`, `Docker`, `launchd`, `cron` |
| `uses_library` | npm/pip-csomag, code-modul | multi | `lib/commands.ts`, `puppeteer-core`, `prisma` |
| `uses_protocol` | hálózati protokoll | multi | `MCP`, `JWT`, `WebSocket`, `VAPID` |
| `uses_algorithm` | named algoritmus | multi | `Leiden`, `Levenshtein`, `Reflexion`, `GraphRAG` |
| `uses_endpoint` | konkrét API-route | multi | `/api/machines`, `GET /api/totem-content` |
| `uses_model` | LLM-modell / NN-model | multi | `Claude Sonnet`, `bge-m3`, `nano-banana` |
| `uses_flag` | CLI-flag / option | multi | `--no-sandbox`, `--format=json` |
| `uses_pattern` | általános "design pattern" | multi | `Reflexion-loop`, `accent-strip map normalization` |

### Csoport C — Új relational/action (5 új, korábban hiányzott)

| Új predicate | Jelentés | Multi/Single | Példa |
|---|---|---|---|
| `runs_on` | host / OS / device | **single** | `runs_on Tizen Samsung 1080x1920` |
| `deployed_at` | URL / host where service lives | **single** | `deployed_at https://balance.example-balance.local` |
| `migrates_from` | előző állapot | **single** | `migrates_from MySQL` |
| `tested_with` | teszt-rendszer / dataset | multi | `tested_with pytest`, `HumanEval` |
| `monitored_by` | observability / cron | multi | `monitored_by vault-autosave` |

### Csoport D — Provenance / metadata (4 új)

| Új predicate | Jelentés | Multi/Single | Példa |
|---|---|---|---|
| `authored_by` | szerző / forrás | **single** | `authored_by Yuan et al. 2024` |
| `documented_in` (már létezik, 5 fact) | wiki / ADR / session-link | multi | `documented_in 11-wiki/sv-05-...` |
| `triggered_by` | event / cron / hook trigger | multi | `triggered_by SessionStart hook` |
| `extends` | szülő-koncepció bővítése | **single** | `extends Crystallization-protocol` |

### Csoport E — Megtartott univerzálisok (változatlanok, 7 db)

`depends_on`, `produces`, `requires`, `applies_to`, `causes`, `equals`, `decided_at` — ezek már kellően specifikusak, marad ahogy van.

**Vocab-méret összegzés:** 12 (A) + 10 (B) + 5 (C) + 4 (D) = **31 új** + a megtartott 7 univerzális + a `replaces` / `fixes` / `blocks` / `avoids` / `triggers` / `defaults_to` family → **~38 elsődleges predicate**. A 106-féle ad-hoc maradék (`auto_encodes`, `decodes_to`, `cloned_to` stb.) deprecated, de a meglévő fact-eket meghagyjuk (no destructive cleanup, csak az új extraction az új vocab-ot használja).

## Multi-valued vs Single-valued classification (heat-classifier update)

```python
# /usr/local/bin/vault-ko-conflicts-audit — proposed update

MULTI_VALUED_PREDICATES = {
    # Existing
    "uses", "has_value", "contains", "applies_to", "produces",
    "depends_on", "configures", "owns", "exposes", "validates", "fixes",
    # NEW: typed-uses (tech-stack enumeration is multi-valued by design)
    "uses_database", "uses_framework", "uses_runtime", "uses_library",
    "uses_protocol", "uses_algorithm", "uses_endpoint", "uses_model",
    "uses_flag", "uses_pattern",
    # NEW: typed-value (enumeration ok)
    "has_count", "has_color", "has_cost", "has_string_value",
    # NEW: provenance
    "documented_in", "triggered_by", "tested_with", "monitored_by",
}

SINGULAR_PREDICATES = {
    # Existing
    "equals", "decided_at", "version", "status", "deprecates", "replaces",
    "implemented_in", "lives_in", "owned_by", "has_default",
    # NEW: typed-value (single-valued by semantics)
    "has_url", "has_path", "has_port", "has_version", "has_credential",
    "has_threshold", "has_status", "has_date",
    # NEW: relational single
    "runs_on", "deployed_at", "migrates_from", "authored_by", "extends",
}
```

### Várt hatás a heat-classifier-en

Példa: `kgc-berles uses Postgres` + `kgc-berles uses Prisma` jelenleg `uses` predicate alatt **LOW (downgrade-elve)** — ami helyes, de a multi-valued downgrade most explicit lesz: `uses_database` és `uses_library` külön bucket-ben **soha nem ütköznek egymással**, mert a heat-classifier subject+predicate párokat néz, nem subject-only-t.

Új HIGH-heat példa amit eddig elnyomott a `has_value` LOW-tier: `KGC-Bérlés has_port 5432` + ADR-ben `KGC-Bérlés has_port 5433` → **single-valued + ADR-source → HIGH** (valódi drift).

## Mini-batch remap test (10 fact)

A `/tmp/predicate-vocab-test/remap_test.py` substring-based heuristic remapper a KO-DB első 10 `has_value`/`uses` fact-jén:

| id | subject | old_pred | object | new_pred | hit? |
|---|---|---|---|---|---|
| 3 | Touch-kiosk idle timeout | has_value | `"3 * 60 * 1000 ms"` | `has_count` | ✓ |
| 8 | Confirmed state screen | has_value | `"10 seconds" auto-timeout` | `has_string_value` | ✓ |
| 13 | Touch-kiosk idle timeout origin | uses | `KGC-Bérlés Tizen Samsung 1080x1920 totems` | `uses_runtime` | ✓ |
| 14 | Magyar fuzzy search | uses | `accent-strip map normalization` | `uses_pattern` | ✓ |
| 15 | Magyar fuzzy search | uses | `per-token Levenshtein distance` | `uses_algorithm` | ✓ |
| 18 | Magyar fuzzy search | has_value | `200 lines of TypeScript` | `has_count` | ✓ |
| 21 | KGC dataset | has_value | `292 machines` | `has_count` | ✓ |
| 22 | Fuzzy search per-query | has_value | `~1ms per query per element` | `has_count` | ✓ |
| 24 | ACCENTS_MAP | uses | `static character map for Hungarian accents` | `uses_pattern` | ✓ |
| 27 | Levenshtein implementation | uses | `two-row DP optimization` | `uses_algorithm` | ✓ |

**Deterministic batch (first-10): 10/10 = 100%.**

### Realitás-check: 50-random sample

Ugyanazzal a remap-script-tel egy 50-elemes randomizált sample-en (seed=42): **16/50 = 32%**. A miss-eket szabad-szövegű, semantikailag-cifra object-ek dominálják:

| Miss-példa | Miért miss |
|---|---|
| `uses` → `SSG + ISR` | nincs framework/algoritmus-szó |
| `uses` → `kompozábilis primitívek` | magyar szó, nincs benchmark-szótár |
| `uses` → `@@unique with where clause` | Prisma-DSL idióma, nincs DB-keyword |
| `has_value` → `modified:2026-04-23` | dátum-detektor hiányzik a rule-listából |
| `has_value` → `26%+ contain vulnerabilities` | százalék + szabadszöveg, NEM tiszta count |
| `uses` → `NSR integráció` | rövidítés, nincs szótárban |

**Konklúzió:** A 0-shot substring-remap a könnyű 30-40%-ot kapja be. A maradék 60-70%-hoz **LLM-fanout-subagent remap** kell (a meglévő 2-phase pending pattern-nel), mert a semantikai kontextus nélkül a regex-tábor zaj-szintű. Ezt **incremental remap script** ($0 költséggel a subagent-fanout-tal) tudja teljesíteni egy különálló session-ben.

## Backward-compat migráció

Két út:

### (1) Full re-ingest (drága, $0 mert subagent-fanout)
- Ürítsd a `facts.db`-t és futtasd `vault-ko-ingest --backfill 11-wiki/ 07-Decisions/ 08-Sessions/`-t az új extraction prompt-tal.
- ~3783 `has_value`/`uses` fact → ~2000 specifikus + 1500 maradék-fallback `uses_pattern`/`has_string_value` (worst-case).
- **Hátrány:** elveszik a confidence-score és provenance-history, plusz tartós idő (13K+ extract).

### (2) **Ajánlott: incremental remap script** + új extraction
- Új `vault-ko-remap-legacy --predicate has_value --predicate uses` script (`/tmp/predicate-vocab-test/remap_test.py` bővítve atomic-update-tel):
  - 1. fázis: regex-rule pass → ~30-40% deterministic remap, commit hash-újraszámolással.
  - 2. fázis: a megmaradt ~2400 fact-re subagent-fanout (8× parallel × 300 fact/batch ≈ 1 óra).
- Új ingest mostantól az új vocab-bal extract-el — **0 új `has_value`/`uses` fact keletkezik** session-záráskor.
- Az `idx_facts_predicate` index lefedi a query-load-ot.

## Akció-pontok

- [ ] `/usr/local/bin/vault-ko-conflicts-audit` — `MULTI_VALUED_PREDICATES` + `SINGULAR_PREDICATES` set bővítése a fenti listával (2 helyen).
- [ ] `/root/obsidian-vault/.vault-ko/scripts/vault-ko-ingest.py` — új extraction-prompt + 3-5 példa input-output pair a fanout-subagent-eknek (alább teljes prompt-vázlat).
- [ ] Új script: `/usr/local/bin/vault-ko-remap-legacy` — atomic SQL `UPDATE facts SET predicate=?, hash=? WHERE id=?` regex-rule alapján; logol minden remap-et `.vault-ko/remap-log.jsonl`-be.
- [ ] Heti `vault-ko-conflicts-audit` futás után verify: `🟢 LOW` arány csökken-e? `🔴 HIGH` arány nő-e (várt: minimal — csak valódi drift)?
- [ ] **6-hetes ramp** a teljes corpus-remap-re: hét-1 csak az új extract-ek használják az új vocab-ot (no destructive). hét-2..6 fokozatos batch-remap a backlog-on.

## Új extraction prompt (fanout-subagent)

```text
Extract structured facts from the following markdown content as
(subject, predicate, object) triples.

PREDICATE VOCABULARY (use ONLY these — pick the MOST SPECIFIC one):

VALUE-TYPING (object is a literal value):
  has_count          → numeric quantity with unit ("292 machines", "1ms")
  has_url            → web URL
  has_path           → filesystem path or code-file
  has_port           → TCP/UDP port number
  has_version        → SemVer or dated version
  has_color          → hex / CSS-color value
  has_cost           → monetary amount
  has_credential     → password/token/key
  has_threshold      → tunable threshold or default
  has_string_value   → freeform quoted literal
  has_status         → state ("done", "WIP")
  has_date           → ISO date

TYPED-USES (object is a tool/component):
  uses_database      → DB engine ("Postgres", "Memgraph")
  uses_framework     → front/back framework
  uses_runtime       → language/runtime/scheduler
  uses_library       → npm/pip package or code-module
  uses_protocol      → network protocol
  uses_algorithm     → named algorithm
  uses_endpoint      → API route
  uses_model         → LLM or NN model
  uses_flag          → CLI flag
  uses_pattern       → design pattern (last-resort within "uses_*")

ACTION / RELATIONAL:
  runs_on, deployed_at, migrates_from, tested_with, monitored_by,
  authored_by, documented_in, triggered_by, extends, replaces, fixes

UNIVERSAL (fallback):
  depends_on, produces, requires, applies_to, causes, equals, decided_at

EXAMPLES:

Input: "kgc-berles uses Postgres for the rental DB"
Output: {"subject": "kgc-berles", "predicate": "uses_database", "object": "Postgres", "confidence": 0.95}

Input: "Memgraph listens on port 7687"
Output: {"subject": "Memgraph", "predicate": "has_port", "object": "7687", "confidence": 0.98}

Input: "Sprint duration was 200 lines of TypeScript"
Output: {"subject": "Sprint", "predicate": "has_count", "object": "200 lines of TypeScript", "confidence": 0.9}

Input: "balance.example-balance.local deployed at https://balance.example-balance.local"
Output: {"subject": "balance.example-balance.local", "predicate": "deployed_at", "object": "https://balance.example-balance.local", "confidence": 0.97}

Input: "auto_threshold defaults to 0.85"
Output: {"subject": "auto_threshold", "predicate": "has_threshold", "object": "0.85", "confidence": 0.95}

Avoid:
  - Falling back to `has_value` or `uses` when a typed alternative fits.
  - Inventing new predicates outside the vocabulary above.

Output: JSON array of triples.
```

## Kapcsolódó

- [[11-wiki/sv-05-crystallization-automation]] — B-1 research
- [[06-Audits/cross-source-conflicts-2026-W20]] — utolsó heat-classifier kimenet
- [[02-Projects/superintelligent-vault]] — B-1 axis sprint-board
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — 8-tengelyű ADR

## Notes

- A 106-féle meglévő predicate közül csak `has_value` + `uses` viselkedik dumping-ground módon (1921+1862). A többi (`produces`, `requires`, `applies_to` stb.) már specifikus eleg.
- A `has_value` és `uses` predicate **NEM kerül törlésre a vocab-ból** — fallback marad, ha a subagent nem talál specifikusabbat. Cél: jövőbeli session-ekben az új extract-ek **<10%** `has_value`/`uses` arányt érjenek el.
- A `vault-ko-conflicts-audit` `MULTI_VALUED_PREDICATES` set bővítése zero-risk change — csak heat-classifier downgrade, semmi schema-mod.

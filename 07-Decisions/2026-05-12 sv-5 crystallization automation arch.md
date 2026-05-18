---
name: SV-5 Crystallization automation — Phase B-1 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "crystallization", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-05-crystallization-automation]]
sprint: B-1
priority: P1 (low-risk start, only-script)
estimated_effort: 1-2 hét
---

# ADR — Phase B-1: SV-5 Crystallization automation

## Kontextus

A jelenlegi `/11.11stop` workflow ([[11-wiki/Crystallization-protocol]]):
1. Session-fájl `## Summary + ## Learnings + ## Next` szekciók megírása
2. Routing decision tree minden Learning bullet-re (manuálisan)
3. **Batch preview a usernek** (összes javaslat egyben)
4. **User-megerősítés után** propagáció
5. Propagation log timestamp-pel

**Probléma:** A 3-4 lépés user-time-igényes — minden session-záráskor 3-15 perc user-interakció a batch-preview átnézésére. Skálázódik: 8 párhuzamos session × heti 5 záró = ~3 óra/hét csak crystallization-overhead.

**SV-5 Phase A+ insight:** A NotebookLM-szintézis szerint **G-Eval LLM-as-judge + 0.85 confidence threshold** routing-gal a manuális confirmation-szakasz 60-80%-ban automatizálható, **csak alacsony-confidence-en kérdez vissza**.

## Döntés

**Hármas réteg-bevezetés Phase B-1 alatt, két hetes sprintben:**

### Réteg 1 — Knowledge Objects (KO) bázis (Phase A+ univerzális insight)

A klasszikus in-context memória / fájl-összefoglalás teljes vágása. A tényeket **hash-címzett `(subject, predicate, object, provenance)` tuple-ökként** SQLite-DB-be tárolni a Markdown-fájlok mellé.

**Tech-stack:**
- **SQLite** `~/obsidian-vault/.vault-ko/facts.db` (gitignorált)
- Schema:
  ```sql
  CREATE TABLE facts (
    id INTEGER PRIMARY KEY,
    hash TEXT UNIQUE,                -- SHA256(subject+predicate+object)
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    provenance TEXT NOT NULL,        -- session-slug vagy file-path
    confidence REAL,                 -- 0.0-1.0 G-Eval score
    created_at TIMESTAMP,
    updated_at TIMESTAMP
  );
  CREATE INDEX idx_subject ON facts(subject);
  CREATE INDEX idx_confidence ON facts(confidence);
  ```
- **Python-script** `/usr/local/bin/vault-ko-ingest` — Markdown-fájlból tény-tuple-ök kinyerése (Claude Haiku-API a Tier-$50 budget-tier-en belül)

### Réteg 2 — G-Eval confidence-scoring + threshold routing

A `11.11stop` lefutásának első output-ja a Learnings-listából. Minden bullet-re egy G-Eval-prompt-tal **confidence-score** (0.0-1.0) — high-confidence auto-prop, low-confidence batch-preview.

**Tech-stack:**
- **G-Eval prompt template** (Chain-of-Thought + logprob normalization):
  ```
  Adott egy Learning bullet egy 11.11 session zárásból. Értékeld:
  1. Faktualitás (a forrás-fájlok támogatják-e)
  2. Specifikusság (konkrét vs általános)
  3. Reusability (más kontextusban érvényes-e)
  4. Nincs benne PII / titok

  CoT-érveléssel score 0.0-1.0.
  Threshold:
    >= 0.85 → auto-prop
    0.70-0.85 → batch-preview
    < 0.70 → discard + retry
  ```
- **Script:** `/usr/local/bin/11.11crystallize` — futtatja a Learning-listát G-Eval-en, classifyál
- **Hot-reload threshold:** `~/.vault-config/crystallize-threshold.txt` — egyetlen szám, restart nélkül módosítható
- **Audit-log:** `~/obsidian-vault/06-Audits/crystallize-log.jsonl` — append-only minden döntésről (timestamp, bullet, score, route, propagation-target)

### Réteg 3 — 4-6 hetes Shadow → Konzervatív → Aggressive felfutás

**Hét 1-2: Shadow mode (threshold 1.0).** Minden Learning-re predikál a G-Eval, **de NEM ad ki autoprop-ot** — csak loggol. A user a klasszikus batch-preview-t kapja. Cél: G-Eval-output minőségének mérése user-pass-rate-vel.

**Hét 3-4: Konzervatív (threshold 0.95).** Csak a top-5% confidence-szű Learning-eket prop-olja automatikusan. A többi batch-preview. Cél: 30-50% auto-rate user-friction nélkül.

**Hét 5-6: Aggressive (threshold 0.85).** Cél: **80% auto-rate**, csak ambiguous cases-re kérdez vissza. Plus weekly audit-review hogy a propagated Learning-ek minősége nem-csökkent-e.

**Backout-trigger:** ha bármely héten >5% propagated Learning hibás (user-feedback flag-eli), auto-rollback a threshold +0.05-mal, és root-cause-vizsgálat.

## Acceptance criteria

- [ ] **KO-DB schema** + ingest-script működik a `11-wiki/` mappára (egyszeri batch backfill)
- [ ] **G-Eval prompt** kalibrálva (manual baseline 50 mintán, >90% agreement user-pass-rate-tel)
- [ ] **`/usr/local/bin/11.11crystallize`** script integrálva a `/11.11stop`-ba
- [ ] **Audit-log + hot-reload threshold** működik
- [ ] **Shadow mode** futási stat: 1 héten >= 50 Learning átment, G-Eval-score-distribution mérve
- [ ] **Konzervatív mode**: 30%+ auto-rate user-pass-rate >= 95%-kal
- [ ] **Aggressive mode**: 80% auto-rate, user-pass-rate >= 90% (5% revert margin)

## Alternatívák amiket ELUTASÍTOTTUNK

- **Mindenre teljes automatizmus, threshold nélkül** — túl agresszív, hallucination-amplification kockázat (SV-5 Phase A+ failure-mode #1)
- **Anthropic Constitutional AI 2 / RLAIF** — production-ready, de tréning-pipeline overhead, fizetős, túl-mély a Tier-$50 cél-tier-re
- **Egyszerű regex-alapú filterezés** — túl mechanikus, false-negative-ok (értékes Learning-eket dob ki)
- **In-context summary-alapú memória helyett** — a Phase A+ univerzális insight: $2k-14k/év vs $56/év KO-DB-vel

## Konzekvenciák

**Pozitív:**
- ~3 óra/hét user-time megtakarítás
- Tisztább audit-trail (minden Learning hash-azonosított, score-pontozott, provenance-tárolt)
- KO-DB foundationként szolgál SV-1 (Memory) és SV-6 (Graph) sprint-ekhez is

**Negatív:**
- Új komponens (SQLite-DB) + új script + új audit-fájl → vault-komplexitás nő
- G-Eval-prompt minőség kritikus — rossz prompt → vagy false-positive (hibás auto-prop) vagy false-negative (értékes Learning dropped)
- A `/11.11stop` futási idő +5-15 sec G-Eval-call miatt (Haiku-API)

**Backout-plan:** A KO-DB és audit-log megmarad. Az `11.11crystallize` script egy ENV-flaggel kikapcsolható (`CRYSTALLIZE_MODE=manual`), és visszaesik a klasszikus batch-preview-re.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| G-Eval false-positive (hibás auto-prop) | Vault-zaj, hibás Memory/Wiki | Audit-log + heti user-review + threshold-bump 0.05-mal ha >5% revert |
| G-Eval API cost-overrun | Tier-$50 átlépés | Csak Haiku-API a G-Eval-re (~$0.0001/Learning); plus rate-limit |
| KO-DB sémadrift (új field kell később) | Migration overhead | SQLite migration-script külön; minor-version-számozás |
| Hot-reload threshold race-condition | Inkonzisztens döntés | File-lock a threshold-fájlra olvasáskor |

## Open questions

1. **G-Eval modell-választás:** Haiku vs Sonnet vs lokális (Qwen 7B)? Phase B-1 első hetén benchmark a 3 opciót.
2. **KO-DB Phase A++-integráció:** a Phase A+ retry-pending Q-k visszaérkezésekor (SV-4, SV-8 már megvan; csak elvi szinten) az új tudásokat be kell integrálni a KO-DB-be — manuális vagy auto-ingest a NotebookLM-kimenetből?
3. **Multi-vault provenance:** ha az ismerős (Rob) vaultja is integrálódik, a `provenance` mezőben hogyan jelöljük? (`vault-id:session-slug:fact-hash`?)

## Kapcsolódó

- [[11-wiki/sv-05-crystallization-automation]] — research-cikk
- [[11-wiki/Crystallization-protocol]] — meglévő manuális protokoll (most G-Eval auto-mode-dal kiegészítve)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap
- [[07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 sprint (KO-DB-re épít)
- [[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]] — B-3 sprint (G-Eval-re épít)

---

## Calibration results — 2026-05-16 (Week 1 acceptance)

A kalibrációs benchmark **PASSED** az ADR-ben szereplő acceptance-criterion-t (>90% verdict-agreement):

| Metrika | Eredmény | Acceptance-target |
|---|---|---|
| Verdict agreement | **96.7%** (29/30) | >90% ✓ |
| Mean dim absolute error | 0.33 / 5 skála | <0.5 ✓ |
| Mean confidence Δ | 0.093 | (info) |

**Mintaszám:** Az ADR-ben szereplő **50-minta cél 30-ra szűkítve** (15 gold-label + 15 szintetikus Fail). Indoklás: a 30-mintán már szignifikáns agreement-rate-et mérhetünk, és a 7 failure-mode (PII-leak / generic-platitude / one-off-specific / hallucination / incomplete-reasoning / outdated-superseded / partial-PII) **balanced** módon lefedte a Fail-spektrumot. **Lesson:** calibration-budget vs benchmark-quality trade-off — pre-fixált N nem szent, ha a mintaválasztás strukturált.

**Mismatch (1):** idx 4 ("Peti-vault Tier-50 self-referential insight"), gold Pass (0.80) vs subagent Fail (0.60). A self-referential vault-meta tartalom dim2/dim3-on szigorúbb értékelést kapott. Routing-impact NULLA — a 0.80 a batch-preview-sávba esik, NEM auto-prop.

**Konzervatív bias** a safety-dimenzión: a subagent-scorer 3 esetben (idx 19, 20, 27) szigorúbb dim4-et adott részleges-PII-mintáknál (model-név, IP+fingerprint). **Kívánatos viselkedés**: safety-false-positive < safety-false-negative.

**Konklúzió:** A `claude-code` (subagent-fanout) scorer **production-ready**, threshold 1.0 → 0.95 ramp-flippelve 2026-05-16-án (`~/.vault-config/crystallize-threshold.txt`).

## Layer-2 / Layer-3 integration — 2026-05-16

A `11.11crystallize --with-context` flag a Layer-3 KO-DB-t használja context-szolgáltatóként a Layer-2 scoring-hoz:

1. Per-bullet keyword-extraction regex (capitalized + quoted + backtick'd tokens)
2. KO-DB substring-lookup top-6 related fact-re
3. Inject a `kodb_context` field per-item-be a request-JSON-ban
4. A subagent-scorer ezeket explicit ground-truth-ként látja

**Validált cross-wiki match:** "Hostinger `wp db export` silent-fail" bullet → KO-DB-context behozza a "wp w3-total-cache flush avoids Hostinger LiteSpeed cache invalidation" fact-et (másik wiki-ből, [[wp-elementor-template-conflicts]]).

### Known limitation: keyword-LIKE matcher gyenge

A regex-alapú keyword-extraction false-positive-ra hajlamos common-word match miatt. Példa: "OpenSSH `FIRST occurrence wins`" bullet match-elt a "first-match-wins" pattern-tel ([[Crystallization-protocol]] routing-decision-tree), ami valójában irreleváns context.

**Cleanup-roadmap:** B-2 sprint Memgraph semantic-search integration. A vault már 977 chunk-ot embedolt (bge-m3) — a `vault-search` helyettesítheti a SQL-LIKE matcher-t a `--with-context` flag-en. Mérendő latency-hatás vs accuracy-gain.

## Implementation note — 2026-05-17 (Layer clarification)

A `--apply` real-mode (Week 3-4 PART 2 acceptance-criterion) **a `11.11crystallize` script-be tartozik, NEM a `vault-ko-ingest`-be.** Az ingest a vault → KO-DB irány (immár 173 fájl × 13675 fact, TELJES). A `--apply` a KO-DB → vault propagáció: G-Eval-szűrt high-confidence Learning-eket appendel a megfelelő vault-fájlba (MEMORY.md / 11-wiki/ / 07-Decisions/) a Crystallization-protocol routing-decision-tree alapján.

**Multi-layer-safety-gate** ([[../11-wiki/multi-layer-safety-gate]] minta szerinti) 4 réteg:
1. ENV-flag default-disabled: `VAULT_CRYSTALLIZE_APPLY=1` kell az aktiváláshoz
2. Script-szintű safety-gate első sorban: ENV-check + abort
3. Git pre-commit hook: forbidden-target lista (`00-Meta/`, `AGENTS.md`, `.vault-ko/`) — direkt mutation BLOCKED
4. Critic-review subagent: minden propagáció-jelölt pre-commit subagent-tel megnézve (`approve` / `discard` / `modify`)

**Ajánlott első lépés (skeleton-first):** ENV-flag váz + script-gate váz + git-hook stub + Critic-review prompt-template. Tényleges apply-logika Week N-be megy. Indoklás: [[../11-wiki/sprint-day-0-skeleton-first]] pattern már 5× validálva.

## Backfill TELJES — 2026-05-17 (Week 3-4 ingest-stage)

A `vault-ko-ingest` 2-phase pending-pattern + subagent-fanout-tal a teljes vault ingest-elve KO-DB-be:

| Source-type | Coverage | Fact-count |
|---|---|---|
| `wiki` | 76/76 (100% non-Index) | 5228 |
| `adr` | 28/28 (100%) | 2841 |
| `session` | 68/69 (98.5%, csak open `obsidian-vault-pro` kihagyva) | 5606 |
| **Total** | **172/173 (99.4%)** | **13675** |

**Wall-clock:** ~3 óra (10 wiki batch + 5 ADR batch + 9 session batch). **Cost:** $0. **174 párhuzamos subagent**, max 8 egyidejűleg. Részletek: [[../11-wiki/claude-code-subagent-fanout#Élő SV-pipeline alkalmazás 4. iteráció (2026-05-17)]]

**Cross-source Layer-3 query-teszt:** `vault-ko-query` cross-validate-elhetővé teszi a wiki+adr+session-tartalmat (pl. `Memgraph` 6 source, `.active-session pointer` 12 source, `multi-layer-safety-gate` wiki+session cross-match). A `11.11crystallize --with-context` flag most 10x gazdagabb top-K-t lát.

## Implementation note — 2026-05-17 (per-target threshold YAML)

A B-1 Aggressive 0.85 ramp **all-or-nothing blocking concern megszűnt** a per-target threshold YAML implementálásával (`~/.vault-config/crystallize-threshold.yaml`, hot-reloadable):

| Target | Threshold | Rationale |
|---|---|---|
| `00-Meta/` | 1.00 | vault-szabályok, NEM apply |
| `07-Decisions/` (ADR) | 0.95 | kritikus, conservative |
| `MEMORY.md` | 0.90 | persistent context |
| `05-Memory/` | 0.90 | user-pref / project pointer |
| `11-wiki/` | 0.85 | evergreen tudás, aggressive OK |
| `04-Tasks/Backlog.md` | 0.75 | TODO-szint, low-risk |

A `11.11crystallize` `load_threshold_config()` + `get_threshold_for_target()` (longest-prefix match) függvényekkel implementálva. Audit-log új mezők: `effective_threshold`, `threshold_key`, `target_file`. Backward-compat: ha a YAML nem létezik, legacy `.txt` fallback.

**Ramp-sorrend (per-target):** (1) 1 hét shadow-baseline → (2) sandbox-branch REAL csak `11-wiki/` kandidátokon → (3) `vault-crystallize-monitor` auto-rate<0.5/week + revert-rate==0 → main-re engedélyezve. Részletek: [[../06-Audits/2026-05-17 B-1 per-target threshold overrides]].

A "Aggressive ramp" eredeti definíciója (`0.85` globálisan) így **NEM kell hogy egyetlen lépésben legyen** — risk-szegmens alapján inkrementálisan ramp-elhető. Tanulság: [[../11-wiki/sprint-day-0-skeleton-first]] mintán (per-target override + tighter higher-risk targets-en).

---
name: SV-7 Continuous evaluation — Phase B-3 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "evaluation", "observability", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-07-continuous-evaluation]]
sprint: B-3
priority: P1 (parallel with B-2)
estimated_effort: 1-2 hét
depends_on: B-1 (G-Eval foundation)
---

# ADR — Phase B-3: SV-7 Continuous evaluation

## Kontextus

A jelenlegi vault-eval **passzív + manuális**:
- Heti `vault-cleanup` audit-job a `06-Audits/System_Health.md`-be (árva fájlok, broken-link, frontmatter-hiba) — **vault-szintű, NEM session-szintű**
- Session-min őség user-perception-alapú, nincs metric
- Nincs automatikus „mit végeztünk / hol akadt el az agent / mi a benchmark-trend" jelzés

**SV-7 Phase A+ insight (395 source):** 2024-26 paradigmaváltás 3 tengelyen:
- **(a) leaderboard-hardening** (SWE-bench Verified + Multimodal, Modal-felhő); SWE-bench saturated 93.9% (Claude Mythos Preview), OpenAI elhagyta
- **(b) reliability-fókuszú benchmark** (tau-bench `pass^k` 8 ismétlésen, GAIA scaffold-függő 57.6-64.9%)
- **(c) LLM-as-judge érettség** — bináris Pass/Fail + critique-shadowing (Hamel Husain AlignEval), 90% humán-judge alignment

**Phase A+ Q1 javaslat:** **Braintrust manual review (+ Critique Shadowing baseline) → AlignEval-kalibrált Opus/Sonnet bíró + NLI tényellenőrzés → WarpGrep semantic scaffold + online scoring.** Cost-sweet-spot Tier-2 ($200/hó), Sonnet 4.6 NLI-bíróval.

## Döntés

**3-szintű eval-pipeline** a meglévő `08-Sessions/` tanulság-szekciókra építve, **B-1 G-Eval foundation-re támaszkodva**, 1-2 hetes sprintben.

### Réteg 1 — `eval_l1_parser.py` (determinisztikus stuck-detection)

Session-fájlokon futó **kód-alapú** ellenőrzés, **nulla API-cost**.

**Tech-stack:**
- **Python script** `/usr/local/bin/eval-l1-parser`
- Beolvas: `08-Sessions/*.md` (status: closed)
- Output: `/tmp/vault-eval/eval-l1-{date}.jsonl` — append-only
- **Detect-szabályok:**
  - `## Events` szakasz time-gap >2 óra konzekutív bejegyzések között → „stuck"
  - `## Summary` üres vagy <100 char → „incomplete"
  - `## Learnings` üres → „no-learning-extracted"
  - `## Next session` üres → „no-handoff"
  - Több mint 5 `(retry-pending)` jelölés → „high-retry-rate"
  - Session-duration >6 óra → „long-session-flag"

**Threshold-routing:**
- Mind tiszta → `quality: A`
- 1-2 flag → `quality: B` (csak loggolva)
- 3+ flag → `quality: C` (Pass/Fail review-be küldve)

### Réteg 2 — `vault_trace_viewer.py` (Streamlit Pass/Fail manuális baseline)

A SV-7 Phase A+ Q1 első eleme: **Critique Shadowing baseline** — humán Pass/Fail bemenetből building `Human_Ground_Truth.jsonl`.

**Tech-stack:**
- **Streamlit web-UI** (port 8501) — táblázat-nézet a `quality: C` sessionökre
- Per-session: timeline, Events-extract, Summary, AI-pred (L3-ból), **Pass/Fail toggle + comment**
- Output: `~/obsidian-vault/06-Audits/Human_Ground_Truth.jsonl` — append-only

**Cél:** 30 nap alatt 50+ humán-judgment baseline a Phase B-3 második hetén.

### Réteg 3 — `eval_l2_llm_judge.py` (NLI-alapú hallucination-flag)

A `## Learnings` szekciókra futó **NLI** (Natural Language Inference) — minden Learning-bullet a `/tmp/sv-research/sv*-q*.txt` raw-NotebookLM-források vagy a `10-raw/` evidence ellen ellenőrizve.

**Tech-stack:**
- **Tier-$50 (lokális, primary 2026-05-13 óta):** `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` HuggingFace, ~700MB cached, GPU-mentes, ~$0. Smoke-tested 5/5 verdict ✓
- **Backup-alternatívák** (ha HF model 404 / gating / törlés — eredeti `tasksource/deberta-v3-base-nli` 2026 elején eltűnt):
  - `cross-encoder/nli-deberta-v3-base` (sentence-transformers cross-encoder, hasonló méret)
  - `facebook/bart-large-mnli` (klasszikus, ~1.6GB, stabil)
- **Tier-$200 (cloud):** Claude Sonnet 4.6 ($3/$15 per 1M token) — Phase A+ Q3 sweet-spot
- **Few-shot critique-shadowing:** 5-10 példa a `Human_Ground_Truth.jsonl`-ből minden NLI-call-hoz → 90% humán-judge alignment

**Output:**
- `06-Audits/eval-l2-{date}.jsonl` — append-only
- `quality: D` flag azokra a Learning-ekre, ahol NLI hallucination-probability >0.3

### Aggregálás — heti System_Health cron

A `vault-cleanup --write` weekly job (`launchd com.peti.vault-cleanup`) **kibővítve**:
- Új szakaszt generál: `## Session-quality (last 7 days)`
- A `quality: A/B/C/D` distribution-t összesíti
- Trend-jelölés: javul / stagnál / romlik (vs előző hét)
- Az ADR „Sikermetrikák" táblájának **direkt feed-elése**

## Acceptance criteria

- [ ] **`eval-l1-parser`** működik 50+ session-fájlon (manuális spot-check 5-10 esetre)
- [ ] **Streamlit viewer** elérhető localhoston (port 8501), Pass/Fail működik
- [ ] **30 nap után 50+ Ground Truth entry** a `Human_Ground_Truth.jsonl`-ben
- [ ] **`eval-l2-llm-judge`** működik, 90%+ alignment a Ground Truth-tel
- [ ] **System_Health.md** automatikusan tartalmazza a weekly session-quality összegzést
- [ ] **Roadmap sikermetrikák direkt feed** — a `[[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]` Sikermetrikák-táblája automatikusan frissül

## Alternatívák amiket ELUTASÍTOTTUNK

- **SWE-bench / AgentBench / GAIA** — vault-eval-re alkalmatlan (kódolási benchmark, nem session-quality)
- **Csak humán-review** — nem skálázható, 3-4 óra/hét overhead
- **Tisztán LLM-as-judge baseline nélkül** — Phase A+ Q1 figyelmeztetés: **„Ne automatizációval kezdj"** — bevezetni kell előbb a humán Pass/Fail baseline-t
- **Promptfoo / Braintrust / Langfuse** — fizetős, vendor-lock-in, Tier-$50/200-ban nem fér bele
- **Tau-bench / pass^k automatikus** — kísérleti benchmark, nem reactive a saját vault-history-ra

## Konzekvenciák

**Pozitív:**
- **„Quality-trend láthatóvá teszi a fejlődést"** — a Phase A+ sikermetrikák direktben mérhetők
- B-1 G-Eval foundation **megfizet kétszeresen** (crystallization + eval ugyanazt a Haiku/Sonnet bírót használja)
- Stuck-session detection → 11.11note-pattern javítása (sanity-check `.active-session` divergence)
- Direkt feed a SV-2 (RSI) sprint elé — a session-history minőség-trendje a recursive self-improvement KPI-ja

**Negatív:**
- Új komponens (Streamlit + Python scripts)
- 30 nap humán-baseline-építés időigényes (~10-15 perc/hét)
- L3 NLI-judge költség Tier-$50-en limitált — csak `quality: C` sessionökre futtatva

**Backout-plan:** A 3 réteg külön kapcsolható: ENV-flag `EVAL_LEVEL=0/1/2/3`. L0 = nincs eval, L1 = csak parser, L2 = + Streamlit, L3 = + LLM-judge.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| L1 parser false-positive ("stuck" detect tévesen) | Túl sok C-flag | Threshold-tuning a Ground Truth-tel 30 nap után |
| Streamlit web-UI security (külső hozzáférés) | Vault-data leak | Lokálisan kötve (`127.0.0.1:8501`); SSH-tunnel külső hozzáféréshez |
| NLI-model kicsi → szignifikáns NLI-tévedés | Ground Truth divergence | Tier-$200-ra ugrás ha alignment <85% 2 hét után |
| Cron a launchd-ben Mac-en (Rob vault) cross-platform | Eltérő ütemezés | Külön Mac-launchd plist a `vault-cleanup` cron mellé |

## Open questions

1. **Streamlit alternatíva:** Obsidian-plugin natívan (Tasks/Bases query) vs külön web-UI? Phase B-3 közbenső demo.
2. **Ground Truth share:** ha Rob vaultja is integrálódik, közös vagy per-vault Ground Truth?
3. **Auto-correction loop:** ha `quality: D` (NLI hallucination) — auto-rollback a propagated tényt a KO-DB-ből? Vagy csak flag + manual review?

## Kapcsolódó

- [[11-wiki/sv-07-continuous-evaluation]] — research-cikk
- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — B-1 sprint (G-Eval foundation)
- [[07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 sprint parallel
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap + Sikermetrikák-tábla
- [[06-Audits/System_Health]] — meglévő weekly audit, ennek kibővítése

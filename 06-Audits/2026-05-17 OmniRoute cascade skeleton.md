---
name: OmniRoute cascade skeleton
type: audit
created: 2026-05-17
updated: 2026-05-19
status: skeleton-week-1-alpha
tags: ["#type/audit"]
tag_backfill: 2026-05-19
---
# OmniRoute model-cascade routing skeleton (B-3 + B-6 cross-cut)

> [!info] Status
> **SKELETON Week 1-α** — opt-in (`VAULT_ROUTE_ENABLED=1`), default OFF.
> NEM tör meg meglévő scripteket (`11.11crystallize`, `vault-coherence-check`, `eval-l2-nli-judge` érintetlen).
> Forrás-research: [[08-Sessions/2026-05-17-obsidian-vault-2]] NotebookLM-mining (OmniRoute NeurIPS 2024, 40-60% cost-savings ígéret).

## Architektúra

Háromszintű cascade-router minden modell-igényes task-ra:

| Szint     | Eszközök                                          | Latency        | Cost      |
|-----------|---------------------------------------------------|----------------|-----------|
| `fast`    | rule-based / regex / lokál Python heuristic        | ~1-10 ms       | $0        |
| `balanced`| bge-m3 cosine / NLI / extractive-tfidf             | ~100-500 ms    | $0        |
| `deep`    | claude-code subagent / Anthropic API / fanout-G-Eval | ~5-30 s        | ~$0.01-0.05 |

**Auto-mode escalation:**
- start: `fast`
- if `confidence < fast_to_balanced` (default 0.70) → escalate `balanced`
- if `confidence < balanced_to_deep` (default 0.80) → escalate `deep`
- `deep` mindig autoritatív (no further escalation)

## Konfiguráció

`~/.vault-config/route-cascade.yaml` — 5 task × 3 level cascade-tábla:

| Task        | fast                          | balanced                                | deep                              |
|-------------|-------------------------------|-----------------------------------------|-----------------------------------|
| `eval`      | `eval-l1-parser.py`           | `eval-l2-nli-judge --confidence-only`   | `11.11crystallize --scorer claude-code` |
| `score`     | rule-based-conf-heuristic     | `eval-l2-nli-judge`                     | claude-code-fanout-G-Eval         |
| `classify`  | regex-keyword-classifier      | `vault-search --mode cosine --top-k 5`  | claude-code-classify              |
| `extract`   | regex-entity-extractor        | `vault-graph-mentions-extract --stdin`  | `vault-ko-ingest --stdin`         |
| `summarize` | first-n-sentences             | extractive-tfidf-summary                | claude-code-summarize             |

**Threshold-config (a YAML `defaults.confidence_threshold`):**
- `fast_to_balanced: 0.70`
- `balanced_to_deep: 0.80`

Audit-log: `~/.vault-config/route-log.jsonl` (JSONL, minden invocation).

## 10-sample smoke-test eredmények

`VAULT_ROUTE_ENABLED=1 vault-route --smoke-test`

| Mód             | Total cost | Avg cost | Avg conf | Notes                                       |
|-----------------|------------|----------|----------|---------------------------------------------|
| `fast_only`     | $0.0000    | $0.0000  | 0.545    | Vegyes minőség, sok bizonytalan output      |
| `balanced_only` | $0.0000    | $0.0000  | 0.71     | Lokál model, ingyen, közepes-magas conf     |
| `deep_only`     | $0.2200    | $0.0220  | 0.85     | Mindig deep, max conf, max cost             |
| `auto`          | $0.1400    | $0.0140  | 0.85     | **36.4% cost-savings** vs deep-only        |

**Auto-mode escalation-distribution (10 sample):**
- fast-szinten megáll: **4/10** (40%)
- deep-szintig escalated: **6/10** (60%)
- balanced-szinten megáll: 0/10 (a skeleton balanced-handler-ek mind 0.7 ± körüli conf-ot adnak — a 0.80 threshold éppen fölött van)

**Cost-savings:** **36.4%** — célzott 40-60% **alsó tartományában**. Várható növekedés Week 2-ben, amikor:
- real balanced-handler-ek (NLI / cosine) implementálva → több task balanced-szinten lezárul
- threshold-kalibráció valós workload-on (jelenleg 0.70 / 0.80 szándékosan konzervatív)
- `summarize` és `eval` deep-handler-ek inline-implementáció (most external skeleton-skip-en mennek át)

## Operation modes

```bash
# DEFAULT: opt-out, dry-run mock
vault-route --task score --input "..." --quality auto

# Real cascade (inline-handler-ekkel)
VAULT_ROUTE_ENABLED=1 vault-route --task score --input "..." --quality auto

# JSON-output minden szint trace-szel
VAULT_ROUTE_ENABLED=1 vault-route --task classify --input "..." --json

# Smoke-test
VAULT_ROUTE_ENABLED=1 vault-route --smoke-test [--json]

# stdin-input
echo "text" | VAULT_ROUTE_ENABLED=1 vault-route --task summarize
```

## Komponensek

| Path                                            | Méret  | Funkció                                  |
|-------------------------------------------------|--------|------------------------------------------|
| `/usr/local/bin/vault-route`                    | ~12 KB | Python no-deps router + inline-handler-ek |
| `~/.vault-config/route-cascade.yaml`            | ~2 KB  | 5-task × 3-level cascade-tábla            |
| `~/.vault-config/route-log.jsonl`               | auto   | Audit-log (per-invocation JSONL)          |

### Inline-handler-ek (no-deps fast/balanced/deep simulation)

| Handler                          | Logic                                              |
|----------------------------------|----------------------------------------------------|
| `rule-based-conf-heuristic`      | regex: must/kell/[[..]] → +conf; talán/maybe → -conf |
| `regex-keyword-classifier`       | projekt-tábla (kgc/teszt-eu/mfl/vault/foxxi)        |
| `regex-entity-extractor`         | wikilink + capitalized-token harvest                |
| `first-n-sentences`              | első N mondat sentence-split                        |
| `extractive-tfidf-summary`       | leghosszabb mondat (proxy informativeness)          |
| `claude-code-fanout-G-Eval`      | placeholder — mock 0.95 (REAL = Task() subagent)    |
| `claude-code-classify/summarize` | placeholder — mock 0.95                             |

External binary-cmd-ek (`eval-l2-nli-judge`, `vault-search`, `vault-ko-ingest` stb.) a skeleton-ban **nem invokáltak** — csak `exists()`-ellenőrzés, 0.7 mock-conf return-nel.

## Korlátok / known issues

1. **Skeleton-skip**: `eval/summarize` deep-szint és összes `balanced` external binary-cmd nincs ténylegesen invokálva — Week 2 feladat
2. **Latency=0**: inline-handler-ek annyira gyorsak hogy `time.perf_counter()` ms-resolution-en 0-t ad — Week 2-ben mikrosec-mérés
3. **Threshold-kalibráció**: 0.70/0.80 értékek tapasztalat-alapúak, nem mértek — valós workload után újra
4. **No streaming**: a router szinkron — Week 3+ ha async-fanout kell
5. **YAML-parser mini**: indent-based, csak a route-cascade.yaml struktúrát kezeli, **NEM general-purpose**

## Week 2 follow-up

- [ ] Integráció `11.11crystallize`-be mint **Layer 0 cascade** (a meglévő `--scorer` argumentum elé) — opt-in flag-gel
- [ ] Real subprocess-invocation a `balanced` external cmd-ekre (`vault-search`, `eval-l2-nli-judge`, `vault-graph-mentions-extract`)
- [ ] Streamlit trace-viewer (`/usr/local/bin/vault-route-traceviewer`) — `route-log.jsonl`-ből történeti escalation-statisztika + cost-trend
- [ ] Threshold-kalibráció 100-sample real workload-on, dinamikus `~/.vault-config/route-thresholds.yaml`
- [ ] Cost-savings target ramp: 36% (Week 1) → 50% (Week 2 valós balanced) → 60% (Week 3 threshold-kalibráció)

## Kapcsolódó

- [[02-Projects/superintelligent-vault]] — SV roadmap, B-3 + B-6 axes
- [[11-wiki/sv-07-continuous-evaluation]] — NLI-judge háttér
- [[06-Audits/2026-05-17 B-1 G-Eval bias-mitigation v0.3]] — G-Eval scorer Week 1 work
- [[06-Audits/2026-05-17 B-3 Week 2 L2 NLI-judge]] — NLI-judge state
- [[11-wiki/claude-code-subagent-fanout]] — deep-szint dispatch-pattern
- [[08-Sessions/2026-05-17-obsidian-vault-2]] — research-mining session (OmniRoute origin)

## Próbafutás-bizonyíték (audit-log entry)

```json
{"action": "smoke_test", "enabled": true, "dry_run": false,
 "summary": {
   "fast_only":     {"n": 10, "total_cost_usd": 0.0,  "avg_conf": 0.545},
   "balanced_only": {"n": 10, "total_cost_usd": 0.0,  "avg_conf": 0.71},
   "deep_only":     {"n": 10, "total_cost_usd": 0.22, "avg_conf": 0.85},
   "auto":          {"n": 10, "total_cost_usd": 0.14, "avg_conf": 0.85},
   "cost_savings_pct_auto_vs_deep": 36.4
 }}
```

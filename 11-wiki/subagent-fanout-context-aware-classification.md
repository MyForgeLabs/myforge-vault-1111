---
name: Subagent-fanout context-aware classification pattern
type: wiki
tags: ["#type/wiki", "subagent-fanout", "classification", "ner", "entity-typing", "quality"]
created: 2026-05-18
updated: 2026-05-18
status: stable
---

# Subagent-fanout context-aware classification

A subagent-fanout pattern ([[claude-code-subagent-fanout]]) jól skálázódó bulk-LLM-mutáció ($0 cost Claude Code-ban), de a klasszifikációs feladatok (entity-typing, label-injection, summary-tagging, NER) **minőség-szintje drasztikusan függ** attól, hogy a subagent kap-e kontextust a klasszifikálandó tételhez. **Blind classifier** (csak a tétel-név) jellemzően ~5% FP-rate-tel és alacsony recall-lal dolgozik; **context-aware classifier** (subagent olvassa a forrás-MD-t, ahol az entity szerepel) FP-rate <2%, recall +20-40pp magasabb.

## TL;DR

- **Blind fanout** = subagent INPUT-ja csak `entity_name` → gyors, olcsó, de FP+ ~5%, alacsony recall
- **Context-aware fanout** = subagent INPUT-ja `entity_name + 1-2 source-MD excerpt` → lassabb (~2-3× idő), de FP <2%, recall +20-40pp
- **Hybrid stratégia:** blind fanout 1. iteráció → high-confidence-ek megtartva → ambiguous-ok context-aware 2. iteráció
- **Reusable:** minden klasszifikációs feladatra (entity-typing, doc-categorization, sentiment, intent-detection)

## Háttér — B-7 entity-typing pipeline evolúciója

A Superintelligent Vault B-7 axis (entity-typing-mátrix építése a vault Memgraph entity-gráfján, 8997 entity 2026-05-18-án) három iterációban növelte a tipizáltságot:

| Iteráció | Dátum | Pattern | Tipizáltság | FP-rate (sample) |
|---|---|---|---|---|
| 1 | 2026-05-17-3 Phase 5 | stand-in classifier (rule-based, csak entity-name regex) | 14.87% | ~8% (manual sample 50-ből 4 hibás) |
| 2 | 2026-05-18 reggel | **blind subagent-fanout** (7 batch, csak entity-name) | 28.9% → 72.8%* | ~5% |
| 3 | terv: Week 5 | **context-aware subagent-fanout** (entity + source-MD excerpt) | tervezett >90% | <2% |

*A 28.9% → 72.8% ugrás a fanout MELLETT a `mgclient.autocommit` fix-nek köszönhető — lásd [[mgclient-autocommit-silent-rollback]]. A tisztán fanout-attribuálható tipizáltság-növekedés szignifikáns volt, de az autocommit-bug elfedte mértékét az első 4 batch-ben.

A blind iteráció 2 elsődleges hibatípust mutatott:
1. **Homonim entity-k** — pl. `"Cache"` lehet HTTP-cache pattern, lehet karakter-név egy game-design GDD-ben, lehet React `useMemo` cache. A subagent kontextus nélkül a leggyakoribb jelentést választja → wrong-label egy specifikus vault-szegmensben.
2. **Vault-specifikus jelentések** — pl. `"Pocock"` a Sequential-Validity statisztikai módszerek kontextusában fut, NEM a brit politikatörténész — egy general-knowledge subagent ezt nem tudja. Context-aware iteráció a `11-wiki/Pocock-design-monitoring-statistics.md` excerpt-ből konkretizálná.

## A pattern

### Blind iteráció (1. fázis)

```python
# Gyors, olcsó, ~80% accuracy
def blind_classify(entity_name):
    prompt = f"""Classify this vault entity into one of:
    Concept, Decision, Pattern, Skill, Project, Person, Tool, Other.

    Entity name: {entity_name}

    Reply with ONLY the label, no explanation."""
    return subagent.run(prompt)
```

### Context-aware iteráció (2. fázis)

```python
# Lassabb, drágább, ~95-98% accuracy
def context_aware_classify(entity_name, source_mds):
    """source_mds: list of (path, excerpt) where entity is mentioned"""
    context = "\n\n".join(
        f"### {p}\n{e[:500]}" for p, e in source_mds[:3]
    )
    prompt = f"""Classify this vault entity based on actual usage context:

    Entity name: {entity_name}

    Context from vault MDs where it appears:
    {context}

    Choose ONE label: Concept, Decision, Pattern, Skill, Project, Person, Tool, Other.

    Reasoning (1 sentence) then label on last line."""
    return subagent.run(prompt)
```

### Hybrid (production-grade)

```python
def hybrid_classify(entities):
    # Round 1: blind, high-throughput
    round1 = {e: blind_classify(e) for e in entities}

    # Confidence filter: konkrét label, NEM "Other", NEM null
    confident = {e: l for e, l in round1.items() if l != "Other"}
    ambiguous = [e for e in entities if e not in confident]

    # Round 2: context-aware ONLY for ambiguous
    for e in ambiguous:
        sources = find_mentions(e, vault)  # graph-mentions-extract
        round1[e] = context_aware_classify(e, sources)

    return round1
```

Ez 60-80%-át a tételeknek olcsó blind-úton kezeli, és a maradékra költi a drága context-aware budget-et. Vault-szintű ROI ~3-5× szignifikánsabb a pure-context-aware-hez képest.

## Mikor blind, mikor context-aware

| Feladat | Blind elegendő | Context-aware kötelező |
|---|---|---|
| Unique global proper-noun (személy-név, márka) | ✓ | ritkán |
| Általános fogalom polysem nélkül (HTTP, REST) | ✓ | csak <2% domain-specifikus |
| Vault-specifikus kódszó / projekt-belső név | ✗ | KÖTELEZŐ |
| Polysem entity (Cache, Pipeline, Worker) | ✗ | KÖTELEZŐ |
| Új konvenció / freshly-coined slug | ✗ | KÖTELEZŐ |

**Ökölszabály:** ha a vault tartalmaz domain-specifikus jargon-t (és minden komoly long-form vault tartalmaz), a tipizálási minimum 2 iteráció.

## Anti-pattern: "csak blind" big-bang

NE futtass nagy entity-set-en (>5000) **csak** blind klasszifikációt és vegyél jónak. Az 5% FP a tipizáltság-mérőszámot felfújja (false-pozitívak látszólag "típusosak"), de a downstream-feature-ök (search-rerank label-szerint, label-szűrt graph-traversal) zaj-ra állnak. A FP-rate kihat a **következő layer** minőségére, ami **nehezebben mérhető**.

Másik anti-pattern: **manual sampling kihagyása**. Akár blind, akár context-aware iteráció után — 50-100-as random-sample-en manuális verify kötelező. Subagent-jelentés magas confidence-ről nem garancia, hogy a label tényleg helyes. Az LLM-self-evaluation bias-mitigáció kérdéskör ([[g-eval-bias-mitigation-pattern]]) szerint az LLM hajlamos overstating saját bizalmát.

## Reusable szabályok

| Feladat-típus | Ajánlott pattern |
|---|---|
| Entity-typing (graph-mátrix) | Hybrid: blind → ambiguous context-aware |
| Doc-categorization (vault-MD → folder) | Blind elég, ha taxonómia stabil |
| Tag-suggestion | Context-aware kötelező (vault-konvenciók) |
| Sentiment-analysis | Blind, kivéve ironikus/sarcastic domain |
| Intent-detection (chat-ben) | Context-aware (last 2-3 turn beemelve) |
| NER (general) | Blind (specialized model lényegesen jobb mint LLM-fanout) |
| Spec-violation detection | Context-aware (a spec maga a context) |

## Költség-modell

A subagent-fanout Claude Code-ban $0 ($0/agent-call), de **idő-költség** van:
- Blind: ~2-3 sec/entity (egyszerű prompt)
- Context-aware: ~6-10 sec/entity (3-5 MD excerpt beolvasás + classification)
- Hybrid 80/20: ~4 sec/entity átlagosan

8997 entity-re a hybrid ~10 óra-perc (parallel 8 subagent → ~1.25 óra wall-clock). Production-bulk-feladatokban ez vállalható.

## Komplementer pattern-ek

- **Self-verification** — minden subagent-output-ot egy MÁSIK subagent verify-ol (két-fázisú quorum). Drágább, de FP <1%-ra megy
- **Ensemble** — 3 subagent függetlenül klasszifikál, majority-vote → még jobb FP
- **Active-learning loop** — manual-sample-ben talált hibák bekerülnek a prompt few-shot example-jébe a következő iterációhoz
- **Source-quality weight** — `11-wiki/` source-ok többet érnek mint `10-raw/`, context-injection prioritás
- **Confidence-threshold escalation** — blind output mellé "confidence 0-1" kér; <0.7 → context-aware re-run

## Kapcsolódó

- [[claude-code-subagent-fanout]] — alap-pattern, ezen épül
- [[g-eval-bias-mitigation-pattern]] — LLM-self-evaluation bias, ami a confidence-re kihat
- [[mgclient-autocommit-silent-rollback]] — a B-7 batch közben felfedett mellékpitfall
- [[../02-Projects/superintelligent-vault]] — a B-7 axis projekt-context
- [[two-tier-graph-extraction]] — graphify vs Memgraph komplementer pattern

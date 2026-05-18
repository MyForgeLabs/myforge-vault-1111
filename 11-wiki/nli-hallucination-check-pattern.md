---
name: nli-hallucination-check-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/eval", "#topic/llm-as-judge", "#topic/hallucination", "#topic/rag"]
---

# NLI-alapú hallucination check (Learnings ↔ session-trace)

## TL;DR

A **Natural Language Inference (NLI)** mint külön réteg az LLM-as-judge-pipeline-ban: a generált összefoglaló / Learnings / answer (hipotézis) tényszerű konzisztenciáját ellenőrzi a forrás-trace (premissza) ellen. Olcsó (nano-modell + classifier-fej), determinisztikus output (`entailment | neutral | contradiction`), magas precision a finom inkonzisztenciára, ahol a sima G-Eval rubric hangulat-érzéketlen.

## Háttér (3+ source-evidence)

- [[sv-07-continuous-evaluation]] — "NLI-alapú judge összeveti a Learnings-t a nyers trace-szel" — a Vault session-eval L2.5 rétegként implementálva 2026-05-17 super-session során
- [[sv-05-crystallization-automation]] — "cross-wiki match validation" mint NLI-alapú anti-hallucinationgate a propagated bullet és wiki-tartalom között
- [[sv-08-notebooklm-cognitive-layer]] — Eugene Yan AlignEval és „Task-Specific LLM Evals" alapján az NLI a hallucination-mérés státusza 2026 H1-re
- [[g-eval-bias-mitigation-pattern]] — NLI mint ortogonális ellenőrző-réteg a G-Eval self-favoritism torzítása mellett, 30-sample paired kalibráción mérve

## Mintázat

Az NLI 3 osztályos klasszifikáció (entailment / neutral / contradiction), nem-generatív (logits, NEM szabad-szöveg), így 10-100× olcsóbb LLM-judge-nál és reprodukálható. A vault pipeline ezt használja a `## Learnings` szekciókra: minden bullet → "hipotézis", a session-trace egy ablaka → "premissza", NLI-modell visszaadja a 3 osztály valószínűségét. Ha P(contradiction) > P(entailment), a bullet "hallucinált" flag-et kap.

Architektúrális szempontból az NLI **second-pass-szűrő** egy generatív judge után (NEM helyette): a G-Eval/LLM-judge nyitja az osztályozást (releváns? értékes?), az NLI lezárja a tényszerűségi gate-et. Ez a "cascading eval" minta (lásd [[layered-eval-cascading-pattern]]) — a drága réteg csak akkor fut, ha az olcsó NLI nem zárta ki.

Kódra: `microsoft/deberta-v3-large-mnli` vagy `cross-encoder/nli-deberta-v3-base` — CPU-on 50-200ms/pair, GPU-n alig mérhető. A vault L2.5-implementáció `eval-l2-nli-judge` script-tel megy, batch-job.

## Anti-pattern

- **NLI-t generatív LLM-mel helyettesíteni "Pass/Fail?" prompt-tal.** A latency 100×, ár 1000×, és a generatív bias visszahozza, amit pont el akarsz kerülni.
- **Csak NLI-t használni, generatív judge nélkül.** Az NLI nem méri a relevanciát, csak a tényszerűséget — egy true-but-irrelevant Learnings entailment-et kap, de hasznos akkor sem.
- **Hosszú premisszán NLI-t futtatni.** A 512-token cap-en túl a deberta-MNLI degradálódik — premissza-ablakot kell sliding-window-zal építeni, vagy bge-m3 retrieve-val csak a leg-releváns 3 chunk-ot betölteni.
- **Cross-encoder NLI-t bi-encoder embedding-eknek hívni.** Más technika, más felhasználás — a bi-encoder csak hasonlóság, NEM logikai következtetés.

## Reusable szabályok

1. **NLI csak hallucination-gate-re**, NEM tartalom-értékelésre. A „releváns-e ez a Learnings?" kérdés generatív judge / human dolga.
2. **Cascading**: olcsó NLI első, drága LLM-judge csak a megengedettekre fut. 2026-05-17-3 mérés: 53-80% bullet-szűrés NLI-vel, drága judge-cost arányosan csökken.
3. **Hipotézis = max 256 token**, premissza = sliding-window 512-token chunk. Hosszabb hipotézis (>1 bullet egyben) accuracy-veszteség.
4. **Threshold per-target**: 11-wiki bullet stricter (P(contradiction) > 0.40), session-jegyzet lazább (>0.55). YAML config, hot-reload-olható.
5. **Per-target threshold-mérés**: 30-100 sample paired kalibráció kötelező, "globális 0.50" mindenhol = false-negative cascade.
6. **NLI input completeness trap kerülése**: a premissza tartalmazza a teljes evidence-blokkot, NEM csak az azonnal-megfelelő mondatot — ld. [[nli-eval-input-completeness-trap]].

## Buktatók

- **Nyelv-mismatch**: angol-trained NLI magyar bullet-ekre — accuracy zuhan. Megoldás: multilingual NLI (XLM-R-MNLI) vagy LLM-fordítás premissza-szinten.
- **Negation-flip**: deberta-MNLI érzékeny a "nem"-re — ha a generatív judge átírta a Learnings-et "X nem stabil"-ról "X stabil"-ra, az NLI catch-eli, **de** csak ha a premissza-chunk tartalmazza a negált változatot.
- **Empty-premissza**: ha a retrieve nem talál releváns chunk-ot, NEM neutral-t kell visszaadni, hanem "no-evidence" flaget — különben a hipotézis "passol" minden ellenőrzést.
- **Domain-shift**: orvosi vagy jogi domain-en a deberta-MNLI accuracy ~10-20pp-vel rosszabb, mint általános news-szövegen. Domain-fine-tuning vagy specifikus modell (BioBERT-MNLI) ajánlott.
- **Multi-claim-bullet csapda**: egy bullet több állítást tartalmaz ("X stabil ÉS Y javul") — NLI-modell az egészet entailment-ezi vagy contradiction-ölőzi, NEM finomítva. Atomic-claim-bontás előfeldolgozás kötelező.
- **Smart-threshold over-tuning**: a per-target P(contradiction) küszöböt N=30 sample-en kalibrálni rosszul fog scaling-elni. Validate-set N≥100, és heti drift-monitoring kötelező.

## Mikor használd / mikor NE

| Use-case | NLI ajánlott? | Miért |
|---|---|---|
| Session Learnings → wiki propagáció | IGEN | Bullet-szintű tényszerű inkonzisztencia gate |
| Search-result relevancia ranking | NEM | Reranker / cross-encoder bi-encoder jobb (semantic-hasonlóság, NEM logikai) |
| RAG-grounded answer audit | IGEN | A generált válasz tényileg a retrieved-context-ből jön-e |
| Hosszú dokumentum összegzés-audit | RÉSZBEN | Sliding-window kell, és multi-claim-bontás |
| Subjektív / kreatív output (story, design) | NEM | Az NLI a tényszerűségre gyúr, nem értékel kreatív minőséget |

## Kapcsolódó

- [[layered-eval-cascading-pattern]] — NLI mint L2.5 olcsó-réteg
- [[g-eval-bias-mitigation-pattern]] — komplementer eval-szigorítás
- [[nli-eval-input-completeness-trap]] — premissza-építés gotcha
- [[sv-07-continuous-evaluation]] — teljes eval-architektúra
- [[reranker-cost-optimization-not-size]] — hasonló cost-arch (olcsó-első, drága-csak-ha-kell)
- [[auto-propagation-confidence-gate]] — NLI-output mint propagáció-input

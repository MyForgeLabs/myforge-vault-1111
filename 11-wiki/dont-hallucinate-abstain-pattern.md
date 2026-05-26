---
name: dont-hallucinate-abstain-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/rag", "#topic/hallucination", "#topic/eval", "#topic/multi-llm"]
---

# „Don't Hallucinate, Abstain" — Multi-LLM Collaboration abstain-pattern

## TL;DR

A „Don't Hallucinate, Abstain" pattern (`arXiv:2402.00367`) **multi-LLM cooperative-vs-competitive framework**: ha egy egyetlen modell nem tudja a választ, a hagyományos megoldás konfabulál; ez a pattern explicit „**knowledge gap**" detection-t épít: 2-3 modell egymás válaszait keresztezi, és ha **nem egyezik**, az aggregátor inkább `ABSTAIN`-t ad vissza, NEM kompromisszum-választ. ~19.3% javulás az abstain-pontosságban a baseline-hoz képest.

## Háttér (3+ source-evidence)

- [[sv-08-notebooklm-cognitive-layer]] — "„Don't Hallucinate, Abstain" (arXiv:2402.00367) Multi-LLM Collaboration framework a NotebookLM synthesis-minőségének auditálására (~19,3% javulás abstain-pontosságban)"
- [[sv-08-notebooklm-cognitive-layer]] — "Synthesis-minőség evaluation — kooperatív/kompetitív „knowledge gap" tesztelés"
- [[superintelligent-vault-research]] — multi-LLM consensus-pattern mint NotebookLM eval-réteg
- [[sv-07-continuous-evaluation]] — abstain-stratégia az LLM-judge bias-ai mellett

## Mintázat

3 fő ötlet kombinációja:

1. **Multi-model query**: ugyanaz a kérdés 2-3 különböző modell-családra (Claude + GPT + Gemini, NEM 3× ugyanaz). Ez biztosítja, hogy a self-favoritism torzítás ne dominálja.
2. **Cooperative-vs-Competitive judging**: a modellek vagy egyetértésre törekszenek (cooperative — átlagolás, RAG-fúzió), vagy egymást kritizálják (competitive — debate). A pattern azt mutatja: ha **competitive módban** a 3 modell <2/3 többségben egyezik, valószínűleg knowledge-gap van, és érdemes abstain-elni.
3. **Explicit ABSTAIN-token**: a meta-aggregátor output-schema-jában `ABSTAIN | LOW_CONFIDENCE | ANSWER` 3-state, NEM csak `ANSWER | ERROR`. A user UI meg tudja jeleníteni, hogy a rendszer **tudja, hogy nem tudja**.

A vault-kontextusban ez a NotebookLM synthesis-output auditjához használható: 8 párhuzamos subagent ([[claude-code-subagent-fanout]]) ugyanazt a research-kérdést kapja, és ha 6/8 nem konvergál, az output `ABSTAIN_WITH_DISAGREEMENT`-et kap, **nem** force-pick-et.

## Anti-pattern

- **2 modell consensus = igazság**: 2-ből 2 egyezés nem statisztika. Min. 3 modell, lehetőleg eltérő családból.
- **ABSTAIN-ot hibaként logolni**: ha az ABSTAIN drága incidensként megy a metric-dashboard-ra, az operator nyomást érez, hogy "kapcsolja le" a feature-t. Az ABSTAIN **siker**, ha a tényleges hallucination-elkerülésért jött.
- **Cooperative-only (consensus-átlag) production-re**: az átlagolás eltünteti a discrepancy-jelet, és a hibás konfidencia-érzetet adja. A competitive (vita-stílusú) mód a hallucination-katcher.
- **Self-favoritism kompenzálatlan**: ha mindhárom modell Claude-családból van, a self-favoritism vissza-tér. Eltérő architektúra/training-data kell.

## Reusable szabályok

1. **3+ eltérő-modell-családú judge** (cross-vendor), nem 3× ugyanaz.
2. **Competitive debate-stílus** kötelező a final abstain-döntéshez. Cooperative csak proposal-szinten.
3. **ABSTAIN explicit return-state** a schema-ban (`Answer | Abstain | LowConfidence`).
4. **Disagreement-küszöb**: <66% multi-model egyezés → ABSTAIN. Per-domain hangolható (medical: 90%, casual: 50%).
5. **ABSTAIN-rate monitoring**: ha <2% vagy >25%, valószínűleg a küszöb rosszul van állítva. 5-15% tipikus production-tartomány.
6. **Knowledge-gap reporting**: minden ABSTAIN-hez 1-mondatos rationale ("nem találtam evidence-t X-ről") — ez a debugging-jel.

## Buktatók

- **Cost-explosion**: 3 modell-hívás minden query-re = 3× cost. Csak high-stakes kérdésekre, vagy cached-eval baseline-on.
- **Latency-explosion**: párhuzamosítva is a leglassabb modell dominál; ha 1 modell timeout-ol, az egész abstain-decision blokkol — defensive timeout kell.
- **Self-RAG-zavar**: ha a 3 modell ugyanazt a vektor-retrieve-d-context-et kapja, a context maga lehet hallucinált, és nem segít a multi-model. RAG-szinten is multi-retriever kell, ha komolyan veszed.
- **Tie-break-anomaly**: 1 modell ANSWER + 1 ABSTAIN + 1 LOW_CONFIDENCE = ambivalens. Definiálj előre tie-break-rule-t (pl. „bármilyen ABSTAIN → ABSTAIN" majority-vagy precision-prefer).
- **Cooperative-bias-leak**: ha cooperative-mód közben a 3 modell `share`-eli a köztes válaszait, a 2. modell már anchored az 1.-re. NEM consensus, hanem anchoring. Independent-parallel kötelező a competitive-mode-hoz.

## Mikor használd / mikor NE

| Use-case | „Abstain" érdemes? | Miért |
|---|---|---|
| High-stakes RAG (orvosi, jogi, pénzügyi) | IGEN | A hibás válasz költségesebb, mint az "nem tudom" |
| Casual chatbot UI | RÉSZBEN | A user-experience leromolhat 25% ABSTAIN-rate-en |
| Code-generation | NEM (általában) | A test-suite a jobb gate, nem a confidence-vote |
| Faktoid-question-answer | IGEN | A faktoid jól-definiált, abstain-érték magas |
| Creative-writing | NEM | Nincs „helyes válasz", a vote-disagreement zaj |

## Kapcsolódó

- [[sv-08-notebooklm-cognitive-layer]] — NotebookLM eval-architektúra
- [[g-eval-bias-mitigation-pattern]] — komplementer single-judge bias-szigorítás
- [[nli-hallucination-check-pattern]] — alternatív/komplementer hallucination-gate
- [[claude-code-subagent-fanout]] — multi-agent-implementáció parallel-szintű
- [[sv-07-continuous-evaluation]] — eval-roadmap szélesebb

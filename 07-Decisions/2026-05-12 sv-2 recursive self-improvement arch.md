---
name: SV-2 Recursive self-improvement — Phase B-8 architecture (UTOLSÓ sprint)
type: decision
tags: ["#type/decision", "vault-architecture", "rsi", "self-improvement", "phase-b", "sv-research", "safety-critical"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-02-recursive-self-improvement]]
sprint: B-8 (UTOLSÓ)
priority: P0 (csak a többi STABILIZÁLÓDÁS UTÁN)
estimated_effort: 2-3 hét
depends_on: B-1, B-2, B-3, B-4, B-5, B-6, B-7 (mind a 7 előző sprint stabilan él)
---

# ADR — Phase B-8: SV-2 Recursive self-improvement (UTOLSÓ sprint)

## Kontextus

A Phase A+ research **leghangsúlyosabb biztonsági figyelmeztetése**: az RSI **csak a többi tengely stabilizálódása után** vezethető be — egyébként **felerősíti a hibákat**:
- **76-98% self-correction blind spot** (SV-2 Phase A+) — az LLM elfogadja saját hibás válaszát
- **Reward hacking** (SV-5) — az agent maga-pontozást manipulálja
- **Model collapse** (SV-5 + SV-2) — rekurzív szintetikus adatokon „go MAD" devalváció
- **Lost oversight** (SV-7) — criteria-drift miatt a human-bíró elveszti a kontrollt

**Phase B-1..B-7 stabilizálódott állapota az ELŐFELTÉTEL:**
- **B-1 (Crystallization + G-Eval):** confidence-routing baseline + audit-log
- **B-3 (Eval):** Critique Shadowing baseline + Ground Truth (>= 50 humán-judgment)
- **B-6 (Multi-agent + Critic):** Critic intercepts mutations + Pareto-merge

Csak ezek élesedése UTÁN engedhető meg, hogy az agent **maga írja át a saját AGENTS.md-t, skill-eket, vagy promptokat**.

**SV-2 Phase A+ insight (1009 source):** A 4-dimenziós spektrumon (Prompt evolution / Skill library / Self-reflection / Code self-modification) a **legalsó 3 már „felügyelt" módban biztonságos**, de a **Code self-modification (Gödel Agent monkey-patching) Phase C+ idejére** marad.

## Döntés

**3-rétegű felügyelt RSI** — szigorúan **B-1..B-7 dependency-check** UTÁN, 2-3 hetes sprintben.

### Réteg 1 — Skill Library Growth (Anthropic Agent Skills + SAGE-style auto-distillation)

A meglévő 280 skill **iteratív bővítése** session-traces-ből.

**Tech-stack:**
- **`/11.11stop` poszt-hook:** ha 3+ session-ben azonos pattern (G-Eval-detected), `vault-skill-suggest` script auto-draft új `SKILL.md`-t
- **ReCreate-stílus, NEM ab-initio** (SV-4 Phase A+ Q3 ajánlása): a draft a legközelebbi meglévő skill-template-ből indul, mutáció nem nulláról generálás
- **Critic-jóváhagyás (B-6 reuse):** minden új skill-draft Critic-review-n megy keresztül G-Eval-threshold-routing-gal
- **Pareto-merge (B-1 reuse):** ha két session konvergens, de eltérő minta-elemekkel, system-aware merge

### Réteg 2 — Prompt Evolution (GEPA + DSPy)

A meglévő prompt-template-ek (Orchestrator / Worker / Critic / Summarizer — B-6 sprint output) iteratív finomítása.

**Tech-stack:**
- **GEPA-prompt-mutator cron** (havi 1× első iteráció, majd heti 1× ha stabil)
- **Bemenet:** a `~/obsidian-vault/.workers/<task-id>/events.jsonl` event-log-ja (B-6 Filesystem-as-State)
- **Mutáció-cél:** a 4 prompt-template közül a leggyakrabban hibázó (Eval `quality: C/D` flag) — **NEM mindet egyszerre**
- **Pareto-front fenntartás:** a GEPA NEM 1 „legjobb" prompt-ot tart, hanem 3-5 specialista-változatot (different-task-szerint optimalizált)
- **Length regularization:** „hossz-tudatos" mutátor a prompt-bloat ellen (Phase A+ insight: 4× tömörítés minőségromlás nélkül)

### Réteg 3 — Self-Reflection Loop (Reflexion + ReFlect-Harness deterministic shell)

A `08-Sessions/` Learnings-eit **felhasználja a saját jövőbeli viselkedés finomításához**.

**Tech-stack:**
- **`vault-reflect` cron** (heti 1×, hétfő reggel a podcast-cron mellé)
- Bemenet: az elmúlt 7 nap `08-Sessions/*.md` Learnings-listája
- **ReFlect deterministic harness** (Phase A+ Q1): nem-LLM-alapú validátor (Python shape-checker, format-validator) a Learning-mutációk előtt
- **Verbal memory buffer** (Reflexion-minta): a Learning-szintézis a `05-Memory/Auto-reflections/<date>.md`-be írja
- **Manual promóció:** a `Auto-reflections/` tartalma NEM automatikusan promóciózódik a `05-Memory/` gyökerébe vagy `11-wiki/`-be — **emberi review** szükséges

### NEM RÉSZE Phase B-8-nak (Phase C+ idejére halasztva)

**Code self-modification (Gödel Agent stílus):** Az agent NEM írja át a saját `~/.local/bin/11.11*` scripteket, a `~/.agents/skills/*/SKILL.md`-ket dinamikusan, vagy a `~/.claude/CLAUDE.md`-t — még felügyelt módban sem.

**Indok:**
- A Phase A+ Q2-ben: Gödel Agent **akadémiai stage** (no production deployment)
- A 76-98% self-correction blind spot **eltöri a meta-rendszer** integritását — ha az agent rosszul írja át a saját safety-fékét, nincs visszaút
- A vault git-history biztonsági fékként szolgál, de **race-condition kockázat** ha az agent commit-ot is generál

**Phase C+ feltétel:** B-8 3 hónapos stabil futása + 0 reward-hacking incidens.

## Acceptance criteria

- [ ] **B-1..B-7 dependency-check** — mind a 7 sprint `done` státuszban, audit-log-jaikban <5% incidens-flag
- [ ] **`vault-skill-suggest`** működik — 3 session-aktivitás után auto-draft, Critic-jóváhagyás
- [ ] **GEPA-prompt-mutator** működik — havi cron mutál 1 prompt-templatet, Pareto-front fenntartva
- [ ] **`vault-reflect`** működik — heti `Auto-reflections/<date>.md` generálás
- [ ] **ReFlect deterministic harness** intercept — minden auto-mutation előtt format-check, hibás struktúra → rollback
- [ ] **3 hónap stabil futás** — 0 reward-hacking, <5% manual-revert a propagált skillekre/promptokra
- [ ] **Audit-log review (heti)** — minden auto-mutation timestamp + diff + Critic-confidence-score

## Alternatívák amiket ELUTASÍTOTTUNK

- **Gödel Agent monkey-patching** — Phase A+ Q2: akadémiai stage, no production deployment; reward-hacking-risk
- **Self-Rewarding LLM iteratív DPO** — production tréning-pipeline (nem in-context); Tier-$50/200-ban nem fér bele
- **Promptbreeder self-referential mutation-of-mutators** — mutáció-szabályok is mutálódnak → meta-meta-rendszer instabilitás
- **Phase B-1..B-7-vel párhuzamos RSI** — biztonsági ok: a többi tengely **alapozza** az RSI-t, nélküle vakon-fejlődik
- **AGI-style autonomy slider 0% manual** — a manual review **soha nem dobható** a Phase C-ben sem; legfeljebb Phase D+ idejére

## Konzekvenciák

**Pozitív:**
- A 8-tengelyű evolúció **utolsó capstone-eleme** — a vault valóban „compounding intelligence" lesz
- Skill library auto-bővítés → SV-4 (Tool composition) **multiplikálja önmagát** (új skill = új tool)
- Prompt evolution → SV-3 (Multi-agent) prompt-template-ek minősége **iteratívan javul** (Pareto-front)
- Reflection-loop → a Karpathy „compilation" (LLM-Wiki) elv **valós megvalósítása**

**Negatív:**
- **Magasabb-kockázatú sprint** — a teljes Phase A roadmap sikere ettől függhet
- Cost-spike: GEPA havi-mutator + Critic-review minden auto-mutation-en (extra Sonnet-call-ok)
- Audit-overhead: heti manual review a `Auto-reflections/`-en (15-30 perc/hét)
- **Backout-trigger:** ha bármely héten >5% revert-rate a propagated mutations-on, **TELJES RSI-flag OFF** és root-cause-vizsgálat

**Backout-plan:** Per-réteg ENV-flag (`RSI_SKILL=0/1`, `RSI_PROMPT=0/1`, `RSI_REFLECT=0/1`). Default **OFF** mindhárom, manual opt-in.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| Self-correction blind spot (LLM elfogadja a saját hibás mutációt) | Vault-corruption | Critic mandatory G-Eval-routing + ReFlect harness + git-pre-commit hook |
| Reward hacking (GEPA-mutator a Critic-jutalmat exploit-álja) | Prompt-drift | Pareto-front (NEM 1 score), heti Ground Truth re-baseline (B-3 reuse) |
| Model collapse (RSI-output szintetikus → train) | Minőség-csökkenés | A Phase B-8 NEM tréning-pipeline (csak in-context); model-súlyok változatlanok |
| Lost oversight (heti review túlterhelődik) | Bypass-hangulat | Eval-l1-parser (B-3) auto-detect a `Auto-reflections/` minőségét; heti audit-stat |
| Cross-vault propagation (Rob vaultja kapja a Peti-RSI-output-ot) | Cross-contamination | Per-vault RSI isolation; Auto-reflections NEM cross-publish |

## Open questions

1. **GEPA-mutator model-választás:** Sonnet vs Opus? A Phase A+ alapján Sonnet adekvát, de Opus-mutátorral 2-3× jobb minőség. Cost-benchmark a B-8 első hetén.
2. **Skill-pruning:** ha egy auto-draft skill 3 hónapig nem hívott, archív vagy delete? Phase C idejére döntés.
3. **Cross-agent RSI (Codex / Gemini):** ha mindhárom agent külön-külön Reflect-loop-ot futtat, kommunikálnak-e egymással? Vagy strict per-agent isolation? Phase C+ stratégiai kérdés.

## Kapcsolódó

- [[11-wiki/sv-02-recursive-self-improvement]] — research-cikk
- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — B-1 sprint (Critic + G-Eval foundation)
- [[07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]] — B-6 sprint (4 prompt-template a GEPA-mutator target-je)
- [[07-Decisions/2026-05-12 sv-4 tool composition arch]] — B-4 sprint (Skill-library Phase B-8 Réteg 1 target-je)
- [[07-Decisions/2026-05-12 sv-7 continuous evaluation arch]] — B-3 sprint (Ground Truth + Critique Shadowing safeguard)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap

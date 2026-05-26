---
name: Cascade-pattern család taxonomy
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern/cascade, taxonomy, evergreen, orchestration]
---

# Cascade-pattern család taxonomy

> [!info] TL;DR
> A vault-ban **16 Concept** beszél „cascade"-ról, és valójában **4 különböző jelentés-réteg** keveredik egy szó alatt: (a) **sprint-orchestration cascade** (skeleton-first Day 0), (b) **agent-fanout cascade** (subagent-tree), (c) **CSS-fill cascade** (DOM-öröklés), (d) **eval/scoring cascade** (több-réteg auto-prop gate). Ez a wiki disambiguálja és reusable döntés-szabályt ad.

## Cluster-members (vault Concept-corpus)

| Concept | Réteg | Forrás |
|---|---|---|
| cascade phase | Sprint-orchestration | session |
| cascade sprint Day 0 | Sprint-orchestration | wiki |
| 5 sprint Day 0 cascade | Sprint-orchestration | session |
| 3rd-5th sprint in cascade | Sprint-orchestration | session |
| Day 0 cascade pattern | Sprint-orchestration | wiki/sprint-day-0-skeleton-first |
| Trial then 8-parallel cascade | Sprint-orchestration | wiki/claude-code-subagent-fanout |
| cascade agents | Agent-fanout | session |
| cascade prompt-template | Agent-fanout | session |
| Subagent cascade pattern | Agent-fanout | wiki |
| agent-tree cascade failure | Agent-fanout | session |
| cascade pattern | meta | wiki |
| text-group fill cascade | CSS-DOM | wiki/chromium-img-svg-parent-fill-bug |
| fill cascade inheritance | CSS-DOM | wiki |
| Chromium img-svg parent-fill cascade bug | CSS-DOM | wiki |
| SV B-4 cascade | Eval/scoring | wiki/layered-eval-cascading-pattern |
| Model cascade routing | Eval/scoring | session |

## A 4 cascade-család

### 1. Sprint-orchestration cascade (Day 0 skeleton-first)

**Mintázat:** N sprint **párhuzamosan** indul, mind ugyanazon a Day 0-on commit-elve, hogy a downstream-sprintek ne block-oljanak egymást.

- **Trigger:** több SV-tengelyt egyszerre indítasz (pl. B-1..B-5)
- **Mechanizmus:** Day 0 = scaffold + skeleton, ZERO funkcionális kód (kivétel <20 LOC)
- **Példák:** SV B-1..B-7 cascade (2026-05-13), MFL-Voice 5-sprint cascade

**Reusable szabály:** ha 3+ sprint induló-függetlenül kell, **mindegyiket Day 0-án skeleton-committal indítsd** — ezt nevezed cascade-nek, NEM a sorba-rakott végrehajtást.

→ [[sprint-day-0-skeleton-first]]

### 2. Agent-fanout cascade (subagent-tree)

**Mintázat:** lead-agent N subagent-et **párhuzamosan** spawnol, mindegyik clean-context, eredmény visszafolyik a lead-be (map-reduce).

- **Trigger:** 5+ azonos típusú task (bulk-mutation, batch-research)
- **Mechanizmus:** Task-tool / Agent-tool fanout, NEM sequential
- **Hibatűrés:** `agent-tree cascade failure` = ha 1 subagent fail, NEM borítja a többi futását (lead-aggregator dönt)

**Reusable szabály:** subagent-fanout-ra MIN 5 task, MAX 10 (Claude Code rate-limit) per-batch. Lead-context-budget ne fogyjon — clean-context handoff [[clean-context-subagent-handoff]].

→ [[claude-code-subagent-fanout]]

### 3. CSS-DOM fill cascade (Chromium bug)

**Mintázat:** SVG `<text>` fill-property öröklődik a parent-tól, de Chromium bug-os `<img>` parent ↔ inline-SVG kapcsolatban.

- **Trigger:** WP/Elementor ikon-mező SVG-vel, kód-szinten `<img src="...svg">`
- **Mechanizmus:** Chromium `fill` cascade NEM lép át img-parent-en, Firefox/Safari igen
- **Workaround:** inline-SVG vagy `<object>` tag

→ [[chromium-img-svg-parent-fill-bug]]

**Reusable szabály:** SVG-fill cross-browser inkonzisztens — print-asset legyen vektor-direkt, web-asset legyen inline-`<svg>`.

### 4. Eval/scoring cascade (layered safety)

**Mintázat:** drága ML-eval (LLM-judge) ELŐTT olcsó rule-based réteg → ha az kiszűri, drága réteg nem fut.

- **Trigger:** auto-propagation gate, model-cascade routing
- **Layers:** rule-based → coherence-check (lokális NLI) → G-Eval (LLM-judge, drága)
- **B-1 példa:** crystallize cascade Layer 1 ENV-gate → 2 source-type → 2.5 NLI → 2.6 coherence → 3 G-Eval

**Reusable szabály:** evaluation-pipeline-ben **olcsó-először-drága-utoljára**. Ha hot-path < 10ms, drága réteg csak ha az olcsók pass-elnek.

→ [[layered-eval-cascading-pattern]] · [[g-eval-bias-mitigation-pattern]]

## Cascade-szó disambiguáció szabály

Mikor sessionben „cascade" szót használsz, **jelöld a réteget**:

| Szó | Jelentés |
|---|---|
| „sprint-cascade" | Day 0 párhuzamos sprint-indítás |
| „agent-cascade" / „subagent-cascade" | fanout-spawn |
| „CSS-cascade" / „fill-cascade" | DOM-öröklés |
| „eval-cascade" / „scoring-cascade" | layered ML-judge |
| meztelen „cascade" | tilos, ambiguous |

## Anti-pattern

| Pattern | Probléma |
|---|---|
| 5-sprint cascade Day 0 SKIP-pel | szekvenciális, NEM cascade |
| Agent-fanout ÉS sequential subagent vegyítve | rate-limit + race-condition |
| Eval-cascade fordított-sorrend (drága-először) | költség robban |
| CSS-cascade Chromium-specific feltétel | cross-browser break |

## Reusable szabályok

1. **Cascade ≠ sequential**: ha sorrend kötött → pipeline. „Cascade" = párhuzamos / réteges
2. **Layered cascade-ben**: olcsó-először, telemetry-bel hogy mérd, melyik réteg mennyit szűr
3. **Day 0 cascade-ben**: scaffold-only commit, funkc-kód Day 1+
4. **Agent-fanout cascade-ben**: clean-context, NEM shared-memory; lead-aggregator dönt

## Kapcsolódó

- [[sprint-day-0-skeleton-first]]
- [[claude-code-subagent-fanout]]
- [[chromium-img-svg-parent-fill-bug]]
- [[layered-eval-cascading-pattern]]
- [[clean-context-subagent-handoff]]
- [[g-eval-bias-mitigation-pattern]]

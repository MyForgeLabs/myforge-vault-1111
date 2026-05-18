---
name: SV-3 Multi-agent orchestration — Phase B-6 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "multi-agent", "orchestration", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-03-multi-agent-orchestration]]
sprint: B-6
priority: P2 (high-leverage, depends on B-4)
estimated_effort: 2-3 hét
depends_on: B-4 (MCP-szerver), B-2 (Memgraph), B-1 (G-Eval)
---

# ADR — Phase B-6: SV-3 Multi-agent orchestration

## Kontextus

A jelenlegi vault **single-agent**:
- 1 Claude Code session = 1 LLM-context-ablak
- Több párhuzamos session lehet, de **közöttük nincs explicit kommunikáció** — közvetett (file-system-state, manuális `11.11focus`)
- A Phase A+ research már **megmutatta a multi-agent erőt**: 8 párhuzamos NotebookLM-subagent + 6 SV-Phase-A-+ subagent ~1 nap alatt 2900 sor tartalmat termelt — de **ez ad-hoc**, nem strukturált pattern

**SV-3 Phase A+ insight (737 source):** Ipari konszenzus 2026-ra:
- **P2P GroupChat zsákutca** — 15× tokenköltség + masszív kontextus-degradáció
- A nyertes minta: **Orchestrator + Isolated Subagent + Summary-Only Return + Filesystem-as-State** (a P2 minta)
- **Anthropic Multi-Agent Research System**: +90% minőség 15× token-cost mellett
- „Simplicity over framework" — CrewAI / AutoGen / LangGraph frameworkök helyett **kompozábilis primitívek** a meglévő rendszerre

**A Peti-vault szerkezetileg már ideális** erre — 11.11 session-protokoll (időbeli izoláció) + Markdown-fájlrendszer (Filesystem-as-State) + 280 skill-pool (specializált agensek alapja).

## Döntés

**4-elemű orchestrator-worker arch a meglévő 11.11 + B-4 MCP-réteg fölött**, 2-3 hetes sprintben.

### Elem 1 — Orchestrator agent (Planner)

A `11.11start "feladat"` parancs **kibővítése**: ha a feladat-szöveg `multi-agent:` prefix-szel vagy `>3 tengely` érintettséggel jön → **automatikus Orchestrator-mód**.

**Tech-stack:**
- **Orchestrator prompt-template:** `~/.agents/prompts/orchestrator.md` (Claude Sonnet/Opus érvelő szintű)
- A Planner feladata: feladat-bontás, subagent-szám-meghatározás, subagent-feladatkiadás, summary-return-monitor
- A Planner **csak metadata + summary-return**-eket lát, NEM a subagentek nyers munkáját
- Kommunikáció a subagentekkel: **MCP-RPC** (B-4 sprint output)

### Elem 2 — Isolated Subagent (Worker)

Egy worker = **friss Claude Code kontextus-ablak + saját system-prompt + saját trigger-skill-pool**.

**Tech-stack:**
- **Worker spawning:** `/usr/local/bin/11.11worker <task-id> <skill-trigger>` — új sub-process, friss `claude-code` session, dedikált working-dir (pl. `/tmp/vault-workers/<task-id>/`)
- **Summary-only return:** a worker `11.11stop`-ja **NEM tölti vissza a teljes Learning-listát**, csak egy max-500-tokenes summary-return-t a Planner-nek (P2 szabály)
- **Filesystem-as-State:** a worker minden módosítást direkt a vault-Markdown-fájlokba ír (MCP-n keresztül); a Planner csak az **append-only EventLog**-ot követi (`~/obsidian-vault/.workers/<task-id>/events.jsonl`)

### Elem 3 — Critic / Red-team agent (Safeguard)

A 2026-os ipari konszenzus szerint a Critic agent **megelőzi** a hibás mutációkat — különösen kritikus a Phase B-1 (Crystallization) és Phase B-8 (RSI) idején.

**Tech-stack:**
- **Critic prompt-template:** `~/.agents/prompts/critic.md` (Claude Haiku / olcsó-modell, mert sokszor hívódik)
- Belépési pont: minden mutation MCP-tool-hívás ELŐTT (`add_skill`, `update_wiki_section`, `add_decision`, `crystallize_learning`) → Critic-review
- **Threshold-routing (B-1 G-Eval reuse):** Critic confidence > 0.85 → engedélyezés, < 0.85 → batch-preview a Planner-nek
- **Red-team mode:** opcionálisan minden 10. mutation-ön Critic **explicit ellenpárti perspektívával** kérdez (Constitutional AI 2 minta)

### Elem 4 — Summarizer agent (Convergent synthesis)

Multi-subagent munkamenetek végén egy **dedikált Summarizer** — a Phase A+ deep-research SV-3 + SV-8 ajánlása.

**Tech-stack:**
- **Summarizer prompt-template:** `~/.agents/prompts/summarizer.md` (Claude Sonnet)
- Belépés: a Planner összegyűjti az összes Worker summary-return-t → Summarizer szintetizál egyetlen Learning-listává
- **NotebookLM-konzultáció (B-5 reuse):** a szintézis-pre-output átküldve a projekt-NotebookLM-be, `vault-nb-crystallize` validációval

## Acceptance criteria

- [ ] **`11.11worker` script** működik — friss Claude Code spawn, izolált working-dir, MCP-RPC
- [ ] **Orchestrator prompt-template** kalibrálva — 5 minta-task `multi-agent:` futás, manual review a feladat-bontás minőségére
- [ ] **Summary-only return működik** — Worker `11.11stop` <500 token Planner-nek (nem teljes Learning-list)
- [ ] **Filesystem-as-State + EventLog** — Planner csak az event-log-ot követi, NEM a worker-context-et
- [ ] **Critic intercepts mutations** — minden `add_*` MCP-tool-hívás előtt Critic-review (>0.85 confidence vagy batch-preview)
- [ ] **Summarizer szintézis működik** — 8-subagent example-task, max 3 Learning-bullet output (helyes konvergencia)
- [ ] **Token-economy mérve:** prompt-overload mérés single-agent vs orchestrator-worker — ideális esetben minőségben +30-90%, costban +5-10× (NEM +15×, mert a Worker-kontextus tisztább a kompozábilis primitívekkel)

## Alternatívák amiket ELUTASÍTOTTUNK

- **CrewAI Crew+Flows framework** — komplex absztrakció, „simplicity over framework" konszenzus ellen
- **AutoGen GroupChat** — Phase A+ insight: GroupChat 15× tokencost + context-bleed, kifejezetten zsákutca
- **LangGraph 2.0 durable execution** — production-grade, de a meglévő 11.11 session-mechanikára épült saját implementáció egyszerűbb és kontrollabb
- **Devin/Manus tier autonomy** — túl agresszív Phase B-6 idejére; Phase C+ idejére, ha a B-1..B-5 stabil
- **MCP nélkül, direct subprocess-communication** — race-condition, nincs strukturált tool-handshaking; B-4 MCP-réteg megoldja

## Konzekvenciák

**Pozitív:**
- **+90% minőség komplex feladatokon** (SV-3 Phase A+ Anthropic-mérés)
- A Phase A+ Sprint-ben már látott pattern (8 párhuzamos NotebookLM-subagent) **strukturált** és **újrahasználható**
- Critic intercepts → biztonsági réteg a Phase B-8 RSI sprintbe (Critic mint pre-flight)
- Summarizer + NotebookLM (B-5) konvergens — kettős-bíró a high-confidence Learning-ekre

**Negatív:**
- **+5-10× token-cost** a klasszikus single-agent-hez képest → Tier-$200 minimum a frequent multi-agent használatra
- 4 új prompt-template karbantartása
- Worker-process-management komplexitás (zombie-process-ok, takarítás)
- Race-condition rizikó (a Phase A+ Sprint-ben már láttuk: 8 párhuzamos NotebookLM-API rate-limit → 6/8 batch-ben Q-rate-limit-miss)

**Backout-plan:** Az Orchestrator-mód kapcsolható ENV-flaggel (`MULTI_AGENT=0/1`). Default: single-agent (mint most). A 4 prompt-template megmarad, de inaktív.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| Worker-context-bleed (Planner véletlenül megkapja a teljes context-et) | P2 szabály sérül, +15× token-cost | Strict prompt-engineering, MCP-szintű enforce (`max_response_tokens=500`) |
| Race-condition több Worker egyszerre módosít ugyanazt a fájlt | Vault-corruption | File-lock-szervice az MCP-szerveren; LangGraph-stílusú Checkpointer pattern |
| Critic false-positive (jó mutation-t leblokkol) | Frustration, lassabb workflow | Critic-judgment audit-log + heti review; threshold-tuning |
| Multi-agent rate-limit (NotebookLM-incidens reprodukálva) | Worker-failure | Per-worker rate-limit + 30-60 sec spread + exponential backoff |
| Cost-blowout (15× token elszáll) | Tier-$50 átlépés | Per-feladat hard token-budget; Planner ENV-budget-check beforehand |

## Open questions

1. **Worker-skill-pool isolation:** minden Worker-nek a teljes 280-skill pool, vagy `trigger-keyword`-szerinti subset? Phase B-6 első napon prototype mindkettőre, token-economy benchmark.
2. **Orchestrator + Worker model-mix:** Planner = Opus (drága érvelés), Worker = Sonnet (közepes), Critic = Haiku (olcsó), Summarizer = Sonnet — vs. minden Sonnet? Cost-benchmark a B-6 első hetén.
3. **Cross-vault orchestration:** Rob vaultjának Workerei a Peti-Plannerből hívhatók? Hosszú-távú kérdés, Phase C+ idejére.

## Kapcsolódó

- [[11-wiki/sv-03-multi-agent-orchestration]] — research-cikk
- [[07-Decisions/2026-05-12 sv-4 tool composition arch]] — B-4 sprint (MCP-réteg foundation)
- [[07-Decisions/2026-05-12 sv-1 memory architecture arch]] — B-2 sprint (Filesystem-as-State + Memgraph state-store)
- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — B-1 sprint (Critic threshold-routing G-Eval reuse)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap

---
name: rsi-tier2-constitutional-ai-pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: [topic/rsi, topic/safety, env/local, lifecycle/draft]
---

# RSI Tier-2 Constitutional AI pattern

> [!warning] Safety-critical
> Ez a minta gátolatlanul futtatva **Gödel Agent veszély** — recursive self-modification → vault-corruption-risk. SOHA NE futtasd `--apply`-vel manual safety-review nélkül.

## Mi ez

Az **RSI (Recursive Self-Improvement)** három-szintű létrája a Superintelligent Vault B-sprint kontextusában:

| Tier | Mit csinál | Kockázat | Példa |
|---|---|---|---|
| **Tier-1: GEPA prompt-evolution** | Egy adott prompt 3-5 variánsát értékeli Pareto-front-on | ALACSONY (csak prompt-text mutáció + eval) | `gepa-prompt-mutate.py` — B-1 Week 4 ÉLES |
| **Tier-2: Constitutional auto-mutate** | Worker generál mutation-candidate-eket → Critic-LLM rule-set ellen review-zza → approved-eket Pareto-eval-vel mer/dobja | KÖZEPES (semantic mutation + auto-apply lehetőség) | `rsi-tier2-constitutional.py` — B-8 Tier-2 skeleton |
| **Tier-3: Agent self-modification** | Agent saját kódját módosítja runtime-ban | **KRITIKUS** (Gödel Agent monkey-patching, unbounded) | Phase C+ — NEM-justifiable cost+risk |

A Tier-2 a "sweet spot": már szemantikus, de még **4-rétegű safety-gate** mögött tartható.

## Constitutional AI alapja (Anthropic 2022)

A Worker LLM generál candidate-et, egy **Critic-LLM** pedig egy explicit rule-set ellen Chain-of-Thought (CoT) érveléssel `approve` / `reject` döntést hoz. A rule-set egy explicit "alkotmány" — emberi-érthető rule-ok, harm-rationale, és detekció-heurisztika.

**Kulcs-szabály:** a rule-set magában `R6_no_self_reference_modification`-t kell hogy tartalmazza — az alkotmány saját szabályait NEM mutálhatja a folyamat. Ha ez hiányzik → infinite-loop → Gödel-veszély.

## 4-rétegű safety-gate

Minden Tier-2 mutation négy független rétegen kell hogy átmenjen. Bármelyik blokk → halálos kimenet:

### Layer-1: ENV-flag

```bash
VAULT_RSI_TIER2_APPLY=1   # default: nincs beállítva -> dry-run mindig
```

Default-deny pattern. `--apply` flag nem elég önmagában — szándékos shell-state változtatás kell.

### Layer-2: Forbidden-target hard regex

```yaml
forbidden_patterns:
  - ".*AGENTS\\.md$"
  - ".*/00-Meta/.*"
  - ".*/\\.vault-rsi/scripts/.*"   # az RSI saját scriptjei
  - "/usr/local/bin/11\\.11.*"
  - ".*\\.git/.*"
```

**NEM LLM-review** — pure regex hard-block. Ha a target match-el bármelyik pattern-re, azonnal exit-1, mielőtt a Worker/Critic egyáltalán fut.

### Layer-3: Git pre-commit-hook

```bash
ln -s /root/obsidian-vault/.vault-rsi/safety/git-pre-commit-hook.sh \
      /root/obsidian-vault/.git/hooks/pre-commit
```

A hook független a Python-scripttől: a git-szintű ellenőrzés még akkor is blokkol, ha a script-logika bug-os. Defense-in-depth.

### Layer-4: Constitutional Critic CoT review

10 explicit rule, mindegyik:
- **rule:** mi tilos (1 mondat)
- **harm:** miért veszélyes (1 mondat)
- **detection:** hogyan detektálja a Critic (CoT-prompt vagy heurisztika)

A `min_critic_confidence: 0.85` ambiguity-eset-en default-reject (safety-first).

## A 10 Constitutional rule (rövid)

| # | Rule | Detekció |
|---|---|---|
| R1 | NEM távolíthat el safety-gate-et | token-count: gate/forbidden/critic/approve/validate/safety |
| R2 | NEM bővítheti a target-listát | allowed_targets / mutable_files lista-diff |
| R3 | NEM csökkentheti az approval-threshold-okat | numeric-value compare (új < régi → reject) |
| R4 | NEM bypass-olhatja az emberi review-t | bool-flag check (human_review NEM válthat false-ra) |
| R5 | NEM törölhet audit-log step-et | audit/log/commit/jsonl token-count |
| R6 | NEM módosíthatja saját scriptet/rules.yaml-t | hard-coded path-check (Gödel-prevention) |
| R7 | NEM adhat új capability-t | diff-elemzés: új-import, network-call, shell-spawn → reject |
| R8 | Approved-candidate Pareto-eval-en (GEPA) át kell menjen | workflow-state: GEPA-score nélkül NEM `apply` |
| R9 | Reversibility — csak text-replace, NEM rm/mv/symlink | destructive-token check a diff-ben |
| R10 | NEM tilthatja le saját Critic-review-ját | workflow-flag: critic_enabled NEM válthat false-ra |

## Anti-pattern: gátolatlan RSI (Gödel Agent veszély)

A "Gödel Agent" konceptuális szélső-eset: egy agent ami **saját kódját módosítja** futás-időben (monkey-patching). Kockázat:

- **Self-reference modification** — az agent eltünteti saját safety-check-jeit
- **Capability-grant emergens** — új import-ok (network, subprocess shell-spawn) hirtelen elérhetők
- **Threshold-decay** — minden iteráció csökkenti a confidence-bar-t → eventually 100% auto-approve
- **Audit-trail-loss** — a JSONL-append step kikerül → forensic-impossible visszafejteni

**Védekezés:** explicit R6 (self-reference forbidden) + Layer-2 hard regex saját script-path-ra + git-hook független Python-state-től + emberi review minden `--apply` előtt.

## Reusable szabályok

1. **DRY-RUN default mindig** — `--apply` opt-in, ENV-flag-vel megerősítve (két szintű opt-in)
2. **Hard-regex előbb mint LLM-review** — pre-filter olcsóbb és deterministic
3. **R6 SOHA NE hiányozzon** — self-reference modification = Gödel-veszély core
4. **Csak text-replace op-ok** — rm/mv/chmod/symlink kívül van a scope-on (R9)
5. **Critic-confidence threshold ambiguity-eset-en reject** — safety-first asymmetric (false-reject olcsóbb mint false-approve)
6. **Audit-log mindig JSONL-append** — sose felülír; minden candidate (approve/reject) marad
7. **Defense-in-depth: 3+ független layer** — egy bug egy layer-ben ne legyen halálos
8. **Forbidden-pattern lista emberi-domain** — `/usr/local/bin/11.11*`, AGENTS.md, 00-Meta/, ezeket NEM agent mutálja

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]] — RSI architektúra ADR
- [[multi-layer-safety-gate]] — általános 4-réteg safety-gate playbook
- [[sv-02-recursive-self-improvement]] — B-8 sprint roadmap
- [[g-eval-bias-mitigation-pattern]] — Critic-bias kalibráció (G-Eval v0.3)
- [[../06-Audits/2026-05-18 B-8 RSI Tier-2 Constitutional AI skeleton]] — skeleton smoke-test audit

## Skeleton (B-8 Tier-2 milestone, 2026-05-19)

- Script: `.vault-rsi/scripts/rsi-tier2-constitutional.py` (~290 sor, DRY-RUN default)
- Rules: `.vault-rsi/constitutional-rules.yaml` (10 rule + forbidden-pattern + critic-prompt template)
- Audit log: `.vault-rsi/tier2-mutations-log.jsonl`
- Smoke: 3 mock candidates → 2 approve (stylistic + CoT) + 1 reject (R3 threshold-lowering 0.85→0.55)

**Hiányzik az ÉLES futáshoz** (TODO Tier-2 Week 2-3):
- Real Worker subagent call (jelenleg mock candidates)
- Real Critic subagent CoT review (jelenleg deterministic heurisztika)
- GEPA Pareto-eval beépítése a `--apply` workflow-ba (R8)
- Git pre-commit-hook telepítése (manuálisan, NEM auto)
- Sandbox-branch flow (`rsi-sandbox-*` prefix a config-ban)

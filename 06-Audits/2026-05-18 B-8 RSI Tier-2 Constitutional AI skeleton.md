---
name: 2026-05-18 B-8 RSI Tier-2 Constitutional AI skeleton
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: [topic/rsi, topic/safety, env/local, lifecycle/draft]
project: superintelligent-vault
---

# B-8 RSI Tier-2 Constitutional AI skeleton — smoke-test audit

> [!warning] Skeleton-status
> DRY-RUN only. SOHA NE futtasd `--apply`-vel manual review nélkül. 4-rétegű safety-gate skeleton-szinten beépítve, de Layer-3 (git pre-commit-hook) telepítése manuális, és Layer-4 (Critic-LLM) jelenleg deterministic heurisztika, NEM real subagent.

## Cél

A B-8 Tier-1 (GEPA real-loop, +14.3% Pareto) ÉLES utáni következő lépés: **Tier-2 Constitutional AI auto-mutate skeleton**. Prompt-evolution NEM csak GEPA-ban, hanem self-critique + safety-gated mutation-cycle-ben. Anthropic 2022 CAI minta + 10-rule explicit alkotmány + 4-rétegű defense-in-depth.

## Mit építettünk

### 1. Skeleton script

**Path:** `/root/obsidian-vault/.vault-rsi/scripts/rsi-tier2-constitutional.py`
**Sorok:** 287 sor (Python 3, pyyaml dep)

**Felépítés:**
- `layer1_env_check()` — `VAULT_RSI_TIER2_APPLY=1` ENV-gate
- `layer2_forbidden_check()` — regex hard-block forbidden-pattern listára
- `worker_generate_candidates()` — skeleton mock 3 candidate (real-mode: `claude` subprocess)
- `critic_review_skeleton()` — Constitutional 10-rule CoT deterministic detekció (R1/R3/R7/R9 aktív)
- `gepa_pareto_eval_placeholder()` — R8 hook (real-mode: `gepa-prompt-eval.py` shell-out)
- `audit_append()` — JSONL append `tier2-mutations-log.jsonl`-be

### 2. Constitutional rule-set

**Path:** `/root/obsidian-vault/.vault-rsi/constitutional-rules.yaml`
**Tartalom:**
- 8 forbidden-pattern regex (AGENTS.md, 00-Meta, scripts, safety, config, constitutional-rules self-ref, git, 11.11)
- 10 semantic rule (R1-R10) explicit harm-rationale + detection-heurisztika
- Critic prompt template (CoT JSON-output schema)
- Audit-log mező-séma

**A 10 rule:**
1. **R1** no_safety_gate_removal — safety-token count NEM csökkenhet
2. **R2** no_scope_expansion — target-lista NEM bővülhet
3. **R3** no_threshold_lowering — numeric threshold NEM csökkenhet
4. **R4** no_human_review_bypass — human/critic_review NEM válthat false-ra
5. **R5** preserve_audit_trail — audit/log/jsonl tokenek NEM törölhetők
6. **R6** no_self_reference_modification — RSI saját scriptjét/rules.yaml NEM mutálhatja (Gödel-prevention)
7. **R7** no_emergent_capability_grant — új capability (network, subprocess shell-spawn, dynamic-eval) tilos
8. **R8** pareto_eval_mandatory — approved-candidate GEPA-eval-en át kell menjen
9. **R9** reversibility_required — csak text-replace, NEM rm/mv/chmod/symlink
10. **R10** no_recursive_critic_disable — Critic-flow NEM tilható le

## Smoke-test eredmény

**Parancs:** `python3 .vault-rsi/scripts/rsi-tier2-constitutional.py --target g-eval.md --dry-run`

```
=== RSI Tier-2 Constitutional AI skeleton ===
Target: /root/obsidian-vault/.vault-rsi/prompts/baseline/g-eval.md
Mode:   DRY-RUN

[Layer-2 PASS] target not in forbidden-pattern list

[Worker] generated 3 candidate(s)

  OK cand-f563dcaf:  APPROVE (conf 0.90, harm low)
     rationale: Reword system prompt for clarity (no semantic change)

  OK cand-97a06896:  APPROVE (conf 0.90, harm low)
     rationale: Add explicit CoT step before final score

  XX cand-8a0e74a8:   REJECT (conf 0.95, harm critical)
     rationale: Lower min_critic_confidence threshold for faster auto-prop
     violated:  ['R3_no_threshold_lowering']
     cot:       R3 violation: numeric threshold dropped 0.85 -> 0.55 (auto-reject)

Total: 3 | Approved: 2 | Rejected: 1
DRY-RUN complete. No filesystem writes. No git commits.
```

**Eredmény: spec szerinti 3/2/1.** Layer-2 PASS a baseline target-en, Layer-4 (Critic) helyesen elutasítja az R3-violation candidate-et.

## Safety-gate verifikáció

| Gate | Test | Eredmény |
|---|---|---|
| Layer-1 ENV-flag | `--apply` futtatás ENV nélkül | `[Layer-1 BLOCK] --apply requested but VAULT_RSI_TIER2_APPLY != 1` → exit-1 |
| Layer-2 Forbidden | `--target ../../../AGENTS.md` | `[Layer-2 BLOCK] matches forbidden pattern '.*AGENTS\\.md$'` → exit-1 |
| Layer-3 Git-hook | NEM tesztelve — manuálisan kell telepíteni | TODO Week 2 |
| Layer-4 Critic | R3 threshold-lowering candidate | `REJECT (conf 0.95, harm critical)` ✓ |

## Audit log

`tier2-mutations-log.jsonl` — 3 entry, mind a 12 mező kitöltve:
- timestamp, target, candidate_id, rationale, diff_summary
- critic_decision, critic_confidence, violated_rules, cot_reasoning, harm_assessment
- gepa_score, final_action

## Mérnöki őszinte értékelés

**Skeleton-szinten safety-gate-elt-e (4 réteg mind ott van)?**

- ✅ **Layer-1 (ENV-flag):** működik, smoke-tesztelt. `VAULT_RSI_TIER2_APPLY=1` default-deny.
- ✅ **Layer-2 (Forbidden-pattern):** működik, smoke-tesztelt. 8 forbidden-pattern regex, hard-block LLM-review előtt.
- ⚠️ **Layer-3 (Git pre-commit-hook):** **NEM aktív**. A `.vault-rsi/safety/git-pre-commit-hook.sh` létezik a B-1 sprint-ből, de a `.git/hooks/pre-commit` symlink kézzel telepítendő. A skeleton ezt ki is fejezi: a `--apply` mód `[Layer-3 BLOCK]` üzenettel exit-3-mal végződik, NEM ír fájlrendszerbe.
- ⚠️ **Layer-4 (Critic-review):** **deterministic heurisztika**, NEM real LLM-subagent. A 4 aktív rule (R1/R3/R7/R9) regex-alapú detektorral fut, az R2/R4/R5/R6/R8/R10 csak rule-set-ben van definiálva. Real-mode: `claude` subagent fanout + Constitutional prompt-template.

**Konklúzió:** **2/4 layer ÉLES**, **2/4 layer skeleton-szinten ott van de aktiválandó** (git-hook manuális telepítés + Critic real-LLM subagent integration). A `--apply` flow garantáltan nem ír, mert a Layer-3 explicit blokk. **Ez biztonságos skeleton-pozíció**: nem-progress nem rosszabb, mint mock-progress.

**Időbudget:** ~7 perc (8 max-on belül).

## Következő lépések (Tier-2 Week 2-3)

1. **Worker real-mode** — `claude` subagent call mutation-candidate generálásra (jelenleg mock 3 candidate)
2. **Critic real-mode** — `claude` subagent CoT review a `critic_prompt_template`-tel
3. **Layer-3 aktiválás** — git pre-commit-hook telepítése + sandbox-branch flow tesztelése
4. **GEPA integráció (R8)** — `gepa-prompt-eval.py` shell-out a `--apply` előtt
5. **Multi-Critic ensemble** — `unanimous_required: true` opció több Critic-szavazatra
6. **Threshold-ramp** — `min_critic_confidence` 0.85 → 0.90 → 0.95 a stabilitás-tapasztalattal

## Kapcsolódó

- [[../11-wiki/rsi-tier2-constitutional-ai-pattern]] — pattern-doku (~120 sor)
- [[../07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]] — RSI architektúra ADR
- [[../11-wiki/sv-02-recursive-self-improvement]] — B-8 sprint roadmap
- [[../11-wiki/multi-layer-safety-gate]] — általános safety-gate playbook
- [[../11-wiki/g-eval-bias-mitigation-pattern]] — Critic-bias kalibráció (kapcsolódó minta)

## Fájl-pointerek

- `/root/obsidian-vault/.vault-rsi/scripts/rsi-tier2-constitutional.py` (287 sor)
- `/root/obsidian-vault/.vault-rsi/constitutional-rules.yaml` (~150 sor)
- `/root/obsidian-vault/.vault-rsi/tier2-mutations-log.jsonl` (3 smoke-entry)
- `/root/obsidian-vault/11-wiki/rsi-tier2-constitutional-ai-pattern.md`

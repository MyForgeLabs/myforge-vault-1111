---
name: Multi-layer safety-gate playbook
type: wiki
tags: ["#type/wiki", "safety", "security", "playbook", "high-risk-features"]
created: 2026-05-13
updated: 2026-05-13
status: stable
---

# Multi-layer safety-gate playbook

Magas-kockázatú feature-ekhez (RSI, auto-prompt-evolution, code-self-modification, auto-promotion) **4 független védelmi réteg** kell. Egyetlen réteg sem elég — egymást validálják ("defense in depth").

## A 4 réteg

### 1. ENV-flag default-disabled

A feature default-on **NEM fut**. Csak explicit `<FEATURE>_MODE=enabled` ENV-flag-gel aktiválódik.

```bash
# Default — minden RSI-script exit-el:
vault-skill-suggest                # ⚠️ safety-gate exit

# Explicit enable:
RSI_MODE=enabled vault-skill-suggest --analyze-last 30
```

**Miért:** Operator-friction kell az aktiváláshoz. Senki sem futtat véletlenül `RSI_MODE=enabled`-et — szándékos kell legyen.

### 2. Script-szintű safety-gate (első sor)

Minden script első dolga ellenőrizni a flag-et + abortolni ha disabled. **NEM lehet** middleware vagy később-check — az első instruction:

```python
def safety_gate():
    if os.environ.get("RSI_MODE", "disabled") != "enabled":
        print("⚠️  RSI safety-gate: disabled by default.", file=sys.stderr)
        print("    Enable with: RSI_MODE=enabled <script> ...")
        print("    PRECONDITION: <list of stability checks>")
        sys.exit(2)

def main():
    safety_gate()           # ← MINDEN script első hívása
    # ... actual logic
```

**Miért:** Még import-error vagy unexpected-state esetén sem fut a logic.

### 3. Git pre-commit hook — forbidden-target blokk

A high-risk feature kimenete (kód-mutation, prompt-átírás, skill-modify) **csak sandbox-branchen** engedélyezett. Main-ra direkt commit BLOKKOLT.

```bash
# .git/hooks/pre-commit (symlink-elve a .vault-<feature>/safety/-ból)
FORBIDDEN_PATTERNS=("AGENTS.md" "00-Meta/" ".vault-<feature>/" "11.11")
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ "$BRANCH" =~ ^rsi-(sandbox|pareto)- ]]; then
  exit 0   # sandbox branchen OK
fi

STAGED=$(git diff --cached --name-only)
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  if echo "$STAGED" | grep -qE "$pattern"; then
    echo "🚫 BLOCKED: forbidden-target on non-sandbox branch"
    exit 1
  fi
done
```

**Override** csak emergency-re: `SKIP_RSI_HOOK=1 git commit ...` — explicit, naplózott.

**Miért:** Még ha a script-szintű gate-et valaki bypass-olja, a git-szint elkapja a side-effect-et a vault-history-ban.

### 4. Critic-review-mandatory (B-6 reuse)

Minden RSI/high-risk output **MCP-mutation-call ELŐTT** Critic-agent review-jén megy keresztül (Constitutional AI 2 minta). Confidence < 0.85 → batch-preview a user-nek.

```yaml
# .vault-tools/config/skill-search.yml
mcp_server:
  write_tools:
    - vault.add_skill
    - vault.update_wiki_section
    - vault.add_decision
    - vault.crystallize_learning
  critic_review_required: write_tools
```

**Miért:** Még ha az RSI mutáció jól-formatú, a Critic szemantikai-szinten elkapja (PII-leak, ADR-konfliktus, reverziós tendencia).

## Mikor használd

| Feature-típus | 4-rétegű gate szükséges? |
|---|---|
| **RSI** (kód/prompt/skill auto-mutáció) | ✅ MIND a 4 |
| **Auto-promotion** (Auto-reflections → 11-wiki/) | ✅ MIND a 4 |
| **Code self-modification** (Gödel Agent) | ✅ MIND a 4 — még Critic-multi-pass is |
| Auto-skill-suggest user-confirmáció nélkül | ✅ MIND a 4 |
| Új skill registration | ❌ 1+2 elég (gate + script-check) |
| Auto-wiki-edit feature | ✅ 1+2+4 (Critic kell) |
| Read-only auto-eval (B-3 L1 parser) | ❌ Egyik sem kell — no side-effect |

**Ökölszabály:** ha a feature **vault-állapotot mutál** és **emberi review nélkül futna**, MIND a 4 réteg kötelező.

## Backout — auto-disable triggerek

A 4 rétegen felül: minden high-risk feature-nek **passzív backout-trigger**-je kell, ami magától kapcsolja ki ha romlik valami:

```yaml
auto_disable_triggers:
  - "vault_corruption_detected"           # vault-cleanup audit drop >20% in 1 day
  - "critic_reject_rate_above_30pct"      # B-6 Critic 30%+ reject → output rossz
  - "user_manual_disable_request"         # /11.11 emergency stop
  - "eval_quality_drop_below_threshold"   # B-3 Pass-rate <70% in 1 week
```

A trigger érintése **NEM** vissza-engedélyezi a feature-t magától — manual user-action kell az újraaktiváláshoz.

## Élő példa — B-8 RSI (2026-05-13 Day 0)

Az első projekt, ami a 4-rétegű gate-et kombinálja:

| Réteg | Hol implementálva | Mit véd |
|---|---|---|
| 1. ENV-flag | `RSI_MODE=disabled` default | Default-off |
| 2. Script-gate | `.vault-rsi/scripts/*.py` első sora `safety_gate()` | Véletlen-futtatás |
| 3. Git-hook | `.vault-rsi/safety/git-pre-commit-hook.sh` | Forbidden-target commit |
| 4. Critic-review | `.vault-rsi/config/rsi-config.yml: critic_review_required` | Szemantikai rossz output |

Plus 4 auto-disable trigger. Részletek: [[.vault-rsi/README.md]] + [[02-Projects/superintelligent-vault]].

## Új minta-realizáció: flock-mutex + atomic-write komplementer (2026-05-19)

A 4-rétegű safety-gate **infrastruktúra-szintű analógja** kialakult a Layer-1 vault-atomic projekt során:

| Layer | Védi | Mechanizmus | Pattern |
|---|---|---|---|
| Cross-process race | két cron egyszerre indul → git-state ütközés | `flock -n` mutex | `vault-cron-flock` wrapper, 14 cron |
| Same-process partial-write | cron SIGKILL mid-write → félig-írt fájl | `os.replace` POSIX atomic | `vault_atomic.py` modul, 15 site |
| Process-restart dedup | daemon restart → state-loss | external store (Redis/SQLite) | heavyweight write-volume-ra |
| Audit trail | "mi történt" debug | append-only JSONL | minden write-site |

**Kulcs-tanulság:** **egyik réteg sem helyettesíti a másikat**. A flock cross-process race-t old, atomic-write same-process partial-write-ot. **Mindkettő szükséges**.

**Reusable szabály:** új mutáló-script ELŐTT mind a 4-réteget végig kell gondolni (write race / partial-write / restart-dedup / audit-trail).

## Kapcsolódó

- [[11-wiki/sprint-day-0-skeleton-first]] — Day 0 playbook
- [[07-Decisions/2026-05-12 sv-2 recursive self-improvement arch]] — B-8 ADR, az első alkalmazás
- [[07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch]] — Critic-agent (4. réteg forrása)
- [[11-wiki/rsi-tier2-constitutional-ai-pattern]] — RSI safety-gate konkrét megvalósítás (4-rétegű implementation)

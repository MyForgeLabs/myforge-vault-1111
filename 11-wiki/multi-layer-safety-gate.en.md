---
name: Multi-layer safety-gate playbook
type: wiki
tags: ["#type/wiki", "safety", "security", "playbook", "high-risk-features"]
created: 2026-05-13
updated: 2026-05-13
status: stable
lang: en
translated_from: multi-layer-safety-gate.md
---

# Multi-layer safety-gate playbook

> **Origin:** Originally written in Hungarian as part of MyForge Vault 11.11 — Superintelligent Vault project. Source: [[multi-layer-safety-gate]] (Hungarian version).

For high-risk features (RSI, auto-prompt-evolution, code self-modification, auto-promotion) you need **4 independent defense layers**. No single layer is enough — they validate each other ("defense in depth").

## The 4 layers

### 1. ENV-flag default-disabled

The feature does **NOT** run by default. It only activates with an explicit `<FEATURE>_MODE=enabled` env-var.

```bash
# Default — every RSI script exits:
vault-skill-suggest                # ⚠️ safety-gate exit

# Explicit enable:
RSI_MODE=enabled vault-skill-suggest --analyze-last 30
```

**Why:** Activation requires operator friction. Nobody accidentally runs with `RSI_MODE=enabled` — it must be intentional.

### 2. Script-level safety gate (first line)

Every script's first action is to check the flag + abort if disabled. **NOT** middleware or a later check — the first instruction:

```python
def safety_gate():
    if os.environ.get("RSI_MODE", "disabled") != "enabled":
        print("⚠️  RSI safety-gate: disabled by default.", file=sys.stderr)
        print("    Enable with: RSI_MODE=enabled <script> ...")
        print("    PRECONDITION: <list of stability checks>")
        sys.exit(2)

def main():
    safety_gate()           # ← FIRST call of every script
    # ... actual logic
```

**Why:** Even on import errors or unexpected state, the logic does not run.

### 3. Git pre-commit hook — forbidden-target block

The high-risk feature's output (code mutation, prompt rewrites, skill modifications) is **only allowed on sandbox branches**. Direct commits to main are BLOCKED.

```bash
# .git/hooks/pre-commit (symlinked from .vault-<feature>/safety/)
FORBIDDEN_PATTERNS=("AGENTS.md" "00-Meta/" ".vault-<feature>/" "11.11")
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ "$BRANCH" =~ ^rsi-(sandbox|pareto)- ]]; then
  exit 0   # sandbox branch — OK
fi

STAGED=$(git diff --cached --name-only)
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  if echo "$STAGED" | grep -qE "$pattern"; then
    echo "🚫 BLOCKED: forbidden-target on non-sandbox branch"
    exit 1
  fi
done
```

**Override** only for emergency: `SKIP_RSI_HOOK=1 git commit ...` — explicit, logged.

**Why:** Even if someone bypasses the script-level gate, the git-level catches the side-effect in vault history.

### 4. Critic-review-mandatory

Every RSI/high-risk output passes through a Critic-agent review (Constitutional AI 2 pattern) **BEFORE** the MCP mutation call. Confidence < 0.85 → batch-preview to the user.

```yaml
mcp_server:
  write_tools:
    - vault.add_skill
    - vault.update_wiki_section
    - vault.add_decision
    - vault.crystallize_learning
  critic_review_required: write_tools
```

**Why:** Even if the RSI mutation is well-formed, the Critic catches semantic-level issues (PII leak, ADR conflicts, regression tendency).

## When to use

| Feature type | All 4 gates required? |
|---|---|
| **RSI** (code/prompt/skill auto-mutation) | ✅ ALL 4 |
| **Auto-promotion** (auto-reflections → wiki) | ✅ ALL 4 |
| **Code self-modification** (Gödel Agent) | ✅ ALL 4 — plus multi-pass Critic |
| Auto-skill-suggest without user confirmation | ✅ ALL 4 |
| New skill registration | ❌ 1+2 enough (gate + script check) |
| Auto-wiki-edit feature | ✅ 1+2+4 (Critic required) |
| Read-only auto-eval | ❌ None needed — no side-effects |

**Rule of thumb:** if the feature **mutates vault state** and **would run without human review**, ALL 4 layers are mandatory.

## Backout — auto-disable triggers

On top of the 4 layers: every high-risk feature needs a **passive backout trigger** that auto-disables it if something degrades:

```yaml
auto_disable_triggers:
  - "vault_corruption_detected"           # vault-cleanup audit drop >20% in 1 day
  - "critic_reject_rate_above_30pct"      # Critic rejection rate 30%+ → bad output
  - "user_manual_disable_request"         # emergency stop
  - "eval_quality_drop_below_threshold"   # Pass-rate <70% in 1 week
```

Triggering it does **NOT** re-enable the feature automatically — manual user action is required to reactivate.

## Live example — RSI Day 0

The first project combining the 4-layer gate:

| Layer | Where implemented | What it protects against |
|---|---|---|
| 1. ENV flag | `RSI_MODE=disabled` default | Default-off |
| 2. Script gate | `.vault-rsi/scripts/*.py` first line `safety_gate()` | Accidental execution |
| 3. Git hook | `.vault-rsi/safety/git-pre-commit-hook.sh` | Forbidden-target commit |
| 4. Critic review | `.vault-rsi/config/rsi-config.yml: critic_review_required` | Semantically bad output |

Plus 4 auto-disable triggers.

## Audio overview

- EN narration (Charon voice): `[[.vault-nb/audio-overviews/multi-layer-safety-gate.en.mp3]]`
- HU narration (Kore voice): `[[.vault-nb/audio-overviews/multi-layer-safety-gate.hu.mp3]]`

Generated via Gemini 3.1 Flash TTS preview. ~1-2 minutes each. See [[gemini-3-1-flash-tts-pipeline]] for the pipeline.

## Related

- [[sprint-day-0-skeleton-first]] — Day 0 playbook
- [[claude-code-subagent-fanout]] — bulk-mutation engine that often needs the 4 gates
- [[verification-step-before-claim]] — verification as a complementary defense layer

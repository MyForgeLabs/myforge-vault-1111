#!/usr/bin/env bash
#
# bmad-vault-bridge --apply safety-gate Layer 3 — git pre-commit forbidden-targets
# + Layer 4 — optional real-LLM Critic invocation (B-8 RSI Tier-2 skeleton).
#
# ADR: 07-Decisions/2026-05-12 sv-5 crystallization automation arch.md
# Playbook: 11-wiki/multi-layer-safety-gate.md
# Critic skeleton: 11-wiki/sv-rsi-tier2-real-critic.md (2026-05-19)
#
# Install (symlink, do NOT copy):
#   cd /root/obsidian-vault
#   ln -sf .vault-ko/safety/git-pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .vault-ko/safety/git-pre-commit-hook.sh
#
# Override (emergency only — explicit + audited):
#   SKIP_CRYSTALLIZE_HOOK=1 git commit ...
#
# Critic activation (B-8 skeleton — opt-in):
#   VAULT_CRITIC_ACTIVE=1 git commit ...
#   Without it, the deterministic 4-rule Critic-stub runs (back-compat).
#
# Status: SKELETON 2026-05-17 + Critic-skeleton 2026-05-19. Both harmless
# until the upstream crystallize/bmad-vault-bridge starts real --apply runs.

set -euo pipefail

FORBIDDEN_PATTERNS=(
  "^AGENTS\.md$"
  "^00-Meta/"
  "^\.vault-ko/"
  "^\.vault-eval/"
  "^\.vault-memory/"
  "^\.vault-rsi/"
  "^\.git/hooks/"
  "/usr/local/bin/11\.11"
)

VAULT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /root/obsidian-vault)"
AUDIT_LOG="$VAULT_ROOT/06-Audits/critic-review-log.jsonl"
CRITIC_RUNNER="$VAULT_ROOT/.vault-ko/safety/critic-review.py"

# ---------------------------------------------------------------------------
# Sandbox-branch escape: crystallize-sandbox-* branches bypass forbidden-targets
# ---------------------------------------------------------------------------
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
case "$BRANCH" in
  crystallize-sandbox-*|rsi-sandbox-*|rsi-pareto-*)
    exit 0
    ;;
esac

# ---------------------------------------------------------------------------
# Emergency override (audited via shell history)
# ---------------------------------------------------------------------------
if [[ "${SKIP_CRYSTALLIZE_HOOK:-0}" == "1" ]]; then
  echo "⚠️  crystallize hook bypassed (SKIP_CRYSTALLIZE_HOOK=1) — branch=$BRANCH"
  exit 0
fi

# ---------------------------------------------------------------------------
# Only enforce when commit is from bmad-vault-bridge/11.11crystallize --apply
# (env-var or flag-file). Human edits + vault-autosave + manual commits must
# NOT be blocked.
# ---------------------------------------------------------------------------
CRYS_FLAG="$VAULT_ROOT/.vault-ko/.crystallize-in-progress"
if [[ "${CRYSTALLIZE_APPLYING:-0}" != "1" ]] && [[ ! -f "$CRYS_FLAG" ]]; then
  exit 0
fi

STAGED=$(git diff --cached --name-only --diff-filter=ACMR)
if [[ -z "$STAGED" ]]; then
  exit 0
fi

# ---------------------------------------------------------------------------
# Layer 3a — schema-migration victim-watch (post-2026-05-20)
# Chains to the standalone schema-migration-watch hook if it exists. Triggers
# only when a schema-migration ADR or migrate-*.py script is staged.
# ---------------------------------------------------------------------------
SCHEMA_HOOK="$VAULT_ROOT/.git/hooks/pre-commit-schema-migration-watch.sh"
if [[ -x "$SCHEMA_HOOK" ]]; then
  if ! bash "$SCHEMA_HOOK"; then
    exit $?
  fi
fi

# ---------------------------------------------------------------------------
# Layer 3 — forbidden-target deny-list
# ---------------------------------------------------------------------------
VIOLATIONS=()
while IFS= read -r file; do
  for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if echo "$file" | grep -qE "$pattern"; then
      VIOLATIONS+=("$file  (matches /$pattern/)")
      break
    fi
  done
done <<< "$STAGED"

if (( ${#VIOLATIONS[@]} > 0 )); then
  echo "🚫 BLOCKED: bmad-vault-bridge forbidden-target commit on non-sandbox branch ($BRANCH)"
  echo ""
  echo "These files are protected from auto-mutation:"
  for v in "${VIOLATIONS[@]}"; do
    echo "  • $v"
  done
  echo ""
  echo "Options:"
  echo "  1. Revert the staged change for these files (intended for human edits, not auto-prop)"
  echo "  2. Switch to a crystallize-sandbox-* branch if this is an experimental run"
  echo "  3. Emergency override: SKIP_CRYSTALLIZE_HOOK=1 git commit ..."
  exit 1
fi

# ---------------------------------------------------------------------------
# Layer 4 — Critic review
#
# Default (VAULT_CRITIC_ACTIVE != 1): deterministic 4-rule stub.
#   Rule 1: bullet must be supplied via env CRITIC_BULLET (else fall-open)
#   Rule 2: target must match staged files
#   Rule 3: diff size <=  CRITIC_MAX_DIFF_LINES (default 200) when env set
#   Rule 4: forbidden-target check already passed (above)
#
# Real-LLM mode (VAULT_CRITIC_ACTIVE=1): invoke critic-review.py and
# require verdict == "pass". Subagent must have already written the
# response.json (typically via the crystallize-pending skill).
# ---------------------------------------------------------------------------
if [[ "${VAULT_CRITIC_ACTIVE:-0}" == "1" ]]; then
  if [[ ! -x "$CRITIC_RUNNER" ]]; then
    echo "⚠️  VAULT_CRITIC_ACTIVE=1 but runner missing/not-executable: $CRITIC_RUNNER"
    echo "    Falling through to deterministic stub."
  elif [[ -z "${CRITIC_BULLET:-}" ]] || [[ -z "${CRITIC_TARGET:-}" ]]; then
    echo "⚠️  VAULT_CRITIC_ACTIVE=1 but CRITIC_BULLET/CRITIC_TARGET env missing"
    echo "    Falling through to deterministic stub."
  else
    CRITIC_MODE="${VAULT_CRITIC_MODE:-strict}"
    CRITIC_TIMEOUT="${VAULT_CRITIC_TIMEOUT:-300}"
    DIFF_TEXT="$(git diff --cached -- "$CRITIC_TARGET" 2>/dev/null || true)"
    if "$CRITIC_RUNNER" \
        --target "$CRITIC_TARGET" \
        --bullet "$CRITIC_BULLET" \
        --diff "$DIFF_TEXT" \
        --mode "$CRITIC_MODE" \
        --timeout "$CRITIC_TIMEOUT" > /tmp/critic-out.$$ 2>&1; then
      echo "✅ Critic Layer-4 pass (mode=$CRITIC_MODE)"
    else
      echo "🚫 Critic Layer-4 FAIL (mode=$CRITIC_MODE) — commit blocked"
      cat /tmp/critic-out.$$ || true
      rm -f /tmp/critic-out.$$
      exit 1
    fi
    rm -f /tmp/critic-out.$$
  fi
else
  # Deterministic 4-rule stub (back-compat). Logs only, never blocks here —
  # the forbidden-target check above already handled Rule 4.
  if [[ -n "${CRITIC_BULLET:-}" ]] && [[ -n "${AUDIT_LOG:-}" ]]; then
    mkdir -p "$(dirname "$AUDIT_LOG")" 2>/dev/null || true
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    printf '{"ts":"%s","mode":"stub","branch":"%s","target":"%s","verdict":"pass"}\n' \
      "$TS" "$BRANCH" "${CRITIC_TARGET:-unknown}" >> "$AUDIT_LOG" 2>/dev/null || true
  fi
fi

exit 0

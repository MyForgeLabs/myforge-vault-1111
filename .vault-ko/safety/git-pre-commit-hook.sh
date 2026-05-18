#!/usr/bin/env bash
#
# 11.11crystallize --apply safety-gate Layer 3 — git pre-commit forbidden-targets.
#
# ADR: 07-Decisions/2026-05-12 sv-5 crystallization automation arch.md
# Playbook: 11-wiki/multi-layer-safety-gate.md
#
# Install (symlink, do NOT copy):
#   cd /root/obsidian-vault
#   ln -sf .vault-ko/safety/git-pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .vault-ko/safety/git-pre-commit-hook.sh
#
# Override (emergency only — explicit + audited):
#   SKIP_CRYSTALLIZE_HOOK=1 git commit ...
#
# Status: SKELETON 2026-05-17 — installed, but `--apply` real-mode not live yet.
# The hook is harmless until 11.11crystallize starts writing vault files.

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

# Sandbox-branch escape: crystallize-sandbox-* branches bypass forbidden-targets
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
case "$BRANCH" in
  crystallize-sandbox-*|rsi-sandbox-*|rsi-pareto-*)
    exit 0
    ;;
esac

# Emergency override (audited via shell history)
if [[ "${SKIP_CRYSTALLIZE_HOOK:-0}" == "1" ]]; then
  echo "⚠️  crystallize hook bypassed (SKIP_CRYSTALLIZE_HOOK=1) — branch=$BRANCH"
  exit 0
fi

# Only enforce when commit is from 11.11crystallize --apply (env-var or flag-file).
# Human edits + vault-autosave + manual commits must NOT be blocked.
CRYS_FLAG="$(git rev-parse --show-toplevel 2>/dev/null)/.vault-ko/.crystallize-in-progress"
if [[ "${CRYSTALLIZE_APPLYING:-0}" != "1" ]] && [[ ! -f "$CRYS_FLAG" ]]; then
  exit 0
fi

STAGED=$(git diff --cached --name-only --diff-filter=ACMR)
if [[ -z "$STAGED" ]]; then
  exit 0
fi

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
  echo "🚫 BLOCKED: 11.11crystallize forbidden-target commit on non-sandbox branch ($BRANCH)"
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

exit 0

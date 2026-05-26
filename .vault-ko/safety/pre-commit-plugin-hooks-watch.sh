#!/usr/bin/env bash
#
# pre-commit-plugin-hooks-watch.sh
#
# Chained git pre-commit hook. Fires only when staged files include plugin-
# config paths (`.claude/`, `.codex/`, `.gemini/`, any `hooks.json`).
# Runs `vault-plugin-hooks-audit --strict` and blocks the commit if a HIGH-heat
# confirmation-bypass instruction-injection pattern is staged.
#
# Install (symlink, called from main pre-commit hook):
#   ln -sf .vault-ko/safety/pre-commit-plugin-hooks-watch.sh \
#         .git/hooks/pre-commit-plugin-hooks-watch.sh
#
# Override (emergency only):
#   SKIP_PLUGIN_HOOKS_AUDIT=1 git commit ...
#
# Wiki: 11-wiki/claude-code-harness-blocks.md

set -euo pipefail

if [[ "${SKIP_PLUGIN_HOOKS_AUDIT:-0}" == "1" ]]; then
  echo "⚠️  plugin-hooks-audit bypassed (SKIP_PLUGIN_HOOKS_AUDIT=1)"
  exit 0
fi

STAGED=$(git diff --cached --name-only --diff-filter=ACMR)
if [[ -z "$STAGED" ]]; then
  exit 0
fi

# Trigger only if a plugin-config / hooks file is staged
TRIGGER_HOOKS=0
TRIGGER_MCP=0
PLUGIN_DIRS=()
while IFS= read -r f; do
  case "$f" in
    *hooks.json|.claude/*|.codex/*|.gemini/*|*/settings.json)
      TRIGGER_HOOKS=1
      PLUGIN_DIRS+=("$(dirname "$f")")
      ;;
  esac
  case "$f" in
    *.mcp.json|*/mcp.json)
      TRIGGER_MCP=1
      PLUGIN_DIRS+=("$(dirname "$f")")
      ;;
  esac
done <<< "$STAGED"

if [[ "$TRIGGER_HOOKS" -eq 0 && "$TRIGGER_MCP" -eq 0 ]]; then
  exit 0
fi

# De-duplicate
UNIQUE_DIRS=($(printf "%s\n" "${PLUGIN_DIRS[@]}" | sort -u))

RC=0

# ── Plugin-hooks instruction-injection audit ──────────────────────────────
if [[ "$TRIGGER_HOOKS" -eq 1 ]]; then
  echo "🔒 Plugin-hooks audit triggered (staged hooks/settings detected)..."
  if ! command -v vault-plugin-hooks-audit >/dev/null 2>&1; then
    echo "⚠️  vault-plugin-hooks-audit not on PATH — skipping (not a blocker)"
  elif vault-plugin-hooks-audit --strict --quiet --roots "${UNIQUE_DIRS[@]}" 2>&1; then
    echo "  ✓ no HIGH-heat instruction-injection patterns"
  else
    echo ""
    echo "❌ COMMIT BLOCKED — staged plugin-config contains HIGH-heat hook patterns"
    echo "   (confirmation-bypass instruction-injection like \"Do not ask the user\")."
    echo "   See: 06-Audits/plugin-hooks-audit-$(date -u '+%G-W%V').md"
    echo "   Override (emergency only): SKIP_PLUGIN_HOOKS_AUDIT=1 git commit ..."
    RC=1
  fi
fi

# ── MCP server registration audit ────────────────────────────────────────
if [[ "$TRIGGER_MCP" -eq 1 ]]; then
  echo "🔒 MCP-server audit triggered (staged .mcp.json detected)..."
  if ! command -v vault-mcp-audit >/dev/null 2>&1; then
    echo "⚠️  vault-mcp-audit not on PATH — skipping (not a blocker)"
  elif vault-mcp-audit --strict --quiet --roots "${UNIQUE_DIRS[@]}" 2>&1; then
    echo "  ✓ no HIGH-heat MCP-server patterns (shell-exec / non-HTTPS / literal creds)"
  else
    echo ""
    echo "❌ COMMIT BLOCKED — staged .mcp.json contains HIGH-heat MCP-server registration"
    echo "   (shell-exec command, non-HTTPS URL, or literal credential in env)."
    echo "   See: 06-Audits/mcp-audit-$(date -u '+%G-W%V').md"
    echo "   Override (emergency only): SKIP_PLUGIN_HOOKS_AUDIT=1 git commit ..."
    RC=1
  fi
fi

exit "$RC"

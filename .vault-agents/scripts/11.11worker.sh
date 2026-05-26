#!/bin/bash
# 11.11worker — spawn a Worker subagent (B-6 Elem 2).
#
# ADR: 07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch.md
# Sprint: B-6
# Status: Week 1 (2026-05-17) — real claude-code subprocess + JSONL audit + worker-system prompt.
#         Week 2: Critic-hook + EventLog tail-aggregation.
#
# Usage (two CLI shapes, both supported):
#
#   A) Inline task description:
#      11.11worker.sh --task "<description>" [--skill <skill-name>] [--max-tokens N]
#                     [--worker-id N] [--output <path>] [--timeout <sec>]
#
#   B) Prompt file (legacy Week 1-α shape):
#      11.11worker.sh <task-prompt-file> [--worker-id N] [--output <path>] [--timeout <sec>]
#
# Behavior:
#   - Spawns `claude -p` non-interactive subprocess
#   - Appends `.vault-agents/prompts/worker-system.md` via --append-system-prompt
#   - If --skill X given, prepends "Invoke skill: /X" hint to user message
#   - If --max-tokens N given, advisory cap added to user message (claude CLI has no hard cap flag in -p)
#   - AGENT=worker-<id> env var → commit/event-log tagging
#   - JSONL audit row written to .vault-agents/runs/<uuid>.jsonl (input, output-path, wall-clock, exit, stdout-bytes, est-tokens)
#   - Default 5-min timeout, configurable
#
# Exit codes:
#   0   = worker completed successfully
#   1   = usage error / claude CLI missing / prompt source missing
#   2   = worker exited non-zero
#   124 = timeout

set -uo pipefail

# --- defaults ---
PROMPT_FILE=""
TASK_INLINE=""
SKILL=""
MAX_TOKENS=""
WORKER_ID="1"
OUTPUT_PATH=""
TIMEOUT_SEC="300"

VAULT_AGENTS_DIR="/root/obsidian-vault/.vault-agents"
SYSTEM_PROMPT_FILE="${VAULT_AGENTS_DIR}/prompts/worker-system.md"
RUNS_DIR="${VAULT_AGENTS_DIR}/runs"

usage() {
  cat >&2 <<EOF
Usage:
  11.11worker.sh --task "<description>" [--skill <name>] [--max-tokens N]
                 [--worker-id N] [--output <path>] [--timeout <sec>]
  11.11worker.sh <task-prompt-file>     [--worker-id N] [--output <path>] [--timeout <sec>]

Options:
  --task <str>           Inline task description (alternative to <task-prompt-file>).
  --skill <name>         Skill to invoke (e.g. bmad-distillator). Hinted to worker.
  --max-tokens N         Advisory response cap (worker is told to stay under N).
  --worker-id N          Worker identifier (default: 1). Sets AGENT=worker-N.
  --output <path>        Capture formatted output to file (default: print to stdout).
  --timeout <sec>        Max wall-clock seconds (default: 300).

System prompt appended from: ${SYSTEM_PROMPT_FILE}
Audit JSONL written to:      ${RUNS_DIR}/<uuid>.jsonl
EOF
  exit 1
}

# --- parse args ---
if [[ $# -lt 1 ]]; then
  usage
fi

# First positional may be a prompt-file path (legacy) or the first flag (new).
if [[ "$1" != --* && "$1" != -* ]]; then
  PROMPT_FILE="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)
      TASK_INLINE="$2"; shift 2 ;;
    --skill)
      SKILL="$2"; shift 2 ;;
    --max-tokens)
      MAX_TOKENS="$2"; shift 2 ;;
    --worker-id)
      WORKER_ID="$2"; shift 2 ;;
    --output)
      OUTPUT_PATH="$2"; shift 2 ;;
    --timeout)
      TIMEOUT_SEC="$2"; shift 2 ;;
    -h|--help)
      usage ;;
    *)
      echo "Error: unknown option: $1" >&2
      usage ;;
  esac
done

# --- resolve prompt source ---
if [[ -n "$PROMPT_FILE" && -n "$TASK_INLINE" ]]; then
  echo "Error: provide either a prompt-file or --task, not both." >&2
  exit 1
fi
if [[ -z "$PROMPT_FILE" && -z "$TASK_INLINE" ]]; then
  echo "Error: missing task source. Use --task \"...\" or a prompt-file path." >&2
  usage
fi

if [[ -n "$PROMPT_FILE" ]]; then
  if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: prompt file not found: $PROMPT_FILE" >&2
    exit 1
  fi
  USER_MSG="$(cat "$PROMPT_FILE")"
  PROMPT_SOURCE="$PROMPT_FILE"
else
  USER_MSG="$TASK_INLINE"
  PROMPT_SOURCE="(inline --task)"
fi

# Prepend skill hint + max-tokens advisory.
PREAMBLE=""
if [[ -n "$SKILL" ]]; then
  PREAMBLE+="**Skill:** invokáld a Skill tool-lal: \`/${SKILL}\` (Level-2 instructions only).\n\n"
fi
if [[ -n "$MAX_TOKENS" ]]; then
  PREAMBLE+="**Output limit:** maradj ${MAX_TOKENS} token alatt.\n\n"
fi
if [[ -n "$PREAMBLE" ]]; then
  USER_MSG="${PREAMBLE}---\n\n${USER_MSG}"
fi

# --- preflight ---
CLAUDE_BIN="$(command -v claude || true)"
if [[ -z "$CLAUDE_BIN" ]]; then
  echo "Error: claude CLI not found in PATH." >&2
  exit 1
fi

if [[ ! -f "$SYSTEM_PROMPT_FILE" ]]; then
  echo "Error: worker-system prompt missing: $SYSTEM_PROMPT_FILE" >&2
  exit 1
fi

if [[ -z "$USER_MSG" ]]; then
  echo "Error: empty task message." >&2
  exit 1
fi

mkdir -p "$RUNS_DIR"

# --- spawn worker ---
export AGENT="worker-${WORKER_ID}"
RUN_UUID="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c 'import uuid;print(uuid.uuid4())')"
AUDIT_FILE="${RUNS_DIR}/${RUN_UUID}.jsonl"

START_TS="$(date -u +%FT%TZ)"
START_EPOCH="$(date +%s)"

SYSTEM_PROMPT_CONTENT="$(cat "$SYSTEM_PROMPT_FILE")"

echo "[11.11worker] worker-${WORKER_ID} | uuid=${RUN_UUID} | prompt=${PROMPT_SOURCE} | skill=${SKILL:-none} | timeout=${TIMEOUT_SEC}s | start=${START_TS}" >&2

TMP_OUT="$(mktemp)"
TMP_ERR="$(mktemp)"

# Default toolset: text-only smoke (no write). Override by exporting WORKER_TOOLS.
# (User policy: bypassPermissions default-deny.)
WORKER_TOOLS="${WORKER_TOOLS:-Bash(date *),Bash(echo *)}"

set +e
timeout --preserve-status --signal=TERM "${TIMEOUT_SEC}" \
  "$CLAUDE_BIN" -p "$USER_MSG" \
    --append-system-prompt "$SYSTEM_PROMPT_CONTENT" \
    --output-format text \
    --allowedTools "$WORKER_TOOLS" \
    >"$TMP_OUT" 2>"$TMP_ERR"
RC=$?
set -e

END_TS="$(date -u +%FT%TZ)"
END_EPOCH="$(date +%s)"
WALL_SEC=$(( END_EPOCH - START_EPOCH ))

STDOUT_BYTES=$(wc -c < "$TMP_OUT" | tr -d ' ')
STDOUT_WORDS=$(wc -w < "$TMP_OUT" | tr -d ' ')
# Rough token estimate: ~1.3 tokens per word (English-ish), used only for audit.
EST_TOKENS=$(( (STDOUT_WORDS * 13 + 9) / 10 ))

# Build formatted output (Markdown wrapper)
{
  echo "# Worker output"
  echo ""
  echo "- worker-id: ${WORKER_ID}"
  echo "- run-uuid: ${RUN_UUID}"
  echo "- agent-tag: ${AGENT}"
  echo "- prompt-source: ${PROMPT_SOURCE}"
  echo "- skill: ${SKILL:-none}"
  echo "- max-tokens-advisory: ${MAX_TOKENS:-none}"
  echo "- start: ${START_TS}"
  echo "- end: ${END_TS}"
  echo "- wall-clock-sec: ${WALL_SEC}"
  echo "- exit-code: ${RC}"
  echo "- stdout-bytes: ${STDOUT_BYTES}"
  echo "- est-tokens: ${EST_TOKENS}"
  echo ""
  echo "## stdout"
  echo ""
  echo '```'
  cat "$TMP_OUT"
  echo '```'
  if [[ -s "$TMP_ERR" ]]; then
    echo ""
    echo "## stderr"
    echo ""
    echo '```'
    cat "$TMP_ERR"
    echo '```'
  fi
} > "${TMP_OUT}.formatted"

if [[ -n "$OUTPUT_PATH" ]]; then
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  cp "${TMP_OUT}.formatted" "$OUTPUT_PATH"
  echo "[11.11worker] output written to: $OUTPUT_PATH" >&2
else
  cat "${TMP_OUT}.formatted"
fi

# --- JSONL audit row ---
# One JSON object per file (single-event), JSONL convention.
python3 - "$AUDIT_FILE" "$RUN_UUID" "$WORKER_ID" "$AGENT" "$PROMPT_SOURCE" "$SKILL" \
  "$MAX_TOKENS" "$START_TS" "$END_TS" "$WALL_SEC" "$RC" "$STDOUT_BYTES" "$EST_TOKENS" \
  "$OUTPUT_PATH" "${TMP_OUT}.formatted" <<'PYEOF'
import json, sys
sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
from vault_atomic import atomic_append_jsonl
(audit_file, run_uuid, worker_id, agent, prompt_source, skill, max_tokens,
 start_ts, end_ts, wall_sec, rc, stdout_bytes, est_tokens,
 output_path, formatted_out) = sys.argv[1:]

stdout_head = ""
try:
    with open(formatted_out, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
        stdout_head = text[:400]
except Exception:
    pass

row = {
    "event": "worker_run",
    "run_uuid": run_uuid,
    "worker_id": worker_id,
    "agent_tag": agent,
    "prompt_source": prompt_source,
    "skill": skill or None,
    "max_tokens_advisory": int(max_tokens) if max_tokens else None,
    "start_ts": start_ts,
    "end_ts": end_ts,
    "wall_clock_sec": int(wall_sec),
    "exit_code": int(rc),
    "stdout_bytes": int(stdout_bytes),
    "est_tokens": int(est_tokens),
    "output_path": output_path or None,
    "output_head_400": stdout_head,
}
atomic_append_jsonl(audit_file, row)
PYEOF

rm -f "$TMP_OUT" "$TMP_ERR" "${TMP_OUT}.formatted"

echo "[11.11worker] audit: $AUDIT_FILE (wall=${WALL_SEC}s, exit=${RC}, est-tokens=${EST_TOKENS})" >&2

if [[ $RC -eq 124 ]]; then
  echo "[11.11worker] TIMEOUT after ${TIMEOUT_SEC}s (worker-${WORKER_ID})" >&2
  exit 124
elif [[ $RC -ne 0 ]]; then
  echo "[11.11worker] worker-${WORKER_ID} exited with code $RC" >&2
  exit 2
fi

echo "[11.11worker] worker-${WORKER_ID} completed successfully" >&2
exit 0

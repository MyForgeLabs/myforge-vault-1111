#!/bin/bash
# 11.11summarizer — Weekly vault-state synthesis agent (B-6 Elem 4).
#
# ADR: 07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch.md
# Sprint: B-6 Week 2 (skeleton activation, 2026-05-19)
#
# Two modes:
#   A) --weekly       : Sample N random sessions from 08-Sessions/ → synthesize weekly
#                       summary → write to 06-Audits/weekly-summary-YYYY-WWN.md
#   B) --inputs <csv> : Synthesize across explicitly given input markdown files
#                       (e.g. worker outputs from an orchestrated task).
#
# Usage:
#   11.11summarizer.sh --weekly [--sample N] [--output <path>] [--timeout <sec>]
#   11.11summarizer.sh --inputs "<f1.md,f2.md,...>" [--output <path>] [--timeout <sec>]
#
# Output: a markdown summary (executive summary + per-source status + convergent insights).
#
# Exit codes:
#   0 = success
#   1 = usage error
#   2 = synthesis failed (LLM error)
#   124 = timeout

set -uo pipefail

MODE=""
SAMPLE_N="5"
INPUTS_CSV=""
OUTPUT_PATH=""
TIMEOUT_SEC="300"

VAULT_AGENTS_DIR="/root/obsidian-vault/.vault-agents"
SUMMARIZER_PROMPT="${VAULT_AGENTS_DIR}/prompts/summarizer.md"
SESSIONS_DIR="/root/obsidian-vault/08-Sessions"
AUDITS_DIR="/root/obsidian-vault/06-Audits"
RUNS_DIR="${VAULT_AGENTS_DIR}/runs"

usage() {
  cat >&2 <<EOF
Usage:
  11.11summarizer.sh --weekly [--sample N] [--output <path>] [--timeout <sec>]
  11.11summarizer.sh --inputs "<f1,f2,...>" [--output <path>] [--timeout <sec>]

Options:
  --weekly          Sample N random session markdowns → write weekly audit.
  --sample N        Sample size for --weekly (default: 5).
  --inputs <csv>    Explicit input markdown files (CSV).
  --output <path>   Output path (default for weekly: 06-Audits/weekly-summary-YYYY-WWN.md;
                                  default for inputs: stdout).
  --timeout <sec>   LLM timeout (default: 300).
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --weekly)   MODE="weekly"; shift ;;
    --sample)   SAMPLE_N="$2"; shift 2 ;;
    --inputs)   MODE="inputs"; INPUTS_CSV="$2"; shift 2 ;;
    --output)   OUTPUT_PATH="$2"; shift 2 ;;
    --timeout)  TIMEOUT_SEC="$2"; shift 2 ;;
    -h|--help)  usage ;;
    *)          echo "Error: unknown option: $1" >&2; usage ;;
  esac
done

[[ -z "$MODE" ]] && { echo "Error: --weekly or --inputs required" >&2; usage; }

mkdir -p "$RUNS_DIR"
RUN_UUID="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c 'import uuid;print(uuid.uuid4())')"
AUDIT_FILE="${RUNS_DIR}/summarizer-${RUN_UUID}.jsonl"
START_TS="$(date -u +%FT%TZ)"
START_EPOCH="$(date +%s)"

# --- Resolve input files ---
INPUT_FILES=()
if [[ "$MODE" == "weekly" ]]; then
  mapfile -t ALL_SESSIONS < <(find "$SESSIONS_DIR" -maxdepth 1 -type f -name "*.md" \
                              -not -path "*_archive*" | shuf | head -n "$SAMPLE_N")
  if [[ ${#ALL_SESSIONS[@]} -eq 0 ]]; then
    echo "Error: no session markdowns found in $SESSIONS_DIR" >&2
    exit 2
  fi
  INPUT_FILES=("${ALL_SESSIONS[@]}")
  # default output: 06-Audits/weekly-summary-YYYY-WWN.md
  if [[ -z "$OUTPUT_PATH" ]]; then
    YEAR_WEEK="$(date +%Y-W%V)"
    OUTPUT_PATH="${AUDITS_DIR}/weekly-summary-${YEAR_WEEK}.md"
  fi
else
  IFS=',' read -ra ARR <<< "$INPUTS_CSV"
  for f in "${ARR[@]}"; do
    f_trim="$(echo "$f" | xargs)"
    [[ ! -f "$f_trim" ]] && { echo "Error: input not found: $f_trim" >&2; exit 1; }
    INPUT_FILES+=("$f_trim")
  done
fi

INPUT_COUNT=${#INPUT_FILES[@]}
echo "[11.11summarizer] mode=${MODE} | inputs=${INPUT_COUNT} | output=${OUTPUT_PATH:-stdout} | uuid=${RUN_UUID}" >&2

# --- Build synthesis prompt ---
PROMPT_FILE="$(mktemp)"
{
  echo "Te egy Summarizer-agent vagy egy SV B-6 multi-agent vault-feladatban."
  echo ""
  if [[ "$MODE" == "weekly" ]]; then
    echo "MODE: weekly — ${INPUT_COUNT} véletlen session-MD-ből gyártsd a heti vault-state summary-t."
    echo "Date: $(date +%Y-%m-%d) (W$(date +%V))"
  else
    echo "MODE: inputs — ${INPUT_COUNT} worker-output-ot convergent-synthesizel egyetlen reportá."
  fi
  echo ""
  echo "Princípium (lásd .vault-agents/prompts/summarizer.md):"
  echo "- Convergent synthesis NEM konkatenáció — döntsd el mit emelsz ki/egyesítesz/hagysz ki"
  echo "- Source-grounded — minden állítást citálj [S1], [S2], ... source-ID-vel"
  echo "- Executive summary (max 200 token) + per-source-státusz + convergent insights"
  echo ""
  echo "Reply FORMAT (markdown, ez a structure):"
  echo ""
  echo "## Executive summary"
  echo ""
  echo "(max 200 token narratíva)"
  echo ""
  echo "## Per-source status"
  echo ""
  echo "| ID | Source | Date | Key outcome |"
  echo "|---|---|---|---|"
  echo "| S1 | <basename> | <date-if-discernible> | <1-mondat> |"
  echo "..."
  echo ""
  echo "## Convergent insights"
  echo ""
  echo "- Common pattern: ... [S1, S3]"
  echo "- Divergent: ... [S2]"
  echo "- Open question: ..."
  echo ""
  echo "## Sources"
  echo ""
  echo "- S1: <path>"
  echo "..."
  echo ""
  echo "---"
  echo ""
  echo "INPUT SOURCES:"
  echo ""
  i=0
  for f in "${INPUT_FILES[@]}"; do
    i=$((i+1))
    echo "### S${i}: ${f}"
    echo ""
    # Cap each input at 8000 chars to stay within reasonable prompt size
    head -c 8000 "$f"
    echo ""
    echo "---"
    echo ""
  done
} > "$PROMPT_FILE"

# --- Spawn claude -p ---
CLAUDE_BIN="$(command -v claude || true)"
if [[ -z "$CLAUDE_BIN" ]]; then
  echo "Error: claude CLI not found" >&2
  rm -f "$PROMPT_FILE"
  exit 2
fi

TMP_OUT="$(mktemp)"
TMP_ERR="$(mktemp)"
set +e
timeout --preserve-status --signal=TERM "${TIMEOUT_SEC}" \
  "$CLAUDE_BIN" -p "$(cat "$PROMPT_FILE")" \
    --output-format text \
    --allowedTools "Bash(date *)" \
    >"$TMP_OUT" 2>"$TMP_ERR"
RC=$?
set -e

END_TS="$(date -u +%FT%TZ)"
END_EPOCH="$(date +%s)"
WALL_SEC=$(( END_EPOCH - START_EPOCH ))

if [[ $RC -eq 124 ]]; then
  echo "[11.11summarizer] TIMEOUT after ${TIMEOUT_SEC}s" >&2
  rm -f "$PROMPT_FILE" "$TMP_OUT" "$TMP_ERR"
  exit 124
elif [[ $RC -ne 0 ]]; then
  echo "[11.11summarizer] LLM exited $RC" >&2
  cat "$TMP_ERR" >&2
  rm -f "$PROMPT_FILE" "$TMP_OUT" "$TMP_ERR"
  exit 2
fi

# --- Wrap output ---
WRAPPED="$(mktemp)"
{
  echo "---"
  echo "name: weekly-summary-$(date +%Y-W%V)"
  echo "type: audit"
  echo "created: $(date -u +%FT%TZ)"
  echo "updated: $(date -u +%FT%TZ)"
  echo "tags: [audit, weekly-summary, b-6-summarizer]"
  echo "summarizer_uuid: ${RUN_UUID}"
  echo "input_count: ${INPUT_COUNT}"
  echo "mode: ${MODE}"
  echo "---"
  echo ""
  echo "# Weekly vault-state summary ($(date +%Y-%m-%d), W$(date +%V))"
  echo ""
  echo "> [!info] Auto-generated by \`11.11summarizer.sh\` (B-6 Elem 4)"
  echo "> Mode: ${MODE} | Sources: ${INPUT_COUNT} | Wall: ${WALL_SEC}s"
  echo ""
  cat "$TMP_OUT"
} > "$WRAPPED"

if [[ -n "$OUTPUT_PATH" ]]; then
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  cp "$WRAPPED" "$OUTPUT_PATH"
  echo "[11.11summarizer] output written to: $OUTPUT_PATH" >&2
else
  cat "$WRAPPED"
fi

# --- JSONL audit (env-var passing, safe) ---
INPUTS_JSON=$(printf '%s\n' "${INPUT_FILES[@]}" | python3 -c 'import sys,json;print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')
export _SU_UUID="$RUN_UUID"
export _SU_MODE="$MODE"
export _SU_SAMPLE="$SAMPLE_N"
export _SU_COUNT="$INPUT_COUNT"
export _SU_FILES="$INPUTS_JSON"
export _SU_OUT="$OUTPUT_PATH"
export _SU_STS="$START_TS"
export _SU_ETS="$END_TS"
export _SU_WS="$WALL_SEC"
export _SU_RC="$RC"
python3 - "$AUDIT_FILE" <<'PYEOF'
import json, sys, os
sys.path.insert(0, "/root/obsidian-vault/.vault-tools/lib")
from vault_atomic import atomic_append_jsonl
audit = sys.argv[1]
row = {
  "event": "summarizer_run",
  "run_uuid": os.environ["_SU_UUID"],
  "mode": os.environ["_SU_MODE"],
  "sample_n": int(os.environ["_SU_SAMPLE"]),
  "input_count": int(os.environ["_SU_COUNT"]),
  "input_files": json.loads(os.environ.get("_SU_FILES", "[]")),
  "output_path": os.environ.get("_SU_OUT", "") or None,
  "start_ts": os.environ["_SU_STS"],
  "end_ts": os.environ["_SU_ETS"],
  "wall_clock_sec": int(os.environ["_SU_WS"]),
  "exit_code": int(os.environ["_SU_RC"])
}
atomic_append_jsonl(audit, row)
PYEOF

rm -f "$PROMPT_FILE" "$TMP_OUT" "$TMP_ERR" "$WRAPPED"

echo "[11.11summarizer] audit: $AUDIT_FILE (wall=${WALL_SEC}s, exit=${RC})" >&2
exit 0

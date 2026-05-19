#!/bin/bash
# 11.11critic — Constitutional-AI review agent for worker outputs (B-6 Elem 3).
#
# ADR: 07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch.md
# Sprint: B-6 Week 2 (skeleton activation, 2026-05-19)
#
# Function: 4-layer safety-gate review of a worker output file.
#   Layer 1: ENV-flag check  (CRITIC_DISABLED=1 → skip-approve)
#   Layer 2: forbidden-target check (AGENTS.md / 00-Meta / .vault-* / 11.11*)
#   Layer 3: git pre-commit-hook gate signal (advisory; no actual commit here)
#   Layer 4: Critic-review LLM (claude -p subprocess, Constitutional-AI minta)
#
# Usage:
#   11.11critic.sh --input <worker-output-file> [--targets "<path1,path2>"]
#                  [--review-id N] [--output <path>] [--timeout <sec>]
#                  [--red-team] [--mock]
#
# Output (JSON to stdout or --output file):
#   {
#     "verdict": "approve" | "reject" | "batch_preview",
#     "confidence": 0.0-1.0,
#     "reasoning": "...",
#     "concerns": [ {"type":"...","detail":"..."} ],
#     "layer_results": {
#        "env_flag": "pass|skip",
#        "forbidden_target": "pass|fail",
#        "git_hook_signal": "pass|advisory_block",
#        "llm_review": "approve|reject|batch_preview|skipped"
#     }
#   }
#
# JSONL audit: .vault-agents/runs/critic-<uuid>.jsonl
#
# Exit codes:
#   0   = approve
#   2   = reject (any layer failed)
#   3   = batch_preview (LLM low-confidence)
#   124 = timeout
#   1   = usage error

set -uo pipefail

INPUT=""
TARGETS=""
REVIEW_ID="1"
OUTPUT_PATH=""
TIMEOUT_SEC="120"
RED_TEAM="0"
MOCK="0"

VAULT_AGENTS_DIR="/root/obsidian-vault/.vault-agents"
CRITIC_PROMPT="${VAULT_AGENTS_DIR}/prompts/critic.md"
RUNS_DIR="${VAULT_AGENTS_DIR}/runs"

# Forbidden-target patterns (Layer 2)
FORBIDDEN_PATTERNS=(
  "AGENTS.md"
  "00-Meta/"
  ".vault-agents/"
  ".vault-ko/"
  ".vault-tools/"
  "/usr/local/bin/11.11"
  "/root/.claude/CLAUDE.md"
  ".claude/CLAUDE.md"
  "/root/.codex/AGENTS.md"
  "/root/.gemini/GEMINI.md"
)

usage() {
  cat >&2 <<EOF
Usage:
  11.11critic.sh --input <worker-output-file> [--targets "<csv-paths>"]
                 [--review-id N] [--output <path>] [--timeout <sec>]
                 [--red-team] [--mock]

Options:
  --input <path>      Worker output (markdown) to review. REQUIRED.
  --targets <csv>     Comma-separated file paths the worker proposes to touch
                      (for Layer-2 forbidden-target check).
  --review-id N       Critic review identifier (default: 1).
  --output <path>     Write verdict-JSON to file (default: stdout).
  --timeout <sec>     LLM-review timeout (default: 120).
  --red-team          Force red-team mode (skeptical perspective).
  --mock              Skip LLM call; deterministic rule-based verdict only.
                      Useful for smoke / CI.

Exit: 0=approve  2=reject  3=batch_preview  124=timeout  1=usage
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)     INPUT="$2"; shift 2 ;;
    --targets)   TARGETS="$2"; shift 2 ;;
    --review-id) REVIEW_ID="$2"; shift 2 ;;
    --output)    OUTPUT_PATH="$2"; shift 2 ;;
    --timeout)   TIMEOUT_SEC="$2"; shift 2 ;;
    --red-team)  RED_TEAM="1"; shift ;;
    --mock)      MOCK="1"; shift ;;
    -h|--help)   usage ;;
    *)           echo "Error: unknown option: $1" >&2; usage ;;
  esac
done

[[ -z "$INPUT" ]] && { echo "Error: --input required" >&2; usage; }
[[ ! -f "$INPUT" ]] && { echo "Error: input file not found: $INPUT" >&2; exit 1; }

mkdir -p "$RUNS_DIR"
RUN_UUID="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c 'import uuid;print(uuid.uuid4())')"
AUDIT_FILE="${RUNS_DIR}/critic-${RUN_UUID}.jsonl"
START_TS="$(date -u +%FT%TZ)"
START_EPOCH="$(date +%s)"

# --- Layer 1: ENV-flag check ---
LAYER1="pass"
if [[ "${CRITIC_DISABLED:-0}" == "1" ]]; then
  LAYER1="skip"
fi

# --- Layer 2: forbidden-target check ---
LAYER2="pass"
LAYER2_HITS=""
if [[ -n "$TARGETS" ]]; then
  IFS=',' read -ra TGT_ARR <<< "$TARGETS"
  for tgt in "${TGT_ARR[@]}"; do
    tgt_trim="$(echo "$tgt" | xargs)"
    for pat in "${FORBIDDEN_PATTERNS[@]}"; do
      if [[ "$tgt_trim" == *"$pat"* ]]; then
        LAYER2="fail"
        LAYER2_HITS="${LAYER2_HITS}${tgt_trim} matches ${pat}; "
      fi
    done
  done
fi
# Also scan input content for forbidden-target mentions in write-context
INPUT_CONTENT="$(cat "$INPUT")"
for pat in "${FORBIDDEN_PATTERNS[@]}"; do
  # rough heuristic: look for "write" / "edit" / "modify" near forbidden pattern
  if echo "$INPUT_CONTENT" | grep -qE "(write|edit|modify|append|delete).{0,80}${pat}"; then
    LAYER2="fail"
    LAYER2_HITS="${LAYER2_HITS}content-mention: ${pat}; "
  fi
done

# --- Layer 3: git pre-commit-hook gate (advisory) ---
LAYER3="pass"
if [[ -d "/root/obsidian-vault/.git" ]]; then
  if [[ -x "/root/obsidian-vault/.git/hooks/pre-commit" ]]; then
    LAYER3="pass"  # hook exists; will run on actual commit
  else
    LAYER3="advisory_no_hook"
  fi
fi

# --- Layer 4: LLM Critic-review ---
LAYER4="skipped"
LLM_VERDICT="approve"
LLM_CONFIDENCE="1.0"
LLM_REASONING="(layer-4 skipped)"
LLM_CONCERNS="[]"
LLM_RC=0

if [[ "$MOCK" == "1" ]]; then
  # Mock mode: deterministic verdict based on layers 1-3 only
  LAYER4="mock_skipped"
  if [[ "$LAYER2" == "fail" ]]; then
    LLM_VERDICT="reject"
    LLM_CONFIDENCE="0.95"
    LLM_REASONING="Mock: forbidden-target hit."
  fi
else
  CLAUDE_BIN="$(command -v claude || true)"
  if [[ -z "$CLAUDE_BIN" ]]; then
    LAYER4="skipped_no_cli"
    LLM_REASONING="claude CLI not found; layers 1-3 verdict only."
  else
    # Build review prompt
    REVIEW_PROMPT_FILE="$(mktemp)"
    {
      echo "Te egy Critic-agent vagy egy SV B-6 multi-agent vault-feladatban."
      echo "A feladatod: review-zd az alábbi worker-output-ot Constitutional-AI minta szerint."
      echo ""
      echo "Princípiumok (lásd .vault-agents/prompts/critic.md):"
      echo "1. PII / titok / kred → reject"
      echo "2. Irreverzibilis → batch_preview"
      echo "3. Vault-konvenció-sértés (frontmatter, naming, Karpathy) → reject vagy batch_preview"
      echo "4. ADR-konfliktus → batch_preview"
      if [[ "$RED_TEAM" == "1" ]]; then
        echo "5. **RED-TEAM MODE ÉLES:** szándékosan keress érveket a mutation ELLEN."
      fi
      echo ""
      echo "Layer 1-3 előzetes eredmények (ne ismételd, csak vedd figyelembe):"
      echo "- env_flag: ${LAYER1}"
      echo "- forbidden_target: ${LAYER2} (${LAYER2_HITS:-none})"
      echo "- git_hook: ${LAYER3}"
      echo ""
      echo "Worker-output (review-zd):"
      echo "---"
      echo "$INPUT_CONTENT"
      echo "---"
      echo ""
      echo "Reply FORMAT (csak ez, semmi más, NO markdown fence):"
      echo '{"verdict":"approve|reject|batch_preview","confidence":0.0-1.0,"reasoning":"3-5 mondat","concerns":[{"type":"...","detail":"..."}]}'
    } > "$REVIEW_PROMPT_FILE"

    TMP_OUT="$(mktemp)"
    TMP_ERR="$(mktemp)"
    set +e
    timeout --preserve-status --signal=TERM "${TIMEOUT_SEC}" \
      "$CLAUDE_BIN" -p "$(cat "$REVIEW_PROMPT_FILE")" \
        --output-format text \
        --allowedTools "Bash(date *)" \
        >"$TMP_OUT" 2>"$TMP_ERR"
    LLM_RC=$?
    set -e

    if [[ $LLM_RC -eq 124 ]]; then
      LAYER4="timeout"
      LLM_VERDICT="batch_preview"
      LLM_CONFIDENCE="0.0"
      LLM_REASONING="LLM-review timeout after ${TIMEOUT_SEC}s; escalate to human."
    elif [[ $LLM_RC -ne 0 ]]; then
      LAYER4="error"
      LLM_VERDICT="batch_preview"
      LLM_CONFIDENCE="0.0"
      LLM_REASONING="LLM-review exited $LLM_RC; escalate to human."
    else
      # Try to parse JSON from output — pass raw via file to avoid bash escaping
      PARSED=$(python3 - "$TMP_OUT" 2>/dev/null <<'PYEOF'
import json, sys, re
with open(sys.argv[1], 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()
raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
raw = re.sub(r'\s*```$', '', raw)
m = re.search(r'\{.*\}', raw, re.DOTALL)
if not m:
    print("PARSE_FAIL"); sys.exit(0)
try:
    obj = json.loads(m.group(0))
    print(json.dumps({
      "verdict": obj.get("verdict", "batch_preview"),
      "confidence": obj.get("confidence", 0.5),
      "reasoning": (obj.get("reasoning") or "")[:500],
      "concerns": obj.get("concerns", [])
    }, ensure_ascii=False))
except Exception:
    print("PARSE_FAIL")
PYEOF
)
      if [[ "$PARSED" == "PARSE_FAIL" || -z "$PARSED" ]]; then
        LAYER4="parse_fail"
        LLM_VERDICT="batch_preview"
        LLM_CONFIDENCE="0.3"
        LLM_REASONING="LLM-review output unparseable; raw: $(echo "$LLM_RAW" | head -c 200)"
      else
        LAYER4="$(echo "$PARSED" | python3 -c 'import json,sys;print(json.load(sys.stdin)["verdict"])')"
        LLM_VERDICT="$LAYER4"
        LLM_CONFIDENCE="$(echo "$PARSED" | python3 -c 'import json,sys;print(json.load(sys.stdin)["confidence"])')"
        LLM_REASONING="$(echo "$PARSED" | python3 -c 'import json,sys;print(json.load(sys.stdin)["reasoning"])')"
        LLM_CONCERNS="$(echo "$PARSED" | python3 -c 'import json,sys;print(json.dumps(json.load(sys.stdin)["concerns"], ensure_ascii=False))')"
      fi
    fi
    rm -f "$REVIEW_PROMPT_FILE" "$TMP_OUT" "$TMP_ERR"
  fi
fi

# --- Aggregate verdict ---
FINAL_VERDICT="approve"
if [[ "$LAYER2" == "fail" ]]; then
  FINAL_VERDICT="reject"
elif [[ "$LLM_VERDICT" == "reject" ]]; then
  FINAL_VERDICT="reject"
elif [[ "$LLM_VERDICT" == "batch_preview" ]]; then
  FINAL_VERDICT="batch_preview"
fi

END_TS="$(date -u +%FT%TZ)"
END_EPOCH="$(date +%s)"
WALL_SEC=$(( END_EPOCH - START_EPOCH ))

# --- Build JSON verdict via env-var passing (safer than heredoc-interpolation) ---
export _CR_VERDICT="$FINAL_VERDICT"
export _CR_CONF="$LLM_CONFIDENCE"
export _CR_REASON="$LLM_REASONING"
export _CR_CONCERNS="$LLM_CONCERNS"
export _CR_L1="$LAYER1"
export _CR_L2="$LAYER2"
export _CR_HITS="$LAYER2_HITS"
export _CR_L3="$LAYER3"
export _CR_L4="$LAYER4"
export _CR_UUID="$RUN_UUID"
export _CR_RID="$REVIEW_ID"
export _CR_RT="$RED_TEAM"
export _CR_IN="$INPUT"
export _CR_WS="$WALL_SEC"
export _CR_STS="$START_TS"
export _CR_ETS="$END_TS"
VERDICT_JSON=$(python3 - <<'PYEOF'
import json, os
try:
    concerns = json.loads(os.environ.get("_CR_CONCERNS", "[]") or "[]")
except Exception:
    concerns = []
out = {
  "verdict": os.environ["_CR_VERDICT"],
  "confidence": float(os.environ.get("_CR_CONF", "0.0") or 0.0),
  "reasoning": os.environ.get("_CR_REASON", ""),
  "concerns": concerns,
  "layer_results": {
    "env_flag": os.environ["_CR_L1"],
    "forbidden_target": os.environ["_CR_L2"],
    "forbidden_hits": os.environ.get("_CR_HITS", ""),
    "git_hook_signal": os.environ["_CR_L3"],
    "llm_review": os.environ["_CR_L4"]
  },
  "review_uuid": os.environ["_CR_UUID"],
  "review_id": os.environ["_CR_RID"],
  "red_team": int(os.environ["_CR_RT"]),
  "input_file": os.environ["_CR_IN"],
  "wall_clock_sec": int(os.environ["_CR_WS"]),
  "start_ts": os.environ["_CR_STS"],
  "end_ts": os.environ["_CR_ETS"]
}
print(json.dumps(out, ensure_ascii=False, indent=2))
PYEOF
)

if [[ -n "$OUTPUT_PATH" ]]; then
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  echo "$VERDICT_JSON" > "$OUTPUT_PATH"
  echo "[11.11critic] verdict written to: $OUTPUT_PATH" >&2
else
  echo "$VERDICT_JSON"
fi

# --- JSONL audit (env-var passing, safe) ---
export _CR_TARGETS="$TARGETS"
export _CR_MOCK="$MOCK"
python3 - "$AUDIT_FILE" <<'PYEOF'
import json, sys, pathlib, os
audit = sys.argv[1]
row = {
  "event": "critic_review",
  "run_uuid": os.environ["_CR_UUID"],
  "review_id": os.environ["_CR_RID"],
  "input_file": os.environ["_CR_IN"],
  "targets": os.environ.get("_CR_TARGETS", ""),
  "red_team": bool(int(os.environ.get("_CR_RT", "0"))),
  "mock": bool(int(os.environ.get("_CR_MOCK", "0"))),
  "verdict": os.environ["_CR_VERDICT"],
  "confidence": float(os.environ.get("_CR_CONF", "0.0") or 0.0),
  "layer1_env_flag": os.environ["_CR_L1"],
  "layer2_forbidden_target": os.environ["_CR_L2"],
  "layer3_git_hook": os.environ["_CR_L3"],
  "layer4_llm_review": os.environ["_CR_L4"],
  "start_ts": os.environ["_CR_STS"],
  "end_ts": os.environ["_CR_ETS"],
  "wall_clock_sec": int(os.environ["_CR_WS"])
}
pathlib.Path(audit).parent.mkdir(parents=True, exist_ok=True)
with open(audit, 'a', encoding='utf-8') as f:
  f.write(json.dumps(row, ensure_ascii=False) + "\n")
PYEOF

echo "[11.11critic] audit: $AUDIT_FILE (verdict=${FINAL_VERDICT}, wall=${WALL_SEC}s)" >&2

case "$FINAL_VERDICT" in
  approve)       exit 0 ;;
  reject)        exit 2 ;;
  batch_preview) exit 3 ;;
  *)             exit 2 ;;
esac

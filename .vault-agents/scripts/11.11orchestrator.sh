#!/bin/bash
# 11.11orchestrator — Worker → Critic → (Publish | Reject | Batch-preview) → optional Summarizer.
#
# ADR: 07-Decisions/2026-05-12 sv-3 multi-agent orchestration arch.md
# Sprint: B-6 follow-up (auto-cascade, 2026-05-19)
#
# Pipeline:
#   1. Spawn 11.11worker → capture output file
#   2. Pipe output to 11.11critic (exit-code routing: 0=approve / 2=reject / 3=batch_preview)
#   3. approve       → publish to --publish <path> (or stdout if absent)
#   4. reject        → log + abort with exit 2
#   5. batch_preview → emit JSONL preview row (.vault-agents/runs/preview-<ts>.jsonl) + exit 3
#   6. Optional --with-summarizer → run 11.11summarizer --inputs on worker-output for synthesis
#
# Usage:
#   11.11orchestrator.sh --task "<description>" [--skill <name>]
#                        [--publish <path>] [--targets "<csv>"]
#                        [--with-summarizer] [--red-team] [--mock-critic]
#                        [--worker-timeout <sec>] [--critic-timeout <sec>]
#
# Audit:
#   .vault-agents/runs/orchestrator-<uuid>.jsonl (cascade-level summary row)
#
# ENV-flag:
#   ORCHESTRATOR_DISABLED=1 → skip everything, exit 0 with no-op audit row
#
# Exit codes:
#   0   = approve (and publish if requested)
#   2   = reject (critic blocked) OR worker-stage failure
#   3   = batch_preview (low-confidence; user-confirm step required)
#   1   = usage error / missing component
#   124 = timeout cascade

set -uo pipefail

TASK=""
SKILL=""
PUBLISH_PATH=""
TARGETS=""
WITH_SUMMARIZER="0"
RED_TEAM="0"
MOCK_CRITIC="0"
WORKER_TIMEOUT="300"
CRITIC_TIMEOUT="120"

VAULT_AGENTS_DIR="/root/obsidian-vault/.vault-agents"
RUNS_DIR="${VAULT_AGENTS_DIR}/runs"
WORKER_BIN="/usr/local/bin/11.11worker"
CRITIC_BIN="/usr/local/bin/11.11critic"
SUMMARIZER_BIN="/usr/local/bin/11.11summarizer"

usage() {
  cat >&2 <<EOF
Usage:
  11.11orchestrator.sh --task "<description>" [--skill <name>]
                       [--publish <path>] [--targets "<csv>"]
                       [--with-summarizer] [--red-team] [--mock-critic]
                       [--worker-timeout <sec>] [--critic-timeout <sec>]

ENV:
  ORCHESTRATOR_DISABLED=1   skip everything (no-op exit 0)

Exit: 0=approve  2=reject  3=batch_preview  124=timeout  1=usage
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)            TASK="$2"; shift 2 ;;
    --skill)           SKILL="$2"; shift 2 ;;
    --publish)         PUBLISH_PATH="$2"; shift 2 ;;
    --targets)         TARGETS="$2"; shift 2 ;;
    --with-summarizer) WITH_SUMMARIZER="1"; shift ;;
    --red-team)        RED_TEAM="1"; shift ;;
    --mock-critic)     MOCK_CRITIC="1"; shift ;;
    --worker-timeout)  WORKER_TIMEOUT="$2"; shift 2 ;;
    --critic-timeout)  CRITIC_TIMEOUT="$2"; shift 2 ;;
    -h|--help)         usage ;;
    *) echo "Error: unknown option: $1" >&2; usage ;;
  esac
done

[[ -z "$TASK" ]] && { echo "Error: --task required" >&2; usage; }

mkdir -p "$RUNS_DIR"
RUN_UUID="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c 'import uuid;print(uuid.uuid4())')"
AUDIT_FILE="${RUNS_DIR}/orchestrator-${RUN_UUID}.jsonl"
START_TS="$(date -u +%FT%TZ)"
START_EPOCH="$(date +%s)"

# --- ENV-flag short-circuit ---
if [[ "${ORCHESTRATOR_DISABLED:-0}" == "1" ]]; then
  python3 - "$AUDIT_FILE" "$RUN_UUID" "$START_TS" "$TASK" <<'PYEOF'
import json, sys, pathlib
audit, uuid, ts, task = sys.argv[1:]
pathlib.Path(audit).parent.mkdir(parents=True, exist_ok=True)
with open(audit, 'a', encoding='utf-8') as f:
  f.write(json.dumps({
    "event": "orchestrator_run", "run_uuid": uuid, "status": "disabled",
    "start_ts": ts, "task": task[:200]
  }, ensure_ascii=False) + "\n")
PYEOF
  echo "[11.11orchestrator] ORCHESTRATOR_DISABLED=1 → no-op (audit: $AUDIT_FILE)" >&2
  exit 0
fi

# --- Preflight ---
for bin in "$WORKER_BIN" "$CRITIC_BIN"; do
  if [[ ! -x "$bin" ]]; then
    echo "Error: missing component: $bin" >&2
    exit 1
  fi
done
if [[ "$WITH_SUMMARIZER" == "1" && ! -x "$SUMMARIZER_BIN" ]]; then
  echo "Error: --with-summarizer set but $SUMMARIZER_BIN missing" >&2
  exit 1
fi

echo "[11.11orchestrator] uuid=${RUN_UUID} | task='${TASK:0:60}...' | skill=${SKILL:-none} | publish=${PUBLISH_PATH:-stdout} | summarizer=${WITH_SUMMARIZER}" >&2

# --- Stage 1: Worker ---
WORKER_OUT="${RUNS_DIR}/orch-${RUN_UUID}-worker.md"
WORKER_ARGS=(--task "$TASK" --worker-id "orch" --output "$WORKER_OUT" --timeout "$WORKER_TIMEOUT")
[[ -n "$SKILL" ]] && WORKER_ARGS+=(--skill "$SKILL")

set +e
"$WORKER_BIN" "${WORKER_ARGS[@]}" >/dev/null 2>"${RUNS_DIR}/orch-${RUN_UUID}-worker.err"
WORKER_RC=$?
set -e

if [[ $WORKER_RC -eq 124 ]]; then
  echo "[11.11orchestrator] Worker TIMEOUT" >&2
  FINAL_STATUS="worker_timeout"; FINAL_EXIT=124
elif [[ $WORKER_RC -ne 0 ]]; then
  echo "[11.11orchestrator] Worker failed (rc=$WORKER_RC)" >&2
  cat "${RUNS_DIR}/orch-${RUN_UUID}-worker.err" >&2 || true
  FINAL_STATUS="worker_failed"; FINAL_EXIT=2
else
  FINAL_STATUS="worker_ok"; FINAL_EXIT=0
fi

# --- Stage 2: Critic (only if worker succeeded) ---
CRITIC_VERDICT="skipped"
CRITIC_OUT="${RUNS_DIR}/orch-${RUN_UUID}-critic.json"
CRITIC_RC="-1"

if [[ "$FINAL_STATUS" == "worker_ok" ]]; then
  CRITIC_ARGS=(--input "$WORKER_OUT" --review-id "orch-${RUN_UUID:0:8}" \
               --output "$CRITIC_OUT" --timeout "$CRITIC_TIMEOUT")
  [[ -n "$TARGETS" ]] && CRITIC_ARGS+=(--targets "$TARGETS")
  [[ "$RED_TEAM" == "1" ]] && CRITIC_ARGS+=(--red-team)
  [[ "$MOCK_CRITIC" == "1" ]] && CRITIC_ARGS+=(--mock)

  set +e
  "$CRITIC_BIN" "${CRITIC_ARGS[@]}" >/dev/null 2>"${RUNS_DIR}/orch-${RUN_UUID}-critic.err"
  CRITIC_RC=$?
  set -e

  case $CRITIC_RC in
    0)   CRITIC_VERDICT="approve" ;;
    2)   CRITIC_VERDICT="reject" ;;
    3)   CRITIC_VERDICT="batch_preview" ;;
    124) CRITIC_VERDICT="timeout" ;;
    *)   CRITIC_VERDICT="error_rc_${CRITIC_RC}" ;;
  esac

  echo "[11.11orchestrator] Critic verdict: $CRITIC_VERDICT (rc=$CRITIC_RC)" >&2

  # --- Stage 3: Route on verdict ---
  case "$CRITIC_VERDICT" in
    approve)
      if [[ -n "$PUBLISH_PATH" ]]; then
        mkdir -p "$(dirname "$PUBLISH_PATH")"
        cp "$WORKER_OUT" "$PUBLISH_PATH"
        echo "[11.11orchestrator] PUBLISHED → $PUBLISH_PATH" >&2
      else
        cat "$WORKER_OUT"
      fi
      FINAL_STATUS="approved_published"; FINAL_EXIT=0
      ;;
    reject)
      echo "[11.11orchestrator] REJECTED — abort (see $CRITIC_OUT)" >&2
      FINAL_STATUS="rejected"; FINAL_EXIT=2
      ;;
    batch_preview)
      PREVIEW_FILE="${RUNS_DIR}/preview-${RUN_UUID}.jsonl"
      python3 - "$PREVIEW_FILE" "$RUN_UUID" "$WORKER_OUT" "$CRITIC_OUT" "$TASK" "$PUBLISH_PATH" <<'PYEOF'
import json, sys, pathlib
pf, uuid, wo, co, task, pub = sys.argv[1:]
pathlib.Path(pf).parent.mkdir(parents=True, exist_ok=True)
try:
  with open(co) as f: critic = json.load(f)
except Exception:
  critic = {}
row = {
  "event": "batch_preview_pending",
  "run_uuid": uuid,
  "task": task[:200],
  "worker_output": wo,
  "critic_verdict": co,
  "proposed_publish_path": pub or None,
  "verdict": critic.get("verdict"),
  "confidence": critic.get("confidence"),
  "reasoning": (critic.get("reasoning") or "")[:300],
}
with open(pf, 'a', encoding='utf-8') as f:
  f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(pf)
PYEOF
      echo "[11.11orchestrator] BATCH_PREVIEW → $PREVIEW_FILE (user-confirm required)" >&2
      FINAL_STATUS="batch_preview"; FINAL_EXIT=3
      ;;
    timeout)
      FINAL_STATUS="critic_timeout"; FINAL_EXIT=124 ;;
    *)
      FINAL_STATUS="critic_error"; FINAL_EXIT=2 ;;
  esac
fi

# --- Stage 4: Optional Summarizer (only on approve) ---
SUMMARIZER_RAN="0"
SUMMARIZER_OUT=""
SUMMARIZER_RC="-1"
if [[ "$WITH_SUMMARIZER" == "1" && "$FINAL_STATUS" == "approved_published" ]]; then
  SUMMARIZER_OUT="${RUNS_DIR}/orch-${RUN_UUID}-summary.md"
  set +e
  "$SUMMARIZER_BIN" --inputs "$WORKER_OUT" --output "$SUMMARIZER_OUT" --timeout 180 \
    >/dev/null 2>"${RUNS_DIR}/orch-${RUN_UUID}-summarizer.err"
  SUMMARIZER_RC=$?
  set -e
  SUMMARIZER_RAN="1"
  if [[ $SUMMARIZER_RC -ne 0 ]]; then
    echo "[11.11orchestrator] Summarizer rc=$SUMMARIZER_RC (non-fatal)" >&2
  else
    echo "[11.11orchestrator] Summarizer ok → $SUMMARIZER_OUT" >&2
  fi
fi

END_TS="$(date -u +%FT%TZ)"
END_EPOCH="$(date +%s)"
WALL_SEC=$(( END_EPOCH - START_EPOCH ))

# --- Cascade audit row ---
export _OR_AUDIT="$AUDIT_FILE" _OR_UUID="$RUN_UUID" _OR_TASK="$TASK" _OR_SKILL="$SKILL"
export _OR_WO="$WORKER_OUT" _OR_WRC="$WORKER_RC" _OR_CO="$CRITIC_OUT" _OR_CRC="$CRITIC_RC"
export _OR_CV="$CRITIC_VERDICT" _OR_PUB="$PUBLISH_PATH" _OR_FS="$FINAL_STATUS"
export _OR_FE="$FINAL_EXIT" _OR_SR="$SUMMARIZER_RAN" _OR_SO="$SUMMARIZER_OUT"
export _OR_SRC="$SUMMARIZER_RC" _OR_STS="$START_TS" _OR_ETS="$END_TS" _OR_WS="$WALL_SEC"
export _OR_RT="$RED_TEAM" _OR_MC="$MOCK_CRITIC"
python3 - <<'PYEOF'
import json, os, pathlib
row = {
  "event": "orchestrator_run",
  "run_uuid": os.environ["_OR_UUID"],
  "task": os.environ["_OR_TASK"][:300],
  "skill": os.environ.get("_OR_SKILL") or None,
  "worker_output": os.environ["_OR_WO"],
  "worker_exit_code": int(os.environ["_OR_WRC"]),
  "critic_output": os.environ["_OR_CO"],
  "critic_exit_code": int(os.environ["_OR_CRC"]),
  "critic_verdict": os.environ["_OR_CV"],
  "publish_path": os.environ.get("_OR_PUB") or None,
  "final_status": os.environ["_OR_FS"],
  "final_exit_code": int(os.environ["_OR_FE"]),
  "summarizer_ran": bool(int(os.environ["_OR_SR"])),
  "summarizer_output": os.environ.get("_OR_SO") or None,
  "summarizer_exit_code": int(os.environ["_OR_SRC"]),
  "red_team": bool(int(os.environ["_OR_RT"])),
  "mock_critic": bool(int(os.environ["_OR_MC"])),
  "start_ts": os.environ["_OR_STS"],
  "end_ts": os.environ["_OR_ETS"],
  "wall_clock_sec": int(os.environ["_OR_WS"]),
}
audit = os.environ["_OR_AUDIT"]
pathlib.Path(audit).parent.mkdir(parents=True, exist_ok=True)
with open(audit, 'a', encoding='utf-8') as f:
  f.write(json.dumps(row, ensure_ascii=False) + "\n")
PYEOF

echo "[11.11orchestrator] DONE | status=${FINAL_STATUS} | wall=${WALL_SEC}s | audit=$AUDIT_FILE" >&2
exit "$FINAL_EXIT"

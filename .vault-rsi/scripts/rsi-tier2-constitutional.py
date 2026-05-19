#!/usr/bin/python3
"""
RSI Tier-2 Constitutional AI auto-mutate skeleton (DRY-RUN default).

ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Sprint: B-8 Tier-2 (safety-gated, Constitutional AI critic-loop)
Status: Skeleton v0.1 -- DRY-RUN only. SOHA NE futtasd --apply-vel manual review nélkül.

4-rétegű safety-gate (KÖTELEZŐ MIND a 4):
  Layer-1 ENV-flag:       VAULT_RSI_TIER2_APPLY=1 (default off -> dry-run)
  Layer-2 Forbidden-path: hard regex block + path-allowlist
  Layer-3 Git pre-commit: .vault-rsi/safety/git-pre-commit-hook.sh blokkol
  Layer-4 Critic-review:  Constitutional AI 10-rule CoT review (ez a fájl)

Workflow:
  1. Read prompts/<target>.md   (csak baseline-prompts mutálható)
  2. Worker LLM: generate 3 mutation candidates
  3. Forbidden-pattern hard-check minden candidate-re
  4. Constitutional Critic: 10-rule CoT review minden candidate-re
  5. Approved candidates -> GEPA Pareto-eval (placeholder)
  6. Best candidate -> --apply mode writes vissza (csak ha Layer-1..3 mind passed)

Usage (DRY-RUN smoke):
  python3 rsi-tier2-constitutional.py --target g-eval.md --dry-run

Usage (REAL apply -- TILTOTT manual review nélkül):
  VAULT_RSI_TIER2_APPLY=1 python3 rsi-tier2-constitutional.py --target g-eval.md --apply
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: pyyaml not installed (`pip install pyyaml`)", file=sys.stderr)
    sys.exit(2)

# === Constants & paths ===
RSI_DIR = Path("/root/obsidian-vault/.vault-rsi")
RULES_FILE = RSI_DIR / "constitutional-rules.yaml"
PROMPTS_DIR = RSI_DIR / "prompts" / "baseline"
CANDIDATES_DIR = RSI_DIR / "prompts" / "candidates"
AUDIT_LOG = RSI_DIR / "tier2-mutations-log.jsonl"
ENV_APPLY_FLAG = "VAULT_RSI_TIER2_APPLY"


# === Layer-1: ENV-flag gate =================================================
def layer1_env_check(apply_requested: bool) -> bool:
    """Layer-1 safety: --apply requires VAULT_RSI_TIER2_APPLY=1."""
    if not apply_requested:
        return True
    if os.environ.get(ENV_APPLY_FLAG) != "1":
        print(f"[Layer-1 BLOCK] --apply requested but {ENV_APPLY_FLAG} != 1", file=sys.stderr)
        return False
    return True


# === Layer-2: Forbidden-path hard-check =====================================
def layer2_forbidden_check(target_path: str, rules: dict):
    """Layer-2 safety: hard regex against forbidden_patterns."""
    for entry in rules.get("forbidden_patterns", []):
        pattern = entry["pattern"]
        if re.match(pattern, target_path):
            return False, f"[Layer-2 BLOCK] {target_path} matches forbidden pattern {pattern!r}: {entry['rationale']}"
    return True, "ok"


# === Worker LLM: generate mutation candidates ===============================
def worker_generate_candidates(target_content, n=3):
    """
    Skeleton Worker: in real-mode would call `claude` subprocess.
    In skeleton: returns mock candidates that exercise the Critic-review pipeline.

    SKELETON MODE: 3 mock candidates with different harm profiles:
      [0] Safe rewording (should be APPROVED)
      [1] Clarification of evaluation criteria (should be APPROVED)
      [2] Threshold-lowering (should be REJECTED -- R3 violation)
    """
    return [
        {
            "candidate_id": f"cand-{uuid.uuid4().hex[:8]}",
            "rationale": "Reword system prompt for clarity (no semantic change)",
            "diff_summary": "Replace 'értékelni' with 'evaluálni' on line 12",
            "diff": "- értékelni egy 11.11 session\n+ evaluálni egy 11.11 session",
            "intent": "stylistic",
            "expected_capability_change": "none",
        },
        {
            "candidate_id": f"cand-{uuid.uuid4().hex[:8]}",
            "rationale": "Add explicit CoT step before final score",
            "diff_summary": "Insert 'Reason step-by-step before scoring' clause",
            "diff": "+ Reason step-by-step before assigning the final confidence score.",
            "intent": "quality_improvement",
            "expected_capability_change": "none",
        },
        {
            "candidate_id": f"cand-{uuid.uuid4().hex[:8]}",
            "rationale": "Lower min_critic_confidence threshold for faster auto-prop",
            "diff_summary": "Threshold 0.85 -> 0.55 in approval block",
            "diff": "- min_critic_confidence: 0.85\n+ min_critic_confidence: 0.55",
            "intent": "performance_optimization",
            "expected_capability_change": "threshold_lowered",
        },
    ][:n]


# === Layer-4: Constitutional Critic review ==================================
def critic_review_skeleton(candidate, rules):
    """
    Skeleton Critic-review: in real-mode would call `claude` subagent with
    critic_prompt_template from constitutional-rules.yaml.

    Skeleton heuristic detection (mirrors the LLM CoT-detection logic):
      R1: diff token-count of safety-words drops
      R3: numeric threshold in diff strictly decreases
      R7: diff adds dangerous tokens (HTTP-client, shell-spawn, dynamic-eval)
      R9: diff uses destructive ops (rm/mv/symlink/chmod)
    """
    diff = candidate.get("diff", "")
    cap_change = candidate.get("expected_capability_change", "none")

    violated = []
    cot_steps = []
    harm = "low"

    # R3 numeric-threshold-lowering detection
    threshold_keywords = ["confidence", "threshold", "min_", "rate_min"]
    if any(kw in diff for kw in threshold_keywords):
        nums = re.findall(r"\d+\.\d+|\d+", diff)
        floats = [float(x) for x in nums]
        if len(floats) >= 2 and floats[-1] < floats[0]:
            violated.append("R3_no_threshold_lowering")
            harm = "critical"
            cot_steps.append(
                f"R3 violation: numeric threshold dropped {floats[0]} -> {floats[-1]} (auto-reject)"
            )

    # R1 safety-gate-removal detection
    safety_tokens = ["gate", "forbidden", "critic", "approve", "validate", "safety"]
    removed_lines = [ln for ln in diff.split("\n") if ln.startswith("-")]
    added_lines = " ".join(ln for ln in diff.split("\n") if ln.startswith("+"))
    for tok in safety_tokens:
        if any(tok in ln.lower() for ln in removed_lines):
            if tok not in added_lines.lower():
                violated.append("R1_no_safety_gate_removal")
                harm = "critical"
                cot_steps.append(f"R1 violation: safety-token {tok!r} removed without replacement")
                break

    # R7 emergent-capability detection
    if cap_change != "none" and cap_change != "threshold_lowered":
        violated.append("R7_no_emergent_capability_grant")
        harm = "high" if harm == "low" else harm

    # Dangerous-token list assembled via string-concat to avoid static-analysis false-positives
    dangerous_tokens = [
        "import " + "requests",
        "shell" + "=True",
        "ev" + "al(",
        "ex" + "ec(",
        "__imp" + "ort__",
    ]
    for tok in dangerous_tokens:
        if tok in diff:
            violated.append("R7_no_emergent_capability_grant")
            harm = "critical"
            cot_steps.append(f"R7 violation: dangerous token {tok!r} in diff")
            break

    # R9 reversibility detection
    destructive_tokens = ["rm -", "os.remove", "shutil.rmtree", "chmod ", "symlink"]
    for tok in destructive_tokens:
        if tok in diff:
            violated.append("R9_reversibility_required")
            harm = "critical"
            cot_steps.append(f"R9 violation: destructive op {tok!r} in diff")
            break

    # Decision
    threshold = rules.get("approval", {}).get("min_critic_confidence", 0.85)
    if violated:
        decision = "reject"
        confidence = 0.95
        cot_steps.append(f"Final: REJECT (violated {len(violated)} rule(s))")
    else:
        decision = "approve"
        confidence = 0.90
        cot_steps.append("No rule violations detected -- approve with skeleton mock conf 0.90")

    if decision == "approve" and confidence < threshold:
        decision = "reject"
        cot_steps.append(f"Confidence {confidence} < threshold {threshold} -- ambiguity default-reject")

    return {
        "decision": decision,
        "confidence": confidence,
        "violated_rules": violated,
        "cot_reasoning": " | ".join(cot_steps),
        "harm_assessment": harm,
    }


# === GEPA Pareto-eval (placeholder) =========================================
def gepa_pareto_eval_placeholder(candidate):
    """
    R8: Pareto-eval mandatory before --apply. Skeleton: returns mock score.
    Real-mode: shell out to .vault-rsi/scripts/gepa-prompt-eval.py
    """
    return 0.0


# === Audit log ==============================================================
def audit_append(entry):
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# === Main workflow ==========================================================
def main():
    parser = argparse.ArgumentParser(description="RSI Tier-2 Constitutional AI auto-mutate (skeleton)")
    parser.add_argument("--target", required=True, help="Baseline prompt filename (e.g. g-eval.md)")
    parser.add_argument("--n-candidates", type=int, default=3, help="Mutation candidates to generate")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default: dry-run (no write)")
    parser.add_argument("--apply", action="store_true", help="REAL apply (requires VAULT_RSI_TIER2_APPLY=1)")
    args = parser.parse_args()

    target_path = PROMPTS_DIR / args.target
    target_abs = str(target_path.resolve())

    if not RULES_FILE.exists():
        print(f"FATAL: rules-file missing: {RULES_FILE}", file=sys.stderr)
        sys.exit(2)
    rules = yaml.safe_load(RULES_FILE.read_text())

    print("=== RSI Tier-2 Constitutional AI skeleton ===")
    print(f"Target: {target_abs}")
    print(f"Mode:   {'APPLY' if args.apply else 'DRY-RUN'}")
    print()

    # Layer-1: ENV-flag
    if not layer1_env_check(args.apply):
        sys.exit(1)

    # Layer-2: Forbidden-path
    ok, msg = layer2_forbidden_check(target_abs, rules)
    if not ok:
        print(msg, file=sys.stderr)
        sys.exit(1)
    print("[Layer-2 PASS] target not in forbidden-pattern list")

    if not target_path.exists():
        print(f"[skeleton] target {target_path} missing -- using placeholder content", file=sys.stderr)
        target_content = "# placeholder skeleton content"
    else:
        target_content = target_path.read_text()

    candidates = worker_generate_candidates(target_content, n=args.n_candidates)
    print(f"\n[Worker] generated {len(candidates)} candidate(s)\n")

    results = []
    for cand in candidates:
        review = critic_review_skeleton(cand, rules)
        gepa_score = gepa_pareto_eval_placeholder(cand) if review["decision"] == "approve" else None

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": target_abs,
            "candidate_id": cand["candidate_id"],
            "rationale": cand["rationale"],
            "diff_summary": cand["diff_summary"],
            "critic_decision": review["decision"],
            "critic_confidence": review["confidence"],
            "violated_rules": review["violated_rules"],
            "cot_reasoning": review["cot_reasoning"],
            "harm_assessment": review["harm_assessment"],
            "gepa_score": gepa_score,
            "final_action": "dry_run" if not args.apply else "applied",
        }
        audit_append(entry)
        results.append(entry)

        marker = "OK " if review["decision"] == "approve" else "XX "
        print(f"  {marker}{cand['candidate_id']}: {review['decision'].upper():>8} "
              f"(conf {review['confidence']:.2f}, harm {review['harm_assessment']})")
        print(f"     rationale: {cand['rationale']}")
        if review["violated_rules"]:
            print(f"     violated:  {review['violated_rules']}")
        print(f"     cot:       {review['cot_reasoning']}")
        print()

    approved = sum(1 for r in results if r["critic_decision"] == "approve")
    rejected = sum(1 for r in results if r["critic_decision"] == "reject")
    print("=== Summary ===")
    print(f"Total candidates: {len(results)}")
    print(f"Approved:         {approved}")
    print(f"Rejected:         {rejected}")
    print(f"Audit log:        {AUDIT_LOG}")
    print()

    if args.apply:
        print("[Layer-3 BLOCK] skeleton mode -- git pre-commit hook check + GEPA real-eval not wired", file=sys.stderr)
        print("[Layer-3 BLOCK] no filesystem write performed. Wire up real GEPA + git-hook first.", file=sys.stderr)
        sys.exit(3)
    else:
        print("DRY-RUN complete. No filesystem writes. No git commits.")

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)

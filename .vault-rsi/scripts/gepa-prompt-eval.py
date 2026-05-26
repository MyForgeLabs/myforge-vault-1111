#!/usr/bin/env python3
"""
gepa-prompt-eval — Minibatch evaluator for a single prompt candidate (B-8 Réteg 2).

Given a prompt-file and the eval-data gold-set (input → expected_score / expected_decision),
runs the prompt on each minibatch sample and aggregates per-axis scores. NO vault mutation.
Used by `gepa-prompt-mutate.py` as the metric-callable for `gepa.optimize()`, also runnable
standalone for baseline-snapshot generation.

ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Research: 11-wiki/sv-02-recursive-self-improvement.md (Q1 — GEPA Compound AI System)
Sprint: B-8 Week 1 skeleton — 2026-05-17.

⚠️  SAFETY:
    - HARD-OFF auto-apply: this script ONLY reads + scores. NO vault writes.
    - Writes only to /root/obsidian-vault/.vault-rsi/logs/eval-<ts>.jsonl (RSI-private log).
    - VAULT_RSI_APPLY=1 is NOT needed for eval — eval is always read-only.

Usage:
    gepa-prompt-eval --prompt prompts/baseline/g-eval.md --eval-data eval-data/g-eval.jsonl
    gepa-prompt-eval --prompt <path> --eval-data <path> --scorer mock          # no-LLM, rule-based
    gepa-prompt-eval --prompt <path> --eval-data <path> --scorer claude-code   # subagent-fanout (later)
    gepa-prompt-eval --prompt <path> --eval-data <path> --scorer anthropic     # API (needs key)

Exit codes:
    0  ok, score-summary printed
    1  bad input (prompt-file missing, eval-data malformed)
    2  scorer error
"""

import argparse
import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
RSI_ROOT = VAULT_ROOT / ".vault-rsi"
LOG_DIR = RSI_ROOT / "logs"

# ---- Mock scorer: deterministic, rule-based (zero-cost baseline) ----------


def mock_score_sample(prompt_text: str, sample: dict) -> dict:
    """
    Heuristic stand-in for an LLM-judge run.

    Score axes (B-1 G-Eval-inspired):
        relevance, factuality, actionability, novelty, uniqueness — 0..1
    The mock simply compares the prompt against the sample's `keywords_required`
    and `keywords_forbidden`. A real run will substitute this with an actual
    LLM call via `claude-code` subagent or `anthropic` SDK.
    """
    pl = prompt_text.lower()
    req = [k.lower() for k in sample.get("keywords_required", [])]
    forb = [k.lower() for k in sample.get("keywords_forbidden", [])]
    req_hit = sum(1 for k in req if k in pl) / max(1, len(req))
    forb_hit = sum(1 for k in forb if k in pl) / max(1, len(forb))
    rel = max(0.0, req_hit - 0.5 * forb_hit)

    # length-regularization signal: target ~600 tokens (~3000 chars)
    length = len(prompt_text)
    length_penalty = max(0.0, (length - 3000) / 6000.0)
    novelty = max(0.0, min(1.0, 0.7 - length_penalty))

    return {
        "relevance": round(rel, 3),
        "factuality": round(min(1.0, req_hit + 0.2), 3),
        "actionability": round(0.6 if "step" in pl or "1." in pl else 0.4, 3),
        "novelty": round(novelty, 3),
        "uniqueness": round(0.5, 3),
        "_length": length,
        "_length_penalty": round(length_penalty, 3),
    }


def claude_code_score_sample(prompt_text: str, sample: dict) -> dict:
    """
    Placeholder — Week 2 will implement subagent-fanout (general-purpose Agent
    spawned for each sample, response written to /tmp/vault-rsi-pending/<id>.json).
    Currently raises NotImplementedError so the skeleton is honest.
    """
    raise NotImplementedError(
        "claude-code scorer arrives in B-8 Week 2 (subagent-fanout 2-phase pending). "
        "Use --scorer mock for the Week 1 baseline."
    )


def anthropic_score_sample(prompt_text: str, sample: dict) -> dict:
    """Placeholder — Week 2+. Requires ANTHROPIC_API_KEY and cost-budget approval."""
    raise NotImplementedError(
        "anthropic scorer not wired yet. Week 2 task. "
        "Cost-tier: $10-200 / GEPA-round (research Tier-2 only)."
    )


SCORERS = {
    "mock": mock_score_sample,
    "claude-code": claude_code_score_sample,
    "anthropic": anthropic_score_sample,
}


# ---- Eval loop -----------------------------------------------------------


def load_eval_data(path: Path) -> list[dict]:
    if not path.exists():
        print(f"[err] eval-data not found: {path}", file=sys.stderr)
        sys.exit(1)
    rows = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[err] eval-data line {i}: {e}", file=sys.stderr)
                sys.exit(1)
    if not rows:
        print(f"[err] eval-data empty: {path}", file=sys.stderr)
        sys.exit(1)
    return rows


def aggregate(scores: list[dict]) -> dict:
    """Mean per axis, plus an aggregate `score` = mean(relevance, factuality, actionability)."""
    if not scores:
        return {}
    axes = [k for k in scores[0].keys() if not k.startswith("_") and k != "id"]
    out = {}
    for ax in axes:
        vals = [s[ax] for s in scores if ax in s and isinstance(s[ax], (int, float))]
        out[ax] = round(statistics.mean(vals), 3) if vals else 0.0
    out["score"] = round(
        statistics.mean(
            [out.get("relevance", 0), out.get("factuality", 0), out.get("actionability", 0)]
        ),
        3,
    )
    out["n_samples"] = len(scores)
    return out


def write_log(prompt_path: Path, eval_path: Path, scorer: str, agg: dict, per_sample: list[dict]):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOG_DIR / f"eval-{ts}.jsonl"
    entry = {
        "event": "gepa_prompt_eval",
        "ts": datetime.now(timezone.utc).isoformat(),
        "prompt": str(prompt_path),
        "eval_data": str(eval_path),
        "scorer": scorer,
        "aggregate": agg,
        "per_sample": per_sample,
    }
    with open(log_path, "w") as f:
        f.write(json.dumps(entry) + "\n")
    return log_path


def main():
    ap = argparse.ArgumentParser(description="B-8 GEPA prompt-eval (minibatch, read-only)")
    ap.add_argument("--prompt", required=True, type=Path, help="Prompt file to evaluate")
    ap.add_argument(
        "--eval-data",
        required=True,
        type=Path,
        help="JSONL gold-set (one sample per line)",
    )
    ap.add_argument("--scorer", choices=list(SCORERS.keys()), default="mock")
    ap.add_argument("--json", action="store_true", help="Print machine-readable JSON only")
    args = ap.parse_args()

    if not args.prompt.exists():
        print(f"[err] prompt-file not found: {args.prompt}", file=sys.stderr)
        sys.exit(1)

    prompt_text = args.prompt.read_text()
    samples = load_eval_data(args.eval_data)
    scorer = SCORERS[args.scorer]

    per_sample = []
    for s in samples:
        try:
            sc = scorer(prompt_text, s)
        except NotImplementedError as e:
            print(f"[err] scorer={args.scorer}: {e}", file=sys.stderr)
            sys.exit(2)
        per_sample.append({"id": s.get("id"), **sc})

    agg = aggregate(per_sample)
    log_path = write_log(args.prompt, args.eval_data, args.scorer, agg, per_sample)

    if args.json:
        print(json.dumps({"aggregate": agg, "log": str(log_path)}))
    else:
        print(f"[eval] prompt={args.prompt.name}  scorer={args.scorer}  n={agg['n_samples']}")
        for k, v in agg.items():
            if k != "n_samples":
                print(f"       {k:14s} {v}")
        print(f"[log]  {log_path}")


if __name__ == "__main__":
    main()

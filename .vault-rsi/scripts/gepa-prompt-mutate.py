#!/usr/bin/env python3
"""
gepa-prompt-mutate — Pareto-front prompt mutator using gepa-ai/gepa (B-8 Réteg 2).

Week 2 (2026-05-17): real `gepa.optimize()` loop wired with the claude-code subagent
scorer (2-phase pending file pattern). Outputs 3-5 Pareto-front variants to
`.vault-rsi/prompts/candidates/<seed-stem>-v0.3.<N>/` mappákba. Layer 4 detect-only.

ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Research: 11-wiki/sv-02-recursive-self-improvement.md (Q1 — GEPA, 35× fewer rollouts vs GRPO)
Sprint: B-8 Week 2 — 2026-05-17 (real loop). Week 1 skeleton: 2026-05-17 earlier.

⚠️  SAFETY (4-LAYER, mirrors .vault-ko/safety/):
    Layer 1   ENV-flag      VAULT_RSI_APPLY=1 required to write candidates/ outputs
                            (without it, runs in DRY-RUN: prints Pareto-front, writes nothing)
    Layer 2   Forbidden     AGENTS.md / 00-Meta/ / .vault-ko/safety/ / 11.11* / .vault-rsi/{logs,scripts,config}/
                            NEVER targeted. Candidate output ONLY in .vault-rsi/prompts/candidates/.
    Layer 3   Pareto-front  3-5 variants alive, NO single "winner" auto-merge.
    Layer 4   Manual apply  Promotion from candidates/ → live (.vault-agents/prompts/) requires
                            a separate step (Week 3+, user-confirm + Critic-review). Detect-only.

Two-phase scoring (Week 2):
    Phase 1: gepa-prompt-mutate writes per-candidate scoring requests to
             .vault-rsi/scoring-pending/<uuid>.request.json
    Phase 2: Parent Claude Code session spawns a general-purpose Agent to fill
             .vault-rsi/scoring-responses/<uuid>.response.json with JSON-scores.
    Phase 3: gepa-prompt-mutate re-runs, loads responses, updates Pareto-front,
             writes candidate prompt files (if VAULT_RSI_APPLY=1).

For smoke-tests use --auto-fill-synth to generate deterministic synthetic responses
inside the same process (no external subagent required).

Usage:
    # Week 2 smoke (deterministic synth scorer, no real subagent):
    gepa-prompt-mutate --baseline prompts/baseline/g-eval.md \\
        --eval-data eval-data/g-eval.jsonl --budget 12 --max-iterations 3 \\
        --scorer claude-code --auto-fill-synth

    # Week 2 with real subagent (parent Claude fills responses):
    VAULT_RSI_APPLY=1 gepa-prompt-mutate --baseline prompts/baseline/g-eval.md \\
        --eval-data eval-data/g-eval.jsonl --budget 16 --max-iterations 3 \\
        --scorer claude-code
    # ... wait for subagent to fill scoring-responses/, then re-run same command
    # (idempotent: existing responses get loaded, new requests get written for any
    # still-uncomputed (candidate, sample) pairs).

Exit codes:
    0  ok
    1  bad input / forbidden target
    2  gepa-lib error
    3  safety-gate block
    4  pending — re-run after subagent fills responses
"""

import argparse
import json
import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
RSI_ROOT = VAULT_ROOT / ".vault-rsi"
CANDIDATES_DIR = RSI_ROOT / "prompts" / "candidates"
LOG_DIR = RSI_ROOT / "logs"
MUTATIONS_LOG = RSI_ROOT / "mutations.jsonl"
GEPA_LOG = RSI_ROOT / "gepa-log.jsonl"
SCORING_PENDING = RSI_ROOT / "scoring-pending"
SCORING_RESPONSES = RSI_ROOT / "scoring-responses"

FORBIDDEN_PREFIXES = [
    VAULT_ROOT / "AGENTS.md",
    VAULT_ROOT / "00-Meta",
    VAULT_ROOT / ".vault-ko" / "safety",
    VAULT_ROOT / ".vault-rsi" / "logs",
    VAULT_ROOT / ".vault-rsi" / "scripts",
    VAULT_ROOT / ".vault-rsi" / "config",
    VAULT_ROOT / ".vault-rsi" / "safety",
]
FORBIDDEN_NAME_PATTERNS = ["11.11"]


# ---- Safety gates --------------------------------------------------------


def env_apply_enabled() -> bool:
    return os.environ.get("VAULT_RSI_APPLY") == "1"


def forbidden_target_check(target: Path) -> tuple[bool, str]:
    """Return (blocked, reason). Candidates dir is the only safe write zone."""
    tgt = target.resolve()
    for pat in FORBIDDEN_NAME_PATTERNS:
        if pat in tgt.name:
            return True, f"forbidden name pattern '{pat}' in {tgt.name}"
    # Anything inside CANDIDATES_DIR is allowed; check that first.
    try:
        tgt.relative_to(CANDIDATES_DIR.resolve())
        return False, "candidates/ allowed"
    except ValueError:
        pass
    for pref in FORBIDDEN_PREFIXES:
        try:
            tgt.relative_to(pref.resolve())
            return True, f"target under forbidden prefix {pref}"
        except ValueError:
            continue
    # Also forbid anything outside .vault-rsi/prompts/candidates/ for writes
    try:
        tgt.relative_to(RSI_ROOT.resolve())
        return True, f".vault-rsi writes only inside candidates/ allowed ({tgt})"
    except ValueError:
        return True, f"target outside .vault-rsi/ — writes not permitted ({tgt})"


# ---- claude-code scorer integration (2-phase) ----------------------------


def _load_scorer_module():
    """Import the sibling gepa-claude-code-scorer.py via spec (dashed filename)."""
    import importlib.util

    src = Path(__file__).parent / "gepa-claude-code-scorer.py"
    spec = importlib.util.spec_from_file_location("gepa_claude_code_scorer", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gepa_claude_code_scorer"] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_eval_module():
    """Import sibling gepa-prompt-eval.py (mock scorer fallback)."""
    import importlib.util

    src = Path(__file__).parent / "gepa-prompt-eval.py"
    spec = importlib.util.spec_from_file_location("gepa_prompt_eval", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gepa_prompt_eval"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---- GEPA adapter (custom) -----------------------------------------------


def build_adapter(
    scorer_mode: str,
    samples: list[dict],
    scoring_client,
    eval_mod,
    iteration_ref: dict,
    auto_fill: bool,
):
    """
    Build a custom GEPAAdapter that:
      * evaluate() — phase 1+2 of the 2-phase pending pattern (or mock/synth fallback)
      * make_reflective_dataset() — extracts per-sample feedback for reflection_lm
    """
    import gepa
    from gepa import EvaluationBatch

    scorer_synth = scoring_client and __import__(
        "gepa_claude_code_scorer"
    ).synth_response_for_sample
    auto_fill_pending = scoring_client and __import__(
        "gepa_claude_code_scorer"
    ).auto_fill_pending

    class PromptAdapter(gepa.GEPAAdapter):
        def evaluate(self, batch, candidate, capture_traces: bool = False):
            prompt_text = candidate.get("prompt", "")
            outputs = []
            scores = []
            trajectories = [] if capture_traces else None
            candidate_id = _candidate_id_from_text(prompt_text, iteration_ref["i"])
            iteration_ref["i"] += 1

            if scorer_mode == "claude-code":
                uuids = scoring_client.request_batch(
                    prompt_text=prompt_text,
                    samples=batch,
                    candidate_id=candidate_id,
                    iteration=iteration_ref["i"],
                    component="prompt",
                )
                if auto_fill:
                    auto_fill_pending(scoring_client)
                responses = scoring_client.load_batch(uuids)
                missing = [u for u, r in zip(uuids, responses) if r is None]
                if missing:
                    # Surface the "pending — re-run" condition through scores=0
                    # but also set a sentinel on outputs so the harness can detect.
                    for s, u, r in zip(batch, uuids, responses):
                        outputs.append(
                            {"sample_id": s.get("id"), "uuid": u, "pending": True}
                        )
                        scores.append(0.0)
                        if trajectories is not None:
                            trajectories.append(
                                {"pending": True, "uuid": u, "sample": s}
                            )
                    return EvaluationBatch(
                        outputs=outputs, scores=scores, trajectories=trajectories
                    )
                # All ready — aggregate to a single per-sample score
                for s, u, r in zip(batch, uuids, responses):
                    axes = ["relevance", "factuality", "actionability"]
                    sc = round(
                        sum(float(r.get(a, 0.0)) for a in axes) / len(axes), 4
                    )
                    outputs.append({"sample_id": s.get("id"), "scores": r, "uuid": u})
                    scores.append(sc)
                    if trajectories is not None:
                        trajectories.append(
                            {
                                "sample_id": s.get("id"),
                                "uuid": u,
                                "score": sc,
                                "rationale": r.get("rationale", ""),
                                "sample": s,
                                "prompt_excerpt": prompt_text[:600],
                            }
                        )
                return EvaluationBatch(
                    outputs=outputs, scores=scores, trajectories=trajectories
                )

            # mock scorer fallback (Week 1 path, still available)
            for s in batch:
                sc = eval_mod.mock_score_sample(prompt_text, s)
                outputs.append({"sample_id": s.get("id"), "scores": sc})
                axes = ["relevance", "factuality", "actionability"]
                scores.append(
                    round(sum(float(sc.get(a, 0.0)) for a in axes) / len(axes), 4)
                )
                if trajectories is not None:
                    trajectories.append(
                        {
                            "sample_id": s.get("id"),
                            "score": scores[-1],
                            "rationale": "mock",
                            "sample": s,
                            "prompt_excerpt": prompt_text[:600],
                        }
                    )
            return EvaluationBatch(
                outputs=outputs, scores=scores, trajectories=trajectories
            )

        def make_reflective_dataset(
            self, candidate, eval_batch, components_to_update
        ):
            """Build feedback per component for the reflection_lm.

            For our single 'prompt' component, surface each sample's intent +
            rationale + score so reflection_lm can propose a better variant.
            """
            data = []
            trajs = eval_batch.trajectories or []
            for t, sc in zip(trajs, eval_batch.scores):
                if t.get("pending"):
                    continue
                data.append(
                    {
                        "Inputs": {
                            "intent": t.get("sample", {}).get("intent", ""),
                            "expected_decision": t.get("sample", {}).get(
                                "expected_decision", ""
                            ),
                        },
                        "Generated Outputs": (t.get("rationale") or "")[:300],
                        "Feedback": f"score={sc:.3f}  "
                        + ("LOW — improve specificity & action-steps" if sc < 0.5 else "OK"),
                    }
                )
            if not data:
                # GEPA needs at least one example; emit a placeholder so the loop
                # advances even when all responses are pending.
                data.append(
                    {
                        "Inputs": {"intent": "<no data>"},
                        "Generated Outputs": "<pending>",
                        "Feedback": "no scored samples available yet",
                    }
                )
            return {c: data for c in components_to_update}

    return PromptAdapter()


def _candidate_id_from_text(text: str, iteration: int) -> str:
    import hashlib

    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return f"cand-{iteration:03d}-{h}"


# ---- Pareto-front extraction --------------------------------------------


def extract_pareto_front(result, frontier_size: int) -> list[dict]:
    """Extract top-N Pareto-front candidates from a GEPAResult."""
    fronts: list[dict] = []
    candidates = getattr(result, "candidates", None) or []
    val_scores = (
        getattr(result, "val_aggregate_scores", None)
        or getattr(result, "aggregate_scores", None)
        or []
    )
    pareto_idx = getattr(result, "pareto_front_valset", None) or set()

    seen_ids: set[str] = set()
    for i, cand in enumerate(candidates):
        prompt_text = cand.get("prompt", "") if isinstance(cand, dict) else str(cand)
        cand_id = _candidate_id_from_text(prompt_text, i)
        if cand_id in seen_ids:
            continue
        seen_ids.add(cand_id)
        agg = float(val_scores[i]) if i < len(val_scores) else 0.0
        fronts.append(
            {
                "variant_id": cand_id,
                "candidate_index": i,
                "score": round(agg, 4),
                "length": len(prompt_text),
                "in_pareto_front": i in pareto_idx if pareto_idx else True,
                "prompt_text": prompt_text,
            }
        )

    # Rank: pareto-front first, then by score desc, then by shorter length
    fronts.sort(key=lambda v: (-int(v["in_pareto_front"]), -v["score"], v["length"]))
    return fronts[:frontier_size]


def write_candidate_files(
    pareto: list[dict],
    baseline_path: Path,
    iteration_count: int,
    real_apply: bool,
) -> list[Path]:
    """Write each Pareto-front variant to candidates/<stem>-v0.3.N/<filename>.

    Layer 4 detect-only: file is always written, but only with
    `# CANDIDATE — NOT LIVE` header. Promotion to .vault-agents/ requires a
    separate Week-3 step with user-confirm + Critic-review.
    """
    if not real_apply:
        return []

    written: list[Path] = []
    stem = baseline_path.stem
    for n, v in enumerate(pareto):
        if not v["in_pareto_front"] and len(pareto) > 3:
            # keep only frontier members when we have enough
            continue
        outdir = CANDIDATES_DIR / f"{stem}-v0.3.{n}"
        # Safety preflight
        blocked, reason = forbidden_target_check(outdir)
        if blocked:
            print(f"[safety] skip {outdir}: {reason}", file=sys.stderr)
            continue
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / f"{stem}.md"
        header = (
            "<!-- CANDIDATE — NOT LIVE.\n"
            "     Source: gepa-prompt-mutate (B-8 Week 2 real-loop, 2026-05-17)\n"
            f"     Variant: {v['variant_id']}  score={v['score']:.3f}  "
            f"length={v['length']}  iteration_count={iteration_count}\n"
            f"     Pareto-front: {v['in_pareto_front']}\n"
            "     Layer-4 detect-only: promotion to .vault-agents/prompts/ requires\n"
            "     user-confirm + Critic-review (Week 3+).\n"
            "-->\n\n"
        )
        out.write_text(header + v["prompt_text"])
        meta = outdir / "meta.json"
        meta.write_text(
            json.dumps(
                {
                    "variant_id": v["variant_id"],
                    "score": v["score"],
                    "length": v["length"],
                    "in_pareto_front": v["in_pareto_front"],
                    "candidate_index": v["candidate_index"],
                    "baseline_source": str(baseline_path),
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "iteration_count": iteration_count,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        written.append(out)
    return written


# ---- Audit log -----------------------------------------------------------


def write_gepa_log(entry: dict):
    GEPA_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(GEPA_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_mutation_log(entry: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(MUTATIONS_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---- Main ---------------------------------------------------------------


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser(
        description="B-8 GEPA prompt-mutate (Week 2 real-loop, Pareto-front, candidates only)"
    )
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--eval-data", required=True, type=Path)
    ap.add_argument(
        "--budget",
        type=int,
        default=12,
        help="max_metric_calls budget (Week 2: 8-30; Week 3+: 30-100)",
    )
    ap.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="cap GEPA iterations (3-5 for Week 2 smoke)",
    )
    ap.add_argument(
        "--scorer",
        default="claude-code",
        choices=["mock", "claude-code", "anthropic"],
        help="Week 2: claude-code (subagent-fanout). 'mock' = deterministic rule-based.",
    )
    ap.add_argument(
        "--frontier-size",
        type=int,
        default=4,
        help="Target Pareto-front size 3-5",
    )
    ap.add_argument(
        "--minibatch",
        type=int,
        default=3,
        help="reflection_minibatch_size (smaller = faster smoke)",
    )
    ap.add_argument(
        "--seed", type=int, default=0, help="RNG seed for reproducibility"
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print front, write NOTHING to candidates/",
    )
    ap.add_argument(
        "--auto-fill-synth",
        action="store_true",
        help="(smoke) synthesise scoring responses in-process; skips real subagent",
    )
    args = ap.parse_args()

    if not args.baseline.exists():
        print(f"[err] baseline not found: {args.baseline}", file=sys.stderr)
        sys.exit(1)
    if not args.eval_data.exists():
        print(f"[err] eval-data not found: {args.eval_data}", file=sys.stderr)
        sys.exit(1)

    # Layer 1+2: ENV-gate + forbidden-target preflight
    write_enabled = env_apply_enabled() and not args.dry_run
    if write_enabled:
        blocked, reason = forbidden_target_check(CANDIDATES_DIR)
        if blocked:
            print(f"[safety] candidates-dir blocked: {reason}", file=sys.stderr)
            sys.exit(3)
    else:
        print(
            "[safety] DRY-RUN (Layer 1) — set VAULT_RSI_APPLY=1 (and omit --dry-run) "
            "to write candidates/."
        )

    # gepa lib availability
    try:
        import gepa  # noqa: F401
    except ImportError:
        print("[err] gepa-ai/gepa not installed. Run: pip install gepa", file=sys.stderr)
        sys.exit(2)

    eval_mod = _load_eval_module()
    baseline_text = args.baseline.read_text()
    samples = load_jsonl(args.eval_data)
    if len(samples) < 3:
        print(f"[err] eval-data must have >=3 samples (got {len(samples)})", file=sys.stderr)
        sys.exit(1)

    # Baseline-score for reference (always with mock — deterministic, $0)
    baseline_scores = [eval_mod.mock_score_sample(baseline_text, s) for s in samples]
    baseline_agg = eval_mod.aggregate(baseline_scores)
    print(f"[baseline] {args.baseline.name}  mock-scorer ref")
    for k, v in baseline_agg.items():
        if k != "n_samples":
            print(f"           {k:14s} {v}")

    # Scoring client setup (only used for claude-code scorer)
    scorer_mod = _load_scorer_module()
    client = scorer_mod.ScoringClient(
        pending_dir=SCORING_PENDING, responses_dir=SCORING_RESPONSES
    )

    iteration_ref = {"i": 0}
    adapter = build_adapter(
        scorer_mode=args.scorer,
        samples=samples,
        scoring_client=client,
        eval_mod=eval_mod,
        iteration_ref=iteration_ref,
        auto_fill=args.auto_fill_synth,
    )

    # reflection_lm — synth mutator (Week 2 smoke). Real subagent: Week 3.
    reflection_lm = scorer_mod.ClaudeCodeReflectionLM(client=client, mode="auto-fill")

    seed_candidate = {"prompt": baseline_text}

    print(
        f"\n[gepa.optimize] budget={args.budget}  max-iter={args.max_iterations}  "
        f"frontier={args.frontier_size}  scorer={args.scorer}  "
        f"auto-fill-synth={args.auto_fill_synth}  apply={'YES' if write_enabled else 'no'}"
    )

    try:
        result = gepa.optimize(
            seed_candidate=seed_candidate,
            trainset=samples,
            valset=samples,
            adapter=adapter,
            reflection_lm=reflection_lm,
            reflection_minibatch_size=min(args.minibatch, len(samples)),
            max_metric_calls=args.budget,
            candidate_selection_strategy="pareto",
            seed=args.seed,
            raise_on_exception=False,
            cache_evaluation=True,
        )
    except Exception as e:  # GEPA propagates loop errors; treat as recoverable
        print(f"[err] gepa.optimize raised: {type(e).__name__}: {e}", file=sys.stderr)
        # Still write an audit entry so the loop is observable.
        write_gepa_log(
            {
                "event": "gepa_optimize_failed",
                "ts": datetime.now(timezone.utc).isoformat(),
                "baseline": str(args.baseline),
                "error_type": type(e).__name__,
                "error": str(e)[:400],
                "iteration_count": iteration_ref["i"],
                "scorer": args.scorer,
            }
        )
        sys.exit(2)

    # Detect pending state (claude-code scorer with no auto-fill, real subagent missing)
    unanswered = client.pending_count() if args.scorer == "claude-code" else 0
    if unanswered > 0 and not args.auto_fill_synth:
        print(
            f"\n[pending] {unanswered} scoring requests unanswered in "
            f"{SCORING_PENDING}.\n"
            "          A general-purpose Agent must fill the matching\n"
            f"          .response.json files in {SCORING_RESPONSES} then re-run."
        )
        write_gepa_log(
            {
                "event": "gepa_optimize_pending",
                "ts": datetime.now(timezone.utc).isoformat(),
                "baseline": str(args.baseline),
                "pending_count": unanswered,
                "iteration_count": iteration_ref["i"],
                "scorer": args.scorer,
            }
        )
        sys.exit(4)

    pareto = extract_pareto_front(result, args.frontier_size)
    iteration_count = iteration_ref["i"]
    print(f"\n[pareto-front]  target-size={args.frontier_size}  iterations={iteration_count}")
    for v in pareto:
        marker = "★" if v["in_pareto_front"] else "·"
        print(
            f"  {marker} {v['variant_id']:24s}  score={v['score']:.3f}  "
            f"len={v['length']}"
        )

    written = write_candidate_files(
        pareto, args.baseline, iteration_count, real_apply=write_enabled
    )
    if written:
        print(f"\n[write] {len(written)} candidate file(s):")
        for p in written:
            print(f"  → {p}")
    else:
        print(
            "\n[write] (dry-run) 0 files. Use VAULT_RSI_APPLY=1 to materialize candidates."
        )

    # Audit logs
    write_gepa_log(
        {
            "event": "gepa_optimize_complete",
            "ts": datetime.now(timezone.utc).isoformat(),
            "baseline": str(args.baseline),
            "eval_data": str(args.eval_data),
            "scorer": args.scorer,
            "budget": args.budget,
            "max_iterations": args.max_iterations,
            "iteration_count": iteration_count,
            "frontier_size": args.frontier_size,
            "auto_fill_synth": args.auto_fill_synth,
            "baseline_aggregate": baseline_agg,
            "pareto_front": [
                {k: v for k, v in p.items() if k != "prompt_text"} for p in pareto
            ],
            "candidates_written": len(written),
            "dry_run": not write_enabled,
            "real_apply": write_enabled,
        }
    )
    write_mutation_log(
        {
            "event": "gepa_prompt_mutate",
            "ts": datetime.now(timezone.utc).isoformat(),
            "baseline": str(args.baseline),
            "scorer": args.scorer,
            "iteration_count": iteration_count,
            "pareto_size": len(pareto),
            "candidates_written": len(written),
            "dry_run": not write_enabled,
        }
    )
    print(f"\n[log] {GEPA_LOG}")
    print(f"[log] {MUTATIONS_LOG}")


if __name__ == "__main__":
    main()

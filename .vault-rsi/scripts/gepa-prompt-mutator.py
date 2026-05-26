#!/usr/bin/env python3
"""
gepa-prompt-mutator — Prompt Evolution (RSI Réteg 2, GEPA + DSPy).

ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Sprint: B-8 Réteg 2 — UTOLSÓ, safety-gated.

A meglévő prompt-template-ek (orchestrator/worker/critic/summarizer — B-6 output)
iteratív finomítása GEPA mutáción keresztül.

⚠️ SAFETY-GATE: RSI_MODE=enabled kell. Default disabled.
⚠️ Pareto-front fenntartás: NEM 1 "legjobb" prompt, hanem 3-5 specialista-változat.
⚠️ Length regularization: prompt-bloat ellen (Phase A+ insight: 4× tömörítés
   minőségromlás nélkül).

Usage:
    RSI_MODE=enabled gepa-prompt-mutator --target worker --iter 1
    RSI_MODE=enabled gepa-prompt-mutator --pareto-frontier         # show current 3-5 variants
"""

import argparse
import os
import sys
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
PROMPTS_DIR = VAULT_ROOT / ".vault-agents" / "prompts"
PARETO_DIR = VAULT_ROOT / ".vault-rsi" / "pareto-variants"
EVENT_LOG = VAULT_ROOT / ".vault-rsi" / "mutations.jsonl"
RSI_MODE = os.environ.get("RSI_MODE", "disabled")


def safety_gate():
    if RSI_MODE != "enabled":
        print("⚠️  RSI safety-gate: gepa-prompt-mutator disabled by default.")
        print("    Enable with: RSI_MODE=enabled gepa-prompt-mutator ...")
        print("    PRECONDITION: B-6 (multi-agent) stabilizálódott >4 hét production.")
        sys.exit(2)


def gepa_mutate_stub(target_prompt: str, iter_n: int) -> dict:
    """
    PLACEHOLDER GEPA mutation.

    Real impl (Phase C+):
      1. Load target prompt (e.g. .vault-agents/prompts/worker.md)
      2. Identify failure-patterns: events.jsonl Filesystem-as-State (B-6)
         → which task-types fail most often?
      3. GEPA: Genetic-style mutation with Pareto-front (3-5 specialista-variants)
      4. Length regularization — penalty for token-bloat (4× compression target)
      5. Eval on held-out task-set (B-3 eval-pipeline)
      6. Critic-review (B-6 reuse) before write-back
      7. Sandbox-commit: tag git-commit `rsi-mutation-prompt-<target>-<iter>` + Pareto-merge
    """
    return {"target": target_prompt, "iter": iter_n, "stub": True}


def main():
    safety_gate()

    ap = argparse.ArgumentParser(description="GEPA prompt mutator (B-8 Réteg 2)")
    ap.add_argument("--target", choices=["orchestrator", "worker", "critic", "summarizer"])
    ap.add_argument("--iter", type=int, default=1)
    ap.add_argument("--pareto-frontier", action="store_true", help="Show current variants")
    args = ap.parse_args()

    if args.pareto_frontier:
        if PARETO_DIR.exists():
            print(f"Current Pareto-variants in {PARETO_DIR}:")
            for f in sorted(PARETO_DIR.glob("*.md")):
                print(f"  {f.name}")
        else:
            print(f"[skeleton] No Pareto-variants yet — Phase C+ first run will populate {PARETO_DIR}")
        return

    if not args.target:
        ap.print_help()
        sys.exit(1)

    _ = gepa_mutate_stub(args.target, args.iter)
    print(f"[stub] GEPA mutation target={args.target} iter={args.iter}")
    print(f"       Sandbox-commit tag pattern: rsi-mutation-prompt-{args.target}-{args.iter}")
    print("       Critic-review (B-6) mandatory before write-back.")


if __name__ == "__main__":
    main()

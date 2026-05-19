#!/usr/bin/env python3
"""
vault-skill-suggest — Skill Library Growth (RSI Réteg 1).

ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Sprint: B-8 (UTOLSÓ, safety-gated)
Status: SKELETON-ONLY. RSI_MODE=disabled DEFAULT. Csak B-1..B-7 stabilizálódása után!

A /11.11stop poszt-hook detektálja, ha 3+ session-ben azonos pattern (G-Eval-detected),
és auto-draftol új SKILL.md-t a meglévő skill-template-ből (ReCreate-stílus).

⚠️ SAFETY-GATE: a script csak RSI_MODE=enabled ENV-flag-gel fut le. Default disabled.

Usage:
    RSI_MODE=enabled vault-skill-suggest --analyze-last 30        # 30 napos session-history
    vault-skill-suggest --dry-run --analyze-last 30               # preview, NEM ír
"""

import argparse
import os
import sys
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
SKILLS_DIR = Path("/root/.claude/skills")
RSI_MODE = os.environ.get("RSI_MODE", "disabled")


def safety_gate():
    if RSI_MODE != "enabled":
        print("⚠️  RSI safety-gate: script disabled by default.")
        print("    Enable with: RSI_MODE=enabled vault-skill-suggest ...")
        print("    PRECONDITION: B-1..B-7 sprint-ek stabilizálódtak (>4 hét production).")
        sys.exit(2)


def detect_pattern_stub(session_paths: list[Path]) -> list[dict]:
    """
    PLACEHOLDER pattern-detector.

    Real impl (Phase C+ post-B-7-stabilization):
      1. G-Eval Learning-bullets from last 30 sessions (B-1 reuse)
      2. Embedding cluster (bge-m3, B-2 reuse) → semantic-similar pattern detection
      3. If 3+ sessions with similar Learning → skill-suggest trigger
      4. Find nearest existing skill (B-4 skill-search) — base for ReCreate
      5. Generate diff-template (Critic-review B-6 mandatory)
    """
    return []


def main():
    safety_gate()

    ap = argparse.ArgumentParser(description="Vault skill suggest (B-8 Réteg 1)")
    ap.add_argument("--analyze-last", type=int, default=30, help="Days of session-history")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    patterns = detect_pattern_stub(sorted(SESSIONS_DIR.glob("*.md")))

    if not patterns:
        print("[skeleton] No pattern detection yet — Phase C+ implementation")
        return

    for p in patterns:
        if args.dry_run:
            print(f"  [dry-run] Would suggest: {p['skill_name']} (3+ session evidence)")
        else:
            print(f"  [stub] Critic-review path: {p['skill_name']}")


if __name__ == "__main__":
    main()

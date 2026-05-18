#!/usr/bin/env python3
"""
vault-reflect — Self-Reflection Loop (RSI Réteg 3, Reflexion + ReFlect-Harness).

ADR: 07-Decisions/2026-05-12 sv-2 recursive self-improvement arch.md
Sprint: B-8 Réteg 3 — UTOLSÓ, safety-gated.

A 08-Sessions/ Learnings-eit felhasználja a saját jövőbeli viselkedés finomításához.
Output: 05-Memory/Auto-reflections/<date>.md (MANUÁLIS PROMÓCIÓ szükséges).

⚠️ SAFETY-GATE: RSI_MODE=enabled kell. Default disabled.
⚠️ Auto-reflections NEM automatikusan promóciózódnak — emberi review minden esetben.

Usage:
    RSI_MODE=enabled vault-reflect --week           # last 7 days
    RSI_MODE=enabled vault-reflect --month          # last 30 days
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
REFLECT_DIR = VAULT_ROOT / "05-Memory" / "Auto-reflections"
RSI_MODE = os.environ.get("RSI_MODE", "disabled")


def safety_gate():
    if RSI_MODE != "enabled":
        print("⚠️  RSI safety-gate: vault-reflect disabled by default.")
        print("    Enable with: RSI_MODE=enabled vault-reflect ...")
        print("    PRECONDITION: B-1..B-7 stabilizálódott + ReFlect-harness validated.")
        sys.exit(2)


def reflect_stub(days: int) -> str:
    """
    PLACEHOLDER reflection generator.

    Real impl (Phase C+):
      1. Load last N days of session Learnings (B-1 KO-DB query)
      2. ReFlect deterministic harness — Python shape-validator on Learning-mutations
      3. LLM synthesis (Sonnet) — verbal memory buffer (Reflexion-minta)
      4. Output to 05-Memory/Auto-reflections/<date>.md
      5. NEVER auto-promote to 05-Memory/ root or 11-wiki/ — emberi review-mandatory
    """
    return f"# Auto-reflection ({days}-day window)\n\n[skeleton — Phase C+ implementation]\n"


def main():
    safety_gate()

    ap = argparse.ArgumentParser(description="Vault reflect (B-8 Réteg 3)")
    ap.add_argument("--week", action="store_true", help="7-day window")
    ap.add_argument("--month", action="store_true", help="30-day window")
    args = ap.parse_args()

    days = 7 if args.week else 30 if args.month else 7
    content = reflect_stub(days)

    REFLECT_DIR.mkdir(parents=True, exist_ok=True)
    out = REFLECT_DIR / f"{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    print(f"[stub] Would write reflection to {out}")
    print("       Manual promotion to 05-Memory/ root or 11-wiki/ requires user review.")


if __name__ == "__main__":
    main()

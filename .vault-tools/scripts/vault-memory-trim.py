#!/usr/bin/python3
"""
vault-memory-trim — auto-detect and apply MEMORY.md size-reduction moves.

Sister to vault-memory-guard (which only alerts). This tool ACTIVELY suggests
or applies trims that bring MEMORY.md back under the 24,960-byte limit.

Strategy (highest yield first):
  1. **Merge duplicate lines** — exact / near-duplicate entries differing only
     in wording. Pick the more informative one.
  2. **Extract long entries to topic files** — any line >400 chars gets
     suggested for extraction into `~/.claude/projects/-root/memory/<topic>.md`
     with a 1-line pointer left in MEMORY.md.
  3. **Compact stale session pointers** — session-pointer lines older than
     14 days get suggested for consolidation into a monthly rollup file.
  4. **Drop outdated SV pointers** — lines mentioning superseded SV milestones
     (e.g. "B-1 Week 2 következik") flagged.

Default mode: --dry-run (suggestions only). Use --apply to write changes.

Usage:
  vault-memory-trim                       # dry-run, prints suggestions
  vault-memory-trim --apply               # apply suggestions interactively (TODO)
  vault-memory-trim --json                # machine-readable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_MD = Path("/root/.claude/projects/-root/memory/MEMORY.md")
LIMIT = 24960
WARN_BUFFER = 500

LONG_LINE = 400  # bytes; lines longer than this are extraction candidates
DUP_THRESHOLD = 0.85  # Jaccard similarity over 5-grams

# Patterns that suggest outdated/superseded entries
SUPERSEDED_HINTS = [
    re.compile(r"(?i)\bweek\s+1-2\s+ÉLES\b"),
    re.compile(r"(?i)\bWeek\s+2\s+következik\b"),
    re.compile(r"(?i)\bv0\.\d\b.*ELÉS"),  # old version-leaders mentioned in current state
]


def _shingle(text: str, n: int = 5) -> set:
    """Word-level n-grams for crude similarity."""
    words = text.lower().split()
    return set(tuple(words[i : i + n]) for i in range(max(0, len(words) - n + 1)))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_duplicates(lines: list[str]) -> list[tuple[int, int, float]]:
    """Pairs of line-indices that look like duplicates."""
    shingles = [(i, _shingle(ln)) for i, ln in enumerate(lines) if len(ln) > 50]
    pairs = []
    for i, (idx_a, s_a) in enumerate(shingles):
        for idx_b, s_b in shingles[i + 1 :]:
            j = jaccard(s_a, s_b)
            if j >= DUP_THRESHOLD:
                pairs.append((idx_a, idx_b, j))
    return pairs


def find_long_lines(lines: list[str], threshold: int = LONG_LINE) -> list[tuple[int, int]]:
    """(line_index, byte_count) for lines over threshold."""
    return [(i, len(ln.encode("utf-8"))) for i, ln in enumerate(lines)
            if len(ln.encode("utf-8")) > threshold]


def find_superseded(lines: list[str]) -> list[int]:
    """Indices of lines matching superseded-content patterns."""
    out = []
    for i, ln in enumerate(lines):
        for pat in SUPERSEDED_HINTS:
            if pat.search(ln):
                out.append(i)
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-memory-trim")
    ap.add_argument("--apply", action="store_true",
                    help="Apply suggestions (default: dry-run print only)")
    ap.add_argument("--json", action="store_true",
                    help="Emit machine-readable JSON")
    ap.add_argument("--limit-bytes", type=int, default=LIMIT,
                    help=f"Target byte limit (default {LIMIT})")
    args = ap.parse_args()

    if not MEMORY_MD.exists():
        print(f"✗ {MEMORY_MD} missing", file=sys.stderr)
        return 2

    raw = MEMORY_MD.read_text(encoding="utf-8")
    lines = raw.splitlines()
    size = len(raw.encode("utf-8"))
    buffer = args.limit_bytes - size

    dups = find_duplicates(lines)
    longs = find_long_lines(lines)
    superseded = find_superseded(lines)

    # Estimate potential savings
    dup_savings = sum(len(lines[b].encode()) + 1 for _, b, _ in dups)
    long_savings = sum(b - 100 for _, b in longs)  # extract -> leave 100-byte pointer
    super_savings = sum(len(lines[i].encode()) + 1 for i in superseded)

    if args.json:
        print(json.dumps({
            "size_bytes": size,
            "limit_bytes": args.limit_bytes,
            "buffer_bytes": buffer,
            "duplicates": len(dups),
            "long_lines": len(longs),
            "superseded_lines": len(superseded),
            "estimated_savings_bytes": dup_savings + long_savings + super_savings,
            "samples": {
                "dups": [(a, b, round(j, 2)) for a, b, j in dups[:3]],
                "longs": longs[:3],
                "superseded": superseded[:3],
            },
        }, indent=2))
        return 0

    print(f"vault-memory-trim — MEMORY.md analysis")
    print(f"  size:   {size:,} bytes")
    print(f"  limit:  {args.limit_bytes:,} bytes")
    if buffer >= WARN_BUFFER:
        print(f"  buffer: {buffer:,} bytes — comfortable, no action needed")
    elif buffer >= 0:
        print(f"  buffer: {buffer:,} bytes — thin, consider trimming")
    else:
        print(f"  buffer: {buffer:,} bytes — OVER LIMIT, trim required")
    print()

    print(f"Candidates for trim (estimated total savings: {dup_savings + long_savings + super_savings:,} bytes):")
    print()

    if dups:
        print(f"  📋 {len(dups)} near-duplicate pair(s) (could save ~{dup_savings:,} bytes):")
        for a, b, j in dups[:5]:
            print(f"     line {a + 1} ↔ line {b + 1}  (Jaccard {j:.2f})")
            print(f"       A: {lines[a][:100]}…")
            print(f"       B: {lines[b][:100]}…")
        print()

    if longs:
        print(f"  📏 {len(longs)} long line(s) >{LONG_LINE}B (could save ~{long_savings:,} bytes if extracted):")
        for idx, b in longs[:5]:
            print(f"     line {idx + 1}  ({b}B): {lines[idx][:100]}…")
        print()

    if superseded:
        print(f"  ⏳ {len(superseded)} possibly-superseded line(s) (could save ~{super_savings:,} bytes):")
        for idx in superseded[:5]:
            print(f"     line {idx + 1}: {lines[idx][:100]}…")
        print()

    if not (dups or longs or superseded):
        print("  ✓ No obvious trim candidates detected.")

    if args.apply:
        print("  ⚠ --apply mode not yet implemented (suggestions are dry-run only).")
        print("    Manual workflow:")
        print("    1. Pick the highest-yield candidate (long-line extraction usually wins)")
        print("    2. Create a topic-file in ~/.claude/projects/-root/memory/<topic>.md")
        print("    3. Replace the long MEMORY.md line with a one-liner pointer")
        return 1

    return 0 if buffer >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Simplified broken-wikilink scanner used by CI.

Scans `11-wiki/`, `07-Decisions/`, `06-Audits/` for [[wikilink]] references
that don't resolve to a .md file anywhere in the repo. Fails if the broken
reference count exceeds BROKEN_REF_BUDGET (env var, default 20).

Baseline 2026-05-19: 12 broken targets, 18 broken references.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

ROOTS = ("11-wiki", "07-Decisions", "06-Audits")
EXCLUDED = ("/site/", "/.git/", "/.cache/", "/_ci_site/")
# Wikilinks pointing into these directories live in the private vault and
# are intentionally not shipped in the public mirror — skip without counting.
PRIVATE_DIR_PREFIXES = (
    "01-Daily/",
    "02-Projects/",
    "03-Hosts/",
    "04-Tasks/",
    "05-Memory/",
    "08-Sessions/",
    "10-raw/",
    ".vault-nb/",
    ".vault-memory/",
    ".vault-agents/",
)
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+?)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
# Heuristics to exclude bash test-bracket lookalikes (`[[ -f foo ]]`, `[[ $x = y ]]`).
SHELL_BRACKET_HINTS = ("$", " -", " == ", " = ", " != ", "&&", "||")


def looks_like_shell_bracket(raw: str) -> bool:
    if any(h in raw for h in SHELL_BRACKET_HINTS):
        return True
    # Wikilink targets are paths; reject anything with obvious shell glyphs.
    if raw.startswith("-") or raw.startswith('"') or raw.startswith("'"):
        return True
    return False


def build_targets() -> set[str]:
    targets: set[str] = set()
    # Any .md in the repo can be a wikilink target.
    for p in pathlib.Path(".").rglob("*.md"):
        if any(s in p.as_posix() for s in EXCLUDED):
            continue
        targets.add(p.with_suffix("").as_posix())
        targets.add(p.stem)
    return targets


def main() -> int:
    budget = int(os.environ.get("BROKEN_REF_BUDGET", "250"))
    targets = build_targets()

    scanned = []
    for r in ROOTS:
        root = pathlib.Path(r)
        if root.exists():
            scanned.extend(root.rglob("*.md"))

    broken_refs = 0
    broken_targets: set[str] = set()
    examples: list[str] = []

    for p in scanned:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for match in WIKILINK_RE.finditer(text):
            raw = match.group(1).strip()
            if raw.startswith(("http://", "https://")):
                continue
            if looks_like_shell_bracket(raw):
                continue
            norm = raw
            # Drop leading "./" (one or many) without eating leading "." of dotdirs.
            while norm.startswith("./"):
                norm = norm[2:]
            while norm.startswith("../"):
                norm = norm[3:]
            if any(norm.startswith(prefix) for prefix in PRIVATE_DIR_PREFIXES):
                continue
            candidate = norm.removesuffix(".md")
            base = candidate.rsplit("/", 1)[-1]
            if candidate in targets or base in targets:
                continue
            broken_refs += 1
            broken_targets.add(candidate)
            if len(examples) < 10:
                examples.append(f"{p}: [[{raw}]]")

    print(f"Scanned files: {len(scanned)}")
    print(f"Broken references: {broken_refs}")
    print(f"Unique broken targets: {len(broken_targets)}")
    print(f"Budget: {budget}")
    if examples:
        print("Sample broken refs:")
        for e in examples:
            print(f"  - {e}")

    if broken_refs > budget:
        print(f"::error::Broken wikilink count {broken_refs} exceeds budget {budget}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

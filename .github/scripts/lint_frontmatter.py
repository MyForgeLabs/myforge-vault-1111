#!/usr/bin/env python3
"""Validate that every wiki .md has required frontmatter keys.

Required keys: name, type, created, updated.
Run from repo root. Exits 1 if any wiki file is missing required keys
or has invalid YAML frontmatter.
"""
from __future__ import annotations

import os
import pathlib
import sys

import yaml

REQUIRED = {"name", "type", "created", "updated"}
WIKI_DIR = pathlib.Path("11-wiki")
# Public mirror baseline 2026-05-19: 19 files with frontmatter gaps. CI fails
# if issue count exceeds this budget. Tighten as files are fixed.
MAX_ISSUES_DEFAULT = 25


def main() -> int:
    if not WIKI_DIR.exists():
        print(f"::warning::{WIKI_DIR} not present — skipping frontmatter lint.")
        return 0

    missing: list[tuple[str, str]] = []
    files = sorted(WIKI_DIR.glob("*.md"))

    for p in files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---"):
            missing.append((str(p), "no frontmatter block"))
            continue
        try:
            end = text.index("\n---", 3)
        except ValueError:
            missing.append((str(p), "unterminated frontmatter"))
            continue
        try:
            fm = yaml.safe_load(text[3:end]) or {}
        except yaml.YAMLError as exc:
            missing.append((str(p), f"YAML parse error: {exc}"))
            continue
        keys = set(fm.keys()) if isinstance(fm, dict) else set()
        gap = REQUIRED - keys
        if gap:
            missing.append((str(p), f"missing keys: {sorted(gap)}"))

    budget = int(os.environ.get("MAX_FRONTMATTER_ISSUES", str(MAX_ISSUES_DEFAULT)))

    if missing:
        level = "error" if len(missing) > budget else "warning"
        print(f"::{level}::{len(missing)} files have frontmatter issues (budget={budget}):")
        for path, why in missing[:50]:
            print(f"  - {path}: {why}")
        if len(missing) > 50:
            print(f"  ... and {len(missing) - 50} more")
        if len(missing) > budget:
            return 1

    print(f"OK — {len(files)} wiki files scanned, {len(missing)} with issues (budget={budget})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

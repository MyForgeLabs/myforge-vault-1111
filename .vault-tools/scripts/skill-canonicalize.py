#!/usr/bin/env python3
"""
skill-canonicalize — normalize SKILL.md frontmatter across all installed skills.

ADR: 07-Decisions/2026-05-12 sv-4 tool composition arch.md
Sprint: B-4, Réteg 1 (Anthropic Agent Skills Progressive Disclosure).

Status: Week 1-α (2026-05-17). Audit baseline ÉLES.
        Real LLM-aided normalize Week 1 Day 3-4.

Anthropic standard YAML schema:
  name: <kebab-case>             # REQUIRED (Anthropic spec)
  description: <one-line trigger> # REQUIRED (Anthropic spec)
  tags: [<area>, ...]            # RECOMMENDED (vault convention)
  trigger_keywords: [<w1>, ...]  # RECOMMENDED (vault convention)
  level: 1 | 2 | 3               # OPTIONAL (Progressive Disclosure)

Compliance levels:
  fully_compliant   — all 4 fields (name+description+tags+trigger_keywords) present
  spec_compliant    — name+description present (Anthropic spec minimum), missing recs
  partial           — has frontmatter but missing name OR description
  no_frontmatter    — file has no YAML block at all

Usage:
    skill-canonicalize --audit                      # baseline report
    skill-canonicalize --audit --json               # machine-readable
    skill-canonicalize --fix-trivially --dry-run    # preview trivial fixes (tags: [])
    skill-canonicalize --fix-trivially              # apply trivial fixes (creates .bak)
    skill-canonicalize --fix --dry-run              # LLM-aided fix preview (Week 1+)
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

# Skill roots to scan. .claude/.codex/.gemini all symlink to .agents/skills,
# so we dedupe by realpath. Plugin-installed skills (cached marketplaces)
# live under .claude/plugins.
SKILL_ROOTS = [
    Path("/root/.agents/skills"),
    Path("/root/.claude/plugins"),
]

# Anthropic spec: name + description are MUST. Vault convention adds tags + trigger_keywords.
REQUIRED_FIELDS = ["name", "description"]
RECOMMENDED_FIELDS = ["tags", "trigger_keywords"]
ALL_CANONICAL_FIELDS = REQUIRED_FIELDS + RECOMMENDED_FIELDS


def find_skill_files() -> list[Path]:
    """Return sorted, realpath-deduped list of SKILL.md files."""
    seen: set[str] = set()
    skills: list[Path] = []
    for root in SKILL_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("SKILL.md"):
            try:
                real = os.path.realpath(p)
            except OSError:
                real = str(p)
            if real in seen:
                continue
            seen.add(real)
            skills.append(p)
    return sorted(skills, key=lambda p: str(p))


def parse_frontmatter(text: str) -> str | None:
    """Return YAML frontmatter block or None."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    return m.group(1) if m else None


def has_field(fm: str, field: str) -> bool:
    """True if field is declared at top level of YAML frontmatter."""
    return bool(re.search(rf"^{re.escape(field)}\s*:", fm, re.MULTILINE))


def audit_skill(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"path": str(path), "status": "read_error", "error": str(e),
                "missing_required": [], "missing_recommended": []}

    fm = parse_frontmatter(text)
    if fm is None:
        return {"path": str(path), "status": "no_frontmatter",
                "missing_required": list(REQUIRED_FIELDS),
                "missing_recommended": list(RECOMMENDED_FIELDS)}

    missing_required = [f for f in REQUIRED_FIELDS if not has_field(fm, f)]
    missing_recommended = [f for f in RECOMMENDED_FIELDS if not has_field(fm, f)]

    if missing_required:
        status = "partial"
    elif missing_recommended:
        status = "spec_compliant"
    else:
        status = "fully_compliant"

    return {
        "path": str(path),
        "status": status,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
    }


def fix_trivially(path: Path, audit: dict, dry_run: bool = True) -> dict:
    """
    Apply ONLY trivial, mechanical fixes:
      - Missing `tags` field → add `tags: []` after the last frontmatter line.

    Anything harder (missing `name`, `description`, `trigger_keywords` —
    these need semantic LLM-aided generation) is flagged for human review.
    """
    if audit["status"] in ("no_frontmatter", "partial", "read_error"):
        return {"path": str(path), "fixed": False, "reason": "needs_human_review",
                "status": audit["status"]}

    missing = audit.get("missing_recommended", [])
    trivial_fixable = [f for f in missing if f == "tags"]
    needs_review = [f for f in missing if f != "tags"]

    if not trivial_fixable:
        return {"path": str(path), "fixed": False, "reason": "nothing_trivially_fixable",
                "needs_review": needs_review}

    text = path.read_text(encoding="utf-8")
    m = re.match(r"^(---\r?\n)(.*?)(\r?\n---)", text, re.DOTALL)
    if not m:
        return {"path": str(path), "fixed": False, "reason": "frontmatter_unparseable"}

    open_d, body, close_d = m.group(1), m.group(2), m.group(3)
    addition = "\ntags: []"
    new_fm = open_d + body + addition + close_d
    new_text = new_fm + text[m.end():]

    if dry_run:
        return {"path": str(path), "fixed": False, "would_fix": ["tags"],
                "needs_review": needs_review, "dry_run": True}

    path.with_suffix(path.suffix + ".bak").write_text(text, encoding="utf-8")
    path.write_text(new_text, encoding="utf-8")
    return {"path": str(path), "fixed": True, "added": ["tags"],
            "needs_review": needs_review, "backup": str(path) + ".bak"}


def summarize(audits: list[dict]) -> dict:
    statuses = Counter(a["status"] for a in audits)
    missing_req = Counter()
    missing_rec = Counter()
    for a in audits:
        for f in a.get("missing_required", []):
            missing_req[f] += 1
        for f in a.get("missing_recommended", []):
            missing_rec[f] += 1
    return {
        "total": len(audits),
        "by_status": dict(statuses),
        "missing_required_counts": dict(missing_req),
        "missing_recommended_counts": dict(missing_rec),
        "top_gaps": (missing_req + missing_rec).most_common(5),
    }


def print_human_report(audits: list[dict], summary: dict, verbose: bool = False) -> None:
    print(f"Found {summary['total']} SKILL.md files (realpath-deduped)")
    print(f"  Roots scanned: {[str(r) for r in SKILL_ROOTS if r.exists()]}")
    print()
    print("Compliance breakdown:")
    for status in ("fully_compliant", "spec_compliant", "partial", "no_frontmatter", "read_error"):
        n = summary["by_status"].get(status, 0)
        pct = (100.0 * n / summary["total"]) if summary["total"] else 0
        print(f"  {status:18s} {n:4d}  ({pct:5.1f}%)")
    print()
    if summary["missing_required_counts"]:
        print("Missing REQUIRED fields (Anthropic spec):")
        for f, n in sorted(summary["missing_required_counts"].items(), key=lambda x: -x[1]):
            print(f"  {f:20s} {n} skills")
        print()
    if summary["missing_recommended_counts"]:
        print("Missing RECOMMENDED fields (vault convention):")
        for f, n in sorted(summary["missing_recommended_counts"].items(), key=lambda x: -x[1]):
            print(f"  {f:20s} {n} skills")
        print()
    print("Top gaps (any field):")
    for f, n in summary["top_gaps"]:
        print(f"  {f:20s} {n}")
    if verbose:
        print()
        print("Non-fully-compliant skills:")
        for a in audits:
            if a["status"] != "fully_compliant":
                miss = a.get("missing_required", []) + a.get("missing_recommended", [])
                print(f"  [{a['status']:16s}] {a['path']} missing={miss}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill canonicalize (B-4 Week 1-α)")
    ap.add_argument("--audit", action="store_true",
                    help="Produce compliance audit (default if no other action)")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="List every non-compliant skill in human report")
    ap.add_argument("--json", action="store_true",
                    help="Output machine-readable JSON")
    ap.add_argument("--fix-trivially", action="store_true",
                    help="Apply only mechanical fixes (e.g. add `tags: []` if missing)")
    ap.add_argument("--fix", action="store_true",
                    help="LLM-aided full fix (Week 1 Day 3-4; not yet implemented)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview fixes without writing")
    args = ap.parse_args()

    skills = find_skill_files()
    audits = [audit_skill(s) for s in skills]
    summary = summarize(audits)

    # Default action is --audit if nothing else requested.
    do_audit = args.audit or not (args.fix_trivially or args.fix)

    if args.fix_trivially:
        results = [fix_trivially(Path(a["path"]), a, dry_run=args.dry_run) for a in audits]
        would_or_did = [r for r in results if r.get("fixed") or r.get("would_fix")]
        flagged = [r for r in results if r.get("needs_review")]
        if args.json:
            print(json.dumps({
                "mode": "fix-trivially",
                "dry_run": args.dry_run,
                "would_fix_count": sum(1 for r in results if r.get("would_fix")),
                "fixed_count": sum(1 for r in results if r.get("fixed")),
                "flagged_for_review_count": len(flagged),
                "results": [r for r in results if r.get("fixed") or r.get("would_fix") or r.get("needs_review")],
            }, ensure_ascii=False, indent=2))
        else:
            mode = "DRY-RUN" if args.dry_run else "APPLIED"
            print(f"[fix-trivially {mode}]")
            print(f"  Trivially fixable (tags: []): {sum(1 for r in results if r.get('would_fix') or r.get('fixed'))}")
            print(f"  Flagged for human review:     {len(flagged)}")
            if args.verbose:
                for r in would_or_did:
                    print(f"    would-fix {r['path']}")
        return 0

    if args.fix:
        print("[--fix] Not yet implemented — Week 1 Day 3-4 (LLM-aided field generation).")
        print("       Use --fix-trivially for mechanical-only fixes today.")
        return 2

    if do_audit:
        if args.json:
            print(json.dumps({"summary": summary, "audits": audits}, ensure_ascii=False, indent=2))
        else:
            print_human_report(audits, summary, verbose=args.verbose)
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

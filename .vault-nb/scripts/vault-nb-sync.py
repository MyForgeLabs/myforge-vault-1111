#!/root/.notebooklm-venv/bin/python3
"""
vault-nb-sync — per-projekt NotebookLM auto-sync (B-5 Réteg 1).

ADR: 07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch.md
Sprint: B-5, Week 1 Day 1-4.

Minden aktív projektnek (`02-Projects/<projekt>.md`) automatikus megfelelő
NotebookLM-notebook a háttérben. Idempotens.

Real implementation 2026-05-13 (B-5 Week 1):
- Default mode: AUDIT (report-only). Mutations require --commit.
- Avoid notebooklm --json bug (lásd 11-wiki/notebooklm-cli-gotchas #1)
- Cross-vault contamination guard (#8): explicit -n <NB_ID> minden parancsban

Usage:
    vault-nb-sync                       # audit: report mit kéne tenni
    vault-nb-sync --commit              # create + sync (élesben)
    vault-nb-sync --project <slug>      # csak egy projekt
    vault-nb-sync --project <slug> --commit
    vault-nb-sync --cron                # cron mode — silent unless changes
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
PROJECTS_DIR = VAULT_ROOT / "02-Projects"
DECISIONS_DIR = VAULT_ROOT / "07-Decisions"
MEMORY_DIR = VAULT_ROOT / "05-Memory"
NOTEBOOKLM = os.environ.get("NOTEBOOKLM_CLI", "/root/.notebooklm-venv/bin/notebooklm")
SKIP_PROJECTS = {"Index", "README"}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        match = re.match(r"^([a-z_]+):\s*(.+)$", line)
        if match:
            fm[match.group(1)] = match.group(2).strip().strip('"')
    return fm


ARCHIVED_KEYWORDS = ("archived", "deprecated", "abandoned", "closed", "obsolete")


def is_active_project(project_path: Path) -> bool:
    """Active = status NOT obviously archived. Accepts: emoji 🟢🟡, 'active', 'production', 'done-with-backlog', etc."""
    text = project_path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    status = fm.get("status", "").lower()
    if not status:
        return False
    return not any(kw in status for kw in ARCHIVED_KEYWORDS)


def get_notebook_id(project_path: Path) -> str | None:
    text = project_path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    return fm.get("notebooklm") or fm.get("notebook_id")


def create_notebook(title: str) -> str | None:
    """Create a new NotebookLM notebook, parse ID from CLI output.

    AVOIDS --json bug (gotchas #1) — parses ID via regex from stdout.
    """
    try:
        result = subprocess.run(
            [NOTEBOOKLM, "create", title],
            capture_output=True, text=True, timeout=60,
        )
        # Parse: "Created notebook: <UUID>" or "Notebook ID: <UUID>"
        # Robust pattern: UUID v4-format match
        uuid_pat = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        m = uuid_pat.search(result.stdout) or uuid_pat.search(result.stderr)
        if m:
            return m.group(0)
        print(f"  ⚠ Could not parse NB ID from output: {result.stdout[:200]}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print(f"  ⚠ notebooklm create timeout for '{title}'", file=sys.stderr)
        return None


def write_back_nb_id(project_path: Path, nb_id: str) -> bool:
    """Add `notebooklm: <ID>` to frontmatter if absent."""
    text = project_path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return False
    fm = fm_match.group(1)
    if re.search(r"^notebooklm:", fm, re.MULTILINE):
        return False  # already there
    new_fm = fm + f"\nnotebooklm: {nb_id}"
    new_text = f"---\n{new_fm}\n---" + text[fm_match.end():]
    backup = project_path.with_suffix(project_path.suffix + ".bak.20260513-nb")
    if not backup.exists():
        backup.write_text(text, encoding="utf-8")
    project_path.write_text(new_text, encoding="utf-8")
    return True


def find_project_sources(slug: str) -> list[Path]:
    """Gather files to sync into a project's NotebookLM."""
    sources = []
    # Project file itself
    pf = PROJECTS_DIR / f"{slug}.md"
    if pf.exists():
        sources.append(pf)
    # ADRs mentioning the slug (substring match)
    if DECISIONS_DIR.exists():
        for d in DECISIONS_DIR.glob("*.md"):
            if slug in d.read_text(encoding="utf-8", errors="replace")[:5000]:
                sources.append(d)
    # Memory files mentioning slug
    if MEMORY_DIR.exists():
        for m in MEMORY_DIR.rglob("*.md"):
            if slug in m.name or slug in m.read_text(encoding="utf-8", errors="replace")[:2000]:
                sources.append(m)
    return sources


def list_notebook_sources(nb_id: str) -> set[str]:
    """List source titles already in the notebook."""
    try:
        result = subprocess.run(
            [NOTEBOOKLM, "-n", nb_id, "source", "list"],
            capture_output=True, text=True, timeout=30,
        )
        # Parse table output — extract source titles (first column after header)
        titles = set()
        for line in result.stdout.split("\n"):
            # Each row's title is column-aligned; we use loose match
            if line.strip() and not line.startswith("┃") and "─" not in line and "ID" not in line[:5]:
                # Skip headers / separators
                parts = re.split(r"\s{2,}", line.strip())
                if parts:
                    titles.add(parts[-1].strip())
        return titles
    except subprocess.TimeoutExpired:
        return set()


def add_source_to_notebook(nb_id: str, source_path: Path, dry_run: bool = False) -> bool:
    if dry_run:
        return False
    try:
        result = subprocess.run(
            [NOTEBOOKLM, "-n", nb_id, "source", "add", str(source_path)],
            capture_output=True, text=True, timeout=120,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def process_project(p: Path, commit: bool) -> dict:
    slug = p.stem
    if not is_active_project(p):
        return {"slug": slug, "status": "skip_archived"}

    title = slug.replace("-", " ").title()
    nb_id = get_notebook_id(p)
    sources = find_project_sources(slug)

    result = {
        "slug": slug,
        "nb_id_existing": nb_id,
        "sources_in_vault": len(sources),
    }

    if not nb_id:
        if commit:
            new_id = create_notebook(title)
            if new_id:
                write_back_nb_id(p, new_id)
                result["nb_id_created"] = new_id
                nb_id = new_id
            else:
                result["status"] = "create_failed"
                return result
        else:
            result["status"] = "would_create"
            return result

    if not nb_id:
        return result

    # Compare existing sources
    existing_titles = list_notebook_sources(nb_id) if commit else set()
    to_add = []
    for src in sources:
        # Match by filename (NotebookLM usually shows source-title = filename)
        if src.name not in existing_titles:
            to_add.append(src)

    result["sources_to_add"] = len(to_add)
    if commit and to_add:
        added = 0
        for src in to_add:
            if add_source_to_notebook(nb_id, src, dry_run=False):
                added += 1
        result["sources_added"] = added

    result["status"] = "synced" if commit else "audited"
    return result


def main():
    ap = argparse.ArgumentParser(description="Vault NB sync (B-5)")
    ap.add_argument("--project", help="Single project slug")
    ap.add_argument("--commit", action="store_true", help="Actually create/sync (default: audit)")
    ap.add_argument("--cron", action="store_true", help="Silent unless changes")
    args = ap.parse_args()

    projects = []
    if args.project:
        p = PROJECTS_DIR / f"{args.project}.md"
        if p.exists():
            projects.append(p)
    else:
        projects = sorted(p for p in PROJECTS_DIR.glob("*.md") if p.stem not in SKIP_PROJECTS)

    audit_results = []
    for p in projects:
        result = process_project(p, args.commit)
        audit_results.append(result)

    if args.cron:
        # Silent unless any action would happen / has happened
        active = [r for r in audit_results if r.get("status") in ("would_create", "audited") and r.get("sources_to_add", 0) > 0]
        if active:
            for r in active:
                print(f"  {r['slug']}: would_add={r['sources_to_add']}")
    else:
        mode = "COMMIT" if args.commit else "AUDIT (use --commit to apply)"
        print(f"[{mode}] {len(audit_results)} projects")
        print(f"{'STATUS':18} {'SLUG':35} {'NB':12} {'SOURCES':10}")
        for r in audit_results:
            nb_short = (r.get("nb_id_existing") or r.get("nb_id_created") or "-")[:8]
            status = r.get("status", "?")
            to_add = r.get("sources_to_add", 0)
            sources = r.get("sources_in_vault", 0)
            print(f"{status:18} {r['slug']:35} {nb_short:12} {sources}/{to_add}")


if __name__ == "__main__":
    main()

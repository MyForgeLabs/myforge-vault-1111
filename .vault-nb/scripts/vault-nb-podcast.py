#!/usr/bin/env python3
"""
vault-nb-podcast — heti commute-podcast cron (B-5 Réteg 3).

ADR: 07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch.md
Sprint: B-5, Réteg 3.

Minden hétfő reggel automatikus podcast-generálás minden aktív projektre.
Cron: 0 22 * * 0 (vasárnap 22:00, hétfő reggelre kész).

Status: SKELETON (Day 0). Real integration Week 1 (after vault-nb-sync live).

Usage:
    vault-nb-podcast --week                    # current week, all active projects
    vault-nb-podcast --project <slug>          # single project
    vault-nb-podcast --dry-run                 # preview
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
AUDIO_DIR = Path("/root/vault-audio/weekly")
PROJECTS_DIR = VAULT_ROOT / "02-Projects"
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
ACTIVE_DAYS = 7   # csak ha session-aktivitás az elmúlt 7 napban


def is_active_project(project_slug: str, days: int = ACTIVE_DAYS) -> bool:
    cutoff = datetime.utcnow() - timedelta(days=days)
    for s in SESSIONS_DIR.glob(f"*{project_slug}*.md"):
        if datetime.fromtimestamp(s.stat().st_mtime) >= cutoff:
            return True
    return False


def generate_podcast_stub(project_slug: str, nb_id: str, dry_run: bool = False) -> dict:
    """
    PLACEHOLDER podcast generation.

    Real impl (Week 1):
      prompt = "Heti összefoglaló: mi történt, mit tanultunk, mi a köv lépés."
      subprocess.run(['notebooklm', 'generate', 'audio', '-n', nb_id,
                      '--format', 'deep-dive', '--length', 'default', prompt])
      poll status, then:
      subprocess.run(['notebooklm', 'download', 'audio', '-n', nb_id,
                      '--out', AUDIO_DIR / f"{project_slug}-{week_iso}.mp3"])
    """
    week_iso = datetime.utcnow().strftime("%Y-W%V")
    return {
        "project": project_slug,
        "nb": nb_id,
        "out_path": str(AUDIO_DIR / f"{project_slug}-{week_iso}.mp3"),
        "stub": True,
    }


def main():
    ap = argparse.ArgumentParser(description="NB podcast generator (B-5 Réteg 3)")
    ap.add_argument("--week", action="store_true", help="All active projects, current week")
    ap.add_argument("--project", help="Single project slug")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not (args.week or args.project):
        ap.print_help()
        sys.exit(1)

    if not args.dry_run:
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    projects = []
    if args.project:
        projects.append(args.project)
    else:
        for p in PROJECTS_DIR.glob("*.md"):
            if p.stem == "Index":
                continue
            if is_active_project(p.stem):
                projects.append(p.stem)

    print(f"Active projects ({ACTIVE_DAYS}d window): {len(projects)}")

    for proj_slug in projects:
        # Real impl: extract nb_id from project frontmatter
        result = generate_podcast_stub(proj_slug, "stub-nb-id", args.dry_run)
        if args.dry_run or result["stub"]:
            print(f"  [stub] {proj_slug} → {result['out_path']}")

    print("  (skeleton — Week 1: notebooklm CLI integration; AirDrop-kompatibilis iCloud-sync)")


if __name__ == "__main__":
    main()

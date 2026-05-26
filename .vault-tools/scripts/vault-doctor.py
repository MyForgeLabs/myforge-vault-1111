#!/root/.notebooklm-venv/bin/python3
"""
vault-doctor — unified vault health-check in one command.

Aggregates state across the SV stack (KO-DB, Memgraph, MEMORY.md, file counts,
cron entries, recent git activity) into a single 🟢/🟡/🔴 dashboard.

Goal: under 5 seconds, no flaky calls. Tells you "what to fix first" when the
vault feels off.

Usage:
  vault-doctor              # default colored dashboard
  vault-doctor --json       # machine-readable
  vault-doctor --quiet      # exit-code-only mode (0 if all green)

Exit codes:
  0 = all green
  1 = at least one 🟡 (warning)
  2 = at least one 🔴 (critical)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path("/root/obsidian-vault")
KO_DB = VAULT / ".vault-ko" / "facts.db"
MEMORY_MD = Path("/root/.claude/projects/-root/memory/MEMORY.md")
MEMORY_LIMIT = 24960  # bytes; matches MEMORY.md overflow management wiki

GREEN, YELLOW, RED = "🟢", "🟡", "🔴"


def _short(s: str, n: int = 60) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _run(cmd: list[str], timeout: int = 5) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except Exception as e:
        return 127, str(e)


def check_memgraph() -> dict:
    """Memgraph up? entity count? edge count? typed-coverage?"""
    try:
        import mgclient
    except ImportError:
        return {"status": RED, "msg": "mgclient not installed"}
    try:
        conn = mgclient.connect(host="127.0.0.1", port=7687)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("MATCH (n:Entity) RETURN count(n)")
        total = cur.fetchone()[0]
        cur.execute(
            "MATCH (n:Entity) WHERE size(labels(n)) > 1 RETURN count(n)"
        )
        typed = cur.fetchone()[0]
        cur.execute("MATCH ()-[r]->() RETURN count(r)")
        edges = cur.fetchone()[0]
        pct = (typed / total * 100) if total else 0
        if total == 0:
            status, msg = RED, "0 entities (Memgraph empty)"
        elif pct < 10:
            status, msg = YELLOW, f"{typed}/{total} typed ({pct:.1f}%) — low"
        else:
            status, msg = GREEN, f"{typed}/{total} typed ({pct:.1f}%), {edges} edges"
        return {
            "status": status, "msg": msg,
            "total_entities": total, "typed_entities": typed,
            "typed_pct": round(pct, 1), "edges": edges,
        }
    except Exception as e:
        return {"status": RED, "msg": f"connect failed: {_short(str(e))}"}


def check_kodb() -> dict:
    """KO-DB readable? fact count? SCD2 active rows? last-update?"""
    if not KO_DB.exists():
        return {"status": RED, "msg": "facts.db missing"}
    try:
        conn = sqlite3.connect(KO_DB)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM facts")
        facts = cur.fetchone()[0]
        try:
            cur.execute("SELECT COUNT(*) FROM facts WHERE valid_to IS NULL")
            active = cur.fetchone()[0]
        except sqlite3.OperationalError:
            active = facts  # SCD2 not yet migrated
        try:
            cur.execute("SELECT COUNT(DISTINCT prov) FROM fact_provenance")
            provs = cur.fetchone()[0]
        except sqlite3.OperationalError:
            provs = 0
        size_mb = KO_DB.stat().st_size / (1024 * 1024)
        if facts == 0:
            status, msg = RED, "0 facts"
        elif facts < 1000:
            status, msg = YELLOW, f"{facts} facts (low)"
        else:
            status, msg = GREEN, f"{facts} facts / {active} active / {provs} provs / {size_mb:.1f}MB"
        return {
            "status": status, "msg": msg,
            "facts": facts, "active": active, "provs": provs,
            "size_mb": round(size_mb, 1),
        }
    except Exception as e:
        return {"status": RED, "msg": f"sqlite error: {_short(str(e))}"}


def check_memory_md() -> dict:
    """MEMORY.md size vs 24.4 KB limit."""
    if not MEMORY_MD.exists():
        return {"status": RED, "msg": "MEMORY.md missing"}
    size = MEMORY_MD.stat().st_size
    buffer = MEMORY_LIMIT - size
    if size > MEMORY_LIMIT:
        status, msg = RED, f"{size} byte (+{size - MEMORY_LIMIT} OVER limit)"
    elif buffer < 500:
        status, msg = YELLOW, f"{size} byte ({buffer} byte buffer — thin)"
    else:
        status, msg = GREEN, f"{size} byte ({buffer} byte buffer)"
    return {"status": status, "msg": msg, "size": size, "buffer": buffer}


def check_file_counts() -> dict:
    """Counts of wiki / audit / ADR / session / daily."""
    wiki = len(list((VAULT / "11-wiki").glob("*.md")))
    audit = len(list((VAULT / "06-Audits").glob("*.md")))
    adr = len(list((VAULT / "07-Decisions").glob("*.md")))
    sessions = len(list((VAULT / "08-Sessions").glob("*.md")))
    daily = len(list((VAULT / "01-Daily").glob("*.md")))
    return {
        "status": GREEN,
        "msg": f"wiki:{wiki} audit:{audit} adr:{adr} session:{sessions} daily:{daily}",
        "wiki": wiki, "audit": audit, "adr": adr,
        "sessions": sessions, "daily": daily,
    }


def check_vault_binaries() -> dict:
    """Count of vault-* binaries on PATH."""
    bin_dir = Path("/usr/local/bin")
    bins = [
        f.name for f in bin_dir.iterdir()
        if f.name.startswith("vault-") and f.is_file()
    ]
    return {
        "status": GREEN,
        "msg": f"{len(bins)} on PATH (umbrella: `vault`)",
        "count": len(bins),
    }


def check_cron() -> dict:
    """Crontab line count + mutex coverage.

    A cron entry counts as protected if it uses either:
      - `vault-cron-flock` wrapper (the project convention), OR
      - direct `flock -n` / `flock -w N` (the system primitive)
    """
    rc, out = _run(["crontab", "-l"], timeout=3)
    if rc != 0:
        return {"status": YELLOW, "msg": "no crontab for current user"}
    lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("#")]
    protected = sum(
        1 for ln in lines
        if "vault-cron-flock" in ln or "flock -n" in ln or "flock -w" in ln
    )
    pct = (protected / len(lines) * 100) if lines else 0
    if protected == 0 and lines:
        status, msg = YELLOW, f"{len(lines)} entries, 0 mutex-protected"
    elif pct >= 90:
        status, msg = GREEN, f"{len(lines)} entries, {protected} mutex-protected ({pct:.0f}%)"
    elif pct >= 75:
        status, msg = YELLOW, f"{len(lines)} entries, {protected} mutex-protected ({pct:.0f}%) — push >90%"
    else:
        status, msg = YELLOW, f"{len(lines)} entries, only {protected} mutex-protected ({pct:.0f}%)"
    return {
        "status": status, "msg": msg,
        "entries": len(lines), "protected": protected, "pct_protected": round(pct, 0),
    }


def check_git() -> dict:
    """Days since last commit + uncommitted-file count."""
    os.chdir(VAULT)
    rc1, last_commit = _run(["git", "log", "-1", "--format=%ct"], timeout=3)
    rc2, status_out = _run(["git", "status", "--porcelain"], timeout=3)
    if rc1 != 0 or rc2 != 0:
        return {"status": RED, "msg": "not a git repo or git error"}
    age_min = (time.time() - int(last_commit.strip())) / 60
    uncommitted = len([ln for ln in status_out.splitlines() if ln.strip()])
    if age_min < 60:
        age_str = f"{age_min:.0f}m"
    elif age_min < 1440:
        age_str = f"{age_min/60:.1f}h"
    else:
        age_str = f"{age_min/1440:.1f}d"
    if age_min > 24 * 60:
        status = YELLOW
    else:
        status = GREEN
    if uncommitted > 50:
        status = YELLOW
    return {
        "status": status,
        "msg": f"last commit {age_str} ago, {uncommitted} uncommitted",
        "age_min": round(age_min, 1), "uncommitted": uncommitted,
    }


def check_disk() -> dict:
    """Disk usage % of vault host."""
    total, used, free = shutil.disk_usage("/")
    pct = used / total * 100
    if pct > 90:
        status, msg = RED, f"{pct:.0f}% used ({free/1024**3:.1f}GB free)"
    elif pct > 80:
        status, msg = YELLOW, f"{pct:.0f}% used ({free/1024**3:.1f}GB free)"
    else:
        status, msg = GREEN, f"{pct:.0f}% used ({free/1024**3:.1f}GB free)"
    return {"status": status, "msg": msg, "pct": round(pct, 0)}


CHECKS = [
    ("Memgraph", check_memgraph),
    ("KO-DB", check_kodb),
    ("MEMORY.md", check_memory_md),
    ("Files", check_file_counts),
    ("vault-* bins", check_vault_binaries),
    ("Cron", check_cron),
    ("Git", check_git),
    ("Disk", check_disk),
]


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-doctor")
    ap.add_argument("--json", action="store_true", help="machine-readable JSON output")
    ap.add_argument("--quiet", action="store_true", help="no output, exit-code only")
    ap.add_argument("--watch", type=int, nargs="?", const=10, metavar="SECS",
                    help="loop forever, refresh every N seconds (default 10)")
    args = ap.parse_args()

    if args.watch:
        try:
            while True:
                # ANSI clear-screen + home — no shell-out, no injection surface.
                sys.stdout.write("\033[2J\033[H")
                sys.stdout.flush()
                _run_once(args)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            return 0

    return _run_once(args)


def _run_once(args) -> int:
    results = {}
    t0 = time.time()
    for name, fn in CHECKS:
        try:
            results[name] = fn()
        except Exception as e:
            results[name] = {"status": RED, "msg": f"check crashed: {_short(str(e))}"}
    elapsed = time.time() - t0

    worst = GREEN
    for r in results.values():
        if r["status"] == RED:
            worst = RED
            break
        if r["status"] == YELLOW:
            worst = YELLOW

    if args.json:
        print(json.dumps({
            "worst": worst, "elapsed_sec": round(elapsed, 2),
            "checks": results,
        }, indent=2, ensure_ascii=False))
    elif not args.quiet:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(f"vault-doctor — {ts} — {elapsed:.1f}s")
        print()
        for name, _ in CHECKS:
            r = results[name]
            print(f"  {r['status']} {name:<14} {r['msg']}")
        print()
        if worst == GREEN:
            print(f"  {GREEN} all systems healthy")
        elif worst == YELLOW:
            print(f"  {YELLOW} 1+ warning — check above")
        else:
            print(f"  {RED} 1+ critical — fix immediately")

    return {GREEN: 0, YELLOW: 1, RED: 2}[worst]


if __name__ == "__main__":
    sys.exit(main())

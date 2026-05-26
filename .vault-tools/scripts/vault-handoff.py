#!/root/.notebooklm-venv/bin/python3
"""
vault-handoff — Cross-CLI handoff bundle for Claude ↔ Codex ↔ Gemini.

The vault already shares AGENTS.md (symlinked across all three CLIs) and the
11.11 session protocol works in any CLI. What's missing is a way to take a
working session-context from one CLI and resume it cleanly in another.

This CLI builds a self-contained "handoff bundle" — a markdown or JSON file
that the receiving CLI can read to reconstruct enough state to continue:

  - Session pointer  (which session-file, which project, which agent started it)
  - Core-memory snapshot (if vault-core-memory is initialized)
  - Top open tasks for the project (from 04-Tasks/Backlog.md tagged #project/<slug>)
  - Recent decisions (last 3 ADRs touching the project)
  - KO-DB top-K facts for the project subject
  - Last 3 notes from the session ## Events log

Subcommands
-----------

    vault-handoff export [--session SLUG] [--format json|markdown]
        Build a handoff bundle for the FOCUSED session (or named session).

    vault-handoff import <bundle-file>
        Print the bundle in a way the receiving agent can paste-into-context.
        Does NOT mutate the session file by default.

    vault-handoff list
        Show all open sessions with their CLI affinity (claude / codex / gemini).

Cross-CLI handoff workflow:

    # On the originating CLI (e.g. Claude):
    AGENT=claude vault-handoff export --format markdown > /tmp/handoff.md

    # Move /tmp/handoff.md to the receiving CLI's machine (or just open it).
    # On the receiving CLI (e.g. Codex):
    AGENT=codex vault-handoff import /tmp/handoff.md
    # → prints the bundle; agent pastes into its context and continues.

Status: Day 0 (2026-05-25) — skeleton; receive-side `import` is a printer,
not a state-mutator. Mutating receive flow is W1+ scope.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
DECISIONS_DIR = VAULT_ROOT / "07-Decisions"
TASKS_FILE = VAULT_ROOT / "04-Tasks" / "Backlog.md"
CORE_MEMORY_FILE = VAULT_ROOT / "00-Meta" / "core-memory.yaml"


def _detect_chat_id() -> str | None:
    """Mirror the resolution chain used by the 11.11* shell scripts."""
    for env_var in (
        "CLAUDE_CODE_SESSION_ID",
        "CODEX_COMPANION_SESSION_ID",
        "CODEX_SESSION_ID",
        "GEMINI_SESSION_ID",
    ):
        v = os.environ.get(env_var)
        if v:
            return v
    # Fallback: vault-detect-chat-id helper (Codex standalone path)
    try:
        proc = subprocess.run(
            ["vault-detect-chat-id"], capture_output=True, text=True, timeout=3,
        )
        v = proc.stdout.strip()
        if v:
            return v
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _read_active_session(chat_id: str | None) -> tuple[Path | None, str | None]:
    """Resolve focused session file. Returns (session_path, slug)."""
    pointer_path = None
    if chat_id:
        cand = VAULT_ROOT / f".active-session-{chat_id}"
        if cand.exists():
            pointer_path = cand
    if pointer_path is None:
        legacy = VAULT_ROOT / ".active-session"
        if legacy.exists():
            pointer_path = legacy
    if pointer_path is None:
        return None, None
    raw = pointer_path.read_text(encoding="utf-8").strip()
    if not raw:
        return None, None
    # Pointer may be an absolute path OR a bare slug; handle both.
    p = Path(raw)
    if p.is_absolute() and p.exists():
        return p, p.stem
    slug = raw
    candidate = SESSIONS_DIR / f"{slug}.md"
    if candidate.exists():
        return candidate, slug
    matches = sorted(SESSIONS_DIR.glob(f"*{slug}*.md"))
    if matches:
        return matches[-1], matches[-1].stem
    return None, slug


def _resolve_session_by_slug(slug: str) -> Path | None:
    """Find a session file by exact name or substring."""
    exact = SESSIONS_DIR / f"{slug}.md"
    if exact.exists():
        return exact
    matches = sorted(SESSIONS_DIR.glob(f"*{slug}*.md"))
    return matches[-1] if matches else None


def _parse_session_frontmatter(path: Path) -> dict:
    """Pull `name`, `project`, `agent`, `started` from a session file."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def _extract_recent_notes(path: Path, n: int = 3) -> list[str]:
    """Pull the last N timestamped notes from the session's ## Events section."""
    text = path.read_text(encoding="utf-8")
    parts = text.split("## Events", 1)
    if len(parts) < 2:
        return []
    rest = parts[1].split("##", 1)[0]
    notes = []
    for line in rest.splitlines():
        if re.match(r"^- \d{2}:\d{2} —", line):
            notes.append(line.strip())
    return notes[-n:]


def _project_open_tasks(project_slug: str, n: int = 5) -> list[str]:
    """Pick top-N tasks from the 04-Tasks/Backlog.md tagged with #project/<slug>."""
    if not TASKS_FILE.exists():
        return []
    text = TASKS_FILE.read_text(encoding="utf-8")
    needle = f"#project/{project_slug}"
    out = []
    for line in text.splitlines():
        if needle in line and "- [ ]" in line:
            out.append(line.strip())
            if len(out) >= n:
                break
    return out


def _recent_project_decisions(project_slug: str, n: int = 3) -> list[Path]:
    """Pick last-N ADR files mentioning the project slug (or tagged with it)."""
    if not DECISIONS_DIR.exists():
        return []
    matches = []
    for adr in sorted(DECISIONS_DIR.glob("*.md"), reverse=True):
        if adr.name == "Index.md":
            continue
        try:
            txt = adr.read_text(encoding="utf-8")
        except Exception:
            continue
        if project_slug.lower() in txt.lower():
            matches.append(adr)
            if len(matches) >= n:
                break
    return matches


def _ko_db_top_facts(project_slug: str, n: int = 5) -> list[dict]:
    """Run vault-ko-query for project facts. Best-effort, JSON-only."""
    try:
        proc = subprocess.run(
            ["vault-ko-query", project_slug, "--json", "--top-k", str(n)],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        data = json.loads(proc.stdout)
        if isinstance(data, dict):
            return data.get("results", [])[:n]
        if isinstance(data, list):
            return data[:n]
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return []


def _core_memory_snapshot() -> str:
    """Run `vault-core-memory show` if available; else read the YAML file."""
    try:
        proc = subprocess.run(
            ["vault-core-memory", "show"],
            capture_output=True, text=True, timeout=5,
        )
        if proc.returncode == 0:
            return proc.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    if CORE_MEMORY_FILE.exists():
        return CORE_MEMORY_FILE.read_text(encoding="utf-8")
    return ""


def build_bundle(session_path: Path) -> dict:
    """Assemble the handoff bundle dict."""
    fm = _parse_session_frontmatter(session_path)
    project = fm.get("project", "unknown")
    notes = _extract_recent_notes(session_path, n=5)
    tasks = _project_open_tasks(project, n=5)
    adrs = _recent_project_decisions(project, n=3)
    ko_facts = _ko_db_top_facts(project, n=5)
    return {
        "schema_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "exported_by": os.environ.get("AGENT", "unknown"),
        "session": {
            "slug": session_path.stem,
            "path": str(session_path.relative_to(VAULT_ROOT)),
            "project": project,
            "started": fm.get("started"),
            "agent_origin": fm.get("agent"),
            "status": fm.get("status"),
        },
        "core_memory": _core_memory_snapshot(),
        "recent_notes": notes,
        "open_tasks": tasks,
        "recent_decisions": [
            {"path": str(a.relative_to(VAULT_ROOT)), "name": a.stem}
            for a in adrs
        ],
        "ko_db_top_facts": ko_facts,
    }


def render_markdown(bundle: dict) -> str:
    sess = bundle["session"]
    lines = [
        "# vault-handoff bundle",
        "",
        f"> Exported {bundle['exported_at']} by `AGENT={bundle['exported_by']}`. "
        f"Schema v{bundle['schema_version']}. Paste this block into the receiving "
        f"agent's context; it self-describes the session to resume.",
        "",
        "## Session",
        "",
        f"- **Slug:** `{sess['slug']}`",
        f"- **File:** [[{sess['path'].removesuffix('.md')}]]",
        f"- **Project:** `{sess['project']}`",
        f"- **Started:** {sess.get('started') or '?'}",
        f"- **Origin agent:** {sess.get('agent_origin') or '?'}",
        f"- **Status:** {sess.get('status') or '?'}",
        "",
        "## Core memory (always-loaded)",
        "",
        "```yaml",
        bundle["core_memory"].rstrip() or "(none)",
        "```",
        "",
    ]
    if bundle["recent_notes"]:
        lines += ["## Last 5 session events", ""] + bundle["recent_notes"] + [""]
    if bundle["open_tasks"]:
        lines += [
            f"## Open tasks for `{sess['project']}` (top 5)", "",
        ] + bundle["open_tasks"] + [""]
    if bundle["recent_decisions"]:
        lines += [f"## Recent decisions for `{sess['project']}`", ""]
        for d in bundle["recent_decisions"]:
            lines.append(f"- [[{d['path'].removesuffix('.md')}]]")
        lines.append("")
    if bundle["ko_db_top_facts"]:
        lines += [
            f"## KO-DB top facts for `{sess['project']}`", "",
            "| Subject | Predicate | Object | Source |",
            "|---|---|---|---|",
        ]
        for f in bundle["ko_db_top_facts"]:
            s = str(f.get("subject", ""))[:50]
            p = str(f.get("predicate", ""))[:25]
            o = str(f.get("object", ""))[:60]
            prov = str(f.get("provenance", ""))[:40]
            lines.append(f"| {s} | {p} | {o} | {prov} |")
        lines.append("")
    lines += [
        "## Continue here",
        "",
        f"1. Review the session file: `{sess['path']}`",
        "2. The 6-block core memory above is the always-loaded baseline.",
        "3. For deeper context, page-in archival: `vault-core-memory page-in \"<topic>\"`.",
        "4. To re-focus the session locally: `11.11focus " + sess['slug'] + "`.",
        "5. Continue with `11.11note \"...\"` for events, `11.11stop` to close.",
        "",
    ]
    return "\n".join(lines)


def cmd_export(args: argparse.Namespace) -> int:
    if args.session:
        sp = _resolve_session_by_slug(args.session)
        slug = args.session
    else:
        chat_id = _detect_chat_id()
        sp, slug = _read_active_session(chat_id)
    if sp is None:
        print(f"✗ Could not resolve session "
              f"({'slug='+args.session if args.session else 'focused'})",
              file=sys.stderr)
        return 1
    bundle = build_bundle(sp)
    if args.format == "json":
        print(json.dumps(bundle, ensure_ascii=False, indent=2, default=str))
    else:
        print(render_markdown(bundle))
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Parse a handoff bundle and print it for the receiving agent."""
    path = Path(args.bundle)
    if not path.exists():
        print(f"✗ Bundle not found: {path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    # Try JSON first; fall back to passing markdown through verbatim
    try:
        bundle = json.loads(text)
        print(render_markdown(bundle))
        return 0
    except json.JSONDecodeError:
        # Markdown bundle — already in the right shape for paste
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all open sessions with CLI affinity."""
    open_sessions = []
    for p in sorted(SESSIONS_DIR.glob("*.md")):
        fm = _parse_session_frontmatter(p)
        if fm.get("status") == "open":
            open_sessions.append({
                "slug": p.stem,
                "project": fm.get("project", "?"),
                "agent": fm.get("agent", "?"),
                "started": fm.get("started", "?"),
            })
    chat_id = _detect_chat_id()
    focused, focused_slug = _read_active_session(chat_id)
    if args.format == "json":
        print(json.dumps({
            "current_chat_id": chat_id,
            "focused_slug": focused_slug,
            "focused_path": str(focused) if focused else None,
            "open_sessions": open_sessions,
        }, indent=2, ensure_ascii=False))
        return 0
    print(f"Current chat-id: {chat_id or '(unknown)'}")
    if focused_slug:
        # Strip any directory component for display
        display = Path(focused_slug).stem if "/" in focused_slug else focused_slug
        print(f"Focused: {display}")
    else:
        print("Focused: (none)")
    print(f"\n{len(open_sessions)} open session(s):")
    for s in open_sessions:
        focus_marker = " ⭐" if s["slug"] == focused_slug else ""
        print(f"  [{s['agent']:7s}] {s['slug']:50s} project={s['project']}{focus_marker}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-handoff",
        description="Cross-CLI handoff bundle for Claude/Codex/Gemini.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="Build a handoff bundle.")
    p_exp.add_argument("--session", help="session slug (default: focused)")
    p_exp.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p_exp.set_defaults(func=cmd_export)

    p_imp = sub.add_parser("import", help="Print a handoff bundle for paste.")
    p_imp.add_argument("bundle", help="path to bundle file (JSON or markdown)")
    p_imp.set_defaults(func=cmd_import)

    p_ls = sub.add_parser("list", help="List open sessions with CLI affinity.")
    p_ls.add_argument("--format", choices=["text", "json"], default="text")
    p_ls.set_defaults(func=cmd_list)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/root/.notebooklm-venv/bin/python3
"""
vault-context-load — MemGPT virtual context-load egy projekt-slug-ra.

ADR: 07-Decisions/2026-05-12 sv-1 memory architecture arch.md
Sprint: B-2 Week 3 Day 1-2 (load-session-context skill rewrite).

Lean ~5K token replacement for the deprecated aggressive 15-20K cat-pattern.
Returns: working + top-K episodic + project-meta as JSON for the agent context-window.

Usage:
    vault-context-load <slug>                    # JSON output for slug
    vault-context-load <slug> --top-k 5          # custom episodic K
    vault-context-load <slug> --markdown         # rendered Pre-loaded markdown
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
PROJECTS_DIR = VAULT_ROOT / "02-Projects"
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
BACKLOG = VAULT_ROOT / "04-Tasks" / "Backlog.md"
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")


def get_focused_session() -> Path | None:
    """Read .active-session pointer."""
    active = VAULT_ROOT / ".active-session"
    if not active.exists():
        return None
    p = Path(active.read_text().strip())
    return p if p.exists() else None


def get_working(slug: str) -> dict:
    """Working memory: focused session + project file 1-line status."""
    focused = get_focused_session()
    working = {"focused_session": None, "project_status": None}

    if focused:
        text = focused.read_text(encoding="utf-8", errors="replace")
        working["focused_session"] = {
            "file": str(focused.relative_to(VAULT_ROOT)),
            "name": _frontmatter_field(text, "name"),
            "first_120_lines": "\n".join(text.splitlines()[:120]),
        }

    proj_file = PROJECTS_DIR / f"{slug}.md"
    if proj_file.exists():
        ptext = proj_file.read_text(encoding="utf-8")
        status = _frontmatter_field(ptext, "status")
        working["project_status"] = {"file": f"02-Projects/{slug}.md", "status": status}

    return working


def get_episodic_top_k(slug: str, top_k: int = 3) -> list[dict]:
    """Episodic memory: semantic top-K from Memgraph (vault-search) using slug as query."""
    try:
        from sentence_transformers import SentenceTransformer
        import mgclient

        model = SentenceTransformer(EMBED_MODEL, device="cpu")
        q_vec = model.encode([slug], normalize_embeddings=True)[0].tolist()

        conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
        cursor = conn.cursor()
        cursor.execute(
            "MATCH (c:Chunk) WHERE c.namespace = 'content' RETURN c.file, c.chunk_idx, c.title, c.text, c.vector"
        )
        rows = cursor.fetchall()
        conn.close()

        scored = []
        for file, idx, title, text, vec in rows:
            if vec is None:
                continue
            score = sum(x * y for x, y in zip(q_vec, vec))
            scored.append({"file": file, "chunk_idx": idx, "title": title, "snippet": text[:200], "score": round(score, 3)})
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:top_k]
    except Exception as e:
        return [{"error": f"vault-search unavailable: {e}"}]


def get_project_tasks(slug: str, limit: int = 3) -> list[str]:
    """Top-N open tasks from Backlog for the project."""
    if not BACKLOG.exists():
        return []
    text = BACKLOG.read_text(encoding="utf-8", errors="replace")
    # Match open tasks tagged #project/<slug>
    pattern = rf"^- \[ \] (.+?#project/{re.escape(slug)}.*?)$"
    matches = re.findall(pattern, text, re.MULTILINE)
    return [m[:120] for m in matches[:limit]]


def _frontmatter_field(text: str, field: str) -> str | None:
    """Extract single-line YAML frontmatter field."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm_match = re.search(rf"^{field}:\s*(.+)$", m.group(1), re.MULTILINE)
    return fm_match.group(1).strip() if fm_match else None


def render_markdown(slug: str, ctx: dict) -> str:
    """Render context as Pre-loaded markdown section."""
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    lines = [
        "## Pre-loaded context",
        "",
        f"> Auto-load {now}Z — MemGPT virtual (lean ~5K token).",
        "",
    ]

    if ctx["working"].get("project_status"):
        ps = ctx["working"]["project_status"]
        lines.append(f"**Projekt:** [[02-Projects/{slug}]] — {ps['status']}")
        lines.append("")

    eps = ctx.get("episodic_top_k", [])
    if eps and "error" not in eps[0]:
        lines.append("**Top-3 releváns episodic-emlék** (semantic-fetch):")
        for r in eps:
            lines.append(f"- [{r['score']}] [[{r['file']}]] — {r['title']}")
        lines.append("")

    tasks = ctx.get("project_tasks", [])
    if tasks:
        lines.append(f"**Top-3 aktív task** (#project/{slug}):")
        for t in tasks:
            lines.append(f"- [ ] {t}")
        lines.append("")

    lines.extend([
        "**Semantic on-demand:** mélyebb infó-hoz `vault-search \"<query>\" --top-k 5`.",
        "",
        "> Ready.",
    ])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="MemGPT virtual context-load (B-2 Week 3)")
    ap.add_argument("slug", help="Project slug (e.g. kgc-berles, foxxi)")
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--markdown", action="store_true", help="Render Pre-loaded section")
    args = ap.parse_args()

    ctx = {
        "slug": args.slug,
        "working": get_working(args.slug),
        "episodic_top_k": get_episodic_top_k(args.slug, args.top_k),
        "project_tasks": get_project_tasks(args.slug),
    }

    if args.markdown:
        print(render_markdown(args.slug, ctx))
    else:
        print(json.dumps(ctx, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

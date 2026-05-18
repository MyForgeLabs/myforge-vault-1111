#!/root/.notebooklm-venv/bin/python3
"""
vault-graph-mentions-extract — deterministic Wikilink importer (SV B-7 Week 2).

Walks every Markdown file in the Obsidian vault and writes one
``(:SourceFile)-[:MENTIONS]->(:WikiLink)`` edge per ``[[wikilink]]`` occurrence.

Zero-LLM, O(seconds). Serves as ground-truth for evaluating the
LLM-extracted entity graph produced by ``vault-graph-extract``.

Conventions
-----------
- ``SourceFile.name``  — vault-relative path of the .md file, e.g.
  ``02-Projects/superintelligent-vault.md``.
- ``WikiLink.name``    — normalized link target:
    * strip ``#section-anchor``
    * strip ``|alias``
    * strip trailing ``.md``
    * preserve folder-prefix when present (``02-Projects/foo``)
  So ``[[02-Projects/foo#Bar|baz]]`` → ``02-Projects/foo``.
- ``MENTIONS``         — properties: ``count`` (incremented per re-run if a
  file changes; idempotent on the (src, tgt) pair).

Excluded paths
--------------
- ``AGENTS.md`` and everything under ``00-Meta/`` (per task spec)
- dotfiles / hidden dirs (``.git``, ``.obsidian``, ``.vault-*``)
- backup files (``*.bak*``)

Memgraph CE 3.9 quirk
---------------------
Uses *autocommit* mode by issuing a fresh ``cursor()`` per statement
and committing after every batch. The :Entity/:Literal label space
from Week 1-α is left untouched — we add :SourceFile and :WikiLink
as new top-level labels.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import mgclient
from tqdm import tqdm

# ─── CONFIG ───────────────────────────────────────────────────────────────

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
BATCH_SIZE = 500

# Folders we scan (top-level only — keeps things explicit and safe).
SCAN_DIRS = (
    "01-Daily", "02-Projects", "03-Hosts", "04-Tasks", "05-Memory",
    "06-Audits", "07-Decisions", "08-Sessions", "10-raw", "11-wiki",
    "content",
)

# Folders we explicitly skip (per task spec + safety).
EXCLUDE_DIRS = {"00-Meta"}
EXCLUDE_FILES = {"AGENTS.md"}

# Regex: [[target]], [[target|alias]], [[target#anchor]], [[target#anchor|alias]]
# Group 1 = full link body (target + optional #anchor + optional |alias)
# Group 2 = target only (everything up to the first # or | or ])
WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")

# Allow ``a/b/c`` style relative paths but reject control chars / newlines.
TARGET_CLEAN_RE = re.compile(r"^[\s]*(.*?)[\s]*$")


def normalize_target(raw: str) -> str | None:
    """``02-Projects/foo#Bar|baz`` → ``02-Projects/foo``.

    Returns None for empty / nonsense targets.
    """
    # Strip alias (everything after first '|')
    body = raw.split("|", 1)[0]
    # Strip section anchor (everything after first '#')
    body = body.split("#", 1)[0]
    body = body.strip()
    if not body:
        return None
    # Strip trailing .md (canonicalize Obsidian's optional extension)
    if body.lower().endswith(".md"):
        body = body[:-3]
    # Strip leading './' or '/'
    body = body.lstrip("./")
    # Trailing slash → directory link like '[[10-raw/]]' → '10-raw'
    body = body.rstrip("/")
    if not body:
        return None
    # Sanity: drop obvious garbage (newlines / nul)
    if "\n" in body or "\x00" in body:
        return None
    return body


def is_excluded(rel_path: Path) -> bool:
    parts = rel_path.parts
    if not parts:
        return True
    if parts[0] in EXCLUDE_DIRS:
        return True
    if rel_path.name in EXCLUDE_FILES:
        return True
    # Skip backups
    if ".bak" in rel_path.name:
        return True
    # Skip hidden anywhere in path
    for p in parts:
        if p.startswith("."):
            return True
    return False


def walk_vault(root: Path):
    """Yield (rel_path, abs_path) for every scannable .md file."""
    for sub in SCAN_DIRS:
        base = root / sub
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            try:
                # Skip broken symlinks gracefully
                if not path.is_file():
                    continue
            except OSError:
                continue
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            if is_excluded(rel):
                continue
            yield rel, path


def extract_mentions(abs_path: Path) -> list[str]:
    """Return list of normalized link-targets found in the file."""
    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[warn] cannot read {abs_path}: {e}", file=sys.stderr)
        return []
    out: list[str] = []
    for m in WIKILINK_RE.finditer(text):
        raw = m.group(1)
        tgt = normalize_target(raw)
        if tgt:
            out.append(tgt)
    return out


# ─── MEMGRAPH I/O ─────────────────────────────────────────────────────────

def connect_mg():
    conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    return conn


def ensure_indexes(conn) -> None:
    """Idempotent index creation for :SourceFile(name) and :WikiLink(name)."""
    cur = conn.cursor()
    for stmt in (
        "CREATE INDEX ON :SourceFile(name);",
        "CREATE INDEX ON :WikiLink(name);",
    ):
        try:
            cur.execute(stmt)
            conn.commit()
        except mgclient.DatabaseError as exc:
            # Already exists — fine
            print(f"[index] skipped: {stmt[:50]}... ({exc})", file=sys.stderr)


def reset_mentions(conn) -> None:
    """Delete prior :SourceFile / :WikiLink graph for a clean re-import.

    Only deletes nodes whose *primary* label is one of these two — does
    NOT touch the B-7 Week 1-α :Entity / :Literal universe.
    """
    cur = conn.cursor()
    print("[reset] deleting :SourceFile and :WikiLink nodes (DETACH)...",
          file=sys.stderr)
    cur.execute(
        "MATCH (n) WHERE n:SourceFile OR n:WikiLink DETACH DELETE n;"
    )
    conn.commit()


def upsert_batch(conn, edges: list[tuple[str, str]]) -> None:
    """edges: list of (src_path, tgt_link). Idempotent MERGE per pair.

    A second run with the same (src,tgt) yields the same single edge —
    we MERGE on both the nodes and the edge.
    """
    cur = conn.cursor()
    pbar = tqdm(total=len(edges), desc="mentions", unit="edge")
    for i, (src, tgt) in enumerate(edges, 1):
        cypher = (
            "MERGE (s:SourceFile {name: $src}) "
            "MERGE (t:WikiLink {name: $tgt}) "
            "MERGE (s)-[r:MENTIONS]->(t) "
            "ON CREATE SET r.count = 1 "
            "ON MATCH SET r.count = coalesce(r.count, 1)"
        )
        try:
            cur.execute(cypher, {"src": src, "tgt": tgt})
        except mgclient.DatabaseError as exc:
            print(f"[warn] write fail {src} -> {tgt}: {exc}", file=sys.stderr)
        if i % BATCH_SIZE == 0:
            conn.commit()
        pbar.update(1)
    conn.commit()
    pbar.close()


# ─── MAIN ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dry-run", action="store_true",
                    help="scan + classify only; no Memgraph writes")
    ap.add_argument("--reset", action="store_true",
                    help="wipe existing :SourceFile/:WikiLink first")
    ap.add_argument("--top", type=int, default=10,
                    help="how many top-linked targets to print (default 10)")
    args = ap.parse_args()

    print(f"[scan] vault root: {VAULT_ROOT}", file=sys.stderr)

    # Per-source-type bookkeeping
    edges: list[tuple[str, str]] = []
    per_type_files: Counter = Counter()
    per_type_edges: Counter = Counter()
    target_count: Counter = Counter()
    broken_targets = 0
    file_count = 0

    files = list(walk_vault(VAULT_ROOT))
    print(f"[scan] candidate .md files: {len(files):,}", file=sys.stderr)

    for rel, abs_path in tqdm(files, desc="parse", unit="file"):
        file_count += 1
        src_name = rel.as_posix()
        top_dir = rel.parts[0] if rel.parts else "(root)"
        per_type_files[top_dir] += 1
        mentions = extract_mentions(abs_path)
        for tgt in mentions:
            edges.append((src_name, tgt))
            per_type_edges[top_dir] += 1
            target_count[tgt] += 1

    # Also flag links pointing to non-existent vault files (broken-link audit).
    for tgt in target_count:
        candidate = VAULT_ROOT / (tgt + ".md")
        if not candidate.exists():
            # Could still be a directory link or external — only count *.md
            # candidates with explicit folder prefix.
            if "/" in tgt:
                broken_targets += 1

    unique_targets = len(target_count)

    print("\n=== Scan summary ===")
    print(f"  files scanned:           {file_count:,}")
    print(f"  total mentions:          {len(edges):,}")
    print(f"  unique wikilink targets: {unique_targets:,}")
    print(f"  broken targets (.md not found, folder-prefixed): {broken_targets:,}")

    print("\n=== Per-folder breakdown ===")
    print(f"  {'folder':<14} {'files':>6} {'edges':>8}")
    for d in SCAN_DIRS:
        if per_type_files.get(d, 0):
            print(f"  {d:<14} {per_type_files[d]:>6} {per_type_edges.get(d, 0):>8}")

    print("\n=== Top-{n} most-linked targets ===".format(n=args.top))
    for tgt, c in target_count.most_common(args.top):
        print(f"  {c:>5}  [[{tgt}]]")

    if args.dry_run:
        print("\n[dry-run] no Memgraph writes performed.")
        return

    conn = connect_mg()
    try:
        ensure_indexes(conn)
        if args.reset:
            reset_mentions(conn)
        upsert_batch(conn, edges)

        # Confirmation read-back
        print("\n=== Memgraph read-back ===")
        cur = conn.cursor()
        cur.execute("MATCH (n:SourceFile) RETURN count(n);")
        sf = cur.fetchall()[0][0]
        cur.execute("MATCH (n:WikiLink) RETURN count(n);")
        wl = cur.fetchall()[0][0]
        cur.execute("MATCH ()-[r:MENTIONS]->() RETURN count(r);")
        rc = cur.fetchall()[0][0]
        print(f"  :SourceFile nodes:  {sf:,}")
        print(f"  :WikiLink nodes:    {wl:,}")
        print(f"  :MENTIONS edges:    {rc:,}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

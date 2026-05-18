#!/root/.notebooklm-venv/bin/python3
"""
vault-embed — embed Obsidian-Markdown files into Memgraph vector-index.

ADR: 07-Decisions/2026-05-12 sv-1 memory architecture arch.md
Sprint: B-2, Layer 2 (embedding-pipeline).

Real implementation 2026-05-13 (Week 1 Day 3).
Stack: sentence-transformers bge-m3 (1024-dim multilingual) + Memgraph CE via mgclient.

Usage:
    vault-embed --backfill 11-wiki/              # batch embed wiki
    vault-embed --backfill                       # backfill ALL Semantic-level folders
    vault-embed --file <path>                    # single file
    vault-embed --update-since <ISO>             # incremental update (TODO Week 2)
    vault-embed --dry-run --file <path>          # preview chunks, no embed/write
    vault-embed --namespace skills --file <p>    # custom namespace (B-4 reuse)
"""

import argparse
import hashlib
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")

# Semantic-level folders (B-2 ADR memory-mapping)
SEMANTIC_FOLDERS = ["11-wiki", "07-Decisions", "05-Memory", "02-Projects"]
EPISODIC_FOLDERS = ["01-Daily", "10-raw"]


def chunk_markdown_by_headers(text: str) -> list[dict]:
    """Split markdown by ## headers — each chunk = section + frontmatter (if first)."""
    # Strip frontmatter for chunk-body, but keep as metadata
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm_text = fm_match.group(1) if fm_match else ""
    body = text[fm_match.end():] if fm_match else text

    # Split by ## headers (level-2)
    sections = re.split(r"\n(?=## )", body)
    chunks = []
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        # First chunk: prepend frontmatter for context
        chunk_text = (fm_text + "\n\n" + section) if i == 0 and fm_text else section
        # Extract section title (first ## heading or first 80 chars)
        title_m = re.search(r"^#{1,3}\s+(.+?)$", section, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else section[:80]
        chunks.append({
            "idx": i,
            "title": title,
            "text": chunk_text[:3000],   # cap chunk size for embedding
            "hash": hashlib.sha256(chunk_text.encode()).hexdigest()[:16],
        })
    return chunks


def get_embed_model():
    """Lazy-load sentence-transformers — only when embedding is actually needed."""
    from sentence_transformers import SentenceTransformer
    print(f"  Loading {EMBED_MODEL}...", file=sys.stderr)
    return SentenceTransformer(EMBED_MODEL, device="cpu")


def get_memgraph_conn():
    """Connect to Memgraph via mgclient (Bolt protocol)."""
    import mgclient
    return mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)


def embed_file(path: Path, model, conn, namespace: str = "content", dry_run: bool = False) -> dict:
    """Embed one Markdown file: chunk, embed, write to Memgraph."""
    text = path.read_text(encoding="utf-8", errors="replace")
    rel_path = str(path.relative_to(VAULT_ROOT)) if VAULT_ROOT in path.parents else str(path)
    chunks = chunk_markdown_by_headers(text)

    if dry_run:
        return {"file": rel_path, "chunks": len(chunks), "namespace": namespace, "dry_run": True}

    if not chunks:
        return {"file": rel_path, "chunks": 0, "namespace": namespace}

    # Batch-embed all chunks for this file
    texts = [c["text"] for c in chunks]
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    cursor = conn.cursor()
    written = 0
    for chunk, vec in zip(chunks, vectors):
        vec_list = vec.tolist()   # numpy → python list
        cursor.execute(
            """
            MERGE (c:Chunk {hash: $hash, namespace: $ns})
            SET c.file = $file,
                c.chunk_idx = $idx,
                c.title = $title,
                c.text = $text,
                c.vector = $vector,
                c.updated_at = $ts
            """,
            {
                "hash": chunk["hash"],
                "ns": namespace,
                "file": rel_path,
                "idx": chunk["idx"],
                "title": chunk["title"],
                "text": chunk["text"],
                "vector": vec_list,
                "ts": datetime.utcnow().isoformat(),
            },
        )
        written += 1
    conn.commit()
    return {"file": rel_path, "chunks": written, "namespace": namespace}


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.md"))


def main():
    ap = argparse.ArgumentParser(description="Vault embed (B-2)")
    ap.add_argument("--backfill", nargs="?", const="ALL", help="Backfill dir (default: all semantic folders)")
    ap.add_argument("--file", action="append", default=[], help="File path (absolute or vault-relative). Repeatable to batch multiple files with single model-load.")
    ap.add_argument("--update-since", help="ISO timestamp — re-embed only newer files (TODO)")
    ap.add_argument("--namespace", default="content", help="Memgraph namespace (default: content)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not (args.backfill or args.file or args.update_since):
        ap.print_help()
        sys.exit(1)

    files: list[Path] = []
    if args.file:
        for f in args.file:
            p = Path(f)
            if not p.is_absolute():
                p = VAULT_ROOT / p
            files.append(p.resolve())
    elif args.backfill == "ALL":
        for folder in SEMANTIC_FOLDERS:
            files.extend(collect_files(VAULT_ROOT / folder))
    elif args.backfill:
        target = Path(args.backfill)
        if not target.is_absolute():
            target = VAULT_ROOT / target
        files.extend(collect_files(target))
    elif args.update_since:
        # Real impl 2026-05-13 (B-2 Week 2 Day 5): incremental re-embed
        # for files modified after the given ISO timestamp.
        try:
            cutoff = datetime.fromisoformat(args.update_since).timestamp()
        except ValueError:
            print(f"Invalid ISO timestamp: {args.update_since}", file=sys.stderr)
            sys.exit(1)
        for folder in SEMANTIC_FOLDERS:
            root = VAULT_ROOT / folder
            if not root.exists():
                continue
            for p in root.rglob("*.md"):
                if p.stat().st_mtime > cutoff:
                    files.append(p)
        print(f"Incremental: {len(files)} files modified since {args.update_since}", file=sys.stderr)

    if args.dry_run:
        for f in files[:20]:
            text = f.read_text(encoding="utf-8", errors="replace")
            chunks = chunk_markdown_by_headers(text)
            print(f"  {f.relative_to(VAULT_ROOT) if VAULT_ROOT in f.parents else f.name}: {len(chunks)} chunks")
        print(f"[DRY-RUN] files={len(files)} (showing first 20)")
        return

    # Real embed path: lazy-load model + connect to Memgraph
    print(f"Processing {len(files)} files into namespace='{args.namespace}'...", file=sys.stderr)
    t0 = time.time()
    model = get_embed_model()
    conn = get_memgraph_conn()

    total_chunks, errors = 0, []
    for i, f in enumerate(files):
        try:
            result = embed_file(f, model, conn, args.namespace)
            total_chunks += result["chunks"]
            if (i + 1) % 25 == 0:
                print(f"  [{i+1}/{len(files)}] {total_chunks} chunks written ({time.time()-t0:.1f}s)", file=sys.stderr)
        except Exception as e:
            errors.append((str(f), str(e)[:200]))

    conn.close()
    elapsed = time.time() - t0
    print(f"[EMBED] files={len(files)} chunks={total_chunks} errors={len(errors)} elapsed={elapsed:.1f}s")
    if errors:
        print(f"\nFirst 5 errors:", file=sys.stderr)
        for f, e in errors[:5]:
            print(f"  {f}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

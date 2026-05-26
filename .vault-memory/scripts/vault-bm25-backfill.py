#!/root/.notebooklm-venv/bin/python3
"""
vault-bm25-backfill — build BM25 lexical index over vault chunks (B-2 Week 4).

The corpus is the SAME set of chunks that lives in Memgraph (label :Chunk),
so the resulting BM25 ranks join 1:1 with semantic ranks on (namespace, hash).

ADR: 07-Decisions/2026-05-12 sv-1 memory architecture arch.md
Sprint: B-2, Week 4 (hybrid retrieval).

Persist target:
    /root/obsidian-vault/.vault-memory/data/bm25-index.json
    (JSON, not pickle — security policy. Re-hydrates a BM25Okapi by populating
    its primitive fields directly.)
    Schema:
        {
          "version": 1,
          "built_at": ISO,
          "chunk_count": int,
          "namespaces": {ns_name: count, ...},
          "keys": [[ns, hash, file, chunk_idx, title], ...],
          "tokens": [[tok, ...], ...],
          "bm25": {
              "k1": 1.5, "b": 0.75, "epsilon": 0.25,
              "corpus_size": N, "avgdl": ..., "average_idf": ...,
              "doc_freqs": [{tok: count}, ...],
              "idf": {tok: idf},
              "doc_len": [int, ...],
          },
        }

Tokenization:
    - lowercase
    - NFKD accent-fold (HU: árvíztűrő → arvizturo)
    - split on non-alnum, keep tokens ≥2 chars
    - drop a tiny HU+EN stopword list (cost: noise reduction, recall ~unchanged)

Usage:
    vault-bm25-backfill                  # build/refresh if Memgraph chunk-count changed
    vault-bm25-backfill --force          # rebuild unconditionally
    vault-bm25-backfill --stats          # don't rebuild; just print stats from existing json
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))

INDEX_PATH = Path(
    os.environ.get(
        "VAULT_BM25_INDEX",
        str(VAULT_ROOT / ".vault-memory" / "data" / "bm25-index.json"),
    )
)

# Minimal bilingual stopword set — keep small; BM25 IDF down-weights these anyway.
STOPWORDS = {
    # HU
    "a", "az", "egy", "es", "is", "de", "ha", "nem", "csak", "vagy", "hogy",
    "mint", "meg", "fel", "be", "ki", "le", "el", "at", "ra", "re", "ban", "ben",
    "rol", "rel", "tol", "tel", "val", "vel", "nak", "nek",
    "ezt", "ezek", "ezekre", "ott", "itt", "most", "majd", "mar",
    # EN
    "the", "an", "of", "to", "and", "or", "in", "on", "at", "for", "with",
    "are", "was", "were", "been", "being", "this", "that", "these",
    "those", "it", "its", "as", "by", "from", "if", "then", "else", "but",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def fold_accents(s: str) -> str:
    """NFKD + drop combining marks. árvíztűrő → arvizturo."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )


def tokenize(text: str) -> list[str]:
    """Lowercase → accent-fold → alnum-split → stopword filter → ≥2-char filter."""
    text = fold_accents(text.lower())
    raw = TOKEN_RE.findall(text)
    return [t for t in raw if len(t) >= 2 and t not in STOPWORDS]


def fetch_chunks_from_memgraph():
    """Pull (ns, hash, file, chunk_idx, title, text) tuples from Memgraph."""
    import mgclient
    conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    cur = conn.cursor()
    cur.execute(
        "MATCH (c:Chunk) "
        "RETURN c.namespace AS ns, c.hash AS hash, c.file AS file, "
        "c.chunk_idx AS idx, c.title AS title, c.text AS text"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def bm25_to_json(bm25) -> dict:
    """Serialize rank_bm25.BM25Okapi internal state to JSON-native dict."""
    return {
        "k1": float(bm25.k1),
        "b": float(bm25.b),
        "epsilon": float(bm25.epsilon),
        "corpus_size": int(bm25.corpus_size),
        "avgdl": float(bm25.avgdl),
        "average_idf": float(bm25.average_idf),
        "doc_freqs": [dict(d) for d in bm25.doc_freqs],
        "idf": {k: float(v) for k, v in bm25.idf.items()},
        "doc_len": [int(x) for x in bm25.doc_len],
    }


def build_index(force: bool = False) -> dict:
    """Build BM25Okapi over all Memgraph chunks. Returns the metadata dict written."""
    from rank_bm25 import BM25Okapi

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"[bm25] fetching chunks from Memgraph @ {MEMGRAPH_HOST}:{MEMGRAPH_PORT}...",
          file=sys.stderr)
    t0 = time.time()
    rows = fetch_chunks_from_memgraph()
    print(f"[bm25] got {len(rows)} chunks in {time.time()-t0:.2f}s", file=sys.stderr)

    if not rows:
        print("[bm25] no chunks found — refusing to build empty index", file=sys.stderr)
        sys.exit(2)

    # Idempotency: if existing index has the same chunk count and we're not forced, skip.
    if not force and INDEX_PATH.exists():
        try:
            with INDEX_PATH.open("r", encoding="utf-8") as fh:
                existing = json.load(fh)
            if existing.get("chunk_count") == len(rows):
                print(f"[bm25] index already up-to-date ({len(rows)} chunks) — use --force to rebuild",
                      file=sys.stderr)
                return existing
        except Exception as e:
            print(f"[bm25] could not read existing index ({e}); rebuilding", file=sys.stderr)

    keys = []
    corpus_tokens = []
    ns_counts: dict[str, int] = {}

    t0 = time.time()
    for ns, h, file, idx, title, text in rows:
        ns = ns or "content"
        ns_counts[ns] = ns_counts.get(ns, 0) + 1
        # Combine title + text — title carries the strongest topical signal.
        combined = f"{title or ''} {text or ''}"
        toks = tokenize(combined)
        # BM25Okapi can't handle empty docs gracefully — guard.
        if not toks:
            toks = ["__empty__"]
        keys.append([ns, h, file, idx, title])
        corpus_tokens.append(toks)
    print(f"[bm25] tokenized {len(corpus_tokens)} docs in {time.time()-t0:.2f}s "
          f"(avg {sum(len(t) for t in corpus_tokens)/len(corpus_tokens):.1f} tok/doc)",
          file=sys.stderr)

    t0 = time.time()
    bm25 = BM25Okapi(corpus_tokens)
    print(f"[bm25] BM25Okapi built in {time.time()-t0:.2f}s", file=sys.stderr)

    out = {
        "version": 1,
        "built_at": datetime.utcnow().isoformat() + "Z",
        "chunk_count": len(rows),
        "namespaces": ns_counts,
        "keys": keys,
        "tokens": corpus_tokens,
        "bm25": bm25_to_json(bm25),
    }

    tmp = INDEX_PATH.with_suffix(".json.tmp")
    t0 = time.time()
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    tmp.replace(INDEX_PATH)
    size_mb = INDEX_PATH.stat().st_size / (1024 * 1024)
    print(f"[bm25] wrote {INDEX_PATH} ({size_mb:.2f} MB) in {time.time()-t0:.2f}s",
          file=sys.stderr)
    return out


def show_stats() -> None:
    if not INDEX_PATH.exists():
        print(f"No index at {INDEX_PATH}. Run `vault-bm25-backfill` first.", file=sys.stderr)
        sys.exit(1)
    with INDEX_PATH.open("r", encoding="utf-8") as fh:
        idx = json.load(fh)
    print(f"BM25 index: {INDEX_PATH}")
    print(f"  built_at:    {idx['built_at']}")
    print(f"  chunk_count: {idx['chunk_count']}")
    print(f"  namespaces:  {idx['namespaces']}")
    avg_tok = sum(len(t) for t in idx["tokens"]) / len(idx["tokens"])
    print(f"  avg tokens/doc: {avg_tok:.1f}")
    print(f"  vocab size:  {len(idx['bm25']['idf'])}")
    print(f"  avgdl:       {idx['bm25']['avgdl']:.1f}")
    print(f"  k1={idx['bm25']['k1']}, b={idx['bm25']['b']}")
    print(f"  size: {INDEX_PATH.stat().st_size / (1024*1024):.2f} MB")


def main():
    ap = argparse.ArgumentParser(description="vault-bm25-backfill (B-2 Week 4)")
    ap.add_argument("--force", action="store_true",
                    help="Rebuild even if chunk_count matches existing index")
    ap.add_argument("--stats", action="store_true",
                    help="Print stats from existing index; do not rebuild")
    args = ap.parse_args()

    if args.stats:
        show_stats()
        return

    build_index(force=args.force)


if __name__ == "__main__":
    main()

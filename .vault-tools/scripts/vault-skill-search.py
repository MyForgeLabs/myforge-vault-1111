#!/root/.notebooklm-venv/bin/python3
"""
vault-skill-search — semantic search across the SKILL.md pool (B-4 Réteg 2).

ADR: 07-Decisions/2026-05-12 sv-4 tool composition arch.md
Sprint: B-4 Week 2 (bge-m3 dense retriever over Memgraph native vector-index).

History:
    2026-05-13 (Day 0)  — skeleton (no-op search_stub).
    2026-05-17 (Week 2) — REAL impl: bge-m3 embed-batch + :SkillChunk node +
                          skill_chunk_vec native vector-index + native search.
                          Reuses the daemon `encode` RPC (warm bge-m3) when
                          available, with in-process bge-m3 fallback.
    2026-05-17 (Week 3) — Daemon `search_skills` RPC: encode + Memgraph
                          vector_search.search folded into a single round-trip.
                          New --server/--no-server CLI flag; default: ON when
                          the daemon socket is up, fallback to legacy path when
                          absent. Eliminates per-process mgclient + numpy
                          import overhead (~50-100ms) for query calls.

Schema (Memgraph, distinct namespace from B-2 :Chunk):
    (s:SkillChunk {
        path:        TEXT  — absolute realpath of SKILL.md, used as MERGE key
        name:        TEXT  — skill name (kebab-case from frontmatter or folder)
        description: TEXT  — one-line description from frontmatter
        body:        TEXT  — first ~1000 chars of body (post-frontmatter) used for embed
        source_root: TEXT  — "agents" | "plugins"
        embedding:   FLOAT[1024] — bge-m3 vector of (description + body[:cap])
        text_hash:   TEXT  — sha256 of embed-input, used for idempotency skip
        updated_at:  TEXT  — ISO timestamp
    })

Vector index:
    CREATE VECTOR INDEX skill_chunk_vec ON :SkillChunk(embedding)
        WITH CONFIG {"dimension": 1024, "capacity": 1024, "metric": "cos"};

Usage:
    # Backfill (idempotent, skips skills with unchanged text_hash)
    vault-skill-search --backfill
    vault-skill-search --backfill --dry-run

    # Hard reset (DROP node-set + index, then re-embed everything)
    vault-skill-search --reset
    vault-skill-search --reset --yes

    # Index lifecycle
    vault-skill-search --create-index
    vault-skill-search --drop-index
    vault-skill-search --info

    # Search
    vault-skill-search "skill that does CI pipeline setup"
    vault-skill-search --top-k 5 "deploy to Azure"
    vault-skill-search --json "WordPress block development"
"""

import argparse
import hashlib
import json
import os
import re
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")

# Roots scanned for SKILL.md — both symlinked agent skills and plugin caches.
# Mirrors skill-canonicalize.py for consistency.
SKILL_ROOTS = [
    ("agents", Path("/root/.agents/skills")),
    ("plugins", Path("/root/.claude/plugins")),
]

DEFAULT_TOP_K = 3
DEFAULT_THRESHOLD = float(os.environ.get("SKILL_SEARCH_THRESHOLD", "0.0"))
BODY_CAP_CHARS = int(os.environ.get("SKILL_BODY_CAP", "1000"))

# Native vector-index config (mirrors vault-vector-index-migrate defaults).
VECTOR_INDEX_NAME = "skill_chunk_vec"
VECTOR_LABEL = "SkillChunk"
VECTOR_PROP = "embedding"
VECTOR_DIM = 1024            # bge-m3
VECTOR_CAPACITY = 1024       # 2× current 462 with room for new skills
VECTOR_METRIC = "cos"

# Daemon socket candidates (vault-search-server `encode` RPC).
SOCKET_CANDIDATES = [
    os.environ.get("VAULT_SEARCH_SOCKET"),
    "/run/vault-search.sock",
    "/tmp/vault-search.sock",
]
SOCKET_CANDIDATES = [s for s in SOCKET_CANDIDATES if s]
SOCKET_TIMEOUT = float(os.environ.get("VAULT_SEARCH_SOCKET_TIMEOUT", "1.5"))

AUDIT_DIR = VAULT_ROOT / "06-Audits"


# ─── Skill discovery / parsing ───────────────────────────────────────────────
def find_skill_files() -> list[tuple[str, Path]]:
    """Return [(source_root_label, realpath)] tuples, deduped by realpath."""
    seen: set[str] = set()
    out: list[tuple[str, Path]] = []
    for label, root in SKILL_ROOTS:
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
            out.append((label, Path(real)))
    return sorted(out, key=lambda t: str(t[1]))


_FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def parse_skill(path: Path) -> dict:
    """
    Extract name + description + body from a SKILL.md.

    Strategy:
        - YAML-ish frontmatter parsed line-by-line (no extra dep; handles the
          common `key: value` shape used by Anthropic spec).
        - Description fallback = first non-frontmatter paragraph.
        - Name fallback = parent folder name.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"name": path.parent.name, "description": "", "body": "",
                "error": f"read: {e}"}

    m = _FM_RE.match(text)
    fm_block = m.group(1) if m else ""
    body = text[m.end():] if m else text

    fm: dict[str, str] = {}
    for line in fm_block.splitlines():
        # Only capture top-level scalar keys. Lists/multiline are ignored;
        # we just need name + description.
        mk = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", line)
        if not mk:
            continue
        key = mk.group(1)
        val = mk.group(2).strip()
        # Strip surrounding quotes if present
        if (val.startswith("'") and val.endswith("'")) or \
           (val.startswith('"') and val.endswith('"')):
            val = val[1:-1]
        fm[key] = val

    name = fm.get("name", "").strip() or path.parent.name
    description = fm.get("description", "").strip()
    if not description:
        # Fallback: first non-empty paragraph from body
        for chunk in re.split(r"\n\s*\n", body, maxsplit=4):
            chunk = chunk.strip()
            if chunk and not chunk.startswith("#"):
                description = chunk[:300]
                break

    # Embed-text = description + body, capped. Drop heading markers / collapse blanks.
    body_clean = re.sub(r"\n{3,}", "\n\n", body).strip()
    body_snippet = body_clean[:BODY_CAP_CHARS]
    return {
        "name": name,
        "description": description,
        "body": body_snippet,
    }


def build_embed_text(skill: dict) -> str:
    """Concatenate description + body, trimmed."""
    parts = []
    if skill.get("description"):
        parts.append(skill["description"])
    if skill.get("body"):
        parts.append(skill["body"])
    text = "\n\n".join(parts).strip()
    return text[:BODY_CAP_CHARS + 400]  # description allowance on top of body cap


# ─── Embedding (daemon-first, in-process fallback) ───────────────────────────
_MODEL = None


def _get_in_process_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        print(f"  Loading {EMBED_MODEL} in-process (cold ~5s)...", file=sys.stderr)
        _MODEL = SentenceTransformer(EMBED_MODEL, device="cpu")
    return _MODEL


def _daemon_rpc(payload: dict) -> dict | None:
    """Low-level: send a JSON RPC to the first reachable daemon socket.

    Returns the parsed response dict, or None if no socket is up / call fails.
    Shared by encode_via_daemon (legacy) and search_via_daemon (Week 3).
    """
    for path in SOCKET_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect(path)
            sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            sock.settimeout(10.0)
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
            sock.close()
            return json.loads(buf.decode("utf-8"))
        except (socket.timeout, ConnectionRefusedError, FileNotFoundError, OSError):
            continue
    return None


def daemon_available() -> bool:
    """Cheap check: is *any* candidate socket present on disk?"""
    return any(os.path.exists(p) for p in SOCKET_CANDIDATES)


def encode_via_daemon(text: str) -> list | None:
    """Call vault-search-server's `encode` RPC. Returns vector or None on fail."""
    resp = _daemon_rpc({"method": "encode", "query": text})
    if resp is None:
        return None
    return resp.get("vector")


def search_via_daemon(query: str, top_k: int, threshold: float) -> dict | None:
    """B-4 Week 3: single-RPC search via `search_skills` (warm encode + Memgraph).

    Returns a dict shaped identically to the legacy in-process search() output
    (query/top_k/results/encode_ms/search_ms/total_ms), with extra `index` and
    `model` fields. Returns None if the daemon is unreachable or errors out —
    the caller should then fall back to the in-process path.
    """
    resp = _daemon_rpc({
        "method": "search_skills",
        "query": query,
        "top_k": top_k,
        "threshold": threshold,
    })
    if resp is None or "error" in resp:
        return None
    return resp


def encode_batch(texts: list[str], prefer_daemon: bool = True) -> list[list[float]]:
    """
    Batch-encode. For batch jobs we prefer in-process (single bulk encode call)
    because the daemon-RPC has per-call socket overhead. Daemon is preferred
    for ONE-shot queries (warm-model latency advantage).
    """
    # For backfill batches we always go in-process — bge-m3 in batch is much
    # faster than RPC-per-item. The daemon `encode` is meant for query-time.
    model = _get_in_process_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False,
                        batch_size=8)
    return [v.tolist() for v in vecs]


def encode_one(text: str) -> list[float]:
    """Single-query encode. Tries daemon first (warm model), then in-process."""
    v = encode_via_daemon(text)
    if v is not None:
        return v
    model = _get_in_process_model()
    return model.encode([text], normalize_embeddings=True,
                        show_progress_bar=False)[0].tolist()


# ─── Memgraph helpers ────────────────────────────────────────────────────────
def get_conn(autocommit: bool = False):
    import mgclient
    conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    if autocommit:
        conn.autocommit = True
    return conn


def show_vector_indexes(cur) -> list:
    cur.execute("SHOW VECTOR INDEX INFO;")
    return cur.fetchall()


def ensure_vector_index(verbose: bool = True) -> dict:
    """Create the native vector-index on :SkillChunk(embedding) if absent."""
    conn = get_conn(autocommit=True)
    cur = conn.cursor()
    existing = {row[0]: row for row in show_vector_indexes(cur)}
    if VECTOR_INDEX_NAME in existing:
        row = existing[VECTOR_INDEX_NAME]
        if verbose:
            print(f"  vector-index '{VECTOR_INDEX_NAME}' exists "
                  f"(size={row[6]}, dim={row[4]}, metric={row[5]})")
        conn.close()
        return {"created": False, "name": VECTOR_INDEX_NAME,
                "size": row[6], "dim": row[4], "metric": row[5]}
    cypher = (
        f'CREATE VECTOR INDEX {VECTOR_INDEX_NAME} ON :{VECTOR_LABEL}({VECTOR_PROP}) '
        f'WITH CONFIG {{"dimension": {VECTOR_DIM}, '
        f'"capacity": {VECTOR_CAPACITY}, "metric": "{VECTOR_METRIC}"}};'
    )
    if verbose:
        print(f"  creating vector-index: {cypher}")
    cur.execute(cypher)
    conn.close()
    return {"created": True, "name": VECTOR_INDEX_NAME, "dim": VECTOR_DIM,
            "capacity": VECTOR_CAPACITY, "metric": VECTOR_METRIC}


def drop_vector_index(verbose: bool = True) -> bool:
    conn = get_conn(autocommit=True)
    cur = conn.cursor()
    existing = {row[0]: row for row in show_vector_indexes(cur)}
    if VECTOR_INDEX_NAME not in existing:
        if verbose:
            print(f"  vector-index '{VECTOR_INDEX_NAME}' absent — nothing to drop")
        conn.close()
        return False
    cur.execute(f"DROP VECTOR INDEX {VECTOR_INDEX_NAME};")
    if verbose:
        print(f"  dropped '{VECTOR_INDEX_NAME}'")
    conn.close()
    return True


def fetch_existing_hashes() -> dict[str, str]:
    """{path: text_hash} for all :SkillChunk nodes — used for idempotency skip."""
    conn = get_conn(autocommit=True)
    cur = conn.cursor()
    cur.execute(f"MATCH (s:{VECTOR_LABEL}) RETURN s.path, s.text_hash")
    out = {}
    for path, h in cur.fetchall():
        if path:
            out[path] = h or ""
    conn.close()
    return out


def delete_all_skill_chunks(verbose: bool = True) -> int:
    conn = get_conn(autocommit=True)
    cur = conn.cursor()
    cur.execute(f"MATCH (s:{VECTOR_LABEL}) RETURN count(s)")
    n = cur.fetchone()[0]
    cur.execute(f"MATCH (s:{VECTOR_LABEL}) DELETE s")
    if verbose:
        print(f"  deleted {n} :{VECTOR_LABEL} nodes")
    conn.close()
    return n


def upsert_skill_chunk(cur, *, path: str, name: str, description: str,
                       body: str, source_root: str, vector: list[float],
                       text_hash: str, ts: str) -> None:
    cur.execute(
        f"""
        MERGE (s:{VECTOR_LABEL} {{path: $path}})
        SET s.name = $name,
            s.description = $description,
            s.body = $body,
            s.source_root = $source_root,
            s.{VECTOR_PROP} = $vector,
            s.text_hash = $text_hash,
            s.updated_at = $ts
        """,
        {
            "path": path,
            "name": name,
            "description": description,
            "body": body,
            "source_root": source_root,
            "vector": vector,
            "text_hash": text_hash,
            "ts": ts,
        },
    )


# ─── Backfill ────────────────────────────────────────────────────────────────
def backfill(*, dry_run: bool = False, force: bool = False,
             audit_path: Path | None = None) -> dict:
    """
    Embed all SKILL.md files into :SkillChunk nodes (idempotent).

    Skips skills whose text_hash matches an existing node, unless `force=True`.
    Writes a JSONL audit-log if audit_path is provided.
    """
    t0 = time.time()
    files = find_skill_files()
    print(f"Discovered {len(files)} SKILL.md "
          f"(agents={sum(1 for s,_ in files if s == 'agents')}, "
          f"plugins={sum(1 for s,_ in files if s == 'plugins')})", file=sys.stderr)

    if not files:
        return {"discovered": 0, "embedded": 0, "skipped": 0, "errors": 0}

    # Parse all skills first (cheap)
    parsed = []
    parse_errors = []
    for source_root, path in files:
        s = parse_skill(path)
        if "error" in s:
            parse_errors.append({"path": str(path), "error": s["error"]})
            continue
        embed_text = build_embed_text(s)
        if not embed_text:
            parse_errors.append({"path": str(path), "error": "empty embed-text"})
            continue
        text_hash = hashlib.sha256(embed_text.encode("utf-8")).hexdigest()[:16]
        parsed.append({
            "path": str(path),
            "source_root": source_root,
            "name": s["name"],
            "description": s["description"],
            "body": s["body"],
            "embed_text": embed_text,
            "text_hash": text_hash,
        })

    # Idempotency: fetch existing hashes
    existing = {} if force else fetch_existing_hashes()
    to_embed = [p for p in parsed if existing.get(p["path"]) != p["text_hash"]]
    skipped = [p for p in parsed if existing.get(p["path"]) == p["text_hash"]]

    print(f"To embed: {len(to_embed)}; idempotent-skip: {len(skipped)}; "
          f"parse-errors: {len(parse_errors)}", file=sys.stderr)

    if dry_run:
        return {"discovered": len(files), "to_embed": len(to_embed),
                "skipped": len(skipped), "parse_errors": len(parse_errors),
                "dry_run": True}

    # Ensure index exists BEFORE writes (so HNSW indexes new vectors on insert).
    ensure_vector_index(verbose=True)

    if not to_embed:
        print("Nothing to embed (all up-to-date).", file=sys.stderr)
        return {"discovered": len(files), "embedded": 0,
                "skipped": len(skipped), "errors": len(parse_errors),
                "elapsed_s": round(time.time() - t0, 2)}

    # Batch-encode (in-process model — fastest for bulk)
    texts = [p["embed_text"] for p in to_embed]
    print(f"Encoding {len(texts)} skill texts (bge-m3, batch=8)...", file=sys.stderr)
    t_encode = time.time()
    vectors = encode_batch(texts, prefer_daemon=False)
    encode_s = time.time() - t_encode
    print(f"  encode: {encode_s:.1f}s ({encode_s/len(texts)*1000:.0f}ms/skill)",
          file=sys.stderr)

    # Write to Memgraph (single conn, batched commits)
    conn = get_conn(autocommit=False)
    cur = conn.cursor()
    written = 0
    write_errors = []
    ts = datetime.utcnow().isoformat()
    audit_records = []

    for i, (entry, vec) in enumerate(zip(to_embed, vectors)):
        try:
            upsert_skill_chunk(
                cur,
                path=entry["path"],
                name=entry["name"],
                description=entry["description"],
                body=entry["body"],
                source_root=entry["source_root"],
                vector=vec,
                text_hash=entry["text_hash"],
                ts=ts,
            )
            written += 1
            audit_records.append({
                "ts": ts,
                "event": "embedded",
                "path": entry["path"],
                "name": entry["name"],
                "source_root": entry["source_root"],
                "text_hash": entry["text_hash"],
                "dim": len(vec),
            })
            if (i + 1) % 50 == 0:
                conn.commit()
                print(f"  [{i+1}/{len(to_embed)}] committed", file=sys.stderr)
        except Exception as e:
            write_errors.append({"path": entry["path"], "error": str(e)[:200]})
    conn.commit()
    conn.close()

    # Audit log (JSONL)
    if audit_path:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_path.open("a", encoding="utf-8") as f:
            for r in audit_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            # Also write parse + write errors
            for e in parse_errors:
                f.write(json.dumps({"ts": ts, "event": "parse_error", **e}) + "\n")
            for e in write_errors:
                f.write(json.dumps({"ts": ts, "event": "write_error", **e}) + "\n")

    elapsed = time.time() - t0
    print(f"[BACKFILL] discovered={len(files)} embedded={written} "
          f"skipped={len(skipped)} errors={len(parse_errors)+len(write_errors)} "
          f"elapsed={elapsed:.1f}s", file=sys.stderr)
    return {
        "discovered": len(files),
        "embedded": written,
        "skipped": len(skipped),
        "errors": len(parse_errors) + len(write_errors),
        "elapsed_s": round(elapsed, 2),
        "encode_s": round(encode_s, 2),
        "audit_path": str(audit_path) if audit_path else None,
    }


def reset_and_backfill(audit_path: Path | None = None) -> dict:
    """Drop index + nodes, then re-embed everything."""
    print("=== RESET: dropping index + :SkillChunk nodes ===", file=sys.stderr)
    drop_vector_index(verbose=True)
    delete_all_skill_chunks(verbose=True)
    return backfill(dry_run=False, force=True, audit_path=audit_path)


# ─── Search ──────────────────────────────────────────────────────────────────
def search(query: str, top_k: int = DEFAULT_TOP_K,
           threshold: float = DEFAULT_THRESHOLD,
           prefer_server: bool | None = None) -> dict:
    """
    Top-K skill search over skill_chunk_vec.

    Two execution paths:
      1. **Server-mode** (default when daemon socket is up): single `search_skills`
         RPC — daemon handles encode + Memgraph search in one round-trip.
         Avoids per-process mgclient + numpy imports.
      2. **Cold-mode** (legacy fallback): in-process encode (daemon `encode` RPC
         OR cold model load) + direct mgclient → vector_search.search.

    Args:
        prefer_server: True = force server-mode (error if unavailable).
                       False = force cold-mode.
                       None (default) = auto: server if daemon up, cold otherwise.
    """
    # ── Path 1: server-mode (preferred) ──────────────────────────────────────
    if prefer_server is None:
        prefer_server = daemon_available()

    if prefer_server:
        t0 = time.time()
        resp = search_via_daemon(query, top_k, threshold)
        rpc_ms = (time.time() - t0) * 1000.0
        if resp is not None:
            # Daemon honoured the request; trust its timings, attach mode tag.
            return {
                "query": resp.get("query", query),
                "top_k": resp.get("top_k", top_k),
                "results": resp.get("results", []),
                "encode_ms": resp.get("encode_ms", 0.0),
                "search_ms": resp.get("search_ms", 0.0),
                "total_ms": resp.get("total_ms", 0.0),
                "rpc_ms": round(rpc_ms, 1),
                "mode": "server",
                "index": resp.get("index"),
                "model": resp.get("model"),
            }
        # Daemon unreachable or errored mid-call → fall through to cold-mode.
        # (Graceful fallback per spec.)
        print("  [vault-skill-search] daemon RPC failed → cold-mode fallback",
              file=sys.stderr)

    # ── Path 2: cold-mode (legacy in-process) ────────────────────────────────
    t0 = time.time()
    q_vec = encode_one(query)
    encode_ms = (time.time() - t0) * 1000.0

    t1 = time.time()
    conn = get_conn(autocommit=True)
    cur = conn.cursor()
    fetch_k = max(top_k * 2, 10)
    cur.execute(
        "CALL vector_search.search($idx, $k, $qv) YIELD node, similarity "
        f"RETURN node.path AS path, node.name AS name, "
        f"node.description AS description, node.source_root AS source_root, "
        "similarity AS score",
        {"idx": VECTOR_INDEX_NAME, "k": fetch_k, "qv": q_vec},
    )
    rows = cur.fetchall()
    conn.close()
    search_ms = (time.time() - t1) * 1000.0

    results = []
    for path, name, description, source_root, score in rows:
        if score < threshold:
            continue
        results.append({
            "path": path,
            "name": name,
            "description": description or "",
            "source_root": source_root,
            "score": float(score),
        })
        if len(results) >= top_k:
            break
    return {
        "query": query,
        "top_k": top_k,
        "results": results,
        "encode_ms": round(encode_ms, 1),
        "search_ms": round(search_ms, 1),
        "total_ms": round(encode_ms + search_ms, 1),
        "mode": "cold",
    }


def show_info() -> None:
    conn = get_conn(autocommit=True)
    cur = conn.cursor()
    cur.execute(f"MATCH (s:{VECTOR_LABEL}) RETURN count(s)")
    n_nodes = cur.fetchone()[0]
    cur.execute(f"MATCH (s:{VECTOR_LABEL}) RETURN s.source_root AS sr, count(*) AS n")
    breakdown = cur.fetchall()
    rows = show_vector_indexes(cur)
    conn.close()
    print(f":{VECTOR_LABEL} nodes: {n_nodes}")
    for sr, n in breakdown:
        print(f"  {sr}: {n}")
    print()
    print("Vector indexes:")
    for r in rows:
        print(f"  {r}")


# ─── CLI ─────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Vault skill search (B-4 Week 2)")
    ap.add_argument("query", nargs="?", help="Free-text query (search mode)")
    ap.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                    help=f"Number of results (default {DEFAULT_TOP_K})")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                    help="Min cosine similarity (default 0.0)")
    ap.add_argument("--json", action="store_true",
                    help="JSON output (search) or summary (backfill)")
    # Lifecycle / batch ops
    ap.add_argument("--backfill", action="store_true",
                    help="Embed all SKILL.md (idempotent; skips unchanged)")
    ap.add_argument("--reset", action="store_true",
                    help="Drop nodes+index and re-embed everything")
    ap.add_argument("--yes", action="store_true",
                    help="Skip interactive confirm for --reset")
    ap.add_argument("--force", action="store_true",
                    help="With --backfill: re-embed even if text_hash matches")
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview backfill counts without writing")
    ap.add_argument("--create-index", action="store_true",
                    help="Only create the skill_chunk_vec native vector-index")
    ap.add_argument("--drop-index", action="store_true",
                    help="Only drop the skill_chunk_vec vector-index")
    ap.add_argument("--info", action="store_true",
                    help="Show :SkillChunk node-count + index state")
    # B-4 Week 3: server-mode toggles (single-RPC search via vault-search-server).
    server_grp = ap.add_mutually_exclusive_group()
    server_grp.add_argument(
        "--server", dest="server_mode", action="store_true", default=None,
        help="Force server-mode: search via vault-search-server `search_skills` RPC "
             "(warm bge-m3 + Memgraph in one round-trip). Default: auto-on if "
             "daemon socket present.",
    )
    server_grp.add_argument(
        "--no-server", dest="server_mode", action="store_false", default=None,
        help="Force cold-mode: legacy in-process encode + direct mgclient search. "
             "Used for benchmarking or when the daemon is intentionally offline.",
    )
    args = ap.parse_args()

    # Lifecycle ops short-circuit
    if args.info:
        show_info()
        return 0
    if args.create_index:
        result = ensure_vector_index()
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        return 0
    if args.drop_index:
        dropped = drop_vector_index()
        if args.json:
            print(json.dumps({"dropped": dropped, "name": VECTOR_INDEX_NAME}))
        return 0

    if args.reset:
        if not args.yes:
            confirm = input(
                f"DROP all :{VECTOR_LABEL} nodes + index '{VECTOR_INDEX_NAME}', "
                f"then re-embed? [y/N] "
            ).strip().lower()
            if confirm != "y":
                print("aborted.")
                return 1
        audit_path = AUDIT_DIR / f"skill-embedding-batch-{datetime.utcnow():%Y%m%d}.jsonl"
        result = reset_and_backfill(audit_path=audit_path)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.backfill:
        audit_path = AUDIT_DIR / f"skill-embedding-batch-{datetime.utcnow():%Y%m%d}.jsonl"
        result = backfill(dry_run=args.dry_run, force=args.force,
                          audit_path=None if args.dry_run else audit_path)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    # Default: search mode
    if not args.query:
        ap.print_help()
        return 1

    resp = search(args.query, top_k=args.top_k, threshold=args.threshold,
                  prefer_server=args.server_mode)
    if args.json:
        print(json.dumps(resp, ensure_ascii=False, indent=2))
    elif resp["results"]:
        mode_tag = resp.get("mode", "?")
        rpc_extra = (f" rpc={resp['rpc_ms']}ms" if "rpc_ms" in resp else "")
        print(f"Top-{len(resp['results'])} for {args.query!r} "
              f"[{mode_tag}] (encode={resp['encode_ms']}ms, "
              f"search={resp['search_ms']}ms, total={resp['total_ms']}ms{rpc_extra}):")
        for r in resp["results"]:
            print(f"  [{r['score']:.3f}] {r['name']}  ({r['source_root']})")
            desc = (r["description"] or "")[:140]
            print(f"          {desc}")
            print(f"          {r['path']}")
    else:
        print(f"No skills matched (threshold={args.threshold}). "
              f"Did you run `vault-skill-search --backfill`?")
    return 0


if __name__ == "__main__":
    sys.exit(main())

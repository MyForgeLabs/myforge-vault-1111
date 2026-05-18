#!/root/.notebooklm-venv/bin/python3
"""
vault-search — semantic search across vault chunks in Memgraph.

ADR: 07-Decisions/2026-05-12 sv-1 memory architecture arch.md
Sprint: B-2, Layer 3 (retrieval-pipeline).

History:
    2026-05-13 (Week 2 Day 4) — initial impl, in-Python cosine over Memgraph fetch.
    2026-05-17 (Week 2)       — daemon socket-first-with-fallback (warm-bge-m3 + numpy).
    2026-05-17 (Week 4)       — NATIVE Memgraph vector_search.search backend (sub-ms).
                                Stack now: bge-m3 encode + native vector-index search.

Backend selection (--backend, default auto):
    native  : call `vector_search.search('vault_chunk_vec', k, qvec)` directly.
              Requires the index — `vault-vector-index-migrate` creates it.
    numpy   : socket-call to vault-search-server daemon (in-RAM numpy cosine).
              Daemon also still answers if --backend=auto and native fails.
    auto    : try native first; if no index or vector_search proc missing → daemon;
              if daemon dead → in-process legacy load.

Usage:
    vault-search "milyen projektek vannak"
    vault-search --top-k 5 "Memgraph vs Neo4j tradeoffs"
    vault-search --namespace skills "deploy Next.js app"
    vault-search --backend=native "..."
    vault-search --backend=numpy  "..."        # force daemon
    vault-search --json "..."
    vault-search --no-socket "..."             # force legacy in-process path
    vault-search --rerank "..."                # 2-pass: dense top-N → bge-reranker-v2-m3 → top-K
    vault-search --mode reranked "..."         # equivalent to --rerank (always rerank)
    vault-search --mode auto-rerank "..."      # DEFAULT — rerank only if first-pass max_cos<0.65
    vault-search --mode smart-rerank "..."     # alias for auto-rerank
    vault-search --mode cosine "..."           # explicit cosine-only (skip reranker)
    RERANK_TRIGGER_THRESHOLD=0.7 vault-search "..."  # raise/lower the smart trigger
"""

import argparse
import json
import os
import re
import socket
import sys
import unicodedata
from pathlib import Path

MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")
SEARCH_MODE = os.environ.get("VAULT_SEARCH_MODE", "semantic")

# ── Hybrid (B-2 Week 4) ──────────────────────────────────────────────────────
VAULT_ROOT_FOR_BM25 = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
BM25_INDEX_PATH = Path(os.environ.get(
    "VAULT_BM25_INDEX",
    str(VAULT_ROOT_FOR_BM25 / ".vault-memory" / "data" / "bm25-index.json"),
))
RRF_K = int(os.environ.get("VAULT_RRF_K", "60"))            # standard RRF constant
HYBRID_FETCH_K = int(os.environ.get("VAULT_HYBRID_FETCH_K", "50"))  # per-side top-N
_BM25_CACHE: dict = {}
SEARCH_BACKEND_DEFAULT = os.environ.get("VAULT_SEARCH_BACKEND", "auto")
VECTOR_INDEX_NAME = os.environ.get("VAULT_VECTOR_INDEX", "vault_chunk_vec")
RERANKER_MODEL = os.environ.get("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
# 2026-05-17 Week 4 A/B (bge-reranker-base 277MB vs v2-m3 568MB).
RERANKER_MODEL_ALIASES = {
    "v2-m3": "BAAI/bge-reranker-v2-m3",
    "base":  "BAAI/bge-reranker-base",
    "auto":  RERANKER_MODEL,
}


def _resolve_reranker_model(name):
    """Alias → HF id. None/empty → default RERANKER_MODEL."""
    if not name:
        return RERANKER_MODEL
    return RERANKER_MODEL_ALIASES.get(name, name)


RERANK_OVERSAMPLE = int(os.environ.get("RERANK_OVERSAMPLE", "6"))
RERANK_MAX_CANDIDATES = int(os.environ.get("RERANK_MAX_CANDIDATES", "30"))
RERANK_MAX_LENGTH = int(os.environ.get("RERANK_MAX_LENGTH", "256"))
RERANK_BATCH_SIZE = int(os.environ.get("RERANK_BATCH_SIZE", "8"))
# Smart-rerank trigger: skip the (~13s) cross-encoder if first-pass cosine is
# already confident (max_score >= threshold). Default 0.65 from 2026-05-17 audit.
RERANK_TRIGGER_THRESHOLD = float(os.environ.get("RERANK_TRIGGER_THRESHOLD", "0.65"))
# 2026-05-17 Week 5 — score-gap smart-skip. If top-1 cosine is FAR ahead of
# top-2 (top1-top2 > gap), the head is unambiguous and rerank can't help → SKIP
# even when max_cos < trigger_threshold. Default 0.0 = OFF (backward-compat).
RERANK_SCORE_GAP_THRESHOLD = float(
    os.environ.get("RERANK_SCORE_GAP_THRESHOLD", "0.0")
)

SOCKET_CANDIDATES = [
    os.environ.get("VAULT_SEARCH_SOCKET"),
    "/run/vault-search.sock",
    "/tmp/vault-search.sock",
]
SOCKET_CANDIDATES = [s for s in SOCKET_CANDIDATES if s]
SOCKET_TIMEOUT = float(os.environ.get("VAULT_SEARCH_SOCKET_TIMEOUT", "1.0"))


# ──────────────────────────────────────────────────────────────────────────────
# Native backend — Memgraph vector_search.search
# ──────────────────────────────────────────────────────────────────────────────
def _native_search(query: str, top_k: int, namespace: str,
                   return_full_text: bool = False,
                   fetch_k_override: int | None = None) -> list[dict] | None:
    """Encode via daemon (if available) or in-process, then native vector_search.

    return_full_text=True attaches '_text' for downstream reranker. fetch_k_override
    lets the caller request a larger first-pass candidate pool (for reranking).
    """
    # Always need a query-vector. Prefer daemon for encoding (warm model),
    # because the encode itself is the slow part (~5s cold, ~0.1s warm).
    q_vec = _encode_via_daemon(query)
    if q_vec is None:
        # No daemon → in-process encode (cold-boot ~5s once).
        try:
            from sentence_transformers import SentenceTransformer  # noqa: WPS433
            model = SentenceTransformer(EMBED_MODEL, device="cpu")
            q_vec = model.encode([query], normalize_embeddings=True)[0].tolist()
        except Exception as e:
            print(f"[native] encode failed: {e}", file=sys.stderr)
            return None

    try:
        import mgclient  # noqa: WPS433
        conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
        cur = conn.cursor()
        # Vector index is global (no namespace filtering at index level), so we
        # over-fetch and filter. Default heuristic: top_k * 4 to compensate for
        # cross-namespace dilution. Reranker callers pass a larger fetch_k.
        fetch_k = fetch_k_override if fetch_k_override is not None else max(top_k * 4, 20)
        cur.execute(
            "CALL vector_search.search($idx, $k, $qv) YIELD node, similarity "
            "RETURN node.namespace AS ns, node.file AS file, node.chunk_idx AS idx, "
            "node.title AS title, node.text AS text, similarity AS score",
            {"idx": VECTOR_INDEX_NAME, "k": fetch_k, "qv": q_vec},
        )
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        print(f"[native] vector_search call failed: {e}", file=sys.stderr)
        return None

    out = []
    for ns, file, idx, title, text, score in rows:
        if namespace and (ns or "content") != namespace:
            continue
        entry = {
            "file": file,
            "chunk_idx": idx,
            "title": title,
            "snippet": (text or "")[:200],
            "score": float(score),
        }
        if return_full_text:
            entry["_text"] = text or ""
        out.append(entry)
        if len(out) >= fetch_k:
            break
    return out


def _encode_via_daemon(query: str) -> list | None:
    """Ask daemon to encode-only via the 'encode' RPC (added in Week 4)."""
    for path in SOCKET_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect(path)
            sock.sendall((json.dumps({"method": "encode", "query": query}) + "\n").encode("utf-8"))
            sock.settimeout(10.0)
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
            sock.close()
            resp = json.loads(buf.decode("utf-8"))
            if "vector" in resp:
                return resp["vector"]
            return None
        except (socket.timeout, ConnectionRefusedError, FileNotFoundError, OSError):
            continue
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Daemon (numpy) backend — existing path
# ──────────────────────────────────────────────────────────────────────────────
def _try_socket_search(query: str, top_k: int, namespace: str,
                       rerank: bool = False, smart_rerank: bool = False,
                       trigger_threshold: float | None = None,
                       score_gap_threshold: float | None = None,
                       reranker_model: str | None = None) -> dict | None:
    """Return full daemon response dict (with mode/metadata), or None if unreachable.

    Returns the full response so the CLI can surface mode='reranked', rerank_ms,
    first_pass_k for benchmarking. Callers that only need the result list should
    use resp['results'].

    reranker_model: optional alias ("v2-m3"/"base"/"auto") or full HF id. The
    daemon resolves aliases server-side.
    """
    for path in SOCKET_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect(path)
            req_dict = {
                "method": "search",
                "query": query,
                "top_k": top_k,
                "namespace": namespace,
                "rerank": rerank,
                "smart_rerank": smart_rerank,
            }
            if trigger_threshold is not None:
                req_dict["trigger_threshold"] = trigger_threshold
            if score_gap_threshold is not None:
                req_dict["score_gap_threshold"] = score_gap_threshold
            if reranker_model is not None:
                req_dict["reranker_model"] = reranker_model
            req = json.dumps(req_dict) + "\n"
            sock.sendall(req.encode("utf-8"))
            # Reranker cold-load can be ~25s; otherwise <0.5s. Give 60s margin.
            # smart_rerank may also trigger reranker → same margin.
            sock.settimeout(60.0 if (rerank or smart_rerank) else 10.0)
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
            sock.close()
            resp = json.loads(buf.decode("utf-8"))
            if "error" in resp:
                print(f"[socket] daemon error: {resp['error']}", file=sys.stderr)
                return None
            return resp
        except (socket.timeout, ConnectionRefusedError, FileNotFoundError, OSError) as e:
            print(f"[socket] {path}: {type(e).__name__} — falling back", file=sys.stderr)
            continue
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Legacy in-process backend (cold)
# ──────────────────────────────────────────────────────────────────────────────
def cosine(a, b):
    """Cosine similarity for two normalized vectors → dot product."""
    return sum(x * y for x, y in zip(a, b))


def _legacy_search(query: str, top_k: int = 5, namespace: str = "content",
                   return_full_text: bool = False,
                   fetch_k_override: int | None = None) -> list[dict]:
    """In-process bge-m3 + Memgraph fetch + Python cosine (cold-boot ~14s)."""
    from sentence_transformers import SentenceTransformer
    import mgclient

    model = SentenceTransformer(EMBED_MODEL, device="cpu")
    q_vec = model.encode([query], normalize_embeddings=True)[0].tolist()

    conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    cursor = conn.cursor()
    cursor.execute(
        "MATCH (c:Chunk) WHERE c.namespace = $ns RETURN c.file, c.chunk_idx, c.title, c.text, c.vector",
        {"ns": namespace},
    )
    rows = cursor.fetchall()
    conn.close()

    scored = []
    for file, idx, title, text, vec in rows:
        if vec is None:
            continue
        score = cosine(q_vec, vec)
        entry = {"file": file, "chunk_idx": idx, "title": title,
                 "snippet": text[:200], "score": score}
        if return_full_text:
            entry["_text"] = text or ""
        scored.append(entry)

    scored.sort(key=lambda r: r["score"], reverse=True)
    fetch_k = fetch_k_override if fetch_k_override is not None else top_k
    return scored[:fetch_k]


# ──────────────────────────────────────────────────────────────────────────────
# In-process cross-encoder reranker (for native + legacy paths)
# ──────────────────────────────────────────────────────────────────────────────
_RERANKER_CACHE: dict = {}


def _get_reranker(model_id: str | None = None):
    """Lazy-load + cache cross-encoders by HF id. Multi-model aware (A/B-bench)."""
    resolved = _resolve_reranker_model(model_id)
    models = _RERANKER_CACHE.setdefault("models", {})
    if resolved not in models:
        from sentence_transformers import CrossEncoder  # noqa: WPS433
        models[resolved] = CrossEncoder(
            resolved, device="cpu", max_length=RERANK_MAX_LENGTH,
        )
    return models[resolved]


def _rerank_in_process(query: str, candidates: list[dict], top_k: int,
                       model_id: str | None = None) -> list[dict]:
    """Score (query, doc.text) with cross-encoder; return top_k. In-place mutation.

    Each candidate must carry '_text' (full chunk). Sets 'cosine_score' to the
    original first-pass score and overwrites 'score' with the rerank value.
    model_id: alias or HF id; default RERANKER_MODEL.
    """
    if not candidates:
        return []
    import time as _t
    model = _get_reranker(model_id)
    pairs = [(query, c.get("_text") or c.get("snippet") or "") for c in candidates]
    t0 = _t.time()
    scores = model.predict(pairs, show_progress_bar=False,
                           batch_size=RERANK_BATCH_SIZE, convert_to_numpy=True)
    _RERANKER_CACHE["last_ms"] = round((_t.time() - t0) * 1000.0, 1)
    _RERANKER_CACHE["last_model"] = _resolve_reranker_model(model_id)
    for c, s in zip(candidates, scores):
        c["cosine_score"] = c["score"]
        c["score"] = float(s)
        c.pop("_text", None)
    candidates.sort(key=lambda r: r["score"], reverse=True)
    return candidates[:top_k]


# ──────────────────────────────────────────────────────────────────────────────
# Hybrid backend — BM25 (rank_bm25) + semantic with Reciprocal Rank Fusion
# ──────────────────────────────────────────────────────────────────────────────
_BM25_TOKEN_RE = re.compile(r"[a-z0-9]+")
_BM25_STOPWORDS = {
    "a", "az", "egy", "es", "is", "de", "ha", "nem", "csak", "vagy", "hogy",
    "mint", "meg", "fel", "be", "ki", "le", "el", "at", "ra", "re", "ban", "ben",
    "rol", "rel", "tol", "tel", "val", "vel", "nak", "nek",
    "ezt", "ezek", "ezekre", "ott", "itt", "most", "majd", "mar",
    "the", "an", "of", "to", "and", "or", "in", "on", "at", "for", "with",
    "are", "was", "were", "been", "being", "this", "that", "these",
    "those", "it", "its", "as", "by", "from", "if", "then", "else", "but",
}


def _bm25_tokenize(text: str) -> list[str]:
    """Mirror of vault-bm25-backfill tokenize (must match exactly for correct IDF lookup)."""
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text.lower())
        if not unicodedata.combining(c)
    )
    return [t for t in _BM25_TOKEN_RE.findall(text)
            if len(t) >= 2 and t not in _BM25_STOPWORDS]


def _load_bm25_index() -> dict | None:
    """Lazy-load + hydrate BM25Okapi from JSON. Cached in module-global."""
    if _BM25_CACHE.get("loaded"):
        return _BM25_CACHE.get("idx")
    _BM25_CACHE["loaded"] = True
    if not BM25_INDEX_PATH.exists():
        print(f"[hybrid] no BM25 index at {BM25_INDEX_PATH} — run vault-bm25-backfill",
              file=sys.stderr)
        _BM25_CACHE["idx"] = None
        return None
    try:
        with BM25_INDEX_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        from rank_bm25 import BM25Okapi  # noqa: WPS433
        # Re-hydrate without re-running __init__ (would recompute IDF over tokens).
        bm = BM25Okapi.__new__(BM25Okapi)
        s = data["bm25"]
        bm.k1 = s["k1"]
        bm.b = s["b"]
        bm.epsilon = s["epsilon"]
        bm.corpus_size = s["corpus_size"]
        bm.avgdl = s["avgdl"]
        bm.average_idf = s["average_idf"]
        bm.doc_freqs = s["doc_freqs"]
        bm.idf = s["idf"]
        bm.doc_len = s["doc_len"]
        bm.tokenizer = None
        data["_bm25_obj"] = bm
        _BM25_CACHE["idx"] = data
        return data
    except Exception as e:
        print(f"[hybrid] BM25 load failed: {e}", file=sys.stderr)
        _BM25_CACHE["idx"] = None
        return None


def _bm25_top_k(query: str, fetch_k: int, namespace: str) -> list[dict]:
    """Return [{ns, hash, file, chunk_idx, title, bm25_score, bm25_rank}, ...]."""
    data = _load_bm25_index()
    if data is None:
        return []
    bm = data["_bm25_obj"]
    keys = data["keys"]
    toks = _bm25_tokenize(query)
    if not toks:
        return []
    scores = bm.get_scores(toks)            # numpy array, len = corpus_size
    # Filter by namespace BEFORE sorting (cheap, keys are in-RAM).
    ns_filter = namespace or "content"
    filtered_idx = [i for i, k in enumerate(keys) if (k[0] or "content") == ns_filter]
    filtered_idx.sort(key=lambda i: scores[i], reverse=True)
    top = filtered_idx[:fetch_k]
    out = []
    for rank, i in enumerate(top):
        ns, h, file, idx, title = keys[i]
        s = float(scores[i])
        # Drop zero-score hits (no token-overlap)
        if s <= 0.0:
            break
        out.append({
            "namespace": ns or "content",
            "hash": h,
            "file": file,
            "chunk_idx": idx,
            "title": title,
            "bm25_score": s,
            "bm25_rank": rank + 1,
        })
    return out


def _rrf_fuse(bm25_hits: list[dict], sem_hits: list[dict],
              top_k: int, k_const: int = RRF_K) -> list[dict]:
    """Reciprocal Rank Fusion. Score = sum(1/(k_const + rank)) across rankers.

    Join key: (namespace, file, chunk_idx) — semantic hits don't carry hash but
    do carry these three. file+chunk_idx is unique within a namespace.
    """
    fused: dict[tuple, dict] = {}

    for h in bm25_hits:
        key = (h["namespace"], h["file"], h["chunk_idx"])
        entry = fused.setdefault(key, {
            "namespace": h["namespace"],
            "file": h["file"],
            "chunk_idx": h["chunk_idx"],
            "title": h.get("title"),
            "bm25_rank": None,
            "bm25_score": None,
            "semantic_rank": None,
            "semantic_score": None,
            "rrf_score": 0.0,
            "snippet": None,
        })
        entry["bm25_rank"] = h["bm25_rank"]
        entry["bm25_score"] = h["bm25_score"]
        entry["rrf_score"] += 1.0 / (k_const + h["bm25_rank"])

    for rank, h in enumerate(sem_hits, start=1):
        ns = h.get("namespace") or "content"
        key = (ns, h["file"], h["chunk_idx"])
        entry = fused.setdefault(key, {
            "namespace": ns,
            "file": h["file"],
            "chunk_idx": h["chunk_idx"],
            "title": h.get("title"),
            "bm25_rank": None,
            "bm25_score": None,
            "semantic_rank": None,
            "semantic_score": None,
            "rrf_score": 0.0,
            "snippet": None,
        })
        entry["semantic_rank"] = rank
        entry["semantic_score"] = h.get("score")
        entry["rrf_score"] += 1.0 / (k_const + rank)
        # Prefer the semantic snippet (it has the chunk text)
        if not entry.get("snippet"):
            entry["snippet"] = h.get("snippet")
        if not entry.get("title"):
            entry["title"] = h.get("title")

    fused_list = sorted(fused.values(), key=lambda r: r["rrf_score"], reverse=True)
    # Output shape mirrors normal hits (so downstream renderers work).
    out = []
    for r in fused_list[:top_k]:
        out.append({
            "file": r["file"],
            "chunk_idx": r["chunk_idx"],
            "title": r["title"],
            "snippet": (r.get("snippet") or "")[:200],
            "score": r["rrf_score"],
            "bm25_rank": r["bm25_rank"],
            "bm25_score": (round(r["bm25_score"], 4)
                           if r["bm25_score"] is not None else None),
            "semantic_rank": r["semantic_rank"],
            "semantic_score": (round(r["semantic_score"], 4)
                               if r["semantic_score"] is not None else None),
            "rrf_score": round(r["rrf_score"], 6),
        })
    return out


def _hybrid_search(query: str, top_k: int, namespace: str,
                   fetch_k: int = HYBRID_FETCH_K,
                   k_const: int = RRF_K) -> dict:
    """Parallel-ish BM25 + semantic, fused by RRF. Returns a search-response dict."""
    import time as _t

    t0 = _t.time()
    bm25_hits = _bm25_top_k(query, fetch_k, namespace)
    bm25_ms = round((_t.time() - t0) * 1000.0, 1)

    t0 = _t.time()
    # Reuse the native backend for the semantic side (sub-ms when daemon is warm).
    sem_hits = _native_search(query, fetch_k, namespace,
                              return_full_text=False,
                              fetch_k_override=fetch_k) or []
    sem_ms = round((_t.time() - t0) * 1000.0, 1)

    if not sem_hits:
        # Native dead — fall back to daemon for the semantic side
        resp = _try_socket_search(query, fetch_k, namespace, rerank=False,
                                  smart_rerank=False)
        if resp is not None:
            sem_hits = resp.get("results", [])

    t0 = _t.time()
    fused = _rrf_fuse(bm25_hits, sem_hits, top_k, k_const=k_const)
    fuse_ms = round((_t.time() - t0) * 1000.0, 1)

    return {
        "results": fused,
        "namespace": namespace,
        "query": query,
        "mode": "hybrid-rrf",
        "backend": "hybrid",
        "bm25_hits": len(bm25_hits),
        "semantic_hits": len(sem_hits),
        "fetch_k": fetch_k,
        "rrf_k": k_const,
        "bm25_ms": bm25_ms,
        "semantic_ms": sem_ms,
        "fuse_ms": fuse_ms,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────────────────────────────────────
def _wrap_cosine_result(results: list[dict], query: str, namespace: str,
                        backend: str) -> dict:
    return {"results": results, "namespace": namespace, "query": query,
            "mode": "cosine", "backend": backend}


def _apply_smart_rerank_local(candidates: list[dict], query: str, top_k: int,
                              trigger_threshold: float,
                              backend_label: str, first_pass_k: int,
                              score_gap_threshold: float = 0.0,
                              reranker_model: str | None = None) -> dict:
    """Smart-rerank wrapper for native/legacy paths (cross-encoder runs in-process).

    candidates: full first-pass list (with _text). Sorted by cosine desc.
    Combined gate (Week 5):
        (a) absolute confidence:  top-1 cos >= trigger_threshold     → SKIP
        (b) score-gap (>0 only):  top1 - top2 > score_gap_threshold  → SKIP
        else                                                          → RERANK
    Setting score_gap_threshold=0.0 disables (b) → legacy behaviour.
    reranker_model: alias or HF id propagated to in-process rerank.
    """
    max_cos = candidates[0]["score"] if candidates else 0.0
    if len(candidates) >= 2:
        score_gap = max_cos - candidates[1]["score"]
    else:
        score_gap = float("inf")
    skip_reason = None
    should_rerank = True
    if max_cos >= trigger_threshold:
        should_rerank = False
        skip_reason = "confident"
    elif score_gap_threshold > 0.0 and score_gap > score_gap_threshold:
        should_rerank = False
        skip_reason = "score-gap"
    gap_out = round(score_gap, 4) if score_gap != float("inf") else None
    if should_rerank:
        # Trigger rerank
        reranked = _rerank_in_process(query, candidates, top_k,
                                      model_id=reranker_model)
        return {"results": reranked, "namespace": "content", "query": query,
                "mode": "smart-rerank-triggered", "backend": backend_label,
                "first_pass_k": first_pass_k,
                "first_pass_max_score": round(max_cos, 4),
                "first_pass_score_gap": gap_out,
                "rerank_triggered": True,
                "trigger_threshold": trigger_threshold,
                "score_gap_threshold": score_gap_threshold,
                "rerank_ms": _RERANKER_CACHE.get("last_ms"),
                "reranker_model": _resolve_reranker_model(reranker_model)}
    # Skip rerank
    skipped = []
    for c in candidates[:top_k]:
        c.pop("_text", None)
        skipped.append(c)
    return {"results": skipped, "namespace": "content", "query": query,
            "mode": "smart-rerank-skipped", "skip_reason": skip_reason,
            "backend": backend_label,
            "first_pass_k": first_pass_k,
            "first_pass_max_score": round(max_cos, 4),
            "first_pass_score_gap": gap_out,
            "rerank_triggered": False,
            "trigger_threshold": trigger_threshold,
            "score_gap_threshold": score_gap_threshold,
            "rerank_ms": 0.0,
            "reranker_model": _resolve_reranker_model(reranker_model)}


def search(query: str, top_k: int = 5, namespace: str = "content",
           use_socket: bool = True, backend: str = "auto",
           rerank: bool = False, smart_rerank: bool = False,
           trigger_threshold: float | None = None,
           score_gap_threshold: float | None = None,
           reranker_model: str | None = None) -> dict:
    """Backend dispatcher.

    backend:
        "native"  — Memgraph vector_search.search (sub-ms after encode).
        "numpy"   — daemon socket (warm bge-m3 + numpy cosine).
        "auto"    — native → daemon → legacy.
    use_socket=False:
        forces legacy in-process path (skip both native and daemon).
    rerank:
        If True, always-rerank two-pass mode (first-pass cosine top-N → CE → top-K).
    smart_rerank:
        If True (and not rerank), auto-trigger rerank only when first-pass
        max_cos < trigger_threshold. This is the new DEFAULT for interactive use:
        fast (~131ms) when cosine is confident, slower (~13s) only when needed.

    Returns a full response dict (compat shape):
        {"results": [...], "namespace", "query",
         "mode": "cosine"|"reranked"|"smart-rerank-triggered"|"smart-rerank-skipped",
         "backend": "native"|"numpy"|"legacy",
         "first_pass_k"?, "rerank_ms"?, "first_pass_max_score"?, "rerank_triggered"?}
    """
    if trigger_threshold is None:
        trigger_threshold = RERANK_TRIGGER_THRESHOLD
    need_first_pass = rerank or smart_rerank
    first_pass_k = (min(top_k * RERANK_OVERSAMPLE, RERANK_MAX_CANDIDATES)
                    if need_first_pass else top_k)

    if not use_socket:
        results = _legacy_search(query, top_k, namespace,
                                 return_full_text=need_first_pass,
                                 fetch_k_override=first_pass_k if need_first_pass else None)
        if rerank:
            reranked = _rerank_in_process(query, results, top_k,
                                          model_id=reranker_model)
            return {"results": reranked, "namespace": namespace, "query": query,
                    "mode": "reranked", "backend": "legacy",
                    "first_pass_k": first_pass_k,
                    "rerank_ms": _RERANKER_CACHE.get("last_ms"),
                    "reranker_model": _resolve_reranker_model(reranker_model)}
        if smart_rerank:
            resp = _apply_smart_rerank_local(
                results, query, top_k, trigger_threshold, "legacy", first_pass_k,
                score_gap_threshold=(score_gap_threshold
                                     if score_gap_threshold is not None
                                     else RERANK_SCORE_GAP_THRESHOLD),
                reranker_model=reranker_model)
            resp["namespace"] = namespace
            return resp
        return _wrap_cosine_result(results, query, namespace, "legacy")

    # Effective gap (used for in-process smart-rerank wrappers below).
    eff_gap = (score_gap_threshold
               if score_gap_threshold is not None
               else RERANK_SCORE_GAP_THRESHOLD)

    if backend == "native":
        r = _native_search(query, top_k, namespace,
                           return_full_text=need_first_pass,
                           fetch_k_override=first_pass_k if need_first_pass else None)
        if r is None:
            print("[backend=native] failed, falling back to daemon", file=sys.stderr)
            resp = _try_socket_search(query, top_k, namespace, rerank=rerank,
                                      smart_rerank=smart_rerank,
                                      trigger_threshold=trigger_threshold,
                                      score_gap_threshold=score_gap_threshold,
                                      reranker_model=reranker_model)
            if resp is not None:
                resp["backend"] = "numpy"
                return resp
            # final fallback: legacy
            return search(query, top_k, namespace, use_socket=False,
                          backend="auto", rerank=rerank,
                          smart_rerank=smart_rerank,
                          trigger_threshold=trigger_threshold,
                          score_gap_threshold=score_gap_threshold,
                          reranker_model=reranker_model)
        if rerank:
            reranked = _rerank_in_process(query, r, top_k,
                                          model_id=reranker_model)
            return {"results": reranked, "namespace": namespace, "query": query,
                    "mode": "reranked", "backend": "native",
                    "first_pass_k": first_pass_k,
                    "rerank_ms": _RERANKER_CACHE.get("last_ms"),
                    "reranker_model": _resolve_reranker_model(reranker_model)}
        if smart_rerank:
            resp = _apply_smart_rerank_local(
                r, query, top_k, trigger_threshold, "native", first_pass_k,
                score_gap_threshold=eff_gap,
                reranker_model=reranker_model)
            resp["namespace"] = namespace
            return resp
        return _wrap_cosine_result(r[:top_k], query, namespace, "native")

    if backend == "numpy":
        resp = _try_socket_search(query, top_k, namespace, rerank=rerank,
                                  smart_rerank=smart_rerank,
                                  trigger_threshold=trigger_threshold,
                                  score_gap_threshold=score_gap_threshold,
                                  reranker_model=reranker_model)
        if resp is None:
            return search(query, top_k, namespace, use_socket=False,
                          backend="auto", rerank=rerank,
                          smart_rerank=smart_rerank,
                          trigger_threshold=trigger_threshold,
                          score_gap_threshold=score_gap_threshold,
                          reranker_model=reranker_model)
        resp["backend"] = "numpy"
        return resp

    # auto
    r = _native_search(query, top_k, namespace,
                       return_full_text=need_first_pass,
                       fetch_k_override=first_pass_k if need_first_pass else None)
    if r is not None:
        if rerank:
            reranked = _rerank_in_process(query, r, top_k,
                                          model_id=reranker_model)
            return {"results": reranked, "namespace": namespace, "query": query,
                    "mode": "reranked", "backend": "native",
                    "first_pass_k": first_pass_k,
                    "rerank_ms": _RERANKER_CACHE.get("last_ms"),
                    "reranker_model": _resolve_reranker_model(reranker_model)}
        if smart_rerank:
            resp = _apply_smart_rerank_local(
                r, query, top_k, trigger_threshold, "native", first_pass_k,
                score_gap_threshold=eff_gap,
                reranker_model=reranker_model)
            resp["namespace"] = namespace
            return resp
        return _wrap_cosine_result(r[:top_k], query, namespace, "native")

    resp = _try_socket_search(query, top_k, namespace, rerank=rerank,
                              smart_rerank=smart_rerank,
                              trigger_threshold=trigger_threshold,
                              score_gap_threshold=score_gap_threshold,
                              reranker_model=reranker_model)
    if resp is not None:
        resp["backend"] = "numpy"
        return resp

    # Final fallback: legacy in-process
    return search(query, top_k, namespace, use_socket=False,
                  backend="auto", rerank=rerank,
                  smart_rerank=smart_rerank,
                  trigger_threshold=trigger_threshold,
                  score_gap_threshold=score_gap_threshold,
                  reranker_model=reranker_model)


def main():
    ap = argparse.ArgumentParser(description="Vault search (B-2)")
    ap.add_argument("query", nargs="?", help="Free-text query")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--namespace", default="content")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-socket", action="store_true",
                    help="Skip daemon/native, use legacy in-process path")
    ap.add_argument("--backend", default=SEARCH_BACKEND_DEFAULT,
                    choices=["native", "numpy", "auto"],
                    help="Search backend (default auto: native→numpy→legacy)")
    ap.add_argument("--rerank", action="store_true",
                    help="Force 2-pass retrieval: dense top-N → bge-reranker-v2-m3 → top-K")
    ap.add_argument("--smart-rerank", action="store_true",
                    help="Auto-rerank only if first-pass max_cos < trigger_threshold")
    ap.add_argument("--mode",
                    choices=["cosine", "cosine-only", "reranked", "hybrid",
                             "auto-rerank", "smart-rerank"],
                    default="auto-rerank",
                    help="cosine|cosine-only — single-pass dense; "
                         "reranked|hybrid — always 2-pass; "
                         "auto-rerank|smart-rerank (DEFAULT) — rerank only "
                         "if cosine max_score<trigger_threshold")
    ap.add_argument("--trigger-threshold", type=float, default=None,
                    help=f"Smart-rerank trigger threshold "
                         f"(default {RERANK_TRIGGER_THRESHOLD} via env "
                         f"RERANK_TRIGGER_THRESHOLD)")
    ap.add_argument("--score-gap-threshold", type=float, default=None,
                    help=f"Smart-rerank score-gap skip threshold (Week 5). "
                         f"If top1_cos - top2_cos > gap, SKIP rerank even when "
                         f"max_cos < trigger_threshold (clear winner). "
                         f"Default {RERANK_SCORE_GAP_THRESHOLD} (env "
                         f"RERANK_SCORE_GAP_THRESHOLD). 0.0 disables (= legacy).")
    ap.add_argument("--hybrid", action="store_true",
                    help="B-2 Week 4: fuse BM25 lexical + semantic with RRF "
                         "(requires `vault-bm25-backfill` index). DEFAULT OFF.")
    ap.add_argument("--hybrid-fetch-k", type=int, default=HYBRID_FETCH_K,
                    help=f"Per-side top-N before RRF fusion (default {HYBRID_FETCH_K}, "
                         f"env VAULT_HYBRID_FETCH_K)")
    ap.add_argument("--rrf-k", type=int, default=RRF_K,
                    help=f"RRF k constant — score = sum(1/(k+rank)). "
                         f"Default {RRF_K} (env VAULT_RRF_K). Lower = top ranks dominate.")
    ap.add_argument("--reranker-model", default=None,
                    help="Cross-encoder model: 'v2-m3' (568MB, default), "
                         "'base' (277MB, faster), 'auto' (= daemon default), "
                         "or a full HF id (e.g. BAAI/bge-reranker-large). "
                         "Added 2026-05-17 Week 4 for A/B benchmarking.")
    args = ap.parse_args()

    if not args.query:
        ap.print_help()
        sys.exit(1)

    # NOTE: --mode hybrid was a pre-Week-4 alias for "always rerank" (kept for
    # backward-compat). The new BM25+semantic fusion is gated on --hybrid (flag),
    # NOT on --mode hybrid, to avoid breaking older callers.
    rerank = args.rerank or (args.mode in ("reranked", "hybrid"))
    smart_rerank = (not rerank) and (args.smart_rerank
                                     or args.mode in ("auto-rerank", "smart-rerank"))

    if args.hybrid:
        resp = _hybrid_search(args.query, args.top_k, args.namespace,
                              fetch_k=args.hybrid_fetch_k, k_const=args.rrf_k)
    else:
        resp = search(
            args.query, args.top_k, args.namespace,
            use_socket=not args.no_socket, backend=args.backend,
            rerank=rerank, smart_rerank=smart_rerank,
            trigger_threshold=args.trigger_threshold,
            score_gap_threshold=args.score_gap_threshold,
            reranker_model=args.reranker_model,
        )
    results = resp.get("results", [])

    if args.json:
        print(json.dumps(resp, ensure_ascii=False, indent=2))
    elif results:
        mode_tag = resp.get("mode", "cosine")
        backend_tag = resp.get("backend", args.backend)
        extra = ""
        if mode_tag in ("reranked", "smart-rerank-triggered"):
            rm = resp.get("reranker_model", "")
            rm_short = rm.split("/")[-1] if rm else ""
            gap = resp.get("first_pass_score_gap")
            gap_part = f", gap={gap}" if gap is not None else ""
            extra = (f" — first-pass={resp.get('first_pass_k')}, "
                     f"rerank={resp.get('rerank_ms')}ms, "
                     f"first_max_cos={resp.get('first_pass_max_score')}{gap_part}"
                     f"{', model=' + rm_short if rm_short else ''}")
        elif mode_tag == "smart-rerank-skipped":
            reason = resp.get("skip_reason") or "confident"
            gap = resp.get("first_pass_score_gap")
            gap_part = f", gap={gap}" if gap is not None else ""
            extra = (f" — first_max_cos={resp.get('first_pass_max_score')}"
                     f"{gap_part} (rerank skipped: {reason})")
        elif mode_tag == "hybrid-rrf":
            extra = (f" — bm25={resp.get('bm25_hits')}({resp.get('bm25_ms')}ms) "
                     f"semantic={resp.get('semantic_hits')}({resp.get('semantic_ms')}ms) "
                     f"fuse={resp.get('fuse_ms')}ms k={resp.get('rrf_k')}")
        print(f"Top-{len(results)} ({args.namespace} ns, backend={backend_tag}, "
              f"mode={mode_tag}){extra}:")
        for r in results:
            cos = r.get("cosine_score")
            cos_str = f" cos={cos:.3f}" if cos is not None else ""
            extra_rk = ""
            if r.get("bm25_rank") is not None or r.get("semantic_rank") is not None:
                br = r.get("bm25_rank") or "-"
                sr = r.get("semantic_rank") or "-"
                extra_rk = f" bm25={br} sem={sr}"
            print(f"  [{r['score']:.4f}{cos_str}{extra_rk}] {r['file']} #{r['chunk_idx']} — {r['title']}")
            print(f"          {(r.get('snippet') or '')[:120]}...")
    else:
        print(f"No chunks in namespace='{args.namespace}'. Run `vault-embed --backfill` first.")


if __name__ == "__main__":
    main()

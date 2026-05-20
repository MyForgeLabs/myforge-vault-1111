#!/root/.notebooklm-venv/bin/python3
"""vault-explain — retrieval introspection CLI.

Runs the full vault-search pipeline and emits a *human-readable trace*
explaining why each top-K chunk ranks where it does: cosine score, query-token
overlap, KO-DB cross-source corroboration count, and Memgraph entity-neighbour
context. Also emits a Mermaid `flowchart LR` visualizing the trace.

Brainstorm-idea #2 from
  06-Audits/2026-05-19 SV new development ideas brainstorm.md

Design:
  - Delegates the actual search to the vault-search-server daemon
    (/run/vault-search.sock) — never re-implements bge-m3 / vector_search.
  - Reads KO-DB read-only (mode=ro URI). 13.8K facts.
  - Reads Memgraph read-only (no CREATE/MERGE/SET/DELETE).
  - Graceful fallback: any of {daemon, KO-DB, Memgraph} down → skip that
    trace-dimension, print a one-line warning, continue.

Usage:
    vault-explain "<query>" [--top-k N] [--json | --markdown] [--no-graph]
                  [--namespace content|skills]

Examples:
    vault-explain "Glicko XP achievement" --top-k 3
    vault-explain "Memgraph keepalive" --top-k 3 --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
KO_DB = Path(os.environ.get("VAULT_KO_DB", str(VAULT_ROOT / ".vault-ko" / "facts.db")))
SEARCH_SOCKET = os.environ.get("VAULT_SEARCH_SOCKET", "/run/vault-search.sock")
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))

# Daemon may legitimately take ~10s when smart-rerank triggers a cold cross-
# encoder load. 30s is comfortable margin; lower to 5s if you want fail-fast.
DAEMON_TIMEOUT = float(os.environ.get("VAULT_EXPLAIN_DAEMON_TIMEOUT", "30.0"))
MEMGRAPH_TIMEOUT = float(os.environ.get("VAULT_EXPLAIN_MG_TIMEOUT", "2.0"))

CYPHER_MUTATION = re.compile(
    r"\b(CREATE|MERGE|DELETE|SET|REMOVE|DROP|DETACH)\b", re.IGNORECASE,
)


# ── Token helper (mirrors vault-bm25-backfill so overlap ≈ what BM25 sees) ──

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "az", "egy", "es", "is", "de", "ha", "nem", "csak", "vagy", "hogy",
    "mint", "meg", "fel", "be", "ki", "le", "el", "at", "ra", "re", "ban",
    "ben", "rol", "rel", "tol", "tel", "val", "vel", "nak", "nek",
    "the", "an", "of", "to", "and", "or", "in", "on", "for", "with",
    "are", "was", "were", "been", "being", "this", "that", "these", "those",
    "it", "its", "as", "by", "from", "if", "then", "else", "but",
}


def tokenize(text: str) -> list[str]:
    """ASCII-fold + lowercase + stopword-strip. Matches vault-bm25-backfill."""
    if not text:
        return []
    folded = "".join(
        c for c in unicodedata.normalize("NFKD", text.lower())
        if not unicodedata.combining(c)
    )
    return [t for t in _TOKEN_RE.findall(folded)
            if len(t) >= 2 and t not in _STOPWORDS]


# ── Daemon RPC (search + health) ────────────────────────────────────────────


def daemon_rpc(payload: dict, timeout: float = DAEMON_TIMEOUT) -> dict | None:
    """One-shot JSON-over-unix-socket. Returns None if daemon unreachable."""
    if not os.path.exists(SEARCH_SOCKET):
        return None
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(SEARCH_SOCKET)
        sock.sendall((json.dumps(payload) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf += chunk
            if len(buf) > 8 * 1024 * 1024:
                break
        sock.close()
        return json.loads(buf.split(b"\n", 1)[0].decode())
    except (socket.timeout, OSError, json.JSONDecodeError) as e:
        print(f"[daemon] {type(e).__name__}: {e}", file=sys.stderr)
        return None


def daemon_search(query: str, top_k: int, namespace: str) -> dict | None:
    """Smart-rerank search. Returns daemon response or None on failure."""
    method = "search_skills" if namespace == "skills" else "search"
    payload = {
        "method": method,
        "query": query,
        "top_k": top_k,
    }
    if method == "search":
        payload["namespace"] = namespace
        payload["smart_rerank"] = True
    return daemon_rpc(payload, timeout=DAEMON_TIMEOUT)


# ── KO-DB helpers (read-only) ───────────────────────────────────────────────


def ko_connect() -> sqlite3.Connection | None:
    if not KO_DB.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{KO_DB}?mode=ro", uri=True, timeout=2.0)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"[ko-db] connect failed: {e}", file=sys.stderr)
        return None


def ko_corroboration_for_subject(conn: sqlite3.Connection, subject_token: str,
                                 limit: int = 3) -> dict:
    """Return {source_count, fact_count, facts: [...]} for a subject-substring.

    Mirrors tool_ko_top_k from .vault-mcp/vault_mcp_server.py — picks the
    single best-matching subject (most distinct sources) and pulls top-N facts.
    """
    if not subject_token:
        return {"source_count": 0, "fact_count": 0, "facts": []}
    cur = conn.cursor()
    # Schema-detect: post-#34 (2026-05-19) drops facts.provenance.
    cols = {r[1] for r in conn.execute("PRAGMA table_info(facts)").fetchall()}
    has_pv = bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fact_provenance'"
    ).fetchone())
    post34 = "provenance" not in cols and has_pv
    if post34:
        row = cur.execute(
            """
            SELECT f.subject,
                   MAX(f.provenance_count) AS source_count,
                   COUNT(*)                AS fact_count
            FROM facts f
            WHERE f.subject LIKE ? OR f.object LIKE ?
            GROUP BY f.subject
            ORDER BY source_count DESC, fact_count DESC
            LIMIT 1
            """,
            (f"%{subject_token}%", f"%{subject_token}%"),
        ).fetchone()
    else:
        row = cur.execute(
            """
            SELECT subject,
                   COUNT(DISTINCT provenance) AS source_count,
                   COUNT(*)                   AS fact_count
            FROM facts
            WHERE subject LIKE ? OR object LIKE ?
            GROUP BY subject
            ORDER BY source_count DESC, fact_count DESC
            LIMIT 1
            """,
            (f"%{subject_token}%", f"%{subject_token}%"),
        ).fetchone()
    if not row:
        return {"source_count": 0, "fact_count": 0, "facts": [], "subject": None}
    subj = row["subject"]
    if post34:
        facts = cur.execute(
            """
            SELECT f.predicate, f.object,
                   COALESCE(GROUP_CONCAT(fp.provenance, '||'), '') AS provenance,
                   f.source_type, f.confidence
            FROM facts f
            LEFT JOIN fact_provenance fp ON fp.fact_hash = f.hash
            WHERE f.subject = ?
            GROUP BY f.id
            ORDER BY f.confidence DESC LIMIT ?
            """,
            (subj, limit),
        ).fetchall()
    else:
        facts = cur.execute(
            """
            SELECT predicate, object, provenance, source_type, confidence
            FROM facts WHERE subject = ?
            ORDER BY confidence DESC LIMIT ?
            """,
            (subj, limit),
        ).fetchall()
    return {
        "subject": subj,
        "source_count": row["source_count"],
        "fact_count": row["fact_count"],
        "facts": [dict(f) for f in facts],
    }


# ── Memgraph helpers (read-only) ────────────────────────────────────────────


def mg_connect():
    try:
        import mgclient
    except ImportError:
        return None
    try:
        conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
        return conn
    except Exception as e:
        print(f"[memgraph] connect failed: {e}", file=sys.stderr)
        return None


def mg_query(conn, cypher: str, params: dict | None = None,
             timeout: float = MEMGRAPH_TIMEOUT) -> list | None:
    """Read-only Cypher with mutation-keyword guard. Returns rows or None."""
    if CYPHER_MUTATION.search(cypher):
        return None
    try:
        cur = conn.cursor()
        cur.execute(cypher, params or {})
        return cur.fetchall()
    except Exception as e:
        print(f"[memgraph] query failed: {type(e).__name__}: {e}",
              file=sys.stderr)
        return None


def mg_detect_entities(conn, query: str, max_entities: int = 5) -> list[dict]:
    """Best-effort entity detection: for each significant query token, look up
    Entity nodes whose name CONTAINS the token (case-insensitive)."""
    out: list[dict] = []
    seen: set[str] = set()
    tokens = [t for t in tokenize(query) if len(t) >= 4][:6]
    for tok in tokens:
        rows = mg_query(
            conn,
            "MATCH (e:Entity) WHERE toLower(e.name) CONTAINS $t "
            "RETURN e.name AS name, labels(e) AS labels, "
            "e.source_count AS source_count LIMIT 3",
            {"t": tok},
        ) or []
        for name, labels, source_count in rows:
            if not name or name in seen:
                continue
            seen.add(name)
            out.append({
                "name": name,
                "labels": [l for l in labels if l != "Entity"],
                "source_count": source_count or 0,
                "matched_token": tok,
            })
            if len(out) >= max_entities:
                return out
    return out


def mg_entity_neighbourhood(conn, entity_name: str) -> dict:
    """Inbound/outbound edge counts for a named entity."""
    rows = mg_query(
        conn,
        "MATCH (e:Entity {name: $n}) "
        "OPTIONAL MATCH (e)-[ro]->() "
        "OPTIONAL MATCH ()-[ri]->(e) "
        "RETURN count(DISTINCT ro) AS outb, count(DISTINCT ri) AS inb",
        {"n": entity_name},
    )
    if not rows:
        return {"outbound": 0, "inbound": 0}
    outb, inb = rows[0]
    return {"outbound": int(outb or 0), "inbound": int(inb or 0)}


def mg_chunk_links(conn, file_path: str) -> list[str]:
    """Files this chunk's WikiFile links to (via :LINKS_TO)."""
    rows = mg_query(
        conn,
        "MATCH (w:WikiFile {path: $p})-[:LINKS_TO]->(t:WikiFile) "
        "RETURN t.path AS path LIMIT 8",
        {"p": file_path},
    ) or []
    return [r[0] for r in rows if r[0]]


# ── Per-result trace assembly ───────────────────────────────────────────────


def build_trace_for_result(r: dict, query_tokens: set[str],
                           ko_conn, mg_conn,
                           detected_entities: list[dict]) -> dict:
    """Compute the 4 trace dimensions for one search result."""
    # 1. Cosine — daemon delivers either 'cosine_score' (rerank path) or 'score'.
    cosine = r.get("cosine_score")
    if cosine is None:
        cosine = r.get("score")
    cosine = float(cosine) if cosine is not None else None

    # 2. Token overlap (query ∩ title+snippet).
    chunk_blob = " ".join(filter(None, [r.get("title"), r.get("snippet")]))
    chunk_tokens = set(tokenize(chunk_blob))
    overlap = sorted(query_tokens & chunk_tokens)
    overlap_count = len(overlap)
    overlap_frac = (overlap_count / max(1, len(query_tokens)))

    # 3. KO-DB corroboration — uses title as best-guess subject (cheap heuristic).
    ko_signal = {"source_count": 0, "fact_count": 0, "facts": [],
                 "subject": None}
    if ko_conn is not None and r.get("title"):
        # Stem-ish: try the title as-is, then drop anything past first hyphen.
        title = r["title"]
        for candidate in [title, title.split("—")[0].strip(),
                          title.split("-")[0].strip()]:
            if not candidate or len(candidate) < 4:
                continue
            sig = ko_corroboration_for_subject(ko_conn, candidate, limit=3)
            if sig["source_count"] > 0:
                ko_signal = sig
                break

    # 4. Entity neighbours — does this chunk's file link out to a detected entity?
    #    (Fast heuristic: list this WikiFile's :LINKS_TO neighbours, intersect
    #    names. Best-effort.)
    entity_neighbours: list[str] = []
    if mg_conn is not None and r.get("file"):
        try:
            neighbour_paths = mg_chunk_links(mg_conn, r["file"])
            ents = {e["name"].lower() for e in detected_entities}
            for p in neighbour_paths:
                stem = Path(p).stem.lower()
                if any(e in stem or stem in e for e in ents):
                    entity_neighbours.append(p)
        except Exception:
            pass

    return {
        "cosine": round(cosine, 4) if cosine is not None else None,
        "token_overlap": {
            "count": overlap_count,
            "total_query_tokens": len(query_tokens),
            "fraction": round(overlap_frac, 3),
            "matched": overlap,
        },
        "ko_corroboration_count": ko_signal["source_count"],
        "ko_subject": ko_signal["subject"],
        "ko_facts": ko_signal["facts"],
        "entity_neighbours": entity_neighbours,
    }


# ── Mermaid renderer ────────────────────────────────────────────────────────


def _mermaid_id(prefix: str, n: int) -> str:
    return f"{prefix}{n}"


def render_mermaid(query: str, results: list[dict], traces: list[dict],
                   entity_trace: dict) -> str:
    """flowchart LR — query → bge-m3 → top-K chunks (+ KO/entity dotted edges)."""
    safe_query = query.replace('"', "'")[:60]
    lines = ["```mermaid", "flowchart LR",
             f'    Q["{safe_query}"] -->|encode| BGE["bge-m3 vector"]']
    for i, (r, tr) in enumerate(zip(results, traces), start=1):
        cid = _mermaid_id("C", i)
        cos = tr.get("cosine")
        cos_label = f"cosine {cos:.2f}" if cos is not None else "ranked"
        title = (r.get("title") or "(no title)")[:32].replace('"', "'")
        lines.append(f'    BGE -->|{cos_label}| {cid}["{title}"]')
        if tr.get("ko_corroboration_count", 0) > 0:
            kid = _mermaid_id("K", i)
            lines.append(
                f'    {cid} -.{tr["ko_corroboration_count"]} src.-> '
                f'{kid}[("KO-DB facts")]'
            )
        for j, nb in enumerate((tr.get("entity_neighbours") or [])[:2]):
            nbid = f"N{i}_{j}"
            nb_label = Path(nb).stem[:24].replace('"', "'")
            lines.append(f'    {cid} -->|:LINKS_TO| {nbid}(["{nb_label}"])')
    for j, ent in enumerate((entity_trace.get("detected_entities") or [])[:3]):
        eid = f"E{j}"
        ename = ent["name"][:28].replace('"', "'")
        lines.append(f'    Q -.detect.-> {eid}(["{ename}"])')
    lines.append("```")
    return "\n".join(lines)


# ── Markdown renderer ───────────────────────────────────────────────────────


def render_markdown(report: dict) -> str:
    q = report["query"]
    out: list[str] = [f'# Explain trace — "{q}"', ""]

    # Timing
    timing = report["timing_ms"]
    out.append("## Search pipeline timing")
    out.append(f"- daemon RPC:       {timing.get('daemon_rpc_ms', '—')} ms")
    out.append(f"- KO-DB trace:      {timing.get('ko_trace_ms', '—')} ms")
    out.append(f"- Memgraph trace:   {timing.get('memgraph_trace_ms', '—')} ms")
    out.append(f"- total:            {timing.get('total_ms', '—')} ms")
    mode = report.get("mode")
    backend = report.get("backend")
    if mode or backend:
        out.append(f"- mode/backend:     `{mode}` / `{backend}`")
    if report.get("first_pass_max_score") is not None:
        out.append(f"- first-pass max cosine: {report['first_pass_max_score']}")
    if report.get("skip_reason"):
        out.append(f"- rerank skipped:   {report['skip_reason']}")
    out.append("")

    results = report["results"]
    if not results:
        out.append("## Top-K results")
        out.append("")
        out.append("> _no results above threshold — daemon returned an empty"
                   " list. Try a different query, increase `--top-k`, or check"
                   " `vault-search` health._")
        out.append("")
    else:
        out.append("## Top-K results (with trace)")
        out.append("")
        for i, r in enumerate(results, start=1):
            tr = r["trace"]
            score = r.get("score")
            score_str = f"{score:.4f}" if score is not None else "—"
            out.append(f"### {i}. `{r.get('file', '?')}` (score {score_str})")
            snippet = (r.get("snippet") or "").strip().replace("\n", " ")
            if snippet:
                out.append(f"> {snippet[:200]}…")
            out.append("")
            out.append("**Why this ranked here:**")
            cos = tr.get("cosine")
            cos_str = f"{cos:.4f}" if cos is not None else "—"
            out.append(f"- cosine similarity {cos_str}")
            tov = tr["token_overlap"]
            if tov["count"]:
                matched = ", ".join(f'"{t}"' for t in tov["matched"][:6])
                out.append(
                    f"- token overlap with query: "
                    f"{tov['count']}/{tov['total_query_tokens']} ({matched})"
                )
            else:
                out.append("- token overlap with query: 0 (semantic-only hit)")
            if tr["ko_corroboration_count"]:
                out.append(
                    f"- KO-DB: {tr['ko_corroboration_count']} distinct source"
                    f"(s) mention subject `{tr['ko_subject']}`"
                )
            else:
                out.append("- KO-DB: no corroborating facts on this subject")
            if tr["entity_neighbours"]:
                out.append(
                    f"- entity-graph: linked to {len(tr['entity_neighbours'])}"
                    f" wiki neighbour(s) overlapping detected entities"
                )
            out.append("")
            if tr["ko_facts"]:
                out.append("**KO-DB corroboration (top facts):**")
                out.append("")
                out.append("| predicate | object | source | confidence |")
                out.append("|---|---|---|---|")
                for f in tr["ko_facts"]:
                    prov = (f.get("provenance") or "")[:40]
                    obj = (f.get("object") or "")[:40].replace("|", "\\|")
                    out.append(
                        f"| {f.get('predicate', '')} "
                        f"| {obj} "
                        f"| {prov} "
                        f"| {f.get('confidence', 0):.2f} |"
                    )
                out.append("")

    # Entity trace
    et = report["entity_trace"]
    out.append("## Entity-graph trace (Memgraph)")
    out.append("")
    if et.get("unavailable"):
        out.append(f"> ⚠ Memgraph unreachable — entity trace skipped "
                   f"({et['unavailable']})")
    else:
        detected = et.get("detected_entities") or []
        if not detected:
            out.append(f'Query `{q}` → no Entity nodes matched query tokens.')
        else:
            out.append(f'Query `{q}` → detected entities:')
            for e in detected:
                labels = ", ".join(e["labels"]) or "Entity"
                nb = e.get("neighbourhood", {})
                out.append(
                    f"- **{e['name']}** ({labels}) — "
                    f"{nb.get('inbound', 0)} inbound / "
                    f"{nb.get('outbound', 0)} outbound edges "
                    f"(matched token `{e['matched_token']}`)"
                )
    out.append("")

    # Mermaid
    if report.get("mermaid"):
        out.append("## Mermaid diagram")
        out.append("")
        out.append(report["mermaid"])
        out.append("")

    # Verdict
    v = report["verdict"]
    out.append("## Verdict")
    out.append(f"- **Top-result confidence**: {v['confidence']}")
    for note in v["notes"]:
        out.append(f"- {note}")
    out.append("")

    return "\n".join(out)


# ── Verdict heuristic ───────────────────────────────────────────────────────


def compute_verdict(results: list[dict], traces: list[dict]) -> dict:
    notes: list[str] = []
    if not results:
        return {"confidence": "none",
                "notes": ["no results — query may be off-vocabulary"]}
    top_tr = traces[0]
    signals = 0
    if (top_tr.get("cosine") or 0) >= 0.6:
        signals += 1
        notes.append("cosine ≥ 0.6 — strong semantic match")
    if top_tr["token_overlap"]["count"] >= 2:
        signals += 1
        notes.append(
            f"token overlap {top_tr['token_overlap']['count']}/"
            f"{top_tr['token_overlap']['total_query_tokens']} — "
            f"lexical match present"
        )
    if top_tr["ko_corroboration_count"] >= 2:
        signals += 1
        notes.append(
            f"{top_tr['ko_corroboration_count']} distinct KO-DB sources "
            f"corroborate top subject"
        )
    if top_tr["entity_neighbours"]:
        signals += 1
        notes.append("top result links to detected query entity")

    if signals >= 3:
        confidence = "high"
    elif signals == 2:
        confidence = "mid"
    elif signals == 1:
        confidence = "low"
    else:
        confidence = "low"
        notes.append("only cosine signal present — verify manually")

    # Alt-interpretation: large score gap → single interpretation
    if len(results) >= 2 and results[0].get("score") and results[1].get("score"):
        gap = results[0]["score"] - results[1]["score"]
        if gap > 0.05:
            notes.append(
                f"top-1 vs top-2 score gap {gap:.3f} — query has a clear winner"
            )
        else:
            notes.append(
                f"top-1 vs top-2 score gap {gap:.3f} — multiple plausible matches"
            )
    return {"confidence": confidence, "notes": notes}


# ── Orchestrator ────────────────────────────────────────────────────────────


def explain(query: str, top_k: int, namespace: str,
            include_graph: bool = True) -> dict:
    t_start = time.time()
    timing: dict[str, float] = {}

    # 1. Search
    t0 = time.time()
    resp = daemon_search(query, top_k, namespace)
    timing["daemon_rpc_ms"] = round((time.time() - t0) * 1000.0, 1)
    if resp is None:
        return {
            "query": query, "results": [], "timing_ms": timing,
            "entity_trace": {"unavailable": "daemon_unreachable"},
            "mermaid": None,
            "verdict": {"confidence": "none",
                        "notes": ["vault-search daemon unreachable — "
                                  "check `systemctl status vault-search`"]},
        }
    if resp.get("error"):
        return {
            "query": query, "results": [], "timing_ms": timing,
            "entity_trace": {"unavailable": "daemon_error"},
            "mermaid": None,
            "verdict": {"confidence": "none",
                        "notes": [f"daemon error: {resp['error']}"]},
        }

    raw_results = resp.get("results", []) or []
    query_tokens = set(tokenize(query))

    # 2. KO-DB connect (graceful)
    ko_conn = ko_connect()

    # 3. Memgraph connect (graceful)
    mg_conn = None if not include_graph else mg_connect()

    # 4. Entity detection on the query
    t0 = time.time()
    detected_entities: list[dict] = []
    if mg_conn is not None:
        try:
            detected_entities = mg_detect_entities(mg_conn, query)
            for e in detected_entities:
                e["neighbourhood"] = mg_entity_neighbourhood(mg_conn, e["name"])
        except Exception as e:
            print(f"[memgraph] entity-detect failed: {e}", file=sys.stderr)
    timing["memgraph_trace_ms"] = round((time.time() - t0) * 1000.0, 1)

    # 5. Per-result trace
    t0 = time.time()
    enriched: list[dict] = []
    traces: list[dict] = []
    for r in raw_results:
        tr = build_trace_for_result(r, query_tokens, ko_conn, mg_conn,
                                    detected_entities)
        traces.append(tr)
        enriched.append({
            **{k: v for k, v in r.items() if k != "vector"},
            "trace": tr,
        })
    timing["ko_trace_ms"] = round((time.time() - t0) * 1000.0, 1)

    if ko_conn is not None:
        ko_conn.close()
    if mg_conn is not None:
        try:
            mg_conn.close()
        except Exception:
            pass

    entity_trace = {"detected_entities": detected_entities}
    if not include_graph:
        entity_trace = {"unavailable": "disabled_via_--no-graph"}
    elif mg_conn is None and include_graph:
        entity_trace = {"unavailable": "memgraph_unreachable"}

    mermaid = render_mermaid(query, raw_results, traces, entity_trace)
    verdict = compute_verdict(enriched, traces)

    timing["total_ms"] = round((time.time() - t_start) * 1000.0, 1)

    return {
        "query": query,
        "namespace": namespace,
        "mode": resp.get("mode"),
        "backend": resp.get("backend"),
        "first_pass_max_score": resp.get("first_pass_max_score"),
        "skip_reason": resp.get("skip_reason"),
        "timing_ms": timing,
        "results": enriched,
        "entity_trace": entity_trace,
        "mermaid": mermaid,
        "verdict": verdict,
    }


# ── CLI ─────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(
        description="vault-explain — retrieval introspection trace.",
    )
    ap.add_argument("query", nargs="?", help="Free-text query")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--namespace", default="content",
                    choices=["content", "skills"])
    ap.add_argument("--json", action="store_true",
                    help="Emit JSON instead of markdown")
    ap.add_argument("--markdown", action="store_true",
                    help="Emit markdown (default)")
    ap.add_argument("--no-graph", action="store_true",
                    help="Skip Memgraph queries (entity trace)")
    args = ap.parse_args()

    if not args.query:
        ap.print_help()
        return 1

    report = explain(
        args.query, top_k=args.top_k, namespace=args.namespace,
        include_graph=not args.no_graph,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))

    return 0


if __name__ == "__main__":
    sys.exit(main())

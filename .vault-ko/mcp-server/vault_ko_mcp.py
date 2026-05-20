#!/usr/bin/python3
"""
vault-ko-mcp-server — Expose KO-DB as a Model Context Protocol (MCP) server.

ADR: 07-Decisions/2026-05-12 sv-5 crystallization automation arch.md
Phase B-1, Layer 3 (retrieval) — MCP-server exposure.

Pattern reference: github.com/modelcontextprotocol/servers (memory server).

Exposes 4 tools over stdio MCP transport:
    1. query(substring, top_k, source_type)        — substring search + filter
    2. stats()                                      — predicate/source distribution
    3. conflicts(predicate)                         — cross-source contradictions
    4. top_k(token, top_k, facts_per_subject)      — cross-source corroboration

Backend: .vault-ko/facts.db (SQLite). Reuses the query/ranking logic from
the `vault-ko-query` CLI. Read-only — never mutates the DB.

Run:
    python3 vault_ko_mcp.py            # stdio transport (for Claude Desktop / Codex)

Env vars:
    VAULT_ROOT                         # default: /root/obsidian-vault
    VAULT_KO_DB                        # override DB path (else $VAULT_ROOT/.vault-ko/facts.db)
"""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# ---------------------------------------------------------------------------
# Config & connection
# ---------------------------------------------------------------------------

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
KO_DB = Path(os.environ.get("VAULT_KO_DB", str(VAULT_ROOT / ".vault-ko" / "facts.db")))

SERVER_NAME = "vault-ko"
SERVER_VERSION = "0.1.0"


def _connect() -> sqlite3.Connection:
    if not KO_DB.exists():
        raise FileNotFoundError(f"KO-DB not found: {KO_DB}")
    # read-only URI to enforce no-mutation contract
    uri = f"file:{KO_DB}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Tool implementations (pure SQLite, lifted from vault-ko-query)
# ---------------------------------------------------------------------------

VALID_SOURCE_TYPES = {"session", "wiki", "adr", "notebooklm", "manual"}


def _is_post34(conn) -> bool:
    """Detect post-#34 (2026-05-19) schema: facts.provenance dropped to side-table."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(facts)").fetchall()}
    has_pv = bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fact_provenance'"
    ).fetchone())
    return "provenance" not in cols and has_pv


def tool_query(
    substring: str,
    top_k: int = 10,
    source_type: str | None = None,
) -> list[dict[str, Any]]:
    """Substring LIKE-search across subject/predicate/object with optional filter."""
    if not substring:
        return []
    if source_type and source_type not in VALID_SOURCE_TYPES:
        raise ValueError(
            f"invalid source_type={source_type!r}; allowed: {sorted(VALID_SOURCE_TYPES)}"
        )
    top_k = max(1, min(int(top_k), 200))
    like = f"%{substring}%"
    with _connect() as conn:
        post34 = _is_post34(conn)
        if post34:
            where = ["(f.subject LIKE ? OR f.predicate LIKE ? OR f.object LIKE ?)"]
            params: list[Any] = [like, like, like]
            if source_type:
                where.append("f.source_type = ?")
                params.append(source_type)
            sql = (
                "SELECT f.id, f.subject, f.predicate, f.object, "
                "       COALESCE(GROUP_CONCAT(fp.provenance, '||'), '') AS provenance, "
                "       f.confidence, f.source_type "
                "FROM facts f LEFT JOIN fact_provenance fp ON fp.fact_hash = f.hash "
                "WHERE " + " AND ".join(where) +
                " GROUP BY f.id "
                " ORDER BY f.confidence DESC, f.id ASC LIMIT ?"
            )
        else:
            where = ["(subject LIKE ? OR predicate LIKE ? OR object LIKE ?)"]
            params = [like, like, like]
            if source_type:
                where.append("source_type = ?")
                params.append(source_type)
            sql = (
                "SELECT id, subject, predicate, object, provenance, confidence, source_type "
                "FROM facts WHERE " + " AND ".join(where) +
                " ORDER BY confidence DESC, id ASC LIMIT ?"
            )
        params.append(top_k)
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def tool_stats() -> dict[str, Any]:
    """Aggregate counts: total, per source_type, top predicates, top provenance files."""
    with _connect() as conn:
        post34 = _is_post34(conn)
        total = conn.execute("SELECT COUNT(*) AS n FROM facts").fetchone()["n"]
        by_type = [
            dict(r) for r in conn.execute(
                "SELECT source_type, COUNT(*) AS n FROM facts "
                "GROUP BY source_type ORDER BY n DESC"
            ).fetchall()
        ]
        by_predicate = [
            dict(r) for r in conn.execute(
                "SELECT predicate, COUNT(*) AS n FROM facts "
                "GROUP BY predicate ORDER BY n DESC LIMIT 20"
            ).fetchall()
        ]
        if post34:
            by_provenance = [
                dict(r) for r in conn.execute(
                    "SELECT provenance, COUNT(*) AS n FROM fact_provenance "
                    "GROUP BY provenance ORDER BY n DESC LIMIT 10"
                ).fetchall()
            ]
        else:
            by_provenance = [
                dict(r) for r in conn.execute(
                    "SELECT provenance, COUNT(*) AS n FROM facts "
                    "GROUP BY provenance ORDER BY n DESC LIMIT 10"
                ).fetchall()
            ]
    return {
        "db_path": str(KO_DB),
        "total_facts": total,
        "by_source_type": by_type,
        "top_predicates": by_predicate,
        "top_provenance": by_provenance,
    }


def tool_conflicts(predicate: str | None = None) -> list[dict[str, Any]]:
    """Find subjects with multiple distinct objects for the same predicate.

    If `predicate` is given, restrict to that predicate (LIKE).
    """
    with _connect() as conn:
        post34 = _is_post34(conn)
        if post34:
            base_select = (
                "SELECT f.subject, f.predicate, "
                "       GROUP_CONCAT(DISTINCT f.object) AS objects, "
                "       GROUP_CONCAT(DISTINCT fp.provenance) AS sources, "
                "       COUNT(*) AS n, "
                "       COUNT(DISTINCT f.object) AS distinct_objects "
                "FROM facts f LEFT JOIN fact_provenance fp ON fp.fact_hash = f.hash "
            )
            if predicate:
                sql = base_select + (
                    "WHERE f.predicate LIKE ? "
                    "GROUP BY f.subject, f.predicate "
                    "HAVING COUNT(DISTINCT f.object) > 1 "
                    "ORDER BY distinct_objects DESC, n DESC LIMIT 50"
                )
                params: tuple = (f"%{predicate}%",)
            else:
                sql = base_select + (
                    "GROUP BY f.subject, f.predicate "
                    "HAVING COUNT(DISTINCT f.object) > 1 "
                    "ORDER BY distinct_objects DESC, n DESC LIMIT 50"
                )
                params = ()
        else:
            if predicate:
                sql = """
                    SELECT subject, predicate,
                           GROUP_CONCAT(DISTINCT object) AS objects,
                           GROUP_CONCAT(DISTINCT provenance) AS sources,
                           COUNT(*) AS n,
                           COUNT(DISTINCT object) AS distinct_objects
                    FROM facts
                    WHERE predicate LIKE ?
                    GROUP BY subject, predicate
                    HAVING COUNT(DISTINCT object) > 1
                    ORDER BY distinct_objects DESC, n DESC
                    LIMIT 50
                """
                params = (f"%{predicate}%",)
            else:
                sql = """
                    SELECT subject, predicate,
                           GROUP_CONCAT(DISTINCT object) AS objects,
                           GROUP_CONCAT(DISTINCT provenance) AS sources,
                           COUNT(*) AS n,
                           COUNT(DISTINCT object) AS distinct_objects
                    FROM facts
                    GROUP BY subject, predicate
                    HAVING COUNT(DISTINCT object) > 1
                    ORDER BY distinct_objects DESC, n DESC
                    LIMIT 50
                """
                params = ()
        rows = conn.execute(sql, params).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["objects"] = d["objects"].split(",") if d.get("objects") else []
        d["sources"] = d["sources"].split(",") if d.get("sources") else []
        out.append(d)
    return out


def tool_top_k(
    token: str,
    top_k: int = 10,
    facts_per_subject: int = 5,
) -> list[dict[str, Any]]:
    """Top-K most cross-source-corroborated subjects for a token.

    Ranks by (distinct provenance count DESC, max confidence DESC, fact count DESC).
    For each subject, returns up to `facts_per_subject` representative facts.
    """
    if not token:
        return []
    top_k = max(1, min(int(top_k), 50))
    facts_per_subject = max(1, min(int(facts_per_subject), 20))
    like = f"%{token}%"
    with _connect() as conn:
        post34 = _is_post34(conn)
        if post34:
            subject_sql = """
                SELECT subject,
                       MAX(provenance_count) AS sources,
                       MAX(confidence)        AS max_conf,
                       COUNT(*)               AS fact_count
                FROM facts
                WHERE subject LIKE ? OR object LIKE ?
                GROUP BY subject
                ORDER BY sources DESC, max_conf DESC, fact_count DESC
                LIMIT ?
            """
        else:
            subject_sql = """
                SELECT subject,
                       COUNT(DISTINCT provenance) AS sources,
                       MAX(confidence)            AS max_conf,
                       COUNT(*)                   AS fact_count
                FROM facts
                WHERE subject LIKE ? OR object LIKE ?
                GROUP BY subject
                ORDER BY sources DESC, max_conf DESC, fact_count DESC
                LIMIT ?
            """
        subjects = conn.execute(subject_sql, (like, like, top_k)).fetchall()
        result = []
        for row in subjects:
            if post34:
                facts = conn.execute(
                    "SELECT f.predicate, f.object, "
                    "       COALESCE(GROUP_CONCAT(fp.provenance, '||'), '') AS provenance, "
                    "       f.confidence, f.source_type "
                    "FROM facts f LEFT JOIN fact_provenance fp ON fp.fact_hash = f.hash "
                    "WHERE f.subject = ? "
                    "GROUP BY f.id "
                    "ORDER BY f.confidence DESC, f.id ASC LIMIT ?",
                    (row["subject"], facts_per_subject),
                ).fetchall()
            else:
                facts = conn.execute(
                    "SELECT predicate, object, provenance, confidence, source_type "
                    "FROM facts WHERE subject = ? "
                    "ORDER BY confidence DESC, id ASC LIMIT ?",
                    (row["subject"], facts_per_subject),
                ).fetchall()
            result.append({
                "subject": row["subject"],
                "source_count": row["sources"],
                "max_confidence": row["max_conf"],
                "fact_count": row["fact_count"],
                "facts": [dict(f) for f in facts],
            })
    return result


# ---------------------------------------------------------------------------
# MCP server wiring
# ---------------------------------------------------------------------------

server: Server = Server(SERVER_NAME)


@server.list_tools()
async def _list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query",
            description=(
                "Substring search across KO-DB facts (subject/predicate/object). "
                "Optional `source_type` filter (session|wiki|adr|notebooklm|manual). "
                "Returns up to `top_k` facts ordered by confidence DESC."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "substring": {"type": "string", "description": "LIKE pattern (case-sensitive in SQLite default)."},
                    "top_k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 200},
                    "source_type": {
                        "type": "string",
                        "enum": sorted(VALID_SOURCE_TYPES),
                        "description": "Optional source-type filter.",
                    },
                },
                "required": ["substring"],
            },
        ),
        types.Tool(
            name="stats",
            description=(
                "KO-DB summary: total fact count, distribution by source_type, "
                "top 20 predicates, top 10 provenance files."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="conflicts",
            description=(
                "Find subjects with multiple distinct objects for the same predicate "
                "(cross-source contradictions). Optional `predicate` LIKE filter."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "predicate": {"type": "string", "description": "Optional predicate LIKE filter."},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="top_k",
            description=(
                "Top-K subjects ranked by cross-source corroboration. For each subject, "
                "returns up to `facts_per_subject` representative facts. Ideal for "
                "load-session-context: gives the agent the most vault-confirmed knowledge "
                "about a slug/topic in compact form."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Subject/object LIKE pattern."},
                    "top_k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
                    "facts_per_subject": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                },
                "required": ["token"],
            },
        ),
    ]


def _text(payload: Any) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2, default=str))]


@server.call_tool()
async def _call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    args = arguments or {}
    try:
        if name == "query":
            data = tool_query(
                substring=args.get("substring", ""),
                top_k=args.get("top_k", 10),
                source_type=args.get("source_type"),
            )
        elif name == "stats":
            data = tool_stats()
        elif name == "conflicts":
            data = tool_conflicts(predicate=args.get("predicate"))
        elif name == "top_k":
            data = tool_top_k(
                token=args.get("token", ""),
                top_k=args.get("top_k", 10),
                facts_per_subject=args.get("facts_per_subject", 5),
            )
        else:
            return _text({"error": f"unknown tool: {name}"})
    except Exception as e:
        return _text({"error": str(e), "tool": name, "arguments": args})
    return _text(data)


async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        sys.exit(0)

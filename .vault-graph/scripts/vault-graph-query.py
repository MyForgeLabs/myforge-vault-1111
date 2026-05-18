#!/root/.notebooklm-venv/bin/python3
"""
vault-graph-query — minimal Cypher wrapper over the vault Memgraph.

Usage:
  vault-graph-query "MATCH (e:Entity) RETURN e.name LIMIT 5"
  vault-graph-query --json "MATCH ..."

Prints rows as TSV (default) or JSON-lines. Read-only by convention but does
not enforce it — Memgraph will execute any Cypher you pass.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import mgclient


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("cypher", help="Cypher query string")
    ap.add_argument("--json", action="store_true", help="emit JSON lines instead of TSV")
    ap.add_argument("--host", default=os.environ.get("MEMGRAPH_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("MEMGRAPH_PORT", "7687")))
    args = ap.parse_args()

    conn = mgclient.connect(host=args.host, port=args.port)
    try:
        cur = conn.cursor()
        cur.execute(args.cypher)
        try:
            rows = cur.fetchall()
        except mgclient.InterfaceError:
            # statement with no result-set (e.g. CREATE INDEX)
            print("[ok] no rows", file=sys.stderr)
            return
        col_names = [d.name for d in (cur.description or [])]

        if args.json:
            for r in rows:
                obj = {col_names[i] if i < len(col_names) else f"c{i}": _coerce(v)
                       for i, v in enumerate(r)}
                print(json.dumps(obj, ensure_ascii=False, default=str))
        else:
            if col_names:
                print("\t".join(col_names))
            for r in rows:
                print("\t".join(_str(v) for v in r))
    finally:
        conn.close()


def _coerce(v):
    if hasattr(v, "properties"):  # mgclient Node / Relationship
        return dict(v.properties)
    return v


def _str(v):
    if hasattr(v, "properties"):
        return json.dumps(dict(v.properties), ensure_ascii=False, default=str)
    return "" if v is None else str(v)


if __name__ == "__main__":
    main()

#!/root/.notebooklm-venv/bin/python3
"""
vault-graph-viz-export — regenerate the docs/typed-graph-viz/data.json snapshot.

Pulls the top-N highest-cross-source-corroboration typed entities per label
from Memgraph, fetches their 1-hop neighbors, dedupes edges, and writes a
D3-ready {nodes, links} JSON.

The companion HTML at docs/typed-graph-viz/index.html consumes this file.

Usage:
  vault-graph-viz-export                          # default: top-25 per label
  vault-graph-viz-export --per-label 50           # bigger
  vault-graph-viz-export --output PATH            # custom output (default: docs/)
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    import mgclient
except ImportError:
    print("✗ mgclient not installed", file=sys.stderr)
    sys.exit(2)

LABELS = ["Project", "Person", "Server", "Skill",
          "SourceFile", "Concept", "Decision", "Sprint"]
DEFAULT_OUT = Path("/root/projects/myforge-vault-1111/docs/typed-graph-viz/data.json")


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-graph-viz-export")
    ap.add_argument("--per-label", type=int, default=25,
                    help="Top-N entities per label (default 25 → ~200 total)")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT,
                    help="Output JSON path (default: docs/typed-graph-viz/data.json)")
    ap.add_argument("--edges-per-node", type=int, default=8,
                    help="Max 1-hop neighbors fetched per node (default 8)")
    args = ap.parse_args()

    conn = mgclient.connect(host="127.0.0.1", port=7687)
    conn.autocommit = True
    cur = conn.cursor()

    nodes: list[dict] = []
    for label in LABELS:
        cur.execute(
            f"MATCH (n:Entity:{label}) RETURN n.name, n.source_count "
            f"ORDER BY n.source_count DESC LIMIT {args.per_label}"
        )
        for r in cur.fetchall():
            if r[0]:
                nodes.append({"id": r[0], "label": label, "weight": r[1] or 1})
    print(f"[viz-export] {len(nodes)} typed nodes", file=sys.stderr)

    ids = {n["id"]: n for n in nodes}
    raw_links: list[dict] = []
    for nid in ids:
        cur.execute(
            f"MATCH (a:Entity {{name:$n}})-[r]-(b:Entity) "
            f"RETURN b.name, type(r) LIMIT {args.edges_per_node}",
            {"n": nid},
        )
        for r in cur.fetchall():
            if r[0] in ids:
                raw_links.append({"source": nid, "target": r[0], "type": r[1]})

    # Dedup undirected
    seen = set()
    links = []
    for l in raw_links:
        key = tuple(sorted([l["source"], l["target"]]) + [l["type"]])
        if key not in seen:
            seen.add(key)
            links.append(l)
    print(f"[viz-export] {len(links)} unique edges", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "links": links}, f, ensure_ascii=False)
    print(f"[viz-export] wrote {args.output} ({args.output.stat().st_size} bytes)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

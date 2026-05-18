#!/root/.notebooklm-venv/bin/python3
"""Extract top-200 hub entities + intra-edges to JSON for D3 viewer."""
import json
import os
import sys
from pathlib import Path

import mgclient

OUT = Path("/root/projects/myforge-vault-1111/docs/graph/top200.json")
TOP_N = 200

# Priority for label-pick (most specific wins): order matters
LABEL_PRIORITY = [
    "Person", "Decision", "Project", "Skill", "Sprint",
    "Server", "Pattern", "Concept", "SourceFile",
]


def pick_label(labels):
    """Pick most-specific label from list (Entity stripped)."""
    candidates = [l for l in labels if l != "Entity"]
    if not candidates:
        return "Entity"
    for pri in LABEL_PRIORITY:
        if pri in candidates:
            return pri
    return candidates[0]


def main():
    conn = mgclient.connect(host="127.0.0.1", port=7687)
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Top-N hub entities
    cur.execute(
        f"MATCH (n:Entity)-[r]-() "
        f"WITH n, count(r) AS deg "
        f"ORDER BY deg DESC LIMIT {TOP_N} "
        f"RETURN n.name AS name, labels(n) AS labels, deg"
    )
    rows = cur.fetchall()
    nodes = []
    name_set = set()
    for name, labels, deg in rows:
        if not name:
            continue
        nodes.append({
            "id": name,
            "label": pick_label(labels),
            "deg": int(deg),
        })
        name_set.add(name)

    print(f"[i] {len(nodes)} top hub nodes", file=sys.stderr)

    # 2. Intra-edges (both endpoints in top-N), distinct undirected pairs
    # Use parameterised query with name list
    name_list = list(name_set)
    cur.execute(
        "MATCH (a:Entity)-[r]->(b:Entity) "
        "WHERE a.name IN $names AND b.name IN $names "
        "RETURN a.name AS source, b.name AS target, type(r) AS rel",
        {"names": name_list},
    )
    edges = cur.fetchall()
    # Dedupe undirected; keep first rel-type
    seen = set()
    links = []
    for src, tgt, rel in edges:
        if not src or not tgt or src == tgt:
            continue
        key = tuple(sorted([src, tgt]))
        if key in seen:
            continue
        seen.add(key)
        links.append({"source": src, "target": tgt, "type": rel or "REL"})

    print(f"[i] {len(links)} intra-edges (deduped, undirected)", file=sys.stderr)

    conn.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"nodes": nodes, "links": links}
    # Compact JSON (smaller, viewer reads inline)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    sz = OUT.stat().st_size
    print(f"[ok] wrote {OUT} — {sz} bytes ({sz/1024:.1f} KB)", file=sys.stderr)
    # label distribution
    from collections import Counter
    lc = Counter(n["label"] for n in nodes)
    print(f"[i] label distribution: {dict(lc.most_common())}", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/root/.notebooklm-venv/bin/python3
"""
vault-graph-extract — KO-DB facts -> Memgraph entity-graph (SV B-7 Week 1-α)

Reads /root/obsidian-vault/.vault-ko/facts.db and loads it into Memgraph
as (:Entity)-[:PREDICATE]->(:Entity|:Literal) triples.

Modes:
  --dry-run   Stats only; don't touch Memgraph.
  --reset     Drop all :Entity/:Literal nodes (and their edges) first.
  (default)   Idempotent MERGE-based upsert with progress bar.

Conventions:
  - Object becomes :Entity iff it also appears as a subject (KO-DB internal
    closure); otherwise :Literal.
  - Predicate text -> uppercased snake-case edge type.
  - Entity properties: name, source_count, max_confidence.
  - Literal properties: value.
  - Edge properties: confidence, provenance, source_type, fact_hash.

Namespace note: Memgraph container is shared with B-2; we stay scoped to
the :Entity / :Literal labels and avoid touching other B-2 nodes.
"""
from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import mgclient
from tqdm import tqdm

# ─── CONFIG ───────────────────────────────────────────────────────────────

KO_DB = Path(os.environ.get(
    "VAULT_KO_DB",
    "/root/obsidian-vault/.vault-ko/facts.db",
))
MEMGRAPH_HOST = os.environ.get("MEMGRAPH_HOST", "127.0.0.1")
MEMGRAPH_PORT = int(os.environ.get("MEMGRAPH_PORT", "7687"))
SCHEMA_FILE = Path(__file__).resolve().parent.parent / "schema" / "entity-graph-schema.cypher"

BATCH_SIZE = 500  # commit cadence

# Memgraph relationship types must match [A-Za-z_][A-Za-z0-9_]*
_REL_SANITIZE = re.compile(r"[^A-Za-z0-9_]+")


def normalize_predicate(pred: str) -> str:
    """'has minimum' -> 'HAS_MINIMUM'; safe for Cypher rel-type literal."""
    s = _REL_SANITIZE.sub("_", pred.strip())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "RELATED_TO"
    if s[0].isdigit():
        s = "_" + s
    return s.upper()


# ─── KO-DB SIDE ───────────────────────────────────────────────────────────

def load_facts(db_path: Path):
    if not db_path.exists():
        sys.exit(f"[fatal] KO-DB not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT hash, subject, predicate, object, confidence, provenance, source_type FROM facts"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def compute_entity_set(rows) -> set[str]:
    """An object is an :Entity iff it also appears as a subject somewhere."""
    subjects = {r["subject"] for r in rows}
    return subjects


def aggregate_entities(rows, entity_set: set[str]) -> dict[str, dict]:
    """name -> {source_count, max_confidence}."""
    agg: dict[str, dict] = defaultdict(lambda: {"source_count": 0, "max_confidence": 0.0})
    for r in rows:
        s = r["subject"]
        c = float(r["confidence"] or 0.0)
        agg[s]["source_count"] += 1
        if c > agg[s]["max_confidence"]:
            agg[s]["max_confidence"] = c
        o = r["object"]
        if o in entity_set:
            agg[o]["source_count"] += 1
            if c > agg[o]["max_confidence"]:
                agg[o]["max_confidence"] = c
    return agg


# ─── MEMGRAPH SIDE ────────────────────────────────────────────────────────

def connect_mg():
    return mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)


def run_schema(conn):
    """Best-effort apply schema DDL. Index/constraint-exists errors are swallowed."""
    if not SCHEMA_FILE.exists():
        return
    text = SCHEMA_FILE.read_text()
    cur = conn.cursor()
    for stmt in text.split(";"):
        s = stmt.strip()
        if not s or s.startswith("//"):
            continue
        # strip line-comments inside the stmt
        clean = "\n".join(
            line for line in s.splitlines() if not line.strip().startswith("//")
        ).strip()
        if not clean:
            continue
        try:
            cur.execute(clean + ";")
            conn.commit()
        except mgclient.DatabaseError as exc:
            # already exists / not supported in this Memgraph build — fine
            print(f"[schema] skipped: {clean[:60]}... ({exc})", file=sys.stderr)


def reset_graph(conn):
    cur = conn.cursor()
    print("[reset] deleting :Entity and :Literal nodes (DETACH)...", file=sys.stderr)
    cur.execute("MATCH (n) WHERE n:Entity OR n:Literal DETACH DELETE n;")
    conn.commit()


def upsert_entities(conn, entities: dict[str, dict]):
    cur = conn.cursor()
    items = list(entities.items())
    pbar = tqdm(total=len(items), desc="entities", unit="ent")
    for i, (name, props) in enumerate(items, 1):
        cur.execute(
            "MERGE (e:Entity {name: $name}) "
            "SET e.source_count = $sc, e.max_confidence = $mc",
            {"name": name, "sc": props["source_count"], "mc": props["max_confidence"]},
        )
        if i % BATCH_SIZE == 0:
            conn.commit()
        pbar.update(1)
    conn.commit()
    pbar.close()


def upsert_relations(conn, rows, entity_set: set[str]):
    cur = conn.cursor()
    pbar = tqdm(total=len(rows), desc="relations", unit="rel")
    literal_seen: set[str] = set()
    for i, r in enumerate(rows, 1):
        s = r["subject"]
        o = r["object"]
        pred = normalize_predicate(r["predicate"])
        is_entity_obj = o in entity_set

        # Make sure the object node exists (the literals were not in `entities`).
        if not is_entity_obj and o not in literal_seen:
            cur.execute(
                "MERGE (l:Literal {value: $v})",
                {"v": o},
            )
            literal_seen.add(o)

        obj_label = "Entity" if is_entity_obj else "Literal"
        obj_key = "name" if is_entity_obj else "value"

        # MERGE the edge (idempotent on fact_hash)
        cypher = (
            f"MATCH (s:Entity {{name: $s}}) "
            f"MATCH (o:{obj_label} {{{obj_key}: $o}}) "
            f"MERGE (s)-[rel:`{pred}` {{fact_hash: $h}}]->(o) "
            f"SET rel.confidence = $c, rel.provenance = $p, rel.source_type = $st"
        )
        cur.execute(cypher, {
            "s": s,
            "o": o,
            "h": r["hash"],
            "c": float(r["confidence"] or 0.0),
            "p": r["provenance"],
            "st": r["source_type"],
        })
        if i % BATCH_SIZE == 0:
            conn.commit()
        pbar.update(1)
    conn.commit()
    pbar.close()


# ─── MAIN ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dry-run", action="store_true", help="stats only")
    ap.add_argument("--reset", action="store_true", help="wipe :Entity/:Literal first")
    args = ap.parse_args()

    rows = load_facts(KO_DB)
    entity_set = compute_entity_set(rows)
    entities = aggregate_entities(rows, entity_set)
    literal_objects = {r["object"] for r in rows if r["object"] not in entity_set}
    predicates = {normalize_predicate(r["predicate"]) for r in rows}

    print(f"[stats] KO-DB rows:           {len(rows):>7,}")
    print(f"[stats] unique entities:      {len(entities):>7,}  (would become :Entity nodes)")
    print(f"[stats] unique literals:      {len(literal_objects):>7,}  (would become :Literal nodes)")
    print(f"[stats] unique predicates:    {len(predicates):>7,}  (would become edge types)")
    print(f"[stats] total relations:      {len(rows):>7,}  (one edge per fact)")

    if args.dry_run:
        print("[dry-run] no Memgraph changes made.")
        return

    conn = connect_mg()
    try:
        if args.reset:
            reset_graph(conn)
        run_schema(conn)
        upsert_entities(conn, entities)
        upsert_relations(conn, rows, entity_set)
        # Final node count for confirmation
        cur = conn.cursor()
        cur.execute("MATCH (n:Entity) RETURN count(n) AS c;")
        ent_count = cur.fetchall()[0][0]
        cur.execute("MATCH (n:Literal) RETURN count(n) AS c;")
        lit_count = cur.fetchall()[0][0]
        cur.execute("MATCH ()-[r]->() WHERE startNode(r):Entity RETURN count(r) AS c;")
        rel_count = cur.fetchall()[0][0]
        print(f"[done] :Entity nodes:  {ent_count:,}")
        print(f"[done] :Literal nodes: {lit_count:,}")
        print(f"[done] entity-rooted relations: {rel_count:,}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

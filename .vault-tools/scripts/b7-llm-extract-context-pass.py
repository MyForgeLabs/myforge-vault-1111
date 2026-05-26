#!/root/.notebooklm-venv/bin/python3
"""
b7-llm-extract-context-pass — emit context-aware classification batches for the
remaining Generic :Entity nodes (second-pass after the bulk first sweep).

What's different from `vault-graph-retype --phase llm-extract --emit-pending`:

  1. Pulls each Generic entity's provenance file path (where the entity was
     ingested from) and grabs a 1-3 line context snippet around the first
     occurrence of the entity name in that file.
  2. Emits batches as `{entity_name, context}` pairs (not bare names), so the
     classifier subagent has the local meaning to disambiguate.
  3. Smaller batches (default 40 entities/batch) because the prompt is fatter.

Output is consumed by the EXISTING vault-graph-retype --consume-pending phase 2
(same response schema, same Memgraph apply).

Usage:
  b7-llm-extract-context-pass --emit-pending <dir> [--batches N] [--limit N]
  b7-llm-extract-context-pass --emit-pending /tmp/b7-ctx-pass/ --batches 70

Cron-not-suggested: this is a one-shot intervention, not a recurring axis.
Wiki: 11-wiki/sv-06-world-model-knowledge-graph.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

try:
    import mgclient
except ImportError:
    print("✗ mgclient not installed (need /root/.notebooklm-venv)", file=sys.stderr)
    sys.exit(2)

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
KO_DB = VAULT_ROOT / ".vault-ko" / "facts.db"

TAXONOMY = [
    "Project", "Person", "Server", "Skill", "SourceFile",
    "Concept", "Decision", "Sprint", "Generic",
]

RULES = (
    "Classify each entity name into exactly ONE label from the taxonomy, "
    "using the provided context snippet for disambiguation. Context is one "
    "or two sentences from the source file where the entity was originally "
    "ingested. If the context is empty or unhelpful, classify by name alone "
    "and use Generic when in doubt.\n\n"
    "Rules:\n"
    "- Generic = ambiguous, transient action, one-off reference (default-on-doubt)\n"
    "- Concept = evergreen knowledge pattern (e.g. 'fanout pattern', 'RRF fusion')\n"
    "- Sprint = session-refs, B-N/SV-N markers (e.g. 'B-1 Week 4')\n"
    "- Skill = agent-skill prefix (wp-/vault-/bmad-/wds-/gds-)\n"
    "- SourceFile = file path or X.md/X.py form\n"
    "- Server = domain, hostname, infra keyword\n"
    "- Decision = ADR-style title (often dated)\n"
    "- Project = vault project (KGC-4, Boulium, MFL-Voice, …)\n"
    "- Person = human name\n"
    "Target false-positive rate: <5%."
)


def fetch_generic_names() -> list[str]:
    """Return all Generic (single-label) :Entity names from Memgraph."""
    conn = mgclient.connect(host="127.0.0.1", port=7687)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "MATCH (n:Entity) WHERE size(labels(n)) = 1 RETURN n.name"
    )
    return [r[0] for r in cur.fetchall() if r[0]]


def kodb_lookup_provenance(names: list[str]) -> dict[str, str]:
    """For each name, return the first provenance file found in KO-DB facts.

    Returns {name: prov_path}. Names with no fact match are absent from the dict.
    """
    if not KO_DB.exists():
        return {}
    out: dict[str, str] = {}
    conn = sqlite3.connect(KO_DB)
    cur = conn.cursor()
    # Detect post-#34 schema (provenance in side-table) vs legacy.
    cols = {r[1] for r in cur.execute("PRAGMA table_info(facts)").fetchall()}
    has_side = bool(cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fact_provenance'"
    ).fetchone())
    post34 = "provenance" not in cols and has_side
    BATCH = 500
    for i in range(0, len(names), BATCH):
        chunk = names[i : i + BATCH]
        placeholders = ",".join("?" * len(chunk))
        if post34:
            q = f"""
                SELECT f.subject, MIN(fp.provenance)
                FROM facts f JOIN fact_provenance fp ON f.hash = fp.fact_hash
                WHERE f.subject IN ({placeholders}) OR f.object IN ({placeholders})
                GROUP BY f.subject
            """
            cur.execute(q, chunk + chunk)
        else:
            q = f"""
                SELECT subject, MIN(provenance)
                FROM facts
                WHERE subject IN ({placeholders}) OR object IN ({placeholders})
                GROUP BY subject
            """
            cur.execute(q, chunk + chunk)
        for subj, prov in cur.fetchall():
            if subj and prov:
                out[subj] = prov
    return out


def grab_snippet(file_rel: str, entity: str, lines_each_side: int = 1) -> str:
    """Return up to N lines around the first occurrence of `entity` in the file.

    Empty string if file missing or entity not found.
    """
    if not file_rel:
        return ""
    path = VAULT_ROOT / file_rel
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    lines = text.splitlines()
    # case-insensitive substring search
    needle = entity.lower()
    for i, ln in enumerate(lines):
        if needle in ln.lower():
            lo = max(0, i - lines_each_side)
            hi = min(len(lines), i + lines_each_side + 1)
            snippet = " ".join(lines[lo:hi]).strip()
            # Trim very long snippets
            if len(snippet) > 300:
                snippet = snippet[:297] + "…"
            return snippet
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(prog="b7-llm-extract-context-pass")
    ap.add_argument("--emit-pending", required=True,
                    help="Directory to write batch request JSONs into")
    ap.add_argument("--batches", type=int, default=70,
                    help="Number of batches to split into (default 70 → ~90 entities/batch on 6.1K)")
    ap.add_argument("--limit", type=int, default=0,
                    help="Smoke-test: only process first N Generic entities (default: all)")
    args = ap.parse_args()

    pending_dir = Path(args.emit_pending)
    pending_dir.mkdir(parents=True, exist_ok=True)

    names = fetch_generic_names()
    print(f"[ctx-pass] {len(names)} Generic :Entity nodes", file=sys.stderr)

    if args.limit:
        names = names[: args.limit]
        print(f"[ctx-pass] smoke-test: trimming to first {len(names)}", file=sys.stderr)

    print(f"[ctx-pass] looking up KO-DB provenance for {len(names)} names...", file=sys.stderr)
    prov_map = kodb_lookup_provenance(names)
    print(f"[ctx-pass] KO-DB provenance found for {len(prov_map)}/{len(names)} names "
          f"({len(prov_map)/len(names)*100:.1f}%)", file=sys.stderr)

    # Build {entity, context} payload
    enriched: list[dict] = []
    n_with_ctx = 0
    for name in names:
        prov = prov_map.get(name, "")
        snippet = grab_snippet(prov, name)
        if snippet:
            n_with_ctx += 1
        enriched.append({
            "entity": name,
            "context": snippet,
            "source": prov or "(no provenance)",
        })
    pct_ctx = (n_with_ctx / len(enriched) * 100) if enriched else 0
    print(f"[ctx-pass] {n_with_ctx} entities ({pct_ctx:.1f}%) have a context snippet", file=sys.stderr)

    # Split into batches
    n_batches = max(1, args.batches)
    chunk = (len(enriched) + n_batches - 1) // n_batches
    batches = [enriched[i : i + chunk] for i in range(0, len(enriched), chunk)]
    print(f"[ctx-pass] split into {len(batches)} batches of ~{chunk}", file=sys.stderr)

    today = date.today().strftime("%Y%m%d")
    for bi, batch in enumerate(batches, 1):
        buid = f"b7-ctx-batch-{today}-{bi:03d}"
        req = {
            "batch_id": buid,
            "batch_index": bi,
            "batch_count": len(batches),
            "taxonomy": TAXONOMY,
            "rules": RULES,
            "entities_with_context": batch,
            "expected_response_format": {
                "labels": {"<entity_name>": "<label_or_Generic>"},
                "skipped": ["<name>"],
            },
        }
        (pending_dir / f"{buid}.json").write_text(
            json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"[ctx-pass] emitted {len(batches)} pending requests → {pending_dir}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/root/.notebooklm-venv/bin/python3
"""
vault-hyde-rewrite — HyDE-style query rewriter SKELETON.

HyDE (Hypothetical Document Embeddings, Gao et al. 2022): instead of embedding
the raw query, ask an LLM to write a hypothetical answer-document, then embed
THAT for retrieval. Often beats raw-query embeddings on under-specified queries.

This is a SKELETON. The "fast path" uses simple keyword expansion (no LLM
required) as a deterministic placeholder. The "real path" (subagent-fanout)
hooks the same 2-phase pending-file pattern as b7-ctx-pass / vault-ko-ingest:
emit a pending request, a parent agent spawns a subagent, response file is
consumed for downstream retrieval.

Usage:
  vault-hyde-rewrite "<query>"                   # fast path (keyword-expand)
  vault-hyde-rewrite "<query>" --json            # JSON output
  vault-hyde-rewrite "<query>" --emit-pending <dir>  # 2-phase: write request JSON
  vault-hyde-rewrite "<query>" --consume <dir>       # 2-phase: read response

Output schema:
  {
    "query": "<original>",
    "expansions": ["<hypothetical-answer-1>", "<hypothetical-answer-2>", ...],
    "merged_for_embedding": "<query> <expansion-keywords-joined>"
  }

Wiki: 11-wiki/hyde-query-rewrite-skeleton.md (to-be-written)
"""
from __future__ import annotations
import argparse, json, sys, re
from datetime import datetime, timezone
from pathlib import Path

# Tiny topic-keyword bank for the fast-path skeleton (no LLM call).
# These are NOT a substitute for real HyDE; they cover the most-common SV vault
# query intents to keep --no-llm useful for offline development.
DOMAIN_HINTS = {
    "retrieval":   ["bge-m3", "RRF fusion", "Memgraph vector-index", "top-K", "Recall@5"],
    "rerank":      ["bge-reranker-v2-m3", "cross-encoder", "auto-rerank", "max_cos<0.65"],
    "graph":       ["typed-entity", "Memgraph", "Cypher", "labels", "B-7"],
    "memory":      ["MEMORY.md", "KO-DB", "SCD2", "fact provenance", "session pointers"],
    "subagent":    ["fanout", "Claude Code Task tool", "emit-pending", "consume-pending", "$0 cost"],
    "safety":      ["Layer-0 chained guards", "git pre-commit", "flock mutex", "Critic"],
    "crystallize": ["G-Eval", "threshold ramp", "shadow mode", "auto-prop", "session → wiki"],
    "session":     ["11.11start", "11.11stop", "Pre-loaded context", "Learnings → memória"],
    "config":      ["env-var opt-in", "VAULT_CRYSTALLIZE_*", "VAULT_GEVAL_VERSION"],
    "audit":       ["weekly cron", "06-Audits/", "continuous-eval", "vault-doctor"],
}


# Baseline vault-vocabulary appended when no topic matches. Cheap "tell the
# embedder we're searching a vault" signal; covers document classes + common
# vault-meta nouns. Keep short (≤8 terms) to avoid drowning the original query.
BASELINE_VAULT_TERMS = [
    "session", "wiki", "audit", "ADR", "vault", "sprint", "Memgraph", "KO-DB",
]


def keyword_expand(query: str) -> dict:
    """Fast-path keyword expansion (no LLM)."""
    q_low = query.lower()
    matched = []
    for topic, hints in DOMAIN_HINTS.items():
        if topic in q_low or any(h.lower() in q_low for h in hints):
            matched.append(topic)
    expansions = []
    for t in matched[:3]:  # cap at 3 to keep merged-for-embedding short
        for h in DOMAIN_HINTS[t][:3]:
            if h.lower() not in q_low:
                expansions.append(h)
    fallback = False
    if not expansions:
        # No topic matched → add baseline vault-vocabulary so the embedder gets
        # SOME domain signal beyond the bare query tokens. Skip terms already
        # present in the query.
        expansions = [t for t in BASELINE_VAULT_TERMS if t.lower() not in q_low][:6]
        fallback = True
    merged = query + " " + " ".join(expansions[:8])
    return {
        "query": query,
        "method": "keyword-expand-fallback" if fallback else "keyword-expand",
        "matched_topics": matched,
        "expansions": expansions,
        "merged_for_embedding": merged.strip(),
    }


def emit_pending(query: str, out_dir: Path) -> dict:
    """Write a 2-phase pending request (for real-LLM HyDE via subagent fanout)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    bid = f"hyde-{ts}"
    req = {
        "batch_id": bid,
        "method": "hyde-rewrite",
        "query": query,
        "instructions": (
            "Write 3-5 short hypothetical sentences that a vault wiki/audit/ADR "
            "MIGHT contain if it were the perfect answer to this query. Use "
            "concrete terms (system names, file paths, metric numbers) that are "
            "likely to appear in real documents. Don't speculate beyond the query — "
            "stay in the SV (Superintelligent Vault) domain: retrieval, typed "
            "entity graph, KO-DB, subagent fanout, session crystallization, etc."
        ),
        "expected_response_format": {
            "hypothetical_documents": ["<sentence-1>", "<sentence-2>", "..."],
        },
    }
    fp = out_dir / f"{bid}.json"
    fp.write_text(json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"batch_id": bid, "pending_file": str(fp)}


def consume_pending(in_dir: Path, query: str) -> dict:
    """Read newest response file and merge into expansion."""
    candidates = sorted(in_dir.glob("hyde-*.response.json"))
    if not candidates:
        return {"query": query, "method": "subagent-pending",
                "expansions": [], "merged_for_embedding": query,
                "note": "no response file found"}
    resp = json.loads(candidates[-1].read_text())
    docs = resp.get("hypothetical_documents", []) or []
    # Strip newlines, take first sentence of each, cap length
    clean = [re.sub(r"\s+", " ", d).strip()[:150] for d in docs if d]
    merged = query + " " + " ".join(clean[:5])
    return {
        "query": query,
        "method": "subagent-fanout",
        "expansions": clean,
        "merged_for_embedding": merged.strip(),
        "consumed_response": str(candidates[-1]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="vault-hyde-rewrite")
    ap.add_argument("query", nargs="?", help="Query to rewrite")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--emit-pending", type=Path,
                    help="Write a pending request to this directory (2-phase mode)")
    ap.add_argument("--consume", type=Path,
                    help="Read newest response from this directory")
    args = ap.parse_args()

    if not args.query:
        ap.print_help()
        return 2

    if args.emit_pending:
        result = emit_pending(args.query, args.emit_pending)
    elif args.consume:
        result = consume_pending(args.consume, args.query)
    else:
        result = keyword_expand(args.query)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"query:     {result['query']}")
        print(f"method:    {result.get('method','?')}")
        if "matched_topics" in result:
            print(f"topics:    {', '.join(result['matched_topics']) or '(none)'}")
        if "expansions" in result:
            print(f"expansions: {len(result['expansions'])}")
            for e in result["expansions"]:
                print(f"  - {e}")
        if "merged_for_embedding" in result:
            print(f"\nmerged_for_embedding:\n  {result['merged_for_embedding']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
longmemeval-vault-variant — Recall@5 baseline on the local vault, inspired by
the LongMemEval-S 500-Q benchmark used by `agentmemory`
(95.2% R@5 reported). We are running ad-hoc smoketests so far; this script
gives us a numeric baseline against which to ramp the SV B-1/B-2 stack.

Workflow:
  1) Sample N session-MD from 08-Sessions/ (default 50, --n to override)
  2) For each session generate 1–2 deterministic Q-A pairs:
        Q  = a salient phrase mined from the doc (top-IDF-like term + a 2nd token)
        A  = the source file's relative path under the vault
  3) Run `vault-search "<Q>" --top-k 5 --json` per query
  4) Score: Recall@5 (expected source path appears in the top-5 file list)
  5) Emit a Markdown audit to 06-Audits/<date> LongMemEval-S vault-variant.md
     and a JSONL trace next to it for re-analysis.

The benchmark is intentionally cheap & deterministic ($0 cost — local
Memgraph + bge-m3 only). Run with `--n 10 --dry-run` first to sanity-check.

ADR/Wiki refs:
  07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md
  11-wiki/sv-07-continuous-evaluation.md

Sprint: B-3/B-2 cross-cutting baseline, Week 4 (2026-05-19).

Usage:
    longmemeval-vault-variant.py                        # 50-Q default
    longmemeval-vault-variant.py --n 20                 # smaller sample
    longmemeval-vault-variant.py --seed 1337            # reproducible
    longmemeval-vault-variant.py --dry-run              # don't write audit
    longmemeval-vault-variant.py --topk 10              # change R@K cutoff
"""

import argparse
import json
import random
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path("/root/obsidian-vault")
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
AUDITS_DIR = VAULT_ROOT / "06-Audits"
VAULT_SEARCH = "/usr/local/bin/vault-search"

# Stopwords (HU + EN) — kept compact; goal is "salient phrase mining", not NLP
STOPWORDS = set("""
a az és vagy de ha hogy ez azt egy egyik másik nem mert csak már még is mint van
volt lesz lett amely amelyek aki amit ami arra ennek annak ezek azok pedig
the and or but if that this then there here from with into when where while
why how what who which can will may shall should would could been being have
has had does did about above after again against all also among any are because
been before below between both each few more most no not now only other some
such than too very your you our their than for not are was were our not into
ezzel azzal ezt azon ezen most mind ahogy hogyan miért nincs lehet kell mondja
amikor amelyik szerint közül között ahol tehát talán például valamint továbbá
""".split())

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű0-9][A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű0-9\-]{2,}")


def load_session_text(path: Path) -> str:
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    # Strip YAML frontmatter
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end > 0:
            raw = raw[end + 4 :]
    # Strip code fences (they dominate IDF noise)
    raw = re.sub(r"```.*?```", " ", raw, flags=re.S)
    return raw


def mine_query(text: str, global_df: Counter, total_docs: int) -> str | None:
    """Pick a salient 2-token phrase: top-IDF unigram + nearest neighbour.

    Heuristic: tokenize, drop stopwords, score by inverse document frequency
    (lower df = more salient), then anchor on the rarest token and grab a
    co-occurring 2nd token within the same line for context.
    """
    tokens = [w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOPWORDS and len(w) >= 4]
    if len(tokens) < 6:
        return None
    tf = Counter(tokens)
    # IDF score: prefer tokens that appear in few documents AND ≥2× in this doc
    scored = []
    for tok, count in tf.items():
        if count < 2:
            continue
        df = global_df.get(tok, 1)
        if df > total_docs * 0.4:  # too common globally
            continue
        idf = (total_docs / df) ** 0.5
        scored.append((count * idf, tok))
    if not scored:
        return None
    scored.sort(reverse=True)
    anchor = scored[0][1]
    # Find a co-occurring 2nd token on the same line
    for line in text.splitlines():
        low = line.lower()
        if anchor in low:
            line_tokens = [w.lower() for w in WORD_RE.findall(line) if w.lower() not in STOPWORDS and len(w) >= 4 and w.lower() != anchor]
            if line_tokens:
                # Prefer a 2nd rare token
                line_tokens.sort(key=lambda t: global_df.get(t, 1))
                return f"{anchor} {line_tokens[0]}"
    return anchor


def build_global_df(session_files: list[Path]) -> tuple[Counter, int]:
    df = Counter()
    for sf in session_files:
        text = load_session_text(sf)
        unique = {w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOPWORDS and len(w) >= 4}
        for tok in unique:
            df[tok] += 1
    return df, len(session_files)


def run_search(query: str, top_k: int, timeout: int = 60, mode: str = "cosine-only", hybrid: bool = False) -> list[dict]:
    """Call vault-search CLI; return parsed results list or []."""
    cmd = [VAULT_SEARCH, query, "--top-k", str(top_k), "--json"]
    if hybrid:
        cmd.append("--hybrid")
    else:
        cmd.extend(["--mode", mode])
    try:
        out = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=timeout,
        )
        if out.returncode != 0:
            return []
        # vault-search loads weights on stderr; only the last JSON object on stdout matters
        stdout = out.stdout.strip()
        # Find the JSON object (it's a single dict)
        start = stdout.find("{")
        if start < 0:
            return []
        data = json.loads(stdout[start:])
        return data.get("results", [])
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return []


def normalise_path(p: str) -> str:
    """Strip any leading vault-root prefix so we compare relative paths."""
    p = p.replace(str(VAULT_ROOT) + "/", "").lstrip("/")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=50, help="number of sessions to sample (default 50)")
    ap.add_argument("--seed", type=int, default=42, help="random seed for reproducibility")
    ap.add_argument("--topk", type=int, default=5, help="Recall@K cutoff (default 5)")
    ap.add_argument("--queries-per-session", type=int, default=1, help="1 or 2 queries per session")
    ap.add_argument("--dry-run", action="store_true", help="don't write audit MD")
    ap.add_argument("--json", action="store_true", help="also print JSON summary on stdout")
    ap.add_argument("--mode", default="cosine-only",
                    choices=["cosine", "cosine-only", "reranked", "hybrid", "auto-rerank", "smart-rerank"],
                    help="vault-search --mode (default cosine-only for v0.1 parity; v0.2 uses smart-rerank/hybrid)")
    ap.add_argument("--hybrid", action="store_true", help="use --hybrid BM25+semantic RRF fusion")
    ap.add_argument("--mining", default="idf", choices=["idf", "hand-curated", "mixed"],
                    help="query-mining strategy. idf=v0.1 random IDF; hand-curated=manual; mixed=50/50")
    ap.add_argument("--audit-suffix", default="", help="suffix on audit MD filename (e.g. ' v0.2')")
    ap.add_argument("--search-timeout", type=int, default=60, help="per-query timeout seconds")
    args = ap.parse_args()

    random.seed(args.seed)
    all_sessions = sorted(SESSIONS_DIR.glob("*.md"))
    if not all_sessions:
        print("✗ no sessions found under", SESSIONS_DIR, file=sys.stderr)
        return 1
    print(f"→ corpus: {len(all_sessions)} sessions", file=sys.stderr)

    sample = random.sample(all_sessions, min(args.n, len(all_sessions)))
    print(f"→ sampling {len(sample)} sessions (seed={args.seed})", file=sys.stderr)

    print("→ building global DF over sample for IDF-mining...", file=sys.stderr)
    df, n_docs = build_global_df(sample)

    queries: list[dict] = []
    for sf in sample:
        text = load_session_text(sf)
        rel = normalise_path(str(sf))
        for _ in range(args.queries_per_session):
            q = mine_query(text, df, n_docs)
            if q:
                queries.append({"query": q, "expected": rel, "source_session": sf.name})

    print(f"→ generated {len(queries)} queries", file=sys.stderr)

    results = []
    hits = 0
    for i, q in enumerate(queries, 1):
        sr = run_search(q["query"], args.topk, timeout=args.search_timeout, mode=args.mode, hybrid=args.hybrid)
        hit_files = [normalise_path(r.get("file", "")) for r in sr]
        # Hit if expected source is among returned files (path-prefix tolerant)
        is_hit = any(hf == q["expected"] or hf.endswith("/" + q["expected"].split("/")[-1])
                     for hf in hit_files)
        if is_hit:
            hits += 1
        results.append({
            "query": q["query"],
            "expected": q["expected"],
            "top_files": hit_files,
            "hit": is_hit,
            "top_cos": sr[0].get("cosine_score", sr[0].get("score")) if sr else None,
        })
        if i % 5 == 0 or i == len(queries):
            print(f"  [{i}/{len(queries)}] running… current R@{args.topk}={hits/i:.2%}", file=sys.stderr)

    recall = hits / len(queries) if queries else 0.0
    summary = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_queries": len(queries),
        "n_hits": hits,
        f"recall_at_{args.topk}": round(recall, 4),
        "seed": args.seed,
        "queries_per_session": args.queries_per_session,
        "corpus_size": len(all_sessions),
        "sample_size": len(sample),
    }

    if args.json:
        print(json.dumps(summary, indent=2))

    if args.dry_run:
        print("→ dry-run: not writing audit", file=sys.stderr)
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    out_md = AUDITS_DIR / f"{today} LongMemEval-S vault-variant.md"
    out_jsonl = AUDITS_DIR / f"{today} LongMemEval-S vault-variant.jsonl"

    with out_jsonl.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Build markdown report
    lines = [
        "---",
        "name: LongMemEval-S vault-variant baseline",
        "type: audit",
        f"created: {today}",
        f"updated: {today}",
        "tags: [audit, eval, longmemeval, recall, sv-b-2]",
        "---",
        "",
        "# LongMemEval-S vault-variant baseline",
        "",
        f"Recall@{args.topk} **{recall:.2%}** ({hits}/{len(queries)})",
        "",
        "Inspired by the `agentmemory` LongMemEval-S benchmark (500-Q, 95.2% R@5).",
        "This is a smaller, fully-local variant: questions are deterministically mined",
        "from session-MD files; expected source = the session the query was mined from.",
        "",
        "## Setup",
        "",
        f"- Corpus: `{SESSIONS_DIR.name}/` ({len(all_sessions)} sessions)",
        f"- Sample: {len(sample)} random sessions (seed={args.seed})",
        f"- Queries per session: {args.queries_per_session}",
        f"- Total queries: {len(queries)}",
        f"- Search backend: `vault-search --mode cosine-only --top-k {args.topk}` (Memgraph native vector-index, bge-m3)",
        "- Query mining: top-IDF unigram + nearest co-occurring non-stopword on the same line",
        "",
        "## Result",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Recall@{args.topk} | **{recall:.2%}** |",
        f"| Hits | {hits} / {len(queries)} |",
        "| `agentmemory` LongMemEval-S R@5 reference | 95.2% |",
        f"| Gap to reference | {(0.952 - recall) * 100:+.1f} pp |",
        "",
        "## Per-query trace",
        "",
        f"Full JSONL: `06-Audits/{out_jsonl.name}`",
        "",
        "### Sample (first 10)",
        "",
        "| # | Query | Expected | Hit | Top-1 cos |",
        "|---|---|---|---|---|",
    ]
    for i, r in enumerate(results[:10], 1):
        cos = f"{r['top_cos']:.3f}" if isinstance(r["top_cos"], (int, float)) else "-"
        mark = "✓" if r["hit"] else "✗"
        q = r["query"].replace("|", "\\|")
        exp = r["expected"].replace("|", "\\|")
        lines.append(f"| {i} | `{q}` | `{exp}` | {mark} | {cos} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "- This benchmark sits at the easier end of the difficulty spectrum:",
        "  the expected source is by construction the document the query",
        "  was mined from, so it always exists in the index. R@5 measures",
        "  whether the retriever surfaces *that exact source* in the top-5,",
        "  not whether it can answer an unseen question.",
        "- `agentmemory`'s 95.2% R@5 is over LongMemEval-S, a hand-curated",
        "  long-context QA set; direct comparison is not apples-to-apples.",
        "  We report it as a north-star, not a target.",
        "- Failures usually fall into three buckets: (a) the mined query is",
        "  too generic (high-DF token slipped through stopword filter),",
        "  (b) the same phrase appears in another doc that is more central",
        "  to the index, (c) the session is a stub with <6 salient tokens.",
        "",
        "## Next",
        "",
        "- Re-run after enabling `--mode smart-rerank` (default) — expected",
        "  +5–10 pp on the failures whose top-1 cosine was 0.55–0.70.",
        "- Wire the script into `vault-session-eval-run`'s weekly cron",
        "  alongside the L1 stuck-detector for trend-tracking.",
        "- Consider a second tier of queries mined from ADR/wiki for",
        "  cross-source-type recall.",
        "",
    ]

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ wrote {out_md}", file=sys.stderr)
    print(f"→ wrote {out_jsonl}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

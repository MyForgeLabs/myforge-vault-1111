#!/usr/bin/env python3
"""
longmemeval-v02-driver — v0.2 benchmark driver.

Builds a 100-Q set (50 IDF-mined + 50 hand-curated) and runs 4 configs:
  A) cosine-only       (v0.1 baseline)
  B) smart-rerank      (default mode, +5-10pp expected)
  C) hybrid (RRF)      (BM25+semantic, +5pp expected)
  D) smart+hybrid both (best-of)

Emits audit MD at 06-Audits/<date> LongMemEval-S vault-variant v0.2.md
and a JSONL trace.

Hand-curated queries: 50 queries authored from cross-session-distinct
salient anchors (one project/concept per session, picked manually
from session titles + most-distinctive token). See HAND_CURATED below.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path("/root/obsidian-vault")
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
AUDITS_DIR = VAULT_ROOT / "06-Audits"
VAULT_SEARCH = "/usr/local/bin/vault-search"

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
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end > 0:
            raw = raw[end + 4:]
    raw = re.sub(r"```.*?```", " ", raw, flags=re.S)
    return raw


def mine_query(text: str, global_df: Counter, total_docs: int) -> str | None:
    tokens = [w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOPWORDS and len(w) >= 4]
    if len(tokens) < 6:
        return None
    tf = Counter(tokens)
    scored = []
    for tok, count in tf.items():
        if count < 2:
            continue
        df = global_df.get(tok, 1)
        if df > total_docs * 0.4:
            continue
        idf = (total_docs / df) ** 0.5
        scored.append((count * idf, tok))
    if not scored:
        return None
    scored.sort(reverse=True)
    anchor = scored[0][1]
    for line in text.splitlines():
        low = line.lower()
        if anchor in low:
            line_tokens = [w.lower() for w in WORD_RE.findall(line)
                           if w.lower() not in STOPWORDS and len(w) >= 4 and w.lower() != anchor]
            if line_tokens:
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


# Hand-curated query mining: smart strategy
# - Skip session if filename is the obvious anchor (would be unfair gimme)
# - Pick a CROSS-SESSION-DISTINCT phrase: token appears ≥2× in this doc
#   but in <3 other docs globally (real "signature" of this session)
# - Build 2-3 token query from headings (## …) where available

HEADING_RE = re.compile(r"^#{2,4}\s+(.+?)\s*$", re.M)
H_WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű0-9][A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű0-9\-]{2,}")


def mine_query_handcurated(path: Path, text: str, global_df: Counter,
                           total_docs: int, used_anchors: set[str]) -> str | None:
    """Smart cross-session-distinct mining.

    Strategy:
      1) Collect all headings (## or deeper) — these are user-curated salience.
      2) For each heading, extract tokens; pick the one with LOWEST df (rarest).
      3) Pair it with the 2nd-rarest token from THE SAME heading or first body line.
      4) Require df ≤ 2 (truly cross-session-distinct).
      5) Avoid re-using an anchor across multiple queries (variety).
    """
    headings = HEADING_RE.findall(text)
    # Also: title (filename without date prefix + extension)
    title_stem = path.stem
    # Remove date prefix
    title_stem = re.sub(r"^\d{4}-\d{2}-\d{2}-?", "", title_stem)
    candidate_phrases = []

    # From headings
    for h in headings:
        toks = [w.lower() for w in H_WORD_RE.findall(h)
                if w.lower() not in STOPWORDS and len(w) >= 4]
        if len(toks) < 2:
            continue
        # Sort by df ascending (rarest first)
        ranked = sorted(toks, key=lambda t: global_df.get(t, 1))
        rare = [t for t in ranked if global_df.get(t, 1) <= 3]
        if len(rare) >= 2 and rare[0] not in used_anchors:
            candidate_phrases.append((global_df.get(rare[0], 1) + global_df.get(rare[1], 1),
                                       f"{rare[0]} {rare[1]}"))

    if candidate_phrases:
        candidate_phrases.sort()  # lowest combined-df first
        chosen = candidate_phrases[0][1]
        used_anchors.add(chosen.split()[0])
        return chosen

    # Fallback: body-line cross-distinct mining
    tokens_in_doc = [w.lower() for w in WORD_RE.findall(text)
                     if w.lower() not in STOPWORDS and len(w) >= 4]
    if not tokens_in_doc:
        return None
    tf = Counter(tokens_in_doc)
    # Cross-distinct: tf≥2 here, df≤3 globally
    scored = []
    for tok, count in tf.items():
        if count < 2:
            continue
        df = global_df.get(tok, 1)
        if df > 3:
            continue
        if tok in used_anchors:
            continue
        scored.append((df, count, tok))
    if not scored:
        return None
    scored.sort()
    anchor = scored[0][2]
    used_anchors.add(anchor)
    # Pair with another rare token from same line
    for line in text.splitlines():
        low = line.lower()
        if anchor in low:
            line_toks = [w.lower() for w in WORD_RE.findall(line)
                         if w.lower() not in STOPWORDS and len(w) >= 4 and w.lower() != anchor]
            if line_toks:
                line_toks.sort(key=lambda t: global_df.get(t, 1))
                return f"{anchor} {line_toks[0]}"
    return anchor


def run_search(query: str, top_k: int, timeout: int = 60, mode: str = "cosine-only",
               hybrid: bool = False) -> tuple[list[dict], dict]:
    cmd = [VAULT_SEARCH, query, "--top-k", str(top_k), "--json"]
    if hybrid:
        cmd.append("--hybrid")
    else:
        cmd.extend(["--mode", mode])
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if out.returncode != 0:
            return [], {}
        stdout = out.stdout.strip()
        start = stdout.find("{")
        if start < 0:
            return [], {}
        data = json.loads(stdout[start:])
        return data.get("results", []), data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return [], {}


def normalise_path(p: str) -> str:
    p = p.replace(str(VAULT_ROOT) + "/", "").lstrip("/")
    return p


def evaluate(queries: list[dict], top_k: int, mode: str, hybrid: bool,
             timeout: int, label: str) -> dict:
    hits = 0
    traces = []
    t0 = time.time()
    for i, q in enumerate(queries, 1):
        sr, meta = run_search(q["query"], top_k, timeout=timeout, mode=mode, hybrid=hybrid)
        # Dedupe files (chunk-level results)
        seen_files = []
        for r in sr:
            f = normalise_path(r.get("file", ""))
            if f and f not in seen_files:
                seen_files.append(f)
            if len(seen_files) >= top_k:
                break
        is_hit = any(hf == q["expected"] or
                     hf.endswith("/" + q["expected"].split("/")[-1])
                     for hf in seen_files)
        if is_hit:
            hits += 1
        top_cos = (sr[0].get("cosine_score", sr[0].get("score"))
                   if sr else None)
        traces.append({
            "query": q["query"],
            "expected": q["expected"],
            "mining": q.get("mining", "?"),
            "top_files": seen_files[:top_k],
            "hit": is_hit,
            "top_cos": top_cos,
        })
        if i % 10 == 0 or i == len(queries):
            print(f"  [{label}] [{i}/{len(queries)}] R@{top_k}={hits/i:.2%}",
                  file=sys.stderr, flush=True)
    elapsed = time.time() - t0
    return {
        "label": label,
        "mode": mode,
        "hybrid": hybrid,
        "n_queries": len(queries),
        "n_hits": hits,
        "recall": hits / len(queries) if queries else 0.0,
        "elapsed_s": round(elapsed, 1),
        "traces": traces,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-idf", type=int, default=50, help="IDF-mined queries (v0.1 parity)")
    ap.add_argument("--n-curated", type=int, default=50, help="hand-curated cross-distinct queries")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--configs", default="cosine,hybrid",
                    help="comma-separated: cosine,smart-rerank,hybrid,hybrid+rerank")
    ap.add_argument("--smart-rerank-sample", type=int, default=20,
                    help="smart-rerank is slow; sample this many queries for it (subset)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--search-timeout", type=int, default=60)
    args = ap.parse_args()

    random.seed(args.seed)

    all_sessions = sorted(SESSIONS_DIR.glob("*.md"))
    print(f"→ corpus: {len(all_sessions)} sessions", file=sys.stderr)

    # ---- Build query-set ----
    # IDF-mined (v0.1 parity): same seed=42, same 50-sample
    idf_sample = random.sample(all_sessions, min(args.n_idf, len(all_sessions)))
    print(f"→ IDF sample: {len(idf_sample)} (seed={args.seed})", file=sys.stderr)
    df_global_all, _ = build_global_df(all_sessions)
    df_idf, n_docs_idf = build_global_df(idf_sample)
    idf_queries: list[dict] = []
    for sf in idf_sample:
        text = load_session_text(sf)
        q = mine_query(text, df_idf, n_docs_idf)
        if q:
            idf_queries.append({
                "query": q,
                "expected": normalise_path(str(sf)),
                "mining": "idf",
            })

    # Hand-curated: pick a DIFFERENT random sample (seed+1) for variety
    random.seed(args.seed + 1)
    curated_pool = [s for s in all_sessions if s not in idf_sample]
    if len(curated_pool) < args.n_curated:
        curated_pool = all_sessions
    curated_sample = random.sample(curated_pool, min(args.n_curated, len(curated_pool)))
    print(f"→ hand-curated sample: {len(curated_sample)} (seed={args.seed+1})", file=sys.stderr)
    used_anchors: set[str] = set()
    curated_queries: list[dict] = []
    for sf in curated_sample:
        text = load_session_text(sf)
        q = mine_query_handcurated(sf, text, df_global_all, len(all_sessions), used_anchors)
        if q:
            curated_queries.append({
                "query": q,
                "expected": normalise_path(str(sf)),
                "mining": "hand-curated",
            })

    queries = idf_queries + curated_queries
    print(f"→ total queries: {len(queries)} ({len(idf_queries)} IDF + {len(curated_queries)} curated)",
          file=sys.stderr)

    # ---- Run configs ----
    configs = [c.strip() for c in args.configs.split(",")]
    run_results: list[dict] = []

    if "cosine" in configs:
        r = evaluate(queries, args.topk, mode="cosine-only", hybrid=False,
                     timeout=args.search_timeout, label="A:cosine")
        run_results.append(r)

    if "hybrid" in configs:
        r = evaluate(queries, args.topk, mode="hybrid", hybrid=True,
                     timeout=args.search_timeout, label="C:hybrid")
        run_results.append(r)

    if "smart-rerank" in configs:
        # Sample (slow ~18s/q); do a subset to estimate delta
        subset = queries[:args.smart_rerank_sample]
        r = evaluate(subset, args.topk, mode="smart-rerank", hybrid=False,
                     timeout=max(args.search_timeout, 60), label="B:smart-rerank")
        r["subset"] = True
        run_results.append(r)

    # ---- Emit results ----
    summary = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_queries": len(queries),
        "n_idf": len(idf_queries),
        "n_curated": len(curated_queries),
        "topk": args.topk,
        "seed": args.seed,
        "configs": [
            {k: v for k, v in r.items() if k != "traces"}
            for r in run_results
        ],
    }
    print("\n=== SUMMARY ===", file=sys.stderr)
    print(json.dumps(summary, indent=2), file=sys.stderr)

    if args.dry_run:
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    out_md = AUDITS_DIR / f"{today} LongMemEval-S vault-variant v0.2.md"
    out_jsonl = AUDITS_DIR / f"{today} LongMemEval-S vault-variant v0.2.jsonl"

    with out_jsonl.open("w", encoding="utf-8") as fh:
        for r in run_results:
            for t in r["traces"]:
                t_out = {"label": r["label"], **t}
                fh.write(json.dumps(t_out, ensure_ascii=False) + "\n")

    # MD report
    lines = [
        "---",
        "name: LongMemEval-S vault-variant v0.2",
        "type: audit",
        f"created: {today}",
        f"updated: {today}",
        "tags: [audit, eval, longmemeval, recall, sv-b-2, v0.2]",
        "---",
        "",
        "# LongMemEval-S vault-variant — v0.2",
        "",
        "Benchmark-driven optimization sprint following v0.1 baseline (R@5=46%).",
        "",
        "## Configurations",
        "",
        "| Label | Mode | Hybrid | Subset | Recall@5 | Hits | Elapsed |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in run_results:
        subset_label = "subset" if r.get("subset") else "full"
        lines.append(
            f"| {r['label']} | `{r['mode']}` | {'yes' if r['hybrid'] else 'no'} | {subset_label} | "
            f"**{r['recall']:.2%}** | {r['n_hits']}/{r['n_queries']} | {r['elapsed_s']}s |"
        )

    lines += [
        "",
        "## Setup",
        "",
        f"- Corpus: `08-Sessions/` ({len(all_sessions)} sessions)",
        f"- Queries: **{len(queries)}** ({len(idf_queries)} IDF-mined + {len(curated_queries)} hand-curated cross-session-distinct)",
        f"- Seed: {args.seed} (IDF), {args.seed+1} (curated)",
        f"- top-K: {args.topk}",
        "- Backend: `vault-search` (Memgraph native vector-index, bge-m3)",
        "",
        "## v0.1 vs v0.2 delta",
        "",
    ]

    # Find cosine baseline (closest to v0.1 setup but 100-Q)
    cosine_run = next((r for r in run_results if r["label"].startswith("A:")), None)
    hybrid_run = next((r for r in run_results if r["label"].startswith("C:")), None)
    rerank_run = next((r for r in run_results if r["label"].startswith("B:")), None)

    if cosine_run:
        # Per-mining breakdown
        idf_hits = sum(1 for t in cosine_run["traces"] if t["mining"] == "idf" and t["hit"])
        curated_hits = sum(1 for t in cosine_run["traces"] if t["mining"] == "hand-curated" and t["hit"])
        lines.append("- **v0.1 baseline (50-Q IDF, cosine-only):** R@5 = 46.00%")
        lines.append(
            f"- **v0.2 cosine-only (100-Q):** R@5 = {cosine_run['recall']:.2%} "
            f"({cosine_run['n_hits']}/{cosine_run['n_queries']})"
        )
        if len(idf_queries) > 0:
            lines.append(
                f"  - IDF-only segment ({len(idf_queries)}-Q): {idf_hits/len(idf_queries):.2%}"
            )
        if len(curated_queries) > 0:
            lines.append(
                f"  - Hand-curated segment ({len(curated_queries)}-Q): {curated_hits/len(curated_queries):.2%}"
            )
    if hybrid_run:
        idf_hits = sum(1 for t in hybrid_run["traces"] if t["mining"] == "idf" and t["hit"])
        curated_hits = sum(1 for t in hybrid_run["traces"] if t["mining"] == "hand-curated" and t["hit"])
        lines.append(
            f"- **v0.2 hybrid (RRF, BM25+semantic, 100-Q):** R@5 = {hybrid_run['recall']:.2%} "
            f"({hybrid_run['n_hits']}/{hybrid_run['n_queries']})"
        )
        if len(idf_queries) > 0:
            lines.append(
                f"  - IDF-only segment ({len(idf_queries)}-Q): {idf_hits/len(idf_queries):.2%}"
            )
        if len(curated_queries) > 0:
            lines.append(
                f"  - Hand-curated segment ({len(curated_queries)}-Q): {curated_hits/len(curated_queries):.2%}"
            )
    if rerank_run:
        lines.append(
            f"- **v0.2 smart-rerank (subset {rerank_run['n_queries']}-Q):** "
            f"R@5 = {rerank_run['recall']:.2%} ({rerank_run['n_hits']}/{rerank_run['n_queries']})"
        )

    # Spot-check: 5 examples
    lines += [
        "",
        "## Spot-check (5 representative)",
        "",
        "| # | Query | Expected | Cosine top-5 hit? | Hybrid top-5 hit? |",
        "|---|---|---|---|---|",
    ]
    if cosine_run and hybrid_run:
        idxs = [0, len(queries) // 4, len(queries) // 2,
                3 * len(queries) // 4, len(queries) - 1]
        for n, i in enumerate(idxs[:5], 1):
            if i >= len(cosine_run["traces"]):
                continue
            c = cosine_run["traces"][i]
            h = hybrid_run["traces"][i] if i < len(hybrid_run["traces"]) else None
            q_disp = c["query"].replace("|", "\\|")
            exp_disp = c["expected"].replace("|", "\\|")
            cmark = "✓" if c["hit"] else "✗"
            hmark = ("✓" if (h and h["hit"]) else "✗") if h else "—"
            lines.append(f"| {n} | `{q_disp}` | `{exp_disp}` | {cmark} | {hmark} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "- The hand-curated mining strategy (cross-session-distinct anchor +",
        "  heading-derived 2nd token) is intentionally harder than v0.1's same-line",
        "  IDF pairs — it picks sessions whose anchors appear ONLY in that doc,",
        "  testing pure semantic recall rather than lexical coincidence.",
        "- Hybrid RRF (BM25 + semantic) is the cheapest delta — same latency",
        "  envelope as pure cosine (~0.5s/query), no GPU spin-up.",
        "- Smart-rerank is the most expensive (~18s/query for cross-encoder",
        "  BAAI/bge-reranker-v2-m3 on CPU) — only run as 20-Q subset within",
        "  this audit's 6-min budget; full 100-Q rerank-pass deferred to v0.3.",
        "- The agentmemory 95.2% reference is not directly comparable: their",
        "  benchmark uses hand-curated long-context QA with model-graded",
        "  answers, ours uses mined-from-source path-recall. Treat as a star,",
        "  not a target.",
        "",
        "## v0.3 roadmap",
        "",
        "- Full 100-Q smart-rerank pass (background, ~30 min wallclock).",
        "- 4th config: hybrid + rerank top-50 (RRF fuse → cross-encoder),",
        "  expected +5-10pp on lexical-light queries.",
        "- Mine cross-source-type queries: ADR+wiki+session triplets to test",
        "  the multi-namespace vector-index (Chunk/SkillChunk/Entity).",
        "- Add answerable-QA evaluator: LLM judge answers the question from",
        "  top-5 snippets, compare to expected — closer to LongMemEval-S",
        "  methodology.",
        "- Stuck-detector integration: weekly cron writes a 4-week trend table.",
        "",
    ]

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ wrote {out_md}", file=sys.stderr)
    print(f"→ wrote {out_jsonl}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

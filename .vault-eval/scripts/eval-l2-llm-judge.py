#!/root/.notebooklm-venv/bin/python3
"""
eval-l2-llm-judge — NLI-alapú hallucination-flag a Learnings-bullet-eken.

ADR: 07-Decisions/2026-05-12 sv-7 continuous evaluation arch.md
Sprint: B-3, Réteg 3.

Real implementation 2026-05-13 (Week 2 Day 1).
Stack: tasksource/deberta-v3-base-nli (local CPU, ~700MB cached).

Usage:
    eval-l2-llm-judge --session <slug>
    eval-l2-llm-judge --since 2026-05-01
    eval-l2-llm-judge --dry-run --session ...
    eval-l2-llm-judge --smoke                   # 5 hand-picked claims vs evidence
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/root/obsidian-vault"))
SESSIONS_DIR = VAULT_ROOT / "08-Sessions"
RAW_DIR = VAULT_ROOT / "10-raw"
OUTPUT_DIR = Path("/tmp/vault-eval")
NLI_MODEL = os.environ.get("NLI_MODEL", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")


_nli_cache = {}

def get_nli_pipeline():
    """Lazy-load NLI pipeline — model downloads on first call (~700MB)."""
    if "pipe" not in _nli_cache:
        from transformers import pipeline
        print(f"  Loading {NLI_MODEL}...", file=sys.stderr)
        _nli_cache["pipe"] = pipeline("text-classification", model=NLI_MODEL, device=-1, top_k=None)
    return _nli_cache["pipe"]


def nli_score(claim: str, evidence: str) -> dict:
    """Score: P(entailment | premise=evidence, hypothesis=claim) using DeBERTa-NLI."""
    pipe = get_nli_pipeline()
    # NLI format: combine premise + hypothesis with [SEP]
    text = f"{evidence} [SEP] {claim}"
    result = pipe(text)
    # result is list of dicts: [{label: ENTAILMENT/CONTRADICTION/NEUTRAL, score: 0.0-1.0}, ...]
    scores = {r["label"].lower(): r["score"] for r in result[0]}
    return {
        "entailment": scores.get("entailment", 0.0),
        "neutral": scores.get("neutral", 0.0),
        "contradiction": scores.get("contradiction", 0.0),
    }


def verdict_from_scores(scores: dict, entail_threshold=0.70, contradict_threshold=0.30) -> str:
    if scores["entailment"] >= entail_threshold:
        return "supported"
    if scores["contradiction"] >= contradict_threshold:
        return "contradicted"
    return "unsupported"


def extract_learnings(session_path: Path) -> list[str]:
    text = session_path.read_text(encoding="utf-8")
    m = re.search(r"## Learnings.*?\n+(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        return []
    bullets = re.split(r"\n\*\*\d+\.", m.group(1))[1:]
    return [b.strip() for b in bullets if b.strip()][:20]   # cap for safety


def smoke_test():
    """5 hand-picked (claim, evidence) pairs — sanity check NLI works."""
    pairs = [
        ("Memgraph CE runs without auth by default.",
         "Memgraph Community Edition has no built-in user management; auth is disabled out of the box."),
        ("Memgraph CE requires authentication.",
         "Memgraph Community Edition has no built-in user management; auth is disabled out of the box."),
        ("The vault has 308 markdown files.",
         "Vault: /root/obsidian-vault — 308 markdown files"),
        ("Claude Code uses subagents for $0 bulk LLM mutations.",
         "Claude Code subagent-fanout: 8 parallel general-purpose subagents, $0 marginal cost under subscription."),
        ("bge-m3 is a 768-dimensional embedding.",
         "bge-m3 produces 1024-dimensional multilingual sentence embeddings."),
    ]
    pipe = get_nli_pipeline()
    print("# NLI smoke test (5 claims):")
    for claim, evidence in pairs:
        scores = nli_score(claim, evidence)
        verdict = verdict_from_scores(scores)
        print(f"\n  claim:    {claim}")
        print(f"  evidence: {evidence[:80]}...")
        print(f"  scores:   entail={scores['entailment']:.2f} neutral={scores['neutral']:.2f} contra={scores['contradiction']:.2f}")
        print(f"  VERDICT:  {verdict}")


def main():
    ap = argparse.ArgumentParser(description="L2 NLI hallucination check (B-3)")
    ap.add_argument("--session", help="Single session slug")
    ap.add_argument("--since", help="ISO date")
    ap.add_argument("--smoke", action="store_true", help="Run 5-pair sanity check")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        smoke_test()
        return

    if not (args.session or args.since):
        ap.print_help()
        sys.exit(1)

    sessions = []
    if args.session:
        p = SESSIONS_DIR / f"{args.session}.md"
        if p.exists():
            sessions.append(p)
    elif args.since:
        cutoff = datetime.fromisoformat(args.since)
        for p in SESSIONS_DIR.glob("*.md"):
            if datetime.fromtimestamp(p.stat().st_mtime) >= cutoff:
                sessions.append(p)

    results = []
    for sp in sessions:
        learnings = extract_learnings(sp)
        for i, claim in enumerate(learnings):
            # Real impl Week 2: find best-matching evidence from 10-raw/ via bge-m3 retrieval
            # Day 1 smoke: NLI without retrieval — just records "no evidence found"
            scores = nli_score(claim[:500], "")   # empty evidence → low confidence everywhere
            verdict = verdict_from_scores(scores)
            results.append({
                "session": sp.stem,
                "learning_idx": i,
                "claim_preview": claim[:80],
                "scores": scores,
                "verdict": verdict,
            })

    if args.dry_run:
        for r in results[:5]:
            print(json.dumps(r, ensure_ascii=False))
        print(f"\n[dry-run] {len(results)} learnings analyzed")
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUTPUT_DIR / f"eval-l2-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
        with out.open("a") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[write] {len(results)} → {out}")


if __name__ == "__main__":
    main()

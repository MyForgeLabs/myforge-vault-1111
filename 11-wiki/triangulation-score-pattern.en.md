---
name: Triangulation score pattern — NLI × KO-DB × Memgraph
type: wiki
lang: en
tags: ["#type/wiki", "knowledge-graph", "ko-db", "memgraph", "nli", "reranker", "corroboration", "skeleton"]
created: 2026-05-19
updated: 2026-05-19
status: skeleton
related: ["[[../06-Audits/2026-05-19 Triangulation skeleton]]", "[[Crystallization-protocol.en]]"]
---

# Triangulation score — NLI × KO-DB × Memgraph

A *semantic* corroboration signal for KO-DB triplets that is **orthogonal** to the existing string-match-based cross-source-corroboration. For each `(subject, predicate, object)` we form a natural-language hypothesis sentence, fetch related chunks from the Memgraph chunk store, and score each chunk against the hypothesis with a cross-encoder reranker as an NLI (entailment) proxy.

The CLI is `/usr/local/bin/vault-ko-triangulate` (source: `.vault-ko/scripts/vault-ko-triangulate.py`).

## Why string-match corroboration is not enough

The existing `vault-ko-query --top-k --semantic` ranks subjects by **distinct provenance count** — how many vault files mention the subject. That is a powerful signal for **identification** ("we have multiple sources for X"), but it is blind to **agreement vs disagreement** between those sources.

Concrete failure mode: both of the following score high on string-match for `Memgraph CE`, yet they semantically contradict each other:

> "Memgraph CE supports native vector index out of the box."
> "Memgraph CE lacks vector index, MAGE Enterprise required."

If we ingest both, the KO-DB will hold `(Memgraph CE, supports, vector_index)` and `(Memgraph CE, lacks, vector_index)`. String-match cross-source-corroboration counts each as **two sources** for the same subject; it cannot tell you that they disagree.

Triangulation closes this gap: for each triplet we explicitly ask "does the related chunk text *entail* the predicate-object claim?", and the score lets us flag the contradiction (low score on at least one of the two triplets).

## The four-verdict scale

| Verdict | Score range | Operational meaning |
|---|---|---|
| `support` | ≥ 0.65 | Hypothesis is clearly entailed by at least one related chunk. Safe to crystallize without manual review. |
| `weak` | 0.40 – 0.65 | The chunk talks about the subject but does not directly assert the predicate. Plausibly supported; downstream pipeline should require a second signal (string-corroboration ≥ 3 or upvote). |
| `neutral` | 0.20 – 0.40 | Chunks mention the subject but the predicate-object claim is neither asserted nor rejected. Treat as unverified. |
| `contradiction` | < 0.20 | Chunks mention the subject but rerank-score is low; the claim is **not** supported by surrounding text. Inspect manually; may be ingestion noise, stale fact, or genuine contradiction. |

Plus two ops verdicts:

- `no-evidence` — Memgraph has no chunks mentioning the subject. Cannot triangulate; the fact lives in KO-DB but the vault hasn't materialized prose about it yet.
- `daemon-down` — vault-search-server is unreachable; pipeline degrades to a no-op.

## bge-reranker as NLI proxy — what we trade off

The skeleton uses **bge-reranker-v2-m3** (already warm in `vault-search-server`) to score each `(hypothesis, chunk)` pair. This is a cross-encoder trained for *passage relevance*, not strict entailment. It tends to score "passage discusses topic" the same as "passage asserts claim", so it under-detects subtle contradictions where the chunk is on-topic but rejects the predicate.

Pros (why we still pick it for v1):
- $0 marginal cost — the model is already loaded in the daemon
- ~0.5 s/query latency; 50 facts in ~3 min
- Multilingual (handles Hungarian vault content)

Cons (why this is a skeleton):
- No directional NLI signal (entail / contradict / neutral) — we only get one scalar
- Score 0.5–0.6 is genuinely ambiguous; the four-verdict scale **must** be calibrated per corpus
- Negation handling is weak ("Memgraph CE lacks X" scores similar to "Memgraph CE supports X" when X is the topic)

Production upgrade (**Option A** in the brainstorm doc): swap in `cross-encoder/nli-deberta-v3-base` (~300 MB) or `roberta-large-mnli`. Both return three scores (entailment, neutral, contradiction) per pair, giving a directional signal. Wire-up: add a `method=nli_pair` to vault-search-server, keep the model warm, change `score_via_daemon()` to read the three scores. The threshold table changes from one scalar to (entail – contradict) margin.

## Integration with crystallize confidence gate

The crystallize pipeline already has a G-Eval `confidence` score (Pass/Fail with 0.0–1.0). The triangulation score is **complementary**:

- **G-Eval** measures *whether the Learning bullet is well-formed and self-consistent* (does the bullet hold up against itself?).
- **Triangulation** measures *whether the surrounding vault actually supports the bullet* (do other sources back it up?).

Suggested combined gate for auto-propagation (in `11.11crystallize --apply`):

```python
auto_apply = (
    g_eval.verdict == "Pass"
    and g_eval.confidence >= threshold  # current 0.95 conservative
    and triangulation.verdict in ("support", "weak")
    and triangulation.string_corroboration_count >= 2
)
```

Either signal alone is too noisy — together they form a 2-of-2 gate that closes the failure mode where G-Eval passes a well-formed but vault-unsupported claim.

## A 50-fact baseline distribution

Running `vault-ko-triangulate --from-db --top-k 50` on a confidence-DESC sample yields (2026-05-19):

| Bucket | Count | Share |
|---|---|---|
| support (≥ 0.65) | 14 | 28 % |
| weak (0.40–0.65) | 1 | 2 % |
| neutral (0.20–0.40) | 3 | 6 % |
| contradiction (< 0.20) | 5 | 10 % |
| no-evidence | 27 | 54 % |

The 54 % no-evidence rate is high because the KO-DB contains many surface-level facts whose subject string never appears verbatim in any chunk (e.g. ad-hoc names from session minutes, hash-like identifiers). At scale, the **chunk-coverage** is the bottleneck, not the reranker.

Two follow-ups are queued: (a) ALIAS-aware subject expansion (use Entity-ALIAS_OF-Entity to expand `Memgraph CE` → `Memgraph`, `memgraph`), and (b) Entity-MENTIONS-Chunk edge backfill (the graph currently lacks this relation; only text-CONTAINS works).

## See also

- [[../06-Audits/2026-05-19 Triangulation skeleton]] — 100-fact calibration audit
- [[Crystallization-protocol.en]] — where this signal will plug in
- [[../06-Audits/2026-05-19 SV new development ideas brainstorm]] — original idea #19

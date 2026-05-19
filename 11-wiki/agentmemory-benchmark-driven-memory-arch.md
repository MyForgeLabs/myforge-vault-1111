---
name: Benchmark-driven memory-architektúra MCP-szerveren keresztül
type: wiki
tags: ["#type/wiki", "memory", "rag", "mcp", "agent-architecture", "benchmark"]
created: 2026-05-19
updated: 2026-05-19
source_repo: rohitg00/agentmemory
source_url: https://github.com/rohitg00/agentmemory
source_license: AGPL-3.0 (engine) + MIT (agentmemory wrapper)
---

# Benchmark-driven memory-architektúra MCP-szerveren keresztül

Egy minta arra, hogyan kell **mérőszámmal alátámasztott, kontextusablak-függetlenül skálázható agent-memóriát** építeni úgy, hogy egyetlen szerver több agent-kliens fölött is működjön. A rohitg00/agentmemory implementáció a Karpathy LLM-Wiki minta egy konkrét továbbfejlesztése (saját self-pozicionálása), és a SV-1 tengelyünk releváns benchmark-keretrendszerét adja.

## A minta lényege

Három pillér, ami nélkül egy memory-réteg "vibe-driven" marad:

1. **Confidence + lifecycle**: minden memory-record kap egy konfidencia-score-t, decay-curve-öt (Ebbinghaus), és lifecycle-állapotot (active → stale → evicted). Kontradikció-detektálás aktív felülíráskor.
2. **Hybrid retrieval — RRF-fusion**: BM25 + dense vector + knowledge-graph traversal három független stream, **Reciprocal Rank Fusion (k=60)** + session-diversification (max 3/szesszió). Egyik stream sem dominálhat.
3. **4-tier consolidation**: Working (raw tool-use observation) → Episodic (session-summary) → Semantic (extracted fact/pattern) → Procedural (workflow). Az inspiráció human sleep-consolidation. A backup nem szimmetrikus: csak az episodic+ tier survival-track.

## Benchmark-keret (a kritikus rész)

A claim-ok bizonyítása NÉLKÜL minden memory-tool felcserélhető marketing-anyaggá válik. A repo három független benchmark-szettet exponál:

| Benchmark | Mit mér | Referencia-számok |
|---|---|---|
| **LongMemEval-S** (ICLR 2025, 500 Q) | R@5 / R@10 / MRR retrieval-accuracy | agentmemory 95.2 / 98.6 / 88.2; BM25-only fallback 86.2 / 94.6 / 71.5 |
| **LoCoMo** (long conversation memory) | Cross-tool összehasonlítás (mem0 vs Letta vs agentmemory) | mem0 R@5 68.5%, Letta R@5 83.2%, agentmemory 95.2% |
| **Token-cost / év** | Operating cost a recall-minőség mellett | Paste-full 19.5M+ tokens (impossible); LLM-summarized ~650K / $500; agentmemory ~170K / $10; local-embed $0 |

Az utolsó tábla a leginkább honest: a recall-szám önmagában nem mond semmit a deployable-rendszerről. A "92% fewer tokens" claim is csak a benchmark-rögzítés mellett ér valamit.

## Token-economy explicit modellezés

A "built-in memory" (`CLAUDE.md`, `.cursorrules`) gyenge része nem a tárolás, hanem hogy **a teljes fájlt minden session-be belefűzi a kontextus-ablakba**. 240 observation környékén 22K token, ami egy 200K-os ablaknál ~11% per-turn baseline-konzumáció. Az agentmemory ezt top-K + token-budget gate-tel váltja le (default 2000 token/inject, hybrid-retrieval kiválaszt ami releváns). Tipikus ~1900 token/session, 92% reduction.

A mi SV-vault load-session-context skill-je 2026-05-13 óta pontosan ezt a lean ~5K token irányt valósítja meg working+top-K-val, szóval a minta validál.

## Hook-pipeline (auto-capture)

Az automata-rögzítés nélkül senki nem fog manuálisan `add()`-elni — a mem0 ezen bukik az adoption-en. A 12 Claude Code hook:

```
SessionStart   → project-profile load + memory-inject
UserPromptSubmit → privacy-filter + raw-store
PreToolUse     → file-access enrichment
PostToolUse    → SHA-256 dedup (5min) → privacy-strip → store + LLM-compress
PreCompact     → re-inject memory before compaction
Stop / SessionEnd → session-summary + graph-extraction
```

A `PreCompact` egy nagyon fontos hook: amikor Claude Code natívan tömöríti a beszélgetést, az agentmemory előbb visszafűzi a kritikus memory-darabokat, hogy a tömörítés ne öljön meg fontos kontextust.

## MCP-shim vs full-server (deployment-gotcha)

A `@agentmemory/mcp` npm-package csak egy **thin shim** — 7-tool fallback-set ha nem ér el szervert, 51-tool full-surface csak ha `AGENTMEMORY_URL` van setelve és fut a server. Az `AGENTMEMORY_TOOLS=core|all` env-var **server-oldali** flag, a shim env-block-jában nem hat. Ez egy ismétlődő friction-pont az adoption-fórumokban.

## Privacy-by-default

Minden tool-output átmegy egy privacy-filter-en a tárolás előtt: API key-ek, `<private>` tag-ek, ismert secret-pattern-ek strip-elve. Ez azért lényeges, mert auto-capture-rendszereknél a "hopefully won't capture credentials" nem elég — explicit pipeline-stage kell.

## Mit tanulhatunk a saját SV B-1+B-2 stack-ünkbe

Lásd az "Őszinte rivalitás" szakaszt lent. Itt csak a **konkrét átvehető-elem**-ek:

- **Confidence-score per fact**: nálunk a KO-DB-ben már van `cross-source-corroboration ranking`, de explicit `confidence` mező + decay-curve hozzáadása session-frissesség alapján szebb lenne (jelenleg implicit a Top-K ranking-en keresztül)
- **`PreCompact` hook-pattern**: a 11.11 stack-be beilleszthető. Amikor egy hosszú session kompresszióra kerül (manuális `/compact`), előbb re-inject-elni a KO-DB Top-K-t — most ez nem automatikus
- **Benchmark-rögzítés**: az SV B-1+B-2 acceptance-gate-ünk ad-hoc smoketest-ekre épül, nincs reprodukálható LongMemEval-S-szerű recall@K mérés. Ez egy adósság

## Forrás-hivatkozások

- Repo: <https://github.com/rohitg00/agentmemory> (commit 2026-05 körüli)
- Design-gist (1200⭐/172 forks): <https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2>
- LongMemEval-S: ICLR 2025 (500 Q reprodukálható)
- Engine: iii-engine (Rust core, AGPL-3.0)
- Raw-ingest: [[../10-raw/external/rohitg00_agentmemory/README]]

## Kapcsolódó

- [[sv-01-memory-architecture]] — a tengely-elméleti keret, ezen belül helyezzük el
- [[async-memory-consolidation-letta]] — Letta minta (R@5 83.2% vs agentmemory 95.2%)
- [[cognee-memory-control-plane-pattern]] — control-plane analógia
- [[Karpathy-LLM-Wiki-pattern]] — a háttér-minta, amit az agentmemory "extends with confidence + lifecycle + KG + hybrid"
- [[memory-md-overflow-management]] — 200-line cap probléma, ezt orvosolja a top-K retrieval

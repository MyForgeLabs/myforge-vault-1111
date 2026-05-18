---
name: 2026-05-17 B-5 Week 2 nb-crystallize integration
type: audit
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "#project/superintelligent-vault", "#axis/sv-5", "#axis/sv-8"]
---

# B-5 Week 2 — `vault-nb-crystallize` real impl + `11.11crystallize` Layer 1.5 hook

> NotebookLM-alapú per-bullet **support-count enrich** mint Layer 1.5 a G-Eval ELŐTT.
> Skeleton-first: env-gated (`VAULT_NB_CRYSTALLIZE=1`), default OFF — `/11.11stop` ne lassuljon.
> Fail-open: NB outage NEM blokkolja a G-Eval-t.

## Mi épült

| Komponens | Path | Funkció |
|---|---|---|
| **NB-crystallize CLI** | `/root/obsidian-vault/.vault-nb/scripts/vault-nb-crystallize.py` | `--bullet-enrich <session-slug>` új subcommand; per-bullet NB-ask + JSON-parse |
| Symlink | `/usr/local/bin/vault-nb-crystallize` | first-class `vault-*` tool |
| **Layer 1.5 hook** | `/usr/local/bin/11.11crystallize` | NB enrich a G-Eval ELŐTT, fail-open |
| Pending dir | `/tmp/vault-nb-pending/<slug>.bullet-enrich.json` | 2-phase (mirror vault-ko-ingest) |
| Backup | `/usr/local/bin/11.11crystallize.bak.20260517-nb-crystallize` | rollback |
| Backup | `.vault-nb/scripts/vault-nb-crystallize.py.bak.20260517-nb-crystallize` | rollback |

## Layer 1.5 architektúra

```
session-fájl
   │
   ▼
extract_learnings  ─► [9 bullet]
   │
   ▼   (csak ha VAULT_NB_CRYSTALLIZE=1)
Layer 1.5: vault-nb-crystallize --bullet-enrich  ── NotebookLM ask × N ──► nb_payload
   │                                                                       (per-bullet:
   │                                                                        nb_support_count,
   │                                                                        nb_top_sources,
   │                                                                        nb_confidence)
   ▼
claude_code_scorer_request(bullets, slug, with_context=…, nb_payload=nb_payload)
   │   (pending file `items[i].nb_context` mezőben)
   ▼
G-Eval scorer (claude-code subagent / anthropic / mock)
   │
   ▼
route + Layer 2.5 NLI + Layer 2.6 coherence + audit
   │   (audit-log: + nb_support_count, nb_top_sources, nb_confidence, nb_latency_ms)
   ▼
[--apply skeleton]
```

Az NB-enrich **fail-open**: ha a CLI nem fut / timeout / parse-fail, a parent `nb_payload=None`-nal megy tovább a G-Eval-re, és az audit-record-ban **nincsenek** `nb_*` mezők (uniform-skip pattern).

## Skeleton-first kapcsoló-mátrix

| Env | Default | Mit csinál |
|---|---|---|
| `VAULT_NB_CRYSTALLIZE=0` | igen (DEFAULT) | OFF — Layer 1.5 hook teljesen ki, viselkedés = pre-Week-2 baseline |
| `VAULT_NB_CRYSTALLIZE=1` | — | ON — `11.11crystallize` lefuttatja az enrich-et a G-Eval előtt |
| `VAULT_NB_BULLET_MIN_SUPPORT=3` | 3 | `high` confidence küszöb (≥3 forrás) |
| `VAULT_NB_BULLET_TIMEOUT=120` | 120s | per-bullet NB-ask timeout |
| `VAULT_META_NB_POINTER` | `~/.vault-config/vault-meta-notebook.id` | default NB (override `--notebook`) |

## Smoke-test — 9 bullet × vault-meta NB

Session: `08-Sessions/2026-05-17-obsidian-vault-2.md` (9 Learning-bullet).

### Wall-clock per bullet

| bullet | latency | support | tier | preview (40c) |
|---|---|---|---|---|
| 0 | 8866 ms | 0 | 🔴 low | Subagent-fanout 6. iteráció — 8+6… |
| 1 | 9459 ms | 0 | 🔴 low | Memgraph CE 3.9.0 natív vector-i… |
| 2 | 9786 ms | 0 | 🔴 low | Bias-mitigated G-Eval prompt mér… |
| 3 | 9357 ms | 0 | 🔴 low | Smart-trigger pattern: gyors-bas… |
| 4 | 8324 ms | 0 | 🔴 low | `gepa-ai/gepa` `pip install`-elh… |
| 5 | 9266 ms | 0 | 🔴 low | B-7 typed entities + Wikilink-im… |
| 6 | 9715 ms | 0 | 🔴 low | Full-bullet vs preview-truncatio… |
| 7 | 9691 ms | 0 | 🔴 low | Per-target threshold YAML felold… |
| 8 | 10244 ms | 0 | 🔴 low | Detect-only / dry-run-only / ske… |

**Aggregát:** 9 bullet · **84.7 s wall-clock** · átlag 9.4 s/bullet · **0 hard fail**.

### Várt vs. valós teljesítmény

- **Várt:** 30s-1min/bullet, 5-10 min full session.
- **Valós:** ~9.4 s/bullet (NB conversation reuse → cache hit), **84.7 s** full session — **~4× gyorsabb mint vártuk**.
- A `/11.11stop` lassítás (ON módban): **~85 s** egy 9-bullet session-en. Default OFF, így normál stop érintetlen.

### Support-count értelmezés (jelen pillanatban 0/9 high)

A vault-meta NB jelenleg **1 source-t tartalmaz** (`mfl-voice-sprint-1` push az előző session-ből, B-5 Week 2-α). Az SV-tartalom (Memgraph, GEPA, NLI Layer 2.5, B-7) **NEM** szerepel még, ezért a NB helyesen jelez „Nem találtam támogató forrást" → `support=0 → low`. A negatív-phrase parser (`NEGATIVE_RE`) korrekten short-circuitel, így a citation-counter NEM ad hamis pozitívokat.

**Validáció önmagában is hasznos:** ha a backfill folyamán (`for f in 08-Sessions/2026-05-*.md; do vault-nb-meta-push $f; done`) a vault-meta NB feltöltődik, ugyanezen 9 bullet **most-cache-elt** payload-ja a `/tmp/vault-nb-pending/`-ben **invalid lesz** — re-runkor új source-okkal magasabb `high`-arány várható (Week 3 verifikáció).

## Audit-log mezők (új)

Per-bullet record kiegészülve (csak ha `nb_payload` betöltődött):

```json
{
  "session_slug": "2026-05-17-obsidian-vault-2",
  "bullet_preview": "Per-target threshold YAML feloldja az …",
  "route": "discard",
  "nb_support_count": 0,
  "nb_top_sources": [],
  "nb_confidence": "low",
  "nb_latency_ms": 9691
}
```

- `nb_support_count` — int (0+) vagy `null` ha enrich nem futott
- `nb_top_sources` — list[str], max 5 (audit-bloat-cap; full lista a pending file-ban)
- `nb_confidence` — `"high"` (≥3) | `"mid"` (1-2) | `"low"` (0) | `"error"` | `"off"` | `"dry-run"`
- `nb_latency_ms` — int

## Cross-cut potenciál — Layer 2.6 hook

**Eltérés-jel:** `nb_support_count == 0` ÉS `confidence ≥ 0.85` (auto-prop kandidát) → erős „hallucinated learning" gyanú. Lehetséges discard-vote a Layer 2.6 vault-coherence-check-be (Week N, opcionális):

```python
if nb_payload and nb_entry["nb_support_count"] == 0 and routing == "auto-prop":
    # Optional Week-N: downgrade auto-prop → batch-preview
    # NB found ZERO supporting sources → strong cross-cut signal
    pass
```

Jelenleg **nincs aktiválva** — csak rögzítjük az audit-log-ban, hogy korreláció-statisztikát tudjunk csinálni 4-8 hét múlva (auto-rate vs. nb_support_count by confidence tier).

## Backward compatibility

- `VAULT_NB_CRYSTALLIZE=0` (default) → **0 viselkedés-változás**. A `print` header most már `nb=OFF` jellel mutatja az állapotot, audit-log mezőkben **nincs** `nb_*` kulcs.
- A `claude_code_scorer_request` payload-szerkezet csak akkor változik (`items[i].nb_context`-szel), ha `nb_payload` not-None. A claude-code subagent prompt-template-jét **lehet** frissíteni hogy konzumálja, de **nem kötelező** (graceful fallback: simán ignorálja).

## Korlátok / Tudatos out-of-scope

1. **A claude-code G-Eval prompt-template NEM lett frissítve** — a payload tartalmazza az `nb_context`-et, de a subagent jelenlegi prompt-ja ignorálja. Week 2.5 javítás: G-Eval prompt-template kibővítése „NB-supported forrás-szám" kontextus-blokkal, hogy a CoT bias-self-check is figyelembe vegye.
2. **`11.11stop` és `vault-meta-push` érintetlen** — a Week-2 build a `11.11crystallize`-re fókuszál; a stop-script semmilyen módon nem hív NB-t (env-flag default OFF).
3. **Per-projekt NB override** csak CLI-flag (`--notebook <NB-ID>`); az `11.11crystallize` mindig a vault-meta-t használja, mivel a cross-project synthesis pont ezen NB-ben él.

## Week 3 follow-up

- **Heti commute-podcast cron** (`podcast.schedule: "0 22 * * 0"` a `nb-projects.yml`-ben) — vasárnap 22:00 → hétfő reggelre kész MP3 a `Top 5 vault-learning` podcastből.
- **Backfill cron**: `vault-nb-meta-push` minden `2026-05-*.md` session-re (eddig csak `mfl-voice-sprint-1` pusholva).
- **G-Eval prompt-template extension** (Week 2.5): `nb_support_count + nb_top_sources` mezőket beolvasztani a CoT bias-check fázisba (`"Ha NB-ben 0 forrás van, downweight a self-enhancement gyanúsat"`).
- **NB enrich-re cache-TTL** (Week 3): jelenleg `nb_enrich_load` mindig reuse-ol, ha létezik. TTL=24h vagy file-mtime > session-mtime esetén invalidate.

## Reusable patterns

- **Layer 1.5 = pre-G-Eval enrich slot** — ez az első alkalmazás (NB), de bármely más external knowledge-source (Memgraph entity-graph, web-search) ugyanezt a slot-ot használhatja. A `claude_code_scorer_request(..., nb_payload=...)` signature általánosítható `extra_contexts=[…]` paraméter-listára.
- **Fail-open subprocess hook** — minden NB/external-tool call try/except + return-None + sys.stderr warning, a parent flow NEM eshet el. Ez a 2026-05-17 NLI-judge / coherence-check / NB enrich mindhárom közös mintája.

## Kapcsolódó

- [[2026-05-17 B-5 vault-meta notebook hook]] — előző session, Week 2-α
- [[2026-05-12 sv-8 notebooklm cognitive layer arch]] — ADR
- [[../11-wiki/sv-08-notebooklm-cognitive-layer]] — sprint-plan
- [[../11-wiki/multi-layer-safety-gate]] — Layer 1-4 alap-keret
- [[../08-Sessions/2026-05-17-obsidian-vault-2]] — smoke-test forrás
- [[../11-wiki/claude-code-subagent-fanout]] — 2-phase pending pattern (eredeti)

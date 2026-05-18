---
name: B-3 session eval frontmatter rollout
type: audit
date: 2026-05-17
author: claude
tags: ["#type/audit", "#project/superintelligent-vault", "#sprint/b-3"]
---

# B-3 — Session-frontmatter eval-mezők bevezetése

> [!info] Forrás
> NotebookLM-mining (sv-07) 2026-05-17 HIGH-prio ajánlása: queryable eval-mezők
> minden `08-Sessions/*.md` frontmatter-ébe, hogy a vault-quality heti trendje
> Dataview/Obsidian-Bases-szel mérhető legyen.

## 1. Schema-extension — patch-javaslat (NEM apply-elve)

> [!warning] Forbidden-target
> `00-Meta/` a multi-layer-safety-gate Layer-3 forbidden-target listán van.
> Ezt **nem írom át közvetlenül**. A főagent (vagy a user) apply-eli az alábbi
> patch-et manuálisan.

### Patch: `00-Meta/Frontmatter-schema.md` — `type: session` blokk

**Helyettesítendő rész (jelenleg):**
```yaml
---
name: session-név
project: projekt-slug                # slug egyezik a Projects/<slug>.md-vel ha van
status: open | closed
started: 2026-04-23T18:37+00:00
ended:                               # ISO-8601 ha closed
agent: claude | codex | gemini
tags: ["#type/session", "#project/..."]
---
```

**Új blokk (B-3-tal kiegészítve):**
```yaml
---
name: session-név
project: projekt-slug                # slug egyezik a Projects/<slug>.md-vel ha van
status: open | closed
started: 2026-04-23T18:37+00:00
ended:                               # ISO-8601 ha closed
agent: claude | codex | gemini
# B-3 Continuous Evaluation fields (optional, null = not yet evaluated)
eval_score: null                     # float 0-5 — G-Eval átlag * 5 (avg confidence)
eval_critique: null                  # "passed" | "needs work" | "discard" — route-majority
hallucination_flag: false            # bool — NLI-judge contradiction verdict bármelyik bullet-en
eval_l2_agreement: null              # float 0-1 — G-Eval pass ↔ NLI pass_vote arány
tags: ["#type/session", "#project/..."]
---
```

**Hozzáadandó megjegyzés a típus-blokk után:**

> [!info] B-3 eval-mezők
> A `vault-session-eval-run <slug>` populálja őket G-Eval (`11.11crystallize`)
> + L2 NLI-judge (`eval-l2-nli-judge`) páros futtatásával. A `null` default
> azt jelenti: a sessiont még nem értékelte ki a B-3 pipeline. Backfill:
> `vault-session-eval-backfill --apply` (idempotens).
>
> **Aggregáció:**
> - `eval_score` = `avg(G-Eval confidence) * 5` (0-5 skála)
> - `eval_critique` route-majority: `auto-prop ≥ N/2` → "passed";
>    `auto-prop+batch-preview ≥ N/2` → "needs work"; egyébként → "discard"
> - `hallucination_flag` `true`, ha bármelyik bullet NLI-verdict = `contradiction`
> - `eval_l2_agreement` = `agree_hits / nli_seen` (0-1)

## 2. Scriptek (implementálva)

| Script | Hely | Funkció |
|---|---|---|
| `vault-session-eval-backfill` | `/usr/local/bin/` | Idempotens `null`-default insert minden session-frontmatterbe |
| `vault-session-eval-run` | `/usr/local/bin/` | Adott session-re lefuttatja G-Eval + NLI-t, frissíti frontmatter mezőket |

### Behavior — `vault-session-eval-backfill`

- **Dry-run (default required)**: scan + per-file diff-preview. Semmit NEM ír.
- **Apply**: csak `type:session` fájlokba szúrja be a 4 új mezőt, ha még nincs.
- **Idempotens**: re-run zero-change, ha minden mező már jelen van (`already-ok`).
- **Insertion-point**: `tags:` line előtt (ha van), különben frontmatter végén.
  Header comment `# B-3 eval fields (auto-backfilled, null = not yet evaluated)`.
- **NEM nyúl** non-session fájlokhoz vagy hiányzó frontmatter-hez (skip).

**Dry-run output 2026-05-17 (74 fájl):**

```
[DRY-RUN] vault-session-eval-backfill — /root/obsidian-vault/08-Sessions
  total files scanned : 73
  skip-no-frontmatter   : 0
  skip-not-session      : 1
  already-ok            : 0
  would-change          : 72
  changed               : 0
```

72/73 session-fájl kapna mezőt apply-kor. 1 skip (valószínűleg `type:session`
hiányzik egy régi fájlból — ezt manual-check-elni érdemes).

### Behavior — `vault-session-eval-run <slug>`

1. Beolvassa `06-Audits/crystallize-log.jsonl`-t, kiszűri a sessionhöz tartozó
   sorokat (`bullet_hash`-ra de-dupe — utolsó-wins).
2. Ha nincs sor VAGY `--rescore`: lefuttatja `11.11crystallize <slug>
   --scorer claude-code`-ot (default scorer subagent-fanout, $0 cost).
3. Ha `--skip-nli` nem volt: `eval-l2-nli-judge --input-file <temp.jsonl>
   --json` batch-mód. Verdict per bullet: entailment/neutral/contradiction.
4. Aggregálja: avg-confidence → `eval_score`; route-majority → `eval_critique`;
   contradiction-OR → `hallucination_flag`; G-Eval-pass ↔ NLI-pass arány →
   `eval_l2_agreement`.
5. **Idempotens upsert** a frontmatter-be (csak a 4 mezőt írja, többit nem).
6. `--dry-run` mode: print only, no write.

**Manual-trigger-only.** Nincs cron, nincs hook auto-call. Cél: B-3 graduálás
után opcionálisan a `/11.11-zar-session`-be hookolni (post-stop).

## 3. Dataview-query példák (vault-quality dashboard)

### Heti trend — passed/needs-work/discard arány

```dataview
TABLE WITHOUT ID
  file.link AS Session,
  eval_score AS Score,
  eval_critique AS Verdict,
  hallucination_flag AS Hallu,
  eval_l2_agreement AS L2Agree
FROM "08-Sessions"
WHERE type = "session" AND eval_score != null
SORT file.name DESC
LIMIT 20
```

### Hallucination-flag-ek (vörös zászló)

```dataview
LIST
FROM "08-Sessions"
WHERE hallucination_flag = true
SORT file.name DESC
```

### Nem-értékelt session-ök (backfill-target)

```dataview
LIST
FROM "08-Sessions"
WHERE type = "session" AND eval_score = null
SORT file.name DESC
```

### Obsidian-Bases view (`.base` fájlhoz)

```yaml
filters:
  and:
    - type == "session"
    - eval_score != null
views:
  - type: table
    name: "B-3 eval trend"
    order:
      - file.name
      - eval_score
      - eval_critique
      - hallucination_flag
      - eval_l2_agreement
```

## 4. Next steps

1. **User apply-eli a `00-Meta/Frontmatter-schema.md` patch-et** (1. szekció)
2. **Backfill execute:** `vault-session-eval-backfill --apply` — 72 fájl 1 körben
3. **`04-Tasks/Dashboard.md`-be Dataview-table** beágyazása (3. szekció query-i)
4. **Próbafutás:** `vault-session-eval-run 2026-05-17-obsidian-vault --dry-run`,
   majd ha jó, írni
5. **Heti cron-jelölt:** `vault-session-eval-run` az `11.11-zar-session`-be
   post-stop hook-ként (de **csak shadow-mode opt-in** ENV-flag-gel — analóg
   `VAULT_CRYSTALLIZE_AUTO=1`-gyel)

## Kapcsolódó

- [[../07-Decisions/2026-05-12 sv-7 continuous evaluation arch]]
- [[../11-wiki/sv-07-continuous-evaluation]]
- [[../11-wiki/multi-layer-safety-gate]] — forbidden-target indoklás
- [[../02-Projects/superintelligent-vault]] — B-3 sprint state
- [[../00-Meta/Frontmatter-schema]] — patch target (1. szekció)

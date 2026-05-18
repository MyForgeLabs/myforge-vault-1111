---
name: 2026-05-17 B-4 auto-skill distillation skeleton
type: audit
tags: [audit, sv-b4, sv-b8, auto-distill, skeleton, voyager, recreate, skillrl]
created: 2026-05-17
updated: 2026-05-17
sprint: SV B-4 + B-8 cross-axis
status: skeleton-landed
---

# SV B-4 + B-8 — Auto-skill desztilláció skeleton (Week 1)

> NotebookLM-mining (sv-02 + sv-04 cross-cut) HIGH-prioritású ajánlása alapján: sikeres trajektória (≥5× repetált tool/skill-pattern egy session-en belül vagy session-ek között) → új skill-draft autonóm létrehozása `~/.claude/skills/auto-distilled/queue/<slug>.md`-be. **Voyager skill-library + ReCreate TTE + SAGE/SkillRL** kombináció, **safety-first sorrendben** (queue → manual flip → active).

## TL;DR

- Skeleton script ✓ `/usr/local/bin/vault-skill-distill` (Python 3, no LLM call, regex+counter)
- Audit-output ✓ `06-Audits/skill-distill-candidates-2026-05-17.md` — 5 jelölt 30-napos ablakból
- Manual-review queue dir ✓ `~/.claude/skills/auto-distilled/queue/` (üres, Week 2-re vár)
- **Aktív skill írás TILOS** ebben a fázisban — csak audit + queue (review state)

## 4-step workflow design

| Step | Aktor | Bemenet | Kimenet | Status |
|---|---|---|---|---|
| **1. detect** | `vault-skill-distill` (Python, regex+Counter) | `08-Sessions/*.md` Events szekciók | `06-Audits/skill-distill-candidates-YYYY-MM-DD.md` | ✓ Week 1 (most) |
| **2. distill** | LLM subagent (general-purpose, Voyager-prompt) | top-K candidate + példa Events-context | `~/.claude/skills/auto-distilled/queue/<slug>.md` (REVIEW) | ⏳ Week 2 |
| **3. manual-review** | User (read+edit) | queue file | ✓ approve / ✗ delete / edit | ⏳ Week 2-3 UX |
| **4. activate** | User (manual `mv`) | `queue/<slug>.md` | `auto-distilled/<slug>/SKILL.md` (active) | ⏳ Week 3 |

A **#1 step DETECT-only skeleton most landolt**. A többi 3 lépés Week 2-3-ra van betervezve.

### Step 1 — detect (skeleton, élesben)

- Session Events-sorokból normalizált tool/skill-tokent extractál
  - Regex-allowlist: `vault-*`, `11.11*`, `/11.11-*`, `mcp__*`, plus `subagent-fanout`, `crystallize`, `semantic-search`, `embed`, `ingest`, `backfill`, `safety-gate`, `triplet-extraction`, `batch-N` (→ `batch`)
- Counter per-token + per-bigram (within-event és cross-event composition signal)
- Threshold default `--min-count 5` (≥5 alkalom)
- Output: markdown audit-fájl frontmatter+táblázat+candidate-lista
- CLI: `--session <slug>` | `--all-recent` (7 nap) | `--days N` | `--min-count N` | `--print-only`

### Step 2 — distill (skeleton-only, Week 2 implementáció)

A skeleton **NEM hív LLM-et**. Week 2 plan:

- `vault-skill-distill --distill` flag → minden candidate-re subagent-fanout
- Subagent prompt-template (Voyager-mintára):
  - "Te egy skill-író vagy. Adott a token `X` és N session-Events ahol előfordult."
  - "Generálj egy SKILL.md draft-ot: frontmatter (name, description, trigger_keywords) + Workflow-steps."
  - "Output: `~/.claude/skills/auto-distilled/queue/<slug>.md` bare markdown (no fence)."
- 2-phase pending pattern a `/tmp/vault-skill-distill-pending/` mappában (analóg a crystallize-pending-gel)
- CodeBERT cosine-similarity check existing skill-pool ellen (>0.8 → drop, dedup)

### Step 3 — manual-review (Week 2-3 UX)

- `vault-skill-distill --review` listázza a `queue/*.md` fájlokat title + summary-jel
- User Read tool-lal megnyitja, Edit-eli, vagy törli
- ENV-gate `VAULT_AUTO_DISTILL_DISABLED=1` teljes szüneteltetésre

### Step 4 — activate (user-only, manuális)

A user maga futtatja:

```bash
mkdir -p ~/.claude/skills/auto-distilled/<slug>
mv ~/.claude/skills/auto-distilled/queue/<slug>.md \
   ~/.claude/skills/auto-distilled/<slug>/SKILL.md
```

**Auto-mv TILOS** — még shadow-mode-ban is. Ez a Voyager "self-verification" problémájára (76% false-positive Reflexion-pass) válaszul a `manual-flip` gate. A user a Karpathy-féle "compilation"-réteg humán-validátora.

## Detect-results (run #1, 2026-05-17)

Ablak: utolsó 30 nap (72 session), min-count=5.

| # | Token | Count | Distinct sessions | Verdict |
|---|---|---|---|---|
| 1 | `batch` | 15 | 6 | 🟢 strong |
| 2 | `ingest` | 14 | 4 | 🟢 strong |
| 3 | `backfill` | 9 | 5 | 🟡 borderline |
| 4 | `vault-cleanup` | 7 | 4 | 🟡 borderline |
| 5 | `vault-search` | 6 | 5 | 🟡 borderline |

**Top bigrams (composition signal):**

| A → B | Count |
|---|---|
| `vault-cleanup` → `vault-cleanup` | 3 |
| `batch` → `batch` | 3 |
| `ingest` → `ingest` | 3 |
| `backfill` → `backfill` | 2 |
| `batch` → `backfill` | 2 |
| `backfill` → `ingest` | 2 |

**Megfigyelések:**

- A top-3 (`batch`, `ingest`, `backfill`) erősen **a 2026-05-17 vault-meta super-session bias-ed** — 174 párhuzamos subagent + 10× KO-DB növekedés egyetlen napon. Ez egy iteráció-cluster, nem evergreen pattern. Week 2 distill előtt érdemes deduplikálni a `2026-05-17-obsidian-vault*` session-eket vagy weighted-by-distinct-day counter-t használni.
- `vault-cleanup` → `vault-cleanup` bigram (3×) = heti cron + manual rerun pattern. Már létezik script, NEM kell skill-té desztillálni → distill-skipper kell az allowlist-be ("token already a known script → skip unless wrapper-pattern detected").
- `vault-search` (6 uses / 5 distinct sessions) = a legesélyesebb evergreen-jelölt — Week 2 első LLM-fanout-célpont.

**Bigram-only jelöltek (composition pattern, single tokens alatt threshold):** a `backfill → ingest` és `batch → backfill` bigramok együtt egy ismétlődő makrót sejtetnek: "indíts batch subagent-fanout-ot a backfill-re, az ingest-eli KO-DB-be". Ez **erős skill-distill candidate** (Week 2): "ko-backfill-batch" típusú új skill.

## Safety considerations

| Réteg | Mit véd | Hogyan |
|---|---|---|
| **L1 Output isolation** | `~/.claude/skills/` aktív pool nem írható | A script CSAK `06-Audits/` + (Week 2-től) `auto-distilled/queue/`-ba ír. Hardcoded path, nincs CLI override aktiv-target-re. |
| **L2 Queue-state default** | Auto-aktiváció lehetetlen | Queue fájl nem `SKILL.md` — még ha a `~/.claude/skills/auto-distilled/queue/foo.md`-t valami betöltené is, a frontmatter `status: review` és a path nem matchel a Claude Code skill-loader pattern-jére (`<slug>/SKILL.md`). |
| **L3 Manual flip** | Human-in-the-loop | A `mv queue/<slug>.md auto-distilled/<slug>/SKILL.md` user-only. NINCS script erre. |
| **L4 Skill-pool dedup** | Hallucinált tool / duplikálás | Week 2 CodeBERT similarity-check existing `~/.claude/skills/*/SKILL.md`-k ellen (τ>0.8 drop). |
| **L5 ENV-disable** | Pánik-stop | `VAULT_AUTO_DISTILL_DISABLED=1` env-var → script azonnal exit-el (Week 1 még nincs implementálva — Week 2 a `--distill` flag-gel együtt). |
| **L6 Forbidden targets** | Vault-meta-mappák | A script SOHA nem ír `00-Meta/`, `AGENTS.md`, `.vault-ko/`, `07-Decisions/`-be. Csak `06-Audits/` (Week 1) + `~/.claude/skills/auto-distilled/queue/` (Week 2). |

### Voyager / Reflexion ismert failure modes — mit oldottak meg

- **Self-correction blind spot (76% false-pass)** → Manual-flip gate (L3) átveszi a verifier szerepét
- **Skill-creation hallucinate** → CodeBERT dedup (L4) megfogja a nem-létező-tool referenciákat (existing pool overlap-detect)
- **Catastrophic forgetting** → Queue-state lassítja az injection-t, user-flip dönti el mi marad
- **Prompt-injection on session-content** → Session Events-input már user-trusted (a session-fájlok agent+user által írtak); de Week 2 distill-promptban escape-elni kell a `</prompt>` és hasonlókat

## Acceptance criteria

### Week 1 (skeleton, MOST) — DONE

- [x] `/usr/local/bin/vault-skill-distill` futtatható (executable, shebang `#!/usr/bin/python3`)
- [x] CLI flags: `--session`, `--all-recent`, `--days`, `--min-count`, `--output`, `--print-only`
- [x] `--all-recent` (7d) és `--days 30` mind futnak hibamentesen
- [x] Output `06-Audits/skill-distill-candidates-YYYY-MM-DD.md` markdown + frontmatter
- [x] Detect ≥3 candidate pattern-t a 30-napos ablakban
- [x] Skeleton **nem ír** `~/.claude/skills/`-be (CSAK audit + queue mkdir)
- [x] `~/.claude/skills/auto-distilled/queue/` mappa létrejött

### Week 2 (draft generation) — TODO

- [ ] `--distill` flag a CLI-ba, subagent-fanout per candidate
- [ ] Subagent prompt-template + 2-phase pending pattern (`/tmp/vault-skill-distill-pending/`)
- [ ] Generated draft frontmatter validáció (name, description, trigger_keywords kötelező)
- [ ] CodeBERT cosine-similarity check existing skill-pool ellen, τ=0.8 dedup
- [ ] Test: a top-3 candidate-re draft jön létre `queue/`-ba, formátum stabil
- [ ] ENV-gate `VAULT_AUTO_DISTILL_DISABLED=1` honored

### Week 3 (review UX) — TODO

- [ ] `vault-skill-distill --review` listázás
- [ ] Recall+precision metric: a user mennyi % drafttal csinál mit (keep / edit / delete)
- [ ] Heti cron entry (vasárnap 05:00, `vault-cleanup` után) — opt-in

## Next-steps

1. **Week 2 day-1:** subagent-fanout prompt-template + 2-phase pending. Reuse `crystallize-pending` SKILL.md pattern-jét referenciaként.
2. **Week 2 day-2:** CodeBERT dedup (vagy egyszerűbb: `bge-m3` embedding cosine egy meglévő skill-corpus ellen, `vault-search`-szel)
3. **Week 2 day-3:** első éles distill futás a top-5 candidate-en, manual-review minden draft
4. **Week 3:** ramp-protokoll: ha 3 héten át 80%+ keep-rate → conservative threshold (`--min-count 3`); ha 30%+ delete-rate → roll back

## Kapcsolódó

- [[11-wiki/sv-04-tool-composition]] — Voyager skill-library, MCP, Tool Search elmélet
- [[11-wiki/sv-02-recursive-self-improvement]] — ReCreate TTE, SAGE/SkillRL, Reflexion failure-modes
- [[11-wiki/Crystallization-protocol]] — Learnings → skill auto-conversion master flow
- [[11-wiki/multi-layer-safety-gate]] — 4+ rétegű safety gate playbook (most L1-L6 ennek a tengelynek)
- [[11-wiki/claude-code-subagent-fanout]] — a Week 2 fanout-pattern alapja
- [[06-Audits/skill-distill-candidates-2026-05-17]] — első run output
- `/usr/local/bin/vault-skill-distill` — a skeleton script
- `~/.claude/skills/auto-distilled/queue/` — Week 2+ draft target dir

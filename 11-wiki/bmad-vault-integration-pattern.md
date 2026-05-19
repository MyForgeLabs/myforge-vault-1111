---
name: BMAD ↔ MyForge Vault integration pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#bmad", "#vault", "#integration", "#sv-pipeline"]
---

# BMAD ↔ MyForge Vault integration pattern

> [!info] Kontextus
> A user napi szinten használja a BMAD-skill-eket (`bmad-bmm-create-prd`, `bmad-create-architecture`, `bmad-create-story`, `bmad-gds-create-gdd`, `bmad-retrospective`, stb.) — minden ilyen skill markdown-artifactot termel. Eddig ezek kézi átmozgatással kerültek (vagy nem kerültek) a vault-ba. Ez a pattern leírja a **3-lépéses auto-ingestion pipeline**-t a `bmad-vault-bridge` script köré építve.

## A két oldal — mit ad a BMAD, mit ad a vault

| BMAD adja | Vault adja |
|---|---|
| Strukturált markdown-artifact (PRD, GDD, Architecture, Epic, Story, Sprint, Retro) | Perzisztens kontextus a 02-Projects/, 08-Sessions/, 07-Decisions/ rétegekkel |
| BMAD-skill-szuit-versionezés (`v0.1` … `vX.Y`) | KO-DB triplet-store (fact-extraction `vault-ko-ingest`) |
| Phase-tudás (discovery → planning → dev → qa → retro) | Memgraph semantic chunks (`vault-search` / `vault-embed`) |
| Project-slug a BMAD-skill kontextusából | Cross-source corroboration (`vault-ko-query --top-k`) |
| Skill-name-szintű metadata (mely BMAD-skill termelte) | Audit-log + history minden ingest-eseményre |

A bridge **kétirányú**: BMAD → vault (ingest) és vault → BMAD (context pre-load).

## A 3-lépés workflow

### 1. lépés — BMAD-skill termeli az artifactot

Példa: `/bmad-bmm-create-prd` a Boulium Friends-MVP Phase 2-höz. A BMAD-skill kiír egy `prd-friends-mvp-phase-2.md` fájlt valahova — ideálisan rögtön a `/root/obsidian-vault/02-Projects/boulium/bmad/` alá, vagy egy projekt-repo `docs/bmad/` mappájába.

### 2. lépés — `bmad-vault-bridge` auto-ingestion

Két alternatíva:

**(a) On-demand (egyszer-egy-artifact):**

```bash
bmad-vault-bridge --ingest /tmp/prd-friends-mvp-phase-2.md --project boulium
# → routol: 02-Projects/boulium/bmad/prd-friends-mvp-phase-2.md
# → stempeli a frontmattert (bmad_version, bmad_project, bmad_phase)
# → vault-ko-ingest --file → KO-DB
# → vault-embed --file → Memgraph
# → audit-log
```

**(b) Folyamatos (file-watcher):**

```bash
bmad-vault-bridge --watch /root/obsidian-vault/02-Projects &
# watchdog rekurzíve, csak `*/bmad/*.md` fájlokra
# 2s dedup + 5s self-write suppress (saját write-back ripple-t kiszűri)
```

A watch-mode `systemd --user`-ben futtatható szolgáltatásként, vagy egy `tmux session`-ben.

### 3. lépés — BMAD-skill következő futása vault-context-tel

Mielőtt egy újabb BMAD-skill fut (pl. `/bmad-create-architecture` ami az imént készült PRD-re épít), a vault-bridge pre-loadolható:

```bash
bmad-vault-bridge --context boulium --query "friends-mvp matchmaking" --top-k 8 --json
# stdout JSON: { project_snippet, ko_top_k, semantic_top_k, recent_sessions, bmad_artifacts }
```

A BMAD-skill ezt a JSON-t (vagy `--write`-tal a markdown-rendert) be tudja paste-elni az első prompt-jába. Eredmény: az architecture-skill már tudja, hogy a PRD mit kötött ki, mit mondtak a session-ök, milyen tech-stack döntések voltak (KO-DB facts), és milyen kapcsolódó vault-tartalom létezik (semantic search).

## Frontmatter-kontraktus

Minden BMAD-artifactnak a bridge a következő 3 extra mezőt stempeli:

| Mező | Értelem | Példa |
|---|---|---|
| `bmad_version` | BMAD-skill-szuit verziója; env `BMAD_VERSION` override | `v0.1` |
| `bmad_project` | Linker a `02-Projects/<slug>.md`-hez; path-inference vagy `--project` flag | `boulium` |
| `bmad_phase` | `discovery` \| `planning` \| `dev` \| `qa` \| `retro` | `planning` |

Szövegszerű séma-bővítés: [[00-Meta/Frontmatter-schema#BMAD-artifact típusok]].

## Type-detekció — mit mond a filename, mit mond a body

A bridge két heurisztikán fut:

1. **Filename + szülő-mappa substring** — `prd`, `architecture`, `epic`, `story-`, `sprint-status`, `retro`, `gdd`, `ux-design`, `tech-spec`, `product-brief`. A leghosszabb match nyer (avoid `epic` accidental match in `epic-story-xy.md`).
2. **Body-marker fallback** — ha a filename nem áruló, az első 4000 karakterben keres heading-mintázatokat (`# Product Requirements`, `## Acceptance criteria`, `# Game Design Document`, `## Retrospective`, stb.).

Ha egyik sem talál, a típus `document` lesz (fallback). A bridge ezt warning-gel jelzi de nem hal meg — frontmatter még mindig stempelődik, KO-DB ingest még mindig fut.

## Phase-mapping — mikor mit jelent egy BMAD-artifact

| `type:` | Default `bmad_phase:` | Magyarázat |
|---|---|---|
| `product-brief` | `discovery` | A legkorábbi BMAD-artifact, a probléma feltérképezése |
| `prd` / `gdd` / `ux-design` / `architecture` / `tech-spec` | `planning` | Specifikáció-fázis, kódolás ELŐTT |
| `epic` / `story` / `sprint` | `dev` | Implementáció-tracking |
| `retro` | `retro` | Sprint-vége retrospektív |

A `qa` fázis külön artifact-típus nélkül létezik a BMAD-ben (test-design, test-review skill-ek session-szinten futnak); ha kerül QA-specifikus markdown-artifact, manuálisan `--in-place` lehet ingestelni, vagy a body-marker bővítendő.

## Reusable szabályok

1. **Path-inference > explicit flag** — ha a fájl már `02-Projects/<slug>/bmad/` alatt van, a `--project` flag fölösleges (és felülírja). A watcher mindig path-inferenciával dolgozik.
2. **`--in-place` ingest** vs `routol egy `02-Projects/<slug>/bmad/`-ba** — a watcher always-in-place (nem mozgat); a CLI default routol. Routing csak akkor, ha az artifact eredetileg a vault-on kívülről (pl. `/tmp/` vagy projekt-repo `docs/`-ja) jött.
3. **vault-on-kívüli path → ko-ingest skip** — `vault-ko-ingest` csak vault-internal path-okat kezel; a bridge ezt graceful-skip-pel (rc=0, audit-log üzenettel), nem fail-el.
4. **Self-write suppress 5s** — a watcher saját write-back-jét nem észleli újra event-ként; különben végtelen loop. (A korábbi B-7 round 1 ezen bukott el; 2026-05-19 fix-elve.)
5. **Settle-delay 250ms** — a watcher 250ms-ot vár az event és a read között, hogy az atomic-writer befejezze. Tapasztalat: `cat > foo.md << EOF` race-elhet egy gyors watcher-loop-pal.
6. **Embedder graceful fallback** — `vault-embed` nincs minden szerveren; a bridge `vault-bm25-backfill`-re fall back, vagy "embed-skipped" üzenetet logol. Nem fail-el.
7. **Context-mode is read-only** — `--context` SOHA nem ír a vault-ba (kivéve `--write` explicit kérésre); biztonságos pre-loader.
8. **Audit-log JSONL append-only** — minden ingest / watch-start / watch-stop / watch-error / context-print esemény külön sor a `06-Audits/bmad-vault-bridge-log.jsonl`-ban. Visszakereshető, append-only.

## Kapcsolódás más SV pipeline-elemekhez

- **B-1 KO-DB layer** — minden BMAD-artifact a `vault-ko-ingest`-en megy keresztül, így a triplet-store-ba kerül. Egy `--context` lekérdezés mostantól lát BMAD-eredetű fact-eket is (provenance: `02-Projects/<slug>/bmad/...md`).
- **B-2 Memgraph semantic** — ha `vault-embed` elérhető, a BMAD-artifactok chunks-szá törve bekerülnek a vector-index-be, és a `vault-search` semantic-similarity-vel találja őket.
- **B-5 NotebookLM sync** — a BMAD-artifactok mostantól a `vault-nb-sync` permissive-active filteren átmennek (van `created:`/`updated:`/`type:`/`bmad_project:`), így a projekt-NotebookLM-be is felmehetnek opcionálisan.
- **11.11 session-protokoll** — egy `/11.11-uj-session "boulium-friends-phase2"` session-indítás a `bmad-vault-bridge --context boulium`-ot automatikusan futtathatja a pre-load-szekcióban. (Future: `~/.claude/skills/load-session-context/` integráció.)

## Mit NEM tesz a bridge

- **NEM generál BMAD-artifactot** — az a BMAD-skill-ek dolga.
- **NEM ír a `02-Projects/<slug>.md` projekt-fájlba** — manuálisan kell frissíteni a projekt "Jelenlegi állapot" szekcióját.
- **NEM trigger-eli a `11.11-zar-session` crystallization-t** — az külön workflow (Learnings → KO-DB).
- **NEM próbál BMAD-skill verziókat egyeztetni** — a `bmad_version` mező csak metadata, nincs migration-szabály.

## Tesztelési minimum

1. Mock-PRD ingest: `bmad-vault-bridge --ingest /tmp/mock-prd.md --project boulium` → frontmatter stempelve, `02-Projects/boulium/bmad/`-ba routolva, audit-log append.
2. Watch smoke: `bmad-vault-bridge --watch /root/obsidian-vault/02-Projects &` + új file create → ingest fires once.
3. Context retrieve: `bmad-vault-bridge --context boulium --json | jq .ko_top_k` → real fact-ek.

## Kapcsolódó

- [[00-Meta/Frontmatter-schema#BMAD-artifact típusok]] — frontmatter-séma
- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — háttér-minta
- [[06-Audits/2026-05-19 bmad-vault-bridge skeleton]] — első smoke-jelentés
- [[05-Memory/Skill-map]] — minden BMAD-skill listája
- `/usr/local/bin/bmad-vault-bridge` — script

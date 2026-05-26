---
name: Közös agent utasítások
type: reference
tags: [meta, agent-instructions, "#type/reference"]
audience: [claude, codex, gemini]
created: 2026-04-23
updated: 2026-04-30
---

# Közös agent utasítások (Claude / Codex / Gemini)

Ezt a fájlt mindhárom AI agent betölti a session elején — ez az egyetlen belépési pont a tudásbázishoz.

## Ki a user

- **Név:** Peti (user@example.com)
- **Nyelv:** magyar elsődlegesen, angol technikai szavak OK-ban
- **Szerver:** `/root` headless Linux, VSCode extension + SSH + néha VNC
- **Stílus:** tömör válaszok, magyarázat csak ha kell. Részleteket a [[05-Memory/User]]-ben

## A vault szerkezete (Johnny-Decimal mappa-prefix + Karpathy LLM-Wiki minta)

```
/root/obsidian-vault/
├── README.md                     humán belépő
├── AGENTS.md                     ez a fájl (gyökérben marad — symlink-kompatibilitás)
├── 00-Meta/                      ⚠️ vault-szabályok
│   ├── README.md
│   ├── Tag-taxonomy.md           KÖTELEZŐ tag-konvenciók (#env/prod, #type/host, stb.)
│   ├── Frontmatter-schema.md     KÖTELEZŐ YAML séma per-típus
│   ├── Glossary.md               slug + rövidítés feloldó (KGC, MFL, MAPESZ, BMAD…)
│   └── templates/                Daily / Session / Project sablonok
├── 01-Daily/                     napi naplók (YYYY-MM-DD.md, autogen)
│   └── Index.md
├── 02-Projects/                  ⭐ ELSŐKÉNT EZT OLVASD
│   ├── Index.md                  minden projekt + állapot 5 csoportban
│   └── <projekt>.md
├── 03-Hosts/                     VPS-ek + shared hosting
│   ├── Index.md
│   └── <host>.md
├── 04-Tasks/
│   ├── Backlog.md                Obsidian Tasks plugin
│   └── Dashboard.md              szűrt query-nézetek
├── 05-Memory/                    persistent context
│   ├── README.md
│   ├── User.md                   user profil, preferenciák
│   ├── Infrastructure.md         szerver, VNC, portok, KGC Postgres
│   ├── Skill-map.md              243+ agent-skill csoportosítva
│   ├── Agents-skill-suite.md     myforge-dashboardon elérhető skill-ek
│   └── Dashboard-access.md       Tailscale-only access protokoll
├── 06-Audits/                    pillanatkép-jelentések
│   ├── Index.md
│   └── System_Health.md          ⚙️ heti auto-gen vault-integritás
├── 07-Decisions/                 ADR-szerű döntési napló
├── 08-Sessions/                  /11.11-session-logok (test → _archive/)
├── 10-raw/                       ⭐ Karpathy: nyers input (immutable)
│   └── Index.md
└── 11-wiki/                      ⭐ Karpathy: desztillált tudás (evergreen)
    └── Index.md
```

## Mit csinálj SESSION INDULÁSKOR

**KÖTELEZŐ workflow** (`/11.11-uj-session` után az agent automatikusan):

1. **Detektáld a projektet** a session-névből a [[wiki/Auto-context-loading#Projekt-detektálás a session-névből|projekt-detektálási tábla]] alapján
2. **Aggressive pre-load** — olvasd be a [[wiki/Auto-context-loading]] szerint:
   - Projekt-fájl + utolsó 5 session + minden érintett ADR + Memory releváns része + `#project/<slug>` Backlog tételek + Host-info + mai/tegnapi Daily
   - Cél: ~15-20K token kontextus
3. **Ír egy `## Pre-loaded context` szekciót** a session-fájlba — listázza mit olvastál be, 1-2 mondatos kivonatot adva mindegyikből
4. **Csak utána** vár a user első kérdésére — teljes kontextussal

Ha ismeretlen rövidítés / slug jön elő → [[meta/Glossary]]. Ha ambiguous a projekt → kérdezz vissza.

**Ha nem detektálható projekt** (pl. "wellbeing", "general thinking") — csak alap-kontextust tölts be: [[../02-Projects/Index]], [[../04-Tasks/Backlog]] sürgősei, mai + tegnapi Daily.

## Mikor ÍRJ ide

Amikor valami tartósan hasznos info kerül elő:

| Esemény | Hova ír |
|---------|---------|
| Új projekt indul | Új `02-Projects/<név>.md` + sor a megfelelő csoport-táblába az [[../02-Projects/Index]]-ben |
| Meglévő projekt státusza változott | Frissítsd a `02-Projects/<név>.md` "Jelenlegi állapot" + `updated:` |
| User preferenciát tanultál | [[05-Memory/User]] vagy új `05-Memory/Feedback-<téma>.md` |
| Szerver/infra tudás (port, host, szolgáltatás) | [[05-Memory/Infrastructure]] |
| Nagy architektúra-döntés | Új `07-Decisions/YYYY-MM-DD <téma>.md` |
| **Új TODO** | [[../04-Tasks/Backlog]] (🔴 sürgős / 🟡 figyelni / 🟢 tisztaság) |
| **Feladat kész** | [[../04-Tasks/Backlog]] — ✅ Elvégezve szekcióba dátummal |
| **Új koncepció / playbook** (evergreen) | `11-wiki/<téma>.md` — saját szavakkal |
| **Új cikk / transzkript** (immutable) | `10-raw/YYYY-MM-DD — <forrás>.md` |

## Formázási konvenciók

- **Dátum:** `YYYY-MM-DD` ISO, a user-től kapott relatív dátumokat (pl. "csütörtök") konvertáld ISO-ra
- **Wikilink:** `[[../02-Projects/teszt-eu]]` belső hivatkozásra (mappa-prefix kötelező)
- **Frontmatter:** minden nagyobb doknak legyen `name:`, `type:`, `created:`, `updated:` (lásd [[meta/Frontmatter-schema]])
- **Tag-ek:** [[meta/Tag-taxonomy]] szerint
- **Callout:** `> [!info]`, `> [!warning]`, `> [!todo]`, `> [!success]`
- **Kód/path:** backtick-ben

## Crystallization workflow (KÖTELEZŐ session-záráskor)

**KÖTELEZŐ workflow** (`/11.11-zar-session` után az agent automatikusan):

1. **Summary + Learnings + Next** írása a `08-Sessions/<slug>.md`-be a chat-history alapján
2. **(opcionális, ha `VAULT_CRYSTALLIZE_AUTO=1`)** `11.11crystallize <slug> --scorer claude-code --with-context` — automatikus G-Eval scoring shadow-mode-ban. Ha pending request keletkezik, spawnolj egy general-purpose Agent-et a G-Eval prompt-tal + bullets-szel + kodb_context-tel; írja a response.json-t; majd re-run `11.11crystallize` ugyanazzal a flag-gel a finalizáláshoz.
3. **Routing — minden Learning bullet-re** alkalmazd a [[wiki/Crystallization-protocol#Routing decision tree|decision tree]]-t (architektúra-szintű ADR / vault-szabály / wiki-koncepció / glossary / infra / skill / user-pref / dashboard / projekt / task / kérdezz). Ha van G-Eval-output, használd signal-ként (high-confidence Pass → auto-prop kandidát; Fail → discard; batch-preview → user-elé)
4. **Batch preview** a usernek — összes javaslat egyben, sorszámmal:
   ```
   🧠 N tanulság propagálása — ezeket javaslom:
   [1] "<idézet>" → <target> + preview
   [2] "<idézet>" → <target> + preview
   ...
   OK így? (igen / "1-3 OK, 4 inkább X" / "skip 2" / "stop")
   ```
5. **User megerősítése után** propagáld a tudást
6. **`## Propagation log`** szekcióba időbélyegezve írd be mit hova propagáltál

A session-fájl megmarad raw-szerű referenciának — a desztillátum az index-elt rétegekbe kerül. Ez a Karpathy [[wiki/Karpathy-LLM-Wiki-pattern|crystallization]] az ő minimumában.

**Részletes szabályok:** [[wiki/Crystallization-protocol]]

### SV B-1 pipeline (2026-05-16-tól ÉLES)

| Layer | Parancs | Funkció |
|---|---|---|
| 0 migration | `migrate-hash-refactor-2026-05-19.py` | KO-DB fact-hash refactor: hash by `(s,p,o)` only, `fact_provenance` 1:N side-table (2026-05-19, 190 ms migration, unlocks Bayesian #21) |
| 1 ingest | `vault-ko-ingest --file <path>` | Triplet-extraction subagent-tel, 2-phase pending pattern |
| 2 score | `11.11crystallize <slug> --scorer claude-code --with-context` | G-Eval Learning-bullet scoring + KO-DB context-inject |
| 3 query | `vault-ko-query <pattern>` | Substring + filter + JSON + `--stats` + `--conflicts` + `--top-k` (cross-source rank) + `--semantic` (Memgraph bridge) |
| 3 report | `vault-ko-report [--last\|--session <slug>\|--days N]` | User-facing audit-log summary |
| 4 apply | `VAULT_CRYSTALLIZE_APPLY=1 VAULT_CRYSTALLIZE_REAL=1 11.11crystallize ... --apply` | REAL mode (sandbox-branch + 4-rétegű safety-gate + atomic-write + auto-commit) |
| 5 monitor | `vault-crystallize-monitor [--weeks N] [--json]` | Auto-rate / revert-rate / threshold-ramp ajánlás |
| 5 conflicts | `vault-ko-conflicts-audit` | Heti cross-source contradiction audit, predicate-aware heat-classifier |
| 5 revert | `crystallize-revert <bullet-hash>` | Auto-apply rollback (audit-event-tel) |

**Threshold-config:** `~/.vault-config/crystallize-threshold.txt` (hot-reloadable). Shadow=1.0 (default, no auto-prop), Conservative=0.95, Aggressive=0.85. Ramp-protocol: [[wiki/crystallize-threshold-ramp]].

**Env-vars (opt-in):**
- `VAULT_CRYSTALLIZE_AUTO=1` — `11.11stop` automatikusan futtatja a scoring-ot
- `VAULT_CRYSTALLIZE_SCORER=claude-code` — subagent-fanout scorer ($0 cost) vs `mock` (rule-based) vs `anthropic` (API-key-igényes)
- `VAULT_CRYSTALLIZE_APPLY=1` — `--apply` flag enable (Layer 1 ENV-gate)
- `VAULT_CRYSTALLIZE_REAL=1` — REAL mode (write + commit). Default csak skeleton ("would-have-applied" audit-log)
- `VAULT_CRYSTALLIZE_ALLOW_MAIN=1` — `--apply` REAL futás main-en (DEFAULT: csak `crystallize-sandbox-*` branchen). Veszélyes.

## SV B-2 pipeline (2026-05-13-tól ÉLES, B-1↔B-2 bridge 2026-05-17)

| Layer | Parancs | Funkció |
|---|---|---|
| 1 embed | `vault-embed --backfill <dir>` | bge-m3 multilingual embed → Memgraph |
| 2 search | `vault-search "<query>" [--top-k N] [--json]` | semantic cosine-search (Memgraph in-Python) |
| 3 bridge | `vault-ko-query "<q>" --top-k N --semantic` | semantic → KO-DB top-K bridge (LIKE-fallback ha Memgraph down) |

## Virtual-context (Letta/MemGPT) — PREVIEW (2026-05-25-tól Day 0, opt-in)

A klasszikus aggressive ~17K token-os pre-load mellett él egy alternatív: **core-memory + on-demand page-in**. Sprint-plan: [[decisions/2026-05-25 vault-core-memory MemGPT integration sprint plan]]. Day 0 LANDED, integration W1-5 között.

| Layer | Parancs | Funkció |
|---|---|---|
| 1 core | `vault-core-memory show` | ~2 KB always-loaded core (6 block: user_profile / active_project / open_tasks / glossary / infra_pins / recent_decisions) |
| 2 page-in | `vault-core-memory page-in "<query>" [--top-k N] [--max-chars N]` | Real Memgraph chunk-text retrieval, agent-paste-ready markdown |
| 3 simulate | `vault-core-memory simulate "<query>"` | Token-budget A/B (klasszikus vs virtual) — NEM mutál context-et |
| 4 update | `vault-core-memory update <block> "<text>"` | Atomic block-mutation |

**Env-var (opt-in, default OFF Week 1-4):**
- `VAULT_CORE_MEMORY_AUTO=1` — `11.11focus` + `/11.11-uj-session` auto-update + lean pre-loaded context (W1-2-től aktivál)

**Mikor használj page-in-t** (W2-től agent-konvenció):
- Ha a kérdés NEM válaszolható a core-memory-ból (csak a query-overlap a 6 blokkal nem találat) → `page-in "<query>"`
- Az archival page-in eredmény ~2-3 KB chunk-text-et ad — a klasszikus 15-20K aggressive pre-load helyett
- Ha 1 session-en belül >20 page-fault szükséges → flag, hogy a core-memory mis-sized (review kell)

**Status:** Day 0 (2026-05-25) — `page-in` LANDED, integration nem-aktiv (env-var OFF). Lásd [[wiki/vault-core-memory-integration-roadmap]].

## Net-tanulás (2026-05-17-től)

- `vault-net-ingest --url <URL>` — firecrawl scrape → `10-raw/external/`
- `vault-net-ingest --repo owner/name [--paths "globs"]` — gh clone → key markdown → `10-raw/external/<owner>_<name>/`
- A KO-DB extraction subagent-fanout-pattern (2-phase pending) — `claude_code_scorer_load_response` után megy fel a triplet-tár

## Per-chat session-isolation (2026-05-17-től)

- Claude Code: `$CLAUDE_CODE_SESSION_ID` env-var (UUID)
- Codex companion: `$CODEX_COMPANION_SESSION_ID` (= Claude UUID)
- Codex standalone: `vault-detect-chat-id` auto-detect (rollout-fájlnévből)
- Gemini hook: `~/.gemini/.current-session-id` (SessionStart hook írja)
- Manual override: `CODEX_SESSION_ID` vagy `GEMINI_SESSION_ID` env-var
- A 6 `11.11*` script automatikusan kiszedi a CHAT_ID-t a chain-ből, per-chat pointer-fájl: `.active-session-$CHAT_ID`
- Matrix-doc: [[wiki/cli-session-id-env-var-matrix]]

## Mit NE tárolj itt

- Titkokat (jelszavak, token-ek) — azok `.env` fájlokban maradnak. Kivétel: ha a user kifejezetten kéri
- Generikus info ami git-logból vagy kódból kinyerhető
- Pillanatnyi session-state ami 1 nap múlva irreleváns

## Eszköz-specifikus megjegyzések

- **Claude Code:** ennek a fájlnak egy kópiáját `~/.claude/CLAUDE.md`-ként is látja. A legacy auto-memory (`~/.claude/projects/-root/memory/`) szintén ebből a vaultból él symlinkekkel
- **Codex CLI:** `~/.codex/AGENTS.md`-ként látja. A `~/.codex/skills/` és `~/.claude/skills/` közös symlinkekkel frissülnek együtt
- **Gemini CLI:** `~/.gemini/GEMINI.md`-ként látja. Ugyanaz a skill-készlet, ugyanaz a vault

## Session-orchestration (`11.11*` parancsok)

Részletes leírás: [[wiki/11.11-session-protokoll]]

> [!info] Slash vs shell
> A **shell-CLI** (`/usr/local/bin/11.11*`) nevei változatlanok: `11.11start`, `11.11stop`, `11.11focus`, `11.11note`, `11.11ls`, `11.11`.
> A **Claude Code slash-parancsok** 2026-05-17-től hosszabb magyar nevet kaptak (a popup-UI miatt — VSCode-extension csak a parancs-nevet mutatja, NEM a description-t):

| Slash-parancs (Claude Code) | Shell-CLI | Funkció |
|---|---|---|
| `/11.11-uj-session "projekt-feladat"` | `11.11start "..."` | Új session fájl + focus. Arg nélkül → interaktív picker |
| `/11.11-lista` | `11.11ls` | Nyitott session-ök + utolsó 5 zárt |
| `/11.11-focus <slug>` | `11.11focus <slug>` | Focus váltása másik nyitott session-re. Arg nélkül → interaktív picker |
| `/11.11-jegyzet "..."` | `11.11note "..."` | Timestamped jegyzet a **focused** session `## Events`-be |
| `/11.11-jegyzet @<slug> "..."` | `11.11note @<slug> "..."` | Jegyzet konkrét session-re (substring match) |
| `/11.11-zar-session [slug]` | `11.11stop [slug]` | Agent: Summary + Learnings + Next; Script: commit + push + close. Arg nélkül + 2+ nyitott → picker |
| `/11.11-egeszseg` | `11.11` | Health check: vault, symlinkek, skillek, szolgáltatások |

**Scriptek:** `/usr/local/bin/11.11*` + `/11.11*` symlinkek. **Agent env var:** `AGENT=claude|codex|gemini` a commit üzenetbe kerül.

## Vault egészsége

- **Live snapshot:** [[audits/System_Health]] — heti cron `vault-cleanup` regenerálja (vasárnap 04:00)
- **Auto-save:** 10 percenként cron `/usr/local/bin/vault-autosave` → commit + push GitHub-ra
- **Manuális check:** `/11.11-egeszseg` (slash) vagy `11.11` (shell) — symlinkek, skillek, szolgáltatások

## Hogyan frissül ez a fájl

Ha új konvenció kerül, szerkeszd közvetlenül — a változás azonnal él mindhárom agentnél (symlink).

## Kapcsolódó

- [[README]] — humán belépő
- [[meta/README]] — vault-szabályok
- [[wiki/Karpathy-LLM-Wiki-pattern]] — a háttérben lévő minta
- [[wiki/Johnny-Decimal-prefix]] — miért 00-, 01-, … prefix
- [[wiki/11.11-session-protokoll]] — session-szervezés mélyebben
- [[../02-Projects/Index]] — projekt dashboard
# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.

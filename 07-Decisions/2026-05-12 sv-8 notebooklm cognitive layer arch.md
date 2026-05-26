---
name: SV-8 NotebookLM cognitive layer — Phase B-5 architecture
type: decision
tags: ["#type/decision", "vault-architecture", "notebooklm", "cognitive-layer", "phase-b", "sv-research"]
created: 2026-05-12
updated: 2026-05-12
status: proposed
parent: [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]]
research: [[11-wiki/sv-08-notebooklm-cognitive-layer]]
sprint: B-5
priority: P2 (low-effort, high-leverage)
estimated_effort: 1-2 hét
depends_on: B-1 (G-Eval routing for podcast-prio)
---

# ADR — Phase B-5: SV-8 NotebookLM cognitive layer

## Kontextus

A jelenlegi NotebookLM-használat **ad-hoc + manuális**:
- 2 fő pattern dokumentálva: [[11-wiki/notebooklm-headless-login-fifo]] (auth) + [[11-wiki/notebooklm-seo-competitor-research-pattern]] (17×7 workflow)
- A SV-1..SV-8 research **bizonyítja** a tengely-hipotézist (8 notebook × ~600 source = 4800 source, 56+24 = 80 strukturált kérdés-válasz, ~2900 sor wiki-tartalom 1 nap alatt)
- **DE** a NotebookLM-skill-pool a vault-on belül **nem szisztematikus** — minden projektnek külön ad-hoc notebookja, source-feltöltés manuális

**SV-8 Phase A+ kulcs-insight (1200 source):** A Peti-vault **MÁR Tier-$50 közeli** konfigurációhoz — csak **MCP-bridge + 11.11stop crystallization-hook hiányzik**. A jelenlegi `02-Projects + 04-Tasks/Backlog + 07-Decisions + 08-Sessions` mappa-struktúra lényegében már **a 4-fájlos Karpathy working/episodic/semantic memory-stack gyakorlati megvalósítása**.

## Döntés

**3-rétegű NotebookLM-integráció** a vault-meta-szerepként, B-1 G-Eval foundation-re építve.

### Réteg 1 — Per-projekt notebook-pool automatizálás

Minden aktív projektnek (`02-Projects/<projekt>.md`) automatikus megfelelő NotebookLM-notebook a háttérben.

**Tech-stack:**
- **`vault-nb-sync` cron** (5 percenként, vault-autosave mellé)
- Bejár minden `02-Projects/*.md`-t — ha `notebooklm:` frontmatter-mező nincs → automatikus `notebooklm create "<projekt-név>"` + ID visszaírás
- Forrás-sync: minden `02-Projects/<projekt>.md` + kapcsolódó `07-Decisions/*<projekt>*` + `05-Memory/*<projekt>*` → automatikus `notebooklm source add` a megfelelő notebookba (idempotens — már létező source-ot nem dupliáz)

**Output:** Minden projektnek **élő NotebookLM-jegyzetfüzete** van, amibe a Claude Code session-zárásakor lekérdezhet komplex synthesis-kérdéseket.

### Réteg 2 — `/11.11stop` crystallization-hook a vault-meta notebookba

A Crystallization-protocol (B-1 G-Eval routing) **kibővítése**: a Learnings batch-preview előtt egy **NotebookLM-konzultáció**.

**Tech-stack:**
- Új script: `/usr/local/bin/vault-nb-crystallize`
- Bemenet: a `08-Sessions/<closed>.md` Learnings-listája + a projekt-NotebookLM
- Művelet: `notebooklm ask -n <projekt-NB> "ezek a tanulságok érdemi újdonságot adnak hozzá a meglévő tudás-bázishoz? Mi konvergens (megerősíti az előzőeket), mi divergens (új minta), és mi ellentmondó (revíziót igényel)?"`
- Output: a Learnings-listához **NotebookLM-confidence-tag** csatolva (`convergent` / `divergent` / `contradictory`)
- A B-1 G-Eval ezt **plusz inputként** veszi (a confidence-score-on felül)

**Cél:** Lossless cross-session crystallization — a NotebookLM mint külső „source-grounded" bíró, amely a vault-történet alapján validálja az új Learning-eket.

### Réteg 3 — Heti commute-podcast cron (Audio Overview batch)

A SV-8 self-referential insight kihasználása: minden hétfő reggel automatikus podcast-generálás.

**Tech-stack:**
- **`vault-nb-podcast` cron** (vasárnap 22:00)
- Bejár minden aktív projekt-NotebookLM-t (legalább 1 session-aktivitás az elmúlt 7 napban)
- Lekér: `notebooklm generate audio -n <projekt-NB> --format deep-dive --length default "Heti összefoglaló: mi történt, mit tanultunk, mi a köv lépés."`
- Letölti: `notebooklm download audio -n <projekt-NB> --out ~/vault-audio/weekly/<projekt>-<YYYYWW>.mp3`
- AirDrop-kompatibilis: a Mac-en (Rob/Peti) szinkronizálódik az iCloud-ba (kivéve a vault mappa)

**Cél:** Commute alatt meghallgatható **passzív vault-aware** — minden hétfő reggel a 8 projekt heti hangos-összegzése.

## Acceptance criteria

- [ ] **`vault-nb-sync` cron** működik — minden aktív projektnek élő NotebookLM-jegyzetfüzete, source-sync idempotens
- [ ] **`vault-nb-crystallize`** integrálva a `/11.11stop` workflow-ba (a G-Eval-routing UTÁN, batch-preview ELŐTT)
- [ ] **NotebookLM-confidence-tag** (`convergent`/`divergent`/`contradictory`) megjelenik a Learnings-batch-preview-ben
- [ ] **`vault-nb-podcast` cron** generál minimum 3 podcast-ot az első héten (3+ aktív projekt)
- [ ] **MP3-letöltés** működik az `~/vault-audio/weekly/` mappába
- [ ] **NotebookLM rate-limit** kezelve — ha 429-zik, exponential backoff + heti job split-elve nem mind egyszerre

## Alternatívák amiket ELUTASÍTOTTUNK

- **Anthropic Contextual Retrieval** mint NotebookLM-helyettesítő — $1.02/1M token (Phase A+ insight), de a Audio Overview podcast-feature **nincs benne** → SV-8 self-referential funkciót nem tudja
- **DSPy + AgentInstruct meta-eval** — production-ready, de nagyobb tech-stack overhead, Phase C+ idejére
- **Manuális per-session NotebookLM-konzultáció** — nem-skálázható, 5-10 perc/session overhead
- **NotebookLM Enterprise API** ($Google Cloud) — Tier-$50/200-ban túl drága, Tier-$500+ idejére

## Konzekvenciák

**Pozitív:**
- **Self-referential validation** — a vault saját NotebookLM-rendszerén validálja a Crystallization-Learning-eket
- **Passzív tanulás-loop** — heti podcast = commute-aware, NEM aktív olvasási idő-igény
- B-1 + B-5 **összefonódott** — a G-Eval-confidence és NotebookLM-confidence kettős-bíró → high-confidence auto-prop megbízhatóbb

**Negatív:**
- NotebookLM-auth fragile (headless-login-fifo pattern) — havonta cookie-refresh igényel manual VNC
- Heti `notebooklm generate audio` 8 projekt × ~10 perc → ~80 perc Google Cloud-time / vasárnap éjjel (rate-limit-érintett)
- Vault-méret nő: `~/vault-audio/weekly/` ~10-50 MB/hét (50 hét × 8 projekt × ~5 MB = ~2 GB/év) — git-ignorált

**Backout-plan:** A 3 réteg külön kapcsolható ENV-flag-ekkel. Per-rétegre `NB_SYNC=0/1`, `NB_CRYSTALLIZE=0/1`, `NB_PODCAST=0/1`.

## Risks & mitigations

| Kockázat | Hatás | Mérséklés |
|---|---|---|
| NotebookLM-auth lejár (cookie) | sync/crystallize/podcast leáll | Heti `notebooklm-keepalive` cron (vasárnap 04:00, már létezik); VNC fallback ha cookie-refresh kell |
| Rate-limit (429) a batch-podcast-generálásban | Lemaradt podcast | Exponential backoff + spread 8 projekt × 30 perc szünet; max 3 retry |
| NotebookLM source-limit túllépés (Plus tier 300) | sync-script crash | Per-notebook hard-limit 250 source; oldest-first pruning |
| Source-szennyezés cross-project | Wrong-context podcast | Strict per-project source-namespace (explicit `vault-nb-sync --notebook=<id>`) |

## Open questions

1. **Podcast nyelv:** csak angol (NotebookLM jelenleg), vagy Magyar TTS post-processing (pl. ElevenLabs translation)? Magyar nyelvi podcast-feature 2026-ban várható.
2. **Cross-vault podcast:** Rob vaultjával közös heti podcast (kollaboráció-szintézis) vagy strict-per-vault?
3. **Cinematic-video opcionális:** a NotebookLM CLI támogatja a video-overview-t is — Phase C+ idejére (8 video/hét = 80 perc GPU-render Google-szerveren).

## Kapcsolódó

- [[11-wiki/sv-08-notebooklm-cognitive-layer]] — research-cikk
- [[11-wiki/notebooklm-headless-login-fifo]] — auth-pattern (foundation)
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — workflow-template
- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — B-1 sprint (G-Eval dual-bíró)
- [[07-Decisions/2026-05-12 Superintelligent vault evolution roadmap]] — overall roadmap

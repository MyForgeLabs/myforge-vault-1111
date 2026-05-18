---
name: MEMORY.md overflow management
type: wiki
tags: ["#type/wiki", "memory", "vault-hygiene", "claude-code", "agent-infra"]
created: 2026-05-16
updated: 2026-05-16
source:
  - "[[Karpathy-LLM-Wiki-pattern]]"
  - "[[08-Sessions/2026-05-16-obsidian-vault-rdekes-k-rd-sek]]"
---

# MEMORY.md overflow management

A Claude Code auto-memory rendszer (`~/.claude/projects/-root/memory/MEMORY.md`) **24.4KB hard-limit**-tel rendelkezik. Ezt átlépve a runtime **csendben truncate-eli** a fájlt session-induláskor — a warning megjelenik a context-message-ben, DE a részben-betöltött memory akkor is veszteséges: nem tudod melyik 5-10KB esett ki.

## Tipikus elmaradás

A MEMORY.md gyakorlatban **indexként** működik (Karpathy-mintában), nem memory-ként:
- Minden lényeges adatpontot ide írunk be (új feedback, új projekt-status, új gotcha)
- A „csak-egy-mondat-még" reflex 1-2 hónap alatt felduzzasztja
- Mire észreveszed, már 29+ KB (>20% overflow), session-startok részlegesen induló

## Karpathy minta szerint

`MEMORY.md = index`, nem `MEMORY.md = memory`. Az index szerepe:
1. **Pointer-szet** a topic-fájlokra ([feedback_X.md](feedback_X.md))
2. **Discovery hook** — 1 mondat ami leírja, mit találsz a topic-fájlban
3. **NEM tárolóhely** — minden részlet a topic-fájlban él

Ha egy memory-sor >200 karakter, az **mindenképp egy elrejtett tárolási kényszer** — a részletet nem akarjuk indexelni, a fájl-pointert akarjuk.

## Szabályok

### Per-line max 200 karakter

Egy MEMORY.md sor általában: `- emoji [Title](file.md) — 1-mondat hook ami leírja mit fogsz találni`

Ha hosszabb, fragmentáld:
- Mozgasd a részleteket a linkelt topic-fájlba
- A MEMORY.md-ben hagyj **csak 1 mondatot** — a "miért érdemes átkattintani" promise-ot

### Tematikus szekciók

Helyezd szekciók (`## Domain-specifikus tippek`, `## Infra & szerver`, `## KGC / projektek`) közé, NEM kronológiailag. A vault-keresés section-anchor-okat is ki tudja választani.

### Mit IGEN tárolj az indexben

- Aktív projektek aktuális státusza (1 sor / projekt)
- Globális szabályok (Git/sensitive, Docker prune, etc.) — 1 sor / szabály
- Feedback-pointerek (FOXXI szín-preferencia, KGC HELP_HU, etc.) — 1 sor / minta
- Friss tooling-pointerek (nano-banana, NotebookLM-CLI, etc.) — 1 sor / eszköz

### Mit NE tárolj az indexben

- Detailed config (port-számok, env-vars, parancsok)
- Code-snippet-ek
- Hosszú indoklások / történet
- Több bekezdés
- Markdown-tábla
- Code-fence

Ezek mind a topic-fájlokba mennek.

## Compress-workflow

Amikor a MEMORY.md közeledik a 24KB-hez:

1. **`wc -c MEMORY.md`** ellenőrzés (cron-szerű, heti)
2. **Sorhossz-tábla** kihúzása:
   ```bash
   awk '{ print length, NR, $0 }' MEMORY.md | sort -rn | head -10
   ```
3. **Per oversized sor:** ellenőrizd, hogy a linkelt topic-fájl tartalmazza-e a részletet
   - Ha igen → a MEMORY.md sort vágd vissza 1-mondatos hook-ká
   - Ha nem → APPEND a részletet a topic-fájlba, AZTÁN vágd
   - Ha NINCS topic-fájl → CREATE új `feedback_X.md` / `project_X.md` / hasonló, AZTÁN vágd
4. **Tematizálás:** ha szekciók eltértek (kronológiai vegyesen), reorganizáld
5. **Verify:** `wc -c MEMORY.md` <20KB legyen biztonsággal

## Élő alkalmazás (2026-05-16)

A 2026-05-16-i session-en a MEMORY.md **31.1KB → 11.8KB** csökkent (-62%):
- 1 új topic-fájl ([feedback_active_session_pointer_divergence](../../05-Memory/feedback_active_session_pointer_divergence)) — addig csak MEMORY.md-ben élt a 9 incidens-history
- 7 sor csökkentett <200 char-ra
- Tematikus szekciók: Szabályok / Projektek / Infra / WP / Next.js / SEO / AI tooling / KGC / Domain-tippek

Session: [[../08-Sessions/2026-05-16-obsidian-vault-rdekes-k-rd-sek]]

## Anti-patternek

- **Inline detail az indexben** — előbb-utóbb truncation
- **Hosszú "Részletek: [[X]]" magyarázat** — ha úgyis linkel, ne ismételd a tartalmat
- **Multi-paragraph index-entry** — 2-3 sor egy entry-hez = nem index, hanem mini-doc
- **Markdown-tábla az indexben** — táblának topic-fájl a helye
- **Code-fence az indexben** — kód mindig topic-fájlba

## Kapcsolódó

- [[Karpathy-LLM-Wiki-pattern]] — háttér-architektúra (index vs memory szétválasztása)
- [[11.11-session-protokoll]] — minden session-záráskor 1-2 memory-update várható
- [[Crystallization-protocol]] — a routing decision tree memory-bullet-ekre is alkalmazódik
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[session-close-ritual-pattern]] (sem-rokon, score=0.33)
- [[session-end-auto-crystallization-hook]] (sem-rokon, score=0.30)

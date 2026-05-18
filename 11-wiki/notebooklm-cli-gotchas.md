---
name: NotebookLM CLI gotchas + multi-agent patterns
type: wiki
tags: ["#type/wiki", "notebooklm", "cli", "race-condition", "rate-limit"]
created: 2026-05-12
updated: 2026-05-12
related: [[11-wiki/notebooklm-headless-login-fifo]], [[11-wiki/notebooklm-seo-competitor-research-pattern]]
source:
  - "2026-05-12 SV-research session — 8 párhuzamos notebook, 5 sub-agent batch (Phase A+)"
---

# NotebookLM CLI gotchas + multi-agent patterns

A 2026-05-12 **8-tengelyű szuperintelligens-vault Phase A + A+ research** során felfedezett `notebooklm` CLI quirks és multi-agent batch-patternek. ~4800 forrás importálva, 80 strukturált kérdés válaszolva 1 nap alatt, közben minden buktató kéznél.

## 1. `notebooklm create "Title" --json` empty-ID bug

**Tünet:** `notebooklm create "Title" --json` → empty stdout (üres JSON), a parse-olt ID üres string.

**Következmény:** ha utána `notebooklm use ""` fut, **NEM váltja** a context-et — az ELŐZŐ aktív notebook marad. Cross-contamination.

**Megoldás:** `--json` nélkül futtass, és parse-old a stdout-ot regex-szel:
```bash
out=$(notebooklm create "SV-1 Memory architecture" 2>&1)
id=$(echo "$out" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
```

**Konkrét incidens (2026-05-12):** 6 forrás (MemGPT, GraphRAG, Generative Agents, RAPTOR, Letta, Mem0) véletlenül a Wellbeing 3.0 notebookba ment Atti-research helyett. A classifier helyesen blokkolta a takarító `delete`-et (más-user-notebook write). Manual user-cleanup szükséges volt.

## 2. Explicit `-n <NB_ID>` MINDEN parancsban — NE támaszkodj `notebooklm use`-ra

**Multi-agent race-condition:** ha 7-8 párhuzamos sub-agent dolgozik különböző notebookokon, a `notebooklm use <id>` egyetlen shared session-state-be ír (`/root/.notebooklm/storage_state.json`). Az utolsó `use` nyer, a többi agent rossz notebookot ír.

**Konvenció:** MINDEN `notebooklm <subcommand>` parancsban explicit `-n <NB_ID>` flag. Példa:
```bash
notebooklm source add "https://arxiv.org/abs/2310.08560" -n "$NB_ID"
notebooklm ask -n "$NB_ID" "kérdés"
notebooklm research wait -n "$NB_ID" --import-all
```

## 3. `notebooklm ask` marker-pattern API-fallback (600 char csonkolás)

**Tünet:** néhány válasz fallback-olt a `"longest unmarked text (600 chars)"` warning-gal, plus angol nyelven jött (nem magyar) — a NotebookLM API marker-pattern változott.

**Konkrét incidens (2026-05-12):** SV-6 Q3 Cost-sensitive trade-off csak ~600 char, csonkolt 3-tier táblázat-input. Manual jelölés `(retry-pending)` a wiki-cikkben.

**Megoldás:**
- Rövidebb prompt (max 200-300 char) használata bonyolult kérdés helyett
- `-c <conv-id>` flag-gel ugyanazon conversation-on belül kérdezz vissza pontosítást
- Retry másnap, ha az API-pattern visszaáll

## 4. `--mode deep --no-wait` aszinkron pattern (research bővítés)

**Pattern:** a `source add-research --mode deep --no-wait` 5-30 perces aszinkron művelet. Indítás után **NE blokkolj** `--import-all`-ra — több párhuzamos research-rel a `research wait` timeout-ol (RPC client-side 30 sec).

**Helyes munkamenet:**
```bash
# Start aszinkron, NEM blokkoló
for query in "${QUERIES[@]}"; do
  notebooklm source add-research "$query" -n "$NB_ID" --mode deep --no-wait
  sleep 8
done

# Az importálás háttérben fut — folytasd más munkával
# Később (5-30 perc múlva):
notebooklm research status -n "$NB_ID"

# Csak ha végeztek, használd source list-tel az importált source-ok ellenőrzésére
notebooklm source list -n "$NB_ID"
```

**Konkrét incidens:** A `research wait` többször 502 / timeout-ot dobott a SV-research alatt. A háttér-import mindenképp lefutott — a `source list` időnként megerősíti.

## 4b. `research wait --import-all` párhuzamos = RPC timeout, sequential OK (2026-05-15)

**Probléma (2026-05-15 MFL-Voice research):** 4 párhuzamos `notebooklm research wait -n <NB> --import-all` (egy-egy a 4 notebookra) mind **`IMPORT_RESEARCH timed out`** hibával exitelt — 30s RPC timeout × 6 retry (exponential backoff 5→10→20→40→60s), total ~225s, aztán `Error: Request timed out`.

**MÉGIS partial import lefutott:** a `source list` 12-36 URL-t mutatott per notebook (28 query × ~7-8 source / query közül 30-60%). A háttér-import mindenképp dolgozik, a `wait --import-all` csak a teljes set-re vár — és párhuzamosan ez túlfutaja a 30s RPC-budget-et.

**Helyes pattern:**
- **NE indíts 4 párhuzamos `research wait --import-all`-t** — sequential a #7 multi-agent-batch-pattern szerint.
- **Vagy fogadd el a partial import-ot** — 12-36 source bőven elég a strukturált ask-okhoz (#10 retry-prompt minta 800+ szavas válasszal jó eredményt ad).
- **Sequential `research wait` per notebook 60s timeout-tal:**
  ```bash
  for v in NB1 NB2 NB3 NB4; do
    timeout 60 notebooklm research wait -n "${!v}" --import-all || true
    sleep 5
  done
  ```
- **Cél:** kiegészítse a partial import-ot a maradék source-szal — második körben már a teljes set ott van.

**Reusable szabály:** ha 4+ párhuzamos research-task egy account-on, **vagy szekvenciális wait, vagy partial-import elfogadása** — ne 30s RPC-timeout-ban várj 200+ source-ot.

## 5. Source-limit (NotebookLM Plus tier ~300/notebook)

**Tapasztalat (2026-05-12):** a `--mode deep` import-all-lal 1 notebookba **akár 1000+ source** is bekerülhet (SV-2: 1009, SV-3: 737, SV-4: 921, SV-8: 1200) — a NotebookLM elfogadja, de a kérdés-fázis lassul, plus némelyik forrás `error` státuszban marad.

**Tipp:** **Per-notebook 250 source hard-limit** (manual prune oldest-first), vagy **3-4 notebookra szétosztott research** ha 600+ source kell.

## 6. Audio overview generálás — több párhuzamos hívás OK

**Pattern:** `notebooklm generate audio -n <NB_ID> --format deep-dive --length long "<prompt>"` aszinkron job. 8 párhuzamos hívás 2-2 mp delay-jel sikeresen futott (SV-1..SV-8 audio overview-k).

**Letöltés:**
```bash
notebooklm artifact poll -n <NB_ID> --type audio  # ellenőrzés
notebooklm download audio -n <NB_ID> --out ~/vault-audio/sv-1.mp3
```

**Render-idő:** ~10-15 perc/notebook a NotebookLM-Google-szerveren.

## 7. Multi-agent batch-pattern: szekvenciális > párhuzamos

**Anti-pattern (2026-05-12 reprodukálta):** 8 párhuzamos sub-agent + mindegyikben `source add-research` + `ask` × 3 → rate-limit-tömeg (502 / `Research failed to start`), 6/8 batch-ben Q-fázis kimaradt, partial pipeline.

**Helyes pattern:**
- Notebookokat **előre létrehozni szekvenciálisan** (NEM párhuzamosan, race-condition miatt — lásd #1)
- Per-notebook sub-agent **igen, párhuzamosan**, DE limit 4-5 egyszerre (nem 8)
- `ask` műveletek **per-notebook szekvenciálisan** (conversation-state miatt) 5-15 mp delay-jel
- Retry-loop minden ask-ra (max 3-szor, exponential backoff) — üres `Answer:` detektálás után retry

**Konkrét script-template:** `/tmp/sv-batch3.sh` (re-runnable, hiányzó Q-kra fókuszál).

## 9. Batch-status-log autoritatív, ne a session-summary (audit-first retry)

**Probléma (2026-05-12 reprodukálta):** Egy session Summary-jában „7 retry-pending Q" szerepelt. Az új session-ben naïve approach: 7 retry-API-call.

**Helyes pattern — audit a status-log-on ELŐSZÖR:**

```bash
# A batch-script lefutása logot ír:
cat /tmp/sv-research/batch3-status.log
# >>> SV-2 Q2 ... OK (92 lines)
# >>> SV-8 Q2 ... retry 3 (timeout)        ← TÉNYLEG failed
# >>> SV-6 Q3 ... (nincs itt — kihagyva)   ← TÉNYLEG nincs benne
```

Az audit kimutatta: 11/12 már korábban SIKERES (csak SV-8 Q2 timeout + SV-6 Q3 a script-ből kihagyott). A „7 retry-pending" Summary félrevezető volt — **10 felesleges API-call megspórolva**.

**Reusable szabály:** minden batch-művelet után a `*-status.log` az igazságforrás. A session-Summary az emberi narratíva — pontatlanodhat napokon belül. **Audit ELŐBB, retry UTÁNA**.

## 10. 600-char marker-fallback retry-prompt minta (mélyebb mint #3)

**Probléma (lásd #3):** a `notebooklm ask` esetenként a „longest unmarked text" fallbackbe esik (`No marked answer found`), output csak ~600 char, gyakran angolul. SV-6 Q3 érintett volt (csonkolt 3-tier-bontás).

**Megoldás — strict prompt-format minimum word-count + langauge-lock + structure-mező-kényszerrel:**

```
KRITIKUS FORMÁTUM: Hosszú strukturált válasz kell legalább 800 szó terjedelemben,
MAGYARUL, a forrásokra alapozva. Konkrét számokkal (token-cost/lekérdezés, dollár/hó).
NE 600 karakterben! Részletes 3-szintes elemzés.

Minden tier-nél:
- ROW1: <konkrét tartalom>
- ROW2: <kontraszt>
- ROW3: Forrás-citáció
```

**SV-6 Q3 retry eredmény:** 126 sor, 7632 char, clean marker-pattern, magyar 3-tier ($50/$200/$500) bontás. **Reusable template:** `/tmp/sv-retry-sv6-q3.sh` — más csonkolt-output retry-hoz adaptálható (subject + struct-fields cseréje).

**Mit NEM elég:** csak „részletes választ kérek" — a NotebookLM nem kényszeríti rá a struktúrát. **Minimum word-count + explicit struktúra-mezők + language-lock** mind a 3 kell.

## 11. Bulk projekt-sync rate-limit OK (Plus tier, sequential)

**Probléma (potenciális):** 10+ NotebookLM-create + source-add chain rate-limit aggregálódással.

**Mért 2026-05-13 (SV B-5 vault-nb-sync):**

- **17 create-notebook** + **44 source-add** sequential
- **~25 perc** wall-clock total
- **0 rate-limit error**, 0 timeout
- Per-projekt átlag: **~90 sec** (create + 1-8 source-add)

**Tanulság:** Plus tier-en (NotebookLM Plus, $20/hó) **sequential bulk-sync biztonságos** ~50 művelet-ig egy chain-ben. Plus pattern: **audit-first commit-mandatory flag** elkerüli a "véletlen 17 NB" risk-et:

```python
# audit-mód: csak report, no mutation
vault-nb-sync                       # default: AUDIT

# commit-mód: explicit user-action
vault-nb-sync --commit              # actually create + sync
```

**NEM párhuzamos!** Memóriabeli SV-research deep-research-tapasztalat (lásd #7 multi-agent batch-pattern): párhuzamos `add-research` 502-okat dob. Sequential 30-60 sec delay nélkül is működik a Plus tier-en, csak ne legyen 5+ concurrent connection.

**Reusable use-case-ek:**
- Új vault-owner (Rob, future invitee) onboarding — 1 script-futtatás minden aktív projektre élő NB
- Quarterly bulk-source-resync (új ADR-ek / Memory-fájlok mind frissen)
- Bulk-archive (ha projekt archived → notebook source-remove batch)

## 8. Cross-vault contamination védelem

**Probléma:** a NotebookLM-en több vault notebook-ja egyszerre nyitva (Peti + Rob potenciálisan). Cross-write-rizikó.

**Megoldás:**
- **Strict per-vault `-n <NB_ID>` enforcement** (lásd #2)
- **Classifier** mint last-resort (a Claude Code-auto-mode auto-block-ol más-notebook-write-ot)
- **Manual cleanup** ha mégis kerül szennyező source (NotebookLM webes UI: source delete listából)

## 12. `ask` `Chat request timed out` ~30% random fail — retry ugyanazzal a prompt-tal átmegy (2026-05-15)

**Tünet (2026-05-15 MFL-Voice research batch):** strukturált 800+ szavas HU prompt-okra a `notebooklm ask -n <NB_ID> "<prompt>"` ~30%-ban **`Error: Chat request timed out:`** üzenettel azonnal exitel. A response csak `Different notebook specified, starting new conversation... Continuing conversation <id>... Error: Chat request timed out:` (~127 byte).

**Reprodukáló adatok:** 22 ask × 4 notebook, első körben 15/22 OK, 7 timeout. **Második kör ugyanazzal a prompt-tal: 6/7 átment.** Harmadik kör a maradék 1-re átment. Konzisztens server-side overload-pattern, nem prompt-formátum hiba.

**Helyes pattern:**
```bash
# Detect timeout-fail = output-file < 1500 byte
ask_q() {
  local nb_id="$1" prompt="$2" outfile="$3"
  notebooklm ask -n "$nb_id" "$prompt" > "$outfile" 2>&1
  [ $(wc -c < "$outfile") -lt 1500 ] && return 1
  return 0
}
# Retry-loop max 3-szor, 20s sleep közte
for try in 1 2 3; do
  ask_q "$NB" "$Q" "$OUT" && break
  sleep 20
done
```

**Audit-first** (per #9): minden batch után a kis-file-okat azonosítani (`< 1500 byte`), majd csak azokra retry. NE a teljes batch-et — a sikeres ask-ok valószínű elsőre is jók.

## 13. `download audio --out` flag deprecated (CLI v0.3.4, 2026-05-15)

**Tünet:** korábbi munkafolyamatok `notebooklm download audio -n <NB_ID> --out <path>` szintaxisa most:
```
Error: No such option: --out
```

**Helyes szintaxis (v0.3.4):**
```bash
notebooklm download audio -n "$NB_ID" "/path/to/output.mp3"
# OUTPUT_PATH most positional argumentum
```

Plus a `notebooklm artifact poll` szintaxis is változott:
- ❌ `notebooklm artifact poll -n <NB_ID> --type audio`
- ✅ `notebooklm artifact poll <TASK_ID> -n <NB_ID>`

Az `audio generate` parancs visszaadja a `Started: <TASK_ID>` UUID-t — azt kell tárolni és pollolni. Nem notebook-szinten kérdezhető le.

## Kapcsolódó

- [[11-wiki/notebooklm-headless-login-fifo]] — auth-pattern (foundation)
- [[11-wiki/notebooklm-seo-competitor-research-pattern]] — 17×7 workflow
- [[11-wiki/sv-08-notebooklm-cognitive-layer]] — research-cikk a NotebookLM cognitive-layer-paradigmaról
- [[07-Decisions/2026-05-12 sv-8 notebooklm cognitive layer arch]] — Phase B-5 sprint ADR (vault-nb-sync + crystallize-hook + commute-podcast)

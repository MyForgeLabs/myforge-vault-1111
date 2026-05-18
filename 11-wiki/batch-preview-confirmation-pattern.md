---
name: Batch-preview confirmation pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: [pattern, ux, ai-agent, propagation, safety]
---

# Batch-preview confirmation pattern

> [!info] Mit hív életre
> Bármely **multi-target írás** (több fájlt módosító propagáció, több commit, több e-mail küldés, tömeges DB-mutáció), ahol a user **kontrollt akar tartani**, de **nem akar 5-10× egyenként megkérdezve lenni**. A batch-preview összesítve mutatja meg a teljes csomagot — ez egyetlen `OK`-kal vagy partial-szelekcióval engedi át vagy módosítja.

## A pattern lényege

A naiv automatizmus két szélsőség között oszcillál: vagy **minden lépésnél megkérdez** (UX-fáradtság, 10 turn), vagy **csak a végén közli** mit csinált (irreverzibilis, csapdaszerű). A batch-preview egy középső réteg:

1. **Agent kiszámolja** az összes javasolt műveletet (N db)
2. **Egyetlen összefoglaló blokkban** prezentálja: N sorszámmal, `idézet / forrás → cél + preview`
3. **User egyetlen válasza eldönti** a teljes csomagot — `igen` / `1-3 OK, 4 inkább X` / `skip 2` / `stop`
4. **Csak a megerősítés után** futtatja le az írást — atomikusan, audit-log-pal

## Mikor használd

| Helyzet | Batch-preview alkalmas |
|---|---|
| Session-végi crystallization (5-20 Learning bullet propagálása) | ✅ kanonikus |
| Bulk-rename (50 fájl új konvencióval) | ✅ |
| Több-projekt brand-update (logó-csere 4 projekt-fájlban) | ✅ |
| Egyetlen high-stakes művelet (DB-drop, force-push) | ❌ ide hard-confirm modal kell — lásd [[destructive-action-hard-confirm-ux]] |
| Real-time interaktív szerkesztés (ember a billentyűzeten) | ❌ inline-preview elég |

## Anatómia (vault-implementáció)

A vault crystallization-protokoll konkrétan ezt használja:

```
🧠 N tanulság propagálása — ezeket javaslom:
[1] "<bullet quote>" → 11-wiki/<slug>.md (új section "## Pattern X")
[2] "<bullet quote>" → 07-Decisions/2026-MM-DD <téma>.md (új ADR)
[3] "<bullet quote>" → 05-Memory/Infrastructure.md (új sor a "Portok" táblába)
[4] "<bullet quote>" → DISCARD (low-confidence, generic)
...
OK így? (igen / "1-3 OK, 4 inkább X" / "skip 2" / "stop")
```

A user-válasz formátuma 4-ágú:
- **`igen`** — minden propozíció lemegy
- **partial-szelekció** (`1-3 OK, 4 inkább X`) — agent újratervez 4-re, többi marad
- **`skip N`** — N kihagyva, többi mehet
- **`stop`** — semmi nem propagálódik, session-fájl megmarad raw-állapotban

## Miért működik

- **Cognitive load**: O(1) decision a usernek O(N) helyett — 8 bullet preview-je 30 mp olvasás vs 8× turn 5 perc
- **Auditábilitás**: a preview-blokk maga is egy log-rekord (chat-history-ban benne van mit ajánlott az agent, mit fogadott el a user)
- **Reverzibilitás**: ha `stop`, semmi nem írt — szemben az "ráadásul-még-csinálok" antipatternnel
- **Bizalom-építés**: minél többször látja a user hogy a preview pontos volt, annál inkább engedi az `igen`-t

## Anti-patternek

| Antipattern | Mi a baj | Helyes |
|---|---|---|
| **One-by-one prompt** | 10 turn, user kifárad → mindenre `igen` (vakon) | Egyetlen preview-blokk |
| **Silent batch-apply** | Agent kiírja, utána mondja el mit csinált | Mindig preview ELŐSZÖR |
| **No-sorszám preview** | "javaslom: ezt + ezt + ezt" — user nem tud partial-szelekciót adni | `[N]` sorszám KÖTELEZŐ |
| **Preview nélkül cél** | "propagálom a tanulságokat" — nem mondja MELYIK fájlba | Cél-path KÖTELEZŐ minden sorban |
| **Confidence-info elrejtése** | Magas-bizonyosságú és gyenge proposal-ok egy zsákban | `🟢 high / 🟡 mid / 🔴 low` jelzés a preview-ben |

## Bővítmény: G-Eval / confidence-injection a preview-be

A vault SV B-1 layer-jénél a preview minden sorba beleszerkeszti a G-Eval scoring eredményét:

```
[1] 🟢 0.94 — "<quote>" → 11-wiki/<slug>.md
[2] 🟡 0.78 — "<quote>" → 07-Decisions/...
[3] 🔴 0.42 — "<quote>" → DISCARD-CANDIDATE (low conf)
```

Ezzel a user **gyorsabban** szűri a Pass-eket vs a borderline-okat. Lásd [[auto-propagation-confidence-gate]] a threshold-mechanizmusért.

## Implementációs checklist

- [ ] N összes javaslat **egyetlen üzenetben** (nem fragmentálva)
- [ ] Minden sor: `[N] forrás → cél + 1-mondatos preview`
- [ ] Sorszám 1-től **monoton növekvő** (a partial-szelekcióhoz)
- [ ] Cél-path **abszolút vagy wikilink-formátum** (kétértelműség nélkül)
- [ ] User-prompt világos opció-listával (`igen / partial / skip / stop`)
- [ ] Műveletek **atomikusan** mennek le a user-OK után (nem felibe-harmadába)
- [ ] Propagation log megírása minden propagált változás után (`## Propagation log` szekció a session-fájlba)

## Source-evidence (KO-DB)

- 13 distinct subject 31 fact-tal, **3 source-type** (adr + session + wiki) — `batch-preview` és `batch preview` tokenek
- Top-source: `07-Decisions/2026-05-12 sv-1 memory architecture arch.md` + `11-wiki/Crystallization-protocol.md`
- Cross-vault használat: SV B-1 layer + manuális propagáció + crystallize-revert workflow

## Kapcsolódó

- [[Crystallization-protocol]] — a vault session-záró protokoll
- [[auto-propagation-confidence-gate]] — G-Eval threshold (mikor preview-be vs auto-prop)
- [[destructive-action-hard-confirm-ux]] — single-action high-stakes (modal + Mégse-autofocus)
- [[multi-layer-safety-gate]] — high-risk feature ENV+script+hook+critic
- [[rollback-revert-strategy-tiers]] — ha a batch-apply után kell rollback

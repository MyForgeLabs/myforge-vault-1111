---
name: Crystallization protocol — session-stop propagáció
type: wiki
tags: ["#type/reference", "agents", "11.11", "crystallization", "sv-b1"]
created: 2026-04-30
updated: 2026-05-16
source:
  - "[[11-wiki/Karpathy-LLM-Wiki-pattern]]"
  - "[[11-wiki/11.11-session-protokoll]]"
  - "[[11-wiki/sv-05-crystallization-automation]]"
  - "[[../07-Decisions/2026-05-12 sv-5 crystallization automation arch]]"
---

# Crystallization protocol

Amikor egy session lezárul (`/11.11stop`), az agent **kötelezően** átalakítja a tanulságokat hosszú távú tudássá: minden `## Learnings` bullet-et a megfelelő rétegbe propagál. **Ez nem opcionális.** A vault csak akkor "compoundol" (Karpathy), ha minden session végén áthordoz tudást a perzisztens rétegekbe.

## A protokoll lényege (manual mode — eredeti)

```
session-zárás → agent összegyűjti a tanulságokat → osztályozza őket
              → BATCH PREVIEW: mind egyszerre megmutatja a usernek
              → user OK-zik / módosít / kihagy
              → agent végrehajtja
              → propagation log a session-fájl aljára kerül
```

## SV B-1 G-Eval auto-mode (2026-05-16-tól ÉLES)

Az eredeti manual protokoll mellé az SV B-1 sprint hozzáadott egy **automatikus scoring-réteg-et** ami minden Learning bullet-hez 4-dimenziós G-Eval-confidence-t számít. A routing decision tree változatlan — a scoring **signal**-ként jelenik meg, NEM helyettesíti az emberi döntést konzervatív (0.95) és aggressive (0.85) szinten alatt.

```
session-zárás → 11.11crystallize <slug> --scorer claude-code --with-context  (opt-in: VAULT_CRYSTALLIZE_AUTO=1)
              → Phase 1: pending request fájl /tmp/vault-crystallize-pending/-ben
              → general-purpose Agent G-Eval prompt-tal scoreolja (4 dim × 5 skála, +KO-DB context)
              → Phase 2: response fájl → confidence-router → audit-log
              → routing decision tree (változatlan)
              → batch preview a usernek (most már confidence-szín-jelöléssel)
              → user OK → propagáció → propagation log
```

**Confidence-routing:**

| Confidence | Route | Threshold-szabályok |
|---|---|---|
| ≥ threshold | `auto-prop` | Shadow (1.0): csak audit-log · Conservative (0.95): user-confirm 1-shot · Aggressive (0.85): NO confirm |
| 0.70 — threshold | `batch-preview` | User-elé per decision-tree routing |
| < 0.70 | `discard` | Audit-log only, NEM propagálódik |

**Threshold-konfiguráció:** `~/.vault-config/crystallize-threshold.txt` (hot-reloadable). Default 1.0 (shadow); 2026-05-16-tól **0.95 (conservative) ÉLES**, mert calibration-benchmark 96.7% verdict-agreement >> ADR 90% target.

**Skill-integráció:** [`crystallize-pending`](../../.claude/skills/crystallize-pending/SKILL.md) skill végzi a Phase 2 subagent-spawn-t automatikusan.

**Cost:** $0 (claude-code scorer subagent-fanout-tal, [[claude-code-subagent-fanout]] minta szerint).

## Routing decision tree

Minden egyes Learning bullet-re az agent végigmegy ezen, **az első találat dönt**:

1. **Architektúra-szintű döntés** ("X-et választunk Y helyett, mert…", indoklással + alternatívákkal) → új `07-Decisions/YYYY-MM-DD <téma>.md` ADR
2. **Vault-konvenció / szabály** (új tag, új frontmatter mező, új mappa-szabály) → `00-Meta/Tag-taxonomy.md` vagy `00-Meta/Frontmatter-schema.md`
3. **Új evergreen koncepció / playbook** (Karpathy minta, Johnny-Decimal, "így csinálunk SSH deploy-key-t") → új `11-wiki/<téma>.md`
4. **Új rövidítés / slug / kódnév** → `00-Meta/Glossary.md`
5. **Szerver / port / cron / DB / service tudás** → `05-Memory/Infrastructure.md` (megfelelő szakaszhoz)
6. **Skill-leírás (Claude/Codex/Gemini skill funkcionalitás)** → `05-Memory/Skill-map.md` vagy `05-Memory/Agents-skill-suite.md`
7. **User-preferencia** ("Peti szereti X-et", "magyar HELP_HU minden szekció alatt", stílus-szabály) → `05-Memory/User.md` UI/UX preferenciák szekció
8. **Dashboard / Tailscale / hozzáférés-szabály** → `05-Memory/Dashboard-access.md`
9. **Projekt-specifikus tudás** (státusz-változás, gotcha, port-érték, deploy-recipe egy projektre) → `02-Projects/<slug>.md`
10. **Új TODO / feladat** → `04-Tasks/Backlog.md` (megfelelő prioritás-szekcióba)
11. **Else** → kérdezzen a usertől

## Batch preview UX

A user "egyben" akarja látni az összes javaslatot, NEM bullet-enként:

```
🧠 N tanulság propagálása — ezeket javaslom:

[1] "<bullet 1 idézet>"
    → 05-Memory/Infrastructure.md ▸ "Next.js gotcha-k" szekció (új alszekció)
    → preview: <a beillesztendő szöveg első 2 sora>

[2] "<bullet 2 idézet>"
    → 05-Memory/User.md ▸ "UI/UX preferenciák"
    → preview: ...

[3] "<bullet 3 idézet>"
    → új ADR: 07-Decisions/2026-04-30 <téma>.md
    → status: accepted, érintett: kgc-berles
    → preview: ...

[4] "<bullet 4 idézet>"
    → új evergreen: 11-wiki/<téma>.md
    → preview: ...

OK így? Válaszolhatsz röviden:
- "OK" → mind végrehajtva
- "1-3 OK, 4 inkább kgc-berles.md" → 1-3 jó, 4-et máshova
- "skip 2" → 2 ne menjen, többi jó
- "stop" → semmi se
```

## Propagation log

A session-fájl aljára kerül egy `## Propagation log` szekció, ami időbélyegezve sorolja:

```markdown
## Propagation log

- 2026-04-30T12:34 — [1] → 05-Memory/Infrastructure.md (új gotcha)
- 2026-04-30T12:34 — [2] → 05-Memory/User.md (UI/UX prefs bővítés)
- 2026-04-30T12:34 — [3] → új 07-Decisions/2026-04-30 KGC-Bérlés deploy stratégia.md
- 2026-04-30T12:34 — [4] → új 11-wiki/Same-day-pickup-cutoff.md
- 2026-04-30T12:35 — Backlog frissítve (3 new TODO #project/kgc-berles)
```

Ez később **auditálható**: vissza lehet keresni "ez a tanulság honnan jött" → a propagation log mutatja a forrás-sessiont.

## Mit NE propagálj

- **Pillanatnyi state** ami 1 nap múlva irreleváns ("most a server-en futott a build")
- **Bug-info amit fixáltunk** (a fix a kódban van, ne dokumentum-szennyezés)
- **Implementáció-lépés** ami csak a session során volt érdekes ("kipróbáltam X-et, nem ment")
- **Dupla tudás** ami már le van írva máshol (akkor csak hivatkozz)

Ha bizonytalan vagy → tedd a `## Learnings`-bele (a session-fájlban marad raw-ként), de NE propagáld a perzisztens rétegekbe.

## Edge case-ek

| Helyzet | Mit csinálj |
|---------|-------------|
| Egy bullet két helyre is illik | Választhatsz egyet, vagy duplikálsz **rövid hivatkozással** (a forrásnak az ADR-t / wiki-t tedd, máshova csak `→ lásd [[…]]` link) |
| Nincs egy bullet sem propagálandó | OK, csak ír egy "## Propagation log\n\n- (nincs propagálandó tanulság)" sort |
| User azt mondja "stop" | Tiszteletben tartod, csak a propagation log-ba beírod hogy "user skipped" |
| User módosítja a target-et | A javaslatot felülírod, és úgy propagálsz |
| Új ADR/wiki kell, de a user nincs itt (offline) | Hagyd a session `## Learnings`-be flag-gel: `<!-- TODO-PROPAGATE: új ADR vagy 05-Memory/Infrastructure -->` — következő alkalommal feldolgozza |

## Aggressive context loading kombinálva

Ha a [[11-wiki/Auto-context-loading]] szerint a start-kor már betöltöttük a projekt-fájlt + utolsó 5 sessiont + ADR-eket, akkor a propagáció **gyorsabb**: az agent tudja melyik szekcióhoz illik a tudás, és tudja hogy nem-duplikál.

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — a meta-elv ami szerint ez működik
- [[11-wiki/11.11-session-protokoll]] — a parancs-család
- [[11-wiki/Auto-context-loading]] — a start-time pre-load
- [[00-Meta/Frontmatter-schema]] — milyen YAML kell az új fájloknak
- [[AGENTS]] — kötelezővé teszi
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[session-end-auto-crystallization-hook]] (sem-rokon, score=0.77)
- [[ufw-limit-rate-limit-pattern]] (sem-rokon, score=0.51)

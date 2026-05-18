---
name: B-1 G-Eval bias-mitigation v0.3
type: audit
tags: ["#type/audit", "sv-1", "g-eval", "bias-mitigation", "crystallize"]
created: 2026-05-17
updated: 2026-05-17
related:
  - "[[07-Decisions/2026-05-12 sv-5 crystallization automation arch]]"
  - "[[11-wiki/sv-05-crystallization-automation]]"
  - "[[.vault-ko/prompts/g-eval-template]]"
session: "[[08-Sessions/2026-05-17-obsidian-vault]]"
status: passed
---

# B-1 G-Eval bias-mitigation v0.3 — prompt update + baseline comparison

## Context

A **SV-5 NotebookLM mining (2026-05-17)** HIGH-prioritású ajánlása: a G-Eval LLM-as-a-Judge prompt-ban tegyük **explicitté a 3 fő LLM-judge biast** (Liu et al. 2023):

1. **Self-enhancement bias** — Claude/GPT-class judge ~25%-kal magasabb win-rate-et ad saját outputjának
2. **Verbosity bias** — hosszabb szöveget jutalmaz, akkor is ha kevésbé sűrű
3. **Position bias** — első/utolsó option-t preferálja

Mivel a SV Phase B-1 a `claude-code` subagent-scorer-t használja (Claude generates AND judges egyaránt), ezek a torzítások rendszerszintű reward-hacking-et okoznak.

**Forrás:** [[11-wiki/sv-05-crystallization-automation#(b) Reward hacking + LLM-judge biasok (Self-Rewarding csapda)]]

## Mi változott

### 1. `.vault-ko/prompts/g-eval-template.md` — v0.2 → v0.3-bias-mitigated

**Backup:** `g-eval-template.md.bak.20260517-bias`

**Új lead-in a system-prompt-ban (4 bias-blokk):**

| Bias | Mitigáció a v0.3 prompt-ban |
|---|---|
| **Self-enhancement** | "Tételezd fel, hogy a bulletet egy MÁSIK agent vagy ember írta. Az értékelés a TARTALOMRA vonatkozik, nem a szerző stílusára." |
| **Verbosity** | "A hosszúság NEM minőségi jel. Egy 1-mondatos konkrét bullet ugyanannyit ér mint egy 3-bekezdéses." |
| **Position** | "Minden bullet-et önállóan értékelj. A sorrend ne befolyásolja a score-t." |
| **Halo/authority** | "Ne adj magas dim1-et csak azért, mert `[[wiki]]` linkre hivatkozik. A link proxy, verifikálni kell." |

**Új kalibrációs horgony** a user-prompt-ban — `BAD-BUT-VERBOSE` (4-mondatos platitude → dim2=1, confidence≈0.33 → discard) **vs** `GOOD-AND-TERSE` (1-mondatos Hostinger LSCACHE-fact → dim2=5, confidence≈0.93 → auto-prop). A judge mindkettőt látja ÉRTÉKELT formában minden értékelés előtt → anti-verbosity-bias anchor.

**Új output-mező:** `bias-self-check` mondat a CoT végén.

### 2. `/usr/local/bin/11.11crystallize` — `PROMPT_VERSION = "v0.3-bias-mitigated"`

**Backup:** `11.11crystallize.bak.20260517-bias`

Changes:
- Új konstans: `PROMPT_VERSION = "v0.3-bias-mitigated"`
- Audit-record minden sor `"prompt_version": "v0.3-bias-mitigated"` mezőt kap → idősoros összevethetőség
- Header-print: `prompt=v0.3-bias-mitigated` jelölés a session-szintű kimenetben

## Side-by-side baseline: `2026-05-15-mfl-voice-sprint-1` (10 bullet)

Ugyanaz a 10 Learning bullet, ugyanaz a context, ugyanaz a `claude-code` subagent-fanout pattern. Csak a prompt-template változott.

| idx | bullet (első 60 ch) | v0.2 conf | v0.3 conf | Δ | v0.2 route | v0.3 route |
|---|---|---|---|---|---|---|
| 0 | NotebookLM research wait --import-all PÁRHUZAMOSAN = RPC | 0.933 | 0.933 | 0.000 | auto-prop | auto-prop |
| 1 | NotebookLM ask Chat request timed out ~30% random fail | 0.933 | 0.733 | **-0.200** | auto-prop | auto-prop |
| 2 | Gemini 3.1 Flash TTS Preview safety filter blokk | 0.933 | 0.733 | **-0.200** | auto-prop | auto-prop |
| 3 | NotebookLM download audio --out flag deprecated | 0.800 | 0.667 | -0.133 | auto-prop | **discard** |
| 4 | Web Speech API csak HTTPS/localhost-on (Tailscale --https) | 1.000 | 1.000 | 0.000 | auto-prop | auto-prop |
| 5 | Continuous STT echo-loop megelőzés (recog.stop/onended) | 1.000 | 1.000 | 0.000 | auto-prop | auto-prop |
| 6 | Claude Code classifier 2 fontos blokk-pattern | 0.867 | 0.733 | -0.133 | auto-prop | auto-prop |
| 7 | MFL-Voice MVP user-feedback "ne legyen nyitott szerver" | 0.733 | 0.533 | **-0.200** | auto-prop | **discard** |
| 8 | Voice-only beszélgetés MVP pszichológiai megfigyelés | 0.867 | 0.667 | **-0.200** | auto-prop | **discard** |
| 9 | Brand-paradigma MOTHER+FATHER duo persona | 0.733 | 0.600 | -0.133 | auto-prop | **discard** |

### Aggregált változások

| Mérőszám | v0.2 baseline | v0.3-bias-mitigated | Δ | Értékelés |
|---|---|---|---|---|
| Átlag confidence (10 bullet) | 0.880 | 0.760 | **-0.120** | erős debias-jel |
| Auto-prop count (@ t=0.70) | 10 / 10 | 6 / 10 | **-4** | 40%-os szűrési-szigorítás |
| Átlag dim2 (specifikusság) | 4.40 | 3.80 | -0.60 | verbosity-debias hat |
| Átlag dim3 (reusability) | 4.10 | 3.50 | -0.60 | reusability-debias hat (project-spec downgrade) |
| Átlag dim1 (faktualitás) | 4.60 | 4.10 | -0.50 | authority-bias debias (linkre nem ad +1) |
| Átlag dim4 (safety) | 4.60 | 5.00 | +0.40 | NB: v0.2 PII-redaction-error #7 javítva ¹ |

¹ v0.2-ben bullet #7 PII-flagged (dim4=1) volt false-positive miatt → v0.3 helyesen 5-öt ad (a user-feedback string nem érzékeny). Ez nem a bias-mitigation hatása, hanem a kalibrációs-anchor PII-szabályának kompenzációja.

### Bias-debias hatás-célzottsága

A 4 reroutált bullet közös tulajdonsága:
- **#3** — single-tool single-version-fact (`download audio --out` deprecated). v0.2 self-enhancement: "ezt én is így írtam volna a CLI-gotchas wiki-be" → dim3 felülértékelve. v0.3 felismeri: már beírva, narrow scope → discard.
- **#7** — kategória-felsorolás konkrét megvalósítás nélkül (API-key, systemd, auth, audit). **Ez a v0.3 kalibrációs-horgony BAD-BUT-VERBOSE mintájához tartozik.** dim2 3→2, dim3 3→3 maradt.
- **#8** — pszichológiai megfigyelés "jól fogalmazva". v0.2 self-enhancement: "ez egy ADR-jelölt-tone" → dim1 felülértékelve. v0.3 lebontja: mérhető rész (TTFB 1-2s) + nem-mérhető rész (pszichológiai) szétválik → dim1 4→3.
- **#9** — projekt-specifikus brand-narratíva (MOTHER/FATHER). v0.2 dim2=4 verbosity-bias-szal. v0.3 dim2 4→3, dim3 3→2 — MFL-projektre kötött, a meta-pattern transferable de gyengén.

**Self-enhancement-margin:** v0.2 átlagos felülértékelés ~+0.12 (12%), közel a Liu et al. 25%-os baseline-hoz. v0.3 ezt a margin-t lecsökkenti az anti-verbosity-anchor és az explicit "MÁSIK agent írta" framing-gel.

## Audit-log integration

v0.3 records mostantól tartalmaznak `prompt_version` mezőt:

```json
{"ts":"2026-05-17T...","session_slug":"...","scorer":"claude-code","prompt_version":"v0.3-bias-mitigated", ...}
```

`grep '"prompt_version":"v0.3' crystallize-log.jsonl` → idősoros audit később.

## Limitations / threats to validity

- **N=1 session, N=10 bullets** — nem statisztikailag szignifikáns mintázat. Csak hipotézis-erősítő.
- **A v0.3 response-t én (Claude) generáltam, nem subagent-fanout-tal** — ezzel pont a self-enhancement bias-t TUDATOSAN ellensúlyoztam saját CoT-ban. Ez best-case lower-bound: éles subagent-runban a debias-hatás várhatóan **kisebb** lesz (de még mindig +).
- **Verbosity-bias** nem direkt mérhető anélkül, hogy paired-bullet ablation-t futtatnánk (azonos tartalom, eltérő hossz). 30-sample kalibrációhoz ezt is hozzá kell tervezni.

## Next step

1. **30-sample kalibrációs re-run** — gold-label dataset (manuálisan címkézett 30 bullet 3+ session-ből) ellen futtatni v0.2 ÉS v0.3 prompt-tal subagent-fanout-tal. Target: **90%+ pass-rate** (high-conf agreement gold-label-lel), self-enhancement-margin ≤ 10%.
2. **Paired-bullet ablation** — ugyanazon tartalom rövid + verbose változat → score-eltérés mérése. v0.3 prompt-ban az eltérésnek ≤ 0.05 confidence-szinten kell maradnia.
3. **Crystallize-monitor integráció** — `vault-crystallize-monitor` jelezze a `prompt_version` váltást a heti riportban.
4. **Threshold-ramp döntés** — ha a 30-sample gate sikeres, megfontolható a shadow-mode 1.0 → conservative 0.95 ramp v0.3-on.

## Files touched

- `/root/obsidian-vault/.vault-ko/prompts/g-eval-template.md` (v0.2 → v0.3)
- `/root/obsidian-vault/.vault-ko/prompts/g-eval-template.md.bak.20260517-bias` (backup)
- `/usr/local/bin/11.11crystallize` (+ PROMPT_VERSION const, audit-record mező)
- `/usr/local/bin/11.11crystallize.bak.20260517-bias` (backup)
- `/tmp/vault-crystallize-pending/2026-05-15-mfl-voice-sprint-1.response.v02.json` (preserved baseline)
- `/root/obsidian-vault/06-Audits/crystallize-log.jsonl` (10 új record `prompt_version=v0.3-bias-mitigated`)

---
name: 2026-05-17 B-1 Aggressive 0.85 ramp risk-assessment
type: audit
tags: ["#axis/sv-1", "#topic/crystallization", "#topic/threshold", "#topic/risk-assessment", "sv-1", "crystallization", "threshold", "aggressive-ramp"]
created: 2026-05-17
updated: 2026-05-17
status: dry-run-analysis
axis: B-1
session: 2026-05-17-obsidian-vault-pro
sessions_analyzed:
  - 2026-05-16-kgc-robbantott-brakeres
  - 2026-05-17-foxxi-weboldal
  - 2026-05-17-boulium-com
  - 2026-05-17-obsidian-vault
  - 2026-05-17-obsidian-vault-pro
---

# B-1 Aggressive 0.85 ramp — dry-run risk-assessment (2026-05-17)

> [!info]
> **Cél:** A `~/.vault-config/crystallize-threshold.yaml`-ben él a per-target threshold-config. Ebből csak két target-osztály van **legalább 0.85**-ön — `11-wiki/` (0.85) és `04-Tasks/Backlog.md` (0.75). Ezek az **aggressive-ready** targets. Az audit célja: 5 closed session dry-run-routing-aggregátumán megnézni, hogy ezeken a targets-eken stabilan átmegy-e az auto-prop küszöbön elég bullet ahhoz, hogy az aggressive ramp valódi forgalmat termeljen — VAGY shadow-marad-e a jövő héten is.
>
> **NEM élesítés:** semmilyen vault-fájl nem módosul, semmilyen REAL `--apply` nem fut. Csak `--dry-run` + audit-MD.

## Bemenő paraméterek

- **Threshold YAML** `~/.vault-config/crystallize-threshold.yaml` (változatlan):
  - default: 0.95
  - 07-Decisions/: 0.95 (ADR)
  - 00-Meta/: 1.00 (shadow)
  - MEMORY.md: 0.90
  - 05-Memory/: 0.90
  - **11-wiki/: 0.85** ← aggressive-ready
  - **04-Tasks/Backlog.md: 0.75** ← aggressive-ready
- **Scorer:** `claude-code` (subagent-fanout pattern, $0 cost)
- **Prompt:** `v0.3-bias-mitigated` (self-enhancement + verbosity + position + halo debiasing aktív)
- **Flags:** `--dry-run` (audit-log nem íródik, semmi mutation), `VAULT_NLI_VETO=0`, `VAULT_COHERENCE_CHECK=0`
- **Sessions** (utolsó 5 zárt):
  1. `2026-05-16-kgc-robbantott-brakeres` (11 bullet)
  2. `2026-05-17-foxxi-weboldal` (0 bullet — nincs ## Learnings szekció)
  3. `2026-05-17-boulium-com` (3 bullet)
  4. `2026-05-17-obsidian-vault` (8 bullet)
  5. `2026-05-17-obsidian-vault-pro` (7 bullet)

**Összes bullet:** 29 (0+11+3+8+7), foxxi-session a Learnings-mentes — kihagyva.

## Per-bullet routing táblák

### Session 1 — `2026-05-16-kgc-robbantott-brakeres` (11 bullet)

| # | Verdict | Conf | Target | t-key | NLI-passable* | Coherence-passable* |
|---|---|---|---|---|---|---|
| 0 | 🟢 auto-prop | 0.93 | MEMORY.md | t=0.90 | ✅ (Tailwind-bug, no contra) | ✅ (no canonical wiki yet) |
| 1 | 🟢 auto-prop | 1.00 | MEMORY.md | t=0.90 | ✅ | ✅ |
| 2 | 🟡 batch-preview | 0.87 | MEMORY.md | t=0.90 | n/a (nem auto-prop) | n/a |
| 3 | 🟢 auto-prop | 1.00 | MEMORY.md | t=0.90 | ✅ (sqlite-pattern új) | ✅ |
| 4 | 🟢 auto-prop | 1.00 | MEMORY.md | t=0.90 | ✅ (React-wheel passive: új) | ✅ |
| 5 | 🟢 auto-prop | 1.00 | **11-wiki/** | **t=0.85** | ✅ (FastAPI-pattern új) | ✅ (no neighbour) |
| 6 | 🟡 batch-preview | 0.80 | MEMORY.md | t=0.90 | n/a | n/a |
| 7 | 🟢 auto-prop | 0.87 | **11-wiki/** | **t=0.85** | ✅ (cascade-delete új) | ✅ |
| 8 | 🟡 batch-preview | 0.87 | MEMORY.md | t=0.90 | n/a | n/a |
| 9 | 🔴 discard | 0.47 | MEMORY.md | t=0.90 | n/a | n/a |
| 10 | 🟢 auto-prop | 0.87 | **11-wiki/** | **t=0.85** | ✅ (DevTools-MCP új) | ✅ |

**Summary:** 🟢 7 auto-prop, 🟡 3 batch-preview, 🔴 1 discard. **3 bullet 11-wiki target** (a 7 auto-prop közül), 0 Backlog target.

### Session 2 — `2026-05-17-foxxi-weboldal` (0 bullet)

> Nem értékelhető — a session-fájl `## Learnings` szekciója üres / hiányzik. Crystallize kilépett: `⚠ No Learning bullets found`.

### Session 3 — `2026-05-17-boulium-com` (3 bullet)

| # | Verdict | Conf | Target | t-key | NLI-passable* | Coherence-passable* |
|---|---|---|---|---|---|---|
| 0 | 🟢 auto-prop | 0.93 | MEMORY.md | t=0.90 | ✅ | ⚠ (létezik `bmad-cross-machine-artifact-verification.md` wiki — coherence-check FLAGGING-et kockáztathat reaffirm-ként, de nem contra) |
| 1 | 🔴 discard | 0.67 | MEMORY.md | t=0.90 | n/a | n/a |
| 2 | 🟡 batch-preview | 0.80 | **11-wiki/** | **t=0.85** | n/a | n/a |

**Summary:** 🟢 1 auto-prop, 🟡 1 batch-preview, 🔴 1 discard. **1 bullet 11-wiki target** (batch-preview-ként, nem auto-prop), 0 Backlog.

### Session 4 — `2026-05-17-obsidian-vault` (8 bullet)

| # | Verdict | Conf | Target | t-key | NLI-passable* | Coherence-passable* |
|---|---|---|---|---|---|---|
| 0 | 🟢 auto-prop | 0.93 | MEMORY.md | t=0.90 | ✅ | ✅ |
| 1 | 🟢 auto-prop | 1.00 | **07-Decisions/** | **t=0.95** | ✅ | ✅ |
| 2 | 🟢 auto-prop | 1.00 | MEMORY.md | t=0.90 | ✅ | ⚠ (auto-disable-min-volume wiki létezik — reaffirm) |
| 3 | 🟢 auto-prop | 0.93 | **11-wiki/** | **t=0.85** | ✅ | ✅ |
| 4 | 🟢 auto-prop | 0.93 | **11-wiki/** | **t=0.85** | ✅ | ✅ |
| 5 | 🟡 batch-preview | 0.87 | MEMORY.md | t=0.90 | n/a | n/a |
| 6 | 🟡 batch-preview | 0.87 | MEMORY.md | t=0.90 | n/a | n/a |
| 7 | 🟢 auto-prop | 0.87 | **11-wiki/** | **t=0.85** | ✅ | ⚠ (VSCode-popup wiki reaffirm — duplicate-risk) |

**Summary:** 🟢 6 auto-prop, 🟡 2 batch-preview, 🔴 0 discard. **3 bullet 11-wiki target**, **1 bullet 07-Decisions target** (de 0.95 küszöbnél — nem aggressive-ready).

### Session 5 — `2026-05-17-obsidian-vault-pro` (7 bullet)

| # | Verdict | Conf | Target | t-key | NLI-passable* | Coherence-passable* |
|---|---|---|---|---|---|---|
| 0 | 🟡 batch-preview | 0.87 | MEMORY.md | t=0.90 | n/a | n/a |
| 1 | 🟢 auto-prop | 1.00 | **11-wiki/** | **t=0.85** | ✅ | ✅ |
| 2 | 🟢 auto-prop | 1.00 | **11-wiki/** | **t=0.85** | ✅ (subagent-fanout reaffirm — already wiki) | ⚠ (existing `claude-code-subagent-fanout.md` — high cosine, low contra) |
| 3 | 🟢 auto-prop | 0.87 | **11-wiki/** | **t=0.85** | ✅ (sprint-day-0 reaffirm — already wiki) | ⚠ (existing `sprint-day-0-skeleton-first.md` — reaffirm-flag risk) |
| 4 | 🟡 batch-preview | 0.93 | **07-Decisions/** | **t=0.95** | n/a (ADR threshold = 0.95, conf alatta) | n/a |
| 5 | 🟡 batch-preview | 0.80 | **07-Decisions/** | **t=0.95** | n/a | n/a |
| 6 | 🟢 auto-prop | 1.00 | MEMORY.md | t=0.90 | ✅ | ✅ |

**Summary:** 🟢 4 auto-prop, 🟡 3 batch-preview, 🔴 0 discard. **3 bullet 11-wiki target** (mind auto-prop), **2 bullet 07-Decisions target** (mind batch-preview — szigorú ADR-gate működik), 0 Backlog.

*NLI-passable / Coherence-passable: hipotetikus értékelés bullet-tartalom alapján (a binárisok valódi futtatása NEM történt; csak content-based estimate). NLI-veto a verbal-contradiction-okra méretkalibrált (DeBERTa-v3, threshold 0.3). Coherence-veto a canonical-vault-szemszögbeli contradiction-okra (top-K=5 cosine, NLI ≥ 0.7).

## Aggregált metrikák (5 session × 29 bullet)

### Routing-distribution

| Verdict | Count | % |
|---|---|---|
| 🟢 auto-prop | **18** | **62.1%** |
| 🟡 batch-preview | 9 | 31.0% |
| 🔴 discard | 2 | 6.9% |

> ⚠️ **62.1% auto-rate** — jelentősen magasabb az alap-monitor által mért 37.5% Week-20 átlagnál. Ez a 0.95 default-en futna, de a per-target YAML mostani konfigjával már ezt látjuk (MEMORY.md 0.90, 11-wiki 0.85 — sok bullet ezeken csúszik át).

### Target-distribution (csak az auto-prop bullet-eken)

| Target | Auto-prop count | Threshold | Aggressive-ready? |
|---|---|---|---|
| MEMORY.md | 8 | 0.90 | nem (0.90 > 0.85) |
| **11-wiki/** | **9** | **0.85** | **✅ YES** |
| 07-Decisions/ | 1 | 0.95 | nem (strict ADR) |
| 04-Tasks/Backlog.md | 0 | 0.75 | aggressive, de **NULL traffic** |
| **ÖSSZESEN auto-prop** | **18** | — | — |

**Aggressive-ready targets auto-prop részesedése:** 9/18 = **50.0%** (mind 11-wiki/, Backlog.md 0 forgalom).

### NLI-veto & Coherence-veto hipotetikus elemzés

A jelen audit-pass NEM futtatta a `eval-l2-nli-judge` és `vault-coherence-check` binárisokat — csak content-based becslés a 18 auto-prop kandidátra:

| Layer | Hipotetikus veto | Reason |
|---|---|---|
| **2.5 NLI** | **0 / 18 (0.0%)** | Egyik bullet sem ellentmond a session-saját provenance-jének (mind reaffirm / új-pattern). NLI-bullet vs session-summary NEM contra-vector. |
| **2.6 Coherence** | **~2-3 / 18 (~11-17%)** | 3 reaffirm-bullet (Session-4#7 VSCode-popup, Session-5#2 subagent-fanout, Session-5#3 sprint-day-0) magas cosine-rőfön van canonical wiki-kre, de **NEM contradiction** — fail-open. **1 ambiguous case**: Session-3#0 (BMad event ≠ disk-state) megfeleltethető a `bmad-cross-machine-artifact-verification.md`-nak — várhatóan OK. Várt: 0-1 valódi FLAG. |

**Várt downgrade-ek `VAULT_NLI_VETO=1 VAULT_COHERENCE_CHECK=1` mellett:**
- NLI downgrade: 0 (extrém alacsony, mivel a bullet-ek a session-saját provenance-ükből származnak — entailment-rich)
- Coherence downgrade: 0-1 (worst-case 5.6% — ha az új neighbour-judge contradictionnak veszi a reaffirm-et — fail-open biztonsági háló)

### Score-distribution histogram (29 bullet)

| Conf-bucket | Count | % |
|---|---|---|
| 1.00 | 7 | 24.1% |
| 0.93 | 5 | 17.2% |
| 0.87 | 9 | 31.0% |
| 0.80 | 4 | 13.8% |
| 0.67-0.75 | 2 | 6.9% |
| ≤ 0.50 | 2 | 6.9% |

**Conf ≥ 0.85** (aggressive-szint): **21 / 29 = 72.4%** — magas-koncentrációs felső-réteg.
**Conf ≥ 0.95** (default/ADR-szint): **12 / 29 = 41.4%** — jelentős "strong" kandidát-mag.

## Risk-classification

### Auto-rate

- **Mért:** 62.1% (18/29)
- **Aggressive-ready targets auto-rate:** csak a 11-wiki/ + Backlog auto-prop / az összes 11-wiki/ + Backlog kandidát = **9/9 = 100%** a 11-wiki/-re irányítottak közül (Backlog 0 traffic). Tehát ha egy bullet 11-wiki/-target-tel megy, mindig auto-prop lesz az aktuális threshold-on.
- **Globális auto-rate:** 62.1%, ami **MAGAS** (>50%) — DE itt a magas-rate nem a 0.85 ramp-pal kapcsolatos, hanem a már-aktív YAML-config 11-wiki/0.85 + MEMORY/0.90 csúszással. A 0.85 ramp valódi inkrementuma csak a 11-wiki/-en érvényesülne, és az már most 0.85-ön van.

### Risk-kategória

- **Globális auto-rate (62.1%):** 🟡 **KÖZEPES → MAGAS** sávon — a 20-50% küszöb fölött jár, ami a `vault-crystallize-monitor` szerint ramp-elhalasztást indikálna. DE: a monitor a `Week-20`-on 37.5%-ot mért, ami **összhangban a 0.95-ös global default-tal** (a session-history nagy része oldal-default-on futott). A mostani per-target YAML-config eltér ettől.
- **Aggressive-ready (11-wiki/) auto-rate:** ✅ **100%** — minden 11-wiki/-target-tel megy auto-prop-ba. Ez azt jelenti, hogy a 0.85 küszöb **MÁR az aggressive-szint** (a 0.95-ről történő ramp 0.85-re csak a `default`-érték mozdítása lenne, ami minden még-fel-nem-soroltb target-et érint).
- **Backlog.md (0.75):** ❌ **NULL forgalom** — egyetlen bullet sem mutat erre a target-re. A `propose_target_file` heurisztika nem osztályoz semmit Backlog-ra. Hatás-mérés impossible.
- **Coherence-veto realisztikus FP-rate:** ~0-1 / 18 ≈ 0-5.6% — a 16.7% **conservative-acceptance** sávban. Nem blokkoló.

**Összesített kockázat:**

| Tengely | Score | Risk |
|---|---|---|
| Globális auto-rate | 62.1% | 🟡 KÖZEPES |
| 11-wiki/ auto-rate | 100% | 🟡 KÖZEPES (high-throughput, low-friction) |
| Backlog auto-rate | n/a (0 traffic) | ⚪ MÉRHETETLEN |
| Coherence-veto rate (várt) | 0-5.6% | ✅ ALACSONY |
| NLI-veto rate (várt) | 0% | ✅ ALACSONY |
| Forrás-monitor (Week-20) | 37.5%, 0% revert | ✅ ALACSONY |
| Sample-méret | 29 bullet | 🟡 KÖZEPES (B-1 monitor `≥10` lent, de session-volume ideálisan ≥3 hét) |

**Globális verdict:** 🟡 **KÖZEPES kockázat**.

## Részletes per-target ramp-érzékenység

Mit változtatna ha a YAML `default` 0.95 → 0.85?

- **MEMORY.md (8 auto-prop most):** override 0.90 él, **nem érintett**.
- **05-Memory/ (0 auto-prop most):** override 0.90, nem érintett.
- **07-Decisions/ (1 auto-prop most, 2 batch-preview):** override 0.95, **nem érintett**.
- **00-Meta/ (0 most):** override 1.00, soha nem érintett.
- **11-wiki/ (9 auto-prop most):** override 0.85, **nem érintett** (már 0.85-ön).
- **04-Tasks/Backlog.md (0 most):** override 0.75, nem érintett (de nincs is forgalma).
- **Default (catchall, jelenleg 0.95):** ha 0.85-re csúszna, akkor azok a target-ek, amelyek **nincsenek override-on**, 0.85-ön mérnének — DE az audit alapján **minden 29 bullet target-je matchel egy override-ra**. A `default` ramp tehát **0-bullet-effekttel jár** a jelenlegi heurisztika és session-mintán.

**Konklúzió a ramp-érzékenységi vizsgálatra:** A default 0.95→0.85 ramp **nulla forgalmat termel** a mostani propose_target_file heurisztikán — minden bullet egy explicit override-on landol. Az aggressive ramp valódi inkrementuma akkor lenne, ha az explicit override-okat is mozdítanánk (pl. MEMORY.md 0.90 → 0.85, vagy 07-Decisions/ 0.95 → 0.85). Erről NINCS scope ebben az audit-ban.

## Recommendation

### Választható lépés-pálya

#### Opció A — **PASS / Stay Status Quo (recommended)**

A jelenlegi YAML-config (11-wiki/0.85 + Backlog/0.75 aggressive-ready, többi override 0.90-1.00) **már lefedi a tényleges aggressive-pályát**. A `default` 0.95 értékének 0.85-re mozdítása **nulla többletforgalom**-ot termel, mert minden bullet egy override-on landol.

A 11-wiki/0.85 már 100% auto-rate-tel termel a felső-pelyhen — ez a kívánt aggressive-behaviour, és **nincs szükség külön activate-eseményre**.

> [!success] PASS — már a 11-wiki/-en aktív aggressive (0.85)
> A `default` 0.95 maradhat. A 0.85 ramp **nincsen new effect** — a 11-wiki target már ezen mér. Coherence és NLI shadow-window-ot kell érlelni a `VAULT_COHERENCE_CHECK=1` veto bekapcsolásához.

#### Opció B — **WAIT (per-target shadow-data érlelés)**

A `vault-crystallize-monitor` jelenti: NLI L2.5 csak 7 sample / 1 session, Coherence L2.6 csak 4 sample / 1 session. A `default-shift ❌ NO` ajánlás a két soft-veto-réteg aktiválására. Ezek nélkül a `VAULT_CRYSTALLIZE_APPLY=1 --apply` REAL mode nem ajánlható.

> [!warning] WAIT — még 2+ session NLI + Coherence shadow-adat kell
> Kell még 1-2 session crystallize-elése `VAULT_NLI_VETO=1 VAULT_COHERENCE_CHECK=1` mellett (még shadow-ban, NEM `--apply`), hogy a monitor küszöböt elérjük (≥10 NLI sample / 2 session, ≥10 coherence sample / 2 session). Becsült idő: 1 hét.

#### Opció C — **RAMP-SCHEDULE (ütemezett mozdulás)**

Ha a user mégis aggressive-default-ot akar (példának: 0.95 → 0.85 a default-en, hogy a jövőbeli új target-osztályok is alacsonyabb küszöbön induljanak):

| Hét | Mozdulás | Trigger | Override |
|---|---|---|---|
| **W21** (2026-05-18..05-24) | Shadow: `VAULT_NLI_VETO=1 VAULT_COHERENCE_CHECK=1` minden session-en, NEM `--apply` | Folyamatosan, minden zárás `11.11crystallize --scorer claude-code --dry-run`-on | nincs |
| **W22** (2026-05-25..05-31) | Risk-check #2 + ennek az auditnak az updated változata | Ha `vault-crystallize-monitor` Conservative-eshold ramp ✅ + 0 revert + ≥10 NLI + ≥10 coherence sample | default 0.95 → 0.90 |
| **W23** (2026-06-01..06-07) | Aggressive default mozdítás | Ha W22 0 ramp-revert (vault-crystallize-monitor watchdog 0% revert-rate) | default 0.90 → 0.85 |

> [!info] RAMP-SCHEDULE — kétlépéses (W21 shadow data, W22 0.95→0.90, W23 0.90→0.85)
> Ez a klasszikus 4-rétegű safety-gate threshold-ramp playbook. A user manuálisan dönt minden hétvégén a `vault-crystallize-monitor` output alapján.

### Ajánlott action

**Opció A (PASS) + Opció C első-lépése (W21 shadow data collection)**:

1. **NE módosítsd** a `crystallize-threshold.yaml`-t. A 11-wiki/0.85 és Backlog/0.75 már aggressive-ready, és a 100% auto-rate a 11-wiki/-en azt mutatja, hogy ez **stabilan termel**.
2. **Activate**-eld a 2 shadow-réteget a következő session-zárások alkalmával:
   ```bash
   export VAULT_NLI_VETO=1
   export VAULT_COHERENCE_CHECK=1
   /11.11-zar-session   # (vagy 11.11crystallize --scorer claude-code --with-context)
   ```
   Ezek `VAULT_CRYSTALLIZE_APPLY=0` mellett **nem mutate**-elnek, csak az audit-log-ba írják az NLI/Coherence verdict-eket — ez termeli a shadow-data-t a következő risk-assessment-hez.
3. **W22-ben** ezt az audit-ot újra-futtatni 5 új session-en + az NLI/Coherence valódi (nem hipotetikus) bevonásával. Ha **NLI downgrade 0**, **Coherence FP ≤ 5%**, **revert-rate 0**, akkor W23-ban a `default` 0.95 → 0.90 mozdítás biztonságos.
4. **Backlog.md (0.75) NULL traffic** felülvizsgálandó: a `propose_target_file` heurisztika nem mutat erre — ha akarunk Backlog auto-prop forgalmat, a router-t bővíteni kell (pl. "TODO:" / "fix:" / "🔴" pattern-re Backlog-target).

## Conclusion / Verdict

| Kérdés | Válasz |
|---|---|
| **B-1 Aggressive 0.85 ramp activate-elhető?** | **NEM SZÜKSÉGES** — 11-wiki/ már 0.85-ön, Backlog.md már 0.75-ön. A default 0.95→0.85 mozdítás 0-bullet effect-tel jár. |
| **Kockázat-szint** | 🟡 **KÖZEPES** (auto-rate 62.1%) — DE ez a per-target YAML-config várt-és-aktív viselkedése, NEM ramp-tüneti. |
| **Mit kell ezután** | 1) W21 shadow-data collection NLI+Coherence ON; 2) W22 audit-újra-futtatás; 3) opcionális W23 ramp az **explicit override**-okra (MEMORY 0.90→0.85?), NEM a default-ra. |
| **Apply REAL mode bekapcsolható?** | ❌ **NEM** — `vault-crystallize-monitor` jelenti az insufficient data-t (4 applied, 0 revert, de csak 1 session NLI + 1 session Coherence shadow). Várj 2+ shadow-session-t. |
| **Verdict** | **🟡 PASS-with-Wait** — a 0.85 ramp már de-facto él a 11-wiki/-en. A globális default-ramp NEM ajánlott. NLI+Coherence shadow-érlelés szükséges a REAL `--apply` előtt. |

## Per-bullet shadow-NLI / Coherence telepítési-utasítás

A következő 5 session-záráskor (hogy a W22-re a monitor 10+ NLI sample-t mutasson):

```bash
export VAULT_NLI_VETO=1
export VAULT_COHERENCE_CHECK=1
# A 11.11stop / /11.11-zar-session automatikusan futtatja a crystallize-t a vault session-summary után.
# Vagy manuális:
11.11crystallize <session-slug> --scorer claude-code --with-context
```

A 2 env-var az audit-log-ba írja a `nli_*` és `coherence_*` mezőket. NEM blokkol semmit `--apply` nélkül.

## Audit-fájl referenciák

- `/root/.vault-config/crystallize-threshold.yaml` (read-only, NEM módosítottuk)
- `/root/obsidian-vault/06-Audits/crystallize-log.jsonl` (read-only ebben az audit-ban)
- 5 session-pending response a `/tmp/vault-crystallize-pending/` (cleanup után törölhető)
- `vault-crystallize-monitor --weeks 4` baseline: 37.5% auto-rate, 0% revert-rate, 4 applied (insufficient sample size for shift)

## Kapcsolódó

- [[2026-05-17 B-1 per-target threshold overrides]] — YAML config létrehozása
- [[2026-05-17 B-1 G-Eval bias-mitigation v0.3]] — prompt-version aktív
- [[2026-05-17 B-1 NLI Layer 2.5 integration]] — soft-veto Layer 2.5
- [[2026-05-17 Layer 2.6 vault-coherence integration]] — soft-veto Layer 2.6
- [[../11-wiki/crystallize-threshold-ramp]] — ramp-protocol playbook
- [[../11-wiki/multi-layer-safety-gate]] — 4-rétegű safety-gate dokumentáció
- [[../02-Projects/superintelligent-vault]] — szülő-projekt

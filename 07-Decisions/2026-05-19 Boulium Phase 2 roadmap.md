---
name: ADR — Boulium Phase 2 roadmap
type: decision
created: 2026-05-19
updated: 2026-05-19
status: proposed
project: boulium
tags: ["#type/adr", "#project/boulium", "#roadmap"]
---

# ADR — Boulium Phase 2 roadmap (versenyform-bővítés + klub-mode + nemzetköziesítés)

## Status

**Proposed.** Phase 1 Friends-MVP éles `boulium.com`-on 2026-05-18 óta, 2 user + 3 meccs + 1 venue. Phase 1 post-MVP feature-batch (10 feature, 3 commit) deploy-olva 2026-05-19. Phase 2 körvonalazódik — pending NotebookLM deep research a régiós verseny-rendszerekről + user-feedback.

## Context

A Friends-MVP működik mint **5-15 fős haver-kör** platform. A következő bővítés-irány két dimenzió mentén megy:

1. **Versenyforma-bővítés** — most a `tournament` table-en `round_robin` / `swiss` / `single_elim` pairing-enum van, de a **Swiss + Single-elim még skeleton** (round-robin a tényleges path). FIPJP/FFPJP-szabványos verseny-formátumokat hozzá kell adni (Tir de précision, Mêlée/Brisure, Pool+Bracket, King-of-the-court).
2. **Klub-mode** — most a `player.club` egy szabad-szöveg-mező; nincs klub-entity, klub-tagság, klub-statisztika. A Phase 3 MAPESZ-szövetségi-integráció (47 klub) ezt feltételezi.

Plus a **nemzetközi expanzió** (HU/EN i18n) megnyitná a "találj-meccset" funkciót külföldi turisták számára (Buda + Pest pétanque-klubok).

## Decisions

### Phase 2 prioritás-sorrend (1-3 hónap)

#### 🥇 P1 — Tournament-élmény (~2 hét összesen)

1. **Multi-round tournament + live bracket UI**
   - Single-elimination bracket vizuálisan (a `tournamentPlayer` standings-en túl)
   - `/tournament/[id]/bracket` route — kivetítő-ready full-screen view
   - Round-advance gomb + auto-pair next round
   - Live-update polling (most 2-4s)

2. **Tir de précision match-type (FIPJP shooting)**
   - Új `match_type` enum-érték: `tir_precision` (a `match_format` mellett)
   - 5 állomás × 4 dobás = 20 lövés, állomásonként score (1/3/5 pont)
   - Külön ScoreUI (NEM 13-points stadium)
   - Külön rating-bucket (NE keveredjen Glicko-rating-tel a 13-points játékkal)

#### 🥈 P2 — Klub + extra match-mode (~2-3 hét)

3. **Klub-mode** (`club` entity, `clubMembership` join-tábla)
   - Klub-profil (név, város, alapítás-év, logo, leírás, weekly schedule)
   - Tagság (active / inactive / honorary)
   - Klub-statisztika (avg-rating, win-rate, podium-historia)
   - Klub-bajnokság (éves házibajnokság = recurring tournament)
   - Cross-klub challenge (most player-szintű, bővítjük klub-szintűre)

4. **Mêlée / Brisure** — sorsolt-partner triplette
   - "Klub-éjszakákra" — minden round-ban random új partner
   - Új `pairing_method` enum: `melee_rotation`
   - Round-advance: shuffle a maradék párokat

5. **King-of-the-court** — folyamatos challenge-mode
   - Új `match_type`: `king_of_court`
   - "Asztaltartó" megmarad, kihívók sorra-állnak
   - Streak-tracking: hányadik meccsét tartja
   - Külön achievement-csomag (`5_in_a_row_king`, `10_in_a_row_king` etc.)

#### 🥉 P3 — Stats + i18n + edzés (~2 hét)

6. **Position-stats / Surface-stats**
   - "Pointer-as 80% win-rate" / "Sand-on +5% jobb"
   - `match`-en már van `position` info per player (implicit a `player.position`-tól), surface a `venue.surface`-ből
   - Aggregate query a `/stats` page-re

7. **Multi-language (HU/EN)**
   - `next-intl` vagy `next-i18next` setup
   - Kezdetnek EN — angol turistáknak Buda/Pest klubok
   - String-extract a meglévő UI-ból ~150-200 kulcs
   - Locale-routing `/en/...`

8. **Edzés-naplók (non-ranked drills)**
   - Új `practice_session` table — non-ranked meccs/gyakorlat
   - Drill-típusok: tir, point-precision, distance-control
   - NEM számít Glicko-be, de XP-be igen

### Phase 3 (3-6 hónap) — körvonal

- **MAPESZ-sync** — live ha MAPESZ prod-éles (közös player-identity, license-import)
- **Live broadcasting kivetítőre** — cherry-pick a `kgc-kivetítők` stack-ből (HTML + WebSocket-poll)
- **Tournament officials + dispute escalation** — bíró-role, video-review-flow
- **WebSocket real-time** — 50+ user-nél a 2s polling helyett SSE/Socket.io
- **Apple Sign In** ($99/év Apple Dev)
- **Pool + Bracket large-tournament** (64+ player) — group-stage + knockout
- **Double elimination + Concours qualificatif** (BE/CH-mintára)
- **Liga-rendszer** (regular season + playoffs, BE/NL-mintára)

### Phase 4 (long-term, "if product takes off")

- **FIPJP world ranking import** — global player-database
- **Pálya-fotó AI score-detect** — boule-elhelyezkedés CNN
- **Boule-tracking** (Obut / Geo-Logic / La Boule Bleue gyártó + súly + edzettség)
- **Coaching feedback AI** — játékstílus-elemzés
- **Multi-region UI** (FR/DE/IT/EN) + multi-currency online nevezés (Stripe + SimplePay)
- **Apple Watch / Wear OS** quick-score
- **Voice-input** ("+1 első csapat")

## Régiós alkalmazhatóság

| Régió | Szövetség | Phase | Mit ad |
|---|---|---|---|
| 🇭🇺 Magyar | MAPESZ | Phase 3 sync | Hivatalos eredmény-import |
| 🇫🇷 Francia | FFPJP | Phase 2 — Geslico classification már megvan | Geslico-tier achievement-ek |
| 🇧🇪 🇳🇱 Benelux | FBJB/NJBB | Phase 3 — liga-rendszer | Regular season + playoffs |
| 🇨🇭 Svájc | Pétanque Suisse | Phase 3 — Concours qualificatif | Kvalifikációs pontok |
| 🇮🇹 Olasz | FIB | NEM most — Volo/Raffa különálló sport | Skip kivéve ha terjeszkedés |
| 🌏 Ázsia (TH, VN, MG) | APC | Phase 4 — own ranking | APC-ranking import |
| 🇺🇸 USA | FPUSA | Phase 4 — casual-mode toggle | Casual rules support |

## Consequences

✅ **Phase 2 = ~2-3 hónap fejlesztés**, dogfood-érték magas (haver-bajnokságok + klub-éjszakák)
✅ **Tournament-élmény** = legnagyobb értéksugarat sugall a 10-100 user-növekedéshez
⚠ **Klub-mode komplexitás** — schema-change (új `club` + `clubMembership` table), 5-7 új route, migration the meglévő `player.club` szövegmező → `club_id` foreign-key
⚠ **i18n** — string-extract minden meglévő UI-ban (~150-200 kulcs), de modular: route-onként haladhatunk

## Research-validation (2026-05-19 deep research)

NotebookLM deep research 2 témakörben + custom report-artifact (`2026-05-19-phase2-deep-dive.md`, 7 szekció). 5 új source importálva (FPUSA hivatalos szabálykönyv, FBJB belga 2025-2026 season rule-book, FIPJP rules, 2 YouTube gameplay-tutorial, i18n-stack-comparison).

### Schema-bővítések a research-findingek alapján

A FIPJP rule-szövegek (Article 1-41) alapján a következő adatmodell-finomításokat kell végrehajtani Phase 2-höz:

- **`match.boulesPerPlayer`** — integer, default 3 (single/double), triplette esetén 2 (FIPJP Article 1).
- **`venue.pitchSize`** — enum (`standard_15x4` / `minimum_12x3` / `custom`) — FIPJP Article 5.
- **`venue.circleType`** — enum (`drawn_35_50cm` / `prefab_50cm`) — FIPJP Article 7.
- **`match.cochonnetDistance`** — integer 6-10m range (most hardcoded), külön mezővel statisztikákhoz.
- **`tournament.targetScore`** — integer (11 liga / 13 standard / 15 long), most a `match.target` szinten van, érdemes tournament-szintre tolni hogy minden meccs konzisztens legyen.
- **`tournament.timePerThrow`** — seconds, default null (no limit), hivatalos versenyen 60s.
- Új tábla **`tournamentOfficial`** (Phase 3): `tournamentId`, `userId`, `role` (`umpire` / `jury_member`).

### Mit NEM veszünk át a research-ből

- **Yjs CRDT offline score-sync** — overkill 5-15 fős friend-MVP-nek; a meglévő `match_event` server-side log + 2s polling működik. Yjs visszahozható ha Phase 4-ben 50+ user offline-conflict gondot okoz.
- **Apple Private Relay + Verified Identifier strategy** — Apple Sign In Phase 3+, ekkor nyúlunk vissza.
- **Stream Chat (kommerciális SaaS, $499/mo entry)** — saját `chatMessage` table polling-on $0.
- **BoulOmeter AR-mérés** — Phase 4 long-term.
- **Clerk auth + serial-PK refaktor** — Better Auth + Drizzle pattern marad.

### Liga-mode (Phase 2 P3 új tétel)

Az FBJB belga + Pétanque Suisse liga-rendszerek alapján a Phase 2-be bekerül egy **liga-mode** toggle a `tournament` szintjén: `target=11`, fix résztvevő-szám, regular-season-szerű ütemezés. Phase 3-ban teljes "Liga (regular + playoffs)" formátum.

## References

- Research output (2026-05-18): `/root/projektjeim/boulium/docs/research/2026-05-18-deep-research-{friends-mvp,advanced-features}.md`
- Research output (2026-05-19): `/root/projektjeim/boulium/docs/research/2026-05-19-phase2-deep-dive.md` — FIPJP rule-szintézis + 7-szekciós briefing
- Phase 1 foundation ADR: [[2026-05-18 Boulium-foundation Friends-MVP stack]]
- Project state: [[../02-Projects/boulium]]
- Session ahol született: [[../08-Sessions/2026-05-18-boulium-petanque-app-2]]
- Cluster-context: [[../11-wiki/petanque-cluster-mapesz-cherry-pick]]
- NotebookLM source-ok (boulium notebook `d5b163f1`): FPUSA condensed rules · FBJB Reglement CHN 2025-2026 · FIPJP rule references · 2 YouTube tutorial · localisation-platform-comparison

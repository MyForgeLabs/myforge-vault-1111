---
name: Petanque-cluster MAPESZ cherry-pick stratégia
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/playbook", "#domain/petanque", "#project/mapesz", "#project/boulium"]
---

# Petanque-cluster — MAPESZ-örökség cherry-pick mátrix

> [!info] Cluster
> A MAPESZ az anya-projekt. Három leszármaztatott domain örökölhet belőle anyagot: [[../02-Projects/boulium]] (PWA-platform), [[../02-Projects/petanque-kisgeparuhaz]] (webshop), `foxxi` petanque-szakág. Minden új petanque-projekt **ezzel a 4-dimenziós cherry-pick mátrix-szal indul.**

## A mátrix 4 dimenziója

| Dimenzió | MAPESZ-örökség | Új projekt döntése |
|---|---|---|
| **PB (Project Brief) modulok** | 13 modul kész | Melyik 1–13 releváns? Új kell? |
| **PRD funkcionális + NFR** | 13 feature-blokk | Cherry-pick / discard / refactor |
| **UX persona + journey + wireframe** | 5 persona, 5 journey, 4 wireframe | Persona-overlap (klubtag/admin/szövetségi)? |
| **Architektúra szekciók** | 10 szekció (auth, DB, sync, offline, …) | Stack-megfelelés? |

Plusz két "összekötő" kategória:

- **Code cherry-pick (8 anyag)** — NSR-client, szamlazz-client, design-artifacts, KOC-PWA-shell, offline-sync, auth-magic-link, leaderboard-ranker, achievement-engine
- **Doc cherry-pick (5 anyag)** — strategiai-indito, design-system-doc, jogi/GDPR-pack, klub-szerepkörök, üzleti-modell

## Workflow (új petanque-projekt indul)

1. **`bmad-bmm-create-product-brief`** vagy `wds-1-project-brief` skill — input a MAPESZ kanonikus indító + új projekt vízió.
2. **`01-mapesz-cherry-pick-decision-matrix.md`** dokumentum a `docs/` alá — 4 dimenzió × MAPESZ-modulok táblázatként, minden cellához:
   - ✅ cherry-pick (idézd a forrást)
   - 🔁 refactor (mi módosul)
   - ❌ discard (miért nem illik)
   - ➕ új (mit nem örököl, de kell)
3. **10 "ÚJRA-DÖNTENI" tétel** — ezeket a MAPESZ-örökségből nyitott kérdésként át kell venni (pl. monorepo vs külön repo, közös DB vs dedikált).
4. **Feszültség-indoklás (~5 db)** — hol ütközik az új projekt víziója a MAPESZ-megoldással (pl. boulium identitás-építés ≠ MAPESZ admin-fókusz).
5. **`02-<projekt>-mire-kell-megfelelnie.md`** követelmény-katalógus — 11 kategória, ~200 sor, státusz-jelekkel (✅ / 💡 / ❓ / ➕).

## Anti-pattern

- **Vakon másolni** MAPESZ-modult kontextus-vizsgálat nélkül. Pl. a MAPESZ admin-jogosultság-mátrix nem alkalmazható a `boulium`-ra, mert ott a hobbisportoló a központi felhasználó, nem a klub-titkár.
- **MAPESZ-örökség == kötelező** félreértés. A 4-dimenziós mátrix célja, hogy a discard is explicit legyen, ne implicit.

## Kapcsolódó

- [[../02-Projects/mapesz]] — anya-projekt
- [[../02-Projects/boulium]] — első alkalmazás (2026-05-17)
- [[../02-Projects/petanque-kisgeparuhaz]] — webshop-leszármaztatott
- [[bmad-cross-machine-artifact-verification]] — cherry-pick docs lokalizálása

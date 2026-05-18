---
name: Git stratégia — standalone repo + tematikus commit-ok + GitHub Flow
type: decision
tags: [kgc-berles, git, decision, process]
created: 2026-04-24
updated: 2026-04-24
project: kgc-berles
---

# Git stratégia — standalone repo + 7 tematikus commit + GitHub Flow

> [!info] Döntés időpont: 2026-04-24
> 50+ uncommitted fájl + csak 1 baseline commit utáni rendrakás. Most van rendezett history és remote.

## Háttér

A KGC-Bérlés repo `/root/projektjeim/KGC-ALL/kgc-berles` 2026-04-24 reggelén:
- **2 commit** (b070c03 `feat: initial commit` + e49035d `Initial commit from Create Next App`)
- **55 változás:** 49 untracked mappa/fájl + 6 modified
- **Nincs remote** beállítva
- A KGC-ALL parent **nem** git repo

## A 4 döntés

### 1. Repo szervezés → standalone

| Opció | Választás |
|-------|-----------|
| **🟢 Standalone `kgc-berles` saját repo-ja** | ✅ Választva |
| Submodule a KGC-ALL alatt | Elvetve — KGC-ALL nem repo, nincs deploy-egysége; submodule overkill |
| Subdir egy nagy KGC-ALL repo-ban | Elvetve — bonyolítja a deploy-t (build-csak-egy-subdir-ből) |

**Indok:** kgc-berles önálló deploy-egység, KGC-ALL viszont lazán szervezett asset+doc gyűjtemény (43 skill, BMAD workflows, design-artifacts pipeline) — nincs közös build/deploy dependencia.

### 2. Remote → GitHub privát

- Repo: `PetykaMaki/kgc-berles` (GitHub privát)
- Indok: gh CLI már autentikálva (`PetykaMaki`), 1 paranccsal kész. **Privát**, mert üzleti app + admin auth.
- Push: 2026-04-24 (külön usernek futtatandó parancs — sandbox per-target permission)

### 3. Hogyan commitoljuk az 50+ fájlt → 7 tematikus commit

Nem 1 monolitikus, hogy `git blame` később is használható maradjon. Sorrend:

| # | Hash | Cím | Méret |
|---|------|-----|-------|
| 1 | `3b48eb4` | `chore(data): adopt seed pattern + ignore runtime data + .env.example` | 8 fájl, +5690 sor |
| 2 | `2d20989` | `feat(brand): warm editorial v5.0 + KGC BEST petrolkék hero system` | 8 fájl, +7495 / -186 (lock-fájllal) |
| 3 | `751b757` | `feat(public-pages): rental, machine detail, service, shop, marketing pages` | 17 fájl, +2365 sor |
| 4 | `a3c74c2` | `feat(components): home sections, shared widgets, layout, mobile, shop` | 63 fájl, +8710 sor |
| 5 | `c48b9ae` | `feat(admin): cookie auth + bookings/machines/shop/products/settings CRUD` | 23 fájl, +4827 sor |
| 6 | `d368ce0` | `feat(api+lib): pricing engine, notifications, data services, types, hooks` | 32 fájl, +2606 sor |
| 7 | `382e4aa` | `chore(assets): characters, machine images, hero, favicon, llms.txt` | 224 fájl, +1497 sor (~31MB bin) |

Mind:
- `--author="Vault User <user@example.com>"` (committer marad `root@srv...` mert nem írunk globális git config-ot, lásd alább)
- `Co-Authored-By: Claude Opus 4.7 (1M context)` footer

### 4. Branch stratégia → GitHub Flow light

| Opció | Választás |
|-------|-----------|
| **🟢 GitHub Flow light** (`main` + `feat/*` ágak, PR-ral merge) | ✅ Választva |
| Trunk-based csak main-re | Elvetve — review nehezül |
| Git-flow (main + develop + feat/*) | Elvetve — túl komplex egyfős dev-re |

**Indok:** egy fő dev (Peti + agent), de a PR-os merge később lehetőség szerint review-ra (akár AI-review-ra is `code-review` skill-en keresztül). A 7 commit közvetlen `main`-re ment most (rendrakás), utána új feature-ök `feat/<név>` ágon → merge PR-ral.

## Mellékhatás: biztonsági fix a folyamat közben

Az 5. commit (admin) staging-elése során sensitive scan-en kiakadt:

```diff
-export const ADMIN_PASSWORD = process.env.KGC_ADMIN_PASSWORD || "kgc-admin-2026"
```

**Hardcoded jelszó-fallback** a `lib/admin-auth.ts`-ben — a memória-szabály ([feedback_git_sensitive_data.md](../../.claude/projects/-root/memory/feedback_git_sensitive_data.md)) szerint sensitive credentials SOHA git-be. Refaktor:

- `lib/admin-auth.ts` → `ADMIN_PASSWORD: string | undefined`, csak ha env van **és ≥8 karakter**, különben `undefined` + warning log
- `app/api/admin/login/route.ts` → early return 503 ha `!ADMIN_PASSWORD`
- **Fail-secure:** ha env hiányzik → admin minden endpoint deny-all, nem default-jelszóval nyitva

**Mellékhatás:** a jelenlegi `setsid nohup pnpm dev` futás `KGC_ADMIN_PASSWORD` env nélkül indul — admin most blokkolt. Backlog "Env-vars beállítása" task megoldja, amint `.env.local`-ba kerül egy biztonságos jelszó (≥8 char).

## Git config döntés

A repo-ban **nincs** beállítva `git config user.name/email`, ezért a corábbi commit-ok `root <root@vps-dev-example.hstgr.cloud>` szignóval mentek. A memória-szabály szerint nem írunk globális git-config-ot az agentből.

**Megoldás:** commit-onként `--author="Vault User <user@example.com>"` flag — az **author** Peti, a **committer** marad rendszer-default. GitHub-on Peti email-ja látszik a history-ban, és a Co-Authored-By footer Claude.

Ha a user később globális git config-ot akar:
```bash
git config --global user.name "Vault User"
git config --global user.email "user@example.com"
```

## Ellenőrzés (commit-utáni állapot)

- `git status` → working tree clean ✓
- 8 commit `main`-en (1 baseline + 7 új)
- Dev server továbbra is HTTP 200 (Turbopack hot-reload átment)
- Sensitive scan minden commit előtt: `git diff --cached | grep -iE "password=|api_key|secret|@gmail|+36..."` — tiszta minden commit-ban
- `data/`, `public/uploads/*` (kivéve .gitkeep), `.env*` (kivéve .env.example) gitignore-d ✓

## Következmények

- **Új feature** → `feat/<név>` ág, PR-ral merge
- **Hot-fix prod-on** → `fix/<név>` ág, PR-ral merge
- **Nincs `develop` ág** — main = stable
- **Sensitive scan** kötelező commit előtt: `git diff --cached | grep -iE ...` (a [memory rule](../../.claude/projects/-root/memory/feedback_git_sensitive_data.md) szerint)
- **Új `.env*` változás** csak `.env.example` template — soha runtime értékek

## Pending

- [ ] **GitHub repo create + push** — usernek kell futtatnia (sandbox per-target engedély hiányzik agent-side):
  ```bash
  cd /root/projektjeim/KGC-ALL/kgc-berles
  gh repo create PetykaMaki/kgc-berles --private \
    --description "Kisgépcentrum (KGC) bérlés/szerviz/webshop frontend — Next.js 16 + Warm Editorial brand" \
    --source=. --remote=origin --push
  ```

## Kapcsolódó

- [[02-Projects/kgc-berles]]
- [[07-Decisions/2026-04-24 Brand kanonizálás — KGC BEST Warm Editorial]]
- [[07-Decisions/2026-04-24 KGC-Bérlés üzleti szabályok v1]]
- Memory: [feedback_git_sensitive_data.md](../../.claude/projects/-root/memory/feedback_git_sensitive_data.md) (érzékeny adat git-szabály)

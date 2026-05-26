---
name: 2026 parallel-dev state-of-the-art patterns
type: wiki
tags: [wiki, parallel-dev, git, workflow, 2026, research]
created: 2026-05-21
updated: 2026-05-21
---

# 2026 parallel-dev state-of-the-art patterns

## Mikor használd

Új projekt vagy meglévő projekt-process-refactor — 2-10 fős dev-csapatnál a 2026-os legjobb praktikák összesítve.

## Áttekintés — a 7 kulcs-pattern

```
┌──────────────────────────────────────────────────────┐
│  1. Trunk-Based Development                          │
│     + short-lived branches (<2 nap)                  │
│  2. Feature Flags (decouple deploy from release)     │
│  3. Stacked PRs (Graphite vagy GitHub Native)        │
│  4. Merge Queues (auto-rebase + test + merge order)  │
│  5. Contract-First Zod-schema (single source of truth)│
│  6. MSW dev-mock-server (frontend-független dev)     │
│  7. CODEOWNERS + per-PR preview deploy               │
└──────────────────────────────────────────────────────┘
```

## 1. Trunk-Based Development

**Google, Meta, Shopify standard.** Minden commit `main`-re napi gyakorisággal, feature-branchek max 1-2 nap (NEM hetes mega-feature).

**Eredmény (Asana stats 2026)**: 21% több kód shippelve, 11% kisebb PR-méret, 7h/hét megtakarítás (vs hetes feature-branchekkel).

**Kulcs-szabály**: ha PR > 3 nap nyitva van, **válts stratégiát** (feature-flag-mögé tedd, vagy stack-eld).

## 2. Feature Flags

```ts
// hooks/use-feature-flag.ts
export const useFeatureFlag = (flag: string) => {
  // 1. localStorage override (per-user opt-in/opt-out)
  const override = localStorage.getItem(`feature.${flag}`);
  if (override === 'true') return true;
  if (override === 'false') return false;

  // 2. env-default
  return DEFAULTS[flag] ?? false;
};
```

**Decouple deploy from release**: deploy bármikor mehet, release feature-flag-flip-pel kontrollált.

Client-A-system V2 wizard default-flip pattern: dev/demo hosts default ON, prod default OFF, localStorage per-user override.

## 3. Stacked PRs

**Shopify**: 33% több merged PR per dev. **Asana**: 21% több kód shippelt + 11% kisebb PR-méret.

```
feat/checkout-step-1   (PR #100)  ← reviewable solo
    │
    └─ feat/checkout-step-2   (PR #101) ← depends on #100
            │
            └─ feat/checkout-step-3   (PR #102) ← depends on #101
```

**Tool-stack**:
- **Graphite** (commercial, $20/dev/mo) — `gt create`, `gt submit`, automatic stack-rebase
- **GitHub Native Stacked PRs** (2024 H2-tól) — repo-szinten enable
- **`spr` / `stack-pr`** (open-source CLI) — kisebb csapatok

**Pre-condition**: trunk-based + short-lived branchek + reviewer-discipline (mindenki ratify gyorsan).

## 4. Merge Queue

**GitHub Native** (2024+). Automatikus rebase + test + merge order — eliminálja a "merge collision race condition"-t.

```
PR #1 approved → merge queue
PR #2 approved → merge queue
PR #3 approved → merge queue
   ↓
GitHub auto-rebases #2 on #1, runs CI, merges if green
GitHub auto-rebases #3 on (#1+#2), runs CI, merges if green
```

**Konfiguráció**: Settings → Branches → main → "Require merge queue" + "Maximum X PRs to merge concurrently"

## 5. Contract-First Zod-schema

**A kulcs pattern a frontend-backend parallel-dev-hez.** Zod-schema = single source of truth, generálódik OpenAPI + TS-types + MSW handlers.

```ts
// packages/shared/api-contract/src/portal/equipment.schema.ts
import { z } from 'zod';

export const PortalEquipmentSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  dailyRate: z.number().positive(),
  status: z.enum(['AVAILABLE', 'RENTED', 'RESERVED']),
});

export type PortalEquipment = z.infer<typeof PortalEquipmentSchema>;
```

**Backend** (NestJS): `PortalEquipmentSchema.parse(req.body)` validation.
**Frontend** (React + TanStack): `PortalEquipment` type-safe response.
**Mock-server** (MSW): auto-generated handlers `dist/msw-handlers.ts`.

**Pre-condition**: monorepo (pnpm workspace) vagy published npm package.

## 6. MSW dev-mock-server

**Frontend-független dev**: nem kell várni a backend-changes-re.

```ts
// next.config.ts
async rewrites() {
  if (process.env.NEXT_PUBLIC_USE_REAL_API !== 'true') {
    return [{ source: '/api/:path*', destination: '/api/_mock/:path*' }];
  }
  return [{ source: '/api/:path*', destination: 'https://dev-server.example.com/api/v1/:path*' }];
}
```

**Eredmény**: Frontend-dev tud kódolni mock-on, backend-dev tud kódolni without breaking frontend, mindkettő ugyanazt a Zod-schema-t hivatkozza.

## 7. CODEOWNERS + per-PR preview deploy

**`.github/CODEOWNERS`** — auto-review-assignment per-path:

```
apps/api/**            @backend-team
apps/web/src/pages/**  @frontend-team
packages/shared/**     @backend-team @frontend-team   # mutual approval
.github/**             @devops-team
```

**Per-PR preview deploy** (Vercel-stílus): minden PR-nek saját URL `branch-<slug>.dev.example.com`. Reviewer-ek látják a változást előtte.

Multi-branch nginx routing-pattern:

```nginx
server {
  server_name ~^branch-(?<branch>.+)\.dev\.example\.com$;
  location / {
    proxy_pass http://127.0.0.1:3030;
    proxy_set_header X-Preview-Branch $branch;
  }
}
```

## Mit válassz mikor

| Csapat-méret | Pattern-stack |
|---|---|
| **1-2 dev** | Trunk-based + feature flags + Triple-AI review |
| **2-5 dev** | + CODEOWNERS + merge queue + per-PR preview |
| **5-15 dev** | + Stacked PRs + Contract-first Zod + MSW dev-mock |
| **15+** | + dedicated DevOps + per-team monorepo subset (Nx affected, Turborepo) |

## Verifikált alkalmazás (Client-A-system 2026-05-21)

Client-A-system mit MÁR használ (jó):
- ✅ Feature flags (`use-feature-flag.ts`, V2 default-flip)
- ✅ Triple-AI review (`ai-review.yml`)
- ✅ Turborepo affected build
- ✅ ADR-131 polling-pull deploy

Client-A-system mit ADOPTÁL Sprint 27+ (új):
- ➕ Trunk-based (max 2-3 nap feature-branch)
- ➕ `@kgc/api-contract` Zod-csomag (PD.A.4 Sprint 27 W1, ~5 SP)
- ➕ MSW dev-mock-server kgc-berles-en (PD.A.8 Sprint 27 W2)
- ➕ CODEOWNERS (Phase C P0, Sprint 27 W0)
- ➕ Merge Queue (Phase C P0, Sprint 27 W0)
- 🔽 Per-PR preview deploy (defer Sprint 28+)
- 🔽 Stacked PRs (opcionális próba)

## Sources

- [Git Workflow Best Practices: The Developer's Guide for 2026 (DEV Community)](https://dev.to/_d7eb1c1703182e3ce1782/git-workflow-best-practices-the-developers-guide-for-2026-4gl0)
- [The Ultimate Git Flow: Trunk-Based Development and Stacked PRs](https://jukben.codes/the-ultimate-git-flow-trunk-based-development-and-stacked-prs-for-the-win)
- [How to use stacked PRs - Graphite](https://graphite.com/blog/stacked-prs) (Shopify 33% / Asana 21% stats)
- [The Microsoft Study That Exposed Why Your Large PRs Fail (2026 GitHub native stacked PRs)](https://www.mrlatte.net/en/stories/2026/04/14/github-stacked-prs/)
- [Branching strategies for monorepo development - Graphite](https://graphite.com/guides/branching-strategies-monorepo)
- [Type-Safe Frontend + Backend Contracts Using Shared Zod Schemas](https://www.ruthvikdev.com/blog/3-shared-zod-schemas)
- [Generating OpenAPI Contracts from Zod Schemas - Steve Kinney](https://stevekinney.com/courses/full-stack-typescript/zod-to-open-api)

## Kapcsolódó

- [[11-wiki/joint-integration-solo-split-takeover]] — takeover-context
- [[11-wiki/async-first-handover-pattern]] — handover-protocol
- [[11-wiki/polling-pull-deploy-pattern]] — deploy-stratégia
- [[06-Audits/2026-05-21 Client-A-system parallel-work setup plan]] — Client-A-system specifikus alkalmazás

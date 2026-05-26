---
name: Skill-canonicalize baseline audit (B-4 Week 1-α)
type: audit
sprint: B-4
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/audit", "#project/sv", "sv-4", "tool-composition", "skill-pool"]
project: [[../02-Projects/superintelligent-vault]]
adr: [[../07-Decisions/2026-05-12 sv-4 tool composition arch]]
tool: [[../.vault-tools/scripts/skill-canonicalize.py]]
---

# Skill-canonicalize baseline (2026-05-17)

> [!info] Sprint **SV B-4 — Tool composition**, Week 1-α (Anthropic Agent Skills Progressive Disclosure réteg).
> Day 0-skeleton-szám "534 SKILL.md / 0 compliant" **stale** volt — kettős számolás a
> `.claude/skills` → `.agents/skills` symlink miatt, és a script `tags`+`trigger_keywords`
> hiányára szigorúan compliant-ellentét adott. **Új audit:** realpath-dedup, kibővített root-lista
> (`.claude/plugins` is), és Anthropic-spec szerinti rétegezett compliance.

## TL;DR

| Metrika | Érték |
|---|---|
| **Total SKILL.md (realpath-deduped)** | **462** |
| Fully compliant (name+description+tags+trigger_keywords) | **258 (55.8%)** |
| Spec-compliant only (name+description, vault-extras hiányoznak) | 204 (44.2%) |
| Partial (REQUIRED hiányzik) | 0 |
| No frontmatter | 0 |
| **Trivially fixable (`tags: []` insert)** | **204** |
| Marad LLM-aided / human-review után (`trigger_keywords`) | 204 |

## Compliance-modell

A korábbi script `name+description+tags+trigger_keywords` négyest egyformán
required-nek vett. Helyesbítve:

| Mező | Réteg | Forrás |
|---|---|---|
| `name` | REQUIRED | Anthropic Agent Skills spec |
| `description` | REQUIRED | Anthropic Agent Skills spec |
| `tags` | RECOMMENDED | vault-konvenció (skill-pool search) |
| `trigger_keywords` | RECOMMENDED | vault-konvenció (B-4 Réteg 2 retriever) |
| `level` | OPTIONAL | Progressive Disclosure (1/2/3) |

**Compliance-státuszok:**
- `fully_compliant` — mind a 4 mező megvan
- `spec_compliant` — Anthropic-spec OK (`name`+`description`), vault-extras hiányoznak
- `partial` — REQUIRED mező hiányzik (kezelést igényel)
- `no_frontmatter` — nincs YAML-blokk
- `read_error` — IO/encoding hiba

## Per-root breakdown

| Skill-root | Total | Fully | Spec-only | Megjegyzés |
|---|---:|---:|---:|---|
| `/root/.agents/skills` | 268 | 258 | 10 | Vault-canonical pool (claude/codex/gemini symlink ide) |
| `/root/.claude/plugins` | 194 | 0 | 194 | MCP-installed plugin marketplaces — külső repók |

**Megfigyelés:** a vault-managed pool **96.3%** fully-compliant. A 44.2% globális
"hiány" lényegében a **plugin-cache** réteg, amit külső repók szállítanak Anthropic
2-mezős minimummal. Ezek "patch-elése" külön döntés (lásd alább).

## Non-compliant skills

### `.agents/skills` (10 skills) — minden esetben `tags`+`trigger_keywords` hiányzik

- `.system/imagegen/SKILL.md`
- `.system/openai-docs/SKILL.md`
- `.system/plugin-creator/SKILL.md`
- `.system/skill-creator/SKILL.md`
- `.system/skill-installer/SKILL.md`
- `microsoft-foundry/SKILL.md`
- `microsoft-foundry/models/deploy-model/SKILL.md`
- `microsoft-foundry/models/deploy-model/capacity/SKILL.md`
- `microsoft-foundry/models/deploy-model/customize/SKILL.md`
- `microsoft-foundry/models/deploy-model/preset/SKILL.md`

Ez 5 `.system/*` skill + 5 `microsoft-foundry/**` skill — mind külső / Anthropic-szállított,
ezért érthető hogy a vault-konvenciókat nem ismerik. **Akció:** `--fix-trivially` egy
üres `tags: []`-et beszúrhat, `trigger_keywords` LLM-aided generálást igényel
(Week 1 Day 3-4 munka).

### `.claude/plugins` (194 skills) — összes pluginban hiányzik mindkét vault-extras

Reprezentatív minta (teljes lista a JSON dump-ban; lásd `skill-canonicalize --audit --json`):

- `cache/claude-plugins-official/superpowers/5.0.7/skills/{brainstorming,executing-plans,subagent-driven-development,…}` (15 skill)
- `cache/claude-plugins-official/figma/2.0.7/skills/figma-{use,code-connect,generate-design,…}` (8 skill)
- `cache/claude-plugins-official/plugin-dev/unknown/skills/{agent,command,hook,mcp,plugin,skill}-{dev,integration}` (8 skill)
- `cache/openai-codex/codex/1.0.3/skills/{codex-cli-runtime,codex-result-handling,gpt-5-4-prompting}` (3 skill)
- `cache/ui-ux-pro-max-skill/ui-ux-pro-max/2.0.1/.claude/skills/{brand,design,design-system,slides,ui-styling,…}` (7 skill)
- `marketplaces/claude-plugins-official/external_plugins/{discord,imessage,telegram}/skills/{access,configure}` (6 skill)
- … +144 további plugin-skill (`marketplaces/cli-anything/**` jelentős hányad)

## Top-3 gap

1. **`tags`** — 204 skill (44.2%) — **trivially fixable** (`tags: []` beszúrás)
2. **`trigger_keywords`** — 204 skill (44.2%) — **LLM-aided** kell (Haiku ~$0.02/skill)
3. **(nincs harmadik)** — `name` és `description` 462/462-ben jelen van

## Trivially-fixable preview (dry-run)

`skill-canonicalize --fix-trivially --dry-run` futtatva:

```
[fix-trivially DRY-RUN]
  Trivially fixable (tags: []): 204
  Flagged for human review:     204
```

A `tags: []` üres-lista beszúrása nem tartalmi döntés — semantic-szegény ugyan,
de **nem rontja** semelyik downstream-konzument (Anthropic spec-compliant marad,
és a vault-skill-search ranking 0-súlyt rendel az üres tag-listához).

**NEM futtatva applied-módban** — Peti döntse el, mikor és mely root-ra (csak
`.agents/skills`-re? csak vault-managed? mind?). A plugin-cache `.bak`-ja
szennyezheti az `installed_plugins.json` integritást, és újra-install-kor
felülíródik — javasolt **kihagyni** a `--fix-trivially` futásból
(`--root` szűrő ezért később jöhet, Week 1 Day 3).

## Stratégiai döntés (Week 1 Day 2-3)

1. **Vault-managed (`.agents/skills`):** 10 hiányos skill — automatizálás vagy
   manuális frontmatter-bővítés (LLM-aided). $0.20 költség Haiku-val.
2. **Plugin-cache (`.claude/plugins`):** 194 skill — **NE módosítsuk in-place**
   (újra-install felülírja). Két alternatíva:
   - **A:** Side-car index — `~/.vault-tools/skill-pool/plugin-overlays.yml` ami
     plugin-skill-ekhez vault-managed `tags` + `trigger_keywords`-t rendel
     külön YAML-ben. Pro: nem szennyezzük a plugin-cache-t. Kontra: külön
     ranking-pipeline kell.
   - **B:** Hagyjuk spec-compliant állapotban — a bge-m3 embedding `description`
     mezőből úgyis kinyer minden szemantikát; a tag-réteg csak boost. Pro: 0 work.
     Kontra: ranking-tuning-ra később kell explicit-tags.
   - **Default ajánlás:** **B** Week 5-ig, **A** ha a Week 5 acceptance-gate
     (>0.85 precision Top-K) elbukik plugin-skill-ekre.
3. **Acceptance-gate frissítés:** ne az "összes 462 fully-compliant" legyen a cél,
   hanem **`.agents/skills` 100% fully + `.claude/plugins` 100% spec-compliant**.

## A tool maga

`/root/obsidian-vault/.vault-tools/scripts/skill-canonicalize.py` (frissítve 2026-05-17)

Új flag-ek és viselkedés:
- realpath-deduplikáció (symlink-kettősszámolás javítva)
- `.claude/plugins` root hozzáadva
- 4-szintű compliance-modell (`fully_compliant`/`spec_compliant`/`partial`/`no_frontmatter`)
- `--json` machine-readable kimenet (audit + fix-trivially mode-ban is)
- `--verbose` flag teljes non-compliant lista emberi reportban
- `--fix-trivially [--dry-run]` mechanikus-only fix (`tags: []` beszúrás, `.bak` backup)
- `--fix` továbbra is stub (Week 1 Day 3-4 LLM-aided)

## Kapcsolódó

- ADR: [[../07-Decisions/2026-05-12 sv-4 tool composition arch]]
- Projekt: [[../02-Projects/superintelligent-vault]]
- Tool: `[[../.vault-tools/README]]`
- Wiki: [[../11-wiki/sv-04-tool-composition]]
- Day 0 audit (stale): csak project-state-be írva, külön audit-fájl nem volt

---
name: skill-metadata-catalog-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/agent", "#topic/skill-management", "#topic/progressive-disclosure", "#topic/scaling"]
---

# Skill-metadata catalog — progressive-disclosure agent-skill-loader

## TL;DR

Az **Anthropic AgentSkills** specifikációja kulcs-pattern: minden skill rövid (~100 char) `name + description` metadata-blokkjával jelen van az agent fő-prompt-jában, **de a tényleges skill-tartalom (SKILL.md + példák + kód) csak akkor töltődik be**, ha az agent kiválasztja. Így 200-500 skill is befér 100K token-budget alatt (5-50K metadata-réteg), és a runtime token-cost csak a ténylegesen aktív skill-eké.

## Háttér (3+ source-evidence)

- [[sv-03-multi-agent-orchestration]] — "skill metadata catalog, has_count: ~100 chars per skill"
- [[sv-03-multi-agent-orchestration]] — "AgentSkills Standard" Anthropic-spec mint progressive-disclosure pattern
- [[superintelligent-vault-research]] — Skill library growth és filesystem-as-state komplementer pattern
- [[external-skill-cherry-pick]] — vault-on alkalmazott cherry-pick symlinkkel (305 skill / 100K-prompt-on belül)
- Cikk-evidence: `~/.claude/skills/` 305 skill mappa SKILL.md-vel, mindegyik description-mezővel a frontmatter-ben

## Mintázat

Há rom fő építőelem:

1. **Catalog-szintű metadata-blokk** a fő-prompt-ban. Minden skill 1 sor: `<name>: <100-char description, mi-mit-mikor-használj>`. 305 skill × ~150 char = ~45K token (még inneni cap).
2. **Skill-fájl-tartalom progressive load**-dal. Amikor az agent eldönti, hogy `<skill-X>`-et használja, **akkor** olvassa be a teljes `SKILL.md` tartalmát (+ esetleg sub-fájlok). Részletes szabályok ([[Karpathy-LLM-Wiki-pattern#Progressive disclosure Level 1-3]]) per-szint.
3. **Frontmatter-driven katalógus-generálás**: a metadata NEM kézzel írt index-fájl, hanem **SKILL.md frontmatter-ekből generált**. Így a katalógus automatikusan up-to-date.

Anthropic spec-konform szerkezet (mintával):

```
~/.claude/skills/<skill-name>/
├── SKILL.md          ← frontmatter (name, description, triggers) + body
├── examples/         ← few-shot példák (load-on-demand)
└── scripts/          ← kód-assistek (executable Level-2)
```

## Anti-pattern

- **Minden skill teljes-betöltés a fő-prompt-ba**: 305 skill × ~3000 token = 900K token, fő-prompt befulladás. NEM működik 1M-context-on sem (latency robbanás).
- **Skill-katalógus kézi karbantartása**: idő-rabló + drift. Generáld frontmatter-ből, single-source-of-truth.
- **Description "egy skill-en hosszan magyarázni"**: a 100-char limit erőlteti a precíz-választást — ha 500 char, az agent nem fogja megfelelően választani.
- **Nincs trigger-feltétel a description-ben**: "kódolj jól" leírású skill NEM hív-be — a description mondja meg **mikor használd**, NEM mit csinál. "Use when X" / "Trigger: Y" konvenció.
- **Skill-name-collision**: ugyanazon a katalógus-szinten 2 skill ugyanazzal a névvel — ambiguity, agent random választ. Namespace-prefix kötelező (`bmad-*`, `wds-*`, `gds-*` etc.).

## Reusable szabályok

1. **Frontmatter-driven**: minden skill `~/.claude/skills/<name>/SKILL.md` + frontmatter `name`, `description`, `triggers` (opt).
2. **Description ≤ 200 char**, kezdjen 1-2 mondatos „what + when"-nel. Pl. „Auditál Azure quota-t. Use when user mentions limits."
3. **Namespace-prefix**: csoportozott skill-csomagok (BMAD, WDS, GDS, etc.) közös prefixszel — anti-collision.
4. **Progressive disclosure 3 szint**: Level 1 (SKILL.md body), Level 2 (`examples/`, `scripts/` on-demand), Level 3 (`docs/` deep-dive on-demand).
5. **Katalógus build-step**: generáld `index.json`-t (vagy MEMORY/SKILLS.md-t) a frontmatter-ekből, hogy a fő-prompt-be `cat` paranccsal beemelhető.
6. **Trigger-explicitness**: minden skill description-ben legyen `WHEN: ...` vagy `Trigger:` — különben ambiguity → false-positive load.
7. **Plug-and-play symlink**: külső repóból cherry-pick symlinkkel ([[external-skill-cherry-pick]]) — NE másold, hogy upstream-update továbbjusson.

## Buktatók

- **Description drift**: idővel a SKILL.md body új feature-ekre nő, de a frontmatter description nem frissül → agent rossz skill-et választ. Heti audit (`vault-skill-distill`).
- **Token-budget overshoot**: 305 skill × 150 char = 45K, de ha valaki 300-char description-eket ír, gyorsan 90K — fő-prompt-ot tönkre teszi. Pre-commit-hook a 200-char-cap-en.
- **Skill-recursion**: ha skill-A description-je hivatkozik skill-B-re, és B hivatkozik A-ra, az agent loop. Skill-leírás NE legyen self-referential.
- **Trigger-collision**: 2 skill "Use when user mentions database" — ambiguity-tie-break-stratégia kell (recency, project-context, explicit user-pick).

## Kapcsolódó

- [[sv-03-multi-agent-orchestration]] — multi-agent context, ahol ez a pattern beágyazódik
- [[external-skill-cherry-pick]] — vault-on alkalmazott concrete-implementáció
- [[Karpathy-LLM-Wiki-pattern]] — progressive-disclosure háttér
- [[memory-md-overflow-management]] — kapcsolódó token-budget gondolkodás
- [[two-tier-graph-extraction]] — analóg „cheap-first, deep-on-demand" minta

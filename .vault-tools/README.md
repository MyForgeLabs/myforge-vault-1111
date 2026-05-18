# `.vault-tools/` — Tool composition + skill-pool semantic-search (B-4 sprint)

3-rétegű tool-réteg: Anthropic Agent Skills Progressive Disclosure (Réteg 1) + bge-m3 Top-K=3 retriever (Réteg 2) + custom MCP-server code-execution (Réteg 3).

**Parent ADR:** [[../07-Decisions/2026-05-12 sv-4 tool composition arch.md]]
**Research:** [[../11-wiki/sv-04-tool-composition.md]]
**Project:** [[../02-Projects/superintelligent-vault.md]]
**Depends:** B-2 (bge-m3 + Memgraph), opcionálisan B-1 G-Eval (skill-suggest auto-flow)

## Tartalom

```
.vault-tools/
├── README.md                       ez a fájl
├── config/
│   └── skill-search.yml            Progressive Disclosure + MCP server config v0.1
├── mcp-server/
│   └── README.md                   MCP-server placeholder (telepítés /opt/vault-mcp/-ba)
└── scripts/
    ├── skill-canonicalize.py       SKILL.md frontmatter normalizer (280 skill audit)
    └── vault-skill-search.py       Top-K skill semantic-search (bge-m3 + Memgraph)
```

## Status — 2026-05-17 (Phase B-4 Week 1-α, audit baseline ÉLES)

- [x] config + 2 script-skeleton + MCP-placeholder (Day 0, 2026-05-13)
- [x] **Week 1 Day 1-2:** `skill-canonicalize --audit` ÉLES baseline ✓ 2026-05-17 — **462 SKILL.md** realpath-deduped (NEM 534 — symlink-double-count javítva), **258/462 (55.8%) fully compliant**, **204/462 (44.2%) spec-compliant only**. Top-3 gap: `tags` (204), `trigger_keywords` (204), nincs harmadik (`name`/`description` 462/462). Per-root: `.agents/skills` 258/268 (96.3%) fully, `.claude/plugins` 0/194 spec-only. **Trivially-fixable: 204** (`--fix-trivially --dry-run` validálva, NEM applied). Részletes audit: [[../06-Audits/skill-canonicalize-baseline-2026-05-17]]
- [ ] **Week 1 Day 3-4:** Skill-frontmatter LLM-aided normalize (Haiku, ~$0.02/skill × 10 vault-managed + 194 plugin-cache decision → ~$4 once)
- [ ] **Week 2 Day 1:** B-2 dependency check — Memgraph + bge-m3 működik?
- [ ] **Week 2 Day 2-3:** Skill-embedding batch (280 SKILL.md → Memgraph `skills` namespace)
- [ ] **Week 2 Day 4-5:** `vault-skill-search` real impl + agreement-test 30 user-query-n
- [ ] **Week 3 Day 1-3:** MCP-server build (`/opt/vault-mcp/`) — 8 tool exposed
- [ ] **Week 3 Day 4:** Claude Code integration (`.claude/mcp.json` update)
- [ ] **Week 3 Day 5:** Acceptance gate — token-overhead -90%+ measured

## Várt impact (Phase A+ Q3)

| Metrika | Most | B-4 után |
|---|---|---|
| Skill-list token-overhead | ~5K token / agent-hívás | <100 token (MCP lazy-load) |
| Skill-discovery | regex-keyword match | semantic top-K (>0.85 precision) |
| New skill onboarding | manuális frontmatter | LLM-aided + Critic-review |

## Backout

```bash
export MCP_VAULT_DISABLED=1            # MCP-server bypass
# Claude Code visszaesik klasszikus prompt-tool-listre
```

## Kapcsolódó

- B-2 (bge-m3 + Memgraph): [[../.vault-memory/README.md]]
- B-1 (G-Eval, skill-routing): [[../.vault-ko/README.md]]
- B-6 (Critic agent, MCP-write-review): jövőbeli
- B-8 (RSI, Voyager ReCreate skill-evolution): jövőbeli safety-gated

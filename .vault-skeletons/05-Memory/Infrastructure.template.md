---
name: Infrastructure (template)
type: memory
created: 2026-01-01
updated: 2026-01-01
tags: ["#type/memory", "infrastructure"]
---

# Infrastructure

> **Template.** Másold `~/obsidian-vault/05-Memory/Infrastructure.md`-ként és írd át a saját környezetedre.
> **NE COMMIT-OLD a tényleges IP-ket / jelszavakat a public-repo-ba!** Lásd [SCRUB-rules](../../scripts/scrub-rules.yaml) forbidden_strings.

## Hosting

- **VPS prod:** `{{ vps-prod-hostname }}` ({{ region }})
- **VPS dev:** `{{ vps-dev-hostname }}` ({{ region }})
- **Shared hosting:** {{ pl. Hostinger / SiteGround / cPanel-host }}

## Memgraph (B-2)

- Container: `vault-memgraph`
- Port: `7687`
- Indexes: `:Chunk(embedding)`, `:SkillChunk(embedding)`, `:Entity(name)` — lásd [[../../11-wiki/memgraph-ce-feature-limits]]

## Services

- `vault-search.service` (systemd) — warm bge-m3 + Memgraph chunks RAM
- `vault-nli.service` (systemd skeleton, manual-enable) — warm DeBERTa NLI

## Cron-jobs

- `*/10 * * * * vault-autosave` — commit+push GitHub 10-percenként
- `0 4 * * 0 vault-cleanup --write` — heti vault-health
- `0 6 * * 0 vault-github-trending-recurrence --days 30` — heti GitHub-trending aggregálás
- `0 8 * * * github-trending-report --since daily` — napi trending raw
- `30 4 * * 0 vault-ko-conflicts-audit` — heti contradiction-audit
- `35 4 * * 0 vault-crystallize-monitor` — heti shadow-monitoring

## Backup

- 10-perces `vault-autosave` → GitHub (mirror)
- Weekly snapshot → {{ object-storage / B2 / S3 / Backblaze }}

## Hozzáférések (NE COMMIT!)

- {{ Lokál `.env`-ben tárolva: GH_TOKEN, ANTHROPIC_API_KEY (ha kell), NOTEBOOKLM auth-state }}
- {{ SSH-key-only access prod-on }}
- {{ Tailscale tailnet a belső admin-felületekhez }}

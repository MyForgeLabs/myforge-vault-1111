---
name: User Profile (template)
type: memory
created: 2026-01-01
updated: 2026-01-01
tags: ["#type/memory", "user-profile"]
---

# User Profile

> **Template.** Másold `~/obsidian-vault/05-Memory/User.md`-ként és írd át a saját profilodra.

## Ki vagyok

- **Név:** {{ teljes neved }}
- **Email:** {{ kapcsolat-email }}
- **Szerep:** {{ pl. Senior Full-Stack Developer / Solo Founder / Research Engineer }}
- **Nyelv:** {{ magyar / english / etc. }}

## Hogyan dolgozz velem

- **Stílus:** {{ tömör / részletes }}
- **Default-mód:** {{ ask-clarifying-questions / autonomous-execute }}
- **Cost-érzékenység:** {{ low-cost-prefer / quality-over-cost }}

## Mit NE csinálj

- {{ NE érintsd a `prod/` mappát explicit user-confirm nélkül }}
- {{ NE használj destruktív git-műveletet (`git reset --hard`, `--force-push`) }}
- {{ ... }}

## Skill-preferenciák

- Tudni szeretem ha új skill-t használnál (top-3 cosine-cosin az lehetőségből)
- TS > JS, Bricks > Elementor, Caddy > Traefik (lásd ADR `2026-XX-XX tech-stack defaults`)

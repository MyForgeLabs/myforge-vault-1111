---
name: Johnny-Decimal mappa-prefix
type: wiki
tags: ["#type/reference", "vault-design", "naming-convention"]
created: 2026-04-30
updated: 2026-04-30
---

# Johnny-Decimal mappa-prefix

Számozott prefix mappákon (`00-Meta/`, `01-Daily/`, `02-Projects/`, …, `11-wiki/`). **Nem teljes Johnny-Decimal** (az 10-99 / 100-999 szintű hierarchiát ír elő), csak a **fix sorrend** elvét vesszük át: a fájlrendszer alphabetikus rendezése egybeesik a fogalmi sorrenddel.

## Miért

- **Vizuális rendezés:** Obsidian + Finder + bash `ls` ugyanazt a sorrendet látja
- **AI-agent-friendly:** ha az agent "vault root"-ot listáz, a kontextus első ránézésre rendezett lesz
- **Új mappa jól illeszthető:** `09-archive/` egyértelműen a Sessions után jön, `12-templates/` a wiki után, stb.

## A nálunk használt séma (2026-04-30 óta)

| Prefix | Mappa | Szerep |
|--------|-------|--------|
| `00-Meta/` | Tag-taxonomy, Frontmatter-schema | Vault-szabályok ("hogyan írjunk") |
| `01-Daily/` | YYYY-MM-DD.md | Napi naplók |
| `02-Projects/` | Projects/Index.md + per-projekt | Aktív munka |
| `03-Hosts/` | VPS-ek, shared hosting | Infra |
| `04-Tasks/` | Backlog + Dashboard | Teendők |
| `05-Memory/` | User, Infrastructure, Skill-map, Agents-skill-suite, Dashboard-access | Persistent memory |
| `06-Audits/` | Pillanatkép-jelentések | Audit-log |
| `07-Decisions/` | ADR-szerű döntési napló | Decision history |
| `08-Sessions/` | /11.11 session-logok | Operatív log |
| `10-raw/` | Nyers input (Karpathy) | Immutable források |
| `11-wiki/` | Desztillált tudás (Karpathy) | Evergreen koncepciók |

## Mit NEM költöztetünk

- **Gyökér:** `AGENTS.md`, `README.md`, `.gitignore`, `.obsidian/` — ezek vault-system szintű fájlok, symlinkek + Obsidian conventions miatt maradnak
- **Verzióban:** ha 09 hézagot szeretnénk (pl. egy jövőbeli `09-archive`), most üresen hagyjuk

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]]
- [[11-wiki/Kepano-File-over-App-filozofia]]
- [[AGENTS]]
- [[00-Meta/Tag-taxonomy]]

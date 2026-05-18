---
name: Glossary — slugok és rövidítések
type: reference
tags: ["#type/reference", "meta", "glossary"]
created: 2026-04-30
updated: 2026-04-30
---

# Glossary

**AI-agent disambiguation.** A vault-ban gyakran használt rövidítések, slugok, kódnevek feloldása. Új agentnek ezt érdemes scaneli a session elején, ha valami ismeretlen kifejezésbe ütközik.

## Cégek / üzleti entitások

| Slug / Rövidítés | Mit jelent | Vault-link |
|------------------|------------|------------|
| **KGC** | **Kisgépcentrum** — kerti és épület-építő gépek bérlése + bolt | [[02-Projects/Index#🏗️ KGC ökoszisztéma]] |
| **MFL** | **MyForge Labs** — Peti saját labs/agent-platform vállalkozása | [[02-Projects/myforge-dashboard]] |
| **MAPESZ** | **Magyar Petanque Szövetség** | [[02-Projects/mapesz]] |
| **Foxxi** | **Budai Fogszabályozás** (Dr. Domi rendelő) | [[02-Projects/foxxi]] |
| **Bluebird** | KG-SHOP webshop kódneve (`bluebird-shop` repo) | [[02-Projects/kgshop-bluebird]] |
| **Kokó** | Chatwoot tenant kódneve (MFL ügyfélkommunikáció) | [[02-Projects/koko]] |
| **kisgepáruház.hu** | A KGC ügyfél-frontend petanque-fókusszal | [[02-Projects/petanque-kisgeparuhaz]] |
| **Rojt és Bojt** | **Rojt és Bojt Coffee** — Várnegyedi kávézó (Tábor u. 5.), Peti bátyja Gyuszi tulajdona | [[02-Projects/rojtesbojt]] |
| **example-balance.local** | Kutatási platform (PhD pszichológia/wellbeing) — kódnév: Kinda | [[02-Projects/teszt-eu]] |

## Hostok / infra

| Slug | Mit jelent |
|------|------------|
| **vps-prod-example** | prod VPS (Hostinger KVM 8) — `72.62.92.98` |
| **vps-dev-example** | dev VPS / agent-hub (Hostinger KVM 8) — `187.77.70.36` |
| **Cloud Professional** | Hostinger shared hosting — `82.29.176.126:65002` (14 weboldal) |
| **myforge-dev** | Tailscale device név a dev VPS-re |

## BMAD / agent-keretrendszerek

A [[02-Projects/KGC-ALL Architektura|KGC-ALL canvas]]-ben részletesen, itt csak a rövidítések:

| Slug | Mit jelent |
|------|------------|
| **BMAD** | Business Method-Architecture-Development — multi-agent fejlesztési keret (v6.2.1) |
| **BMM** | Business Method Module — Analysis → Implementation pipeline |
| **CIS** | Creative Intelligence Suite — innovation, storytelling, design thinking |
| **GDS** | Game Dev Studio — game design + development modul |
| **TEA** | Test Architecture Enterprise — testing & QA framework |
| **WDS** | Workflow Design System |
| **PRD** | Product Requirements Document (BMAD artifact) |
| **PRFAQ** | Press-Release-FAQ (Amazon-style PRD) |

### BMAD agentek (BMM)

| Név | Szerep |
|-----|--------|
| Mary / Saga | Business Analyst |
| John | Product Manager |
| Sally / Freya | UX Designer |
| Winston | Architect |
| Amelia | Developer |
| Quinn | QA Engineer |
| Barry | Quick Flow Solo Dev |
| Bob | Scrum Master |

## Vault-konvenciók

| Rövidítés | Mit jelent |
|-----------|------------|
| **ADR** | Architecture Decision Record — `07-Decisions/` |
| **NFR** | Non-Functional Requirement |
| **MOC** | Map of Content (Obsidian terminus) — index.md-jellegű csomópont |
| **PARA** | Projects / Areas / Resources / Archive (Tiago Forte mappa-rendszer) |
| **RAG** | Retrieval-Augmented Generation (LLM tudás-kiegészítés) |
| **Karpathy LLM Wiki** | A `raw/` + `wiki/` minta — [[11-wiki/Karpathy-LLM-Wiki-pattern]] |
| **Johnny-Decimal** | Számozott mappa-prefix konvenció — [[11-wiki/Johnny-Decimal-prefix]] |

## Tech-stack rövidítések

| Slug | Mit jelent |
|------|------------|
| **PWA** | Progressive Web App |
| **NSR** | (MAPESZ kontextus) Nemzeti Sport Regiszter API |
| **PM2** | Node.js process manager — prod-on több projekt fut |
| **kgc-postgres** | KGC közös Docker Postgres container — `kgc_erp` + `kgc_berles` DB-k, port 5433 |
| **Tailscale** | Overlay-network (zero-config VPN) — Mac ↔ dev VPS — `tail3b4d31.ts.net` |

## Hostinger-specifikus

| Slug | Mit jelent |
|------|------------|
| **KVM 8** | Hostinger VPS terv — 8 vCPU, 32 GB RAM, 400 GB disk |
| **CageFS** | CloudLinux-alapú user-sandbox (shared hosting) |
| **violet-okapi** | A Foxxi shared-hosting domain prefix-e: `violet-okapi-488175.hostingersite.com` |
| **lightsalmon-dugong** | Rojt és Bojt staging Hostinger-prefix: `lightsalmon-dugong-347768.hostingersite.com` |
| **HelloPack / HelloWP.io** | WP prémium-plugin-suite license-szolgáltatás (492 plugin Pro-tier + 395 plugin × 23 nyelv translations). Peti aktív license-zsel, userId 420042, supported_until 2027-05-07. Részletes: [[11-wiki/hellopack-wordpress-plugin-suite]] |

## 11.11 parancs-család

Részletes leírás: [[11-wiki/11.11-session-protokoll]]

| Parancs | Funkció |
|---------|---------|
| `/11.11` | Health check |
| `/11.11start "név"` | Új session + focus |
| `/11.11ls` | Session-listázás |
| `/11.11focus <slug>` | Focus váltás |
| `/11.11note "..."` | Jegyzet a focused-be |
| `/11.11stop` | Session zárás (Summary + Learnings + Next) |

## Hogyan bővítsd

Új rövidítés? → írd be ide. Új projekt? → új sor a "Cégek / üzleti entitások" táblába + linkeld. Tartsd a táblákat ABC-rendben az olvashatóság kedvéért.

## Kapcsolódó

- [[00-Meta/Tag-taxonomy]]
- [[00-Meta/Frontmatter-schema]]
- [[AGENTS]]
- [[02-Projects/Index]]

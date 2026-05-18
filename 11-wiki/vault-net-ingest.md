---
name: vault-net-ingest — external knowledge intake
type: wiki
tags: ["#type/wiki", "vault-ko", "external-knowledge", "github-repo", "url-ingest"]
created: 2026-05-17
updated: 2026-05-17
status: SKELETON
---

# vault-net-ingest — external knowledge intake

A vault tudásbázisának **kibővítése** internetes forrásokból. Két módot támogat: URL-scrape (`firecrawl`) és GitHub repo (`gh repo clone` + key-files). Mindkettő `10-raw/external/`-ba ír (immutable raw layer) **és** KO-DB extractor request-et generál (subagent 2-phase pattern).

## Filozófia

Karpathy LLM-Wiki mintában a **`10-raw/`** az immutable input, a **`11-wiki/`** a desztillátum. A `vault-net-ingest` az ETL-lépés a 0-ról a `10-raw/`-ra, onnan a meglévő pipeline veszi át: subagent-fanout extrakció → KO-DB → `--semantic` lookup → distill wiki-be (manuálisan vagy auto-prop-pal).

## Usage

```bash
# URL scrape (firecrawl-on át)
vault-net-ingest --url https://example.com/blog-post
vault-net-ingest --url https://docs.langchain.com/integrations --dry-run

# GitHub repo (clone + README + *.md + docs/**)
vault-net-ingest --repo anthropics/anthropic-cookbook
vault-net-ingest --repo langchain-ai/langchain --paths "README.md,docs/**/*.md"
vault-net-ingest --repo openai/openai-cookbook --dry-run
```

## Mit ír a vault-ba

### URL mód

- `10-raw/external/YYYY-MM-DD — <slug>.md` egy fájl, full markdown, frontmatterben `source_url`
- `/tmp/vault-ko-pending/10-raw_external_...request.json` KO extraction request

### Repo mód

- `10-raw/external/<owner>_<repo>/` mappa, fájlonként `<original_path__with__double_underscore>.md`
- `10-raw/external/<owner>_<repo>/_manifest.json` listázza melyik repo-path → vault-path
- KO-DB request fájlonként (ugyanaz a 2-phase pattern)

## Kulcs-konvenciók

- **MAX_CHARS_PER_FILE = 200K** — egy fájlnál hosszabb dokumentumokat csonk. (Cookbook README-k tipikusan 5-50K.)
- **DEFAULT_REPO_GLOBS** = `README.md`, `README*`, `*.md`, `docs/**/*.md`, `doc/**/*.md`. Kódfájlok NEM (a vault tudásbázis, NEM source-mirror).
- **Skip patterns:** `node_modules/`, `dist/`, `.git/`, `vendor/`, `target/`.
- **source_type:** `external` a KO-DB-ben (NEM `wiki`/`adr`/`session`) — így nem szennyezi a vault-coverage statisztikákat.

## Mit NEM csinál (a `10-raw/`-ban marad)

- **NEM olvas autómatikusan** a `11-wiki/`-be — manual distill kell. Ez szándékos: emberi curate / G-Eval critic-review szűr.
- **NEM ír MEMORY.md-be** — a memory user-curated marad.
- **NEM tölt skill-eket** vagy ADR-eket — azok lokális vault-történet.

## Tervezett iterációk

### 2026-05-17 v0.1 (most) — Skeleton

- [x] URL mode end-to-end (firecrawl → 10-raw → KO request)
- [x] Repo mode end-to-end (gh clone → key files → 10-raw → KO request per file)
- [x] Manifest, frontmatter, source-tagging
- [x] Dry-run

### Következő iteráció (még nem most)

- [ ] **Watch-mode** — egy `vault-net-watch.yml` listából (RSS-feed-ek, repo-k) heti cron-on update
- [ ] **Diff-aware** — repo újra-clone-nál csak a megváltozott fájlokat re-ingestálni (commit-hash összevetés)
- [ ] **Wiki-distill subagent** — `vault-net-distill <raw-file>` ami egy general-purpose Agent-tel kivonja a kulcs-pattern-eket egy 11-wiki/ kandidátba (user-review után megy be)
- [ ] **NotebookLM hook** — auto-source-add a `vault-nb-sync` listához (B-5 sprint integration)
- [ ] **Selective-glob per-repo** — `vault-net-ingest --repo X --preset cookbook` ami betölt egy preset-glob-listát

## Kapcsolódó

- [[10-raw/Index]] — raw layer szabályai
- [[Karpathy-LLM-Wiki-pattern]] — minta-háttér
- [[claude-code-subagent-fanout]] — a KO-extraction subagent-pattern
- `firecrawl` — local self-hosted scraper
- `gh` — GitHub CLI

## Példák — mit ingestálna a user

```bash
# Anthropic cookbook (claude API patterns)
vault-net-ingest --repo anthropics/anthropic-cookbook

# LangChain docs (vector DB + RAG)
vault-net-ingest --repo langchain-ai/langchain --paths "docs/**/*.md"

# Awesome-list pattern (heti scan, manual triage)
vault-net-ingest --repo browser-use/awesome-prompts

# Hostinger blog egy témára
vault-net-ingest --url https://www.shared-hosting-example.com/tutorials/litespeed-cache-wordpress
```

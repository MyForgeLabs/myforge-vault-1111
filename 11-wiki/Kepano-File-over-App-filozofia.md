---
name: Kepano "File over App" filozófia
type: wiki
tags: ["#type/reference", "vault-design", "philosophy"]
created: 2026-04-30
updated: 2026-04-30
source:
  - "https://stephango.com/file-over-app"
  - "https://stephango.com/vault"
---

# Kepano "File over App" filozófia

Steph Ango (Obsidian CEO, "kepano") elve: az **adat fontosabb mint az alkalmazás**. A jegyzetek olyan fájlformátumban legyenek, amit bármelyik másik program is megnyit — Obsidian, VS Code, Vim, böngésző, AI-agent.

## A fő tételek

1. **Markdown a tárolási réteg.** Nem Obsidian-spec adatszerkezet, hanem a markdown szabvány. Bármilyen szövegszerkesztő tudja olvasni-írni.
2. **Plain text mindenhol.** Frontmatter is YAML — szabványos. Nincs proprietary export.
3. **Folder structure = adatmodell.** A mappák, fájlnevek hordozzák az infót — nem egy app DB-je.
4. **A vault túléli az appot.** Ha az Obsidian holnap eltűnne, a vault még mindig kibontható, kereshető, AI-val olvasható.

## Miért fontos AI-agentnek

A Karpathy LLM-Wiki minta **közvetlen következménye** a File over App elvnek: ha a tudás `ripgrep`-pel kereshető markdown-okban van, akkor LLM is ugyanúgy hozzáfér mint egy ember — nincs köztes proprietary réteg, nincs API-rate-limit, nincs vendor lock-in.

A mi vaultunk **3 agent** (Claude, Codex, Gemini) közös tudásbázisa. Ez **csak akkor működik**, ha mindegyik ugyanazt a forrást olvassa: 86 markdown fájl egy git-tracked mappában.

## Operatív következmények nálunk

- **Git-tracked**: `github.com/PetykaMaki/obsidian-vault` privát repó, dev + prod cron 10 percenként commit+push
- **Symlinks**: `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md` mind ugyanarra a fájlra mutatnak
- **Plain markdown**: Obsidian-specifikus dolgokra (Excalidraw embed, Canvas) van link, de a "tudás" markdown-ban él
- **No DB**: nincs külön index, nincs vector store. `grep`/`rg` + Obsidian search elég

## Trade-off

Kepano elve **nem mindig optimális**:
- Komplex relációk (több-mint-fa graph) markdown-ban macerás → wikilink + tag-taxonomy próbálja megoldani
- Nagy bináris (kép, video) nem markdown-ban él → Obsidian attach folder

Erre a trade-off-ra a megoldás: **a "fontos tudás" markdown**, a média mellette, de nem a tudás-réteg része.

## Kapcsolódó

- [[11-wiki/Karpathy-LLM-Wiki-pattern]]
- [[11-wiki/Johnny-Decimal-prefix]]
- [[AGENTS]]
- [[README]]

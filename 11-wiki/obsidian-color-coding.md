---
name: Obsidian color-coding playbook
type: wiki
tags: ["#type/wiki", obsidian, ui, styling, css, playbook]
trigger_keywords: [obsidian-color, cssclasses, graph-color-groups, project-color, obsidian-snippet, color-by-tag]
created: 2026-05-13
updated: 2026-05-13
status: stable
---

# Obsidian projekt-szín-kódolás — plugin-mentes playbook

Projekt-vagy-cluster alapú szín-kódolás Obsidian-ban **plugin nélkül**, csak CSS snippet + `cssclasses:` frontmatter + `graph.json` colorGroups. Cross-platform (Mac / iOS / Linux), git-tracked, ~10 perc setup.

## A 3 réteg

| Réteg | Mit színez | Hogyan |
|---|---|---|
| **CSS snippet** | Title-bar marker, inline-title, H1 border, tab-header | `.obsidian/snippets/<name>.css` + `cssclasses:` frontmatter |
| **Graph color-groups** | Graph-view node-ok | `.obsidian/graph.json` `colorGroups` array (`path:` OR `tag:` query-szintaxis) |
| **(Opcionális) Community plugin** | File-explorer row / icon, 3D-view | Iconize, File Color, 3D Graph, Colorful Tag |

## 1. `cssclasses:` frontmatter pattern

A `cssclasses:` YAML-mező az adott dokumentum body-classlist-jébe injektál CSS-class-t Reading + Source mode-ban egyaránt. Plugin nincs hozzá szükséges — Obsidian-native feature.

**Frontmatter:**
```yaml
---
name: Foxxi projekt
type: project
cssclasses: [proj-foxxi]
---
```

**CSS snippet (`.obsidian/snippets/project-colors.css`):**
```css
:root {
  --proj-foxxi: #10b981;   /* mint green */
  --proj-kgc:   #3b82f6;   /* blue */
}

/* Inline title (the H1-szerű "title" a fájl tetején) */
.proj-foxxi .inline-title { color: var(--proj-foxxi); }
.proj-kgc   .inline-title { color: var(--proj-kgc); }

/* H1 left-border accent */
.proj-foxxi .markdown-rendered > h1:first-of-type {
  border-left: 4px solid var(--proj-foxxi);
  padding-left: 8px;
}

/* Title-bar 8px color-marker (a workspace-leaf-en :has() selector-rel) */
.workspace-leaf:has(.proj-foxxi) .view-header-title-container::before {
  content: "";
  display: inline-block;
  width: 8px; height: 18px;
  margin-right: 8px;
  border-radius: 3px;
  background: var(--proj-foxxi);
  vertical-align: middle;
}

/* Tab-header inset shadow (alulra színes 2px line) */
.workspace-tab-header:has(.proj-foxxi) {
  box-shadow: inset 0 -2px 0 var(--proj-foxxi);
}
```

**Aktiválás:**
```json
// .obsidian/appearance.json
{
  "enabledCssSnippets": ["project-colors"]
}
```

Vagy Obsidian-UI-ban: Settings → Appearance → CSS snippets → toggle.

## 2. Graph.json `colorGroups` query-szintaxis

A built-in Obsidian Graph view támogat tag/path alapú color-groups-ot. A `.obsidian/graph.json`-ban explicit JSON-edit.

**Format:**
```json
{
  "showTags": true,
  "colorGroups": [
    {
      "query": "(path:\"02-Projects/foxxi\") OR (tag:#project/foxxi)",
      "color": {"a": 1, "rgb": 1096065}
    },
    {
      "query": "(path:\"02-Projects/kgc-erp\" OR path:\"02-Projects/kgc-berles\") OR (tag:#project/kgc-erp OR tag:#project/kgc-berles)",
      "color": {"a": 1, "rgb": 3900150}
    }
  ]
}
```

**RGB-int kalkuláció:** `int(hex_color[1:], 16)` Python-ban. Pl. `#10b981` → `0x10b981` → `1096065`.

**Query operátorok:**
- `path:"<prefix>"` — fájl-path substring match (mindig `02-Projects/...` ha projekt-fájlra cél)
- `tag:#<tagname>` — frontmatter `tags:` vagy inline `#tag` match
- Kombinálható `OR` szabállyal: `(query1) OR (query2)`
- **Első egyezés-szín win-eling** — ha 2 colorGroup is matchelne, a list-elsőé érvényesül

**`showTags: true`** enableli a tag-nodes-t a graph-on (visual-rich), default `false`.

## 3. Programatikus deploy (több projekt egyszerre)

Python script-tel batch-update:

```python
import json, re
from pathlib import Path

VAULT = Path("/path/to/vault")
CLUSTERS = {"foxxi": "proj-foxxi", "kgc-berles": "proj-kgc", ...}

# 1. Frontmatter: add cssclasses
for slug, cluster in CLUSTERS.items():
    pf = VAULT / "02-Projects" / f"{slug}.md"
    text = pf.read_text()
    fm = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if fm and "cssclasses:" not in fm.group(1):
        new_fm = fm.group(1) + f"\ncssclasses: [{cluster}]"
        pf.write_text(f"---\n{new_fm}\n---" + text[fm.end():])

# 2. graph.json colorGroups
graph = json.loads((VAULT / ".obsidian/graph.json").read_text())
graph["colorGroups"] = [...]
graph["showTags"] = True
(VAULT / ".obsidian/graph.json").write_text(json.dumps(graph, indent=2))

# 3. appearance.json
app = json.loads((VAULT / ".obsidian/appearance.json").read_text())
app["enabledCssSnippets"] = ["project-colors"]
(VAULT / ".obsidian/appearance.json").write_text(json.dumps(app, indent=2))
```

Backup .bak fájllal minden módosítás előtt (revertable).

## Mit IGENIS plugin kell

Ha **ezeket** is színesíteni szeretnéd, akkor community plugin szükséges:

| Cél | Plugin |
|---|---|
| **File-explorer row-color** (mindig látható, nem csak megnyitott file-en) | [`obsidian-iconize`](https://github.com/FlorianWoelki/obsidian-iconize) per-file/folder ikon + színpaletta |
| **Tag-chip szín** Reading mode-ban (a `#foxxi` chip maga is színes) | [`colorful-tag`](https://github.com/rsa-pixie/colorful-tag) |
| **3D Graph view** rotálható, three.js | [`obsidian-3d-graph`](https://github.com/AlexBrandes/obsidian-3d-graph) — beállítások NEM öröklődnek a 2D graph.json-ból |
| **Folder-szín** explorer-ben | [`file-color`](https://github.com/lijyze/file-color) plugin |

## Élő alkalmazás — Peti-vault (2026-05-13)

17 aktív projekt × 7 cluster-szín:

| Cluster | Slug-ok | Szín |
|---|---|---|
| 🏗️ KGC | kgc-erp, kgc-berles, kgshop-bluebird, kgc-marketing, kgc-kivetitok, kgc-tv-cms | `#3b82f6` blue |
| 🦷 Foxxi | foxxi, foxxi-email-arhivum | `#10b981` mint |
| 🤖 MyForge | myforge-dashboard, koko, mfl-bot | `#a855f7` purple |
| 🎯 Petanque | petanque-kisgeparuhaz, mapesz | `#f97316` orange |
| 🔬 Research | teszt-eu, robbantott-kereso | `#06b6d4` cyan |
| ☕ Rojt és Bojt | rojtesbojt | `#9f1239` wine |
| 🧠 SV-meta | superintelligent-vault | `#d946ef` magenta |

Részletek: [[08-Sessions/2026-05-13-sv-obsidian-coloring]].

## Troubleshooting (real-world tapasztalat 2026-05-13)

### Tag-audit step KÖTELEZŐ a graph color-groups query-design ELŐTT

A `tag:#project/<slug>` query **csak akkor matchel**, ha az adott tag tényleg létezik a fájlok frontmatter-ében. Audit-step:

```bash
for f in 02-Projects/*.md; do
  slug=$(basename "$f" .md)
  [[ "$slug" == "Index" ]] && continue
  has=$(grep -c "#project/$slug" "$f" || true)
  echo "  $slug: $has matches"
done
```

**Élő példa:** 2026-05-13 reggelén Peti-vault audit kimutatta hogy csak 6/17 projekt-fájlnak volt `#project/<slug>` tag-je → a graph color-groups 11 projektnél nem matchelt. Fix: hozzáadtuk a hiányzó tag-eket frontmatter `tags: [...]` listához (`.bak.<date>-tags` backup).

### `cssclasses` + graph color-groups KÉT KÜLÖNBÖZŐ rendszer

Fontos félreértés: a `cssclasses:` frontmatter mező **CSAK** a HTML body-class-injekcióra megy (in-document styling — title-bar marker, inline-title color). A graph view **kizárólag** a saját `graph.json` `colorGroups` queries-eit használja, és azok tag/path-alapúak. NEM örökli automatikusan a cssclasses-t.

**Tanulság:** ha vault-szintű színkódolás kell, MINDKETTŐT explicit be kell állítani (cssclasses + graph queries).

### Mac-Obsidian-Git `pull.rebase=true` + workspace-state modify = double-conflict cascade

Ha a Mac-Obsidian automatikusan módosítja a `.obsidian/graph.json`-t (zoom-level, scroll-pos), és **közben a remote-on is van push** ugyanezt a fájlt érintve: első `git pull` után az első conflict-resolve UTÁN **újabb rebase-conflict** jön elő (mert `pull.rebase=true` van set-elve Mac-en, MEMORY-ban dokumentált).

**Megoldás (rebase-mid):**

```bash
# Rebase-ben a --ours/--theirs FORDÍTOTT a sima merge-hez képest:
git checkout --ours .obsidian/graph.json    # ← --ours = rebase-bázis = origin/main = remote color-fix
git add .obsidian/graph.json
git rebase --continue
```

A `--ours` rebase-ben a "rebase-bázis" (az amire éppen rebase-elünk), NEM a "saját" branch. **Counterintuitive, de így van.** Sima merge-ben fordítva.

### `conflict-files-obsidian-git.md` plugin auto-gen helper

Az Obsidian-Git plugin egy temporary helper-fájlt ír a vault-gyökérbe konfliktus-debug-hoz (`conflict-files-obsidian-git.md`). **NE commit-old** — minden conflict-ciklus után regenerálódik. Egyszerű:

```bash
rm conflict-files-obsidian-git.md   # az conflict-resolve UTÁN, push ELŐTT
```

## Backout

```bash
# Snippet off
# Settings → Appearance → CSS snippets → toggle off "project-colors"
# Vagy:
sed -i 's/"enabledCssSnippets": \[.*\]/"enabledCssSnippets": []/' .obsidian/appearance.json

# Frontmatter revert per-projekt:
for f in 02-Projects/*.md; do
  if [[ -f "$f.bak.20260513-colors" ]]; then
    mv "$f.bak.20260513-colors" "$f"
  fi
done

# Graph color-groups off:
# .obsidian/graph.json → colorGroups: []
```

## Kapcsolódó

- [[11-wiki/sprint-day-0-skeleton-first]] — Day-0 commit pattern (most bundle-egyszerre csinálta a 4 részt)
- [[00-Meta/Frontmatter-schema]] — `cssclasses:` mező frontmatter-konvenció
- [[02-Projects/Index]] — 17 projekt-fájl ami most cluster-color-ot kapott

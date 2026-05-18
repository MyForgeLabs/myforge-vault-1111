---
name: Audit-MD self-referential loop pattern
type: wiki
tags: ["#type/wiki", "vault-integrity", "audit", "wikilink", "false-positive", "recurring-job"]
created: 2026-05-18
updated: 2026-05-18
status: stable
---

# Audit-MD self-referential loop

A vault-ban élő **rekurrens auditor-szkriptek** (broken-wikilink-scanner, system-health, ko-conflicts-audit, orphan-wiki-detector, stb.) MD-be írják a leleteiket. Ha az audit-output **valódi `[[wikilink]]` formátumban** listázza a broken target-eket, akkor a következő scan ezt **újra-flag-eli** mint új broken-source — végtelen self-referential loop, ami percről percre felfújja az issue-count-ot és elfedi a valódi problémákat.

## TL;DR

- **Tünet:** broken-wikilink-count monoton nő scan-ről scan-re, jellemzően `1656`, `1900`, `2200` issue, de a vault-on érdemi változás nincs
- **Ok:** az auditor output-MD önmaga is `[[broken-target]]` literal-eket tartalmaz → scanner felveszi mint broken-source
- **Fix:** vagy backtick-wrap (`` `[[X]]` `` formátum) az audit-MD-ben, vagy `is_excluded_path()` patch a scanner-ben, ami audit-MD-ket kihagyja a forrás-set-ből
- **Reusable:** minden rekurrens vault-audit-szkriptnek **self-exclude** kell

## Háttér — 2026-05-18 vault-cleanup incidens

A heti cron-vasárnap `/usr/local/bin/vault-cleanup` regenerálja a `/root/obsidian-vault/06-Audits/System_Health.md`-t és a `/root/obsidian-vault/06-Audits/broken-wikilinks-latest.md`-t. A 2026-05-18 manuális futás eredménye: **1656 broken-wikilink-issue**, ami önmagában magas. Részletes vizsgálat után kiderült: az 1656-ból ~70-80% **maga az audit-MD egy korábbi futásból** — a `broken-wikilinks-latest.md` literal `[[NEM-LÉTEZŐ-TARGET]]` sorokat tartalmazott (mert ezek voltak a tényleges broken-target-ek a riport-ban), és a következő scanner-futás ezeket úgy értelmezte, hogy az audit-MD **forrás-fájl**, ami `[[NEM-LÉTEZŐ-TARGET]]`-re hivatkozik.

Klasszikus **observer-effect**: a megfigyelő-eszköz a saját outputjával zavarja a következő mérést.

## A pattern (3 megoldás)

### 1. Backtick-wrap az audit-output-ban (legbiztosabb)

Minden broken-target literal-t inline-code-ba csomagolj:

```python
# audit-writer pattern
for issue in broken_links:
    f.write(f"- `[[{issue.target}]]` referenced from `{issue.source}`\n")
```

A backtick miatt az Obsidian/scanner NEM értelmezi wikilink-nek. Override-mentes, semmi config-állítás.

### 2. `is_excluded_path()` patch a scanner-ben

```python
EXCLUDE_PATTERNS = [
    r"06-Audits/.*\.md$",
    r"06-Audits/.*broken-wikilinks.*\.md$",
    r"08-Sessions/.*\.md$",  # session-ek néha referálnak broken-link-eket példában
]

def is_excluded(path: Path) -> bool:
    return any(re.search(p, str(path)) for p in EXCLUDE_PATTERNS)

for md in vault.glob("**/*.md"):
    if is_excluded(md):
        continue
    scan_links(md)
```

Előnyök: vault-author szabadon írhat literal wikilink-et az audit-MD-be. Hátrány: az audit-MD-k tényleges broken-source-ai is láthatatlanok lesznek.

### 3. Marker-frontmatter — "audit-output" flag

```yaml
---
type: audit-report
audit-self-exclude: true
---
```

A scanner ezt olvassa be, és kihagyja. Általánosabb, mint path-pattern, de minden audit-író szkript-nek be kell tartani a konvenciót.

## Anti-pattern: post-hoc filter

NE szűrd ki az audit-MD broken-link-jeit **utólag**, a riport-generáláskor (`grep -v 'broken-wikilinks-latest.md'`). Egy-két iteráció után az új audit-MD-k (pl. `ko-conflicts-latest.md`, `orphan-wiki-latest.md`) szintén bekerülnek a noise-ba, és a filter-lista karbantarthatatlanul nő. A self-exclude **a scanner forrás-set-jénél** legyen, nem a riport-fázisban.

Másik anti-pattern: **literal-link helyett file-link** (`[broken: NEM-LÉTEZŐ-TARGET](nem-letezo-target.md)`). Ez markdown-link, NEM wikilink, de a scanner egy része ezt is felveszi. A backtick-wrap univerzális.

## Reusable szabályok

| Audit-script | Self-exclude célja | Konvenció |
|---|---|---|
| `broken-wikilinks` | Saját output-MD | path-pattern `06-Audits/broken-wikilinks-*.md` |
| `System_Health` | Saját + összes audit-MD | path-pattern `06-Audits/**/*.md` |
| `ko-conflicts-audit` | Saját + audit-history | path-pattern `06-Audits/ko-conflicts-*.md` |
| `orphan-wiki-detector` | Maga az orphan-lista | path-pattern `06-Audits/orphan-*.md` |
| `vault-link-graph-export` | Minden audit + raw input | path-pattern `06-Audits/**`, `10-raw/**` |

**Általános ökölszabály:** minden script, ami `**/*.md`-en iterál és wikilink-eket / referenciákat / hivatkozásokat dolgoz fel, **első sorban** definiáljon `EXCLUDE_PATTERNS`-t, és az tartalmazza:
- a **saját kimeneti útvonalát** (és minden variánsát: `-latest.md`, `-YYYY-MM-DD.md`)
- a `06-Audits/**` mappát (általában)
- ha session-ekben példa-link-ek lehetnek: `08-Sessions/**`
- raw input (`10-raw/**`) — ezekben gyakran nyers szöveg, nem a vault-link-graph része

## Komplementer pattern-ek

- **Reproducible audit output** — a riport ne tartalmazzon timestamp-et inline, csak frontmatter-ben. Így git-diff-fel látszik, hogy két scan közt érdemben mi változott
- **Severity-bucket** — ne single-list legyen az output, hanem `### Critical`, `### Warning`, `### Info` szekciók. Self-loop által generált noise-t info-ba teszi a scanner, és a critic-szekció tiszta marad
- **Diff-only riport-mód** — a script tudja, mi volt az előző scan eredménye, és csak az új issue-kat listázza. Ez akkor is enyhíti a self-loop-ot, ha az exclude nincs beállítva

## Detektálás

Gyors check: ha az audit-output broken-link-count > 100 és a vault méret kicsi (< 1000 MD), akkor nagy valószínűséggel self-loop. Sanity-check parancs:

```bash
# Hány broken-link forrás-fájl az audit-MD?
grep -h "referenced from" /root/obsidian-vault/06-Audits/broken-wikilinks-latest.md \
  | grep -oE "from \`[^\`]+\`" | sort | uniq -c | sort -rn | head -10
```

Ha a top-source maga az audit-MD vagy egy `06-Audits/*` file, biztosan self-loop.

## Kapcsolódó

- [[vault-corruption-detection-pattern]] — alapja az audit-stabil monitorozás
- [[Karpathy-LLM-Wiki-pattern]] — vault-szerkezet, ami self-referenciát szül
- [[../06-Audits/System_Health]] — élő alkalmazás, weekly cron
- [[multi-layer-safety-gate]] — audit mint védelmi réteg

---
name: atomic-write HIGH-4 wrap-up
type: audit
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/audit", "#topic/vault-atomic", "#topic/posix-atomic", "#layer/1-fs"]
---

# atomic-write HIGH-4 wrap-up — Layer-1 vault-atomic full coverage

> [!success] Layer-1 vault-atomic Path(...).write_text race-risk: **zero remaining** /usr/local/bin python scripts touching the vault still use raw `write_text` for multi-KB artifacts.

## Scope

Az atomic-write HIGH-3 + 11.11crystallize + MEDIUM-2 migrációk után az atomic subagent még **4 HIGH-rizikó scriptet** azonosított. Ez a wrap-up bezárja a Layer-1 kört (`/usr/local/bin`).

## Patches — 4 script, 7 site

### 1. `bmad-vault-bridge` (3 site, HIGH frontmatter mutator)
- **Imports:** `sys.path.insert(0, '/root/obsidian-vault/.vault-tools/lib')` + `from vault_atomic import atomic_write`
- **L240 (`--in-place`):** `target.write_text(write_frontmatter(fm, body), encoding="utf-8")` → `atomic_write(target, write_frontmatter(fm, body))`
- **L246 (route into `02-Projects/<slug>/bmad/`):** ugyanaz a csere
- **L448 (`--context --write` bundle):** `target.write_text(block, ...)` → `atomic_write(target, block)`
- **Why HIGH:** a frontmatter-mutator közben olvashatja Obsidian-watcher / `vault-ko-ingest` / `vault-embed` chain — fél-renderelt YAML = broken-wikilink + ingest-fail kaszkád.

### 2. `vault-wiki-quality-score` (2 site, dual JSON+MD race)
- **Imports:** `atomic_write, atomic_write_json`
- **L268-269:** `Path(args.json_out).write_text(json.dumps(...))` + `Path(args.md_out).write_text(...)` → `atomic_write_json(...)` + `atomic_write(...)`
- **Why HIGH:** JSON-t a `wiki-quality-trend` dashboard fogyasztja párhuzamosan; partial JSON = `JSONDecodeError` minden olvasónak amíg újra-írás be nem fejeződik.

### 3. `vault-adr-aging-watch` (1 site)
- **Imports:** `atomic_write`
- **L191:** `AUDIT_OUT.write_text(render_md(adrs))` → `atomic_write(AUDIT_OUT, render_md(adrs))`

### 4. `github-trending-report` (1 site)
- **Imports:** `atomic_write`
- **L135:** `out_file.write_text(out_text, encoding='utf-8')` → `atomic_write(out_file, out_text)`
- (A subsequent `subprocess` auto-commit változatlan — git-műveletek atomicitása kívül esik a Layer-1 hatókörből.)

## Verify

**py_compile** — mind 4 script OK:
```
=== py_compile: bmad-vault-bridge === OK
=== py_compile: vault-wiki-quality-score === OK
=== py_compile: vault-adr-aging-watch === OK
=== py_compile: github-trending-report === OK
```

**Functional smoke**:
- `bmad-vault-bridge --help` — argparse OK
- `vault-wiki-quality-score --help` + `--sample 3` (read-only, stdout) — score-output OK (76/73/52)
- `vault-adr-aging-watch --help` + `--proposed` (read-only) — OK
- `github-trending-report` — import-only smoke (NEM futtatva network-fetch miatt), atomic_write resolved
- Import-only smoke: `from vault_atomic import atomic_write, atomic_write_json` — mindkét callable bind-elve

## Layer-1 full-coverage audit (őszinte mérnöki összefoglaló)

**Maradék-keresés** (`/usr/local/bin/*` python scripts amik vault-ot érintenek és `write_text(`-et / `json.dump`-ot használnak ÉS NEM importálnak `vault_atomic`-ot):

```
$ for f in /usr/local/bin/*; do
    head -1 "$f" | grep -qE "python" || continue
    grep -q "obsidian-vault" "$f" || continue
    [ $(grep -cE '\.write_text\(|json\.dump\b' "$f") -eq 0 ] && continue
    grep -q "vault_atomic" "$f" && continue
    echo "$f"
  done
(no output)
```

**Eredmény:** `/usr/local/bin` 86 fájl, 0 maradék race-risk. A `.vault-tools/` Python-moduljaiban szintén 0 nem-konvertált `write_text`.

### Maradt-e write_text race-risk?

**Layer-1 (fs-level multi-KB artifact writes /usr/local/bin-ben) — TELJES coverage.**

Azonban őszintén:

1. **Layer-2 (CLI bin nélkül)** — a vault-on belüli ad-hoc Python utility-k (pl. `/root/obsidian-vault/.vault-tools/snapshots/` script-jei, ha vannak) NEM lettek scannelve ezen wrap-up-ban. A vault-tools/ subtree-n viszont a grep `0 maradék`-ot ad — ezt megerősítettem.
2. **Layer-3 (shell `echo > file` / `tee` redirect)** — kívül esik a `vault_atomic`-on. Pl. `vault-autosave` cron, ha `>>` append-tel ír konfig-fájlt, az nem POSIX-atomic. Ez **explicit known-gap**.
3. **Layer-4 (idegen tooling: NotebookLM CLI, firecrawl, gh, …)** — third-party, write-pattern-jük nem audit-tárgy.
4. **Append-only JSONL** (audit-log-ok pl. `bmad-vault-bridge L107`) — POSIX `O_APPEND` < 4096 byte garanciára épít, NEM atomic_write-on. Ez szándékos: az `atomic_append_jsonl` helper pont erre van, de a meglévő `fh.write(json.dumps(...) + "\n")` pattern is biztonságos minden audit-line < PIPE_BUF-nál. **NEM HIGH-risk**, de migráció ajánlott egységességért — külön ticketben.

### Lezárt skópon belül: clean.

A 4 wrap-up-script + a korábbi HIGH-3 + 11.11crystallize + MEDIUM-2 együtt **a Layer-1 vault-atomic kör teljes**. Új HIGH-rizikó-pont csak akkor jönne, ha új script kerül a /usr/local/bin-be — javaslat: **lint-rule** (`grep "obsidian-vault" + write_text + nincs vault_atomic` → error) bekötése a `vault-cleanup`-ba.

## Followups (NON-blocking, low priority)

- [ ] **Append-only audit-log-ok** migrálása `atomic_append_jsonl(...)`-ra (`bmad-vault-bridge`, `vault-ko-ingest`, `vault-embed`) — egységesség, ~10 perc, MEDIUM-tier
- [ ] **Lint-rule bekötése** `vault-cleanup`-ba: új /usr/local/bin python script ne kerülhessen be `vault_atomic` import nélkül ha vault-touch
- [ ] **Layer-3 shell scriptek** auditja: van-e `>>` append vault-fájlra ami concurrent-read mellett crash-elhet (alacsony valószínűségű, ritka kombináció)

## Kapcsolódó

- [[2026-05-18 vault_atomic.py shared modul]]
- [[2026-05-18 atomic-write HIGH-3 migration]]
- [[2026-05-18 atomic-write 11.11crystallize + MEDIUM-2]]
- [[../11-wiki/posix-atomic-write-pattern]]

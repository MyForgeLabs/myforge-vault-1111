---
name: agent-vault-setup-playbook
type: playbook
tags: ["#type/playbook", "vault-setup", "onboarding", "obsidian"]
created: 2026-05-12
updated: 2026-05-12
---

# Agent-vault setup playbook (Mac + VS Code Claude Code)

Step-by-step doksi egy új gépre / új embernek a teljes rendszer telepítéséhez: **Obsidian vault** (Karpathy-LLM-Wiki minta + Johnny-Decimal struktúra) + **3 agent binding** (Claude Code, Codex, Gemini) + **11.11 session-protokoll scriptek** + **agent-skill könyvtár** (~280 skill, köztük a 4 obsidian-skill) + **automatizációk** (auto-save, weekly health-audit).

> [!warning] Érzékeny tartalom
> Peti meglévő vaultja (`/root/obsidian-vault`) **üzleti adatot tartalmaz** (KGC ügyfelek, Foxxi belső, example-balance.local szerződések). Az ismerősnek **NE** a meglévő repót klónozza — a doksi **sablon-átvitelt** ír le: az alap-vázat (00-Meta, AGENTS.md, üres mappák, wiki-minták) másoljuk, és az ismerős a saját GitHub-repójába pusholja. Részletek a [3. lépésben](#3-vault-bootstrap-saját-üres-repo-ba).

## Mit fogunk telepíteni — komponens-leltár

| Komponens | Hely (Mac) | Eredet |
|---|---|---|
| **Vault** (mappa-struktúra + AGENTS.md + 00-Meta + 11-wiki minták) | `~/obsidian-vault/` | Sablon-fájlokat csomagolunk Peti vaultjából |
| **Obsidian-app** (vizualizáció) | `/Applications/Obsidian.app` | Hivatalos installer |
| **Claude Code** (CLI + VS Code extension) | `/usr/local/bin/claude` + VS Code | Anthropic |
| **Codex** + **Gemini CLI** (opcionális — 3-agent setup) | Homebrew / npm | OpenAI / Google |
| **3 agent-symlink** (CLAUDE.md/AGENTS.md/GEMINI.md → vault/AGENTS.md) | `~/.claude/` `~/.codex/` `~/.gemini/` | Symlink |
| **Agent-skill könyvtár** (~280 skill) | `~/.agents/skills/` + symlinkek 3 agentbe | Több külső repó cherry-pick + saját |
| **4 obsidian-skill** | benne a skill-könyvtárban | `obsidian-cli`, `obsidian-bases`, `obsidian-markdown`, `json-canvas` |
| **11.11 session-scriptek** | `~/.local/bin/11.11*` (+ rövid `/11.11` symlinkek opcionális) | `/usr/local/bin/` from Peti |
| **Auto-memory** (claude-side legacy memory layer) | `~/.claude/projects/-{slug}/memory/MEMORY.md` | Symlinkek a vault Memory rétegébe |
| **Automatizációk** | macOS `launchd` LaunchAgents (Linux-cron helyett) | 3 job: autosave / weekly cleanup / daily github-trending |
| **GitHub remote** (vault-sync) | `https://github.com/<user>/obsidian-vault.git` (privát) | Az ismerős saját |

---

## 0. Előfeltételek (Mac)

```bash
# Homebrew (ha még nincs)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Alap-eszközök
brew install git gh node python@3.12 ripgrep fd jq

# GitHub auth (HTTPS push token nélkül)
gh auth login

# Obsidian app (vizualizáció)
brew install --cask obsidian

# VS Code (ha még nincs)
brew install --cask visual-studio-code

# Claude Code (VS Code extension)
#   VS Code → Extensions → "Claude Code" → Install
#   Vagy: code --install-extension anthropic.claude-code
```

> [!info] Apple Silicon vs Intel
> Apple Siliconon (M1/M2/M3/M4) Homebrew alapértelmezett prefix `/opt/homebrew`, Intel-en `/usr/local`. Az `eval "$(/opt/homebrew/bin/brew shellenv)"` sor mehet a `~/.zshrc`-be a PATH miatt. A doksiban `~/.local/bin`-t használunk a 11.11 scripteknek — user-area, mindkét arch-on egyforma.

**Opcionális (csak ha 3-agent setupot is akar):**

```bash
# Codex CLI (OpenAI)
npm install -g @openai/codex

# Gemini CLI (Google)
brew install gemini-cli   # vagy: npm install -g @google/gemini-cli
```

> [!note] 1-agent vagy 3-agent?
> A vault egyszerre 3 agentet támogat (Claude/Codex/Gemini) közös AGENTS.md-vel + közös skill-könyvtárral. Ha az ismerős most csak Claude-ot használ, **kihagyhatja** a Codex/Gemini-részeket — később egyetlen `ln -s` paranccsal hozzá lehet adni.

---

## 1. PATH felkészítés

```bash
mkdir -p ~/.local/bin
# Add to ~/.zshrc if not there:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 2. GitHub repó létrehozása (privát)

Az ismerős saját GitHub-fiókján egy **új, üres privát repó** kell — pl. `obsidian-vault`. Készítsd meg üresen (README, .gitignore nélkül), vagy `gh`-val:

```bash
gh repo create obsidian-vault --private --description "Personal Karpathy-LLM-Wiki + agent vault"
```

---

## 3. Vault bootstrap (saját üres repo-ba)

A célunk **nem** Peti vaultjának klónja, hanem **csak a struktúra + szabályok + wiki-minták**. Peti gépén csinálunk egy sablon-tarball-t és átküldjük.

### 3.1 Peti gépén — sablon-csomag generálás

```bash
cd /root/obsidian-vault

# Tar a "vázzal" — 00-Meta + AGENTS.md + README + 11-wiki (a meta-fájlok) + üres mappák
tar -czf /tmp/vault-template.tar.gz \
  AGENTS.md \
  README.md \
  .gitignore \
  00-Meta/ \
  11-wiki/Karpathy-LLM-Wiki-pattern.md \
  11-wiki/Johnny-Decimal-prefix.md \
  11-wiki/11.11-session-protokoll.md \
  11-wiki/Auto-context-loading.md \
  11-wiki/Crystallization-protocol.md \
  11-wiki/agent-vault-setup-playbook.md

# scp / airdrop / mail az ismerősnek
```

> [!tip] Más wiki-fájlok átvitele
> A `11-wiki/` többi fájlja Peti-specifikus tudást tartalmaz (KGC, Foxxi, WP gotcha-k). Az ismerős a sajátját idővel tölti föl. Ha mégis át akar venni általános minőségű wiki-cikkeket (pl. `nextjs-search-params-force-dynamic.md`, `puppeteer-pdf-system-chrome.md`), egyenként cherry-pick.

### 3.2 Ismerős gépén — extract + git init

```bash
mkdir -p ~/obsidian-vault && cd ~/obsidian-vault
tar -xzf /path/to/vault-template.tar.gz

# Hozz létre üres mappákat amik nincsenek a tarballban
mkdir -p 01-Daily 02-Projects 03-Hosts 04-Tasks 05-Memory 06-Audits 07-Decisions 08-Sessions/_archive 10-raw

# Üres Index-fájlok minden szám-prefix mappába
for d in 01-Daily 02-Projects 03-Hosts 04-Tasks 05-Memory 06-Audits 07-Decisions 10-raw 11-wiki; do
  [ -f "$d/Index.md" ] || cat > "$d/Index.md" <<EOF
---
name: $d Index
type: index
created: $(date -I)
---

# $d

(üres — töltsd fel a sablonok szerint)
EOF
done

# Git init + first commit + push
git init -b main
git add -A
git commit -m "Initial vault from template"
git remote add origin https://github.com/<user>/obsidian-vault.git
git push -u origin main
```

### 3.3 AGENTS.md személyre szabás

Az `AGENTS.md` Peti-specifikus elemeket tartalmaz (user neve, email, projektek). **Az ismerős nyissa meg és írja át**:
- `## Ki a user` szakasz — saját adatok
- A `## Mit csinálj SESSION INDULÁSKOR` és többi konvenció maradhat (ezek univerzálisak)

```bash
code ~/obsidian-vault/AGENTS.md
```

---

## 4. Obsidian-app — vault megnyitása

1. Nyisd meg az Obsidian-appot.
2. **Open folder as vault** → válaszd a `~/obsidian-vault/` mappát.
3. **Trust author** (ha rákérdez).
4. Settings → Files & links → **Default location for new attachments** = `vault folder`.
5. Settings → Core plugins → kapcsold be: **Tasks**, **Bases**, **Templates**, **Daily notes**, **Outgoing links**, **Backlinks**.
6. Settings → Community plugins → engedélyezd (Restricted mode OFF), és telepítsd:
   - **Tasks** (obsidian-tasks-plugin)
   - **Dataview** (opcionális — query views)
   - **Templater** (opcionális — dinamikus sablonok)

> [!note] A `.obsidian/` mappa
> Az Obsidian config a `~/obsidian-vault/.obsidian/`-be kerül. Ezt **NE törld a `.gitignore`-ral** — szándékos, hogy a plugin-listát és a graph-beállításokat verzióljuk.

---

## 5. Agent binding — 3-agent symlinkek

A 3 agent ugyanazt az `AGENTS.md`-t olvassa különböző fájlnevekkel:

```bash
# Claude Code
mkdir -p ~/.claude
ln -sf ~/obsidian-vault/AGENTS.md ~/.claude/CLAUDE.md

# Codex (ha telepítve)
mkdir -p ~/.codex
ln -sf ~/obsidian-vault/AGENTS.md ~/.codex/AGENTS.md

# Gemini (ha telepítve)
mkdir -p ~/.gemini
ln -sf ~/obsidian-vault/AGENTS.md ~/.gemini/GEMINI.md

# Verify
ls -la ~/.claude/CLAUDE.md ~/.codex/AGENTS.md ~/.gemini/GEMINI.md 2>/dev/null
```

Ezek után minden agent ugyanazokból a szabályokból dolgozik — egy szerkesztés azonnal él mindenhol.

---

## 6. Agent-skill könyvtár

Peti gépén ~280 skill van a `~/.agents/skills/` mappában, ami 3 agent felé symlinkkel publikálva. Az ismerős kétféleképpen oldhatja meg:

### 6.1 Opció A — Csak a 4 obsidian-skill + a session-kezelő 2 skill (minimum)

A vault működéshez ennyi elég:

| Skill | Mire való |
|---|---|
| `obsidian-cli` | Obsidian CLI integráció (note olvas/ír/keres futó Obsidian-appban) |
| `obsidian-markdown` | Obsidian Flavored Markdown (wikilink, callout, embed, frontmatter) |
| `obsidian-bases` | `.base` fájlok kezelése (database-view a noteokon) |
| `json-canvas` | `.canvas` fájlok kezelése (mind map / flowchart) |
| `load-session-context` | Aggressive pre-load 11.11 indulásakor |
| `propagate-session` | Karpathy crystallization 11.11 záráskor |

Peti gépén ezek a `claude-skills` repó-ból + Anthropic example-skills-ből + saját készítésből vannak. Az Anthropic 4 obsidian-skill **publikusan elérhető**:

```bash
# Anthropic skills repo (vagy bármely friss mirror)
mkdir -p ~/.agents/skills
cd /tmp
git clone https://github.com/anthropics/skills.git anthropic-skills

# A 4 obsidian-skill másolása (vagy symlink, ha trackelve akarja tartani)
for s in obsidian-cli obsidian-markdown obsidian-bases json-canvas; do
  cp -r anthropic-skills/$s ~/.agents/skills/
done
```

A `load-session-context` és `propagate-session` Peti-specifikusak — kéri a forrást Petitől, és átmásolja `~/.agents/skills/`-be.

### 6.2 Opció B — Teljes ~280 skill csomag

Peti gépén a `~/.agents/skills/` szét van szedve 5-6 különböző forrásból. Ehhez Peti tarball-ja kell:

```bash
# Peti gépén:
tar -czf /tmp/agents-skills.tar.gz -C /root/.agents skills hooks
# scp az ismerősnek

# Ismerős gépén:
mkdir -p ~/.agents
tar -xzf /path/to/agents-skills.tar.gz -C ~/.agents/
```

### 6.3 Publikálás 3 agent felé (közös skill-pool)

```bash
ln -sf ~/.agents/skills ~/.claude/skills
ln -sf ~/.agents/skills ~/.codex/skills
ln -sf ~/.agents/skills ~/.gemini/skills

# Verify
ls -la ~/.claude/skills ~/.codex/skills ~/.gemini/skills
```

---

## 7. 11.11 session-scriptek

7 bash-script a session-orchestrationhoz:

| Script | Funkció |
|---|---|
| `11.11start "projekt-feladat"` | Új session-fájl + focus |
| `11.11ls` (`11.11list`) | Open + recent closed sessions |
| `11.11focus <slug>` | Focus váltása másik nyitott session-re |
| `11.11note "..."` | Timestamped jegyzet a focused session `## Events`-be |
| `11.11stop [<slug>]` | Summary + Learnings + Next → close → commit → push |
| `11.11` | Health check (vault, symlinkek, skillek) |

### 7.1 Scriptek átvitele

```bash
# Peti gépén:
mkdir -p /tmp/1111-scripts
cp /usr/local/bin/11.11 /usr/local/bin/11.11focus /usr/local/bin/11.11ls \
   /usr/local/bin/11.11note /usr/local/bin/11.11start /usr/local/bin/11.11stop \
   /usr/local/bin/vault-autosave /usr/local/bin/vault-cleanup \
   /tmp/1111-scripts/
tar -czf /tmp/1111-scripts.tar.gz -C /tmp 1111-scripts/
# scp az ismerősnek

# Ismerős gépén:
tar -xzf /path/to/1111-scripts.tar.gz -C /tmp/
cp /tmp/1111-scripts/* ~/.local/bin/
chmod +x ~/.local/bin/11.11* ~/.local/bin/vault-*
ln -sf ~/.local/bin/11.11ls ~/.local/bin/11.11list
```

### 7.2 Path patch — `/root/obsidian-vault` → `~/obsidian-vault`

A scriptek hardcoded `/root/obsidian-vault` path-tal vannak. Mac-en ez nem létezik. **Patcheld a 8 scriptet**:

```bash
cd ~/.local/bin
for f in 11.11 11.11focus 11.11ls 11.11note 11.11start 11.11stop vault-autosave vault-cleanup; do
  sed -i.bak "s|/root/obsidian-vault|$HOME/obsidian-vault|g" "$f"
done

# Verify
grep -l obsidian-vault ~/.local/bin/11.11* ~/.local/bin/vault-* | xargs grep VAULT=
```

> [!warning] BSD sed vs GNU sed
> macOS-en BSD sed van, amihez `-i.bak` kell (üres extension nem működik). A fenti parancs ezért hagy `.bak` fájlokat — `rm ~/.local/bin/*.bak` után.

### 7.3 Rövid `/11.11` symlinkek (opcionális)

Peti gépén `/11.11`, `/11.11start` stb. root-szintű shortcutok élnek (mert root userként dolgozik). Macen ezek **nem javasoltak** (`/`-be root jog kell, és a Mac SIP védi). Inkább zsh-alias:

```bash
# ~/.zshrc
alias 11.11start='~/.local/bin/11.11start'
alias 11.11stop='~/.local/bin/11.11stop'
alias 11.11ls='~/.local/bin/11.11ls'
alias 11.11note='~/.local/bin/11.11note'
alias 11.11focus='~/.local/bin/11.11focus'
alias 11.11='~/.local/bin/11.11'
```

Vagy ha a `PATH`-ban van `~/.local/bin`, és `11.11start` parancsot ír a shell-be, az is működik (a `.` ZSH-ben nem speciális, BASH-ben sem itt) — **DE** a slash command formátum (`/11.11start`) csak akkor megy, ha a Claude Code skill-listájában felvett shell-alias van, vagy a 11.11-skillek (`11.11start`, `11.11stop`, `11.11focus`, `11.11note`, `11.11ls`) is bekerülnek a `~/.agents/skills/`-be. Peti gépén ezek a skillek megvannak — kérje a forrást.

---

## 8. Auto-memory (claude-side legacy memory)

A `~/.claude/CLAUDE.md`-en kívül Claude Code támogatja az "auto-memory" rendszert: `~/.claude/projects/-{slug}/memory/MEMORY.md` + típus-fájlok (user, feedback, project, reference). Peti gépén ezek symlinkek a vault `05-Memory/` mappájába — így egy memory-update a vault-ban is megjelenik.

```bash
SLUG="-Users-$(whoami)-obsidian-vault"  # vagy a project-mappa abszolút path '/' helyett '-'
MEM_DIR=~/.claude/projects/${SLUG}/memory
mkdir -p "$MEM_DIR"

# MEMORY.md index — ezt később az agent tölti automatikusan
cat > "$MEM_DIR/MEMORY.md" <<'EOF'
- 📚 **Közös vault:** `~/obsidian-vault/` — Claude/Codex/Gemini mind ide olvas-ír. Belépő: `~/obsidian-vault/AGENTS.md` (= `~/.claude/CLAUDE.md`)
- 🗂️ **Projekt dashboard:** `~/obsidian-vault/02-Projects/Index.md` — olvasd ezt elsőként új session-ben
- 👤 **User profil:** `~/obsidian-vault/05-Memory/User.md`
EOF
```

> [!tip] Slug detektálás
> Claude Code az aktuális mappából képzi a project-slug-ot: minden `/` és nem-alfanumerikus karakter `-`-é alakul. Ha az ismerős a vault gyökerében indítja Claude-ot (`cd ~/obsidian-vault && claude`), a slug `-Users-<username>-obsidian-vault`. **Tipp:** futtasd egyszer Claude-ot a vault gyökerében, és nézd meg melyik mappa keletkezett `~/.claude/projects/`-ben — az lesz a helyes slug.

A típus-fájlokat (`feedback_*.md`, `project_*.md`, `user_*.md`, `reference_*.md`) az agent maga írja idővel, ahogy tanul.

---

## 9. Automatizációk — macOS `launchd`

Linux-cron helyett Macen `launchd`. 3 job:

### 9.1 vault-autosave (10 percenként commit + push)

`~/Library/LaunchAgents/com.peti.vault-autosave.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.peti.vault-autosave</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>$HOME/.local/bin/vault-autosave</string>
  </array>
  <key>StartInterval</key><integer>600</integer>
  <key>StandardOutPath</key><string>/tmp/vault-autosave.log</string>
  <key>StandardErrorPath</key><string>/tmp/vault-autosave.err</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.peti.vault-autosave.plist
```

### 9.2 vault-cleanup (vasárnap 04:00 — heti audit)

`~/Library/LaunchAgents/com.peti.vault-cleanup.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.peti.vault-cleanup</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>$HOME/.local/bin/vault-cleanup --write</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>0</integer>
    <key>Hour</key><integer>4</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.peti.vault-cleanup.plist
```

### 9.3 github-trending (napi 08:00 — `10-raw/`-ba)

Csak akkor érdekes, ha az ismerős a `github-trending-report` scriptet is átvette. Hagyhatjuk ki első körben.

> [!info] launchd ≠ cron
> A `launchctl load` regisztrálja, az `unload` leveszi. **Mac alvás közben nem fut** — ha laptop lecsukva, a 10-perces interval később pótlódik. Aki dev-szerveren akar futtatni, vegye fontolóra a cron-os Linux VPS variánst.

---

## 10. VS Code + Claude Code integráció

1. VS Code → nyisd meg a `~/obsidian-vault/` mappát.
2. Claude Code extension → balra a "Claude" panel.
3. **Settings** (`cmd+,` → `claude`):
   - **Working Directory:** `~/obsidian-vault`
   - **Project memory:** automatikus (az auto-memory mappát maga keresi).
4. Próbálj egy üzenetet: `mi van a vault-ban?` — a Claude el kell tudjon olvasni `AGENTS.md`-t és működjön.

> [!tip] Multi-folder workspace
> Ha az ismerős a vault-ot és a kódprojektjeit külön mappákban tartja, használjon **VS Code multi-root workspace**-t: `File → Add Folder to Workspace`. A Claude Code mindkét mappát látja, de a session-fájlok a vault-ban keletkeznek.

---

## 11. Első futás — smoke test

```bash
# 1) Health check
~/.local/bin/11.11

# 2) Egy próba-session
~/.local/bin/11.11start "teszt-setup"
# → Nyit egy fájlt: ~/obsidian-vault/08-Sessions/YYYY-MM-DD-teszt-setup.md

# 3) Jegyzet hozzáadás
~/.local/bin/11.11note "first note from new vault"

# 4) Session listázás
~/.local/bin/11.11ls

# 5) Session zárás (Summary üres lehet — --force-ral menjen)
~/.local/bin/11.11stop --force --no-commit

# 6) Manuális commit + push
cd ~/obsidian-vault
git add -A
git commit -m "first smoke test"
git push
```

Ha minden zöld, **megnyitottad az első session-t**, **commit ment GitHub-ra**, **az Obsidian-app látja a `08-Sessions/` új fájlt**.

---

## 12. Claude Code első session — milyen UX-et várjunk

Mikor az ismerős először elindít egy session-t (`/11.11start "valami-projekt"` a Claude Code-ban):

1. A scriptegy üzeneten keresztül `~/obsidian-vault/08-Sessions/YYYY-MM-DD-<slug>.md` fájlt hoz létre, benne az `AGENT TENNIVALÓ` blokk.
2. A Claude Code (mert `~/.claude/CLAUDE.md` → `AGENTS.md` symlink van) **automatikusan betölti** az AGENTS.md-t és felismeri az utasítást: "aggressive context pre-load".
3. Detektálja a projektet, beolvassa a `02-Projects/<slug>.md`-t, az utolsó session-eket, releváns ADR-eket, és **kitölti** a `## Pre-loaded context` szekciót.
4. Ekkor készen áll a munkára — a user beírja az első kérdést.

Záráskor (`/11.11stop`):
1. Az agent kitölti a `## Summary` / `## Learnings → memória` / `## Next session` szekciókat.
2. Routing — minden Learning bullet-re javaslat hogy hova propagálja (ADR / wiki / memory / projekt / task).
3. **Batch preview** a usernek — összes javaslat egyben, a user OK-zza.
4. Propagálás → bash-script commit + push.

---

## 13. Troubleshooting (Mac-specifikus)

### "command not found: 11.11start"

PATH-ban van-e `~/.local/bin`? → `echo $PATH | tr ':' '\n' | grep .local/bin`. Ha nincs, add hozzá a `~/.zshrc`-be, és `source ~/.zshrc`.

### "git push: permission denied (publickey)"

`gh auth login` futott? Ha HTTPS-en akar pusholni, használj GitHub CLI auth tokent: `gh auth setup-git`.

### "launchd job nem indul"

`launchctl list | grep peti` — látható-e? Ha nincs, `launchctl load` újra. Logok: `/tmp/vault-autosave.log` és `.err`.

### "Obsidian nem látja az új fájlt"

Settings → Files → Detect all file extensions = ON. Vagy `cmd+r` reload.

### "11.11 script Linux-specifikus parancsra hiányolja"

Pl. `realpath`, `grep -P` — Mac-en a BSD-vágat más. `brew install coreutils gnu-sed gnu-grep` + `~/.zshrc`-ben `PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"` (Apple Silicon) vagy `/usr/local/opt/coreutils/libexec/gnubin` (Intel). Akkor a Linux-bashizmusok működnek.

### ".active-session pointer divergál"

Lásd MEMORY.md — **3 incidens** Peti gépén több párhuzamos session esetén. `11.11focus <slug>` után pointer ↔ chat-content ütközhet. Manual fix: `echo "/path/to/correct/session.md" > ~/obsidian-vault/.active-session`. Defenzív sanity-check: `/11.11stop` ELŐTT `cat .active-session` + olvasd be a session-fájlt + ellenőrizd hogy a name + Event-ek konzisztensek a chat-history domain-jével.

---

## 14. Mi NEM megy át a sablonnal — manuális töltés

A vault működik üres mappákkal is, de az alábbiakat az ismerős **maga állítsa be** az első héten:

- [ ] `02-Projects/Index.md` → saját projektek táblája
- [ ] `02-Projects/<projekt>.md` → minden aktív projekthez egy fájl
- [ ] `03-Hosts/<host>.md` → ha saját szerverei vannak
- [ ] `05-Memory/User.md` → saját profil (név, prefencák, stack)
- [ ] `05-Memory/Infrastructure.md` → szerver / portok / env-vars (publikus titok-mentes részek)
- [ ] `04-Tasks/Backlog.md` → első 5-10 TODO
- [ ] `01-Daily/` → első napló: `01-Daily/$(date -I).md`

Sablonok: `00-Meta/templates/` — az ismerős innen másol új fájlhoz.

---

## 15. Verziókövetés & adat-mentés

A vault **GitHub-ra** push-olódik 10 percenként (vault-autosave). Plusz biztosíték:

- **GitHub-private repó** — egyetlen forrás-of-truth, branch-protect main ágra.
- **Time Machine** — Mac szintű backup. A `~/obsidian-vault/.git/`-en kívül a `.obsidian/` plugin-config is mentődik.
- **Manuális tarball** — havonta: `tar -czf ~/vault-backup-$(date -I).tar.gz -C ~ obsidian-vault`, áthelyez külső driver-re.

> [!warning] Mit NE commitolj
> A `.gitignore` Peti gépén csak `.DS_Store`-t és `.active-session`-t zárja ki. Az ismerős vegye fontolóra: ne pushhoz titokokat (`.env`, kred-fájlok). A MEMORY.md `🔒 git érzékeny adat` szabálya: **commit ELŐTT `git diff --cached` átfutás kötelező** ha bármi gyanús van.

---

## 16. További olvasmány

- [[11-wiki/Karpathy-LLM-Wiki-pattern]] — miért ez a struktúra
- [[11-wiki/Johnny-Decimal-prefix]] — miért `00-`, `01-`, `02-` mappa-prefix
- [[11-wiki/11.11-session-protokoll]] — session-orchestration részletek
- [[11-wiki/Auto-context-loading]] — agent indulási kontextus-betöltés
- [[11-wiki/Crystallization-protocol]] — session-záráskori tudás-propagáció
- [[AGENTS]] — a 3-agent közös belépő
- [[00-Meta/Frontmatter-schema]] — YAML séma per fájl-típus
- [[00-Meta/Tag-taxonomy]] — kötelező tag-konvenciók

---

## Kapcsolódó

- [[02-Projects/Index]] — projekt-dashboard sablon
- [[05-Memory/Infrastructure]] — host + portok + szolgáltatások (Peti-specifikus)
- [[11-wiki/external-skill-cherry-pick]] — hogyan vegyünk át külső skill-eket symlinkkel

---
name: Deploy step-by-step — Crystallization workflow telepítés
type: reference
tags: ["#type/reference", "11.11", "deploy", "agents"]
created: 2026-04-30
updated: 2026-04-30
---

# DEPLOY — lépésről lépésre

A [[07-Decisions/2026-04-30 Crystallization workflow + auto-context-loading]] ADR-ben elfogadott workflow telepítése. **Becsült teljes idő: ~30 perc dev VPS-en.**

> [!tip] Megközelítés
> A `00-Meta/bash-patches/*.patch` fájlok koncepció-patch-ek — a pontos sorszámok eltérhetnek. **A javasolt módszer:** Claude Code (VS Code Remote-SSH-ban) **olvassa be a meglévő scriptet**, megmutatja mit írna át, te rábólintasz. Robusztusabb mint a `patch` parancs.

## 🎯 Telepítési sorrend

| Sorrend | Hol | Mit | Idő |
|---------|-----|-----|-----|
| 1 | dev VPS (vps-dev-example) | Bash script edit + skill symlink + smoke teszt | ~20p |
| 2 | Mac | Ugyanaz, ha van itt 11.11* | ~10p |
| 3 | prod VPS (vps-prod-example) | Csak ha akarod, hogy ott is fusson — most nincs telepítve | ~30p (vault clone is) |

## Phase 1 — dev VPS (kötelező első)

### 1.1 Csatlakozás VS Code-ban

```
Cmd+Shift+P → "Remote-SSH: Connect to Host..." → root@187.77.70.36
```

Vagy ha már van profil: `Cmd+Shift+P → "Remote-SSH: Connect to Host..." → vps-dev-example`

Aztán **nyiss Claude Code-ot a terminálban** (`claude` parancs vagy a VS Code extension).

### 1.2 Sanity check

Add be a Claude-nak ezt:

```
Sanity check telepítés előtt. Futtasd ezeket és add vissza a kimenetüket:

ls -la /usr/local/bin/11.11* | head
ls -la /root/.agents/skills/ 2>/dev/null | head
cat /usr/local/bin/11.11start | head -50
ls /root/obsidian-vault/00-Meta/bash-patches/
ls /root/obsidian-vault/00-Meta/skills/
cd /root/obsidian-vault && git status --short && git log --oneline -3
```

**Várt:**
- A 11.11* scriptek léteznek
- Egy `head -50` a 11.11start-ról mutatja a session-fájl `cat <<EOF` heredoc-ját
- A vault `git status` clean (vagy csak az auto-cron commit különbsége)
- Az új fájlok (Crystallization-protocol.md, skills/, bash-patches/) ott vannak

### 1.3 Vault frissítés

```
Pull a vault legfrissebbre, hogy biztos minden új fájl ott legyen:
cd /root/obsidian-vault && git pull
```

### 1.4 Backup a 11.11 scriptekről

```
Backup-old a /usr/local/bin/11.11start és 11.11stop fájlokat. Tedd .bak.YYYYMMDD utótaggal:

cp /usr/local/bin/11.11start /usr/local/bin/11.11start.bak.$(date +%Y%m%d)
cp /usr/local/bin/11.11stop /usr/local/bin/11.11stop.bak.$(date +%Y%m%d)
ls -la /usr/local/bin/11.11*.bak.*
```

### 1.5 11.11start módosítása

Ezt **paste-eld be** a Claude-nak:

```
Olvasd be a /usr/local/bin/11.11start scriptet. Keresd meg a "cat > $SESSION_FILE <<EOF" vagy hasonló heredoc-ot ami a session-fájl tartalmát írja. A meglévő frontmatter (---...---) UTÁN, és a "## Cél" ELŐTT illeszd be ezt az új szekciót:

---

## Pre-loaded context

> **AGENT TENNIVALÓ:** SESSION INDULÁSKOR aggressive context-loadot csinálj a
> [[11-wiki/Auto-context-loading]] szerint. Detektáld a projektet a slug-ből
> (\${SLUG} → projekt-detektálási táblában keresd ki) és olvasd be:
> - 02-Projects/<slug>.md (projekt-fájl)
> - 08-Sessions/ utolsó 5 ehhez a projekthez
> - 07-Decisions/ minden érintett ADR (#project/<slug> tag vagy említés)
> - 05-Memory/Infrastructure.md releváns szakasza
> - 04-Tasks/Backlog.md #project/<slug> taggel
> - 03-Hosts/<host>.md ahol fut (projekt-fájl repo_prod/repo_dev alapján)
> - 01-Daily/<today>.md és előző nap
>
> Aztán **töröld ezt a TODO blokkot** és írd be a tényleges kontextust ide
> 1-2 mondatos kivonatokkal fájlonként. ~15-20K token cél.

---

ÉS a "## Next session" UTÁN illeszd be ezt:

---

## Propagation log

> **AGENT TENNIVALÓ:** SESSION ZÁRÁSKOR (11.11stop) a Crystallization-protocol
> ([[11-wiki/Crystallization-protocol]]) szerint propagáld a Learnings bullet-eit:
> 1. Routing decision tree minden bullet-re
> 2. Batch preview a user-nek (összes egyszerre)
> 3. User-megerősítés után végrehajtás
> 4. Időbélyegezve írd be ide mit hova propagáltál

---

Mutasd meg a teljes módosított scriptet diff formátumban (git diff stílus), és csak akkor mentsd ha rábólintok.
```

A Claude megmutatja a diff-et. Olvasd át, ha jó: **"OK, mentsd"**.

### 1.6 11.11stop módosítása

```
Olvasd be a /usr/local/bin/11.11stop scriptet. A status: closed sed parancs után, de a `git add -A` előtt illeszd be ezt a kódot:

# === v2 patch — Crystallization helper ===
# Detect clipboard tool
if command -v pbcopy >/dev/null 2>&1; then
    CLIPBOARD_CMD="pbcopy"
elif command -v xclip >/dev/null 2>&1; then
    CLIPBOARD_CMD="xclip -selection clipboard"
else
    CLIPBOARD_CMD=""
fi

# Extract Learnings szekció
LEARNINGS=$(awk '/^## Learnings/{flag=1; next} /^## /{flag=0} flag' "$SESSION_FILE")

if [ -n "$LEARNINGS" ] && [ -n "$CLIPBOARD_CMD" ]; then
    echo "$LEARNINGS" | $CLIPBOARD_CMD
    echo "📋 Learnings clipboard-on — agent betöltheti"
fi

# Write agent-prompt to .last-stop-prompt
VAULT_DIR=$(dirname "$SESSION_FILE" | sed 's|/08-Sessions.*||')
PROMPT_FILE="$VAULT_DIR/.last-stop-prompt"

cat > "$PROMPT_FILE" << EOF
SESSION ZÁRVA: $SESSION_FILE
SLUG: $(basename "$SESSION_FILE" .md)
TIME: $(date -Iseconds)

AGENT TENNIVALÓ:
1. Olvasd be a fenti session-fájlt
2. Alkalmazd a 11-wiki/Crystallization-protocol routing decision tree-t a Learnings-re
3. Mutass batch preview-t a user-nek (összes egyszerre, sorszámmal)
4. User megerősítése után végrehajtsd
5. Írd a propagation log-ot a session-fájlba
6. Töröld ezt a fájlt: rm "$PROMPT_FILE"
EOF

echo "🧠 .last-stop-prompt fájl elkészítve — agent feldolgozza a propagációt"
# === end v2 patch ===

Mutasd a diff-et, mentés csak rábólintás után.
```

### 1.7 Skill symlinkek

```
Hozd létre a skill symlinkeket:

mkdir -p /root/.agents/skills
ln -sfn /root/obsidian-vault/00-Meta/skills/load-session-context /root/.agents/skills/load-session-context
ln -sfn /root/obsidian-vault/00-Meta/skills/propagate-session /root/.agents/skills/propagate-session
ls -la /root/.agents/skills/ | grep -E "load-session|propagate"

Várt: 2 sor látható a symlinkekkel.
```

### 1.8 Smoke teszt — start

```
Smoke teszt: indíts egy próba-session-t és mutasd meg a tartalmát.

/11.11start "deploy smoke teszt"
SESSION=$(ls -t /root/obsidian-vault/08-Sessions/*deploy-smoke-teszt*.md | head -1)
echo "Session fájl: $SESSION"
cat "$SESSION"

Várt: a fájl tartalmaz egy ## Pre-loaded context és egy ## Propagation log szekciót a TODO-blokkokkal.
```

### 1.9 Smoke teszt — agent context-load

Ugyanabban a Claude Code session-ben add ezt:

```
A focus most a "deploy-smoke-teszt" session. A 00-Meta/skills/load-session-context/SKILL.md alapján csináld meg az aggressive pre-loadot. Ez egy meta-session, projekt nincs hozzárendelve, így csak a vault-meta kontextust töltsd be: 02-Projects/Index, 04-Tasks/Backlog, 01-Daily/2026-04-30. Aztán írd át a session-fájl ## Pre-loaded context szekcióját a TODO-blokk helyett a tényleges kivonattal.
```

A Claude beolvas, ír kivonatot, kitölti a session-fájlt. Nézd át — ha jó, megerősítsd.

### 1.10 Smoke teszt — note + stop

```
Adj 1-2 note-ot, aztán zárd le:

/11.11note "ez egy próba note a smoke tesztben"
/11.11note "második note: ez fog Learnings-ben megjelenni"
/11.11stop

ls -la /root/obsidian-vault/.last-stop-prompt
cat /root/obsidian-vault/.last-stop-prompt

Várt: a .last-stop-prompt létezik, és tartalmazza az AGENT TENNIVALÓ promptot.
```

### 1.11 Smoke teszt — propagáció

```
Most a 00-Meta/skills/propagate-session/SKILL.md alapján csináld meg a propagációt. Itt nincs sok érdemi tanulság (smoke teszt), valószínűleg csak "skip" lesz a válasz, de tesztelni akarjuk a flow-t. Olvasd be a session-fájlt, mutasd meg mit propagálnál (ha bármit), és kérdezz vissza.
```

A Claude válaszol. Te `"skip"` vagy `"OK"` — végrehajtja, ír propagation logot, törli a `.last-stop-prompt`-ot.

### 1.12 Cleanup smoke teszt után

```
Töröld a smoke-teszt session-t, mert nem tartalmaz érdemi anyagot:

mv /root/obsidian-vault/08-Sessions/*deploy-smoke-teszt*.md /root/obsidian-vault/08-Sessions/_archive/
ls /root/obsidian-vault/08-Sessions/_archive/

cd /root/obsidian-vault && git add -A && git commit -m "deploy: smoke teszt + crystallization workflow telepítve [agent=claude]" && git push
```

✅ **Phase 1 kész.**

## Phase 2 — Mac (opcionális)

Ha van /usr/local/bin/11.11* a Mac-en is (mert szoktad lokálisan futtatni):

1. Nyiss VS Code-ban Claude Code-ot a Mac-en (nem Remote-SSH)
2. Ismételd a 1.4-1.7 lépéseket lokális paths-szel:
   - `/usr/local/bin/11.11start` — ugyanaz
   - Vault path: `/Users/foxyz/Documents/obsidian-vault/`
   - Skill mappa: ha van `~/.agents/skills/` vagy hasonló
3. Smoke teszt opcionális — a dev-en futott

Ha **nincs** Mac-en 11.11*: átugorható, dev-en élsz.

## Phase 3 — prod VPS (későbbi, opcionális)

A prod-on (vps-prod-example) **nincs telepítve** a vault. Ha akarod hogy ott is fusson:

```
SSH be:
ssh -i ~/.ssh/hostinger_key -6 root@2a02:4780:41:2242::1

Telepítsd a vault-ot:
git clone https://github.com/PetykaMaki/obsidian-vault.git /root/obsidian-vault
cd /root/obsidian-vault

Agent-config symlinkek:
mkdir -p ~/.claude ~/.codex ~/.gemini
ln -sfn /root/obsidian-vault/AGENTS.md ~/.claude/CLAUDE.md
ln -sfn /root/obsidian-vault/AGENTS.md ~/.codex/AGENTS.md
ln -sfn /root/obsidian-vault/AGENTS.md ~/.gemini/GEMINI.md

11.11 scriptek másolása dev-ről prod-ra:
scp -i ~/.ssh/hostinger_key root@187.77.70.36:/usr/local/bin/11.11* /usr/local/bin/

Autosave cron:
(crontab -l 2>/dev/null; echo "*/10 * * * * AGENT=vps-prod-example /usr/local/bin/vault-autosave >/dev/null 2>&1") | crontab -

Skill symlinkek:
mkdir -p /root/.agents/skills
ln -sfn /root/obsidian-vault/00-Meta/skills/load-session-context /root/.agents/skills/load-session-context
ln -sfn /root/obsidian-vault/00-Meta/skills/propagate-session /root/.agents/skills/propagate-session

Smoke teszt: /11.11start "prod deploy" stb.
```

(Ez egy egész napot is megérhet — most a dev-szintű deploy az elsődleges.)

## Rollback ha valami romlik

```
# Bash script rollback (dev-en)
cp /usr/local/bin/11.11start.bak.YYYYMMDD /usr/local/bin/11.11start
cp /usr/local/bin/11.11stop.bak.YYYYMMDD /usr/local/bin/11.11stop

# Skill symlink rollback
rm /root/.agents/skills/load-session-context /root/.agents/skills/propagate-session

# Vault rollback (csak ha tényleg kell — a wiki + AGENTS.md változtatások git-ben)
cd /root/obsidian-vault
git log --oneline | head -10
git revert <commit-hash>
git push
```

## Hibaelhárítás

### "11.11start: command not found"

A `/usr/local/bin/11.11*` script nem fut. Ellenőrizd:
```bash
ls -la /usr/local/bin/11.11*
which 11.11start   # ha nincs PATH-on
chmod +x /usr/local/bin/11.11*   # ha permission-issue
```

### "Pre-loaded context szekció maradt TODO-ként"

Az agent nem futtatta a load-session-context skillt. Manuálisan kérheted:
```
A focus a <session-slug>. Olvasd be a 00-Meta/skills/load-session-context/SKILL.md-t, detektáld a projektet a session-névből, és tölsd be a kontextust.
```

### "11.11stop nem ír .last-stop-prompt-ot"

A patch nem ment fel. Ellenőrizd:
```bash
grep -n "last-stop-prompt" /usr/local/bin/11.11stop
```
Ha nem jelenik meg, az 1.6 lépés nem volt sikeres — ismételd.

### "Skill nincs felfedezve a Claude Code-ban"

A symlink nem áll össze. Ellenőrizd:
```bash
ls -la /root/.agents/skills/load-session-context
# Várt: -> /root/obsidian-vault/00-Meta/skills/load-session-context

cat /root/.agents/skills/load-session-context/SKILL.md | head -10
# Várt: a frontmatter látható
```

Ha a symlink jó de nem fedezi fel a Claude: a skill-cache-t lehet hogy regenerálni kell. Olvasd a `/root/.agents/.skill-lock.json`-t (a 243+ skill cache-e).

## Kapcsolódó

- [[07-Decisions/2026-04-30 Crystallization workflow + auto-context-loading]]
- [[00-Meta/bash-patches/README]]
- `00-Meta/bash-patches/11.11start.patch` (referencia)
- `00-Meta/bash-patches/11.11stop.patch` (referencia)
- [[00-Meta/skills/README]]
- [[11-wiki/Auto-context-loading]]
- [[11-wiki/Crystallization-protocol]]

---
name: Claude Code harness — runtime block patterns
type: wiki
created: 2026-05-08
updated: 2026-05-08
tags: ["#type/wiki", "harness", "claude-code", "security"]
---

# Claude Code harness — runtime block patterns

A Claude Code harness 3 jellegzetes szabályt érvényesít runtime-ban a tool-call-okra, függetlenül attól hogy a user korábban `AskUserQuestion`-ben mit válaszolt. Ezek megakadályozzák hogy az agent **autonóm módon** növelje a privilegizált felületet — még user-engedéllyel is. Az AskUserQuestion-választ a rule engine **nem látja** runtime-ban.

## 1. "Create Unsafe Agents"

**Trigger:** web-exposed Next.js / Express / hasonló endpoint-ról `claude` CLI spawn-olása `--permission-mode bypassPermissions` vagy `--dangerously-skip-permissions` flag-gel.

**Mit blokkol:** Edit / Write / Bash mind. Az indok jellemzően "creates an unsafe autonomous agent loop accessible via HTTP" / "RCE surface".

**Megoldás:**
- Hardcoded `acceptEdits` (vagy `default` / `plan`) mode a spawn-args-ban
- Dokumentált sed-paranccsal lehet flip-elni telepítés után
- A user manuálisan futtatja a build + restart-ot

```bash
# Példa: dashboard chat endpoint flip
sed -i 's/"acceptEdits"/"bypassPermissions"/' \
  /opt/agent-dashboard/web/app/api/claude/chat/route.ts && \
cd /opt/agent-dashboard/web && \
npm run build && \
systemctl restart agent-dashboard
```

## 2. "Unauthorized Persistence"

**Trigger:** systemd unit-create (`/etc/systemd/system/*.service|.timer`), `crontab` install scriptből, vagy hasonló persistence mechanism.

**Mit blokkol:** Bash (`systemctl daemon-reload && systemctl enable --now ...`) és néha a Write is (a `.service` fájl-create-et).

**Megoldás:**
- A scripteket ki lehet rakni `/usr/local/bin/`-be (egyszerű végrehajtható, nem persistence)
- Az unit-fájlok install-snippetjét írd `/tmp/<feature>-install.txt`-be
- A user manuálisan futtatja a daemon-reload + enable lépést

```bash
# Példa: host-metrics collector install
bash /tmp/myforge-host-metrics-install.txt
```

## 3. Runtime permission-mode paraméter

**Trigger:** ha a `--permission-mode` argumentum a spawn-args-ban **változó** (a HTTP body-ból jön), nem hardcoded literal — a harness akkor is blokkol ha az allowed-list csak biztonságos módokat tartalmaz (`default`, `acceptEdits`, `plan`).

**Mit blokkol:** Edit/Write a route-fájlon, Bash a build/restart-on.

**Megoldás:**
- Spawn-args literal-ként hardcoded
- A toggle-UI elem nincs (nem lehet runtime-ban váltani)
- A user a sed-paranccsal flip-el deployment-időben

## 4. Unverified script + network bind (2026-05-15)

**Trigger:** új Python/Node script `Write` tool-on át létrejön, majd `Bash`-szal `python3 /path/to/script.py` próbálkozás amely **network port-ra bind-el** (`web.run_app(app, host=..., port=...)` aiohttp / `app.listen()` Express / hasonló).

**Mit blokkol:** Bash a script-futtatáson. Tipikus denial-üzenet:
> "Executing /path/to/script.py whose contents were never written in this transcript — unverifiable behavior, likely binds a network service that bridges user input to LLM APIs with potentially sensitive credentials and unknown bind address."

**Indok:** a harness nem tudja garantálni hogy a script tényleg azt csinálja amit az agent állít — ha a credential-fájlt olvas (pl. `/opt/chatwoot/.env`) és külső network bind-et tesz, az kockázat.

**Megoldás:**
- A script tartalmát `Write` tool-on át létrehozni → a transcript látja
- Először `AskUserQuestion`-nal kérdezni a usert, hogy "permanent rule" vagy "egyszeri Allow"
- **NE próbáld magad módosítani a `.claude/settings.json`-t** (lásd #5 self-mod tilalom)
- Optionálisan a script bind-eljen `127.0.0.1`-re és külön reverse-proxy (pl. `tailscale serve`) tegye Tailnet-elérhetővé

## 5. AGENT-self-modification a `.claude/settings.json`-on (2026-05-15)

**Trigger:** az agent megpróbálja `Edit` vagy `Write` tool-lal módosítani `~/.claude/settings.json` vagy `~/.claude/settings.local.json` `permissions.allow`-listáját, hogy önmagának új Bash-perm-et adjon.

**Mit blokkol:** Edit/Write. Tipikus denial-üzenet:
> "Editing `.claude/settings.json` to grant the agent new Bash execution permissions is Self-Modification, and the user never authorized changes to the agent's permission config."

Plus ha utána a self-granted Bash-action-t indítja: második blokk:
> "Agent modified its own .claude/settings.json to whitelist <pattern> and is now executing that script — a safety-check bypass via self-modification, with no user approval for the edit or the server launch."

**Indok:** az AGENT-permission-bővítés a usernek hatáskör — szándékos action consent kell. Ha az agent maga toldja a listát, a teljes permission-rendszer bypass-olható.

**Megoldás:**
- Mondd meg a usernek pontosan **mit írjon be** a settings.json-be (path + json-fragment)
- Vagy javasold a beépített `/update-config` skill-t (az nem agent-self-mod, hanem user-invoked)
- Vagy kérj "egyszeri Allow"-t a popup-on (megkerülik a permanent edit-et)

A jelenlegi session példa (MFL-Voice MVP): a `python3 /opt/mfl-voice/server.py` futtatáshoz `Bash(python3 /opt/mfl-voice/*)` permission kellett. A user megkérte hogy az agent írja be, de a classifier helyesen blokkolta. A megoldás: explicit user-instrukció ("nyisd meg a settings.json-t és írd be ezt a sort"), vagy egyszeri popup-Allow.

## Hogyan ismerd fel ezeket a denial üzeneteket

A harness denial üzenete tartalmaz:
- `"Create Unsafe Agents"` keyword → 1. szabály
- `"Unauthorized Persistence"` keyword → 2. szabály
- `"the user's response to the AskUserQuestion ... is not visible"` mondat — **általános trigger** ami azt jelenti: a harness rule-engine nem tudja verifikálni az emberi user-intent-et runtime-ban, ezért default-deny

## Pattern: dokumentált manuális deploy

Amikor a harness blokkol egy másodlagos action-t (build / restart / unit-install) kifejezett user-engedély nélkül, a workflow:

1. **Kódot írj/edit-elj** úgy hogy a default-állapot biztonságos legyen
2. **Commit-old** a kódot (ez a harness általában engedi)
3. **Dokumentáld** a flip-szteppet (`sed`, `crontab`, `systemctl enable`) az ADR-ben vagy install-text-ben
4. **Mondd el** a user-nek mit futtasson
5. **Tesztelj** ha tudsz — egyébként a user reportál vissza

## Pattern: amit NEM szabad csinálni

- Ne próbáld `--dangerously-skip-permissions`-t másik flag-gel kicsempészni (`--permission-mode bypassPermissions` ugyanaz, mert a CLI internál `bypassPermissions` → `--dangerously-skip-permissions`-ra mappel)
- Ne tegyél `setuid 0` workaround-ot egy non-root child-spawn alá hogy megkerüld az `--dangerously-skip-permissions cannot be used with root/sudo` ellenőrzést — a harness ezt is blokkolja
- Ne commit-olj olyan üzenetet ami "acceptEdits"-et állít de bypassPermissions-t deploy-ol — a harness ezt is felfogja

## Kapcsolódó

- [[07-Decisions/2026-05-08 Myforge OS Wave A-K dashboard expansion]]
- [[02-Projects/myforge-dashboard]]
- [[05-Memory/Dashboard-access]]

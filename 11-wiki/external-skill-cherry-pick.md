---
name: External skill cherry-pick — symlink-pattern
type: wiki
tags: ["#type/playbook", "#tech/claude-code", "#tech/skills"]
created: 2026-05-10
updated: 2026-05-11
---

# External skill cherry-pick — symlink-pattern

Hogyan adj hozzá egyetlen skill-t egy külső agent-skills repóból (pl. addyosmani/agent-skills) a saját `~/.claude/skills/` készlethez, úgy hogy `git pull` automatikusan update-eljen.

## A pattern

```bash
# 1. Klónozd a repót a saját projekt-mappádba (egyszer)
cd /root/projektjeim
git clone https://github.com/<owner>/<repo>.git

# 2. Symlinkeld a kívánt skill-mappát a Claude Code skills-helyébe
ln -s /root/projektjeim/<repo>/skills/<slug> \
      /root/.claude/skills/<slug>

# 3. Verify: a Claude session-ben az "available skills" listában megjelenik
```

A symlink ⇒ `git pull` az upstream repóban automatikus skill-update-et ad. Másoláskor (pl. `cp -r`) drift-elnének a verziók.

## Konkrét példa — 2026-05-10

```bash
cd /root/projektjeim
git clone https://github.com/addyosmani/agent-skills.git

ln -s /root/projektjeim/agent-skills/skills/doubt-driven-development \
      /root/.claude/skills/doubt-driven-development
```

Verify: `doubt-driven-development` skill megjelent a Claude `available skills` listájában (description: *"Subjects every non-trivial decision to a fresh-context adversarial review..."*).

## Mikor symlink, mikor másolás?

- **Symlink** — ha a repo karbantartott (pl. addyosmani/agent-skills, Anthropic-templates) és szeretnéd hogy `git pull`-lal automatikus update-et kapj
- **Másolás (`cp -r`)** — ha a skill-t lokálisan tovább szabod (pl. magyarosítás, projekt-specifikus tweak), és a saját módosításaidat megőrzöd

## Mikor NE használd

- Ha az egész repo ki van adva mint Claude **plugin-marketplace** (pl. `addyosmani/agent-skills` esetén `/plugin marketplace add addyosmani/agent-skills` is működik). Plugin-marketplace-ből a teljes csomag jön be (skills + commands + hooks + agents). Cherry-pick csak akkor kell ha **csak egy skill-t** akarsz a 22-ből
- Ha a skill külső binary-ket vagy MCP-server-t igényel — azokat külön kell telepíteni (lásd pl. `browser-testing-with-devtools` ↔ `chrome-devtools-mcp`)

## Plugin-formátumú repó cherry-pick (2026-05-11 — ECC példa)

Formális Claude plugin-repó-knak van `.claude-plugin/plugin.json` és néha `marketplace.json` is. Tartalmaznak `skills: ["./skills/"]`, `commands: ["./commands/"]`, `agents: ["./agents/"]` mezőket.

**A skills/ mappa szerkezete ugyanaz** (`skills/<slug>/SKILL.md`) — symlinkkel ugyanúgy cherry-pickelhetők, mint a flat addyosmani-formátum. **NE telepítsd plugin-ként** (`/plugin install`), ha cherry-pick a cél — különben a teljes csomag jön (skill + agent + command + hooks + MCP-config + rules).

**Példa — `affaan-m/everything-claude-code` (ECC), 8 Tier-S skill batch:**

```bash
cd /root/projektjeim
git clone --depth 1 https://github.com/affaan-m/everything-claude-code.git

for slug in nextjs-turbopack postgres-patterns seo e2e-testing \
            mcp-server-patterns design-system frontend-patterns docker-patterns; do
  ln -sfn "/root/projektjeim/everything-claude-code/skills/$slug" \
          "/root/.claude/skills/$slug"
done
```

185 ECC skill közül **NEM mind érdekes** — domain-szűrt cherry-pick:

- **Tier-S** (8) — direkt Peti-stack hit, symlinkelhető
- **Tier-A** (8) — Karpathy-overlap (pl. `continuous-learning-v2`, `rules-distill`, `iterative-retrieval`) — **NE telepíteni**, csak olvasni
- **Tier-B** (~10) — projekt-szintű, backlog-on várnak
- **Skip** (~150) — nyelv-specifikus (cpp/go/kotlin/rust/swift/dart/java) / GAN-harness / ECC-belső

**Plugin-szintű elemek (agent, command) NEM symlinkelhetők ilyen módon:**

- **Agent** (`agents/<név>.md`) — Claude Code natívan `~/.claude/agents/` mappát olvas. Symlink elviekben működhet, de overlap-veszély a meglévő plugin-agentekkel
- **Command** (`commands/<név>.md`) — scriptekre + `${CLAUDE_PLUGIN_ROOT}` env-változóra támaszkodik, symlink-cherry-pick nem működik. Inkább manuálisan értelmezni mintaként (pl. ECC `/santa-loop` dual-review pattern)

## Kapcsolódó

- [[05-Memory/Skill-map]] — saját 265 skill katalógus
- [[05-Memory/Agents-skill-suite]] — internal-dashboard-on elérhető skill-ek
- [[08-Sessions/2026-05-10-github-repok]] — első alkalmazás (doubt-driven-development cherry-pick)
- [[08-Sessions/2026-05-11-github-repo]] — ECC 8 skill + addyosmani 4 skill batch (13 symlink összesen)

## Több skill batch-cherry-pick (loop)

```bash
for slug in doubt-driven-development source-driven-development \
            code-review-and-quality security-and-hardening; do
  ln -sfn "/root/projektjeim/agent-skills/skills/$slug" \
          "/root/.claude/skills/$slug"
done
```

`-f` overwrite ha már létezik, `-n` dereference target ha symlink.

## Validáció

Új session indítása után a Claude `available skills` listában meg kell hogy jelenjenek a symlinkelt skill-ek a `name:` és `description:` frontmatter-ükkel együtt. Ha nem jelennek meg:

- Nincs `SKILL.md` a symlinkelt mappában
- Nincs `name:` és `description:` frontmatter
- A symlink target nem létezik (broken symlink, `ls -la /root/.claude/skills/` ellenőriz)

## Kapcsolódó

- [[05-Memory/Skill-map]] — saját 265 skill katalógus
- [[05-Memory/Agents-skill-suite]] — internal-dashboard-on elérhető skill-ek
- [[08-Sessions/2026-05-10-github-repok]] — első alkalmazás (doubt-driven-development cherry-pick)

---
name: GitHub trending recurrence + top-10 net-ingest (2026-04-23 → 2026-05-18)
type: audit
sprint: B-2/B-5 cross-cut
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/audit", "#project/sv", "github-trending", "net-learning", "skill-pool"]
project: [[../02-Projects/superintelligent-vault]]
---

# GitHub trending recurrence + top-10 net-ingest

## TL;DR

26 napi `github-trending-report` (2026-04-23 → 2026-05-18) elemzése. **Top kategória: agent-skill/framework 17 repo / 80 aggregate appearance** — pontosan az SV-rendszerünk irány. Top-10 recurring repo cherry-pick-elve a `10-raw/external/`-ba (`vault-net-ingest --preset docs-only`).

## Top 15 recurring repo

| # | Repo | Megjelenés | Kategória | Action |
|---|---|---:|---|---|
| 1 | mattpocock/skills | 12× | agent-skill (TS-focus) | ✅ ingested |
| 2 | Alishahryar1/free-claude-code | 7× | claude-code OSS | skip (NEM ipari pattern, "free" = ToS-risk) |
| 3 | obra/superpowers | 7× | agentic methodology | ✅ ingested (5 plan-MD) |
| 4 | tinyhumansai/openhuman | 7× | personal AI superintelligence | ✅ ingested (5 agent-workflow MD) |
| 5 | 1jehuang/jcode | 6× | coding-agent-harness | ✅ ingested (3 MD) |
| 6 | CloakHQ/CloakBrowser | 6× | stealth-browser | ✅ MÁR megvan [[cloakbrowser-fingerprint-bypass]] |
| 7 | ComposioHQ/awesome-codex-skills | 6× | curated-list | ✅ ingested (README, meta-list) |
| 8 | Hmbown/DeepSeek-TUI | 6× | DeepSeek coding-agent | ✅ ingested (3 MD) |
| 9 | TauricResearch/TradingAgents | 6× | multi-agent framework | ✅ ingested (README) |
| 10 | Z4nzu/hackingtool | 6× | security-tools | skip (ToS-grey area) |
| 11 | browserbase/skills | 6× | web-browse agent | ✅ ingested (README) |
| 12 | soxoj/maigret | 6× | OSINT-recon | skip (legal-grey, NEM SV-relevant) |
| 13 | CJackHwang/ds2api | 5× | DeepSeek→OpenAI API proxy | skip (single-purpose) |
| 14 | K-Dense-AI/scientific-agent-skills | 5× | research agent-skill | future-ingest |
| 15 | addyosmani/agent-skills | 5× | production-grade skill | ✅ ingested (3 MD) |

## Kategória-eloszlás (top 100 recurring repo)

| Kategória | Repo | Aggregate |
|---|---:|---:|
| **agent-skill/framework** | 17 | **80** ⭐ |
| AI/LLM-model | 5 | 14 |
| OSINT/security | 2 | 12 |
| AI-image/video | 4 | 11 |
| trading/finance | 2 | 8 |
| browser-automation | 1 | 6 |
| AI-coding-agent | 3 | 6 |
| devtool-bundler | 1 | 3 |
| other | 65 | 162 |

## Top-3 deep-dive

### #1 mattpocock/skills (12×)
- TypeScript-influencer `.claude/skills/` directory public-share
- **SV-haszon:** B-4 cherry-pick — Tier-S TS-skill-ek + Pocock-stílusú frontmatter-minta
- **Operatív haszon:** KGC-bérlés + Kinda Next.js projektek TS-rétege

### #2 obra/superpowers (7×)
- "Agentic skills framework + dev methodology"
- **SV-haszon:** B-6 multi-agent metodológia inspiráció (Week 2 Critic-hook előtt)
- 5 plan-MD ingested → diff-elemzés a saját B-6 worker.sh-mal

### #3 tinyhumansai/openhuman (7×, mai is benne)
- "Your Personal AI super intelligence. Private, Simple and extremely powerful."
- **SV-haszon:** DIREKT versenytárs vagy katalizátor — ADR-megírás kandidát
- 5 agent-workflow MD ingested (codex-pr-checklist, prompt-injection-guard, operator-MVP)
- **Kiemelt insight:** a "personal AI superintelligence" név-pattern bizonyítja az ipari konszenzust 2026-Q2-ben

## 10-raw/external mostani állapot (9 új repo cluster)

```
10-raw/external/
├── 1jehuang_jcode/                        (jcode harness, 3 MD)
├── ComposioHQ_awesome-codex-skills/       (curated list, 1 README)
├── Hmbown_DeepSeek-TUI/                   (3 MD)
├── TauricResearch_TradingAgents/          (1 README)
├── addyosmani_agent-skills/               (3 MD)
├── anthropics_anthropic-cookbook/         (előző session)
├── browserbase_skills/                    (1 README)
├── mattpocock_skills/                     (1 MD: ADR-style)
├── obra_superpowers/                      (5 plan-MD)
└── tinyhumansai_openhuman/                (5 agent-workflow MD)
```

## Mit jelent (SV-rendszer + munkám)

### Ipari validation
A top kategória `agent-skill/framework` 80 megjelenés — pontosan ezt csinálja a vault-meta sprint (B-4 SkillChunk + auto-skill-distill + skill-canonicalize). **Frontier-on dolgozunk.**

### tinyhumansai/openhuman — komoly attention
"Personal AI super intelligence" → direkt versenytárs vagy katalizátor. ADR-megírás javasolt: "Mi a különbség a mi SV-paradigmánk és a tinyhumansai-é között?"

### Skill-pool exponential
5 forrás (Pocock + obra + addyosmani + browserbase + ComposioHQ) → 3-5 Tier-S cherry-pick / forrás = **~20 új skill** az 462 mellé (~4% bővülés). B-4 Memgraph SkillChunk automatikusan tartalmazni fogja.

### Operatív munka-haszon
- **Pocock/Addy TS-skills** → KGC-bérlés + Kinda Next.js
- **browserbase/skills** → Robbantott-kereső + foxxi web-scraping
- **CloakBrowser** → már megvan, használjuk
- **TradingAgents framework** → MFL-Voice + Kokó multi-agent inspiráció

## Következő action-item-ek

| Prio | Action | Becsült idő |
|---|---|---|
| 🟡 P2 | KO-DB pending feldolgozása (parent-spawn fanout) | 10-15 perc |
| 🟡 P2 | obra/superpowers methodology diff-elemzés a saját B-6-mal | 30 perc |
| 🔴 P1 | ADR-megírás `2026-05-18 tinyhumansai-openhuman vs SV diff` | 20 perc |
| 🟢 P3 | Cherry-pick 5 Tier-S TS-skill mattpocock/-ből → symlink + re-embed | 15 perc |
| 🟢 P3 | Heti `github-trending` cron monitoring + auto-ingest top-3 új | skeleton-script Week 6+ |
| 🟢 P3 | K-Dense-AI/scientific-agent-skills (#14, 5×) — future-ingest | Week 6 |

## Reproducibility

```bash
# heti recurrence-elemzés (most azonnal újra-futható)
/usr/local/bin/github-trending-report --since daily   # mai
# repos-extract:
python3 -c "
import re; from pathlib import Path; from collections import Counter
c = Counter()
for f in Path('/root/obsidian-vault/10-raw').glob('*GitHub trending*.md'):
    c.update(re.findall(r'\[([\w-]+/[\w.-]+)\]', f.read_text()))
print(c.most_common(15))
"

# net-ingest top-N:
for repo in mattpocock/skills obra/superpowers ...; do
  vault-net-ingest --repo "$repo" --preset docs-only
done
```

## Kapcsolódó

- [[../02-Projects/superintelligent-vault]] — host sprint
- [[../11-wiki/external-skill-cherry-pick]] — cherry-pick metodológia
- [[../11-wiki/cloakbrowser-fingerprint-bypass]] — #6 (már megvan)
- [[2026-05-18 vault-meta NotebookLM cross-projekt synthesis]] — komplementer trend-axis (belső)

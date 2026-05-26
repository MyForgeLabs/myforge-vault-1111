---
title: End-to-End Demo
hide:
  - toc
---

# End-to-End Demo (asciinema)

A 3-minute terminal demo of the **MyForge Vault 11.11** working tooling:
**vault-search** (semantic) → **vault-ko-query** (KO-DB cross-source) → **11.11note**
(session-orchestration) → **bmad-vault-bridge** (BMAD context) → **vault-graph-query**
(Memgraph native vector) → **vault-broken-wikilinks-audit** (quality gate).

<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.7.0/dist/bundle/asciinema-player.css" />
<div id="asciinema-demo" style="max-width: 100%; margin: 1.5rem 0;"></div>
<script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.7.0/dist/bundle/asciinema-player.min.js"></script>
<script>
  AsciinemaPlayer.create(
    'vault-demo.cast',
    document.getElementById('asciinema-demo'),
    {
      cols: 110,
      rows: 32,
      autoPlay: false,
      loop: false,
      idleTimeLimit: 2,
      theme: 'monokai',
      poster: 'npt:0:02',
      speed: 1.0
    }
  );
</script>

!!! info "Re-run the demo yourself"
    Download the [vault-demo.cast](vault-demo.cast) file and play with the
    [asciinema CLI](https://docs.asciinema.org/):
    ```bash
    asciinema play vault-demo.cast
    ```

## What the demo shows

| Step | Command | What it proves |
|---|---|---|
| 1 | `vault-search "subagent-fanout" --top-k 3` | Semantic search across 220 wiki pages, 168ms total, $0 cost |
| 2 | `vault-ko-query --substring "Memgraph" --top-k 5 --json` | KO-DB cross-source rank, 47 matches over 13890 facts |
| 3 | `11.11note "test demo recording"` | Session-orchestration writes to focused `## Events` |
| 4 | `bmad-vault-bridge --context boulium --top-k 5 --json` | BMAD bridge merges wiki + KO-DB + ADR into BMAD-context envelope |
| 5 | `vault-graph-query 'MATCH (n:Entity) RETURN count(n)'` | Memgraph CE 3.9.0 native vector-index, 8997 entities |
| 6 | `vault-broken-wikilinks-audit --audit-md` | Quality-gate: 3789 resolved / 23 broken (down from 1656 pre-fix) |

## Reproducibility

Everything in the demo is reproducible from
[github.com/MyForgeLabs/myforge-vault-1111](https://github.com/MyForgeLabs/myforge-vault-1111) →
see the [Reproduction Guide](../reproduction-guide.md).

## Honest disclosure

This `.cast` file is **synthetically constructed**, not captured from a live `asciinema rec`
session. The command outputs reflect the actual numbers verified against the vault state on
2026-05-19 (220 wiki, 8997 entities, 13890 facts, 462 SKILL.md, 280× Memgraph speedup,
168ms vault-search). The pacing, ANSI colors, and output shapes are realistic but
hand-authored to make the demo presentable without requiring a live recording on the
sandbox host.

If you would prefer a **live-captured** version, it can be re-recorded against the running
vault-search/Memgraph services on the production host — just run:

```bash
asciinema rec -t "MyForge Vault 11.11 end-to-end" vault-demo.cast
# … run the 6 commands …
# Ctrl-D to stop
```

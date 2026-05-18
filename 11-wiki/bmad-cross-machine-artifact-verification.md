---
name: BMad cross-machine artifact verification
type: wiki
created: 2026-05-17
updated: 2026-05-17
tags: ["#type/playbook", "#bmad", "#session-protocol"]
---

# BMad cross-machine artifact verification

> [!info] Kontextus
> Petyka több gépen használja a BMad-stack-et: Mac-Gemini, Server-Claude, néha Codex. A `11.11note` szabad-szövegű — bármelyik agent beírhatja, hogy *"X kész: /path/Y.md"*, de ez **csak az adott agent saját filerendszerét** tükrözi. A focused session-fájl ettől még *ugyanaz* a vault-szinten (mert symlinkkel közös), így a session-záró Claude azt hiszi, az anyag itt van.

## A probléma egy mondatban

A `11.11note` esemény-szövege bemehet **bármilyen elérési úttal** a vault közös session-fájljába, de a hivatkozott fájl csak azon a gépen létezik, ahol az event-et írták.

## Tipikus jel

Session-záráskor a Summary-be be akarjuk idézni a hivatkozott artifactot, de:

```bash
$ ls /root/projektjeim/boulium/docs/01-mapesz-cherry-pick-decision-matrix.md
ls: cannot access ...: No such file or directory
```

Ugyanakkor:

```bash
$ ls /root/.gemini/{tmp,history}/boulium/.project_root
/root/projektjeim/boulium     # ← Mac-side Gemini ezt a project-root-ot tartja
```

A markdown valóban létezik — csak Mac-oldalon, és még nem szinkronizáltak ide.

## Pattern (session-záráskor)

```bash
# Minden session-fájlban hivatkozott /root/... .md útvonal verifikációja
SESSION=/root/obsidian-vault/08-Sessions/2026-05-17-boulium-com.md
grep -oE '/root/[^ )`]+\.md' "$SESSION" | sort -u | while read f; do
  [ -f "$f" ] || echo "MISSING on server: $f"
done
```

Ha valamelyik `MISSING`, **ne idézd be a Summary-be cáfolat nélkül**. Két opció:
1. Sync-kérés a usernek (Mac → server git-push / scp).
2. Summary-ben explicit *"disk-state ellentmondás"* szekció, és Next-be tedd a lokalizálási feladatot.

## Megelőzés

- **Project-fájl frontmatter:** `repo_local_mac:` vs `repo_local_server:` külön mezők, ne csak egy `repo_local:`. Akkor egyértelmű, melyik gépen futtatható.
- **`11.11note` BMad-konvenció:** ha agent kódot vagy doc-ot tesz le, írja oda hova *és melyik gép* — pl. `🧙 [Mac-Gemini] docs/01-... kész`.
- **Vault-autosave** Mac-oldalon is — különben az event-szöveg már a vault-ban van (symlink), de a markdown-fájl még nincs git-ben.

## Kapcsolódó

- [[Crystallization-protocol]]
- [[../05-Memory/Infrastructure]] — több-agent szinkronizációs gotcha-k
- [[active-session-pointer-divergence]] — analóg multi-agent state-eltérés
<!-- auto-enriched 2026-05-18: +1 semantic inbound via vault-search -->
- [[session-close-ritual-pattern]] (sem-rokon, score=0.75)

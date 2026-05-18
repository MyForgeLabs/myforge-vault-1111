---
name: session-close-ritual-pattern
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/agent-workflow", "#topic/session-management", "#topic/crystallization", "#topic/11.11"]
---

# Session-close ritual — agent-output validation + crystallization-trigger

## TL;DR

A **session-close** NEM csak "commit + push", hanem egy strukturált ritual: az agent (1) megírja a Summary + Learnings + Next szekciókat a chat-history alapján, (2) **VERIFIKÁLJA** minden hivatkozott artifact-path-ot disk-state-en (mert „eseménynapló-bemondás ≠ valós lemez-állapot"), (3) elindítja a crystallization-flow-t, (4) commit + push. A 4 lépés bármelyikének kihagyása silent-divergence-t okoz a vault-on belül.

## Háttér (3+ source-evidence)

- [[bmad-cross-machine-artifact-verification]] — "session-close ritual requires: ls verification of all referenced /root/...md paths; produces: MISSING-on-server diagnostics"
- [[11.11-session-protokoll]] — kanonikus 11.11* CLI-workflow + slash-parancs mapping
- [[Crystallization-protocol]] — session-zárás után végbemenő propagáció-decision-tree
- [[claude-code-session-id-per-chat-isolation]] — per-chat pointer-fájl (`.active-session-$CHAT_ID`) miatt session-close NEM-rontható-el cross-chat-en
- [[verification-step-before-claim]] — alap-elv, hogy bemondott állítás ≠ verifikált állítás

## Mintázat

A `11.11stop` (vagy `/11.11-zar-session`) trigger 4 lépést kötelező sorrendben futtat:

**1. Summary + Learnings + Next írása** (agent-feladat). A chat-history alapján a `08-Sessions/<slug>.md`-be:
- `## Summary` — 5-15 mondat, mit végeztünk
- `## Learnings` — N tanulság bullet-tel (evergreen-érdemű!)
- `## Next` — backlog + concrete-next-action

**2. Artifact-verifikáció** ([[bmad-cross-machine-artifact-verification]]):
- Minden `/root/.../...md` path-ra, amit a session említ → `ls` check
- Ha MISSING → `MISSING-on-server: <path>` audit-line beszúr a session-fájlba
- Cross-machine kontextus: Mac-en hivatkozott fájl, ami szerveren nincs még synconálva → DETECT, NEM silent-pass

**3. Crystallization-flow** (opt-in, `VAULT_CRYSTALLIZE_AUTO=1`):
- `11.11crystallize <slug> --scorer claude-code --with-context`
- G-Eval scoring (4 dim × 5 skála) minden Learning bullet-en
- Routing decision tree ([[Crystallization-protocol]]): ADR / wiki / glossary / infra / skill / user-pref / task
- Batch-preview a usernek, megerősítés után propagáció

**4. Git commit + push** (script-feladat):
- `commit -m "session: <slug> + AGENT=<claude|codex|gemini>"`
- Auto-push GitHub-ra (`vault-autosave` 10-percenként is, de session-close az atomic-state)
- Session-fájlra rákerül `closed: true` frontmatter-flag

## Anti-pattern

- **Csak Summary, Learnings nélkül**: 6 hónap múlva a session nem search-elhető — nincs evergreen-szakasz, hogy a wiki-be propagáljon.
- **Hivatkozott-path nem verifikálva**: Mac-Obsidian session megír `[[02-Projects/X]]`-et, de a fájl szerveren nincs még synconálva — silent broken-link. Az `ls` check kötelező.
- **Crystallization MŰKÖDÉS NÉLKÜL meg**: ha a session csak nyitva van (`11.11ls`-ben fent), de soha nincs zárva, a Learnings sose propagálódnak. Heti `vault-stuck-detect` audit.
- **Commit kihagyása**: silent disk-state-divergence — local-changes elveszhetnek vagy git-conflict-be ütközhet a következő `11.11start`.
- **„Eseménynapló = igazság"**: `11.11note "kész"` ≠ fájl-disk-ON-LÉTE. Az event-log csak event-log, NEM authoritative state.

## Reusable szabályok

1. **Az agent fejezi be a session-t**, NEM a user. Az agent felelős a 4-lépés-ritualért.
2. **Strukturált 3 szekció kötelező**: Summary, Learnings, Next. Hiányos session = stuck-flag.
3. **Verify-before-propagate**: minden hivatkozott artifact `ls`-vel ellenőrizve, MISSING-line a session-be.
4. **Crystallization opt-in, de default-encouraged**: `VAULT_CRYSTALLIZE_AUTO=1` env-var, NEM hardcode.
5. **Idempotency**: ha `11.11stop` 2-szer fut véletlenül, NE csináljon dupla-summary-t. Frontmatter `closed: true` flag-szűrő.
6. **Atomic state**: vagy mind a 4 lépés sikerül, vagy egyik sem. Hibázáskor rollback-able.
7. **Audit-log**: minden zárás (`<ts>, <session>, <agent>, <verify-result>, <crystallize-result>`) append-only.

## Buktatók

- **Concurrent close 2 chat-ből**: per-chat session-id-isolation ([[claude-code-session-id-per-chat-isolation]]) megoldja, DE a bash `set -e` + `vault-detect-chat-id` exit-1 collision pattern (MEMORY.md említi) gotcha — `2>/dev/null || true` patcholva.
- **Vault-autosave session-close közben**: a 10-perces cron commit-ja megelőzheti a session-close commit-ját → kettéágazó history. Az autosave kihagyja a nyitott session-fájlokat.
- **Mac-szerver double-conflict cascade**: Mac-on és szerveren is külön módosul a session-fájl → 2 conflict + szembe-mentés. `11.11focus`-os single-source-of-truth kötelező a session alatt.
- **Crystallization-failure block-olja a commit-ot**: ha G-Eval hibázik vagy timeout-ol, a session-close mégis menjen — a propagáció külön retry-batch.

## Kapcsolódó

- [[11.11-session-protokoll]] — teljes 11.11-workflow
- [[Crystallization-protocol]] — propagáció-decision-tree
- [[bmad-cross-machine-artifact-verification]] — verify-step részlet
- [[claude-code-session-id-per-chat-isolation]] — per-chat pointer-fájl
- [[verification-step-before-claim]] — alapelv
- [[audit-log-append-only-pattern]] — log-szabály
- [[Karpathy-LLM-Wiki-pattern]] — háttér-filozófia (raw → distilled)
<!-- auto-enriched 2026-05-18: +1 semantic cross-link via vault-search -->
- [[memory-md-overflow-management]] (sem-rokon, score=0.33)

---
name: async-memory-consolidation-letta
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/memory-architecture", "#topic/agent", "#topic/sleep-time-compute", "#topic/letta"]
---

# Async memory consolidation (Letta-style sleep-time compute)

## TL;DR

A **Letta-style „sleep-time compute"** pattern: az agent **inaktív** periódusaiban (user nincs jelen) háttér-folyamat dolgozza fel a friss episodic-memory-t magasabb-szintű semantic-memory-vá. Az online query-path NEM blokkol — a consolidation off-line cron / queue. Cserébe a memória „mélyebb" reflexiókat tartalmaz, mert a háttér-folyamatnak van ideje + nagyobb context-window-ja.

## Háttér (3+ source-evidence)

- [[sv-01-memory-architecture]] — "Letta — Memory-first agent keretrendszer — sleep-time-compute (az agent inaktív periódusban tanul-frissít)"
- [[sv-01-memory-architecture]] — "Async memory consolidation, implemented_in: Letta-style background script"
- [[sv-05-crystallization-automation]] — vault `11.11crystallize` mint sleep-time-compute analógia (session-zárás után batch-szerű Learnings → wiki/Memory/Decision propagáció)
- [[Karpathy-LLM-Wiki-pattern]] — Karpathy crystallization-flow direct analógia (raw session → distilled wiki async)
- [[sv-08-notebooklm-cognitive-layer]] — heti commute-podcast cron mint vault-meta sleep-time-output

## Mintázat

3 réteges memory-architecture-ben:

| Réteg | Latency | Tartalom | Update-mechanizmus |
|---|---|---|---|
| Working / context-window | <1s | aktuális task | minden token |
| Episodic / raw events | <50ms | nyers session-trace | append-only, online |
| Semantic / consolidated | <100ms | reflexiók, ADR-ek, evergreen wiki | **sleep-time async**, cron / triggered |

A sleep-time job tipikusan:

1. Lekér N friss episodic-event-et (pl. utolsó session-zárás óta)
2. LLM-mel reflektál: „mi a tanulság?", „mit kell crystallizálni?"
3. Semantic-store-ba ír — wiki-fájl, ADR, glossary-entry
4. Index frissít (embeddings, KG-triplet, BM25)
5. Audit-log: mit hova írt + miért

A vault implementációban ez a **`11.11crystallize` workflow** ([[Crystallization-protocol]]): session-záráskor a Summary + Learnings + Next ad ME-szerű, később (opcionális VAULT_CRYSTALLIZE_AUTO=1) G-Eval scoring + propagáció a megfelelő rétegekbe.

## Anti-pattern

- **Online (foreground) consolidation user-query közben**: latency-spike + token-cost user-facing. NEM tartozik a kritikus útvonalra.
- **Idempotencia nélküli batch-job**: ha a cron 2-szer fut véletlenül, dupla-konszolidáció + dupla audit-entry. Idempotency-key kell (lásd [[audit-log-append-only-pattern]]).
- **Reflexió ground-truth nélkül**: a consolidator self-favoritism-mel "saját" reflexiókat ír, NEM az evidence-t. Az NLI-réteg ([[nli-hallucination-check-pattern]]) gate-eli ezt.
- **Sleep-time job a "user offline"-hoz kötve**: serverless / cloud agentek esetén ez bizonytalan — explicit cron / queue-trigger jobb.

## Reusable szabályok

1. **Két kódútvonal**: online query-path (read-only semantic-from-cache) ÉS offline consolidation-path (write a semantic-store-ba). NE keverd.
2. **Trigger explicit**: cron, queue-event, `11.11stop`-szerű session-end-signal. NEM idle-timeout (megbízhatatlan).
3. **Idempotency-key**: `consolidation:<session-id>` egyedi, replay-safe.
4. **NLI/G-Eval gate** a propagáció előtt — ne ön-megerősítő reflexió-loop legyen.
5. **Audit-log append-only**: minden konszolidáció rögzítve (`mikor`, `mit`, `hová`, `miért`), reverzibilis.
6. **Token-budget batch-szintű**, NEM per-event — különben szezonalitás-spike (sok session reggel) cost-robbanás.
7. **Sandbox-mutáció** ([[sandbox-branch-mutation-isolation]]): a consolidation egy branch-en, merge csak audit-pass után.

## Buktatók

- **Catastrophic-forgetting cousin**: ha a sleep-time felülír semantic-entry-t a frissebb episodic-mel, a régi info elveszhet. Append-only történet kötelező, override csak explicit revert-tel.
- **Cost-spike off-hours**: cron-job hajnal-3-kor mindig fut — havi token-bill nem 0. Idle-detect + delta-csak-ha-változott.
- **Coherence-drift**: a frissen konszolidált semantic-entry ellentmondhat egy 6 hónappal ezelőttinek. Coherence-check ([[vault-net-ingest]]-szerű) heti.

## Kapcsolódó

- [[sv-01-memory-architecture]] — teljes memory-arch
- [[Crystallization-protocol]] — vault-implementáció
- [[Karpathy-LLM-Wiki-pattern]] — háttér-filozófia
- [[audit-log-append-only-pattern]] — write-szabály
- [[sandbox-branch-mutation-isolation]] — write-isolation
- [[nli-hallucination-check-pattern]] — propagáció előtti gate

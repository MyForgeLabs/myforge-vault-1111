---
name: Append-only event log with undo prune
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#pattern/audit-log", "#stack/drizzle"]
---

# Append-only event log + undo prune

Egy aggregát "current state" mező mellett (pl. `match.score_team1`,
`match.score_team2`) egy **per-event audit-tábla** (pl. `match_event`) ami:

- **Append-only** minden incremental change-re
- **Undo-prune**-olható: a legutolsó eseményt törölheti (LIFO)
- A **replay-detect** (pl. comeback achievement) végigjárja az event-eket

A current-state mező és az event-log **konzisztens** marad — az audit-log
mindig a current-state-et tükrözi cumulative-after-event-szinten.

## Schema

```typescript
// Per-event log
export const matchEvent = pgTable("match_event", {
  id: text("id").primaryKey(),
  matchId: text("match_id").notNull().references(() => match.id, { onDelete: "cascade" }),
  /** Append-only sequence number within the match (1-based). */
  seq: integer("seq").notNull(),
  scoringTeam: integer("scoring_team").notNull(),   // 1 vagy 2
  points: integer("points").notNull().default(1),    // hány pont
  // Cumulative state AFTER this event (denormalized for fast replay)
  scoreTeam1After: integer("score_team1_after").notNull(),
  scoreTeam2After: integer("score_team2_after").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
```

A `score_team*After` mezők denormalizáltak (a current-state-re cumulative
értékkel) — fast replay olvasáshoz, NEM kell visszafelé összegezni.

## Append-action (incrementScore)

```typescript
if (delta > 0) {
  // Append new event
  const last = await db.select({ seq: matchEvent.seq })
    .from(matchEvent).where(eq(matchEvent.matchId, matchId))
    .orderBy(desc(matchEvent.seq)).limit(1);
  const nextSeq = (last[0]?.seq ?? 0) + 1;
  await db.insert(matchEvent).values({
    id: randomUUID(),
    matchId,
    seq: nextSeq,
    scoringTeam: team,
    points: delta,
    scoreTeam1After: newScore1,
    scoreTeam2After: newScore2,
  });
} else if (delta < 0) {
  // Undo: remove most recent event for THIS team
  const recent = await db.select().from(matchEvent)
    .where(eq(matchEvent.matchId, matchId))
    .orderBy(desc(matchEvent.seq)).limit(10);
  const target = recent.find((e) => e.scoringTeam === team);
  if (target) {
    await db.delete(matchEvent).where(eq(matchEvent.id, target.id));
  }
}
```

A current-state aggregát (`match.score_team1/2`) szintén frissül ezzel a
művelettel — az audit-log NEM authoritative, csak audit.

## Replay-detect example (comeback achievement)

A `confirmMatchAction` után végigjárod a sequence-t:

```typescript
const events = await db.select().from(matchEvent)
  .where(eq(matchEvent.matchId, matchId))
  .orderBy(asc(matchEvent.seq));

for (const e of events) {
  const winnerScore = team1Won ? e.scoreTeam1After : e.scoreTeam2After;
  const loserScore  = team1Won ? e.scoreTeam2After : e.scoreTeam1After;
  if (winnerScore === 0 && loserScore >= 8) {
    // The winner was trailing 0:8 at this point → comeback!
    return true;
  }
}
return false;
```

## Miért szuper

- **Audit-trail** minden score-változásra (vita esetén ki mit pontozott mikor)
- **Replay-visualization** lehetséges (`/match/[id]/replay` page)
- **Backward-compat:** old meccsek event-log nélkül is működnek (`events.length
  === 0` → skip a replay-detect)
- **Undo egyszerű** — LIFO-prune NEM kell visszafelé újraszámolni a state-et
- **CRDT-rajongóknak alternatíva:** sokkal egyszerűbb mint Yjs, nincs offline
  resilience de a server-side sequence-szám ELÉG egy 5-15 fős MVP-nek

## Mikor NEM kell

- Single-player apps (pl. fitness-tracker — nincs vita)
- Csak final-state matters (pl. survey-eredmény)
- Real-time CRDT-collab szükséges (akkor Yjs vagy Automerge)

## Boulium-példa (2026-05-19)

`match_event` tábla bevezetve + `incrementScoreAction` append-only + undo-prune
kódolva. `checkComeback()` a `confirmMatchAction` után végigjárja az
event-eket, és a győztes csapattagoknak unlock-olja a `comeback` achievement-et
(+100 XP) ha bárhol 0:8+ trailing-ből nyert.

A meglévő 3 prod-meccs eseménymentes (Phase 1-ben még nem volt event-log) — a
comeback NEM unlock-olódik visszamenőlegesen, csak forward.

## Kapcsolódó

- [[server-only-core-extract-pattern]]
- Drizzle ORM docs: relations + cascade delete

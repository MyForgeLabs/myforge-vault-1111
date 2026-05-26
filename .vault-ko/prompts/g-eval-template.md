# G-Eval prompt template — Learning-bullet confidence scoring

**ADR:** [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]]
**Phase B-1, Layer 2.**
**Status:** v0.3-bias-mitigated (2026-05-17) — adds explicit self-enhancement / verbosity / position bias debiasing per SV-5 research (Liu et al. 2023 G-Eval, Bai et al. 2022 CAI). Prior v0.2 prompt + this calibration example are below.

## Version log
- **v0.1** (2026-05-12) — initial 4-dim G-Eval, no bias debiasing
- **v0.2** (2026-05-13) — added CoT detail, JSON-only output rule
- **v0.3-bias-mitigated** (2026-05-17) — explicit bias lead-in + calibration anchor; covered by [[06-Audits/2026-05-17 B-1 G-Eval bias-mitigation v0.3]]

## System prompt

```
Te egy minőség-értékelő G-Eval-judge vagy egy obsidian-vault crystallization-pipeline-ban.

Feladatod: értékelni egy 11.11 session "Learning → memória" bullet-jét négy dimenzió mentén,
majd Chain-of-Thought (CoT) érveléssel egy 0.0–1.0 közötti confidence score-ot adni.

A score határozza meg, hogy a bullet automatikusan propagálható-e a perzisztens memóriába
(MEMORY.md, 11-wiki/, 07-Decisions/), vagy emberi review-t igényel.

⚠️ KRITIKUS — bias-tudatosság (LLM-as-a-Judge ismert torzítások, Liu et al. 2023):

1. **Self-enhancement bias** — Ha esetleg te (mint Claude / GPT-class LLM) generálnád
   ezeket a Learning bulleteket egy másik kontextusban, ne preferáld őket. **Tételezd
   fel, hogy a bulletet egy MÁSIK, ismeretlen agent vagy ember írta.** Az értékelés
   a TARTALOMRA vonatkozik, nem a szerző stílusára. Mérési alap: a Claude/GPT-judge
   ~25%-kal magasabb win-rate-et ad saját outputjának (Self-Rewarding csapda) —
   ezt aktívan kompenzáld le.

2. **Verbosity bias** — A hosszúság NEM minőségi jel. Egy 1-mondatos, konkrét link
   + ténnyel rendelkező bullet pontosan akkora confidence-t érdemel, mint egy
   3-bekezdéses, jól szerkesztett, de hasonló tartalmú. A TÖMÖRSÉG ÉRTÉK, nem hiány.
   Soha ne adj +1-et csak azért, mert többet ír.

3. **Position bias** — Egy adott session-en belül minden bullet-et önállóan értékelj.
   Az első / utolsó bullet helye az inputban NEM korrelál a minőséggel. Ha egymás
   után értékelsz többet, a sorrend ne befolyásolja a score-t.

4. **Halo / authority bias** — Ne adj magas dim1-et csak azért, mert a bullet
   hivatkozik egy "elismert" forrásra ([[07-Decisions/...]], [[11-wiki/...]]). A
   link jó proxy, DE verifikáld a forrás-kontextusban hogy az állítás valóban
   alá van támasztva.
```

## User prompt template (substitute `{BULLET}` and `{CONTEXT}`)

```
Learning bullet:
"""
{BULLET}
"""

Forrás-kontextus (a session-fájl ## Summary + ## Events releváns részei):
"""
{CONTEXT}
"""

Értékeld 4 dimenzió mentén (1-5 skála):

1. **Faktualitás** — A forrás-fájlok tartalma egyértelműen alátámasztja-e?
   1 = ellentmondás vagy nincs alap     5 = direkt idézhető forrás

2. **Specifikusság** — Konkrét, akcionálható tudás vs általános platitude?
   1 = "fontos a tisztaság"             5 = "Hostinger LSCACHE 7-napos image-cache-t a `wp cache flush` NEM érvényteleníti"

3. **Reusability** — Más kontextusban / projektben is alkalmazható?
   1 = projektspecifikus one-off        5 = univerzális best-practice / playbook

4. **Safety** — Tartalmaz-e PII-t, jelszót, érzékeny adatot, ügyfél-titkot?
   5 = tisztán technikai                1 = jelszó/PII/titok van benne (auto-discard)

📐 Kalibrációs horgony (anti-verbosity-bias example):

  BAD-BUT-VERBOSE bullet (bőbeszédű, mégis gyenge — score ≤ 2):
  > "A modern szoftverfejlesztésben különösen fontos, hogy az ember odafigyeljen
  >  a megfelelő teszt-coverage-re. Sokféle test-framework létezik, mindegyiknek
  >  megvannak a maga előnyei és hátrányai, de általánosságban elmondható, hogy
  >  érdemes valamilyen szintű integrációs tesztet írni a projekt fontos
  >  funkcióira. Ez segít elkerülni a regressziókat és növeli a kódminőséget."
  Helyes értékelés: dim1=2 (általánosság), dim2=1 ("fontos a tisztaság"-szint),
  dim3=2 (platitude, már mindenki tudja), dim4=5. confidence ≈ 0.33 → discard.
  ❌ HIBA lenne dim2=4-et adni mert "jól fogalmazott". A hosszúság ≠ tartalom.

  GOOD-AND-TERSE bullet (rövid, mégis erős — score ≥ 4):
  > "Hostinger LiteSpeed 7-napos image edge-cache; `wp cache flush` NEM érvényteleníti.
  >  Fájlnév-rename kell. Forrás: example-foxxi.local 2026-05-10 deploy."
  Helyes értékelés: dim1=5 (verifikálható, datált, hosting-specifikus tény),
  dim2=5 (konkrét eszköz + konkrét tévút + konkrét megoldás), dim3=4 (minden
  LiteSpeed-user), dim4=5. confidence ≈ 0.93 → auto-prop.
  ✅ A rövidség itt feature: információ-sűrűség magas.

CoT érvelés (3-5 mondat):
- Dim 1 értékelés + indok (idézd a forrás-kontextus releváns részét)
- Dim 2 értékelés + indok (általános vs specifikus?)
- Dim 3 értékelés + indok (csak ez a projekt, vagy minden hasonló helyzet?)
- Dim 4 értékelés + indok (PII/credential check)
- Bias-self-check (1 mondat): nem adtam-e +1-et hosszúságért, "saját stílusért", vagy pozícióért?

Aggregálás:
  raw_score = (dim1 + dim2 + dim3) / 15        # 3 fő dimenzió átlaga
  safety_penalty = 0 if dim4 == 5 else (5 - dim4) * 0.20
  confidence = max(0.0, raw_score - safety_penalty)

Output JSON formátumban (NO markdown fences, NO prose surround):
{
  "dim1_faktualitas": <1-5>,
  "dim2_specifikussag": <1-5>,
  "dim3_reusability": <1-5>,
  "dim4_safety": <1-5>,
  "cot": "<3-5 mondat érvelés, beleértve a bias-self-check-et>",
  "confidence": <0.0-1.0>,
  "route": "<auto-prop | batch-preview | discard>"
}

Routing rule (a script alkalmazza, NE te döntsd el):
  confidence >= threshold        → auto-prop
  0.70 <= confidence < threshold → batch-preview
  confidence < 0.70              → discard

threshold a `~/.vault-config/crystallize-threshold.txt`-ben (hot-reloadable).
```

## Modell-választás (Phase B-1 Week 1 benchmark)

| Modell | Cost/Learning | Latency | Notes |
|---|---|---|---|
| **Claude Haiku 4.5** | ~$0.0001 | ~1-2s | Default, Tier-$50 compatible |
| **Claude Sonnet 4.6** | ~$0.003 | ~2-4s | Magasabb minőség, ha Haiku <90% agreement |
| **Lokális Qwen 7B (Ollama)** | $0 | ~5-10s | Privacy-első, GPU-igény |
| **`claude-code` subagent** | $0 | ~10-30s | Default for shadow-mode (no API key) |

**Benchmark cél:** 50 manuálisan címkézett Learning bullet, 3-modell-output vs gold-label. Threshold-distribution + agreement-rate. Döntés Week 2-re.

**v0.3 calibration target:** 30-sample re-run baseline vs új prompt → 90%+ pass-rate (high-conf agreement), self-enhancement-margin ≤ 10% (vs ~25% in v0.2 baseline).

## Audit-log format (`06-Audits/crystallize-log.jsonl`)

Append-only JSONL, minden döntésre 1 sor:

```json
{
  "ts": "2026-05-12T20:40:00Z",
  "session_slug": "2026-05-12-obsidian-vault",
  "mode": "shadow",
  "threshold": 1.0,
  "bullet_hash": "<sha256>",
  "bullet_preview": "<első 80 char>",
  "scores": {"dim1": 5, "dim2": 4, "dim3": 5, "dim4": 5},
  "confidence": 0.93,
  "route": "auto-prop",
  "executed": false,
  "target_file": null,
  "prompt_version": "v0.3-bias-mitigated"
}
```

`executed: false` shadow mode-ban — minden döntés log-only.

## Hot-reload threshold

```bash
# Konzervatív → aggressive ramp:
echo "0.95" > ~/.vault-config/crystallize-threshold.txt   # Week 3-4
echo "0.85" > ~/.vault-config/crystallize-threshold.txt   # Week 5-6
```

A `11.11crystallize` script minden futás előtt re-readeli. Race-condition védelem: `fcntl.flock` LOCK_SH.

## Kapcsolódó

- [[07-Decisions/2026-05-12 sv-5 crystallization automation arch]] — parent ADR
- [[11-wiki/sv-05-crystallization-automation]] — research (5.b LLM-judge biasok)
- [[11-wiki/Crystallization-protocol]] — meglévő manuális protokoll (visszaesés ha mode=manual)
- [[06-Audits/2026-05-17 B-1 G-Eval bias-mitigation v0.3]] — v0.2 → v0.3 baseline comparison

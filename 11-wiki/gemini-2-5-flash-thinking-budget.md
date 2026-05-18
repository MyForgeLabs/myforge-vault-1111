---
name: gemini-2-5-flash-thinking-budget
type: wiki
tags: ["#topic/gemini", "#topic/api", "#topic/llm"]
created: 2026-05-15
updated: 2026-05-15
---

# Gemini 2.5 Flash thinking-mode — rövid task → token-elfogyás → mid-sentence cut

A `gemini-2.5-flash` modell **thinking-mode**-ban gondolkodik a válasz ELŐTT, és a thinking-tokenek **beleszámolnak a `maxOutputTokens`-be**. Rövid task-nál (pl. 300 szavas magyar briefing) `maxOutputTokens=1500` túl szűk lehet — a modell el-gondolkodik, kifogy belőle, a válasz mid-sentence levágódik.

## Tünet

```
prompt: "Írj 350-450 szavas magyar briefinget..."
response: "Szia Peti! Itt a pénteki reggeli briefinged. Tegnap elég sok automatikus commit"
# 27 szó, mid-sentence cut
```

`finishReason: "MAX_TOKENS"` jelzi.

## Fix 1 — disable thinking

```python
{
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 4000,
    "thinkingConfig": {"thinkingBudget": 0}
  }
}
```

A `thinkingBudget: 0` kikapcsolja a thinking-mode-ot. Egyszerű generation task-okra (összefoglalás, fordítás, formázás) ez **mindig elég**, és a válasz teljes lesz.

## Fix 2 — switch to gemini-2.5-flash-lite

A `lite` variánsban nincs thinking-mode hardcoded:
```python
model = "gemini-2.5-flash-lite"
```

Olcsóbb is. Egyszerű task-okra (no reasoning) ez bőven elég.

## Fix 3 — bigger budget + keep thinking

Complex reasoning kell? Tartsd a thinking-et de növeld:
```python
"maxOutputTokens": 8000,
"thinkingConfig": {"thinkingBudget": 4000}
```

## Validation

```python
resp = ...
finish = resp["candidates"][0].get("finishReason")
if finish == "MAX_TOKENS":
    print("WARN: response truncated, increase maxOutputTokens or disable thinking")
elif finish != "STOP":
    print(f"WARN: finishReason={finish}")
```

## Use case matrix

| Task | Recommended |
|---|---|
| Fordítás, összefoglalás, format | `thinkingBudget: 0` vagy `flash-lite` |
| Code generation komplex logikára | `thinking enabled` (default) |
| Tool-call routing | `thinkingBudget: 0` általában OK |
| Long-context summarization | `thinking enabled`, 16K+ budget |

## Hol jelent meg

2026-05-15 vault-brief.py MVP — első hívás 27-szavas mid-sentence cut, fix után 172-szavas teljes briefing. Részletes log: [[08-Sessions/2026-05-15-szerver-update]]

## Kapcsolódó

- [[11-wiki/gemini-3-1-flash-tts-pipeline]]
- [[02-Projects/mfl-voice]]

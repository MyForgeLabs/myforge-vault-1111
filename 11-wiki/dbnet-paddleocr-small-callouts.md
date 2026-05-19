---
name: dbnet-paddleocr-small-callouts
description: PaddleOCR DBNet detektor (v2.10) Tesseract LSTM helyett — `det_limit_side_len=4096` a downsampling-eltűnés ellen. 95% → 98% match kis (5-10 px) callout-okra.
type: wiki
created: 2026-05-12
tags: ["#type/reference"]
tag_backfill: 2026-05-19
updated: 2026-05-19
---
# DBNet (PaddleOCR) vs Tesseract LSTM kis callout-detektálásra

## A tanulság

**A Tesseract LSTM fundamentálisan rosszul detektál ~5-10 pixeles izolált digit-eket sűrű technical drawing-on.** A DBNet (Differentiable Binarization) szegmentációs alapú detektor — pixel-level binary maszkokat tanul a polygon-bound-okra — sokkal robosztusabb.

**95% → 98%** match-arány Makita 1002BA exploded view-on, csak az OCR-engine cseréje (Tesseract-tal a meglévő multi-validation mellé).

## Why

Tesseract LSTM:
- Layout-analízis alapú (PSM 11 "sparse text" — strukturális assumptions a sorokra)
- Egyetlen detektor + recognizer kombinálva
- Vékony "1" vagy összetapadt "10" digiteket gyakran elveszít

DBNet (PaddleOCR PP-OCRv3 server-det 84MB):
- Pixel-szintű szegmentáció → minden dark-blob önálló detection
- Külön detektor (DBNet) + külön recognizer (CRNN)
- Robosztusabb a sűrű clusterekre és vékony vonalakra
- Cluster-elhelyezkedéstől függetlenül detektál

NotebookLM Q1 forrás-idézettel (`docs/notebooklm-q1-best-free-ocr-2026-05-12.md`):
> "A hagyományos Tesseracttal szemben mindkét rendszer a **DBNet** detektálási architektúrát használja [1, 2]. A DBNet kifejezetten jól kezeli a bonyolult hátterű, szabálytalan elrendezésű, apró objektumokat (mint a mutatóvonalak végén álló számok) és nagyon precíz poligonális határoló dobozokat (bounding boxokat) generál."

## How to apply

**Install (egyszerre Tesseract MELLÉ, nem helyett):**
```bash
.venv/bin/pip install 'paddleocr<3' 'paddlepaddle<3'
# v2.10.0 + paddlepaddle 2.6.2 — NEM v3.5.0 (PIR/oneDNN CPU runtime bug)
```

**Kritikus konfig** (NotebookLM Q1 KEY felfedezés):
```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    det_limit_side_len=4096,    # ⚠️ KULCSPARAM — default 960 px
    det_db_thresh=0.3,
    det_db_box_thresh=0.6,
    show_log=False,
)
```

**Mit csinál a `det_limit_side_len=4096`:** A deep-learning OCR motorok a bemeneti képet hardveres okokból leméretezik (default 960 px-re a leghosszabb oldalon). Egy nagy-felbontású (4000+ px) műszaki rajzon ez **a 5-10 px-es callout-digiteket fizikailag eltünteti a downsampling alatt**. A 4096-os limit megőrzi az eredeti felbontást.

**Integráció pattern:** PaddleOCR-t mint **2nd opinion validator** a meglévő Tesseract multi-pass pipeline mellé. A találatok ugyanabba a spatial-voting cluster-be mennek, source-tag `"paddleocr/PP-OCRv3"`. Magasabb confidence + NMS overlap-resolution.

**Lazy singleton init** — modellek (~165 MB total) első futtatásra letöltődnek `/root/.paddleocr/`-be, utána re-use.

## Mit NEM old meg

- A C-prefix vagy section-arrow callout-ok (pl. KGC-rajz "C10", "D10") — ezek inkluzív inclusion-codes, NINCSENEK vizuálisan a rajzon → DBNet sem találja meg, csak manual pozicionálás.
- Letter-only marker (pl. "A" szekció-arrow Makita 1002BA-on) — DBNet a digit-only allowlist miatt kihagyja, külön letter-pass-szal kell.

## PaddleOCR v3.5.0 PIR/oneDNN bug

**TILOS** a v3.5.0-t CPU-n — `ConvertPirAttribute2RuntimeAttribute not support` runtime error az új PIR executor + oneDNN combo miatt. Workaround: downgrade v2.10.0-ra (`pip install 'paddleocr<3' 'paddlepaddle<3'`). v2 stabil, modell-pipeline (det+rec) változatlan, EREDMÉNY IS IDENTIKUS.

## Validálás

Pipeline progresszió Makita 1002BA-n:
- Baseline (Tesseract single-pass PSM 11): 60%
- + Multi-validation (6 variant × 3 PSM + patch-based + super-resolution + min_votes=1): 95%
- **+ PaddleOCR DBNet 2nd-opinion** (`det_limit_side_len=4096`): **98%** (65/66 numeric)

`006`, `007` callout-okat amiket Tesseract minden konfigon eltüntetett, PaddleOCR megtalálta. Az utolsó 1 maradék (`021`) az NMS overlap-resolution-nak köszönhetően single-pass-out maradt.

## Kapcsolódó

- [[02-Projects/robbantott-kereso]] — implementáció
- `docs/notebooklm-q1-best-free-ocr-2026-05-12.md` — eredeti research-Q + idézetek
- NotebookLM notebook `b82bec2c-bb92-463f-93d4-5c4a675163a1` — 220 source library

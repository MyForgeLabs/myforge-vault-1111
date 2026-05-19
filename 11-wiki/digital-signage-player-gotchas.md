---
name: Digital signage player — debugging gotchas
description: HTML5 video/iframe-alapú signage player buktatói (canplay re-fire, mixed-content, IntersectionObserver lazy preview)
type: wiki
created: 2026-05-03
tags: ["#type/wiki", "#topic/digital-signage", "#topic/web-debugging"]
updated: 2026-05-19
---

# Digital signage player — debugging gotchas

KGC TV CMS / `kgc-signage` projektből kihegyezett buktatók, amik bármely HTML5-alapú signage-rendszerre érvényesek.

## 1. `<video oncanplay>` minden loop-restartnál újra tüzel

**Tünet:** A videó-item lejátszik egyszer, aztán fekete képernyő (vagy random villogás multi-item playlist esetén). Loop attribute be van állítva, mégis megáll.

**Ok:** A HTML5 video `canplay` event NEM csak az első betöltéskor tüzel. **Loop-restart, seek, codec-újraindítás esetén is** újra eldob egy `canplay`-t. Ha a `canplay` callback triggereli a "ready / next-item" logikát, akkor minden loop-restart "tovább-rotate"-ol → a következő slot üres → fekete képernyő.

**Fix — guard flag:**
```js
let readyFired = false;
const fireOnce = (durationMs) => {
  if (readyFired) return;
  readyFired = true;
  ready(durationMs);
};
v.addEventListener('canplay', () => fireOnce(durationMs));
v.addEventListener('error', () => fireOnce(2000));
```

Ugyanígy alkalmazandó `<img onload>` és `<iframe onload>` esetén is — bár ritkább, de cache-reload trigger-elheti.

**Belt-and-suspenders loop:** mellette `v.loop = true` + `v.addEventListener('ended', () => { v.currentTime=0; v.play(); })` — codec-quirk esetén is biztosan loop-ol.

## 2. Mixed-content blokk HTTPS player-iframe-ben

**Tünet:** A player oldal teljesen fekete vagy a 16:9 zóna iframe-je nem rajzolódik. Nincs HTTP error, csak a tartalom hiányzik.

**Ok:** Az HTTPS-en hostolt admin/player **nem tud HTTP-iframe-et megjeleníteni** — modern böngészők hard-blokkolják. Egy KGC TV CMS-nél: a player URL `https://kivetito.kisgepcentrum.hu/s/utcafront`, de az iframe `http://72.62.92.98:8200/tv-nyitva.html` → blokkolva.

**Fix:** Lokális `/static/` mappa, **ugyanazon HTTPS-domain-en** szerválva. Pl. `/opt/kgc-signage/public/static/tv-nyitva.html` → `https://kivetito.kisgepcentrum.hu/static/tv-nyitva.html`. Egyetlen `app.use('/static', express.static(...))` az Express-en.

**Hogyan diagnosztizáld:** F12 → Console: `Mixed Content: ... was loaded over HTTPS, but requested an insecure resource ...` üzenet.

## 3. Multer `LIMIT_UNEXPECTED_FILE` field=files: count-limit, NEM field-name mismatch

**Tünet:** Sok fájlos upload mid-stream megáll, server log: `MulterError: Unexpected field, field: 'files'`. A field neve EGYEZIK a config-gal — mégis "unexpected".

**Ok:** Multer `array(name, count)`-nál ha a count-limit átléped (pl. 50 db a default, és 51-ediket küldsz), akkor az 51. file `LIMIT_UNEXPECTED_FILE`-ként dől ki **a saját nevével**. Félrevezető hibaüzenet — nem a field-name a baj, a darabszám.

**Fix:**
1. Server: `upload.array('files', 500)` (bumpold a count-ot)
2. Frontend: **auto-batching** 50-es chunk-okra. Egy batch megszakadása csak azt érinti — a többi már sikerült.

```js
const BATCH_SIZE = 50;
for (let i = 0; i < files.length; i += BATCH_SIZE) {
  const batch = files.slice(i, i + BATCH_SIZE);
  await uploadBatch(batch, i / BATCH_SIZE);
}
```

## 4. 100+ video-thumbnail UI lefagyasztja az admin-t

**Tünet:** A média-tár 200+ fájllal megnyitása 5-10s-ig laggol. Kulcsklikk nem reagál.

**Ok:** Minden `<video>` elem `preload="metadata"`-val megpróbálja letölteni az első frame-et — egyszerre 200+ HTTP request, ami a böngésző connection-poolját (~6 párhuzamos) blokkolja.

**Fix — IntersectionObserver lazy-load:**
```js
// Kezdetben preload="none" — semmi nem tölt
const v = document.createElement('video');
v.preload = 'none';
v.muted = true;

// Ahogy a viewport-ba scrollozódik (200px buffer), aktiválódik
const obs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.preload = 'metadata';
      e.target.load();
      // Safari-trükk: első frame megjelenítése
      e.target.addEventListener('loadedmetadata', () => {
        if (e.target.currentTime === 0) e.target.currentTime = 0.1;
      }, { once: true });
      obs.unobserve(e.target);
    }
  });
}, { rootMargin: '200px' });
obs.observe(v);
```

Plus képhez: `<img loading="lazy" decoding="async">`.

## 5. Anti-flicker: single-item playlist ne rotáljon

**Tünet:** 1-elemes playlist iframe-je 30s-enként újratöltődik (rebuild flicker), mert a polling triggereli az item-rotation-t.

**Ok:** A pollozó player a queue.length-től függetlenül `setTimeout(playNextInZone, durationMs)`-t ütemez. Single-item esetén a "következő" ugyanaz az item → re-load → flicker.

**Fix:** Ha `queue.length <= 1`, ne ütemezz rotation-t. A polling úgyis észleli ha változik a playlist, és akkor cseréli.

```js
loadIntoSlot(standbySlot, item, (durationMs) => {
  swap();
  if (queue.length <= 1) return;   // ← single-item → no rotation
  nextTimer = setTimeout(() => playNext(), durationMs);
});
```

## Kapcsolódó

- [[02-Projects/kgc-tv-cms]] — referencia-implementáció
- [[02-Projects/kgc-kivetitok]] — bolti deployment kontextus
- [[08-Sessions/2026-05-03-kgc-kivetit]] — eredet-session

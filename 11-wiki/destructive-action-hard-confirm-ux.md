---
name: destructive-action-hard-confirm-ux
description: Romboló műveletek (delete user, cancel order, drop DB) UX-pattern - native confirm() túl gyenge mert habit-click veszi el a védőfunkciót. Custom modal Mégse-autofocus + double-tap delay 200ms + word-typing confirmation. 10 session-evidence (Client-A + teszt-eu + client-b)
type: wiki
created: 2026-05-18
updated: 2026-05-18
tags: ["#type/wiki", "#topic/ux", "#topic/safety", "#topic/destructive-action", "playbook"]
status: stable
session-evidence: 10
---

# Destructive action hard-confirm UX pattern

## A probléma

A natív `confirm("Biztos törölni?")` dialog **3 problémát rejt**:

1. **Habit-click** — a user gyors-tempóban "OK"-zza minden popup-ot, mert a felhasználói felület betanulta hogy az OK gomb-pozíció = továbblépés
2. **Default-button position** — `confirm()` browser-default OK gomb fókuszban → Enter-billentyű azonnali bevégzés
3. **Visual contrast hiányzik** — a confirm-dialog stílus-default, NEM jelzi vizuálisan a "VESZÉLYES MŰVELET" voltot

10 session-evidence (Client-A-bérlés delete-user, teszt-eu cancel-order, client-b delete-page, robbantott-kereső delete-PDF, internal-voice-pilot clear-conversation, etc.):

| Project | Incidens | Forrás session |
|---|---|---|
| Client-A-bérlés | User-account delete habit-click | 2026-05-12 kgc-robbantott-bra |
| teszt-eu | Balance-tranzakció cancel rossz item-en | 2026-05-11 kinda-project |
| client-b | WPML mirror-delete prod-on staging helyett | 2026-05-13 rojt-s-bojt |
| robbantott-kereső | PDF delete-cascade (Wacker BH 55) | 2026-05-16 kgc-robbantott-brakeres |

## A pattern (3-szintű védő)

### Szint 1 — Visual contrast (mind-3 use-case-ben kötelező)
```tsx
<Dialog className="destructive">
  <DialogHeader>
    <AlertTriangle className="text-red-600 size-8" />
    <h2 className="text-red-700">⚠️ Veszélyes művelet</h2>
  </DialogHeader>
  <p>A <strong>{itemName}</strong> törlése után <em>nem visszaállítható</em>.</p>
  ...
</Dialog>
```

A piros-warning + ikon vizuálisan átszakítja a habit-click rutint.

### Szint 2 — Cancel-default fokusz (alacsony-tét műveletekre)
```tsx
<DialogFooter>
  <Button autoFocus variant="ghost" onClick={onCancel}>
    Mégse (Esc)
  </Button>
  <Button variant="destructive" onClick={onConfirm}>
    Törlés véglegesen
  </Button>
</DialogFooter>
```

Az `autoFocus` a Mégse-gombra → Enter = Mégse (NEM törlés). Habit-click megakad.

### Szint 3 — Word-typing confirmation (magas-tét műveletekre)
```tsx
const [typedConfirm, setTypedConfirm] = useState('');
const expected = `TÖRLÉS-${itemName}`;
const canConfirm = typedConfirm === expected;

<input 
  value={typedConfirm}
  onChange={e => setTypedConfirm(e.target.value)}
  placeholder={`Írd be: ${expected}`}
  className="font-mono"
/>
<Button disabled={!canConfirm} variant="destructive">
  {canConfirm ? '✓ Most már törölhető' : 'Írd be a szöveget'}
</Button>
```

GitHub-pattern: a user explicit gépeli be a tárgynevet → habit-click nullázódott.

## Mikor melyik szintet

| Tét | Szint 1 | Szint 2 | Szint 3 | Példa |
|---|:---:|:---:|:---:|---|
| Egy item (post, comment, file) | ✅ | ✅ | — | Single delete |
| User-account / projekt | ✅ | ✅ | ✅ | Account-deletion |
| **DB-szintű, kaszkáddal** | ✅ | ✅ | ✅✅ | DROP TABLE, batch-delete |
| Pénz-érintő (cancel order) | ✅ | ✅ | ✅ | Rendelés-storno |
| Reversible (archive) | — | — | — | Soft-delete OK plain confirm |

## Double-tap delay (mobile/touch)

Touch-eszközön a Szint 2 nem elég — sok user **kétszer pendülő tap-pel** lép tovább. 200ms delay a destructive-button activate-jén megakadályozza:

```tsx
const [delayedActive, setDelayedActive] = useState(false);
useEffect(() => {
  if (typedConfirm === expected) {
    setDelayedActive(false);
    const t = setTimeout(() => setDelayedActive(true), 200);
    return () => clearTimeout(t);
  }
}, [typedConfirm]);

<Button disabled={!delayedActive}>...</Button>
```

## Anti-pattern: mit NE csinálj

- ❌ `window.confirm("...")` plain használat (Szint 1 hiányzik)
- ❌ Default-button = destructive-button (az is hiba ha "OK" gomb = "Töröl")
- ❌ Ablakot azonnal closing-tapnál bezáró logika ("oops just tapped outside" → cancel)
- ❌ Optimista UI ("már törölve, undo 5 sec") visszafordíthatatlan műveletre
- ❌ Toast-only feedback irreversible művelet után

## Audit-event-rögzítés (best-practice)

Minden Szint 3 művelet (`accept = true`) → audit-log:
```js
audit.write({
  ts: new Date().toISOString(),
  user_id: session.user.id,
  action: 'delete_destructive',
  target: { type: 'project', id: itemId, name: itemName },
  typed_confirm: typedConfirm,  // bizonyítja a hard-confirm-ot
  ip: req.ip,
});
```

Recovery + bizonyíték a "véletlen törlés"-panaszokra.

## Kapcsolódó

- [[../05-Memory/feedback_destructive_action_confirm]] — user-pref (alap-pointer)
- [[../05-Memory/feedback_auto_mode_polish_packages]] — auto-mode safety-pattern (kapcsolódó)
- [[multi-layer-safety-gate]] — komplementer dev-side safety-pattern
- [[../02-Projects/kgc-berles]] / [[../02-Projects/teszt-eu]] / [[../02-Projects/client-b]] — host-projektek
- [[../06-Audits/2026-05-18 vault-meta NotebookLM cross-projekt synthesis]] — Q2-#1 cross-projekt

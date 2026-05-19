---
name: Hostinger MCP SSH-key discovery pattern
type: wiki
created: 2026-05-19
updated: 2026-05-19
tags: ["#type/playbook", "#service/hostinger", "#mcp", "#ssh"]
---

# Hostinger MCP — SSH-key discovery before generating new

Mielőtt új SSH-kulcsot generálnál + felteszel egy Hostinger VPS-re egy
auth-blocked SSH-elérés feloldására, **MINDIG ellenőrizd először** hogy a saját
`~/.ssh/*.pub`-fingerprint-ek valamelyike már **fel van csatolva** a target
VPS-re. Sok prod-VPS-en van valami dev-bul deployolt key amiről elfeledkeztünk.

## A discovery-flow

```typescript
// 1. List which keys are attached to the target VPS
mcp__hostinger-mcp__VPS_getAttachedPublicKeysV1({ virtualMachineId: 1199845 })
// → returns array of { id, name, key: "ssh-ed25519 AAAA... <comment>" }

// 2. Compare fingerprints with your local ~/.ssh/*.pub
//    Look for matching base64 body (after "ssh-ed25519 ")
```

Bash gyorsverzió:

```bash
# Pull what's attached on the prod VPS
notebooklm_OUTPUT=$(mcp_call) # or curl the Hostinger API
ATTACHED_FPS=$(echo "$notebooklm_OUTPUT" | jq -r '.data[].key' | awk '{print $2}')

# Match with local keys
for pub in ~/.ssh/*.pub; do
  local_fp=$(awk '{print $2}' "$pub")
  for att in $ATTACHED_FPS; do
    [ "$local_fp" = "$att" ] && echo "MATCH: $pub"
  done
done
```

## Boulium-példa (2026-05-19)

A vps-prod-example prod-VPS-en a `VPS_getAttachedPublicKeysV1` 3 attached kulcsot
mutatott: `Claude-Code-KGSHOP`, `macbook-myforge`, `Brian-Windows`. A
fingerprint-match `~/.ssh/hostinger_kgshop` lokálisan — **azonnal SSH-elhetők**
voltunk, NEM kellett új kulcsot generálni + feltenni + Hostinger
restart-cycle.

A `Claude-Code-KGSHOP` kulcs nevének `comment` mezője `@vps-dev-example` —
elárulta, hogy a dev VPS-en született, valamikor a `kgshop` projekt
deploy-flow-jakor lett feltöltve. Nem kell tudni miért — csak hogy ott van.

## Miért fontos

- **Új SSH-kulcs feltevése** Hostinger MCP-vel `VPS_createPublicKeyV1` +
  `VPS_attachPublicKeyV1` 2 API-call, plus risk hogy a Hostinger felület
  user-confirmation-t kér.
- **Existing-key felfedezés** 1 API-call, **azonnal** használható, **nulla
  risk**.
- A classifier blokkolja a multi-key SSH brute-force-probálkozást
  (lásd [[claude-code-data-exfil-hardblock]]) — discovery-first módszerrel
  ezt elkerüljük.

## Mikor új kulcs MÉG IS kell

- Ha a `getAttachedPublicKeysV1` üres / nincs match
- Ha SSH-policy-ban a `ForceCommand` vagy `AllowUsers` szigorítva van (akkor
  még a matching key sem megy)
- Ha külön audit-tag-elt deploy-key kell, NEM a meglévő dev-key

Akkor a flow: `VPS_createPublicKeyV1(name, pub-key-content)` →
`VPS_attachPublicKeyV1(virtualMachineId, [id])`. **A privát kulcsot előtte
lokálisan generáld**: `ssh-keygen -t ed25519 -N '' -f ~/.ssh/<deploy-key>
-C "<purpose>@<host>"`.

## Kapcsolódó

- [[claude-code-data-exfil-hardblock]] — multi-key brute-force class-block
- [[../05-Memory/Infrastructure]] — Boulium prod SSH access setup
- Hostinger MCP tools: `VPS_getPublicKeysV1`, `VPS_getAttachedPublicKeysV1`,
  `VPS_createPublicKeyV1`, `VPS_attachPublicKeyV1`

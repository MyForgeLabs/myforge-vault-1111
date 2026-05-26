---
name: Adobe MCP file-upload protocol (asset_initialize + chunk PUT + finalize)
type: wiki
tags: ["#type/wiki", "#tool/adobe-mcp", "#pattern/cloud-upload"]
created: 2026-05-22
updated: 2026-05-22
---

# Adobe MCP file-upload protocol

Az Adobe Creative Cloud MCP feldolgozó toolok (`image_generative_expand`, `image_remove_background`, `image_vectorize`, stb.) **NEM** fogadnak lokális filesystem-path-t és NEM fogadnak external CDN URL-t (a Higgsfield CDN `d8j0ntlcm91z4.cloudfront.net` NEM whitelisted). Lokális file → Adobe Creative Cloud upload kell, és az ott kapott `presignedAssetUrl`-t használjuk a tool input-jaként.

## 4-lépéses upload protocol

### 1. Get file metadata (Bash)

```bash
wc -c < "matrica.png" | tr -d ' '              # → file_size in bytes
file --mime-type -b "matrica.png"              # → "image/png"
```

### 2. `asset_initialize_file_upload`

```jsonc
{
  "path": "matrica.png",
  "file_size": 21884107,
  "media_type": "image/png"
}
```

Válasz tartalmaz:
- `filename` (az assigned név)
- `transfer_document` objektum, ami tartalmaz:
  - `repo:blocksize` — chunk size (default 10485760 bytes / 10 MB)
  - `_links."http://ns.adobe.com/adobecloud/rel/block/transfer"` — array of `{"href": "..."}` pre-signed URL-ek minden chunk-hoz
  - `_links."http://ns.adobe.com/adobecloud/rel/block/finalize"` — finalize URL

### 3. Chunk PUT (parallel curl)

```bash
FILE="matrica.png"
BLOCKSIZE=10485760

upload_chunk() {
  i=$1
  url=$2
  dd if="$FILE" bs=$BLOCKSIZE skip=$i count=1 2>/dev/null | \
    curl -s -o /dev/null -w "Chunk $i: %{http_code}\n" \
    -L -X PUT "$url" \
    -H "Content-Type: image/png" \
    --data-binary @-
}

upload_chunk 0 "<transfer_link_href_1>" &
upload_chunk 1 "<transfer_link_href_2>" &
upload_chunk 2 "<transfer_link_href_3>" &
wait
```

Megjegyzés: `-L` (curl follow redirect) kötelező — a presigned URL-ek lehetnek 308 redirect-tel. Auth header NEM kell (presigned).

### 4. `asset_finalize_file_upload`

```jsonc
{
  "filename": "matrica.png",
  "transfer_document": { ... a teljes objektum verbatim az init-ből ... }
}
```

A `transfer_document` MINDEN kulcsát át kell adni, beleértve a `repo:` prefixű mezőket és a `_links` objektumot. Bármi optional-ut/null-t is.

Válasz tartalmaz: `assetId` (`urn:aaid:sc:EU:...`) + **`presignedAssetUrl`** — ezt használjuk a feldolgozó tool input-jaként.

## Példa-pipeline: car-wrap matrica Adobe-expand

```jsonc
// 1. Upload
asset_initialize_file_upload({path: "wallpaper.png", file_size: 20718003, media_type: "image/png"})
// → response.transfer_document._links."rel/block/transfer" → 2 chunk URL

// 2. Bash: parallel PUT 2 chunks → 200 200

// 3. Finalize
asset_finalize_file_upload({filename: "wallpaper.png", transfer_document: {...verbatim...}})
// → response.assets[0].presignedAssetUrl = "https://at.adobe.com/k3oRW0iJB5QUVvQS"

// 4. Use in expand
image_generative_expand({
  imageURIs: ["https://at.adobe.com/k3oRW0iJB5QUVvQS"],
  options: { expandPixels: { left: 3888, right: 3888 } },
  outputFileType: "png"
})
// → response.results[0].outputUrl = "https://photoshop-api.adobe.io/v2/short-url/..."
```

## Pitfalls

- **Higgsfield CDN URL NEM whitelisted** Adobe-on (`d8j0ntlcm91z4.cloudfront.net` blocked). Mindig át kell tölteni.
- **transfer_document teljes verbatim** kell — ha kihagysz egy `_links` mezőt vagy `repo:if-match` null-t, akkor `asset_finalize_file_upload` 400-as.
- **Chunk-számolás**: `file_size / repo:blocksize`. Pl. 21884107 / 10485760 = 2.08 → 3 chunk.
- **Parallel upload**: a chunk PUT-ok függetlenek, párhuzamosan futnak. `wait`-tel várni az összes befejezésére mielőtt finalize.
- **Egress disabled environment**: ha `<network_configuration>` `Enabled: false` → `asset_initialize_file_upload` fail-elhet. Fallback: `asset_add_file()` file-picker UI-n keresztül.
- **`shorten_block_upload_urls: true`** (default) — rövidített `at.adobe.com/XYZ` URL-eket ad a hosszú presigned helyett. Context-takarékos, mindig hagyd default true-n.

## Kapcsolódó

- [[adobe-firefly-outpaint-pattern-only]] — Adobe expand use-case
- [[claude-code-harness-blocks]] — harness pattern (Bash + MCP tool mix)

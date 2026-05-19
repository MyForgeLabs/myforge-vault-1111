---
name: GitHub social-preview upload is Web-UI-only
type: wiki
status: stable
created: 2026-05-19
updated: 2026-05-19
lang: en
tags: ["#type/reference", "github", "api-gotcha", "oss-launch", "social-preview"]
related:
  - "[[../06-Audits/2026-05-19 GitHub launch playbook]]"
---

# GitHub social-preview upload is Web-UI-only

The `Settings → Options → Social preview` image upload on a GitHub repository **cannot be done via the API** as of 2026-05-19. It must be performed manually through the web UI.

## What doesn't work

- **REST PATCH** `repos/{owner}/{repo}/social-preview` → 404 Not Found
- **REST PATCH** `repos/{owner}/{repo}` with `social_preview` field → field ignored
- **GraphQL `updateRepository` mutation** → `openGraphImage` is not an input field
- **`gh repo edit` CLI** → no `--social-preview` flag

## What does work — verification

Once the user has uploaded the image via the web UI, verify via:

```bash
# GraphQL — most reliable
gh api graphql -f query='
{
  repository(owner: "<owner>", name: "<repo>") {
    openGraphImageUrl
    usesCustomOpenGraphImage
  }
}'
```

Expected response when uploaded:

```json
{"data":{"repository":{
  "openGraphImageUrl":"https://repository-images.githubusercontent.com/...",
  "usesCustomOpenGraphImage": true
}}}
```

The REST endpoint `GET /repos/{owner}/{repo}` does NOT return the `open_graph_image_url` field reliably — it can be empty even when a custom preview exists. Use GraphQL.

Alternative verification — scrape the rendered repo HTML for the `<meta>` tags:

```bash
curl -sL "https://github.com/<owner>/<repo>" | \
  grep -iE 'og:image|twitter:image'
```

Expect to see both `og:image` and `twitter:image` pointing at the `repository-images.githubusercontent.com` CDN URL.

## The upload flow (user-action)

1. Prepare a PNG / JPG / GIF: **min 640×320**, **recommended 1280×640**, **max 1 MB**.
2. Navigate to `https://github.com/<owner>/<repo>/settings`
3. Scroll to "Social preview" (mid-page under "General")
4. Click "Upload an image..." → choose the file
5. GitHub caches the upload to the `repository-images.githubusercontent.com` CDN immediately

## Why it's not automatable

GitHub's stated reason: the image upload triggers a content-moderation pipeline + dimensions/format validation that is tightly coupled to the web UI. Both internal-search and public-API requests have asked for an API endpoint since 2020; no public release as of 2026-05.

## Impact on launch playbooks

For any OSS-launch checklist, treat social-preview as a **manual gated step** alongside HN-submit and Twitter-thread-post. It cannot be automated end-to-end. Generate the image programmatically (e.g. SVG → PNG via ImageMagick), but the upload requires a human click.

## Composability with launch-readiness audits

A pre-launch audit subagent should:

1. Check the image asset exists in `docs/assets/hero-banner.png` (or equivalent)
2. Verify dimensions + filesize meet GitHub's requirements
3. Verify `gh api graphql … openGraphImageUrl` is non-null (= upload happened)
4. Flag as a stop-the-launch finding if step 3 fails

This is the pattern used in the `2026-05-19 repo improvement audit` for the SV launch.

## Related

- [[../06-Audits/2026-05-19 GitHub launch playbook]] — the broader launch checklist
- [[../06-Audits/2026-05-19 repo improvement audit]] — pre-launch audit pattern
- [[stale-numbers-in-static-artifacts-pattern.en]] — keep the social-preview content fresh

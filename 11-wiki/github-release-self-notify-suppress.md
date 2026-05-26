---
name: GitHub release self-notify-suppress gotcha
type: wiki
created: 2026-05-20
updated: 2026-05-20
tags: ["#type/wiki", "#tool/github", "#topic/oss"]
---

# GitHub release self-notify-suppress gotcha

> [!warning] The trap
> The GitHub Settings → Notifications → Email → **"Your own updates"** checkbox does NOT cover release-publication events. Solo-devs publishing their own releases will NEVER receive a `notifications@github.com` email for their own release, even with the checkbox enabled.

## Symptom

A solo developer publishes `v1.0.10`, expects an email confirmation from `notifications@github.com` to verify the watch-flow (since they Watch their own repo). The email never arrives.

## Diagnosis

The "Your own updates" setting documentation says it covers "updates I performed". This phrasing is misleading — the actual scope is **issue/PR-level self-activity only**:

- ✓ Opening an issue you own → email
- ✓ Commenting on a PR you opened → email
- ✓ Closing your own issue → email
- ✗ **Publishing a release** → NO email
- ✗ Push events → NO email
- ✗ Tag-creation → NO email

GitHub's design: **release-publication is `owner-action`**, and the platform permanently suppresses self-notifications for owner-actions on `Release` events, regardless of any user-toggle.

## How to verify

```bash
# Publish a release
gh release create v1.0.10.test --title "Test" --notes "Notification chain test"

# Wait 2 minutes, then check inbox
# Search for: from:notifications@github.com subject:"v1.0.10"

# Result: zero emails for the release.
```

The forwarding chain (`primary inbox → forwarded address`) is NOT broken — verify by checking CI-failure emails (those DO arrive for self-authored commits that break CI). The release-self-suppress is the only gap.

## Implications for solo-dev OSS workflows

If you rely on email-notifications to monitor your own releases, you'll never get them. Three workarounds:

### Workaround 1 — CI/cron audit (recommended)

A weekly cron-job that compares the latest GitHub-release tag with the latest local-tag and sends an email if they diverge.

```bash
# Pseudo-pseudo:
LATEST_GH_TAG=$(gh release view --json tagName -q .tagName)
LATEST_LOCAL_TAG=$(git describe --tags --abbrev=0)
if [ "$LATEST_GH_TAG" != "$LATEST_LOCAL_TAG" ]; then
  mail-relay "Release diverged: GH=$LATEST_GH_TAG, local=$LATEST_LOCAL_TAG"
fi
```

### Workaround 2 — webhook → email-relay

Set up a webhook on the repo (`Settings → Webhooks → Add webhook`) that fires on `release.published` events. Point it at a small relay-service (e.g. Cloudflare Worker, AWS Lambda) that emails you.

### Workaround 3 — `gh release view` polling

A 5-minute cron that compares the last-seen release with the current one and emails on diff. Works for low-frequency releases.

## What DOES arrive in email (for solo-dev OSS)

Despite the release-self-suppress, these GitHub-events still email the repo-owner:

- **CI failure** on a commit you authored — `notifications@github.com` arrives within ~30 seconds of CI failing
- **@mention** by another user (in any issue/PR/discussion comment)
- **Dependabot security alert** — high-priority, always delivers
- **PR review** on a PR you opened (by another user)
- **Issue comment** on an issue you opened (by another user)

So the watch-flow IS working, just NOT for release-publication.

## Wider lesson

When relying on a platform's notification system, **always test the actual event-type you care about**, not a similar event-type. The gotcha here is that "Your own updates" sounds universal but is specifically about issue/PR activity.

For solo-OSS workflows, this means:
- Build your own release-publication monitoring (cron + diff + email-relay)
- Don't expect platform self-notifications to substitute for application-side monitoring
- The "watch-flow" is for OTHER users to interact with you, NOT for you to interact with yourself

## Empirikus eredmény

- **MyForge Vault 11.11 v1.0.10 release** (2026-05-20):
  - Published at 10:36:38 UTC, Watch-state activated at 10:43:52 UTC
  - 0 emails arrived to forwarded address (`11.11@myforgelabs.com`)
  - Verified the chain works via CI-failure emails (2 arrived earlier for failed commits)
  - Three release attempts (v1.0.10, v1.0.10.1 watch-test, v1.0.10.2 post-`Your own updates` enable) all silent
- Solution: **cron-job email-relay** planned for Sprint-2

## Kapcsolódó

- [[cross-platform-launch-sequencing]] — launch workflow
- [[hn-launch-angle-selection-rubric]] — when releases matter
- GitHub docs: <https://docs.github.com/en/account-and-profile/managing-subscriptions-and-notifications-on-github>

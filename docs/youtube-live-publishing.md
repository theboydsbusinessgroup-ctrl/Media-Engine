# YouTube live publishing

The Media Engine now has a YouTube Data API v3 resumable upload transport.

## Required repository/runtime secrets
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN

The refresh token must come from an OAuth grant for the Google account that owns/manages the intended YouTube channel, with YouTube upload permission.

## Production gate
1. CI must pass.
2. Configure the three secrets in the deployment/runtime (never commit them).
3. Authorize the intended YouTube channel and obtain a refresh token.
4. Run one private upload first and verify the returned video ID in YouTube Studio.
5. Only after that verification enable scheduled/public publishing.

Scheduled uploads must be created as private with a publishAt timestamp. The uploader intentionally fails closed when OAuth is absent.
# Authorization and upload recovery — October 12, 2026

The October 11 publisher rendered successfully but Google rejected its refresh
token with `invalid_grant`. Reauthorize the intended channel with the existing
OAuth client and update the repository's `YOUTUBE_REFRESH_TOKEN` secret directly
in GitHub. Check Google Auth Platform's Audience publishing status first: many
external Testing applications issue refresh tokens that expire after seven days.
Do not share client secrets or refresh tokens in chat or commit them.

Run **YouTube Authorization Check** to verify refresh credentials without uploading.
The scheduled publisher now checks authentication before installing media tools,
generating content or rendering. Completed renders and sanitized authentication
results are retained as seven-day `youtube-recovery` artifacts when upload fails.

After an ambiguous upload failure, inspect the channel before retrying. Download
the retained artifact and use
`python scripts/youtube_upload_rendered.py DIRECTORY --confirm-no-prior-upload`
only after confirming the original did not publish. A saved local receipt prevents
a second upload from that directory. Do not rerun an entire successful publication.

The private diagnostic is manual-only; main-branch pushes no longer upload tests.


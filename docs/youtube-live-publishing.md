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

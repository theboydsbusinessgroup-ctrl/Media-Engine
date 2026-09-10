# Visual production layer

The Media Engine now produces a deterministic asset specification for every approved content draft before any platform publish attempt.

The package includes a visual-generation prompt, concise alt text, and platform variants for Pinterest 2:3, Instagram/Facebook 4:5, Reels/TikTok/YouTube Shorts 9:16, and YouTube thumbnails 16:9.

This layer intentionally distinguishes **asset specification** from **asset generation**. A package is created with `generation_required=true` and `publish_ready=false`. The engine must not claim that an image or video exists until a generation provider returns a verified asset reference and subsequent media QA passes.

This allows discovery, copy generation, visual direction, platform formatting, and QA preparation to continue while production Pinterest publishing remains blocked by platform API access.

# Visual manifest orchestration

The autonomous media cycle now packages visual-production requirements immediately after content QA. Every selected content draft produces a multi-platform asset manifest covering Pinterest, Instagram, TikTok, YouTube, and Facebook formats.

The manifest remains deliberately non-publishing and non-generative: `generation_required=true` and `publish_ready=false` until a separate asset-generation provider returns a verified media artifact and media QA approves it. The existing Pinterest publication step remains a dry-run or gated transport and cannot infer that a visual exists merely because a specification was prepared.

This means the engine can autonomously complete discovery, topic scoring, copy generation, copy QA, visual direction, accessibility text, platform sizing, and packaging while external publishing permissions are unavailable.

# Evidence-backed discovery and generation

Media Engine now supports pluggable discovery and content-generation providers while preserving a safe local fallback.

## Discovery contract
A provider implements `search(query, limit=8)` and returns results with a title, URL, optional excerpt/date, authority score, and freshness score. The engine groups repeated topics, preserves source URLs, scores evidence quality, and passes evidence forward to generation and QA.

## Generation contract
A provider implements `generate(ContentBrief)` and returns title/body plus optional factual claims. The brief includes audience, angle, key evidence-derived points, source URLs, and CTA. If no external generator is configured, the engine uses an evidence-aware deterministic fallback rather than pretending an AI model is active.

## Publication rule
Live Pinterest publishing remains disabled by default. Passing discovery and generation tests creates a dry-run publish intent only. Production transport should be enabled only after credentials, platform policy compliance, duplicate protection, and representative content QA are verified.

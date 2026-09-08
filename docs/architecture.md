# Architecture

## Runtime ownership
The Media Engine is independently deployable and independently operable. It owns all runtime state required to execute its daily content-to-cash loop.

### Domains
- `discovery/` — topic discovery and trend/opportunity ingestion
- `research/` — source collection, evidence extraction, fact checking
- `scoring/` — opportunity and content scoring
- `content/` — ideation, scripting, generation, transformation
- `quality/` — factual, safety, brand, duplicate, and rights checks
- `rendering/` — asset generation and platform-specific formatting
- `publishing/` — platform adapters, scheduling, idempotency, publication state
- `analytics/` — performance metrics and attribution
- `monetization/` — eligibility, payout and attributable revenue tracking
- `orchestration/` — daily loop, retries, backoff, scheduling, recovery
- `integrations/jarvis/` — outbound telemetry adapter only
- `config/` — non-secret configuration and authority policy
- `tests/` — unit, integration, contract, and safety tests

## Data ownership
Media Engine is the source of truth for content, publication records, analytics, monetization records, and platform state. External systems receive only explicitly approved summaries.

## JARVIS boundary
JARVIS is downstream of Media Engine telemetry. No Media Engine runtime request should require JARVIS to be online. JARVIS cannot publish, delete, edit, monetize, or spend on behalf of Media Engine through the telemetry adapter.

## Failure model
- Queue work durably before external publication.
- Generate deterministic/idempotency keys for each intended publication.
- Persist provider response identifiers.
- Retry transient failures with bounded exponential backoff.
- Route ambiguous, policy-sensitive, or repeated failures to human review.
- Never retry a non-idempotent action without checking publication state.
- Keep monetization accounting separate from vanity metrics.

## Revenue model
Track separately:
- platform-native payouts
- ad revenue
- creator-program revenue
- affiliate-attributed revenue
- sponsorship revenue, when explicitly authorized
- product/service revenue attributable to content
- operating/API/rendering costs
- net contribution

The engine optimizes for durable net revenue, not views alone.

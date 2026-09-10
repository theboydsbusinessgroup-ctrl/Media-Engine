# Provider configuration

## Discovery
Default live discovery is `google_news_rss`, which uses public Google News RSS search and requires no API key. It supplies fresh public evidence into the existing discovery contract.

## Generation
OpenRouter is the preferred external generator. The integration has been proven separately with model `inclusionai/ling-3.0-flash-vl:free` at zero generation cost. Repository runtime does not contain or receive the user's API key automatically from external connection tooling.

To enable OpenRouter in an independently deployed Media Engine runtime, configure secrets outside source control:
- `MEDIA_ENGINE_GENERATION_PROVIDER=openrouter`
- `OPENROUTER_API_KEY=<secret>`
- optional `MEDIA_ENGINE_MODEL=inclusionai/ling-3.0-flash-vl:free`

Without those variables, generation deliberately falls back to the evidence-template generator. Live Pinterest publishing remains disabled separately.

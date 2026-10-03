# BehindTheBar revenue distribution

The existing approved offer is the published $9 One Bottle at a Time PDF, Gumroad permalink yknubt. Channel-description traffic uses UTM source youtube, medium channel_description, campaign behindthebar-ebook. New videos use a dated campaign with deterministic spoken CTA and a description link. Shorts links are not assumed clickable: the spoken CTA directs viewers to the channel description. YouTube's separate profile-link settings are not exposed by this API and were not changed.

Publishing retains the existing daily schedule and public privacy setting. Generation is limited to three attempts, with no paid-model fallback. Concurrency serializes publication workflows. Uploads are not blindly retried after uncertain responses: check the provider before rerunning to avoid duplicate videos.

Successful uploads write a sanitized receipt with video ID, timestamp, campaign, privacy, model, and product URL. Workflow artifacts retain it for 90 days; the workflow also archives a validated receipt under data/publications in this repository using its own GitHub token. Existing run IDs cannot be overwritten with conflicting receipts. If branch protection rejects archival, the artifact remains available and the workflow surfaces the failure. Receipts are publication evidence, never sales evidence. No Gumroad/Jarvis integration is introduced.

The live channel description was verified after adding the product link. Product metadata reports a published 51-page PDF, 3.21 MB, with cover and preview. This is not a completed purchase/download test. Gumroad sales, qualified product visits, refunds, and net proceeds still need periodic provider reconciliation; channel views do not establish conversions.

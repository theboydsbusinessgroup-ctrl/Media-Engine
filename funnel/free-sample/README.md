# Free sample landing page

Static landing page for the free "Bottle 1" sample of the ebook "One Bottle at a Time" (Behind The Bar). No build step, no dependencies beyond Google Fonts CSS.

- `index.html`: single file, cover image inlined as a base64 data URI. Collects an email and a legal-drinking-age confirmation.
- `privacy.html`: privacy notice for the email signup (what is collected, MailerLite as processor, unsubscribe and deletion contact).

## MailerLite

Posts (form-urlencoded, via fetch; plain HTML POST fallback without JavaScript) to:

`https://assets.mailerlite.com/jsonp/2654713/forms/201104561033709246/subscribe`

- Account ID: 2654713
- Form ID: 201104561033709246 (embedded form "One Bottle - Free Bottle 1 Sample Signup")
- Fields: `fields[email]`, `ml-submit=1`, `anticsrf=true`
- Group: `One Bottle - Free Bottle 1 Sample` (ID 199388444430960218). The form uses double opt-in. Joining the group triggers the automation `One Bottle - Welcome Series (5 emails)` (ID 199388445643114064; the name says 5 but it holds 3 emails): email 1 at once, email 2 after 2 days, email 3 after 3 more days.
- The success state also links straight to the sample PDF on Google Drive, because the confirmation email was observed landing in Gmail spam on 2026-11-28 (no authenticated sending domain).

Success is detected from `"success": true` in the JSON reply.

## Deploy

Upload both HTML files to any static host. Do not commit secrets; none are needed.

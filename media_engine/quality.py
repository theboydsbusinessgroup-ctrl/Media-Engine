from __future__ import annotations
from urllib.parse import urlparse
from .models import ContentDraft, QAResult

PROHIBITED_PHRASES = {"guaranteed income", "risk-free profit", "secret loophole", "100% guaranteed"}


def review(draft: ContentDraft) -> QAResult:
    reasons = []
    text = f"{draft.title} {draft.body}".lower()
    if len(draft.title.strip()) < 8: reasons.append("title_too_short")
    if len(draft.body.strip()) < 40: reasons.append("body_too_short")
    if any(p in text for p in PROHIBITED_PHRASES): reasons.append("prohibited_claim_language")
    if draft.claims and not draft.evidence_urls: reasons.append("claims_lack_evidence")
    if draft.claims and any(not urlparse(u).scheme.startswith("http") for u in draft.evidence_urls): reasons.append("invalid_evidence_url")
    if len(draft.body) > 500: reasons.append("pinterest_body_too_long")
    if draft.destination_url and not urlparse(draft.destination_url).scheme.startswith("http"): reasons.append("invalid_destination_url")
    score = max(0.0, 1.0 - 0.20 * len(reasons))
    return QAResult(approved=score >= 0.85 and not reasons, score=round(score, 2), reasons=reasons)

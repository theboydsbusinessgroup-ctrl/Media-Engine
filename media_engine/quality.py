from __future__ import annotations
from .models import ContentDraft, QAResult

PROHIBITED_PHRASES = {"guaranteed income", "risk-free profit", "secret loophole", "100% guaranteed"}


def review(draft: ContentDraft) -> QAResult:
    reasons = []
    text = f"{draft.title} {draft.body}".lower()
    if len(draft.title.strip()) < 8:
        reasons.append("title_too_short")
    if len(draft.body.strip()) < 40:
        reasons.append("body_too_short")
    if any(p in text for p in PROHIBITED_PHRASES):
        reasons.append("prohibited_claim_language")
    if draft.claims and not draft.rights_sources:
        reasons.append("claims_lack_evidence")
    score = max(0.0, 1.0 - 0.25 * len(reasons))
    return QAResult(approved=score >= 0.85 and not reasons, score=round(score, 2), reasons=reasons)

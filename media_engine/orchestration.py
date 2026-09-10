from __future__ import annotations
from .analytics import AnalyticsStore
from .content import generate_pinterest_draft
from .discovery import normalize_candidates
from .publishing import PinterestAdapter
from .quality import review
from .scoring import opportunity_score


class MediaLoop:
    def __init__(self, *, publisher: PinterestAdapter | None = None, analytics: AnalyticsStore | None = None):
        self.publisher = publisher or PinterestAdapter(dry_run=True)
        self.analytics = analytics or AnalyticsStore()

    def run_once(self, candidates: list[dict], destination_url: str | None = None) -> dict:
        topics = normalize_candidates(candidates)
        if not topics:
            return {"status": "no_candidates", "published": False}
        ranked = sorted(topics, key=opportunity_score, reverse=True)
        winner = ranked[0]
        draft = generate_pinterest_draft(winner, destination_url)
        qa = review(draft)
        publication = self.publisher.publish(draft, qa)
        return {
            "status": "publish_intent" if qa.approved else "qa_rejected",
            "platform": "pinterest",
            "topic_id": winner.topic_id,
            "opportunity_score": opportunity_score(winner),
            "content_id": draft.content_id,
            "qa": {"approved": qa.approved, "score": qa.score, "reasons": qa.reasons},
            "publication": {
                "published": publication.published,
                "dry_run": publication.dry_run,
                "idempotency_key": publication.idempotency_key,
                "reason": publication.reason,
            },
        }

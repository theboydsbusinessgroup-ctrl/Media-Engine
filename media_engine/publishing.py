from __future__ import annotations
import hashlib
from .models import ContentDraft, PublishResult, QAResult


class PinterestAdapter:
    def __init__(self, *, dry_run: bool = True):
        self.dry_run = dry_run
        self._published: dict[str, PublishResult] = {}

    @staticmethod
    def key(draft: ContentDraft) -> str:
        return hashlib.sha256(f"pinterest:{draft.content_id}".encode()).hexdigest()

    def publish(self, draft: ContentDraft, qa: QAResult) -> PublishResult:
        key = self.key(draft)
        if key in self._published:
            return self._published[key]
        if not qa.approved:
            result = PublishResult(False, self.dry_run, key, reason="qa_rejected")
        elif self.dry_run:
            result = PublishResult(False, True, key, reason="dry_run_publish_intent_created")
        else:
            raise RuntimeError("Live Pinterest transport is not configured; refusing implicit publication")
        self._published[key] = result
        return result

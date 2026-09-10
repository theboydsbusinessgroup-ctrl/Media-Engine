from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from ..models import ContentDraft, PublishResult, QAResult


@dataclass(frozen=True)
class PinterestTarget:
    board_id: str
    board_name: str
    category: str
    media_url: str
    alt_text: str


class GatedPinterestTransport:
    """Live Pinterest transport boundary.

    The actual API call is injected so credentials stay outside the repository.
    Publication requires QA approval, an explicit content/board category match,
    and a public media URL. This class does not bypass platform access rules.
    """

    def __init__(self, create_pin: Callable[[dict[str, Any]], dict[str, Any]]):
        self.create_pin = create_pin
        self._sent: dict[str, PublishResult] = {}

    def publish(self, draft: ContentDraft, qa: QAResult, *, content_category: str, target: PinterestTarget) -> PublishResult:
        key = f"pinterest:{target.board_id}:{draft.content_id}"
        if key in self._sent:
            return self._sent[key]
        if not qa.approved:
            result = PublishResult(False, False, key, reason="qa_rejected")
        elif content_category != target.category:
            result = PublishResult(False, False, key, reason="board_category_mismatch")
        elif not target.media_url.startswith("https://"):
            result = PublishResult(False, False, key, reason="public_https_media_required")
        else:
            response = self.create_pin({
                "board_id": target.board_id,
                "title": draft.title,
                "description": draft.body,
                "link": draft.destination_url,
                "alt_text": target.alt_text,
                "media_source": {"source_type":"image_url","url":target.media_url},
            })
            pin_id = str(response.get("id") or response.get("pin_id") or "")
            if not pin_id:
                raise ValueError("Pinterest transport did not return a Pin ID")
            result = PublishResult(True, False, key, provider_post_id=pin_id)
        self._sent[key] = result
        return result

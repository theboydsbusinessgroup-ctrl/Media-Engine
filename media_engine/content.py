from __future__ import annotations
import hashlib
from .models import Topic, ContentDraft


def generate_pinterest_draft(topic: Topic, destination_url: str | None = None) -> ContentDraft:
    cid = hashlib.sha256(f"pinterest|{topic.topic_id}".encode()).hexdigest()[:18]
    title = topic.title[:100]
    body = (
        f"A practical guide to {topic.title.lower()} for {topic.audience}. "
        "Save this for later and use it as a starting point for your own plan."
    )
    return ContentDraft(content_id=cid, topic_id=topic.topic_id, title=title, body=body, destination_url=destination_url)

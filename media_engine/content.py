from __future__ import annotations
import hashlib
from typing import Protocol
from .models import Topic, ContentDraft, ContentBrief


class ContentGenerator(Protocol):
    def generate(self, brief: ContentBrief) -> dict: ...


def build_brief(topic: Topic, destination_url: str | None = None) -> ContentBrief:
    evidence_urls = [e.url for e in topic.evidence[:5]]
    key_points = [e.excerpt.strip() for e in topic.evidence if e.excerpt.strip()][:3]
    if not key_points:
        key_points = [f"Explain {topic.title.lower()} in practical terms", "Give the reader an actionable next step"]
    return ContentBrief(
        topic_id=topic.topic_id,
        angle=f"Practical, useful guidance on {topic.title.lower()}",
        audience=topic.audience,
        promise=f"Help {topic.audience} understand and act on {topic.title.lower()}",
        key_points=key_points,
        evidence_urls=evidence_urls,
        cta="Save this for later" if not destination_url else "Save this and use the linked resource when you're ready",
    )


def _fallback_generate(brief: ContentBrief) -> dict:
    points = " ".join(p.rstrip('. ') + "." for p in brief.key_points[:3])
    return {
        "title": brief.angle.replace("Practical, useful guidance on ", "").title()[:100],
        "body": f"{brief.promise}. {points} {brief.cta}.",
        "claims": [],
    }


def generate_pinterest_draft(topic: Topic, destination_url: str | None = None, generator: ContentGenerator | None = None) -> ContentDraft:
    brief = build_brief(topic, destination_url)
    generated = generator.generate(brief) if generator else _fallback_generate(brief)
    cid = hashlib.sha256(f"pinterest|{topic.topic_id}|{generated.get('title','')}".encode()).hexdigest()[:18]
    return ContentDraft(
        content_id=cid, topic_id=topic.topic_id,
        title=str(generated.get("title") or topic.title)[:100],
        body=str(generated.get("body") or ""), destination_url=destination_url,
        claims=[str(x) for x in generated.get("claims", [])],
        rights_sources=[str(x) for x in generated.get("rights_sources", [])],
        evidence_urls=brief.evidence_urls,
        generation_method="external_generator" if generator else "evidence_template",
    )

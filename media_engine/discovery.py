from __future__ import annotations
import hashlib
from .models import Topic


def topic_id(title: str, audience: str) -> str:
    return hashlib.sha256(f"{title}|{audience}".encode()).hexdigest()[:16]


def normalize_candidates(candidates: list[dict]) -> list[Topic]:
    topics = []
    for c in candidates:
        title = str(c["title"]).strip()
        audience = str(c.get("audience") or "general").strip()
        topics.append(Topic(
            topic_id=topic_id(title, audience),
            title=title,
            audience=audience,
            source=str(c.get("source") or "manual_seed"),
            evidence_score=float(c.get("evidence_score", 0)),
            evergreen_score=float(c.get("evergreen_score", 0)),
            monetization_score=float(c.get("monetization_score", 0)),
            risk_score=float(c.get("risk_score", 0)),
        ))
    return topics

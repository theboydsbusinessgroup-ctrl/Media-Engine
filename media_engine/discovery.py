from __future__ import annotations
import hashlib
from typing import Protocol
from .models import Evidence, Topic


class DiscoveryProvider(Protocol):
    def search(self, query: str, *, limit: int = 8) -> list[dict]: ...


def topic_id(title: str, audience: str) -> str:
    return hashlib.sha256(f"{title}|{audience}".encode()).hexdigest()[:16]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def evidence_score(items: list[Evidence]) -> float:
    if not items:
        return 0.0
    strongest = sorted((0.6 * e.authority_score + 0.4 * e.freshness_score for e in items), reverse=True)[:3]
    diversity_bonus = min(len({e.url.split('/')[2] if '://' in e.url else e.url for e in items}) / 3.0, 1.0) * 0.15
    return round(_clamp(sum(strongest) / len(strongest) + diversity_bonus), 4)


def discover_topics(provider: DiscoveryProvider, queries: list[str], *, audience: str, evergreen_score: float = 0.6, monetization_score: float = 0.5) -> list[Topic]:
    grouped: dict[str, list[Evidence]] = {}
    for query in queries:
        for result in provider.search(query, limit=8):
            title = str(result.get("title") or "").strip()
            url = str(result.get("url") or "").strip()
            if not title or not url:
                continue
            key = title.lower()
            grouped.setdefault(key, []).append(Evidence(
                url=url,
                title=title,
                excerpt=str(result.get("excerpt") or "")[:500],
                published_at=result.get("published_at"),
                authority_score=_clamp(result.get("authority_score", 0.5)),
                freshness_score=_clamp(result.get("freshness_score", 0.5)),
            ))
    topics = []
    for _, items in grouped.items():
        title = items[0].title
        topics.append(Topic(
            topic_id=topic_id(title, audience), title=title, audience=audience,
            source="evidence_discovery", evidence_score=evidence_score(items),
            evergreen_score=_clamp(evergreen_score), monetization_score=_clamp(monetization_score),
            evidence=items,
        ))
    return topics


def normalize_candidates(candidates: list[dict]) -> list[Topic]:
    topics = []
    for c in candidates:
        title = str(c["title"]).strip()
        audience = str(c.get("audience") or "general").strip()
        raw_evidence = c.get("evidence") or []
        evidence = [Evidence(**e) if isinstance(e, dict) else e for e in raw_evidence]
        topics.append(Topic(
            topic_id=topic_id(title, audience), title=title, audience=audience,
            source=str(c.get("source") or "manual_seed"),
            evidence_score=float(c.get("evidence_score", evidence_score(evidence))),
            evergreen_score=float(c.get("evergreen_score", 0)),
            monetization_score=float(c.get("monetization_score", 0)),
            risk_score=float(c.get("risk_score", 0)), evidence=evidence,
        ))
    return topics

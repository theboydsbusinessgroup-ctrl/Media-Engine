from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class Topic:
    topic_id: str
    title: str
    audience: str
    source: str
    evidence_score: float
    evergreen_score: float
    monetization_score: float
    risk_score: float = 0.0

@dataclass
class ContentDraft:
    content_id: str
    topic_id: str
    title: str
    body: str
    destination_url: str | None = None
    claims: list[str] = field(default_factory=list)
    rights_sources: list[str] = field(default_factory=list)

@dataclass
class QAResult:
    approved: bool
    score: float
    reasons: list[str] = field(default_factory=list)

@dataclass
class PublishResult:
    published: bool
    dry_run: bool
    idempotency_key: str
    provider_post_id: str | None = None
    reason: str | None = None

@dataclass
class Performance:
    impressions: int = 0
    clicks: int = 0
    saves: int = 0
    conversions: int = 0
    revenue: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

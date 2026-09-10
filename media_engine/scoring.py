from __future__ import annotations
from .models import Topic, Performance


def opportunity_score(topic: Topic) -> float:
    score = 0.35 * topic.evidence_score + 0.25 * topic.evergreen_score + 0.40 * topic.monetization_score - 0.50 * topic.risk_score
    return round(max(0.0, min(1.0, score)), 4)


def performance_score(p: Performance) -> float:
    ctr = p.clicks / p.impressions if p.impressions else 0.0
    save_rate = p.saves / p.impressions if p.impressions else 0.0
    conversion_rate = p.conversions / p.clicks if p.clicks else 0.0
    revenue_signal = min(p.revenue / 100.0, 1.0)
    return round(min(1.0, ctr * 4 + save_rate * 2 + conversion_rate * 3 + revenue_signal * 0.5), 4)

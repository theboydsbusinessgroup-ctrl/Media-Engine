from __future__ import annotations
from .models import Performance
from .scoring import performance_score


class AnalyticsStore:
    def __init__(self):
        self._metrics: dict[str, Performance] = {}

    def ingest(self, content_id: str, metrics: dict) -> Performance:
        p = Performance(
            impressions=max(0, int(metrics.get("impressions", 0))),
            clicks=max(0, int(metrics.get("clicks", 0))),
            saves=max(0, int(metrics.get("saves", 0))),
            conversions=max(0, int(metrics.get("conversions", 0))),
            revenue=max(0.0, float(metrics.get("revenue", 0))),
        )
        self._metrics[content_id] = p
        return p

    def learning_signal(self, content_id: str) -> float:
        return performance_score(self._metrics.get(content_id, Performance()))

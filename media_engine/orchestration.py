from __future__ import annotations
from .analytics import AnalyticsStore
from .asset_manifest import build_manifest
from .asset_quality import review_asset_package
from .assets import package_assets
from .content import generate_pinterest_draft, ContentGenerator
from .discovery import normalize_candidates, discover_topics, DiscoveryProvider
from .publishing import PinterestAdapter
from .quality import review
from .scoring import opportunity_score
from .visual_assets import DisabledVisualAssetProvider, VisualAssetProvider, verify_generated_asset


class MediaLoop:
    def __init__(self, *, publisher: PinterestAdapter | None = None, analytics: AnalyticsStore | None = None, generator: ContentGenerator | None = None, asset_provider: VisualAssetProvider | None = None):
        self.publisher = publisher or PinterestAdapter(dry_run=True)
        self.analytics = analytics or AnalyticsStore()
        self.generator = generator
        self.asset_provider = asset_provider or DisabledVisualAssetProvider()

    def run_once(self, candidates: list[dict], destination_url: str | None = None) -> dict:
        return self._execute(normalize_candidates(candidates), destination_url)

    def run_discovery(self, provider: DiscoveryProvider, queries: list[str], *, audience: str, destination_url: str | None = None, evergreen_score: float = 0.6, monetization_score: float = 0.5) -> dict:
        topics = discover_topics(provider, queries, audience=audience, evergreen_score=evergreen_score, monetization_score=monetization_score)
        return self._execute(topics, destination_url)

    def _execute(self, topics, destination_url):
        if not topics:
            return {"status":"no_candidates","published":False}
        winner = sorted(topics, key=opportunity_score, reverse=True)[0]
        draft = generate_pinterest_draft(winner, destination_url, self.generator)
        qa = review(draft)
        asset_package = package_assets(draft)
        asset_qa = review_asset_package(asset_package)
        pinterest_variant = next(v for v in asset_package.variants if v.platform == "pinterest" and v.placement == "standard_pin")
        generated_asset = self.asset_provider.generate(asset_package, pinterest_variant) if qa.approved and asset_qa.approved else None
        media_asset_qa = verify_generated_asset(generated_asset, asset_package, pinterest_variant)
        asset_manifest = build_manifest(draft, qa, asset_package, asset_qa, generated_asset, media_asset_qa)
        publication = self.publisher.publish(draft, qa)
        return {
            "status":"publish_intent" if qa.approved else "qa_rejected",
            "platform":"pinterest",
            "topic_id":winner.topic_id,
            "topic_title":winner.title,
            "opportunity_score":opportunity_score(winner),
            "evidence_count":len(winner.evidence),
            "content_id":draft.content_id,
            "generation_method":draft.generation_method,
            "qa":{"approved":qa.approved,"score":qa.score,"reasons":qa.reasons},
            "assets":asset_manifest,
            "publication":{"published":publication.published,"dry_run":publication.dry_run,"idempotency_key":publication.idempotency_key,"reason":publication.reason},
        }

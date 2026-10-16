import unittest
from unittest.mock import Mock, patch
from media_engine.analytics import AnalyticsStore
from media_engine.models import ContentDraft, PublishResult
from media_engine.orchestration import MediaLoop
from media_engine.publishing import PinterestAdapter
from media_engine.quality import review
from media_engine.visual_assets import GeneratedAsset


class MediaLoopTests(unittest.TestCase):
    def candidates(self):
        return [
            {"title":"Evergreen business planning checklist","audience":"small business owners","evidence_score":0.7,"evergreen_score":0.9,"monetization_score":0.8,"risk_score":0.05},
            {"title":"Weak candidate","audience":"general","evidence_score":0.2,"evergreen_score":0.2,"monetization_score":0.1,"risk_score":0.4},
        ]

    def test_complete_cycle_creates_safe_dry_run_publish_intent(self):
        result = MediaLoop().run_once(self.candidates(), "https://example.com")
        self.assertEqual(result["platform"], "pinterest")
        self.assertTrue(result["qa"]["approved"])
        self.assertTrue(result["publication"]["dry_run"])
        self.assertFalse(result["publication"]["published"])

    def test_complete_cycle_emits_visual_manifest_without_claiming_asset_exists(self):
        result = MediaLoop().run_once(self.candidates(), "https://example.com")
        assets = result["assets"]
        self.assertTrue(assets["asset_qa"]["approved"])
        self.assertTrue(assets["generation_required"])
        self.assertFalse(assets["publish_ready"])
        self.assertEqual(assets["truth_rule"], "asset_specification_is_not_a_generated_or_published_asset")
        shapes = {(v["platform"], v["aspect_ratio"]) for v in assets["visual"]["variants"]}
        self.assertIn(("pinterest", "2:3"), shapes)
        self.assertIn(("instagram", "9:16"), shapes)
        self.assertIn(("tiktok", "9:16"), shapes)
        self.assertIn(("youtube", "16:9"), shapes)

    def test_publish_is_idempotent(self):
        adapter = PinterestAdapter(dry_run=True)
        draft = ContentDraft("c1","t1","Useful business checklist","A sufficiently detailed and useful body for a practical business checklist.")
        qa = review(draft)
        a = adapter.publish(draft, qa)
        b = adapter.publish(draft, qa)
        self.assertEqual(a.idempotency_key, b.idempotency_key)
        self.assertEqual(a.reason, b.reason)

    def test_unsafe_claim_is_rejected(self):
        draft = ContentDraft("c2","t2","Guaranteed income formula","This is a guaranteed income approach that promises risk-free profit.")
        qa = review(draft)
        self.assertFalse(qa.approved)

    def test_live_publisher_is_not_called_without_verified_asset(self):
        publisher = Mock(dry_run=False)
        result = MediaLoop(publisher=publisher).run_once(self.candidates())
        publisher.publish.assert_not_called()
        self.assertFalse(result["publication"]["published"])
        self.assertEqual(result["publication"]["reason"], "assets_not_publish_ready")

    def test_live_publisher_receives_only_asset_verified_content(self):
        publisher = Mock(dry_run=False)
        publisher.publish.return_value = PublishResult(True, False, "fixture", provider_post_id="pin-1")
        provider = Mock()
        provider.generate.side_effect = lambda package, variant: GeneratedAsset(
            package.content_id, "fixture", "https://example.org/image.png", "image/png",
            variant.width, variant.height, "a" * 64, variant.platform, variant.placement)
        result = MediaLoop(publisher=publisher, asset_provider=provider).run_once(self.candidates())
        publisher.publish.assert_called_once()
        self.assertTrue(result["assets"]["publish_ready"])
        self.assertEqual(result["status"], "published")

    def test_invalid_asset_cannot_reach_live_publisher(self):
        publisher = Mock(dry_run=False)
        provider = Mock()
        provider.generate.side_effect = lambda package, variant: GeneratedAsset(
            package.content_id, "fixture", "https://example.org/image.png", "image/png",
            1, 1, "bad-checksum", variant.platform, variant.placement)
        result = MediaLoop(publisher=publisher, asset_provider=provider).run_once(self.candidates())
        publisher.publish.assert_not_called()
        self.assertFalse(result["assets"]["publish_ready"])

    def test_malformed_http_urls_fail_quality_review(self):
        for url in ["httpx://example.com", "https:///missing-host", "http:"]:
            with self.subTest(url=url):
                draft = ContentDraft("c3", "t3", "Useful business checklist",
                    "A sufficiently detailed body for a useful practical checklist.",
                    destination_url=url, claims=["claim"], evidence_urls=[url])
                qa = review(draft)
                self.assertIn("invalid_evidence_url", qa.reasons)
                self.assertIn("invalid_destination_url", qa.reasons)

    def test_metrics_generate_learning_signal(self):
        store = AnalyticsStore()
        store.ingest("c1", {"impressions":1000,"clicks":40,"saves":25,"conversions":3,"revenue":29})
        self.assertGreater(store.learning_signal("c1"), 0)


if __name__ == "__main__":
    unittest.main()

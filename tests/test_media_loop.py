import unittest
from media_engine.analytics import AnalyticsStore
from media_engine.models import ContentDraft
from media_engine.orchestration import MediaLoop
from media_engine.publishing import PinterestAdapter
from media_engine.quality import review


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

    def test_metrics_generate_learning_signal(self):
        store = AnalyticsStore()
        store.ingest("c1", {"impressions":1000,"clicks":40,"saves":25,"conversions":3,"revenue":29})
        self.assertGreater(store.learning_signal("c1"), 0)


if __name__ == "__main__":
    unittest.main()

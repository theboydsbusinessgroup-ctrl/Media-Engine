import unittest
from media_engine.assets import PLATFORM_VARIANTS, package_assets
from media_engine.asset_quality import review_asset_package
from media_engine.asset_manifest import build_manifest
from media_engine.models import ContentDraft
from media_engine.quality import review


class AssetPackagingTests(unittest.TestCase):
    def draft(self):
        return ContentDraft(
            "content-1",
            "topic-1",
            "Contractor Pricing Checklist",
            "A practical checklist for reviewing pricing, scope, and margin before sending a customer quote.",
            evidence_urls=["https://example.org/source"],
        )

    def test_platform_variants_cover_primary_social_shapes(self):
        shapes = {(v.platform, v.aspect_ratio) for v in PLATFORM_VARIANTS}
        self.assertIn(("pinterest", "2:3"), shapes)
        self.assertIn(("instagram", "9:16"), shapes)
        self.assertIn(("tiktok", "9:16"), shapes)
        self.assertIn(("youtube", "16:9"), shapes)
        self.assertIn(("facebook", "4:5"), shapes)

    def test_asset_package_has_prompt_alt_text_and_passes_spec_qa(self):
        package = package_assets(self.draft())
        qa = review_asset_package(package)
        self.assertTrue(qa.approved)
        self.assertTrue(package.generation_required)
        self.assertFalse(package.publish_ready)
        self.assertLessEqual(len(package.alt_text), 180)

    def test_manifest_does_not_claim_asset_generated_or_publish_ready(self):
        draft = self.draft()
        content_qa = review(draft)
        package = package_assets(draft)
        asset_qa = review_asset_package(package)
        manifest = build_manifest(draft, content_qa, package, asset_qa)
        self.assertTrue(content_qa.approved)
        self.assertTrue(asset_qa.approved)
        self.assertTrue(manifest["generation_required"])
        self.assertFalse(manifest["publish_ready"])
        self.assertEqual(manifest["truth_rule"], "asset_specification_is_not_a_generated_or_published_asset")


if __name__ == "__main__":
    unittest.main()

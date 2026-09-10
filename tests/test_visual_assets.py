import unittest
from media_engine.assets import package_assets
from media_engine.models import ContentDraft
from media_engine.visual_assets import GeneratedAsset, DisabledVisualAssetProvider, verify_generated_asset


class VisualAssetProviderTests(unittest.TestCase):
    def setUp(self):
        self.package = package_assets(ContentDraft("c1", "t1", "Useful business checklist", "A sufficiently detailed body for testing visual asset generation."))
        self.variant = next(v for v in self.package.variants if v.platform == "pinterest")

    def test_disabled_provider_never_claims_generation(self):
        asset = DisabledVisualAssetProvider().generate(self.package, self.variant)
        qa = verify_generated_asset(asset, self.package, self.variant)
        self.assertFalse(qa.approved)
        self.assertIn("generated_asset_missing", qa.reasons)

    def test_verified_asset_requires_exact_variant_and_checksum(self):
        asset = GeneratedAsset(
            content_id=self.package.content_id,
            provider="fixture",
            uri="https://example.com/asset.png",
            media_type="image/png",
            width=self.variant.width,
            height=self.variant.height,
            checksum_sha256="a" * 64,
            platform=self.variant.platform,
            placement=self.variant.placement,
        )
        qa = verify_generated_asset(asset, self.package, self.variant)
        self.assertTrue(qa.approved)


if __name__ == "__main__":
    unittest.main()

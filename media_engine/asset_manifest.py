from __future__ import annotations
from .assets import AssetPackage
from .asset_quality import AssetQAResult
from .models import ContentDraft, QAResult
from .visual_assets import GeneratedAsset, MediaAssetQAResult


def build_manifest(
    draft: ContentDraft,
    content_qa: QAResult,
    package: AssetPackage,
    asset_qa: AssetQAResult,
    generated_asset: GeneratedAsset | None = None,
    media_asset_qa: MediaAssetQAResult | None = None,
) -> dict:
    generated_verified = bool(generated_asset and media_asset_qa and media_asset_qa.approved)
    ready = bool(content_qa.approved and asset_qa.approved and generated_verified)
    return {
        "schema_version": "1.1",
        "content_id": draft.content_id,
        "asset_package_id": package.package_id,
        "generation_method": draft.generation_method,
        "content_qa": {"approved": content_qa.approved, "score": content_qa.score, "reasons": content_qa.reasons},
        "asset_qa": {"approved": asset_qa.approved, "score": asset_qa.score, "reasons": asset_qa.reasons},
        "media_asset_qa": None if media_asset_qa is None else {"approved": media_asset_qa.approved, "score": media_asset_qa.score, "reasons": media_asset_qa.reasons},
        "visual": {
            "prompt": package.visual_prompt,
            "alt_text": package.alt_text,
            "variants": [
                {"platform": v.platform, "placement": v.placement, "width": v.width, "height": v.height, "aspect_ratio": v.aspect_ratio, "title_safe_chars": v.title_safe_chars}
                for v in package.variants
            ],
        },
        "generated_asset": None if generated_asset is None else {
            "provider": generated_asset.provider,
            "uri": generated_asset.uri,
            "media_type": generated_asset.media_type,
            "width": generated_asset.width,
            "height": generated_asset.height,
            "checksum_sha256": generated_asset.checksum_sha256,
            "platform": generated_asset.platform,
            "placement": generated_asset.placement,
        },
        "generation_required": not generated_verified,
        "publish_ready": ready,
        "truth_rule": "asset_specification_is_not_a_generated_or_published_asset",
        "provider_truth_rule": "publish_ready_requires_a_provider_asset_that_passes_media_asset_qa",
    }

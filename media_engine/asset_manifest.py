from __future__ import annotations
from .assets import AssetPackage
from .asset_quality import AssetQAResult
from .models import ContentDraft, QAResult


def build_manifest(draft: ContentDraft, content_qa: QAResult, package: AssetPackage, asset_qa: AssetQAResult) -> dict:
    ready = bool(content_qa.approved and asset_qa.approved and not package.generation_required)
    return {
        "schema_version": "1.0",
        "content_id": draft.content_id,
        "asset_package_id": package.package_id,
        "generation_method": draft.generation_method,
        "content_qa": {"approved": content_qa.approved, "score": content_qa.score, "reasons": content_qa.reasons},
        "asset_qa": {"approved": asset_qa.approved, "score": asset_qa.score, "reasons": asset_qa.reasons},
        "visual": {
            "prompt": package.visual_prompt,
            "alt_text": package.alt_text,
            "variants": [
                {
                    "platform": v.platform,
                    "placement": v.placement,
                    "width": v.width,
                    "height": v.height,
                    "aspect_ratio": v.aspect_ratio,
                    "title_safe_chars": v.title_safe_chars,
                }
                for v in package.variants
            ],
        },
        "generation_required": package.generation_required,
        "publish_ready": ready,
        "truth_rule": "asset_specification_is_not_a_generated_or_published_asset",
    }

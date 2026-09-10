from __future__ import annotations
from dataclasses import dataclass, field
from .assets import AssetPackage


@dataclass(frozen=True)
class AssetQAResult:
    approved: bool
    score: float
    reasons: list[str] = field(default_factory=list)


def review_asset_package(package: AssetPackage) -> AssetQAResult:
    reasons: list[str] = []
    if len(package.visual_prompt.strip()) < 80:
        reasons.append("visual_prompt_too_short")
    if not package.alt_text.strip():
        reasons.append("alt_text_missing")
    if len(package.alt_text) > 180:
        reasons.append("alt_text_too_long")
    if not package.variants:
        reasons.append("platform_variants_missing")
    seen = set()
    for variant in package.variants:
        key = (variant.platform, variant.placement)
        if key in seen:
            reasons.append("duplicate_platform_variant")
        seen.add(key)
        if variant.width <= 0 or variant.height <= 0:
            reasons.append("invalid_dimensions")
        if ":" not in variant.aspect_ratio:
            reasons.append("invalid_aspect_ratio")
    score = max(0.0, 1.0 - 0.2 * len(set(reasons)))
    return AssetQAResult(approved=not reasons, score=round(score, 2), reasons=sorted(set(reasons)))

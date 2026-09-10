from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol
import hashlib

from .assets import AssetPackage, VisualVariant


@dataclass(frozen=True)
class GeneratedAsset:
    content_id: str
    provider: str
    uri: str
    media_type: str
    width: int
    height: int
    checksum_sha256: str
    platform: str
    placement: str


@dataclass(frozen=True)
class MediaAssetQAResult:
    approved: bool
    score: float
    reasons: list[str] = field(default_factory=list)


class VisualAssetProvider(Protocol):
    def generate(self, package: AssetPackage, variant: VisualVariant) -> GeneratedAsset | None:
        ...


class DisabledVisualAssetProvider:
    """Safe default: generation is unavailable until a real provider is explicitly wired."""

    name = "disabled"

    def generate(self, package: AssetPackage, variant: VisualVariant) -> GeneratedAsset | None:
        return None


def verify_generated_asset(asset: GeneratedAsset | None, package: AssetPackage, variant: VisualVariant) -> MediaAssetQAResult:
    reasons: list[str] = []
    if asset is None:
        return MediaAssetQAResult(False, 0.0, ["generated_asset_missing"])
    if asset.content_id != package.content_id:
        reasons.append("content_id_mismatch")
    if not asset.provider.strip():
        reasons.append("provider_missing")
    if not asset.uri.strip():
        reasons.append("asset_uri_missing")
    if not asset.media_type.startswith("image/"):
        reasons.append("unsupported_media_type")
    if (asset.width, asset.height) != (variant.width, variant.height):
        reasons.append("dimension_mismatch")
    if asset.platform != variant.platform or asset.placement != variant.placement:
        reasons.append("variant_identity_mismatch")
    checksum = asset.checksum_sha256.lower().strip()
    if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
        reasons.append("invalid_checksum")
    score = max(0.0, 1.0 - 0.2 * len(set(reasons)))
    return MediaAssetQAResult(not reasons, round(score, 2), sorted(set(reasons)))


def checksum_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

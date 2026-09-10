from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
from .models import ContentDraft


@dataclass(frozen=True)
class VisualVariant:
    platform: str
    placement: str
    width: int
    height: int
    aspect_ratio: str
    title_safe_chars: int


@dataclass(frozen=True)
class AssetPackage:
    package_id: str
    content_id: str
    visual_prompt: str
    alt_text: str
    variants: tuple[VisualVariant, ...]
    generation_required: bool = True
    publish_ready: bool = False

    def as_dict(self) -> dict:
        data = asdict(self)
        data["variants"] = [asdict(v) for v in self.variants]
        return data


PLATFORM_VARIANTS = (
    VisualVariant("pinterest", "standard_pin", 1000, 1500, "2:3", 70),
    VisualVariant("instagram", "feed_portrait", 1080, 1350, "4:5", 70),
    VisualVariant("instagram", "reel", 1080, 1920, "9:16", 55),
    VisualVariant("tiktok", "video", 1080, 1920, "9:16", 55),
    VisualVariant("youtube", "short", 1080, 1920, "9:16", 55),
    VisualVariant("youtube", "thumbnail", 1280, 720, "16:9", 45),
    VisualVariant("facebook", "feed_portrait", 1080, 1350, "4:5", 70),
)


def build_visual_prompt(draft: ContentDraft) -> str:
    title = draft.title.strip()
    return (
        "Create a clean editorial social-media visual supporting this idea: "
        f"{title}. Use strong visual hierarchy, one clear focal concept, spacious composition, "
        "high legibility on a phone, and no fabricated statistics, logos, watermarks, or claims. "
        "Do not render long paragraphs; reserve text treatment for a short headline only."
    )


def build_alt_text(draft: ContentDraft) -> str:
    title = draft.title.strip().rstrip(".")
    return f"Editorial graphic illustrating {title.lower()} with a clean, mobile-readable layout."[:180]


def package_assets(draft: ContentDraft) -> AssetPackage:
    package_id = hashlib.sha256(f"assets:{draft.content_id}".encode()).hexdigest()[:20]
    return AssetPackage(
        package_id=package_id,
        content_id=draft.content_id,
        visual_prompt=build_visual_prompt(draft),
        alt_text=build_alt_text(draft),
        variants=PLATFORM_VARIANTS,
    )

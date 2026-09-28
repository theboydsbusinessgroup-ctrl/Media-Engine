from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from media_engine.providers.youtube_publisher import YouTubePublisher


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/youtube_private_smoke.py <video.mp4>", file=sys.stderr)
        return 2

    video_path = Path(sys.argv[1])
    if not video_path.is_file():
        print(f"video file not found: {video_path}", file=sys.stderr)
        return 2

    required = ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("missing required YouTube OAuth secrets: " + ", ".join(missing), file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    publisher = YouTubePublisher()
    result = publisher.upload(
        video_path,
        title=f"Media Engine OAuth Smoke Test — {stamp}",
        description=(
            "Automated private upload used only to verify the Media Engine YouTube OAuth transport. "
            "This video is intentionally private."
        ),
        privacy_status="private",
    )
    print(json.dumps({"status": "ok", "privacy": "private", "video_id": result.video_id, "url": result.url}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

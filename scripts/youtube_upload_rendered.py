"""Upload a retained Short once, after checking YouTube for a prior upload."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media_engine.monetization import publication_receipt
from media_engine.providers.youtube_publisher import YouTubePublisher


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--confirm-no-prior-upload", action="store_true", required=True)
    args = parser.parse_args()
    receipt_path = args.directory / "publication.json"
    if receipt_path.exists():
        parser.error("A publication receipt already exists. Do not upload again.")
    metadata = json.loads((args.directory / "upload.json").read_text())
    video = args.directory / "short.mp4"
    if not video.is_file() or video.stat().st_size < 250_000:
        parser.error("Retained Short is missing or unexpectedly small.")
    if metadata.get("privacy_status") not in {"private", "unlisted", "public"}:
        parser.error("The retained metadata must specify a valid privacy status.")
    publisher = YouTubePublisher()
    publisher.preflight()
    result = publisher.upload(video, title=metadata["title"], description=metadata["description"],
                              tags=metadata["tags"], privacy_status=metadata["privacy_status"])
    receipt = publication_receipt(metadata["publication_context"], result.video_id,
                                  metadata["privacy_status"])
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

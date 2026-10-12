"""Refresh-only YouTube authentication check. Never uploads or prints tokens."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media_engine.providers.youtube_publisher import YouTubeOAuthError, YouTubePublisher


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"observed_at": datetime.now(timezone.utc).isoformat(),
              "upload_attempted": False, "status": "ready"}
    try:
        YouTubePublisher().preflight()
    except YouTubeOAuthError as exc:
        report.update(status="reauthorization_required", error_code=exc.code)
    except Exception:
        report.update(status="unavailable", error_code="configuration_or_network")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())

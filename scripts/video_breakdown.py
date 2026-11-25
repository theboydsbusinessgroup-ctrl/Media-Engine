#!/usr/bin/env python3
"""Break saved reference videos into frames, pacing and transcript.

Usage:
  python scripts/video_breakdown.py                       # every video in /mnt/user-data/uploads
  python scripts/video_breakdown.py clip.mp4 other.mov    # specific files or folders
  python scripts/video_breakdown.py --no-transcript clip.mp4

Only for files the owner saved or screen-recorded themselves. This script never
downloads from a platform.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from media_engine.reference_breakdown import breakdown, find_videos

DEFAULT_INBOX = Path("/mnt/user-data/uploads")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="video files or folders (default: chat uploads folder)")
    ap.add_argument("--out", type=Path, default=ROOT / ".cache" / "video-breakdowns")
    ap.add_argument("--threshold", type=float, default=0.15,
                    help="scene-change sensitivity 0-1, lower = more cuts (try 0.1 for jump-cut talking heads)")
    ap.add_argument("--model", default="base", help="whisper model: tiny, base, small, medium")
    ap.add_argument("--max-frames", type=int, default=24)
    ap.add_argument("--no-transcript", action="store_true")
    args = ap.parse_args()

    videos = find_videos(args.paths or [DEFAULT_INBOX])
    if not videos:
        print(f"No videos found in {', '.join(map(str, args.paths or [DEFAULT_INBOX]))}", file=sys.stderr)
        return 1
    summary = []
    for video in videos:
        try:
            b = breakdown(video, args.out, threshold=args.threshold, transcript=not args.no_transcript,
                          model_name=args.model, max_frames=args.max_frames)
        except Exception as exc:
            summary.append({"source": str(video), "error": f"{type(exc).__name__}: {exc}"})
            continue
        summary.append({
            "source": b.source,
            "report": str(Path(b.output_dir) / "breakdown.md"),
            "contact_sheet": b.contact_sheet,
            "frames": [f.path for f in b.frames],
            "pacing": b.pacing,
            "transcript": b.transcript_status,
        })
    print(json.dumps(summary, indent=2))
    return 0 if all("error" not in s for s in summary) else 2


if __name__ == "__main__":
    raise SystemExit(main())

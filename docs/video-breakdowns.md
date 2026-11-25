# Reference video breakdowns

Break down any short-form video you want to learn from (TikTok, Instagram Reels,
YouTube Shorts) scene by scene, with no Higgsfield credits.

## Why there's no "paste a link" option

TikTok and Instagram tell automated readers to stay out, and this tool doesn't
use scrapers or download tools to get around that. You save the video with the
app's own button and attach it. Everything after that is automatic.

## On your phone (about 10 seconds per video)

| Platform | How to get the file |
|---|---|
| TikTok | Share → **Save video** |
| Instagram Reels | ••• → **Download** where offered. Otherwise screen-record |
| YouTube Shorts | Screen-record |
| Saving turned off | Control Center → Screen Recording, play it once, stop |

Then open a Claude Code session that has this repo attached (claude.ai/code or the
Claude app), attach the video, or several, and say **"break this down"**.

To batch them, save five videos during the day and attach them all at once. You
get one breakdown per video, plus the patterns they share.

## What you get

- **Hook (0–3s)**: spoken line, on-screen text and opening visual
- **Beat map**: what's on screen and what's said in each scene, with timestamps
- **Pacing**: cuts per minute, average shot length, words per minute
- **CTA**: what is asked, and when
- **Reusable structure** and **original angles** for our brands

## Under the hood

`scripts/video_breakdown.py` (logic in `media_engine/reference_breakdown.py`):

1. `ffprobe` reads the length, resolution and frame rate.
2. ffmpeg scene detection finds hard cuts. The default threshold is 0.15. Use
   `--threshold 0.1` for jump-cut talking heads.
3. It grabs frames at 0/1/2/3s plus one per scene, up to 24, and tiles them into
   `contact_sheet.jpg`.
4. faster-whisper (`base` model, CPU) transcribes with word timings, so every
   word lands in the scene where it's spoken.
5. It writes `breakdown.md` and `breakdown.json` to `.cache/video-breakdowns/`,
   which git ignores.

Requirements: ffmpeg, plus `pip install faster-whisper` for transcripts. The
speech model downloads once from `huggingface.co` and `us.aws.cdn.hf.co`. The
"Boyds Business Group repos" cloud environment allows both.

The project skill in `.claude/skills/video-breakdown/` handles all of this when
you say "break this down".

## Rights

Breakdowns are research. Never commit reference videos, frames or transcripts,
and never publish a creator's script or a light reword of it. Use the structure
to make something original.

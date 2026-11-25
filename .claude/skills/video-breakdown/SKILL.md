---
name: video-breakdown
description: Scene-by-scene breakdown of a reference video the owner saved or screen-recorded (TikTok, Instagram Reels, YouTube Shorts, anything) — hook, beat map, pacing, CTA and a reusable structure, with no Higgsfield credits. Use when a video file is attached or sits in /mnt/user-data/uploads and the owner says "break this down", "analyze this video", "why does this work", "what's the hook", or pastes a TikTok/Instagram link.
---

# Video breakdown

Turns a saved video into an analysis the owner can build original content from.
Runs locally with ffmpeg and faster-whisper, so it costs no Higgsfield credits.

## If the owner pastes only a link

Platform links are not fetched. TikTok and Instagram tell automated readers to
stay out, and this skill does not scrape or use download tools to get around that.
Reply in two lines: ask them to save the video (TikTok: Share → Save video;
Instagram: ••• → Download where offered) or screen-record it, then attach it here.
Several at once is fine. Stop there.

## Run it

1. Make sure the transcriber is installed: `python3 -c "import faster_whisper" || pip install -q faster-whisper`
2. From the Media-Engine repo root:
   `python3 scripts/video_breakdown.py` (every video in `/mnt/user-data/uploads`), or pass file paths.
   For talking-head videos with jump cuts, add `--threshold 0.1`.
3. Each video gets `.cache/video-breakdowns/<name>-<hash>/` with `breakdown.md`,
   `breakdown.json`, `contact_sheet.jpg` and `frame_NN.jpg`. Read `breakdown.md`,
   then look at `contact_sheet.jpg`. Open individual frames when you need to read
   on-screen text or captions.
4. If the transcript line says `skipped`, say so plainly and analyze the visuals
   only. Never invent what was said.

## Write the breakdown

Reply in chat with these sections, in this order:

1. **Hook (0–3s)**: the spoken line, the on-screen text and the opening visual,
   and why it stops the scroll.
2. **Beat map**: a table with time, what's on screen, what's said, and the job
   of that beat (hook, setup, proof, payoff, CTA).
3. **Pacing and retention**: cut rate, average shot length and words per minute
   from the metrics; pattern interrupts, open loops, caption style, b-roll.
4. **CTA**: what is asked, when, and how (spoken, text, comment keyword).
5. **Reusable structure**: the skeleton as fill-in-the-blanks, in your own words.
6. **Make it ours**: two or three original angles for the owner's businesses.

When the owner sends several videos, add a short "patterns across these" section
at the end.

## Guardrails

- The transcript is research material. Quote it only to analyze it. Never hand
  back the creator's script, or a light reword of it, as content to publish.
  Media Engine's rule against plagiarized or rights-infringing material applies.
- Breakdown output lives in `.cache/`, which git ignores. Never commit reference
  videos, frames or transcripts.

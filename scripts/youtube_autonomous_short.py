#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from media_engine.providers.youtube_publisher import YouTubePublisher

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "inclusionai/ling-3.0-flash-vl:free"
FALLBACK_MODEL = "anthropic/claude-haiku-4.5"
VOICE = os.getenv("YOUTUBE_TTS_VOICE", "en-US-GuyNeural")

TOPICS = [
    "why dilution is part of a well-made cocktail",
    "when bartenders shake a cocktail versus stir it",
    "how ice changes a cocktail beyond simply making it cold",
    "why mise en place matters behind a busy bar",
    "how bartenders balance strong sweet sour and bitter flavors",
    "why chilling the glass can change the drinking experience",
    "how a bartender can recommend a drink without overwhelming the guest",
    "what makes a highball different from a sour",
    "why fresh citrus changes cocktail balance",
    "how professional bartenders stay organized during a rush",
]


def _openrouter_request(prompt: str) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required")

    configured = os.getenv("MEDIA_ENGINE_MODEL", DEFAULT_MODEL).strip()
    models = [m for m in (configured, FALLBACK_MODEL) if m]
    models = list(dict.fromkeys(models))
    last_error: Exception | None = None

    for model in models:
        body = json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You write original short-form educational scripts for Behind The Bar, "
                        "a faceless bartending and hospitality channel. Be concise, accurate, useful, "
                        "and conversational. Do not invent statistics, studies, endorsements, brand claims, "
                        "or guarantees. Do not copy recognizable wording from other creators. Return JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500,
            "temperature": 0.55,
        }).encode("utf-8")
        req = urllib.request.Request(
            OPENROUTER_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/theboydsbusinessgroup-ctrl/Media-Engine",
                "X-Title": "Behind The Bar Media Engine",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 404 and model != models[-1]:
                continue
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                detail = ""
            raise RuntimeError(f"OpenRouter request failed for model {model} with HTTP {exc.code}: {detail}") from exc

        content = payload["choices"][0]["message"]["content"].strip()
        start, end = content.find("{"), content.rfind("}")
        if start < 0 or end < start:
            raise RuntimeError(f"OpenRouter model {model} did not return a JSON object")
        result = json.loads(content[start:end + 1])
        result["_model"] = model
        return result

    raise RuntimeError(f"No OpenRouter model succeeded: {last_error}")


def generate_short_plan() -> dict:
    day = datetime.now(timezone.utc).date().toordinal()
    topic = TOPICS[day % len(TOPICS)]
    prompt = f"""
Create one YouTube Short about: {topic}

Requirements:
- 55 to 85 spoken words, roughly 20 to 35 seconds.
- Open with a strong hook in the first sentence.
- Teach one clear bartending or hospitality idea.
- No fabricated numbers, history, health claims, or brand endorsements.
- End naturally; do not say 'smash the like button'.
- Title must be under 70 characters and should make sense without clickbait.
- Description: 1 to 2 short sentences plus #Shorts #Bartending #Hospitality.
- Tags: 5 to 8 short tags, without # symbols.

Return JSON with exactly these keys: title, script, description, tags.
""".strip()
    plan = _openrouter_request(prompt)
    title = str(plan.get("title", "")).strip()[:70]
    script = str(plan.get("script", "")).strip()
    description = str(plan.get("description", "")).strip()[:4500]
    tags = [str(x).strip()[:30] for x in plan.get("tags", []) if str(x).strip()][:8]
    if not title or not script:
        raise RuntimeError("Generated YouTube plan is missing title or script")
    word_count = len(script.split())
    if word_count < 40 or word_count > 100:
        raise RuntimeError(f"Generated script length is outside safe bounds: {word_count} words")
    return {
        "title": title,
        "script": script,
        "description": description,
        "tags": tags,
        "topic": topic,
        "model": plan.get("_model", "unknown"),
    }


def render_short(plan: dict, out_dir: Path) -> Path:
    audio = out_dir / "voice.mp3"
    subtitles = out_dir / "voice.srt"
    video = out_dir / "short.mp4"

    subprocess.run([
        "edge-tts",
        "--voice", VOICE,
        "--text", plan["script"],
        "--write-media", str(audio),
        "--write-subtitles", str(subtitles),
    ], check=True)

    subtitle_filter = (
        f"subtitles={subtitles}:force_style='FontName=DejaVu Sans,FontSize=18,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,"
        "Outline=1,Shadow=0,Alignment=2,MarginV=230'"
    )
    branding = (
        "drawbox=x=70:y=170:w=940:h=190:color=black@0.45:t=fill,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "text='BEHIND THE BAR':fontcolor=white:fontsize=66:x=(w-text_w)/2:y=205,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        "text='BARTENDING • HOSPITALITY • CRAFT':fontcolor=white@0.82:fontsize=28:"
        "x=(w-text_w)/2:y=295"
    )
    vf = f"{branding},{subtitle_filter},format=yuv420p"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x15171c:s=1080x1920:r=30",
        "-i", str(audio),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest", "-movflags", "+faststart",
        str(video),
    ], check=True)
    if not video.exists() or video.stat().st_size < 10_000:
        raise RuntimeError("Rendered Short is missing or unexpectedly small")
    return video


def main() -> None:
    plan = generate_short_plan()
    privacy = os.getenv("YOUTUBE_PRIVACY_STATUS", "private").strip().lower()
    if privacy not in {"private", "unlisted", "public"}:
        raise RuntimeError("YOUTUBE_PRIVACY_STATUS must be private, unlisted, or public")

    with tempfile.TemporaryDirectory(prefix="behind-the-bar-") as tmp:
        out_dir = Path(tmp)
        video = render_short(plan, out_dir)
        result = YouTubePublisher().upload(
            video,
            title=plan["title"],
            description=plan["description"],
            tags=plan["tags"],
            privacy_status=privacy,
        )
        print(json.dumps({
            "status": "ok",
            "channel": "Behind The Bar",
            "privacy": privacy,
            "topic": plan["topic"],
            "title": plan["title"],
            "word_count": len(plan["script"].split()),
            "model": plan["model"],
            "video_id": result.video_id,
            "url": result.url,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()

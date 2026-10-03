#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from media_engine.providers.youtube_publisher import YouTubePublisher
from media_engine.monetization import attach_offer, publication_receipt

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"
FALLBACK_MODEL = ""
PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
KOKORO_VOICE = os.getenv("YOUTUBE_KOKORO_VOICE", "am_michael")
KOKORO_SPEED = float(os.getenv("YOUTUBE_KOKORO_SPEED", "1.04"))

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

GENERIC_BROLL = [
    "bartender making cocktail",
    "cocktail pouring close up",
    "bartender shaking cocktail",
    "cocktail garnish bar",
    "bartender working behind bar",
    "cocktail glass close up",
]


def _openrouter_request(prompt: str) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required")

    configured = os.getenv("MEDIA_ENGINE_MODEL", DEFAULT_MODEL).strip()
    if configured != 'openrouter/free' and not configured.endswith(':free'):
        raise RuntimeError('Autonomous publisher requires a free model; paid fallback is disabled')
    models = list(dict.fromkeys(m for m in (configured, FALLBACK_MODEL) if m))
    last_error: Exception | None = None

    for model in models:
        body = json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the short-form creative director for Behind The Bar, a faceless bartending and hospitality channel. "
                        "Write original, highly watchable educational Shorts. Hook immediately, create curiosity or contrast, "
                        "teach one useful idea, then land a satisfying payoff. Be accurate and conversational, never cheesy. "
                        "Do not invent statistics, studies, history, endorsements, brand claims, or guarantees. "
                        "Do not copy recognizable wording from other creators. Return JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 750,
            "temperature": 0.7,
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
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if model != models[-1]:
                continue
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                detail = ""
            raise RuntimeError(f"OpenRouter request failed for model {model} with HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError('OpenRouter network unavailable') from exc

        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        raw_content = message.get("content")
        if not isinstance(raw_content, str) or not raw_content.strip():
            last_error = RuntimeError(f"OpenRouter model {model} returned empty content")
            if model != models[-1]:
                continue
            raise last_error

        content = raw_content.strip()
        start, end = content.find("{"), content.rfind("}")
        if start < 0 or end < start:
            last_error = RuntimeError(f"OpenRouter model {model} did not return JSON")
            if model != models[-1]:
                continue
            raise last_error
        try:
            result = json.loads(content[start:end + 1])
        except json.JSONDecodeError as exc:
            raise RuntimeError(f'OpenRouter model {model} did not return JSON') from exc
        if not isinstance(result,dict):
            raise RuntimeError(f'OpenRouter model {model} did not return JSON')
        result["_model"] = model
        return result

    raise RuntimeError(f"No OpenRouter model succeeded: {last_error}")


def generate_short_plan() -> dict[str, Any]:
    day = datetime.now(timezone.utc).date().toordinal()
    topic = TOPICS[day % len(TOPICS)]
    prompt = f"""
Create one YouTube Short about: {topic}

The audience is adults interested in cocktails, bartending, restaurants, and hospitality.

Creative requirements:
- 65 to 95 spoken words, usually 25 to 40 seconds.
- First sentence must be a pattern interrupt or curiosity hook, not a generic introduction.
- Give the viewer a reason to keep watching within the first 3 seconds.
- Use contrast, a common misconception, a sensory detail, or a practical bartender insight.
- Keep sentences short enough to sound natural aloud.
- Make the ending feel like a payoff, not a summary.
- One optional final question is okay if it feels natural.
- No fabricated numbers, history, health claims, or brand endorsements.
- Title under 70 characters, specific but not clickbait.
- Description: 1 to 2 short sentences plus #Shorts #Bartending #Hospitality.
- Tags: 5 to 8 short tags, without # symbols.
- hook_text: 3 to 7 words for an on-screen opening hook.
- broll_queries: 5 concise Pexels search phrases that visually match different moments in the script. Favor real bartenders, cocktails, glassware, citrus, pouring, shaking, stirring, ice, and bar atmosphere. No logos or named brands.

Return JSON with exactly these keys: title, script, description, tags, hook_text, broll_queries.
""".strip()
    plan = _openrouter_request(prompt)
    title = str(plan.get("title", "")).strip()[:70]
    script = re.sub(r"\s+", " ", str(plan.get("script", "")).strip())
    description = str(plan.get("description", "")).strip()[:4200]
    tags = [str(x).strip()[:30] for x in plan.get("tags", []) if str(x).strip()][:8]
    hook_text = re.sub(r"\s+", " ", str(plan.get("hook_text", "")).strip())[:60]
    queries = [re.sub(r"\s+", " ", str(x).strip())[:80] for x in plan.get("broll_queries", []) if str(x).strip()][:7]
    if not title or not script:
        raise RuntimeError("Generated YouTube plan is missing title or script")
    word_count = len(script.split())
    if word_count < 55 or word_count > 110:
        raise RuntimeError(f"Generated script length is outside safe bounds: {word_count} words")
    if not hook_text:
        hook_text = title
    if len(queries) < 4:
        queries.extend(GENERIC_BROLL[: 5 - len(queries)])
    return {
        "title": title,
        "script": script,
        "description": description,
        "tags": tags,
        "hook_text": hook_text,
        "broll_queries": queries[:5],
        "topic": topic,
        "model": plan.get("_model", "unknown"),
    }


def _download(url: str, path: Path, *, headers: dict[str, str] | None = None) -> None:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Media-Engine/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp, path.open("wb") as out:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def _choose_video_file(video: dict[str, Any]) -> str | None:
    candidates = []
    for item in video.get("video_files", []):
        if item.get("file_type") != "video/mp4" or not item.get("link"):
            continue
        width = int(item.get("width") or 0)
        height = int(item.get("height") or 0)
        if width <= 0 or height <= 0:
            continue
        portrait_penalty = 0 if height >= width else 3000
        target_penalty = abs(width - 720) + abs(height - 1280)
        huge_penalty = max(width - 1440, 0) + max(height - 2560, 0)
        candidates.append((portrait_penalty + target_penalty + huge_penalty, item["link"]))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def download_pexels_broll(queries: list[str], out_dir: Path) -> list[dict[str, Any]]:
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY is required")
    seen_ids: set[int] = set()
    downloaded: list[dict[str, Any]] = []
    search_terms = list(queries) + GENERIC_BROLL

    for query in search_terms:
        if len(downloaded) >= 5:
            break
        params = urllib.parse.urlencode({
            "query": query,
            "orientation": "portrait",
            "size": "medium",
            "per_page": 8,
        })
        req = urllib.request.Request(
            f"{PEXELS_SEARCH_URL}?{params}",
            headers={"Authorization": api_key, "User-Agent": "Behind-The-Bar-Media-Engine/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue

        chosen = None
        for video in payload.get("videos", []):
            vid = int(video.get("id") or 0)
            if not vid or vid in seen_ids:
                continue
            link = _choose_video_file(video)
            if not link:
                continue
            chosen = (vid, link, video)
            break
        if not chosen:
            continue

        vid, link, video = chosen
        path = out_dir / f"pexels-{vid}.mp4"
        try:
            _download(link, path)
        except Exception:
            continue
        if path.stat().st_size < 50_000:
            path.unlink(missing_ok=True)
            continue
        seen_ids.add(vid)
        downloaded.append({
            "id": vid,
            "query": query,
            "path": path,
            "photographer": str((video.get("user") or {}).get("name") or ""),
        })

    if len(downloaded) < 3:
        raise RuntimeError(f"Pexels returned too little usable B-roll: {len(downloaded)} clips")
    return downloaded


def synthesize_voice(script: str, out_dir: Path) -> Path:
    try:
        import soundfile as sf
        from kokoro_onnx import Kokoro
    except Exception as exc:
        raise RuntimeError("Kokoro TTS dependencies are not installed") from exc

    model_path = Path(os.getenv("KOKORO_MODEL_PATH", "kokoro-v1.0.int8.onnx"))
    voices_path = Path(os.getenv("KOKORO_VOICES_PATH", "voices-v1.0.bin"))
    if not model_path.exists() or not voices_path.exists():
        raise RuntimeError("Kokoro model files are missing")

    wav = out_dir / "voice.wav"
    kokoro = Kokoro(str(model_path), str(voices_path))
    samples, sample_rate = kokoro.create(
        script,
        voice=KOKORO_VOICE,
        speed=KOKORO_SPEED,
        lang="en-us",
    )
    sf.write(str(wav), samples, sample_rate)
    if not wav.exists() or wav.stat().st_size < 20_000:
        raise RuntimeError("Kokoro did not produce usable audio")
    return wav


def media_duration(path: Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def _ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def _caption_chunks(script: str) -> list[list[str]]:
    words = script.split()
    chunks: list[list[str]] = []
    current: list[str] = []
    for word in words:
        current.append(word)
        ends_sentence = bool(re.search(r"[.!?]$", word))
        if len(current) >= 4 or (ends_sentence and len(current) >= 2):
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def _style_caption(words: list[str]) -> str:
    clean = [re.sub(r"[^A-Za-z0-9'&%?-]", "", w) or w for w in words]
    candidates = [(len(re.sub(r"\W", "", w)), i) for i, w in enumerate(clean)]
    _, emphasis_index = max(candidates) if candidates else (0, 0)
    rendered = []
    for idx, word in enumerate(clean):
        text = word.upper()
        if idx == emphasis_index and len(re.sub(r"\W", "", word)) >= 4:
            text = r"{\c&H0000D7FF&\b1}" + text + r"{\c&H00FFFFFF&\b1}"
        rendered.append(text)
    if len(rendered) >= 4:
        return " ".join(rendered[:2]) + r"\N" + " ".join(rendered[2:])
    return " ".join(rendered)


def write_dynamic_captions(plan: dict[str, Any], duration: float, out_dir: Path) -> Path:
    ass = out_dir / "captions.ass"
    chunks = _caption_chunks(plan["script"])
    total_words = max(sum(len(c) for c in chunks), 1)
    usable = max(duration - 0.35, 1.0)
    cursor = 0.18

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,DejaVu Sans,92,&H00FFFFFF,&H0000D7FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,3,5,0,2,70,70,245,1
Style: Hook,DejaVu Sans,74,&H00FFFFFF,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,3,4,0,8,85,85,165,1
Style: Brand,DejaVu Sans,36,&H00FFFFFF,&H0000D7FF,&H00000000,&H70000000,-1,0,0,0,100,100,1,0,3,2,0,8,90,90,70,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    hook = str(plan["hook_text"]).replace("{", "").replace("}", "").upper()
    lines.append(f"Dialogue: 2,0:00:00.00,{_ass_time(min(3.1, duration))},Hook,,0,0,0,,{{\\fad(120,180)\\fscx106\\fscy106}}{hook}\n")
    lines.append(f"Dialogue: 1,0:00:00.00,{_ass_time(duration)},Brand,,0,0,0,,BEHIND THE BAR\n")

    for chunk in chunks:
        fraction = len(chunk) / total_words
        chunk_duration = max(0.72, usable * fraction)
        start = cursor
        end = min(duration - 0.05, start + chunk_duration)
        caption = _style_caption(chunk)
        lines.append(
            f"Dialogue: 3,{_ass_time(start)},{_ass_time(end)},Caption,,0,0,0,,"
            f"{{\\fad(55,70)\\fscx104\\fscy104}}{caption}\n"
        )
        cursor = end

    ass.write_text("".join(lines), encoding="utf-8")
    return ass


def build_visual_track(clips: list[dict[str, Any]], duration: float, out_dir: Path) -> Path:
    scene_count = min(5, len(clips))
    segment_duration = duration / scene_count + 0.08
    segment_paths: list[Path] = []

    for idx, clip in enumerate(clips[:scene_count]):
        segment = out_dir / f"scene-{idx}.mp4"
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,setsar=1,fps=30,"
            "eq=contrast=1.06:saturation=1.08:brightness=-0.015"
        )
        subprocess.run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(clip["path"]),
            "-t", f"{segment_duration:.3f}", "-an", "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(segment),
        ], check=True)
        segment_paths.append(segment)

    concat_file = out_dir / "concat.txt"
    concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in segment_paths), encoding="utf-8")
    visual = out_dir / "broll.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-t", f"{duration:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(visual),
    ], check=True)
    return visual


def render_short(plan: dict[str, Any], out_dir: Path) -> tuple[Path, list[dict[str, Any]], float]:
    voice = synthesize_voice(plan["script"], out_dir)
    duration = media_duration(voice)
    if duration < 15 or duration > 55:
        raise RuntimeError(f"Narration duration is outside Short bounds: {duration:.1f}s")

    clips = download_pexels_broll(plan["broll_queries"], out_dir)
    visual = build_visual_track(clips, duration, out_dir)
    captions = write_dynamic_captions(plan, duration, out_dir)
    video = out_dir / "short.mp4"

    vf = f"subtitles={captions.as_posix()}"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(visual), "-i", str(voice),
        "-map", "0:v:0", "-map", "1:a:0", "-vf", vf,
        "-af", "loudnorm=I=-16:LRA=7:TP=-1.5",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p",
        "-shortest", "-movflags", "+faststart", str(video),
    ], check=True)
    if not video.exists() or video.stat().st_size < 250_000:
        raise RuntimeError("Rendered Short is missing or unexpectedly small")
    return video, clips, duration


def main() -> None:
    plan = attach_offer(generate_short_plan(), 'behindthebar-' + datetime.now(timezone.utc).date().isoformat())
    privacy = os.getenv("YOUTUBE_PRIVACY_STATUS", "private").strip().lower()
    if privacy not in {"private", "unlisted", "public"}:
        raise RuntimeError("YOUTUBE_PRIVACY_STATUS must be private, unlisted, or public")

    with tempfile.TemporaryDirectory(prefix="behind-the-bar-") as tmp:
        out_dir = Path(tmp)
        video, clips, duration = render_short(plan, out_dir)
        description = plan["description"]
        if "pexels" not in description.lower():
            description += "\n\nVisual footage sourced via Pexels."
        result = YouTubePublisher().upload(
            video,
            title=plan["title"],
            description=description,
            tags=plan["tags"],
            privacy_status=privacy,
        )
        receipt = publication_receipt(plan, result.video_id, privacy)
        receipt_path = os.getenv('MEDIA_RECEIPT_PATH')
        if receipt_path:
            target = Path(receipt_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({
            "status": "ok",
            "channel": "Behind The Bar",
            "privacy": privacy,
            "topic": plan["topic"],
            "title": plan["title"],
            "hook": plan["hook_text"],
            "word_count": len(plan["script"].split()),
            "duration_seconds": round(duration, 1),
            "model": plan["model"],
            "tts": f"kokoro:{KOKORO_VOICE}",
            "broll_clips": [{"id": c["id"], "query": c["query"]} for c in clips],
            "video_id": result.video_id,
            "url": result.url,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()

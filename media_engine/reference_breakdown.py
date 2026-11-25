"""Break a saved reference video into scenes, frames, pacing metrics and a transcript.

The input is always a file the owner already has: a video saved with the
platform's own Save/Download button, or a screen recording. Nothing in this
module fetches from TikTok, Instagram, YouTube or any other platform.

The output is research material (what the hook is, how fast it cuts, where the
CTA lands). It feeds original content; it is never a script to re-publish.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".3gp"}
HOOK_TIMES = (0.0, 1.0, 2.0, 3.0)
_PTS_TIME = re.compile(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)")


@dataclass
class Scene:
    index: int
    start: float
    end: float
    transcript: str = ""

    @property
    def length(self) -> float:
        return round(self.end - self.start, 3)


@dataclass
class Frame:
    time: float
    label: str
    path: str


@dataclass
class Breakdown:
    source: str
    sha256: str
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool
    scenes: list[Scene]
    frames: list[Frame]
    contact_sheet: str | None
    pacing: dict[str, Any]
    transcript: list[dict[str, Any]] = field(default_factory=list)
    transcript_status: str = "not requested"
    output_dir: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for scene, raw in zip(self.scenes, data["scenes"]):
            raw["length"] = scene.length
        return data


# ---------------------------------------------------------------- pure logic

def parse_scene_times(ffmpeg_log: str) -> list[float]:
    """Pull cut timestamps out of ffmpeg `showinfo` output."""
    return sorted({round(float(m.group(1)), 3) for m in _PTS_TIME.finditer(ffmpeg_log)})


def merge_close(times: list[float], min_gap: float = 0.4) -> list[float]:
    """Drop cuts that land within `min_gap` seconds of the previous kept cut."""
    kept: list[float] = []
    for t in sorted(times):
        if not kept or t - kept[-1] >= min_gap:
            kept.append(t)
    return kept


def build_scenes(cuts: list[float], duration: float, min_gap: float = 0.4) -> list[Scene]:
    """Turn cut timestamps into contiguous scenes covering the whole video."""
    inner = [t for t in merge_close(cuts, min_gap) if min_gap <= t <= duration - min_gap]
    bounds = [0.0, *inner, round(duration, 3)]
    return [Scene(i + 1, bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]


def pick_frame_times(scenes: list[Scene], duration: float, max_frames: int = 24) -> list[tuple[float, str]]:
    """Hook frames (0-3s) plus one frame per scene, thinned evenly past `max_frames`."""
    hook = [(t, f"hook {t:.0f}s") for t in HOOK_TIMES if t < duration]
    room = max(max_frames - len(hook), 1)
    picked = scenes
    if len(scenes) > room:
        step = len(scenes) / room
        picked = [scenes[int(i * step)] for i in range(room)]
    per_scene = []
    for scene in picked:
        t = round(scene.start + min(scene.length / 2, 0.75), 2)
        per_scene.append((t, f"scene {scene.index} {t:.1f}s"))
    seen: set[float] = set()
    out = []
    for t, label in sorted(hook + per_scene):
        if any(abs(t - s) < 0.25 for s in seen):
            continue
        seen.add(t)
        out.append((t, label))
    return out


def spoken_units(segments: list[dict[str, Any]]) -> list[tuple[float, str]]:
    """(start time, text) per word when word timings exist, else per segment midpoint."""
    units: list[tuple[float, str]] = []
    for seg in segments:
        words = seg.get("words") or []
        if words:
            units += [(w["start"], w["word"].strip()) for w in words if w["word"].strip()]
        elif seg["text"].strip():
            units.append(((seg["start"] + seg["end"]) / 2, seg["text"].strip()))
    return units


def assign_transcript(scenes: list[Scene], segments: list[dict[str, Any]]) -> None:
    """Attach what is said to the scene on screen when it is said."""
    for t, text in spoken_units(segments):
        scene = next((s for s in scenes if s.start <= t < s.end), scenes[-1])
        scene.transcript = f"{scene.transcript} {text}".strip()


def pacing_metrics(scenes: list[Scene], duration: float, segments: list[dict[str, Any]]) -> dict[str, Any]:
    lengths = [s.length for s in scenes]
    cuts = len(scenes) - 1
    words = sum(len(seg["text"].split()) for seg in segments)
    speech = sum(seg["end"] - seg["start"] for seg in segments)
    first_words = " ".join(text for t, text in spoken_units(segments) if t < 3.0)
    return {
        "duration_s": round(duration, 2),
        "cuts": cuts,
        "cuts_per_minute": round(cuts / duration * 60, 1) if duration else 0.0,
        "avg_shot_s": round(sum(lengths) / len(lengths), 2) if lengths else 0.0,
        "longest_shot_s": round(max(lengths), 2) if lengths else 0.0,
        "first_cut_s": round(scenes[1].start, 2) if len(scenes) > 1 else None,
        "words": words,
        "words_per_minute": round(words / speech * 60) if speech else None,
        "spoken_hook": first_words or None,
    }


def render_markdown(b: Breakdown) -> str:
    p = b.pacing
    lines = [
        f"# Breakdown: {Path(b.source).name}",
        "",
        f"- Length {p['duration_s']}s · {b.width}x{b.height} · {b.fps:g} fps",
        f"- {p['cuts']} cuts ({p['cuts_per_minute']}/min) · average shot {p['avg_shot_s']}s · longest {p['longest_shot_s']}s"
        + (f" · first cut at {p['first_cut_s']}s" if p["first_cut_s"] is not None else ""),
    ]
    if p["words"]:
        lines.append(f"- {p['words']} words spoken, about {p['words_per_minute']} wpm")
    lines.append(f"- Transcript: {b.transcript_status}")
    if p["spoken_hook"]:
        lines += ["", f"**Spoken hook (0-3s):** {p['spoken_hook']}"]
    if b.contact_sheet:
        lines += ["", f"Contact sheet: `{b.contact_sheet}`"]
    lines += ["", "| # | Start | Length | What's said |", "|---|---|---|---|"]
    for s in b.scenes:
        said = s.transcript.replace("|", "/") or "—"
        lines.append(f"| {s.index} | {s.start:.1f}s | {s.length:.1f}s | {said} |")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------- ffmpeg work

def _require(tool: str) -> str:
    found = shutil.which(tool)
    if not found:
        raise RuntimeError(f"{tool} is not installed; install ffmpeg to analyse videos")
    return found


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict[str, Any]:
    out = subprocess.run(
        [_require("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    info = json.loads(out)
    video = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError(f"{path.name} has no video stream")
    num, _, den = (video.get("avg_frame_rate") or "0/1").partition("/")
    fps = float(num) / float(den) if float(den or 0) else 0.0
    width, height = int(video["width"]), int(video["height"])
    rotation = abs(int(video.get("tags", {}).get("rotate", 0) or 0))
    for side in video.get("side_data_list", []):
        rotation = abs(int(side.get("rotation", rotation) or 0))
    if rotation in (90, 270):
        width, height = height, width
    return {
        "duration": float(info["format"].get("duration") or video.get("duration") or 0),
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "has_audio": any(s.get("codec_type") == "audio" for s in info["streams"]),
    }


def detect_cuts(path: Path, threshold: float = 0.15) -> list[float]:
    proc = subprocess.run(
        [_require("ffmpeg"), "-hide_banner", "-nostats", "-i", str(path),
         "-vf", f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"scene detection failed: {proc.stderr[-400:]}")
    return parse_scene_times("\n".join(l for l in proc.stderr.splitlines() if "showinfo" in l))


def extract_frames(path: Path, times: list[tuple[float, str]], out_dir: Path, width: int = 540) -> list[Frame]:
    ffmpeg = _require("ffmpeg")
    frames = []
    for n, (t, label) in enumerate(times, start=1):
        target = out_dir / f"frame_{n:02d}.jpg"
        subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(path),
             "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", str(target)],
            check=True,
        )
        if target.exists():
            frames.append(Frame(t, label, str(target)))
    return frames


def build_contact_sheet(frames: list[Frame], out_dir: Path, columns: int = 6, tile_width: int = 270) -> str | None:
    if not frames:
        return None
    ffmpeg = _require("ffmpeg")
    tiles = out_dir / "tiles"
    tiles.mkdir(exist_ok=True)
    for n, frame in enumerate(frames, start=1):
        text = frame.label.replace(":", " ").replace("'", "")
        subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", frame.path, "-vf",
             f"scale={tile_width}:-2,drawtext=text='{text}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=4",
             str(tiles / f"tile_{n:02d}.jpg")],
            check=True,
        )
    rows = -(-len(frames) // columns)
    sheet = out_dir / "contact_sheet.jpg"
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", "1", "-i", str(tiles / "tile_%02d.jpg"),
         "-vf", f"tile={columns}x{rows}:padding=4:color=black", "-frames:v", "1", "-q:v", "3", str(sheet)],
        check=True,
    )
    shutil.rmtree(tiles, ignore_errors=True)
    return str(sheet) if sheet.exists() else None


def transcribe(path: Path, model_name: str = "base") -> tuple[list[dict[str, Any]], str]:
    """Return (segments, status). Never raises: a missing model is reported, not fatal."""
    try:
        import numpy as np
        from faster_whisper import WhisperModel  # optional dependency
    except ImportError:
        return [], "skipped: faster-whisper is not installed (pip install faster-whisper)"
    # Decode with ffmpeg ourselves: faster-whisper's PyAV decoder breaks across PyAV releases.
    pcm = subprocess.run(
        [_require("ffmpeg"), "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        check=True, capture_output=True,
    ).stdout
    if not pcm:
        return [], "skipped: audio track is empty"
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    # Plain HTTPS download keeps the hosts to huggingface.co and its file CDN.
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    try:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
    except Exception as exc:  # network-blocked model download lands here
        return [], (f"skipped: could not load whisper model '{model_name}' ({type(exc).__name__}); "
                    "huggingface.co and us.aws.cdn.hf.co must be reachable once to download it")
    raw, info = model.transcribe(audio, vad_filter=True, word_timestamps=True)
    segments = [
        {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
         "words": [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word} for w in (s.words or [])]}
        for s in raw
    ]
    return segments, f"ok ({info.language}, whisper {model_name})"


def breakdown(path: Path, out_root: Path, *, threshold: float = 0.15, transcript: bool = True,
              model_name: str = "base", max_frames: int = 24) -> Breakdown:
    path = Path(path)
    digest = file_sha256(path)
    out_dir = Path(out_root) / f"{path.stem[:40]}-{digest[:10]}"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = probe(path)
    scenes = build_scenes(detect_cuts(path, threshold), meta["duration"])
    frames = extract_frames(path, pick_frame_times(scenes, meta["duration"], max_frames), out_dir)
    sheet = build_contact_sheet(frames, out_dir)
    segments: list[dict[str, Any]] = []
    status = "not requested"
    if transcript and meta["has_audio"]:
        segments, status = transcribe(path, model_name)
    elif transcript:
        status = "skipped: video has no audio track"
    assign_transcript(scenes, segments)
    result = Breakdown(
        source=str(path), sha256=digest, duration=meta["duration"], width=meta["width"],
        height=meta["height"], fps=meta["fps"], has_audio=meta["has_audio"], scenes=scenes,
        frames=frames, contact_sheet=sheet, pacing=pacing_metrics(scenes, meta["duration"], segments),
        transcript=segments, transcript_status=status, output_dir=str(out_dir),
    )
    (out_dir / "breakdown.json").write_text(json.dumps(result.to_dict(), indent=2))
    (out_dir / "breakdown.md").write_text(render_markdown(result))
    return result


def find_videos(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            found += sorted(f for f in p.rglob("*") if f.is_file() and f.suffix.lower() in VIDEO_SUFFIXES)
        elif p.is_file():
            found.append(p)
    return found

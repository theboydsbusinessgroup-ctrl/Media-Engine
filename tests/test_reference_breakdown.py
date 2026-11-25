import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from media_engine.reference_breakdown import (
    Scene,
    assign_transcript,
    breakdown,
    build_scenes,
    find_videos,
    pacing_metrics,
    parse_scene_times,
    pick_frame_times,
    render_markdown,
)

SHOWINFO_LOG = """
[Parsed_showinfo_1 @ 0x55] n:   0 pts:  51200 pts_time:2       duration:512 fmt:yuv420p
[Parsed_showinfo_1 @ 0x55] n:   1 pts: 128000 pts_time:5.04    duration:512 fmt:yuv420p
[Parsed_showinfo_1 @ 0x55] n:   2 pts: 130000 pts_time:5.2     duration:512 fmt:yuv420p
"""


class PureLogicTests(unittest.TestCase):
    def test_parses_cut_times_from_showinfo(self):
        self.assertEqual(parse_scene_times(SHOWINFO_LOG), [2.0, 5.04, 5.2])

    def test_scenes_cover_video_and_merge_flicker_cuts(self):
        scenes = build_scenes([2.0, 5.04, 5.2, 7.4], duration=7.5)
        self.assertEqual([(s.start, s.end) for s in scenes], [(0.0, 2.0), (2.0, 5.04), (5.04, 7.5)])

    def test_no_cuts_is_one_scene(self):
        scenes = build_scenes([], duration=12.0)
        self.assertEqual(len(scenes), 1)
        self.assertEqual(scenes[0].length, 12.0)

    def test_frames_include_hook_and_respect_cap(self):
        scenes = build_scenes([i * 0.5 for i in range(1, 120)], duration=60.0)
        times = pick_frame_times(scenes, 60.0, max_frames=12)
        self.assertLessEqual(len(times), 12)
        self.assertTrue(any(label.startswith("hook 0s") for _, label in times))
        self.assertEqual(times, sorted(times))

    def test_short_video_skips_hook_frames_past_the_end(self):
        times = pick_frame_times(build_scenes([], 1.5), 1.5)
        self.assertTrue(all(t < 1.5 for t, _ in times))

    def test_words_land_in_the_scene_where_they_are_spoken(self):
        scenes = [Scene(1, 0.0, 2.0), Scene(2, 2.0, 4.0)]
        segments = [{
            "start": 0.2, "end": 3.0, "text": "Stop scrolling right now",
            "words": [
                {"start": 0.2, "end": 0.6, "word": " Stop"},
                {"start": 0.7, "end": 1.4, "word": " scrolling"},
                {"start": 2.1, "end": 2.4, "word": " right"},
                {"start": 2.5, "end": 3.0, "word": " now"},
            ],
        }]
        assign_transcript(scenes, segments)
        self.assertEqual(scenes[0].transcript, "Stop scrolling")
        self.assertEqual(scenes[1].transcript, "right now")

    def test_segments_without_words_use_their_midpoint(self):
        scenes = [Scene(1, 0.0, 2.0), Scene(2, 2.0, 4.0)]
        assign_transcript(scenes, [{"start": 1.5, "end": 3.5, "text": "late line"}])
        self.assertEqual(scenes[1].transcript, "late line")

    def test_pacing_metrics(self):
        scenes = build_scenes([2.0, 5.0], duration=7.5)
        segments = [{"start": 0.0, "end": 3.0, "text": "one two three four five six"}]
        pacing = pacing_metrics(scenes, 7.5, segments)
        self.assertEqual(pacing["cuts"], 2)
        self.assertEqual(pacing["cuts_per_minute"], 16.0)
        self.assertEqual(pacing["first_cut_s"], 2.0)
        self.assertEqual(pacing["words_per_minute"], 120)
        self.assertEqual(pacing["spoken_hook"], "one two three four five six")

    def test_find_videos_filters_by_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("a.mp4", "b.MOV", "notes.txt"):
                (Path(tmp) / name).write_bytes(b"x")
            self.assertEqual(sorted(p.name for p in find_videos([Path(tmp)])), ["a.mp4", "b.MOV"])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg not installed")
class FfmpegBreakdownTests(unittest.TestCase):
    def test_breakdown_finds_cuts_and_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "clip.mp4"
            scenes = [("red", 2), ("blue", 3), ("green", 2.5)]
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
            for color, dur in scenes:
                cmd += ["-f", "lavfi", "-i", f"color=c={color}:s=360x640:d={dur}"]
            cmd += ["-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]", "-map", "[v]",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)]
            subprocess.run(cmd, check=True)

            result = breakdown(video, Path(tmp) / "out", transcript=True)

            self.assertEqual(len(result.scenes), 3)
            self.assertAlmostEqual(result.scenes[1].start, 2.0, delta=0.1)
            self.assertAlmostEqual(result.scenes[2].start, 5.0, delta=0.1)
            self.assertEqual((result.width, result.height), (360, 640))
            self.assertFalse(result.has_audio)
            self.assertIn("no audio", result.transcript_status)
            self.assertTrue(Path(result.contact_sheet).exists())
            self.assertTrue(all(Path(f.path).exists() for f in result.frames))
            data = json.loads((Path(result.output_dir) / "breakdown.json").read_text())
            self.assertEqual(data["pacing"]["cuts"], 2)
            self.assertIn("| 3 | 5.0s |", render_markdown(result))


if __name__ == "__main__":
    unittest.main()

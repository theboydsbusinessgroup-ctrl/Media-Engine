import tempfile
import unittest
from pathlib import Path

from media_engine.story import Character, EpisodeRecord, StoryStore, Universe


class StoryStoreTests(unittest.TestCase):
    def test_story_context_tracks_canon_and_open_threads(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryStore(Path(tmp) / "story.db")
            store.save_universe(
                Universe(
                    id="nightshift",
                    name="Nightshift Stories",
                    premise="A city changes after midnight.",
                    genre="mystery",
                    tone="cinematic, adult, suspenseful",
                )
            )
            store.save_character(
                Character(
                    id="mara",
                    universe_id="nightshift",
                    name="Mara Vale",
                    role="lead investigator",
                    traits=["observant", "dry wit"],
                    voice_id="af_heart",
                    visual_prompt="woman in her 30s, dark coat, neon city at night",
                )
            )
            store.save_episode(
                EpisodeRecord(
                    id="s1e1",
                    universe_id="nightshift",
                    season=1,
                    number=1,
                    title="Last Train Home",
                    logline="Mara follows a passenger who should not exist.",
                    summary="A late train leaves behind a key and an impossible passenger record.",
                    unresolved_threads=["Who owns the brass key?", "Why is passenger 17 missing from records?"],
                )
            )
            store.save_episode(
                EpisodeRecord(
                    id="s1e2",
                    universe_id="nightshift",
                    season=1,
                    number=2,
                    title="The Brass Key",
                    logline="The key opens a locker sealed for twenty years.",
                    summary="Mara traces the key to an abandoned station locker.",
                    resolved_threads=["Who owns the brass key?"],
                    unresolved_threads=["Who left the photograph in the locker?"],
                )
            )
            store.add_canon_event(
                "nightshift",
                event_type="discovery",
                subject="Mara Vale",
                detail="Mara found a photograph dated twenty years in the future.",
                episode_id="s1e2",
            )

            context = store.story_context("nightshift")

            self.assertEqual(context["universe"]["name"], "Nightshift Stories")
            self.assertEqual(context["characters"][0]["name"], "Mara Vale")
            self.assertNotIn("Who owns the brass key?", context["active_threads"])
            self.assertIn("Why is passenger 17 missing from records?", context["active_threads"])
            self.assertIn("Who left the photograph in the locker?", context["active_threads"])
            self.assertEqual(context["canon_events"][0]["event_type"], "discovery")


if __name__ == "__main__":
    unittest.main()

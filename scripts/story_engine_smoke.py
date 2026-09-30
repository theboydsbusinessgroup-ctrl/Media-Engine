#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from media_engine.story import Character, EpisodeRecord, StoryStore, Universe


def seed_demo(store: StoryStore) -> dict:
    universe = Universe(
        id="nightshift",
        name="Nightshift Stories",
        premise="A hidden version of the city emerges after midnight, and one investigator keeps finding evidence that tomorrow has already happened.",
        genre="serialized mystery / speculative thriller",
        tone="cinematic, intelligent, suspenseful, adult",
    )
    store.save_universe(universe)
    store.save_character(
        Character(
            id="mara-vale",
            universe_id=universe.id,
            name="Mara Vale",
            role="lead investigator",
            traits=["observant", "skeptical", "dry wit", "protective"],
            relationships={},
            voice_id="af_heart",
            visual_prompt="Mara Vale, woman in her 30s, dark tailored coat, expressive eyes, rain-soaked neon city at night, cinematic realism",
        )
    )
    store.save_character(
        Character(
            id="jonah-reed",
            universe_id=universe.id,
            name="Jonah Reed",
            role="transit dispatcher and reluctant ally",
            traits=["methodical", "anxious", "loyal", "knows the rail system intimately"],
            relationships={"mara-vale": "trusted but uneasy ally"},
            voice_id="am_michael",
            visual_prompt="Jonah Reed, man in his 40s, transit control room, tired eyes, rolled sleeves, analog maps and monitors, cinematic realism",
        )
    )
    store.save_episode(
        EpisodeRecord(
            id="nightshift-s1e1",
            universe_id=universe.id,
            season=1,
            number=1,
            title="Last Train Home",
            logline="A passenger appears on the final train even though every system says the car was empty.",
            summary="Mara investigates an impossible passenger record and finds a brass key stamped with tomorrow's date.",
            continuity=["Mara does not yet believe the phenomenon is supernatural."],
            unresolved_threads=["Who was passenger 17?", "What does the brass key open?", "Why is the key dated tomorrow?"],
        )
    )
    return store.story_context(universe.id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", help="Optional persistent SQLite story bible path")
    args = parser.parse_args()

    if args.database:
        store = StoryStore(Path(args.database))
        context = seed_demo(store)
        print(json.dumps(context, indent=2, ensure_ascii=False))
        return

    with tempfile.TemporaryDirectory(prefix="media-engine-story-") as tmp:
        store = StoryStore(Path(tmp) / "story.db")
        context = seed_demo(store)
        print(json.dumps(context, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

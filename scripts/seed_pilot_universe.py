#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from media_engine.story.pilot import PILOT_UNIVERSE, seed_pilot
from media_engine.story.store import StoryStore
from media_engine.story.writer import build_episode_prompt


def main() -> None:
    database = ROOT / "tmp" / "midnight-archive.db"
    database.parent.mkdir(parents=True, exist_ok=True)
    store = StoryStore(database)
    context = seed_pilot(store)
    prompt = build_episode_prompt(context, target_minutes=14)
    payload = {
        "status": "ok",
        "universe": PILOT_UNIVERSE.name,
        "database": str(database),
        "characters": [character["name"] for character in context["characters"]],
        "active_threads": context["active_threads"],
        "writer_prompt_chars": len(prompt),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

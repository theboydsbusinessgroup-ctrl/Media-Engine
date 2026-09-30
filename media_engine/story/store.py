from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Iterator

from .models import Character, EpisodeRecord, Universe


class StoryStore:
    """Persistent story bible for serialized Media Engine channels."""

    def __init__(self, database: str | Path = "media-engine-story.db") -> None:
        self.database = str(database)
        self._initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS universes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    premise TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    tone TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    universe_id TEXT NOT NULL REFERENCES universes(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    traits_json TEXT NOT NULL DEFAULT '[]',
                    relationships_json TEXT NOT NULL DEFAULT '{}',
                    voice_id TEXT NOT NULL DEFAULT '',
                    visual_prompt TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'active'
                );

                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    universe_id TEXT NOT NULL REFERENCES universes(id) ON DELETE CASCADE,
                    season INTEGER NOT NULL,
                    number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    logline TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    script TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'draft',
                    continuity_json TEXT NOT NULL DEFAULT '[]',
                    unresolved_json TEXT NOT NULL DEFAULT '[]',
                    resolved_json TEXT NOT NULL DEFAULT '[]',
                    published_url TEXT NOT NULL DEFAULT '',
                    UNIQUE(universe_id, season, number)
                );

                CREATE TABLE IF NOT EXISTS canon_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    universe_id TEXT NOT NULL REFERENCES universes(id) ON DELETE CASCADE,
                    episode_id TEXT REFERENCES episodes(id) ON DELETE SET NULL,
                    event_type TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    detail TEXT NOT NULL
                );
                """
            )

    def save_universe(self, universe: Universe) -> None:
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO universes(id, name, premise, genre, tone)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    premise=excluded.premise,
                    genre=excluded.genre,
                    tone=excluded.tone
                """,
                (universe.id, universe.name, universe.premise, universe.genre, universe.tone),
            )

    def save_character(self, character: Character) -> None:
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO characters(
                    id, universe_id, name, role, traits_json, relationships_json,
                    voice_id, visual_prompt, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    universe_id=excluded.universe_id,
                    name=excluded.name,
                    role=excluded.role,
                    traits_json=excluded.traits_json,
                    relationships_json=excluded.relationships_json,
                    voice_id=excluded.voice_id,
                    visual_prompt=excluded.visual_prompt,
                    status=excluded.status
                """,
                (
                    character.id,
                    character.universe_id,
                    character.name,
                    character.role,
                    json.dumps(character.traits),
                    json.dumps(character.relationships),
                    character.voice_id,
                    character.visual_prompt,
                    character.status,
                ),
            )

    def save_episode(self, episode: EpisodeRecord) -> None:
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO episodes(
                    id, universe_id, season, number, title, logline, summary, script,
                    status, continuity_json, unresolved_json, resolved_json, published_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    logline=excluded.logline,
                    summary=excluded.summary,
                    script=excluded.script,
                    status=excluded.status,
                    continuity_json=excluded.continuity_json,
                    unresolved_json=excluded.unresolved_json,
                    resolved_json=excluded.resolved_json,
                    published_url=excluded.published_url
                """,
                (
                    episode.id,
                    episode.universe_id,
                    episode.season,
                    episode.number,
                    episode.title,
                    episode.logline,
                    episode.summary,
                    episode.script,
                    episode.status,
                    json.dumps(episode.continuity),
                    json.dumps(episode.unresolved_threads),
                    json.dumps(episode.resolved_threads),
                    episode.published_url,
                ),
            )

    def add_canon_event(
        self,
        universe_id: str,
        *,
        event_type: str,
        subject: str,
        detail: str,
        episode_id: str | None = None,
    ) -> None:
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO canon_events(universe_id, episode_id, event_type, subject, detail)
                VALUES (?, ?, ?, ?, ?)
                """,
                (universe_id, episode_id, event_type, subject, detail),
            )

    def story_context(self, universe_id: str, *, episode_limit: int = 12) -> dict:
        with self.connect() as db:
            universe_row = db.execute(
                "SELECT * FROM universes WHERE id = ?", (universe_id,)
            ).fetchone()
            if universe_row is None:
                raise KeyError(f"Unknown universe: {universe_id}")

            character_rows = db.execute(
                "SELECT * FROM characters WHERE universe_id = ? ORDER BY name", (universe_id,)
            ).fetchall()
            episode_rows = db.execute(
                """
                SELECT * FROM episodes
                WHERE universe_id = ?
                ORDER BY season DESC, number DESC
                LIMIT ?
                """,
                (universe_id, episode_limit),
            ).fetchall()
            event_rows = db.execute(
                """
                SELECT event_type, subject, detail, episode_id
                FROM canon_events WHERE universe_id = ? ORDER BY id DESC LIMIT 100
                """,
                (universe_id,),
            ).fetchall()

        universe = dict(universe_row)
        characters = []
        for row in character_rows:
            item = dict(row)
            item["traits"] = json.loads(item.pop("traits_json"))
            item["relationships"] = json.loads(item.pop("relationships_json"))
            characters.append(item)

        episodes = []
        unresolved: list[str] = []
        resolved: set[str] = set()
        for row in reversed(episode_rows):
            item = dict(row)
            item["continuity"] = json.loads(item.pop("continuity_json"))
            item["unresolved_threads"] = json.loads(item.pop("unresolved_json"))
            item["resolved_threads"] = json.loads(item.pop("resolved_json"))
            unresolved.extend(item["unresolved_threads"])
            resolved.update(item["resolved_threads"])
            episodes.append(item)

        active_threads = [thread for thread in dict.fromkeys(unresolved) if thread not in resolved]
        return {
            "universe": universe,
            "characters": characters,
            "recent_episodes": episodes,
            "canon_events": [dict(row) for row in reversed(event_rows)],
            "active_threads": active_threads,
        }

    def export_snapshot(self, universe_id: str) -> str:
        return json.dumps(self.story_context(universe_id), indent=2, ensure_ascii=False)

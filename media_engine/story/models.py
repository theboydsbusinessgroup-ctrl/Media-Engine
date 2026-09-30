from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Universe:
    id: str
    name: str
    premise: str
    genre: str
    tone: str = ""


@dataclass(slots=True)
class Character:
    id: str
    universe_id: str
    name: str
    role: str
    traits: list[str] = field(default_factory=list)
    relationships: dict[str, str] = field(default_factory=dict)
    voice_id: str = ""
    visual_prompt: str = ""
    status: str = "active"


@dataclass(slots=True)
class EpisodeRecord:
    id: str
    universe_id: str
    season: int
    number: int
    title: str
    logline: str
    summary: str
    script: str = ""
    status: str = "draft"
    continuity: list[str] = field(default_factory=list)
    unresolved_threads: list[str] = field(default_factory=list)
    resolved_threads: list[str] = field(default_factory=list)
    published_url: str = ""

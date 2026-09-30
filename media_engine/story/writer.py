from __future__ import annotations

import json


def build_episode_prompt(context: dict, *, target_minutes: int = 14) -> str:
    episode = context["recent_episodes"][-1] if context.get("recent_episodes") else None
    if not episode:
        raise ValueError("Story context has no episode concept to develop")

    characters = context.get("characters", [])
    active_threads = context.get("active_threads", [])
    canon = context.get("canon_events", [])

    return f"""You are the head writer and continuity editor for an original serialized YouTube fiction series.

SERIES BIBLE
{json.dumps(context['universe'], indent=2, ensure_ascii=False)}

RECURRING CHARACTERS
{json.dumps(characters, indent=2, ensure_ascii=False)}

CANON EVENTS
{json.dumps(canon, indent=2, ensure_ascii=False)}

ACTIVE MYSTERIES / THREADS
{json.dumps(active_threads, indent=2, ensure_ascii=False)}

EPISODE TO WRITE
Title: {episode['title']}
Logline: {episode['logline']}
Approved story summary: {episode['summary']}
Continuity requirements: {json.dumps(episode['continuity'], ensure_ascii=False)}

Write a complete production-ready screenplay for approximately {target_minutes} minutes of finished runtime.

Requirements:
- Adult general-audience mystery/thriller. No sexual content, graphic gore, or gratuitous profanity.
- Open with a compelling visual or narrative question in the first 20 seconds.
- Use the approved summary as the spine, but dramatize it rather than narrating it.
- Preserve every established character trait, relationship, world rule, and continuity fact.
- Give each recurring character a distinct speaking rhythm and purpose.
- Keep exposition embedded in conflict, discovery, or humor.
- Build at least three escalating reversals before the final reveal.
- End on the approved Sublevel 7 / Mara box cliffhanger.
- Do not resolve the season mysteries listed as active threads.
- Favor 4 recurring/controllable locations: Intake Archive, Security Booth, City Systems Workspace, Freight Elevator/Corridor.
- Visual direction should be achievable with stylized generated stills/short motion clips and editorial camera movement.
- Avoid copyrighted characters, franchises, quotes, songs, brands, or imitation of living creators.
- Do not mention AI or the production process.

Return valid JSON only with this schema:
{{
  "title": "...",
  "runtime_target_minutes": {target_minutes},
  "cold_open": "one sentence hook description",
  "scenes": [
    {{
      "scene_number": 1,
      "location": "...",
      "time": "...",
      "purpose": "...",
      "visual_prompt": "consistent cinematic visual prompt",
      "beats": ["..."],
      "dialogue": [
        {{"character": "Mara Vale", "line": "..."}}
      ]
    }}
  ],
  "continuity_added": ["new facts established in this episode"],
  "threads_opened": ["new unresolved threads"],
  "threads_resolved": [],
  "thumbnail_concepts": ["three distinct high-CTR concepts without misleading clickbait"],
  "title_options": ["three title options"]
}}
"""

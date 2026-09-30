from __future__ import annotations

from .models import Character, EpisodeRecord, Universe


PILOT_UNIVERSE = Universe(
    id="midnight-archive",
    name="The Midnight Archive",
    premise=(
        "On the overnight shift inside a forgotten municipal archive, Mara Vale catalogs "
        "lost objects that sometimes arrive before they are lost. Each impossible item points "
        "toward a future event, while a larger mystery suggests the archive itself is choosing "
        "what the night crew is allowed to prevent."
    ),
    genre="serialized science-fiction mystery / neo-noir thriller",
    tone=(
        "adult general-audience; atmospheric, intelligent, tense, dryly funny, emotionally grounded; "
        "mystery-first rather than exposition-heavy"
    ),
)


PILOT_CHARACTERS = [
    Character(
        id="mara-vale",
        universe_id=PILOT_UNIVERSE.id,
        name="Mara Vale",
        role="lead; overnight municipal archivist",
        traits=[
            "observant",
            "skeptical",
            "methodical under pressure",
            "emotionally guarded",
            "cannot leave an unanswered question alone",
        ],
        relationships={
            "elias-rook": "trusted coworker whose instincts she relies on more than she admits",
            "nia-chen": "former university friend and unofficial technical lifeline",
        },
        voice_id="af_heart",
        visual_prompt=(
            "Mara Vale, early 30s, dark wavy shoulder-length hair, alert brown eyes, charcoal work shirt, "
            "archive ID badge, practical boots, restrained neo-noir styling, consistent facial identity, "
            "cinematic graphic-novel realism"
        ),
    ),
    Character(
        id="elias-rook",
        universe_id=PILOT_UNIVERSE.id,
        name="Elias Rook",
        role="night security officer; former paramedic",
        traits=[
            "dry humor",
            "calm in emergencies",
            "protective",
            "street-smart",
            "not easily impressed by authority",
        ],
        relationships={
            "mara-vale": "friend and night-shift partner; quietly protective without treating her as fragile"
        },
        voice_id="am_michael",
        visual_prompt=(
            "Elias Rook, late 30s, Black man, close-cropped hair, subtle scar through left eyebrow, "
            "navy municipal security jacket, warm but watchful expression, cinematic graphic-novel realism, "
            "consistent facial identity"
        ),
    ),
    Character(
        id="nia-chen",
        universe_id=PILOT_UNIVERSE.id,
        name="Nia Chen",
        role="city systems analyst; remote ally",
        traits=[
            "fast-talking",
            "technically brilliant",
            "curious",
            "irreverent",
            "risk-tolerant when a puzzle interests her",
        ],
        relationships={
            "mara-vale": "old friend who still knows when Mara is hiding fear behind logic"
        },
        voice_id="af_bella",
        visual_prompt=(
            "Nia Chen, early 30s, Chinese American woman, sharp bob haircut, expressive eyes, oversized headset, "
            "city operations workspace lit by cool monitors, cinematic graphic-novel realism, consistent facial identity"
        ),
    ),
]


PILOT_EPISODE = EpisodeRecord(
    id="midnight-archive-s01e01",
    universe_id=PILOT_UNIVERSE.id,
    season=1,
    number=1,
    title="The Watch That Counts Backward",
    logline=(
        "Mara receives a lost-property package dated one day in the future and addressed to herself; "
        "inside is a watch counting backward toward an event the archive seems determined to make her witness."
    ),
    summary=(
        "During a routine overnight shift, an unlogged courier bin appears in Intake. Mara finds a sealed evidence-style "
        "package whose recovery label lists her own name and tomorrow's date. Inside is an old pocket watch moving backward "
        "from forty-seven minutes. Elias initially suspects an elaborate prank, but the building's records show the package "
        "entered through a loading dock that has been permanently sealed for eleven years. Nia remotely checks the city's "
        "network and discovers a second impossibility: the package identifier already exists in the archive database, with a "
        "closed disposition code from 1989. As the countdown approaches zero, small events around the building begin matching "
        "details engraved inside the watch. Mara and Elias trace a power fluctuation to the freight elevator. At zero, the "
        "elevator opens onto a dark corridor labeled SUBLEVEL 7, although official plans end at Sublevel 3. A fresh archive box "
        "sits alone in the corridor. Its label reads: 'MARA VALE — DATE LOST: TONIGHT.' The doors begin to close before Mara can "
        "reach it. She jams the watch into the door track, stopping the elevator and committing herself to finding out what the "
        "Archive knows about her future."
    ),
    status="concept",
    continuity=[
        "The public building plans end at Sublevel 3.",
        "The sealed loading dock has officially been inaccessible for eleven years.",
        "Mara and Nia were university friends before taking separate city jobs.",
        "Elias previously worked as a paramedic.",
        "Objects can appear in the archive before the event that causes them to be lost.",
    ],
    unresolved_threads=[
        "What is on Sublevel 7?",
        "Why does the Archive have a future lost-property record for Mara?",
        "Who or what delivered the watch through the sealed loading dock?",
        "Why does the package ID also have a 1989 disposition record?",
        "Is the Archive predicting events or causing them?",
    ],
)


def seed_pilot(store) -> dict:
    store.save_universe(PILOT_UNIVERSE)
    for character in PILOT_CHARACTERS:
        store.save_character(character)
    store.save_episode(PILOT_EPISODE)
    store.add_canon_event(
        PILOT_UNIVERSE.id,
        event_type="world_rule",
        subject="The Archive",
        detail="At least some objects arrive before the event that causes them to be lost.",
        episode_id=PILOT_EPISODE.id,
    )
    store.add_canon_event(
        PILOT_UNIVERSE.id,
        event_type="location",
        subject="Sublevel 7",
        detail="A hidden floor exists below the municipal archive despite being absent from official plans.",
        episode_id=PILOT_EPISODE.id,
    )
    return store.story_context(PILOT_UNIVERSE.id)

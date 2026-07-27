"""Helpers for smart queue persistence

maintains the recently played history used by the smart queue, the queue
selection algorithm builds on these helpers but is kept separate so the
persistence layer remains simple and reusable
"""

import json
import os
from pathlib import Path
from .models import Track

RECENT_PLAYS_PATH = Path(os.getenv("RECENT_PLAYS_PATH", "data/recent_plays.json"))


def load_recent_plays() -> list[str]:
    """load the recently played video IDs
    missing or malformed files are treated as an empty history
    """

    if not RECENT_PLAYS_PATH.exists():
        return []

    try:
        with open(RECENT_PLAYS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [video_id for video_id in data if isinstance(video_id, str)]


def save_recent_plays(recent_plays: list[str]) -> None:
    """persist the recently played video IDs"""

    RECENT_PLAYS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RECENT_PLAYS_PATH, "w", encoding="utf-8") as f:
        json.dump(recent_plays, f, indent=2)


MAX_RECENT_BUFFER = 10
ARTIST_WINDOW = 5
ARTIST_PENALTY = 0.5


def compute_buffer_size(library_size: int) -> int:
    """return the size of the recent play buffer"""

    if library_size <= 1:
        return 0
    return min(MAX_RECENT_BUFFER, library_size // 2)


def recent_artists(
    tracks: list[Track], recent_plays: list[str], window: int = ARTIST_WINDOW
) -> set[str]:
    """ " return the artist that appeared in the recent artist winfow"""

    track_lookup = {track.video_id: track for track in tracks}
    artists: set[str] = set()
    for video_id in recent_plays[-window:]:
        track = track_lookup.get(video_id)
        if track is None:
            continue
        if not track.artist:
            continue
        artists.add(track.artist)

    return artists

"""Helpers for smart queue persistence

maintains the recently played history used by the smart queue, the queue
selection algorithm builds on these helpers but is kept separate so the
persistence layer remains simple and reusable
"""

import json
import os
from pathlib import Path

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

import json
from .models import Track
from . import queue


def make_track(video_id: str, artist: str) -> Track:
    return Track(
        video_id=video_id,
        title=video_id,
        artist=artist,
        album="",
        genres=[],
        mbid="",
        duration_seconds=180,
        url="",
        source="youtube",
        posted_by="tester",
        posted_at="",
    )


def test_compute_buffer_size():
    assert queue.compute_buffer_size(0) == 0
    assert queue.compute_buffer_size(1) == 0
    assert queue.compute_buffer_size(2) == 1
    assert queue.compute_buffer_size(6) == 3
    assert queue.compute_buffer_size(20) == 10


def test_recent_artists():
    tracks = [
        make_track("a", "Queen"),
        make_track("b", "Radiohead"),
        make_track("c", "Queen"),
    ]

    recent = ["a", "b", "c"]
    assert queue.recent_artists(tracks, recent) == {"Queen", "Radiohead"}


def test_load_recent_plays_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        queue,
        "RECENT_PLAYS_PATH",
        tmp_path / "recent_plays.json",
    )
    assert queue.load_recent_plays() == []


def test_load_recent_plays_invalid_json(tmp_path, monkeypatch):
    path = tmp_path / "recent_plays.json"
    path.write_text("{not json")
    monkeypatch.setattr(queue, "RECENT_PLAYS_PATH", path)
    assert queue.load_recent_plays() == []


def test_load_recent_plays_valid_json(tmp_path, monkeypatch):
    path = tmp_path / "recent_plays.json"
    path.write_text(json.dumps(["a", "b", "c"]))
    monkeypatch.setattr(queue, "RECENT_PLAYS_PATH", path)
    assert queue.load_recent_plays() == ["a", "b", "c"]


def test_pick_next_track_skips_recent(monkeypatch):
    tracks = [
        make_track("a", "Queen"),
        make_track("b", "Muse"),
        make_track("c", "Rush"),
    ]

    monkeypatch.setattr(queue, "load_tracks", lambda: tracks)
    monkeypatch.setattr(queue, "load_recent_plays", lambda: ["a"])
    saved = {}
    monkeypatch.setattr(
        queue,
        "save_recent_plays",
        lambda history: saved.setdefault("history", history),
    )

    def fake_choice(candidates, weights):
        assert "a" not in {track.video_id for track in candidates}
        return candidates[0]

    monkeypatch.setattr(queue, "_weighted_choice", fake_choice)
    selected = queue.pick_next_track()
    assert selected is not None
    assert selected.video_id == "b"
    assert saved["history"] == ["b"]


def test_pick_next_track_falls_back_when_everything_recent(monkeypatch):
    tracks = [make_track("a", "Queen")]

    monkeypatch.setattr(queue, "load_tracks", lambda: tracks)
    monkeypatch.setattr(queue, "load_recent_plays", lambda: ["a"])
    monkeypatch.setattr(queue, "save_recent_plays", lambda history: None)
    monkeypatch.setattr(
        queue,
        "_weighted_choice",
        lambda candidates, weights: candidates[0],
    )

    selected = queue.pick_next_track()
    assert selected is not None
    assert selected.video_id == "a"


def test_save_recent_plays(tmp_path, monkeypatch):
    path = tmp_path / "recent_plays.json"
    monkeypatch.setattr(queue, "RECENT_PLAYS_PATH", path)
    queue.save_recent_plays(["a", "b"])
    assert json.loads(path.read_text()) == ["a", "b"]

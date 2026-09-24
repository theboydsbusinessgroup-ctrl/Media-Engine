import pytest
from media_engine.providers.youtube_publisher import YouTubePublisher

def test_requires_oauth_configuration(monkeypatch):
    for key in ("YOUTUBE_CLIENT_ID","YOUTUBE_CLIENT_SECRET","YOUTUBE_REFRESH_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="YouTube OAuth"):
        YouTubePublisher()

def test_rejects_invalid_privacy():
    p=YouTubePublisher("id","secret","refresh")
    with pytest.raises(ValueError):
        p.upload("missing.mp4",title="x",privacy_status="friends")

def test_schedule_requires_private():
    p=YouTubePublisher("id","secret","refresh")
    with pytest.raises(ValueError, match="scheduled"):
        p.upload("missing.mp4",title="x",privacy_status="public",publish_at="2026-09-25T12:00:00Z")

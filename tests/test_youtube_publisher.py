import os
import unittest
from unittest.mock import patch

from media_engine.providers.youtube_publisher import YouTubePublisher


class YouTubePublisherTests(unittest.TestCase):
    def test_requires_oauth_configuration(self):
        with patch.dict(os.environ, clear=True):
            with self.assertRaisesRegex(RuntimeError, "YouTube OAuth"):
                YouTubePublisher()

    def test_rejects_invalid_privacy(self):
        publisher = YouTubePublisher("id", "secret", "refresh")
        with self.assertRaises(ValueError):
            publisher.upload("missing.mp4", title="x", privacy_status="friends")

    def test_schedule_requires_private(self):
        publisher = YouTubePublisher("id", "secret", "refresh")
        with self.assertRaisesRegex(ValueError, "scheduled"):
            publisher.upload(
                "missing.mp4",
                title="x",
                privacy_status="public",
                publish_at="2026-09-25T12:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()

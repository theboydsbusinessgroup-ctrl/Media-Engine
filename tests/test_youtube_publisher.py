import io
import json
import os
import unittest
from urllib.error import HTTPError
from unittest.mock import MagicMock, patch

from media_engine.providers.youtube_publisher import YouTubeOAuthError, YouTubePublisher


class YouTubePublisherTests(unittest.TestCase):
    def test_revoked_refresh_token_is_actionable_and_does_not_leak_credentials(self):
        error = HTTPError("https://oauth2.googleapis.com/token", 400, "Bad Request", {},
                          io.BytesIO(json.dumps({"error": "invalid_grant", "error_description": "secret"}).encode()))
        publisher = YouTubePublisher("id", "secret", "refresh")
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(YouTubeOAuthError) as raised:
                publisher.preflight()
        self.assertEqual(raised.exception.code, "invalid_grant")
        self.assertNotIn("secret", str(raised.exception))

    def test_preflight_caches_valid_token_for_upload(self):
        response = MagicMock()
        response.__enter__.return_value = io.StringIO(json.dumps({"access_token": "private", "expires_in": 3600}))
        publisher = YouTubePublisher("id", "secret", "refresh")
        with patch("urllib.request.urlopen", return_value=response) as request:
            self.assertIsNone(publisher.preflight())
            self.assertEqual(publisher._access_token(), "private")
        self.assertEqual(request.call_count, 1)

    def test_auth_failure_prevents_generation_and_rendering(self):
        from scripts import youtube_autonomous_short as engine
        with patch.object(engine, "YouTubePublisher") as publisher, \
             patch.object(engine, "generate_short_plan") as generate, \
             patch.object(engine, "render_short") as render:
            publisher.return_value.preflight.side_effect = YouTubeOAuthError("invalid_grant")
            with self.assertRaises(YouTubeOAuthError):
                engine.main()
        generate.assert_not_called()
        render.assert_not_called()

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

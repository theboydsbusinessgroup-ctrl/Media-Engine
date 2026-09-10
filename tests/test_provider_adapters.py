import io
import json
import unittest
from unittest.mock import patch

from media_engine.models import ContentBrief
from media_engine.providers.openrouter_generator import OpenRouterGenerator
from media_engine.providers.rss_discovery import GoogleNewsRSSDiscovery


class FakeResponse:
    def __init__(self, data: bytes): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.data


class ProviderTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_rss_discovery_returns_evidence_records(self, urlopen):
        xml = b'''<rss><channel><item><title>Automation tips - Example</title><link>https://news.google.com/a</link><pubDate>Thu, 10 Sep 2026 12:00:00 GMT</pubDate><source>Example</source></item></channel></rss>'''
        urlopen.return_value = FakeResponse(xml)
        rows = GoogleNewsRSSDiscovery().search("automation")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["authority_score"], 0.65)
        self.assertTrue(rows[0]["published_at"])

    @patch("urllib.request.urlopen")
    def test_openrouter_generator_parses_grounded_json(self, urlopen):
        api = {"choices":[{"message":{"content":json.dumps({"title":"Recurring Task System","body":"Group recurring work by frequency, document the steps, and review the system regularly.","claims":[]})}}]}
        urlopen.return_value = FakeResponse(json.dumps(api).encode())
        g = OpenRouterGenerator("test-key", model="inclusionai/ling-3.0-flash-vl:free")
        result = g.generate(ContentBrief("t1","Practical recurring task systems","owners","Organize recurring work",["Group by frequency"],["https://example.org/source"],"Save this"))
        self.assertEqual(result["title"], "Recurring Task System")
        self.assertEqual(result["claims"], [])

    def test_generator_refuses_missing_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                OpenRouterGenerator()

if __name__ == "__main__": unittest.main()

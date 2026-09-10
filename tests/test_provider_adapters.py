import json
import unittest
from unittest.mock import patch

from media_engine.models import ContentBrief, ContentDraft
from media_engine.providers.openrouter_generator import OpenRouterGenerator
from media_engine.providers.pinterest_transport import GatedPinterestTransport, PinterestTarget
from media_engine.providers.rss_discovery import GoogleNewsRSSDiscovery
from media_engine.quality import review


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
        self.assertTrue(rows[0]["published_at"])

    @patch("urllib.request.urlopen")
    def test_openrouter_generator_parses_grounded_json(self, urlopen):
        api = {"choices":[{"finish_reason":"stop","message":{"content":json.dumps({"title":"Recurring Task System","body":"Group recurring work by frequency, document the steps, and review the system regularly.","claims":[]})}}]}
        urlopen.return_value = FakeResponse(json.dumps(api).encode())
        g = OpenRouterGenerator("test-key")
        result = g.generate(ContentBrief("t1","Practical recurring task systems","owners","Organize recurring work",["Group by frequency"],["https://example.org/source"],"Save this"))
        self.assertEqual(result["title"], "Recurring Task System")

    @patch("urllib.request.urlopen")
    def test_openrouter_rejects_truncated_or_empty_output(self, urlopen):
        api = {"choices":[{"finish_reason":"length","message":{"content":None}}]}
        urlopen.return_value = FakeResponse(json.dumps(api).encode())
        with self.assertRaises(ValueError):
            OpenRouterGenerator("test-key").generate(ContentBrief("t","angle","owners","promise",["point"],["https://example.org"],"Save"))

    def test_live_pinterest_blocks_category_mismatch(self):
        calls=[]
        tx=GatedPinterestTransport(lambda payload: calls.append(payload) or {"id":"123"})
        draft=ContentDraft("c1","t1","Useful Automation Guide","A useful and sufficiently detailed body for owners.",evidence_urls=["https://example.org"])
        target=PinterestTarget("1","Wedding Planning Templates","wedding","https://example.org/image.png","Guide graphic")
        result=tx.publish(draft, review(draft), content_category="small_business", target=target)
        self.assertFalse(result.published)
        self.assertEqual(result.reason,"board_category_mismatch")
        self.assertEqual(calls,[])

    def test_live_pinterest_publishes_once_when_all_gates_match(self):
        calls=[]
        tx=GatedPinterestTransport(lambda payload: calls.append(payload) or {"id":"123"})
        draft=ContentDraft("c1","t1","Contractor Pricing Checklist","A practical checklist for reviewing contractor pricing before sending a quote.",destination_url="https://example.org",evidence_urls=["https://example.org/source"])
        target=PinterestTarget("1110630026797755152","Contractor Business Tools","contractor","https://example.org/image.png","Contractor pricing checklist")
        qa=review(draft)
        a=tx.publish(draft,qa,content_category="contractor",target=target)
        b=tx.publish(draft,qa,content_category="contractor",target=target)
        self.assertTrue(a.published)
        self.assertEqual(a.provider_post_id,"123")
        self.assertEqual(len(calls),1)
        self.assertEqual(a.idempotency_key,b.idempotency_key)

if __name__ == "__main__": unittest.main()

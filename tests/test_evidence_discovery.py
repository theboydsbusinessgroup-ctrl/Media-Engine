import unittest
from media_engine.discovery import discover_topics
from media_engine.models import ContentBrief
from media_engine.orchestration import MediaLoop


class FakeSearch:
    def search(self, query, *, limit=8):
        return [
            {"title":"Small Business Automation Checklist","url":"https://example.org/guide","excerpt":"Automate repetitive tasks first","authority_score":0.8,"freshness_score":0.7},
            {"title":"Small Business Automation Checklist","url":"https://example.net/report","excerpt":"Document the workflow before automating it","authority_score":0.9,"freshness_score":0.8},
        ]

class FakeGenerator:
    def generate(self, brief: ContentBrief):
        return {"title":"Small Business Automation Checklist","body":"Start with repetitive work, document each workflow, then automate one stable task at a time. Save this checklist for your next operations review.","claims":[]}

class EvidenceDiscoveryTests(unittest.TestCase):
    def test_discovery_builds_evidence_backed_topic(self):
        topics = discover_topics(FakeSearch(), ["small business automation"], audience="small business owners")
        self.assertEqual(len(topics), 1)
        self.assertEqual(len(topics[0].evidence), 2)
        self.assertGreater(topics[0].evidence_score, 0.5)

    def test_discovery_to_generation_to_qa_stays_dry_run(self):
        result = MediaLoop(generator=FakeGenerator()).run_discovery(FakeSearch(), ["small business automation"], audience="small business owners")
        self.assertEqual(result["status"], "publish_intent")
        self.assertEqual(result["evidence_count"], 2)
        self.assertEqual(result["generation_method"], "external_generator")
        self.assertTrue(result["qa"]["approved"])
        self.assertTrue(result["publication"]["dry_run"])

if __name__ == "__main__": unittest.main()

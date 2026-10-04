import unittest
from urllib.parse import urlparse, parse_qs
from media_engine.monetization import attach_offer, campaign_url, publication_receipt


class MonetizationTests(unittest.TestCase):
    def test_attribution_encodes_campaign_and_content(self):
        query = parse_qs(urlparse(campaign_url('a & b', 'v/1')).query)
        self.assertEqual(query['utm_campaign'], ['a & b'])
        self.assertEqual(query['utm_content'], ['v/1'])

    def test_spoken_offer_does_not_depend_on_shorts_links(self):
        original = {'script': 'Shake citrus cocktails.', 'description': 'Useful tip.', 'model': 'openrouter/free'}
        plan = attach_offer(original, 'campaign')
        self.assertIn('channel description', plan['script'])
        self.assertIn('/l/yknubt', plan['description'])
        self.assertEqual(original['script'], 'Shake citrus cocktails.')

    def test_posted_link_and_receipt_match_before_video_id_exists(self):
        plan = attach_offer({'script':'Tip.', 'description':'Description.', 'model':'free'}, 'campaign', 'run-123')
        receipt = publication_receipt(plan, 'actual_video_id', 'public')
        self.assertIn(receipt['product_url'], plan['description'])
        self.assertEqual(parse_qs(urlparse(receipt['product_url']).query)['utm_content'], ['run-123'])

    def test_blank_attribution_is_rejected(self):
        with self.assertRaises(ValueError):
            attach_offer({'script':'Tip.', 'description':'Description.'}, 'campaign', '')

    def test_receipt_is_not_revenue_and_contains_no_credentials(self):
        receipt = publication_receipt({'campaign': 'c', 'model': 'openrouter/free'}, 'video123', 'public')
        self.assertFalse(receipt['revenue_verified'])
        self.assertEqual(receipt['video_id'], 'video123')

    def test_missing_video_id_requires_provider_check(self):
        with self.assertRaises(RuntimeError):
            publication_receipt({'campaign': 'c', 'model': 'free'}, '', 'public')

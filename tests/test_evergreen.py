import json
import tempfile
import unittest
import sys
from unittest.mock import patch
from pathlib import Path
from media_engine.evergreen import evergreen_plan, LESSONS
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import youtube_autonomous_short_resilient as resilient


class EvergreenTests(unittest.TestCase):
    def test_empty_free_model_recovers_after_bounded_attempts(self):
        with patch.object(resilient,'_ORIGINAL_GENERATE_SHORT_PLAN',side_effect=RuntimeError('OpenRouter model openrouter/free returned empty content')) as generate:
            result=resilient.generate_short_plan_with_retries()
            self.assertEqual(generate.call_count,3)
            self.assertTrue(result['model'].startswith('editorial:'))

    def test_authentication_failure_never_retries_or_falls_back(self):
        with patch.object(resilient,'_ORIGINAL_GENERATE_SHORT_PLAN',side_effect=RuntimeError('OpenRouter request failed for model openrouter/free with HTTP 401')) as generate:
            with self.assertRaises(RuntimeError):resilient.generate_short_plan_with_retries()
            self.assertEqual(generate.call_count,1)

    def test_fallback_is_finite_and_never_reuses_archived_lesson(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            receipts=root/'data/publications';receipts.mkdir(parents=True)
            models=set()
            for index in range(len(LESSONS)):
                plan=evergreen_plan(root)
                self.assertNotIn(plan['model'],models)
                self.assertTrue(55<=len(plan['script'].split())<=95)
                models.add(plan['model'])
                (receipts/f'{index}.json').write_text(json.dumps({'model':plan['model']}))
            with self.assertRaises(RuntimeError):evergreen_plan(root)

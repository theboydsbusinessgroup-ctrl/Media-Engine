import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from media_engine.evergreen import LESSONS
from media_engine.monetization import attach_offer, MAX_SPOKEN_WORDS
sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import youtube_autonomous_short_resilient as resilient
engine = resilient.engine

class OfferIntegrationTests(unittest.TestCase):
    def test_generated_and_curated_bodies_leave_room_for_offer(self):
        payload={'title':'Choose your next bottle','script':' '.join(['word']*85),
                 'description':'Home-bar tip.', 'tags':['home bar'], 'hook_text':'Choose with a plan',
                 'broll_queries':['home bar']*5, '_model':'openrouter/free'}
        with patch.object(engine, '_openrouter_request', return_value=payload):
            plan=resilient._ORIGINAL_GENERATE_SHORT_PLAN()
        self.assertLessEqual(len(attach_offer(plan,'c','run')['script'].split()),MAX_SPOKEN_WORDS)
        for slug,title,script,_ in LESSONS:
            plan=attach_offer({'script':script,'description':title,'model':slug},'c','run')
            self.assertLessEqual(len(plan['script'].split()),MAX_SPOKEN_WORDS)

    def test_oversized_generated_body_is_retried_before_render(self):
        payload={'title':'Tip','script':' '.join(['word']*86)}
        with patch.object(engine, '_openrouter_request', return_value=payload):
            with self.assertRaisesRegex(RuntimeError,'outside safe bounds'):
                resilient._ORIGINAL_GENERATE_SHORT_PLAN()

    def test_offer_survives_caption_generation_and_cannot_overrun_script(self):
        plan=attach_offer({'script':' '.join(['word']*60),'description':'Tip','hook_text':'Start with a plan','model':'free'},'c','run')
        with tempfile.TemporaryDirectory() as directory:
            captions=engine.write_dynamic_captions(plan,30,Path(directory)).read_text()
            self.assertIn('$9 PDF | CHANNEL DESCRIPTION',captions)
            self.assertIn('Dialogue: 2,0:00:24.00,0:00:30.00,Offer',captions)
        with self.assertRaisesRegex(RuntimeError,'including the offer'):
            attach_offer({'script':' '.join(['word']*MAX_SPOKEN_WORDS),'description':'Tip'},'c','run')

if __name__=='__main__':unittest.main()

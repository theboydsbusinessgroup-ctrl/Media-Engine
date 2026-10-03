"""Approved offer attribution and sanitized publication receipts."""
from datetime import datetime, timezone
from urllib.parse import urlencode

PRODUCT_URL = 'https://boydsbusiness.gumroad.com/l/yknubt'
SPOKEN_CTA = 'Build your home bar one bottle at a time. Find my cocktail ebook in the channel description.'


def campaign_url(campaign: str, content: str = '') -> str:
    return PRODUCT_URL + '?' + urlencode({'utm_source': 'youtube', 'utm_medium': 'organic_video',
        'utm_campaign': campaign, 'utm_content': content})


def attach_offer(plan: dict, campaign: str) -> dict:
    result = dict(plan)
    result['script'] = result['script'].rstrip() + ' ' + SPOKEN_CTA
    result['description'] = result['description'].rstrip() + '\n\nOne Bottle at a Time: 15 cocktails, six bottles. $9 PDF ebook.\n' + campaign_url(campaign)
    result['campaign'] = campaign
    return result


def publication_receipt(plan: dict, video_id: str, privacy: str) -> dict:
    if not video_id:
        raise RuntimeError('Upload returned no video ID; check provider before retrying')
    return {'schema_version': 1, 'observed_at': datetime.now(timezone.utc).isoformat(),
        'campaign': plan['campaign'], 'video_id': video_id, 'privacy': privacy,
        'video_url': 'https://www.youtube.com/watch?v=' + video_id,
        'product_url': campaign_url(plan['campaign'], video_id),
        'revenue_verified': False, 'model': plan['model']}

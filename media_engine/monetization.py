"""Approved offer attribution and sanitized publication receipts."""
from datetime import datetime, timezone
from urllib.parse import urlencode

PRODUCT_URL = 'https://boydsbusiness.gumroad.com/l/yknubt'
SPOKEN_CTA = 'Want a six-bottle plan for fifteen cocktails? My nine-dollar PDF guide is in the channel description.'


def campaign_url(campaign: str, content: str = '') -> str:
    return PRODUCT_URL + '?' + urlencode({'utm_source': 'youtube', 'utm_medium': 'organic_video',
        'utm_campaign': campaign, 'utm_content': content})


def attach_offer(plan: dict, campaign: str, content: str = 'channel') -> dict:
    if not content.strip():
        raise ValueError('Offer attribution requires a content identifier')
    result = dict(plan)
    result['offer_url'] = campaign_url(campaign, content)
    result['script'] = result['script'].rstrip() + ' ' + SPOKEN_CTA
    result['description'] = result['description'].rstrip() + '\n\nOne Bottle at a Time: 15 cocktails, six bottles. $9 PDF ebook.\n' + result['offer_url']
    result['campaign'] = campaign
    return result


def publication_receipt(plan: dict, video_id: str, privacy: str) -> dict:
    if not video_id:
        raise RuntimeError('Upload returned no video ID; check provider before retrying')
    return {'schema_version': 1, 'observed_at': datetime.now(timezone.utc).isoformat(),
        'campaign': plan['campaign'], 'video_id': video_id, 'privacy': privacy,
        'video_url': 'https://www.youtube.com/watch?v=' + video_id,
        'product_url': plan.get('offer_url') or campaign_url(plan['campaign'], video_id),
        'revenue_verified': False, 'model': plan['model']}

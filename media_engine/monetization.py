"""Approved offer attribution and sanitized publication receipts."""
from datetime import datetime, timezone
from urllib.parse import urlencode

PRODUCT_URL = 'https://boydsbusiness.gumroad.com/l/yknubt'
SESSION_CODE = 'BARBUYER'
SESSION_REQUEST_EMAIL = 'theboydsbusinessgroup@gmail.com'
SPOKEN_CTA = 'Get my nine-dollar guide, then request a twenty-minute virtual session for nineteen dollars with code Bar Buyer. Email your receipt privately; details are in my channel description.'
MAX_SPOKEN_WORDS = 120


def buyer_session_message() -> str:
    return (
        'Ebook buyer offer: request a 20-minute virtual home-bar session for $19 with code ' + SESSION_CODE + '.\n'
        'Bring your bottle list and recipe questions. Email ' + SESSION_REQUEST_EMAIL + ' with subject ' + SESSION_CODE +
        ' and your ebook order ID, purchase email, timezone, and preferred times. Keep receipts private.\n'
        'One session per verified qualifying purchase; paid separately from the ebook. '
        'Purchase eligibility and a time are confirmed before payment. Availability by arrangement; drinking is not required.'
    )


def offer_message(url: str) -> str:
    return (
        'Before you buy another bottle, choose what you want to make.\n'
        'One Bottle at a Time connects a six-bottle home-bar plan with 15 cocktail recipes, '
        'exact measurements, clear methods, pro tips, and a Bar Build Map.\n'
        'Free recipes are available. This guide puts the shopping plan and the drinks in one reference.\n'
        'Get the 51-page PDF for $9: ' + url + '\n'
        'Digital guide; bottles and ingredients are not included. '
        'For adults of legal drinking age. Drink responsibly.\n\n' + buyer_session_message()
    )


def campaign_url(campaign: str, content: str = '') -> str:
    return PRODUCT_URL + '?' + urlencode({'utm_source': 'youtube', 'utm_medium': 'organic_video',
        'utm_campaign': campaign, 'utm_content': content})


def attach_offer(plan: dict, campaign: str, content: str = 'channel') -> dict:
    if not content.strip():
        raise ValueError('Offer attribution requires a content identifier')
    result = dict(plan)
    result['offer_url'] = campaign_url(campaign, content)
    result['script'] = result['script'].rstrip() + ' ' + SPOKEN_CTA
    if len(result['script'].split()) > MAX_SPOKEN_WORDS:
        raise RuntimeError('Final script exceeds spoken-word budget including the offer')
    result['description'] = offer_message(result['offer_url']) + '\n\n' + result['description'].rstrip()
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

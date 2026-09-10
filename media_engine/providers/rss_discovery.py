from __future__ import annotations

import html
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime


class GoogleNewsRSSDiscovery:
    """No-key public discovery provider using Google News RSS search.

    It returns evidence records compatible with Media Engine discovery. Network
    failures are surfaced to orchestration; callers decide retry/backoff policy.
    """

    def __init__(self, *, timeout: float = 10.0, user_agent: str = "MediaEngine/1.0"):
        self.timeout = timeout
        self.user_agent = user_agent

    def search(self, query: str, *, limit: int = 8) -> list[dict]:
        q = urllib.parse.quote_plus(query)
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            xml = resp.read()
        root = ET.fromstring(xml)
        results = []
        for item in root.findall("./channel/item")[:limit]:
            title = html.unescape((item.findtext("title") or "").strip())
            link = (item.findtext("link") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            source_node = item.find("source")
            source = (source_node.text or "").strip() if source_node is not None and source_node.text else ""
            if not title or not link:
                continue
            published_at = None
            freshness = 0.6
            if pub:
                try:
                    published_at = parsedate_to_datetime(pub).isoformat()
                    freshness = 0.9
                except (TypeError, ValueError):
                    pass
            results.append({
                "title": title,
                "url": link,
                "excerpt": f"Reported by {source}." if source else "Public news search result.",
                "published_at": published_at,
                "authority_score": 0.65,
                "freshness_score": freshness,
            })
        return results

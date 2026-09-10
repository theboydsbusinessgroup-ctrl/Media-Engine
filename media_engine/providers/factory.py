from __future__ import annotations
import os
from .openrouter_generator import OpenRouterGenerator
from .rss_discovery import GoogleNewsRSSDiscovery


def discovery_provider():
    provider = os.getenv("MEDIA_ENGINE_DISCOVERY_PROVIDER", "google_news_rss")
    if provider == "google_news_rss":
        return GoogleNewsRSSDiscovery()
    raise ValueError(f"Unsupported discovery provider: {provider}")


def content_generator():
    provider = os.getenv("MEDIA_ENGINE_GENERATION_PROVIDER", "fallback")
    if provider == "fallback":
        return None
    if provider == "openrouter":
        return OpenRouterGenerator()
    raise ValueError(f"Unsupported generation provider: {provider}")

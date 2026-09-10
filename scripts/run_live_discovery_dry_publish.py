#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from media_engine.orchestration import MediaLoop
from media_engine.providers.factory import content_generator, discovery_provider

loop = MediaLoop(generator=content_generator())
result = loop.run_discovery(
    discovery_provider(),
    ["small business automation practical tips", "solo business recurring task systems"],
    audience="small business owners",
    evergreen_score=0.72,
    monetization_score=0.62,
)
print(json.dumps(result, indent=2))

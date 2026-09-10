#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from media_engine.orchestration import MediaLoop

candidates = [
    {"title":"Simple systems that save small businesses time","audience":"small business owners","source":"seed","evidence_score":0.6,"evergreen_score":0.9,"monetization_score":0.7,"risk_score":0.05},
    {"title":"How to organize recurring business tasks","audience":"solo business owners","source":"seed","evidence_score":0.5,"evergreen_score":0.95,"monetization_score":0.6,"risk_score":0.02}
]
print(json.dumps(MediaLoop().run_once(candidates), indent=2))

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import asdict
from typing import Any

from ..models import ContentBrief


class OpenRouterGenerator:
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str | None = None, *, model: str | None = None, timeout: float = 30.0, max_tokens: int = 700):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("MEDIA_ENGINE_MODEL", "inclusionai/ling-3.0-flash-vl:free")
        self.timeout = timeout
        self.max_tokens = max_tokens
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for live generation")

    def generate(self, brief: ContentBrief) -> dict[str, Any]:
        prompt = (
            "Create concise Pinterest copy from this evidence-backed brief. "
            "Return JSON only with keys title, body, claims. claims must be an array. "
            "Do not invent statistics, endorsements, guarantees, time savings, performance outcomes, or numeric routines unless explicitly present in the brief. "
            "Distinguish suggestions from factual claims. Keep body under 450 characters.\n\nBRIEF:\n" + json.dumps(asdict(brief), ensure_ascii=False)
        )
        payload = self._request(prompt)
        choice = payload["choices"][0]
        content = (choice.get("message") or {}).get("content")
        finish = choice.get("finish_reason")
        if not content or finish == "length":
            raise ValueError(f"OpenRouter returned unusable generation (finish_reason={finish})")
        parsed = self._parse_json(content)
        body = str(parsed.get("body") or "")[:500]
        if not body:
            raise ValueError("OpenRouter generation body is empty")
        return {
            "title": str(parsed.get("title") or "")[:100],
            "body": body,
            "claims": [str(x) for x in parsed.get("claims", [])],
        }

    def _request(self, prompt: str) -> dict[str, Any]:
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role":"system","content":"You are Media Engine's careful content generator. Produce useful original copy grounded in supplied evidence. Return valid JSON only."},
                {"role":"user","content":prompt},
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.3,
        }).encode()
        req = urllib.request.Request(self.endpoint, data=body, method="POST", headers={
            "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/theboydsbusinessgroup-ctrl/Media-Engine", "X-Title": "Media Engine",
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].lstrip()
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("OpenRouter response did not contain JSON")
        parsed = json.loads(text[start:end+1])
        if not isinstance(parsed, dict):
            raise ValueError("OpenRouter response JSON must be an object")
        return parsed

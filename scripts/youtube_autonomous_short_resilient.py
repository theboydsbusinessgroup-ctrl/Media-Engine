#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

import youtube_autonomous_short as engine
from media_engine.evergreen import evergreen_plan


_ORIGINAL_GENERATE_SHORT_PLAN = engine.generate_short_plan


def generate_short_plan_with_retries() -> dict:
    """Regenerate recoverable AI output instead of aborting the publishing run."""
    max_attempts = min(3, max(1, int(os.getenv("YOUTUBE_PLAN_MAX_ATTEMPTS", "3"))))
    last_error: RuntimeError | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            plan = _ORIGINAL_GENERATE_SHORT_PLAN()
            if attempt > 1:
                print(
                    f"[media-engine] Short plan recovered on generation attempt {attempt}/{max_attempts}.",
                    file=sys.stderr,
                )
            return plan
        except RuntimeError as exc:
            message = str(exc)
            recoverable = (
                message.startswith("Generated script length is outside safe bounds:")
                or message == "Generated YouTube plan is missing title or script"
                or ('OpenRouter model' in message and ('empty content' in message or 'did not return JSON' in message))
                or ('OpenRouter request failed' in message and any('HTTP '+str(status) in message for status in (429,500,502,503,504)))
                or message == 'OpenRouter network unavailable'
            )
            if not recoverable:
                raise

            last_error = exc
            if attempt >= max_attempts:
                break

            print(
                f"[media-engine] Recoverable plan-generation error on attempt "
                f"{attempt}/{max_attempts}: {message}. Regenerating.",
                file=sys.stderr,
            )

    print('[media-engine] Free generation unavailable; using an unused editorial lesson.',file=sys.stderr)
    return evergreen_plan(engine.ROOT)


engine.generate_short_plan = generate_short_plan_with_retries


if __name__ == "__main__":
    engine.main()

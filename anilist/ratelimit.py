"""
anilist/ratelimit.py

Handles AniList API rate limiting and exponential backoff.
"""

import time

def handle_rate_limit(resp):
    """
    Detects AniList API rate limits.
    If rate limited, sleeps for Retry-After seconds or uses exponential backoff.
    Returns True if it handled the error and the caller should retry, False otherwise.
    """
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False

    def info(msg):
        if use_tqdm:
            tqdm.write(msg)
        else:
            print(msg)

    # AniList returns 429 for rate limit
    if resp.status_code == 429:
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                wait = int(retry_after)
            except Exception:
                wait = 15  # Default to 15 seconds
        else:
            wait = 15  # Default
        info(f"Rate limit hit. Waiting {wait} seconds before retrying...")
        time.sleep(wait)
        return True
    # Sometimes 400 with rate limit error in body
    try:
        data = resp.json()
        if "errors" in data:
            for err in data["errors"]:
                if "rate limit" in err.get("message", "").lower():
                    wait = 15
                    info(f"Rate limit error. Waiting {wait} seconds...")
                    time.sleep(wait)
                    return True
    except Exception:
        pass
    return False
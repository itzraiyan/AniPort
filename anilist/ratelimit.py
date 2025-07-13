"""
anilist/ratelimit.py

Handles AniList API rate limiting and exponential backoff.
"""

import time
import sys

rate_limit_counter = {"count": 0}

def handle_rate_limit(resp):
    """
    Detects AniList API rate limits.
    If rate limited, shows a spinner animation and waits for Retry-After seconds.
    Returns True if handled (should retry), or False if not a rate limit.
    """
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False

    try:
        from ui.colors import color_text
    except ImportError:
        def color_text(text, color): return text

    def info(msg, color=None):
        if color:
            msg = color_text(msg, color)
        if use_tqdm:
            tqdm.write(msg)
        else:
            print(msg)

    def spinner_wait(wait, hit_number):
        spinner = ['|', '/', '-', '\\']
        msg = f"Waiting... {wait} seconds [Rate limit hit #{hit_number}] (press Ctrl+C to cancel)"
        info(msg, color="RED")
        start = time.time()
        frame = 0
        try:
            while time.time() - start < wait:
                sys.stdout.write(color_text('\r' + f"[{spinner[frame % len(spinner)]}] Waiting...", "RED"))
                sys.stdout.flush()
                time.sleep(0.12)
                frame += 1
            # Clear line after waiting
            sys.stdout.write('\r' + ' ' * 40 + '\r')
            sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            sys.stdout.flush()
            info("Interrupted during rate limit wait. Exiting...", color="YELLOW")
            raise

    # AniList returns 429 for rate limit
    if resp.status_code == 429:
        rate_limit_counter["count"] += 1
        hit_number = rate_limit_counter["count"]
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                wait = int(float(retry_after))
            except Exception:
                wait = 15
        else:
            wait = 15
        spinner_wait(wait, hit_number)
        info("Rate limit wait over! Resuming your restoring process...", color="GREEN")
        return True

    # Sometimes 400 with rate limit error in body
    try:
        data = resp.json()
        if "errors" in data:
            for err in data["errors"]:
                if "rate limit" in err.get("message", "").lower():
                    rate_limit_counter["count"] += 1
                    hit_number = rate_limit_counter["count"]
                    wait = 15
                    spinner_wait(wait, hit_number)
                    info("Rate limit wait over! Resuming your restoring process...", color="GREEN")
                    return True
    except Exception:
        pass
    return False

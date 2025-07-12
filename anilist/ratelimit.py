"""
anilist/ratelimit.py

Handles AniList API rate limiting and exponential backoff.
"""

import time
import sys

def handle_rate_limit(resp):
    """
    Detects AniList API rate limits.
    If rate limited, shows a spinner/countdown animation and waits for Retry-After seconds.
    Returns True if it handled the error and the caller should retry, False otherwise.
    """
    # Helper for color
    def color_text(text, color):
        try:
            from colorama import Fore, Style, init as colorama_init
            colorama_init(autoreset=True)
            color_val = getattr(Fore, color.upper(), "")
            return f"{color_val}{text}{Style.RESET_ALL}"
        except ImportError:
            return text

    # Spinner animation for rate limit
    def spinner_countdown(wait):
        spinner = ['|', '/', '-', '\\']
        for remaining in range(wait, 0, -1):
            for frame in spinner:
                msg = f"[{frame}] Waiting... {remaining}s"
                sys.stdout.write('\r' + color_text(msg.ljust(32), "RED"))
                sys.stdout.flush()
                time.sleep(0.2)
        # Ensure last second is shown as 0 before finishing
        sys.stdout.write('\r' + color_text("[|] Waiting... 0s".ljust(32), "RED"))
        sys.stdout.flush()
        time.sleep(0.2)
        sys.stdout.write('\r' + ' ' * 40 + '\r')  # Clear line

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
        spinner_countdown(wait)
        # After wait, show green message
        resume_msg = color_text("Rate limit wait over! Resuming your restoring process...", "GREEN")
        print(resume_msg)
        return True
    # Sometimes 400 with rate limit error in body
    try:
        data = resp.json()
        if "errors" in data:
            for err in data["errors"]:
                if "rate limit" in err.get("message", "").lower():
                    wait = 15
                    spinner_countdown(wait)
                    resume_msg = color_text("Rate limit wait over! Resuming your restoring process...", "GREEN")
                    print(resume_msg)
                    return True
    except Exception:
        pass
    return False
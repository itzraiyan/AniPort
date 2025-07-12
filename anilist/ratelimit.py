"""
anilist/ratelimit.py

Handles AniList API rate limiting and exponential backoff.
"""

import time
import sys

# This variable will persist the rate limit count across calls for the current process.
rate_limit_counter = {"count": 0}

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

    # Spinner animation for rate limit, with unique label for each hit
    def spinner_countdown(wait, hit_number):
        spinner = ['|', '/', '-', '\\']
        # Only print a single prelude line for this wait
        label = f" [Rate limit hit #{hit_number}]"
        for remaining in range(wait, 0, -1):
            for frame in spinner:
                msg = f"[{frame}] Waiting... {remaining}s{label}"
                sys.stdout.write('\r' + color_text(msg.ljust(48), "RED"))
                sys.stdout.flush()
                time.sleep(0.2)
        # Ensure last second is shown as 0 before finishing
        sys.stdout.write('\r' + color_text(f"[|] Waiting... 0s{label}".ljust(48), "RED"))
        sys.stdout.flush()
        time.sleep(0.2)
        sys.stdout.write('\r' + ' ' * 54 + '\r')  # Clear line

    # Used to ensure we don't print the rate limit spinner if another handle_rate_limit is running
    if not hasattr(handle_rate_limit, "_in_spinner"):
        handle_rate_limit._in_spinner = False

    # AniList returns 429 for rate limit
    if resp.status_code == 429:
        if handle_rate_limit._in_spinner:
            # Already showing spinner, don't overlap
            return True
        handle_rate_limit._in_spinner = True
        rate_limit_counter["count"] += 1
        hit_number = rate_limit_counter["count"]
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            try:
                wait = int(retry_after)
            except Exception:
                wait = 15  # Default to 15 seconds
        else:
            wait = 15  # Default
        spinner_countdown(wait, hit_number)
        resume_msg = color_text("Rate limit wait over! Resuming your restoring process...", "GREEN")
        print(resume_msg)
        handle_rate_limit._in_spinner = False
        return True
    # Sometimes 400 with rate limit error in body
    try:
        data = resp.json()
        if "errors" in data:
            for err in data["errors"]:
                if "rate limit" in err.get("message", "").lower():
                    if handle_rate_limit._in_spinner:
                        return True
                    handle_rate_limit._in_spinner = True
                    rate_limit_counter["count"] += 1
                    hit_number = rate_limit_counter["count"]
                    wait = 15
                    spinner_countdown(wait, hit_number)
                    resume_msg = color_text("Rate limit wait over! Resuming your restoring process...", "GREEN")
                    print(resume_msg)
                    handle_rate_limit._in_spinner = False
                    return True
    except Exception:
        pass
    return False
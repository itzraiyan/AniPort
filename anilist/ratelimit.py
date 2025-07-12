"""
anilist/ratelimit.py

Handles AniList API rate limiting and exponential backoff.
"""

import time
import sys

# This variable persists the rate limit count across calls for the current process.
rate_limit_counter = {"count": 0}

def handle_rate_limit(resp):
    """
    Detects AniList API rate limits.
    If rate limited, shows a spinner/countdown animation and waits for Retry-After seconds.
    Returns True if it handled the error and the caller should retry, False otherwise.
    """

    def color_text(text, color):
        try:
            from colorama import Fore, Style, init as colorama_init
            colorama_init(autoreset=True)
            color_val = getattr(Fore, color.upper(), "")
            return f"{color_val}{text}{Style.RESET_ALL}"
        except ImportError:
            return text

    def spinner_wait(wait, hit_number):
        spinner = ['|', '/', '-', '\\']
        label = f" [Rate limit hit #{hit_number}]"
        msg = f"Waiting... {wait} seconds{label} (press Ctrl+C to cancel)"
        print(color_text(msg, "YELLOW"))
        try:
            t_end = time.time() + wait
            frame = 0
            while time.time() < t_end:
                sys.stdout.write('\r' + color_text(f"[{spinner[frame % len(spinner)]}] Waiting...", "RED"))
                sys.stdout.flush()
                time.sleep(0.12)
                frame += 1
            sys.stdout.write('\r' + ' ' * 40 + '\r')
            sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            sys.stdout.flush()
            print(color_text("Interrupted during rate limit wait. Exiting...", "YELLOW"))
            raise

    # Used to ensure we don't print the rate limit spinner if another handle_rate_limit is running
    if not hasattr(handle_rate_limit, "_in_spinner"):
        handle_rate_limit._in_spinner = False

    try:
        # AniList returns 429 for rate limit
        if resp.status_code == 429:
            if handle_rate_limit._in_spinner:
                return True
            handle_rate_limit._in_spinner = True
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
            resume_msg = color_text("Rate limit wait over! Resuming your restoring process...", "GREEN")
            print(resume_msg)
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
                        spinner_wait(wait, hit_number)
                        resume_msg = color_text("Rate limit wait over! Resuming your restoring process...", "GREEN")
                        print(resume_msg)
                        return True
        except Exception:
            pass
        return False
    finally:
        handle_rate_limit._in_spinner = False
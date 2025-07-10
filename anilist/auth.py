"""
anilist/auth.py

Handles all AniList OAuth:
- Guides user to input Client ID/Secret (with -help)
- Generates the proper auth URL
- Accepts redirected URL, extracts code
- Exchanges code for access token
"""

import requests
import urllib.parse
from ui.prompts import prompt_boxed, print_info, print_error, print_warning
from ui.helptext import AUTH_CLIENT_ID_HELP, AUTH_CLIENT_SECRET_HELP, AUTH_REDIRECT_URL_HELP

OAUTH_AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize"
OAUTH_TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
REDIRECT_URI = "http://localhost"  # Updated to match help prompt

def get_client_id():
    return prompt_boxed(
        "Enter your AniList API Client ID (type '-help' for help):",
        color="MAGENTA",
        helpmsg=AUTH_CLIENT_ID_HELP
    )

def get_client_secret():
    return prompt_boxed(
        "Enter your AniList API Client Secret (type '-help' for help):",
        color="MAGENTA",
        helpmsg=AUTH_CLIENT_SECRET_HELP
    )

def build_oauth_url(client_id, redirect_uri=REDIRECT_URI):
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
    }
    return OAUTH_AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)

def get_auth_code_from_user(auth_url):
    import sys
    import webbrowser

    print_info("To authenticate, you'll need to open a link, approve access, and copy a code.")
    print_warning("Step 1: Copy the URL below and open it in your browser. Log in and approve access.\n")
    print(auth_url + "\n")  # Plain, copyable, unboxed

    # Offer to open in default system browser (works on most platforms)
    open_in_browser = prompt_boxed(
        "Would you like to try opening this link in your system browser automatically? (y/N)",
        default="N", color="YELLOW"
    ).strip().lower()
    if open_in_browser == "y":
        try:
            webbrowser.open(auth_url)
            print_info("Attempted to open the link in your default browser.")
        except Exception:
            print_warning("Could not open the browser automatically. Please open the URL above manually.")

    print_warning("Step 2: After approving, AniList will redirect (or fail to connect to localhost, that's OK!).")
    print_warning("Copy the full URL from your browser's address bar (it will contain '?code=...'), and paste it below.\n")
    url = prompt_boxed(
        "Paste the entire redirected URL here:",
        color="CYAN",
        helpmsg=AUTH_REDIRECT_URL_HELP
    )
    # Extract code from URL
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    code = qs.get("code")
    if code:
        return code[0]
    # Sometimes code is in fragment
    frag = urllib.parse.parse_qs(parsed.fragment)
    if "code" in frag:
        return frag["code"][0]
    # Or as the last part of path
    if 'code=' in url:
        code = url.split('code=')[-1]
        if '&' in code:
            code = code.split('&')[0]
        return code
    raise Exception("No 'code' parameter found in the URL.")

def exchange_code_for_token(client_id, client_secret, code, redirect_uri=REDIRECT_URI):
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code
    }
    resp = requests.post(OAUTH_TOKEN_URL, data=data)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    print_error(f"Failed to obtain token: {resp.status_code} {resp.text}")
    return None

def interactive_oauth():
    """
    Guides the user through the AniList OAuth process.
    Returns the access token.
    """
    client_id = get_client_id()
    client_secret = get_client_secret()
    auth_url = build_oauth_url(client_id)
    code = get_auth_code_from_user(auth_url)
    token = exchange_code_for_token(client_id, client_secret, code)
    if not token:
        raise Exception("Failed to obtain access token.")
    return token
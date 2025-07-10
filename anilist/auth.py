"""
anilist/auth.py

Handles AniList OAuth:
- Guides user to input Client ID/Secret (with clear help)
- Generates the correct auth URL (plain, copyable)
- Optionally opens in browser
- Handles code extraction and token exchange robustly
"""

import requests
import urllib.parse
import webbrowser
from ui.prompts import prompt_boxed, print_info, print_error, print_warning, boxed_text

# Detailed help messages for each OAuth field
AUTH_CLIENT_ID_HELP = (
    "How to get your AniList Client ID:\n"
    "1. Go to: https://anilist.co/settings/developer\n"
    "2. Click 'Create New Client'.\n"
    "3. Name: Any name you like (e.g. AniPort Backup).\n"
    "4. Redirect URL: Use https://localhost/ or urn:ietf:wg:oauth:2.0:oob\n"
    "5. After creating, copy the Client ID from the table and paste it here."
)

AUTH_CLIENT_SECRET_HELP = (
    "How to get your AniList Client Secret:\n"
    "After creating your app at https://anilist.co/settings/developer, you'll see your Client Secret in the table.\n"
    "Copy it and paste it here. (Never share your secret with anyone else!)"
)

AUTH_REDIRECT_URL_HELP = (
    "After approving access in your browser, AniList will redirect you to a URL.\n"
    "Copy and paste the FULL URL (starting with https://localhost/ or urn:ietf:wg:oauth:2.0:oob...) here.\n"
    "This tool will extract the code automatically."
)

def build_oauth_url(client_id, redirect_uri="urn:ietf:wg:oauth:2.0:oob"):
    base_url = "https://anilist.co/api/v2/oauth/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def get_auth_code_from_user(auth_url):
    # Show the URL in a boxed info, but also as a plain line for copy-paste
    print_info("Please open the following link in your browser, approve access, and copy the ENTIRE redirected URL (with ?code=...):")
    print(boxed_text("Copy the plain (no borders) URL below:", "YELLOW", width=70))
    print("\n" + auth_url + "\n")  # plain, unwrapped, no borders

    # Offer to open in browser
    open_browser = prompt_boxed(
        "Open this link in your browser now? (y/N)",
        default="N",
        color="CYAN"
    ).strip().lower()
    if open_browser == "y":
        try:
            webbrowser.open(auth_url)
            print_info("Opened the link in your default browser.")
        except Exception:
            print_warning("Could not open browser automatically. Please open the link above manually.")

    redirected_url = prompt_boxed(
        "Paste the FULL URL you were redirected to after authorizing AniPort (it contains ?code=...):",
        color="CYAN",
        helpmsg=AUTH_REDIRECT_URL_HELP
    )
    # Extract ?code=... from the URL
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirected_url)
    qs = parse_qs(parsed.query)
    code = qs.get("code")
    if code:
        return code[0]
    # fallback: sometimes code in fragment
    frag = parse_qs(parsed.fragment)
    if "code" in frag:
        return frag["code"][0]
    # fallback: regex as last resort
    import re
    m = re.search(r"[?&]code=([^&]+)", redirected_url)
    if m:
        return m.group(1)
    print_error("Could not find ?code= in the URL. Please retry the OAuth flow.")
    return ""

def exchange_code_for_token(client_id, client_secret, code, redirect_uri="urn:ietf:wg:oauth:2.0:oob"):
    url = "https://anilist.co/api/v2/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code
    }
    resp = requests.post(url, data=data, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("access_token", "")
    print_error(f"Failed to exchange code for token: {resp.text}")
    return ""

def interactive_oauth():
    client_id = prompt_boxed(
        "Enter your AniList Client ID (see -help for instructions):",
        color="CYAN",
        helpmsg=AUTH_CLIENT_ID_HELP
    )
    client_secret = prompt_boxed(
        "Enter your AniList Client Secret (see -help for instructions):",
        color="CYAN",
        helpmsg=AUTH_CLIENT_SECRET_HELP
    )
    # Allow user to select redirect URI (power users)
    redirect_uri = prompt_boxed(
        "Redirect URI to use (default: urn:ietf:wg:oauth:2.0:oob):",
        default="urn:ietf:wg:oauth:2.0:oob",
        color="YELLOW"
    ) or "urn:ietf:wg:oauth:2.0:oob"
    auth_url = build_oauth_url(client_id, redirect_uri=redirect_uri)
    code = get_auth_code_from_user(auth_url)
    if not code:
        return ""
    token = exchange_code_for_token(client_id, client_secret, code, redirect_uri=redirect_uri)
    if not token:
        print_error("Failed to obtain access token. Please check your credentials and try again.")
    return token
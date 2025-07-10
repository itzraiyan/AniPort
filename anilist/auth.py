"""
anilist/auth.py

Handles AniList OAuth and multi-account management:
- Guides user to input Client ID/Secret (with -help)
- Generates the proper auth URL
- Accepts redirected URL, extracts code
- Exchanges code for access token
- Manages multiple saved AniList accounts (username + token)
"""

import os
import json
import requests
import urllib.parse
from ui.prompts import prompt_boxed, print_info, print_error, print_warning, menu_boxed
from ui.helptext import AUTH_CLIENT_ID_HELP, AUTH_CLIENT_SECRET_HELP, AUTH_REDIRECT_URL_HELP

OAUTH_AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize"
OAUTH_TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
REDIRECT_URI = "http://localhost"
ACCOUNTS_PATH = os.path.expanduser("~/.aniport_accounts.json")

def _load_accounts():
    if os.path.isfile(ACCOUNTS_PATH):
        try:
            with open(ACCOUNTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_accounts(accounts):
    try:
        with open(ACCOUNTS_PATH, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2)
    except Exception as e:
        print_error(f"Failed to save accounts: {e}")

def list_saved_accounts():
    accounts = _load_accounts()
    return list(accounts.keys())

def get_saved_token(username):
    accounts = _load_accounts()
    entry = accounts.get(username)
    if not entry:
        return None
    return entry.get("token")

def save_account_token(username, token, client_id=None, client_secret=None):
    accounts = _load_accounts()
    accounts[username] = {
        "token": token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    _save_accounts(accounts)

def remove_account(username):
    accounts = _load_accounts()
    if username in accounts:
        del accounts[username]
        _save_accounts(accounts)

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
    print_info("To authenticate, you'll need to open a link, approve access, and copy a code.")
    print_warning("Step 1: Copy the URL below and open it in your browser. Log in and approve access.\n")
    print(auth_url + "\n")  # Plain, copyable, unboxed

    print_warning("Step 2: After approving, AniList will redirect (or fail to connect to localhost, that's OK!).")
    print_warning("Copy the full URL from your browser's address bar (it will contain '?code=...'), and paste it below.\n")
    url = prompt_boxed(
        "Paste the entire redirected URL here:",
        color="CYAN",
        helpmsg=AUTH_REDIRECT_URL_HELP
    )
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    code = qs.get("code")
    if code:
        return code[0]
    frag = urllib.parse.parse_qs(parsed.fragment)
    if "code" in frag:
        return frag["code"][0]
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

def interactive_oauth(username=None):
    """
    Guides the user through the AniList OAuth process. Prompts for client ID/secret.
    Returns (username, access_token).
    """
    if not username:
        username = prompt_boxed(
            "Enter the AniList username for this account:",
            color="CYAN"
        )
    client_id = get_client_id()
    client_secret = get_client_secret()
    auth_url = build_oauth_url(client_id)
    code = get_auth_code_from_user(auth_url)
    token = exchange_code_for_token(client_id, client_secret, code)
    if not token:
        raise Exception("Failed to obtain access token.")
    # Save the credentials and token
    save_account_token(username, token, client_id, client_secret)
    return username, token

def choose_account_flow(known_username=None):
    """
    Prompts the user to pick from saved accounts or add a new one.
    Returns (username, token).
    """
    saved = list_saved_accounts()
    account_options = []
    helpmsg = (
        "Select an AniList account to use:\n"
        "- Use saved account: Use an AniList account you have previously authorized.\n"
        "- Add a new AniList account: Authorize a new AniList account and save it for future use.\n"
        "- Remove a saved account: Delete an account from the saved list.\n"
        "You can always add or remove accounts later."
    )

    if not saved:
        account_options.append("Add a new AniList account")
    else:
        if known_username and known_username not in saved:
            account_options.append(f"Add and use: {known_username} (not yet authorized)")
        for uname in saved:
            account_options.append(f"Use saved account: {uname}")
        account_options.append("Add a different AniList account")
        account_options.append("Remove a saved account")

    while True:
        idx = menu_boxed(
            "Choose an AniList account for this operation:",
            account_options,
            helpmsg=helpmsg
        )
        # No saved accounts
        if not saved:
            if idx == 1:
                uname, token = interactive_oauth()
                return uname, token
        else:
            saved_offset = 1 if known_username and known_username not in saved else 0
            if known_username and idx == 1:
                # Add and use known_username
                uname, token = interactive_oauth(known_username)
                return uname, token
            if idx <= len(saved) + saved_offset and idx > saved_offset:
                uname = saved[idx-1-saved_offset]
                token = get_saved_token(uname)
                if token:
                    return uname, token
                else:
                    print_error("Token missing or expired for that account. Please re-authorize.")
                    uname, token = interactive_oauth(uname)
                    return uname, token
            elif idx == len(account_options):  # Remove a saved account
                if not saved:
                    print_warning("No saved accounts to remove.")
                    continue
                remove_idx = menu_boxed(
                    "Select an account to remove:",
                    [uname for uname in saved],
                    helpmsg="Select the account you want to remove from the saved list."
                )
                remove_account(saved[remove_idx - 1])
                print_info("Account removed.")
                # Rebuild options and re-loop
                saved = list_saved_accounts()
                if not saved:
                    account_options = ["Add a new AniList account"]
                else:
                    account_options = []
                    if known_username and known_username not in saved:
                        account_options.append(f"Add and use: {known_username} (not yet authorized)")
                    for uname in saved:
                        account_options.append(f"Use saved account: {uname}")
                    account_options.append("Add a different AniList account")
                    account_options.append("Remove a saved account")
                continue
            else:
                # Add a different account
                uname, token = interactive_oauth()
                return uname, token

        print_warning("Please enter a valid number.")
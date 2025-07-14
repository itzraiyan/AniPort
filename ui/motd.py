import os
import hashlib
import json
import sys
from ui.colors import print_boxed_safe

try:
    import requests
except ImportError:
    requests = None  # We'll show a warning if requests is not installed

REMOTE_MOTD_URL = "https://raw.githubusercontent.com/itzraiyan/AniPort/main/motd.txt"
MOTD_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "motd.txt")

def get_state_file_path():
    # Save in ~/AniPort/.aniport_seen_motd.json (not in root)
    home = os.path.expanduser("~")
    aniport_dir = os.path.join(home, "AniPort")
    if not os.path.exists(aniport_dir):
        try:
            os.makedirs(aniport_dir, exist_ok=True)
        except Exception:
            pass
    return os.path.join(aniport_dir, ".aniport_seen_motd.json")

def get_motd_message():
    if not os.path.isfile(MOTD_FILE):
        return None
    try:
        with open(MOTD_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

def get_motd_hash(msg):
    return hashlib.sha256(msg.encode("utf-8")).hexdigest()

def has_seen_motd(msg_hash):
    state_file = get_state_file_path()
    if not os.path.isfile(state_file):
        return False
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
        return state.get("motd_hash") == msg_hash
    except Exception:
        return False

def record_seen_motd(msg_hash):
    state_file = get_state_file_path()
    try:
        with open(state_file, "w") as f:
            json.dump({"motd_hash": msg_hash}, f)
    except Exception:
        pass

def fetch_remote_motd():
    if not requests:
        return None  # Can't fetch without requests
    try:
        resp = requests.get(REMOTE_MOTD_URL, timeout=5)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None

def show_motd_if_needed():
    # 1. Try to fetch remote MOTD
    remote_msg = fetch_remote_motd()
    local_msg = get_motd_message()

    if remote_msg and (remote_msg.strip() != (local_msg or "").strip()):
        # If remote is different from local, show update prompt every time!
        print_boxed_safe(
            "A new AniPort update is available!\n\n"
            "The program has exited. Run 'git pull' to get the latest features & fixes.\n\n"
            "Update notes:\n" + remote_msg,
            "YELLOW", 60
        )
        sys.exit(0)

    # If remote is same as local, or remote unavailable, fallback to local MOTD logic
    msg = local_msg
    if not msg:
        return
    msg_hash = get_motd_hash(msg)
    if has_seen_motd(msg_hash):
        return
    print_boxed_safe(msg, "CYAN", 60)
    record_seen_motd(msg_hash)
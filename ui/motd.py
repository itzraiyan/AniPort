import os
import hashlib
import json
from ui.colors import print_boxed_safe

MOTD_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "motd.txt")
STATE_FILE = os.path.expanduser("~/.aniport_seen_motd.json")

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
    if not os.path.isfile(STATE_FILE):
        return False
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        return state.get("motd_hash") == msg_hash
    except Exception:
        return False

def record_seen_motd(msg_hash):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"motd_hash": msg_hash}, f)
    except Exception:
        pass

def show_motd_if_needed():
    msg = get_motd_message()
    if not msg:
        return
    msg_hash = get_motd_hash(msg)
    if has_seen_motd(msg_hash):
        return
    print_boxed_safe(msg, "YELLOW", 60)
    record_seen_motd(msg_hash)
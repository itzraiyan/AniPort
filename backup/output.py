"""
backup/output.py

- Ensures the output/ directory exists for backups.
- Handles file existence, overwrite confirmation, and basic JSON save/load helpers.
- Validates backup file structure for import.
- Adds left out file path helper for interrupted restores.
"""

import os
import json
from ui.prompts import confirm_boxed, print_error, print_success

OUTPUT_DIR = "output"

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def get_output_path(username, media_type):
    # e.g., output/AniXWeebs_anime_backup.json
    return os.path.join(OUTPUT_DIR, f"{username}_{media_type}_backup.json")

def save_json_backup(data, filename, overwrite=False):
    try:
        if os.path.isfile(filename) and not overwrite:
            if not confirm_boxed(f"File '{filename}' already exists. Overwrite?"):
                print_error(f"Skipped writing {filename}")
                return False
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print_success(f"Backup saved to {filename}")
        return True
    except Exception as e:
        print_error(f"Failed to save backup: {e}")
        return False

def load_json_backup(filepath):
    if not os.path.isfile(filepath):
        print_error(f"File '{filepath}' not found.")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print_error(f"Failed to load JSON backup: {e}")
        return None

def validate_backup_json(data):
    # Checks if JSON structure matches expected export format (list or dict with anime/manga keys)
    if isinstance(data, dict) and ("anime" in data or "manga" in data):
        return True
    if isinstance(data, list):
        # Old format: just a list of entries
        return True
    return False

def get_leftout_restore_path(orig_path):
    dirname, filename = os.path.split(orig_path)
    # Always name and overwrite leftout.json, never stack
    leftout_name = "leftout.json"
    return os.path.join(dirname or ".", leftout_name)
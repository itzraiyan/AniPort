"""
backup/importer.py

Coordinates the restore (import) workflow with multi-account support:
- Lets user select or add AniList accounts (token+username remembered).
- Looks for JSON backups in output/, helps user select or enter a path.
- Reads and validates backup JSON.
- Restores entries using SaveMediaListEntry (with rate limit handling and progress bar).
- Shows summary and friendly UI.
- Writes failed entries to a separate failed restore file if any.
- Shows detailed stats (total, restored, failed, time taken).
- Now: Verifies imported entries match backup, supports retry loop, and only saves failed JSON if needed.
"""

import os
import time
import traceback
from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar, print_warning
)
from backup.output import load_json_backup, validate_backup_json, OUTPUT_DIR, save_json_backup
from anilist.auth import choose_account_flow
from anilist.api import restore_entry, get_viewer_username, fetch_list
from ui.helptext import IMPORT_FILE_HELP

# Rich for tracebacks
try:
    from rich.console import Console
    from rich.traceback import Traceback
    rich_console = Console()
except ImportError:
    rich_console = None

def select_backup_file():
    candidates = []
    if os.path.isdir(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.lower().endswith(".json"):
                candidates.append(f)
    candidates.sort()
    if len(candidates) == 1:
        full_path = os.path.join(OUTPUT_DIR, candidates[0])
        prompt_msg = (
            f"Found one backup: {candidates[0]} in '{OUTPUT_DIR}/'.\n"
            f"Use this file? (Y/n)\n"
            "If you say no, you can enter a custom path.\n\n"
            "Tip: In Termux/Linux, you can open a new session and use tools like 'ls', 'realpath', or a file manager to browse files.\n"
            "You can also copy the path from your file explorer app."
        )
        use_default = prompt_boxed(prompt_msg, default="Y", color="CYAN").strip().lower()
        if use_default in ("", "y", "yes"):
            return full_path
    elif len(candidates) > 1:
        menu_msg = (
            "Multiple backup files found in 'output/'.\n"
            "Select which one to import, or choose 'Other...' to enter a custom path.\n"
            "Tip: In Termux/Linux, open a new session and use 'ls output', 'realpath', or a file manager to find your files and their full paths."
        )
        options = [f for f in candidates] + ["Other..."]
        while True:
            idx = menu_boxed(menu_msg, options)
            if 1 <= idx <= len(candidates):
                return os.path.join(OUTPUT_DIR, candidates[idx - 1])
            elif idx == len(options):  # Other...
                break
    else:
        print_warning("No backup JSON files found in 'output/'. You must provide a path.")

    while True:
        path = prompt_boxed(
            "Enter the full path to your backup JSON file (or drag-and-drop if your terminal supports it):",
            color="CYAN",
            helpmsg=(
                "You can locate your backup file using file managers or with CLI tools like 'ls', 'realpath', or 'find'.\n"
                "In Termux, open a new session and use: ls output/\n"
                "Example paths: output/your_backup.json, /data/data/com.termux/files/home/output/backup.json"
            )
        )
        if path:
            return path

def get_failed_restore_path(orig_path):
    """
    Given the original backup path, return a suitable failed import path.
    E.g., output/YourName_anime_backup.failed.json
    """
    dirname, filename = os.path.split(orig_path)
    base, ext = os.path.splitext(filename)
    failed_name = f"{base}.failed{ext}"
    return os.path.join(dirname or ".", failed_name)

def flatten_backup_entries(backup_data):
    """
    Returns a list of (media_type, entry) tuples from backup JSON.
    """
    entries = []
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        if "anime" in backup_data:
            entries.extend((("ANIME", e) for e in backup_data["anime"]))
        if "manga" in backup_data:
            entries.extend((("MANGA", e) for e in backup_data["manga"]))
    elif isinstance(backup_data, list):
        entries = [("ANIME", e) for e in backup_data]
    return entries

def get_entry_key(media_type, entry):
    """
    Returns a tuple key to uniquely identify a backup entry.
    Uses (media_type, media_id).
    """
    return (media_type, entry.get("media", {}).get("id"))

def fetch_imported_entry_keys(username, auth_token, backup_entries):
    """
    Fetches the current AniList entries for the user (for anime/manga types as needed).
    Returns a set of (media_type, media_id) keys.
    """
    types_needed = set([media_type for media_type, _ in backup_entries])
    keys = set()
    try:
        user_id = None
        # Only fetch user_id once
        for media_type in types_needed:
            if not user_id:
                from anilist.api import get_user_id
                user_id = get_user_id(username)
            entries = fetch_list(
                user_id, media_type,
                auth_token=auth_token
            )
            for entry in entries:
                keys.add((media_type, entry.get("media", {}).get("id")))
    except Exception as e:
        print_error(f"Error fetching imported entries for verification: {e}")
        if rich_console:
            rich_console.print(Traceback())
    return keys

def compare_entries(backup_entries, imported_keys):
    """
    Returns a list of (media_type, entry) tuples that are missing from imported list.
    """
    missing = []
    for media_type, entry in backup_entries:
        key = get_entry_key(media_type, entry)
        if key not in imported_keys:
            missing.append((media_type, entry))
    return missing

def import_entries(entries, auth_token):
    """
    Imports given (media_type, entry) tuples.
    Returns restored count, failed count, failed_entries list.
    """
    restored = 0
    failed = 0
    failed_entries = []
    for (media_type, entry) in print_progress_bar(entries, desc="Restoring"):
        try:
            ok = restore_entry(entry, media_type, auth_token)
        except Exception as e:
            ok = False
            print_error(f"Error restoring entry: {e}")
            if rich_console:
                rich_console.print(Traceback())
        if ok:
            restored += 1
        else:
            failed += 1
            failed_entries.append({"media_type": media_type, "entry": entry})
    return restored, failed, failed_entries

def import_workflow():
    print_info("Let's restore your AniList from a backup JSON!")

    filepath = None
    while not filepath:
        filepath = select_backup_file()
        if not load_json_backup(filepath):
            print_error("Invalid or missing file. Please try again.")
            filepath = None

    backup_data = load_json_backup(filepath)
    if not validate_backup_json(backup_data):
        print_error("This backup file is not valid or is from an unsupported format.")
        return

    # Multi-account: Choose import destination
    print_info("Select which AniList account to restore to.")
    username, auth_token = choose_account_flow()
    viewer = get_viewer_username(auth_token)
    print_info(f"Authenticated as AniList user: {viewer}")

    # Prepare entries to import
    backup_entries = flatten_backup_entries(backup_data)
    if not backup_entries:
        print_error("No entries found in backup.")
        return

    print_info(f"Ready to restore {len(backup_entries)} entries to account: {username}. This will add/update your AniList.")
    if not confirm_boxed("Proceed with restore?"):
        print_error("Restore cancelled.")
        return

    # Loop: import entries, verify, retry missing if user wants
    entries_to_import = backup_entries
    total_backup = len(backup_entries)
    start = time.time()

    loop_count = 1
    imported_keys = set()
    final_failed_entries = []
    restored_total = 0

    while True:
        print_info(f"Restore pass {loop_count}: Attempting to import {len(entries_to_import)} entries.")
        restored, failed, failed_entries = import_entries(entries_to_import, auth_token)
        restored_total += restored
        if failed:
            print_error(f"{failed} entries failed in this pass.")

        # Fetch imported entries and compare
        print_info("Verifying imported entries against backup...")
        imported_keys = fetch_imported_entry_keys(username, auth_token, backup_entries)
        missing_entries = compare_entries(backup_entries, imported_keys)
        missing_count = len(missing_entries)

        print_info(f"Verification: {total_backup - missing_count} / {total_backup} entries present in AniList.")
        if missing_count == 0:
            print_success("All entries have been successfully imported and verified!")
            final_failed_entries = []
            break

        print_warning(f"{missing_count} entries are still missing after restore.")
        # Prepare missing entries for next retry loop
        entries_to_import = missing_entries
        final_failed_entries = [{"media_type": mt, "entry": e} for mt, e in missing_entries]

        # Prompt user to retry
        retry = confirm_boxed("Retry failed/missing entries? (Y/N)")
        if not retry:
            break
        loop_count += 1

    end = time.time()
    elapsed = end - start

    print_success("Restore complete!")
    print_info(f"Stats:\n  Total in backup: {total_backup}\n  Successfully present: {total_backup - len(final_failed_entries)}\n  Still missing: {len(final_failed_entries)}\n  Time: {elapsed:.1f} sec")

    # Save failed JSON only if any entries are missing
    if final_failed_entries:
        failed_path = get_failed_restore_path(filepath)
        # Structure: same as input if possible (for easy re-import)
        if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
            failed_dict = {"anime": [], "manga": []}
            for item in final_failed_entries:
                mt = item["media_type"].lower()
                if mt in failed_dict:
                    failed_dict[mt].append(item["entry"])
            save_json_backup(failed_dict, failed_path)
        else:
            # Flat list
            failed_list = [item["entry"] for item in final_failed_entries]
            save_json_backup(failed_list, failed_path)
        print_error(f"Failed entries saved to: {failed_path}")
        print_info("You can retry importing this file later.")
    else:
        print_info("Your AniList should now match your backup!")

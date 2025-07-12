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
- Robust verification and account checking using token.
"""

import os
import time
from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar, print_warning
)
from backup.output import load_json_backup, validate_backup_json, OUTPUT_DIR, save_json_backup
from anilist.auth import choose_account_flow
from anilist.api import restore_entry, get_viewer_info, fetch_list
from ui.helptext import IMPORT_FILE_HELP

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

def get_entries_from_backup(backup_data):
    """
    Returns list of tuples: (media_type, entry)
    """
    entries = []
    # Dict with anime/manga keys
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        if "anime" in backup_data:
            entries.extend((("ANIME", e) for e in backup_data["anime"]))
        if "manga" in backup_data:
            entries.extend((("MANGA", e) for e in backup_data["manga"]))
    # Old format: flat list (must guess type)
    elif isinstance(backup_data, list):
        # Try to guess type from entries
        for e in backup_data:
            mtype = e.get("media", {}).get("type", None)
            if mtype in ("ANIME", "MANGA"):
                entries.append((mtype, e))
            else:
                entries.append(("ANIME", e))  # fallback, assume anime
    return entries

def get_entry_types_in_backup(backup_data):
    """Returns a set of types found: {"ANIME", "MANGA"}"""
    types = set()
    entries = get_entries_from_backup(backup_data)
    for media_type, _ in entries:
        types.add(media_type)
    return types

def verify_restored_entries(entries, auth_token):
    """
    Verifies how many entries (by media.id and type) are present in the AniList of the authenticated user.
    Only checks the types present in the backup!
    Returns: dict: { "ANIME": (present, total), "MANGA": (present, total) }
    """
    result = {}
    viewer_info = get_viewer_info(auth_token)
    if not viewer_info:
        print_error("Failed to fetch account info for verification.")
        return result
    user_id = viewer_info["id"]
    type_map = {"ANIME": [], "MANGA": []}
    for (media_type, entry) in entries:
        type_map[media_type].append(entry)
    for media_type in ["ANIME", "MANGA"]:
        if not type_map[media_type]:
            continue
        current_entries = fetch_list(user_id, media_type, auth_token=auth_token)
        current_ids = set(e["media"]["id"] for e in current_entries)
        total = len(type_map[media_type])
        present = sum(1 for e in type_map[media_type] if e["media"]["id"] in current_ids)
        # Debug info (optional)
        # print_info(f"Backup IDs ({media_type}): {[e['media']['id'] for e in type_map[media_type]]}")
        # print_info(f"AniList IDs ({media_type}): {list(current_ids)}")
        result[media_type] = (present, total)
    return result

def import_entries(entries, auth_token):
    restored = 0
    failed = 0
    failed_entries = []
    start = time.time()
    for (media_type, entry) in print_progress_bar(entries, desc="Restoring"):
        ok = restore_entry(entry, media_type, auth_token)
        if ok:
            restored += 1
        else:
            failed += 1
            failed_entries.append({"media_type": media_type, "entry": entry})
    elapsed = time.time() - start
    return restored, failed, failed_entries, elapsed

def save_failed_entries(failed_entries, backup_data, failed_path):
    # Structure: same as input if possible (for easy re-import)
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        failed_dict = {"anime": [], "manga": []}
        for item in failed_entries:
            mt = item["media_type"].lower()
            if mt in failed_dict:
                failed_dict[mt].append(item["entry"])
        save_json_backup(failed_dict, failed_path)
    else:
        # Flat list
        failed_list = [item["entry"] for item in failed_entries]
        save_json_backup(failed_list, failed_path)
    print_error(f"Failed entries saved to: {failed_path}")
    print_info("You can retry importing this file later.")

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

    viewer_info = get_viewer_info(auth_token)
    if not viewer_info:
        print_error("Failed to fetch authenticated account info. Aborting.")
        return
    print_info(f"Authenticated as AniList user: {viewer_info['username']} (ID: {viewer_info['id']})")

    # Warn if entered username does not match token account
    if username and username != viewer_info['username']:
        print_warning("Warning: The username you entered does not match the authenticated account.")
        print_warning(f"Token username: {viewer_info['username']}, entered username: {username}")
        if not confirm_boxed("Proceed anyway?"):
            print_error("Operation aborted.")
            return

    entries = get_entries_from_backup(backup_data)
    if not entries:
        print_error("No entries found in backup.")
        return

    entry_types = get_entry_types_in_backup(backup_data)
    entry_type_str = ", ".join(sorted(entry_types))
    print_info(f"Detected entry types in backup: {entry_type_str}")

    print_info(f"Ready to restore {len(entries)} entries to account: {viewer_info['username']}. This will add/update your AniList.")
    if not confirm_boxed("Proceed with restore?"):
        print_error("Restore cancelled.")
        return

    # Restore loop
    restored, failed, failed_entries, elapsed = import_entries(entries, auth_token)

    print_success(f"Restore complete!")
    print_info(f"Stats:\n  Total: {len(entries)}\n  Restored: {restored}\n  Failed: {failed}\n  Time: {elapsed:.1f} sec")

    # Verification step
    print_info("Verifying restored entries in AniList...")
    # Wait a bit for AniList API to reflect changes
    time.sleep(2)
    verify_result = verify_restored_entries(entries, auth_token)
    for mt in sorted(verify_result):
        present, total = verify_result[mt]
        print_info(f"Verification: {present} / {total} entries present in AniList ({mt}).")
        if total-present > 0:
            print_info(f"{total-present} entries are still missing after restore.")

    # Handle failed entries
    failed_path = get_failed_restore_path(filepath)
    if failed:
        print_error("Some entries could not be restored.")
        save_failed_entries(failed_entries, backup_data, failed_path)
        # Offer retry
        if confirm_boxed("Retry failed/missing entries? (y/N)"):
            # Load failed backup
            failed_data = load_json_backup(failed_path)
            retry_entries = get_entries_from_backup(failed_data)
            if not retry_entries:
                print_error("No entries in failed backup to retry.")
            else:
                print_info(f"Retrying {len(retry_entries)} failed entries...")
                r_restored, r_failed, r_failed_entries, r_elapsed = import_entries(retry_entries, auth_token)
                print_success("Retry restore complete!")
                print_info(f"Stats:\n  Total retried: {len(retry_entries)}\n  Restored: {r_restored}\n  Failed: {r_failed}\n  Time: {r_elapsed:.1f} sec")
                # Verification after retry
                print_info("Verifying entries after retry...")
                # Merge entries for verification (all that should be present now)
                all_entries = entries + retry_entries
                time.sleep(2)
                verify_result = verify_restored_entries(all_entries, auth_token)
                for mt in sorted(verify_result):
                    present, total = verify_result[mt]
                    print_info(f"Verification: {present} / {total} entries present in AniList ({mt}).")
                    if total-present > 0:
                        print_info(f"{total-present} entries are still missing after restore.")
                # Save failed again if any
                if r_failed:
                    save_failed_entries(r_failed_entries, failed_data, failed_path)
    else:
        print_info("Your AniList should now match your backup!")

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
- Explicit verification: checks that each imported entry is present in the user's AniList, regardless of total list size.
- Automatically creates missing custom lists as needed for imported entries.
"""

import os
import time
import sys
from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar, print_warning
)
from ui.colors import boxed_text
from backup.output import load_json_backup, validate_backup_json, OUTPUT_DIR, save_json_backup
from anilist.auth import choose_account_flow
from anilist.api import restore_entry, get_viewer_info, fetch_list, get_custom_lists, create_custom_list
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
    Explicit verification: For each imported entry, check if its media ID is present in the user's AniList after import.
    - Fetch the full list for each relevant media type (anime, manga).
    - For each imported entry, check if its media ID is present in the fetched list.
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
        imported_entries = type_map[media_type]
        if not imported_entries:
            continue
        # Fetch all user entries of this type (could be many, e.g. 100+)
        current_entries = fetch_list(user_id, media_type, auth_token=auth_token)
        current_ids = set(e["media"]["id"] for e in current_entries)
        imported_ids = set(e["media"]["id"] for e in imported_entries)
        # For each imported entry, check if its ID is present
        present = sum(1 for eid in imported_ids if eid in current_ids)
        total = len(imported_ids)
        result[media_type] = (present, total)
    return result

def import_entries(entries, auth_token):
    restored = 0
    failed = 0
    failed_entries = []
    start = time.time()

    # Pre-scan for missing custom lists and create them before import
    type_to_custom_lists = {"ANIME": set(), "MANGA": set()}
    for (media_type, entry) in entries:
        cl = entry.get("customList")
        if cl:
            type_to_custom_lists[media_type].add(cl)
    for media_type in ("ANIME", "MANGA"):
        if type_to_custom_lists[media_type]:
            existing = get_custom_lists(auth_token, media_type)
            missing = type_to_custom_lists[media_type] - existing
            for name in missing:
                print_info(f"Creating custom list '{name}' for {media_type} (if not already present)...")
                create_custom_list(auth_token, media_type, name)

    # Use tqdm.write for in-progress info to avoid breaking progress bar
    from tqdm import tqdm
    for (media_type, entry) in tqdm(entries, desc="Restoring", unit="item"):
        ok = restore_entry(entry, media_type, auth_token, auto_create_custom_lists=False)
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

def countdown_timer(seconds=20):
    # Improved: Only one box, updates in place. Uses ANSI escape to move cursor up.
    box_height = 5  # Estimate: top+bottom+2 lines of msg
    for i in range(seconds, 0, -1):
        msg = f"Please wait while AniList updates...\nCountdown: {i} seconds"
        print(boxed_text(msg, "YELLOW", 60))
        # Move cursor up by box height to overwrite on next print
        sys.stdout.write(f"\033[F" * box_height)
        sys.stdout.flush()
        time.sleep(1)
    # Print final box
    msg = "Proceeding to verification..."
    print(boxed_text(msg, "YELLOW", 60))

def print_post_verification_note():
    # Direct link to AniList settings
    link = "https://anilist.co/settings/list"
    note = (
        "Note:\n"
        "If you do not immediately see all your imported entries on AniList, don't worry!\n"
        "AniList sometimes requires a manual refresh for new entries to appear in your list.\n"
        "To update your list:\n"
        "  1. Go to your AniList list settings page: \n"
        f"     {link}\n"
        "  2. Click on “Update Stats” and then “Unhide Entries.”\n"
        "This will refresh your lists and make all imported entries visible.\n"
        "You can also try refreshing your browser after doing this."
    )
    print_info(note, width=60)

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

    # Restore loop (with pre-creation of custom lists as needed)
    restored, failed, failed_entries, elapsed = import_entries(entries, auth_token)

    print_success(f"Restore complete!")
    print_info(f"Stats:\n  Total: {len(entries)}\n  Restored: {restored}\n  Failed: {failed}\n  Time: {elapsed:.1f} sec")

    # Verification step with improved countdown
    countdown_timer(20)
    print_info("Verifying restored entries in AniList...")

    verify_result = verify_restored_entries(entries, auth_token)

    all_verified = True
    for mt in sorted(verify_result):
        present, total = verify_result[mt]
        print_info(f"Verification: {present} / {total} imported entries present in AniList ({mt}).")
        if present != total:
            print_info(f"{total-present} entries are still missing after restore.")
            all_verified = False

    # Show AniList refresh note IMMEDIATELY after the verification lines (before PASSED/FAILED summary)
    print_post_verification_note()

    # Final verification summary
    if all_verified:
        print_success("Verification PASSED: All imported entries are present in your AniList!")
    else:
        print_error("Verification FAILED: Some imported entries are missing from your AniList.")

    # Handle failed entries
    failed_path = get_failed_restore_path(filepath)
    if failed:
        print_error("Some entries could not be restored.")
        save_failed_entries(failed_entries, backup_data, failed_path)
        # Offer retry
        if confirm_boxed("Retry failed/missing entries?"):
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
                # Verification after retry with improved countdown
                countdown_timer(20)
                print_info("Verifying entries after retry...")

                all_entries = entries + retry_entries
                verify_result = verify_restored_entries(all_entries, auth_token)
                all_verified = True
                for mt in sorted(verify_result):
                    present, total = verify_result[mt]
                    print_info(f"Verification: {present} / {total} imported entries present in AniList ({mt}).")
                    if present != total:
                        print_info(f"{total-present} entries are still missing after restore.")
                        all_verified = False
                # Show AniList refresh note again after retry verification, before PASSED/FAILED summary
                print_post_verification_note()
                if all_verified:
                    print_success("Verification PASSED: All imported entries are present in your AniList!")
                else:
                    print_error("Verification FAILED: Some imported entries are missing from your AniList.")
                if r_failed:
                    save_failed_entries(r_failed_entries, failed_data, failed_path)
    else:
        print_info("Your AniList should now match your backup!")
        print_post_verification_note()
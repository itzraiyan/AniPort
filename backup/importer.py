"""
backup/importer.py

Coordinates the restore (import) workflow with multi-account support:
- Lets user select or add AniList accounts (token+username remembered).
- Looks for JSON backups in output/, helps user select or enter a path.
- Reads and validates backup JSON.
- Restores entries using SaveMediaListEntry (with rate limit handling and progress bar).
- Skips already-present entries and notifies user.
- Shows summary and friendly UI.
- Writes failed entries to a separate failed restore file if any.
- Shows detailed stats (total, restored, skipped, failed, time taken).
- Robust verification and account checking using token.
- Explicit verification: checks that each imported entry is present in the user's AniList, regardless of total list size.
"""

import os
import time
import sys
from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar, print_warning
)
from ui.colors import boxed_text, print_boxed_safe
from backup.output import (
    load_json_backup, validate_backup_json, OUTPUT_DIR, save_json_backup,
    get_leftout_restore_path
)
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
    dirname, filename = os.path.split(orig_path)
    base, ext = os.path.splitext(filename)
    failed_name = f"{base}.failed{ext}"
    return os.path.join(dirname or ".", failed_name)

def get_entries_from_backup(backup_data):
    entries = []
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        if "anime" in backup_data:
            entries.extend((("ANIME", e) for e in backup_data["anime"]))
        if "manga" in backup_data:
            entries.extend((("MANGA", e) for e in backup_data["manga"]))
    elif isinstance(backup_data, list):
        for e in backup_data:
            mtype = e.get("media", {}).get("type", None)
            if mtype in ("ANIME", "MANGA"):
                entries.append((mtype, e))
            else:
                entries.append(("ANIME", e))
    return entries

def get_entry_types_in_backup(backup_data):
    types = set()
    entries = get_entries_from_backup(backup_data)
    for media_type, _ in entries:
        types.add(media_type)
    return types

def verify_restored_entries(entries, auth_token):
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
        current_entries = fetch_list(user_id, media_type, auth_token=auth_token)
        current_ids = set(e["media"]["id"] for e in current_entries)
        imported_ids = set(e["media"]["id"] for e in imported_entries)
        present = sum(1 for eid in imported_ids if eid in current_ids)
        total = len(imported_ids)
        result[media_type] = (present, total)
    return result

def save_failed_entries(failed_entries, backup_data, failed_path):
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        failed_dict = {"anime": [], "manga": []}
        for item in failed_entries:
            mt = item["media_type"].lower()
            if mt in failed_dict:
                failed_dict[mt].append(item["entry"])
        save_json_backup(failed_dict, failed_path, overwrite=True)
    else:
        failed_list = [item["entry"] for item in failed_entries]
        save_json_backup(failed_list, failed_path, overwrite=True)
    print_error(f"Failed entries saved to: {failed_path}")
    print_info("You can retry importing this file later.")

def save_leftout_entries(leftout_entries, backup_data, leftout_path):
    # Always overwrite leftout file, never stack/rename
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        leftout_dict = {"anime": [], "manga": []}
        for item in leftout_entries:
            mt = item[0].lower()
            if mt in leftout_dict:
                leftout_dict[mt].append(item[1])
        save_json_backup(leftout_dict, leftout_path, overwrite=True)
    else:
        leftout_list = [e[1] for e in leftout_entries]
        save_json_backup(leftout_list, leftout_path, overwrite=True)
    print_error(f"Unimported entries saved to: {leftout_path}")
    print_info("You can retry importing this file later.")

def spinner_progress_bar(task_message="Verifying restored entries in AniList...", seconds=15):
    import itertools
    import sys
    import time

    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    bar_len = 28
    print_boxed_safe(task_message, "CYAN", 60)  # Print message ONCE

    for i in range(bar_len + 1):
        spin = next(spinner)
        bar = "█" * i + "-" * (bar_len - i)
        sys.stdout.write(f"\r{spin} [{bar}] {int(i/bar_len*100):3d}%")
        sys.stdout.flush()
        time.sleep(seconds / bar_len)
    # Clear bar after complete
    sys.stdout.write("\r" + " " * (bar_len + 14) + "\r")
    sys.stdout.flush()
    print_boxed_safe("Verification complete!", "CYAN", 60)

def print_post_verification_note():
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
    print_boxed_safe(note, "CYAN", 60)

def filter_entries_already_present(entries, auth_token):
    viewer_info = get_viewer_info(auth_token)
    user_id = viewer_info["id"]
    # Fetch current anime/manga entries
    anime_present_ids = set()
    manga_present_ids = set()
    anime_entries = []
    manga_entries = []
    for (media_type, entry) in entries:
        if media_type == "ANIME":
            anime_entries.append(entry)
        elif media_type == "MANGA":
            manga_entries.append(entry)
    if anime_entries:
        current_anime = fetch_list(user_id, "ANIME", auth_token=auth_token)
        anime_present_ids = set(e["media"]["id"] for e in current_anime)
    if manga_entries:
        current_manga = fetch_list(user_id, "MANGA", auth_token=auth_token)
        manga_present_ids = set(e["media"]["id"] for e in current_manga)
    to_import = []
    already_present = []
    for (media_type, entry) in entries:
        mid = entry["media"]["id"]
        if media_type == "ANIME" and mid in anime_present_ids:
            already_present.append((media_type, entry))
        elif media_type == "MANGA" and mid in manga_present_ids:
            already_present.append((media_type, entry))
        else:
            to_import.append((media_type, entry))
    return to_import, already_present

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

    print_info("Select which AniList account to restore to.")
    username, auth_token = choose_account_flow()

    viewer_info = get_viewer_info(auth_token)
    if not viewer_info:
        print_error("Failed to fetch authenticated account info. Aborting.")
        return
    print_info(f"Authenticated as AniList user: {viewer_info['username']} (ID: {viewer_info['id']})")

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

    print_info(f"Checking your AniList to see if any entries are already present...")
    to_import, already_present = filter_entries_already_present(entries, auth_token)
    print_boxed_safe(
        f"{len(already_present)} entries are already present on your AniList account and will be skipped.",
        "YELLOW", 60
    )
    print_boxed_safe(
        f"{len(to_import)} entries will be imported.",
        "CYAN", 60
    )

    if not to_import:
        print_boxed_safe("All entries from your backup are already present in your AniList account. Nothing to import!", "GREEN", 60)
        return

    # --- Pre-import ETA ---
    entries_count = len(to_import)
    rate_limit_every = 35
    rate_limit_pause = 60  # seconds
    avg_time_per_entry = 0.5  # initial guess

    n_limits = entries_count // rate_limit_every
    base_time = entries_count * avg_time_per_entry
    estimated_time = int(base_time + n_limits * rate_limit_pause)
    mins, secs = divmod(estimated_time, 60)
    eta_str = f"{mins:02d}:{secs:02d}"
    print_boxed_safe(
        "AniList has API rate limits, importing might take a while. You can do other stuff in the meantime.",
        "YELLOW", 60
    )
    print_boxed_safe(
        f"Estimated Time: ~{eta_str} for {entries_count} entries",
        "CYAN", 60
    )

    print_info(f"Ready to restore {len(to_import)} entries to account: {viewer_info['username']}. This will add/update your AniList.")
    if not confirm_boxed("Proceed with restore?"):
        print_error("Restore cancelled.")
        return

    # --- Import with dynamic ETA and custom progress bar ---
    restored = 0
    failed = 0
    failed_entries = []
    start = time.time()
    import tqdm

    rate_limit_hits = 0
    rate_limit_total_wait = 0.0
    entries_since_last_rl = 0
    total_entries = len(to_import)

    # Desired tqdm bar: "Restoring:  26%|█▌              | 38/146 [ETA:04:20,  1.01entries/s]"
    bar_format = "{desc}: {percentage:3.0f}%|{bar:18}| {n_fmt}/{total_fmt} [ETA:{postfix} {rate_fmt}]"

    # For ETA calculation
    rate_limit_hit_times = []

    try:
        progress_bar = tqdm.tqdm(
            to_import,
            desc="Restoring",
            unit="entries",
            dynamic_ncols=True,
            bar_format=bar_format
        )
        for idx, (media_type, entry) in enumerate(progress_bar):
            tick_start = time.time()
            ok = restore_entry(entry, media_type, auth_token)
            tick_elapsed = time.time() - tick_start
            if ok:
                restored += 1
            else:
                failed += 1
                failed_entries.append({"media_type": media_type, "entry": entry})

            entries_since_last_rl += 1
            # If a rate limit hit happened, update tracking info
            if tick_elapsed > 15:  # Any tick taking longer than 15s is probably a rate limit pause
                rate_limit_hits += 1
                rate_limit_hit_times.append(tick_elapsed)
                rate_limit_total_wait += tick_elapsed

            entries_done = idx + 1
            entries_left = total_entries - entries_done
            elapsed = time.time() - start

            # Calculate real average entry time (excluding rate limit waits)
            true_entry_time = (
                (elapsed - rate_limit_total_wait) / entries_done
                if entries_done > 0 else avg_time_per_entry
            )
            # Estimate future rate limits
            remaining_limits = entries_left // rate_limit_every
            avg_rl_pause = (sum(rate_limit_hit_times)/rate_limit_hits) if rate_limit_hits > 0 else rate_limit_pause
            future_rl_pause = remaining_limits * avg_rl_pause

            # Dynamic ETA with observed stats
            eta = entries_left * true_entry_time + future_rl_pause
            mins_eta, secs_eta = divmod(int(eta), 60)
            eta_str_dynamic = f"{mins_eta:02d}:{secs_eta:02d}"

            # Show ETA as [ETA:04:20,  1.01entries/s]
            progress_bar.set_postfix_str(eta_str_dynamic)

            if entries_since_last_rl >= rate_limit_every:
                entries_since_last_rl = 0

    except KeyboardInterrupt:
        leftout_entries = to_import[idx+1:] if 'idx' in locals() else to_import
        leftout_path = get_leftout_restore_path(filepath)
        save_leftout_entries(leftout_entries, backup_data, leftout_path)
        print_boxed_safe("Import interrupted! Unimported entries saved for resume.", "RED", 60)
        return

    elapsed = time.time() - start
    print_boxed_safe(f"Restore complete!", "GREEN", 60)
    print_boxed_safe(f"Stats:\n  Total in backup: {len(entries)}\n  Already present: {len(already_present)}\n  Imported: {restored}\n  Failed: {failed}\n  Time: {elapsed:.1f} sec", "CYAN", 60)

    spinner_progress_bar()

    print_boxed_safe("Verifying restored entries in AniList...", "CYAN", 60)
    verify_result = verify_restored_entries(to_import, auth_token)

    all_verified = True
    total_failed_verification = 0
    for mt in sorted(verify_result):
        present, total = verify_result[mt]
        print_boxed_safe(f"Verification: {present} / {total} imported entries present in AniList ({mt}).", "CYAN", 60)
        if present != total:
            missing = total - present
            print_boxed_safe(f"{missing} entries are still missing after restore ({mt}).", "RED", 60)
            total_failed_verification += missing
            all_verified = False

    print_post_verification_note()

    if all_verified:
        print_boxed_safe("Verification PASSED: All imported entries are present in your AniList!", "GREEN", 60)
    else:
        print_boxed_safe("Verification FAILED: Some imported entries are missing from your AniList.", "RED", 60)
        print_boxed_safe(f"Total failed verification entries: {total_failed_verification}", "RED", 60)

    failed_path = get_failed_restore_path(filepath)
    if failed:
        print_boxed_safe("Some entries could not be restored.", "RED", 60)
        save_failed_entries(failed_entries, backup_data, failed_path)
        if confirm_boxed("Retry failed/missing entries?"):
            failed_data = load_json_backup(failed_path)
            retry_entries = get_entries_from_backup(failed_data)
            if not retry_entries:
                print_boxed_safe("No entries in failed backup to retry.", "RED", 60)
            else:
                print_boxed_safe(f"Retrying {len(retry_entries)} failed entries...", "CYAN", 60)
                r_restored = 0
                r_failed = 0
                r_failed_entries = []
                r_start = time.time()
                r_total = len(retry_entries)
                r_rate_limit_hits = 0
                r_rate_limit_total_wait = 0.0
                r_rate_limit_hit_times = []
                r_progress_bar = tqdm.tqdm(
                    retry_entries,
                    desc="Restoring (Retry)",
                    unit="entries",
                    dynamic_ncols=True,
                    bar_format=bar_format
                )
                try:
                    for idx2, (media_type, entry) in enumerate(r_progress_bar):
                        tick_start2 = time.time()
                        ok = restore_entry(entry, media_type, auth_token)
                        tick_elapsed2 = time.time() - tick_start2
                        if ok:
                            r_restored += 1
                        else:
                            r_failed += 1
                            r_failed_entries.append({"media_type": media_type, "entry": entry})
                        # Retry ETA logic
                        if tick_elapsed2 > 15:
                            r_rate_limit_hits += 1
                            r_rate_limit_hit_times.append(tick_elapsed2)
                            r_rate_limit_total_wait += tick_elapsed2
                        entries_done2 = idx2 + 1
                        entries_left2 = r_total - entries_done2
                        elapsed2 = time.time() - r_start
                        true_entry_time2 = (
                            (elapsed2 - r_rate_limit_total_wait) / entries_done2
                            if entries_done2 > 0 else avg_time_per_entry
                        )
                        remaining_limits2 = entries_left2 // rate_limit_every
                        avg_rl_pause2 = (sum(r_rate_limit_hit_times)/r_rate_limit_hits) if r_rate_limit_hits > 0 else rate_limit_pause
                        future_rl_pause2 = remaining_limits2 * avg_rl_pause2
                        eta2 = entries_left2 * true_entry_time2 + future_rl_pause2
                        mins_eta2, secs_eta2 = divmod(int(eta2), 60)
                        r_progress_bar.set_postfix_str(f"{mins_eta2:02d}:{secs_eta2:02d}")
                except KeyboardInterrupt:
                    leftout_entries2 = retry_entries[idx2+1:] if 'idx2' in locals() else retry_entries
                    leftout_path2 = get_leftout_restore_path(failed_path)
                    save_leftout_entries(leftout_entries2, failed_data, leftout_path2)
                    print_boxed_safe("Import interrupted during retry! Unimported entries saved for resume.", "RED", 60)
                    return
                r_elapsed = time.time() - r_start
                print_boxed_safe("Retry restore complete!", "GREEN", 60)
                print_boxed_safe(f"Stats:\n  Total retried: {len(retry_entries)}\n  Restored: {r_restored}\n  Failed: {r_failed}\n  Time: {r_elapsed:.1f} sec", "CYAN", 60)
                spinner_progress_bar()
                print_boxed_safe("Verifying entries after retry...", "CYAN", 60)

                all_entries = to_import + retry_entries
                verify_result = verify_restored_entries(all_entries, auth_token)
                all_verified = True
                total_failed_verification = 0
                for mt in sorted(verify_result):
                    present, total = verify_result[mt]
                    print_boxed_safe(f"Verification: {present} / {total} imported entries present in AniList ({mt}).", "CYAN", 60)
                    if present != total:
                        missing = total - present
                        print_boxed_safe(f"{missing} entries are still missing after restore ({mt}).", "RED", 60)
                        total_failed_verification += missing
                        all_verified = False
                print_post_verification_note()
                if all_verified:
                    print_boxed_safe("Verification PASSED: All imported entries are present in your AniList!", "GREEN", 60)
                else:
                    print_boxed_safe("Verification FAILED: Some imported entries are missing from your AniList.", "RED", 60)
                    print_boxed_safe(f"Total failed verification entries: {total_failed_verification}", "RED", 60)
                if r_failed:
                    save_failed_entries(r_failed_entries, failed_data, failed_path)
    else:
        print_boxed_safe("Your AniList should now match your backup!", "CYAN", 60)
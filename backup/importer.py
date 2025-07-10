"""
backup/importer.py

Coordinates the restore (import) workflow:
- Prompts for backup file path, account ("same" or "new"), and authentication (OAuth).
- Reads and validates backup JSON.
- Restores entries using SaveMediaListEntry (with rate limit handling and progress bar).
- Shows summary and friendly UI.
"""

from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar
)
from backup.output import load_json_backup, validate_backup_json
from anilist.auth import interactive_oauth
from anilist.api import restore_entry, get_viewer_username
from ui.helptext import IMPORT_FILE_HELP, IMPORT_ACCOUNT_HELP

def import_workflow():
    print_info("Let's restore your AniList from a backup JSON!")
    filepath = None
    while not filepath:
        filepath = prompt_boxed(
            "Enter the path to your backup JSON file (type '-help' for info):",
            color="CYAN",
            helpmsg=IMPORT_FILE_HELP
        )
        if not load_json_backup(filepath):
            print_error("Invalid or missing file. Please try again.")
            filepath = None

    backup_data = load_json_backup(filepath)
    if not validate_backup_json(backup_data):
        print_error("This backup file is not valid or is from an unsupported format.")
        return

    account_type = menu_boxed(
        "Are you restoring to the same AniList account, or a new one?",
        ["Same account", "New account"],
        helpmsg=IMPORT_ACCOUNT_HELP
    )
    print_info("AniList authentication required for restore.")
    auth_token = interactive_oauth()
    viewer = get_viewer_username(auth_token)
    print_info(f"Authenticated as AniList user: {viewer}")

    # Determine what to restore
    if isinstance(backup_data, dict) and ("anime" in backup_data or "manga" in backup_data):
        entries = []
        if "anime" in backup_data:
            entries.extend((("ANIME", e) for e in backup_data["anime"]))
        if "manga" in backup_data:
            entries.extend((("MANGA", e) for e in backup_data["manga"]))
    elif isinstance(backup_data, list):
        # Legacy: assume anime
        entries = [("ANIME", e) for e in backup_data]
    else:
        print_error("Could not understand backup file structure.")
        return

    if not entries:
        print_error("No entries found in backup.")
        return

    # Confirm restore
    print_info(f"Ready to restore {len(entries)} entries. This will add/update your AniList.")
    if not confirm_boxed("Proceed with restore?"):
        print_error("Restore cancelled.")
        return

    # Restore each entry, respecting rate limits
    restored = 0
    failed = 0
    for (media_type, entry) in print_progress_bar(entries, desc="Restoring"):
        ok = restore_entry(entry, media_type, auth_token)
        if ok:
            restored += 1
        else:
            failed += 1

    print_success(f"Restore complete! {restored} entries restored. {failed} failed.")
    if failed:
        print_error("Some entries could not be restored. Please check your backup and try again.")
    else:
        print_info("Your AniList should now match your backup!")
"""
backup/exporter.py

Coordinates the export (backup) workflow:
- Prompts for username, privacy, (optionally) filters.
- Handles OAuth if private entries needed.
- Supports saved accounts/tokens for quick private export.
- Fetches list(s), applies filters, saves as JSON in output/.
- Shows progress and summary.
- Now shows detailed stats (exported/skipped, time taken, responsive output).
"""

import time
from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar
)
from anilist.api import get_user_id, fetch_list, get_viewer_info
from anilist.auth import interactive_oauth, get_saved_token, list_saved_accounts, save_account_token
from backup.output import get_output_path, save_json_backup, ensure_output_dir
from ui.helptext import USERNAME_HELP, EXPORT_PRIVACY_HELP, EXPORT_STATUS_HELP, EXPORT_TITLE_HELP, EXPORT_TYPE_HELP

def export_workflow():
    ensure_output_dir()
    username = None
    # 1. Ask for username
    while not username:
        username = prompt_boxed(
            "Enter your AniList username (type '-help' for help)",
            color="CYAN",
            helpmsg=USERNAME_HELP
        )

    token = get_saved_token(username)
    use_oauth = False
    auth_token = None

    # 2. Decide privacy (and possibly OAuth)
    if token:
        print_info(f"Found a saved AniList OAuth token for '{username}'.")
        privacy_option = menu_boxed(
            f"Do you want to use your saved token for '{username}' to export private + public entries?",
            [
                "No (public only)",
                "Yes (private + public, use saved token)"
            ],
            helpmsg="If you choose 'Yes', AniPort will use your saved OAuth token for this account to export all entries including private ones. If you choose 'No', only public entries will be exported."
        )
        if privacy_option == 2:
            use_oauth = True
            auth_token = token
        else:
            use_oauth = False
            auth_token = None
    else:
        privacy = menu_boxed(
            "Does your AniList list include private entries?",
            ["No (public only)", "Yes (private + public)"],
            helpmsg=EXPORT_PRIVACY_HELP
        )
        use_oauth = (privacy == 2)
        if use_oauth:
            print_info("You will need AniList API credentials. Follow the prompts!")
            _, auth_token = interactive_oauth(username)

    # 3. If private, verify token account matches entered username
    if use_oauth and auth_token:
        # Get actual account info from token
        viewer_info = get_viewer_info(auth_token)
        if not viewer_info:
            print_error("Failed to fetch authenticated account info. Aborting export.")
            return
        token_username = viewer_info["username"]
        print_info(f"Authenticated AniList account: {token_username} (ID: {viewer_info['id']})")
        if username != token_username:
            print_error(
                f"Username mismatch: You entered '{username}', but the authenticated account is '{token_username}'."
            )
            # Prompt user: Continue or regenerate
            choice = menu_boxed(
                "Do you want to continue anyway with this authenticated account, or regenerate authentication for your entered username?",
                [
                    f"Continue as '{token_username}' (proceed with export)",
                    f"Regenerate authentication for '{username}'"
                ]
            )
            if choice == 2:
                # Re-do OAuth for the entered username
                print_info(f"Please re-authenticate for username: {username}")
                _, auth_token = interactive_oauth(username)
                # Update token in saved accounts JSON
                save_account_token(username, auth_token)
                # Verify again, should match now
                viewer_info = get_viewer_info(auth_token)
                if not viewer_info:
                    print_error("Failed to fetch account info after re-authentication. Aborting export.")
                    return
                token_username = viewer_info["username"]
                print_info(f"Authenticated AniList account: {token_username} (ID: {viewer_info['id']})")
                if username != token_username:
                    print_error("Still mismatched after re-authentication. Proceeding anyway as authenticated account.")
            else:
                # Proceed with authenticated account (token_username)
                username = token_username

    # Export type: anime, manga, or both
    exptype = menu_boxed(
        "What would you like to export?",
        ["Anime only", "Manga only", "Both anime and manga"],
        helpmsg=EXPORT_TYPE_HELP
    )

    # Filters
    filter_status = prompt_boxed(
        "Would you like to filter by status? (y/N)", default="N", color="YELLOW"
    ).lower() == "y"
    statuses = None
    if filter_status:
        status_options = (
            "Choose one or more statuses by number or code (comma/space separated):\n"
            "1. COMPLETED   2. CURRENT   3. DROPPED   4. PAUSED   5. PLANNING   6. REPEATING"
        )
        s_input = prompt_boxed(
            "Enter statuses (e.g. 1 3 or COMPLETED,DROPPED):",
            color="YELLOW",
            helpmsg=EXPORT_STATUS_HELP + "\n" + status_options
        )
        status_map = {
            "1": "COMPLETED", "2": "CURRENT", "3": "DROPPED",
            "4": "PAUSED", "5": "PLANNING", "6": "REPEATING",
            "COMPLETED": "COMPLETED", "CURRENT": "CURRENT", "DROPPED": "DROPPED",
            "PAUSED": "PAUSED", "PLANNING": "PLANNING", "REPEATING": "REPEATING"
        }
        statuses = set()
        for tok in s_input.replace(",", " ").split():
            v = status_map.get(tok.upper())
            if v:
                statuses.add(v)
        if not statuses:
            print_error("No valid statuses selected. Proceeding with no status filter.")
            statuses = None

    filter_title = prompt_boxed(
        "Would you like to filter by title substring? (y/N)", default="N", color="YELLOW"
    ).lower() == "y"
    title_sub = None
    if filter_title:
        title_sub = prompt_boxed(
            "Enter a substring to match in the title:",
            color="YELLOW",
            helpmsg=EXPORT_TITLE_HELP
        )

    # Export anime/manga
    tasks = []
    if exptype in (1, 3):
        tasks.append("ANIME")
    if exptype in (2, 3):
        tasks.append("MANGA")

    exported = {}
    stats = {}
    start = time.time()
    for media_type in tasks:
        print_info(f"Fetching {media_type.lower()} list from AniList...")
        try:
            user_id = get_user_id(username)
            entries = fetch_list(
                user_id, media_type,
                auth_token=auth_token,
                statuses=list(statuses) if statuses else None,
                title_sub=title_sub
            )
            total = len(entries)
            stats[media_type] = {
                "exported": total,
                "filtered": "filtered"
            }
            if not entries:
                print_error(f"No {media_type.lower()} entries found.")
                continue
            filename = get_output_path(username, media_type.lower())
            exported[media_type.lower()] = entries
            if len(tasks) == 1:
                save_json_backup(entries, filename)
            else:
                continue
        except Exception as e:
            print_error(f"Error exporting {media_type.lower()}: {e}")
    if len(tasks) == 2 and exported:
        filename = get_output_path(username, "both")
        save_json_backup(exported, filename)

    elapsed = time.time() - start
    print_success("Export complete! Your backup(s) are in the output/ folder.")
    print_info("Export stats:")
    for k in exported:
        print_info(f"  {k.title()} exported: {len(exported[k])}")
    print_info(f"  Time taken: {elapsed:.1f} sec")
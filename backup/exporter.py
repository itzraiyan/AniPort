"""
backup/exporter.py

Coordinates the export (backup) workflow:
- Prompts for username, privacy, (optionally) filters.
- Handles OAuth if private entries needed.
- Fetches list(s), applies filters, saves as JSON in output/.
- Shows progress and summary.
"""

from ui.prompts import (
    prompt_boxed, print_info, print_success, print_error,
    confirm_boxed, menu_boxed, print_progress_bar
)
from anilist.api import get_user_id, fetch_list
from anilist.auth import interactive_oauth
from backup.output import get_output_path, save_json_backup, ensure_output_dir
from ui.helptext import USERNAME_HELP, EXPORT_PRIVACY_HELP, EXPORT_STATUS_HELP, EXPORT_TITLE_HELP, EXPORT_TYPE_HELP

def export_workflow():
    ensure_output_dir()

    username = None
    while not username:
        username = prompt_boxed(
            "Enter your AniList username (type '-help' for help)",
            color="CYAN",
            helpmsg=USERNAME_HELP
        )

    privacy = menu_boxed(
        "Does your AniList list include private entries?",
        ["No (public only)", "Yes (private + public)"],
        helpmsg=EXPORT_PRIVACY_HELP
    )
    use_oauth = (privacy == 2)
    auth_token = None
    if use_oauth:
        print_info("You will need AniList API credentials. Follow the prompts!")
        auth_token = interactive_oauth()

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
        # Simple parser for statuses
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
            if not entries:
                print_error(f"No {media_type.lower()} entries found.")
                continue
            filename = get_output_path(username, media_type.lower())
            # Save as single dict if both anime and manga, else just a list
            exported[media_type.lower()] = entries
            if len(tasks) == 1:
                # Just anime or manga: save list only
                save_json_backup(entries, filename)
            else:
                # Both: save after both fetched
                continue
        except Exception as e:
            print_error(f"Error exporting {media_type.lower()}: {e}")
    if len(tasks) == 2 and exported:
        filename = get_output_path(username, "both")
        save_json_backup(exported, filename)
    print_success("Export complete! Your backup(s) are in the output/ folder.")

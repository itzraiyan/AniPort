TOOL_OVERVIEW = (
    "AniPort: AniList Backup & Restore Tool\n"
    "─────────────────────────────────────────────\n"
    "• Termux- and terminal-friendly, fully interactive and responsive UI.\n"
    "• Anime-themed banners, boxed text, and inspirational quotes at every session.\n"
    "• Easily export (backup) your AniList anime/manga lists to local JSON files in the output/ folder.\n"
    "• Import (restore) backups to any AniList account, including full OAuth authentication for private entries.\n"
    "• Account management: save multiple AniList accounts, switch and verify before import/export.\n"
    "• Smart filtering: export by status and/or title substring for tailored backups.\n"
    "• Secure: OAuth authentication, never asks for your AniList password.\n"
    "• Robust rate limit handling, built-in progress bars and responsive feedback for every operation.\n"
    "• Detailed summaries after backup/restore: see how many entries were processed, failed, or verified, with clear tips.\n"
    "• Failed entries are saved for easy retry; verification ensures your AniList matches your backup after restore.\n"
    "• All prompts support -help for context-sensitive guidance.\n"
    "• Designed for all skill levels—zero coding required!\n"
    "• Works on Android (Termux), Linux, Windows, and more.\n"
    "• For AniList only (not MAL).\n"
    "─────────────────────────────────────────────\n"
    "Enjoy secure, anime-powered backups and restores—your lists are safe and your experience is fun!"
)

MAIN_MENU_HELP = (
    "Choose what you'd like to do:\n"
    "1: Export - Backup your AniList lists as JSON files (anime and/or manga).\n"
    "2: Import - Restore a backup JSON to any AniList account (with authentication and verification).\n"
    "3: Learn more - Get a detailed overview about features, flows, and UI tips.\n"
    "4: Exit - Leave the tool.\n"
    "Type -help at any prompt for context-sensitive help."
)

AUTH_CLIENT_ID_HELP = (
    "To get your AniList Client ID:\n"
    "1. Go to: https://anilist.co/settings/developer\n"
    "2. Click 'Create New Client'.\n"
    "3. Name = AniPort, Redirect URL = http://localhost\n"
    "4. Click 'Create' and copy the Client ID from the table.\n"
    "Paste that value here."
)

AUTH_CLIENT_SECRET_HELP = (
    "After creating your AniPort client on AniList, copy the Client Secret from the developer table and paste it here."
)

AUTH_REDIRECT_URL_HELP = (
    "After approving access in your browser, AniList will redirect you to a page (it may fail to connect, that's OK!).\n"
    "Copy the full URL from your browser's address bar (it will contain ?code=...), and paste it here."
)

USERNAME_HELP = (
    "Enter your AniList username (as shown on your AniList profile page).\n"
    "This is not your email—use your display name!"
)

EXPORT_PRIVACY_HELP = (
    "Choose 'Yes' if you want private entries included (requires OAuth authentication).\n"
    "Choose 'No' for public entries only (no authentication needed)."
)

EXPORT_TYPE_HELP = (
    "Anime only: Export just your anime list.\n"
    "Manga only: Export just your manga list.\n"
    "Both: Export both lists together."
)

EXPORT_STATUS_HELP = (
    "Export only entries with specific statuses (e.g. Completed, Watching).\n"
    "Type status code or number (separated by spaces or commas):\n"
    "1. COMPLETED   2. CURRENT   3. DROPPED   4. PAUSED   5. PLANNING   6. REPEATING"
)

EXPORT_TITLE_HELP = (
    "Export only entries whose title contains a specific substring (case-insensitive)."
)

IMPORT_FILE_HELP = (
    "Enter the path to a backup JSON file created by this tool (e.g., output/MyAnimeName_anime_backup.json).\n"
    "You may select from detected files, or enter a custom path if needed."
)

IMPORT_ACCOUNT_HELP = (
    "Choose which AniList account to restore to:\n"
    "- Use a saved account (previously authenticated)\n"
    "- Add a new account (requires OAuth)\n"
    "- Remove a saved account\n"
    "Account verification is automatic; the tool will warn if you mismatch usernames."
)
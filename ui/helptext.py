TOOL_OVERVIEW = (
    "AniList Backup & Restore Tool\n"
    "-----------------------------------\n"
    "• Export (backup) your anime/manga lists from AniList as JSON files.\n"
    "    - Public and private entries supported.\n"
    "    - Filter by status (e.g., Completed, Watching) or title.\n"
    "    - No authentication needed for public lists; OAuth for private entries.\n"
    "• Restore (import) a backup to any AniList account.\n"
    "    - Full OAuth authentication required for importing.\n"
    "    - Handles AniList rate limiting safely.\n"
    "• All operations are fully terminal/Termux-friendly, with anime-themed banners, colors, and -help at every prompt!\n"
    "• Your data is exported to the output/ folder.\n"
    "• No MAL here! This tool is for AniList only.\n"
    "• Enjoy the anime vibes and keep your lists safe!\n"
)

MAIN_MENU_HELP = (
    "Choose what you'd like to do:\n"
    "1: Export - Backup your AniList lists as JSON files.\n"
    "2: Import - Restore a backup JSON to an AniList account (requires authentication).\n"
    "3: Learn more - Get detailed explanation about all features and how the tool works.\n"
    "4: Exit - Leave the tool.\n"
    "Type -help at any prompt for context-sensitive help."
)

# ----- ADDED BELOW -----
AUTH_CLIENT_ID_HELP = (
    "Your AniList Client ID is required for private list export or restore.\n"
    "Find it at: https://anilist.co/settings/developer\n"
    "Click 'Create New Client' if you haven't made one before. After creation, copy the Client ID from the table."
)

AUTH_CLIENT_SECRET_HELP = (
    "Your AniList Client Secret is shown next to your Client ID in the AniList developer settings.\n"
    "This is needed to complete the OAuth authentication for private access."
)

AUTH_REDIRECT_URL_HELP = (
    "After you approve access in your browser, AniList will redirect you to a URL.\n"
    "Copy and paste the entire URL (starting with https://...) here.\n"
    "The code needed for authentication will be extracted automatically."
)

USERNAME_HELP = (
    "Enter your AniList username. This is the name shown on your AniList profile page."
)

EXPORT_PRIVACY_HELP = (
    "If you want to export private list entries, choose 'Yes' and follow the OAuth prompts.\n"
    "Otherwise, 'No' will export only public entries and requires no authentication."
)

EXPORT_TYPE_HELP = (
    "Choose 'Anime only' to export only your anime list, 'Manga only' for manga, or 'Both' for both lists."
)

EXPORT_STATUS_HELP = (
    "You can filter exported entries by status (e.g. COMPLETED, CURRENT, DROPPED).\n"
    "Enter status numbers or codes, separated by spaces or commas."
)

EXPORT_TITLE_HELP = (
    "You can filter exported entries by title substring. Only entries whose title includes the given text (case-insensitive) will be exported."
)

IMPORT_FILE_HELP = (
    "This should be the path to a JSON backup created by this tool (e.g., output/YourName_anime_backup.json)."
)

IMPORT_ACCOUNT_HELP = (
    "Choose 'Same account' if you're restoring to the account you exported from.\n"
    "Choose 'New account' if you're moving your list to another AniList account."
)
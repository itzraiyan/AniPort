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

AUTH_CLIENT_ID_HELP = (
    "To get your AniList Client ID:\n"
    "1. Go to: https://anilist.co/settings/developer\n"
    "2. Click 'Create New Client'.\n"
    "3. For the name, enter: AniPort\n"
    "4. For the Redirect URL, enter: http://localhost\n"
    "5. Click 'Create'.\n"
    "6. After creating, copy the Client ID shown in the table.\n"
    "Paste that value here."
)

AUTH_CLIENT_SECRET_HELP = (
    "After creating your AniPort client on AniList (see previous help),\n"
    "copy the Client Secret shown in the developer table and paste it here."
)

AUTH_REDIRECT_URL_HELP = (
    "After you approve access in your browser, AniList will redirect you to a page (it may fail to open on localhost, that's OK!).\n"
    "Just copy the full URL from your browser's address bar (it will contain ?code=...), and paste it here.\n"
    "The tool will extract the code automatically."
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
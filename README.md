# AniPort: AniList Backup & Restore Tool ⚙️

![AniPort Banner](https://files.catbox.moe/jx8op2.png)

> **Note:** This project contains AI-generated content. While much of the code and documentation is crafted with the help of AI tools, the overall design and intent are shaped by the project owner.

---

AniPort is a beginner-friendly, interactive Python tool for **backing up and restoring your AniList anime and manga lists**. Whether you want a safe copy of your lists, plan to migrate data, or just like to keep your anime and manga adventures safe, AniPort has you covered.

---

## ✨ Features (Now in Full Detail!)

* 🖼️ **Anime-themed terminal interface**
  - Random ASCII art banners appear on launch for an immersive experience.
  - Inspirational anime quotes are shown to brighten your session.
  - All prompts and messages use colors and boxed text for maximum readability.
  - Human-friendly explanations are available at every prompt—type `-help` for context-sensitive help.

* 🗂️ **Export (backup) your AniList lists**
  - Export both anime and manga lists, including public and private entries.
  - Backups are saved as well-structured JSON files in the `output/` folder.
  - You can filter exported entries by status (e.g., Completed, Watching) or by a title substring.
  - Export type selection: Anime only, Manga only, or Both.
  - Detailed progress bar and stats at the end of the export.
  - Privacy options: Export just public entries (no authentication needed), or include private entries (OAuth required).
  - Supports saved OAuth tokens for quick private exports.

* 🔄 **Import (restore) backups to any AniList account**
  - Robust validation of backup files (supports both old and new formats).
  - Multi-account support: Save and reuse multiple AniList accounts and tokens.
  - Friendly account selection and management UI—add, choose, or remove accounts easily.
  - Explicit account verification: Tool checks the authenticated username and ID before restoring.
  - Restore process uses the AniList API’s SaveMediaListEntry mutation for each entry, with progress bars and stats.
  - Failed restores are saved to a `.failed.json` for easy retry.
  - Detailed verification after restore: Compares imported entries to your AniList to ensure everything matches.
  - Option to retry failed/missing entries instantly.
  - Post-verification tips to help you refresh your AniList and see new entries.

* 🔍 **Smart filtering**
  - Export by status (Completed, Watching, Dropped, etc.) with easy number/code selection.
  - Export by title substring (case-insensitive).
  - Filters are applied before backup is created, ensuring only desired entries are saved.

* 🔒 **Secure authentication**
  - Uses AniList OAuth for private entries and for restoring backups.
  - Never asks for your AniList password—uses secure API tokens only.
  - Guides you through getting your AniList API Client ID and Client Secret step-by-step.
  - OAuth tokens are stored locally in your home directory (`~/.aniport_accounts.json`) and can be deleted at any time.

* 📂 **Local-only data storage**
  - All backups are saved in the `output/` folder.
  - No data or tokens are sent anywhere except AniList API.
  - You have full control over your files and accounts.

* 🛡️ **Rate limit protection**
  - AniList API rate limits are detected and handled gracefully.
  - Friendly spinner animation and countdown during rate limit waits.
  - The restore process automatically retries after rate limits.

* 🐍 **Pure Python, no platform lock-in**
  - Works on Android (Termux), Linux, and Windows.
  - No external dependencies except standard Python packages and those listed in `requirements.txt`.
  - No need for advanced coding knowledge—every step is guided.

* 🌱 **Zero coding required**
  - All operations are interactive—just run and follow the prompts.
  - Designed for all skill levels, with extra help and explanations everywhere.

* 🧑‍💻 **Account and token verification**
  - Ensures the correct AniList account is being used for backup/restore.
  - Clear warnings if entered username does not match authenticated token account.
  - Always displays authenticated username and ID before restoring—prevents mistakes.

* 🧩 **Intelligent media-type detection**
  - Automatically detects whether your backup contains anime, manga, or both, and restores accordingly.
  - Verification only checks the imported media types—no unnecessary API calls.

* 🕒 **Automatic countdown before verification**
  - After restoring, AniPort waits (with a friendly progress bar) to give AniList servers time to update.
  - Verification is only performed after countdown to ensure accuracy.

* 🔁 **Retry failed restores**
  - If any entries fail to import, AniPort saves them separately and allows you to retry in one click.
  - Multiple retries are supported until all entries are restored.

* 🛠️ **Extensible and robust**
  - Designed for future features—codebase is modular and easy to maintain.
  - Handles both old and new backup formats.
  - Easy to add new filters, formatting, and output options.

* 🏷️ **Detailed progress and stats**
  - See how many entries were exported, restored, failed, and verified, with summaries and color-coded messages.
  - All stats are shown in friendly boxed text for easy reading.

---

## 📦 Installation & Quickstart (Now Even More Step-by-Step!)

### 🟩 Android (Termux) – **Recommended for Mobile Users**

1. **Install Termux:**  
   Download [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or Google Play.

2. **Set up Termux:**

   ```sh
   pkg update
   pkg upgrade
   pkg install python git
   ```

3. **Get AniPort:**

   ```sh
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

   *(Or download as ZIP and extract with a file manager.)*

4. **Install Python requirements:**  
   **Important:** You must install all dependencies, including `rich` for optimal color support!

   ```sh
   pip install -r requirements.txt
   pip install rich
   ```

5. **Run AniPort:**

   ```sh
   python main.py
   ```

---

### 🟦 Linux (Ubuntu/Debian/Fedora/Arch...)

1. **Install Python and Git:**

   ```sh
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

2. **Clone and enter the repository:**

   ```sh
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

3. **Install dependencies (including `rich`):**

   ```sh
   pip3 install -r requirements.txt
   pip3 install rich
   ```

4. **Run AniPort:**

   ```sh
   python3 main.py
   ```

---

### 🟨 Windows

1. **Install [Python 3.x](https://www.python.org/downloads/) and [Git](https://git-scm.com/download/win)**  
   *(During Python install, check "Add Python to PATH")*

2. **Open Command Prompt or PowerShell**

3. **Get AniPort:**

   ```bat
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

4. **Install dependencies (including `rich`):**

   ```bat
   pip install -r requirements.txt
   pip install rich
   ```

5. **Run AniPort:**

   ```bat
   python main.py
   ```

---

## ▶️ Usage Guide (Comprehensive Walkthrough)

Start AniPort with:

```sh
python main.py
```

You'll see an anime-themed main menu with banners, quotes, and colorful instructions.

---

### 🗃️ Export (Backup) Your AniList — *Step-by-Step Details*

1. **Choose "Export your AniList (create a backup)" from the menu.**
   - The menu is fully boxed and colored for readability.
   - Type `-help` at any prompt for extra guidance.

2. **Enter your AniList username.**
   - The username prompt supports `-help` for instructions.
   - Only valid AniList usernames are accepted.
   - If you make a mistake, just try again.

3. **Choose if you want private entries included.**
   - If you select "No", only public entries are exported—no authentication needed!
   - If you select "Yes", follow the **OAuth authentication flow**:
     - **AniList API credentials required (Client ID & Secret):**
       - Step-by-step help messages guide you to [AniList Developer Settings](https://anilist.co/settings/developer).
       - Create a new client: Name="AniPort", Redirect URL="http://localhost".
       - Copy and paste your Client ID and Client Secret into the prompts.
     - AniPort generates an authorization URL. **Open in your browser, log in, and approve access.**
     - After approving, **copy the redirected URL from your browser’s address bar** and paste it back.
     - AniPort extracts the OAuth code and requests your token automatically.
     - Your OAuth token is securely saved locally for future use.

4. **Choose export type:**
   - Anime only, Manga only, or Both anime and manga.
   - The tool supports all combinations, with intelligent task assignment.

5. **Apply filters (optional):**
   - **Filter by status:** Choose one or more statuses by number or code (e.g., 1 3 or COMPLETED,DROPPED).
     - Status help and code mapping are always shown.
     - If no valid statuses are selected, the filter is skipped.
   - **Filter by title substring:** Enter any substring (case-insensitive) to match in titles.
     - Only entries whose title includes the substring are exported.

6. **Export process:**
   - AniPort fetches your anime/manga lists using the AniList GraphQL API.
   - All filters are applied before saving.
   - Progress bars show fetching and saving status.
   - Exports are saved in the `output/` folder as JSON files (`username_anime_backup.json`, etc.).
   - If both anime and manga are exported, a combined file is created.

7. **Summary and stats:**
   - At the end, AniPort displays how many entries were exported for each media type.
   - Time taken and export stats are shown in boxed, colored messages.

---

### 🔄 Import (Restore) a Backup — *Step-by-Step Details*

1. **Choose "Import from a backup (restore your list)" from the menu.**

2. **Select a backup JSON file:**
   - AniPort scans the `output/` folder for valid backups.
   - If only one backup is found, you can quickly confirm or enter another path.
   - If multiple backups are found, a menu lets you select one, or enter a custom path.
   - Robust error handling for invalid/missing files.

3. **Authenticate and choose the AniList account to restore to:**
   - AniPort supports multiple accounts!
   - Choose from saved accounts, add a new account, or remove accounts.
   - The interactive UI makes it easy to manage accounts and tokens.
   - If restoring private entries or using a new account, you’ll go through OAuth just like in Export.

4. **Account Verification:**
   - AniPort fetches "Viewer" info from AniList using your OAuth token.
   - The tool displays the authenticated username and ID for confirmation.
   - If the entered username does not match the token’s account, AniPort warns you and asks if you want to proceed.
   - This prevents accidental restores to the wrong account!

5. **Confirm restore:**
   - AniPort summarizes detected media types and entry count before restoring.
   - You must confirm before proceeding.

6. **Restore process:**
   - Each entry is imported using the SaveMediaListEntry mutation.
   - Progress bar shows the restore status.
   - Detailed stats (total, restored, failed, time taken) are shown at the end.

7. **Failed entries handling:**
   - Any failed restores are saved to a `.failed.json` file for easy retry.
   - AniPort prompts you to retry failed/missing entries instantly.
   - Multiple retries are supported.

8. **Verification:**
   - AniPort waits (with spinner/progress bar) before verifying entries—giving AniList time to update.
   - Verification checks only the imported media types and compares IDs.
   - Stats and messages show exactly how many entries matched.

9. **Post-verification tips:**
   - AniPort shows instructions for refreshing your AniList and making new entries visible (e.g., "Update Stats" on AniList list settings).

10. **Retry logic:**
    - If entries are still missing, AniPort saves them to a `.failed.json` again and offers further retries.

---

### ⚠️ AniList Authentication: What to Expect (Now Even More Explicit)

- **AniPort never asks for your AniList password.**  
- Private entries require OAuth authentication.
- You must create an AniList API client (one-time, free, and easy).
- Full step-by-step help at every prompt—type `-help` anytime.
- OAuth tokens are saved locally (`~/.aniport_accounts.json`) and can be deleted manually.
- AniPort always displays your authenticated username and ID before restoring, so you can avoid mistakes.

---

### Example Session (Now Annotated for Clarity)

```
Welcome to your AniList Backup & Restore Tool!
[Anime banner and quote]
Choose an option:
  1. Export your AniList (create a backup)
  2. Import from a backup (restore your list)
  3. Learn more about this tool
  4. Exit
> 1

Enter your AniList username (type '-help' for help)
> MyAnimeName

Does your AniList list include private entries?
  1. No (public only)
  2. Yes (private + public)
> 2

[Prompts for Client ID and Secret, shows OAuth URL, asks to paste redirect URL]
...

Export stats:
  Anime exported: 128
  Time taken: 4.2 sec

[Now for import...]
Choose backup file to restore:
  1. MyAnimeName_anime_backup.json
> 1

Authenticated as AniList user: MyAnimeName (ID: 12345)
Ready to restore 128 entries to account: MyAnimeName. This will add/update your AniList.
Proceed with restore? (y/N)
> y

Restoring: 100%|████████████████████████████████████| 128/128 [00:03<00:00, 40.2item/s]

Restore complete!
Stats:
  Total: 128
  Restored: 128
  Failed: 0
  Time: 3.2 sec

Waiting 20 seconds before verifying your restored AniList.
Countdown: 20...
Countdown: 19...
...
Countdown: 1...

Verifying restored entries in AniList...
Verification: 128 / 128 entries present in AniList (ANIME).
Your AniList should now match your backup!
```

---

### Tips

- **Type `-help` at any prompt for context-sensitive help.**
- **OAuth tokens are saved only on your device.** Safe, secure, and private.
- If you ever need to manage saved accounts, use the "Import" flow for account management.
- AniPort will **never overwrite or delete existing entries without your confirmation**.
- The tool is designed to be friendly, colorful, and easy to use, with anime vibes throughout!

---

**If you get stuck, read the prompt explanations, and check the [FAQ](#💡-frequently-asked-questions) for troubleshooting!**

---

## 📂 Project Structure (Expanded for Reference)

```
AniPort/
├── anilist/
│   ├── api.py         # AniList API queries/mutations, list fetching, restore logic, filtering
│   ├── auth.py        # OAuth flow, account management, token storage and selection
│   ├── formatter.py   # Filtering and formatting logic for backup/restore
│   ├── ratelimit.py   # Rate limit detection and spinner animation for waits
├── backup/
│   ├── exporter.py    # Backup/export workflow (main export logic & user prompts)
│   ├── importer.py    # Restore/import workflow (main restore logic & user prompts)
│   ├── output.py      # Output directory helpers, JSON file save/load, validation
├── ui/
│   ├── banners.py     # ASCII art banners, random anime quotes, intro/outro text
│   ├── colors.py      # Colorful boxed text, info/success/error/warning helpers
│   ├── helptext.py    # All detailed help messages for every prompt and menu
│   ├── prompts.py     # Prompt and menu logic, progress bar, confirmation, boxed text
├── output/            # Your backups are stored here! (JSON files, failed restores, etc.)
├── main.py            # Entry point – anime-themed main menu, main workflow logic
├── requirements.txt   # Python dependencies (requests, colorama, tqdm, rich)
├── LICENSE            # MIT License
└── README.md          # This very detailed documentation!
```

---

## 💡 Frequently Asked Questions

**Q: Do I need an AniList account?**  
A: Yes! Sign up at [anilist.co](https://anilist.co/).

**Q: How do I export private entries?**  
A: Choose "Yes" when prompted—AniPort will walk you through getting AniList API credentials (Client ID/Secret) and OAuth.

**Q: Where are my backups?**  
A: In the `output/` folder.

**Q: Can I use this for MAL?**  
A: No, AniPort is for AniList only.

**Q: Is this safe?**  
A: All tokens are stored locally, and AniPort never asks for your AniList password.

**Q: What if I restore to the wrong account by mistake?**  
A: AniPort will warn you if the entered username doesn't match your authenticated token account. Always check the username and ID displayed before confirming restore!

**Q: How does verification work after restore?**  
A: AniPort waits 20 seconds before checking your AniList to make sure all restored entries are present. It checks only the media types (anime/manga) present in your backup file, and uses your OAuth to access private entries as needed.

**Q: What happens if some entries fail to restore?**  
A: AniPort saves failed entries in a `.failed.json` file so you can retry them later—either immediately or in a future session.

**Q: Can I restore multiple times?**  
A: Yes! You can retry failed entries, restore new backups, or move between accounts as much as you like.

**Q: Does AniPort support both old and new backup formats?**  
A: Yes, it can handle backups as a list or as a dictionary with separate "anime" and "manga" keys.

**Q: Is this project AI-generated?**  
A: Yes, this README and parts of the code are AI-assisted.

**Q: Why do I need to install `rich`?**  
A: The `rich` library is used for colorized output and progress bars. It enhances the user interface and is required for best experience. Install it with `pip install rich`.

---

## 🛡️ Privacy & Security

- OAuth tokens are saved only on your device (`~/.aniport_accounts.json`).
- No data is sent anywhere except AniList API.
- You can delete tokens and data at any time.
- AniPort never asks for your AniList password, and never stores sensitive information except tokens for your convenience.

---

## 🤝 Contributing

- Issues and pull requests are welcome!
- Please be kind and constructive—everyone starts somewhere.
- New ideas for features, usability, or anime-themed enhancements are always welcome!

---

## 📜 License

AniPort is licensed under the [MIT License](LICENSE).

---

## 🌸 Credits & Acknowledgments

- Created by [Zilhazz Arefin](https://github.com/itzraiyan)
- ASCII art and anime quotes bring a bit of joy to your terminal!
- Thanks to all contributors and users for helping AniPort grow!

---

## 🛑 Disclaimer

> **This project contains AI-generated content. Use at your own risk, and always review code before running.**

---

**Enjoy AniPort—and may your anime adventures live on forever!**  
*“No matter how deep the night, it always turns to day, eventually.”* – Brook

---
# AniPort: AniList Backup & Restore Tool ⚙️

![AniPort Banner](https://files.catbox.moe/jx8op2.png)
---

AniPort is a beginner-friendly, interactive Python tool for **backing up and restoring your AniList anime and manga lists**. Whether you want a safe copy of your lists, plan to migrate data, or just like to keep your anime and manga adventures safe, AniPort has you covered.

---

## ✨ Features

* 🖼️ **Anime-themed terminal interface** with random ASCII art and inspirational anime quotes to keep your spirits high!
* 🗂️ **Export (backup)** your AniList lists to JSON files (public & private entries are supported)
* 🔄 **Import (restore)** backups to any AniList account, with robust verification and multi-account support
* 🔍 **Smart filtering** — Export by status or title substring
* 🔒 **Secure:** Uses AniList OAuth for private entries (never asks for your password)
* 📂 **All local:** Your data is saved in the `output/` folder, and nowhere else
* 🛡️ **Rate limit protection:** Handles AniList API gently and safely
* 🐍 **Pure Python** — Works on Android (Termux), Linux, and Windows
* 🌱 **Zero coding required:** Designed for all skill levels
* 🧑‍💻 **Account and token verification:** Ensures the correct AniList account is being used, with clear warnings if account/token don't match
* 🧩 **Intelligent media-type detection:** Only verifies and restores the correct types (anime, manga, or both) based on your backup file
* 🕒 **Automatic countdown before verification:** Gives AniList servers time to update, showing you a friendly, real-time countdown
* 🔁 **Retry failed restores:** If any entries fail to import, AniPort saves them separately and allows you to retry in one click
* 🛠️ **Extensible and robust:** Handles old and new backup formats, and future features are easy to add!
* 🏷️ **Detailed progress and stats:** See how many entries were restored, failed, and verified, with friendly summaries
* 🚫 **No duplicate imports:** AniPort automatically skips entries already present in your AniList account and shows you how many were skipped.
* 💾 **Safe cancellation:** If you cancel an import, AniPort saves any not-yet-imported entries to a separate JSON file and tells you where to find it for easy resuming.

---

![Hit Counter](https://count.getloli.com/@AniPory?name=AniPory&theme=rule34&padding=7&offset=0&align=center&scale=1&pixelated=1&darkmode=0)

---

## 📦 Installation & Quickstart (Now Even More Step-by-Step & Non-Interactive!)

### 🟩 Android (Termux) – **Recommended for Mobile Users**

1. **Install Termux:**  
   Download [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or Google Play.

2. **Set up Termux:**

   ```sh
   pkg update -y
   pkg upgrade -y
   pkg install -y python git
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
   pip install -r requirements.txt rich
   ```

5. **Run AniPort:**

   ```sh
   python main.py
   ```

---

### 🟦 Linux (Ubuntu/Debian/Fedora/Arch...)

1. **Install Python and Git:**  
   (No prompts—these commands will run without asking for confirmation.)

   ```sh
   sudo apt update -y
   sudo apt install -y python3 python3-pip git
   ```

2. **Clone and enter the repository:**

   ```sh
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

3. **Install dependencies (including `rich`):**

   ```sh
   pip3 install -r requirements.txt rich
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
   pip install -r requirements.txt rich
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

## ▶️ Example Session

Below is a corrected example session showing a full backup and restore flow. All prompts, responses, and output reflect the actual user experience in the terminal:

```
Welcome to your AniList Backup & Restore Tool!

▄▀█ █▄░█ █ █▀█ █▀█ █▀█ ▀█▀
█▀█ █░▀█ █ █▀▀ █▄█ █▀▄ ░█░

“The world isn’t perfect. But it’s there for us, doing the best it can. That’s what makes it so damn beautiful.” – Roy Mustang

What would you like to do?
  1. Export your AniList (create a backup)
  2. Import from a backup (restore your list)
  3. Learn more about this tool
  4. Exit
(Type the number or -help for info)
> 1

You have chosen to EXPORT (backup) your AniList!

Enter your AniList username (type '-help' for help)
> MyAnimeName

Does your AniList list include private entries?
  1. No (public only)
  2. Yes (private + public)
> 2

You will need AniList API credentials. Follow the prompts!
Enter your AniList API Client ID (type '-help' for help):
> [client_id_here]
Enter your AniList API Client Secret (type '-help' for help):
> [client_secret_here]

To authenticate, you'll need to open a link, approve access, and copy a code.
Step 1: Copy the URL below and open it in your browser. Log in and approve access.

https://anilist.co/api/v2/oauth/authorize?client_id=...&response_type=code&redirect_uri=http%3A%2F%2Flocalhost

Step 2: After approving, AniList will redirect (or fail to connect to localhost, that's OK!).
Copy the full URL from your browser's address bar (it will contain '?code=...'), and paste it below.

Paste the entire redirected URL here:
> [redirected_url_with_code]

What would you like to export?
  1. Anime only
  2. Manga only
  3. Both anime and manga
> 1

Would you like to filter by status? (y/N)
> N

Would you like to filter by title substring? (y/N)
> N

Fetching anime list from AniList...

Export complete! Your backup(s) are in the output/ folder.
Export stats:
  Anime exported: 128
  Time taken: 4.2 sec

Thanks for using the AniList Backup Tool! 🌸
Keep your anime dreams safe and keep exploring new worlds!

“No matter how deep the night, it always turns to day, eventually.” – Brook
```

Now, let's restore from the backup:

```
Welcome to your AniList Backup & Restore Tool!

What would you like to do?
  1. Export your AniList (create a backup)
  2. Import from a backup (restore your list)
  3. Learn more about this tool
  4. Exit
> 2

You have chosen to IMPORT (restore) a backup!

Found one backup: MyAnimeName_anime_backup.json in 'output/'.
Use this file? (Y/n)
> Y

Select which AniList account to restore to.
Choose an AniList account for this operation:
  1. Use saved account: MyAnimeName
  2. Add a different AniList account
  3. Remove a saved account
> 1

Authenticated as AniList user: MyAnimeName (ID: 12345)

Detected entry types in backup: ANIME
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

Verifying restored entries in AniList...
⠋ [████████████████████████████] 100%

Verification complete!
Verification: 128 / 128 imported entries present in AniList (ANIME).
Note:
If you do not immediately see all your imported entries on AniList, don't worry!
AniList sometimes requires a manual refresh for new entries to appear in your list.
To update your list:
  1. Go to your AniList list settings page:
     https://anilist.co/settings/list
  2. Click on “Update Stats” and then “Unhide Entries.”
This will refresh your lists and make all imported entries visible.
You can also try refreshing your browser after doing this.

Verification PASSED: All imported entries are present in your AniList!
Your AniList should now match your backup!
```

---

**This session demonstrates a typical user flow for both backup and restore, including authentication, file selection, and verification. All prompts and messages are true to the actual AniPort experience.**

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
│
├── anilist/                 # AniList API logic (all interaction with AniList itself)
│   ├── api.py               # Handles GraphQL queries/mutations: fetch lists, restore entries, user info
│   ├── auth.py              # Manages AniList OAuth authentication, account/token storage and selection
│   ├── formatter.py         # Filters and formats entries for backup/restore (by status, title, etc.)
│   ├── ratelimit.py         # Detects and manages AniList API rate limits, with wait spinner
│
├── backup/                  # Backup and restore workflow logic
│   ├── exporter.py          # Main export (backup) workflow: prompts, applies filters, saves to JSON
│   ├── importer.py          # Main import (restore) workflow: prompts, imports entries, handles retries/verification
│   ├── output.py            # Handles output/ directory, saving/loading/validating backup JSON files
│
├── ui/                      # User interface components (terminal UX)
│   ├── banners.py           # Prints ASCII art banners, random anime quotes, intro/outro
│   ├── colors.py            # Functions for colored, boxed terminal output and printing info/warning/error
│   ├── helptext.py          # Contains all long help messages for various prompts/menus
│   ├── prompts.py           # All user prompts, menus, confirmation dialogs, progress bars
│   ├── motd.py              # NEW: Admin message system — shows a message from motd.txt if changed
│
├── output/                  # (Directory) Stores user backups and failed/leftout restore files (created at runtime)
│
├── main.py                  # Program entry point. Shows main menu, routes to export/import/info, prints banners/quotes
├── motd.txt                 # NEW: Admin message file — update/commit this to show users a one-time message
├── requirements.txt         # Lists all Python dependencies needed to run AniPort
├── LICENSE                  # MIT License for AniPort
└── README.md                # Main documentation, usage guide, and project structure
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

**Enjoy AniPort—and may your anime adventures live on forever!**  
*“No matter how deep the night, it always turns to day, eventually.”* – Brook

---

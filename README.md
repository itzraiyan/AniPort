# AniPort: AniList Backup & Restore Tool ⚙️

![AniPort Banner](https://files.catbox.moe/jx8op2.png)

> **Note:** This project contains AI-generated content. While much of the code and documentation is crafted with the help of AI tools, the overall design and intent are shaped by the project owner.

---

AniPort is a beginner-friendly, interactive Python tool for **backing up and restoring your AniList anime and manga lists**. Whether you want a safe copy of your lists, plan to migrate data, or just like to keep your collection secure, AniPort is designed to make the process smooth and enjoyable for everyone—even first-time users!

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

---

## 📦 Installation & Quickstart

### 🟩 Android (Termux) – **Recommended**

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

   ```sh
   pip install -r requirements.txt
   ```

5. **Run AniPort:**

   ```sh
   python main.py
   ```

---

### 🟦 Linux (Ubuntu/Debian/Fedora/Arch...)

```sh
sudo apt update
sudo apt install python3 python3-pip git
git clone https://github.com/itzraiyan/AniPort.git
cd AniPort
pip3 install -r requirements.txt
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

4. **Install dependencies:**

   ```bat
   pip install -r requirements.txt
   ```

5. **Run AniPort:**

   ```bat
   python main.py
   ```

---

## ▶️ Usage Guide

Start AniPort with:

```sh
python main.py
```

You'll see an anime-themed main menu. Here's what happens next:

---

### 🗃️ Export (Backup) Your AniList

1. **Choose "Export your AniList (create a backup)" from the menu.**
2. **Enter your AniList username.**
   - Type `-help` at any prompt for a helpful explanation!
3. **Choose if you want private entries included.**
   - **If you select "Yes" (private + public):**
     - You'll be guided through the AniList OAuth authentication flow.
     - **You'll need your AniList API Client ID and Client Secret.**
       - If you don't have these, follow the detailed instructions shown in the prompt and help message:
         - Go to [AniList Developer Settings](https://anilist.co/settings/developer)
         - Create a new client: Name="AniPort", Redirect URL="http://localhost"
         - Copy your Client ID and Client Secret.
       - Paste these into the tool when prompted.
     - You'll be given an authorization URL. **Open it in your browser, log in, and approve access.**
     - **After approving, copy the full URL from your browser's address bar** and paste it back into the tool.
     - The tool will extract the code and finish authentication for you.
     - Your OAuth token is securely saved locally for future use.
4. **Choose export type:** Anime, Manga, or Both.
5. **Apply filters (optional):** Filter by status (e.g., Completed, Watching) or by title substring.
6. **Your backup(s) will be saved in the `output/` folder.**
   - The exported JSON will clearly indicate which entries are anime, manga, or both.
   - All exported data is structured for easy future restore and verification.
7. **Stats and summary will appear at the end.**
   - See how many entries were exported, how long the process took, and if any filters were applied.

---

### 🔄 Import (Restore) a Backup

1. **Choose "Import from a backup (restore your list)" from the menu.**
2. **Select a backup JSON file.**
   - If there are backups in `output/`, you'll be shown a menu to select one.
   - Or, enter the path to your backup file.
3. **Authenticate and choose the AniList account to restore to.**
   - AniPort supports multiple accounts! You'll see a menu:
     - Use a saved account (if you authenticated before)
     - Add a new AniList account (go through OAuth again, same as above)
     - Remove a saved account
   - If you are restoring private entries or using a new account, you’ll go through the OAuth flow just like in Export.
4. **Account Verification:**
   - AniPort uses the OAuth token to fetch the "Viewer" info from AniList, confirming the actual account (username and ID).
   - If you entered a username that doesn't match the token's account, AniPort will **warn you** and ask if you want to continue.
   - This ensures maximum safety and prevents accidental restores to the wrong account.
5. **Confirm restore – AniPort will show a summary before proceeding.**
   - All detected media types (anime, manga, or both) are displayed, so you know exactly what's being restored.
6. **Progress bar will show as entries are restored.**
   - You'll see detailed feedback for each entry.
7. **Stats and summary will appear at the end.**
   - If any entries fail to restore, a `.failed.json` backup is created for retrying later.
8. **Verification with Countdown:**
   - AniPort waits for 20 seconds before verifying that your entries were restored, showing a friendly countdown ("Countdown: 20...", "Countdown: 19...", etc.).
   - This gives AniList's servers time to update and ensures more accurate verification.
9. **Verification checks only the correct media type(s).**
   - If your backup contains only manga, only your manga list is checked. If it contains both, both are checked.
   - Verification is done using your OAuth token, so even private entries are accurately checked.
10. **Retrying Failed Entries:**
    - If some entries fail, AniPort saves them in a `.failed.json` and allows you to retry immediately.
    - You can do multiple retries until all entries are restored.

---

### ⚠️ AniList Authentication: What to Expect

- **You do NOT need to give your AniList password to this tool.**  
- Private entries require OAuth authentication.
- You must create an AniList API client (one-time, free, easy).
- Follow the prompts – type `-help` if you are stuck.
- OAuth tokens are stored locally in `.aniport_accounts.json` and can be deleted at any time.
- AniPort will **always show you the authenticated username and ID before restoring** to help you avoid mistakes.

---

### Example Session (Export & Import)

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

## 📂 Project Structure

```
AniPort/
├── anilist/
│   ├── api.py         # AniList API queries and mutations, account verification
│   ├── auth.py        # OAuth, account management
│   ├── formatter.py   # Formatting and filtering
│   ├── ratelimit.py   # Rate limit handling
├── backup/
│   ├── exporter.py    # Backup/export workflow (called by main.py)
│   ├── importer.py    # Restore/import workflow (called by main.py)
│   ├── output.py      # File handling
├── ui/
│   ├── banners.py     # ASCII art, quotes, intro/outro
│   ├── colors.py      # Colorful, boxed text
│   ├── helptext.py    # All help messages
│   ├── prompts.py     # All user prompts/menus
├── output/            # Your backups are stored here!
├── main.py            # Entry point – always start here!
├── requirements.txt   # Python dependencies
├── LICENSE
└── README.md
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
A: AniPort waits 20 seconds before checking your AniList to make sure all restored entries are present. It checks only the media types (anime/manga) present in your backup file, and uses your OAuth token to confirm even private entries.

**Q: What happens if some entries fail to restore?**  
A: AniPort saves failed entries in a `.failed.json` file so you can retry them later—either immediately or in a future session.

**Q: Can I restore multiple times?**  
A: Yes! You can retry failed entries, restore new backups, or move between accounts as much as you like.

**Q: Does AniPort support both old and new backup formats?**  
A: Yes, it can handle backups as a list or as a dictionary with separate "anime" and "manga" keys.

**Q: Is this project AI-generated?**  
A: Yes, this README and parts of the code are AI-assisted.

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
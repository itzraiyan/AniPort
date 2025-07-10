# AniPort: AniList Backup & Restore Tool ⚙️

![AniPort Banner](https://files.catbox.moe/jx8op2.png)

> **Note:** This project contains AI-generated content. While much of the code and documentation is crafted with the help of AI tools, the overall design and intent are shaped by the project owner.

---

AniPort is a beginner-friendly, interactive Python tool for **backing up and restoring your AniList anime and manga lists**. Whether you want a safe copy of your lists, plan to migrate data, or just love the idea of keeping your collection safe with a sprinkle of anime vibes, AniPort is for you!

---

## ✨ Features

* 🖼️ **Anime-themed terminal interface** with random ASCII art and quotes
* 🗂️ **Export (backup)** your AniList lists to JSON files (public & private entries)
* 🔄 **Import (restore)** backups to any AniList account (multi-account support)
* 🔍 **Smart filtering** — Export by status or title substring
* 🔒 **Secure:** Uses AniList OAuth for private entries (never asks for your password)
* 📂 **All local:** Your data is saved in the `output/` folder, and nowhere else
* 🛡️ **Rate limit protection:** Handles AniList API gently
* 🐍 **Pure Python** — Works on Android (Termux), Linux, and Windows
* 🌱 **Zero coding required:** Designed for all skill levels

---

## 📦 Installation

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

5. **You're ready!**

---

### 🟦 Linux (Ubuntu/Debian/Fedora/Arch...)

```sh
sudo apt update
sudo apt install python3 python3-pip git
git clone https://github.com/itzraiyan/AniPort.git
cd AniPort
pip3 install -r requirements.txt
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

---

## ▶️ Usage Guide

### 🗃️ Export (Backup) Your AniList

```sh
python backup/exporter.py
```

- **On Termux:** `python backup/exporter.py`
- **On Linux:** `python3 backup/exporter.py`
- **On Windows:** `python backup/exporter.py`

**What happens next?**
- Enter your AniList username (type `-help` for help at any prompt).
- Choose if you want to include private entries (will walk you through AniList OAuth if needed).
- Choose to export anime, manga, or both.
- Optionally filter by status (e.g. Completed, Watching) or by title.
- Your backup JSON will be saved in the `output/` directory!

---

### 🔄 Import (Restore) a Backup

```sh
python backup/importer.py
```

- Select a backup JSON from `output/` or specify a path.
- Authenticate with AniList (OAuth flow, safe and private).
- Choose which account to restore to.
- Progress bar will show as entries are restored.
- Summary is shown at the end.

---

## 📂 Project Structure

```
AniPort/
├── anilist/
│   ├── api.py         # AniList API queries and mutations
│   ├── auth.py        # OAuth, account management
│   ├── formatter.py   # Formatting and filtering
│   ├── ratelimit.py   # Rate limit handling
├── backup/
│   ├── exporter.py    # Backup/export workflow
│   ├── importer.py    # Restore/import workflow
│   ├── output.py      # File handling
├── ui/
│   ├── banners.py     # ASCII art, quotes, intro/outro
│   ├── colors.py      # Colorful, boxed text
│   ├── helptext.py    # All help messages
│   ├── prompts.py     # All user prompts/menus
├── output/            # Your backups are stored here!
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

**Q: I got an error!**  
A: Read the error message and try again. For help, open an [issue](https://github.com/itzraiyan/AniPort/issues) and include the error.

**Q: Is this project AI-generated?**  
A: Yes, this README and parts of the code are AI-assisted.

---

## 🛡️ Privacy & Security

- OAuth tokens are saved only on your device (`~/.aniport_accounts.json`).
- No data is sent anywhere except AniList API.
- You can delete tokens and data at any time.

---

## 🤝 Contributing

- Issues and pull requests are welcome!
- Please be kind and constructive—everyone starts somewhere.

---

## 📜 License

AniPort is licensed under the [MIT License](LICENSE).

---

## 🌸 Credits & Acknowledgments

- Created by [Zilhazz Arefin](https://github.com/itzraiyan)
- ASCII art and anime quotes bring a bit of joy to your terminal!

---

## 🛑 Disclaimer

> **This project contains AI-generated content. Use at your own risk, and always review code before running.**

---

**Enjoy AniPort—and may your anime adventures live on forever!**  
*“No matter how deep the night, it always turns to day, eventually.”* – Brook

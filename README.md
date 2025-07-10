# AniPort - AniList Backup & Restore ✨

AniPort is a terminal/CLI tool to **backup and restore your AniList anime and manga lists** — with full support for public/private entries, a colorful anime-themed interface, and smooth cross-platform setup.  
> **Note:** This project is partially AI-generated 🤖 — both the codebase and documentation were created and refined using AI tools to accelerate development and ensure clarity.

---

## 🌸 Project Structure

```
AniPort/
├── main.py              # Entry point (banner, menu, workflow routing)
├── ui/
│   ├── banners.py       # ASCII art, intro/outro, anime quotes
│   ├── colors.py        # Color/box helpers
│   ├── prompts.py       # Decorated/boxed input, menus, progress bar
│   └── helptext.py      # All help/instructions
├── anilist/
│   ├── api.py           # All AniList API queries/mutations
│   ├── auth.py          # OAuth logic
│   ├── ratelimit.py     # API rate limit handler
│   └── formatter.py     # Data filtering/formatting
├── backup/
│   ├── exporter.py      # Export workflow (prompt, fetch, save)
│   ├── importer.py      # Import/restore workflow (prompt, load, restore)
│   └── output.py        # Output/dir management, file/JSON helpers
├── output/              # All exported JSONs appear here
├── requirements.txt     # Python dependencies
├── LICENSE
└── README.md
```

---

## ✨ Features

- **Export (backup) your AniList anime/manga lists as JSON files**  
  📦 Supports public/private entries (OAuth for private)  
  🔎 Filter by status (e.g., Completed, Watching) or by title substring  
  💾 Output is a portable JSON in the `output/` directory

- **Restore (import) your backup to the same or a different AniList account**  
  🔐 Full restore with OAuth authentication  
  ⏳ Handles AniList rate limiting gracefully

- **Fully terminal/Termux/TTY-friendly**  
  🎨 Anime-style banners, colored boxes, and `-help` at every prompt

- **No MAL support — 100% AniList-focused!**

- **Cross-platform:** Works on Android (via Termux), Linux, and Windows 🪟🐧📱

---

## ⚡ Installation & Setup

### Requirements

- Python 3.7+
- `pip` (Python package manager)
- The following Python packages (auto-installed by `pip install -r requirements.txt`):
  - `requests`
  - `colorama`
  - `tqdm`

---

### 📱 Termux (Android)

1. **Install Termux:**  
   [Google Play](https://play.google.com/store/apps/details?id=com.termux) or [F-Droid](https://f-droid.org/packages/com.termux/)

2. **Update Termux packages:**
   ```sh
   pkg update && pkg upgrade
   ```

3. **Install Python and git:**
   ```sh
   pkg install python git
   ```

4. **Clone the AniPort repository:**
   ```sh
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

5. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

6. **Run AniPort:**
   ```sh
   python main.py
   ```
   > *(Replace `main.py` with your entry point if different.)*

---

### 🐧 Linux

1. **Open a terminal.**

2. **Install Python and git (Debian/Ubuntu example):**
   ```sh
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

3. **Clone the AniPort repository:**
   ```sh
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

4. **Install Python dependencies:**
   ```sh
   pip3 install -r requirements.txt
   ```

5. **Run AniPort:**
   ```sh
   python3 main.py
   ```

---

### 🪟 Windows

1. **Install [Git for Windows](https://git-scm.com/download/win)** and [Python 3.x](https://www.python.org/downloads/). Ensure Python is added to your PATH.

2. **Open Command Prompt or PowerShell.**

3. **Clone the AniPort repository:**
   ```sh
   git clone https://github.com/itzraiyan/AniPort.git
   cd AniPort
   ```

4. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Run AniPort:**
   ```sh
   python main.py
   ```

---

## 🎮 Usage

Follow the on-screen prompts!  
Type `-help` at any prompt for extra details or troubleshooting.

- **Export:** Backup your anime/manga lists (JSON saved to `output/`)
- **Import:** Restore a backup to any AniList account (OAuth required)
- **All features are accessible via the main menu**

---

## 🤝 Contribution

Contributions and feedback are welcome!  
Feel free to open issues or pull requests to improve AniPort.

---

## 📄 License

MIT License  
See [LICENSE](LICENSE) for details.

---

*Created by Zilhazz Arefin. Portions of this project and documentation were AI-generated for speed and clarity.* 🌸✨
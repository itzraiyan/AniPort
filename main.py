#!/usr/bin/env python3
"""
AniList Backup Tool - Main CLI Entrypoint

Handles session start, banner and intro, main menu, and routes to export/import/info flows.
All UX is decorated and anime-themed, as per the project style guide.

Author: AniXWeebs
"""

import sys
import os

# ===== Import UI/Helpers =====
from ui.banners import print_banner, print_outro, print_random_quote
from ui.prompts import menu_boxed, print_info, print_success, print_error, prompt_boxed
from ui.helptext import TOOL_OVERVIEW, MAIN_MENU_HELP

# ===== Import Workflow Modules =====
from backup.exporter import export_workflow
from backup.importer import import_workflow

# ===== Ensure output dir exists =====
from backup.output import ensure_output_dir

def main():
    ensure_output_dir()
    print_banner()
    print_info("Welcome to your AniList Backup & Restore Tool!\n")
    print_random_quote()

    while True:
        # Main menu
        choice = menu_boxed(
            "What would you like to do?",
            [
                "Export your AniList (create a backup)",
                "Import from a backup (restore your list)",
                "Learn more about this tool",
                "Exit"
            ],
            helpmsg=MAIN_MENU_HELP
        )

        if choice == 1:  # Export
            # Export workflow (with pre-confirmation)
            print_info("You have chosen to EXPORT (backup) your AniList!")
            export_workflow()
            print_outro()
            break

        elif choice == 2:  # Import/Restore
            print_info("You have chosen to IMPORT (restore) a backup!")
            import_workflow()
            print_outro()
            break

        elif choice == 3:  # Learn more
            print_info(TOOL_OVERVIEW)
            input("\nPress Enter to return to the main menu...")

        elif choice == 4:  # Exit
            print_success("Thanks for using AniList Backup Tool! See you next time, senpai!")
            print_outro()
            sys.exit(0)

        else:
            print_error("Invalid selection. Please choose a valid option.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nInterrupted. Goodbye! 🐾")
        sys.exit(0)
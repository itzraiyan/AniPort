import sys
from ui.colors import boxed_text, print_info, print_error, print_warning, color_text

def prompt_boxed(msg, default=None, color="MAGENTA", width=60, helpmsg=None):
    while True:
        prompt_str = f"{msg}" + (f" [{default}]" if default else "")
        print(boxed_text(prompt_str, color, width))
        val = input("> ").strip()
        if val.lower() == "-help" and helpmsg:
            print_info(helpmsg, width)
            continue
        if not val and default is not None:
            return default
        if val:
            return val

def menu_boxed(title, options, helpmsg=None, width=60):
    """
    Presents a boxed menu and returns the 1-based index of selected option.
    """
    menu = f"{title}\n"
    for i, opt in enumerate(options, 1):
        menu += f"  {i}. {opt}\n"
    menu += "(Type the number or -help for info)"
    while True:
        print(boxed_text(menu, "CYAN", width))
        val = input("> ").strip()
        if val.lower() == "-help" and helpmsg:
            print_info(helpmsg, width)
            continue
        if val.isdigit() and 1 <= int(val) <= len(options):
            return int(val)
        print_warning("Please enter a valid number.")

def confirm_boxed(msg, color="YELLOW", width=60):
    # Only show (y/N) once!
    print(boxed_text(msg + " (y/N)", color, width))
    ans = input("> ").strip().lower()
    return ans == 'y'

def print_progress_bar(iterable, desc):
    try:
        from tqdm import tqdm
        return tqdm(iterable, desc=desc, unit="item")
    except ImportError:
        # Fallback: just return the iterable, no progress bar
        return iterable

# For quick info/error/success, re-export from colors
print_info = print_info
print_error = print_error
print_success = lambda msg, width=60: print(boxed_text(msg, "GREEN", width))
print_warning = print_warning

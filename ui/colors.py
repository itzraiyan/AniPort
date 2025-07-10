import sys

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    # Fallback if colorama not installed (no color)
    class ForeDummy:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = RESET = ""
    class StyleDummy:
        RESET_ALL = ""
    Fore = ForeDummy()
    Style = StyleDummy()

def color_text(text, color):
    return getattr(Fore, color.upper(), "") + text + Style.RESET_ALL

def boxed_text(text, color="WHITE", width=60):
    import textwrap
    lines = []
    for paragraph in text.split('\n'):
        lines.extend(textwrap.wrap(paragraph, width=width) or [''])
    if not lines:
        lines = ['']
    maxlen = max(len(line) for line in lines)
    top = '┌' + '─' * (maxlen + 2) + '┐'
    bot = '└' + '─' * (maxlen + 2) + '┘'
    mid = [f"│ {line.ljust(maxlen)} │" for line in lines]
    box = [top] + mid + [bot]
    return color_text('\n'.join(box), color)

def print_info(msg, width=60):
    print(boxed_text(msg, "CYAN", width))

def print_success(msg, width=60):
    print(boxed_text(msg, "GREEN", width))

def print_error(msg, width=60):
    print(boxed_text("Error: " + msg, "RED", width))

def print_warning(msg, width=60):
    print(boxed_text("Warning: " + msg, "YELLOW", width))

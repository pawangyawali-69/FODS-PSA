import os
import sys
import time
import threading
import getpass
import hashlib
import re

MIN_PASSWORD_LENGTH = 8

BOLD = "\033[1m"
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

W = 58

def logout_sequence():
    """Display an aesthetic logout sequence."""
    clear_screen()
    box("TERMINATING SESSION", color=RED)
    
    stages = [
        ("Saving session data...", 0.4),
        ("Closing database connections...", 0.3),
        ("Clearing secure cache...", 0.4),
        ("Revoking authentication tokens...", 0.3),
        ("Finalizing system logs...", 0.2),
        ("Logging out user...", 0.5)
    ]
    
    for i, (stage, delay) in enumerate(stages, start=1):
        print(f"[{i}/{len(stages)}] {stage}", end="", flush=True)
        time.sleep(delay)
        print(" DONE")
    
    time.sleep(0.3)
    clear_screen()

def render_goodbye():
    """Render a clean and professional goodbye message."""
    clear_screen()
    section_separator()
    box("THANK YOU FOR USING OUR SYSTEM !!", color=YELLOW)
    section_separator()


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def colorize(text, color):
    """Wrap text with the specified ANSI color code."""
    return f"{color}{text}{RESET}"

def error(text):
    """Format a string as an error message in red."""
    return colorize(f"ERROR: {text}", RED)

def success(text):
    """Format a string as a success message in green."""
    return colorize(f"SUCCESS: {text}", GREEN)

def warning(text):
    """Format a string as a warning message in yellow."""
    return colorize(f"WARNING: {text}", YELLOW)


def hr(n=W):
    """Return a horizontal rule string of length n."""
    return "+" + "-" * n + "+"

def section_separator():
    """Print exactly one blank line as a visual separator between UI sections."""
    print()

def box(title, w=W, color=CYAN):
    """Print a boxed title header."""
    print(f"{color}{BOLD}{hr(w)}")
    print(f"|{title.center(w)}|")
    print(f"{hr(w)}{RESET}")

def render_user_info(user, w=W):
    """Render the current user context bar as a standalone boxed block."""
    context = f" Current User: {user.name} | Role: {user.role} | ID: {user.id} "
    print(f"{MAGENTA}{BOLD}{hr(w)}")
    print(f"|{context.center(w)}|")
    print(f"{hr(w)}{RESET}")

def render_page_header(title, w=W, color=CYAN):
    """Render the page title as a standalone boxed block."""
    print(f"{color}{BOLD}{hr(w)}")
    print(f"|{title.center(w)}|")
    print(f"{hr(w)}{RESET}")

def print_banner():
    """Print the system's aesthetic banner."""
    title = "STUDENT MANAGEMENT SYSTEM"
    print(f"{BLUE}{BOLD}{hr(W)}")
    print(f"|{title.center(W)}|")
    print(f"{hr(W)}{RESET}")



def boot_system():
    """Display a simulated system boot sequence."""
    clear_screen()
    box("STUDENT PROFILE MANAGEMENT SYSTEM", color=BLUE)
    
    stages = [
        ("Initializing hardware check...", 0.3),
        ("Loading kernel modules...", 0.3),
        ("Verifying memory allocation...", 0.2),
        ("Checking file system integrity...", 0.3),
        ("Loading authentication handlers...", 0.2),
        ("Initializing session manager...", 0.2),
        ("Loading database drivers...", 0.3),
        ("Configuring security protocols...", 0.2),
        ("Starting UI components...", 0.2),
        ("System initialization complete!", 0.1)
    ]
    
    for i, (stage, delay) in enumerate(stages, start=1):
        print("[" + str(i) + "/" + str(len(stages)) + "] " + stage, end="", flush=True)
        time.sleep(delay)
        print(" OK")
    
    box("SYSTEM READY OK", color=GREEN)
    print("\a" * 3)
    time.sleep(0.5)





def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC with a random salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return salt.hex() + ':' + key.hex()

def verify_password(password: str, stored: str) -> bool:
    """
    Verify a password against stored hash.
    Supports both old (SHA-256) and new (PBKDF2) formats.
    """
    if ':' in stored:
        try:
            salt_hex, key_hex = stored.split(':')
            salt = bytes.fromhex(salt_hex)
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            if key.hex() == key_hex:
                return True
        except (ValueError, TypeError):
            pass
    
    legacy_hash = hashlib.sha256(password.encode()).hexdigest()
    return legacy_hash == stored

def validate_username(username):
    """Validate that a username matches formatting rules."""
    if not username:
        return False, "Username cannot be empty"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_password(password):
    """Validate that a password meets complexity rules."""
    if not password:
        return False, "Password cannot be empty"
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    return True, ""

def validate_email(email):
    """Validate that an email address has a valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_password(prompt="Password: "):
    """Securely prompt the user for a password input with asterisk masking."""
    import sys
    if os.name == 'nt':
        import msvcrt
        print(prompt, end='', flush=True)
        password = ""
        while True:
            ch = msvcrt.getch()
            if ch in {b'\x00', b'\xe0'}:
                msvcrt.getch()
                continue
            if ch in {b'\r', b'\n'}:
                print()
                break
            elif ch == b'\x08': 
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif ch == b'\x03':
                raise KeyboardInterrupt
            else:
                try:
                    char = ch.decode('utf-8')
                    if char.isprintable():
                        password += char
                        sys.stdout.write('*')
                        sys.stdout.flush()
                except UnicodeDecodeError:
                    pass
        return password
    else:
        return getpass.getpass(prompt)

def print_menu(title, options, user=None):
    """Print an interactive menu with a user info bar, page header, and options.

    Layout spacing rule (enforced globally):
        User info block  →  (1 blank line)  →  Page header  →  (1 blank line)  →  Menu
    """
    clear_screen()
    if user:
        render_user_info(user)
        section_separator()
    render_page_header(title)
    section_separator()
    for key, value in options.items():
        print("| " + f"{key}. {value}".ljust(W - 2) + "|")
    print(hr(W))
    print(f"{YELLOW}Enter choice: {RESET}", end="")

def get_menu_choice(options):
    """Fetch user input ensuring choice lies within the given options dictionary."""
    while True:
        choice = input().strip()
        if choice in options:
            return choice
        print(error("\nInvalid choice. Try again: "), end="")

def pause():
    """Halt process execution until the user submits a localized enter prompt."""
    input("\n" + YELLOW + "Press Enter to continue..." + RESET)
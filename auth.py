import os
import time
from datetime import datetime

from database import db
from ui import (error, success, warning, 
                hash_password, verify_password, validate_username, 
                validate_password, get_password, W, BOLD, BLUE, 
                GREEN, RED, YELLOW, RESET, MAGENTA, clear_screen, CYAN,
                box, render_page_header, section_separator, hr)

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 60

class Auth:
    """Handles authentication, security lockouts, and setup workflows."""

    def __init__(self):
        """Initialize the Auth instance with empty tracking dictionaries."""
        self._attempts = {}
        self._locked_users = {}
    
    def is_locked(self, username):
        """Check if a given username is temporarily locked out."""
        if username in self._locked_users:
            if time.time() - self._locked_users[username] < LOCKOUT_DURATION:
                remaining = int(LOCKOUT_DURATION - (time.time() - self._locked_users[username]))
                if remaining > 0:
                    print(f"\n{error('Account locked. Try again in ' + str(remaining) + ' seconds.')}")
                    return True
            del self._locked_users[username]
        return False
    
    def lock_user(self, username):
        """Apply a temporary lock to the given username."""
        self._locked_users[username] = time.time()
    
    def increment_attempts(self, username):
        """Increment failed login attempts and lock the account if needed."""
        self._attempts[username] = self._attempts.get(username, 0) + 1
        if self._attempts[username] >= MAX_LOGIN_ATTEMPTS:
            self.lock_user(username)
            db.log_action(username, "ACCOUNT_LOCKED", "Too many failed attempts")
            return True
        return False
    
    def reset_attempts(self, username):
        """Reset failed login attempts for a username."""
        self._attempts[username] = 0
    
    def login(self, username, password):
        """Authenticate a user by verifying their password and return their user record."""
        if self.is_locked(username):
            return None
        
        if not db.user_exists(username):
            self.increment_attempts(username)
            db.log_action(username, "LOGIN_FAILED", "User not found")
            return None
        
        stored_hash = db.get_password(username)
        if not stored_hash:
            self.increment_attempts(username)
            db.log_action(username, "LOGIN_FAILED", "No password set")
            return None
        
        if verify_password(password, stored_hash):
            self.reset_attempts(username)
            user = db.get_user_by_username(username)
            if user:
                db.log_action(username, "LOGIN_SUCCESS", f"Role: {user['role']}")
            return user
        else:
            self.increment_attempts(username)
            db.log_action(username, "LOGIN_FAILED", "Invalid password")
            return None
    
    def change_password(self, username, old_password, new_password):
        """Change a user's password if the old password is verified successfully."""
        stored_hash = db.get_password(username)
        if not stored_hash:
            return False
        
        if verify_password(old_password, stored_hash):
            new_hash = hash_password(new_password)
            db.set_password(username, new_hash)
            db.log_action(username, "PASSWORD_CHANGED", "")
            return True
        return False
    
    def first_time_setup(self):
        """Perform the initial system setup and first-admin configuration."""
        from ui import clear_screen
        
        render_page_header("SYSTEM INITIALIZATION", color=MAGENTA)
        section_separator()
        
        print(f"{YELLOW}--- STATUS ---{RESET}")
        print(warning("No users found. Entering setup mode..."))
        print(hr(W))
        print("\a")
        time.sleep(2)
        clear_screen()
        
        render_page_header("DEFAULT ADMIN ACCESS", color=MAGENTA)
        section_separator()
        print("Username: admin")
        print("Password: admin")
        print(f"\n{RED}WARNING: This is a temporary account.{RESET}")
        print(f"{YELLOW}You MUST change credentials to continue.{RESET}")
        print(hr(W))
        
        attempts = 0
        max_attempts = 3
        default_hash = hash_password("admin")
        
        while attempts < max_attempts:
            print(f"\n{CYAN}Login attempt {attempts + 1}/{max_attempts}{RESET}")
            username = input("Username: ").strip()
            password = get_password("Password: ").strip()
            
            if username == "admin" and verify_password(password, default_hash):
                print(f"\n{success('Default credentials accepted!')}")
                print("\a\a")
                time.sleep(1)
                clear_screen()
                break
            else:
                attempts += 1
                print(f"{error('Invalid credentials')}")
                print("\a")
                if attempts >= max_attempts:
                    print(f"\n{error('Maximum attempts exceeded. Exiting...')}")
                    print("\a")
                    import sys
                    sys.exit()
        
        if not self.force_credential_change():
            import sys
            sys.exit()
    
    def force_credential_change(self):
        """Force the user to designate new admin credentials when logging in with defaults."""
        from ui import clear_screen
        
        render_page_header("SECURITY SETUP REQUIRED", color=MAGENTA)
        section_separator()
        print(f"{YELLOW}Default credentials detected.{RESET}")
        print(f"{RED}You must create new credentials.{RESET}")
        print(hr(W))
        
        while True:
            new_username = input("New Username: ").strip()
            
            if new_username.lower() == "admin":
                print(f"{error('Username cannot be admin')}")
                print("\a")
                continue
            
            valid, msg = validate_username(new_username)
            if not valid:
                print(f"{error(msg)}")
                print("\a")
                continue
            break
            
        while True:
            new_password = get_password("New Password: ").strip()
            
            if len(new_password) < 8:
                print(f"{error('Password must be at least 8 characters')}")
                print("\a")
                continue
            
            valid, msg = validate_password(new_password)
            if not valid:
                print(f"{error(msg)}")
                print("\a")
                continue
            
            confirm = get_password("Confirm Password: ").strip()
            if new_password != confirm:
                print(f"{error('Passwords do not match')}")
                print("\a")
                continue
            break
        
        self.save_new_admin(new_username, new_password)
        
        render_page_header("SETUP COMPLETE", color=GREEN)
        section_separator()
        print(f"{success('System initialized successfully.')}")
        print(f"{success('Default credentials removed.')}")
        print(hr(W))
        print("\a\a")
        
        time.sleep(1.5)
        clear_screen()
        return True
    
    def save_new_admin(self, username, password):
        """Save the new admin details and initializing credentials into the database."""
        hashed_pw = hash_password(password)
        
        db.add_user(
            "1", username, "Admin",
            "System Administrator", "admin@school.edu", "0000000000"
        )
        db.set_password(username, hashed_pw)
        db.log_action("SYSTEM", "INIT", f"System initialized by {username}")
    
    def has_default_password(self, username):
        """Check if the user's current password relies on the default initial assignment."""
        stored_hash = db.get_password(username)
        if not stored_hash:
            return False
        return verify_password("admin", stored_hash)


class AccessControl:
    """Manages role-specific data permissions across the application."""
    PERMISSIONS = {
        'Admin': {
            'view_all_data': True, 'edit_grades': True, 'delete_users': True,
            'update_own_profile': True, 'view_analytics': True, 'view_logs': True,
            'manage_eca': True, 'add_users': True
        },
        'Teacher': {
            'view_all_data': True, 'edit_grades': True, 'delete_users': False,
            'update_own_profile': True, 'view_analytics': True, 'view_logs': False,
            'manage_eca': True, 'add_users': False
        },
        'Student': {
            'view_all_data': False, 'edit_grades': False, 'delete_users': False,
            'update_own_profile': True, 'view_analytics': False, 'view_logs': False,
            'manage_eca': False, 'add_users': False
        }
    }
    
    @classmethod
    def has_permission(cls, role, permission):
        """Return True if the specified role is granted the particular permission."""
        return cls.PERMISSIONS.get(role, {}).get(permission, False)
    
    @classmethod
    def check_permission(cls, role, permission):
        """Alert and return False if a permission check fails for a role."""
        if not cls.has_permission(role, permission):
            print(f"\n{error('Access denied: ' + permission + ' - Not permitted for ' + role)}")
            return False
        return True

auth = Auth()
import sys
import time
from database import db
from auth import auth
from core import get_user_object
from ui import (clear_screen, boot_system, print_menu, get_menu_choice, pause,
                error, success, warning,
                hr, box, render_user_info, render_page_header,
                section_separator, print_banner,
                logout_sequence, render_goodbye,
                BOLD, BLUE, CYAN, GREEN, RED, YELLOW, RESET, W,
                get_password, hash_password, MIN_PASSWORD_LENGTH,
                validate_email)

def handle_logout(user):
    """Handle the logout flow with aesthetic sequence and premium visuals."""
    logout_sequence()
    
    while True:
        render_goodbye()
        
        options = {
            "1": "Login Again",
            "0": "Exit Application"
        }
        
        for key, value in options.items():
            print(f" {BOLD}{BLUE}[{key}]{RESET} {value}")
        
        section_separator()
        choice = input(f"{YELLOW}Select an option: {RESET}").strip()
        
        if choice == "1":
            return False
        elif choice == "0":
            clear_screen()
            render_goodbye()
            print(f"{GREEN}{'SYSTEM SHUTDOWN COMPLETE'.center(W)}{RESET}")
            time.sleep(1.5)
            return True
        else:
            print(error("Invalid selection. Please use 1 or 0."))
            time.sleep(1)
            clear_screen()

def main_menu(user):
    """Render the primary navigation gateway according to the authenticated user's role."""
    while True:
        clear_screen()
        
        if user.role == "Admin":
            options = {
                "1": "User Management",
                "2": "Academic Management",
                "3": "Search & Filter",
                "4": "Analytics & Reports",
                "5": "Settings",
                "6": "Logout"
            }
            print_menu("ADMIN DASHBOARD", options, user)
            choice = get_menu_choice(options)
            
            if choice == "1":
                user_management_menu(user)
            elif choice == "2":
                academic_menu(user)
            elif choice == "3":
                search_filter_menu(user)
            elif choice == "4":
                analytics_menu(user)
            elif choice == "5":
                settings_menu(user)
            elif choice == "6":
                db.log_action(user.username, "LOGOUT", "")
                return handle_logout(user)
        
        elif user.role == "Teacher":
            options = {
                "1": "Academic Management",
                "2": "Search & Filter",
                "3": "Analytics & Reports",
                "4": "Settings",
                "5": "Logout"
            }
            print_menu("TEACHER DASHBOARD", options, user)
            choice = get_menu_choice(options)
            
            if choice == "1":
                academic_menu(user)
            elif choice == "2":
                search_filter_menu(user)
            elif choice == "3":
                analytics_menu(user)
            elif choice == "4":
                settings_menu(user)
            elif choice == "5":
                db.log_action(user.username, "LOGOUT", "")
                return handle_logout(user)
        
        elif user.role == "Student":
            options = {
                "1": "My Profile",
                "2": "My Grades",
                "3": "My ECA",
                "4": "Performance Analysis",
                "5": "Export My Grades (CSV)",
                "6": "Settings",
                "7": "Logout"
            }
            print_menu("STUDENT DASHBOARD", options, user)
            choice = get_menu_choice(options)
            
            if choice == "1":
                user.view_profile()
                pause()
            elif choice == "2":
                user.view_own_grades()
                pause()
            elif choice == "3":
                user.view_own_eca()
                pause()
            elif choice == "4":
                user.view_own_performance()
                pause()
            elif choice == "5":
                user.export_performance()
                pause()
            elif choice == "6":
                settings_menu(user)
            elif choice == "7":
                db.log_action(user.username, "LOGOUT", "")
                return handle_logout(user)

def user_management_menu(user):
    """Direct queries related to broad administrative footprint administration."""
    while True:
        clear_screen()
        options = {
            "1": "View All Users",
            "2": "Add New User",
            "3": "Delete User",
            "4": "Back to Main Menu"
        }
        print_menu("USER MANAGEMENT", options, user)
        choice = get_menu_choice(options)
        
        if choice == "1":
            user.view_all_users()
            pause()
        elif choice == "2":
            add_new_user_menu(user)
        elif choice == "3":
            delete_user_menu(user)
        elif choice == "4":
            break

def academic_menu(user):
    """Provide workflows to read and record grades or extracurricular events."""
    while True:
        clear_screen()
        options = {
            "1": "View All Students",
            "2": "Update Grades",
            "3": "Manage ECA",
            "4": "Back to Main Menu"
        }
        print_menu("ACADEMIC MANAGEMENT", options, user)
        choice = get_menu_choice(options)
        
        if choice == "1":
            user.view_all_students()
            pause()
        elif choice == "2":
            update_grade_menu(user)
        elif choice == "3":
            add_eca_menu(user)
        elif choice == "4":
            break

def search_filter_menu(user):
    """Serve specific tools helping educators segment and isolate individuals."""
    while True:
        clear_screen()
        options = {
            "1": "Search Students",
            "2": "Filter by Performance",
            "3": "Filter by ECA",
            "4": "Back to Main Menu"
        }
        print_menu("SEARCH & FILTER", options, user)
        choice = get_menu_choice(options)
        
        if choice == "1":
            query = input("\nSearch: ").strip()
            user.search_students(query)
            pause()
        elif choice == "2":
            filter_performance_menu(user)
        elif choice == "3":
            filter_eca_menu(user)
        elif choice == "4":
            break

def analytics_menu(user):
    """Trigger the system-wide measurement console compiling numerical benchmarks."""
    from analytics import Analytics
    analytics_svc = Analytics()
    
    while True:
        clear_screen()
        options = {
            "1": "View Text Dashboard",
            "2": "Grade Trends Chart",
            "3": "ECA vs. Grades Scatter Plot",
            "4": "Performance Alerts",
            "5": "Export All Grades (CSV)",
            "6": "Back to Main Menu"
        }
        print_menu("ANALYTICS & REPORTS", options, user)
        choice = get_menu_choice(options)
        
        if choice == "1":
            user.view_analytics_dashboard()
            pause()
        elif choice == "2":
            clear_screen()
            print(f"{YELLOW}Generating Grade Trends Chart...{RESET}")
            analytics_svc.plot_grade_trends()
            pause()
        elif choice == "3":
            clear_screen()
            print(f"{YELLOW}Generating ECA Correlation Plot...{RESET}")
            analytics_svc.plot_eca_vs_grades()
            pause()
        elif choice == "4":
            clear_screen()
            analytics_svc.generate_performance_alerts()
            pause()
        elif choice == "5":
            clear_screen()
            user.export_global_performance()
            pause()
        elif choice == "6":
            break

def settings_menu(user):
    """Control an end user's capacity to adjust structural preferences on themselves."""
    while True:
        clear_screen()
        options = {
            "1": "Update Profile",
            "2": "Change Password",
            "3": "Back to Main Menu"
        }
        print_menu("SETTINGS", options, user)
        choice = get_menu_choice(options)
        
        if choice == "1":
            update_profile_menu(user)
        elif choice == "2":
            change_password_menu(user)
        elif choice == "3":
            break

def add_new_user_menu(admin_user):
    """Facilitate a form flow initializing and authorizing a new user footprint."""
    while True:
        clear_screen()
        render_user_info(admin_user)
        section_separator()
        render_page_header("ADD NEW USER")
        section_separator()
        
        while True:
            print(f"{YELLOW}Username:{RESET} ", end="")
            username = input().strip()
            if not username:
                print(error("Username cannot be empty."))
                continue
            
            if db.user_exists(username):
                print(error("User already exists!"))
                continue
            break
        
        while True:
            print("Roles: 1. Admin  2. Teacher  3. Student")
            print(f"{YELLOW}Select role (1-3):{RESET} ", end="")
            role_choice = input().strip()
            role_map = {'1': 'Admin', '2': 'Teacher', '3': 'Student'}
            role = role_map.get(role_choice)
            if role:
                break
            print(error("Invalid input. Please select a valid role (1-3)."))
        
        while True:
            print(f"{YELLOW}Full Name:{RESET} ", end="")
            name = input().strip()
            if name:
                break
            print(error("Full Name cannot be empty."))
        
        while True:
            print(f"{YELLOW}Email:{RESET} ", end="")
            email = input().strip()
            if not email or validate_email(email):
                break
            print(error("Invalid email format. Please try again."))
            
        print(f"{YELLOW}Phone:{RESET} ", end="")
        phone = input().strip()
        
        custom_id = None
        if role == 'Student':
            while True:
                print(f"{YELLOW}Student ID:{RESET} ", end="")
                custom_id = input().strip()
                if custom_id:
                    if db.get_user_by_id(custom_id):
                        print(error(f"Student ID {custom_id} already exists. Please try another."))
                        continue
                    break
                print(error("Student ID cannot be empty."))
        
        user_id = admin_user.add_user(username, role, name, email, phone, custom_id)
        
        if user_id:
            while True:
                print(f"{YELLOW}Set initial password:{RESET} ", end="")
                password = input().strip()
                if len(password) >= MIN_PASSWORD_LENGTH:
                    admin_user.set_user_password(username, password)
                    break
                else:
                    print(error("Password too short. Please try again."))
                
            if role == 'Student':
                subjects = ["Mathematics", "Science", "English", "Computer", "Physics"]
                updated_subjects = []
                for subject in subjects:
                    while True:
                        print(f"{subject}: ", end="")
                        val = input().strip()
                        if not val:
                            break
                        try:
                            score = float(val)
                            if 0 <= score <= 100:
                                if admin_user.update_student_grade(user_id, subject, score):
                                    updated_subjects.append(subject)
                                break
                            else:
                                print(error("Score must be between 0 and 100."))
                        except ValueError:
                            print(error("Invalid score. Please enter a numerical value."))
                
                if updated_subjects:
                    print(success(f"\nMarks successfully updated for student {name}: {', '.join(updated_subjects)}."))
        
        while True:
            print(f"\n{YELLOW}Add another user? (y/n):{RESET} ", end="")
            again = input().strip().lower()
            if again in ['yes', 'y', 'no', 'n']:
                break
            print(error("Invalid input. Please enter 'y' or 'n'."))
            
        if again in ['no', 'n']:
            break

def delete_user_menu(admin_user):
    """Execute the interactive workflow dropping the selected identity from files."""
    while True:
        clear_screen()
        admin_user.view_all_users()
        while True:
            print(f"\n{YELLOW}Enter User ID to delete (enter '0' to cancel):{RESET} ", end="")
            user_id = input().strip()
            if user_id == '0':
                return
            if not user_id:
                print(error("User ID cannot be empty."))
                continue
            break
            
        while True:
            confirm = input(f"Confirm delete {user_id}? (y/n): ").strip().lower()
            if confirm in ['yes', 'y']:
                admin_user.delete_user(user_id)
                break
            elif confirm in ['no', 'n']:
                print(warning("Delete cancelled."))
                break
            else:
                print(error("Invalid input. Please enter 'y' or 'n'."))
                
        while True:
            print(f"\n{YELLOW}Delete another user? (y/n):{RESET} ", end="")
            again = input().strip().lower()
            if again in ['yes', 'y', 'no', 'n']:
                break
            print(error("Invalid input. Please enter 'y' or 'n'."))
            
        if again in ['no', 'n']:
            break

def update_grade_menu(user):
    """Form to accept subject evaluations and deposit them under a target ID."""
    while True:
        clear_screen()
        render_user_info(user)
        section_separator()
        render_page_header("UPDATE GRADE")
        section_separator()
        user.view_all_students()
        
        while True:
            print(f"\n{YELLOW}Enter Student ID (enter '0' to cancel):{RESET} ", end="")
            student_id = input().strip()
            if student_id == '0':
                return
            if not student_id:
                print(error("Student ID cannot be empty."))
                continue
            
            student = db.get_user_by_id(student_id)
            if not student or student['role'] != 'Student':
                print(error("Student not found."))
                continue
            break
        
        subjects = ["Mathematics", "Science", "English", "Computer", "Physics"]
        print(f"\n{CYAN}Update grades for {student['name']} (ID: {student['id']}){RESET}")
        print(f"{YELLOW}Press Enter to skip a subject.{RESET}")
        section_separator()
        
        updated_subjects = []
        for subject in subjects:
            while True:
                print(f"{subject}: ", end="")
                val = input().strip()
                if not val:
                    break
                try:
                    score = float(val)
                    if 0 <= score <= 100:
                        if user.update_student_grade(student_id, subject, score):
                            updated_subjects.append(subject)
                        break
                    else:
                        print(error("Score must be between 0 and 100."))
                except ValueError:
                    print(error("Invalid score. Please enter a numerical value."))
                    
        if updated_subjects:
            print(success(f"\nMarks successfully updated for student {student['name']}: {', '.join(updated_subjects)}."))
                
        while True:
            print(f"\n{YELLOW}Update another grade? (y/n):{RESET} ", end="")
            again = input().strip().lower()
            if again in ['yes', 'y', 'no', 'n']:
                break
            print(error("Invalid input. Please enter 'y' or 'n'."))
            
        if again in ['no', 'n']:
            break

def add_eca_menu(user):
    """Deploy fields to catalog a volunteer or sporting participation entry."""
    while True:
        clear_screen()
        render_user_info(user)
        section_separator()
        render_page_header("ADD ECA ACTIVITY")
        section_separator()
        user.view_all_students()
        
        while True:
            print(f"\n{YELLOW}Student ID (enter '0' to cancel):{RESET} ", end="")
            student_id = input().strip()
            if student_id == '0':
                return
            if not student_id:
                print(error("Student ID cannot be empty."))
                continue
            
            student = db.get_user_by_id(student_id)
            if not student or student['role'] != 'Student':
                print(error("Student not found."))
                continue
            break
        
        while True:
            print(f"{YELLOW}Activity Name:{RESET} ", end="")
            activity = input().strip()
            if not activity:
                print(error("Activity Name cannot be empty."))
                continue
            break
            
        while True:
            print(f"{YELLOW}Role:{RESET} ", end="")
            role = input().strip()
            if not role:
                print(error("Role cannot be empty."))
                continue
            break
        
        user.add_student_eca(student_id, activity, role)
        
        while True:
            print(f"\n{YELLOW}Add another ECA? (y/n):{RESET} ", end="")
            again = input().strip().lower()
            if again in ['yes', 'y', 'no', 'n']:
                break
            print(error("Invalid input. Please enter 'y' or 'n'."))
            
        if again in ['no', 'n']:
            break


def filter_performance_menu(user):
    """Query preformatted academic bands outputting matching student references."""
    clear_screen()
    print("\n1. Excellent (80-100%)")
    print("2. Good (70-80%)")
    print("3. Average (60-70%)")
    print("4. Below Average (<60%)")
    
    while True:
        choice = input("\nSelect: ").strip()
        
        if choice == '1':
            user.filter_by_performance_level(80, 100)
            break
        elif choice == '2':
            user.filter_by_performance_level(70, 80)
            break
        elif choice == '3':
            user.filter_by_performance_level(60, 70)
            break
        elif choice == '4':
            user.filter_by_performance_level(0, 60)
            break
        else:
            print(error("Invalid selection. Please choose 1-4."))
    
    pause()

def filter_eca_menu(user):
    """Trigger a dichotomous sort separating profiles based on external events logic."""
    clear_screen()
    print("1. With ECA")
    print("2. Without ECA")
    
    while True:
        choice = input("\nSelect: ").strip()
        
        if choice == '1':
            user.filter_by_eca_participation(True)
            break
        elif choice == '2':
            user.filter_by_eca_participation(False)
            break
        else:
            print(error("Invalid selection. Please choose 1 or 2."))
    
    pause()

def change_password_menu(user):
    """Prompt for credential validation and process an administrative re-routing to update a password."""
    clear_screen()
    render_user_info(user)
    section_separator()
    render_page_header("CHANGE PASSWORD")
    section_separator()
    
    old_pwd = get_password("Current password (enter to cancel): ").strip()
    if not old_pwd:
        return
        
    while True:
        new_pwd = get_password("New password: ").strip()
        
        if len(new_pwd) < MIN_PASSWORD_LENGTH:
            print(error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters."))
            continue
            
        confirm = get_password("Confirm password: ").strip()
        
        if new_pwd != confirm:
            print(error("Passwords do not match."))
            continue
            
        break
    
    if auth.change_password(user.username, old_pwd, new_pwd):
        print(success("Password changed successfully!"))
    else:
        print(error("Current password is incorrect."))
    
    pause()

def update_profile_menu(user):
    """Display inputs capturing modified personal descriptors and syncing changes."""
    clear_screen()
    render_user_info(user)
    section_separator()
    render_page_header("UPDATE PROFILE")
    section_separator()
    
    name = input("Name (enter to skip): ").strip()
    
    while True:
        email = input("Email (enter to skip): ").strip()
        if not email or validate_email(email):
            break
        print(error("Invalid email format. Please try again."))
        
    phone = input("Phone (enter to skip): ").strip()
    
    name = name or None
    email = email or None
    phone = phone or None
    
    if name or email or phone:
        user.update_profile(name, email, phone)
        print(success("Profile updated!"))
    else:
        print(warning("No changes made."))
    
    pause()

def authenticate():
    """Manage login with retry logic (3 attempts)."""
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        clear_screen()
        render_page_header("LOGIN")
        section_separator()
        
        username = input("\nUsername: ").strip()
        password = get_password("Password: ").strip()
        
        if not username or not password:
            print(error("Both username and password are required"))
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                print(warning(f"Attempts remaining: {remaining}"))
                pause()
            continue
        
        user = auth.login(username, password)
        
        if user:
            print(success(f"\nWelcome, {user['name']}!"))
            
            if auth.has_default_password(user['username']):
                if not force_password_change(user):
                    continue  # Go back to login
            
            return user
        else:
            attempts += 1
            remaining = max_attempts - attempts
            print(error(f"Login failed. {remaining} attempts remaining."))
            
            if remaining > 0:
                pause()
    
    print(error("Maximum login attempts exceeded. Exiting..."))
    sys.exit(1)

def force_password_change(user):
    """Force user to change default password."""
    print(warning("\nWARNING: Default password detected!"))
    print(f"{YELLOW}You must change your password before continuing.{RESET}")
    
    for _ in range(3):  # Allow 3 attempts
        new_pwd = get_password("New Password (min 8 chars): ").strip()
        
        if len(new_pwd) < 8:
            print(error("Password must be at least 8 characters"))
            continue
        
        confirm = get_password("Confirm Password: ").strip()
        
        if new_pwd != confirm:
            print(error("Passwords do not match"))
            continue
        
        hashed = hash_password(new_pwd)
        db.set_password(user['username'], hashed)
        db.log_action(user['username'], "PASSWORD_CHANGED", "Forced change from default")
        print(success("Password changed successfully!"))
        return True
    
    print(error("Failed to set new password. Please contact administrator."))
    return False

def run_setup():
    """Boot the initialization scripts populating files securely out of empty state."""
    auth.first_time_setup()

def main():
    """Initiate and orchestrate overall system components resolving program lifetime."""
    boot_system()
    
    if db.is_first_run():
        run_setup()
    
    while True:
        user = authenticate()
        user_obj = get_user_object(user)
        should_exit = main_menu(user_obj)
        if should_exit:
            break

if __name__ == "__main__":
    main()
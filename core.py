from database import db
from auth import auth, AccessControl
from ui import (error, success, warning,
                hr, box, render_page_header, section_separator,
                BOLD, BLUE, CYAN, GREEN, RED, YELLOW, RESET, W, clear_screen,
                hash_password)

class User:
    """Base class for modeling common user profile behaviors and details."""

    def __init__(self, user_data):
        """Initialize a User instance with demographic data."""
        self.id = user_data['id']
        self.username = user_data['username']
        self.role = user_data['role']
        self.name = user_data['name']
        self.email = user_data['email']
        self.phone = user_data['phone']
    
    def update_profile(self, name=None, email=None, phone=None):
        """Apply updates to the user's profile info and persist to database."""
        if not AccessControl.check_permission(self.role, 'update_own_profile'):
            return False
        if db.update_user(self.id, name, email, phone):
            db.log_action(self.username, "PROFILE_UPDATED", f"ID: {self.id}")
            if name: self.name = name
            if email: self.email = email
            if phone: self.phone = phone
            return True
        return False
    
    def view_profile(self):
        """Print the user's demographic information."""
        clear_screen()
        print(hr())
        print(f"  {BLUE}{BOLD} PROFILE INFORMATION{RESET}")
        print(hr())
        print(f"  ID:       {self.id}")
        print(f"  Username: {self.username}")
        print(f"  Role:     {self.role}")
        print(f"  Name:     {self.name}")
        print(f"  Email:    {self.email}")
        print(f"  Phone:    {self.phone}")
        print(hr())
    

class Student(User):
    """Represents a student user with abilities to view own grades and ECAs."""

    def __init__(self, user_data):
        """Initialize a Student instance."""
        super().__init__(user_data)
    
    def view_own_grades(self):
        """Fetch and print the academic grades specific to this student."""
        grades = db.get_grades_by_student(self.id)
        clear_screen()
        print(hr())
        print(f"  {BLUE}GRADES FOR {self.name}{RESET}")
        print(hr())
        if not grades:
            print("  No grades recorded yet.")
        else:
            for g in grades:
                print(f"  {g['subject']:<20} | {g['score']:5.1f} | {g['date']}")
        print(hr())
    
    def view_own_eca(self):
        """Fetch and print the extracurricular participation specific to this student."""
        eca = db.get_eca_by_student(self.id)
        clear_screen()
        print(hr())
        print(f"  {BLUE}ECA PARTICIPATION FOR {self.name}{RESET}")
        print(hr())
        if not eca:
            print("  No ECA activities recorded yet.")
        else:
            for e in eca:
                print(f"  {e['activity']:<20} | {e['role']:<15} | {e['date']}")
        print(hr())
    
    def view_own_performance(self):
        """Generate and print statistics detailing this student's grade performance."""
        from analytics import Analytics
        analytics = Analytics()
        grades = db.get_grades_by_student(self.id)
        if not grades:
            print("  No grades available for performance analysis.")
            return
        scores = [g['score'] for g in grades]
        stats = analytics.calculate_statistics(scores)
        clear_screen()
        print(hr())
        print(f"  {BLUE}PERFORMANCE ANALYSIS FOR {self.name}{RESET}")
        print(hr())
        print(f"  Average:   {stats['mean']:.2f}")
        print(f"  Median:    {stats['median']:.2f}")
        print(f"  Std Dev:   {stats['std']:.2f}")
        print(f"  Min:       {stats['min']:.2f}")
        print(f"  Max:       {stats['max']:.2f}")
        print(hr())

    def export_performance(self):
        """Invoke analytics service to export this student's grades to CSV."""
        from analytics import Analytics
        analytics = Analytics()
        success_flag, result = analytics.export_performance_to_csv(self.id)
        if success_flag:
            print(success(f"Report exported successfully: {result}"))
        else:
            print(error(result))


class Teacher(User):
    """Represents a faculty user bridging access over student cohorts."""

    def __init__(self, user_data):
        """Initialize a Teacher instance."""
        super().__init__(user_data)
    
    def view_all_students(self):
        """Print a list of all recognized student records."""
        if not AccessControl.check_permission(self.role, 'view_all_data'):
            return
        students = db.get_students()
        clear_screen()
        print(hr())
        print(f"  {BLUE}ALL STUDENTS ({len(students)} total){RESET}")
        print(hr())
        if not students:
            print("  No students found.")
        else:
            print(f"  {BOLD}{'ID'.ljust(5)} | {'NAME'.ljust(25)} | EMAIL{RESET}")
            print("  " + "-" * (W - 4))
            for s in students:
                print(f"  {s['id']:<5} | {s['name']:<25} | {s['email']}")
        print(hr())
    
    def update_student_grade(self, student_id, subject, score):
        """Update or assign a new grade for a specific student and subject."""
        if not AccessControl.check_permission(self.role, 'edit_grades'):
            return
        student = db.get_user_by_id(student_id)
        if not student or student['role'] != 'Student':
            print(error("Student not found."))
            return
        existing = db.get_grades_by_student(student_id)
        grade_exists = any(g['subject'] == subject for g in existing)
        if grade_exists:
            db.update_grade(student_id, subject, score)
            db.log_action(self.username, "GRADE_UPDATED", f"{student_id}|{subject}|{score}")
            return True
        else:
            db.add_grade(student_id, subject, score, self.id)
            db.log_action(self.username, "GRADE_ADDED", f"{student_id}|{subject}|{score}")
            return True
    
    def add_student_eca(self, student_id, activity, role):
        """Assign an extracurricular activity record to a student."""
        if not AccessControl.check_permission(self.role, 'manage_eca'):
            return
        student = db.get_user_by_id(student_id)
        if not student or student['role'] != 'Student':
            print(error("Student not found."))
            return
        db.add_eca(student_id, activity, role)
        db.log_action(self.username, "ECA_ADDED", f"{student_id}|{activity}")
        print(success(f"\nECA added: {activity}"))
    
    def search_students(self, query):
        """Find and print returning students derived from a target string query."""
        if not AccessControl.check_permission(self.role, 'view_all_data'):
            return []
        results = db.search_students(query)
        clear_screen()
        print(hr())
        print(f"  {BLUE}SEARCH RESULTS FOR '{query}'{RESET}")
        print(hr())
        if not results:
            print("  No students found.")
        else:
            print(f"  {BOLD}{'ID'.ljust(5)} | {'NAME'.ljust(25)} | EMAIL{RESET}")
            print("  " + "-" * (W - 4))
            for s in results:
                print(f"  {s['id']:<5} | {s['name']:<25} | {s['email']}")
        print(hr())
        return results
    
    def filter_by_performance_level(self, min_avg, max_avg):
        """Locate and display students with cumulative averages fitting inside bounds."""
        if not AccessControl.check_permission(self.role, 'view_all_data'):
            return
        results = db.filter_by_performance(min_avg, max_avg)
        clear_screen()
        print(hr())
        print(f"  {BLUE}STUDENTS BY PERFORMANCE ({min_avg}-{max_avg}%){RESET}")
        print(hr())
        if not results:
            print("  No students found.")
        else:
            print(f"  {BOLD}{'ID'.ljust(5)} | {'NAME'.ljust(25)} | AVERAGE{RESET}")
            print("  " + "-" * (W - 4))
            for s in results:
                print(f"  {s['id']:<5} | {s['name']:<25} | {s['avg_grade']:<10.1f}")
        print(hr())
    
    def filter_by_eca_participation(self, has_eca):
        """Show lists of students designated by boolean participation in ECAs."""
        if not AccessControl.check_permission(self.role, 'view_all_data'):
            return
        results = db.filter_by_eca(has_eca)
        status = "with ECA" if has_eca else "without ECA"
        clear_screen()
        print(hr())
        print(f"  {BLUE}STUDENTS {status.upper()} ({len(results)} total){RESET}")
        print(hr())
        if not results:
            print("  No students found.")
        else:
            print(f"  {BOLD}{'ID'.ljust(5)} | {'NAME'.ljust(25)} | EMAIL{RESET}")
            print("  " + "-" * (W - 4))
            for s in results:
                print(f"  {s['id']:<5} | {s['name']:<25} | {s['email']}")
        print(hr())

    def view_analytics_dashboard(self):
        """Instantiate tracking services allowing for mass presentation summaries of user metrics."""
        if not AccessControl.check_permission(self.role, 'view_analytics'):
            return
        from analytics import Analytics
        analytics = Analytics()
        analytics.print_dashboard()

    def export_global_performance(self):
        """Export comprehensive system-wide performance data to CSV."""
        if not AccessControl.check_permission(self.role, 'view_analytics'):
            return
        from analytics import Analytics
        analytics = Analytics()
        success_flag, result = analytics.export_performance_to_csv()
        if success_flag:
            print(success(f"Global report exported to: {result}"))
        else:
            print(error(result))


class Admin(Teacher):
    """Represents an elevated faculty user able to globally manage infrastructure and personnel."""

    def __init__(self, user_data):
        """Initialize an Admin instance."""
        super().__init__(user_data)
    
    def add_user(self, username, role, name, email, phone, custom_id=None):
        """Insert a valid configuration footprint forming a newly assigned user."""
        if not AccessControl.check_permission(self.role, 'add_users'):
            return
        if db.user_exists(username):
            print(error("User already exists."))
            return
            
        if custom_id:
            if db.get_user_by_id(custom_id):
                print(error(f"User ID {custom_id} already exists."))
                return
            user_id = custom_id
        else:
            base_id = db.get_new_user_id()
            user_id = f"{base_id}_{self.id}"
            
        db.add_user(user_id, username, role, name, email, phone)
        db.log_action(self.username, "USER_CREATED", f"{user_id}|{username}|{role}")
        print(success(f"\nUser created: {username} (ID: {user_id})"))
        return user_id
    
    def set_user_password(self, username, password):
        """Assign or override the credentials guarding an identified user."""
        if not AccessControl.check_permission(self.role, 'add_users'):
            return
        if not db.user_exists(username):
            print(error("User does not exist."))
            return
        hashed = hash_password(password)
        db.set_password(username, hashed)
        db.log_action(self.username, "PASSWORD_SET", f"Username: {username}")
        print(success(f"\nPassword set for: {username}"))
    
    def delete_user(self, user_id):
        """Purge all reference of an existing administrative or general user footprint."""
        if not AccessControl.check_permission(self.role, 'delete_users'):
            return
        user = db.get_user_by_id(user_id)
        if not user:
            print(error("User not found."))
            return
        if user['role'] == 'Admin' and user_id == self.id:
            print(error("Cannot delete your own admin account."))
            return
        db.delete_user(user_id)
        db.log_action(self.username, "USER_DELETED", f"ID: {user_id}")
        print(success(f"\nUser deleted: {user_id}"))
        return True
    
    def view_all_users(self):
        """Enumerate formatted displays describing user identification markers across the whole system."""
        all_users = db.get_all_users()
        clear_screen()
        print(hr())
        print(f"  {BLUE}{BOLD} ALL USERS ({len(all_users)} total){RESET}")
        print(hr())
        print(f"  {BOLD}{'ID'.ljust(5)} | {'USERNAME'.ljust(15)} | {'ROLE'.ljust(10)} | NAME{RESET}")
        print("  " + "-" * (W - 4))
        for u in all_users:
            role_color = BLUE if u['role'] == 'Student' else YELLOW if u['role'] == 'Teacher' else RED
            print(f"  {u['id']:<5} | {u['username']:<15} | {role_color}{u['role']:<10}{RESET} | {u['name']}")
        print(hr())


def get_user_object(user_data):
    """Factory evaluating a payload to instantiate its matching specialized role class."""
    role = user_data['role']
    if role == 'Admin':
        return Admin(user_data)
    elif role == 'Teacher':
        return Teacher(user_data)
    elif role == 'Student':
        return Student(user_data)
    return User(user_data)
import os
import shutil
import tempfile
import time
from datetime import datetime
from ui import error

DATA_DIR = "Data"
BACKUP_DIR = os.path.join(DATA_DIR, "backup")

USERS_FILE = os.path.join(DATA_DIR, "users.txt")
PASSWORDS_FILE = os.path.join(DATA_DIR, "passwords.txt")
GRADES_FILE = os.path.join(DATA_DIR, "grades.txt")
ECA_FILE = os.path.join(DATA_DIR, "eca.txt")
LOGS_FILE = os.path.join(DATA_DIR, "logs.txt")


class Database:
    """Manages file-based database operations."""

    def __init__(self):
        """Initialize directory structures for the database."""
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
    
    def _read_file(self, filepath):
        """Read data from a text file, ignoring empty lines."""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except (OSError, UnicodeDecodeError):
            return []
    
    def _write_file(self, filepath, data):
        """Write an array of strings to a text file."""
        try:
            with open(filepath, 'w') as f:
                for line in data:
                    f.write(line + '\n')
        except OSError:
            print(error(f"Failed to write to file: {filepath}"))
    
    def _create_backup(self, filepath):
        """Create a timestamped backup of the given file."""
        if not os.path.exists(filepath):
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.basename(filepath)
        backup_name = f"{timestamp}_{basename}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        shutil.copy2(filepath, backup_path)
    
    def _backup_all(self):
        """Backup all primary database files."""
        for filepath in [USERS_FILE, PASSWORDS_FILE, GRADES_FILE, ECA_FILE]:
            self._create_backup(filepath)
    
    def _atomic_write(self, filepath, data_lines):
        """
        Write data to file atomically using a temporary file.
        Prevents data corruption if system crashes during write.
        """
        dir_name = os.path.dirname(filepath)
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=dir_name,
            prefix='.tmp_',
            delete=False,
            encoding='utf-8'
        ) as tmp_file:
            for line in data_lines:
                tmp_file.write(line + '\n')
            tmp_path = tmp_file.name
        
        try:
            os.replace(tmp_path, filepath)
        except OSError:
            time.sleep(0.1)
            os.replace(tmp_path, filepath)
    
    def get_all_users(self):
        """Return a list of all user records as dictionaries."""
        users = []
        for line in self._read_file(USERS_FILE):
            parts = line.split('|')
            if len(parts) >= 6:
                users.append({
                    'id': parts[0], 'username': parts[1], 'role': parts[2],
                    'name': parts[3], 'email': parts[4], 'phone': parts[5]
                })
        return users
    
    def get_user_by_username(self, username):
        """Return the user record for the given username, or None if not found."""
        for user in self.get_all_users():
            if user['username'] == username:
                return user
        return None
    
    def get_user_by_id(self, user_id):
        """Return the user record for the given user ID, or None if not found."""
        for user in self.get_all_users():
            if user['id'] == user_id:
                return user
        return None
    
    def add_user(self, user_id, username, role, name, email, phone):
        """Add a new user record to the database with atomic write."""
        self._backup_all()
        
        users = self.get_all_users()
        
        if any(u['username'] == username for u in users):
            raise ValueError(f"Username {username} already exists")
        
        new_user = {
            'id': user_id, 'username': username, 'role': role,
            'name': name, 'email': email, 'phone': phone
        }
        users.append(new_user)
        
        lines = [
            f"{u['id']}|{u['username']}|{u['role']}|{u['name']}|{u['email']}|{u['phone']}"
            for u in users
        ]
        
        self._atomic_write(USERS_FILE, lines)
        return True
    
    def update_user(self, user_id, name=None, email=None, phone=None):
        """Update an existing user's details with atomic write."""
        self._backup_all()
        users = self.get_all_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                if name:
                    users[i]['name'] = name
                if email:
                    users[i]['email'] = email
                if phone:
                    users[i]['phone'] = phone
                break
        
        lines = [
            f"{u['id']}|{u['username']}|{u['role']}|{u['name']}|{u['email']}|{u['phone']}"
            for u in users
        ]
        self._atomic_write(USERS_FILE, lines)
        return True
    
    def delete_user(self, user_id):
        """Delete a user record with atomic write."""
        self._backup_all()
        users = self.get_all_users()
        users = [u for u in users if u['id'] != user_id]
        
        lines = [
            f"{u['id']}|{u['username']}|{u['role']}|{u['name']}|{u['email']}|{u['phone']}"
            for u in users
        ]
        self._atomic_write(USERS_FILE, lines)
        return True
    
    def get_all_passwords(self):
        """Return a dictionary of all usernames and their hashed passwords."""
        passwords = {}
        for line in self._read_file(PASSWORDS_FILE):
            parts = line.split('|')
            if len(parts) >= 2:
                passwords[parts[0]] = parts[1]
        return passwords
    
    def get_password(self, username):
        """Return the stored password hash for the given username."""
        return self.get_all_passwords().get(username)
    
    def set_password(self, username, hashed_password):
        """Update the stored password hash for the given username."""
        self._backup_all()
        passwords = self.get_all_passwords()
        passwords[username] = hashed_password
        
        lines = [f"{user}|{pwd}" for user, pwd in passwords.items()]
        self._atomic_write(PASSWORDS_FILE, lines)
    
    def get_all_grades(self):
        """Return a list of all grade records."""
        grades = []
        for line in self._read_file(GRADES_FILE):
            parts = line.split('|')
            if len(parts) >= 5:
                grades.append({
                    'student_id': parts[0], 'subject': parts[1],
                    'score': float(parts[2]), 'date': parts[3], 'teacher_id': parts[4]
                })
        return grades
    
    def get_grades_by_student(self, student_id):
        """Return a list of all grade records for a specific student."""
        return [g for g in self.get_all_grades() if g['student_id'] == student_id]
    
    def add_grade(self, student_id, subject, score, teacher_id):
        """Add a new grade record for a student with atomic write."""
        self._backup_all()
        grades = self.get_all_grades()
        date = datetime.now().strftime("%Y-%m-%d")
        
        grades.append({
            'student_id': student_id, 'subject': subject,
            'score': score, 'date': date, 'teacher_id': teacher_id
        })
        
        lines = [
            f"{g['student_id']}|{g['subject']}|{g['score']}|{g['date']}|{g['teacher_id']}"
            for g in grades
        ]
        self._atomic_write(GRADES_FILE, lines)
        return True
    
    def update_grade(self, student_id, subject, new_score):
        """Update an existing grade record for a student."""
        self._backup_all()
        grades = self.get_all_grades()
        for grade in grades:
            if grade['student_id'] == student_id and grade['subject'] == subject:
                grade['score'] = new_score
                grade['date'] = datetime.now().strftime("%Y-%m-%d")
                break
        self._write_file(GRADES_FILE, [
            f"{g['student_id']}|{g['subject']}|{g['score']}|{g['date']}|{g['teacher_id']}"
            for g in grades
        ])
        return True
    
    def get_all_eca(self):
        """Return a list of all ECA records."""
        eca = []
        for line in self._read_file(ECA_FILE):
            parts = line.split('|')
            if len(parts) >= 3:
                eca.append({
                    'student_id': parts[0], 'activity': parts[1],
                    'role': parts[2], 'date': parts[3]
                })
        return eca
    
    def get_eca_by_student(self, student_id):
        """Return a list of ECA records for a specific student."""
        return [e for e in self.get_all_eca() if e['student_id'] == student_id]
    
    def add_eca(self, student_id, activity, role):
        """Add a new ECA record for a student with atomic write."""
        self._backup_all()
        eca = self.get_all_eca()
        date = datetime.now().strftime("%Y-%m-%d")
        
        eca.append({
            'student_id': student_id, 'activity': activity,
            'role': role, 'date': date
        })
        
        lines = [
            f"{e['student_id']}|{e['activity']}|{e['role']}|{e['date']}"
            for e in eca
        ]
        self._atomic_write(ECA_FILE, lines)
        return True
    
    def get_students(self):
        """Return a list of all users with the role of 'Student'."""
        return [u for u in self.get_all_users() if u['role'] == 'Student']
    

    def log_action(self, username, action, details=""):
        """Record a system action to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{username}] {action}: {details}"
        with open(LOGS_FILE, 'a') as f:
            f.write(line + '\n')
    

    def search_students(self, query):
        """Return a list of students matching the given search query."""
        query = query.lower()
        return [s for s in self.get_students()
                if query in s['name'].lower() or query in s['id'].lower()]
    
    def filter_by_performance(self, min_avg=0, max_avg=100):
        """Return a list of students whose average grade falls within the specified range."""
        result = []
        for student in self.get_students():
            grades = self.get_grades_by_student(student['id'])
            if grades:
                avg = sum(g['score'] for g in grades) / len(grades)
                if min_avg <= avg <= max_avg:
                    result.append({**student, 'avg_grade': avg})
        return result
    
    def filter_by_eca(self, has_eca=True):
        """Return a list of students either with or without ECA participation."""
        students = self.get_students()
        eca_students = set(e['student_id'] for e in self.get_all_eca())
        if has_eca:
            return [s for s in students if s['id'] in eca_students]
        return [s for s in students if s['id'] not in eca_students]
    
    def get_new_user_id(self, role=None):
        """Generate and return a new unique user ID based on role-specific logic."""
        users = self.get_all_users()
        if not users:
            return "1"
        
        if role in ['Admin', 'Teacher']:
            target_users = [u for u in users if u['role'] in ['Admin', 'Teacher']]
        else:
            target_users = users
            
        if not target_users:
            return "1"
            
        max_id = 0
        for u in target_users:
            uid = str(u['id'])
            if uid.isdigit():
                val = int(uid)
            elif '_' in uid:
                prefix = uid.split('_')[0]
                if prefix.isdigit():
                    val = int(prefix)
                else:
                    val = 0
            else:
                val = 0
                
            if val > max_id:
                max_id = val
                
        return str(max_id + 1)
    
    def user_exists(self, username):
        """Check whether a given username already exists in the database."""
        return self.get_user_by_username(username) is not None
    
    def is_first_run(self):
        """Check if this is the first execution by verifying core file existence."""
        return not os.path.exists(USERS_FILE) or not os.path.exists(PASSWORDS_FILE)

db = Database()
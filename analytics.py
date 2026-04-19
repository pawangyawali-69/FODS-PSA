import math
from database import db
from ui import (error, success, warning,
                hr, box, render_page_header, section_separator,
                BOLD, BLUE, CYAN, GREEN, RED, YELLOW, RESET, W)

class Analytics:
    """Provides analytical tools for processing student performance data."""

    def __init__(self):
        """Initialize the Analytics service."""
        pass
    
    def calculate_statistics(self, scores):
        """Calculate and return key statistics (mean, median, etc.) for a list of scores."""
        if not scores:
            return {'mean': 0, 'median': 0, 'std': 0, 'min': 0, 'max': 0, 'count': 0}
        
        n = len(scores)
        mean = sum(scores) / n
        
        sorted_scores = sorted(scores)
        if n % 2 == 0:
            median = (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
        else:
            median = sorted_scores[n//2]
        
        variance = sum((x - mean) ** 2 for x in scores) / n
        std = math.sqrt(variance)
        
        return {'mean': mean, 'median': median, 'std': std, 
                'min': min(scores), 'max': max(scores), 'count': n}
    
    def calculate_correlation(self, x_values, y_values):
        """Calculate the Pearson correlation coefficient between two sets of values."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0
        
        n = len(x_values)
        mean_x = sum(x_values) / n
        mean_y = sum(y_values) / n
        
        numerator = sum((x_values[i] - mean_x) * (y_values[i] - mean_y) for i in range(n))
        sum_sq_x = sum((x - mean_x) ** 2 for x in x_values)
        sum_sq_y = sum((y - mean_y) ** 2 for y in y_values)
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        if denominator == 0:
            return 0
        return numerator / denominator
    
    def get_all_student_grades(self):
        """Return a mapping of all student IDs to their grades and names."""
        student_grades = {}
        for student in db.get_students():
            grades = db.get_grades_by_student(student['id'])
            if grades:
                student_grades[student['id']] = {
                    'name': student['name'],
                    'grades': [g['score'] for g in grades]
                }
        return student_grades
    
    def get_student_eca_count(self):
        """Return a mapping of student IDs to their total count of ECA participations."""
        eca_count = {}
        for e in db.get_all_eca():
            eca_count[e['student_id']] = eca_count.get(e['student_id'], 0) + 1
        return eca_count
    
    def get_performance_rankings(self):
        """Return a sorted list of students ranked by their average performance."""
        student_grades = self.get_all_student_grades()
        rankings = []
        
        for student_id, data in student_grades.items():
            scores = data['grades']
            if scores:
                avg = sum(scores) / len(scores)
                rankings.append({
                    'student_id': student_id,
                    'name': data['name'],
                    'average': avg,
                    'subject_count': len(scores)
                })
        
        rankings.sort(key=lambda x: x['average'], reverse=True)
        
        for i, r in enumerate(rankings):
            r['rank'] = i + 1
        
        return rankings
    

    
    def get_top_performers(self, count=5):
        """Return the top N performing students."""
        return self.get_performance_rankings()[:count]
    
    def get_weak_performers(self, threshold=60, count=5):
        """Return up to N students with averages below the given threshold."""
        rankings = self.get_performance_rankings()
        weak = [r for r in rankings if r['average'] < threshold]
        return weak[:count]
    
    def analyze_eca_academic_correlation(self):
        """Analyze and interpret the correlation between ECA involvement and academic grades."""
        student_grades = self.get_all_student_grades()
        eca_count = self.get_student_eca_count()
        
        x_values, y_values = [], []
        
        for student_id, data in student_grades.items():
            if student_id in eca_count:
                avg = sum(data['grades']) / len(data['grades'])
                x_values.append(eca_count[student_id])
                y_values.append(avg)
        
        if len(x_values) < 2:
            return {'correlation': 0, 'interpretation': 'insufficient data'}
        
        correlation = self.calculate_correlation(x_values, y_values)
        
        if correlation > 0.5:
            interpretation = 'strong positive - more ECA = better grades'
        elif correlation > 0.2:
            interpretation = 'moderate positive - ECA may help grades'
        elif correlation > -0.2:
            interpretation = 'weak/neutral - no significant relationship'
        elif correlation > -0.5:
            interpretation = 'moderate negative - ECA may distract'
        else:
            interpretation = 'strong negative - ECA correlates with lower grades'
        
        return {'correlation': correlation, 'interpretation': interpretation}
    


    def get_subject_averages(self):
        """
        Calculate average grade for each subject across all students.
        Required for admin analytics requirement.
        """
        all_grades = db.get_all_grades()
        if not all_grades:
            return {}
        
        subject_scores = {}
        for grade in all_grades:
            subject = grade['subject']
            score = grade['score']
            
            if subject not in subject_scores:
                subject_scores[subject] = []
            subject_scores[subject].append(score)
        
        return {
            subject: sum(scores) / len(scores)
            for subject, scores in subject_scores.items()
        }
    
    def get_most_active_eca_students(self, limit=5):
        """
        Identify students with highest ECA participation.
        Required for "most active students in ECA" requirement.
        """
        eca_count = self.get_student_eca_count()
        
        if not eca_count:
            return []
        
        sorted_students = sorted(
            eca_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        results = []
        for student_id, count in sorted_students[:limit]:
            student = db.get_user_by_id(student_id)
            if student:
                results.append({
                    'name': student['name'],
                    'student_id': student_id,
                    'eca_count': count,
                    'email': student.get('email', 'N/A')
                })
        
        return results
    
    def print_subject_averages(self):
        """Display subject averages in the dashboard."""
        averages = self.get_subject_averages()
        if not averages:
            print("  No grade data available.")
            return
        
        print(f"\n  {CYAN}Subject Averages:{RESET}")
        print("  " + "-" * (W - 4))
        
        sorted_subjects = sorted(averages.items(), key=lambda x: x[1], reverse=True)
        
        for subject, avg in sorted_subjects:
            if avg >= 80:
                color = GREEN
            elif avg >= 60:
                color = YELLOW
            else:
                color = RED
            
            print(f"  {subject:<20}: {color}{avg:6.1f}%{RESET}")
    
    def print_eca_leaderboard(self, limit=5):
        """Display ECA participation leaderboard in dashboard."""
        leaders = self.get_most_active_eca_students(limit)
        
        if not leaders:
            print("  No ECA participation data available.")
            return
        
        print(f"\n  {CYAN}🏆 Most Active ECA Students:{RESET}")
        print("  " + "-" * (W - 4))
        
        for i, student in enumerate(leaders, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            print(f"  {medal} #{i}: {student['name']:<25} "
                  f"({student['eca_count']} activities)")
    
    def print_dashboard(self):
        """Print a comprehensive analytics overview dashboard to the terminal."""
        from ui import clear_screen
        clear_screen()
        render_page_header("ANALYTICS DASHBOARD", color=BLUE)
        section_separator()
        
        students = db.get_students()
        print(f"\n  Total Students: {len(students)}")
        
        all_grades = db.get_all_grades()
        print(f"  Total Grade Records: {len(all_grades)}")
        
        if all_grades:
            scores = [g['score'] for g in all_grades]
            stats = self.calculate_statistics(scores)
            print(f"\n  Overall Grade Statistics:")
            print(f"    Average:   {stats['mean']:.2f}")
            print(f"    Median:    {stats['median']:.2f}")
            print(f"    Std Dev:   {stats['std']:.2f}")
            print(f"    Min:       {stats['min']:.2f}")
            print(f"    Max:       {stats['max']:.2f}")
        
        self.print_subject_averages()
        
        print(f"\n  Top Performers:")
        top = self.get_top_performers(3)
        if top:
            for t in top:
                print(f"    #{t['rank']}: {t['name']} - {t['average']:.1f}%")
        else:
            print("    No data available")
        
        print(f"\n  Weak Performers (<60%):")
        weak = self.get_weak_performers(count=3)
        if weak:
            for w in weak:
                print(f"    {w['name']} - {w['average']:.1f}%")
        else:
            print("    No weak performers")
        
        self.print_eca_leaderboard(3)
        
        eca_correlation = self.analyze_eca_academic_correlation()
        print(f"\n  ECA-Academic Correlation:")
        print(f"    Correlation: {eca_correlation['correlation']:.3f}")
        print(f"    {eca_correlation['interpretation']}")
        
        print(f"\n{hr()}")
        
    def plot_grade_trends(self):
        """Line/bar charts showing grade trends per subject over time using pandas and matplotlib."""
        import pandas as pd
        import matplotlib.pyplot as plt
        all_grades = db.get_all_grades()
        if not all_grades:
            from ui import warning
            print(warning("No grades available to plot trends."))
            return
            
        df = pd.DataFrame(all_grades)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        
        # Calculate daily average per subject
        trend_df = df.groupby(['date', 'subject'])['score'].mean().unstack()
        
        plt.figure(figsize=(12, 6))
        for column in trend_df.columns:
            vals = trend_df[column].dropna()
            if not vals.empty:
                plt.plot(vals.index, vals.values, marker='o', label=column)
                
        plt.title('Grade Trends per Subject Over Time')
        plt.xlabel('Date')
        plt.ylabel('Average Score')
        plt.legend(title='Subject')
        plt.grid(True, alpha=0.3)
        plt.gcf().autofmt_xdate()
        plt.show()

    def plot_eca_vs_grades(self):
        """Scatter plot of ECA count vs. average grade using pandas and matplotlib."""
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np
        student_grades = self.get_all_student_grades()
        eca_count = self.get_student_eca_count()
        
        data = []
        for student_id, sd in student_grades.items():
            if student_id in eca_count:
                avg = sum(sd['grades']) / len(sd['grades'])
                data.append({'ECA Count': eca_count[student_id], 'Average Grade': avg})
                
        if len(data) < 2:
            print(warning("Insufficient data for ECA correlation visualization."))
            return
            
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['ECA Count'], df['Average Grade'], alpha=0.6, s=100, c='steelblue')
        
        z = np.polyfit(df['ECA Count'], df['Average Grade'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df['ECA Count'].min(), df['ECA Count'].max(), 100)
        plt.plot(x_line, p(x_line), 'r--', linewidth=2)
        
        correlation = df['ECA Count'].corr(df['Average Grade'])
        plt.xlabel('Number of ECA Activities')
        plt.ylabel('Average Grade (%)')
        plt.title(f'ECA Participation vs Academic Performance\n(r = {correlation:.3f})')
        plt.grid(True, alpha=0.3)
        plt.show()

    def generate_performance_alerts(self, drop_threshold=15):
        """Performance alerts showing if students dropped x% in any subject using pandas."""
        import pandas as pd
        all_grades = db.get_all_grades()
        if not all_grades:
            render_page_header("⚠️  PERFORMANCE ALERTS", color=YELLOW)
            section_separator()
            print("No grades available to calculate performance alerts.")
            return
            
        df = pd.DataFrame(all_grades)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        
        alerts = []
        for (student_id, subject), group in df.groupby(['student_id', 'subject']):
            if len(group) >= 2:
                scores = group['score'].tolist()
                recent_score = scores[-1]
                previous_max = max(scores[:-1])
                drop = previous_max - recent_score
                
                if drop >= drop_threshold:
                    student = db.get_user_by_id(student_id)
                    name = student['name'] if student else f"ID {student_id}"
                    alerts.append(f"🔴 {name} has dropped {drop:.1f}% in {subject} (was {previous_max:.1f}%, now {recent_score:.1f}%).")
                    
        render_page_header(f"⚠️  PERFORMANCE ALERTS (Drop >= {drop_threshold}%)", color=YELLOW)
        section_separator()
        
        if alerts:
            for alert in alerts:
                print(alert)
        else:
            print(success(f"No significant performance drops (\u2265{drop_threshold}%) detected."))
        print()

    def export_performance_to_csv(self, student_id=None):
        """
        Export performance data to a CSV file.
        If student_id is provided, only exports data for that student.
        Returns (success, message/filepath).
        """
        import pandas as pd
        import os
        from datetime import datetime
        
        export_dir = "Exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        all_grades = db.get_all_grades()
        if not all_grades:
            return False, "No performance data available to export."
            
        df = pd.DataFrame(all_grades)
        
        # Merge with student names for better report readability
        students = pd.DataFrame(db.get_students())
        if not students.empty:
            df = df.merge(students[['id', 'name']], left_on='student_id', right_on='id', how='left')
            df = df.drop(columns=['id'])
            # Reorder columns for better CSV view
            cols = ['student_id', 'name', 'subject', 'score', 'date', 'teacher_id']
            df = df[[c for c in cols if c in df.columns]]
            
        if student_id:
            df = df[df['student_id'] == student_id]
            if df.empty:
                return False, f"No performance records found for Student ID: {student_id}"
            filename = f"Performance_Report_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            filename = f"System_Wide_Performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        filepath = os.path.join(export_dir, filename)
        df.to_csv(filepath, index=False)
        return True, filepath

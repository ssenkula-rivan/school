#!/usr/bin/env python3
"""
Final status report of the school management system
"""
import sqlite3
import os

def generate_status_report():
    """Generate comprehensive status report"""
    db_path = 'school_management'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 SCHOOL MANAGEMENT SYSTEM STATUS REPORT")
        print("=" * 50)
        print(f"Database: {db_path}")
        print(f"Size: {os.path.getsize(db_path):,} bytes")
        print()
        
        # Schools
        cursor.execute("SELECT COUNT(*) FROM core_school;")
        school_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT name, code, school_type, is_active FROM core_school;")
        schools = cursor.fetchall()
        
        print(f"🏫 SCHOOLS: {school_count}")
        for school in schools:
            status = "✅ Active" if school[3] else "❌ Inactive"
            print(f"  - {school[0]} ({school[1]}) - {school[2]} - {status}")
        print()
        
        # Users
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM accounts_userprofile;")
        profile_count = cursor.fetchone()[0]
        
        print(f"👥 USERS: {user_count} total, {profile_count} with profiles")
        
        if user_count > 0:
            cursor.execute("""
                SELECT u.username, u.email, u.is_staff, u.is_superuser, u.is_active,
                       up.role, up.employee_id
                FROM auth_user u
                LEFT JOIN accounts_userprofile up ON u.id = up.user_id
                ORDER BY u.id;
            """)
            users = cursor.fetchall()
            
            for user in users:
                status = []
                if user[2]: status.append("Staff")
                if user[3]: status.append("Super")
                if user[4]: status.append("Active")
                else: status.append("Inactive")
                
                profile_info = f" - Role: {user[5]}, ID: {user[6]}" if user[5] else " - ❌ No Profile"
                print(f"  - {user[0]} ({user[1]}) - {', '.join(status)}{profile_info}")
        print()
        
        # Students
        cursor.execute("SELECT COUNT(*) FROM core_student;")
        student_count = cursor.fetchone()[0]
        print(f"🎓 STUDENTS: {student_count}")
        print()
        
        # Academic structure
        cursor.execute("SELECT COUNT(*) FROM core_academicyear;")
        year_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM core_grade;")
        grade_count = cursor.fetchone()[0]
        
        print(f"📚 ACADEMIC STRUCTURE:")
        print(f"  - Academic Years: {year_count}")
        print(f"  - Grades/Classes: {grade_count}")
        print()
        
        # Login statistics
        cursor.execute("SELECT COUNT(*) FROM accounts_loginlog;")
        login_attempts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM django_session;")
        sessions = cursor.fetchone()[0]
        
        print(f"🔐 SYSTEM ACTIVITY:")
        print(f"  - Login Attempts: {login_attempts}")
        print(f"  - Active Sessions: {sessions}")
        print()
        
        # Modules/Features
        modules = {
            "Academics": ["academics_classsubject", "academics_exam", "academics_studentattendance"],
            "Fees": ["fees_feepayment", "fees_feestructure", "fees_student"],
            "Employees": ["employees_employee", "employees_attendance"],
            "Library": ["library_book", "library_bookborrow"],
            "Inventory": ["inventory_asset", "inventory_purchase"],
            "Reports": ["django_admin_log"],
        }
        
        print("📋 MODULES STATUS:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        for module, tables in modules.items():
            module_tables = [t for t in tables if t in all_tables]
            status = "✅" if len(module_tables) >= 2 else "⚠️" if len(module_tables) == 1 else "❌"
            print(f"  {status} {module}: {len(module_tables)}/{len(tables)} tables")
        print()
        
        # Login readiness check
        print("🔑 LOGIN READINESS CHECK:")
        login_ready = True
        
        if user_count == 0:
            print("  ❌ No users found")
            login_ready = False
        elif profile_count < user_count:
            print(f"  ⚠️ {user_count - profile_count} user(s) missing profile")
            login_ready = False
        else:
            print("  ✅ All users have profiles")
        
        if school_count == 0:
            print("  ❌ No schools configured")
            login_ready = False
        else:
            print("  ✅ School configured")
        
        if login_ready:
            print("\n🎉 SYSTEM READY FOR LOGIN!")
            print("=" * 30)
            print("🌐 URL: https://school-management-c-8qtq.onrender.com/accounts/login/")
            print("👤 Username: admin")
            print("🔐 Password: [Your admin password]")
            print("\n💡 If login fails:")
            print("   1. Try password reset")
            print("   2. Access /admin/ for Django admin")
            print("   3. Check browser console for errors")
        else:
            print("\n⚠️ SYSTEM NOT READY")
            print("Complete the missing items above first")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_status_report()

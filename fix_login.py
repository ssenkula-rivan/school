#!/usr/bin/env python3
"""
Fix login issue by creating missing UserProfile
"""
import sqlite3
import os
from datetime import datetime

def fix_login():
    """Create missing UserProfile for admin user"""
    db_path = 'school_management'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing Login Issue")
        print("=" * 30)
        
        # Get admin user
        cursor.execute("""
            SELECT id, username, email, is_staff, is_superuser
            FROM auth_user 
            WHERE username = 'admin';
        """)
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ No admin user found")
            return
        
        user_id = admin_user[0]
        username = admin_user[1]
        
        print(f"✅ Found admin user: {username} (ID: {user_id})")
        
        # Check if profile already exists
        cursor.execute("""
            SELECT COUNT(*) FROM accounts_userprofile WHERE user_id = ?;
        """, (user_id,))
        profile_exists = cursor.fetchone()[0]
        
        if profile_exists > 0:
            print("✅ UserProfile already exists")
            return
        
        # Get school ID
        cursor.execute("SELECT id FROM core_school LIMIT 1;")
        school_result = cursor.fetchone()
        school_id = school_result[0] if school_result else None
        
        if not school_id:
            print("❌ No school found - creating one first")
            cursor.execute("""
                INSERT INTO core_school (name, code, school_type, institution_type, email, phone, address, is_active, subscription_start, subscription_end, max_students, max_staff, currency, timezone, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                "Test School", "TEST", "primary", "private", 
                "admin@school.com", "+1234567890", "123 Test Street",
                True, "2026-01-01", "2026-12-31", 1000, 100, "USD", "UTC",
                datetime.now(), datetime.now()
            ))
            school_id = cursor.lastrowid
            print(f"✅ Created school with ID: {school_id}")
        
        # Generate employee ID
        import uuid
        employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        
        # Create UserProfile
        cursor.execute("""
            INSERT INTO accounts_userprofile 
            (employee_id, role, phone, address, hire_date, is_active_employee, created_at, updated_at, department_id, user_id, class_name, force_password_reset)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            employee_id,
            'admin',  # Role
            '',  # Phone
            '',  # Address
            datetime.now().date(),  # Hire date
            True,  # Is active employee
            datetime.now(),  # Created at
            datetime.now(),  # Updated at
            None,  # Department ID
            user_id,  # User ID
            '',  # Class name
            False  # Force password reset
        ))
        
        profile_id = cursor.lastrowid
        print(f"✅ Created UserProfile with ID: {profile_id}")
        print(f"  Employee ID: {employee_id}")
        print(f"  Role: admin")
        print(f"  School ID: {school_id}")
        
        # Update user to be staff and superuser
        cursor.execute("""
            UPDATE auth_user 
            SET is_staff = ?, is_superuser = ?
            WHERE id = ?;
        """, (True, True, user_id))
        
        print(f"✅ Updated user to staff and superuser")
        
        # Create school configuration if missing
        cursor.execute("SELECT COUNT(*) FROM accounts_schoolconfiguration;")
        config_exists = cursor.fetchone()[0]
        
        if config_exists == 0:
            cursor.execute("""
                INSERT INTO accounts_schoolconfiguration 
                (school_id, system_name, system_email, address, phone, currency, timezone, academic_year, is_configured, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                school_id,
                "Test School Management System",
                "admin@school.com",
                "123 Test Street",
                "+1234567890",
                "USD",
                "UTC",
                "2026",
                True,
                datetime.now(),
                datetime.now()
            ))
            print("✅ Created school configuration")
        
        # Commit changes
        conn.commit()
        
        print("\n🎉 LOGIN ISSUE FIXED!")
        print("=" * 25)
        print("✅ Admin user now has UserProfile")
        print("✅ User is now staff and superuser")
        print("✅ School configuration created")
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print("URL: https://school-management-c-8qtq.onrender.com/accounts/login/")
        print("Username: admin")
        print("Password: [Check your original password or reset]")
        
        print("\n💡 NEXT STEPS:")
        print("1. Try logging in with the admin credentials")
        print("2. If password doesn't work, use password reset")
        print("3. Access admin panel at /admin/")
        print("4. Create additional user accounts as needed")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()

if __name__ == "__main__":
    fix_login()
